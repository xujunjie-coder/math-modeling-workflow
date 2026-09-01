from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


GLOBAL_HEADINGS = [
    "问题重述",
    "问题分析",
    "数据预处理",
    "模型假设",
    "符号说明",
    "模型的建立与求解",
    "模型检验",
    "模型评价",
    "参考文献",
]


def read_text(path: Path) -> str:
    if path.suffix.lower() in {".md", ".txt", ".tex"}:
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        return "\n".join(
            "".join(node.text or "" for node in paragraph.findall(".//w:t", ns))
            for paragraph in root.findall(".//w:body/w:p", ns)
        )
    raise ValueError(f"unsupported paper format: {path.suffix}")


def count_heading(text: str, keyword: str) -> int:
    pattern = re.compile(
        rf"(?m)^\s*(?:#+\s*)?(?:[一二三四五六七八九十]+、|\d+(?:\.\d+)*\s*)?{re.escape(keyword)}[^\n]*$"
    )
    return len(pattern.findall(text))


def validate(text: str, questions: list[str]) -> list[str]:
    errors: list[str] = []
    for heading in GLOBAL_HEADINGS:
        count = count_heading(text, heading)
        if count != 1:
            errors.append(f"global heading '{heading}' occurs {count} times; expected 1")

    for index, question in enumerate(questions, start=1):
        number = question[1:] if question.upper().startswith("Q") else str(index)
        patterns = [
            rf"(?m)^\s*(?:#+\s*)?6\.{number}\s+.*$",
            rf"(?m)^\s*(?:#+\s*)?6\.{index}\s+.*问题[一二三四五六七八九十{number}].*$",
        ]
        count = max(len(re.findall(pattern, text)) for pattern in patterns)
        if count != 1:
            errors.append(f"{question} model section occurs {count} times; expected 1")

    model_start = re.search(r"(?m)^.*模型的建立与求解.*$", text)
    validation_start = re.search(r"(?m)^.*模型检验.*$", text)
    if model_start and validation_start and model_start.end() < validation_start.start():
        model_block = text[model_start.end() : validation_start.start()]
        restarted = re.findall(r"(?m)^\s*(?:#+\s*)?[一二三四五六七八九十]+、\s*(?:问题重述|问题分析|数据预处理|模型假设)", model_block)
        if restarted:
            errors.append("a global chapter restarts inside the model/solution chapter")
    return errors


def validate_manifest(path: Path, questions: list[str]) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("paper_scope") != "full_submission":
        errors.append("manifest paper_scope must be 'full_submission'")
    if data.get("questions") != questions:
        errors.append("manifest questions do not match requested questions")
    mapping = data.get("question_mapping", {})
    targets = []
    for question in questions:
        if question not in mapping:
            errors.append(f"manifest missing question_mapping for {question}")
            continue
        target = mapping[question].get("target_section")
        if not target:
            errors.append(f"manifest missing target_section for {question}")
        targets.append(target)
    if len(targets) != len(set(targets)):
        errors.append("manifest target sections are not unique")
    return errors


def self_test() -> int:
    valid = """
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
    invalid = valid + "\n## 一、问题重述\n"
    if validate(valid, ["Q1", "Q2"]):
        print("self-test failed: valid fixture rejected", file=sys.stderr)
        return 1
    if not validate(invalid, ["Q1", "Q2"]):
        print("self-test failed: invalid fixture accepted", file=sys.stderr)
        return 1
    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate full mathematical-modeling paper assembly structure.")
    parser.add_argument("paper", nargs="?", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--questions", default="Q1,Q2,Q3,Q4")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.paper:
        parser.error("paper is required unless --self-test is used")
    questions = [item.strip() for item in args.questions.split(",") if item.strip()]
    errors = validate(read_text(args.paper), questions)
    if args.manifest:
        errors.extend(validate_manifest(args.manifest, questions))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: full-paper assembly structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
