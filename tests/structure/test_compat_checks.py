"""KZ-C001 to KZ-C008 (compatibility registry)."""

import unittest

from support import COMPAT, ERROR, INFO, REGISTRY, WARNING, TreeCase

SPEC_RECORD = "  - skill_id: example-specialist-skill"
RECORD_TAIL = ('    skill_version: "0.1.0"\n    platforms:\n      exampleplatform:\n'
               '        compatibility: unverified\n        evidence: "None. Nothing has been tested."\n')


class RecordsReferenceRegisteredSkills(TreeCase):  # KZ-C001
    def test_record_for_unregistered_skill(self):
        self.write(COMPAT, self.read(COMPAT).rstrip("\n") + "\n\n  - skill_id: ghost-skill\n" + RECORD_TAIL)
        report = self.check()
        self.assertPairs(report, {("KZ-C001", ERROR)})
        self.find(report, "KZ-C001", ERROR, file=COMPAT, text="ghost-skill")
        self.assertErrorExit(report)


class EverySkillHasARecord(TreeCase):  # KZ-C002
    def test_registered_skill_without_record(self):
        self.write(COMPAT, self.read(COMPAT).split(SPEC_RECORD)[0].rstrip("\n") + "\n")
        report = self.check()
        self.assertPairs(report, {("KZ-C002", ERROR)})
        self.find(report, "KZ-C002", ERROR, file=REGISTRY, text="example-specialist-skill")
        self.assertErrorExit(report)


class RecordVersionMatchesRegistry(TreeCase):  # KZ-C003
    def test_stale_record_with_a_claim_is_an_error(self):
        self.edit(COMPAT, '    skill_version: "0.1.0"\n    platforms:\n      exampleplatform:\n        compatibility: unverified\n        evidence: "None. Nothing has been tested."\n        limitations: "Fixture only."\n\n  - skill_id: example-specialist-skill',
                  '    skill_version: "0.0.9"\n    platforms:\n      exampleplatform:\n        compatibility: partially_supported\n        evidence: "Recorded observation."\n        limitations: "Fixture only."\n\n  - skill_id: example-specialist-skill')
        report = self.check()
        self.assertPairs(report, {("KZ-C003", ERROR)})
        self.find(report, "KZ-C003", ERROR, file=COMPAT, text="0.0.9")
        self.assertErrorExit(report)

    def test_stale_record_without_a_claim_is_only_a_warning(self):
        self.edit(COMPAT, '    skill_version: "0.1.0"\n    platforms:\n      exampleplatform:\n        compatibility: unverified\n        evidence: "None. Nothing has been tested."\n        limitations: "Fixture only."\n\n  - skill_id: example-specialist-skill',
                  '    skill_version: "0.0.9"\n    platforms:\n      exampleplatform:\n        compatibility: unverified\n        evidence: "None. Nothing has been tested."\n        limitations: "Fixture only."\n\n  - skill_id: example-specialist-skill')
        self.assertWarningOnly(self.check(), "KZ-C003", file=COMPAT, text="0.0.9")


class PlatformsAreDeclared(TreeCase):  # KZ-C004
    def test_undeclared_platform_in_a_record(self):
        self.edit(COMPAT, "      exampleplatform:\n        compatibility", "      otherplatform:\n        compatibility")
        report = self.check()
        self.assertPairs(report, {("KZ-C004", ERROR)})
        self.find(report, "KZ-C004", ERROR, file=COMPAT, text="otherplatform")
        self.assertErrorExit(report)


class LevelsComeFromTheVocabulary(TreeCase):  # KZ-C005
    def test_unknown_level(self):
        self.edit(COMPAT, "compatibility: unverified", "compatibility: tested")
        report = self.check()
        self.assertPairs(report, {("KZ-C005", ERROR)})
        self.find(report, "KZ-C005", ERROR, file=COMPAT, text="tested")
        self.assertErrorExit(report)


class ClaimsNeedEvidence(TreeCase):  # KZ-C006
    def test_every_claiming_level_needs_evidence(self):
        for level in ("compatible", "compatible_with_adaptation", "partially_supported"):
            with self.subTest(level=level):
                original = self.read(COMPAT)
                self.edit(COMPAT, "compatibility: unverified\n        evidence: \"None. Nothing has been tested.\"\n",
                          f"compatibility: {level}\n")
                report = self.check()
                self.assertPairs(report, {("KZ-C006", ERROR)})
                self.find(report, "KZ-C006", ERROR, file=COMPAT, text=level)
                self.assertErrorExit(report)
                self.write(COMPAT, original)

    def test_claim_with_evidence_passes(self):
        self.edit(COMPAT, "compatibility: unverified\n        evidence: \"None. Nothing has been tested.\"",
                  "compatibility: compatible\n        evidence: \"Recorded observation.\"")
        self.assertPairs(self.check(), set())

    def test_unverified_and_unsupported_need_no_evidence(self):
        for level in ("unverified", "unsupported"):
            with self.subTest(level=level):
                original = self.read(COMPAT)
                self.edit(COMPAT, "compatibility: unverified\n        evidence: \"None. Nothing has been tested.\"\n",
                          f"compatibility: {level}\n")
                self.assertPairs(self.check(), set())
                self.write(COMPAT, original)


class AdapterLifecycle(TreeCase):  # KZ-C007 (NR-5)
    def test_draft_without_directory_is_an_error(self):
        self.delete("adapters/exampleplatform")
        report = self.check()
        self.assertPairs(report, {("KZ-C007", ERROR)})
        self.find(report, "KZ-C007", ERROR, file=COMPAT, text="README.md")
        self.assertErrorExit(report)

    def test_draft_without_readme_is_an_error(self):
        self.delete("adapters/exampleplatform/README.md")
        self.assertPairs(self.check(), {("KZ-C007", ERROR)})

    def test_planned_or_future_without_directory_is_info_and_never_blocks(self):
        for status in ("planned", "future"):
            with self.subTest(status=status):
                original = self.read(COMPAT)
                self.edit(COMPAT, 'status: "draft"', f'status: "{status}"')
                self.delete("adapters/exampleplatform")
                self.assertWarningOnly(self.check(), "KZ-C007", INFO, file=COMPAT, text=status)
                self.write(COMPAT, original)
                self.write("adapters/exampleplatform/README.md", "Fixture.\n")

    def test_planned_with_directory_is_clean(self):
        self.edit(COMPAT, 'status: "draft"', 'status: "planned"')
        self.assertPairs(self.check(), set())

    def test_unknown_adapter_status_is_a_schema_error(self):
        self.edit(COMPAT, 'status: "draft"', 'status: "tested"')
        self.assertIn(("KZ-S001", ERROR), self.pairs(self.check()))

    def test_adapter_path_outside_the_repository_is_not_a_directory(self):
        self.edit(COMPAT, 'adapter: "adapters/exampleplatform/"', 'adapter: "../elsewhere/"')
        self.assertIn(("KZ-C007", ERROR), self.pairs(self.check()))


class AdapterDirectoriesAreDeclared(TreeCase):  # KZ-C008
    def test_directory_without_platform_entry_warns_and_never_blocks(self):
        self.write("adapters/orphan/README.md", "Fixture.\n")
        self.assertWarningOnly(self.check(), "KZ-C008", file="adapters/orphan", text="platform entry")

    def test_files_directly_under_adapters_are_not_adapters(self):
        self.write("adapters/README.md", "Contract.\n")
        self.assertPairs(self.check(), set())


if __name__ == "__main__":
    unittest.main()
