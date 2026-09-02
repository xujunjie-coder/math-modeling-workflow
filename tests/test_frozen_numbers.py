from __future__ import annotations

import importlib.util
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/math-modeling-workflow/scripts/check_frozen_numbers.py"
SPEC = importlib.util.spec_from_file_location("check_frozen_numbers", SCRIPT)
cfn = importlib.util.module_from_spec(SPEC)
sys.modules["check_frozen_numbers"] = cfn
assert SPEC and SPEC.loader
SPEC.loader.exec_module(cfn)


class NormalizeTest(unittest.TestCase):
    def test_thousands_and_trailing_zeros(self):
        self.assertEqual(cfn.normalize("1,234.50"), Decimal("1234.5"))
        self.assertEqual(cfn.normalize("42.0"), Decimal("42"))
        self.assertEqual(cfn.normalize("2e-3"), Decimal("0.002"))
        self.assertEqual(cfn.normalize("88%"), Decimal("88"))
        self.assertIsNone(cfn.normalize("3.2.1"))

    def test_extract_skips_structural_numbers(self):
        paper = (
            "## 6.1 结果\n"  # heading dotted id
            "RMSE 为 2.40，如图3所示，得分 0.912。\n"
            "Top10 重叠率 0.90，扰动 ±5%，年份 2026。\n"
            "代码 `x=0.123` 链接 https://x/0.999 公式 $a=0.456$。\n"
        )
        tokens = {t.raw for t in cfn.extract_paper_numbers(paper)}
        self.assertIn("2.40", tokens)
        self.assertIn("0.912", tokens)  # result after a label is not swallowed
        self.assertIn("0.90", tokens)
        self.assertNotIn("6.1", tokens)
        self.assertNotIn("3", tokens)          # 图3 numbering
        self.assertNotIn("10", tokens)         # Top10 identifier
        self.assertNotIn("5%", tokens)         # ± perturbation setting
        self.assertNotIn("2026", tokens)       # year
        self.assertNotIn("0.123", tokens)      # inline code
        self.assertNotIn("0.999", tokens)      # url
        self.assertNotIn("0.456", tokens)      # inline math

    def test_keep_math_flag(self):
        tokens = {t.raw for t in cfn.extract_paper_numbers("公式 $a=0.456$。", keep_math=True)}
        self.assertIn("0.456", tokens)


class ClassifyTest(unittest.TestCase):
    def setUp(self):
        self.authorized = {
            Decimal("2.4"): ["frozen"],
            Decimal("0.912"): ["frozen"],
            Decimal("0.8832"): ["frozen"],
        }

    def _tokens(self, text):
        return cfn.extract_paper_numbers(text)

    def test_match_near_unfrozen(self):
        tokens = self._tokens("精确 2.40，近似 0.883，编造 77.77。")
        findings = cfn.classify_tokens(tokens, self.authorized, set(), [], Decimal("0.01"))
        kinds = {f.token.raw: f.kind for f in findings}
        self.assertEqual(kinds["2.40"], "MATCH")
        self.assertEqual(kinds["0.883"], "NEAR")
        self.assertEqual(kinds["77.77"], "UNFROZEN")

    def test_explicit_ignore(self):
        tokens = self._tokens("设定参数 512，结果 2.4。")
        findings = cfn.classify_tokens(tokens, self.authorized, {"512"}, [], Decimal("0.01"))
        kinds = {f.token.raw: f.kind for f in findings}
        self.assertEqual(kinds["512"], "IGNORED")
        self.assertEqual(kinds["2.4"], "MATCH")

    def test_collect_authorized_wrapped_and_nested(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            frozen = Path(tmp) / "frozen.json"
            frozen.write_text(json.dumps({"numbers": [{"value": 2.4}, {"value": 0.912}]}), encoding="utf-8")
            metrics = Path(tmp) / "metrics.json"
            metrics.write_text(json.dumps({"outer": {"n": 420}, "flag": True}), encoding="utf-8")
            values = cfn.collect_authorized([frozen, metrics])
            self.assertIn(Decimal("2.4"), values)
            self.assertIn(Decimal("0.912"), values)
            self.assertIn(Decimal("420"), values)
            self.assertNotIn(Decimal("1"), values)  # bool must not count as a number


if __name__ == "__main__":
    unittest.main()
