# 数学建模竞赛工作流全局系统指令 (Mathematical Modeling Workflow Policy)

本工作区为**全国大学生数学建模竞赛全自动（Auto-Pilot）实战工作区**。
任何接入本工作区的 AI 智能体（无论会话切换、模型切换或新任务开启），均必须强制遵循本文件及 `.agents/rules/` 下的所有工作流规约。

---

## 一、工作流技能与入口索引

本仓库已内置完整的端到端建模技能库（位于 `plugins/math-modeling-workflow/skills/`），由以下核心流程驱动：
1. **总编排与门禁调度**：`workflow-orchestrator`（门禁检查由 `plugins/math-modeling-workflow/scripts/gate_check.py` 执行）
2. **题目解析与数据清洗**：`problem-parser`, `problem-classifier`, `data-auditor-cleaner`
3. **模型选型与代码生成**：`method-selector`, `python-model-code-generator`, `matlab-model-code-generator`, `code-reviewer`
4. **统一科研绘图**：`math-figure-generator`
5. **论文写作与总装**：`paper-section-writer`, `full-paper-assembler`, `national-modeling-paper-formatter`
6. **图表自动重排脚本**：`plugins/math-modeling-workflow/scripts/renumber_figures_tables.py`

---

## 二、八大核心执行铁律 (Invariants)

1. **AI 全自动无人值守（Auto-Pilot 模式）**：
   - 默认采取端到端自主推进，中间过程无需等待人类交互；
   - 方法选型（G2.5）与结果冻结（G4）由 AI 自主评判并签署（`decided_by: "autonomous_agent"`），门禁系统一路绿灯通过 G1 至 G5.6；
   - 人类仅在最终生成主论文后进行通读审核。

2. **奥卡姆剃刀：简单模型优先（Simplicity First）**：
   - 详见规则：`.agents/rules/model-selection-principles.md`
   - 允许并提倡联网检索背景常数与专业机理；
   - 复杂模型与简单模型都能解决时，坚决选用可解释性高、数值稳定的简单模型。

3. **代码变量与文件命名简明规范**：
   - 详见规则：`.agents/rules/code-variable-naming.md`
   - 变量与文件命名严禁冗长生僻英文；
   - 化学元素/物质强制采用化学式（如 `Pb`, `SiO2`）；
   - 英语四级以内核心词允许英文（如 `data`, `rate`, `main.py`）；
   - 所使用的数学模型/动力学模型/机器学习算法统一使用公认标准英文命名（如 `logistic`, `arrhenius`, `random_forest`, `rsm`, `ridge`, `bayes`，禁止生硬转拼音）；
   - 题目特有业务领域专有名词强制使用全拼拼音（如 `fenghua`, `wenshi`, `qianbei`）。

4. **参考文献 100% 真实且权威**：
   - 详见规则：`.agents/rules/reference-citation-rules.md`
   - 零伪造、零杜撰；优先引用经典权威教材（姜启源、司守奎、李航、周志华等）、奠基性经典算法论文、国家标准（GB/T）；
   - 严格遵循 GB/T 7714-2015 格式，与正文方括号引用严格 1-to-1 匹配。

5. **统一科研绘图配色方案**：
   - 详见规则：`.agents/rules/scientific-chart-color-scheme.md`
   - 统一采用科研级配色标准（极高值 `#6A0624`、高值 `#B80824`、偏高值 `#D71C2C`、中高值 `#FEAB88`、中等值 `#FDD2BC`、中性偏低 `#C7E0ED`、偏低值 `#6FAFD2`、低值 `#327DB7`、较低值 `#134B87`、极低值 `#053061`）；
   - 热力图统一使用红蓝发散色，折线/柱状图使用标准 6 色板，基线使用中性灰虚线。

