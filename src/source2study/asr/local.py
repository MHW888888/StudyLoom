from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AsrResult:
    status: str
    text: str
    confidence: float
    engine: str
    warnings: list[str]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "text": self.text,
            "confidence": self.confidence,
            "engine": self.engine,
            "warnings": self.warnings,
        }


def inspect_local_asr() -> dict:
    executable = shutil.which("whisper")
    return {
        "available": bool(executable),
        "engine": "whisper_cli" if executable else "unavailable",
        "executable": executable,
        "note": "ASR is optional and only runs on user-provided local media files.",
    }


def run_local_asr(media_path: Path) -> AsrResult:
    executable = shutil.which("whisper")
    if not executable:
        return AsrResult(
            status="unavailable",
            text="",
            confidence=0.0,
            engine="unavailable",
            warnings=["whisper CLI is not installed; provide a transcript file or install a local ASR engine."],
        )
    with tempfile.TemporaryDirectory() as tmp:
        completed = subprocess.run(
            [executable, str(media_path), "--output_format", "txt", "--output_dir", tmp],
            check=False,
            capture_output=True,
            text=True,
            timeout=60 * 30,
        )
        if completed.returncode != 0:
            return AsrResult(
                status="fail",
                text="",
                confidence=0.0,
                engine="whisper_cli",
                warnings=[(completed.stderr or "whisper CLI failed").strip()],
            )
        txt_files = sorted(Path(tmp).glob("*.txt"))
        text = txt_files[0].read_text(encoding="utf-8", errors="replace").strip() if txt_files else ""
        return AsrResult(
            status="pass" if text else "fail",
            text=text,
            confidence=0.72 if text else 0.0,
            engine="whisper_cli",
            warnings=[] if text else ["whisper CLI produced no transcript text."],
        )
