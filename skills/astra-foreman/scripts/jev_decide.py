#!/usr/bin/env python3
"""Optional, advisory Jev decision call. See --help for the request contract."""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "~typesafe/jev-latest"
PIN_FALLBACKS = ("typesafe/jev-1.14", "typesafe/jev-1.13")
JEV_PIN = re.compile(r"typesafe/jev-[0-9]+(?:\.[0-9]+)+(?:-[0-9]{8})?\Z")
MAX_REQUEST_BYTES = 16_384  # Deliberately a byte cap, not a token estimate.
MAX_RESPONSE_BYTES = 131_072
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
TAG = re.compile(r"^[A-Za-z][A-Za-z0-9_ -]{0,79}$")


class Invalid(ValueError):
    pass


def number(value, low, high):
    return type(value) in (int, float) and low <= value <= high and math.isfinite(value)


def text(value, limit):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit


def settings():
    """Read an existing user opt-in; never create or modify it."""
    path = os.path.join(os.path.expanduser("~"), ".foreman", "jev-enabled")
    enabled = os.environ.get("FOREMAN_JEV") == "1" or os.path.isfile(path)
    config = {}
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as stream:
                for line in stream:
                    if ":" in line and not line.lstrip().startswith("#"):
                        key, value = line.split(":", 1)
                        if key.strip() in ("privacy", "keychain-service", "provider", "model"):
                            config[key.strip()] = value.strip()
        except (OSError, UnicodeError):
            raise Invalid("opt-in configuration unreadable") from None
    return enabled, config


def credential(config):
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    service = config.get("keychain-service", "")
    if service and sys.platform == "darwin" and len(service) <= 128 and "\n" not in service:
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", service, "-w"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return ""


def selected_models(config, override=None):
    """Explicit pins override discovery and never silently fall back."""
    selected = override or os.environ.get("FOREMAN_JEV_MODEL") or config.get("model")
    if selected:
        if not isinstance(selected, str) or not (selected == MODEL or JEV_PIN.fullmatch(selected)):
            raise Invalid("model override must be the Jev alias or a Jev pin")
        return (selected,)
    return (MODEL, *PIN_FALLBACKS)


