"""Safe loading of repository files.

Every file is treated as untrusted input: YAML is read with a safe loader that
also rejects duplicate keys, nothing is executed, and nothing is written.

File-size limit: no file is read if it is larger than MAX_FILE_BYTES (1 MiB).
Such a file, like an unreadable or invalid one, is reported as KZ-L001.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .report import ERROR, Report

MAX_FILE_BYTES = 1024 * 1024  # 1 MiB

TYPE_DIRS = ("core", "meta-skills", "specialist-skills")  # where skills are discovered


class StrictLoader(yaml.SafeLoader):
    """yaml.SafeLoader that rejects duplicate mapping keys."""


def _construct_mapping(loader: StrictLoader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=True)
        try:
            hash(key)
        except TypeError:
            raise yaml.constructor.ConstructorError(None, None, "unhashable mapping key", key_node.start_mark)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", key_node.start_mark)
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


@dataclass
class SkillDoc:
    dir: str  # repository-relative skill directory, e.g. "core/quality-guardian"
    file: str  # repository-relative SKILL.md
    data: dict | None = None  # parsed frontmatter, None if unavailable
    body: str | None = None  # Markdown after the frontmatter, None if unavailable


@dataclass
class Context:
    root: Path
    registry: dict | None = None
    compat: dict | None = None
    skill_docs: dict[str, SkillDoc] = field(default_factory=dict)


def read_text(root: Path, rel: str, report: Report) -> str | None:
    """Read a UTF-8 file (a leading BOM is ignored). Report KZ-L001 on failure."""
    path = root / rel
    try:
        if not path.is_file():
            report.add("KZ-L001", ERROR, rel, "file", "File not found or not a regular file.",
                       "Create the file or correct the path.")
            return None
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            report.add("KZ-L001", ERROR, rel, "file",
                       f"File is {size} bytes, over the {MAX_FILE_BYTES}-byte (1 MiB) limit.",
                       "Shorten or split the file; the validator reads at most 1 MiB per file.")
            return None
        return path.read_bytes().decode("utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        report.add("KZ-L001", ERROR, rel, "file", f"File cannot be read as UTF-8 text: {exc.__class__.__name__}.",
                   "Make the file readable and save it as UTF-8.")
        return None


def load_yaml_text(text: str, rel: str, report: Report):
    """Return (ok, data). Report KZ-L001 for invalid YAML or a duplicate key."""
    try:
        return True, yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f"line {mark.line + 1}" if mark is not None else "file"
        problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        report.add("KZ-L001", ERROR, rel, where, f"Invalid YAML: {problem}.",
                   "Fix the YAML syntax and remove duplicate keys.")
        return False, None


def load_yaml_file(root: Path, rel: str, report: Report):
    text = read_text(root, rel, report)
    if text is None:
        return False, None
    return load_yaml_text(text, rel, report)


def extract_frontmatter(text: str):
    """Return (frontmatter_text, body) or None if there is no terminated frontmatter block."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1:])
    return None


def check_path(root: Path, rel: str) -> str:
    """Resolve a repository-relative path. Returns 'ok', 'missing', 'outside' or 'case'.

    'case' means an entry exists whose name differs only in letter case, which
    resolves on some file systems but not on Linux.
    """
    rel = rel.strip()
    if not rel or rel.startswith(("/", "\\")) or "\\" in rel or re.match(r"^[A-Za-z]:", rel):
        return "outside"
    parts = [p for p in rel.split("/") if p not in ("", ".")]
    if ".." in parts:
        return "outside"
    current = root
    for part in parts:
        try:
            names = os.listdir(current)
        except OSError:
            return "missing"
        if part not in names:
            return "case" if any(n.lower() == part.lower() for n in names) else "missing"
        current = current / part
    try:
        current.resolve().relative_to(root.resolve())
    except ValueError:
        return "outside"
    return "ok"


def norm_path(value: str) -> str:
    """Normalize a registry path for comparison: no trailing slash."""
    return value.strip().rstrip("/")


def discover_skill_dirs(root: Path) -> list[str]:
    """Directories directly under core/, meta-skills/ or specialist-skills/ that contain SKILL.md."""
    found = []
    for type_dir in TYPE_DIRS:
        base = root / type_dir
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir(), key=lambda p: p.name):
            if child.is_dir() and (child / "SKILL.md").is_file():
                found.append(f"{type_dir}/{child.name}")
    return found


def registry_entries(ctx: Context) -> list[tuple[int, dict]]:
    skills = ctx.registry.get("skills") if ctx.registry else None
    if not isinstance(skills, list):
        return []
    return [(i, e) for i, e in enumerate(skills) if isinstance(e, dict)]


def text_field(entry: dict, key: str) -> str | None:
    value = entry.get(key)
    return value if isinstance(value, str) else None
