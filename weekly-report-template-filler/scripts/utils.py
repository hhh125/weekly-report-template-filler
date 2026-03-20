#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

from docx import Document
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".txt", ".md", ".docx", ".pdf"}


def normalize_text(text: str) -> str:
    """Normalize line endings, bullets, and repeated blank lines."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    bullet_map = {
        "•": "- ",
        "◦": "- ",
        "▪": "- ",
        "·": "- ",
        "●": "- ",
        "○": "- ",
    }
    for old, new in bullet_map.items():
        text = text.replace(old, new)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_docx(path: Path) -> str:
    doc = Document(str(path))
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(lines)


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text)
    return "\n".join(pages)


def load_text_from_file(path: str | Path) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {suffix}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    if suffix in {".txt", ".md"}:
        return normalize_text(_read_txt(file_path))
    if suffix == ".docx":
        return normalize_text(_read_docx(file_path))
    if suffix == ".pdf":
        return normalize_text(_read_pdf(file_path))
    raise ValueError(f"Unsupported file type: {suffix}")


def chunk_nonempty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def looks_like_heading(line: str) -> bool:
    line = line.strip().strip(":：")
    if not line:
        return False
    if len(line) > 40:
        return False
    if re.match(r"^(section|chapter)\s+\d+", line, re.I):
        return True
    if re.match(r"^(\d+[.)]|[一二三四五六七八九十]+[、.])", line):
        return True
    if any(token in line.lower() for token in [
        "progress", "done", "completed", "issue", "risk", "blocker",
        "plan", "next", "support", "summary", "work"
    ]):
        return True
    if any(token in line for token in ["本周", "下周", "风险", "问题", "计划", "事项", "进展", "完成"]):
        return True
    if 1 <= len(line) <= 20:
        return True
    return False


def split_heading_prefix(line: str) -> str:
    cleaned = re.sub(r"^(\d+[.)]|[一二三四五六七八九十]+[、.])\s*", "", line.strip())
    return cleaned.strip().strip(":：")


def infer_tone(lines: Iterable[str]) -> str:
    sample = " ".join(list(lines)[:20]).lower()
    if any(token in sample for token in ["风险", "问题", "状态", "进展", "blocker", "status"]):
        return "status-oriented"
    if any(token in sample for token in ["请", "敬请", "formal", "therefore", "completed"]):
        return "formal"
    if len(sample) < 200:
        return "concise"
    return "custom"
