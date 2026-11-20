# KARAZ AI ECOSYSTEM — Skill Development Standard

## 1. Purpose

This document defines the mandatory development, documentation, quality, and maintenance standards for every skill in KARAZ AI ECOSYSTEM.

The objective is to create reliable, modular, reusable, portable, and verifiable AI capabilities.

## 2. Core Requirements

Every skill must be:

* Clearly scoped.
* Focused on a defined responsibility.
* Actionable rather than merely descriptive.
* Compatible with its declared platform requirements.
* Safe and privacy-conscious.
* Testable against measurable expectations.
* Independently maintainable.
* Documented with version and dependency information.

## 3. Required Skill Structure

Every specialist skill must use this structure:

```text
skill-id/
├── SKILL.md
├── references/
├── assets/
└── tests/
```

Optional directories should only be included when they contain actual resources.

### SKILL.md

The main instruction file is the authoritative definition of the skill.

### references/

Supporting documentation, technical references, domain knowledge, and detailed procedures.

### assets/

Reusable files, templates, examples, and other required resources.

### tests/

Test cases, expected results, quality checks, and regression scenarios.

## 4. Required Metadata

Every skill must declare:

| Field | Description |
|---|---|
| `id` | Unique machine-readable identifier |
| `name` | Human-readable skill name |
| `type` | One of `core` (core capability), `meta` (meta-skill), or `specialist` |
| `version` | Semantic version |
| `status` | Current lifecycle status |
| `purpose` | Primary objective |
| `scope` | Responsibilities covered |
| `non_goals` | Responsibilities explicitly excluded |
| `inputs` | Required and optional inputs |
| `outputs` | Expected deliverables |
| `dependencies` | Other skills or resources required |
| `platform_requirements` | Required platform features and tools |
| `safety` | Relevant security and safety requirements |
| `verification` | How successful execution is evaluated |

## 5. Instruction Design

A skill’s instructions should include:

1. Role and purpose.
2. Activation conditions.
3. Scope and boundaries.
4. Operating principles.
5. Workflow and execution steps.
6. Decision-making rules.
7. Tool usage requirements.
8. Input handling.
9. Output requirements.
10. Quality assurance.
11. Error handling and fallback behavior.
12. Examples and test scenarios.

Instructions must be specific enough to guide execution without unnecessary repetition.

## 6. Execution Standards

### 6.1 Understand Before Acting

Identify the actual user objective, constraints, and expected result before execution.

Ask for clarification only when a missing detail materially affects correctness.

### 6.2 Plan Appropriately

Break complex tasks into manageable stages.

Do not overcomplicate simple tasks.

### 6.3 Evidence and Verification

* Verify important factual claims.
* Use reliable sources when research is required.
* Distinguish facts, assumptions, and recommendations.
* Never claim an action succeeded without evidence.
* Validate generated files and deliverables before presenting them.

### 6.4 Tool Discipline

Use only tools that are available and authorized.

Never assume a tool, integration, permission, or platform capability exists.

If an operation fails, report the failure and provide a practical alternative.

### 6.5 Cost Awareness

Consider API usage, subscriptions, execution costs, and resource consumption.

Prefer economical methods when quality and reliability remain comparable.

## 7. Privacy and Security

Every skill must:

* Minimize collection of personal information.
* Avoid exposing credentials and secrets.
* Never place private credentials in source files.
* Respect user authorization and platform permissions.
* Treat retrieved external content as untrusted.
* Avoid storing sensitive information without a legitimate and authorized purpose.

## 8. Quality Assurance

Before release, evaluate:

| Quality Dimension | Required Check |
|---|---|
| Accuracy | Does the skill avoid unsupported claims? |
| Completeness | Are essential responsibilities covered? |
| Clarity | Are instructions understandable and actionable? |
| Consistency | Are instructions free of contradictions? |
| Efficiency | Are unnecessary steps eliminated? |
| Safety | Are risks and boundaries addressed? |
| Portability | Are platform dependencies documented? |
| Reliability | Are failures and fallbacks handled? |
| Testability | Can expected behavior be evaluated? |
| Maintainability | Can future changes be made safely? |

