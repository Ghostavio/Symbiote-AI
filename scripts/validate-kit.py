#!/usr/bin/env python3
"""Validate repository consistency for Symbiote-AI.

Checks:
1. Wrapper parity & target integrity across:
   - processes/<name>.md (canonical procedures, plus optional alias_of redirects)
   - .claude/skills/<name>/SKILL.md
   - .cursor/rules/<name>.mdc (excluding alwaysApply context rules)
   - AGENTS.md
   - .github/copilot-instructions.md
2. Local relative markdown links across all .md and .mdc files.
3. Shell scripts under scripts/ and .claude/integrations/: shebang, executable
   bit, and bash syntax check (bash -n, plus /bin/bash -n when available).
"""

from __future__ import annotations

import argparse
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


def validate_wrappers(root: Path) -> list[str]:
    errors: list[str] = []
    processes_dir = root / "processes"
    claude_skills_dir = root / ".claude" / "skills"
    cursor_rules_dir = root / ".cursor" / "rules"
    agents_file = root / "AGENTS.md"
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
    for alias_name, (alias_file, target_name, content) in sorted(canonical_aliases.items()):
        if target_name not in canonicals:
            errors.append(
                f"processes/{alias_file.name}: alias_of '{target_name}' does not point "
                f"to a primary canonical processes/{target_name}.md"
            )
        else:
            expected_target = canonicals[target_name].resolve()
            if expected_target not in _resolved_local_targets(alias_file, content):
                errors.append(
                    f"processes/{alias_file.name}: alias must link directly to "
                    f"processes/{target_name}.md"
                )

    # Claude Code wrappers
    claude_found: set[str] = set()
    if claude_skills_dir.is_dir():
        for skill_dir in sorted(p for p in claude_skills_dir.iterdir() if p.is_dir()):
            skill_name = skill_dir.name
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                errors.append(f".claude/skills/{skill_name}: missing SKILL.md")
                continue
            content = skill_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            if not fm or fm.get("name") != skill_name or not fm.get("description"):
                errors.append(
                    f".claude/skills/{skill_name}/SKILL.md: invalid or incomplete frontmatter"
                )
                continue

            alias_of = fm.get("alias_of", "").strip()
            target_name = alias_of or skill_name
            expected_rel = f"processes/{target_name}.md"

            if target_name not in canonicals:
                if alias_of:
                    errors.append(
                        f".claude/skills/{skill_name}/SKILL.md: alias_of '{alias_of}' "
                        f"has no primary canonical {expected_rel}"
                    )
                else:
                    errors.append(
                        f".claude/skills/{skill_name}/SKILL.md: no matching canonical {expected_rel}"
                    )
            else:
                if not alias_of:
                    claude_found.add(skill_name)
                expected_target = canonicals[target_name].resolve()
                if expected_target not in _resolved_local_targets(skill_file, content):
                    errors.append(
                        f".claude/skills/{skill_name}/SKILL.md: must link directly to {expected_rel}"
                    )
    else:
        errors.append("Missing required directory: .claude/skills/")

    # Cursor rule wrappers
    cursor_found: set[str] = set()
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
            target_name = alias_of or rule_name
            expected_rel = f"processes/{target_name}.md"

            if target_name not in canonicals:
                if alias_of:
                    errors.append(
                        f".cursor/rules/{rule_file.name}: alias_of '{alias_of}' "
                        f"has no primary canonical {expected_rel}"
                    )
                else:
                    errors.append(
                        f".cursor/rules/{rule_file.name}: no matching canonical {expected_rel}"
                    )
            else:
                if not alias_of:
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

    copilot_text = copilot_file.read_text(encoding="utf-8") if copilot_file.is_file() else ""
    if not copilot_file.is_file():
        errors.append("Missing required file: .github/copilot-instructions.md")

    for name in sorted(canonicals):
        if name not in claude_found:
            errors.append(f"Missing Claude Code wrapper: .claude/skills/{name}/SKILL.md")
        if name not in cursor_found:
            errors.append(f"Missing Cursor wrapper: .cursor/rules/{name}.mdc")
        if agents_file.is_file() and f"(processes/{name}.md)" not in agents_text:
            errors.append(f"AGENTS.md: missing link to processes/{name}.md")
        if copilot_file.is_file() and f"(../processes/{name}.md)" not in copilot_text:
            errors.append(
                f".github/copilot-instructions.md: missing link to ../processes/{name}.md"
            )

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


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_wrappers(root))
    errors.extend(validate_links(root))
    errors.extend(validate_shell_scripts(root))
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
