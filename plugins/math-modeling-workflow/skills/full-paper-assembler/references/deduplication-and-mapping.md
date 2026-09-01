# 全文去重与映射规则

## Semantic Block Classes

Classify content before drafting:

- `GLOBAL_SHARED`: problem statement, shared data scope, common preprocessing, global assumptions, symbols, common definitions.
- `QUESTION_SPECIFIC`: one Qx formulation, solution, result, interpretation, limitation, and question summary.
- `VALIDATION`: robustness, sensitivity, holdout, error, feasibility, and failure-region evidence.
- `EVALUATION`: system-level strengths, limitations, transfer conditions, and final conclusions.
- `REFERENCE_APPENDIX`: verified citations and real supporting material.
- `EXCLUDED_DIAGNOSTIC`: debugging, abandoned methods, repeated EDA, obsolete results, and Type 1 diagnostic figures.

## Mapping Decisions

- Merge identical shared rules into one global statement and list all source blocks in the manifest.
- Keep a method-specific exception local even when the base rule is global.
- If two sources disagree on a number, symbol, unit, threshold, sample scope, or label, stop; repair the canonical source and re-freeze rather than choosing prose.
- If a downstream Qx consumes an upstream output, name the object and version at the transition; do not merely say “based on the previous question”.
- Keep a result near its model. Move only reusable validation evidence to the global validation chapter, leaving a precise pointer in the question section.
- Include a figure/table only when it supports a retained paper claim. Record excluded diagnostics rather than copying them.

## Transition Contract

Each dependent question begins with a short interface sentence covering:

1. upstream object read;
2. unchanged scope/unit/label contract;
3. purpose in the current question;
4. any documented transformation.

Do not use transitions to conceal a changed sample filter, threshold, symbol, or model version.
