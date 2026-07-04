from __future__ import annotations

from pathlib import Path

from source2study.adapters.utils import read_text_lossy
from source2study.ocr.base import OcrResult


def read_sidecar_or_placeholder(image_path: Path) -> OcrResult:
    for sidecar in (image_path.with_suffix(image_path.suffix + ".ocr.txt"), image_path.with_suffix(".ocr.txt")):
        if sidecar.exists():
            text = read_text_lossy(sidecar).strip()
            if text:
                return OcrResult(text=text, confidence=0.75, engine="sidecar_text")
    return OcrResult(
        text=f"OCR text is not available for {image_path.name}. Use this screenshot as low-confidence visual evidence only.",
        confidence=0.2,
        engine="placeholder",
    )
