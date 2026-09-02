# 目录命名映射：教学结构、脚手架与 Skill 规范路径

本工作流中同时出现三套目录命名，它们不是三个互相竞争的方案，而是三个层次：

| 层次 | 出处 | 角色 |
|---|---|---|
| A. 教学结构 | `assets/workflow/competition-workflow.zh-CN.md` | 面向人讲方法论，用 `problem_1/subproblem_x` 描述“大问/小问”的思维方式 |
| B. 脚手架 | `scripts/init_workspace.py` 实际创建的空目录 | 项目初始化时落地的物理目录 |
| C. Skill 规范路径（canonical） | 各 `SKILL.md` 的输出契约、`scripts/gate_check.py` 的判定依据 | Agent 与脚本真正读写、门控真正检查的路径 |

**规则：Agent 执行与门控判定一律以 C（canonical）为准；A 只是讲解时的叫法；B 创建的目录是 C 的子集落地。** 小问编号在 canonical 中统一为 `Q1`、`Q2`、`Q1_sub1`（正则 `^Q[0-9]+(?:_sub[0-9]+)?$`）。

## 1. 概念级一一对应

| 概念 | A 教学命名 | B 脚手架 | C Skill canonical |
|---|---|---|---|
| 题目与附件 | `problem_statement/` | `problem_statement/` | 只读输入，路径不强制 |
| 原始数据（只读） | `data_raw/` | `data_raw/`（根级，legacy） | `workspace/data_raw/`（根级路径在迁移期仍可读取） |
| 清洗数据 | `data_clean/` | `data_clean/`（根级，legacy） | `workspace/data_clean/` |
| 数据画像 | 数据审查 JSON | — | `workspace/data/data_profile.json` |
| 大问 | `problem_1/` | 由 `active_questions` 声明 | `Q1` |
| 子问 | `subproblem_1/` | — | `Q1_sub1` |
| 问题解析 | `workflow/` 记录 | `planning/` | `planning/parse/problem_parse.json` |
| 问题分类 | — | — | `planning/classification/problem_classification.json` |
| 每问清单 | `subproblem_manifest.json` | `planning/manifests/` | `planning/manifests/Q1.json` |
| 全局配置 | — | `planning/session_config.json`（模板） | `planning/session_config.json` |
| 人工决策台账 | `workflow/` | `planning/decisions/` | `methods/Qx/qx_decisions.jsonl`；全局早期决策在 `planning/framing_decisions.jsonl` |
| 方法说明 | `subproblem_x/method.md` | `methods/` | `methods/Qx/qx_method_card.md` |
| 风险探针 | — | — | `methods/Qx/probes/risk_probe_summary.json` |
| 代码计划 | — | — | `code/Qx/qx_code_plan.md`（MATLAB：`code/matlab/Qx/`） |
| 模型代码 | `subproblem_x/model_code.py` | `code/` | `code/Qx/qx_main.py`、`qx_baseline.py`（MATLAB：`code/matlab/Qx/`） |
| 代码评审 | — | — | `code/Qx/reviews/qx_python_review.json` |
| 实验轮次结果 | `subproblem_x/{tables,figures,metrics}` | `results/` | `results/Qx/experiments/roundN/{tables,figures,metrics,run_summary.json}` |
| 大问最终结果包 | `problem_1/final/` | — | `results/Qx/reports/` + 最新轮 `run_summary.json` |
| 最终结果分析 | `problem_1_final.md` | — | `results/Qx/reports/qx_final_result_analysis.md` |
| 最终方法说明 | — | — | `methods/Qx/qx_final_method_explanation.md` |
| 稳健性 | `metrics/` 中的敏感性结果 | `robustness/` | `robustness/Qx/qx_robustness_summary.json`（submission 另出 `qx_robustness_report.md`） |
| 写作者结果包 | — | — | `results/Qx/reports/qx_solution_package_for_writer.md` |
| 冻结数字 | `solution_manifest.json` | — | `results/Qx/reports/frozen_numbers.json` |
| 图表计划 | — | — | `methods/Qx/qx_figure_table_plan.md` |
| 探索图（不进论文） | `subproblem_x/figures/` | — | `results/Qx/experiments/roundN/figures/`（Type 1/2） |
| 论文图 | `final/figures/` | `paper/figures/` | `paper/figures/Qx/`（Type 3/4，矢量+PNG） |
| 小问论文 | `subproblem_x/paper.md` | `paper/sections/` | `paper/sections/Qx/qx_model_and_results.md` + `qx_section_manifest.json` |
| 整篇论文母稿 | `final_paper/` | `paper/master/` | `paper/master/full_paper.md`（另含 matrix/manifest/claim_map/renumber_map） |
| 最终成稿 | `final_paper/` | `paper/final/` | `paper/final/final_paper.docx`、`final_paper.pdf`、`rendered_pages/` |
| 三审记录 | — | — | `paper/audits/{cross_media_consistency_audit,completeness_audit,qa_report}.md` |
| 交付目录 | `deliverable/` | `deliverables/` | `paper/final/` 成稿 + `deliverables/` |
| 内部排版脚本 | `internal_tools/` | — | 非 canonical，不随模型代码交付、不重新计算结果 |

