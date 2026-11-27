#!/usr/bin/env python3
"""Validate repository consistency for Symbiote-AI.

Checks:
1. Wrapper parity & target integrity across:
   - processes/<name>.md (canonical procedures, plus optional alias_of redirects)
   - .claude/skills/<name>/SKILL.md (Claude Code)
   - .agents/skills/<name>/SKILL.md (Antigravity, Gemini CLI, Codex, Agent Skills)
   - .cursor/rules/<name>.mdc (excluding alwaysApply context rules)
   - AGENTS.md and GEMINI.md (including Antigravity's 24 KB per-file rule cap)
   - .github/copilot-instructions.md
2. Local relative markdown links across all .md and .mdc files.
3. Shell scripts under scripts/ and .claude/integrations/: shebang, executable
   bit, and bash syntax check (bash -n, plus /bin/bash -n when available).
4. Optional adapters under adapters/<category>/<id>/: manifest schema, matching
   category/id, detection signals, referenced files, and optional JSON/skills.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
FENCED_CODE_RE = re.compile(r"(^|\n)([`~]{3,})[^\n]*\n.*?\n\2[ \t]*(?=\n|\Z)", re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")
MAX_RULE_BYTES = 24_000
ADAPTER_CATEGORIES = {
    "stacks": "stack",
    "cloud": "cloud",
    "observability": "observability",
}
ADAPTER_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ADAPTER_DETECT_KEYS = ("files", "packages", "directories")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def strip_non_link_regions(text: str) -> str:
    text = FENCED_CODE_RE.sub("\n", text)
    text = HTML_COMMENT_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def extract_local_links(text: str) -> list[str]:
    cleaned = strip_non_link_regions(text)
    links: list[str] = []
    for match in MD_LINK_RE.finditer(cleaned):
        raw = match.group(1).strip()
        if not raw or raw.startswith("#") or raw.startswith(EXTERNAL_PREFIXES):
            continue
        if "<" in raw and ">" in raw:
            continue
        links.append(raw)
    return links


def _resolved_local_targets(source_file: Path, content: str) -> set[Path]:
    return {
        (source_file.parent / target.split("#", 1)[0]).resolve()
        for target in extract_local_links(content)
        if target.split("#", 1)[0] and not target.startswith("/")
    }


def _validate_skill_dir(
    skills_dir: Path,
    rel_prefix: str,
    label: str,
    canonicals: dict[str, Path],
    canonical_aliases: dict[str, tuple[Path, str, str]],
    valid_aliases: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    found: set[str] = set()
    aliases_found: set[str] = set()

    if not skills_dir.is_dir():
        return [f"Missing required directory: {rel_prefix}/"]

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_name = skill_dir.name
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{rel_prefix}/{skill_name}: missing SKILL.md")
            continue
        content = skill_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        if not fm or fm.get("name") != skill_name or not fm.get("description"):
            errors.append(
                f"{rel_prefix}/{skill_name}/SKILL.md: invalid or incomplete frontmatter"
            )
            continue

        alias_of = fm.get("alias_of", "").strip()
        if alias_of:
            if skill_name not in canonical_aliases:
                errors.append(
                    f"{rel_prefix}/{skill_name}/SKILL.md: alias_of '{alias_of}' "
                    f"has no canonical alias processes/{skill_name}.md"
                )
                continue
            canonical_target = canonical_aliases[skill_name][1]
            if alias_of != canonical_target:
                errors.append(
                    f"{rel_prefix}/{skill_name}/SKILL.md: alias_of '{alias_of}' "
                    f"disagrees with processes/{skill_name}.md (expected '{canonical_target}')"
                )
                continue
            if canonical_target not in canonicals:
                continue
            aliases_found.add(skill_name)
            expected_rel = f"processes/{canonical_target}.md"
            expected_target = canonicals[canonical_target].resolve()
            if expected_target not in _resolved_local_targets(skill_file, content):
                errors.append(
                    f"{rel_prefix}/{skill_name}/SKILL.md: must link directly to {expected_rel}"
                )
        else:
            expected_rel = f"processes/{skill_name}.md"
            if skill_name in canonical_aliases:
                canonical_target = canonical_aliases[skill_name][1]
                errors.append(
                    f"{rel_prefix}/{skill_name}/SKILL.md: must declare "
                    f"alias_of: {canonical_target} to match processes/{skill_name}.md"
                )
            elif skill_name not in canonicals:
                errors.append(
                    f"{rel_prefix}/{skill_name}/SKILL.md: no matching canonical {expected_rel}"
                )
            else:
                found.add(skill_name)
                expected_target = canonicals[skill_name].resolve()
                if expected_target not in _resolved_local_targets(skill_file, content):
                    errors.append(
                        f"{rel_prefix}/{skill_name}/SKILL.md: must link directly to {expected_rel}"
                    )

    for name in sorted(canonicals):
        if name not in found:
            errors.append(f"Missing {label} wrapper: {rel_prefix}/{name}/SKILL.md")
    for alias_name in sorted(valid_aliases):
        if alias_name not in aliases_found:
            errors.append(f"Missing {label} alias wrapper: {rel_prefix}/{alias_name}/SKILL.md")

    return errors


def validate_wrappers(root: Path) -> list[str]:
    errors: list[str] = []
    processes_dir = root / "processes"
    claude_skills_dir = root / ".claude" / "skills"
    agents_skills_dir = root / ".agents" / "skills"
    cursor_rules_dir = root / ".cursor" / "rules"
    agents_file = root / "AGENTS.md"
    gemini_file = root / "GEMINI.md"
    copilot_file = root / ".github" / "copilot-instructions.md"

    if not processes_dir.is_dir():
        return ["Missing required directory: processes/"]

    canonicals: dict[str, Path] = {}
    canonical_aliases: dict[str, tuple[Path, str, str]] = {}
    for md_file in sorted(processes_dir.glob("*.md")):
        name = md_file.stem
        content = md_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        if not fm:
            errors.append(f"processes/{md_file.name}: missing YAML frontmatter")
            continue
        if fm.get("name") != name:
            errors.append(
                f"processes/{md_file.name}: frontmatter name '{fm.get('name', '')}' "
                f"does not match filename '{name}'"
            )
        if not fm.get("description"):
            errors.append(f"processes/{md_file.name}: missing frontmatter description")

        alias_of = fm.get("alias_of", "").strip()
        if alias_of:
            canonical_aliases[name] = (md_file, alias_of, content)
        else:
            canonicals[name] = md_file

    # Validate canonical alias_of entries point directly to a primary canonical
    valid_aliases: dict[str, str] = {}
    for alias_name, (alias_file, target_name, content) in sorted(canonical_aliases.items()):
        if target_name not in canonicals:
            errors.append(
                f"processes/{alias_file.name}: alias_of '{target_name}' does not point "
                f"to a primary canonical processes/{target_name}.md"
            )
        else:
            valid_aliases[alias_name] = target_name
            expected_target = canonicals[target_name].resolve()
            if expected_target not in _resolved_local_targets(alias_file, content):
                errors.append(
                    f"processes/{alias_file.name}: alias must link directly to "
                    f"processes/{target_name}.md"
                )

    # Skill wrappers: Claude Code (.claude/skills) and open Agent Skills (.agents/skills)
    errors.extend(
        _validate_skill_dir(
            claude_skills_dir,
            ".claude/skills",
            "Claude Code",
            canonicals,
            canonical_aliases,
            valid_aliases,
        )
    )
    errors.extend(
        _validate_skill_dir(
            agents_skills_dir,
            ".agents/skills",
            "Agent Skills",
            canonicals,
            canonical_aliases,
            valid_aliases,
        )
    )

    # Cursor rule wrappers
    cursor_found: set[str] = set()
    cursor_aliases_found: set[str] = set()
    if cursor_rules_dir.is_dir():
        for rule_file in sorted(cursor_rules_dir.glob("*.mdc")):
            content = rule_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            if fm is None:
                errors.append(f".cursor/rules/{rule_file.name}: missing frontmatter")
                continue
            if fm.get("alwaysApply", "").lower() == "true":
                continue
            rule_name = rule_file.stem
            if not fm.get("description"):
                errors.append(f".cursor/rules/{rule_file.name}: missing frontmatter description")

            alias_of = fm.get("alias_of", "").strip()
            if alias_of:
                if rule_name not in canonical_aliases:
                    errors.append(
                        f".cursor/rules/{rule_file.name}: alias_of '{alias_of}' "
                        f"has no canonical alias processes/{rule_name}.md"
                    )
                    continue
                canonical_target = canonical_aliases[rule_name][1]
                if alias_of != canonical_target:
                    errors.append(
                        f".cursor/rules/{rule_file.name}: alias_of '{alias_of}' "
                        f"disagrees with processes/{rule_name}.md (expected '{canonical_target}')"
                    )
                    continue
                if canonical_target not in canonicals:
                    continue
                cursor_aliases_found.add(rule_name)
                expected_rel = f"processes/{canonical_target}.md"
                if expected_rel not in content:
                    errors.append(
                        f".cursor/rules/{rule_file.name}: does not reference {expected_rel}"
                    )
            else:
                expected_rel = f"processes/{rule_name}.md"
                if rule_name in canonical_aliases:
                    canonical_target = canonical_aliases[rule_name][1]
                    errors.append(
                        f".cursor/rules/{rule_file.name}: must declare "
                        f"alias_of: {canonical_target} to match processes/{rule_name}.md"
                    )
                elif rule_name not in canonicals:
                    errors.append(
                        f".cursor/rules/{rule_file.name}: no matching canonical {expected_rel}"
                    )
                else:
                    cursor_found.add(rule_name)
                    if expected_rel not in content:
                        errors.append(
                            f".cursor/rules/{rule_file.name}: does not reference {expected_rel}"
                        )
    else:
        errors.append("Missing required directory: .cursor/rules/")

    agents_text = agents_file.read_text(encoding="utf-8") if agents_file.is_file() else ""
    if not agents_file.is_file():
        errors.append("Missing required file: AGENTS.md")
    elif agents_file.stat().st_size > MAX_RULE_BYTES:
        errors.append(
            f"AGENTS.md: exceeds Antigravity {MAX_RULE_BYTES}-byte per-file rule cap"
        )

    if not gemini_file.is_file():
        errors.append("Missing required file: GEMINI.md")
    else:
        gemini_text = gemini_file.read_text(encoding="utf-8")
        if gemini_file.stat().st_size > MAX_RULE_BYTES:
            errors.append(
                f"GEMINI.md: exceeds Antigravity {MAX_RULE_BYTES}-byte per-file rule cap"
            )
        if agents_file.is_file() and agents_file.resolve() not in _resolved_local_targets(
            gemini_file, gemini_text
        ):
            errors.append("GEMINI.md: must link to AGENTS.md")

    copilot_text = copilot_file.read_text(encoding="utf-8") if copilot_file.is_file() else ""
    if not copilot_file.is_file():
        errors.append("Missing required file: .github/copilot-instructions.md")

    for name in sorted(canonicals):
        if name not in cursor_found:
            errors.append(f"Missing Cursor wrapper: .cursor/rules/{name}.mdc")
        if agents_file.is_file() and f"(processes/{name}.md)" not in agents_text:
            errors.append(f"AGENTS.md: missing link to processes/{name}.md")
        if copilot_file.is_file() and f"(../processes/{name}.md)" not in copilot_text:
            errors.append(
                f".github/copilot-instructions.md: missing link to ../processes/{name}.md"
            )

    for alias_name in sorted(valid_aliases):
        if alias_name not in cursor_aliases_found:
            errors.append(f"Missing Cursor alias wrapper: .cursor/rules/{alias_name}.mdc")

    return errors


def validate_links(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.suffix not in (".md", ".mdc"):
            continue
        rel_file = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for target in extract_local_links(text):
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            if target_path.startswith("/"):
                errors.append(
                    f"{rel_file}: root-relative link '{target}' should be relative"
                )
                continue
            resolved = (path.parent / target_path).resolve()
            if not resolved.exists():
                errors.append(f"{rel_file}: broken local link '{target}'")
    return errors


def _bash_interpreters() -> list[str]:
    interpreters: list[str] = []
    found_bash = shutil.which("bash")
    if found_bash:
        interpreters.append(found_bash)
    if Path("/bin/bash").is_file() and "/bin/bash" not in interpreters:
        interpreters.append("/bin/bash")
    return interpreters


def validate_shell_scripts(root: Path) -> list[str]:
    errors: list[str] = []
    search_roots = [root / "scripts", root / ".claude" / "integrations"]
    interpreters = _bash_interpreters()
    if not interpreters:
        return ["No bash interpreter found to validate shell scripts"]

    scripts: list[Path] = []
    for base in search_roots:
        if base.is_dir():
            scripts.extend(sorted(base.rglob("*.sh")))

    for script in scripts:
        rel_script = script.relative_to(root).as_posix()
        first_line = script.read_text(encoding="utf-8").splitlines()[:1]
        if not first_line or not first_line[0].startswith("#!"):
            errors.append(f"{rel_script}: missing shebang line")
        if not os.access(script, os.X_OK):
            errors.append(f"{rel_script}: file is not executable (chmod +x)")
        for bash_bin in interpreters:
            result = subprocess.run(
                [bash_bin, "-n", str(script)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                detail = result.stderr.strip() or result.stdout.strip()
                errors.append(f"{rel_script}: '{bash_bin} -n' failed: {detail}")
    return errors


def _has_symlink_component(base: Path, rel: Path) -> bool:
    current = base
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _resolve_inside_adapter(root: Path, adapter_dir: Path, rel_path: object) -> Path | None:
    if not isinstance(rel_path, str) or not rel_path.strip():
        return None
    candidate = Path(rel_path)
    if candidate.is_absolute():
        return None
    if _has_symlink_component(adapter_dir, candidate):
        return None
    repo_root = root.resolve()
    adapter_root = adapter_dir.resolve()
    if not adapter_root.is_relative_to(repo_root):
        return None
    resolved = (adapter_root / candidate).resolve()
    if (
        not resolved.is_relative_to(adapter_root)
        or not resolved.is_relative_to(repo_root)
        or resolved == adapter_root
    ):
        return None
    return resolved


def validate_adapters(root: Path) -> list[str]:
    errors: list[str] = []
    seen_adapter_skills: dict[str, str] = {}
    repo_root = root.resolve()
    adapters_dir = root / "adapters"
    if not adapters_dir.exists() and not adapters_dir.is_symlink():
        return []
    if adapters_dir.is_symlink():
        return ["adapters: symlinks are not allowed for adapters directory"]
    if not adapters_dir.is_dir():
        return ["adapters: expected a directory"]

    for entry in sorted(adapters_dir.iterdir()):
        if entry.is_symlink():
            errors.append(
                f"adapters/{entry.name}: symlinks are not allowed inside adapters/"
            )
            continue
        if entry.is_file():
            if entry.name != "README.md":
                errors.append(
                    f"adapters/{entry.name}: unexpected file (only README.md and category directories are allowed)"
                )
            continue
        if entry.name not in ADAPTER_CATEGORIES:
            errors.append(
                f"adapters/{entry.name}: unsupported category directory "
                f"(expected one of {', '.join(sorted(ADAPTER_CATEGORIES))})"
            )
            continue

        expected_category = ADAPTER_CATEGORIES[entry.name]
        for adapter_dir in sorted(entry.iterdir()):
            rel_adapter = adapter_dir.relative_to(root).as_posix()
            if adapter_dir.is_symlink():
                errors.append(
                    f"{rel_adapter}: symlinks are not allowed for adapter directories"
                )
                continue
            if adapter_dir.is_file():
                if adapter_dir.name != "README.md":
                    errors.append(
                        f"{rel_adapter}: unexpected file inside category directory"
                    )
                continue
            if not adapter_dir.resolve().is_relative_to(repo_root):
                errors.append(
                    f"{rel_adapter}: adapter directory resolves outside repository root"
                )
                continue
            if not ADAPTER_ID_RE.match(adapter_dir.name):
                errors.append(
                    f"{rel_adapter}: invalid adapter id '{adapter_dir.name}' (use lowercase kebab-case)"
                )

            manifest_path = adapter_dir / "adapter.json"
            rel_manifest = manifest_path.relative_to(root).as_posix()
            if manifest_path.is_symlink():
                errors.append(f"{rel_manifest}: symlinks are not allowed for adapter.json")
                continue
            if not manifest_path.is_file():
                errors.append(f"{rel_adapter}: missing adapter.json")
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{rel_manifest}: invalid JSON ({exc.msg})")
                continue
            if not isinstance(manifest, dict):
                errors.append(f"{rel_manifest}: manifest must be a JSON object")
                continue

            adapter_id = manifest.get("id")
            if adapter_id != adapter_dir.name:
                errors.append(
                    f"{rel_manifest}: id '{adapter_id}' does not match directory '{adapter_dir.name}'"
                )
            if manifest.get("category") != expected_category:
                errors.append(
                    f"{rel_manifest}: category '{manifest.get('category')}' does not match "
                    f"parent directory '{entry.name}' (expected '{expected_category}')"
                )
            for field in ("name", "description"):
                value = manifest.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{rel_manifest}: missing or invalid '{field}'")
            if "version" in manifest:
                version = manifest["version"]
                if not isinstance(version, str) or not version.strip():
                    errors.append(f"{rel_manifest}: 'version' must be a non-empty string")

            detect = manifest.get("detect")
            if not isinstance(detect, dict):
                errors.append(f"{rel_manifest}: missing or invalid 'detect' object")
            else:
                unknown_detect = sorted(set(detect) - set(ADAPTER_DETECT_KEYS))
                if unknown_detect:
                    errors.append(
                        f"{rel_manifest}: unsupported detect key(s): {', '.join(unknown_detect)}"
                    )
                has_signal = False
                for key in ADAPTER_DETECT_KEYS:
                    if key not in detect:
                        continue
                    items = detect[key]
                    if not isinstance(items, list) or not all(
                        isinstance(item, str) and item.strip() for item in items
                    ):
                        errors.append(
                            f"{rel_manifest}: detect.{key} must be a list of non-empty strings"
                        )
                    elif items:
                        has_signal = True
                if not has_signal:
                    errors.append(
                        f"{rel_manifest}: detect must declare at least one signal in files, packages, or directories"
                    )

            if "commands" in manifest:
                commands = manifest["commands"]
                if not isinstance(commands, dict) or not all(
                    isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
                    for k, v in commands.items()
                ):
                    errors.append(
                        f"{rel_manifest}: 'commands' must map non-empty strings to non-empty strings"
                    )

            files = manifest.get("files")
            if not isinstance(files, dict):
                errors.append(f"{rel_manifest}: missing or invalid 'files' object")
                continue

            for req_key in ("conventions", "review_checks"):
                raw_path = files.get(req_key)
                resolved = _resolve_inside_adapter(root, adapter_dir, raw_path)
                if resolved is None:
                    errors.append(
                        f"{rel_manifest}: files.{req_key} must be a non-symlink relative path inside the adapter directory"
                    )
                elif not resolved.is_file():
                    errors.append(
                        f"{rel_manifest}: files.{req_key} target '{raw_path}' does not exist"
                    )

            if "editor_settings" in files:
                raw_editor = files["editor_settings"]
                resolved_editor = _resolve_inside_adapter(root, adapter_dir, raw_editor)
                if resolved_editor is None:
                    errors.append(
                        f"{rel_manifest}: files.editor_settings must be a non-symlink relative path inside the adapter directory"
                    )
                elif not resolved_editor.is_file():
                    errors.append(
                        f"{rel_manifest}: files.editor_settings target '{raw_editor}' does not exist"
                    )
                else:
                    try:
                        parsed_editor = json.loads(resolved_editor.read_text(encoding="utf-8"))
                    except json.JSONDecodeError as exc:
                        errors.append(
                            f"{rel_adapter}/{raw_editor}: invalid JSON ({exc.msg})"
                        )
                    else:
                        if not isinstance(parsed_editor, dict):
                            errors.append(
                                f"{rel_adapter}/{raw_editor}: editor settings must be a JSON object"
                            )

            if "skills" in files:
                raw_skills = files["skills"]
                if not isinstance(raw_skills, list):
                    errors.append(f"{rel_manifest}: files.skills must be a list of relative paths")
                else:
                    for raw_skill in raw_skills:
                        resolved_skill = _resolve_inside_adapter(root, adapter_dir, raw_skill)
                        if resolved_skill is None:
                            errors.append(
                                f"{rel_manifest}: files.skills entry '{raw_skill}' must be a non-symlink path inside the adapter directory"
                            )
                            continue
                        skill_md = resolved_skill / "SKILL.md"
                        if skill_md.is_symlink():
                            errors.append(
                                f"{rel_adapter}/{raw_skill}/SKILL.md: symlinks are not allowed"
                            )
                            continue
                        if not resolved_skill.is_dir() or not skill_md.is_file():
                            errors.append(
                                f"{rel_manifest}: files.skills entry '{raw_skill}' must contain SKILL.md"
                            )
                            continue
                        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
                        if not fm or fm.get("name") != resolved_skill.name or not fm.get("description"):
                            errors.append(
                                f"{rel_adapter}/{raw_skill}/SKILL.md: invalid or incomplete frontmatter"
                            )
                            continue
                        skill_name = fm["name"]
                        skill_ref = f"{rel_adapter}/{raw_skill}/SKILL.md"
                        if skill_name in seen_adapter_skills:
                            errors.append(
                                f"{skill_ref}: skill name '{skill_name}' collides with "
                                f"{seen_adapter_skills[skill_name]} (both target processes/{skill_name}.md)"
                            )
                        else:
                            seen_adapter_skills[skill_name] = skill_ref

    return errors


def find_adapter_skill_collisions(
    root: Path, adapter_dirs: list[Path] | None = None
) -> list[str]:
    """Check selected adapters for skill name collisions against each other and processes/."""
    collisions: list[str] = []
    repo_root = root.resolve()
    processes_dir = root / "processes"
    existing_processes = (
        {p.stem for p in processes_dir.glob("*.md") if p.is_file()}
        if processes_dir.is_dir()
        else set()
    )

    if adapter_dirs is None:
        adapter_dirs = []
        adapters_dir = root / "adapters"
        if adapters_dir.is_dir() and not adapters_dir.is_symlink():
            for cat_dir in sorted(adapters_dir.iterdir()):
                if cat_dir.is_dir() and not cat_dir.is_symlink() and cat_dir.name in ADAPTER_CATEGORIES:
                    for item in sorted(cat_dir.iterdir()):
                        if item.is_dir() and not item.is_symlink():
                            adapter_dirs.append(item)

    seen_skills: dict[str, str] = {}
    for adapter_dir in adapter_dirs:
        if adapter_dir.is_symlink() or not adapter_dir.is_dir():
            continue
        if not adapter_dir.resolve().is_relative_to(repo_root):
            continue
        manifest_path = adapter_dir / "adapter.json"
        if manifest_path.is_symlink() or not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(manifest, dict):
            continue
        files = manifest.get("files")
        if not isinstance(files, dict) or not isinstance(files.get("skills"), list):
            continue
        rel_adapter = adapter_dir.resolve().relative_to(repo_root).as_posix()
        for raw_skill in files["skills"]:
            resolved_skill = _resolve_inside_adapter(root, adapter_dir, raw_skill)
            if resolved_skill is None:
                continue
            skill_md = resolved_skill / "SKILL.md"
            if skill_md.is_symlink() or not skill_md.is_file():
                continue
            fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            if not fm or not fm.get("name"):
                continue
            skill_name = fm["name"]
            skill_ref = f"{rel_adapter}/{raw_skill}/SKILL.md"
            if skill_name in seen_skills:
                collisions.append(
                    f"{skill_ref}: skill name '{skill_name}' collides with "
                    f"{seen_skills[skill_name]} (both target processes/{skill_name}.md)"
                )
            else:
                seen_skills[skill_name] = skill_ref
            if skill_name in existing_processes:
                collisions.append(
                    f"{skill_ref}: skill name '{skill_name}' collides with existing "
                    f"processes/{skill_name}.md"
                )

    return collisions


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_wrappers(root))
    errors.extend(validate_links(root))
    errors.extend(validate_shell_scripts(root))
    errors.extend(validate_adapters(root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Symbiote-AI repository.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root directory (default: parent of scripts/).",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    errors = validate_repo(root)
    if errors:
        print(f"Validation failed with {len(errors)} issue(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK: repository validation passed ({root})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
