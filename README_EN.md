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

## License

Original code, skills, and documentation are licensed under Apache-2.0. Contest statements, datasets, papers, official templates, and third-party materials require their own redistribution rights.
