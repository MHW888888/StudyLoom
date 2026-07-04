from __future__ import annotations

import re
from pathlib import Path
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)cookie\s*:\s*[^;\n]+(?:;[^;\n]+)*"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)(cookie|authorization|token|api[_-]?key)\s*[:=]\s*['\"]?[^'\"\s]+"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
]

BROWSER_PROFILE_PATTERN = re.compile(
    r"(?i)([A-Z]:\\Users\\[^\\]+\\AppData\\Local\\(?:Google\\Chrome|Microsoft\\Edge|Mozilla\\Firefox)[^'\"\s]*)"
)
WINDOWS_HOME_PATTERN = re.compile(r"(?i)([A-Z]:\\Users\\)([^\\]+)")


def find_secrets(text: str) -> list[str]:
    findings: list[str] = []
    for pattern in SECRET_PATTERNS:
        findings.extend(match.group(0) for match in pattern.finditer(text))
    return findings


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def redact_paths(text: str) -> str:
    redacted = BROWSER_PROFILE_PATTERN.sub("[REDACTED_BROWSER_PROFILE]", text)
    return WINDOWS_HOME_PATTERN.sub(r"\1[REDACTED_USER]", redacted)


def redact_text(text: str) -> str:
    return redact_paths(redact_secrets(text))


def safe_display_path(path: str | Path, workspace: str | Path | None = None, root: str | Path | None = None) -> str:
    candidate = Path(path)
    try:
        resolved = candidate.resolve()
    except OSError:
        return redact_text(str(path))

    bases = [Path(item).resolve() for item in (workspace, root) if item]
    for base in bases:
        try:
            return str(resolved.relative_to(base)).replace("\\", "/")
        except ValueError:
            continue
    return redact_text(str(resolved))


def sanitize_for_response(value: Any, *, workspace: str | Path | None = None, root: str | Path | None = None, max_chars: int = 20000) -> Any:
    if isinstance(value, dict):
        return {
            redact_text(str(key)): sanitize_for_response(item, workspace=workspace, root=root, max_chars=max_chars)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize_for_response(item, workspace=workspace, root=root, max_chars=max_chars) for item in value]
    if isinstance(value, tuple):
        return [sanitize_for_response(item, workspace=workspace, root=root, max_chars=max_chars) for item in value]
    if isinstance(value, Path):
        return safe_display_path(value, workspace=workspace, root=root)
    if isinstance(value, str):
        redacted = redact_text(value)
        if max_chars >= 0 and len(redacted) > max_chars:
            return redacted[:max_chars] + "...[TRUNCATED]"
        return redacted
    return value
