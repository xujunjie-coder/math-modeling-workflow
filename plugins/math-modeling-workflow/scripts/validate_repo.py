#!/usr/bin/env python3
"""Validate the public plugin repository without third-party dependencies.

Checks:
- plugin/marketplace manifest identity, strict semver and source path;
- every skill has well-formed YAML front matter (name == folder, description);
- no TODO placeholders, personal absolute paths, or broken local links;
- the explicit stage routing table below stays in two-way sync with the
  skills actually on disk (a suffix guess can no longer hide a missing or
  unregistered skill);
- every backtick/``$`` skill reference in the orchestrator resolves to a real
  skill or an explicitly whitelisted non-skill term.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")
WINDOWS_ABSOLUTE = re.compile(r"[A-Za-z]:\\(?:Users|Documents and Settings)\\", re.IGNORECASE)
# A skill reference is an explicit call: `skill-name` or $skill-name.
BACKTICK_REF = re.compile(r"`([a-z0-9][a-z0-9-]+)`")
DOLLAR_REF = re.compile(r"\$([a-z0-9][a-z0-9-]+)")
FRONTMATTER_KEY = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")

# Explicit, authoritative stage -> skills routing table. This is the single
# registry the orchestrator follows; it must list every shipped skill exactly
# once. Adding/removing a skill requires updating this table deliberately.
STAGE_ROUTES: dict[str, list[str]] = {
    "orchestration": ["workflow-orchestrator"],
    "framing": [
        "problem-parser",
        "problem-classifier",
        "data-auditor-cleaner",
    ],
    "foundations": [
        "symbol-table-builder",
        "model-assumptions-builder",
        "related-paper-analyzer",
        "reference-manager",
    ],
    "method_decision": [
        "method-selector",
        "decision-prompt-builder",
        "modeler-decision-logger",
    ],
    "code": [
        "model-code-analyzer",
        "python-model-code-generator",
        "matlab-model-code-generator",
        "code-reviewer",
        "python-code-reviewer",
        "matlab-code-reviewer",
    ],
    "results": [
        "result-report-generator",
        "robustness-checker",
        "final-method-explainer",
        "figure-table-planner",
        "math-figure-generator",
        "solution-package-builder",
    ],
    "paper": [
        "paper-section-writer",
        "full-paper-assembler",
        "paper-polisher",
        "national-modeling-paper-formatter",
    ],
    "audit": [
        "consistency-auditor",
        "completeness-auditor",
        "quality-assurance-auditor",
    ],
}

# Backtick/$ tokens that are legitimate references but not skills (config keys,
# commands). Keep this list minimal and explicit.
NON_SKILL_REFERENCES: set[str] = set()


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - error path
        errors.append(f"invalid JSON: {path}: {exc}")
        return {}


def frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Parse leading YAML front matter robustly (BOM/CRLF/EOF tolerated).

    Returns (fields, problems). Only the flat ``key: value`` shape used by
    SKILL.md is supported; duplicate top-level keys and malformed lines are
    reported instead of silently dropped.
    """
    problems: list[str] = []
    stripped = text.lstrip("﻿")
    lines = stripped.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["missing opening front matter delimiter ---"]
    fields: dict[str, str] = {}
    index = 1
    closed = False
    while index < len(lines):
        line = lines[index].rstrip("\r")
        if line.strip() == "---":
            closed = True
            break
        if not line.strip():
            index += 1
            continue
        if line[:1] in {" ", "\t"}:  # nested/multiline value, intentionally unsupported
            index += 1
            continue
        match = FRONTMATTER_KEY.match(line)
        if not match:
            problems.append(f"malformed front matter line: {line.strip()!r}")
            index += 1
            continue
        key, value = match.group(1), match.group(2).strip().strip('"\'')
        if key in fields:
            problems.append(f"duplicate front matter key: {key}")
        fields[key] = value
        index += 1
    if not closed:
        problems.append("missing closing front matter delimiter ---")
    return fields, problems


