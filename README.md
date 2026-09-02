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

它只会创建通用目录与初始配置，不会覆盖已有文件。物理目录与各 Skill 规范路径（canonical）一致；教学文档里的 `problem_1/subproblem_x` 叫法、脚手架目录与 canonical 路径的一一对应见 [docs/directory-mapping.zh-CN.md](docs/directory-mapping.zh-CN.md)。从 lean 探索档升级到 submission 参赛档的补件清单见 [docs/lean-to-submission-checklist.zh-CN.md](docs/lean-to-submission-checklist.zh-CN.md)。

不使用 Codex 时（Claude Code、Cursor 或任意网页对话），Skill 是纯 Markdown、脚本只依赖标准库，可按 [docs/agent-agnostic-loading.zh-CN.md](docs/agent-agnostic-loading.zh-CN.md) 手动加载，由人承担路由、用脚本做硬校验。

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

## 门控硬检查

门控不仅是 Skill 里的规则，还附带标准库实现的强制执行器，用磁盘证据而不是自报清单来判断进度：

```powershell
# 查看每个活动问题实际由证据支撑到哪一道门（exit 2 = 清单超前/越权等完整性违规）
python plugins/math-modeling-workflow/scripts/gate_check.py <项目目录> status

# 动作前硬阻断：未过 G2.5 不允许写模型代码，未过 G3 不允许冻结，以此类推
python plugins/math-modeling-workflow/scripts/gate_check.py <项目目录> guard --action code_generation --question Q1
```

`--action` 支持 `code_generation`（需 G2.5）、`freeze`（需 G3）、`paper_writing`（需 G4）和 `final_assembly`（所有活动问题达 G5）。纯机理/无数据题可在该问题 manifest 中声明 `"waivers": ["data_profile"]`，检查会显式标注豁免而不是静默跳过。

论文数字与冻结证据的机械一致性由另一个标准库脚本负责，它会排除章节/图表/公式编号、年份、代码、链接与公式，只核对结果论断数字：

```powershell
python plugins/math-modeling-workflow/scripts/check_frozen_numbers.py paper/master/full_paper.md `
  --source results --source paper/master/claim_map.json
```

精确匹配（千分位、尾零、科学计数法归一）后仍找不到来源的数字判为 UNFROZEN 并以非零码退出；四舍五入近似值给 NEAR 警告；确属编号或设定值的例外写进 sidecar `.frozenignore`（支持字面量与 `regex:`）。

## 开发与验证

```powershell
python plugins/math-modeling-workflow/scripts/validate_repo.py .
python -m unittest discover -s tests -v
```

## 许可证

代码、Skills 和原创文档采用 [Apache License 2.0](LICENSE)。比赛题目、数据、论文、官方模板和第三方材料不因本许可证自动获得再分发授权。
