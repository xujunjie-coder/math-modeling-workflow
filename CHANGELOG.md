# Changelog

All notable changes are documented here. Versions follow Semantic Versioning.

## 0.2.1 - 2026-09-08

### Added
- Register the `paper-rigor-gatekeeper` and `scipilot-figure` Skills in the explicit stage-routing registry so the repository validator and orchestrator remain synchronized with the shipped 32 Skills.

### Changed
- Align workflow documentation and quick-start materials with the 32-Skill package.

### Fixed
- Resolve the CI failure where `validate_repo.py` reported `paper-rigor-gatekeeper` and `scipilot-figure` as unregistered Skills.

## 0.2.0 - 2026-09-02

### Added
- `scripts/gate_check.py`: deterministic gate enforcer (standard library only). `status` evaluates the highest gate actually supported by on-disk artifacts and reports integrity violations (manifest running ahead, `allowed` flag without evidence, model code before G2.5); `guard` hard-blocks `code_generation` (G2.5), `freeze` (G3), `paper_writing` (G4), and `final_assembly` (all questions at G5). Only human-owned (`decided_by=human`) decisions advance a gate; data-free questions declare an explicit `data_profile` waiver.
- `scripts/check_frozen_numbers.py`: mechanical paper-number vs frozen/metrics consistency linter. Skips section/figure/equation numbers, years, code spans, URLs and math; exact normalization (thousands separators, trailing zeros, scientific notation), NEAR rounding warnings, UNFROZEN hard failure, and a sidecar `.frozenignore`.
- `docs/directory-mapping.zh-CN.md`: explicit mapping across the teaching layout (`problem_1/subproblem_x`), the initializer layout, and canonical Skill paths, including the `Qx`/`qx_` naming convention.
- `docs/lean-to-submission-checklist.zh-CN.md`: artifact-by-artifact upgrade checklist from lean (G4) to submission (G6).
- `docs/agent-agnostic-loading.zh-CN.md`: load the workflow outside Codex (Claude Code, Cursor, ordinary chat sessions), with humans routing and scripts enforcing.
- End-to-end lean golden example under `examples/synthetic-demo`: standard-library OLS main method vs mean baseline, real reproducible metrics, robustness study, and a canonical artifact at every gate G0–G4 (verified to reach G4 by `gate_check.py`).
- Tests grow from 1 to 42: table-driven coverage of gate evaluation/guards, frozen-number extraction/classification, full-paper structure, template/schema/enforcer consistency, repository routing and robust front matter. CI adds the full-paper self-test, enforcement-script CLI smoke, and compiles the whole plugin tree.

### Changed
- `scripts/validate_repo.py`: replaced suffix-guess route checking with an explicit `STAGE_ROUTES` registry kept in two-way sync with skills on disk; orchestrator references now resolve against real skills; front matter parsing tolerates BOM/CRLF/EOF and reports malformed lines and duplicate keys.
- `scripts/init_workspace.py`: created directories now mirror canonical paths (`planning/parse`, `planning/classification`, `workspace/data*`, `paper/audits`); root-level data dirs remain as documented legacy/teaching locations.
- `manifest.schema.json`: adds the explicit `waivers` field.
- `.gitignore`: whitelist the golden example's `results/`, `robustness/`, and `data_clean/` evidence so the shipped example is complete, while real-project output directories stay ignored.
- `workflow-orchestrator`, `consistency-auditor` skills and both READMEs document the deterministic enforcers; READMEs link the new docs.

## 0.1.0 - 2026-09-01

- Publish the repository-backed Codex plugin and Marketplace entry.
- Include 30 modeling workflow skills with `workflow-orchestrator` as the main entry point.
- Add lean/submission gates, formal figure planning and generation, master-paper assembly, generic national-paper formatting, and three final audits.
- Add a non-destructive workspace initializer, JSON schemas, a synthetic example, tests, and GitHub Actions validation.
- Exclude private contest data, current-project status, and non-redistributable DOCX templates.
