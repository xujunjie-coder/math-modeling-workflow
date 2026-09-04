# Neutral Chinese Modeling Paper Contract

Use the current contest rules or a user-supplied authorized template when they are more specific.

## Page and text

- A4 portrait with conservative margins suitable for binding and PDF export.
- Chinese body text uses an available Song-style font; Latin text and numbers use a readable serif font.
- Body paragraphs are justified with consistent first-line indentation and line spacing.
- Headings use real semantic styles and a consistent Chinese/Arabic numbering hierarchy.
- The final document contains no colored teaching notes, tracked placeholders, comments, or personal information prohibited by the contest.

## Figures and tables

- Put table captions above and figure captions below.
- Use numbered captions and keep every in-text reference synchronized.
- Center figures and inspect them at final placement size.
- Prefer three-line tables; avoid clipped fixed row heights and unnecessary full grids.
- Ensure all tables fit strictly within the page body width (`\textwidth`). In LaTeX, employ `tabularx` with auto-wrapping `X` columns for descriptive text columns or use `\resizebox{\textwidth}{!}{...}` for wide matrices/tables to prevent any horizontal overflow beyond the right margin.

## Equations

- Use editable Word math/OMML or an equivalent editable equation representation.
- Display equations are centered and numbers are right aligned outside the equation object.
- Preserve mathematical italics, upright functions/units, fractions, roots, scripts, matrices, and cases structurally.

## Final verification

- Render to PDF and page images.
- Inspect every page for overflow, blank pages, broken tables, missing figures, glyph fallback, equation clipping, caption separation, headers, footers, and page numbering.
