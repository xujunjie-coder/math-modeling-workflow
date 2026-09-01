---
name: national-modeling-paper-formatter
description: Format and render-verify a Chinese mathematical-modeling contest paper from an approved master Markdown file, using a user-supplied authorized DOCX template when available and a documented neutral format otherwise.
---

# National Modeling Paper Formatter

Create the final DOCX/PDF only after `full-paper-assembler` and whole-paper polishing are current. Do not calculate model results or rewrite frozen claims.

## Inputs

- `paper/master/full_paper.md` and its assembly manifest;
- frozen numbers, figure manifest, reference list, and appendices;
- the current contest formatting rules;
- an authorized user-supplied DOCX template when available.

Read [references/formatting-contract.md](references/formatting-contract.md) before formatting. If the user supplies a template, inspect it and preserve its authorized page geometry and semantic styles. Never assume a private or third-party template is redistributable.

## Workflow

1. Confirm `paper_scope=full_submission`, G5.5 passed, and the master paper is the only content authority.
2. Resolve the applicable contest rules and user-supplied template. Record any explicit deviations from the neutral contract.
3. Generate one DOCX from the master Markdown. Do not concatenate per-question Word files.
4. Preserve editable equations, real heading levels, figure/table captions, cross-references, references, and appendices.
5. Render the DOCX to PDF and page images with an available document/PDF toolchain.
6. Inspect every page at final size for clipping, overlap, broken tables, unreadable figures, missing glyphs, bad page breaks, and stray placeholders.
7. Iterate until visual checks pass, then record the DOCX, PDF, rendered-page paths, template source, and verification status in the project manifest.

## Rules

- Do not invent content to fill template slots.
- Do not edit a user-supplied template in place; work on a copy.
- Remove instructional annotations and sample content from a supplied template.
- Keep all final text anonymous when the contest requires anonymity.
- Use three-line tables unless the contest or data structure requires another form.
- Figures must use the verified outputs registered by `math-figure-generator`.
- Displayed equations remain editable and separately numbered; do not rasterize formulas.
- Text extraction or successful file creation alone does not count as visual QA.

## Output

- `paper/final/final_paper.docx`;
- `paper/final/final_paper.pdf`;
- `paper/final/rendered_pages/`;
- a compact formatting/render verification record.
