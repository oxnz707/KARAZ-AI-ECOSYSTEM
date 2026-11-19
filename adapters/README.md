# KARAZ AI ECOSYSTEM — Adapter Contract

## 1. Purpose

This document defines what a platform adapter is, what an adapter directory contains, and how an adapter is declared. It is the authoritative source for requirement NR-5 (adapter lifecycle), listed in `docs/SKILL-STANDARD.md` §13.

An adapter describes technical adoption on one platform. It never defines an assistant's identity, and it never claims that a skill is installed, activated, or compatible without evidence (`docs/ARCHITECTURE.md` §2 and §4.5, `docs/IMPORT-AND-VERIFICATION.md` §2).

This file is the contract only. It is not an adapter, and no platform adapter exists yet.

## 2. Layout

* `adapters/generic/` holds platform-independent adaptation guidance.
* `adapters/<platform>/` holds guidance for one platform, for example `adapters/chatgpt/`. Each platform has its own directory so that one platform's limitations are never assumed to apply to another.
* A directory is created only when its first real file is added. Empty placeholder directories are not created.
* `<platform>` is a lowercase kebab-case name that matches a key under `platforms` in `registry/compatibility.yaml`.
* This `README.md`, which sits directly in `adapters/`, is not an adapter.

## 3. Declaring an adapter

Every platform is declared under `platforms` in `registry/compatibility.yaml` with a `status` and an `adapter` path. The platform name used in any compatibility record must be declared there.

## 4. Adapter status values (NR-5)

**Authoritative wording of NR-5.** The `status` of a platform in `registry/compatibility.yaml` is one of `future`, `planned`, or `draft`. A platform with status `draft` must have the directory named by its `adapter` field, and that directory must contain a `README.md`. A platform with status `future` or `planned` may have no directory.

| Status | Meaning | Directory and `README.md` |
|---|---|---|
| `future` | Reserved. No work has started | May be absent |
| `planned` | Intended. Platform mechanisms are not yet understood or tested | May be absent |
| `draft` | Guidance has been written but has not been tested on the platform | Required |

* `draft` records that guidance exists. It is not a statement that anything works.
* Status values beyond `draft`, such as a tested state, are not defined. They will be defined when adapters have real platform evidence (roadmap Phase 4).
* The status of an adapter is separate from a skill's compatibility level. A skill's level on a platform is recorded per skill in `registry/compatibility.yaml` and needs evidence for every claim other than `unverified` or `unsupported`.

## 5. Contents of `adapters/<platform>/README.md`

The README of a `draft` adapter has these sections. They follow the five adoption stages of `docs/IMPORT-AND-VERIFICATION.md` §3, so that each stage is reported separately.

| Section | Stage | Content |
|---|---|---|
| Platform and scope | — | The platform this adapter covers and the skills or skill types it addresses |
| Retrieval | 1. Retrieved | How an assistant on this platform can obtain the skill files, and what it cannot access |
| Understanding | 2. Understood | Instruction format limits, context and file limits, and any required reformatting |
| Registration | 3. Registered | The platform's actual mechanism for adding instructions or skills, or the statement that none is supported |
| Activation | 4. Activated | How activation is observed on this platform, or the statement that it cannot be confirmed |
| Execution and verification | 5. Executed and verified | The test procedure, with expected results |
| Limitations | — | Tools, permissions, and platform restrictions that affect adoption |
| Evidence | — | Observable results of tests actually performed. For a `draft` adapter this section states that none have been performed |

## 6. Rules

* No identity content. An adapter does not contain a persona, name, personality, voice, or communication style for any assistant.
* No claims without evidence. An adapter does not state that a skill is installed, activated, or compatible unless the Evidence section records an observed result.
* Each stage is reported separately. Retrieval or understanding is never reported as registration or activation.
* No assumed capabilities. An adapter describes only mechanisms that its platform actually provides.
* Platform-specific behavior lives only in adapters. Skills describe capabilities and stay platform-independent; the platform-specific parts are written here.
* No secrets. Tokens, credentials, and private user information never appear in an adapter.

## 7. Current state

All platforms in `registry/compatibility.yaml` are `planned` or `future`, and no adapter directory exists.
