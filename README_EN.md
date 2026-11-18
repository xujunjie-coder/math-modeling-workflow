# Math Modeling Workflow
> A Codex plugin connecting mathematical modeling tasks, reproducible experiments, and paper evidence.

**Markdown Skills · Python validation helpers · JSON / JSONL · Apache-2.0**

[中文介绍](README.md) · [Guide](使用教程.md) · [Contributing](CONTRIBUTING.md)

## What it does

The plugin routes problem parsing, data auditing, method selection, Python or MATLAB code work, robustness checks, figures, paper writing, and final audits through specialized Skills.

The engineering focus is traceability: per-question manifests record progress, decision logs capture choices, and validation scripts inspect the evidence behind gates and numerical claims.

## Explore the implementation

- [Skills](plugins/math-modeling-workflow/skills/): task contracts and execution rules.
- [Gate checker](plugins/math-modeling-workflow/scripts/gate_check.py): evidence-based progress checks.
- [Frozen-number checker](plugins/math-modeling-workflow/scripts/check_frozen_numbers.py): paper-to-result consistency.
- [Workspace template](plugins/math-modeling-workflow/assets/workspace-template/): initial directories and configuration.
- [Tests](tests/) and [CI](.github/workflows/validate.yml): repository validation entry points.

## Getting started

Register this repository as a local Marketplace:

```powershell
git clone https://github.com/xujunjie-coder/math-modeling-workflow.git
codex plugin marketplace add C:\path\to\math-modeling-workflow
codex plugin add math-modeling-workflow@personal
```

Open a new task after installation. Initialize a separate contest workspace:

```powershell
python plugins/math-modeling-workflow/scripts/init_workspace.py C:\path\to\contest-project
```

Place the problem statement in `problem_statement/` and original attachments in `data_raw/`. Ask `$workflow-orchestrator` to inspect evidence and route the next action. See the [Chinese README](README.md) for mode details and documentation links.

## Validation

```powershell
python plugins/math-modeling-workflow/scripts/validate_repo.py .
python -m unittest discover -s tests -v
```

These are validation entry points, not a claim that the current revision has passed every check. Auto-Pilot instructions and decision-recording gates coexist in this repository; reconcile their configuration before relying on automated execution. Human review remains necessary for model validity, references, and final papers.

## License

Original code, Skills, and documentation use [Apache-2.0](LICENSE). Contest data, papers, templates, and other third-party materials require separate authorization. Additional modeling and rendering dependencies require their own version and license review.
