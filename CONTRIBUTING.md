# Contributing

This guide covers how to change KARAZ AI ECOSYSTEM. Read `README.md` and `docs/SKILL-STANDARD.md` first.

## Rules

* Never commit to `main`. Every change goes through a pull request, and the repository owner merges it.
* Name branches `p<N>/<topic>`, for example `p0/truthful-records`.
* One concern per pull request.
* Do not describe a skill as validated or released, or claim installation, activation, or platform compatibility, without evidence recorded in the repository.
* Never commit secrets or private information.

## Validate locally

Python 3.12 is the version CI uses. From the repository root, in a virtual environment:

```
pip install --require-hashes --only-binary=:all: --no-deps -r tools/requirements.txt
python -m tools.karaz_validate
python -m unittest discover -s tests/structure
```

These are the same commands the `validate` workflow (`.github/workflows/validate.yml`) runs on every pull request.

* The validator exits 0 when it finds no ERROR, 1 when it finds any ERROR, and 2 when it cannot run. WARNING and INFO diagnostics never fail a run.
* A passing run checks structure only. It does not validate or release any skill.
* To change a dependency, edit `tools/requirements.in`, regenerate `tools/requirements.txt` with `pip-compile --generate-hashes --strip-extras` on Python 3.12, and submit that in a pull request of its own.

## Create a skill

1. Create `<type-dir>/<skill-id>/SKILL.md` with the 14 frontmatter fields defined in `docs/SKILL-STANDARD.md`. The field shapes are defined by `schemas/skill-frontmatter.schema.json`.
2. Add `references/`, `assets/`, or `tests/` folders only when they contain real files.
3. Run the validator and the tests.

## Register a skill

1. Add an entry to `registry/skills.yaml`.
2. Add a record to `registry/compatibility.yaml`. Mark every platform `unverified` unless evidence exists.
3. Update `CHANGELOG.md`.

## Add a platform adapter

Follow `adapters/README.md`. Declare the adapter in `registry/compatibility.yaml`; its status stays `planned` until the adapter directory exists.

## Run tests

Use the two commands in "Validate locally". The test suite uses only the Python standard library.

## Validation and evidence

A passing validator run checks structure only. It does not show that anything was evaluated, scanned, or reviewed. Evidence is recorded as described in `docs/EVIDENCE-MODEL.md`.

* Record an evaluation or scan in an evidence record: `<skill-directory>/evidence/<id>.md` for a skill, `docs/evidence/<id>.md` for the repository. Create the directory when the first record is added.
* A record states who or what executed the work, when, how independent it was, where the preserved artifact is, the result, and its limitations. A record starts `unreviewed`.
* A human reviewer who is not the executor marks a record `reviewed` by writing the reviewer's name, the date, and what was checked. An assistant does not review its own work.
* Do not set `behavioral_scenario_evaluation` or `repository_security_scan` to `recorded` in `registry/skills.yaml` without a matching reviewed record (`docs/SKILL-STANDARD.md` §14). The validator checks the declaration (KZ-G001 for `validated` and `released`, KZ-G002 for `released`). It does not read or verify the record. Review does.
* Evidence is public. Never put secrets, private user information, or raw scanner output in a record or its artifact.

## Submit

1. Create a branch named `p<N>/<topic>` from the current `main`.
2. Make one scoped change.
3. Open a pull request against `main`. Paste the validator output and the test output into the description.
4. The owner reviews and merges.
