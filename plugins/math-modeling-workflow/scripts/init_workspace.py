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
