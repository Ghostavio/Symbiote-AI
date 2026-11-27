import importlib.util
import json
from pathlib import Path
import re
import shutil
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

    def test_installed_layout_from_simbiose_passes_validation(self):
        simbiose_text = (REPO_ROOT / "processes" / "simbiose.md").read_text(encoding="utf-8")
        match = re.search(
            r"## Passo 3 — Instalar o kit no projeto novo.*?```\n(.*?)\n```",
            simbiose_text,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "Could not locate Step 3 install layout in processes/simbiose.md")
        entries = match.group(1).split()
        self.assertTrue(entries, "Step 3 install layout is empty")
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp)
            for rel in entries:
                clean = rel.rstrip("/")
                src = REPO_ROOT / clean
                self.assertTrue(src.exists(), f"Documented install path does not exist: {rel}")
                target = dst / clean
                if src.is_dir():
                    shutil.copytree(src, target)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, target)
            errors = validator.validate_repo(dst)
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

    def test_valid_adapter_passes_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            adapter_dir = root / "adapters" / "stacks" / "sample-stack"
            skill_dir = adapter_dir / "skills" / "sample-helper"
            skill_dir.mkdir(parents=True)
            (root / "adapters" / "README.md").write_text("# Adapters\n", encoding="utf-8")
            (adapter_dir / "conventions.md").write_text("# Conventions\n", encoding="utf-8")
            (adapter_dir / "review-checks.md").write_text("# Checks\n", encoding="utf-8")
            (adapter_dir / "editor-settings.json").write_text(
                json.dumps({"editor.formatOnSave": True}), encoding="utf-8"
            )
            (skill_dir / "SKILL.md").write_text(
                "---\nname: sample-helper\ndescription: \"Helper skill\"\n---\n\n# Helper\n",
                encoding="utf-8",
            )
            (adapter_dir / "adapter.json").write_text(
                json.dumps(
                    {
                        "id": "sample-stack",
                        "name": "Sample Stack",
                        "category": "stack",
                        "version": "1.0.0",
                        "description": "Sample stack adapter",
                        "detect": {"files": ["sample.config.json"], "packages": ["sample-pkg"]},
                        "commands": {"test": "sample test"},
                        "files": {
                            "conventions": "conventions.md",
                            "review_checks": "review-checks.md",
                            "editor_settings": "editor-settings.json",
                            "skills": ["skills/sample-helper"],
                        },
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(validator.validate_repo(root), [])

    def test_detects_invalid_adapter_manifest_and_category_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            (root / "adapters" / "unknown-axis").mkdir(parents=True)
            adapter_dir = root / "adapters" / "cloud" / "demo-cloud"
            adapter_dir.mkdir(parents=True)
            (adapter_dir / "conventions.md").write_text("# Conventions\n", encoding="utf-8")
            (adapter_dir / "review-checks.md").write_text("# Checks\n", encoding="utf-8")
            (adapter_dir / "adapter.json").write_text(
                json.dumps(
                    {
                        "id": "wrong-id",
                        "name": "Demo Cloud",
                        "category": "stack",
                        "description": "Mismatched category and empty detect",
                        "detect": {"files": []},
                        "files": {
                            "conventions": "conventions.md",
                            "review_checks": "review-checks.md",
                        },
                    }
                ),
                encoding="utf-8",
            )
            errors = validator.validate_adapters(root)
            joined = "\n".join(errors)
            self.assertIn("adapters/unknown-axis: unsupported category directory", joined)
            self.assertIn("id 'wrong-id' does not match directory 'demo-cloud'", joined)
            self.assertIn("category 'stack' does not match parent directory 'cloud'", joined)
            self.assertIn("detect must declare at least one signal", joined)

    def test_detects_missing_or_escaping_adapter_files_and_bad_editor_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            adapter_dir = root / "adapters" / "observability" / "otel"
            adapter_dir.mkdir(parents=True)
            (root / "adapters" / "escape.md").write_text("# Outside\n", encoding="utf-8")
            (adapter_dir / "editor-settings.json").write_text("{not valid json", encoding="utf-8")
            (adapter_dir / "adapter.json").write_text(
                json.dumps(
                    {
                        "id": "otel",
                        "name": "OpenTelemetry",
                        "category": "observability",
                        "description": "Broken file references",
                        "detect": {"packages": ["@opentelemetry/api"]},
                        "files": {
                            "conventions": "../../escape.md",
                            "review_checks": "missing.md",
                            "editor_settings": "editor-settings.json",
                        },
                    }
                ),
                encoding="utf-8",
            )
            errors = validator.validate_adapters(root)
            joined = "\n".join(errors)
            self.assertIn("files.conventions must be a non-symlink relative path inside the adapter directory", joined)
            self.assertIn("files.review_checks target 'missing.md' does not exist", joined)
            self.assertIn("editor-settings.json: invalid JSON", joined)

    def test_detects_symlink_escaping_adapter_or_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as external_tmp:
            root = Path(tmp)
            external = Path(external_tmp)
            create_minimal_valid_repo(root)

            # Case 1: external adapter dir linked into adapters/stacks/
            ext_adapter = external / "ext-stack"
            ext_adapter.mkdir()
            (ext_adapter / "conventions.md").write_text("# External\n", encoding="utf-8")
            (ext_adapter / "review-checks.md").write_text("# External\n", encoding="utf-8")
            (ext_adapter / "adapter.json").write_text(
                json.dumps(
                    {
                        "id": "ext-stack",
                        "name": "External Stack",
                        "category": "stack",
                        "description": "Symlinked outside repo",
                        "detect": {"files": ["ext.json"]},
                        "files": {
                            "conventions": "conventions.md",
                            "review_checks": "review-checks.md",
                        },
                    }
                ),
                encoding="utf-8",
            )
            stacks_dir = root / "adapters" / "stacks"
            stacks_dir.mkdir(parents=True)
            (stacks_dir / "ext-stack").symlink_to(ext_adapter)

            # Case 2: real adapter dir containing a symlinked file escaping to external dir
            real_adapter = stacks_dir / "real-stack"
            real_adapter.mkdir()
            ext_file = external / "secret.md"
            ext_file.write_text("# Secret\n", encoding="utf-8")
            (real_adapter / "conventions.md").symlink_to(ext_file)
            (real_adapter / "review-checks.md").write_text("# Checks\n", encoding="utf-8")
            (real_adapter / "adapter.json").write_text(
                json.dumps(
                    {
                        "id": "real-stack",
                        "name": "Real Stack",
                        "category": "stack",
                        "description": "Has symlinked file",
                        "detect": {"files": ["real.json"]},
                        "files": {
                            "conventions": "conventions.md",
                            "review_checks": "review-checks.md",
                        },
                    }
                ),
                encoding="utf-8",
            )

            errors = validator.validate_adapters(root)
            joined = "\n".join(errors)
            self.assertIn("adapters/stacks/ext-stack: symlinks are not allowed for adapter directories", joined)
            self.assertIn(
                "adapters/stacks/real-stack/adapter.json: files.conventions must be a non-symlink relative path inside the adapter directory",
                joined,
            )

    def test_installed_adapter_skill_via_canonical_and_thin_wrappers_passes_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            adapter_dir = root / "adapters" / "cloud" / "demo-cloud"
            skill_src = adapter_dir / "skills" / "demo-deploy"
            skill_src.mkdir(parents=True)
            (adapter_dir / "conventions.md").write_text("# Cloud\n", encoding="utf-8")
            (adapter_dir / "review-checks.md").write_text("# Checks\n", encoding="utf-8")
            skill_body = (
                "---\nname: demo-deploy\ndescription: \"Deploy helper\"\n---\n\n"
                "# Demo Deploy\n"
            )
            (skill_src / "SKILL.md").write_text(skill_body, encoding="utf-8")
            (adapter_dir / "adapter.json").write_text(
                json.dumps(
                    {
                        "id": "demo-cloud",
                        "name": "Demo Cloud",
                        "category": "cloud",
                        "description": "Cloud adapter with optional skill",
                        "detect": {"files": ["cloud.toml"]},
                        "files": {
                            "conventions": "conventions.md",
                            "review_checks": "review-checks.md",
                            "skills": ["skills/demo-deploy"],
                        },
                    }
                ),
                encoding="utf-8",
            )
            # Install adapter skill following source-of-truth convention: canonical + thin wrappers
            (root / "processes" / "demo-deploy.md").write_text(skill_body, encoding="utf-8")
            wrapper = (
                "---\nname: demo-deploy\ndescription: \"Deploy helper\"\n---\n\n"
                "Follow [`processes/demo-deploy.md`](../../../processes/demo-deploy.md).\n"
            )
            for base in (root / ".claude" / "skills", root / ".agents" / "skills"):
                d = base / "demo-deploy"
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(wrapper, encoding="utf-8")
            (root / ".cursor" / "rules" / "demo-deploy.mdc").write_text(
                "---\ndescription: \"Deploy helper\"\n---\n\nFollow `processes/demo-deploy.md`.\n",
                encoding="utf-8",
            )
            with (root / "AGENTS.md").open("a", encoding="utf-8") as f:
                f.write("| `demo-deploy` | [processes/demo-deploy.md](processes/demo-deploy.md) |\n")
            with (root / ".github" / "copilot-instructions.md").open("a", encoding="utf-8") as f:
                f.write("| `demo-deploy` | [processes/demo-deploy.md](../processes/demo-deploy.md) |\n")

            self.assertEqual(validator.validate_repo(root), [])

    def test_installed_layout_with_selected_adapter_passes_validation(self):
        simbiose_text = (REPO_ROOT / "processes" / "simbiose.md").read_text(encoding="utf-8")
        match = re.search(
            r"## Passo 3 — Instalar o kit no projeto novo.*?```\n(.*?)\n```",
            simbiose_text,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        entries = match.group(1).split()
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp)
            for rel in entries:
                clean = rel.rstrip("/")
                src = REPO_ROOT / clean
                target = dst / clean
                if src.is_dir():
                    shutil.copytree(src, target)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, target)
            shutil.copytree(
                REPO_ROOT / "adapters" / "stacks" / "angular",
                dst / "adapters" / "stacks" / "angular",
            )
            errors = validator.validate_repo(dst)
            self.assertEqual(errors, [], "\n".join(errors))

    def test_adapter_with_custom_file_paths_passes_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root)
            adapter_dir = root / "adapters" / "stacks" / "custom-stack"
            (adapter_dir / "docs").mkdir(parents=True)
            (adapter_dir / "checks").mkdir(parents=True)
            (adapter_dir / "presets").mkdir(parents=True)
            (adapter_dir / "docs" / "guidelines.md").write_text("# Guidelines\n", encoding="utf-8")
            (adapter_dir / "checks" / "review.md").write_text("# Review\n", encoding="utf-8")
            (adapter_dir / "presets" / "cursor.json").write_text(
                json.dumps({"editor.tabSize": 2}), encoding="utf-8"
            )
            (adapter_dir / "adapter.json").write_text(
                json.dumps(
                    {
                        "id": "custom-stack",
                        "name": "Custom Stack",
                        "category": "stack",
                        "description": "Adapter using custom relative file paths",
                        "detect": {"files": ["custom.toml"]},
                        "files": {
                            "conventions": "docs/guidelines.md",
                            "review_checks": "checks/review.md",
                            "editor_settings": "presets/cursor.json",
                        },
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(validator.validate_repo(root), [])

    def test_detects_adapter_skill_name_collisions_across_adapters_and_existing_processes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_minimal_valid_repo(root, "demo")

            for cat_dir, cat_name, adapter_id, skill_name in (
                ("cloud", "cloud", "cloud-a", "shared-deploy"),
                ("observability", "observability", "obs-b", "shared-deploy"),
                ("stacks", "stack", "stack-c", "demo"),
            ):
                adapter_dir = root / "adapters" / cat_dir / adapter_id
                skill_dir = adapter_dir / "skills" / skill_name
                skill_dir.mkdir(parents=True)
                (adapter_dir / "conventions.md").write_text("# Conv\n", encoding="utf-8")
                (adapter_dir / "review-checks.md").write_text("# Checks\n", encoding="utf-8")
                (skill_dir / "SKILL.md").write_text(
                    f"---\nname: {skill_name}\ndescription: \"Skill {skill_name}\"\n---\n\n# {skill_name}\n",
                    encoding="utf-8",
                )
                (adapter_dir / "adapter.json").write_text(
                    json.dumps(
                        {
                            "id": adapter_id,
                            "name": adapter_id,
                            "category": cat_name,
                            "description": "Collision test adapter",
                            "detect": {"files": [f"{adapter_id}.cfg"]},
                            "files": {
                                "conventions": "conventions.md",
                                "review_checks": "review-checks.md",
                                "skills": [f"skills/{skill_name}"],
                            },
                        }
                    ),
                    encoding="utf-8",
                )

            validator_errors = validator.validate_adapters(root)
            self.assertTrue(
                any(
                    "skill name 'shared-deploy' collides with" in err
                    for err in validator_errors
                ),
                validator_errors,
            )

            plan_collisions = validator.find_adapter_skill_collisions(root)
            joined = "\n".join(plan_collisions)
            self.assertIn("skill name 'shared-deploy' collides with", joined)
            self.assertIn("skill name 'demo' collides with existing processes/demo.md", joined)


if __name__ == "__main__":
    unittest.main()
