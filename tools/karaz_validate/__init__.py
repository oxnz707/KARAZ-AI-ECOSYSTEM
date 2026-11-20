"""KARAZ structural validator.

Read-only: it never writes files, never uses the network, never executes
repository content, and never changes a skill's status. A passing run is a
necessary condition for validation, not evidence that a skill is validated.

Run from the repository root:  python -m tools.karaz_validate [--root PATH] [--format text|json]
"""

from __future__ import annotations

from pathlib import Path

from . import compat_checks, fs_checks, loader, registry_checks, schema_checks
from .loader import Context
from .report import Report

REGISTRY_FILE = "registry/skills.yaml"
COMPAT_FILE = "registry/compatibility.yaml"


class RootError(Exception):
    """The validator cannot run: the root is not a directory."""


def _check_modules():
    return (registry_checks, fs_checks, compat_checks)


def validate(root) -> Report:
    root = Path(root)
    if not root.is_dir():
        raise RootError(f"root is not a directory: {root}")
    root = root.resolve()
    report = Report()
    schemas = schema_checks.Schemas()

    ctx = Context(root=root)
    ctx.registry = schema_checks.load_registry_like(root, schemas, REGISTRY_FILE, "registry", report)
    ctx.compat = schema_checks.load_registry_like(root, schemas, COMPAT_FILE, "compatibility", report)
    for skill_dir in loader.discover_skill_dirs(root):
        ctx.skill_docs[skill_dir] = schema_checks.load_skill(root, schemas, skill_dir, report)

    available = {"registry": ctx.registry is not None, "compat": ctx.compat is not None}
    files = {"registry": REGISTRY_FILE, "compat": COMPAT_FILE}
    for module in _check_modules():
        for code, check, needs in module.CHECKS:
            missing = sorted(n for n in needs if not available[n])
            if missing:
                report.skip(code, " and ".join(f"{files[n]} was not loaded or validated" for n in missing))
                continue
            check(ctx, report)
    return report