def validate_request(request, config, model=MODEL):
    if not isinstance(request, dict) or set(request) - {"privacy", "state", "questions"}:
        raise Invalid("request must contain only privacy, state, questions")
    privacy = request.get("privacy", "metadata")
    if privacy not in ("metadata", "snippets"):
        raise Invalid("privacy must be metadata or snippets")
    if privacy == "snippets" and config.get("privacy") != "snippets":
        raise Invalid("snippets require privacy: snippets in the existing opt-in file")
    state = request.get("state")
    if not isinstance(state, dict) or set(state) != {"items"}:
        raise Invalid("state must contain only items")
    items = state["items"]
    if not isinstance(items, list) or not 1 <= len(items) <= 32:
        raise Invalid("items must contain 1 to 32 entries")
    seen = set()
    for item in items:
        allowed = {"id", "kind", "labels", "signals"}
        if privacy == "snippets":
            allowed.add("snippet")
        if not isinstance(item, dict) or set(item) - allowed or not {"id", "kind"} <= set(item):
            raise Invalid("item has missing or unapproved fields")
        item_id = item["id"]
        if not isinstance(item_id, str) or not ID.fullmatch(item_id) or item_id in seen:
            raise Invalid("item ids must be unique opaque identifiers")
        seen.add(item_id)
        if not isinstance(item["kind"], str) or not TAG.fullmatch(item["kind"]):
            raise Invalid("item kind must be a short category")
        labels = item.get("labels", [])
        if not isinstance(labels, list) or len(labels) > 12 or any(
            not isinstance(label, str) or not TAG.fullmatch(label) for label in labels
        ):
            raise Invalid("labels must be short category tags")
        signals = item.get("signals", {})
        if not isinstance(signals, dict) or len(signals) > 16 or any(
            not isinstance(name, str) or not ID.fullmatch(name)
            or not (type(value) is bool or number(value, -1_000_000, 1_000_000))
            for name, value in signals.items()
        ):
            raise Invalid("signals must be bounded numeric or boolean metadata")
        if "snippet" in item and (privacy != "snippets" or not text(item["snippet"], 400)):
            raise Invalid("snippet requires explicit consent and at most 400 characters")
    questions = request.get("questions")
    if not isinstance(questions, dict) or not 1 <= len(questions) <= 8:
        raise Invalid("questions must contain 1 to 8 entries")
    for name, question in questions.items():
        if not isinstance(name, str) or not ID.fullmatch(name) or not isinstance(question, dict):
            raise Invalid("invalid question id or body")
        kind = question.get("type")
        required = {"type", "instructions"} | ({"criteria"} if kind != "noul" else set())
        if kind not in ("noul", "choice", "score") or set(question) != required:
            raise Invalid("question fields or type invalid")
        if not text(question["instructions"], 300):
            raise Invalid("question instructions must be 1 to 300 characters")
        criteria = question.get("criteria")
        if kind == "choice" and (
            not isinstance(criteria, dict) or not 2 <= len(criteria) <= 16 or any(
                not isinstance(option, str) or not ID.fullmatch(option)
                or not text(description, 160) for option, description in criteria.items()
            )
        ):
            raise Invalid("choice needs 2 to 16 described option ids")
        if kind == "score" and (
            not isinstance(criteria, list) or not 2 <= len(criteria) <= 10
            or any(not text(level, 160) for level in criteria)
        ):
            raise Invalid("score needs 2 to 10 ordered descriptions")
    body = json.dumps({"model": model, "state": state, "questions": questions},
                      ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if len(body) > MAX_REQUEST_BYTES:
        raise Invalid("request exceeds byte cap")
    return body


def probabilities(values, expected):
    if not isinstance(values, dict) or set(values) != set(expected):
        raise Invalid("probability keys do not match criteria")
    if any(not number(value, 0, 1) for value in values.values()):
        raise Invalid("probabilities must be finite numbers from 0 to 1")
    if not 0.98 <= sum(values.values()) <= 1.02:
        raise Invalid("probabilities do not sum to one")


def validate_response(response, questions, model=MODEL):
    if not isinstance(response, dict) or not isinstance(response.get("answers"), dict):
        raise Invalid("missing answers")
    answers = response["answers"]
    if set(answers) != set(questions):
        raise Invalid("answer keys do not match questions")
    clean_answers = {}
    for name, question in questions.items():
        answer = answers[name]
        kind = question["type"]
        if not isinstance(answer, dict) or answer.get("type") != kind:
            raise Invalid("answer type mismatch")
        if kind == "noul":
            if not number(answer.get("noul"), 0, 1):
                raise Invalid("invalid noul probability")
            clean_answers[name] = {"type": kind, "noul": answer["noul"]}
        elif kind == "choice":
            options = question["criteria"]
            if not isinstance(answer.get("choice"), str) or answer["choice"] not in options or not number(answer.get("confidence"), 0, 1):
                raise Invalid("invalid choice or confidence")
            probabilities(answer.get("probabilities"), options)
            clean_answers[name] = {"type": kind, "choice": answer["choice"],
                                   "probabilities": answer["probabilities"],
                                   "confidence": answer["confidence"]}
        else:
            levels = question["criteria"]
            indices = {str(i) for i in range(len(levels))}
            if not number(answer.get("score"), 0, len(levels) - 1) or not number(answer.get("confidence"), 0, 1):
                raise Invalid("invalid score or confidence")
            legend = answer.get("legend")
            if not isinstance(legend, dict) or legend != {str(i): value for i, value in enumerate(levels)}:
                raise Invalid("score legend mismatch")
            probabilities(answer.get("probabilities"), indices)
            clean_answers[name] = {"type": kind, "score": answer["score"],
                                   "legend": legend, "probabilities": answer["probabilities"],
                                   "confidence": answer["confidence"]}
    reported = response.get("model")
    if not isinstance(reported, str) or not JEV_PIN.fullmatch(reported):
        raise Invalid("missing or unexpected reported model")
    if model != MODEL and not (reported == model or re.fullmatch(re.escape(model) + r"-[0-9]{8}", reported)):
        raise Invalid("unexpected reported model")
    usage = response.get("usage")
    safe_usage = {"input_tokens": None, "output_tokens": None, "cost": None}
    if isinstance(usage, dict):
        for field in safe_usage:
            value = usage.get(field)
            if number(value, 0, 1_000_000_000):
                safe_usage[field] = value
    return {"status": "ok", "model_requested": model, "model_reported": reported,
            "usage": safe_usage, "answers": clean_answers}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def http_failure(code, body=b""):
    if code == 400 and b"does not exist" in body.lower():
        return "MODEL_NOT_FOUND"
    if code in (301, 302, 303, 307, 308):
        return "REDIRECT_BLOCKED"
    if code == 401:
        return "AUTH_REQUIRED"
    if code == 402:
        return "BALANCE_EXHAUSTED"
    if code == 429:
        return "RATE_LIMITED"
    if type(code) is int and 100 <= code <= 599:
        return f"HTTP_{code}"
    return "HTTP_FAILURE"


def post(body, key):
    request = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "Accept": "application/json",
    })
    opener = urllib.request.build_opener(NoRedirect())
    start = time.monotonic()
    try:
        with opener.open(request, timeout=10) as response:
            if response.status != 200:
                raw_error = response.read(MAX_RESPONSE_BYTES) if response.status == 400 else b""
                raise Invalid(http_failure(response.status, raw_error))
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as error:
        code = error.code
        raw_error = b""
        if code == 400:
            try:
                raw_error = error.read(MAX_RESPONSE_BYTES)
            except Exception:
                pass  # Unreadable bodies remain HTTP_400, never a fallback signal.
        try:
            error.close()
        except Exception:
            pass
        raise Invalid(http_failure(code, raw_error)) from None
    except Invalid:
        raise
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Invalid("provider transport failure") from None
    except Exception:
        raise Invalid("provider transport failure") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise Invalid("provider response exceeds byte cap")
    try:
        return json.loads(raw), round(time.monotonic() - start, 3)
    except (UnicodeError, ValueError):
        raise Invalid("provider returned malformed JSON") from None


