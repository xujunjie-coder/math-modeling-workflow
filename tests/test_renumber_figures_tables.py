from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/math-modeling-workflow/scripts/renumber_figures_tables.py"
SPEC = importlib.util.spec_from_file_location("renumber_figures_tables", SCRIPT)
renumber_tool = importlib.util.module_from_spec(SPEC)
sys.modules["renumber_figures_tables"] = renumber_tool
assert SPEC and SPEC.loader
SPEC.loader.exec_module(renumber_tool)


class TestRenumberFiguresTables(unittest.TestCase):
    def test_renumber_captions_and_references(self):
        sample = """# 第四章 模型求解

## 4.1 数据分析
如图 1-1 所示，变量随时间递增。
通过上述图1-1可以得出主要变化规律。参见表1-1的数据统计。

![图1-1：风化指标随时间走势图](figures/fig1.png)

**表1-1 玻璃样本统计量汇总**
| 编号 | 均值 |
| --- | --- |
| 01 | 12.5 |

## 4.2 进一步分类
由图2-1可以看出分类界限明显。另外结合表2-1与表1-1进行比对。

![图2-1：聚类散点图](figures/fig2.png)

**表2-1 聚类中心坐标**
| 中心 | X | Y |
| --- | --- | --- |
"""
        renumbered, mapping = renumber_tool.renumber_text(sample)

        self.assertEqual(mapping.get("图1-1"), "图1")
        self.assertEqual(mapping.get("表1-1"), "表1")
        self.assertEqual(mapping.get("图2-1"), "图2")
        self.assertEqual(mapping.get("表2-1"), "表2")

        # Check caption replacement
        self.assertIn("![图1：风化指标随时间走势图](figures/fig1.png)", renumbered)
        self.assertIn("**表1 玻璃样本统计量汇总**", renumbered)
        self.assertIn("![图2：聚类散点图](figures/fig2.png)", renumbered)
        self.assertIn("**表2 聚类中心坐标**", renumbered)

        # Check in-text reference replacement
        self.assertIn("如图1", renumbered)
        self.assertIn("通过上述图1可以得出主要变化规律", renumbered)
        self.assertIn("参见表1的数据统计", renumbered)
        self.assertIn("由图2可以看出分类界限明显", renumbered)
        self.assertIn("结合表2与表1进行比对", renumbered)

    def test_cli_in_place(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "paper.md"
            file_path.write_text("通过图1-1可知。\n![图1-1](a.png)", encoding="utf-8")
            
            exit_code = renumber_tool.main([str(file_path), "--in-place"])
            self.assertEqual(exit_code, 0)
            
            content = file_path.read_text(encoding="utf-8")
            self.assertIn("通过图1可知", content)
            self.assertIn("![图1](a.png)", content)


if __name__ == "__main__":
    unittest.main()
