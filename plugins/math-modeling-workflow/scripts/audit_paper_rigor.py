#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
audit_paper_rigor.py
--------------------
Automated Rigor, Consistency & Gatekeeping Linter for Mathematical Modeling Papers.
Specialized guardian for:
1. Inequality Directional Consistency (不等式数值与方向一致性)
2. Text-Formula-Data Tri-Consistency (正文数据、公式系数与数据源三位一体对齐)
3. DoE Table Parameter Inversion Prevention (实验设计矩阵背景参数颠倒防范)
4. Decision Threshold Sourcing & Degrees of Freedom (自适应决策硬阈值数理统计来源)
5. Model Extrapolation vs Empirical Truth Boundary (推演先验与实测真值边界界定)
6. Academic Restraint & Anti-Hype Blacklist (去口号化与学术克制文风审查)
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

# 1. Non-academic hype slogans and non-restrained wording blacklist
HYPE_BLACKLIST = [
    (r"坚如磐石", "口号式非学术用语，应替换为'具有显著的统计稳健性'"),
    (r"无可替代", "非学术夸张修辞，应替换为'具有不可忽视的独特工艺优势'"),
    (r"所向披靡", "极度夸张煽情用语，数模论文严禁出现"),
    (r"国家工业示范(工况)?", "未经国家权威机构认定的虚假拔高，应替换为'优选推荐工况'"),
    (r"工业使命", "煽情拟人修辞，应替换为'工业应用需求'或'工程优化目标'"),
    (r"遥遥领先", "商业营销词汇，学术论文严禁使用"),
    (r"神级表现|毫无悬念|大获全胜", "非学术口语化夸张"),
    (r"完美无瑕|举世瞩目|绝对正确", "违背科研审慎原则的绝对化论调"),
    # AI-flavor anti-patterns (去AI味核心拦截规则)
    (r"(只是|仅是|仅仅是)[^。！？\n]{0,60}?(不能|无法|不可)[^。！？\n]{0,60}?(只是|仅是|仅仅是)[^。！？\n]{0,60}?(还是|必须|仍需|要看)", "AI免责声明模板：'只是…不能…只是…最终还是要'三重套娃免责零判断，应明确界定先验数理边界与加点指导作用"),
    (r"需要注意的是，?(这个|该|本)?方案只是", "AI免责套娃开场白，应直接陈述先验区间的数理定义与靶向设计目标"),
    (r"不能代替全空间的全面估计", "AI免责套话，应改为明确聚焦的核心高收率温区及其排除理由"),
    (r"(总的来说|综上所述|总体而言)，?(这个|该|本|这一)?(设计|模型|方案|架构|算法)", "AI总结段模板：'总的来说'开场+无信息增量复述，应删除或改为定量容差指标与决策执行指令"),
    (r"(可以考虑|不妨考虑|或许可以|可酌情考虑)(用|采用|将|作为|替换|引入)", "模糊建议词：决策规则里'可以考虑'不敢下结论，应改为确定性判定动作（如'判定采纳/执行工艺切换'）"),
    (r"(说明|表明|显示)可能(存在|有|是|会导致)?", "两头占推脱式表达：'说明可能'既想下结论又留余地，应给出确切物理判定或明确异常预案（如'判定存在…触发预案…'）"),
]

# 2. Known stale numbers or conflicting values (historical errata check)
STALE_NUMBER_PATTERNS = [
    (r"A3.*?(?:450|450\.0).*?28\.1[67]%", "A3 在 450℃ 真实收率为 43.12% (86.41%×49.90%)，误写为 28.17% 会与拟合系数 b1=6.2713 产生直接代数矛盾！"),
    (r"28\.1[67]%.*?A3.*?(?:450|450\.0)", "A3 在 450℃ 真实收率为 43.12%，严禁残留 28.17% 历史笔误！"),
]

