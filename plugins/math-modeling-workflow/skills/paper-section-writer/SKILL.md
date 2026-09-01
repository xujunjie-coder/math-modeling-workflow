---
name: paper-section-writer
description: Draft submission-ready mathematical-modeling paper sections from the approved solution package, frozen numbers, human decision ledger, and verified figures without searching scattered exploratory outputs or inventing interpretation.
---

# Preconditions

- `rigor_profile` is `submission`.
- Final method explanation exists.
- Final result analysis exists.
- Solution package and current frozen numbers exist.
- Required human claim-scope and physical/domain-meaning decisions are recorded.

If any prerequisite is missing, return to its producer rather than drafting around the gap.

# Primary Sources

Use, in order:

1. `qx_solution_package_for_writer.md`
2. `frozen_numbers.json`
3. `qx_decisions.jsonl`
4. verified paper figures/tables
5. final method explanation and robustness report for clarification

Do not hunt through raw experiment folders to invent a narrative.

# Workflow

1. Resolve the requested section and contest format.
2. Build a claim map:
   - claim ID;
   - frozen value/source;
   - robustness support;
   - human decision ID;
   - figure/table reference;
   - limitation.
3. Draft the method description to match the final explanation and code.
4. Draft results with:
   - value and comparison;
   - human-confirmed physical/domain meaning;
   - uncertainty or robustness;
   - limitation and applicable scope.
5. Mention the baseline and eliminated alternatives only when they explain a real decision.
6. Use only Type 2–4 figures as appropriate; never place Type 1 diagnostics in the paper.
7. For `full_submission`, save a semantic module at `paper/sections/Qx/qx_model_and_results.md` plus `qx_section_manifest.json`. For an explicitly requested `single_problem` paper, save the requested standalone section/document without implying that it is the final multi-question paper.

# Full-Submission Assembly Contract

When the section will enter a complete contest paper:

- do not include a paper title, abstract, keywords, global problem restatement, global references, or appendix;
- include only Qx-specific formulation, solution, results, interpretation, limitations, validation pointer, and question summary;
- reference shared preprocessing, assumptions, and symbols by canonical identifier rather than restating them;
- record all claims, figures, tables, equations, upstream inputs, and downstream outputs in `qx_section_manifest.json`;
- preserve a clear interface when Qx consumes an earlier question's output;
- do not render the semantic module as a standalone DOCX for final submission.

The section manifest contains at least:

```json
{
  "schema_version": 1,
  "question_id": "Q1",
  "paper_scope": "full_submission",
  "section_role": "model_and_results",
  "source_package": "results/Q1/reports/q1_solution_package_for_writer.md",
  "upstream_inputs": [],
  "downstream_outputs": [],
  "claims": [],
  "figures": [],
  "tables": [],
  "equations": [],
  "contains_global_front_matter": false,
  "contains_references_or_appendix": false
}
```

# Human-Owned Content

The AI must not originate:

- why the method was chosen;
- what the headline number means physically;
- confidence and claim scope;
- contribution framing.

Transcribe these from the decision ledger with provenance. If absent, invoke a compact choice card and stop the final draft until answered; do not fill the paper with repeated sentinels.

# Rules

- Every numerical claim must match `frozen_numbers.json`.
- Do not overclaim against untested methods or populations.
- Do not fabricate citations or causal meaning.
- Avoid procedural diary prose and ceremonial detail.
- Keep formulas, symbols, units, captions, and filenames consistent.
- Do not create a new decision artifact.
- Do not concatenate semantic modules or per-question DOCX files; final multi-question assembly belongs to `full-paper-assembler`.

# Verification

- Three writer prerequisites pass.
- Claim map resolves all numbers and judgments.
- Method, results, and figures match canonical artifacts.
- Physical meaning and contribution are human-owned.
- Limitations and uncertainty are visible.
- No Type 1 figure appears.
- Full-submission modules contain no duplicate global front matter and have a complete section manifest.
