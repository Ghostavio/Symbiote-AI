import importlib.util
from pathlib import Path
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-kit.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_kit", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def create_minimal_valid_repo(root: Path, process_name: str = "demo") -> None:
    (root / "processes").mkdir(parents=True)
    (root / ".claude" / "skills" / process_name).mkdir(parents=True)
    (root / ".agents" / "skills" / process_name).mkdir(parents=True)
    (root / ".cursor" / "rules").mkdir(parents=True)
    (root / ".github").mkdir(parents=True)
    (root / "scripts").mkdir(parents=True)

    (root / "processes" / f"{process_name}.md").write_text(
        f"---\nname: {process_name}\ndescription: \"Demo process\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    skill_body = (
        f"---\nname: {process_name}\ndescription: \"Demo process\"\n---\n\n"
        f"Follow [`processes/{process_name}.md`](../../../processes/{process_name}.md).\n"
    )
    (root / ".claude" / "skills" / process_name / "SKILL.md").write_text(
        skill_body, encoding="utf-8"
    )
    (root / ".agents" / "skills" / process_name / "SKILL.md").write_text(
        skill_body, encoding="utf-8"
    )
    (root / ".cursor" / "rules" / f"{process_name}.mdc").write_text(
        f"---\ndescription: \"Demo process\"\n---\n\n"
        f"Follow `processes/{process_name}.md`.\n",
        encoding="utf-8",
    )
    (root / ".cursor" / "rules" / "PROJECT-REFERENCE-md.mdc").write_text(
        "---\ndescription:\nalwaysApply: true\n---\n\nRead project reference.\n",
        encoding="utf-8",
    )
    (root / "AGENTS.md").write_text(
        f"| `{process_name}` | [processes/{process_name}.md](processes/{process_name}.md) |\n",
        encoding="utf-8",
    )
    (root / "GEMINI.md").write_text(
        "See [`AGENTS.md`](AGENTS.md) and `.agents/skills/`.\n",
        encoding="utf-8",
    )
    (root / ".github" / "copilot-instructions.md").write_text(
        f"| `{process_name}` | [processes/{process_name}.md](../processes/{process_name}.md) |\n",
        encoding="utf-8",
    )
    script = root / "scripts" / "ok.sh"
    script.write_text("#!/usr/bin/env bash\nset -euo pipefail\necho ok\n", encoding="utf-8")
    script.chmod(0o755)


