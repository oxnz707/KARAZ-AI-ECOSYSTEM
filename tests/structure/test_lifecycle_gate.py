"""KZ-G001 and KZ-G002: the evidence gates for the validated and released statuses (EV-1, EV-2).

The gates check declarations only. These tests also pin that limit: a gate pass does not read or
verify any evidence record, and the gates are the only reason the gated scenarios fail.
"""

import re
import unittest
from unittest import mock

from support import CORE, CORE_MD, ERROR, REGISTRY, REPO, TreeCase, run_cli

from tools.karaz_validate import registry_checks

P1_CODES = {
    "KZ-C001", "KZ-C002", "KZ-C003", "KZ-C004", "KZ-C005", "KZ-C006", "KZ-C007", "KZ-C008",
    "KZ-F001", "KZ-F002", "KZ-F003", "KZ-I001", "KZ-L001", "KZ-L002",
    "KZ-R001", "KZ-R002", "KZ-R003", "KZ-R004", "KZ-R005", "KZ-R006", "KZ-R007", "KZ-R008", "KZ-R009", "KZ-R010",
    "KZ-S001", "KZ-S002", "KZ-S003", "KZ-S004",
}
CORE_BLOCK = ('    dependencies: []\n    platform_compatibility: "registry/compatibility.yaml"\n    validation:\n'
              '      behavioral_scenario_evaluation: "not_run"\n      repository_security_scan: "not_run"\n')


class GateCase(TreeCase):
    def set_core(self, status, evaluation="not_run", scan="not_run"):
        """Give the core skill a status and evidence flags. None leaves a flag out of the registry entry."""
        self.edit(REGISTRY, 'status: draft\n    path: "core', f'status: {status}\n    path: "core')
        self.edit(CORE_MD, "status: draft", f"status: {status}")
        lines = ""
        if status in ("validated", "released"):  # satisfy KZ-R008 so that only the gates are under test
            for name in ("t.md", "r.md"):
                self.write(f"{CORE}/tests/{name}", "Placeholder file for the structural test.\n")
            lines += f'      tests: "{CORE}/tests/t.md"\n      results: "{CORE}/tests/r.md"\n'
        if evaluation is not None:
            lines += f'      behavioral_scenario_evaluation: "{evaluation}"\n'
        if scan is not None:
            lines += f'      repository_security_scan: "{scan}"\n'
        head = CORE_BLOCK.split("    validation:\n")[0] + "    validation:\n"
        self.edit(REGISTRY, CORE_BLOCK, head + lines)


class EvaluationGate(GateCase):  # KZ-G001 (EV-1)
    def test_validated_with_evaluation_not_run_is_an_error(self):
        self.set_core("validated")
        report = self.check()
        self.assertPairs(report, {("KZ-G001", ERROR)})
        d = self.find(report, "KZ-G001", ERROR, file=REGISTRY, text="not_run")
        self.assertEqual(d.location, "$.skills[0].validation.behavioral_scenario_evaluation")
        self.assertIn("EV-1", d.message)
        self.assertErrorExit(report)

    def test_released_with_evaluation_not_run_is_an_error(self):
        self.set_core("released", scan="recorded")
        self.assertPairs(self.check(), {("KZ-G001", ERROR)})

    def test_missing_flag_is_treated_as_not_recorded(self):
        self.set_core("validated", evaluation=None)
        report = self.check()
        self.assertPairs(report, {("KZ-G001", ERROR)})
        self.find(report, "KZ-G001", ERROR, text="'missing'")

    def test_missing_validation_block_is_treated_as_not_recorded(self):
        self.set_core("validated", evaluation=None, scan=None)
        self.assertPairs(self.check(), {("KZ-G001", ERROR)})

    def test_validated_with_evaluation_recorded_passes_and_needs_no_scan(self):
        self.set_core("validated", evaluation="recorded", scan="not_run")  # EV-2 applies to released only
        report = self.check()
        self.assertPairs(report, set())
        self.assertEqual(report.exit_code, 0)

    def test_gate_does_not_apply_before_validation(self):
        for status in ("proposed", "draft", "deprecated", "retired"):
            with self.subTest(status=status):
                original = self.read(REGISTRY), self.read(CORE_MD)
                if status != "draft":
                    self.set_core(status)
                self.assertPairs(self.check(), set())
                self.write(REGISTRY, original[0])
                self.write(CORE_MD, original[1])

    def test_gate_reports_each_skill_separately(self):
        self.set_core("validated")
        self.edit(REGISTRY, 'status: draft\n    path: "specialist', 'status: validated\n    path: "specialist')
        self.edit(f"specialist-skills/example-specialist-skill/SKILL.md", "status: draft", "status: validated")
        for name in ("t.md", "r.md"):
            self.write(f"specialist-skills/example-specialist-skill/tests/{name}", "Placeholder.\n")
        self.edit(REGISTRY, 'dependencies:\n      - example-core-skill\n    platform_compatibility: "registry/compatibility.yaml"\n    validation:\n',
                  'dependencies:\n      - example-core-skill\n    platform_compatibility: "registry/compatibility.yaml"\n    validation:\n'
                  '      tests: "specialist-skills/example-specialist-skill/tests/t.md"\n'
                  '      results: "specialist-skills/example-specialist-skill/tests/r.md"\n')
        report = self.check()
        locations = sorted(d.location for d in report.diagnostics if d.code == "KZ-G001")
        self.assertEqual(locations, ["$.skills[0].validation.behavioral_scenario_evaluation",
                                     "$.skills[1].validation.behavioral_scenario_evaluation"])