# 3. Decision threshold sourcing requirements
REQUIRED_THRESHOLD_GROUNDINGS = [
    {
        "threshold_pattern": r"1\.86%",
        "name": "±1.86% 判据",
        "required_context_keywords": ["纯误差", "重复", "标准差", "方差", "自由度", "df", "1.96", "置信", "正态"],
        "err_msg": "出现判据 ±1.86%，但未在临近上下文交代其数理统计来源（来自中心点重复实验纯误差标准差 s_rep ≈ 0.95% 的 95% 置信半宽 1.96*s_rep）！"
    },
    {
        "threshold_pattern": r"(?:≥|>=|不低于)\s*45(?:\.0)?%",
        "name": "≥45.0% 突破判据",
        "required_context_keywords": ["历史", "最大", "样本", "44.73", "超越", "突破", "上界"],
        "err_msg": "出现判据 ≥45.0%，但未交代其数理统计来源（历史实测全样本最大值 44.73% 的统计显著突破）！"
    },
    {
        "threshold_pattern": r"(?:≥|>=|不低于)\s*23(?:\.0)?%",
        "name": "≥23.0% 低温达标判据",
        "required_context_keywords": ["帕累托", "Pareto", "理论", "上限", "极值", "23.41", "前沿"],
        "err_msg": "出现判据 ≥23.0%，但未交代其数理统计来源（相对问题三严苛低温约束下 Pareto 理论上限 23.41% 的 98% 达成率）！"
    }
]

def check_inequality_consistency(text):
    """
    Scans and asserts all inequality chains like:
    val1% < val2% < val3% or val1% > val2% > val3%
    Detects reversed inequalities such as 60.47% < 36.80% < 67.88%.
    """
    errors = []
    # Pattern for inequality comparisons containing numbers/percentages
    # e.g., 60.47% < 36.80% or (60.47%) < (36.80%)
    ineq_regex = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*\)?\s*(<|>|≤|≥|\\le|\\ge)\s*\(?\s*(\d+(?:\.\d+)?)\s*%", re.IGNORECASE)
    
    for line_idx, line in enumerate(text.splitlines(), 1):
        for m in ineq_regex.finditer(line):
            v1_str, op, v2_str = m.group(1), m.group(2), m.group(3)
            v1 = float(v1_str)
            v2 = float(v2_str)
            
            is_valid = True
            if op in ('<', '≤', '\\le') and not (v1 <= v2):
                is_valid = False
            elif op in ('>', '≥', '\\ge') and not (v1 >= v2):
                is_valid = False
                
            if not is_valid:
                errors.append({
                    "line": line_idx,
                    "snippet": line.strip()[:100],
                    "claim": f"{v1}% {op} {v2}%",
                    "reason": f"数值逻辑自相矛盾：{v1} 与 {v2} 的实际大小关系不符合关系符 '{op}'！"
                })
    return errors

def check_stale_and_formula_consistency(text):
    """
    Checks for conflicting or stale numbers and algebraic derivations.
    """
    errors = []
    for pat, explanation in STALE_NUMBER_PATTERNS:
        for m in re.finditer(pat, text, re.IGNORECASE | re.DOTALL):
            errors.append({
                "pattern": pat,
                "reason": explanation,
                "snippet": text[max(0, m.start() - 50):min(len(text), m.end() + 50)].replace('\n', ' ')
            })
            
    # Check A3 450C quadratic regression coefficient consistency
    # If b1 = 6.2713 appears, 43.12% must be present in the paper
    if "6.2713" in text and "-3.538" in text:
        if "43.12" not in text and "43.118" not in text:
            errors.append({
                "pattern": "b1=6.2713, b2=-3.5380",
                "reason": "回归方程包含系数 b1=6.2713 与 b2=-3.5380，该系数由 A3 450℃ 实测 43.12% 严格计算得到，但正文中未见 43.12% 实测数据锚点！",
                "snippet": "b1 = 6.2713 ... b2 = -3.5380"
            })
    return errors

def check_doe_table_integrity(text):
    """
    Verifies that experimental matrix parameters are not inverted or swapped.
    Specifically:
    Exp-1~Exp-4 (A3 series) must have flow rate 0.90 mL/min (not 1.68).
    Exp-5 (A2 series) must have flow rate 1.68 mL/min (not 0.90).
    """
    errors = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, 1):
        if "Exp-1" in line or "Exp-2" in line or "Exp-3" in line or "Exp-4" in line:
            if "1.68" in line and ("A3" in line or "1wt%" in line or "200mg" in line):
                errors.append({
                    "line": idx,
                    "snippet": line.strip(),
                    "reason": "DoE 表格参数颠倒：Exp-1~Exp-4 (A3 体系) 的乙醇流速应为 0.90 mL/min，误写为 1.68 mL/min！"
                })
        if "Exp-5" in line and ("A2" in line or "0.90" in line):
            if "0.90" in line and "A2" in line:
                errors.append({
                    "line": idx,
                    "snippet": line.strip(),
                    "reason": "DoE 表格参数颠倒：Exp-5 (A2 体系) 的乙醇流速应为 1.68 mL/min，误写为 0.90 mL/min！"
                })
    return errors

