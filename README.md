# Math Modeling Workflow

一套可安装到 Codex 的数学建模竞赛工作流插件。它以 `workflow-orchestrator` 为统一入口，按门控状态调用题目解析、数据审查、方法选择、代码生成与复核、稳健性分析、正式图表、论文写作、全文装配和最终审计 Skills。

本仓库只包含通用规则、Skills、初始化模板和合成示例，不包含任何真实比赛题目、队伍信息、私有数据或最终论文。

## 主要能力

- `lean` 与 `submission` 两种严谨度配置；
- 每个子问题一份机器可读 manifest；
- 人工方法选择、结果边界和冻结决定可追溯；
- Python 与 MATLAB/北太天元双路线；
- 正式热力图、敏感性图、分布图、预测图和结构图规划与渲染检查；
- 冻结数字驱动的论文写作；
- 多问题全文装配、国赛排版、逐页检查和三层终审。

## 安装

克隆仓库：

```powershell
git clone https://github.com/xujunjie-coder/math-modeling-workflow.git
```

把克隆后的仓库注册为本地 Marketplace：

```powershell
codex plugin marketplace add C:\path\to\math-modeling-workflow
codex plugin add math-modeling-workflow@personal
```

安装或更新插件后，请在 Codex 中开启一个新任务，使新的 Skills 被完整加载。

## 最短使用方式

在一个新的比赛项目目录中输入：

```text
请使用 $workflow-orchestrator 初始化当前数学建模项目。
严谨度先使用 lean，代码语言使用 Python，随机种子使用 2026。
```

之后通常只需要输入：

```text
请使用 $workflow-orchestrator 检查全部活动问题的门控状态，并执行下一项允许的工作。
```

编排器一次只路由一个主要动作，不会在人工判断尚未完成时擅自生成下游结论。

## 初始化目录

也可以直接运行插件附带的初始化工具：

```powershell
python plugins/math-modeling-workflow/scripts/init_workspace.py <项目目录>
```

它只会创建通用目录与初始配置，不会覆盖已有文件。

## Skill 调用链

```text
workflow-orchestrator
  → problem-parser → problem-classifier → data-auditor-cleaner
  → symbol-table-builder → model-assumptions-builder
  → related-paper-analyzer（可选）→ method-selector
  → decision-prompt-builder → modeler-decision-logger
  → model-code-analyzer
  → python/matlab-model-code-generator
  → code-reviewer → python/matlab-code-reviewer
  → result-report-generator → robustness-checker
  → final-method-explainer → figure-table-planner
  → math-figure-generator → solution-package-builder
  → paper-section-writer
  → full-paper-assembler → paper-polisher
  → national-modeling-paper-formatter
  → consistency-auditor → completeness-auditor
  → quality-assurance-auditor
```

完整门控和路由说明见 [工作流文档](plugins/math-modeling-workflow/assets/workflow/competition-workflow.zh-CN.md) 与 [Skill 路由表](docs/skill-routing.md)。

## 图表原则

- 精确的少量数值优先用三线表；
- 分布、趋势、不确定性、多对象比较优先用统计图；
- 相关矩阵、混淆矩阵、缺失矩阵和双参数敏感性优先评估热力图；
- 正式数据图由确定性代码从保存的 CSV/JSON 生成，同时保存 PDF/SVG 和至少 300 dpi PNG；
- ImageGen 等生成式图片工具只用于不承载数值证据的概念插图。

## 排版模板说明

仓库不再分发个人保留或许可状态不明确的 DOCX 模板。`national-modeling-paper-formatter` 会优先使用用户自行提供、且有权使用的当届官方模板；没有模板时使用公开记录的 A4、字体、标题、三线表、图题和公式规则生成文档。

## 开发与验证

```powershell
python plugins/math-modeling-workflow/scripts/validate_repo.py .
python -m unittest discover -s tests -v
```

## 许可证

代码、Skills 和原创文档采用 [Apache License 2.0](LICENSE)。比赛题目、数据、论文、官方模板和第三方材料不因本许可证自动获得再分发授权。
