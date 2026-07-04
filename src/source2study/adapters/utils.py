from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:12]
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", prefix).strip("_").lower()
    return f"{clean}_{digest}"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def read_text_lossy(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_bytes().decode("utf-8", errors="replace")


def split_paragraphs(text: str, max_chars: int = 900) -> list[str]:
    rough = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    for part in rough or [text.strip()]:
        if len(part) <= max_chars:
            if part:
                chunks.append(part)
            continue
        for i in range(0, len(part), max_chars):
            chunk = part[i : i + max_chars].strip()
            if chunk:
                chunks.append(chunk)
    return chunks
