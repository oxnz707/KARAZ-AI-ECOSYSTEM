"""Diagnostics, text and JSON output, and exit codes.

Levels: ERROR makes the run exit 1. WARNING and INFO never do.
Exit 2 is used by the command line when the validator itself cannot run.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

ERROR = "ERROR"
WARNING = "WARNING"
INFO = "INFO"

PASS_SENTENCE = (
    "Structural validation passed. "
    "This does not establish that any skill is validated or released."
)
FAIL_SENTENCE = "Structural validation failed."


@dataclass(frozen=True)
class Diagnostic:
    code: str
    level: str
    file: str
    location: str
    message: str
    hint: str = ""


class Report:
    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []
        self.applied: set[tuple[str, str]] = set()  # (schema name, version applied)
        self.later_minor: list[str] = []  # files checked under a later minor version
        self.skipped: dict[str, list[str]] = {}  # reason -> check codes

    def add(self, code: str, level: str, file: str, location: str, message: str, hint: str = "") -> None:
        self.diagnostics.append(Diagnostic(code, level, file, location, message, hint))

    def skip(self, code: str, reason: str) -> None:
        self.skipped.setdefault(reason, []).append(code)

    def count(self, level: str) -> int:
        return sum(1 for d in self.diagnostics if d.level == level)

    @property
    def exit_code(self) -> int:
        return 1 if self.count(ERROR) else 0

    def sorted(self) -> list[Diagnostic]:
        return sorted(self.diagnostics, key=lambda d: (d.file, d.location, d.code, d.level, d.message))

    def _summary(self) -> dict:
        return {
            "errors": self.count(ERROR),
            "warnings": self.count(WARNING),
            "info": self.count(INFO),
            "schema_versions_applied": sorted(f"{n} {v}" for n, v in self.applied),
            "later_minor_files": sorted(set(self.later_minor)),
            "skipped": {r: sorted(set(c)) for r, c in sorted(self.skipped.items())},
            "passed": self.exit_code == 0,
        }

    def render_text(self) -> str:
        lines: list[str] = []
        for d in self.sorted():
            lines.append(f"{d.level} {d.code} {d.file}: {d.location}: {d.message}")
            if d.hint:
                lines.append(f"    Fix: {d.hint}")
        s = self._summary()
        if lines:
            lines.append("")
        lines.append(f"{s['errors']} error(s), {s['warnings']} warning(s), {s['info']} info.")
        lines.append("Schema versions applied: " + (", ".join(s["schema_versions_applied"]) or "none") + ".")
        for reason, codes in s["skipped"].items():
            lines.append(f"Skipped checks ({reason}): {', '.join(codes)}.")
        if s["later_minor_files"]:
            lines.append(
                "Checked under a later minor schema version than this validator supports "
                f"({', '.join(s['later_minor_files'])}): rules newer than the validator were not applied."
            )
        lines.append(PASS_SENTENCE if self.exit_code == 0 else FAIL_SENTENCE)
        return "\n".join(lines) + "\n"

    def render_json(self) -> str:
        payload = {
            "summary": self._summary(),
            "diagnostics": [d.__dict__ for d in self.sorted()],
            "result": PASS_SENTENCE if self.exit_code == 0 else FAIL_SENTENCE,
        }
        return json.dumps(payload, indent=2) + "\n"
