---
name: related-paper-analyzer
description: Collect and analyze relevant papers, Google Scholar search results, and reference mathematical models to inform method selection and populate the temporary knowledge base without fabricating references.
license: MIT
---

# Purpose

Collect and analyze relevant papers, authoritative literature, and domain mathematical models before final method selection.

This skill operates in two synchronized modes:
1. **Google Scholar & Academic Web Research Mode (Default & Proactive)**: Automatically formulates scholarly queries from the parsed problem statement, retrieves real publications and governing equations from Google Scholar, CNKI, IEEE, ScienceDirect, and arXiv, extracts transferable mathematical models, and populates the temporary knowledge base under `workspace/literature/`.
2. **Local Paper Mode**: Reads user-provided paper files or extracted texts under `workspace/papers/` when available.

This skill does not fabricate references or DOIs, does not write the final method card, and does not blindly copy infeasible black-box models.

# When to use

Use this skill:

- Immediately after `problem-parser` and `problem-classifier` have produced validated artifacts.
- Before `method-selector`.
- When the team wants to ground mathematical modeling in solid physical/chemical/economic mechanisms and authentic peer-reviewed literature.
- When populating the temporary knowledge base `workspace/literature/` for downstream modeling and citation generation.

# Preconditions

The following should already exist or be provided:

- A validated problem parse (`workspace/problem/problem-parser/problem_parse.json` or `planning/parse/problem_parse.json`).
- A validated problem classification artifact.

# Inputs

Use or request:

- `planning/parse/problem_parse.json` or `workspace/problem/problem-parser/problem_parse.json`.
- `planning/classification/problem_classification.json` or `workspace/problem/problem-classifier/problem_classification.json`.
- User notes or domain constraints, if available.
- Optional local paper files under `workspace/papers/`.

# Workflow

1. **Query Formulation for Academic Search**:
   - Extract primary research targets, governing mechanisms, reaction processes, or economic dynamics.
   - Construct precision Google Scholar search terms (both in English and Chinese), e.g. `"ethanol coupling" "catalyst deactivation" kinetics model` and `乙醇偶合 C4 烯烃 反应动力学 模型`.

2. **Google Scholar Retrieval & Metadata Verification**:
   - Conduct academic search across Google Scholar, CNKI, ScienceDirect, or arXiv.
   - Collect 100% authentic literature metadata: Title, Authors, Venue/Journal, Year, and verifiable DOI/URL.
   - Prohibit all hallucinated or fabricated citations.

3. **Mathematical Model & Governing Equation Extraction**:
   - Extract concrete mathematical formulations: ODEs/PDEs, reaction rate equations, loss functions, constraints, and statistical distributions.
   - Record realistic empirical parameter ranges, physical constants, or standard boundary values.
   - Evaluate applicability to the contest dataset and identify simplifying assumptions aligning with Occam's razor.

4. **Construct Temporary Knowledge Base Artifacts**:
   - Write search logs to `workspace/literature/scholar_search_records.json`.
   - Write structured mathematical models to `workspace/literature/candidate_models.json`.
   - Write human-readable synthesis to `workspace/literature/literature_summary.md`.
   - (Optional) If local papers exist under `workspace/papers/`, synthesize them into `workspace/papers/related_paper_analysis.md`.

5. **Map to Contest Subquestions**:
   - Assign candidate models explicitly to `Q1`, `Q2`, `Q3`, etc.
   - Separate reusable mathematical foundations from overly complex experimental apparatus.

6. **Hand off to `method-selector` and `reference-manager`**:
   - Supply the structured candidate models to `method-selector` for Occam's razor screening.
   - Pass verified metadata directly to `reference-manager` to ensure 100% authentic GB/T 7714-2015 bibliography generation.

# Outputs

Produce canonical temporary knowledge base artifacts under `workspace/literature/`:

1. `workspace/literature/scholar_search_records.json`:
   - Search query strings, dates, and authentic citation metadata (Title, Authors, Venue, Year, DOI).
2. `workspace/literature/candidate_models.json`:
   - Extracted mathematical equations, input/output variables, parameter bounds, and modeling rationale.
3. `workspace/literature/literature_summary.md`:
   - Comprehensive domain synthesis, prior literature review, and subquestion mapping.

# Output Schema Example: `candidate_models.json`

```json
{
  "target_subquestion": "Q1",
  "candidate_models": [
    {
      "model_name": "First-Order Catalyst Deactivation Kinetics",
      "source_ref_id": "ref_1",
      "core_equations": ["da/dt = -kd * a", "kd = A * exp(-Ea / (R * T))"],
      "input_variables": ["reaction time t", "temperature T"],
      "output_variables": ["activity a", "rate constant kd"],
      "parameter_ranges": {"Ea": "40-90 kJ/mol", "t_half": "10-50 h"},
      "applicability": "Isothermal fixed-bed reactor catalyst deactivation",
      "simplicity_rationale": "High numerical stability, physically meaningful parameters"
    }
  ]
}
```

# Rules

- Do not fabricate paper titles, authors, years, venues, DOIs, or conclusions.
- Ground mathematical equations in peer-reviewed literature or authoritative textbooks.
- Strictly adhere to Occam's razor: favor simple, interpretable, numerically stable models over gratuitous neural networks or intractable PDEs.
- Output artifacts must be formatted cleanly so `method-selector` and `reference-manager` can ingest them deterministically.
- All saved literature metadata must be preserved for 1-to-1 citation matching in the final paper.

# Handoff

After populating `workspace/literature/`, hand off to:

`method-selector`

The handoff includes:
- `workspace/literature/candidate_models.json`
- `workspace/literature/scholar_search_records.json`
- `workspace/literature/literature_summary.md`