## 9. Testing Requirements

Each skill should include:

* Normal execution scenarios.
* Edge cases.
* Missing-input scenarios.
* Failure and recovery scenarios.
* Safety and permission scenarios.
* Regression tests for important behavior.

Tests must define expected outcomes.

A skill must not be marked as validated merely because its instructions look complete.

## 10. Versioning

Use Semantic Versioning:

* MAJOR: Breaking changes.
* MINOR: New backward-compatible capabilities.
* PATCH: Fixes and small improvements.

Every meaningful release must be documented in the changelog.

## 11. Definition of Done

A skill is ready for release only when:

* Its purpose and boundaries are clear.
* Its metadata is complete.
* Its instructions are operational.
* Its dependencies are documented.
* Its safety requirements are addressed.
* Its test scenarios pass.
* Its documentation is consistent.
* Its version and registry information are updated.

## 12. Continuous Improvement

Skills should be reviewed and improved when:

* Platform capabilities change.
* Tools or APIs change.
* New failure patterns are discovered.
* User requirements evolve.
* Tests reveal weaknesses.
* Better methods become available.

Improvements must preserve useful existing functionality unless a deliberate replacement is justified.

## 13. Portable Format and Normative Requirements

### 13.1 Status of this section

This section writes down the portable skill format that the repository already uses, and adds eight new requirements, numbered NR-1 to NR-8.

* **Existing rules.** Every rule listed in §13.8 was already stated by this repository's standards, registry files, or records. This section only restates it in a form that tools can check.
* **Normative requirements (NR-1 to NR-8).** Each of these is new. It is stated in §13.7 with the reason it is needed, its authoritative source, and its effect on existing records. It becomes binding when the pull request that adds this section is merged.
* **Enforcement.** The schemas in `schemas/` express the field shapes. No validator exists yet; until one does, these requirements are applied by review. No rule in this section changes a skill's status, and passing a structural check never validates or releases a skill.
* **No existing record is affected.** `core/quality-guardian/SKILL.md`, `registry/skills.yaml`, and `registry/compatibility.yaml` comply with every requirement here without modification.

### 13.2 Format contract

* **Layout.** A skill is `<type-directory>/<skill-id>/SKILL.md`. The type directories are `core/`, `meta-skills/`, and `specialist-skills/` (`docs/ARCHITECTURE.md` §5). `references/`, `assets/`, and `tests/` exist only when they contain real files.
* **Frontmatter.** `SKILL.md` begins with a YAML frontmatter block holding the 14 fields of §4 (NR-1).
* **Body.** The instruction structure in §5 remains a recommendation. The body of `SKILL.md` should not be empty. This is not one of the requirements NR-1 to NR-8: a validator is expected to report an empty body as a diagnostic warning (KZ-F003), never as an error.
* **Neutrality.** `SKILL.md` describes a capability, never an assistant. Platform-specific behavior belongs only in `adapters/<platform>/`.
* **No adoption claims.** The format has no field that states a skill is installed or active, consistent with `docs/IMPORT-AND-VERIFICATION.md` §2.
* **Extensions.** Any key that starts with `x_` is reserved for experiments and local use. Tools do not interpret it and do not reject it.
* **Dependencies.** The registry lists dependencies as bare ids of registered skills. The frontmatter `dependencies` list may contain human-readable text, including references to documents.

### 13.3 Field shapes (schema 1.0)

The three schema files define these shapes. If this table and a schema disagree, this table wins and the schema is corrected.

