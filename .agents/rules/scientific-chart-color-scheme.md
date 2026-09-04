# 科研绘图统一颜色方案与规范 (Scientific Chart Color Scheme)

本规范定义全国大学生数学建模竞赛全流程中所有数据可视化图表（包括 Python Matplotlib/Seaborn、MATLAB 等）必须严格遵守的**统一科研绘图配色方案**。
所有生成的论文插图必须保持调色风格高度一致，严禁使用杂乱随机色或未定义的高饱和度默认配色（如 `jet`）。

---

## 一、标准色板速查表 (HEX & RGB)

| 梯度级别 | 语义说明 | 推荐十六进制 (HEX) | RGB 对应值 | 适用视觉场景 |
| :--- | :--- | :--- | :--- | :--- |
| **极高值 (Extreme High)** | 极强相关/极大值/顶层聚类 | `#6A0624` | `(106, 6, 36)` | 热力图最高点、关键极值标记 |
| **高值 (High)** | 强正相关/高指标 | `#B80824` | `(184, 8, 36)` | 强显著性、第二对比线 |
| **偏高值 (Medium-High)** | 中强相关/偏高指标 | `#D71C2C` | `(215, 28, 44)` | 对比曲线、重点关注类 |
| **中高值 (Lower-High)** | 弱正相关/适度偏高 | `#FEAB88` | `(254, 171, 136)` | 过渡区域、次要分类柱 |
| **中等值 (Neutral-Light)** | 接近零/中性基准过渡 | `#FDD2BC` | `(253, 210, 188)` | 浅红暖色过渡、中度基线 |
| **中性偏低 (Neutral-Low)** | 浅蓝过渡/中性偏弱 | `#C7E0ED` | `(199, 224, 237)` | 浅蓝冷色过渡、背景对比 |
| **偏低值 (Medium-Low)** | 弱负相关/适度偏低 | `#6FAFD2` | `(111, 175, 210)` | 次级蓝色系、置信区间填充 |
| **低值 (Low)** | 中强负相关/偏低指标 | `#327DB7` | `(50, 125, 183)` | 辅助分类曲线、天青蓝 |
| **较低值 (Lower)** | 强负相关/低指标 | `#134B87` | `(19, 75, 135)` | 主方法/第一主曲线、深海蓝 |
| **极低值 (Extreme Low)** | 极强负相关/极低指标 | `#053061` | `(5, 48, 97)` | 极夜深蓝、最低点强调 |

---

## 二、图表类型与色彩映射规则

### 1. 双极发散图（Diverging Colormap）
- **适用场景**：相关性矩阵热力图（带数值）、层次聚类热力图、接触图/距离矩阵、正负残差图。
- **色彩序列（由低至高）**：
  `#053061` (极暗蓝) $\rightarrow$ `#134B87` $\rightarrow$ `#327DB7` $\rightarrow$ `#6FAFD2` $\rightarrow$ `#C7E0ED` $\rightarrow$ `#FFFFFF` (或 `#FDD2BC`) $\rightarrow$ `#FEAB88` $\rightarrow$ `#D71C2C` $\rightarrow$ `#B80824` $\rightarrow$ `#6A0624` (极暗红)。
- **中心对齐**：相关系数必须以 `0.0` 为居中白/浅过渡色，`vmin=-1.0, vmax=1.0`。

### 2. 顺序图（Sequential Colormap）
- **适用场景**：非负单向指标、样本密度、概率分布、混淆矩阵、距离矩阵。
- **蓝色系（推荐默认）**：
  `#C7E0ED` (浅) $\rightarrow$ `#6FAFD2` $\rightarrow$ `#327DB7` $\rightarrow$ `#134B87` $\rightarrow$ `#053061` (深)。
- **红色系（风险/损失/耗散类）**：
  `#FDD2BC` (浅) $\rightarrow$ `#FEAB88` $\rightarrow$ `#D71C2C` $\rightarrow$ `#B80824` $\rightarrow$ `#6A0624` (深)。

