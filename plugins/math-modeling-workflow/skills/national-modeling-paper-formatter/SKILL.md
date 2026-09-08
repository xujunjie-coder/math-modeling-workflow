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
- an authorized user-supplied DOCX template when available, or the default official national contest template at `plugins/math-modeling-workflow/assets/templates/national_contest_template.docx` (sourced from user's standard template).

Read [references/formatting-contract.md](references/formatting-contract.md) and [.agents/rules/national-contest-paper-structure.md](../../../../.agents/rules/national-contest-paper-structure.md) before formatting. When using the default national contest template, preserve its standard page geometry, margins, title styling, abstract header, three-line table layout, and heading hierarchy. Never edit the source template directly; work on a copy.

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
- Page Geometry & Margins: A4 portrait, Top margin 72 pt (2.54 cm), Bottom margin 72 pt (2.54 cm), Left margin 76.5 pt (2.7 cm), Right margin 76.5 pt (2.7 cm).
- Typography & Headings: Main title 黑体 16 pt bold centered; Abstract header 黑体 14 pt bold centered; Keywords line 小四 12 pt bold (黑体 label + 宋体 content); Level 1 headings 黑体 14 pt bold centered; Level 2 headings 黑体 12 pt bold flush left; Level 3 headings 黑体 12 pt bold flush left (non-italic); Body text 宋体/Times New Roman 小四 12 pt, 1.25 line spacing, 2-character indent.
- Three-line Tables & Cell Indent Zeroing: Standard three-line borders (top 1.5 pt, bottom 1.5 pt, header divider 0.75 pt). Table cell paragraphs MUST clear first-line indentation (`first_line_indent = Pt(0)` and XML `w:firstLineChars="0"` / `w:firstLine="0"`) to prevent inheriting Normal 2-character indentation; table cells use single line spacing, 10.5 pt (五号) or 9 pt (小五号). In LaTeX, always use `tabularx` with `X` columns for multi-word text columns (or `\resizebox{\textwidth}{!}{...}`) so tables never overflow the page margins horizontally.
- Displayed equations remain editable Word OMML / LaTeX math and separately numbered (centered equation with right-aligned number `(1)`, `(2)`); do not rasterize formulas. Mathematical variables italicized, constants/functions/chemistry upright; all text and math strictly black (`#000000`).
- Text extraction or successful file creation alone does not count as visual QA. Visual QA must inspect rendered pages to confirm no table columns are clipped or overflowing the right margin.

## Output

- `paper/final/final_paper.docx`;
- `paper/final/final_paper.pdf`;
- `paper/final/rendered_pages/`;
- a compact formatting/render verification record.
