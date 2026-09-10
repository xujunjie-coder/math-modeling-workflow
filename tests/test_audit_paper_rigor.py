#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_audit_paper_rigor.py
-------------------------
Unit tests for the 10-dimension paper rigor, consistency, and gatekeeping auditor.
Specifically tests avoidance of the 4 key real contest failure modes:
1. Parameter Range vs Concrete Instance Consistency (Dimension 7)
2. Cross-Table Benchmark Value Consistency (Dimension 8)
3. Scholar Citation & Bibliography Cross-Lock (Dimension 9)
4. Uncited Fabricated Specifics in Assumptions (Dimension 10)
5. Overstated Theoretical Claims in Academic Restraint (Dimension 6)
"""

import unittest
from pathlib import Path
import sys

# Add plugins path
PLUGIN_SCRIPTS = Path(__file__).resolve().parent.parent / "plugins" / "math-modeling-workflow" / "scripts"
if str(PLUGIN_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PLUGIN_SCRIPTS))

from audit_paper_rigor import (
    check_parameter_range_and_instance_consistency,
    check_benchmark_cross_table_consistency,
    check_citation_cross_consistency,
    check_uncited_fabricated_specifics,
    check_academic_restraint,
)


class TestAuditPaperRigor(unittest.TestCase):

    def test_parameter_range_conflict_detected(self):
        """Detects when concrete parameter (e.g. 0.40) breaches declared range [0.10, 0.35]."""
        bad_text = (
            "自身需求价格弹性响应系数 \\beta_i \\in [0.10, 0.35] (主粮为 0.10, 蔬菜为 0.20)。\n"
            "后文具体标定: \\beta_{fungi} = 0.40。"
        )
        errors = check_parameter_range_and_instance_consistency(bad_text)
        self.assertTrue(len(errors) > 0)
        self.assertIn("0.40", errors[0]["reason"])

    def test_parameter_range_valid_passes(self):
        """Passes when all concrete parameters reside within declared range [0.10, 0.40]."""
        good_text = (
            "自身需求价格弹性响应系数 \\beta_i \\in [0.10, 0.40] (主粮为 0.12, 蔬菜为 0.25)。\n"
            "后文具体标定: \\beta_{fungi} = 0.40, \\beta_{grain} = 0.12。"
        )
        errors = check_parameter_range_and_instance_consistency(good_text)
        self.assertEqual(len(errors), 0)

    def test_cross_table_benchmark_mismatch_detected(self):
        """Detects when Q2 M=50 benchmark expected profit differs between abstract/main table and SAA table."""
        bad_text = (
            "在置信水平 0.90 下，求得 2024~2030 年期望净利润为 43,021,046.19 元。\n"
            "| M = 50 (基准) | 42,721,685.91 | 6.72% |"
        )
        errors = check_benchmark_cross_table_consistency(bad_text)
        self.assertTrue(len(errors) > 0)
        self.assertIn("基准情景跨表数值自相矛盾", errors[0]["reason"])

    def test_citation_cross_lock_missing_author_detected(self):
        """Detects when a scholar (e.g. 黄季焜) is cited in text but missing in bibliography."""
        bad_text = (
            "根据黄季焜等在中国农产品供求弹性领域的计量实证研究，主粮弹性较小。\n"
            "\\begin{thebibliography}{99}\n"
            "\\bibitem{ref1} 姜启源. 数学模型. 2018.\n"
            "\\bibitem{ref2} 司守奎. 数学建模算法与应用. 2021.\n"
            "\\end{thebibliography}"
        )
        errors = check_citation_cross_consistency(bad_text)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(errors[0]["scholar"], "黄季焜")

    def test_citation_cross_lock_present_author_passes(self):
        """Passes when the cited scholar exists in the bibliography."""
        good_text = (
            "根据黄季焜等在中国农产品供求弹性领域的计量实证研究，主粮弹性较小。\n"
            "\\begin{thebibliography}{99}\n"
            "\\bibitem{ref1} 黄季焜, 仇焕广. 中国农业发展与政策研究[M]. 2012.\n"
            "\\end{thebibliography}"
        )
        errors = check_citation_cross_consistency(good_text)
        self.assertEqual(len(errors), 0)

    def test_uncited_fabricated_specifics_in_assumptions_detected(self):
        """Detects ungrounded high-precision cost/loss figures in model assumptions."""
        bad_text = (
            "## 三、模型假设\n"
            "千吨级大型气调保鲜库建造成本超 300 万元，且制冷月度电费折合达 0.40 ~ 0.60 元/斤·月，"
            "常温与冷链周转月均损耗率达 8% ~ 12%。因此假定当季出清。\n"
            "## 四、符号说明"
        )
        errors = check_uncited_fabricated_specifics(bad_text)
        self.assertTrue(len(errors) > 0)
        self.assertIn("建造成本", errors[0]["item"])

    def test_uncited_fabricated_specifics_with_standards_passes(self):
        """Passes when specific figures in assumptions cite standards or literature."""
        good_text = (
            "## 三、模型假设\n"
            "根据国家标准《冷库设计标准》GB 50072 与农业农村部冷链物流行业通则，建造千吨级气调库建造成本超 300 万元 [1]。"
            "因此设定当季出清。\n"
            "## 四、符号说明"
        )
        errors = check_uncited_fabricated_specifics(good_text)
        self.assertEqual(len(errors), 0)

    def test_academic_restraint_theoretical_overstatement(self):
        """Detects exaggerated theoretical claims like '全球唯一均衡' and '理论保证全局收敛'."""
        bad_text1 = "快速单调收敛，理论保证全局内生唯一均衡。"
        errors1 = check_academic_restraint(bad_text1)
        self.assertTrue(len(errors1) > 0)

        bad_text2 = "证明了内生价格均衡点全局唯一且无局部多峰震荡。"
        errors2 = check_academic_restraint(bad_text2)
        self.assertTrue(len(errors2) > 0)


if __name__ == "__main__":
    unittest.main()
