"""Schema checks: KZ-L002, KZ-S001 to KZ-S004 (and the loading step for SKILL.md).

The schemas are read from the validator's own checkout (the schemas/ directory
next to tools/), never from the repository being checked. The supported schema
version is the one named in each schema's $id.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from . import loader
from .loader import SkillDoc
from .report import ERROR, WARNING, Report

SCHEMA_FILES = {
    "skill-frontmatter": "skill-frontmatter.schema.json",
    "registry": "registry.schema.json",
    "compatibility": "compatibility.schema.json",
}
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+$")


def _fmt(version: tuple[int, int]) -> str:
    return f"{version[0]}.{version[1]}"


class Schemas:
    def __init__(self, directory: Path | None = None) -> None:
        directory = directory or Path(__file__).resolve().parents[2] / "schemas"
        self.docs = {n: json.loads((directory / f).read_text(encoding="utf-8")) for n, f in SCHEMA_FILES.items()}
        self.supported = {}
        for name, doc in self.docs.items():
            major, minor = doc["$id"].rsplit(":", 1)[1].split(".")
            self.supported[name] = (int(major), int(minor))
        self.reserved = frozenset(self.docs["skill-frontmatter"]["$defs"]["reservedKey"]["enum"])
        self.validators = {n: Draft202012Validator(d) for n, d in self.docs.items()}


def _location(path) -> str:
    out = "$"
    for part in path:
        out += f"[{part}]" if isinstance(part, int) else f".{part}"
    return out


def _walk_keys(node, path):
    if isinstance(node, dict):
        for key, value in node.items():
            yield path, key
            yield from _walk_keys(value, path + [key])
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _walk_keys(value, path + [i])


def check_document(schemas: Schemas, name: str, data, rel: str, report: Report) -> str:
    """Validate a parsed document. Returns 'full', 'later_minor' or 'skipped'."""
    supported = schemas.supported[name]
    status = "full"
    declared = data.get("schema_version") if isinstance(data, dict) else None
    if isinstance(declared, str) and VERSION_RE.match(declared):
        major, minor = (int(p) for p in declared.split("."))
        if major != supported[0]:
            report.add("KZ-S004", ERROR, rel, "$.schema_version",
                       f"Schema version {declared} has a different major version from the supported "
                       f"{_fmt(supported)}; the file was not validated.",
                       f"Use a validator that supports schema {declared}, or migrate the file to {_fmt(supported)}.")
            return "skipped"
        if minor > supported[1]:
            status = "later_minor"
            report.later_minor.append(rel)
            report.add("KZ-S004", WARNING, rel, "$.schema_version",
                       f"Schema version {declared} is later than the supported {_fmt(supported)}; "
                       "only the rules this validator knows were applied.",
                       "Update the validator, or lower schema_version if the file does not use newer fields.")
    report.applied.add((name, _fmt(supported)))

    for path, key in _walk_keys(data, []):
        if key in schemas.reserved:
            report.add("KZ-S002", ERROR, rel, _location(path + [key]),
                       f"Reserved key '{key}': identity and activation claims are not allowed.",
                       "Remove the key. KARAZ files describe capabilities, not assistant identity or installation state.")

    schema = schemas.docs[name]
    for err in sorted(schemas.validators[name].iter_errors(data),
                      key=lambda e: ([str(p) for p in e.absolute_path], e.message)):
        path = list(err.absolute_path)
        if "propertyNames" in err.schema_path and isinstance(err.instance, str) and err.instance in schemas.reserved:
            continue  # reported as KZ-S002
        if err.validator == "additionalProperties":
            props = err.schema.get("properties", {})
            patterns = err.schema.get("patternProperties", {})
            for key in err.instance:
                if key in props or key in schemas.reserved or any(re.search(p, key) for p in patterns):
                    continue
                if status == "later_minor":
                    report.add("KZ-S003", WARNING, rel, _location(path + [key]),
                               f"Unknown key '{key}' in a file declaring a later minor schema version.",
                               "Keep it if a newer validator understands it, or prefix experimental keys with x_.")
                else:
                    report.add("KZ-S001", ERROR, rel, _location(path + [key]),
                               f"Unknown key '{key}'.",
                               "Correct the key name, or prefix an extension key with x_.")
            continue
        hint = f"Correct the value to match schemas/{SCHEMA_FILES[name]}; see docs/SKILL-STANDARD.md section 13.3."
        if err.validator == "required":
            hint = "Add the missing field; see docs/SKILL-STANDARD.md section 13.3."
        elif (err.validator in ("type", "pattern") and path and path[-1] in ("version", "schema_version", "skill_version")
              and isinstance(err.instance, (int, float)) and not isinstance(err.instance, bool)):
            hint = ('Quote the value, for example version: "1.0". '
                    "YAML reads an unquoted 1.0 as a number.")
        message = err.message if len(err.message) <= 160 else err.message[:157] + "..."
        report.add("KZ-S001", ERROR, rel, _location(path), message, hint)

    if name == "skill-frontmatter" and isinstance(data, dict):
        known = set(schema["properties"])
        for key in data:
            if key not in known and not str(key).startswith("x_") and key not in schemas.reserved:
                report.add("KZ-S003", WARNING, rel, _location([key]),
                           f"Unknown frontmatter key '{key}'.",
                           "Remove the key, or prefix an experimental key with x_.")
    return status


def load_registry_like(ctx_root: Path, schemas: Schemas, rel: str, name: str, report: Report):
    """Load and schema-check registry/skills.yaml or registry/compatibility.yaml.

    Returns the parsed mapping, or None when later checks must be skipped.
    """
    ok, data = loader.load_yaml_file(ctx_root, rel, report)
    if not ok:
        return None
    status = check_document(schemas, name, data, rel, report)
    if status == "skipped" or not isinstance(data, dict):
        return None
    return data


def load_skill(root: Path, schemas: Schemas, skill_dir: str, report: Report) -> SkillDoc:
    """Load a SKILL.md: KZ-L001 (unreadable or invalid YAML), KZ-L002 (no frontmatter), then schema checks."""
    rel = f"{skill_dir}/SKILL.md"
    doc = SkillDoc(dir=skill_dir, file=rel)
    text = loader.read_text(root, rel, report)
    if text is None:
        return doc
    parts = loader.extract_frontmatter(text)
    if parts is None:
        report.add("KZ-L002", ERROR, rel, "line 1",
                   "SKILL.md must begin with a YAML frontmatter block between '---' lines, and the block must be closed.",
                   "Add '---' as the first line, the metadata fields, and a closing '---' line.")
        return doc
    front, body = parts
    ok, data = loader.load_yaml_text(front, rel, report)
    if not ok:
        return doc
    status = check_document(schemas, "skill-frontmatter", data, rel, report)
    doc.body = body
    if status != "skipped" and isinstance(data, dict):
        doc.data = data
    return doc
