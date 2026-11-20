"""KZ-L001, KZ-L002 and KZ-S001 to KZ-S004, including schema-version semantics."""

import unittest

from support import (COMPAT, CORE_MD, ERROR, REGISTRY, SPEC_MD, WARNING, TreeCase, run_cli)

from tools.karaz_validate.loader import MAX_FILE_BYTES

CLOSING = 'verification:\n  - "Checked by the structural test suite."\n---'


class ValidTree(TreeCase):
    def test_canonical_tree_has_no_diagnostics(self):
        report = self.check()
        self.assertPairs(report, set())
        self.assertEqual(report.exit_code, 0)
        self.assertEqual(sorted(report.applied),
                         [("compatibility", "1.0"), ("registry", "1.0"), ("skill-frontmatter", "1.0")])

    def test_crlf_and_bom_are_tolerated(self):
        for rel in (CORE_MD, REGISTRY):
            text = self.read(rel).replace("\n", "\r\n")
            (self.root / rel).write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
        self.assertPairs(self.check(), set())


class LoaderErrors(TreeCase):  # KZ-L001
    def test_duplicate_yaml_key(self):
        self.edit(REGISTRY, 'schema_version: "1.0"\n', 'schema_version: "1.0"\nschema_version: "1.0"\n')
        report = self.check()
        self.assertPairs(report, {("KZ-L001", ERROR)})
        self.find(report, "KZ-L001", ERROR, file=REGISTRY, text="duplicate key")
        self.assertErrorExit(report)

    def test_duplicate_key_in_frontmatter(self):
        self.edit(CORE_MD, "status: draft\n", "status: draft\nstatus: draft\n")
        self.find(self.check(), "KZ-L001", ERROR, file=CORE_MD, text="duplicate key")

    def test_invalid_yaml(self):
        self.write(REGISTRY, "skills: [unclosed\n")
        report = self.check()
        self.assertPairs(report, {("KZ-L001", ERROR)})
        self.find(report, "KZ-L001", ERROR, file=REGISTRY, text="Invalid YAML")

    def test_missing_registry_file(self):
        self.delete(COMPAT)
        report = self.check()
        self.assertPairs(report, {("KZ-L001", ERROR)})
        self.find(report, "KZ-L001", ERROR, file=COMPAT, text="not found")
        self.assertIn(COMPAT, " ".join(report.skipped))  # dependent checks are listed as skipped

    def test_file_over_size_limit(self):
        self.write(REGISTRY, self.read(REGISTRY) + "#" * (MAX_FILE_BYTES + 1 - len(self.read(REGISTRY).encode())))
        self.assertEqual((self.root / REGISTRY).stat().st_size, MAX_FILE_BYTES + 1)
        report = self.check()
        self.assertPairs(report, {("KZ-L001", ERROR)})
        self.find(report, "KZ-L001", ERROR, file=REGISTRY, text="1 MiB")

    def test_file_at_size_limit_is_read(self):
        base = self.read(REGISTRY)
        self.write(REGISTRY, base + "#" * (MAX_FILE_BYTES - len(base.encode())))
        self.assertEqual((self.root / REGISTRY).stat().st_size, MAX_FILE_BYTES)
        self.assertPairs(self.check(), set())

    def test_undecodable_file(self):
        (self.root / CORE_MD).write_bytes(b"---\n\xff\xfe\n---\nbody\n")
        self.find(self.check(), "KZ-L001", ERROR, file=CORE_MD, text="UTF-8")


class FrontmatterLocation(TreeCase):  # KZ-L002
    def test_frontmatter_missing(self):
        self.write(CORE_MD, "# Title\n\nBody only.\n")
        report = self.check()
        self.assertPairs(report, {("KZ-L002", ERROR)})
        self.find(report, "KZ-L002", ERROR, file=CORE_MD)

    def test_frontmatter_not_terminated(self):
        self.edit(CORE_MD, CLOSING, CLOSING[:-3])
        self.assertPairs(self.check(), {("KZ-L002", ERROR)})

    def test_frontmatter_must_be_first(self):
        self.write(CORE_MD, "\n" + self.read(CORE_MD))
        self.assertPairs(self.check(), {("KZ-L002", ERROR)})


