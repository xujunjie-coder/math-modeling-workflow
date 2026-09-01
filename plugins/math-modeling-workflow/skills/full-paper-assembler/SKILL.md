---
name: full-paper-assembler
description: Assemble multiple approved mathematical-modeling question packages and semantic paper sections into one submission paper with a single global outline. Use after all active Qx sections are ready and before whole-paper polishing or DOCX/PDF formatting; do not use to concatenate Word files.
---

# Purpose

Create one evidence-traceable master paper from all active questions. Treat per-question papers and DOCX files as source evidence only, never as blocks to append.

# Preconditions

- `rigor_profile` is `submission`.
- Every active Qx reached G5 and has a current solution package, freeze, decision ledger, semantic paper section, and verified figures/tables.
- Global problem parse, assumptions, symbol table, and contest profile exist.
- Human claim-scope and contribution decisions are recorded.

Stop and route to the missing producer when a prerequisite is absent. Do not draft around missing evidence.

# Sources

Use, in order:

1. problem parse and question dependency structure;
2. `qx_solution_package_for_writer.md` and `frozen_numbers.json`;
3. `qx_section_manifest.json` and semantic question sections;
4. human decision ledgers;
5. verified figures/tables and final method/robustness reports for clarification.

Do not derive canonical claims from legacy DOCX prose or exploratory output folders.

# Workflow

1. Resolve `paper_scope`. This skill handles `full_submission`; route `single_problem` to ordinary section writing/template formatting.
2. Build `paper/master/cross_question_matrix.md` with each Qx goal, inputs, upstream dependencies, core outputs, downstream consumers, validation evidence, claims, figures, and tables.
3. Read [references/deduplication-and-mapping.md](references/deduplication-and-mapping.md) and classify every source block as global-shared, question-specific, validation, evaluation, reference, appendix, or excluded diagnostic.
4. Read [references/full-paper-outline.md](references/full-paper-outline.md), choose one global outline, and map every retained block to exactly one destination.
5. Build the assembly manifest using [references/assembly-manifest-schema.md](references/assembly-manifest-schema.md). Record provenance, duplicate disposition, downstream interfaces, and numbering maps.
6. Draft `paper/master/full_paper.md`. Write the body first; write the abstract and final conclusions last from already placed claims.
7. Create `paper/master/claim_map.json` and `paper/master/renumber_map.json` so all numerical claims, figures, tables, equations, and references remain traceable.
8. Run `scripts/validate_full_paper.py` against the master draft and manifest. Repair assembly defects without changing canonical evidence.

# Assembly Invariants

- Exactly one title, abstract, keyword line, global problem restatement, global problem analysis, assumptions section, symbol section, reference list, and appendix sequence.
- Every active Qx appears once in the model/solution chapter and has goal, method, result, validation pointer, limitation, and question summary.
- Shared preprocessing, shared assumptions, and shared symbols appear globally once; question-specific exceptions remain local and are labeled.
- A downstream question reads upstream outputs with the same sample scope, units, symbols, thresholds, labels, and versions.
- No `一、问题重述` or equivalent global heading may restart inside a `6.x` question section.
- Every number resolves to a current freeze; every interpretive judgment resolves to a human decision ID.
- Every figure/table reference resolves to an existing verified artifact. Captions cannot survive without their artifact.
- Numbering is continuous across the whole paper rather than restarting per Qx.
- Abstract and conclusion contain no claim absent from the assembled body.

# Prohibited Merge Patterns

- Appending DOCX body XML or copying fixed paragraph ranges.
- Concatenating complete per-question papers with their own front matter, references, or appendices.
- Compressing a question to headline results when its formulation or validation is needed for reproducibility.
- Recomputing or silently reconciling conflicting numbers during writing.
- Keeping diagnostic figures solely because they existed in a question draft.

# Outputs

- `paper/master/cross_question_matrix.md`
- `paper/master/assembly_manifest.json`
- `paper/master/claim_map.json`
- `paper/master/renumber_map.json`
- `paper/master/full_paper.md`

The master Markdown is the only content input to whole-paper polishing and final document formatting. Per-question DOCX files remain intermediate artifacts.

# Verification and Handoff

- Structural validator passes.
- All active Qx and dependency interfaces are covered.
- Duplicate disposition and provenance are recorded.
- No missing/orphan figure, table, equation, or claim exists.
- Route next to `paper-polisher` in whole-paper mode, then to `national-modeling-paper-formatter` with `paper_scope=full_submission`.
