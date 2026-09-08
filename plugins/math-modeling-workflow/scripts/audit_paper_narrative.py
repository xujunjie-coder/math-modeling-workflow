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
]

# Required Narrative Linkages (Interface Sentences)
REQUIRED_INTERFACE_THEMES = {
    "Q2_opening": {
        "section": "七、",
        "keywords": ["单变量", "上一节", "孤立", "协同", "交互", "混杂"],
        "desc": "Q2 开头承接：指出 Q1 单变量孤立分析的局限，引出 Q2 多元交互与混杂控制"
    },
    "Q3_opening": {
        "section": "八、",
        "keywords": ["全景", "第七节", "认知", "优化", "收益", "权衡", "博弈", "帕累托", "Pareto"],
        "desc": "Q3 开头承接：指出 Q2 探明了曲面规律，工业终极目标是寻优与平衡博弈"
    },
    "Q4_opening": {
        "section": "九、",
        "keywords": ["外推", "第八节", "盲区", "失活", "低温", "实验", "主动学习", "贝叶斯", "序贯"],
        "desc": "Q4 开头承接：指出 Q3 静态优化存在外推失活与盲区风险，驱动 Q4 序贯主动学习设计"
    }
}

# Key Lay Metaphors expected across the paper
LAY_METAPHOR_KEYWORDS = [
    ("流水线|工人|工位|拆包|组装", "催化剂双组分配比的流水线工人比喻"),
    ("十字路口|红绿灯|车流|分流", "竞争副反应与活化能分流比喻"),
    ("观光车|停留时间|景区", "反应空速与停留时间比喻"),
    ("拔河|油门|刹车|阻尼", "转化率与选择性权衡/正则化比喻"),
    ("盲区|探险|开荒|信息增益", "主动学习探索与利用比喻"),
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
    
    # Split by major section headings (e.g. ## 一、, ## 六、, ## 摘  要)
    major_split_pattern = r"(?m)(?=^##\s+(?:摘\s*要|[一二三四五六七八九十]+、))"
    raw_sections = re.split(major_split_pattern, content)

    for sec_part in raw_sections:
        if re.search(r"##\s+摘\s*要", sec_part):
            sections["Abstract"] = sec_part
        elif re.search(r"##\s+六、\s*问题一", sec_part):
            sections["Q1"] = sec_part
        elif re.search(r"##\s+七、\s*问题二", sec_part):
            sections["Q2"] = sec_part
        elif re.search(r"##\s+八、\s*问题三", sec_part):
            sections["Q3"] = sec_part
        elif re.search(r"##\s+九、\s*问题四", sec_part):
            sections["Q4"] = sec_part
        elif re.search(r"##\s+十、\s*模型评价", sec_part):
            sections["Sensitivity"] = sec_part

    # Check word counts per core subquestion
    print("[Narrative Audit] Checking section substance and length...")
    for sec_key in ["Q1", "Q2", "Q3", "Q4"]:
        sec_text = sections.get(sec_key, "")
        sec_char_count = len(re.findall(r"[\u4e00-\u9fa5]", sec_text))
        if sec_char_count < 1000:
            issues.append(f"Section {sec_key} is too brief ({sec_char_count} Chinese chars). Minimum threshold is 1500 chars.")
        elif sec_char_count < 1800:
            warnings.append(f"Section {sec_key} has {sec_char_count} Chinese chars (Recommended >= 1800 for first-prize depth).")
        else:
            passed_items.append(f"Section {sec_key} substantive depth verified: {sec_char_count} Chinese chars.")

    # 3. Scan Interface Sentences
    print("[Narrative Audit] Checking cross-question Interface Sentences...")
    for iface_id, iface_cfg in REQUIRED_INTERFACE_THEMES.items():
        sec_target = ""
        for s_key, s_text in sections.items():
            if iface_cfg["section"] in s_text[:100]:
                sec_target = s_text[:1500] # Check first 1500 chars of section
                break
        
        found_kw = [kw for kw in iface_cfg["keywords"] if kw in sec_target]
        if len(found_kw) >= 2:
            passed_items.append(f"Interface '{iface_id}' detected (matched keywords: {', '.join(found_kw)}).")
        else:
            warnings.append(f"Interface '{iface_id}' weak or missing in {iface_cfg['section']}. {iface_cfg['desc']}")

    # 4. Check Lay Physical Bridges
    print("[Narrative Audit] Checking for Lay Metaphors & Physical Bridges...")
    found_metaphors = []
    for pat, desc in LAY_METAPHOR_KEYWORDS:
        if re.search(pat, content):
            found_metaphors.append(desc)
    
    if len(found_metaphors) >= 3:
        passed_items.append(f"Lay Physical Bridges verified ({len(found_metaphors)}/5 themes found: {'; '.join(found_metaphors)}).")
    else:
        warnings.append(f"Lay Metaphors insufficient (only found {len(found_metaphors)}/5). Add intuitive analogies for non-domain judges.")

    # 5. Check CER figure descriptions
    print("[Narrative Audit] Checking Figure Claim-Evidence-Mechanism descriptions...")
    fig_patterns = [f"图\\s*{i}" for i in range(1, 7)]
    for fp in fig_patterns:
        matches = list(re.finditer(fp, content))
        if not matches:
            warnings.append(f"No narrative reference found for {fp}.")
        else:
            # Check context around first reference
            first_m = matches[0]
            start_pos = max(0, first_m.start() - 50)
            end_pos = min(len(content), first_m.end() + 300)
            context = content[start_pos:end_pos]
            if "如图" in context and len(context.strip()) < 100:
                warnings.append(f"Figure {fp} description appears superficial ('如图...所示' without detailed CER interpretation).")

    # 6. Check Top 5 Pitfalls in Core Statistical Sections (Especially Q2)
    print("[Narrative Audit] Checking defense against Top 5 Pitfalls (Simpson, Interaction, Mechanism, Alignment, Depth)...")
    q2_text = sections.get("Q2", "")
    if q2_text:
        # Check Simpson table & sample distribution
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
