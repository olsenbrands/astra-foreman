"""Offline model-line discovery against synthetic provider catalogs."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/astra-foreman/scripts/resolve_models.py"
SPEC = importlib.util.spec_from_file_location("resolve_models", SCRIPT)
models = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(models)


def entry(slug, description="Latest model", visibility="list"):
    return {"slug": slug, "description": description, "visibility": visibility,
            "supported_reasoning_levels": [], "other_future_field": True}


def catalog():
    return {"models": [
        entry("gpt-6.1-sol"), entry("gpt-6-sol", "Previous generation"),
        entry("gpt-6-astra"), entry("gpt-6-luna"),
        *(entry("gpt-5.6-" + line, "Older") for line in ("sol", "astra", "luna")),
        entry("gpt-reserve", visibility="hidden"),
        entry("codex-auto-review", visibility="hidden"),
    ]}


class ResolverTests(unittest.TestCase):
    def test_dated_catalog_newest_by_line_and_premium(self):
        for line, expected in (("sol", "gpt-6.1-sol"), ("luna", "gpt-6-luna"),
                               ("astra", "gpt-6-astra")):
            with self.subTest(line=line):
                selected = models.resolve_codex(catalog(), line)
                self.assertEqual(selected, expected)
                self.assertEqual(models.is_premium(selected), line == "astra")
        self.assertEqual(models.codex_candidates(catalog(), "sol"),
                         ["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol"])

    def test_successor_in_known_line_is_automatic(self):
        data = catalog()
        data["models"].append(entry("gpt-6.2-luna"))
        self.assertEqual(models.resolve_codex(data, "luna"), "gpt-6.2-luna")

    def test_numeric_versions_not_float_or_lexical(self):
        data = {"models": [entry("gpt-6.9-sol"), entry("gpt-6.10-sol"),
                           entry("gpt-6-sol"), entry("gpt-5.60-sol")]}
        self.assertEqual(models.resolve_codex(data, "sol"), "gpt-6.10-sol")

    def test_hidden_newer_and_nonmatching_ids_ignored(self):
        data = catalog()
        data["models"].extend([entry("gpt-9-sol", visibility="hidden"),
                               entry("gpt-10-sol", visibility="unrecognized"),
                               entry("gpt-7-sol-fast"), entry("gpt-8sol"),
                               entry("gpt-7.0-sol-preview"), entry("gpt-x-sol"), None, {},
                               {"slug": ["gpt-20-sol"]}])
        self.assertEqual(models.resolve_codex(data, "sol"), "gpt-6.1-sol")

    def test_visibility_must_explicitly_be_list(self):
        data = {"models": [entry("gpt-6.1-sol"), {"slug": "gpt-9-sol"},
                           entry("gpt-10-sol", visibility="visible"),
                           entry("gpt-11-sol", visibility=None)]}
        self.assertEqual(models.codex_candidates(data, "sol"), ["gpt-6.1-sol"])

    def test_unknown_line_recon_first_never_default(self):
        data = catalog()
        data["models"].append(entry("gpt-7-nova"))
        self.assertEqual(models.unknown_lines(data), [{"line": "nova",
                         "status": "unknown line — recon first", "premium": False,
                         "models": ["gpt-7-nova"]}])
        self.assertIsNone(models.resolve_codex(data, "nova"))
        self.assertEqual(models.resolve_codex(data, "sol"), "gpt-6.1-sol")

    def test_empty_absent_and_malformed_catalog(self):
        self.assertIsNone(models.resolve_codex({"models": []}, "sol"))
        self.assertIsNone(models.resolve_codex({"models": [entry("gpt-6-luna")]}, "sol"))
        for data in (None, [], {}, {"models": None}, {"models": "wrong"}):
            with self.subTest(data=data), self.assertRaises(models.CatalogError):
                models.resolve_codex(data, "sol")

    def test_grok_base_only_numeric_versions(self):
        self.assertEqual(models.resolve_grok(["grok-4.6", "grok-4.7", "grok-4.7-build-fast",
                                             "grok-9-fast", None, "grok-build-0.1"]), "grok-4.7")
        self.assertEqual(models.resolve_grok(["grok-4.9", "grok-4.10"]), "grok-4.10")
        self.assertIsNone(models.resolve_grok(["grok-4.7-build-fast"]))
        self.assertIsNone(models.resolve_grok([]))
        with self.assertRaises(models.CatalogError):
            models.resolve_grok("grok-4.7")

    def test_premium_follows_line_for_every_version(self):
        for model in ("gpt-5.6-astra", "gpt-6-astra", "gpt-6.10-astra", "gpt-7-astra",
                      "gpt-6-astra-mini", "gpt-7-astrafuture", "Fable", "fable-5.1",
                      "vendor/FABLE-preview", "not-fable", "astra", "fable", "claude-fable",
                      "claude-fable-5-1", "claude-fable-6-2"):
            with self.subTest(model=model):
                self.assertTrue(models.is_premium(model))
        for model in ("gpt-6.1-sol", "gpt-7-luna", "grok-4.7", "sonnet", None, ""):
            with self.subTest(model=model):
                self.assertFalse(models.is_premium(model))

    def test_premium_normalizes_case_provider_and_bracket_suffix(self):
        for model in ("GPT-6-ASTRA", "gpt-6-Astra", "Astra", "openai/gpt-6-astra",
                      "gpt-6-astra[1m]", "vendor/GPT-6-ASTRA-FAST[1m]"):
            with self.subTest(model=model):
                self.assertTrue(models.is_premium(model))
        for model in ("OPENAI/GPT-8-SOL[1m]", "vendor/SONNET[1m]", [], {}):
            with self.subTest(model=model):
                self.assertFalse(models.is_premium(model))

    def test_premium_normalizes_spacing_colons_parentheses_and_embedded_names(self):
        for model in ("gpt-6-astra [1m]", "openai:gpt-6-astra", "gpt-6-astra(1m)",
                      "gpt-6-sol-astra", "vendor:OPENAI/GPT-6-SOL-ASTRA (1m) [fast]",
                      " vendor/anthropic:CLAUDE-FABLE (1m) "):
            with self.subTest(model=model):
                self.assertTrue(models.is_premium(model))
        for model in (" openai:GPT-6.1-SOL [1m] ", "vendor/SONNET (1m)",
                      "astra-provider:gpt-6-sol", "fable-provider/grok-5"):
            with self.subTest(model=model):
                self.assertFalse(models.is_premium(model))

    def test_grok_normalizes_matching_and_preserves_original_ids(self):
        ids = ["grok-4.7", "grok-4.10", "GROK-5", "xai/grok-4.11"]
        self.assertEqual(models.resolve_grok(ids), "GROK-5")
        self.assertEqual(models.grok_candidates(ids),
                         ["GROK-5", "xai/grok-4.11", "grok-4.10", "grok-4.7"])
        for slug in ("XAI:GROK-5", "xai/grok-5", " GROK-5 [1m] ", "grok-5(1m)"):
            with self.subTest(slug=slug):
                self.assertEqual(models.resolve_grok(["grok-4.10", slug,
                                                      "XAI:GROK-9-FAST"]), slug)

    def test_cli_uppercase_lines_preserve_catalog_slugs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            slug = "OpenAI:GPT-8-Sol (1m)"
            path.write_text(json.dumps({"models": [entry("gpt-6.1-sol"), entry(slug)]}))
            code, raw = self.cli("--line", "SOL", "--catalog", str(path), "--json")
            report = json.loads(raw)
            self.assertEqual(code, 0)
            self.assertEqual(report["line"], "sol")
            self.assertEqual(report["model"], slug)
            self.assertEqual(report["candidates"][0]["id"], slug)
            self.assertFalse(report["premium"])
        code, raw = self.cli("--line", "GROK", "--ids", "grok-4.10,xai:GROK-5", "--json")
        report = json.loads(raw)
        self.assertEqual(code, 0)
        self.assertEqual(report["line"], "grok")
        self.assertEqual(report["model"], "xai:GROK-5")

    def test_cli_lines_strip_whitespace_before_resolution_and_provider_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(catalog()))
            for line, expected, premium in ((" Sol ", "gpt-6.1-sol", False),
                                            ("\tLUNA\n", "gpt-6-luna", False),
                                            (" Astra ", "gpt-6-astra", True)):
                with self.subTest(line=line):
                    code, raw = self.cli("--line", line, "--catalog", str(path), "--json")
                    report = json.loads(raw)
                    self.assertEqual(code, 0)
                    self.assertEqual(report["line"], line.strip().lower())
                    self.assertEqual(report["model"], expected)
                    self.assertEqual(report["status"], "resolved")
                    self.assertEqual(report["premium"], premium)
        with patch.object(models, "read_catalog", side_effect=AssertionError("must not read Codex")):
            code, raw = self.cli("--line", " GroK ", "--ids", "grok-4.10,xai:GROK-5", "--json")
            report = json.loads(raw)
            self.assertEqual(code, 0)
            self.assertEqual(report["line"], "grok")
            self.assertEqual(report["model"], "xai:GROK-5")

    def test_catalog_matching_normalizes_but_preserves_dispatch_ids(self):
        for slug in ("GPT-8-SOL", "gpt-8-Sol", "openai/gpt-8-sol",
                     "gpt-8-sol[1m]", "vendor/GPT-8-SOL[1m]",
                     " openai:GPT-8-SOL [1m] ", "gpt-8-sol(1m)"):
            with self.subTest(slug=slug), tempfile.TemporaryDirectory() as directory:
                data = {"models": [entry("gpt-6.1-sol"), entry(slug, "Successor")]}
                self.assertEqual(models.resolve_codex(data, "sol"), slug)
                path = Path(directory) / "catalog.json"
                path.write_text(json.dumps(data))
                code, raw = self.cli("--line", "sol", "--catalog", str(path), "--json")
                report = json.loads(raw)
                self.assertEqual(code, 0)
                self.assertEqual(report["model"], slug)
                self.assertEqual(report["candidates"][0], {"id": slug, "description": "Successor"})
                self.assertFalse(report["premium"])
                self.assertEqual(report["unknown_lines"], [])

    def test_catalog_normalized_astra_ids_remain_premium(self):
        for slug in ("GPT-6-ASTRA", "gpt-6-Astra", "openai/gpt-6-astra",
                     "gpt-6-astra[1m]"):
            with self.subTest(slug=slug), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "catalog.json"
                path.write_text(json.dumps({"models": [entry(slug)]}))
                code, raw = self.cli("--line", "astra", "--catalog", str(path), "--json")
                report = json.loads(raw)
                self.assertEqual(code, 0)
                self.assertEqual(report["model"], slug)
                self.assertTrue(report["premium"])
                _, raw = self.cli("--line", "astra", "--catalog", str(path))
                self.assertIn("premium; double approval required", raw)

    def test_unknown_premium_variants_never_recommend_recon(self):
        for slug in ("gpt-6-astra-fast", "vendor/GPT-6-ASTRA-FAST[1m]",
                     "gpt-7-astrafuture"):
            with self.subTest(slug=slug), tempfile.TemporaryDirectory() as directory:
                data = {"models": [entry("gpt-6.1-sol"), entry(slug)]}
                unknown = models.unknown_lines(data)[0]
                self.assertTrue(unknown["premium"])
                self.assertEqual(unknown["status"], "premium; double approval required")
                self.assertEqual(unknown["models"], [slug])
                self.assertIsNone(models.resolve_codex(data, unknown["line"]))
                path = Path(directory) / "catalog.json"
                path.write_text(json.dumps(data))
                for line in ("sol", unknown["line"]):
                    code, raw = self.cli("--line", line, "--catalog", str(path), "--json")
                    report = json.loads(raw)
                    self.assertEqual(code, 0)
                    self.assertTrue(report["unknown_lines"][0]["premium"])
                    self.assertNotIn("recon first", raw)
                    if line != "sol":
                        self.assertTrue(report["premium"])
                        self.assertEqual(report["status"], "premium; double approval required")
                    _, raw = self.cli("--line", line, "--catalog", str(path))
                    self.assertIn("premium; double approval required", raw)
                    self.assertNotIn("recon first", raw)

    def cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = models.main(list(args))
        return code, output.getvalue()

    def test_cli_catalog_override_and_default_codex_home(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "models_cache.json"
            path.write_text(json.dumps(catalog()))
            code, raw = self.cli("--line", "sol", "--catalog", str(path), "--json")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(raw)["model"], "gpt-6.1-sol")
            with patch.dict(os.environ, {"CODEX_HOME": directory}):
                code, raw = self.cli("--line", "astra", "--json")
                self.assertEqual(code, 0)
                self.assertTrue(json.loads(raw)["premium"])
                self.assertEqual(models.read_catalog(), catalog())
            with patch.dict(os.environ, {"HOME": directory, "CODEX_HOME": ""}):
                (Path(directory) / ".codex").mkdir()
                (Path(directory) / ".codex/models_cache.json").write_text(path.read_text())
                self.assertEqual(models.read_catalog(), catalog())

    def test_cli_errors_and_unknown_line_are_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            for content in (None, "", "not JSON", "[]", '{"models": null}'):
                if content is not None:
                    path.write_text(content)
                code, raw = self.cli("--line", "sol", "--catalog", str(path), "--json")
                self.assertEqual(code, 2)
                self.assertIsNone(json.loads(raw)["model"])
            path.write_text('{"models": []}')
            code, raw = self.cli("--line", "sol", "--catalog", str(path), "--json")
            self.assertEqual(code, 0)
            self.assertIsNone(json.loads(raw)["model"])
            path.write_text(json.dumps({"models": [entry("gpt-7-nova")]}))
            code, raw = self.cli("--line", "nova", "--catalog", str(path), "--json")
            self.assertEqual(code, 0)
            self.assertIsNone(json.loads(raw)["model"])
            self.assertEqual(json.loads(raw)["status"], "unknown line — recon first")
            _, raw = self.cli("--line", "sol", "--catalog", str(path))
            self.assertIn("nova: unknown line — recon first", raw)

    def test_cli_grok_provider_and_line_resolve_without_codex_catalog(self):
        ids = "grok-4.9,grok-4.10, grok-4.11-build-fast,grok-9-fast"
        for args in (("--provider", "grok"), ("--line", "grok"),
                     ("--provider", "grok", "--line", "grok")):
            with self.subTest(args=args), patch.object(
                    models, "read_catalog", side_effect=AssertionError("must not read Codex")):
                code, raw = self.cli(*args, "--ids", ids, "--json")
                report = json.loads(raw)
                self.assertEqual(code, 0)
                self.assertEqual(report["model"], "grok-4.10")
                self.assertEqual(report["status"], "resolved")
                self.assertFalse(report["premium"])
                self.assertEqual([candidate["id"] for candidate in report["candidates"]],
                                 ["grok-4.10", "grok-4.9"])
        code, raw = self.cli("--line", "grok", "--ids", ids)
        self.assertEqual(code, 0)
        self.assertEqual(raw.strip(), "grok-4.10")

    def test_cli_grok_absent_and_invalid_inputs(self):
        for ids in ("", "grok-4.7-fast,invalid"):
            with self.subTest(ids=ids):
                code, raw = self.cli("--provider", "grok", "--ids", ids, "--json")
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(raw)["status"], "absent")
                self.assertIsNone(json.loads(raw)["model"])
        for args in (("--line", "grok"), ("--provider", "grok", "--line", "sol"),
                     ("--provider", "codex", "--line", "sol", "--ids", "grok-4.7")):
            with self.subTest(args=args):
                code, raw = self.cli(*args, "--json")
                self.assertEqual(code, 2)
                self.assertEqual(json.loads(raw)["status"], "error")
                self.assertNotIn("unknown line", raw)

    def test_cli_candidates_preserve_description_and_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(catalog()))
            code, raw = self.cli("--line", "sol", "--catalog", str(path), "--json")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(raw)["candidates"], [
                {"id": "gpt-6.1-sol", "description": "Latest model"},
                {"id": "gpt-6-sol", "description": "Previous generation"},
                {"id": "gpt-5.6-sol", "description": "Older"}])

    def test_terra_known_but_never_routed_or_flagged_for_new_line_recon(self):
        data = catalog()
        data["models"].append(entry("gpt-5.6-terra", "Older balanced model"))
        self.assertIn("terra", models.CODEX_LINES)
        self.assertEqual(models.unknown_lines(data), [])
        self.assertEqual(models.codex_candidates(data, "terra"), [])
        self.assertIsNone(models.resolve_codex(data, "terra"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(data))
            code, raw = self.cli("--line", "sol", "--catalog", str(path))
            self.assertEqual(code, 0)
            self.assertIn("terra: known/superseded-or-unused (gpt-5.6-terra)", raw)
            self.assertNotIn("unknown line", raw)
            code, raw = self.cli("--line", "terra", "--catalog", str(path), "--json")
            report = json.loads(raw)
            self.assertEqual(code, 0)
            self.assertIsNone(report["model"])
            self.assertEqual(report["status"], "known/superseded-or-unused")
            self.assertEqual(report["unused_lines"], [{"line": "terra",
                             "status": "known/superseded-or-unused", "models": ["gpt-5.6-terra"]}])


if __name__ == "__main__":
    unittest.main()
