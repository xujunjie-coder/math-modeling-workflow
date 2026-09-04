# 数学建模代码变量与文件命名特殊约束规则

本规则适用于在当前数学建模工作流中编写或审查的所有计算分析代码、脚本文件、中间数据、结果表格与输出图片（包括 Python、MATLAB / 北太天元、CSV、PNG、SVG 等）。

## 核心原则与禁忌

1. **禁用通用标准命名规范与复杂超长英文**：
   - 严禁使用通用冗长、教科书式、脱离题目实际背景的复杂英文命名（如 `lead_barium_weathered_ratio`、`silicon_dioxide_concentration` 或超长文件名 `multivariate_heterogeneous_weathering_pipeline.py`）。
   - 变量与文件均严格遵循“化学式优先 + 大学英语四级（CET-4）简单英文 + 其余全拼拼音”的精炼法则。

## 命名三层判定逻辑

### 1. 化学元素与分子式（最高优先级）
- 只要变量概念涉及化学元素、无机化合物、化学分子式或材料成分，**必须直接使用规范化学式或元素符号**（严格保持标准大小写）。
- **禁止使用英语化学名称**。
- 示例：
  - 铅（Lead） $\rightarrow$ `Pb`
  - 钡（Barium） $\rightarrow$ `Ba`
  - 二氧化硅（Silica） $\rightarrow$ `SiO2`
  - 氧化铁 $\rightarrow$ `Fe2O3`
  - 氧化铝 $\rightarrow$ `Al2O3`
  - 氧化钙 $\rightarrow$ `CaO`

### 2. 大学英语四级（CET-4）词汇界限
- **四级以内词汇**：仅属于大学英语四级（CET-4）大纲常用基础词汇的概念，可以使用**英文**命名。
  - 常用允许词汇：`data`, `time`, `loss`, `score`, `weight`, `rate`, `speed`, `step`, `mean`, `max`, `min`, `price`, `type`, `error`, `result`, `index`, `group`, `train`, `test`, `model`, `status`, `target` 等。
- **四级以外词汇 / 领域专有名词**：凡超出大学英语四级范围的专有名词、业务概念、中文特有术语，**必须强制使用汉语拼音（全拼）**命名。禁止使用四级以上的生僻高级英文。
  - 必须使用拼音的示例：
    - 风化 $\rightarrow$ `fenghua`
    - 纹饰 $\rightarrow$ `wenshi`
    - 铅钡 $\rightarrow$ `qianbei`
    - 高钾 $\rightarrow$ `gaojia`
    - 颜色 $\rightarrow$ `yanse`
    - 文物 $\rightarrow$ `wenwu`
    - 采样 $\rightarrow$ `caiyang`
    - 特征 $\rightarrow$ `tezheng`
    - 残差 $\rightarrow$ `cancha`
    - 聚类 $\rightarrow$ `julei`
    - 差异 $\rightarrow$ `chayi`

### 3. 复合变量命名规范
复合概念变量通过下划线 `_` 拼接各单元：
- 化学式 + 四级英文 / 拼音：
  - 铅含量/比例：`Pb_rate` 或 `Pb_hanliang`
  - 二氧化硅均值：`SiO2_mean`
  - 氧化钡预测值：`BaO_pred` 或 `BaO_yuce`
- 拼音 + 四级英文 / 拼音：
  - 纹饰类型：`wenshi_type`
  - 风化状态：`fenghua_status`
  - 铅钡风化样本：`qianbei_fenghua`
  - 高钾文物分组：`gaojia_wenwu_group`
  - 聚类结果：`julei_result`

## 复核判定清单

在执行 `code-reviewer`、`python-code-reviewer` 或 `matlab-code-reviewer` 审查时，必须对照下表检查代码变量命名是否合规：

| 变量场景 | 违规示例（必须拦截） | 合规示例（准许通过） | 判定原因 |
|---|---|---|---|
| 铅元素比例 | `lead_ratio`, `pb_content_val` | `Pb_rate` / `Pb_hanliang` | 铅必须用化学式 `Pb`；ratio在四级内或hanliang拼音 |
| 二氧化硅 | `silica`, `silicon_dioxide` | `SiO2` | 化学分子式强制使用 `SiO2` |
| 纹饰分类 | `ornamentation_type` | `wenshi_type` | 纹饰超出四级范围，必须用拼音 `wenshi` |
| 风化程度 | `weathering_level` | `fenghua_level` / `fenghua_chengdu` | 风化超出四级范围，必须用拼音 `fenghua` |
| 铅钡类别 | `lead_barium_category` | `qianbei_type` / `qianbei_fenlei` | 铅钡为领域专有名词，必须用拼音 `qianbei` |

## 第三方库形参及数学算法术语豁免白名单

为了保证代码运行稳定与自动化审查顺畅，以下两类场景享有豁免权，代码审查 Agent **严禁误报拦截**：

1. **第三方库与内置函数关键字参数（API Kwargs）**：
   - 依赖库的固有参数名保持原样，完全豁免拼音限制，例如：
     - `pd.read_excel(sheet_name=..., index_col=...)`
     - `train_test_split(test_size=..., random_state=...)`
     - `scipy.optimize.minimize(method=..., bounds=..., constraints=...)`
     - `plt.plot(color=..., linestyle=..., label=...)`
2. **标准数学与通用算法简写**：
   - 算法与数学中的公认核心简写允许使用英文简写：
     - `opt` (优化/最优), `loss` (损失), `res` (残差/结果), `grad` (梯度), `iter` (迭代), `dim` (维度), `dist` (距离), `pred` (预测), `prob` (概率), `step` (步长), `idx` (索引), `val` (数值)。

## 文件命名特殊约束规范（简单词汇或拼音优先）

在数学建模工作流中创建或导出的所有文件（分析脚本、数据表格、可视化图片、模型权重等），必须严格遵循**“尽量简单词汇或全拼拼音命名”**的原则：

1. **基础简单词汇（简单英文）**：
   - 仅限使用最简单通俗的英文单词（如四级以内常用基础功能词）：
     - 常用基础词：`data`, `clean`, `main`, `test`, `train`, `model`, `run`, `check`, `score`, `loss`, `tab`, `fig`, `metric`, `q1`, `q2`, `q3` 等；
     - 合规文件名示例：`clean_data.py`, `q1_main.py`, `q1_model.py`, `fig1_trend.png`, `tab1_summary.csv`。
2. **业务与领域专有概念强制使用全拼拼音**：
   - 凡涉及题目特有的背景、具体业务、中文专属名词，**一律使用汉语全拼拼音**，严禁自创生僻超长英文：
     - 风化相关数据：`fenghua_data.csv`（不使用 `weathering_processed_data.csv`）
     - 铅钡聚类分析：`qianbei_julei.py`（不使用 `lead_barium_clustering_pipeline.py`）
     - 纹饰分类图：`wenshi_fenlei.png`（不使用 `ornamentation_classification_plot.png`）
     - 高钾特征表：`gaojia_tezheng.csv`（不使用 `high_potassium_feature_set.csv`）
     - 采样残差图：`caiyang_cancha.png`（不使用 `sampling_residuals_analysis.png`）
3. **化学物质优先化学式**：
   - 凡涉及化学元素或化学分子式的文件名，优先直接采用化学式命名：
     - `Pb_Ba_rate.csv`（铅钡含量比例）
     - `SiO2_caiyang.png`（二氧化硅采样分布）
4. **严禁冗长生僻英文**：
   - 坚决杜绝如 `multivariate_heterogeneous_weathering_feature_extraction_pipeline.py` 这种超长英文文件名。保持文件命名短小精炼、易读易懂。
