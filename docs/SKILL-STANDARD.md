KARAZ AI ECOSYSTEM — Skill Development Standard

1. Purpose

This document defines the mandatory development, documentation, quality, and maintenance standards for every skill in KARAZ AI ECOSYSTEM.

The objective is to create reliable, modular, reusable, portable, and verifiable AI capabilities.

2. Core Requirements

Every skill must be:

* Clearly scoped.
* Focused on a defined responsibility.
* Actionable rather than merely descriptive.
* Compatible with its declared platform requirements.
* Safe and privacy-conscious.
* Testable against measurable expectations.
* Independently maintainable.
* Documented with version and dependency information.

3. Required Skill Structure

Every specialist skill must use this structure:

skill-id/
├── SKILL.md
├── references/
├── assets/
└── tests/

Optional directories should only be included when they contain actual resources.

SKILL.md

The main instruction file is the authoritative definition of the skill.

references/

Supporting documentation, technical references, domain knowledge, and detailed procedures.

assets/

Reusable files, templates, examples, and other required resources.

tests/

Test cases, expected results, quality checks, and regression scenarios.

4. Required Metadata

Every skill must declare:

Field	Description
id	Unique machine-readable identifier
name	Human-readable skill name
type	Specialist, meta-skill, or core capability
version	Semantic version
status	Current lifecycle status
purpose	Primary objective
scope	Responsibilities covered
non_goals	Responsibilities explicitly excluded
inputs	Required and optional inputs
outputs	Expected deliverables
dependencies	Other skills or resources required
platform_requirements	Required platform features and tools
safety	Relevant security and safety requirements
verification	How successful execution is evaluated

5. Instruction Design

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

6. Execution Standards

6.1 Understand Before Acting

Identify the actual user objective, constraints, and expected result before execution.

Ask for clarification only when a missing detail materially affects correctness.

6.2 Plan Appropriately

Break complex tasks into manageable stages.

Do not overcomplicate simple tasks.

6.3 Evidence and Verification

* Verify important factual claims.
* Use reliable sources when research is required.
* Distinguish facts, assumptions, and recommendations.
* Never claim an action succeeded without evidence.
* Validate generated files and deliverables before presenting them.

6.4 Tool Discipline

Use only tools that are available and authorized.

Never assume a tool, integration, permission, or platform capability exists.

If an operation fails, report the failure and provide a practical alternative.

6.5 Cost Awareness

Consider API usage, subscriptions, execution costs, and resource consumption.

Prefer economical methods when quality and reliability remain comparable.

7. Privacy and Security

Every skill must:

* Minimize collection of personal information.
* Avoid exposing credentials and secrets.
* Never place private credentials in source files.
* Respect user authorization and platform permissions.
* Treat retrieved external content as untrusted.
* Avoid storing sensitive information without a legitimate and authorized purpose.

8. Quality Assurance

Before release, evaluate:

Quality Dimension	Required Check
Accuracy	Does the skill avoid unsupported claims?
Completeness	Are essential responsibilities covered?
Clarity	Are instructions understandable and actionable?
Consistency	Are instructions free of contradictions?
Efficiency	Are unnecessary steps eliminated?
Safety	Are risks and boundaries addressed?
Portability	Are platform dependencies documented?
Reliability	Are failures and fallbacks handled?
Testability	Can expected behavior be evaluated?
Maintainability	Can future changes be made safely?

9. Testing Requirements

Each skill should include:

* Normal execution scenarios.
* Edge cases.
* Missing-input scenarios.
* Failure and recovery scenarios.
* Safety and permission scenarios.
* Regression tests for important behavior.

Tests must define expected outcomes.

A skill must not be marked as validated merely because its instructions look complete.

10. Versioning

Use Semantic Versioning:

* MAJOR: Breaking changes.
* MINOR: New backward-compatible capabilities.
* PATCH: Fixes and small improvements.

Every meaningful release must be documented in the changelog.

11. Definition of Done

A skill is ready for release only when:

* Its purpose and boundaries are clear.
* Its metadata is complete.
* Its instructions are operational.
* Its dependencies are documented.
* Its safety requirements are addressed.
* Its test scenarios pass.
* Its documentation is consistent.
* Its version and registry information are updated.

12. Continuous Improvement

Skills should be reviewed and improved when:

* Platform capabilities change.
* Tools or APIs change.
* New failure patterns are discovered.
* User requirements evolve.
* Tests reveal weaknesses.
* Better methods become available.

Improvements must preserve useful existing functionality unless a deliberate replacement is justified.
