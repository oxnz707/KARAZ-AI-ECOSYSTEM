# Baseline 1.0

This folder is the pinned backward-compatibility baseline for schema 1.x. It holds the real KARAZ records as they stood on `main` at commit `c7e74101413453e39f8ea0f89d21d13e49ba37dc` (provenance only; no test reads git).

| File | What it is | SHA-256 |
|---|---|---|
| `core/quality-guardian/SKILL.md` | frontmatter verbatim, body stubbed | `fc05513eea4fe0b8807cf55cb71f981e3b379f82cba0ae214aac78f104ffad51` |
| `core/quality-guardian/tests/test-cases.md` | empty stub | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `core/quality-guardian/tests/test-results.md` | empty stub | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `registry/compatibility.yaml` | verbatim | `a4081a47a70f557685f03df3ad2013bfb26abd9277ee9044dc26280050a95fd3` |
| `registry/skills.yaml` | verbatim | `c46e1d19a2b5aebb4e15b475e4778245b39f91a9512e9249dc579549c76d70d0` |

* `registry/skills.yaml` and `registry/compatibility.yaml` are byte-for-byte copies.
* `SKILL.md` keeps the original frontmatter byte-for-byte; the Markdown body is replaced by a one-line stub.
* The two files under `tests/` are empty stubs for the evidence files that the registry references.
* The baseline is never edited to make a test pass. It changes only at a schema MAJOR version bump, in a reviewed pull request that states why. `baseline-1.0/` is then kept for migration tests and a new baseline is added.
* Every later schema 1.x and validator must report zero ERROR and zero WARNING on this folder. The only diagnostics expected are four INFO notices (KZ-C007) for the `planned` and `future` platforms `chatgpt`, `gemini`, `generic` and `grok`, whose adapter directories do not exist.
