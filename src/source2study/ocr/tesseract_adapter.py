from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from source2study.ocr.base import OcrResult


def run_tesseract_if_available(image_path: Path) -> OcrResult | None:
    executable = shutil.which("tesseract")
    if not executable:
        return None
    try:
        completed = subprocess.run(
            [executable, str(image_path), "stdout", "-l", "eng+chi_sim"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (completed.stdout or "").strip()
    if completed.returncode != 0 or not text:
        return None
    return OcrResult(text=text, confidence=0.72, engine="tesseract_cli")
