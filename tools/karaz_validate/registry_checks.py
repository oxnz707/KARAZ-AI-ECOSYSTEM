"""Registry checks: KZ-R001 to KZ-R006, KZ-R008, KZ-R009, KZ-F001, and the evidence gates KZ-G001 and KZ-G002.

Each check is a function (ctx, report) listed in CHECKS with the inputs it needs.
Checks tolerate malformed data: shape errors are reported by the schema checks.
"""

from __future__ import annotations

from . import loader
from .loader import Context, registry_entries, text_field
from .report import ERROR, WARNING, Report

REGISTRY = "registry/skills.yaml"
TYPE_TO_DIR = {"core": "core", "meta": "meta-skills", "specialist": "specialist-skills"}


def _loc(index: int, key: str | None = None) -> str:
    return f"$.skills[{index}]" + (f".{key}" if key else "")


def _ids(ctx: Context) -> dict[str, dict]:
    ids: dict[str, dict] = {}
    for _, entry in registry_entries(ctx):
        sid = text_field(entry, "id")
        if sid is not None:
            ids.setdefault(sid, entry)
    return ids


def kz_r001(ctx: Context, report: Report) -> None:
    seen: set[str] = set()
    for i, entry in registry_entries(ctx):
        sid = text_field(entry, "id")
        if sid is None:
            continue
        if sid in seen:
            report.add("KZ-R001", ERROR, REGISTRY, _loc(i, "id"), f"Duplicate skill id '{sid}'.",
                       "Give every skill a unique id, or remove the duplicate entry.")
        seen.add(sid)


def _vocabulary(ctx: Context, key: str) -> list | None:
    values = ctx.registry.get(key) if ctx.registry else None
    return values if isinstance(values, list) else None


def kz_r002(ctx: Context, report: Report) -> None:
    allowed = _vocabulary(ctx, "skill_types")
    if allowed is None:
        return
    for i, entry in registry_entries(ctx):
        value = text_field(entry, "type")
        if value is not None and value not in allowed:
            report.add("KZ-R002", ERROR, REGISTRY, _loc(i, "type"),
                       f"Type '{value}' is not listed in skill_types ({', '.join(map(str, allowed))}).",
                       "Use a listed type, or add the type to skill_types in a deliberate change.")


def kz_r003(ctx: Context, report: Report) -> None:
    allowed = _vocabulary(ctx, "lifecycle_statuses")
    if allowed is None:
        return
    for i, entry in registry_entries(ctx):
        value = text_field(entry, "status")
        if value is not None and value not in allowed:
            report.add("KZ-R003", ERROR, REGISTRY, _loc(i, "status"),
                       f"Status '{value}' is not listed in lifecycle_statuses ({', '.join(map(str, allowed))}).",
                       "Use a listed lifecycle status.")


def _dependencies(entry: dict) -> list[str]:
    deps = entry.get("dependencies")
    return [d for d in deps if isinstance(d, str)] if isinstance(deps, list) else []


def kz_r004(ctx: Context, report: Report) -> None:
    ids = _ids(ctx)
    for i, entry in registry_entries(ctx):
        for dep in _dependencies(entry):
            if dep not in ids:
                report.add("KZ-R004", ERROR, REGISTRY, _loc(i, "dependencies"),
                           f"Dependency '{dep}' is not a registered skill id.",
                           "List only ids of registered skills. Documents belong in the SKILL.md prose, not here.")


def kz_r005(ctx: Context, report: Report) -> None:
    ids = _ids(ctx)
    graph = {sid: [d for d in _dependencies(e) if d in ids] for sid, e in ids.items()}
    index = {text_field(e, "id"): i for i, e in registry_entries(ctx)}
    for sid, deps in sorted(graph.items()):
        if sid in deps:
            report.add("KZ-R005", ERROR, REGISTRY, _loc(index[sid], "dependencies"),
                       f"Skill '{sid}' depends on itself.", "Remove the self-dependency.")
    # strongly connected components of size > 1 are dependency cycles (Tarjan, iterative)
    counter = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    number: dict[str, int] = {}
    low: dict[str, int] = {}
    for root_id in sorted(graph):
        if root_id in number:
            continue
        work = [(root_id, iter(sorted(graph[root_id])))]
        number[root_id] = low[root_id] = counter
        counter += 1
        stack.append(root_id)
        on_stack.add(root_id)
        while work:
            node, children = work[-1]
            advanced = False
            for child in children:
                if child not in number:
                    number[child] = low[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(sorted(graph[child]))))
                    advanced = True
                    break
                if child in on_stack:
                    low[node] = min(low[node], number[child])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == number[node]:
                component = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                if len(component) > 1:
                    members = sorted(component)
                    report.add("KZ-R005", ERROR, REGISTRY, _loc(index[members[0]], "dependencies"),
                               "Dependency cycle: " + " -> ".join(members + [members[0]]) + ".",
                               "Break the cycle so that every skill can be adopted independently.")