def run(request_path, artifact_path, model=None):
    if not artifact_path.endswith(".json") or os.path.lexists(artifact_path):
        raise Invalid("artifact path must be a fresh .json file")
    enabled, config = settings()
    if not enabled:
        raise Invalid("Jev disabled; no existing opt-in")
    if config.get("provider", "openrouter") != "openrouter":
        raise Invalid("opt-in provider must be openrouter for this helper")
    try:
        with open(request_path, "rb") as stream:
            raw = stream.read(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES:
            raise Invalid("request exceeds byte cap")
        payload = json.loads(raw)
    except Invalid:
        raise
    except (OSError, UnicodeError, ValueError):
        raise Invalid("request unreadable or malformed") from None
    models = selected_models(config, model)
    body = validate_request(payload, config, models[0])
    key = credential(config)
    if not key:
        raise Invalid("OpenRouter key unavailable")
    attempts = []
    total_latency = 0.0
    for index, candidate in enumerate(models):
        if index:
            body = validate_request(payload, config, candidate)
        start = time.monotonic()
        try:
            response, latency = post(body, key)
        except Invalid as error:
            # Do not retry auth, balance, rate limits, transport, or invalid output.
            if str(error) not in ("HTTP_404", "MODEL_NOT_FOUND") or index == len(models) - 1:
                raise
            total_latency += time.monotonic() - start
            attempts.append({"model": candidate, "reason": str(error)})
            continue
        total_latency += latency
        envelope = validate_response(response, payload["questions"], candidate)
        break
    envelope["latency_seconds"] = round(total_latency, 3)
    envelope["fallback_attempts"] = attempts
    encoded = json.dumps(envelope, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8") + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(artifact_path, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
    except OSError:
        raise Invalid("artifact cannot be created safely") from None
    print("Jev decision validated; advisory artifact written")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        'Request JSON: {"privacy":"metadata", "state":{"items":[{"id":"opaque-id",'
        '"kind":"category","labels":["tag"],"signals":{"metric":1}}]},'
        '"questions":{"q":{"type":"noul","instructions":"Is the signal relevant?"}}}. '
        'choice adds criteria {"option_id":"description",...}; score adds ordered criteria '
        '["low", "high"]. Optional item snippet requires request privacy=snippets and '
        'privacy: snippets in existing ~/.foreman/jev-enabled. Only metadata or explicitly '
        'consented snippets are sent. The lead must screen all fields, including question text, '
        'for secrets before calling. Existing flag provider must be openrouter. Network socket '
        'timeout is 10 seconds, not a hard wall-clock deadline. Failure exits '
        'nonzero; preserve all source items and checks.'
    ))
    parser.add_argument("command", choices=["run"])
    parser.add_argument("request")
    parser.add_argument("artifact")
    parser.add_argument("--model", help="session served pin or explicit Jev override; disables fallbacks")
    args = parser.parse_args(argv)
    try:
        run(args.request, args.artifact, args.model)
    except (Invalid, TypeError) as error:
        print("Jev unavailable: " + str(error), file=sys.stderr)
        return 1
    except Exception:
        print("Jev unavailable: internal failure", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
