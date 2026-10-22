"""Synthetic contract tests: never make a paid network call."""

import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import urllib.error
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "astra-foreman" / "scripts" / "jev_decide.py"
SPEC = importlib.util.spec_from_file_location("jev_decide", SCRIPT)
jev = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(jev)


def request():
    return {"state": {"items": [{"id": "item_1", "kind": "claim", "signals": {"overlap": 0.8}}]},
            "questions": {
                "yes": {"type": "noul", "instructions": "Is overlap strong?"},
                "pick": {"type": "choice", "instructions": "Which candidate?", "criteria": {
                    "keep": "Keep for review", "inspect": "Inspect for review"}},
                "rank": {"type": "score", "instructions": "Rank evidence strength", "criteria": [
                    "weak", "mixed", "strong"]}}}


def response():
    return {"model": "typesafe/jev-1.14-20261014", "answers": {
        "yes": {"type": "noul", "noul": 0.8},
        "pick": {"type": "choice", "choice": "keep", "probabilities": {
            "keep": 0.7, "inspect": 0.3}, "confidence": 0.7},
        "rank": {"type": "score", "score": 1.4, "legend": {
            "0": "weak", "1": "mixed", "2": "strong"}, "probabilities": {
            "0": 0.1, "1": 0.4, "2": 0.5}, "confidence": 0.6}},
        "usage": {"input_tokens": 350, "output_tokens": 20, "cost": 0.00002}}