### 命名前缀约定（重要）

- **目录名**做小问替换：占位符 `Qx` 替换为实际编号，如 `methods/Qx/` → `methods/Q1/`、`code/Qx/` → `code/Q1/`（MATLAB 为 `code/matlab/Q1/`）。
- **共享证据文件名**保留字面前缀 `qx_`，不随编号替换：`methods/Q1/qx_method_card.md`、`methods/Q1/qx_decisions.jsonl`、`code/Q1/reviews/qx_python_review.json`、`robustness/Q1/qx_robustness_summary.json`。门控器 `gate_check.py` 按这一约定查找证据。
- **每问可执行代码**用小写编号前缀：`code/Q1/q1_main.py`、`q1_baseline.py`（与 `run_summary.json` 的 `script` 字段一致）。
- 子问编号形如 `Q1_sub1`，目录与 manifest 均用该完整 id。

## 2. 一个小问的生命周期对照

教学叙述“在 `problem_1/subproblem_2/` 里写方法、跑代码、出表图、写小论文”，在 canonical 下展开为：

```text
methods/Q1/qx_method_card.md                         # 方法卡（含 main 与 usable baseline）
methods/Q1/probes/risk_probe_summary.json            # 风险探针
methods/Q1/qx_decisions.jsonl                        # 人工方法选择（G2.5）
code/Q1/q1_main.py, q1_baseline.py                   # 主方法 + 可用基线
results/Q1/experiments/round1/run_summary.json       # 第一轮运行
code/Q1/reviews/q1_python_review.json                # 代码评审（G3）
methods/Q1/qx_decisions.jsonl  # result_verdict      # 人工结果裁决（lean 终点 G4）
```

## 3. 迁移与兼容约定

- 根级 `data_raw/`、`data_clean/` 是教学结构遗留路径，`data-auditor-cleaner` 在迁移期读取；新项目推荐直接使用 `workspace/data_raw/`、`workspace/data_clean/`。
- 历史的 `methods/Qx/qx_decision_log.md`、`methods/Qx/decisions/*_modeler_decision.md` 统一迁移为 append-only 的 `methods/Qx/qx_decisions.jsonl`，一行一个 JSON，旧记录只迁已完成的人工决策。
- 被否决的方法/代码移动到 `workspace/archived/Qx/<method>_REJECTED_roundN/`，不要删除决策历史。
- 任何文档、脚本或示例新增路径时，以本表 C 列为准；新增 canonical 路径必须同步更新 `gate_check.py` 的证据契约与本表。

## 4. 如何验证当前项目落在哪些门

```powershell
python plugins/math-modeling-workflow/scripts/gate_check.py <项目目录> status
```

它只依据 C 列 canonical 路径上的真实证据判门，不读取 A 的教学目录名，也不相信 manifest 的自报进度。
