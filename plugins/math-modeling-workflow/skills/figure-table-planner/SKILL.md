---
name: figure-table-planner
description: Decide whether verified mathematical-modeling claims need tables, static plots, diagrams, or no visual, then plan the smallest traceable set of diagnostic, comparison, paper, and appendix artifacts.
---

# Purpose

Make every visual evidence-bearing. Prefer fewer useful visuals over a decorative inventory.

# Inputs

- method card and decision ledger;
- run summaries and final result analysis;
- robustness evidence;
- solution package and frozen numbers in submission mode;
- existing figures/tables.

# Figure Types

- Type 1 diagnostic: internal debugging; never in the paper.
- Type 2 comparison: main vs usable baseline or a genuinely tested alternative; optional in paper.
- Type 3 paper: directly supports a main claim; required only when the claim benefits materially from a visual.
- Type 4 appendix: supplementary evidence referenced from the main text.

# Workflow

1. List verified claims that need visual or exact tabular support.
2. Run the visual-decision gate for every result-bearing claim:
   - exact small values or parameters -> table;
   - trend, distribution, uncertainty, sensitivity, spatial/temporal pattern, matrix, or many-item comparison -> plot;
   - mechanism, dependency, or workflow -> diagram;
   - prose-only when a visual would not improve interpretation.
3. Reuse an existing artifact when it already communicates the claim at final placement size.
4. For each proposed visual record:
   - ID and Qx;
   - type;
   - source artifact and frozen claim IDs when applicable;
   - one core claim;
   - chart/table form;
   - target section;
   - output formats and final placement size;
   - status and render needs.
5. Ask the human to confirm judgment-bearing Type 3 claims through one compact choice card when they are not already in the decision ledger.
6. Save `methods/Qx/qx_figure_table_plan.md` when submission work or downstream generation needs durable routing. In lean exploration, a compact in-conversation plan is sufficient.

# Planning Heuristics

- Use tables for exact values, parameters, and small comparisons.
- Use plots for trends, distributions, sensitivity, or many-item comparisons.
- Use diagrams for mechanisms, dependencies, and workflows.
- Prefer a heatmap for a meaningful matrix such as correlation, confusion, missingness, transition, or two-parameter sensitivity; do not convert an ordinary table into a heatmap merely to add color.
- Prefer box/violin/strip plots for group distributions, scatter plus fit or uncertainty for relationships, line plus band for time or sensitivity, and a confusion matrix plus class-aware metric for classification.
- When several figures use the same categories, methods, variables, or groups, require stable ordering and visual identity across them.
- Assign chapter-based identifiers (e.g. `图X-Y`, `表X-Y`) during planning and drafting; global sequential renumbering (图1, 2, 3... and 表1, 2, 3...) occurs only after human review of the assembled master paper.
- A main-vs-baseline figure needs compatible metrics and the same evaluation setup.
- Do not create a multi-method comparison merely to imply breadth.

# Rules

- Type 1 never enters the paper.
- Type 3 uses final validated sources and a human-confirmed core claim.
- For every Type 3 paper figure, specify the concrete conclusion to be derived in text, ensuring downstream paper sections discuss findings centered on the visual (e.g. "通过上述图片得出……结论").
- Do not use unresolved exploratory figures as paper evidence.
- Do not fabricate data, captions, or claims.
- Do not fill plans with placeholder sentinels; pause for one human choice instead.
- Every visual must have a source and purpose.
- Do not impose an arbitrary figure quota. Require an explicit no-figure decision when a result-bearing claim is left to prose or tables.
- A planned Type 3/4 figure must request editable source plus vector output when compatible and a high-resolution raster fallback.

# Verification

- Each planned visual supports a verified claim.
- Types, sources, sections, and statuses are explicit.
- Type 3 claims trace to human decisions and frozen evidence.
- Every result-bearing claim passed the visual-decision gate.
- Matrix, distribution, sensitivity, classification, and many-item claims were not defaulted to tables without a reason.
- No unnecessary or decorative visual remains.
