---
name: scipilot-figure
description: Publication-grade scientific figure generation and Visual QA system. Embeds "Think first, plot second" philosophy, multi-panel composition, journal layout specs, proactive pitfall interception, and unified national-modeling scientific color schemes.
---

# scipilot-figure: 顶刊出版级科研绘图与视觉质检引擎

`scipilot-figure` 是专为数学建模竞赛与顶级学术期刊打造的科研级数据可视化 Skill。它脱离“拿到数据直接画图”的初级模式，严格践行 **“先思考，后绘图（Think first, plot second）”** 的科研哲学，结合全国大学生数学建模竞赛的全局铁律，提供从数据画像、图式决策、多面板排版、红蓝科研配色到视觉质检（Visual QA）的全流程闭环。

---

## 核心工作流：8 步闭环（The 8-Step Scientific Visualization Pipeline）

```
[1. 论点提炼] ➔ [2. 数据画像] ➔ [3. 选图决策] ➔ [4. 版心规范]
      │
      ▼
[5. 环境注入] ➔ [6. 高清渲染] ➔ [7. 视觉质检] ➔ [8. 双轨导出]
```

### Step 1: 科学论点提炼（Understand the Claim）
- 明确本张图在论文中服务于哪一个**核心科学命题**（如：“证明反应温度在 400℃ 达到极值”、“证实装料方式 I 比装料方式 II 使活化温度提前 31℃”）；
- 严禁为了“好看”而堆砌无论证价值的装饰性图表。

### Step 2: 数据特征画像（Profile the Data）
- 检查输入数据的维度、连续/离散属性、样本量 $n$、数据偏度与极值；
- 可调用 `scripts/profile_data.py` 自动获取数据画像；
- **防虚假外推**：若数据点稀疏（如 $n < 5$），绝不能只画一条光滑连线或单一柱状图，必须叠加散点并标明实测点数。

### Step 3: 图式架构与多面板设计（Select & Compose）
- 查阅 `references/chart_selection.md` 选用最佳图表形态；
- **坚守表图 2:1 黄金平衡律**：国赛 20~30 页论文严防“表多图少”导致的枯燥感，全书协同规划 **8 ~ 10 幅高质量科研级复合图版**（覆盖流程架构、资源画像、基准排产、时空排产热力图、风险分布箱线图与前沿、供求弹性与雷达、结构演变气泡图、灵敏度曲面与收敛回测四面板），与 15~20 张精修三线表形成 **2:1 的黄金学术视觉节奏**；
- **强制推行多面板复合图（Multi-panel Packaging）**：杜绝孤立、粗糙、低信息量的单线条小图，一律升格为带 (a)、(b)、(c) 编号的高信息密度复合图版（例如：左面板年度利润折线对比 + 右面板播种面积堆叠柱图；或 2×2 四面板全景图版）；
- 保持各子图坐标轴范围（xlim/ylim）与变量排布次序的高度一致性与视觉对称性。

### Step 4: 国赛与期刊版心规范（Journal & Contest Specs）
- 查阅 `references/journal_specs.md`；
- 国赛论文为 **A4 单栏页面**，版心宽度对应 Matplotlib 推荐尺寸：
  - **单面板图**：`figsize=(7.5, 4.8)`，DPI $\ge 300$；
  - **横向双面板图 (1×2)**：`figsize=(11, 4.8)`，DPI $\ge 300$；
  - **四面板网格图 (2×2)**：`figsize=(10, 8)`，DPI $\ge 300$；
- **排版版面自适应控制**：在 LaTeX 中嵌入时，推荐设置 `width=0.75\textwidth` 至 `0.80\textwidth`，并在长表处采用双栏并排压缩，确保大幅增图后总页数依然严格守死在 **30 页黄金预算** 以内；
- 字体层级阶梯：
  - 图表主标题（Title）：12~13 pt，黑体加粗；
  - 坐标轴标签（X/Y Label）：10~11 pt，宋体/黑体；
  - 刻度数字与图例（Ticks / Legend）：8.5~9.5 pt；
  - 面板标识符（(a), (b)）：12 pt，Times New Roman 加粗。

### Step 5: 规范样式与统一色板注入（Setup Environment）
- 在绘图代码开头统一导入 `scripts/setup_style.py`：
  ```python
  from scripts.setup_style import set_sci_style, SCI_PALETTE, cm_diverging
  set_sci_style() # 自动配置 CJK 中文字体抗乱码、负号支持与学术精美轴线
  ```
- **色彩映射铁律**：
  - 相关性/差异发散图：必须使用红蓝发散色板 `cm_diverging`（`#053061` 极深蓝 $\rightarrow$ 白/浅 $\rightarrow$ `#6A0624` 极深红），以 0.0 为中心对齐；
  - 连续单向密度/热度：使用单向蓝 `cm_seq_blue` 或单向红 `cm_seq_red`；
  - 多曲线/多分类离散图：按优先级使用 `SCI_PALETTE`（`#134B87` 深海蓝、`#D71C2C` 学术红、`#327DB7` 湛蓝、`#FEAB88` 珊瑚橙等）；
  - 基线/对照辅助线：固定使用中性灰虚线 `#767676`。

### Step 6: 确定性代码绘制与信息增强（Deterministic Plotting & Callouts）
- **直接指向型信息标注（In-situ Annotations）**：在关键拐点、极值点处使用 `ax.annotate()` 增加引线与数值框，注明机理意义（如 $T_{50}$、半衰期 $t_{1/2}$、Pareto 最优点）；
- 避免冗余或遮挡主要数据的图例，推荐将图例放置于 `bbox_to_anchor=(1.02, 1), loc='upper left'` 或右上角无数据空白区。

### Step 7: 视觉质量审核与雷区拦截（Visual QA Loop）
- 查阅 `references/viz_pitfalls.md` 与 `references/visual_review.md`，执行 12 点通关核验：
  1. [ ] 是否存在纵坐标无断轴标识的非零截断？
  2. [ ] 是否存在小样本下的均值柱状图欺骗？
  3. [ ] 图例是否压盖了数据折线或离群点？
  4. [ ] 坐标轴物理单位（如 ℃, wt%, ml/min, kJ/mol）是否齐全？
  5. [ ] 中文字体是否正常渲染（无豆腐块 `□` 或问号 `?`）？
  6. [ ] 多个子图的物理量级是否匹配、刻度是否对齐？
  7. [ ] 图中数值与论文正文统计结果（如 $R^2$, $F$, $P$）是否 100% 吻合？

### Step 8: 双轨高清导出（Dual-Track Export）
- 统一调用 `scripts/export_figure.py` 或保存为：
  - 交付/论文专用：`paper/figures/Qx/<fig_name>.png` 与 `paper/latex/figures/<fig_name>.png`（300+ DPI）；
  - 矢量支持：兼容生成 `.pdf` 矢量图供 LaTeX 高清嵌入。

---

## 参考文献与工具集索引

- `references/chart_selection.md`：数模六大常见场景选图决策表
- `references/journal_specs.md`：A4 单栏版面与字体度量标准
- `references/viz_pitfalls.md`：科研绘图十大常见雷区拦截手册
- `references/visual_review.md`：AI 视觉自检通关清单（Visual QA Checklist）
- `scripts/setup_style.py`：学术配色与 CJK 字体自适应配置模块
- `scripts/profile_data.py`：数据特征自动化探索画像脚本
- `scripts/export_figure.py`：双轨高分图像导出模块
