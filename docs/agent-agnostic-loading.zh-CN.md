# 在非 Codex 环境中使用本工作流（Claude Code / Cursor / 通用对话）

本插件的能力由两部分组成，二者都不绑定 Codex：

1. **Skill 指令**：每个 `skills/<name>/SKILL.md` 是带 YAML frontmatter 的纯 Markdown，描述输入、流程、输出契约与校验项；
2. **确定性脚本**：`scripts/` 与 `full-paper-assembler/scripts/` 下的 Python 只依赖标准库，本地直接运行。

Codex 提供的只是 `$skill-name` 自动发现与注入。换一个 Agent，等于由**人来承担 orchestrator 的路由职责**：决定当前在哪道门、该把哪个 SKILL.md 交给模型、产物是否落盘到 canonical 路径，再用脚本做硬校验。工作流的门控纪律、人工决策门、冻结数字等约束全部保持不变。

## 1. 目录准备（与 Agent 无关）

```powershell
# 1) 初始化 canonical 目录（零三方依赖）
python plugins/math-modeling-workflow/scripts/init_workspace.py <项目目录>
# 2) 之后随时用门控器查看真实进度
python plugins/math-modeling-workflow/scripts/gate_check.py <项目目录> status
```

canonical 路径含义见 [directory-mapping.zh-CN.md](directory-mapping.zh-CN.md)。无论哪个 Agent，都要求它把产物写到这些路径，否则门控器不认。

## 2. 三种加载模式

### 模式 A：项目规则常驻（推荐，Claude Code / Cursor / Cline 等支持规则文件的工具）

把总控 Skill 作为常驻规则，子 Skill 按需读取。

- **Claude Code**：把 `skills/workflow-orchestrator/SKILL.md` 的正文并入项目根 `CLAUDE.md`（或在 `CLAUDE.md` 里用文件引用指向它）。让模型在每个阶段用 Read 工具按需读取对应 `skills/<name>/SKILL.md`，而不是一次性塞满上下文。
- **Cursor**：在 Project Rules 中新建规则，总控规则设为始终附带（always attach），子 Skill 规则设为按 Agent 请求附带（agent requested），并在规则描述里写明触发场景（例如“生成 Python 建模代码时读取 python-model-code-generator”）。等价的手工方式是在输入框用 `@skills/<name>/SKILL.md` 显式引入。
- **其他支持规则/指令文件的工具**：同理，总控常驻、子 Skill 按阶段引入。

常驻总控时，建议在规则开头加一句给模型的话：

> 你是数学建模工作流的执行器。严格按 G0→G6 门控推进；每次只执行一个已授权动作；人工决策门（G2.5 方法选择、结果裁决、claim scope、package signoff、提交授权）必须等我本人回答，不得替我决定；产物写入 canonical 路径；动作前我会运行 gate_check.py，非零退出时停止。

### 模式 B：手动粘贴（任意网页对话，如 ChatGPT / Gemini / 豆包网页版）

1. 开工时把 `workflow-orchestrator/SKILL.md` 全文贴入，声明 `rigor_profile`、语言、随机种子与活动问题；
2. 每进入一个阶段，打开对应 `skills/<name>/SKILL.md` 贴入，再让它执行（例如分类阶段贴 `problem-classifier`，写代码前贴 `model-code-analyzer` + `python-model-code-generator`）；
3. 让模型把 JSON/Markdown/代码产物以文件内容形式输出，你手动保存到 canonical 路径；
4. 在本地运行 `gate_check.py` 与 `check_frozen_numbers.py`，把输出贴回对话让模型据此修复。

这种模式上下文不连续，更要依赖落盘产物与脚本，而不是模型的“记忆”。

### 模式 C：只借用脚本（已有自己的提示词体系）

即使不用任何 SKILL.md，也可以单独使用四个确定性工具为既有流程兜底：

| 脚本 | 作用 |
|---|---|
| `init_workspace.py` | 建 canonical 目录与初始配置 |
| `gate_check.py status/guard` | 按磁盘证据判门、动作前硬阻断 |
| `check_frozen_numbers.py` | 论文数字与冻结/指标 JSON 机械对账 |
| `full-paper-assembler/scripts/validate_full_paper.py` | 整篇论文结构校验（`--self-test` 自检） |

## 3. 阶段 → 需要加载的 Skill（人来路由）

按 `validate_repo.py` 的显式阶段表推进，顺序与门控严格对应：

| 门 | 阶段 | 按需加载的 Skill |
|---|---|---|
| G0→G1 | 解析/分类/数据 | problem-parser → problem-classifier → data-auditor-cleaner（配合 symbol-table-builder、model-assumptions-builder、related-paper-analyzer、reference-manager） |
| G1→G2.5 | 方法决策 | method-selector → decision-prompt-builder →（人回答选择卡）→ modeler-decision-logger |
| G2.5→G3 | 代码与实验 | model-code-analyzer → python/matlab-model-code-generator → code-reviewer → python/matlab-code-reviewer，结果由 result-report-generator 汇总 |
| G3→G4 | 稳健与裁决 | robustness-checker →（人 result_verdict）→ modeler-decision-logger；lean 到此为止 |
| G4→G5 | 参赛成文 | final-method-explainer、figure-table-planner、math-figure-generator、solution-package-builder（人 package_signoff 后冻结）、paper-section-writer |
| G5.5→G5.6 | 整篇 | full-paper-assembler → paper-polisher → national-modeling-paper-formatter |
| G6 | 终审 | consistency-auditor → completeness-auditor → quality-assurance-auditor（人 submission_authorization） |

## 4. 最小手动闭环（lean，七步）

1. `init_workspace.py` 建目录，填 `planning/session_config.json` 与每问 manifest；
2. 贴 problem-parser / problem-classifier，落盘 parse、classification JSON；
3. 贴 data-auditor-cleaner，落盘 `workspace/data/data_profile.json`；`gate_check.py status` 应到 G1；
4. 贴 method-selector 出风险探针，人回答方法选择卡，modeler-decision-logger 追加决策；
5. `gate_check.py guard --action code_generation --question Q1` 放行后再贴代码生成/评审 Skill；
6. 实验与评审落盘，人给 result_verdict，lean 到 G4；
7. 决定参赛时按 [lean-to-submission-checklist.zh-CN.md](lean-to-submission-checklist.zh-CN.md) 升级。

## 5. 通用环境下不可省略的三条纪律

- **人工决策门不能自动化**：模型可以生成选择卡，但 `decided_by` 必须是 `human`；`gate_check.py` 只认人工决策，AI 自造的 DECIDED 记录不能推进门。
- **数字先冻结后写作**：submission 下先有 `package_signoff` 再有 `frozen_numbers.json`，论文数字用 `check_frozen_numbers.py` 对账，不允许先写数字再倒改结果。
- **以磁盘证据为准**：换任何模型/会话，进度都由 canonical 路径上的文件与脚本判定，不以上一个对话里“它说做完了”为准。

## 6. 平台差异与边界

- 非 Codex 环境没有插件市场与 `$skill` 自动补全，Skill 的选择与引入由人（或规则）完成；SKILL.md 本身是纯 Markdown，可自由复制、纳入版本管理或裁剪，但裁剪后应仍能通过 `validate_repo.py`（若保留仓库结构）与门控脚本。
- 各工具规则文件的确切位置、触发方式与附件语法会随版本变化，以对应工具官方文档为准；本工作流只要求“总控常驻、子 Skill 按需、产物落 canonical 路径、脚本硬校验”这一可移植内核。
- 脚本需要本机 Python 3.10+（开发与 CI 使用 3.12），不安装任何第三方包。