class SchemaShape(TreeCase):  # KZ-S001
    def test_missing_required_field(self):
        self.edit(CORE_MD, 'purpose: "Fixture skill used only by the structural tests."\n', "")
        report = self.check()
        self.assertPairs(report, {("KZ-S001", ERROR)})
        self.find(report, "KZ-S001", ERROR, file=CORE_MD, text="purpose")
        self.assertErrorExit(report)

    def test_version_that_is_not_semver_is_rejected(self):
        self.edit(CORE_MD, 'version: "0.1.0"', 'version: "1.0"')
        report = self.check()
        self.find(report, "KZ-S001", ERROR, file=CORE_MD, text="does not match")

    def test_unquoted_version_gets_a_quote_hint(self):
        self.edit(CORE_MD, 'version: "0.1.0"', "version: 1.0")
        report = self.check()
        self.assertPairs(report, {("KZ-S001", ERROR)})
        self.find(report, "KZ-S001", ERROR, file=CORE_MD, text="Quote the value")

    def test_empty_list_where_one_item_is_required(self):
        self.edit(SPEC_MD, 'scope:\n  - "Give the validator something to check."\n', "scope: []\n")
        self.assertPairs(self.check(), {("KZ-S001", ERROR)})

    def test_unknown_key_in_registry_is_an_error(self):
        self.edit(REGISTRY, 'path: "core/example-core-skill/"\n', 'path: "core/example-core-skill/"\n    depedencies: []\n')
        report = self.check()
        self.assertPairs(report, {("KZ-S001", ERROR)})
        self.find(report, "KZ-S001", ERROR, file=REGISTRY, text="depedencies")

    def test_unknown_key_in_compatibility_is_an_error(self):
        self.edit(COMPAT, 'rules:\n', 'extra_section: 1\nrules:\n')
        self.assertPairs(self.check(), {("KZ-S001", ERROR)})

    def test_registry_extension_key_is_accepted(self):
        self.edit(REGISTRY, 'path: "core/example-core-skill/"\n', 'path: "core/example-core-skill/"\n    x_note: "ok"\n')
        self.assertPairs(self.check(), set())

    def test_invalid_platform_name_in_compatibility(self):
        self.edit(COMPAT, "  exampleplatform:\n    status", "  Bad_Name:\n    status")
        self.assertIn(("KZ-S001", ERROR), self.pairs(self.check()))


class ReservedKeys(TreeCase):  # KZ-S002
    def test_persona_in_frontmatter(self):
        self.edit(CORE_MD, CLOSING, CLOSING.replace("\n---", '\npersona: "x"\n---'))
        report = self.check()
        self.assertPairs(report, {("KZ-S002", ERROR)})
        self.find(report, "KZ-S002", ERROR, file=CORE_MD, text="persona")
        self.assertErrorExit(report)

    def test_installed_in_frontmatter(self):
        self.edit(CORE_MD, CLOSING, CLOSING.replace("\n---", "\ninstalled: true\n---"))
        self.find(self.check(), "KZ-S002", ERROR, text="installed")

    def test_every_reserved_key_is_rejected_in_registry_files(self):
        for key in ("persona", "identity", "personality", "voice", "character",
                    "installed", "activated", "auto_install", "auto_activate"):
            for rel in (REGISTRY, COMPAT):
                with self.subTest(key=key, file=rel):
                    original = self.read(rel)
                    self.edit(rel, 'schema_version: "1.0"\n', f'schema_version: "1.0"\n{key}: true\n')
                    report = self.check()
                    self.assertPairs(report, {("KZ-S002", ERROR)})
                    self.find(report, "KZ-S002", ERROR, file=rel, text=key)
                    self.write(rel, original)