def check_decision_threshold_grounding(text):
    """
    Ensures that every hard decision threshold has statistical provenance
    explained in its surrounding context (within 500 characters).
    """
    errors = []
    for item in REQUIRED_THRESHOLD_GROUNDINGS:
        pat = item["threshold_pattern"]
        for m in re.finditer(pat, text):
            start = max(0, m.start() - 400)
            end = min(len(text), m.end() + 400)
            window = text[start:end]
            
            # Check if any required grounding keyword is present in window
            has_grounding = any(kw in window for kw in item["required_context_keywords"])
            if not has_grounding:
                errors.append({
                    "threshold": item["name"],
                    "reason": item["err_msg"],
                    "snippet": window[:120].replace('\n', ' ')
                })
                break # Report once per threshold type
    return errors

def check_extrapolation_vs_empirical_truth(text):
    """
    Ensures that model extrapolation (e.g. T*=422.2C, Y*=47.51%) is explicitly
    framed as a heuristic prior / exploration guidance, rather than a definitive
    untested industrial truth.
    """
    errors = []
    heuristic_keywords = ["先验", "探索", "启发", "引导", "指导", "实测为准", "待实测", "外推", "验证", "预测", "理论"]
    
    for pat in [r"422\.2", r"422\.16"]:
        for m in re.finditer(pat, text):
            start = max(0, m.start() - 350)
            end = min(len(text), m.end() + 350)
            window = text[start:end]
            
            has_prior_claim = any(kw in window for kw in heuristic_keywords)
            if not has_prior_claim:
                errors.append({
                    "item": "T*=422.2℃ 外推极值点",
                    "reason": "文中提及 422.2℃ 极值推演，但未在邻近上下文明确声明其为'探索性先验导向'，存在与'实测为准铁律'脱节的张力风险！",
                    "snippet": window[:120].replace('\n', ' ')
                })
                break
    return errors

def check_academic_restraint(text):
    """
    Scans for hype slogans and emotional or promotional language.
    """
    errors = []
    for pat, explanation in HYPE_BLACKLIST:
        for m in re.finditer(pat, text):
            errors.append({
                "phrase": m.group(0),
                "reason": explanation,
                "snippet": text[max(0, m.start() - 30):min(len(text), m.end() + 30)].replace('\n', ' ')
            })
    return errors

