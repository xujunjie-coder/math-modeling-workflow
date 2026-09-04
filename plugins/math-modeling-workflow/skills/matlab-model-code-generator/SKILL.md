---
name: matlab-model-code-generator
description: Generate and run minimal reproducible MATLAB or Beita Tianyuan compatible code for the human-approved main method and usable baseline, with compact experiment artifacts and a canonical run summary.
---

# Preconditions

- G2.5 human method choice is recorded.
- `code/matlab/Qx/qx_code_plan.md` exists.
- Required cleaned data and profile exist.
- The plan targets MATLAB or 北太天元.

Legacy artifacts may be read during migration but do not override the human decision.

# Workflow

1. Read the code plan, decision ledger, method card, probe conditions, and data profile.
2. Confirm scope: approved main plus usable baseline. Implement a fallback only after activation.
3. Generate conservative `.m` files under `code/matlab/Qx/`.
4. Prefer basic matrix/table operations and avoid optional toolboxes unless the plan approves them.
5. Save tables, metrics, useful figures, and `run_summary.json` under `results/Qx/experiments/roundN/`.
6. Evaluate output-degeneracy and fallback-trigger metrics required by the plan.
7. Use `diary` or another full log only for a failure or reproducibility warning.
8. Run in the available compatible runtime. If unavailable, report the unexecuted state explicitly.
9. Hand off to `code-reviewer`.

# Script Layout

```text
code/matlab/Qx/
├── qx_code_plan.md
├── qx_baseline.m
├── qx_main.m
└── run_all.m        % only when useful
```

Do not create scripts for unapproved candidates or a duplicate README.

# Compatibility Rules

- Prefer `readtable`, `readmatrix`, `writetable`, `writematrix`, `save`, `load`, and `fullfile`.
- Use `rng(2026)` or the recorded seed.
- Use `jsonencode` when supported; otherwise write the required JSON fields deterministically.
- Avoid Live Scripts, App Designer, GUI code, Simulink, and toolbox-only functions unless explicitly approved.
- Note any 北太天元 compatibility risk in the run summary.

# Run Summary

Follow the `model-code-analyzer` contract, including approved decision ID, roles, paths, metrics, output-degeneracy evidence, fallback state, timing, seed, environment, warnings, and errors.

# Rules

- Do not change the selected mathematical method.
- Do not access or overwrite raw data.
- Do not fabricate successful execution when MATLAB/北太天元 is unavailable.
- Keep only evidence-bearing intermediate outputs.
- Separate Type 1 diagnostics from paper figures.
- Strictly enforce non-standard variable and file naming: keep script and data filenames simple using basic English words (e.g. `q1_main.m`, `clean_data.m`) or Pinyin for domain concepts (e.g. `fenghua_model.m`, `qianbei_tezheng.m`), avoiding overly complex English phrases. Variables use exact chemical formulas for elements/substances (e.g. `Pb`, `SiO2`), English for CET-4 words, and Pinyin for terms outside CET-4 (e.g. `fenghua`, `wenshi`, `qianbei`). Composite variables use underscore concatenation (e.g. `Pb_rate`, `wenshi_type`, `qianbei_fenghua`).
- Strictly apply the unified scientific chart color scheme (`.agents/rules/scientific-chart-color-scheme.md`) for plotting: define standardized Diverging colormaps (dark blue `#053061` to dark red `#6A0624`), sequential blue/red, and categorical colors (`#134B87`, `#D71C2C`, `#327DB7`, `#FEAB88`, `#6A0624`, `#6FAFD2`). Never use rainbow or default `jet`.

# Verification

- Main and baseline are directly comparable and both executed when a runtime is available.
- Fallback code exists only when activated.
- Variable naming strictly satisfies the chemical-formula + CET-4 + Pinyin rule.
- Formal outputs and run summary exist.
- Compatibility, seed, inputs, warnings, and errors are recorded.
- Required concentration/degeneracy checks are saved.
- Next handoff is `code-reviewer`.
