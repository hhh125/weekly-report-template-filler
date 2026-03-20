#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from utils import chunk_nonempty_lines, infer_tone, load_text_from_file, looks_like_heading, split_heading_prefix


def detect_sections(text: str) -> list[dict[str, Any]]:
    lines = chunk_nonempty_lines(text)
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith('[') and line.endswith(']'):
            if current is None:
                current = {
                    "id": "section_1",
                    "heading": "周报内容",
                    "fixed_text": "",
                    "placeholder": line,
                    "required": True,
                }
            else:
                current["placeholder"] = line
            continue
        if looks_like_heading(line):
            if current:
                sections.append(current)
            heading = split_heading_prefix(line)
            current = {
                "id": f"section_{len(sections) + 1}",
                "heading": heading,
                "fixed_text": "",
                "placeholder": f"[填写{heading}]",
                "required": not any(token in heading.lower() for token in ["risk", "issue", "support", "dependency"])
                    and not any(token in heading for token in ["风险", "问题", "需协调"]),
            }
        else:
            if current is None:
                current = {
                    "id": "section_1",
                    "heading": "周报内容",
                    "fixed_text": "",
                    "placeholder": "[填写周报内容]",
                    "required": True,
                }
            if current["fixed_text"]:
                current["fixed_text"] += "\n" + line
            else:
                current["fixed_text"] = line

    if current:
        sections.append(current)

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for sec in sections:
        heading_key = sec["heading"].strip().lower()
        if not heading_key:
            continue
        if heading_key in seen:
            continue
        seen.add(heading_key)
        deduped.append(sec)

    if not deduped:
        deduped = [{
            "id": "section_1",
            "heading": "周报内容",
            "fixed_text": "",
            "placeholder": "[填写周报内容]",
            "required": True,
        }]
    return deduped


def build_schema(input_path: str) -> dict[str, Any]:
    text = load_text_from_file(input_path)
    lines = chunk_nonempty_lines(text)
    sections = detect_sections(text)
    return {
        "template_name": Path(input_path).stem.replace("_", " ").replace("-", " ").strip() or "weekly report",
        "source_type": Path(input_path).suffix.lower().lstrip("."),
        "tone": infer_tone(lines),
        "format": "markdown",
        "sections": sections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a weekly report template into JSON schema.")
    parser.add_argument("--input", required=True, help="Path to .txt, .md, .docx, or .pdf template")
    parser.add_argument("--output", required=True, help="Path to output JSON schema")
    args = parser.parse_args()

    schema = build_schema(args.input)
    output_path = Path(args.output)
    output_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote schema to {output_path}")


if __name__ == "__main__":
    main()
