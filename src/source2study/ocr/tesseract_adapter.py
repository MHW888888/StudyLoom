from __future__ import annotations

from pathlib import Path

from source2study.ocr.base import OcrResult


def run_tesseract_if_available(image_path: Path) -> OcrResult | None:
    return None