class ValidateKitTests(unittest.TestCase):
    def test_current_repository_passes_validation(self):
        errors = validator.validate_repo(REPO_ROOT)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_minimal_synthetic_repo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            self.assertEqual(validator.validate_repo(root), [])

    def test_detects_missing_wrappers_for_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            (root / "processes" / "orphan-canonical.md").write_text(
                "---\nname: orphan-canonical\ndescription: \"Missing wrappers\"\n---\n",
                encoding="utf-8",
            )
            errors = validator.validate_wrappers(root)
            joined = "\n".join(errors)
            self.assertIn(".claude/skills/orphan-canonical/SKILL.md", joined)
            self.assertIn(".agents/skills/orphan-canonical/SKILL.md", joined)
            self.assertIn(".cursor/rules/orphan-canonical.mdc", joined)
            self.assertIn("AGENTS.md: missing link to processes/orphan-canonical.md", joined)
            self.assertIn(
                ".github/copilot-instructions.md: missing link to ../processes/orphan-canonical.md",
                joined,
            )

    def test_detects_stale_wrapper_without_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            stale_dir = root / ".claude" / "skills" / "stale"
            stale_dir.mkdir(parents=True)
            (stale_dir / "SKILL.md").write_text(
                "---\nname: stale\ndescription: \"Stale\"\n---\n\nFollow processes/stale.md.\n",
                encoding="utf-8",
            )
            stale_agents = root / ".agents" / "skills" / "stale-agent"
            stale_agents.mkdir(parents=True)
            (stale_agents / "SKILL.md").write_text(
                "---\nname: stale-agent\ndescription: \"Stale\"\n---\n\nFollow processes/stale-agent.md.\n",
                encoding="utf-8",
            )
            errors = validator.validate_wrappers(root)
            joined = "\n".join(errors)
            self.assertIn("no matching canonical processes/stale.md", joined)
            self.assertIn("no matching canonical processes/stale-agent.md", joined)

    def test_detects_skill_wrappers_pointing_to_wrong_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root, "alpha")
            (root / "processes" / "beta.md").write_text(
                "---\nname: beta\ndescription: \"Beta\"\n---\n\n# Beta\n",
                encoding="utf-8",
            )
            wrong = (
                "---\nname: alpha\ndescription: \"Alpha\"\n---\n\n"
                "Follow [`processes/alpha.md`](../../../processes/beta.md).\n"
            )
            (root / ".claude" / "skills" / "alpha" / "SKILL.md").write_text(wrong, encoding="utf-8")
            (root / ".agents" / "skills" / "alpha" / "SKILL.md").write_text(wrong, encoding="utf-8")
            errors = validator.validate_wrappers(root)
            joined = "\n".join(errors)
            self.assertIn(".claude/skills/alpha/SKILL.md: must link directly to processes/alpha.md", joined)
            self.assertIn(".agents/skills/alpha/SKILL.md: must link directly to processes/alpha.md", joined)

    def test_detects_missing_or_unlinked_gemini_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            (root / "GEMINI.md").write_text("# Gemini\nNo link here.\n", encoding="utf-8")
            errors = validator.validate_wrappers(root)
            self.assertTrue(any("GEMINI.md: must link to AGENTS.md" in e for e in errors), errors)

    def test_detects_broken_and_root_relative_links_but_ignores_code_and_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            (root / "README.md").write_text(
                "\n".join(
                    [
                        "[ok](processes/demo.md)",
                        "[broken](missing.md)",
                        "[root](/processes/demo.md)",
                        "[placeholder](<file>.md)",
                        "Inline `[ignored](nope.md)`",
                        "<!-- [commented](nope.md) -->",
                        "```md",
                        "[fenced](nope.md)",
                        "```",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            errors = validator.validate_links(root)
            self.assertEqual(len(errors), 2, errors)
            self.assertTrue(any("broken local link 'missing.md'" in e for e in errors))
            self.assertTrue(any("root-relative link '/processes/demo.md'" in e for e in errors))

    def test_detects_shell_syntax_error_and_non_executable_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            bad = root / "scripts" / "broken.sh"
            bad.write_text("#!/usr/bin/env bash\nif true; then\n", encoding="utf-8")
            bad.chmod(0o644)
            errors = validator.validate_shell_scripts(root)
            joined = "\n".join(errors)
            self.assertIn("not executable", joined)
            self.assertIn("-n' failed", joined)

    def test_valid_alias_passes_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root, "simbiose")
            (root / "processes" / "scaffold.md").write_text(
                "---\nname: scaffold\nalias_of: simbiose\ndescription: \"Alias\"\n---\n\n"
                "Follow [`processes/simbiose.md`](simbiose.md).\n",
                encoding="utf-8",
            )
            alias_body = (
                "---\nname: scaffold\nalias_of: simbiose\ndescription: \"Alias\"\n---\n\n"
                "Follow [`processes/simbiose.md`](../../../processes/simbiose.md).\n"
            )
            for base in (root / ".claude" / "skills", root / ".agents" / "skills"):
                alias_skill = base / "scaffold"
                alias_skill.mkdir(parents=True)
                (alias_skill / "SKILL.md").write_text(alias_body, encoding="utf-8")
            (root / ".cursor" / "rules" / "scaffold.mdc").write_text(
                "---\nalias_of: simbiose\ndescription: \"Alias\"\n---\n\n"
                "Follow `processes/simbiose.md`.\n",
                encoding="utf-8",
            )
            self.assertEqual(validator.validate_repo(root), [])

    def test_detects_alias_pointing_to_missing_or_chained_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root, "simbiose")
            (root / "processes" / "scaffold.md").write_text(
                "---\nname: scaffold\nalias_of: simbiose\ndescription: \"Alias\"\n---\n\n"
                "Follow [`processes/simbiose.md`](simbiose.md).\n",
                encoding="utf-8",
            )
            (root / "processes" / "chained.md").write_text(
                "---\nname: chained\nalias_of: scaffold\ndescription: \"Chained\"\n---\n\n"
                "Follow [`processes/scaffold.md`](scaffold.md).\n",
                encoding="utf-8",
            )
            alias_skill = root / ".claude" / "skills" / "missing-alias"
            alias_skill.mkdir(parents=True)
            (alias_skill / "SKILL.md").write_text(
                "---\nname: missing-alias\nalias_of: ghost\ndescription: \"Broken\"\n---\n\n"
                "Follow [`processes/ghost.md`](../../../processes/ghost.md).\n",
                encoding="utf-8",
            )
            errors = validator.validate_wrappers(root)
            joined = "\n".join(errors)
            self.assertIn("processes/chained.md: alias_of 'scaffold'", joined)
            self.assertIn("missing-alias/SKILL.md: alias_of 'ghost'", joined)

    def test_detects_alias_wrapper_pointing_to_wrong_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root, "simbiose")
            (root / "processes" / "other.md").write_text(
                "---\nname: other\ndescription: \"Other\"\n---\n\n# Other\n",
                encoding="utf-8",
            )
            (root / "processes" / "scaffold.md").write_text(
                "---\nname: scaffold\nalias_of: simbiose\ndescription: \"Alias\"\n---\n\n"
                "Follow [`processes/simbiose.md`](simbiose.md).\n",
                encoding="utf-8",
            )
            alias_skill = root / ".agents" / "skills" / "scaffold"
            alias_skill.mkdir(parents=True)
            (alias_skill / "SKILL.md").write_text(
                "---\nname: scaffold\nalias_of: simbiose\ndescription: \"Alias\"\n---\n\n"
                "Follow [`processes/simbiose.md`](../../../processes/other.md).\n",
                encoding="utf-8",
            )
            errors = validator.validate_wrappers(root)
            self.assertTrue(
                any(
                    ".agents/skills/scaffold/SKILL.md: must link directly to processes/simbiose.md"
                    in e
                    for e in errors
                ),
                errors,
            )

    def test_detects_alias_target_mismatch_across_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root, "simbiose")
            (root / "processes" / "timesync.md").write_text(
                "---\nname: timesync\ndescription: \"Timesync\"\n---\n\n# Timesync\n",
                encoding="utf-8",
            )
            ts_body = (
                "---\nname: timesync\ndescription: \"Timesync\"\n---\n\n"
                "Follow [`processes/timesync.md`](../../../processes/timesync.md).\n"
            )
            for base in (root / ".claude" / "skills", root / ".agents" / "skills"):
                d = base / "timesync"
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(ts_body, encoding="utf-8")
            (root / ".cursor" / "rules" / "timesync.mdc").write_text(
                "---\ndescription: \"Timesync\"\n---\n\nFollow `processes/timesync.md`.\n",
                encoding="utf-8",
            )
            with (root / "AGENTS.md").open("a", encoding="utf-8") as f:
                f.write("| `timesync` | [processes/timesync.md](processes/timesync.md) |\n")
            with (root / ".github" / "copilot-instructions.md").open("a", encoding="utf-8") as f:
                f.write("| `timesync` | [processes/timesync.md](../processes/timesync.md) |\n")

            (root / "processes" / "scaffold.md").write_text(
                "---\nname: scaffold\nalias_of: simbiose\ndescription: \"Alias\"\n---\n\n"
                "Follow [`processes/simbiose.md`](simbiose.md).\n",
                encoding="utf-8",
            )
            (root / ".cursor" / "rules" / "scaffold.mdc").write_text(
                "---\nalias_of: simbiose\ndescription: \"Alias\"\n---\n\n"
                "Follow `processes/simbiose.md`.\n",
                encoding="utf-8",
            )
            mismatch_body = (
                "---\nname: scaffold\nalias_of: timesync\ndescription: \"Conflicting alias\"\n---\n\n"
                "Follow [`processes/timesync.md`](../../../processes/timesync.md).\n"
            )
            for base in (root / ".claude" / "skills", root / ".agents" / "skills"):
                d = base / "scaffold"
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(mismatch_body, encoding="utf-8")
            errors = validator.validate_wrappers(root)
            joined = "\n".join(errors)
            self.assertIn(
                ".claude/skills/scaffold/SKILL.md: alias_of 'timesync' disagrees with processes/scaffold.md (expected 'simbiose')",
                joined,
            )
            self.assertIn(
                ".agents/skills/scaffold/SKILL.md: alias_of 'timesync' disagrees with processes/scaffold.md (expected 'simbiose')",
                joined,
            )


if __name__ == "__main__":
    unittest.main()