def kz_r006(ctx: Context, report: Report) -> None:
    ids = _ids(ctx)
    for i, entry in registry_entries(ctx):
        if text_field(entry, "status") != "released":
            continue
        for dep in _dependencies(entry):
            dep_status = text_field(ids.get(dep, {}), "status")
            if dep in ids and dep_status != "released":
                report.add("KZ-R006", WARNING, REGISTRY, _loc(i, "dependencies"),
                           f"Released skill depends on '{dep}', whose status is '{dep_status}'.",
                           "Release the dependency first, or review whether the dependency is needed.")


def kz_r008(ctx: Context, report: Report) -> None:
    for i, entry in registry_entries(ctx):
        status = text_field(entry, "status")
        if status not in ("validated", "released"):
            continue
        validation = entry.get("validation")
        validation = validation if isinstance(validation, dict) else {}
        for key in ("tests", "results"):
            value = validation.get(key)
            if not isinstance(value, str) or not value.strip():
                report.add("KZ-R008", ERROR, REGISTRY, _loc(i, f"validation.{key}"),
                           f"Skill is '{status}' but declares no validation.{key} file.",
                           "Declare the file, or return the skill to an earlier status until evidence exists.")
            elif loader.check_path(ctx.root, value) != "ok":
                report.add("KZ-R008", ERROR, REGISTRY, _loc(i, f"validation.{key}"),
                           f"Skill is '{status}' but validation.{key} '{value}' does not exist.",
                           "Add the file, or return the skill to an earlier status until evidence exists.")


def _declared_state(entry: dict, key: str) -> str:
    validation = entry.get("validation")
    value = validation.get(key) if isinstance(validation, dict) else None
    return value if isinstance(value, str) and value.strip() else "missing"


def kz_g001(ctx: Context, report: Report) -> None:
    """EV-1: a validated or released skill declares its behavioral scenario evaluation as recorded.

    This checks the declaration only. It does not show that an evaluation was performed or reviewed.
    """
    for i, entry in registry_entries(ctx):
        status = text_field(entry, "status")
        if status not in ("validated", "released"):
            continue
        state = _declared_state(entry, "behavioral_scenario_evaluation")
        if state != "recorded":
            report.add("KZ-G001", ERROR, REGISTRY, _loc(i, "validation.behavioral_scenario_evaluation"),
                       f"Skill is '{status}' but validation.behavioral_scenario_evaluation is '{state}', not 'recorded' (EV-1).",
                       "Record a reviewed behavioral-scenario-evaluation evidence record (docs/EVIDENCE-MODEL.md) "
                       "and then declare it, or return the skill to an earlier status.")


def kz_g002(ctx: Context, report: Report) -> None:
    """EV-2: a released skill declares its repository security scan as recorded.

    This checks the declaration only. It does not check the scan's scope or that anyone reviewed it.
    """
    for i, entry in registry_entries(ctx):
        status = text_field(entry, "status")
        if status != "released":
            continue
        state = _declared_state(entry, "repository_security_scan")
        if state != "recorded":
            report.add("KZ-G002", ERROR, REGISTRY, _loc(i, "validation.repository_security_scan"),
                       f"Skill is 'released' but validation.repository_security_scan is '{state}', not 'recorded' (EV-2).",
                       "Record a reviewed, qualifying repository-security-scan evidence record (docs/EVIDENCE-MODEL.md §9) "
                       "and then declare it, or keep the skill at 'validated'.")


def kz_r009(ctx: Context, report: Report) -> None:
    for i, entry in registry_entries(ctx):
        skill_type, path = text_field(entry, "type"), text_field(entry, "path")
        if skill_type in TYPE_TO_DIR and path is not None:
            prefix = TYPE_TO_DIR[skill_type] + "/"
            if not loader.norm_path(path).startswith(prefix):
                report.add("KZ-R009", WARNING, REGISTRY, _loc(i, "path"),
                           f"Path '{path}' is not under {prefix}, the directory for type '{skill_type}'.",
                           f"Move the skill under {prefix}, or check the type.")


def kz_f001(ctx: Context, report: Report) -> None:
    for i, entry in registry_entries(ctx):
        path = text_field(entry, "path")
        doc = ctx.skill_docs.get(loader.norm_path(path)) if path is not None else None
        if doc is None or doc.data is None:
            continue
        for key, level in (("id", ERROR), ("type", ERROR), ("version", ERROR), ("status", ERROR), ("name", WARNING)):
            expected, actual = text_field(entry, key), doc.data.get(key)
            if expected is not None and isinstance(actual, str) and actual != expected:
                report.add("KZ-F001", level, doc.file, f"$.{key}",
                           f"Frontmatter {key} '{actual}' differs from the registry value '{expected}'.",
                           f"Make {doc.file} and {REGISTRY} agree; update both in the same change.")


CHECKS = [
    ("KZ-R001", kz_r001, {"registry"}),
    ("KZ-R002", kz_r002, {"registry"}),
    ("KZ-R003", kz_r003, {"registry"}),
    ("KZ-R004", kz_r004, {"registry"}),
    ("KZ-R005", kz_r005, {"registry"}),
    ("KZ-R006", kz_r006, {"registry"}),
    ("KZ-R008", kz_r008, {"registry"}),
    ("KZ-G001", kz_g001, {"registry"}),
    ("KZ-G002", kz_g002, {"registry"}),
    ("KZ-R009", kz_r009, {"registry"}),
    ("KZ-F001", kz_f001, {"registry"}),
]
