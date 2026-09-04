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
- Highlight domain, algorithmic, and statistical technical terms using bold (`**term**`) to facilitate human revision into conversational phrasing.
- Do not invent unnatural, terse compressed phrases or acronyms; use full standard terminology or explanatory clauses.
- Permit and encourage conversational, plain-language explanations where helpful for conceptual clarity and intuition.
- When the contest problem does not explicitly declare subquestions, do not write mechanical phrases like "the first subquestion of question one" or label headings with internal subproblem IDs; omit structural subjects and transition naturally by concrete task objectives.
- Model assumptions and conventions: every drafted assumption section must include explicit assumptions; title the section "模型假设与约定" if conventions exist, or dynamically adjust to "模型假设" if conventions are absent; format every assumption item using the standard template "假设……" (e.g., `假设1：假设……`).
- Mandatory in-text figure discussion: every figure placed in the text must be immediately followed by in-depth discussion centered on the visual evidence, explicitly stating conclusions (e.g., "通过上述图片得出……", "由图X可以看出……").
- Number figures and tables by chapter (e.g., `图X-Y`, `表X-Y`) in drafted sections; ensure in-text references use this scheme prior to final global renumbering.
- Do not create a new decision artifact.
- Do not concatenate semantic modules or per-question DOCX files; final multi-question assembly belongs to `full-paper-assembler`.

# Verification

- Three writer prerequisites pass.
- Claim map resolves all numbers and judgments.
- Method, results, and figures match canonical artifacts.
- Physical meaning and contribution are human-owned.
- Technical terms are highlighted in bold, no invented terse phrases appear, and conceptual explanations are plain and intuitive.
- No mechanical "subquestion" phrases appear when the original prompt lacked explicit subquestion divisions; structural subjects are omitted or task-oriented.
- Assumptions strictly use the "假设……" template and section heading dynamically reflects convention presence.
- Embedded figures are accompanied by in-depth in-text analytical discussions centered on the visual conclusions.
- Figures and tables strictly use chapter-based numbering (`图X-Y`, `表X-Y`) consistent with in-text references.
- Limitations and uncertainty are visible.
- No Type 1 figure appears.
- Full-submission modules contain no duplicate global front matter and have a complete section manifest.
