---
name: workflow-orchestrator
description: Inspect a mathematical-modeling workspace, evaluate lean or submission gates per subquestion, update machine-readable manifests, classify change impact, and route one next action without duplicating downstream work.
---

# Purpose

Act as the gate-driven scheduler and state reader. Do not solve models, write model code, or draft paper sections.

`../../AGENTS.md` is the packaged policy source. Prefer a project-root `AGENTS.md` when one exists; otherwise read the packaged copy relative to this `SKILL.md`. Apply that policy without reproducing large reports or dashboards.

# Session Start

Before orchestration in a new workspace:

- show `git status --short`;
- check the chosen runtime and required core packages;
- verify the workspace skeleton needed for the current request;
- read `planning/session_config.json`, accepting legacy `mode`.

Report warnings concisely. Do not create the full project skeleton unless the user is initializing a project.

# State Sources

Prefer, in order:

1. `planning/manifests/Qx.json`
2. canonical artifacts on disk
3. legacy dashboard and legacy method/decision artifacts

Never trust a dashboard over newer canonical artifacts.

# Manifest Contract

Maintain one compact JSON manifest per subquestion:

```json
{
  "schema_version": 1,
  "question_id": "Q1",
  "rigor_profile": "lean",
  "current_gate": "G2",
  "status": "method_screened_waiting_human",
  "artifacts": {
    "method_card": "methods/Q1/q1_method_card.md",
    "decision_ledger": "methods/Q1/q1_decisions.jsonl",
    "risk_probe": "methods/Q1/probes/risk_probe_summary.json",
    "latest_run": null
  },
  "allowed": {
    "code_generation": false,
    "freeze": false,
    "paper_writing": false,
    "final_assembly": false
  },
  "blockers": [],
  "next_action": {
    "owner": "human",
    "skill": "decision-prompt-builder",
    "reason": "method choice not recorded"
  },
  "updated_at": "ISO-8601"
}
```

Update only fields affected by the current state change. Generate a human dashboard on request or at a milestone; otherwise derive status directly from manifests.

# Gate Evaluation

Evaluate each Qx independently.

## G1 — PROBLEM_FRAMED

Pass when parse, classification, data inventory, success criteria, and human framing exist. A placeholder in a human-owned field blocks the gate.

## G2 — METHOD_SCREENED

Pass when:

- `qx_method_card.md` defines a main candidate and usable baseline;
- the baseline completes the real task with comparable output;
- `risk_probe_summary.json` covers applicable checks, including output degeneracy;
- main and baseline verdicts are `PASS` or justified `CONDITIONAL`;
- any fallback has a concrete trigger.

Do not require a fixed number of candidates, universal PoCs, or a source-line limit.

## G2.5 — METHOD_CHOSEN_BY_HUMAN

Pass when `qx_decisions.jsonl` contains a human `DECIDED` method choice citing probe evidence. While blocked, allow data preparation but not model code generation.

## G3 — CODE_AND_EXPERIMENT_REVIEWED

Pass when:

- approved main and baseline executed;
- latest `run_summary.json` is complete;
- language review contains passing named checks for syntax, input contract, method alignment, reproducibility, and output contract.

Accept legacy Markdown review artifacts during migration, but prefer JSON for new work.

## G4 — RESULTS_JUDGED_AND_FROZEN

In `lean`, pass the result-judgment subgate when final-result and stability decisions cite computed evidence. Continue iterating without freezing when the human selects `adjust` or `fallback`.

In `submission`, additionally require:

- final method explanation;
- final result analysis;
- robustness report;
- package sign-off in the decision ledger;
- solution package;
- current `frozen_numbers.json`.

## G5 — PAPER_SECTION_READY

Require the three writer rules, frozen-number sourcing, human-confirmed interpretation/claim scope, a current figure/table plan for result-bearing claims, and verified Type 3/4 figures when the plan calls for them.

## G5.5 — FULL_PAPER_ASSEMBLED

Evaluate globally after every active submission Qx passed G5. Require:

