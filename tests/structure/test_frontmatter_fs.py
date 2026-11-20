"""KZ-F002, KZ-F003, KZ-R007, KZ-R010 and KZ-I001 (filesystem checks)."""

import os
import unittest

from support import CORE, CORE_MD, ERROR, REGISTRY, WARNING, TreeCase


class DirectoryNameEqualsId(TreeCase):  # KZ-F002
    def test_directory_differs_from_id(self):
        self.edit(CORE_MD, "id: example-core-skill", "id: renamed-skill")
        report = self.check()
        self.find(report, "KZ-F002", ERROR, file=CORE_MD, text="renamed-skill")
        self.assertErrorExit(report)

    def test_applies_to_every_skill_type(self):
        self.edit("specialist-skills/example-specialist-skill/SKILL.md", "id: example-specialist-skill", "id: other")
        self.find(self.check(), "KZ-F002", ERROR)


class NonEmptyBody(TreeCase):  # KZ-F003
    def test_empty_body_warns_and_never_blocks(self):
        text = self.read(CORE_MD)
        self.write(CORE_MD, text[:text.index("---\n", 4) + 4])
        self.assertWarningOnly(self.check(), "KZ-F003", file=CORE_MD)

    def test_whitespace_only_body_warns(self):
        text = self.read(CORE_MD)
        self.write(CORE_MD, text[:text.index("---\n", 4) + 4] + "\n   \n\n")
        self.assertWarningOnly(self.check(), "KZ-F003", file=CORE_MD)


class RegisteredPathsResolve(TreeCase):  # KZ-R007
    def test_missing_documentation_file(self):
        self.delete(CORE_MD)
        report = self.check()
        self.assertPairs(report, {("KZ-R007", ERROR)})
        self.find(report, "KZ-R007", ERROR, file=REGISTRY, text="does not exist")
        self.assertErrorExit(report)

    def test_wrong_letter_case(self):
        self.edit(REGISTRY, 'documentation: "core/example-core-skill/SKILL.md"', 'documentation: "core/example-core-skill/skill.md"')
        report = self.check()
        self.assertPairs(report, {("KZ-R007", ERROR)})
        self.find(report, "KZ-R007", ERROR, text="letter case")

    def test_wrong_letter_case_in_a_directory_component(self):
        self.edit(REGISTRY, 'path: "core/example-core-skill/"', 'path: "Core/example-core-skill/"')
        self.find(self.check(), "KZ-R007", ERROR, text="letter case")

    def test_path_outside_the_repository(self):
        for value in ("../outside.md", "/etc/passwd", "C:\\\\x.md"):
            with self.subTest(value=value):
                original = self.read(REGISTRY)
                self.edit(REGISTRY, 'documentation: "core/example-core-skill/SKILL.md"', f'documentation: "{value}"')
                self.find(self.check(), "KZ-R007", ERROR, text="outside this repository")
                self.write(REGISTRY, original)

    def test_symlink_that_escapes_the_repository(self):
        outside = self.root.parent / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        try:
            os.symlink(outside, self.root / "core" / "escape.md")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are not available here")
        self.edit(REGISTRY, 'documentation: "core/example-core-skill/SKILL.md"', 'documentation: "core/escape.md"')
        self.find(self.check(), "KZ-R007", ERROR, text="outside this repository")


class SkillDirectoriesAreRegistered(TreeCase):  # KZ-R010
    def test_unregistered_skill_directory(self):
        self.write("core/unlisted-skill/SKILL.md", self.read(CORE_MD).replace("example-core-skill", "unlisted-skill"))
        report = self.check()
        self.assertPairs(report, {("KZ-R010", ERROR)})
        self.find(report, "KZ-R010", ERROR, file="core/unlisted-skill/SKILL.md", text="unlisted-skill")
        self.assertErrorExit(report)

    def test_tests_directory_is_never_scanned_for_skills_or_links(self):
        self.write("tests/some-fixture/SKILL.md", "no frontmatter here\n")
        self.write("tests/notes.md", "[broken](missing.md)\n")
        self.assertPairs(self.check(), set())

    def test_only_directories_directly_under_type_directories_are_skills(self):
        self.write("core/example-core-skill/nested/deeper/SKILL.md", "no frontmatter\n")
        self.write("docs/SKILL.md", "no frontmatter\n")
        self.assertPairs(self.check(), set())


class RelativeLinks(TreeCase):  # KZ-I001
    def test_broken_relative_link_warns_and_never_blocks(self):
        self.write("docs/guide.md", "See [the missing page](missing.md).\n")
        self.assertWarningOnly(self.check(), "KZ-I001", file="docs/guide.md", text="missing.md")

    def test_broken_image_link_warns(self):
        self.write("docs/guide.md", "![diagram](img/none.png)\n")
        self.assertWarningOnly(self.check(), "KZ-I001", file="docs/guide.md")

    def test_valid_and_ignored_links_produce_nothing(self):
        self.write("docs/other.md", "Target.\n")
        self.write("docs/guide.md", "\n".join([
            "[ok](other.md) [ok with anchor](other.md#top) [anchor only](#local)",
            "[web](https://example.invalid/x) [mail](mailto:a@b.invalid) [protocol-relative](//example.invalid/x)",
            "[root relative](/docs/other.md) [up](../registry/skills.yaml)",
            "`[inline code](nope.md)`",
            "```", "[fenced](nope.md)", "```",
            "[titled](other.md \"Title\")",
        ]) + "\n")
        self.assertPairs(self.check(), set())

    def test_wrong_case_link_warns(self):
        self.write("docs/other.md", "Target.\n")
        self.write("docs/guide.md", "[x](Other.md)\n")
        self.assertWarningOnly(self.check(), "KZ-I001", file="docs/guide.md")

    def test_link_escaping_the_repository_warns(self):
        self.write("docs/guide.md", "[x](../../outside.md)\n")
        self.assertWarningOnly(self.check(), "KZ-I001", file="docs/guide.md")


if __name__ == "__main__":
    unittest.main()
