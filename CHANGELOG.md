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

### Changed

* Foundation documents converted to Markdown (formatting only; wording unchanged).
* Test records reconciled: `test-results.md` is the single source of truth for execution status, and the skill version each test ran against is recorded.
* Adapter layout standardized to `adapters/generic/` and `adapters/<platform>/`.
* Status text in `README.md`, `core/README.md`, and the roadmap aligned with the repository's actual state.

### Notes

* No skill is validated or released. `quality-guardian` remains a draft.
* Quality Guardian results are behavioral scenario evaluations only. No repository security scan has been run.

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