- `paper/master/cross_question_matrix.md`;
- `paper/master/assembly_manifest.json` covering every active Qx with unique `6.x` destinations;
- `paper/master/claim_map.json` and `renumber_map.json`;
- one current `paper/master/full_paper.md` produced by `full-paper-assembler`;
- passing automated `paper-rigor-gatekeeper` audit (`audit_paper_rigor.py`) verifying text-formula consistency, DoE parameters, statistical threshold sourcing, and academic restraint;
- passing automated narrative audit (`audit_paper_narrative.py`);
- passing structural assembly validation.

Per-question DOCX files or concatenated question papers do not satisfy this gate.

## G5.6 — FORMATTED_AND_RENDERED

Require the whole-paper polish to be current, `paper_scope=full_submission`, and final DOCX/PDF artifacts generated from the master paper. Every rendered page must have passed visual inspection; text extraction alone is insufficient.

## G6 — FINAL_AUDIT_PASSED

Evaluate only in `submission` after G5.6. Require passing final consistency, completeness, and QA artifacts against the assembled master and rendered final document. Never infer that one auditor covers another.

# Deterministic Enforcement

Gate prose is backed by `../../scripts/gate_check.py` (standard library only). Prefer its evidence over a self-reported manifest; the manifest is never authoritative by itself.

- State inspection: `python scripts/gate_check.py <workspace> status [--json]`. It computes the highest gate actually supported by on-disk artifacts. Exit code 2 means an integrity violation (manifest gate runs ahead of evidence, an `allowed` flag is true without evidence, or model code exists before G2.5).
- Hard action guard — run before the corresponding write action and stop when it exits non-zero:
  - model code generation → `gate_check.py <ws> guard --action code_generation --question Qx` (requires G2.5);
  - result freeze → `guard --action freeze --question Qx` (requires G3);
  - paper section writing → `guard --action paper_writing --question Qx` (requires G4; frozen numbers in submission);
  - global assembly → `guard --action final_assembly` (every active question at G5).
- A data-free/mechanism-only question may declare `"waivers": ["data_profile"]` in its manifest; the check is then reported as waived rather than silently skipped. No other gate evidence may be waived.
- The guard does not replace the Skill checks; it blocks work that the gate contract does not yet authorize.

# Core Backbone Routing (五阶段主干路由)

为防止 32 个精细化辅助技能造成认知过载与碎片化，编排器强制将工作流收敛为**五大主干战役阶段**，在每个阶段精准调度对应的核心主力技能：

1. **阶段一（审题、文献与数据实核）**：
   - 核心调用：`problem-parser` + `data-auditor-cleaner`；
   - 必须产出：赛题抽象画像、临时文献知识库 `workspace/literature/`、数据清洗分布图与缺失值实核。
2. **阶段二（方法选型与机理代码实现）**：
   - 核心调用：`method-selector` + `python-model-code-generator`；
   - 必须产出：严守奥卡姆剃刀与简单机理模型（拒绝无物理机理的高次黑箱）、可复现代码、`frozen_numbers.json` 计算凭证。
3. **阶段三（统一科研级图版规划与视觉质检）**：
   - 核心调用：`scipilot-figure` + `figure-table-planner`；
   - 必须产出：坚守“表图 2:1 黄金平衡律”（表图比 1.5:1 ~ 2.2:1，全书规划 8~10 幅多面板复合科研图版 vs 15~20 张三线表，每 2~3 页必有彩色视觉锚点，消除评委阅读疲劳）；执行“先思考后绘图”8 步闭环、红蓝科研级发散色板、多面板复合高清插图 `paper/latex/figures/`；长表格采用双栏并排压缩法为增图预留版面。
4. **阶段四（逐题破案式深度论文撰写与即时去 AI 味消杀）**：
   - 核心调用：`paper-section-writer` + `paper-polisher`（每题撰写完成后立即执行第 13 项去 AI 味专项审查，坚决清洗免责套娃、空洞总结、模糊建议词与“说明可能”两头占）；
   - 必须产出：**强制遵循 `.agents/rules/reference-template-logic.md`**，单题严格按照“通俗引桥 $\rightarrow$ 机理方程 $\rightarrow$ 四类三线表 $\rightarrow$ 深度反应工程机理归因 $\rightarrow$ 决策矩阵/DoE 设计”四步闭环展开，每题 2500~3500 字，四题总字数逾万字。
