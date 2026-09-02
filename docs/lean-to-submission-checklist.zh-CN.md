# 从 lean 探索档升级到 submission 参赛档：补件清单

`rigor_profile` 有两档：

- **lean（探索档）**：快速验证思路，每个活动问题止于 **G4**（人工 `result_verdict`）。只需要方法卡、风险探针、人工方法选择、可复现实验、代码评审、结果裁决。不要求最终报告、冻结数字、论文与 G6 审计。
- **submission（参赛档）**：产出可提交论文，每个问题走到 **G5**，全局走到 **G5.5 → G5.6 → G6**。

升级不是推倒重来：lean 阶段的方法卡、决策台账、实验轮次、评审 JSON 全部复用，缺什么补什么。每补完一项可用 `gate_check.py status` 复核。

## 0. 切换档位

- [ ] `planning/session_config.json` 的 `rigor_profile` 改为 `submission`。
- [ ] 每个 `planning/manifests/Qx.json` 的 `rigor_profile` 同步为 `submission`，并按实际证据更新 `current_gate` 与 `allowed`（门控器会抓“清单超前于证据”）。

## 1. 每个活动问题（G4 → G5）

### 1.1 稳健性成文

- [ ] 在 `robustness/Qx/qx_robustness_summary.json` 已有机器证据基础上，产出 `robustness/Qx/qx_robustness_report.md`。
- [ ] 若 summary 出现 `CONDITIONAL`/`FAIL`，在 `methods/Qx/qx_decisions.jsonl` 追加人工 `stability_verdict` 决策。

### 1.2 三份最终说明

- [ ] `methods/Qx/qx_final_method_explanation.md`（最终方法、公式、假设、基线、回退是否触发、适用范围）。
- [ ] `results/Qx/reports/qx_final_result_analysis.md`（主方法 vs 基线、误差与不确定性、退化/集中性、局限，每个数字标注来源路径）。
- [ ] `results/Qx/reports/qx_solution_package_for_writer.md`（写作者单一结果包）。

### 1.3 主张冻结（反编造关键）

- [ ] 对每条顶层主张走一次 keep / downgrade / drop 选择卡，把人工 `package_signoff` 决策追加进决策台账。
- [ ] 签字之后才生成 `results/Qx/reports/frozen_numbers.json`；每条 `{claim_id, value, unit, source_file, source_locator, frozen_at, decision_id}`，且 `source_file` 必须真实存在。
- [ ] 运行数字一致性检查：`check_frozen_numbers.py` 对结果包/论文草稿与冻结值做机械比对。

### 1.4 图表与小问论文（G5）

- [ ] `methods/Qx/qx_figure_table_plan.md`：Type 3/4 论文图必须有矢量（PDF/SVG）+ 300dpi 以上 PNG，落到 `paper/figures/Qx/`；Type 1 诊断图不得进论文。
- [ ] 人工 `claim_scope` 决策入台账。
- [ ] `paper/sections/Qx/qx_model_and_results.md` 与 `paper/sections/Qx/qx_section_manifest.json`。

## 2. 全局材料（所有问题达 G5 后）

### 2.1 全局共享件

- [ ] `planning/symbol_table.md`（全局符号与单位，全文一致）。
- [ ] `planning/model_assumptions.md`（假设及人工必要性标注）。
- [ ] `reference-manager` 产出的参考文献齐备且可核验。

### 2.2 整篇组装（G5.5）

- [ ] `paper/master/cross_question_matrix.md`（每问目标、输入、上下游依赖、主张、图表）。
- [ ] `paper/master/assembly_manifest.json`：`paper_scope=full_submission`，`question_mapping` 的 `target_section` 唯一且覆盖全部活动问题。
- [ ] `paper/master/claim_map.json`、`paper/master/renumber_map.json`（主张、图表、公式、参考文献编号可追溯）。
- [ ] `paper/master/full_paper.md`：先写正文，摘要与结论最后写，且只能包含正文已有的主张。
- [ ] 运行 `full-paper-assembler/scripts/validate_full_paper.py`：全局章节唯一、每问出现一次、章节不在 6.x 内重启。

### 2.3 润色与成稿（G5.6）

- [ ] `paper-polisher` 全文模式润色，保留 assembly manifest 与冻结证据不变，过度主张降级而非静默删除。
- [ ] `national-modeling-paper-formatter` 产出 `paper/final/final_paper.docx`、`final_paper.pdf`、`rendered_pages/`，并逐页做视觉检查（截断、重叠、乱码、空图、占位符）。

### 2.4 三审与授权（G6）

- [ ] `paper/audits/cross_media_consistency_audit.md`（跨介质一致性，先跑 `check_frozen_numbers.py` 机械检查）。
- [ ] `paper/audits/completeness_audit.md`（按 submission 清单核对语义齐备性）。
- [ ] `paper/audits/qa_report.md`。
- [ ] 三份审计结论均为 `PASSED`（不得是 `FAILED`/`NOT_RUN`），最后追加人工 `submission_authorization` 决策。

## 3. 升级后自检命令

```powershell
# 门控：每问应到 G5，全局 G5.5/G5.6/G6 逐级转 PASS
python plugins/math-modeling-workflow/scripts/gate_check.py <项目目录> status
# 总装动作硬门禁：所有活动问题达 G5 才放行
python plugins/math-modeling-workflow/scripts/gate_check.py <项目目录> guard --action final_assembly
# 论文数字与冻结证据机械对账
python plugins/math-modeling-workflow/scripts/check_frozen_numbers.py paper/master/full_paper.md --source results
```

## 4. 反向说明：什么情况下留在 lean

- 只是在比较候选方法、验证可行性、淘汰思路时，保持 lean：不要提前写最终报告或冻结数字。
- lean 的实验轮次、被否决方法、决策台账都应保留；一旦决定参赛，再按本清单升级，证据链不需要重建。
