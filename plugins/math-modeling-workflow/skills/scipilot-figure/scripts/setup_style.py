"""
scipilot-figure: Unified Scientific Plotting Style & Palette Setup Module
Provides publication-grade style configurations conforming to national mathematical modeling contest invariants.
"""

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

# -------------------------------------------------------------------------
# 1. 统一科研色板体系 (Invariants: Scientific Color Scheme)
# -------------------------------------------------------------------------

# 统一离散学术 6 色板 (Categorical Palette)
SCI_PALETTE = [
    '#134B87',  # 主色1: 经典深海蓝 (第一主曲线/核心方法)
    '#D71C2C',  # 主色2: 学术红 (基线/第二对比曲线)
    '#327DB7',  # 主色3: 湛蓝 (第三对比曲线)
    '#FEAB88',  # 主色4: 珊瑚橙 (第四对比曲线)
    '#6A0624',  # 主色5: 深酒红 (极端极值强调点)
    '#6FAFD2',  # 主色6: 天青浅蓝 (次级分类/置信填充)
]

# 统一红蓝科研发散色板 (Diverging Colormap: 极夜深蓝 -> 浅色过渡 -> 极夜深红)
# 严格用于相关性热力图、聚类图、双极残差图，以 0.0 为中心对齐
DIVERGING_COLORS = [
    '#053061',  # 极低值 (Extreme Low: -1.0)
    '#134B87',  # 较低值
    '#327DB7',  # 低值
    '#6FAFD2',  # 偏低值
    '#C7E0ED',  # 中性偏低
    '#FFFFFF',  # 零点中性过渡
    '#FDD2BC',  # 中等值偏高
    '#FEAB88',  # 中高值
    '#D71C2C',  # 偏高值
    '#B80824',  # 高值
    '#6A0624'   # 极高值 (Extreme High: +1.0)
]
cm_diverging = LinearSegmentedColormap.from_list('sci_diverging', DIVERGING_COLORS, N=256)

# 统一单向顺序蓝色板 (Sequential Blue: 浅蓝 -> 极夜深蓝)
BLUE_COLORS = ['#C7E0ED', '#6FAFD2', '#327DB7', '#134B87', '#053061']
cm_seq_blue = LinearSegmentedColormap.from_list('sci_blue', BLUE_COLORS, N=256)

# 统一单向顺序红色板 (Sequential Red: 浅红 -> 极夜深红)
RED_COLORS = ['#FDD2BC', '#FEAB88', '#D71C2C', '#B80824', '#6A0624']
cm_seq_red = LinearSegmentedColormap.from_list('sci_red', RED_COLORS, N=256)

# 基线/参考线统一中性灰
SCI_BASELINE_GRAY = '#767676'


# -------------------------------------------------------------------------
# 2. 全局样式注入函数 (set_sci_style)
# -------------------------------------------------------------------------

def set_sci_style(font_scale=1.0, grid=True):
    """
    Apply top-tier scientific publication style:
    - Cross-platform CJK font fallbacks
    - True minus sign rendering
    - Refined line weights, tick directions, and spine aesthetics
    """
    # 跨平台中文字体自适应列表
    fonts = [
        'SimHei',             # Windows 黑体
        'Microsoft YaHei',    # Windows 微软雅黑
        'PingFang SC',        # macOS 苹方
        'Hiragino Sans GB',   # macOS 冬青黑体
        'WenQuanYi Micro Hei',# Linux 文泉驿微米黑
        'Noto Sans CJK SC',   # 通用开源中文字体
        'DejaVu Sans'         # 兜底英文字体
    ]
    
    style_dict = {
        # 字体
        'font.sans-serif': fonts,
        'axes.unicode_minus': False, # 正确显示负号
        'mathtext.fontset': 'stix',  # 数学公式使用 STIX 类似 Times
        
        # 字号阶梯 (按比例缩放)
        'font.size': 10.0 * font_scale,
        'axes.titlesize': 12.0 * font_scale,
        'axes.labelsize': 10.5 * font_scale,
        'xtick.labelsize': 9.0 * font_scale,
        'ytick.labelsize': 9.0 * font_scale,
        'legend.fontsize': 9.0 * font_scale,
        'figure.titlesize': 13.0 * font_scale,
        
        # 轴线与刻度
        'axes.linewidth': 1.0,
        'axes.edgecolor': '#333333',
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 4.0,
        'ytick.major.size': 4.0,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        
        # 网格规范 (浅灰细虚线置于底层)
        'axes.grid': grid,
        'grid.linestyle': ':',
        'grid.linewidth': 0.6,
        'grid.alpha': 0.5,
        'grid.color': '#B0B0B0',
        
        # 图例默认样式
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.edgecolor': '#CCCCCC',
        'legend.fancybox': True,
        
        # 渲染与清晰度
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05
    }
    
    mpl.rcParams.update(style_dict)
    print("SciPilot Scientific Plotting Style applied successfully!")


if __name__ == '__main__':
    set_sci_style()
    print("Color palettes available:")
    print("  SCI_PALETTE:", SCI_PALETTE)
    print("  cm_diverging:", cm_diverging.name)