class Contract(unittest.TestCase):
    def setUp(self):
        # A developer's session pin must not influence these synthetic calls.
        model_env = patch.dict(jev.os.environ, {"FOREMAN_JEV_MODEL": ""})
        model_env.start()
        self.addCleanup(model_env.stop)

    def test_real_settings_opt_in_parser_with_temporary_home(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            flag = root / ".foreman" / "jev-enabled"
            with patch.object(jev.os, "environ", {"HOME": directory}):
                self.assertEqual(jev.settings(), (False, {}))
                self.assertFalse(flag.parent.exists())
            with patch.object(jev.os, "environ", {"HOME": directory, "FOREMAN_JEV": "1"}):
                self.assertEqual(jev.settings(), (True, {}))
                self.assertFalse(flag.parent.exists())
            flag.parent.mkdir()
            flag.write_text("")
            with patch.object(jev.os, "environ", {"HOME": directory}):
                self.assertEqual(jev.settings(), (True, {}))
            flag.write_text("# comment\nprivacy: snippets\nprovider: openrouter\nkeychain-service: test-service\nignored: value\n")
            with patch.object(jev.os, "environ", {"HOME": directory}):
                self.assertEqual(jev.settings(), (True, {"privacy": "snippets",
                                                        "provider": "openrouter",
                                                        "keychain-service": "test-service"}))
            flag.write_bytes(b"privacy: \xff\n")
            with patch.object(jev.os, "environ", {"HOME": directory}):
                with self.assertRaisesRegex(jev.Invalid, "configuration unreadable"):
                    jev.settings()
            with patch.object(jev.os, "environ", {"HOME": directory}), patch(
                "builtins.open", side_effect=OSError("secret-path")):
                with self.assertRaisesRegex(jev.Invalid, "configuration unreadable"):
                    jev.settings()

    def test_valid_all_three(self):
        body = jev.validate_request(request(), {})
        self.assertEqual(json.loads(body)["model"], jev.MODEL)
        result = jev.validate_response(response(), request()["questions"])
        self.assertEqual(result["usage"]["cost"], 0.00002)
        self.assertEqual(result["model_reported"], "typesafe/jev-1.14-20261014")

    def test_request_rejects_raw_state_and_invalid_score_before_spend(self):
        bad = request()
        bad["state"]["raw_document"] = "secret"
        with self.assertRaises(jev.Invalid):
            jev.validate_request(bad, {})
        bad = request()
        bad["questions"].update({f"q{i}": {"type": "noul", "instructions": "Synthetic?"}
                                 for i in range(6)})
        with self.assertRaisesRegex(jev.Invalid, "1 to 8"):
            jev.validate_request(bad, {})
        bad = request()
        bad["state"]["items"] = [{"id": f"item_{i}", "kind": "claim"} for i in range(33)]
        with self.assertRaisesRegex(jev.Invalid, "1 to 32"):
            jev.validate_request(bad, {})
        bad = request()
        bad["state"]["items"] = [{"id": f"item_{i}", "kind": "claim",
                                     "labels": ["x" * 79 for _ in range(12)]} for i in range(32)]
        with self.assertRaisesRegex(jev.Invalid, "byte cap"):
            jev.validate_request(bad, {})
        bad = request()
        bad["questions"]["rank"]["criteria"] = ["only one"]
        with self.assertRaises(jev.Invalid):
            jev.validate_request(bad, {})
        bad = request()
        bad["state"]["items"][0]["signals"]["bad"] = float("nan")
        with self.assertRaises(jev.Invalid):
            jev.validate_request(bad, {})

    def test_snippets_need_double_opt_in_and_cap(self):
        req = request()
        req["privacy"] = "snippets"
        req["state"]["items"][0]["snippet"] = "synthetic excerpt"
        with self.assertRaises(jev.Invalid):
            jev.validate_request(req, {})
        jev.validate_request(req, {"privacy": "snippets"})
        req["state"]["items"][0]["snippet"] = "x" * 401
        with self.assertRaises(jev.Invalid):
            jev.validate_request(req, {"privacy": "snippets"})
        req = request()
        req["state"]["items"][0]["snippet"] = "snippet without request consent"
        with self.assertRaises(jev.Invalid):
            jev.validate_request(req, {"privacy": "snippets"})
        req = request()
        req["state"]["items"][0]["path"] = "/private/document.md"
        with self.assertRaises(jev.Invalid):
            jev.validate_request(req, {})
        req = request()
        req["model"] = "attacker/model"
        with self.assertRaises(jev.Invalid):
            jev.validate_request(req, {})

    def test_response_rejects_missing_extra_and_bad_values(self):
        for mutate in (
            lambda r: r["answers"].pop("yes"),
            lambda r: r["answers"].update({"unknown": {"type": "noul", "noul": 0.5}}),
            lambda r: r["answers"]["yes"].update({"noul": True}),
            lambda r: r["answers"]["pick"].update({"choice": "unknown"}),
            lambda r: r["answers"]["pick"]["probabilities"].pop("inspect"),
            lambda r: r["answers"]["rank"].update({"score": float("inf")}),
            lambda r: r["answers"]["rank"]["legend"].update({"0": "changed"}),
            lambda r: r.update({"model": "unrelated/model"}),
            lambda r: r["answers"]["pick"]["probabilities"].update({"keep": 0.6}),
        ):
            with self.subTest(mutate=mutate):
                result = response()
                mutate(result)
                with self.assertRaises(jev.Invalid):
                    jev.validate_response(result, request()["questions"])
        result = response()
        result["answers"]["yes"]["future_field"] = "secret-key"
        clean = jev.validate_response(result, request()["questions"])
        self.assertNotIn("future_field", clean["answers"]["yes"])

    def test_disabled_or_invalid_request_never_resolves_key_or_posts(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            with patch.object(jev, "settings", return_value=(False, {})), patch.object(
                jev, "credential", side_effect=AssertionError("must not resolve key")), patch.object(
                jev, "post", side_effect=AssertionError("must not call network")):
                with self.assertRaises(jev.Invalid):
                    jev.run(str(source), str(target))
            with patch.object(jev, "settings", return_value=(True, {"provider": "typesafe"})), patch.object(
                jev, "credential", side_effect=AssertionError("must not resolve key")), patch.object(
                jev, "post", side_effect=AssertionError("must not call network")):
                with self.assertRaises(jev.Invalid):
                    jev.run(str(source), str(target))
            source.write_text(json.dumps({"state": "raw", "questions": {}}))
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", side_effect=AssertionError("must not resolve key")), patch.object(
                jev, "post", side_effect=AssertionError("must not call network")):
                with self.assertRaises(jev.Invalid):
                    jev.run(str(source), str(target))
            source.write_bytes(b" " * (jev.MAX_REQUEST_BYTES + 1))
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", side_effect=AssertionError("must not resolve key")), patch.object(
                jev, "post", side_effect=AssertionError("must not call network")):
                with self.assertRaisesRegex(jev.Invalid, "request exceeds byte cap"):
                    jev.run(str(source), str(target))
            self.assertFalse(target.exists())

    def test_mocked_success_and_existing_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", return_value="secret-key"), patch.object(
                jev, "post", return_value=(response(), 0.125)) as post:
                jev.run(str(source), str(target))
                self.assertEqual(post.call_count, 1)
                artifact = json.loads(target.read_text())
                self.assertEqual(artifact["status"], "ok")
                self.assertEqual(artifact["latency_seconds"], 0.125)
                self.assertNotIn("secret-key", target.read_text())
                with self.assertRaises(jev.Invalid):
                    jev.run(str(source), str(target))
                self.assertEqual(post.call_count, 1)

    def test_symlink_and_malformed_success_do_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            target.symlink_to(Path(directory) / "missing.json")
            with self.assertRaises(jev.Invalid):
                jev.run(str(source), str(target))
            target.unlink()
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", return_value="secret-key"), patch.object(
                jev, "post", return_value=({"answers": {}}, 0.2)):
                with self.assertRaises(jev.Invalid):
                    jev.run(str(source), str(target))
            self.assertFalse(target.exists())

    def test_key_selection_and_redirect_block(self):
        with patch.object(jev.os, "environ", {"OPENROUTER_API_KEY": "env-secret"}):
            self.assertEqual(jev.credential({"keychain-service": "other"}), "env-secret")
        with patch.object(jev.os, "environ", {"OPENROUTER_API_KEY": ""}), patch.object(
            jev.sys, "platform", "darwin"), patch.object(jev.subprocess, "run") as command:
            command.return_value.returncode = 0
            command.return_value.stdout = "keychain-secret\n"
            self.assertEqual(jev.credential({"keychain-service": "codex-openrouter"}), "keychain-secret")
            self.assertEqual(command.call_args.args[0], [
                "security", "find-generic-password", "-s", "codex-openrouter", "-w"])
            self.assertTrue(command.call_args.kwargs["capture_output"])
        handler = jev.NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "move", {}, "https://evil.test"))
        redirect = urllib.error.HTTPError(jev.ENDPOINT, 302, "secret-key", {}, None)
        with patch.object(jev.urllib.request, "build_opener") as builder:
            builder.return_value.open.side_effect = redirect
            with self.assertRaisesRegex(jev.Invalid, "REDIRECT_BLOCKED") as caught:
                jev.post(b"{}", "secret-key")
        self.assertNotIn("secret-key", str(caught.exception))

    def test_http_statuses_and_transport_are_safe_and_distinct(self):
        cases = {401: "AUTH_REQUIRED", 403: "HTTP_403",
                 402: "BALANCE_EXHAUSTED", 429: "RATE_LIMITED",
                 404: "HTTP_404", 500: "HTTP_500"}
        for status, expected in cases.items():
            with self.subTest(status=status), patch.object(jev.urllib.request, "build_opener") as builder:
                builder.return_value.open.side_effect = urllib.error.HTTPError(
                    jev.ENDPOINT, status, "secret-key", {}, None)
                with self.assertRaises(jev.Invalid) as caught:
                    jev.post(b"{}", "secret-key")
                self.assertEqual(str(caught.exception), expected)
        for error in (urllib.error.URLError("secret-key"), TimeoutError("secret-key")):
            with self.subTest(error=type(error).__name__), patch.object(
                jev.urllib.request, "build_opener") as builder:
                builder.return_value.open.side_effect = error
                with self.assertRaises(jev.Invalid) as caught:
                    jev.post(b"{}", "secret-key")
                self.assertEqual(str(caught.exception), "provider transport failure")

    def test_http_400_model_refusal_is_classified_without_exposing_body(self):
        cases = ((400, b'{"error":{"message":"Model DOES NOT EXIST secret-key"}}',
                  "MODEL_NOT_FOUND"),
                 (400, b'{"error":{"message":"Invalid questions secret-key"}}', "HTTP_400"),
                 (401, b"model does not exist secret-key", "AUTH_REQUIRED"),
                 (404, b"secret-key", "HTTP_404"))
        for status, body, expected in cases:
            with self.subTest(status=status, expected=expected), patch.object(
                    jev.urllib.request, "build_opener") as builder:
                stream = io.BytesIO(body)
                builder.return_value.open.side_effect = urllib.error.HTTPError(
                    jev.ENDPOINT, status, "secret-key", {}, stream)
                with self.assertRaises(jev.Invalid) as caught:
                    jev.post(b"{}", "secret-key")
                self.assertEqual(str(caught.exception), expected)
                self.assertTrue(stream.closed)

    def test_http_400_body_read_is_bounded_and_unreadable_body_does_not_fallback(self):
        for unreadable in (False, True):
            with self.subTest(unreadable=unreadable), patch.object(
                    jev.urllib.request, "build_opener") as builder:
                error = urllib.error.HTTPError(jev.ENDPOINT, 400, "secret-key", {}, None)
                builder.return_value.open.side_effect = error
                with patch.object(error, "read") as read:
                    if unreadable:
                        read.side_effect = OSError("secret-key")
                    else:
                        read.return_value = b"x" * jev.MAX_RESPONSE_BYTES
                    with self.assertRaisesRegex(jev.Invalid, "^HTTP_400$"):
                        jev.post(b"{}", "secret-key")
                    read.assert_called_once_with(jev.MAX_RESPONSE_BYTES)

    def test_nonraising_http_400_response_is_also_classified(self):
        with patch.object(jev.urllib.request, "build_opener") as builder:
            reply = builder.return_value.open.return_value.__enter__.return_value
            reply.status = 400
            reply.read.return_value = b"model does not exist secret-key"
            with self.assertRaisesRegex(jev.Invalid, "^MODEL_NOT_FOUND$"):
                jev.post(b"{}", "secret-key")
            reply.read.assert_called_once_with(jev.MAX_RESPONSE_BYTES)

    def test_real_http_layer_alias_refused_then_114_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                    jev, "credential", return_value="secret-key"), patch.object(
                    jev.urllib.request, "build_opener") as builder:
                reply_context = builder.return_value.open.return_value
                reply = reply_context.__enter__.return_value
                reply.status = 200
                reply.read.return_value = json.dumps(response()).encode()
                builder.return_value.open.side_effect = [urllib.error.HTTPError(
                    jev.ENDPOINT, 400, "bad request", {}, io.BytesIO(
                        b'{"error":{"message":"~typesafe/jev-latest does not exist"}}')),
                    reply_context]
                jev.run(str(source), str(target))
                self.assertEqual([json.loads(call.args[0].data)["model"]
                                  for call in builder.return_value.open.call_args_list],
                                 [jev.MODEL, "typesafe/jev-1.14"])
            artifact = json.loads(target.read_text())
            self.assertEqual(artifact["model_requested"], "typesafe/jev-1.14")
            self.assertEqual(artifact["model_reported"], "typesafe/jev-1.14-20261014")
            self.assertEqual(artifact["fallback_attempts"], [
                {"model": jev.MODEL, "reason": "MODEL_NOT_FOUND"}])

    def test_real_http_layer_explicit_pin_refusal_never_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            for model in ("typesafe/jev-1.14", "typesafe/jev-1.14-20261014"):
                with self.subTest(model=model), patch.object(
                        jev, "settings", return_value=(True, {})), patch.object(
                        jev, "credential", return_value="secret-key"), patch.object(
                        jev.urllib.request, "build_opener") as builder:
                    builder.return_value.open.side_effect = urllib.error.HTTPError(
                        jev.ENDPOINT, 400, "bad request", {}, io.BytesIO(
                            b'{"error":{"message":"requested model does not exist"}}'))
                    with self.assertRaisesRegex(jev.Invalid, "^MODEL_NOT_FOUND$"):
                        jev.run(str(source), str(target), model)
                    self.assertEqual(builder.return_value.open.call_count, 1)
                    self.assertEqual(json.loads(builder.return_value.open.call_args.args[0].data)["model"],
                                     model)
                    self.assertFalse(target.exists())

    def test_response_cap_and_main_failure_do_not_emit_secret(self):
        with patch.object(jev.urllib.request, "build_opener") as builder:
            response = builder.return_value.open.return_value.__enter__.return_value
            response.status = 200
            response.read.return_value = b"x" * (jev.MAX_RESPONSE_BYTES + 1)
            with self.assertRaisesRegex(jev.Invalid, "response exceeds byte cap"):
                jev.post(b"{}", "secret-key")
            self.assertEqual(builder.return_value.open.call_args.kwargs["timeout"], 10)
            self.assertEqual(response.read.call_args.args[0], jev.MAX_RESPONSE_BYTES + 1)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            stderr = io.StringIO()
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", return_value="secret-key"), patch.object(
                jev.urllib.request, "build_opener") as builder, contextlib.redirect_stderr(stderr):
                builder.return_value.open.side_effect = urllib.error.URLError("secret-key")
                self.assertNotEqual(jev.main(["run", str(source), str(target)]), 0)
            self.assertIn("transport failure", stderr.getvalue())
            self.assertNotIn("secret-key", stderr.getvalue())
            self.assertFalse(target.exists())

    def test_alias_accepts_new_release_and_requires_served_identity(self):
        result = response()
        result["model"] = "typesafe/jev-1.15-20261201"
        self.assertEqual(jev.validate_response(result, request()["questions"])["model_reported"],
                         result["model"])
        for reported in (None, "", jev.MODEL, "typesafe/jev-1.14-untrusted", 42):
            result["model"] = reported
            with self.subTest(reported=reported), self.assertRaises(jev.Invalid):
                jev.validate_response(result, request()["questions"])

    def test_explicit_pin_checks_exact_release_and_session_id(self):
        jev.validate_response(response(), request()["questions"], "typesafe/jev-1.14")
        jev.validate_response(response(), request()["questions"], "typesafe/jev-1.14-20261014")
        for model in ("typesafe/jev-1.13", "typesafe/jev-1.14-20261015"):
            with self.subTest(model=model), self.assertRaises(jev.Invalid):
                jev.validate_response(response(), request()["questions"], model)

    def test_model_selection_override_precedence(self):
        self.assertEqual(jev.selected_models({}), (jev.MODEL, *jev.PIN_FALLBACKS))
        self.assertEqual(jev.selected_models({"model": "typesafe/jev-1.13"}),
                         ("typesafe/jev-1.13",))
        with patch.dict(jev.os.environ, {"FOREMAN_JEV_MODEL": "typesafe/jev-1.14"}):
            self.assertEqual(jev.selected_models({"model": "typesafe/jev-1.13"}),
                             ("typesafe/jev-1.14",))
            self.assertEqual(jev.selected_models({}, "typesafe/jev-1.14-20261014"),
                             ("typesafe/jev-1.14-20261014",))
        with self.assertRaises(jev.Invalid):
            jev.selected_models({}, "unrelated/model")

    def test_mocked_default_fallback_order_and_served_pin_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            older = response()
            older["model"] = "typesafe/jev-1.13-20260917"
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", return_value="secret-key"), patch.object(
                jev, "post", side_effect=[jev.Invalid("HTTP_404"),
                                          jev.Invalid("MODEL_NOT_FOUND"), (older, 0.125)]) as post:
                jev.run(str(source), str(target))
                requested = [json.loads(call.args[0])["model"] for call in post.call_args_list]
                self.assertEqual(requested, ["~typesafe/jev-latest", "typesafe/jev-1.14",
                                             "typesafe/jev-1.13"])
            artifact = json.loads(target.read_text())
            self.assertEqual(artifact["model_requested"], "typesafe/jev-1.13")
            self.assertEqual(artifact["model_reported"], older["model"])
            self.assertEqual([attempt["model"] for attempt in artifact["fallback_attempts"]],
                             requested[:2])
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", return_value="secret-key"), patch.object(
                jev, "post", return_value=(older, 0.1)) as post:
                self.assertEqual(jev.main(["run", str(source), str(Path(directory) / "next.json"),
                                           "--model", artifact["model_reported"]]), 0)
                self.assertEqual(json.loads(post.call_args.args[0])["model"], older["model"])
                self.assertEqual(post.call_count, 1)

    def test_mocked_first_pin_fallback_success(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", return_value="secret-key"), patch.object(
                jev, "post", side_effect=[jev.Invalid("HTTP_404"), (response(), 0.1)]) as post:
                jev.run(str(source), str(target))
                self.assertEqual(post.call_count, 2)
                self.assertEqual(json.loads(target.read_text())["model_requested"], "typesafe/jev-1.14")

    def test_failures_do_not_spend_on_fallback_or_write_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            target = Path(directory) / "answer.json"
            source.write_text(json.dumps(request()))
            for failure in ("AUTH_REQUIRED", "BALANCE_EXHAUSTED", "RATE_LIMITED",
                            "provider transport failure", "HTTP_400", "HTTP_500"):
                with self.subTest(failure=failure), patch.object(
                    jev, "settings", return_value=(True, {})), patch.object(
                    jev, "credential", return_value="secret-key"), patch.object(
                    jev, "post", side_effect=jev.Invalid(failure)) as post:
                    with self.assertRaises(jev.Invalid):
                        jev.run(str(source), str(target))
                    self.assertEqual(post.call_count, 1)
                    self.assertFalse(target.exists())
            with patch.object(jev, "settings", return_value=(True, {})), patch.object(
                jev, "credential", return_value="secret-key"), patch.object(
                jev, "post", side_effect=jev.Invalid("HTTP_404")) as post:
                with self.assertRaises(jev.Invalid):
                    jev.run(str(source), str(target))
                self.assertEqual(post.call_count, 3)
                self.assertFalse(target.exists())
                post.reset_mock()
                with self.assertRaises(jev.Invalid):
                    jev.run(str(source), str(target), "typesafe/jev-1.14")
                self.assertEqual(post.call_count, 1)

    def test_config_model_override_is_read_without_enabling(self):
        with tempfile.TemporaryDirectory() as directory:
            flag = Path(directory) / ".foreman/jev-enabled"
            flag.parent.mkdir()
            flag.write_text("model: typesafe/jev-1.14-20261014\n")
            with patch.object(jev.os, "environ", {"HOME": directory}):
                enabled, config = jev.settings()
                self.assertTrue(enabled)
                self.assertEqual(jev.selected_models(config), ("typesafe/jev-1.14-20261014",))


if __name__ == "__main__":
    unittest.main()
