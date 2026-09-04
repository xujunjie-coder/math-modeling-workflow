#!/usr/bin/env python3
"""Initialize a non-destructive mathematical-modeling project workspace."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


# Physical layout mirrors the canonical Skill paths (see docs/directory-mapping.zh-CN.md).
# Root-level data_raw/data_clean stay as the documented legacy/teaching locations;
# the canonical data home is workspace/data*.
DIRECTORIES = (
    "problem_statement",
    "data_raw",
    "data_clean",
    "planning/parse",
    "planning/classification",
    "planning/manifests",
    "planning/decisions",
    "workspace/data_raw",
    "workspace/data_clean",
    "workspace/data",
    "workspace/literature",
    "workspace/papers",
    "methods",
    "code",
    "results",
    "robustness",
    "outputs",
    "paper/sections",
    "paper/figures",
    "paper/master",
    "paper/final",
    "paper/audits",
    "paper/latex",
    "paper/latex/figures",
    "deliverables",
)


def initialize(target: Path) -> list[Path]:
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    for relative in DIRECTORIES:
        path = target / relative
        if not path.exists():
            path.mkdir(parents=True)
            created.append(path)

    template_root = Path(__file__).resolve().parent.parent / "assets" / "workspace-template"
    for source in template_root.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(template_root)
        destination = target / relative
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        created.append(destination)

    repo_root = Path(__file__).resolve().parent.parent.parent.parent

    # 1. 复制全局系统指令 AGENTS.md
    src_agents = repo_root / "AGENTS.md"
    if src_agents.is_file():
        dest_agents = target / "AGENTS.md"
        if not dest_agents.exists():
            shutil.copy2(src_agents, dest_agents)
            created.append(dest_agents)

    # 2. 复制工作区规则目录 .agents/rules
    src_agents_dir = repo_root / ".agents"
    if src_agents_dir.is_dir():
        dest_agents_dir = target / ".agents"
        for rule_file in src_agents_dir.rglob("*"):
            if rule_file.is_file():
                rel = rule_file.relative_to(src_agents_dir)
                dest_file = dest_agents_dir / rel
                if not dest_file.exists():
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(rule_file, dest_file)
                    created.append(dest_file)

    # 3. 复制完整的技能与脚本插件库 plugins/math-modeling-workflow
    src_plugin = repo_root / "plugins" / "math-modeling-workflow"
    if src_plugin.is_dir():
        dest_plugin = target / "plugins" / "math-modeling-workflow"
        for pfile in src_plugin.rglob("*"):
            if pfile.is_file() and "__pycache__" not in pfile.parts and not pfile.name.endswith(".pyc"):
                rel = pfile.relative_to(src_plugin)
                dest_pfile = dest_plugin / rel
                if not dest_pfile.exists():
                    dest_pfile.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(pfile, dest_pfile)
                    created.append(dest_pfile)

    # 4. 复制一键启动指令和国赛模板
    for extra_name in ("一键启动指令.txt", "国赛模板 (1).docx"):
        src_extra = repo_root / extra_name
        if src_extra.is_file():
            dest_extra = target / extra_name
            if not dest_extra.exists():
                shutil.copy2(src_extra, dest_extra)
                created.append(dest_extra)

    marker = target / ".math-modeling-workflow.json"
    if not marker.exists():
        marker.write_text(
            json.dumps({"schema_version": 1, "initialized_by": "math-modeling-workflow"}, indent=2) + "\n",
            encoding="utf-8",
        )
        created.append(marker)

    return created



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Project directory to initialize")
    args = parser.parse_args()
    created = initialize(args.target)
    print(f"Initialized {args.target.resolve()}")
    print(f"Created {len(created)} directories/files; existing files were preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
