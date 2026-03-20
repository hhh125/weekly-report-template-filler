#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from utils import load_text_from_file, normalize_text


SECTION_HINTS = {
    "completed": ["本周", "完成", "进展", "工作", "progress", "done", "completed", "work"],
    "blockers": ["风险", "问题", "阻塞", "blocker", "risk", "issue", "dependency"],
    "next": ["下周", "计划", "下一步", "next", "plan", "upcoming"],
    "support": ["支持", "协调", "协助", "support", "help needed"],
}


def read_schema(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_notes(path: str | None) -> str:
    if not path:
        return ""
    suffix = Path(path).suffix.lower()
    if suffix in {".txt", ".md", ".docx", ".pdf"}:
        return load_text_from_file(path)
    return normalize_text(Path(path).read_text(encoding="utf-8"))


def classify_notes(notes: str) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {k: [] for k in SECTION_HINTS}
    buckets["general"] = []
    priority = ["next", "blockers", "support", "completed"]
    for raw in [line.strip("- " ).strip() for line in notes.splitlines() if line.strip()]:
        lowered = raw.lower()
        matched = False
        for bucket in priority:
            hints = SECTION_HINTS[bucket]
            if any(h.lower() in lowered for h in hints):
                buckets[bucket].append(raw)
                matched = True
                break
        if not matched:
            buckets["general"].append(raw)
    return buckets


def choose_bucket(heading: str) -> str:
    lowered = heading.lower()
    for bucket, hints in SECTION_HINTS.items():
        if any(h.lower() in lowered for h in hints):
            return bucket
    return "general"


def polish_lines(lines: list[str]) -> str:
    if not lines:
        return ""
    cleaned = []
    for line in lines:
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        if line[-1] not in ".!?。；;":
            line += "。" if re.search(r"[\u4e00-\u9fff]", line) else "."
        cleaned.append(f"- {line}")
    return "\n".join(cleaned)


def render_blank(schema: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    markdown_parts: list[str] = []
    section_outputs: list[dict[str, Any]] = []
    for sec in schema["sections"]:
        content = sec["placeholder"]
        if sec.get("fixed_text"):
            content = f"{sec['fixed_text']}\n{content}"
        markdown_parts.append(f"## {sec['heading']}\n{content}")
        section_outputs.append({"heading": sec["heading"], "content": content, "missing": False})
    return "\n\n".join(markdown_parts), section_outputs


def render_filled(schema: dict[str, Any], notes: str) -> tuple[str, list[dict[str, Any]]]:
    classified = classify_notes(notes)
    general_pool = list(classified.get("general", []))
    markdown_parts: list[str] = []
    section_outputs: list[dict[str, Any]] = []

    for index, sec in enumerate(schema["sections"]):
        bucket = choose_bucket(sec["heading"])
        selected = list(classified.get(bucket, []))
        if not selected and general_pool:
            selected = general_pool[:]
            general_pool.clear()
        rendered = polish_lines(selected)
        missing = False
        if not rendered:
            rendered = sec["placeholder"]
            missing = True
        if sec.get("fixed_text"):
            rendered = f"{sec['fixed_text']}\n{rendered}"
        markdown_parts.append(f"## {sec['heading']}\n{rendered}")
        section_outputs.append({
            "heading": sec["heading"],
            "content": rendered,
            "missing": missing,
            "source_bucket": bucket,
            "required": bool(sec.get("required", False)),
        })
    return "\n\n".join(markdown_parts), section_outputs


def build_output_json(schema: dict[str, Any], mode: str, markdown: str, sections: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "template_name": schema.get("template_name", "weekly report"),
        "mode": mode,
        "tone": schema.get("tone", "custom"),
        "markdown_preview": markdown,
        "sections": sections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate blank or completed weekly report outputs from schema JSON.")
    parser.add_argument("--template", required=True, help="Path to template schema JSON")
    parser.add_argument("--notes", help="Path to weekly notes text/docx/pdf file")
    parser.add_argument("--mode", choices=["blank", "filled"], required=True)
    parser.add_argument("--markdown-output", required=True)
    parser.add_argument("--json-output", required=True)
    args = parser.parse_args()

    schema = read_schema(args.template)
    if args.mode == "blank":
        markdown, sections = render_blank(schema)
    else:
        notes = read_notes(args.notes)
        markdown, sections = render_filled(schema, notes)

    Path(args.markdown_output).write_text(markdown, encoding="utf-8")
    Path(args.json_output).write_text(
        json.dumps(build_output_json(schema, args.mode, markdown, sections), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote markdown to {args.markdown_output}")
    print(f"Wrote json to {args.json_output}")


if __name__ == "__main__":
    main()
