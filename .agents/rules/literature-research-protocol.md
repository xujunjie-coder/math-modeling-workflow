# Google 学术文献调研与临时知识区构建规约 (Literature Research & Knowledge Base Protocol)

本文件规定了在数学建模工作流中，AI 解析赛题后进行学术文献调研、Google 学术（Google Scholar）检索与构建临时知识区的标准流程。

---

## 一、核心原则 (Core Invariants)

1. **先文献调研，后数学建模 (Literature-First Modeling)**：
   - 严禁在完全脱离学科机理与学术前沿的情况下闭门造车或凭空捏造模型；
   - 题目解析（G1）完成之后、方法选型（G2）与代码生成（G3）之前，AI 必须围绕赛题的核心研究对象、物理/化学反应机理、经济学规律或统计分布特性，主动进行文献检索与机理沉淀。

2. **Google 学术（Google Scholar）优先**：
   - 检索源以 Google 学术、知网、万方、IEEE Xplore、ScienceDirect、arXiv 等主流权威学术数据库为主；
   - 提取真实、权威学者发表的经典数学模型、反应机理方程、控制变量经验范围及验证方法。

3. **文献 100% 真实可追溯**：
   - 检索到的文献元数据（篇名、作者、发表刊物、年份、DOI/URL）必须真实存在，绝对严禁杜撰；
   - 提取的高价值文献直接沉淀为后续论文写作（G5）中参考文献的标准源头。

4. **全真模拟国赛纪律：严禁检索或参考历届竞赛论文与网络题解 (Anti-Contest-Paper Rule)**：
   - 本工作区处于全国大学生数学建模竞赛**全真模拟实战状态**；
   - 文献调研对象**必须 100% 限定在正规学术期刊（如 ACS Catalysis, ChemSusChem 等）、权威学科教科书（如 Fogler, Montgomery, Levenspiel 等）与奠基性算法专著（如 Breiman, Box & Draper 等）**；
   - **绝对严禁检索、阅读、借鉴或引用任何历届数模竞赛获奖论文、网络论坛代解或博客答案**；
   - 必须从化学反应工程、试验设计（DoE）与统计学习的**第一性原理**出发独立分析与建模，确保竞赛成果的原创性、合规性与权威性。

---

## 二、临时知识区目录与数据契约

临时知识区统一建立在工作区目录：`workspace/literature/`。
AI 完成文献检索与模型提取后，必须在该目录下输出以下规范文件：

### 1. 学术检索记录表：`workspace/literature/scholar_search_records.json`
记录检索关键词、检索逻辑与真实文献元数据，例如：
```json
{
  "search_timestamp": "2026-09-04T19:45:00Z",
  "search_queries": [
    "ethanol coupling C4 olefins mechanism kinetics model",
    "乙醇偶合制备 C4 烯烃 反应动力学 催化剂失活"
  ],
  "retrieved_papers": [
    {
      "id": "ref_1",
      "title": "Kinetics and Mechanism of Ethanol Coupling to Higher Alcohols and Olefins",
      "authors": ["Smith, J.", "Zhang, W."],
      "venue": "Journal of Catalysis",
      "year": 2019,
      "doi": "10.1016/j.jcat.2019.01.012",
      "relevance": "提供了一级失活阿伦尼乌斯动力学方程及活化能参考范围"
    }
  ]
}
```

### 2. 候选数学模型库：`workspace/literature/candidate_models.json`
从高引文献中提炼出的可供建模借鉴的成熟方程、参数范围与假设：
```json
{
  "target_subquestion": "Q1",
  "candidate_models": [
    {
      "model_name": "一级反应动力学失活模型 (First-Order Catalyst Deactivation)",
      "source_paper_id": "ref_1",
      "core_equation": "da/dt = -kd * a,  k_d = A * exp(-Ea / (R * T))",
      "input_variables": ["时间 t", "绝对温度 T"],
      "output_variables": ["催化剂活性因子 a", "失活速率常数 kd"],
      "prior_parameter_ranges": {
        "Ea": "40 ~ 90 kJ/mol",
        "half_life": "10 ~ 50 hours"
      },
      "applicability": "适用于 350℃ 等温固定床催化反应的时变规律拟合",
      "advantages": "物理机理清晰、参数量少、数值拟合极其稳定（契合奥卡姆剃刀）"
    }
  ]
}
```

### 3. 文献调研综合综述：`workspace/literature/literature_summary.md`
提供人类与评审专家阅读的 Markdown 综述报告，内容涵盖：
- 研究背景与前人研究进展；
- 赛题各子问题在学术文献中的典型数学处理思路；
- 推荐的模型选型倾向及机理支撑理由。

---

## 三、下游消费与贯通机制

1. **驱动方法选型 (`method-selector`)**：
   - 选型器必须读取 `workspace/literature/candidate_models.json`；
   - 在 `method_card.md` 的论证中必须阐述文献机理模型的借鉴依据，将先验模型与当前实际数据进行结合；
   - 遵循“奥卡姆剃刀”：在文献提供的复杂偏微分方程与简明动力学方程之间，优先选取参数收敛性好、可解释性强的模型。

2. **驱动参考文献生成 (`reference-manager`)**：
   - 论文附录或正文后的参考文献列表，直接以 `scholar_search_records.json` 为底册，自动格式化为 GB/T 7714-2015 格式；
   - 确保正文中引用的公式（如“基于文献[1]的一级失活机理……”）与文末参考文献 $100\%$ 一对一精准锚定。