5. **阶段五（全篇穿透总装、G5.5 去 AI 味双轨硬核质检与排版）**：
   - 核心调用：`full-paper-assembler` + `paper-rigor-gatekeeper`（由 `gate_check.py` 在 Gate G5.5 自动联动执行 `audit_paper_narrative.py` 与 `audit_paper_rigor.py`，违禁 AI 套话与表图失衡一票否决）+ `renumber_figures_tables.py` + `compile_latex.py` / `build_complete_word.py`；
   - 必须产出：五段式量化摘要、图表全局连续重编号、100% 满分通过叙事与去 AI 味质检、**20~30 页超清学术 PDF（当前实测标杆为 24~28 页）与 Word 提交版**，强制前置版本号与时间戳（绝不覆盖历史文件）。

# Pacing & Page Budget Standards (慢工出细活与篇幅预算)

- **慢工出细活铁律**：严禁急于求成跳步或快餐式秒出论文。核心价值在于公式完整推导、中间步骤展开、全样本三线表呈现（包含全部 21 组参数，严禁写“其余略”）与微观机理深度归因；
- **表图 2:1 黄金平衡律与视觉节奏**：全篇图表比例严格控制在 1.5:1 ~ 2.2:1（8~10 幅多面板插图 vs 15~20 张三线表），绝不出现“表多图少（>2.8:1）”导致的审美疲劳；超过 20 行的长表强制双栏并排压缩，保证扩图后总页数严格锁死在 30 页以内；
- **20~30 页国赛黄金学术篇幅**：
  - 前置部分（独立成页且严格恰好 1 页的五段式摘要、重述/分析/假设/符号/清洗）：约 4~5 页（摘要严禁跨页溢出，800~1000字，后紧跟强制分页符，正文一、问题重述从第 2 页顶格开始）；
  - 核心建模（Q1~Q4 逐题破案展开）：约 12~18 页（每题 3~4.5 页）；
  - 后置部分（评价/AI声明/真实文献/附录代码）：约 4~7 页；
  - 全篇总厚度稳定锁定在 **20~30 页** 黄金区间，由质检脚本全面保驾护航。

# Change Impact

Classify changes before scheduling checks:

- `NONE`: scratch, formatting, comments, non-semantic docs.
- `LOCAL`: exploratory code or method-card updates before freeze.
- `CANONICAL`: schema/units, symbols, equations, parameters, official values, figure paths.
- `FROZEN`: changes affecting frozen values or paper claims.

Route checks:

- `NONE`: none.
- `LOCAL`: local tests/review.
- `CANONICAL`: scoped consistency for affected Qx.
- `FROZEN`: thaw log, rerun affected work, re-freeze, scoped consistency.

Never schedule a full-workspace consistency audit solely because more than one file changed.

# Lean vs Submission

In `lean`:

- require only manifests, method card, decision ledger, probe summary, and run summaries;
- do not require per-round Markdown reports, full success logs, frozen numbers, paper artifacts, or final audits;
- persist a detailed report only at a human decision point or final round.

In `submission`:

- require final explanations, reviews, analyses, robustness, package, freeze, paper, and G6;
- require G5.5 global assembly and G5.6 rendered final artifacts;
- run the full three-auditor layer after final assembly and render verification.

# Compatibility

Read legacy artifacts when new ones are absent:

- `planning/progress_dashboard.md`
- `qx_method_candidates.md`
- `qx_method_iteration_log.md`
- `qx_decision_log.md`
- `decisions/*_modeler_decision.md`
- Markdown code reviews

Mark them `legacy_source` in the manifest and recommend migration at the next material edit. Do not regenerate legacy files for new work.

# Output

Return a compact state report:

- profile;
- per-question current gate and blocker;
- artifacts changed or missing;
- change-impact class;
- one next action;
- optional runners-up only when they can proceed independently.

Do not paste a full dashboard or large JSON structure unless the user asks.

# Verification

- State is derived from current canonical artifacts.
- Lean requirements are not confused with submission requirements.
- Human decisions were not inferred from AI suggestions.
- Code generation, freeze, paper writing, and final assembly flags match the gates.
- Global G5.5/G5.6 state is not inferred from per-question completion.
- Audit scope matches semantic impact.
- Manifest and reported next action agree.
