# Color Systems for Mathematical Modeling Figures (科研绘图统一配色系统)

## Design Philosophy

Color in mathematical modeling figures serves three purposes:
1. **Identity**: which method/data series is this?
2. **Direction**: is this better (+) or worse (-), or positive vs negative correlation?
3. **Hierarchy**: is this primary evidence or supporting information?

Every color choice should answer one of these. Avoid using color purely decoratively. All figures must adhere to this unified scientific palette.

---

## 统一科研绘图标准色表 (Scientific Palette Lookup)

依据竞赛标准化科研色彩方案定义：

| 级别 | 语义 | HEX | RGB | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **极高值** | 极大值 / 顶层聚类 | `#6A0624` | `(106, 6, 36)` | 深酒红 |
| **高值** | 强正相关 / 高指标 | `#B80824` | `(184, 8, 36)` | 鲜红 |
| **偏高值** | 中强相关 / 偏高指标 | `#D71C2C` | `(215, 28, 44)` | 明红 |
| **中高值** | 弱正相关 / 适度偏高 | `#FEAB88` | `(254, 171, 136)` | 珊瑚橙 |
| **中等值** | 浅红暖过渡 / 中性 | `#FDD2BC` | `(253, 210, 188)` | 浅粉暖色 |
| **中性偏低** | 浅蓝冷过渡 / 中性 | `#C7E0ED` | `(199, 224, 237)` | 冰浅蓝 |
| **偏低值** | 弱负相关 / 偏低 | `#6FAFD2` | `(111, 175, 210)` | 天青浅蓝 |
| **低值** | 中强负相关 / 偏低指标 | `#327DB7` | `(50, 125, 183)` | 湛蓝 |
| **较低值** | 强负相关 / 低指标 | `#134B87` | `(19, 75, 135)` | 深海蓝 |
| **极低值** | 极负相关 / 极低指标 | `#053061` | `(5, 48, 97)` | 极夜深蓝 |

---

## 1. 连续尺度与矩阵图表 (Continuous Scales & Heatmaps)

### 双极发散调色板 (Diverging Colormap: 蓝 -> 白 -> 红)
适用：相关性矩阵、层次聚类热力图、接触矩阵、残差矩阵、有正负意义的差异图。
```python
from matplotlib.colors import LinearSegmentedColormap

DIVERGING_COLORS = [
    '#053061', '#134B87', '#327DB7', '#6FAFD2', '#C7E0ED',
    '#FFFFFF',
    '#FDD2BC', '#FEAB88', '#D71C2C', '#B80824', '#6A0624'
]
cm_diverging = LinearSegmentedColormap.from_list('sci_diverging', DIVERGING_COLORS, N=256)
```

### 单向顺序调色板 (Sequential Colormap)
适用：非负数量、概率密度、混淆矩阵、距离矩阵。
```python
# 蓝色系 (默认非负/密度指标)
BLUE_COLORS = ['#C7E0ED', '#6FAFD2', '#327DB7', '#134B87', '#053061']
cm_seq_blue = LinearSegmentedColormap.from_list('sci_blue', BLUE_COLORS, N=256)

# 红色系 (损失/风险/耗散)
RED_COLORS = ['#FDD2BC', '#FEAB88', '#D71C2C', '#B80824', '#6A0624']
cm_seq_red = LinearSegmentedColormap.from_list('sci_red', RED_COLORS, N=256)
```

---

## 2. 离散类别与多曲线图表 (Categorical Palette)

适用：折线对比图、分组柱状图、散点图聚类类别。

```python
SCI_PALETTE = [
    '#134B87',  # 主色1: 核心方法 / 主曲线 (深海蓝)
    '#D71C2C',  # 主色2: 对比方法 / 第二主曲线 (学术红)
    '#327DB7',  # 主色3: 辅助方法 (湛蓝)
    '#FEAB88',  # 主色4: 辅助分类 (珊瑚橙)
    '#6A0624',  # 主色5: 次要类别 (深酒红)
    '#6FAFD2',  # 主色6: 补充类别 (天青浅蓝)
]

BASELINE_COLOR = '#767676'  # 基线/参考线统一采用中性灰虚线
```

---

## 3. 配色一致性规则 (Consistency Rules)

1. **同模型同色**：在全篇论文的不同插图中，同一个模型或算法必须固定使用同一种颜色。
2. **禁止随机配色与默认彩虹色**：严禁在论文中使用高饱和度杂乱的 `jet`、纯红纯绿或系统默认色卡。
3. **清晰可读性**：热力图中的数值文字标签必须随背景深浅自适应切换反色（深色背景使用白字，浅色背景使用黑字）。