6. **国赛标准模板十二大板块与 Word/LaTeX 双轨排版**：
   - 详见规则：`.agents/rules/national-contest-paper-structure.md`
   - 必须包含五段式摘要、禁止抄原题的问题重述、三线表符号说明、独立数据预处理、深入三步法图文论述、官方AI使用声明、附录A支撑材料文件列表。
   - **强制执行 Word 与 LaTeX 双轨渲染与符号纯净化**：
     1. **Word 轨**（`final_paper.docx`）：强制清洗剔除任何原始 `$` LaTeX 代码残留，所有数学符号（如 $\chi^2$、$\pm$、$\le$）与化学式角标（如 $\text{SiO}_2$、$\text{K}_2\text{O}$）必须规范转为 Unicode 与上下标格式，杜绝纯文本占位符与乱码；
     2. **LaTeX 轨**（`paper/latex/paper.tex` ➔ `final_paper_latex.pdf`）：基于 XeLaTeX + ctexart 原生编译完整学术级 PDF，公式、`booktabs` 三线表、矢量图与交叉引用达到顶级学术期刊出版标准；三线表强制引入 `tabularx` 宏包，长文本说明列统一设为自适应 `X` 列或使用 `\resizebox{\textwidth}{!}{...}` 弹性缩放，严防表格右侧冲出版心；
     3. 参赛队可根据赛委会当届规定自由选择提交高质量 Word 论文或 LaTeX 编译的超清 PDF 论文。

7. **先文献调研后建模与 Google 学术临时知识区机制 (Literature-First Modeling)**：
   - 详见规则：`.agents/rules/literature-research-protocol.md`
   - AI 解析赛题后，必须在方法选型前主动基于 Google 学术（Google Scholar）检索赛题领域相关论文及权威机理方程；
   - 筛选提炼核心数学模型、动力学方程与经验参数，规范归档至临时知识区 `workspace/literature/`（生成检索日志 `scholar_search_records.json`、候选模型库 `candidate_models.json` 及调研综述 `literature_summary.md`）；
   - 后续方法选型必须消费该知识区，参考文献 100% 绑定真实检索文献，杜绝空对空建模与虚假引用。

8. **严谨统计推断、数据实核与机理一致性铁律 (Data-First & Rigorous Statistical Modeling)**：
   - 详见规则：`.agents/rules/rigorous-statistical-modeling-protocol.md`
   - **数据实核优先**：严禁脱离实际数据盲目套用文献理论（如武断宣称“火山型”），下达任何趋势结论前必须强制运行代码核验各水平真实样本量 $n$、均值与分布；
   - **混杂控制与非平衡检验**：非平衡观测数据方差分析强制采用 Type-III 边际平方和，严防因变量顺序导致的检验漂移；必须通过多元控制变量回归剖析辛普森悖论（Simpson's Paradox）；
   - **严守统计术语红线**：观测性数据一律使用“统计关联/影响机制”，严禁出现“因果识别/因果推断”等夸大表述；随机森林准确界定为 Gini 纯度增益占比（MDI），严禁与方差贡献率混为一谈；
   - **多响应变量归属分明**：存在多个因变量时，交互项显著性与物理机理必须分别独立归属陈述，严禁笼统概括；
   - **跨问题机理参数全篇贯通**：前序子问题解出的本征机理参数（如动力学参数 $T_{50}$、活化能差 $\Delta E$）必须作为后续统计分析的响应变量，实现微观到宏观的逻辑闭环。

---

## 三、用户启动响应机制

当用户输入包含**“我已经将赛题放入 problem_statement/，数据附件放入 data_raw/。请启动 Auto-Pilot 模式……”**时：
1. 立即确认 `problem_statement/` 与 `data_raw/` 中的赛题和附件文件；
2. 自动启动 Auto-Pilot 管道：从 G1（题目解析与清洗）自动推进至 G5.6（国赛格式化输出）；
3. 产出最终交付成果包：
   - **Word 提交版**：`paper/final/final_paper.docx`（已完成化学分子式角标化与符号美化，零原始代码残留）
   - **LaTeX 编译超清 PDF**：`paper/final/final_paper_latex.pdf`（或 `<赛题名称>_LaTeX论文.pdf`）
   - **LaTeX 完整工程源码**：`paper/latex/paper.tex` 与插图库 `paper/latex/figures/`
   并通知参赛队员进行最终通读审核。

