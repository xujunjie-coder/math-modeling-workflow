#!/usr/bin/env python3
"""Automated Figure and Table Renumbering Tool for Mathematical Modeling Papers.

Converts chapter-based numbers (e.g., 图1-1, 表1-1, 图2-1) into sequential
global numbers (e.g., 图1, 图2, 表1, 表2) in chronological order of appearance,
and synchronously updates all in-text cross-references without manual intervention.

Usage:
    python renumber_figures_tables.py <file.md> [--in-place] [--output <out.md>] [--json-map <map.json>]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Patterns to match chapter-based figure/table identifiers
# e.g., 图1-1, 图2-3, 图1.1, 表1-1, 表2-3, 表1.2
FIG_PATTERN = re.compile(r"图\s*([0-9]+[\-\.][0-9]+)")
TAB_PATTERN = re.compile(r"表\s*([0-9]+[\-\.][0-9]+)")


def extract_captions_and_order(text: str) -> tuple[dict[str, str], dict[str, str]]:
    """Extract distinct chapter-based figure and table IDs in order of first appearance."""
    fig_map: dict[str, str] = {}
    tab_map: dict[str, str] = {}
    
    fig_counter = 1
    tab_counter = 1

    # Match any occurrence of 图X-Y or 表X-Y in text
    token_pattern = re.compile(r"(图|表)\s*([0-9]+[\-\.][0-9]+)")
    for match in token_pattern.finditer(text):
        kind, num = match.group(1), match.group(2)
        normalized_old = f"{kind}{num.replace('.', '-')}"
        
        if kind == "图":
            if normalized_old not in fig_map:
                fig_map[normalized_old] = f"图{fig_counter}"
                fig_counter += 1
        elif kind == "表":
            if normalized_old not in tab_map:
                tab_map[normalized_old] = f"表{tab_counter}"
                tab_counter += 1

    return fig_map, tab_map


def renumber_text(text: str) -> tuple[str, dict[str, str]]:
    """Renumber figures and tables and replace all references across the text."""
    fig_map, tab_map = extract_captions_and_order(text)
    combined_map = {**fig_map, **tab_map}

    if not combined_map:
        return text, {}

    # Sort keys by length descending so "图1-10" matches before "图1-1"
    sorted_keys = sorted(combined_map.keys(), key=lambda k: len(k), reverse=True)

    # Build regex to replace exact identifiers
    # We match (图|表)\s*(X-Y) with word boundary or non-digit boundary following
    result = text
    for old_token in sorted_keys:
        kind = old_token[0]  # '图' or '表'
        num = old_token[1:]  # '1-1'
        new_token = combined_map[old_token]

        # Match kind followed by optional spaces and num, ensuring no trailing digit or dash
        pattern = re.compile(rf"{re.escape(kind)}\s*{re.escape(num)}(?![0-9\-])")
        result = pattern.sub(new_token, result)

    return result, combined_map


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Renumber figures and tables in markdown papers.")
    parser.add_argument("input_file", type=Path, help="Path to markdown paper file")
    parser.add_argument("--in-place", "-i", action="store_true", help="Modify file in-place")
    parser.add_argument("--output", "-o", type=Path, help="Output file path (default: stdout if not --in-place)")
    parser.add_argument("--json-map", "-m", type=Path, help="Save mapping dictionary as JSON")

    args = parser.parse_args(argv)

    if not args.input_file.exists():
        print(f"Error: input file '{args.input_file}' not found.", file=sys.stderr)
        return 1

    content = args.input_file.read_text(encoding="utf-8")
    renumbered, mapping = renumber_text(content)

    if args.json_map:
        args.json_map.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Mapping saved to {args.json_map}", file=sys.stderr)

    if args.in_place:
        args.input_file.write_text(renumbered, encoding="utf-8")
        print(f"Successfully renumbered {len(mapping)} figures/tables in-place in {args.input_file}", file=sys.stderr)
    elif args.output:
        args.output.write_text(renumbered, encoding="utf-8")
        print(f"Successfully renumbered {len(mapping)} figures/tables into {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(renumbered)

    return 0


if __name__ == "__main__":
    sys.exit(main())
