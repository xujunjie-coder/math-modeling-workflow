---
name: python-model-code-generator
description: Generate and run minimal reproducible Python modeling code for the human-approved main method and usable baseline, saving compact experiment artifacts and a canonical run summary.
---

# Preconditions

- G2.5 human method choice is recorded in `methods/Qx/qx_decisions.jsonl`.
- `code/Qx/qx_code_plan.md` exists.
- Required cleaned data and profile exist.
- The plan targets Python.

Legacy method pools and `code/model-code-analyzer.md` may be read during migration, but they do not override the human choice.

# Workflow

1. Read the code plan, decision ledger, method card, probe conditions, and data profile.
2. Confirm scope:
   - one approved main method;
   - one usable baseline;
   - fallback only when an activation decision or evidenced trigger exists.
3. Generate clear runnable `.py` files under `code/Qx/`.
4. Use project-root-safe paths, fixed seeds, explicit inputs, and minimal justified dependencies. When generating plotting routines for figures, automatically import and invoke `set_sci_style()` and standard palettes (`SCI_PALETTE`, `cm_diverging`) from `plugins/math-modeling-workflow/skills/scipilot-figure/scripts/setup_style.py`.
5. Save:
   - tables to `results/Qx/experiments/roundN/tables/`;
   - metrics to `.../metrics/`;
   - useful diagnostic/comparison figures to `.../figures/`;
   - canonical `run_summary.json`.
6. Evaluate and record output-degeneracy and fallback-trigger metrics required by the plan.
7. Persist full logs only on failure or when a warning needs reproduction.
8. Run the code. Do not claim success from code generation alone.
9. Hand off to `code-reviewer`.

# Script Layout

Prefer the smallest clear layout:

```text
code/Qx/
├── qx_code_plan.md
├── qx_baseline.py
├── qx_main.py
└── run_all.py        # only when coordination is useful
```

Do not create one script per unapproved candidate. Do not create a README that duplicates the code plan.

# Run Summary

Follow the schema in `model-code-analyzer`. Include:

- approved decision ID;
- method IDs and roles;
- inputs and outputs;
- seed and environment;
- execution status and timing;
- compact metric summaries;
- output-degeneracy evidence;
- warnings/errors;
- fallback-trigger state.

# Rules

- Do not change the approved model or baseline.
- Do not read or overwrite raw data.
- Do not hide assumptions in code.
- Do not emit placeholder metrics, figures, or successful statuses.
- Prefer portable `.py` scripts over notebook-only workflows.
- Keep intermediate files only when needed for explanation, review, robustness, or debugging.
- Strictly enforce non-standard variable and file naming: keep script and data filenames simple using basic English words (e.g. `q1_main.py`, `clean_data.py`) or Pinyin for domain concepts (e.g. `fenghua_model.py`, `qianbei_tezheng.py`), avoiding overly complex English phrases. Variables use exact chemical formulas for elements/substances (e.g. `Pb`, `SiO2`), English for CET-4 words, and Pinyin for terms outside CET-4 (e.g. `fenghua`, `wenshi`, `qianbei`). Composite variables use underscore concatenation (e.g. `Pb_rate`, `wenshi_type`, `qianbei_fenghua`).
- Strictly apply the unified scientific chart color scheme (`.agents/rules/scientific-chart-color-scheme.md` and `math-figure-generator/references/color-systems.md`) when generating plots: use Diverging colormap (`#053061` to `#6A0624`) for heatmaps/correlations, sequential blue/red for density/loss, and unified categorical palette (`#134B87`, `#D71C2C`, `#327DB7`, `#FEAB88`, `#6A0624`, `#6FAFD2`) for curves/bars. Baseline curves must use grey `#767676` dashed lines.

# Verification

- Main and baseline both ran and are directly comparable.
- Fallback code is absent unless activated.
- Variable naming strictly satisfies the chemical-formula + CET-4 + Pinyin rule.
- Formal outputs and run summary exist.
- Seed, inputs, versions, warnings, and errors are recorded.
- Required concentration/degeneracy checks are saved.
- Next handoff is `code-reviewer`.