class ScanGate(GateCase):  # KZ-G002 (EV-2)
    def test_released_with_scan_not_run_is_an_error(self):
        self.set_core("released", evaluation="recorded", scan="not_run")
        report = self.check()
        self.assertPairs(report, {("KZ-G002", ERROR)})
        d = self.find(report, "KZ-G002", ERROR, file=REGISTRY, text="not_run")
        self.assertEqual(d.location, "$.skills[0].validation.repository_security_scan")
        self.assertIn("EV-2", d.message)
        self.assertErrorExit(report)

    def test_missing_scan_flag_is_treated_as_not_recorded(self):
        self.set_core("released", evaluation="recorded", scan=None)
        report = self.check()
        self.assertPairs(report, {("KZ-G002", ERROR)})
        self.find(report, "KZ-G002", ERROR, text="'missing'")

    def test_released_with_both_recorded_passes(self):
        self.set_core("released", evaluation="recorded", scan="recorded")
        report = self.check()
        self.assertPairs(report, set())
        self.assertEqual(report.exit_code, 0)

    def test_released_with_neither_recorded_reports_both_gates(self):
        self.set_core("released")
        self.assertPairs(self.check(), {("KZ-G001", ERROR), ("KZ-G002", ERROR)})

    def test_invalid_flag_value_does_not_satisfy_the_gate(self):
        self.set_core("released", evaluation="recorded", scan="done")
        pairs = self.pairs(self.check())
        self.assertIn(("KZ-G002", ERROR), pairs)
        self.assertIn(("KZ-S001", ERROR), pairs)  # the schema check reports the invalid value separately

    def test_cli_output_and_exit_code(self):
        self.set_core("released", evaluation="recorded")
        code, out, _ = run_cli("--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("ERROR KZ-G002", out)
        self.assertIn("    Fix: ", out)
        self.assertIn("Structural validation failed.", out)


class DeclarationOnly(GateCase):
    def test_a_pass_does_not_read_or_require_any_evidence_record(self):
        self.set_core("released", evaluation="recorded", scan="recorded")
        self.assertFalse((self.root / CORE / "evidence").exists())
        self.assertFalse((self.root / "docs" / "evidence").exists())
        self.assertPairs(self.check(), set())  # the gates check the declaration; review checks the evidence

    def test_the_closing_sentence_still_says_a_pass_proves_nothing_about_release(self):
        self.set_core("released", evaluation="recorded", scan="recorded")
        code, out, _ = run_cli("--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertIn("does not establish that any skill is validated or released", out)


class GatesAreTheOnlyCause(GateCase):
    """The disable-the-check negative test: without the gates, the same scenarios pass."""

    def test_scenarios_fail_only_because_of_the_gates(self):
        self.set_core("released")
        self.assertPairs(self.check(), {("KZ-G001", ERROR), ("KZ-G002", ERROR)})
        without_gates = [c for c in registry_checks.CHECKS if c[0] not in ("KZ-G001", "KZ-G002")]
        self.assertEqual(len(without_gates), len(registry_checks.CHECKS) - 2)
        with mock.patch.object(registry_checks, "CHECKS", without_gates):
            self.assertPairs(self.check(), set())

    def test_each_gate_can_be_disabled_independently(self):
        self.set_core("released", evaluation="recorded")
        for disabled, expected in (("KZ-G002", set()), ("KZ-G001", {("KZ-G002", ERROR)})):
            with self.subTest(disabled=disabled):
                remaining = [c for c in registry_checks.CHECKS if c[0] != disabled]
                with mock.patch.object(registry_checks, "CHECKS", remaining):
                    self.assertPairs(self.check(), expected)


class SkippedAndInventory(GateCase):
    def test_gates_are_skipped_and_listed_when_the_registry_is_not_validated(self):
        self.set_core("released")
        self.edit(REGISTRY, 'schema_version: "1.0"', 'schema_version: "2.0"')
        report = self.check()
        self.assertNotIn("KZ-G001", {d.code for d in report.diagnostics})
        skipped = {c for codes in report.skipped.values() for c in codes}
        self.assertTrue({"KZ-G001", "KZ-G002"} <= skipped)

    def test_the_validator_has_30_checks_and_the_28_p1_codes_are_unchanged(self):
        codes = set()
        for path in (REPO / "tools" / "karaz_validate").glob("*.py"):
            codes |= set(re.findall(r'"(KZ-[A-Z]\d{3})"', path.read_text(encoding="utf-8")))
        self.assertEqual(len(P1_CODES), 28)
        self.assertEqual(codes, P1_CODES | {"KZ-G001", "KZ-G002"})
        self.assertEqual(len(codes), 30)


if __name__ == "__main__":
    unittest.main()