### 3. 离散分类图（Categorical Palette for Curves / Bars / Scatters）
折线图多曲线对比、柱状图分组、散点图聚类类别必须按固定顺序选用高对比、协调的高级学术色彩：
1. **主曲线 / 类别1（核心方法/最高优先级）**：`#134B87`（经典深海蓝）
2. **对比曲线 / 类别2（基线/对比方法）**：`#D71C2C`（经典学术红）
3. **对比曲线 / 类别3**：`#327DB7`（湛蓝）
4. **对比曲线 / 类别4**：`#FEAB88`（珊瑚橙）
5. **对比曲线 / 类别5**：`#6A0624`（深酒红）
6. **对比曲线 / 类别6**：`#6FAFD2`（天青浅蓝）
7. **背景/基线/参考辅助线 (Baseline)**：固定使用中性灰 `#767676`（虚线 `linestyle='--'`）。

---

## 三、标准代码模板集成

### 1. Python (Matplotlib / Seaborn)

在绘图代码开头统一定义并注册：

```python
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# 统一科研绘图离散色板 (Categorical)
SCI_PALETTE = [
    '#134B87',  # 主色1: 深海蓝
    '#D71C2C',  # 主色2: 学术红
    '#327DB7',  # 主色3: 湛蓝
    '#FEAB88',  # 主色4: 珊瑚橙
    '#6A0624',  # 主色5: 深酒红
    '#6FAFD2',  # 主色6: 天青浅蓝
]

# 统一科研发散色板 (Diverging Colormap: 蓝 -> 白/浅 -> 红)
DIVERGING_COLORS = [
    '#053061', '#134B87', '#327DB7', '#6FAFD2', '#C7E0ED',
    '#FFFFFF',
    '#FDD2BC', '#FEAB88', '#D71C2C', '#B80824', '#6A0624'
]
cm_diverging = LinearSegmentedColormap.from_list('sci_diverging', DIVERGING_COLORS, N=256)

# 统一顺序蓝色板 (Sequential Blue)
BLUE_COLORS = ['#C7E0ED', '#6FAFD2', '#327DB7', '#134B87', '#053061']
cm_seq_blue = LinearSegmentedColormap.from_list('sci_blue', BLUE_COLORS, N=256)

# 统一顺序红色板 (Sequential Red)
RED_COLORS = ['#FDD2BC', '#FEAB88', '#D71C2C', '#B80824', '#6A0624']
cm_seq_red = LinearSegmentedColormap.from_list('sci_red', RED_COLORS, N=256)

# 设置全局绘图属性
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

### 2. MATLAB

```matlab
% 统一科研配色矩阵 (RGB 归一化)
diverging_colors = [
    5, 48, 97;
    19, 75, 135;
    50, 125, 183;
    111, 175, 210;
    199, 224, 237;
    255, 255, 255;
    253, 210, 188;
    254, 171, 136;
    215, 28, 44;
    184, 8, 36;
    106, 6, 36
] / 255;

colormap(diverging_colors);

% 离散曲线/柱状图标准色
sci_palette = {
    [19, 75, 135]/255, ...  % 主色1: 深海蓝
    [215, 28, 44]/255, ...  % 主色2: 学术红
    [50, 125, 183]/255, ... % 主色3: 湛蓝
    [254, 171, 136]/255, ...% 主色4: 珊瑚橙
    [106, 6, 36]/255, ...   % 主色5: 深酒红
    [111, 175, 210]/255     % 主色6: 天青浅蓝
};
```

---

## 四、强制校验清单

1. **热力图检查**：
   - 互相关系数图 `cmap=cm_diverging, vmin=-1, vmax=1`，带数值标注；
   - 混淆矩阵使用 `cmap=cm_seq_blue`，背景深时数字文本为白色，背景浅时数字文本为黑色。
2. **多图一致性**：
   - 同一论文中，同一模型/算法在不同折线图或柱状图中颜色必须固定一致；
   - 对比基线/基准线固定采用灰度 `#767676` 虚线。
3. **输出要求**：
   - 论文图表分辨率最低 300 dpi，推荐 600 dpi，无毛刺、标签文字无遮挡。
