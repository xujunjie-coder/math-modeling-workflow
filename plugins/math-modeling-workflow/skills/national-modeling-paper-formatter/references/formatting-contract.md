# Neutral Chinese Modeling Paper Contract

Use the current contest rules or a user-supplied authorized template when they are more specific.

## Page and text

- A4 portrait (210×297 mm): Top margin 72 pt (2.54 cm), Bottom margin 72 pt (2.54 cm), Left margin 76.5 pt (2.7 cm), Right margin 76.5 pt (2.7 cm).
- Main title 黑体三号 16 pt bold centered, space after 16 pt; Abstract header 黑体四号 14 pt bold centered.
- Keywords line 小四 12 pt bold (黑体 label + 宋体 content, all bold), space before 12 pt, space after 12 pt.
- Headings: H1 黑体四号 14 pt bold centered (space before 12 pt, after 6 pt); H2 黑体小四 12 pt bold flush left (space before 6 pt, after 6 pt); H3 黑体小四 12 pt bold flush left, non-italic (space before 4 pt, after 4 pt).
- Chinese body text uses Song-style font (宋体 小四 12 pt); Latin text and numbers use Times New Roman (小四 12 pt).
- Body paragraphs are justified with 2-character first-line indentation and 1.25 line spacing. All body text is black (`#000000`).

## Figures and tables

- Put table captions above (10.5 pt bold centered) and figure captions below (9.5 pt bold centered).
- Use numbered captions and keep every in-text reference synchronized.
- Center figures and inspect them at final placement size.
- Standard three-line tables: top border 1.5 pt, bottom border 1.5 pt, header divider 0.75 pt. Table cells use 10.5 pt (五号) or 9 pt (小五号) single line spacing.
- **Table Cell Indent Zeroing**: Explicitly clear first-line indentation for all table cell paragraphs (`first_line_indent = Pt(0)` and XML `w:firstLine="0"`, `w:firstLineChars="0"`). This prevents inheriting Normal style's 2-character indentation, which would cause cell text wrapping and overflow.
- Symbol table: concise dictionary of 6–15 rows (max ~17 rows, within half a page), one family per line, no regression coefficients $\beta$ or error terms $\varepsilon$ or temporary indices. Local variables explained in-situ below formulas.
- Ensure all tables fit strictly within the page body width (`\textwidth`). In LaTeX, employ `tabularx` with auto-wrapping `X` columns for descriptive text columns or use `\resizebox{\textwidth}{!}{...}` for wide matrices/tables to prevent any horizontal overflow beyond the right margin.

## Equations

- Use editable Word math/OMML or clean mathematical representation.
- Display equations are centered and numbers are right aligned outside the equation object, e.g. `(1)`, `(2)`. Inline formulas are embedded in text without numbers.
- Preserve mathematical italics for variables, upright for constants/functions/units/chemistry. Text and math color strictly black (`#000000`).
- Local variables and model coefficients must be explained in-situ immediately below each equation using "设/记/其中/式中...", and "含义同前" for recurring symbols.

## Final verification

- Render to PDF and page images.
- Inspect every page for overflow, blank pages, broken tables, missing figures, glyph fallback, equation clipping, caption separation, headers, footers, and page numbering.
