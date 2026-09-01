#!/usr/bin/env python3
"""Validate the public plugin repository without third-party dependencies."""

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


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - error path
        errors.append(f"invalid JSON: {path}: {exc}")
        return {}


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}
    block = text.split("\n---\n", 1)[0][4:]
    result: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"\'')
    return result


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
        metadata = frontmatter(text)
        name = metadata.get("name", "")
        if name != skill_dir.name or not SKILL_NAME.fullmatch(name):
            errors.append(f"skill name/folder mismatch: {skill_dir}")
        if not metadata.get("description"):
            errors.append(f"missing skill description: {skill_file}")
        if "[TODO:" in text or "TODO]" in text:
            errors.append(f"unfinished placeholder: {skill_file}")
        if WINDOWS_ABSOLUTE.search(text):
            errors.append(f"personal absolute path: {skill_file}")
        skill_names.add(name)
        for link in MARKDOWN_LINK.findall(text):
            if link.startswith(("http://", "https://", "plugin://", "#")):
                continue
            target = (skill_dir / link.split("#", 1)[0]).resolve()
            if not target.exists():
                errors.append(f"broken local link in {skill_file}: {link}")

    orchestrator = (skills_root / "workflow-orchestrator" / "SKILL.md").read_text(encoding="utf-8")
    routed = set(re.findall(r"`([a-z][a-z0-9-]+)`", orchestrator))
    missing_routes = sorted(name for name in routed if name.endswith(("-builder", "-generator", "-planner", "-writer", "-assembler", "-polisher", "-auditor", "-checker", "-cleaner", "-selector", "-formatter")) and name not in skill_names)
    if missing_routes:
        errors.append("orchestrator routes to missing skills: " + ", ".join(missing_routes))

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
