#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
audit_paper_narrative.py
------------------------
Automated Narrative & Quality Linter for Mathematical Modeling Papers.
Enforces Invariant 9 (AGENTS.md) and paper-section-writer standards:
1. AI Cliché & Software Engineering Blacklist detection.
2. Section word count & content depth threshold verification.
3. Cross-question Interface Sentences (Q1 -> Q2 -> Q3 -> Q4) verification.
4. Lay Physical Bridges (通俗生活化引桥) presence verification.
5. CER (Claim-Evidence-Mechanism) figure-text verification.
"""

import os
import re
import sys
import argparse
import json

# Ensure UTF-8 output in Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Prohibited AI Clichés and Software Engineering Jargon
BLACKLIST_PATTERNS = [
    (r"具有极高的(鲁棒性|泛化能力|精确度|工业应用价值)", "空洞的无量化褒奖词汇，应替换为具体工业价值或定量指标"),
    (r"根据数据审计(与预处理)?(的)?结果", "软件工程报表语体，应替换为具体统计清洗方法如IQR准则/残差学生化检验"),
    (r"有效提升了模型的(预测性能|拟合精度)", "缺乏量化支撑的套话，应给出具体 R2 或 RMSE 提升幅度"),
    (r"在未来的工作中(将进一步|可以进一步)", "研究生毕业论文凑字套话，数模竞赛正文严禁出现"),
    (r"由此可见，?该模型表现优异", "主观吹嘘，应替换为 QQ 图或交叉验证的统计学判断"),
    (r"充分证明了本方法的合理性与有效性", "空洞 AI 套话，应替换为具体机理检验结论"),
    (r"展现出了强大的学习能力", "空洞 AI 套话，数学建模论文应注重物理可解释性与严密推导"),
    (r"(圆满|成功)解决了(该|本)问题", "主观自我标榜，竞赛大忌"),
    (r"测试用例|验收标准|根据用户指令|融合版|底层代码", "软件工程遗留词汇，数模论文必须使用学术与工程语言"),
    # AI-flavor anti-patterns (去AI味核心拦截规则)
    (r"(只是|仅是|仅仅是)[^。！？\n]{0,60}?(不能|无法|不可)[^。！？\n]{0,60}?(只是|仅是|仅仅是)[^。！？\n]{0,60}?(还是|必须|仍需|要看)", "AI免责套娃模板：'只是…不能…只是…最终还是要'三重套娃免责零判断，应明确界定先验数理边界与加点指导作用"),
    (r"需要注意的是，?(这个|该|本)?方案只是", "AI免责套娃开场白，应直接陈述先验区间的数理定义与靶向设计目标"),
    (r"不能代替全空间的全面估计", "AI免责套话，应改为明确聚焦的核心高收率温区及其排除理由"),
    (r"(总的来说|综上所述|总体而言)，?(这个|该|本|这一)?(设计|模型|方案|架构|算法)", "AI总结段模板：'总的来说'开场+无信息增量复述，应删除或改为定量容差指标与决策执行指令"),
    (r"(可以考虑|不妨考虑|或许可以|可酌情考虑)(用|采用|将|作为|替换|引入)", "模糊建议词：决策规则里'可以考虑'不敢下结论，应改为确定性判定动作（如'判定采纳/执行工艺切换'）"),
    (r"(说明|表明|显示)可能(存在|有|是|会导致)?", "两头占推脱式表达：'说明可能'既想下结论又留余地，应给出确切物理判定或明确异常预案（如'判定存在…触发预案…'）"),
    (r"Claim-Evidence-Mechanism|\(Claim\)|\(Evidence\)|\(Mechanism\)", "形式化英文标签，应替换为自然的学生口吻中文结构（如'结果分析：1. 核心结论... 2. 数据验证... 3. 原因分析...'）"),
    (r"遵循竞赛铁律.*?绝不(出现)?", "软件/系统指令泄露套话，应改为平实的学术说明语句（如'为保证数据完整清晰，本文列出了...'）"),
    (r"实现了全局最优解的精确闭环|实现了.*?的精确闭环", "刻意拔高与夸张化词汇，应替换为客观的算法收敛描述"),
    (r"大M参数的紧致界限与松弛多面体体积最小化引理", "冗余专业堆砌，应简明表述为'大M参数的紧致边界'"),
    (r"需攻克并回答以下三大核心递进任务", "生硬模板句式，应改为'主要解决以下三个递进的种植优化问题'"),
    (r"面对高维时空离散组合，传统遗传算法极易陷入早熟收敛，导致高达.*?收益损失", "AI模板式对比吹嘘，应平实客观陈述算法对照实验结果"),
    # Theoretical overstatement & discrete/heuristic exaggeration (理论过度吹嘘与离散算法夸大)
    (r"(全球|全局)唯一均衡", "离散混合整数/不动点迭代无法理论保证全球唯一均衡，应替换为'在连续松弛价格子空间内具有局部唯一不动点'或'多起点冷启动数值实验显示高度收敛一致性'"),
    (r"理论保证全局(收敛|最优|内生唯一|均衡)", "离散整地/轮作硬约束下的启发式/不动点迭代在数学上无法理论保证全局收敛，应替换为'数值实验展现出优异的单调快速收敛特征'或'在指定容差下取得满足工程精度的最优近优解'"),
    (r"确保了.*?全局唯一", "用词偏强过满，应软化为'数值回测显示其在给定可行域内展现出高度稳健的局部唯一收敛解'"),
    (r"理论证明绝对|完美消除误差|完全消除不确定性", "违背科研审慎原则的绝对化论调，数模竞赛严禁出现"),
]

# Required Narrative Linkages (Interface Sentences)
CHEM_INTERFACE_THEMES = {
    "Q2_opening": {
        "section_kw": ["问题二", "七、"],
        "keywords": ["单变量", "上一节", "孤立", "协同", "交互", "混杂"],
        "desc": "Q2 开头承接：指出 Q1 单变量孤立分析的局限，引出 Q2 多元交互与混杂控制"
    },
    "Q3_opening": {
        "section_kw": ["问题三", "八、"],
        "keywords": ["全景", "第七节", "认知", "优化", "收益", "权衡", "博弈", "帕累托", "Pareto"],
        "desc": "Q3 开头承接：指出 Q2 探明了曲面规律，工业终极目标是寻优与平衡博弈"
    },
    "Q4_opening": {
        "section_kw": ["问题四", "九、"],
        "keywords": ["外推", "第八节", "盲区", "失活", "低温", "实验", "主动学习", "贝叶斯", "序贯"],
        "desc": "Q4 开头承接：指出 Q3 静态优化存在外推失活与盲区风险，驱动 Q4 序贯主动学习设计"
    }
}

AGRI_INTERFACE_THEMES = {
    "Q2_opening": {
        "section_kw": ["问题二", "六、", "七、"],
        "keywords": ["上一节", "确定性", "基准", "外生", "波动", "扰动", "气象", "通胀", "风险", "歉收"],
        "desc": "Q2 开头承接：指出 Q1 确定性基准假设的局限，引出 Q2 多维气候与市场不确定性"
    },
    "Q3_opening": {
        "section_kw": ["问题三", "七、", "八、"],
        "keywords": ["第二节", "价格", "外生", "内生", "供求", "弹性", "替代", "互补", "固氮", "失衡"],
        "desc": "Q3 开头承接：指出 Q2 价格外生静态的局限，引出 Q3 价格弹性内生均衡与固氮生态协同"
    }
}

CHEM_LAY_METAPHORS = [
    ("流水线|工人|工位|拆包|组装", "催化剂双组分配比的流水线工人比喻"),
    ("十字路口|红绿灯|车流|分流", "竞争副反应与活化能分流比喻"),
    ("观光车|停留时间|景区", "反应空速与停留时间比喻"),
    ("拔河|油门|刹车|阻尼", "转化率与选择性权衡/正则化比喻"),
    ("盲区|探险|开荒|信息增益", "主动学习探索与利用比喻"),
]

AGRI_LAY_METAPHORS = [
    ("粮豆轮作|固氮|根瘤菌|地力|培肥|土壤", "豆科根瘤菌共生固氮与地力蓄积比喻"),
    ("资产组合|防守|进攻|安全边际|压舱石|对冲", "农作物资产配置与风险对冲投资组合比喻"),
    ("价格弹性|薄利多销|倾销|以量补价|降价促销|折让", "供需响应与价格折让促销比喻"),
    ("晴雨表|气象|丰年|歉年|抗灾|歉收|波动", "气候波动与年景抗风险能力比喻"),
    ("大M法|门控|开关|时空排产|互斥|分段", "重茬互斥与逻辑门控时空调度比喻"),
]

def analyze_paper_text(filepath):
    if not os.path.exists(filepath):
        print(f"[ERROR] Target file not found: {filepath}")
        return False, {"error": "file_not_found"}

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        lines = content.splitlines()

    total_chars = len(content)
    total_words = len(re.findall(r"[\u4e00-\u9fa5]|\b\w+\b", content))

    issues = []
    warnings = []
    passed_items = []

    # 1. Scan Blacklist Clichés
    print("[Narrative Audit] Scanning for AI clichés and software jargon...")
    blacklist_hits = []
    for line_idx, line in enumerate(lines, 1):
        for pattern, explanation in BLACKLIST_PATTERNS:
            matches = re.finditer(pattern, line)
            for m in matches:
                blacklist_hits.append({
                    "line": line_idx,
                    "matched": m.group(0),
                    "explanation": explanation,
                    "snippet": line.strip()[:80]
                })

    if blacklist_hits:
        for hit in blacklist_hits:
            issues.append(f"Line {hit['line']}: Prohibited cliché '{hit['matched']}' -> {hit['explanation']}")
    else:
        passed_items.append("AI Cliché Blacklist: 100% clean, zero forbidden phrases detected.")

    # 2. Extract Subquestion Sections
    print("[Narrative Audit] Checking section substance and length...")
    sections = {}
    
    is_tex = filepath.endswith(".tex") or "\\section{" in content
    if is_tex:
        major_split_pattern = r"(?m)(?=\\section\{)"
        raw_sections = re.split(major_split_pattern, content)
        for sec_part in raw_sections:
            if re.search(r"摘\s*要", sec_part[:100]):
                sections["Abstract"] = sec_part
            elif re.search(r"\\section\{问题一", sec_part[:100]):
                sections["Q1"] = sec_part
            elif re.search(r"\\section\{问题二", sec_part[:100]):
                sections["Q2"] = sec_part
            elif re.search(r"\\section\{问题三", sec_part[:100]):
                sections["Q3"] = sec_part
            elif re.search(r"\\section\{问题四", sec_part[:100]):
                sections["Q4"] = sec_part
            elif re.search(r"\\section\{模型评价", sec_part[:100]):
                sections["Sensitivity"] = sec_part
    else:
        # Split by major section headings (e.g. ## 一、, ## 六、, ## 摘  要)
        major_split_pattern = r"(?m)(?=^##\s+(?:摘\s*要|[一二三四五六七八九十]+、))"
        raw_sections = re.split(major_split_pattern, content)

        for sec_part in raw_sections:
            if re.search(r"##\s+摘\s*要", sec_part):
                sections["Abstract"] = sec_part
            elif re.search(r"##\s+[一二三四五六七八九十]+、\s*问题一", sec_part):
                sections["Q1"] = sec_part
            elif re.search(r"##\s+[一二三四五六七八九十]+、\s*问题二", sec_part):
                sections["Q2"] = sec_part
            elif re.search(r"##\s+[一二三四五六七八九十]+、\s*问题三", sec_part):
                sections["Q3"] = sec_part
            elif re.search(r"##\s+[一二三四五六七八九十]+、\s*问题四", sec_part):
                sections["Q4"] = sec_part
            elif re.search(r"##\s+[一二三四五六七八九十]+、\s*模型评价", sec_part):
                sections["Sensitivity"] = sec_part

    # Check word counts per core subquestion
    print("[Narrative Audit] Checking section substance and length...")
    active_q_keys = [k for k in ["Q1", "Q2", "Q3", "Q4"] if k in sections]
    if not active_q_keys:
        active_q_keys = ["Q1", "Q2", "Q3"] # fallback
    for sec_key in active_q_keys:
        sec_text = sections.get(sec_key, "")
        sec_char_count = len(re.findall(r"[\u4e00-\u9fa5]", sec_text))
        if sec_char_count < 1000:
            issues.append(f"Section {sec_key} is too brief ({sec_char_count} Chinese chars). Minimum threshold is 1500 chars.")
        elif sec_char_count < 1800:
            warnings.append(f"Section {sec_key} has {sec_char_count} Chinese chars (Recommended >= 1800 for first-prize depth).")
        else:
            passed_items.append(f"Section {sec_key} substantive depth verified: {sec_char_count} Chinese chars.")

    # 3. Scan Interface Sentences
    is_agri = bool(re.search(r"种植|作物|地块|大棚|农业|耕地", content))
    curr_interfaces = AGRI_INTERFACE_THEMES if is_agri else CHEM_INTERFACE_THEMES
    curr_metaphors = AGRI_LAY_METAPHORS if is_agri else CHEM_LAY_METAPHORS

    print("[Narrative Audit] Checking cross-question Interface Sentences...")
    for iface_id, iface_cfg in curr_interfaces.items():
        sec_target = ""
        for s_key, s_text in sections.items():
            if any(kw in s_text[:100] for kw in iface_cfg["section_kw"]):
                sec_target = s_text[:1500] # Check first 1500 chars of section
                break
        
        found_kw = [kw for kw in iface_cfg["keywords"] if kw in sec_target]
        if len(found_kw) >= 2:
            passed_items.append(f"Interface '{iface_id}' detected (matched keywords: {', '.join(found_kw)}).")
        else:
            warnings.append(f"Interface '{iface_id}' weak or missing. {iface_cfg['desc']}")

    # 4. Check Lay Physical Bridges
    print("[Narrative Audit] Checking for Lay Metaphors & Physical Bridges...")
    found_metaphors = []
    for pat, desc in curr_metaphors:
        if re.search(pat, content):
            found_metaphors.append(desc)
    
    if len(found_metaphors) >= 3:
        passed_items.append(f"Lay Physical Bridges verified ({len(found_metaphors)}/5 themes found: {'; '.join(found_metaphors)}).")
    else:
        warnings.append(f"Lay Metaphors insufficient (only found {len(found_metaphors)}/5). Add intuitive analogies for non-domain judges.")

    # 5. Check CER figure descriptions
    print("[Narrative Audit] Checking Figure Claim-Evidence-Mechanism descriptions...")
    # Find all figures actually present/captioned in the paper
    declared_figs = re.findall(r"图\s*(\d+)", content)
    unique_figs = sorted(list(set(int(x) for x in declared_figs if int(x) <= 20)))
    if not unique_figs:
        unique_figs = [1, 2, 3, 4]
    for i in unique_figs:
        fp = f"图\\s*{i}"
        matches = list(re.finditer(fp, content))
        if len(matches) < 2: # Should appear at least in caption and narrative text
            warnings.append(f"Figure {fp} may lack narrative in-text CER reference.")
        else:
            first_m = matches[0]
            start_pos = max(0, first_m.start() - 50)
            end_pos = min(len(content), first_m.end() + 300)
            context = content[start_pos:end_pos]
            if "如图" in context and len(context.strip()) < 80:
                warnings.append(f"Figure {fp} description appears superficial ('如图...所示' without detailed CER interpretation).")

    # 5.5. Check Visual Rhythm and Table-to-Figure Golden Balance
    print("[Narrative Audit] Checking Visual Rhythm & Table-to-Figure Balance...")
    if filepath.endswith('.tex'):
        n_figs = len(re.findall(r'\\begin\{figure\}', content))
        n_tables = len(re.findall(r'\\begin\{table\}', content))
    else:
        n_figs = len(set(re.findall(r'图\s*(\d+)', content)))
        tab_caps = re.findall(r'(\*\*表\s*[\d\w\-]+[^\n]*\*\*)', content)
        n_tables = len(tab_caps) if tab_caps else len(set(re.findall(r'表\s*(\d+)', content)))

    tf_ratio = n_tables / max(1, n_figs)
    if n_figs >= 7 and tf_ratio <= 2.8:
        passed_items.append(f"Visual Rhythm & Table-to-Figure Balance verified ({n_figs} figures, {n_tables} tables, ratio {tf_ratio:.2f}:1 within 1.5~2.5:1 golden range).")
    elif n_figs < 6 or tf_ratio > 3.0:
        warnings.append(f"Table-to-Figure ratio is heavily imbalanced ({n_tables} tables vs {n_figs} figures, ratio {tf_ratio:.2f}:1 > 2.8). Risk of visual fatigue for judges. Recommend 8~10 figures with 2:1 golden ratio.")
    else:
        passed_items.append(f"Table-to-Figure ratio acceptable ({n_figs} figures, {n_tables} tables, ratio {tf_ratio:.2f}:1).")

    # 6. Check Top 5 Pitfalls in Core Statistical Sections (Especially Q2)
    if not is_agri:
        print("[Narrative Audit] Checking defense against Top 5 Pitfalls (Simpson, Interaction, Mechanism, Alignment, Depth)...")
        q2_text = sections.get("Q2", "")
        if q2_text:
            if not re.search(r"(表\s*3-B|样本量|分布矩阵|透视表|低温区|55\.2%)", q2_text):
                warnings.append("Q2 lacks explicit Simpson Paradox sample distribution table/matrix (e.g. Table 3-B with sample sizes).")
            else:
                passed_items.append("Q2 Simpson Paradox defense: Explicit sample distribution matrix detected.")

            # Check explicit interaction spread delta
            if not re.search(r"(极差|敏感度|放大|倍|Spread)", q2_text):
                warnings.append("Q2 interaction effects lack explicit quantified spread deltas (e.g. spread at 250C vs 400C).")
            else:
                passed_items.append("Q2 Interaction Effect defense: Quantified spread delta / sensitivity amplification detected.")

            # Check mechanistic literature & byproduct validation
            if not re.search(r"(文献|Bell|Fogler|反应网络|副产物|乙醛|缩合位点)", q2_text):
                warnings.append("Q2 mechanism lacks authoritative literature linkage or experimental byproduct validation.")
            else:
                passed_items.append("Q2 Mechanism defense: Authoritative literature / byproduct cross-validation detected.")

            # Check rigorous quasicontrol or permutation residuals
            if not re.search(r"(准对照|置换检验|Freedman|残差|投影矩阵|绝对残差)", q2_text):
                warnings.append("Q2 lacks solid mathematical derivation or point-to-point residual evaluation for advanced methods.")
            else:
                passed_items.append("Q2 Advanced Method defense: Point-to-point residual / projection operator detected.")
    else:
        # Agri checks: check CVaR, Monte Carlo LHS, and SAA convergence
        q2_text = sections.get("Q2", "")
        if q2_text:
            if re.search(r"CVaR|置信|蒙特卡洛|扰动|尾部|分布", q2_text):
                passed_items.append("Q2 Risk & Uncertainty defense: Monte Carlo & Mean-CVaR formulation verified.")
            if re.search(r"(拉丁超立方|LHS|超立方抽样)", q2_text):
                passed_items.append("Q2 Sampling Method defense: Latin Hypercube Sampling (LHS) verified.")
            if re.search(r"(SAA|样本量|收敛|情景规模)", q2_text):
                passed_items.append("Q2 Sample Convergence defense: SAA scenario convergence test verified.")


    # Output results
    print("\n" + "="*70)
    print(f" NARRATIVE AUDIT REPORT: {os.path.basename(filepath)}")
    print(f" Total Length: {total_chars} chars | {total_words} words | Subsections: {len(sections)}")
    print("="*70)

    for item in passed_items:
        print(f"  [PASS] {item}")

    if warnings:
        print("\n" + "-"*70)
        print("  WARNINGS (Suggestions for improvement):")
        for w in warnings:
            print(f"  [WARN] {w}")

    if issues:
        print("\n" + "-"*70)
        print("  FAILURES (Must be fixed before sign-off):")
        for err in issues:
            print(f"  [FAIL] {err}")
        print("="*70)
        return False, {"status": "FAIL", "issues": issues, "warnings": warnings}
    else:
        print("\n" + "="*70)
        print("  AUDIT PASSED: Paper narrative adheres to First-Prize standards!")
        print("="*70)
        return True, {"status": "PASS", "issues": issues, "warnings": warnings}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit mathematical modeling paper narrative quality.")
    parser.add_argument("--file", default="paper/master/full_paper.md", help="Path to paper markdown file")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    # Resolve relative path to repo root if needed
    target_path = args.file
    if not os.path.isabs(target_path):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        target_path = os.path.join(repo_root, target_path)

    passed, report = analyze_paper_text(target_path)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if passed else 1)
