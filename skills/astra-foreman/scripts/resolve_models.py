#!/usr/bin/env python3
"""Resolve model lines from local catalog data; never dispatch or contact a provider."""

import argparse
import json
import os
from pathlib import Path
import re
import sys


CODEX_LINES = frozenset(("sol", "luna", "astra", "terra"))
UNUSED_CODEX_LINES = frozenset(("terra",))
CODEX_ID = re.compile(r"gpt-([0-9]+(?:\.[0-9]+)*)-([a-z][a-z0-9-]*)\Z")
GROK_ID = re.compile(r"grok-([0-9]+(?:\.[0-9]+)*)\Z")
PREMIUM_STATUS = "premium; double approval required"


class CatalogError(ValueError):
    pass


def normalize_model_id(model):
    """Normalize matching only; retain the catalog's exact ID for dispatch."""
    if not isinstance(model, str):
        return ""
    model = re.split(r"[/:]", model.strip().lower())[-1].strip()
    return re.sub(r"(?:\s*(?:\[[^\[\]]*\]|\([^()]*\)))+$", "", model).strip()


def version_key(version):
    """Numeric components, never float or lexical comparison."""
    return tuple(int(part) for part in version.split("."))


def read_catalog(path=None):
    if path is None:
        path = Path(os.environ.get("CODEX_HOME") or "~/.codex").expanduser() / "models_cache.json"
    try:
        with open(Path(path).expanduser(), encoding="utf-8") as stream:
            catalog = json.load(stream)
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise CatalogError("catalog missing, unreadable, or malformed") from None
    # Check the container even when no line is present.
    visible_codex_models(catalog)
    return catalog


def visible_codex_models(catalog):
    if not isinstance(catalog, dict) or not isinstance(catalog.get("models"), list):
        raise CatalogError("catalog must contain a models list")
    result = {}
    for entry in catalog["models"]:
        if not isinstance(entry, dict) or entry.get("visibility") != "list":
            continue
        slug = entry.get("slug")
        match = CODEX_ID.fullmatch(normalize_model_id(slug))
        if match:
            try:
                result[slug] = (version_key(match[1]), match[2])
            except ValueError:
                # Includes unreasonably large numeric strings in malformed data.
                continue
    return result


def codex_candidates(catalog, line):
    models = visible_codex_models(catalog)
    if line not in CODEX_LINES or line in UNUSED_CODEX_LINES:
        return []  # Unknown and retired lines are never routing candidates.
    return sorted((slug for slug, (_, name) in models.items() if name == line),
                  key=lambda slug: (models[slug][0], slug), reverse=True)


def resolve_codex(catalog, line):
    candidates = codex_candidates(catalog, line)
    return candidates[0] if candidates else None


def unknown_lines(catalog):
    grouped = {}
    models = visible_codex_models(catalog)
    for slug, (_, line) in models.items():
        if line not in CODEX_LINES:
            grouped.setdefault(line, []).append(slug)
    return [{"line": line,
             "status": PREMIUM_STATUS if is_premium(line) else "unknown line — recon first",
             "premium": is_premium(line),
             "models": sorted(slugs, key=lambda slug: (models[slug][0], slug), reverse=True)}
            for line, slugs in sorted(grouped.items())]


def grok_candidates(model_ids):
    """Only the base Grok line is eligible; every suffixed variant is excluded."""
    if not isinstance(model_ids, (list, tuple)):
        raise CatalogError("Grok model ids must be a list")
    candidates = {}
    for model in model_ids:
        match = GROK_ID.fullmatch(normalize_model_id(model))
        if match:
            try:
                candidates[model] = version_key(match[1])
            except ValueError:
                continue
    return sorted(candidates, key=lambda model: (candidates[model], model), reverse=True)


def resolve_grok(model_ids):
    candidates = grok_candidates(model_ids)
    return candidates[0] if candidates else None


def is_premium(model):
    model = normalize_model_id(model)
    return "astra" in model or "fable" in model


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("codex", "grok"), help="inferred from --line by default")
    parser.add_argument("--line", type=lambda value: value.strip().lower(),
                        help="Codex line (sol/luna/astra), or grok")
    parser.add_argument("--ids", help="comma-separated Grok model IDs from the provider catalog")
    parser.add_argument("--catalog", help="defaults to ${CODEX_HOME:-~/.codex}/models_cache.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    provider = args.provider or ("grok" if args.line == "grok" else "codex")
    line = args.line or ("grok" if provider == "grok" else None)
    if line is None:
        parser.error("--line is required for Codex")
    try:
        if provider == "grok":
            if line != "grok":
                raise CatalogError("Grok provider requires --line grok")
            if args.ids is None:
                raise CatalogError("Grok requires --ids with comma-separated provider model IDs")
            candidates = grok_candidates([model.strip() for model in args.ids.split(",")])
            descriptions = {}
            unknown = []
            unused = []
            status = "resolved" if candidates else "absent"
        else:
            if args.ids is not None:
                raise CatalogError("--ids requires the Grok provider")
            catalog = read_catalog(args.catalog)
            candidates = codex_candidates(catalog, line)
            descriptions = {entry["slug"]: entry.get("description")
                            for entry in catalog["models"]
                            if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
                            and entry.get("visibility") == "list"}
            unknown = unknown_lines(catalog)
            unused = [{"line": name, "status": "known/superseded-or-unused",
                       "models": sorted(slug for slug, (_, model_line)
                                        in visible_codex_models(catalog).items() if model_line == name)}
                      for name in sorted(UNUSED_CODEX_LINES)
                      if any(model_line == name for _, model_line in visible_codex_models(catalog).values())]
            status = (PREMIUM_STATUS if line not in CODEX_LINES and is_premium(line) else
                      "unknown line — recon first" if line not in CODEX_LINES else
                      "known/superseded-or-unused" if line in UNUSED_CODEX_LINES else
                      "resolved" if candidates else "absent")
        model = candidates[0] if candidates else None
        report = {"line": line, "model": model,
                  "premium": is_premium(model) or is_premium(line),
                  "candidates": [{"id": candidate, "description": descriptions.get(candidate)}
                                 for candidate in candidates],
                  "status": status, "unknown_lines": unknown, "unused_lines": unused}
    except CatalogError as error:
        report = {"line": line, "model": None, "status": "error", "error": str(error)}
        print(json.dumps(report) if args.json else report["error"])
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        label = model or report["status"]
        if report["premium"] and label != PREMIUM_STATUS:
            label += " (" + PREMIUM_STATUS + ")"
        print(label)
        for entry in report["unknown_lines"] + report["unused_lines"]:
            print("{}: {} ({})".format(entry["line"], entry["status"], ", ".join(entry["models"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
