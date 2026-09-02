# Math Modeling Workflow

An installable Codex plugin for evidence-driven mathematical-modeling contests. The `workflow-orchestrator` skill reads per-question manifests, evaluates gates, and routes one authorized next action across problem framing, data audit, method decisions, reproducible experiments, robustness, publication figures, paper assembly, formatting, and final audits.

This repository contains reusable workflow logic, skills, templates, and a synthetic example only. It does not contain real contest inputs, private team information, or submission artifacts.

## Install

```powershell
git clone https://github.com/xujunjie-coder/math-modeling-workflow.git
codex plugin marketplace add C:\path\to\math-modeling-workflow
codex plugin add math-modeling-workflow@personal
```

Start a new Codex task after installing or updating the plugin, then use:

```text
Use $workflow-orchestrator to initialize this mathematical-modeling project in lean mode with Python and seed 2026.
```

See the [Chinese README](README.md) for the complete routing chain, visualization policy, and development commands.

## Deterministic gate enforcement

Gate prose is backed by a standard-library enforcer that judges progress from on-disk evidence, never from the self-reported manifest alone:

```powershell
# Inspect the highest gate actually supported by artifacts (exit 2 = integrity violation)
python plugins/math-modeling-workflow/scripts/gate_check.py <workspace> status
# Hard pre-action guard: code_generation needs G2.5, freeze needs G3,
# paper_writing needs G4, final_assembly needs every active question at G5.
python plugins/math-modeling-workflow/scripts/gate_check.py <workspace> guard --action code_generation --question Q1
```

A data-free/mechanism-only question may declare `"waivers": ["data_profile"]` in its manifest; the waiver is reported, never silently applied.

`check_frozen_numbers.py` mechanically diffs the numbers in a paper against frozen/metrics JSON (section/figure/equation numbers, years, code, URLs and math are skipped): an UNFROZEN claim number exits non-zero, rounding near-matches are warnings, and a sidecar `.frozenignore` holds explicit exceptions.

## Using it without Codex

Skills are plain Markdown and the scripts need only the Python standard library, so the workflow also runs in Claude Code, Cursor, or an ordinary chat session: a human performs the routing (loading each `SKILL.md` at the right gate) while `gate_check.py` / `check_frozen_numbers.py` provide hard local enforcement. See `docs/agent-agnostic-loading.zh-CN.md`, `docs/directory-mapping.zh-CN.md`, and `docs/lean-to-submission-checklist.zh-CN.md`.

## License

Original code, skills, and documentation are licensed under Apache-2.0. Contest statements, datasets, papers, official templates, and third-party materials require their own redistribution rights.