def run_rigor_audit(filepath):
    print("=" * 70)
    print(f"  PAPER RIGOR & DATA-FORMULA INTEGRITY AUDIT")
    print(f"  Target: {filepath}")
    print("=" * 70)
    
    if not os.path.exists(filepath):
        print(f"[FATAL] Target file not found: {filepath}")
        return 1
        
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
        
    all_passed = True
    
    # 1. Inequalities
    ineq_errors = check_inequality_consistency(text)
    if ineq_errors:
        all_passed = False
        print(f"\n[FAIL] Dimension 1: 不等式方向自相矛盾 ({len(ineq_errors)} 处错误):")
        for err in ineq_errors:
            print(f"  - 第 {err['line']} 行: '{err['claim']}' -> {err['reason']}")
            print(f"    代码片段: {err['snippet']}")
    else:
        print("\n[PASS] Dimension 1: 不等式方向与数值逻辑 100% 吻合")

    # 2. Formula & Stale Numbers
    formula_errors = check_stale_and_formula_consistency(text)
    if formula_errors:
        all_passed = False
        print(f"\n[FAIL] Dimension 2: 正文数据与公式系数脱节/历史笔误 ({len(formula_errors)} 处错误):")
        for err in formula_errors:
            print(f"  - 原因: {err['reason']}")
            print(f"    片段: {err['snippet']}")
    else:
        print("[PASS] Dimension 2: 正文数值与公式系数三位一体严格对齐")

    # 3. DoE Table Matrix
    doe_errors = check_doe_table_integrity(text)
    if doe_errors:
        all_passed = False
        print(f"\n[FAIL] Dimension 3: DoE 表格背景参数颠倒 ({len(doe_errors)} 处错误):")
        for err in doe_errors:
            print(f"  - 第 {err['line']} 行: {err['reason']}")
            print(f"    行内容: {err['snippet']}")
    else:
        print("[PASS] Dimension 3: 实验设计表格工况参数严格继承，无行颠倒")

    # 4. Threshold Grounding
    thresh_errors = check_decision_threshold_grounding(text)
    if thresh_errors:
        all_passed = False
        print(f"\n[FAIL] Dimension 4: 决策硬阈值缺乏统计学来源 ({len(thresh_errors)} 处错误):")
        for err in thresh_errors:
            print(f"  - 阈值: {err['threshold']} -> {err['reason']}")
            print(f"    片段: {err['snippet']}")
    else:
        print("[PASS] Dimension 4: 自适应决策树硬阈值均具备明确的纯误差/自由度/置信度来源")

    # 5. Extrapolation vs Empirical Truth
    extrap_errors = check_extrapolation_vs_empirical_truth(text)
    if extrap_errors:
        all_passed = False
        print(f"\n[FAIL] Dimension 5: 模型推演外推与实测真值张力 ({len(extrap_errors)} 处错误):")
        for err in extrap_errors:
            print(f"  - {err['item']}: {err['reason']}")
            print(f"    片段: {err['snippet']}")
    else:
        print("[PASS] Dimension 5: 模型推演极值点已清晰定义为先验导向，坚守实测为准铁律")

    # 6. Academic Restraint
    hype_errors = check_academic_restraint(text)
    if hype_errors:
        all_passed = False
        print(f"\n[FAIL] Dimension 6: 学术文风欠克制/口号化词汇 ({len(hype_errors)} 处错误):")
        for err in hype_errors:
            print(f"  - 命中违禁词: '{err['phrase']}' -> {err['reason']}")
            print(f"    片段: {err['snippet']}")
    else:
        print("[PASS] Dimension 6: 学术文风冷静客观，零煽情口号词汇")

    print("\n" + "=" * 70)
    if all_passed:
        print("  ALL RIGOR AUDIT GATES PASSED! Paper is robust, verified & contest-ready.")
        print("=" * 70)
        return 0
    else:
        print("  RIGOR AUDIT FAILED! Please fix the reported inconsistencies above.")
        print("=" * 70)
        return 1

def main():
    parser = argparse.ArgumentParser(description="Audit mathematical modeling paper for rigor, consistency and restraint.")
    parser.add_argument("--file", default="paper/master/full_paper.md", help="Path to markdown paper file to audit")
    args = parser.parse_args()
    
    code = run_rigor_audit(args.file)
    sys.exit(code)

if __name__ == "__main__":
    main()
