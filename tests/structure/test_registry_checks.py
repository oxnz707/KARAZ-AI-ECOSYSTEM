"""KZ-R001 to KZ-R006, KZ-R008, KZ-R009 and KZ-F001 (registry rules)."""

import unittest

from support import CORE, CORE_MD, ERROR, REGISTRY, SPEC, SPEC_MD, WARNING, TreeCase

DEPENDS_ON_CORE = "dependencies:\n      - example-core-skill\n"


class UniqueIds(TreeCase):  # KZ-R001
    def test_duplicate_id(self):
        self.edit(REGISTRY, "id: example-specialist-skill", "id: example-core-skill")
        report = self.check()
        self.find(report, "KZ-R001", ERROR, file=REGISTRY, text="example-core-skill")
        self.assertErrorExit(report)


class Vocabularies(TreeCase):  # KZ-R002, KZ-R003
    def test_unknown_type(self):
        self.edit(REGISTRY, "type: specialist\n    version", "type: wizard\n    version")
        self.find(self.check(), "KZ-R002", ERROR, file=REGISTRY, text="wizard")

    def test_unknown_status(self):
        self.edit(REGISTRY, "status: draft\n    path: \"specialist", "status: published\n    path: \"specialist")
        self.find(self.check(), "KZ-R003", ERROR, file=REGISTRY, text="published")

    def test_every_listed_value_is_accepted(self):
        for status in ("proposed", "draft", "deprecated", "retired"):
            with self.subTest(status=status):
                self.edit(REGISTRY, "status: draft\n    path: \"core", f"status: {status}\n    path: \"core")
                self.edit(CORE_MD, "status: draft", f"status: {status}")
                self.assertPairs(self.check(), set())
                self.edit(REGISTRY, f"status: {status}\n    path: \"core", "status: draft\n    path: \"core")
                self.edit(CORE_MD, f"status: {status}", "status: draft")


class Dependencies(TreeCase):  # KZ-R004, KZ-R005, KZ-R006
    def test_unregistered_dependency(self):
        self.edit(REGISTRY, "- example-core-skill", "- missing-skill")
        report = self.check()
        self.assertPairs(report, {("KZ-R004", ERROR)})
        self.find(report, "KZ-R004", ERROR, file=REGISTRY, text="missing-skill")
        self.assertErrorExit(report)

    def test_self_dependency(self):
        self.edit(REGISTRY, "- example-core-skill", "- example-specialist-skill")
        report = self.check()
        self.assertPairs(report, {("KZ-R005", ERROR)})
        self.find(report, "KZ-R005", ERROR, text="depends on itself")

    def test_two_skill_cycle(self):
        self.edit(REGISTRY, "dependencies: []\n", "dependencies:\n      - example-specialist-skill\n")
        report = self.check()
        self.assertPairs(report, {("KZ-R005", ERROR)})
        self.find(report, "KZ-R005", ERROR, text="Dependency cycle")

    def test_three_skill_cycle(self):
        third = self.read(SPEC_MD).replace("example-specialist-skill", "example-third-skill")
        self.write("specialist-skills/example-third-skill/SKILL.md", third)
        entry = self.read(REGISTRY).split("  - id: example-specialist-skill")[1]
        entry = "  - id: example-third-skill" + entry.replace("example-specialist-skill", "example-third-skill")
        entry = entry.replace(DEPENDS_ON_CORE, "dependencies:\n      - example-specialist-skill\n")
        self.write(REGISTRY, self.read(REGISTRY).rstrip("\n") + "\n\n" + entry)
        self.edit(REGISTRY, "dependencies: []\n", "dependencies:\n      - example-third-skill\n")
        self.edit(COMPAT_PATH, "\n  - skill_id: example-specialist-skill", "\n  - skill_id: example-third-skill\n"
                  '    skill_version: "0.1.0"\n    platforms:\n      exampleplatform:\n        compatibility: unverified\n'
                  '        evidence: "None."\n\n  - skill_id: example-specialist-skill')
        report = self.check()
        self.assertPairs(report, {("KZ-R005", ERROR)})
        self.find(report, "KZ-R005", ERROR,
                  text="Dependency cycle: example-core-skill -> example-specialist-skill -> example-third-skill -> example-core-skill")

    def test_released_skill_depending_on_a_draft_warns_and_never_blocks(self):
        self.release_specialist()
        self.assertWarningOnly(self.check(), "KZ-R006", file=REGISTRY, text="example-core-skill")

    def release_specialist(self):
        for rel in ("tests/test-cases.md", "tests/test-results.md"):
            self.write(f"{SPEC}/{rel}", "Evidence placeholder for the structural test.\n")
        self.edit(REGISTRY, 'status: draft\n    path: "specialist', 'status: released\n    path: "specialist')
        self.edit(REGISTRY, 'dependencies:\n      - example-core-skill\n    platform_compatibility: "registry/compatibility.yaml"\n    validation:\n',
                  'dependencies:\n      - example-core-skill\n    platform_compatibility: "registry/compatibility.yaml"\n    validation:\n'
                  f'      tests: "{SPEC}/tests/test-cases.md"\n      results: "{SPEC}/tests/test-results.md"\n')
        self.edit(SPEC_MD, "status: draft", "status: released")


