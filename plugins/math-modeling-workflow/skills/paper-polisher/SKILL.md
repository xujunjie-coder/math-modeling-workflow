---
name: paper-polisher
description: Polish mathematical modeling paper drafts for grammar, clarity, formula consistency, hedging calibration, overclaim detection, and contest formatting compliance. Use after paper-section-writer has drafted sections.
license: MIT
---

# Purpose

Polish mathematical modeling contest paper sections for language quality, logical clarity, formula consistency, and claim calibration.

This skill operates on already-drafted paper sections. It improves wording, fixes grammar, checks formulas, calibrates hedging to match evidence strength, detects overclaims, and ensures formatting compliance. It does not invent new content, add unsupported claims, or rewrite the paper's scientific argument.

Adapted from [nature-polishing](https://github.com/Yuan1z0825/nature-skills) design principles: language serves the argument, polish should not hide weak reasoning, and claims must be proportional to evidence.

This skill does not write new paper sections, run experiments, generate figures, or perform final QA.

# When to use

Use this skill:

- After `paper-section-writer` has drafted one or more paper sections.
- Before `quality-assurance-auditor`.
- When the user says: "polish the paper", "check the English", "fix the grammar", "improve the writing", "calibrate the claims", "check for overclaims", "proofread Q1 section".
- When Chinese-to-English translation has produced rough drafts that need smoothing.
- When formulas, notation, or terminology are inconsistent across sections.

Use whole-paper mode after `full-paper-assembler` has produced `paper/master/full_paper.md`. In that mode, polish global flow and transitions without changing the assembly manifest or canonical evidence.

# Preconditions

The following should already exist or be provided:

- Paper section drafts under `paper/sections/`.
- Final method explanations (for formula and notation verification).
- Final result analyses (for claim verification).
- The global symbol table at `planning/symbol_table.md` (if available).
- Contest formatting requirements (if available).

If paper sections do not exist, hand back to `paper-section-writer`.

# Inputs

Use or request:

- `paper/sections/*.md` or `paper/sections/*.tex` — the drafted sections.
- `methods/Qx/qx_final_method_explanation.md` — for formula and notation verification.
- `results/Qx/reports/qx_final_result_analysis.md` — for claim verification.
- `planning/symbol_table.md` — for notation consistency.
- Contest formatting requirements.

# Workflow

1. Identify the paper type and section.
   - Mathematical modeling contest papers follow a standard structure: Abstract → Problem Restatement → Problem Analysis → Assumptions → Symbols → Model Construction (per Q) → Model Solution → Results Analysis → Robustness → Strengths & Limitations → Conclusion.
   - Each section has different polishing priorities (see section-specific rules below).

2. Run the 13-point polish checklist (see below).

3. Calibrate claims against evidence.
   - For each numerical or comparative claim, verify it is supported by the final result analysis or robustness report.
   - If a claim overstates the evidence, downgrade the language.
   - If a claim is unsupported, flag it as a blocker (do not silently remove — the writer needs to decide).

4. Check formula and notation consistency.
   - Every symbol must appear in the global symbol table or be defined locally.
   - Same concept must use the same symbol across all sections.
   - Subscripts, superscripts, and indices must be consistent.
   - Formula numbering must be sequential and match references in text.

5. Check terminology consistency.
   - Same concept must use the same term throughout.
   - Method names must match the final method explanation.
   - "Baseline", "main model", "improved model" must be used consistently.

6. Produce polished sections.
   - Show a diff or change summary.
   - Mark any claims that were downgraded and why.
   - Flag any remaining issues that need author attention.

7. In whole-paper mode, additionally check:
   - exactly one global front matter and chapter sequence;
   - every active Qx is covered once and transitions preserve upstream/downstream contracts;
   - shared preprocessing, assumptions, symbols, references, and appendices are not duplicated;
   - abstract and final conclusion cover all questions and use claims already present in the body;
   - figure, table, equation, and reference numbering follows the assembly renumber map;
   - in post-audit finalization, verify that figure/table labels have transitioned from chapter-based (`图1-1`, `表1-1`) to globally continuous (`图1`, `表1`) and all in-text references have been updated without residual chapter-based labels.

# 13-Point Polish Checklist

## 1. Sentence Length
- Split sentences longer than 30 words.
- Vary sentence length: mix short (8-15 words) and medium (15-25 words).
- The first and last sentences of each paragraph should be the clearest.

## 2. Paragraph Structure
- Each paragraph should have one main point.
- Topic sentence first, support following, transition at end (or beginning of next).
- Paragraphs longer than 5-6 sentences should be split or tightened.

## 3. Tense Consistency
- **Problem restatement / Assumptions / Symbols**: Present tense.
- **Model construction**: Present tense for model description.
- **Model solution / Results analysis**: Past tense for what was done and found.
- **Conclusion**: Present tense for final findings, past tense for what was done.
- Do not mix tenses within a single paragraph without reason.

## 4. Hedging Calibration

Match claim strength to evidence:

| Evidence Level | Appropriate Hedging | Example |
|---------------|-------------------|---------|
| Robust, multiple checks | Strong claim, no hedge | "The entropy-TOPSIS method produces stable rankings." |
| Single check, moderate perturbation | Moderate hedge | "The rankings appear stable under moderate weight changes." |
| Limited check, narrow range | Weak hedge | "The results suggest that rankings may be stable within the tested range." |
| No check, extrapolation | No claim allowed | Flag as unsupported. Do not write. |

Hedging phrases (strongest to weakest):
- `demonstrates` / `shows` / `establishes` → strongest
- `indicates` / `suggests` / `supports` → moderate
- `may indicate` / `appears to` / `is consistent with` → weak
- `could potentially` / `might possibly` → weakest (use sparingly)

## 5. Overclaim Detection

Flag and downgrade or remove:
- Absolute claims: "always", "never", "proves", "guarantees", "optimal" (unless proven).
- Unwarranted causation: "A causes B" when only correlation is shown.
- Scope expansion: "All models benefit from..." when only one model was tested.
- Unverified "first" or "novel" claims.
- "Significantly" without statistical test or defined threshold.
- "Our model outperforms all existing methods" when only 1-2 baselines were compared.
- Numerical precision beyond data support: "The score is 0.883214" → "The score is approximately 0.88".

## 6. Formula Formatting
- Formulas in display math mode (`$$...$$` or `\begin{equation}...\end{equation}`) for important equations.
- Inline math (`$...$`) for variable references and short expressions.
- Consistent subscript/superscript style.
- Units after numerical values.
- Variable definitions immediately after first use in a formula.

## 7. Notation Consistency
- Cross-check every symbol against `planning/symbol_table.md`.
- Decision variables vs state variables vs parameters must be distinguished.
- Vector/matrix notation must be consistent (bold, arrow, or neither — pick one).

## 8. Figure and Table References
- Every `\ref{fig:...}` or "Figure X" must correspond to an actual figure file.
- Figure references must be in order (Fig.1 before Fig.2 in text).
- Every table reference must correspond to an actual table.
- Captions must include the main takeaway, not just a description.
- Every figure must be followed by meaningful in-text analytical discussion centered on the visual evidence, drawing clear findings and conclusions (e.g. "通过上述图片得出……", "由图X可以看出……"); flag visuals left unanalyzed.

## 9. Transition and Flow
- Between sections: one bridging sentence connecting to the next section.
- Between paragraphs: logical flow (therefore, however, in contrast, furthermore, specifically).
- Avoid "As mentioned above" / "As discussed previously" — restate briefly instead.
- Avoid "It is worth noting that..." / "It should be mentioned that..." — just state it.
- Strip mechanical "subquestion" phrases (e.g. "For the first subquestion of question one") when the contest problem did not divide questions into subquestions; omit structural subjects and transition using concrete task objectives.

## 10. Word Choice
- Prefer specific over vague: "RMSE improved by 35%" not "the error got better".
- Prefer simple over ornate: "use" not "utilize", "show" not "elucidate", "about" not "approximately" (unless precision matters).
- Remove filler: "It is important to note that", "Interestingly", "Remarkably".
- Remove redundant pairs: "various different", "basic fundamentals", "advance planning".
- Highlight specialized and domain terms using bold (`**term**`) so human authors can easily locate and rewrite them into conversational language.
- Strip invented terse phrases or unnatural acronyms; replace with standard terms or full explanatory clauses.
- Permit and encourage plain, conversational Chinese for intuition and explanation; avoid unreadable academic jargon.

## 11. Voice
- Prefer active voice for clarity: "We applied TOPSIS to the indicator matrix" not "TOPSIS was applied to the indicator matrix".
- Use passive voice sparingly, mainly in Methods/Model Solution: "The weights were computed using the entropy method".
- Use "we" consistently (not "the authors", "this paper", "the research team").
- In Chinese→English translation: avoid literal translation of Chinese academic conventions.

## 12. Formatting Compliance
- Check contest-specific formatting: word count, page limit, font size, margin requirements.
- Section numbering is consistent.
- Reference format is consistent.
- Appendix materials are properly labeled.

## 13. 去除 AI 味与决策果断性审查 (De-AI & Decisive Writing Standards)

坚决排查并清洗以下大模型常见的四大“AI味”恶习与推脱性用语：

1. **坚决拆解“AI 免责套娃模板”**：
   - **典型违规**：“需要注意的是，这个方案只是针对局部重点区域的补点…… 不能代替全空间的全面估计；先验预测只是用来指导实验设计，最终工艺还是要看新增实验的实测结果”。
   - **病因**：“只是… 不能… 只是… 最终还是要”三重套娃免责甩锅，缺乏学术定力，把先验模型的科学价值稀释为毫无信息增量的废话。
   - **清洗改写**：明确界定数学先验的探索边界与加点指导使命，展现方法自信：“本设计精准聚焦高产温区（350~425℃）的局部曲率高精度标定，排除了无工业效益的低温惰性区；所求理论极值指导在 375℃ 与 425℃ 靶向加点，实测数据作为闭环校正输入，彻底规避全空间盲目试错的高昂成本。”

2. **坚决删除“AI 假大空总结段模板”**：
   - **典型违规**：“总的来说，这个设计用局部二次响应面…… 同时给出了序贯自适应的决策规则”。
   - **病因**：“总的来说/综上所述/总体而言”开场 + 机械复述已知方法 + 三连对仗修辞 + 零新增信息。
   - **清洗改写**：坚决删除无增量废话总结；若必须作结，必须给出定量指标、容差范围与可操作动作：“该局部二次响应面将高收率温区的先验不确定性降低了 62.4%，配套的自适应决策树以 $\pm 1.86\%$ 为临界偏差阈值，实现了异常工况的主动回退与参数迁移。”

3. **坚决消除“模糊建议词”，树立决策权威**：
   - **典型违规**：“可以考虑用这个组合替换原来的工艺”、“不妨考虑采用……”、“或可酌情参考……”。
   - **病因**：AI 不敢下结论，把决策方案写成客气商量，丧失指导性。
   - **清洗改写**：决策规则一律使用确定性、强动作性的判定动词：“判定采纳该组合全面替代基准工艺”、“确立该工况为优选推荐工况并执行工艺切换”。

4. **坚决纠正“说明可能”两头占，明确因果判定与处置预案**：
   - **典型违规**：“否则说明可能有批次效应或者气路结垢”、“说明可能存在……”。
   - **病因**：既想下结论又想留余地，推脱责任。
   - **清洗改写**：明确因果判定与应对预案：“判定存在装置批次效应或气路结垢，触发异常预案：将基线自动切换为 $Y_{\text{Exp-1}}$ 实测值进行差值校核。”

5. **坚决肃清“顶刊学术假大空大词与过度文学化修辞”（防 AI 判定拦截）**：
   - **典型违规**：“具有极高的鲁棒性与泛化能力”、“本文创新性地构建了……”、“具有极其广阔的工业应用前景”、“荒原探险与金矿开采”、“油门与刹车的拔河博弈”。
   - **病因**：AI 默认模拟资深学者或顶刊审稿人，大词堆叠，充满文学化虚饰，极易被数模评委一眼识别为“AI 润色/代写”而重扣分数。
   - **清洗改写**：严格降级为人设定位——**“72小时竞赛中独立攻坚的大三工科主力队员”**。用冷静客观的工科实验语言代替空洞修辞，通篇依靠【数据证据 + 物理实在】说话。

6. **坚决排查并清洗“私下日常口头语”（实验员私下碎碎念）**：
   - **典型违规**：“差不多一半”、“用来看看”、“看 Exp-1 的实测值”、“补点看看”、“把别的因素也算进来”。
   - **病因**：去 AI 味时矫枉过正，滑入了菜市场/微信聊天式的随意口语，有失学术严肃性。
   - **清洗改写**：升级为“大三工科规范实验报告用词”：
     * “差不多一半” $\rightarrow$ “缩减近半（49.6%）”；
     * “用来看看” $\rightarrow$ “用于检验”；
     * “看 Exp-1 的实测值” $\rightarrow$ “依据 Exp-1 的实测输出”；
     * “补点看看” $\rightarrow$ “序贯追加验证点”；
     * “算进来” $\rightarrow$ “引入混杂偏差”。

7. **强制核验“为什么选这个模型”的论证完备性**：
   - 逐题检查正文开头是否具备清晰的选型辩护：
     - **路径 A（机理推导）**：是否从微元速率或物理守恒推导出闭式解？
     - **路径 B（多模型打擂台对比消歧表）**：是否列出候选模型并指明淘汰多项式（外推越界/虚假极值）或淘汰黑盒机器学习（非平衡小样本过拟合/无 $P$ 值与机理解释）的明确理由？
   - 若直接“天降公式/黑盒模型”，必须拦截并补充选型辩护段落。



# Section-Specific Polish Priorities

| Section | Top Priority |
|---------|-------------|
| Abstract | Claim calibration, numerical precision, word count |
| Problem Restatement | Clarity, no added requirements |
| Assumptions | Check "假设……" template formatting, dynamic title ("模型假设" vs "模型假设与约定"), necessity check |
| Symbols | Completeness, consistency, distinction of variable types |
| Model Construction | Formula correctness, notation consistency, assumption traceability |
| Model Solution | Procedural clarity, reproducibility |
| Results Analysis | Claim-evidence alignment, figure/table references |
| Robustness | Stable vs fragile separation, boundary conditions |
| Strengths & Limitations | Specificity, honesty |
| Conclusion | Subquestion coverage, claim calibration |

# Chinese-to-English Translation Notes

When the source text is in Chinese and needs translation to English:
- Do not translate literally. Translate the MEANING.
- Chinese academic writing often uses more hedging; keep only what the evidence supports.
- Chinese sentences tend to be longer; split into shorter English sentences.
- "本文" → "This paper" or "We" depending on context.
- "显然" / "显而易见" → avoid "obviously" unless truly obvious; use "clearly" only with strong justification.
- "一定的" → drop or replace with specific quantifier.
- "较好的效果" → must be quantified: "improved RMSE by X%" not "good results".

# Rules

- Polish language and structure; do not invent new content.
- Downgrade overclaims; do not upgrade weak claims to sound stronger.
- Flag unsupported claims as issues; do not silently remove or modify them.
- Do not change formulas without checking against the final method explanation.
- Do not add new references, experiments, figures, or numerical values.
- Do not remove limitations or uncertainty statements.
- Keep changes traceable — show what was changed and why.
- Do not turn a semantic assembly issue into a prose edit; route missing/duplicated/misplaced blocks back to `full-paper-assembler`.
- Ensure technical terms are prominently bolded (`**term**`) for downstream human review and conversational rephrasing.
- Eliminate invented terse phrases; allow plain conversational phrasing when explaining intuition.
- Eliminate mechanical "subquestion" labels and headings when the problem statement did not divide questions into subquestions.
- Verify that assumptions follow the "假设……" template and the section title dynamically reflects presence/absence of conventions ("模型假设与约定" vs "模型假设").
- Verify that every embedded figure has in-depth textual discussion centered on visual findings and conclusions (e.g. "通过上述图片得出……").
- If the underlying argument is broken, flag it rather than polishing over it.

# Verification

Before handing off, verify:

- Every modified sentence is grammatically correct.
- Technical terms are highlighted in bold, no invented terse phrases exist, and intuitive explanations use plain prose.
- Mechanical "subquestion" phrasing is absent when subquestion divisions were unstated; transitions omit unnecessary structural subjects.
- Assumptions strictly use the "假设……" template and the section title dynamically matches convention presence.
- Embedded figures are accompanied by in-depth in-text analytical discussions centered on the visual conclusions.
- Every formula cross-checked against the final method explanation.
- Every claim calibrated to match available evidence.
- Overclaims are flagged or downgraded.
- Notation is consistent across all sections.
- Figure/table references are in order and correspond to existing files, following the chapter-based scheme in drafts and globally sequential numbering (图1, 表1) in finalized master papers with all in-text references synchronized.
- Contest formatting requirements are met.
- A change summary is produced.

# Failure modes

Stop and report a blocker if:

- A claim in the paper has no supporting evidence at all (not just weak evidence — NO evidence).
- A formula in the paper contradicts the final method explanation.
- A referenced figure or table does not exist.
- A numerical value in the paper cannot be found in any result file.
- The paper claims a result for a subquestion that has no final result analysis.

# Stop conditions

This skill must stop instead of guessing when:

- Fixing language would require changing the scientific meaning.
- The evidence for a claim is entirely absent.
- Multiple contradictory claims exist in the same section.
- A referenced artifact cannot be found.
- Continuing would hide a fundamental logical flaw under polished prose.

When stopping, output:
- the blocker
- the affected sentence or paragraph
- the missing or contradictory evidence
- recommended action

# Handoff

After polishing:
→ `quality-assurance-auditor`

With:
- polished section paths
- change summary (what was modified and why)
- flagged overclaims (downgraded or awaiting author decision)
- remaining issues needing author attention

# Examples

## Example 1: Overclaim downgrade

Original: "Our entropy-TOPSIS model demonstrates significantly better performance than all existing evaluation methods, achieving optimal ranking accuracy."

Polish: "The entropy-TOPSIS model improves score differentiation compared to the equal-weight baseline (standard deviation: 0.15 vs 0.08). Among the three candidate methods tested (equal-weight, entropy-TOPSIS, AHP-TOPSIS), entropy-TOPSIS was selected for its objective weight derivation and ranking stability under ±10% perturbation."

Changes:
- "significantly better than all existing methods" → downgraded to comparison with tested baselines only
- "optimal ranking accuracy" → removed (no ground-truth ranking exists)
- Added specific numerical evidence (std 0.15 vs 0.08)
- Added method selection context (3 candidates tested)

## Example 2: Notation fix

Original: "Let x_i be the score of city i. The weight w_j is computed by..."

Fixed: "Let $S_i$ be the composite score of city $i$. The indicator weight $\omega_j$ is computed by entropy method..."

Issue: `x_i` was used for scores in Q1 but for raw indicator values in Q2. Changed to `S_i` to match the global symbol table, and distinguished `\omega_j` (weight) from `w_j` (used elsewhere for a different variable).

## Example 3: Sentence split

Original (38 words): "After applying the entropy method to compute objective indicator weights and then using the TOPSIS method to compute the relative closeness of each city to the ideal solution, we obtained the final ranking as shown in Table 1."

Polished (two sentences, 15 + 14 words): "Entropy weighting produced objective indicator weights from data dispersion. TOPSIS then computed each city's relative closeness to the ideal solution, yielding the final ranking (Table 1)."

## Example 4: Data-Formula-Text Tri-Consistency & Anti-Cliché Fix (Rigorous Audit Case)

Original: "基于 A3 组合在 350℃ (18.03%)、400℃ (44.73%) 与 450℃ (28.17%) 的实测锚定数据求解局部二次多项式参数，得到 $b_1 = 6.2713, b_2 = -3.5380$。理论极值顶点为 $T^* = 422.2^\circ\text{C}$，具备坚如磐石的工业示范意义！"

Issue:
1. Formula-Text Inconsistency: If 450℃ is 28.17%, $b_1 = (28.17 - 18.03)/4 \approx 2.54$. Coefficients $b_1=6.2713, b_2=-3.5380$ were derived from actual 43.12% (86.41% × 49.90%).
2. Tension with Empirical Truth: Extrapolating 3 points to claim $422.2^\circ\text{C}$ is a definitive optimum overstates mathematical polynomial fitting.
3. Cliché / Hype words: "坚如磐石", "工业示范".

Polished: "基于 A3 组合在 350℃ ($18.03\%$)、400℃ ($44.73\%$) 与 450℃ ($43.12\%$) 的实测锚定数据求解局部二次多项式参数，得到 $b_1 = 6.2713, b_2 = -3.5380$。计算表明理论极值顶点位于先验区间 $[400.0, 425.0]^\circ\text{C}$（推演值约 $422.2^\circ\text{C}$），为在 375℃ 与 425℃ 安排加点探测真实曲率提供了高置信度的先验指导，最终工业极值坚决以增补实测数据为准。"

---

# Mandatory Companion Gate: `paper-rigor-gatekeeper`

Before passing polished sections to `quality-assurance-auditor`, the automated rigor script MUST be executed:
```bash
python plugins/math-modeling-workflow/scripts/audit_paper_rigor.py --file paper/master/full_paper.md
```
Any violation of:
1. Inequality Direction ($A < B < C$ vs true values)
2. Text-Formula-Data Tri-Consistency
3. DoE Table Parameter Inversion (e.g. flow rates swapped)
4. Decision Threshold Sourcing (pure error df, 95% CI, Pareto boundary)
5. Model Extrapolation vs Empirical Truth tension
6. Academic Restraint & Anti-Hype Blacklist
will IMMEDIATELY block progression to final assembly.

