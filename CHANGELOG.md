# Changelog

All notable changes to KARAZ AI ECOSYSTEM are documented here.

## Versioning

The repository version (`ecosystem.version` in `registry/skills.yaml`) and each skill's version (in its `SKILL.md` frontmatter and registry entry) are independent. Both follow Semantic Versioning (see `docs/SKILL-STANDARD.md`). A skill's version changes when that skill changes. The repository version changes only at a repository release; none has been made since 0.1.0.

## [Unreleased]

### Added

* Core operating standards specification (`core/README.md`).
* `quality-guardian` core skill, draft. Version history: 0.1.0 (initial specification), 0.2.0 (security and secret-exposure review), 0.3.0 (credential authenticity, scanning-tool guidance, machine-readable reports).
* Quality Guardian test specifications (QG-001 to QG-013) and scenario-evaluation records.
* Development roadmap (`docs/DEVELOPMENT-ROADMAP.md`).
* Registry entry and platform compatibility record for `quality-guardian` (draft; platform compatibility unverified).
* JSON Schemas (draft 2020-12, schema version 1.0) for skill frontmatter, the skills registry, and the platform compatibility registry (`schemas/`).
* Portable format and normative requirements NR-1 to NR-8 (`docs/SKILL-STANDARD.md` §13), with the existing rules they build on listed separately.
* Adapter contract, including adapter status values and the authoritative wording of NR-5 (`adapters/README.md`).
* Read-only structural validator (`tools/karaz_validate/`, run as `python -m tools.karaz_validate [--root PATH] [--format text|json]`) with 28 checks classified as existing rules, new normative requirements, or diagnostics. Exit 0 means no ERROR, 1 means an ERROR, 2 means the validator could not run; WARNING and INFO never fail a run. Files larger than 1 MiB are rejected (KZ-L001).
* Hash-locked dependency install for the validator (`tools/requirements.in`, `tools/requirements.txt`; PyYAML and jsonschema).
* Structural test suite (`tests/structure/`, standard-library `unittest`) with a canonical fixture and a pinned backward-compatibility baseline of the real records (`tests/structure/fixtures/baseline-1.0/`).
* `.gitignore` for Python cache files and virtual environments.

### Changed

* Foundation documents converted to Markdown (formatting only; wording unchanged).
* Test records reconciled: `test-results.md` is the single source of truth for execution status, and the skill version each test ran against is recorded.
* Adapter layout standardized to `adapters/generic/` and `adapters/<platform>/`.
* Status text in `README.md`, `core/README.md`, and the roadmap aligned with the repository's actual state.
* `docs/SKILL-STANDARD.md` §4: the `type` field now names the registry values `core`, `meta`, and `specialist`.
* `docs/ARCHITECTURE.md` §5: the proposed repository tree lists `schemas/`, `tools/`, and `adapters/README.md`.

### Notes

* No skill is validated or released. `quality-guardian` remains a draft.
* Quality Guardian results are behavioral scenario evaluations only. No repository security scan has been run.
* The structural validator checks structure only. A passing run does not validate or release any skill, and it is not wired into CI yet. No registry file or skill file was changed.

## [0.1.0] - Initial Foundation

### Added

* Initial repository structure and architectural direction.
* Platform-independent skill ecosystem principles.
* Separation between AI identity and reusable capabilities.
* Skill lifecycle and quality standards.

### Planned

* Core operating standards.
* Meta-skills framework.
* Specialist skills migration and improvement.
* Platform adapters.
* Validation and regression testing.

### Notes

No specialist skills have been migrated or released in this version.
