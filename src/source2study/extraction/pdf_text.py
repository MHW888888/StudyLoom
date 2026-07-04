from __future__ import annotations

from pathlib import Path

from source2study.adapters.pdf_adapter import PdfAdapter
from source2study.adapters.base import SourceRequest


def extract_document(path: Path, request: SourceRequest):
    return PdfAdapter().ingest(SourceRequest(str(path), request.workspace, request.policy, request.authorization))
