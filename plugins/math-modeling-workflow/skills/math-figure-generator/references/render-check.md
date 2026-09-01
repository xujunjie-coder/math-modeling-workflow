# Render Check

Inspect the rendered image or PDF page, not only the plotting code.

## Required checks

- no clipped title, axis label, legend, annotation, or colorbar;
- no overlapping labels that obscure values;
- readable font size at final placement dimensions;
- correct units, ordering, scales, and category labels;
- no empty or unintended subplot;
- color and marker distinctions survive grayscale or common color-vision deficiencies;
- uncertainty, baseline, and main method are identified correctly;
- caption and visual support the same claim;
- source row/count/metric agrees with the canonical data artifact;
- Type 3/4 output exists under `paper/figures/`.
- PDF/SVG and PNG were generated from the same code and show the same content;
- PNG metadata or pixel dimensions are consistent with the declared placement size and resolution;
- Chinese glyphs, minus signs, superscripts/subscripts, and mathematical symbols render correctly;
- related heatmaps share variable order, limits, center, and colorbar meaning;
- matrix annotations remain legible; if not, the figure uses selective annotations and the exact values remain available in a source table;
- the figure was inspected at its intended paper width, not only zoomed in on a large standalone canvas.

Record failures concisely and rerender after correction.

## Acceptance record

For submission figures, retain a compact record containing the figure ID, source artifact, claim ID when available, output paths, intended width, render result, and any deliberate omission such as masked matrix cells or selective annotations. This may live in the figure plan or solution manifest rather than a separate report.
