---
name: math-figure-generator
description: Generate and render-verify publication-quality static mathematical-modeling figures from approved plans and saved evidence, with deterministic code, vector/raster outputs, traceable sources, and a consistent visual system.
---

# Preconditions

- Figure type, source artifacts, and target claim are known.
- Type 3 claim is human-confirmed.
- Submission figures use final/frozen evidence.

# References

Load only what the requested chart needs:

- `references/chart-patterns.md` for the selected chart family, especially matrices, distributions, sensitivity, classification, or multi-panel evidence;
- `references/color-systems.md` when choosing categorical, sequential, or diverging color mappings;
- `references/layout-guide.md` for final paper dimensions, Chinese typography, or multi-panel composition;
- `references/render-check.md` before accepting any Type 3/4 output.

# Workflow

1. Verify source files and the exact variables/units to plot.
2. Choose the smallest chart form that communicates the claim and preserve comparable scales/order across related figures.
3. Generate with deterministic code. Prefer matplotlib for submission figures; seaborn may simplify statistical plots, NetworkX may support networks, and Plotly is primarily for exploration unless a verified static export is required.
4. Use a shared project plotting style when several figures are produced; do not hand-draw final statistical charts cell-by-cell with a raster canvas when a plotting library can preserve scales, typography, and vector output.
5. Save editable source code and paired outputs: vector PDF or SVG when compatible, plus a PNG fallback. Type 3/4 PNG output should normally be 600 dpi and must be at least 300 dpi.
6. Apply the shared color, typography, sizing, and labeling conventions at the intended paper placement width.
7. Render the individual figure and, when it is already embedded, the target paper page; inspect both visually.
8. Check clipping, overlap, illegible text, misleading axes, legends, empty panels, colorbar semantics, and source/claim mismatch.
9. Compare plotted counts, extrema, labels, and key annotations against the canonical source artifact.
10. Iterate until render checks pass and record paths/status in the figure plan or solution manifest.

# Output Locations

- Type 1/2 exploration: `results/Qx/experiments/roundN/figures/`
- Type 3/4 submission: `paper/figures/Qx/`

Use stable descriptive filenames. Do not copy Type 1 diagnostics into the paper directory.

# Figure Requirements

- Labels include units where applicable.
- Captions state what is shown and the evidence-backed takeaway without overstating causality.
- Baseline is visually distinct but not exaggerated.
- Uncertainty is shown when it is part of the claim.
- Type 3/4 output includes vector PDF or SVG when compatible and a PNG fallback; PNG is normally 600 dpi and never below 300 dpi.
- Chinese text uses an available CJK font with an explicit fallback; minus signs, mathematical symbols, and embedded vector text render correctly.
- Related heatmaps share variable order, limits, center, and color semantics. Diverging matrices use a meaningful center such as zero; sequential quantities do not use a diverging palette.
- Dense matrix annotations are selective or moved to a companion table when all-cell labels would be unreadable.
- Accessibility and grayscale differentiation are considered.

# Rules

- Do not fabricate or manually alter plotted values.
- Do not use a chart type that hides concentration, uncertainty, or negative results.
- Do not truncate axes misleadingly.
- Do not create decorative 3D effects.
- Do not upscale a low-resolution image as a substitute for regenerating it from source data.
- Do not manually edit plotted values, labels, or significance marks in an image editor.
- Do not treat code execution as render verification.
- Keep diagnostic and paper roles separate.

# Verification

- Source, claim, type, and target section agree.
- Render inspection passed.
- Text is readable at final paper size.
- Legends, colors, markers, axes, units, and captions are consistent.
- Vector and raster outputs agree, and the raster carries the declared resolution.
- Key plotted values and category counts agree with the canonical source.
- Final output path exists and is recorded in the figure plan.
