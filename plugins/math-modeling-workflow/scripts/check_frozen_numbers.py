#!/usr/bin/env python3
"""Numerical-consistency linter for mathematical-modeling papers.

The workflow requires every numerical paper claim to trace to a frozen value
(``frozen_numbers.json``) or a saved metrics artifact. The auditor Skills check
this semantically; this script checks it *mechanically* and deterministically:

1. collect every authorized number from frozen/metrics JSON;
2. extract every number token from the paper (``.md``/``.txt``/``.docx``),
   skipping section/figure/equation numbers, years, code spans, URLs and math;
3. flag any claim number that is neither an authorized value (after exact
   normalization), a near-match (rounding warning), nor explicitly ignored.

Exit code 1 when at least one UNFROZEN claim number is found. Standard library
only. Number extraction/normalization are pure functions so they are unit
testable without files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET

# A number with thousands separators, decimals, optional exponent, optional %.
# The plain branch keeps every dotted segment so identifiers like 3.2.1 stay one
# token; Decimal normalization then rejects multi-dot ids instead of leaking a
# trailing "1".
NUMBER_RE = re.compile(
    r"\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:[eE][+-]?\d+)?%?|\d+(?:\.\d+)*(?:[eE][+-]?\d+)?%?"
)
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
URL_RE = re.compile(r"(?:https?://|www\.)\S+|!\[[^\]]*\]\([^)]*\)|\[[^\]]*\]\((?:https?://|file:)[^)]*\)")
DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$", re.DOTALL)
INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)[^\n$]+\$")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")

# A label that ENDS immediately before a number (only whitespace between) marks
# the number as figure/table/equation/step numbering, e.g. 图3, Fig. 4, 式(5).
ADJACENT_LABEL_RE = re.compile(
    r"(?:图|表|式|公式|步骤|节|章|第[一二三四五六七八九十0-9]+[章节步]?|"
    r"fig\.?|figure|table|eq(?:uation)?\.?|section|step|phase|stage)[\s(（]*$",
    re.IGNORECASE,
)
# Dotted ids such as 6.1, 3.2.1 are section/numbering when in a heading or
# directly after a label.
DOTTED_ID_RE = re.compile(r"^\d+(?:\.\d+)+$")
YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")
QID_RE = re.compile(r"^Q\d+(?:_sub\d+)?$", re.IGNORECASE)
ASCII_LETTER = re.compile(r"[A-Za-z]")

DEFAULT_NEAR_RTOL = Decimal("0.01")  # within 1% -> rounding warning, not a hard fail


@dataclass(frozen=True)
class Token:
    line: int
    raw: str
    value: Decimal
    is_percent: bool
    context: str


@dataclass
class Finding:
    kind: str  # MATCH | NEAR | UNFROZEN | IGNORED
    token: Token
    detail: str = ""


# --------------------------------------------------------------------------- #
# Pure normalization / extraction
# --------------------------------------------------------------------------- #
def normalize(raw: str) -> Decimal | None:
    """Normalize a raw number token to an exact Decimal (thousands, exponent)."""
    text = raw.strip().rstrip("%").replace(",", "")
    try:
        value = Decimal(text)
    except InvalidOperation:
        return None
    return value.normalize()


def strip_non_claim_text(text: str, keep_math: bool = False) -> list[tuple[int, str]]:
    """Remove code/URL/math regions; return (line_number, line) pairs.

    Removed spans are replaced with spaces so remaining line numbers and column
    positions stay aligned with the source.
    """
    def blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = FENCED_CODE_RE.sub(blank, text)
    text = INLINE_CODE_RE.sub(blank, text)
    text = URL_RE.sub(blank, text)
    if not keep_math:
        text = DISPLAY_MATH_RE.sub(blank, text)
        text = INLINE_MATH_RE.sub(blank, text)
    return [(index, line) for index, line in enumerate(text.splitlines(), start=1)]


def is_structural_number(raw: str, line: str, start: int, end: int, extra_years: set[str]) -> bool:
    """Decide whether a token is numbering/identifier/setup rather than a claim."""
    core = raw.rstrip("%")
    if YEAR_RE.match(core) and core not in extra_years:
        return True
    if QID_RE.match(core):
        return True
    # A number glued to an ASCII letter is part of an identifier (Top10, fold5, x1).
    before = line[start - 1] if start > 0 else " "
    after = line[end] if end < len(line) else " "
    if ASCII_LETTER.match(before) or ASCII_LETTER.match(after):
        return True
    # A perturbation setting such as ±5% is experiment design, not a result.
    if raw.endswith("%") and "±" in line[max(0, start - 3):start]:
        return True
    if DOTTED_ID_RE.match(core) and (
        HEADING_RE.match(line) or ADJACENT_LABEL_RE.search(line[max(0, start - 8):start])
    ):
        return True
    # Label must END right next to the number (图3, Fig. 4, 式(5)); a wide gap
    # means the number is a later result on the same line and stays a claim.
    adjacent = line[max(0, start - 8):start]
    if ADJACENT_LABEL_RE.search(adjacent):
        return True
    return False


def extract_paper_numbers(text: str, keep_math: bool = False, extra_years: set[str] | None = None) -> list[Token]:
    extra_years = extra_years or set()
    tokens: list[Token] = []
    for line_no, line in strip_non_claim_text(text, keep_math=keep_math):
        for match in NUMBER_RE.finditer(line):
            raw = match.group(0)
            if is_structural_number(raw, line, match.start(), match.end(), extra_years):
                continue
            value = normalize(raw)
            if value is None:
                continue
            tokens.append(
                Token(
                    line=line_no,
                    raw=raw,
                    value=value,
                    is_percent=raw.endswith("%"),
                    context=line.strip()[:120],
                )
            )
    return tokens


def iter_json_numbers(node: Any):  # noqa: ANN401 - recursively walk arbitrary JSON
    if isinstance(node, bool):  # bool is an int subclass; never a claim number
        return
    if isinstance(node, (int, float)):
        yield Decimal(str(node)).normalize()
    elif isinstance(node, str):
        parsed = normalize(node)
        if parsed is not None:
            yield parsed
    elif isinstance(node, dict):
        for key, value in node.items():
            # Keys like "2026" are identifiers, not values.
            yield from iter_json_numbers(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_json_numbers(item)


def collect_authorized(paths: list[Path]) -> dict[Decimal, list[str]]:
    """Map every authorized numeric value to the source files it came from."""
    authorized: dict[Decimal, list[str]] = {}
    for path in paths:
        if path.is_dir():
            files = sorted([*path.rglob("*.json")])
        else:
            files = [path]
        for file in files:
            try:
                doc = json.loads(file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            # frozen_numbers.json may wrap entries under numbers/claims/values.
            if isinstance(doc, dict) and any(k in doc for k in ("numbers", "claims", "values", "entries")):
                for key in ("numbers", "claims", "values", "entries"):
                    if key in doc:
                        for value in iter_json_numbers(doc[key]):
                            authorized.setdefault(value.normalize(), []).append(str(file))
                continue
            for value in iter_json_numbers(doc):
                authorized.setdefault(value.normalize(), []).append(str(file))
    return authorized


def load_ignores(path: Path | None) -> tuple[set[str], list[re.Pattern[str]]]:
    literals: set[str] = set()
    patterns: list[re.Pattern[str]] = []
    if not path or not path.exists():
        return literals, patterns
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("regex:"):
            patterns.append(re.compile(line[6:].strip()))
        else:
            literals.add(line.replace(",", "").rstrip("%"))
    return literals, patterns


def nearest_authorized(value: Decimal, authorized: dict[Decimal, list[str]], rtol: Decimal) -> Decimal | None:
    best: Decimal | None = None
    best_gap: Decimal | None = None
    for candidate in authorized:
        if candidate == 0:
            gap = abs(value)
        else:
            gap = abs(value - candidate) / abs(candidate)
        if best_gap is None or gap < best_gap:
            best_gap, best = gap, candidate
    if best is not None and best_gap is not None and best_gap <= rtol and best != value:
        return best
    return None


def classify_tokens(
    tokens: list[Token],
    authorized: dict[Decimal, list[str]],
    ignore_literals: set[str],
    ignore_patterns: list[re.Pattern[str]],
    near_rtol: Decimal,
) -> list[Finding]:
    findings: list[Finding] = []
    for token in tokens:
        normalized_text = format(token.value, "f")
        ignored = normalized_text in ignore_literals or any(p.search(token.raw) for p in ignore_patterns)
        if ignored:
            findings.append(Finding("IGNORED", token))
            continue
        if token.value in authorized:
            findings.append(Finding("MATCH", token, ", ".join(sorted(set(authorized[token.value])))))
            continue
        near = nearest_authorized(token.value, authorized, near_rtol)
        if near is not None:
            findings.append(
                Finding("NEAR", token, f"closest frozen value {near} (rounding? register display value or ignore)")
            )
        else:
            findings.append(Finding("UNFROZEN", token, "no matching frozen/metrics value"))
    return findings


# --------------------------------------------------------------------------- #
# Paper IO
# --------------------------------------------------------------------------- #
def read_paper(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".tex"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        return "\n".join(
            "".join(node.text or "" for node in paragraph.findall(".//w:t", ns))
            for paragraph in root.findall(".//w:body/w:p", ns)
        )
    raise ValueError(f"unsupported paper format: {suffix}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def format_report(findings: list[Finding], authorized: dict[Decimal, list[str]], used: set[Decimal]) -> str:
    buckets = {kind: [f for f in findings if f.kind == kind] for kind in ("MATCH", "NEAR", "UNFROZEN", "IGNORED")}
    lines = [
        f"scanned claim numbers: {len(findings)}",
        f"  MATCH {len(buckets['MATCH'])}   NEAR {len(buckets['NEAR'])}   "
        f"UNFROZEN {len(buckets['UNFROZEN'])}   IGNORED {len(buckets['IGNORED'])}",
        f"authorized distinct values: {len(authorized)}; cited in paper: {len(used)}",
    ]
    if buckets["UNFROZEN"]:
        lines.append("\nUNFROZEN (paper numbers absent from frozen/metrics evidence):")
        for finding in buckets["UNFROZEN"]:
            lines.append(f"  L{finding.token.line:<4} {finding.token.raw:<12} | {finding.token.context}")
    if buckets["NEAR"]:
        lines.append("\nNEAR (not exact; likely rounding — confirm or register the display value):")
        for finding in buckets["NEAR"]:
            lines.append(f"  L{finding.token.line:<4} {finding.token.raw:<12} {finding.detail}")
    unused = sorted(set(authorized) - used)
    if unused:
        lines.append(f"\nUNUSED frozen values not cited in paper ({len(unused)}):")
        lines.append("  " + ", ".join(format(v, "g") for v in unused[:30]) + (" ..." if len(unused) > 30 else ""))
    if not buckets["UNFROZEN"]:
        lines.append("\nPASS: every claim number resolves to frozen/metrics evidence (or an explicit ignore).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper", type=Path, help="Paper file (.md/.txt/.tex/.docx)")
    parser.add_argument(
        "--source",
        type=Path,
        action="append",
        required=True,
        help="Authorized number source: frozen_numbers.json / metrics JSON, or a directory (repeatable)",
    )
    parser.add_argument("--ignore-file", type=Path, help="Sidecar .frozenignore: literal values or regex:... lines")
    parser.add_argument("--keep-math", action="store_true", help="Also scan numbers inside $...$ math regions")
    parser.add_argument("--near-rtol", type=Decimal, default=DEFAULT_NEAR_RTOL, help="Relative tolerance for NEAR warnings")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    if not args.paper.exists():
        print(f"paper not found: {args.paper}", file=sys.stderr)
        return 2
    authorized = collect_authorized(args.source)
    if not authorized:
        print("no authorized numbers found in --source inputs", file=sys.stderr)
        return 2
    ignore_literals, ignore_patterns = load_ignores(args.ignore_file)
    text = read_paper(args.paper)
    tokens = extract_paper_numbers(text, keep_math=args.keep_math)
    findings = classify_tokens(tokens, authorized, ignore_literals, ignore_patterns, args.near_rtol)
    used = {f.token.value for f in findings if f.kind == "MATCH"}

    if args.json:
        payload = {
            "counts": {kind: sum(1 for f in findings if f.kind == kind) for kind in ("MATCH", "NEAR", "UNFROZEN", "IGNORED")},
            "unfrozen": [
                {"line": f.token.line, "raw": f.token.raw, "context": f.token.context}
                for f in findings if f.kind == "UNFROZEN"
            ],
            "near": [
                {"line": f.token.line, "raw": f.token.raw, "detail": f.detail}
                for f in findings if f.kind == "NEAR"
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_report(findings, authorized, used))
    return 1 if any(f.kind == "UNFROZEN" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