class ValidationEvidence(TreeCase):  # KZ-R008
    def test_validated_without_declared_evidence(self):
        self.edit(REGISTRY, 'status: draft\n    path: "core', 'status: validated\n    path: "core')
        self.edit(CORE_MD, "status: draft", "status: validated")
        report = self.check()
        self.assertPairs(report, {("KZ-R008", ERROR)})
        self.find(report, "KZ-R008", ERROR, file=REGISTRY, text="validation.tests")
        self.find(report, "KZ-R008", ERROR, file=REGISTRY, text="validation.results")
        self.assertErrorExit(report)

    def test_declared_but_missing_files(self):
        self.edit(REGISTRY, 'status: draft\n    path: "core', 'status: released\n    path: "core')
        self.edit(CORE_MD, "status: draft", "status: released")
        self.edit(REGISTRY, '    validation:\n', f'    validation:\n      tests: "{CORE}/tests/t.md"\n      results: "{CORE}/tests/r.md"\n')
        self.find(self.check(), "KZ-R008", ERROR, text="does not exist")

    def test_evidence_files_present_passes(self):
        self.edit(REGISTRY, 'status: draft\n    path: "core', 'status: validated\n    path: "core')
        self.edit(CORE_MD, "status: draft", "status: validated")
        self.edit(REGISTRY, '    validation:\n', f'    validation:\n      tests: "{CORE}/tests/t.md"\n      results: "{CORE}/tests/r.md"\n')
        for name in ("t.md", "r.md"):
            self.write(f"{CORE}/tests/{name}", "Placeholder evidence file.\n")
        self.assertPairs(self.check(), set())


class PathUnderTypeDirectory(TreeCase):  # KZ-R009
    def test_type_and_directory_disagree(self):
        self.edit(REGISTRY, "type: specialist\n    version", "type: core\n    version")
        self.edit(SPEC_MD, "type: specialist", "type: core")
        self.assertWarningOnly(self.check(), "KZ-R009", file=REGISTRY, text="core/")


class FrontmatterAgreesWithRegistry(TreeCase):  # KZ-F001
    def test_version_mismatch_is_an_error_and_stale_compat_record_warns(self):
        self.edit(REGISTRY, 'version: "0.1.0"\n    status: draft\n    path: "specialist',
                  'version: "0.2.0"\n    status: draft\n    path: "specialist')
        report = self.check()
        self.assertPairs(report, {("KZ-F001", ERROR), ("KZ-C003", WARNING)})
        self.find(report, "KZ-F001", ERROR, file=SPEC_MD, text="0.2.0")
        self.assertErrorExit(report)

    def test_id_type_and_status_mismatches_are_errors(self):
        for key, old, new in (("type", "type: specialist\n    version", "type: meta\n    version"),
                              ("status", 'status: draft\n    path: "specialist', 'status: validated\n    path: "specialist')):
            with self.subTest(key=key):
                original = self.read(REGISTRY)
                self.edit(REGISTRY, old, new)
                self.find(self.check(), "KZ-F001", ERROR, file=SPEC_MD, text=key)
                self.write(REGISTRY, original)

    def test_name_mismatch_is_only_a_warning(self):
        self.edit(REGISTRY, 'name: "Example Specialist Skill"', 'name: "Another Name"')
        self.assertWarningOnly(self.check(), "KZ-F001", file=SPEC_MD, text="name")


COMPAT_PATH = "registry/compatibility.yaml"

if __name__ == "__main__":
    unittest.main()
