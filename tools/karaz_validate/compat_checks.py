"""Compatibility checks: KZ-C001 to KZ-C008."""

from __future__ import annotations

from . import loader
from .loader import Context, registry_entries, text_field
from .report import ERROR, INFO, WARNING, Report

COMPAT = "registry/compatibility.yaml"
UNCLAIMING = ("unverified", "unsupported")
CLAIMING = ("compatible", "compatible_with_adaptation", "partially_supported")


def _records(ctx: Context) -> list[tuple[int, dict]]:
    skills = ctx.compat.get("skills") if ctx.compat else None
    return [(i, r) for i, r in enumerate(skills) if isinstance(r, dict)] if isinstance(skills, list) else []


def _platform_records(record: dict) -> list[tuple[str, dict]]:
    platforms = record.get("platforms")
    if not isinstance(platforms, dict):
        return []
    return [(str(k), v) for k, v in platforms.items() if isinstance(v, dict)]


def _declared(ctx: Context) -> dict:
    platforms = ctx.compat.get("platforms") if ctx.compat else None
    return platforms if isinstance(platforms, dict) else {}


def _registry_by_id(ctx: Context) -> dict[str, dict]:
    return {text_field(e, "id"): e for _, e in registry_entries(ctx) if text_field(e, "id") is not None}


def kz_c001(ctx: Context, report: Report) -> None:
    ids = _registry_by_id(ctx)
    for i, record in _records(ctx):
        sid = text_field(record, "skill_id")
        if sid is not None and sid not in ids:
            report.add("KZ-C001", ERROR, COMPAT, f"$.skills[{i}].skill_id",
                       f"Compatibility record names '{sid}', which is not a registered skill.",
                       "Register the skill in registry/skills.yaml, or remove the record.")


def kz_c002(ctx: Context, report: Report) -> None:
    recorded = {text_field(r, "skill_id") for _, r in _records(ctx)}
    for i, entry in registry_entries(ctx):
        sid = text_field(entry, "id")
        if sid is not None and sid not in recorded:
            report.add("KZ-C002", ERROR, "registry/skills.yaml", f"$.skills[{i}].id",
                       f"Registered skill '{sid}' has no record in {COMPAT}.",
                       "Add a record with every platform marked unverified unless evidence exists.")


def kz_c003(ctx: Context, report: Report) -> None:
    ids = _registry_by_id(ctx)
    for i, record in _records(ctx):
        sid, version = text_field(record, "skill_id"), text_field(record, "skill_version")
        entry = ids.get(sid)
        if entry is None or version is None:
            continue
        registered = text_field(entry, "version")
        if registered is None or registered == version:
            continue
        claims = any(text_field(p, "compatibility") not in UNCLAIMING + (None,) for _, p in _platform_records(record))
        report.add("KZ-C003", ERROR if claims else WARNING, COMPAT, f"$.skills[{i}].skill_version",
                   f"Record is for version {version} but the registry has {registered}"
                   + ("; a compatibility level is claimed for a version nobody verified." if claims else "."),
                   "Re-verify and update the record, or reset the claim to unverified.")


def kz_c004(ctx: Context, report: Report) -> None:
    declared = _declared(ctx)
    for i, record in _records(ctx):
        for name, _ in _platform_records(record):
            if name not in declared:
                report.add("KZ-C004", ERROR, COMPAT, f"$.skills[{i}].platforms.{name}",
                           f"Platform '{name}' is not declared under platforms.",
                           "Declare the platform, or correct the name.")


def kz_c005(ctx: Context, report: Report) -> None:
    levels = ctx.compat.get("compatibility_levels") if ctx.compat else None
    if not isinstance(levels, list):
        return
    for i, record in _records(ctx):
        for name, platform in _platform_records(record):
            level = text_field(platform, "compatibility")
            if level is not None and level not in levels:
                report.add("KZ-C005", ERROR, COMPAT, f"$.skills[{i}].platforms.{name}.compatibility",
                           f"Level '{level}' is not listed in compatibility_levels.",
                           "Use a listed level.")


def kz_c006(ctx: Context, report: Report) -> None:
    for i, record in _records(ctx):
        for name, platform in _platform_records(record):
            level = text_field(platform, "compatibility")
            evidence = text_field(platform, "evidence")
            if level in CLAIMING and (evidence is None or not evidence.strip()):
                report.add("KZ-C006", ERROR, COMPAT, f"$.skills[{i}].platforms.{name}.evidence",
                           f"Level '{level}' is claimed without evidence.",
                           "Record the observed evidence, or set the level to unverified.")


def kz_c007(ctx: Context, report: Report) -> None:
    for name, platform in sorted(_declared(ctx).items(), key=lambda kv: str(kv[0])):
        if not isinstance(platform, dict):
            continue
        status, adapter = text_field(platform, "status"), text_field(platform, "adapter")
        if adapter is None:
            continue
        where = f"$.platforms.{name}"
        directory = loader.check_path(ctx.root, adapter)
        if status == "draft":
            readme = loader.check_path(ctx.root, loader.norm_path(adapter) + "/README.md")
            if directory != "ok" or readme != "ok":
                report.add("KZ-C007", ERROR, COMPAT, where,
                           f"Adapter for '{name}' is draft but {loader.norm_path(adapter)}/ with a README.md does not exist.",
                           "Add the adapter directory and README.md (see adapters/README.md), or set the status to planned.")
        elif status in ("planned", "future") and directory != "ok":
            report.add("KZ-C007", INFO, COMPAT, where,
                       f"Adapter for '{name}' is {status}; {loader.norm_path(adapter)}/ does not exist yet.",
                       "No action needed. Create the directory only when its first real file is added.")


def kz_c008(ctx: Context, report: Report) -> None:
    base = ctx.root / "adapters"
    if not base.is_dir():
        return
    declared = {loader.norm_path(p["adapter"]) for p in _declared(ctx).values()
                if isinstance(p, dict) and isinstance(p.get("adapter"), str)}
    for child in sorted(base.iterdir(), key=lambda p: p.name):
        if child.is_dir() and f"adapters/{child.name}" not in declared:
            report.add("KZ-C008", WARNING, f"adapters/{child.name}", "directory",
                       "Adapter directory has no matching platform entry in registry/compatibility.yaml.",
                       "Declare the platform under platforms, or remove the directory.")


CHECKS = [
    ("KZ-C001", kz_c001, {"registry", "compat"}),
    ("KZ-C002", kz_c002, {"registry", "compat"}),
    ("KZ-C003", kz_c003, {"registry", "compat"}),
    ("KZ-C004", kz_c004, {"compat"}),
    ("KZ-C005", kz_c005, {"compat"}),
    ("KZ-C006", kz_c006, {"compat"}),
    ("KZ-C007", kz_c007, {"compat"}),
    ("KZ-C008", kz_c008, {"compat"}),
]
