"""Shared helpers for the structural tests (standard library only).

Each test copies the canonical fixture to a temporary directory, applies one
small mutation in code, runs the validator in-process, and asserts the exact
set of (code, level) pairs. The fixtures on disk are never modified.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True  # tests must not leave __pycache__ files in the tree

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.karaz_validate import validate  # noqa: E402
from tools.karaz_validate.__main__ import main  # noqa: E402
from tools.karaz_validate.report import ERROR, INFO, WARNING  # noqa: E402,F401

FIXTURES = HERE / "fixtures"
VALID = FIXTURES / "valid"
BASELINE = FIXTURES / "baseline-1.0"

CORE = "core/example-core-skill"
SPEC = "specialist-skills/example-specialist-skill"
REGISTRY = "registry/skills.yaml"
COMPAT = "registry/compatibility.yaml"
CORE_MD = f"{CORE}/SKILL.md"
SPEC_MD = f"{SPEC}/SKILL.md"


def file_hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def run_cli(*argv) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as exc:  # argparse usage errors
            code = exc.code
    return code, out.getvalue(), err.getvalue()


class TreeCase(unittest.TestCase):
    """A fresh writable copy of the canonical valid fixture for every test."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "repo"
        shutil.copytree(VALID, self.root)

    # -- editing helpers ----------------------------------------------------
    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="")

    def edit(self, rel: str, old: str, new: str) -> None:
        text = self.read(rel)
        self.assertIn(old, text, f"mutation target not found in {rel}")
        self.write(rel, text.replace(old, new, 1))

    def delete(self, rel: str) -> None:
        path = self.root / rel
        shutil.rmtree(path) if path.is_dir() else path.unlink()

    # -- running and asserting ------------------------------------------------
    def check(self):
        return validate(self.root)

    @staticmethod
    def pairs(report) -> set[tuple[str, str]]:
        return {(d.code, d.level) for d in report.diagnostics}

    def assertPairs(self, report, expected) -> None:
        self.assertEqual(self.pairs(report), set(expected), "\n" + report.render_text())

    def find(self, report, code: str, level: str, *, file: str | None = None, text: str | None = None):
        """Return the first diagnostic with this code and level, checking that it is actionable."""
        for d in report.diagnostics:
            if d.code == code and d.level == level and (file is None or d.file == file) \
                    and (text is None or text in d.message or text in d.hint):
                self.assertTrue(d.file and d.location and d.message and d.hint,
                                "a diagnostic must name the file, the location, the problem and the fix")
                return d
        self.fail(f"no {level} {code} (file={file}, text={text}) in:\n{report.render_text()}")

    def assertErrorExit(self, report) -> None:
        self.assertEqual(report.exit_code, 1)
        self.assertEqual(run_cli("--root", str(self.root))[0], 1)

    def assertWarningOnly(self, report, code: str, level: str = WARNING, **kw) -> None:
        """Exactly one diagnostic kind, and it never blocks: exit 0 in the API and on the command line."""
        self.assertPairs(report, {(code, level)})
        self.find(report, code, level, **kw)
        self.assertEqual(report.exit_code, 0)
        self.assertEqual(run_cli("--root", str(self.root))[0], 0)