class UnknownFrontmatterKeys(TreeCase):  # KZ-S003
    def test_unknown_key_warns_and_never_blocks(self):
        self.edit(CORE_MD, CLOSING, CLOSING.replace("\n---", "\ncustom_field: 1\n---"))
        self.assertWarningOnly(self.check(), "KZ-S003", file=CORE_MD, text="custom_field")

    def test_x_prefixed_key_is_accepted(self):
        self.edit(CORE_MD, CLOSING, CLOSING.replace("\n---", "\nx_custom: 1\n---"))
        self.assertPairs(self.check(), set())


class SchemaVersion(TreeCase):  # KZ-S004 and KZ-S003 under a later minor version
    def test_absent_in_frontmatter_means_supported_version(self):
        self.assertNotIn("schema_version", self.read(CORE_MD))
        self.assertPairs(self.check(), set())

    def test_supported_version_declared_in_frontmatter(self):
        self.edit(CORE_MD, "id: example-core-skill\n", 'schema_version: "1.0"\nid: example-core-skill\n')
        self.assertPairs(self.check(), set())

    def test_absent_in_registry_file_is_an_error(self):
        self.edit(REGISTRY, 'schema_version: "1.0"\n', "")
        self.assertIn(("KZ-S001", ERROR), self.pairs(self.check()))

    def test_unquoted_schema_version_is_malformed(self):
        self.edit(REGISTRY, 'schema_version: "1.0"', "schema_version: 1.0")
        report = self.check()
        self.assertPairs(report, {("KZ-S001", ERROR)})
        self.find(report, "KZ-S001", ERROR, file=REGISTRY, text="Quote the value")

    def test_later_minor_warns_lists_unknown_fields_and_exits_zero(self):
        self.edit(REGISTRY, 'schema_version: "1.0"\n', 'schema_version: "1.1"\nfuture_section: {a: 1}\nx_ok: 1\n')
        report = self.check()
        self.assertPairs(report, {("KZ-S004", WARNING), ("KZ-S003", WARNING)})
        self.find(report, "KZ-S003", WARNING, file=REGISTRY, text="future_section")
        self.assertEqual(report.exit_code, 0)
        self.assertEqual(report.later_minor, [REGISTRY])
        code, out, _ = run_cli("--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertIn("later minor schema version", out)  # a pass is never read as full understanding

    def test_later_minor_in_frontmatter(self):
        self.edit(CORE_MD, "id: example-core-skill\n", 'schema_version: "1.7"\nid: example-core-skill\n')
        self.assertPairs(self.check(), {("KZ-S004", WARNING)})

    def test_later_minor_still_checks_known_rules(self):
        self.edit(REGISTRY, 'schema_version: "1.0"\n', 'schema_version: "1.1"\n')
        self.edit(REGISTRY, "version: \"0.1.0\"\n    status: draft\n    path: \"core", "version: \"nope\"\n    status: draft\n    path: \"core")
        self.assertIn(("KZ-S001", ERROR), self.pairs(self.check()))

    def test_different_major_is_an_error_and_skips_dependent_checks(self):
        for declared in ("2.0", "0.9"):
            with self.subTest(declared=declared):
                original = self.read(REGISTRY)
                self.edit(REGISTRY, 'schema_version: "1.0"', f'schema_version: "{declared}"')
                report = self.check()
                self.assertPairs(report, {("KZ-S004", ERROR)})
                self.find(report, "KZ-S004", ERROR, file=REGISTRY, text="not validated")
                skipped = {c for codes in report.skipped.values() for c in codes}
                self.assertTrue({"KZ-R001", "KZ-C001", "KZ-F001"} <= skipped)
                self.assertErrorExit(report)
                self.assertIn("Skipped checks", run_cli("--root", str(self.root))[1])
                self.write(REGISTRY, original)

    def test_different_major_in_frontmatter(self):
        self.edit(CORE_MD, "id: example-core-skill\n", 'schema_version: "2.0"\nid: example-core-skill\n')
        self.assertPairs(self.check(), {("KZ-S004", ERROR)})


if __name__ == "__main__":
    unittest.main()
