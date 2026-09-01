# Skill Routing Map

`workflow-orchestrator` is the normal public entry point. It reads canonical artifacts and routes one primary next action. Users may explicitly invoke a specialist skill when they already know the desired stage.

| Gate or need | Primary skill | Important downstream artifact |
|---|---|---|
| Workspace initialization and state | `workflow-orchestrator` | `planning/session_config.json`, manifests |
| Problem framing | `problem-parser` | parsed problem frame |
| Output/task classification | `problem-classifier` | task type and framing choice |
| Data readiness | `data-auditor-cleaner` | reusable data profile |
| Shared notation | `symbol-table-builder` | global symbol/unit table |
| Assumptions | `model-assumptions-builder` | global and method assumptions |
| Literature support | `related-paper-analyzer` | verified reference-method notes |
| Method screening | `method-selector` | main, baseline, optional fallback |
| Human choice | `decision-prompt-builder`, `modeler-decision-logger` | canonical JSONL decision ledger |
| Implementation contract | `model-code-analyzer` | language-neutral code plan |
| Python implementation | `python-model-code-generator` | reproducible experiment package |
| MATLAB implementation | `matlab-model-code-generator` | reproducible experiment package |
| Review routing | `code-reviewer` | selected language reviewer |
| Python verification | `python-code-reviewer` | compact JSON review |
| MATLAB verification | `matlab-code-reviewer` | compact JSON review |
| Evidence summary | `result-report-generator` | decision or final result report |
| Robustness | `robustness-checker` | targeted robustness evidence |
| Final method narrative | `final-method-explainer` | authoritative method explanation |
| Visual choice | `figure-table-planner` | traceable figure/table plan |
| Formal figures | `math-figure-generator` | code, vector output, raster fallback |
| Freeze package | `solution-package-builder` | solution package and frozen numbers |
| Per-question paper | `paper-section-writer` | `paper/sections/Qx.md` |
| Master paper | `full-paper-assembler` | `paper/master/full_paper.md` |
| Language and claims | `paper-polisher` | polished master draft |
| DOCX/PDF formatting | `national-modeling-paper-formatter` | rendered final document |
| Cross-media consistency | `consistency-auditor` | scoped or final audit |
| Required evidence | `completeness-auditor` | profile-aware audit |
| Submission readiness | `quality-assurance-auditor` | final QA verdict |

## Gate summary

- G1: problem framed.
- G2: method and usable baseline screened.
- G2.5: human method decision recorded.
- G3: code, experiment, and named checks reviewed.
- G4: results judged; submission mode additionally freezes final evidence.
- G5: each active question has an evidence-backed paper section and verified planned visuals.
- G5.5: all active questions are assembled once into one master paper.
- G5.6: the master is formatted, rendered, and inspected page by page.
- G6: consistency, completeness, and quality-assurance audits all pass.
