"""Filesystem checks: KZ-R007, KZ-R010, KZ-F002, KZ-F003 and KZ-I001.

Skills are discovered only under core/, meta-skills/ and specialist-skills/.
The top-level tests/ directory is never scanned for skills or links.
"""

from __future__ import annotations

import os
import re

from . import loader
from .loader import Context, registry_entries, text_field
from .report import ERROR, WARNING, Report

REGISTRY = "registry/skills.yaml"
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def kz_r007(ctx: Context, report: Report) -> None:
    for i, entry in registry_entries(ctx):
        for key in ("path", "documentation"):
            value = text_field(entry, key)
            if value is None:
                continue
            status = loader.check_path(ctx.root, value)
            if status == "ok":
                continue
            reason = {
                "missing": "does not exist in this repository",
                "outside": "points outside this repository",
                "case": "differs in letter case from the file on disk (paths are case-sensitive on Linux)",
            }[status]
            report.add("KZ-R007", ERROR, REGISTRY, f"$.skills[{i}].{key}", f"Registered {key} '{value}' {reason}.",
                       "Correct the path so that it matches the file or directory exactly.")


def kz_r010(ctx: Context, report: Report) -> None:
    registered = {loader.norm_path(p) for _, e in registry_entries(ctx) if (p := text_field(e, "path")) is not None}
    for skill_dir, doc in sorted(ctx.skill_docs.items()):
        if skill_dir not in registered:
            report.add("KZ-R010", ERROR, doc.file, "file",
                       f"Skill directory '{skill_dir}/' is not registered in {REGISTRY}.",
                       "Add a registry entry and a compatibility record, or move the directory out of the skill tree.")


def kz_f002(ctx: Context, report: Report) -> None:
    for skill_dir, doc in sorted(ctx.skill_docs.items()):
        skill_id = doc.data.get("id") if doc.data else None
        if isinstance(skill_id, str) and skill_dir.rsplit("/", 1)[-1] != skill_id:
            report.add("KZ-F002", ERROR, doc.file, "$.id",
                       f"Directory name '{skill_dir.rsplit('/', 1)[-1]}' differs from the skill id '{skill_id}'.",
                       "Rename the directory or the id so that they are equal.")


def kz_f003(ctx: Context, report: Report) -> None:
    for _, doc in sorted(ctx.skill_docs.items()):
        if doc.body is not None and not doc.body.strip():
            report.add("KZ-F003", WARNING, doc.file, "body", "SKILL.md has no instructions after the frontmatter.",
                       "Write the skill's instructions below the closing '---'.")


def _markdown_files(root):
    for current, dirs, files in os.walk(root):
        rel_dir = os.path.relpath(current, root)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")
                         and not (rel_dir == "." and d == "tests"))
        for name in sorted(files):
            if name.lower().endswith(".md"):
                yield os.path.normpath(os.path.join(rel_dir, name)).replace(os.sep, "/")


def kz_i001(ctx: Context, report: Report) -> None:
    for rel in _markdown_files(ctx.root):
        text = loader.read_text(ctx.root, rel, report)
        if text is None:
            continue
        in_fence = False
        for number, line in enumerate(text.splitlines(), start=1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line = re.sub(r"`[^`]*`", "", line)
            for match in LINK_RE.finditer(line):
                target = match.group(1)
                if target.startswith(("#", "//")) or SCHEME_RE.match(target):
                    continue
                target = re.split(r"[#?]", target, maxsplit=1)[0]
                if not target:
                    continue
                if target.startswith("/"):
                    resolved = target.lstrip("/")
                else:
                    resolved = os.path.normpath(os.path.join(os.path.dirname(rel), target)).replace(os.sep, "/")
                if loader.check_path(ctx.root, resolved) != "ok":
                    report.add("KZ-I001", WARNING, rel, f"line {number}",
                               f"Relative link '{match.group(1)}' does not resolve to a file or directory here.",
                               "Fix the link target or remove the link.")


CHECKS = [
    ("KZ-R007", kz_r007, {"registry"}),
    ("KZ-R010", kz_r010, {"registry"}),
    ("KZ-F002", kz_f002, set()),
    ("KZ-F003", kz_f003, set()),
    ("KZ-I001", kz_i001, set()),
]
