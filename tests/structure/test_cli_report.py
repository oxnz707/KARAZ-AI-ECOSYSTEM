"""Command line, exit codes, JSON output, and the read-only / no-network guarantees."""

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from support import COMPAT, CORE_MD, REGISTRY, REPO, VALID, TreeCase, file_hashes, run_cli

PACKAGE = REPO / "tools" / "karaz_validate"
FORBIDDEN_IMPORTS = {"socket", "ssl", "urllib", "http", "ftplib", "smtplib", "requests", "subprocess",
                     "shutil", "tempfile", "asyncio", "xmlrpc", "telnetlib"}
FORBIDDEN_CALLS = {"write_text", "write_bytes", "mkdir", "unlink", "touch", "rmdir", "remove", "makedirs",
                   "symlink_to", "rmtree", "system", "popen"}


class ExitCodes(TreeCase):
    def test_clean_tree_exits_zero_with_the_closing_sentence(self):
        code, out, err = run_cli("--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertIn("0 error(s), 0 warning(s), 0 info.", out)
        self.assertIn("does not establish that any skill is validated or released", out)
        self.assertEqual(err, "")

    def test_error_tree_exits_one(self):
        self.edit(REGISTRY, "- example-core-skill", "- missing-skill")
        code, out, _ = run_cli("--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("ERROR KZ-R004", out)
        self.assertIn("Structural validation failed.", out)
        self.assertNotIn("does not establish", out)

    def test_warning_only_tree_exits_zero_and_prints_the_warning(self):
        self.write("docs/guide.md", "[missing](nope.md)\n")
        code, out, _ = run_cli("--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertIn("WARNING KZ-I001 docs/guide.md", out)
        self.assertIn("    Fix: ", out)  # every diagnostic says how to fix it

    def test_info_only_tree_exits_zero(self):
        self.edit(COMPAT, 'status: "draft"', 'status: "planned"')
        self.delete("adapters/exampleplatform")
        code, out, _ = run_cli("--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertIn("INFO KZ-C007", out)

    def test_warnings_and_info_alongside_an_error_do_not_change_the_cause(self):
        self.write("docs/guide.md", "[missing](nope.md)\n")
        self.edit(REGISTRY, "- example-core-skill", "- missing-skill")
        report = self.check()
        self.assertEqual(report.count("ERROR"), 1)
        self.assertEqual(report.exit_code, 1)

    def test_validator_cannot_run_exits_two(self):
        self.assertEqual(run_cli("--root", str(self.root / "does-not-exist"))[0], 2)
        self.assertEqual(run_cli("--root", str(self.root / REGISTRY))[0], 2)  # a file, not a directory

    def test_usage_errors_exit_two_and_there_is_no_strict_option(self):
        self.assertEqual(run_cli("--format", "xml")[0], 2)
        code, _, err = run_cli("--strict")
        self.assertEqual(code, 2)
        self.assertIn("unrecognized arguments", err)

    def test_internal_failure_is_never_a_pass(self):
        with mock.patch("tools.karaz_validate.__main__.validate", side_effect=RuntimeError("boom")):
            code, out, err = run_cli("--root", str(self.root))
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("validator cannot run", err)

    def test_empty_directory_reports_missing_registry_files(self):
        with tempfile.TemporaryDirectory() as empty:
            code, out, _ = run_cli("--root", empty)
        self.assertEqual(code, 1)
        self.assertEqual(out.count("KZ-L001"), 2)

    def test_skipped_checks_are_listed(self):
        self.edit(REGISTRY, 'schema_version: "1.0"', 'schema_version: "2.0"')
        _, out, _ = run_cli("--root", str(self.root))
        self.assertIn("Skipped checks (registry/skills.yaml was not loaded or validated)", out)


class JsonOutput(TreeCase):
    def test_json_is_parseable_and_complete(self):
        self.edit(REGISTRY, "- example-core-skill", "- missing-skill")
        self.write("docs/guide.md", "[missing](nope.md)\n")
        code, out, _ = run_cli("--root", str(self.root), "--format", "json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual(data["summary"]["errors"], 1)
        self.assertEqual(data["summary"]["warnings"], 1)
        self.assertFalse(data["summary"]["passed"])
        self.assertEqual({d["code"] for d in data["diagnostics"]}, {"KZ-R004", "KZ-I001"})
        for d in data["diagnostics"]:
            self.assertEqual(set(d), {"code", "level", "file", "location", "message", "hint"})
            self.assertTrue(d["message"] and d["hint"])

    def test_output_is_deterministic(self):
        self.write("docs/a.md", "[x](1.md) [y](2.md)\n")
        first = run_cli("--root", str(self.root))[1]
        self.assertEqual(first, run_cli("--root", str(self.root))[1])


class ReadOnlyAndOffline(TreeCase):
    def test_a_run_changes_nothing(self):
        self.write("docs/guide.md", "[missing](nope.md)\n")
        before = file_hashes(self.root)
        run_cli("--root", str(self.root))
        run_cli("--root", str(self.root), "--format", "json")
        self.assertEqual(before, file_hashes(self.root))

    def test_the_fixture_on_disk_is_untouched(self):
        before = file_hashes(VALID)
        run_cli("--root", str(VALID))
        self.assertEqual(before, file_hashes(VALID))

    def test_validator_source_has_no_network_process_or_write_calls(self):
        for path in sorted(PACKAGE.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    names = {(node.module or "").split(".")[0]}
                else:
                    names = set()
                self.assertFalse(names & FORBIDDEN_IMPORTS, f"{path.name} imports {names & FORBIDDEN_IMPORTS}")
                if isinstance(node, ast.Call):
                    func = node.func
                    called = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
                    self.assertNotIn(called, FORBIDDEN_CALLS, f"{path.name} calls {called}()")
                    if called == "open":
                        modes = [a.value for a in node.args[1:2] if isinstance(a, ast.Constant)]
                        modes += [k.value.value for k in node.keywords if k.arg == "mode" and isinstance(k.value, ast.Constant)]
                        for mode in modes:
                            self.assertFalse(set(str(mode)) & set("wax+"), f"{path.name} opens a file for writing")

    def test_a_run_with_networking_and_subprocesses_disabled_still_works(self):
        def refuse(*args, **kwargs):
            raise AssertionError("the validator must not use the network or start processes")
        with mock.patch("socket.socket", refuse), mock.patch("socket.create_connection", refuse), \
                mock.patch("socket.getaddrinfo", refuse), mock.patch("subprocess.Popen", refuse):
            self.assertEqual(run_cli("--root", str(self.root))[0], 0)


class ModuleEntryPoint(TreeCase):
    def test_python_dash_m_runs_and_returns_the_exit_code(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        ok = subprocess.run([sys.executable, "-m", "tools.karaz_validate", "--root", str(self.root)],
                            cwd=REPO, env=env, capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.edit(CORE_MD, "id: example-core-skill", "id: renamed-skill")
        bad = subprocess.run([sys.executable, "-m", "tools.karaz_validate", "--root", str(self.root), "--format", "json"],
                             cwd=REPO, env=env, capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertFalse(json.loads(bad.stdout)["summary"]["passed"])


if __name__ == "__main__":
    unittest.main()