def validate_routing_registry(skill_names: set[str]) -> list[str]:
    errors: list[str] = []
    registered = [name for stage in STAGE_ROUTES.values() for name in stage]
    duplicates = sorted({name for name in registered if registered.count(name) > 1})
    if duplicates:
        errors.append("skills registered more than once in STAGE_ROUTES: " + ", ".join(duplicates))
    registered_set = set(registered)
    unregistered = sorted(skill_names - registered_set)
    if unregistered:
        errors.append(
            "skills on disk missing from the explicit STAGE_ROUTES registry: " + ", ".join(unregistered)
        )
    missing_on_disk = sorted(registered_set - skill_names)
    if missing_on_disk:
        errors.append(
            "STAGE_ROUTES references skills that do not exist on disk: " + ", ".join(missing_on_disk)
        )
    return errors


def validate_orchestrator_references(orchestrator_text: str, skill_names: set[str]) -> list[str]:
    references = set(BACKTICK_REF.findall(orchestrator_text)) | set(DOLLAR_REF.findall(orchestrator_text))
    unresolved = sorted(
        token
        for token in references
        if "-" in token and token not in skill_names and token not in NON_SKILL_REFERENCES
    )
    if unresolved:
        return ["orchestrator references unknown skills: " + ", ".join(unresolved)]
    return []


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    plugin = root / "plugins" / "math-modeling-workflow"
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"

    manifest = load_json(manifest_path, errors)
    if manifest.get("name") != "math-modeling-workflow":
        errors.append("plugin name must be math-modeling-workflow")
    if not SEMVER.fullmatch(str(manifest.get("version", ""))):
        errors.append("plugin version must be strict semver")
    if manifest.get("skills") != "./skills/":
        errors.append("plugin skills path must be ./skills/")

    marketplace = load_json(marketplace_path, errors)
    entries = marketplace.get("plugins", [])
    matching = [entry for entry in entries if entry.get("name") == manifest.get("name")]
    if len(matching) != 1:
        errors.append("marketplace must contain exactly one matching plugin entry")
    elif matching[0].get("source", {}).get("path") != "./plugins/math-modeling-workflow":
        errors.append("marketplace plugin source path is invalid")

    skills_root = plugin / "skills"
    skill_names: set[str] = set()
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"missing SKILL.md: {skill_dir}")
            continue
        text = skill_file.read_text(encoding="utf-8")
        metadata, fm_problems = frontmatter(text)
        for problem in fm_problems:
            errors.append(f"{skill_file}: {problem}")
        name = metadata.get("name", "")
        if name != skill_dir.name or not SKILL_NAME.fullmatch(name):
            errors.append(f"skill name/folder mismatch: {skill_dir} (front matter name={name!r})")
        if not metadata.get("description"):
            errors.append(f"missing skill description: {skill_file}")
        if "[TODO:" in text or "TODO]" in text:
            errors.append(f"unfinished placeholder: {skill_file}")
        if WINDOWS_ABSOLUTE.search(text):
            errors.append(f"personal absolute path: {skill_file}")
        skill_names.add(name)
        for link in MARKDOWN_LINK.findall(text):
            if link.startswith(("http://", "https://", "plugin://", "#", "mailto:")):
                continue
            target = (skill_dir / link.split("#", 1)[0]).resolve()
            if not target.exists():
                errors.append(f"broken local link in {skill_file}: {link}")

    errors.extend(validate_routing_registry(skill_names))

    orchestrator_path = skills_root / "workflow-orchestrator" / "SKILL.md"
    if orchestrator_path.exists():
        orchestrator_text = orchestrator_path.read_text(encoding="utf-8")
        errors.extend(validate_orchestrator_references(orchestrator_text, skill_names))

    for text_path in root.rglob("*"):
        if not text_path.is_file() or text_path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".py"}:
            continue
        text = text_path.read_text(encoding="utf-8", errors="replace")
        if WINDOWS_ABSOLUTE.search(text):
            errors.append(f"personal absolute path: {text_path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