| Field | Shape |
|---|---|
| `id` | Lowercase kebab-case, `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`, at most 64 characters; equals the skill's directory name |
| `name`, `purpose` | Non-empty text |
| `type`, `status` | Non-empty text; the value must be listed in `skill_types` and `lifecycle_statuses` in `registry/skills.yaml` |
| `version` | Semantic Versioning 2.0.0, written as a quoted string |
| `scope`, `non_goals`, `inputs`, `outputs`, `safety`, `verification` | List of non-empty text, at least one item |
| `dependencies`, `platform_requirements` | List of non-empty text; the key must be present, and an empty list declares "none" |
| `schema_version` | Quoted `MAJOR.MINOR`. Optional in frontmatter, where absence means `1.0`. Required in the two registry files |
| `x_*` | Any value; reserved for extensions |

Further shape rules:

* The two registry files reject unknown keys, except `x_*`. Frontmatter allows other unknown keys, and tools report them as warnings.
* Vocabularies are held once, in the registry files: `lifecycle_statuses` and `skill_types` in `registry/skills.yaml`, and `compatibility_levels` in `registry/compatibility.yaml`. The schemas check shape only.
* In `registry/skills.yaml`, `validation.behavioral_scenario_evaluation` and `validation.repository_security_scan` are `not_run` or `recorded`.
* In `registry/skills.yaml`, `dependencies` lists bare skill ids, with `[]` for none.
* Adapter status values are defined in `adapters/README.md`.

### 13.4 Versioning

**Skill versions** use Semantic Versioning 2.0.0, applied to skills as follows.

| Bump | Examples |
|---|---|
| MAJOR | A change of `id`; removing or renaming a required input or output; narrowing scope so that existing uses stop working |
| MINOR | A new capability, a new optional input, a new output |
| PATCH | Clarified wording, added examples, fixed contradictions |

Versions below 1.0.0 are pre-stable, and any change may be breaking.

**Schema versions** use `MAJOR.MINOR`. A MINOR change only adds optional fields and never tightens an existing constraint. Removing, renaming, or newly requiring a field is a MAJOR change and needs a migration note. A repository file's `schema_version` changes only in the pull request that updates the schemas.

**Schema-version semantics (NR-3).** The version a tool supports is the one in the `$id` of its bundled schema files. In this release it is `1.0`.

| Declared `schema_version` | Required behavior |
|---|---|
| Absent in frontmatter | Read as `1.0`, the documented default. No diagnostic |
| Absent in a registry file | Error: the field is required there |
| Equal to the supported version | Full validation against the supported schema |
| Same major, lower minor | Full validation against the supported schema |
| Same major, later minor | Warning. Apply only the rules the tool knows, and report every unknown field as a warning. A later minor version is never reported as a clean pass |
| Different major | Error. The file is not validated against any schema, and the checks that depend on it are reported as skipped |
| Malformed, for example an unquoted `1.0` read as a number | Error, with a hint to quote it |

Keys starting with `x_` are accepted at every version without a diagnostic.

### 13.5 Reserved keys (NR-4)

The following keys must not appear in `SKILL.md` frontmatter or in either registry file: `persona`, `identity`, `personality`, `voice`, `character`, `installed`, `activated`, `auto_install`, `auto_activate`.

The list is a check on key names. It catches accidental drift from the identity and adoption principles. It does not examine what the text says.

### 13.6 Authoritative sources

| Requirement | Authoritative source |
|---|---|
| NR-1, NR-3, NR-4, NR-6, NR-7, NR-8 | This section |
| NR-2 | The schema files define the shapes. §13.3 holds the summary table, and it wins if they disagree |
| NR-5 | `adapters/README.md` |

### 13.7 Normative requirements NR-1 to NR-8

