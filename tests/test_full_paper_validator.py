from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "plugins/math-modeling-workflow/skills/full-paper-assembler/scripts/validate_full_paper.py"
)
SPEC = importlib.util.spec_from_file_location("validate_full_paper", SCRIPT)
vfp = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(vfp)

VALID = """
# 示例题
## 一、问题重述
## 二、问题分析
## 三、数据预处理
## 四、模型假设
## 五、符号说明
## 六、模型的建立与求解
### 6.1 问题一：模型
### 6.2 问题二：模型
## 七、模型检验
## 八、模型评价
## 参考文献
"""


class FullPaperStructureTest(unittest.TestCase):
    def test_valid_outline_passes(self):
        self.assertEqual(vfp.validate(VALID, ["Q1", "Q2"]), [])

    def test_duplicate_global_heading_fails(self):
        errors = vfp.validate(VALID + "\n## 一、问题重述\n", ["Q1", "Q2"])
        self.assertTrue(any("occurs 2 times" in e for e in errors))

    def test_question_section_must_appear_once(self):
        errors = vfp.validate(VALID, ["Q1", "Q2", "Q3"])
        self.assertTrue(any("Q3" in e for e in errors))

    def test_global_chapter_restart_inside_model_block(self):
        bad = VALID.replace("### 6.2 问题二：模型", "### 6.2 问题二：模型\n## 一、问题重述")
        errors = vfp.validate(bad, ["Q1", "Q2"])
        self.assertTrue(any("restarts inside" in e for e in errors))

    def test_manifest_unique_target_sections(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "assembly_manifest.json"
            manifest.write_text(json.dumps({
                "paper_scope": "full_submission",
                "questions": ["Q1", "Q2"],
                "question_mapping": {
                    "Q1": {"target_section": "6.1"},
                    "Q2": {"target_section": "6.1"},
                },
            }), encoding="utf-8")
            errors = vfp.validate_manifest(manifest, ["Q1", "Q2"])
            self.assertTrue(any("not unique" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
