"""Backward-compatibility test against the pinned baseline (schema 1.x).

The baseline is the real KARAZ records, copied once into fixtures/baseline-1.0/.
This test is local (reads only that folder), deterministic, network-independent
(sockets and subprocesses are disabled), and mutation-free (the folder's hashes
and file list are verified before and after the run). It uses no Git.
It never reads the live repository records, so a legitimate edit to those
records cannot break it; CI validates the live tree separately.
"""

import contextlib
import hashlib
import os
import re
import tempfile
import unittest
from unittest import mock

from support import BASELINE, ERROR, INFO, WARNING, file_hashes, validate

EXPECTED_INFO = {
    ("KZ-C007", INFO, "$.platforms.chatgpt"),
    ("KZ-C007", INFO, "$.platforms.gemini"),
    ("KZ-C007", INFO, "$.platforms.generic"),
    ("KZ-C007", INFO, "$.platforms.grok"),
}


def recorded_hashes() -> dict[str, str]:
    rows = re.findall(r"^\| `([^`]+)` \|[^|]*\| `([0-9a-f]{64})` \|$",
                      (BASELINE / "BASELINE.md").read_text(encoding="utf-8"), re.M)
    return dict(rows)


def refuse(*args, **kwargs):
    raise AssertionError("the baseline test must not use the network or start processes")


class BaselineCompatibility(unittest.TestCase):
    def test_baseline_matches_its_recorded_hashes(self):
        actual = file_hashes(BASELINE)
        actual.pop("BASELINE.md")
        self.assertEqual(actual, recorded_hashes(), "the baseline was edited; it changes only at a schema MAJOR bump")

    def test_baseline_files_are_the_real_record_shapes(self):
        files = file_hashes(BASELINE)
        for rel in ("registry/skills.yaml", "registry/compatibility.yaml", "core/quality-guardian/SKILL.md"):
            self.assertIn(rel, files)
        self.assertEqual(hashlib.sha256(b"").hexdigest(), files["core/quality-guardian/tests/test-cases.md"])

    def test_current_validator_accepts_the_baseline_without_errors_or_warnings(self):
        before = file_hashes(BASELINE)
        with tempfile.TemporaryDirectory() as workdir, contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch("socket.socket", refuse))
            stack.enter_context(mock.patch("socket.create_connection", refuse))
            stack.enter_context(mock.patch("socket.getaddrinfo", refuse))
            stack.enter_context(mock.patch("subprocess.Popen", refuse))
            previous = os.getcwd()
            os.chdir(workdir)  # a fresh directory that is not a Git repository
            stack.callback(os.chdir, previous)
            self.assertFalse(os.path.exists(os.path.join(workdir, ".git")))
            report = validate(str(BASELINE.resolve()))  # absolute path
        self.assertEqual(report.count(ERROR), 0, report.render_text())
        self.assertEqual(report.count(WARNING), 0, report.render_text())
        self.assertEqual({(d.code, d.level, d.location) for d in report.diagnostics}, EXPECTED_INFO)
        self.assertEqual(report.exit_code, 0)
        self.assertEqual(sorted(report.applied),
                         [("compatibility", "1.0"), ("registry", "1.0"), ("skill-frontmatter", "1.0")])
        self.assertEqual(report.skipped, {})
        self.assertEqual(report.later_minor, [])
        self.assertEqual(before, file_hashes(BASELINE), "the validator changed the baseline folder")


if __name__ == "__main__":
    unittest.main()