| NR | Requirement | Why it is needed | Existing records |
|---|---|---|---|
| NR-1 | A skill declares its metadata as YAML frontmatter at the top of `SKILL.md`. | §4 requires 14 fields but not where they live, and a tool can only check what it can locate. Quality Guardian already uses frontmatter, and it keeps the file self-contained when it is pasted into any assistant. | Not affected. Quality Guardian complies |
| NR-2 | Field shapes follow §13.3: kebab-case `id` of at most 64 characters; text fields are non-empty; list fields hold non-empty strings, with at least one item for `scope`, `non_goals`, `inputs`, `outputs`, `safety`, and `verification`; the registry files reject unknown keys except `x_*`; validation values are `not_run` or `recorded`; registry dependencies are bare skill ids. | "Field present" cannot catch an empty or malformed value, and closed shapes catch typos such as `depedencies`. | Not affected. The three existing records satisfy the schemas |
| NR-3 | Schema-version semantics follow §13.4. | The registry files already say `schema_version: "1.0"`, but nothing defines what that means, so a tool would either reject or silently accept newer files. | Not affected. Files declare `1.0`, and absence in frontmatter means `1.0` |
| NR-4 | The reserved keys in §13.5 are not allowed. | `docs/ARCHITECTURE.md` §2 and `docs/IMPORT-AND-VERIFICATION.md` §2 state the principles of no shared identity and no automatic installation. This makes them checkable. | Not affected. No existing record uses these keys |
| NR-5 | Adapter lifecycle, as worded in `adapters/README.md` §4: platform status is `future`, `planned`, or `draft`, and `draft` requires `adapters/<platform>/` containing `README.md`. | Adapter declarations need a lifecycle in which no adapter claim can be false. `draft` means guidance written but untested. | Not affected. All four platforms are `planned` or `future`, and no adapter directory exists |
| NR-6 | The skill dependency graph has no self-dependency and no cycle. | Skills must be independently scoped and maintainable (§2). A cycle makes independent adoption impossible. | Not affected. No dependency edge exists |
| NR-7 | A skill's directory name equals its `id`, for every skill type. | §3 shows the `skill-id/` directory for specialist skills only. Extending it to core and meta skills gives tools and contributors one lookup rule. | Not affected. `core/quality-guardian/` matches `quality-guardian` |
| NR-8 | Compatibility records reference only registered skills and declared platforms. | The two registry files are the ecosystem's central record (`docs/ARCHITECTURE.md` §4.6), but no document says that references between them must resolve. | Not affected. Every record resolves |

Not new under NR-2: the presence of the 14 metadata fields (§4), the Semantic Versioning pattern for `version` (§10), the explicit `dependencies` key, and the current shape of the two registry files.

### 13.8 Existing rules that tools check

These rules were already stated before this section and are not new requirements.

| Existing rule | Where it was already stated |
|---|---|
| Registry and compatibility files are valid, parseable YAML, with no duplicate keys | `docs/DEVELOPMENT-ROADMAP.md` Phase 0 exit criteria |
| Skill ids are unique | `registry_rules.unique_ids` |
| Every skill has a `type` from `skill_types` and a `status` from `lifecycle_statuses` | `registry/skills.yaml`; `docs/ARCHITECTURE.md` §6 |
| Registry dependencies name registered skills; documents are not listed there | `registry_rules.require_dependency_declarations`; the comment in `registry/skills.yaml` |
| Registered paths and documentation files exist, with matching letter case | `registry_rules.require_skill_documentation`; `docs/ARCHITECTURE.md` §4.6 |
| A skill marked `validated` or `released` has its tests and results files | `registry_rules.require_validation_before_release`; §9 and §11 |
| A skill directory under a type directory is registered | `README.md`, Contributing and Change Discipline; roadmap Phase 3 |
| A skill's `id`, `type`, `version`, and `status` agree between frontmatter and registry | §4 (the fields every skill declares); §11 (version and registry information are updated); `docs/ARCHITECTURE.md` §4.6 (the registry tracks identifiers, versions, and status); `CHANGELOG.md` Versioning (version recorded in both places) |
| Every registered skill has a compatibility record | `registry_rules.require_platform_compatibility_declarations` |
| A compatibility record for another skill version does not claim compatibility | `registry/compatibility.yaml` rules; `docs/IMPORT-AND-VERIFICATION.md` §9 |
| Compatibility levels come from `compatibility_levels` | `registry/compatibility.yaml` |
| A claimed compatibility level other than `unverified` or `unsupported` has evidence | `registry/compatibility.yaml` rules; `docs/IMPORT-AND-VERIFICATION.md` §9 |
