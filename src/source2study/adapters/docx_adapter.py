from __future__ import annotations

from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.models.source import AdapterCapability


class DocxAdapter(SourceAdapter):
    name = "docx_document"
    source_types = ("docx",)
    risk_level = "low"
    default_enabled = False
    allowed_methods = ("planned_user_uploaded_docx",)
    blocked_methods = ("silent_table_loss", "silent_image_loss", "comment_loss")
    source_type_aliases = ("word", "docx", "word_document")

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        return path.exists() and path.is_file() and path.suffix.lower() == ".docx"

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="docx",
            availability="planned",
            supported_methods=["planned_user_uploaded_docx"],
            required_authorization=["user_authorized_local_processing"],
            expected_outputs=["headings", "body text", "tables", "images", "comments", "headers and footers"],
            known_risks=["table structure loss", "image extraction loss", "comments and footnotes not preserved yet"],
            fallbacks=["export DOCX to PDF/Markdown", "paste key sections", "upload images/screenshots with OCR sidecars"],
            risk_level=self.risk_level,
            default_enabled=self.default_enabled,
            allowed_methods=list(self.allowed_methods),
            blocked_methods=list(self.blocked_methods),
        )

    def ingest(self, request: SourceRequest) -> AdapterResult:
        raise AdapterError(
            "DOCX intake is planned but not implemented yet.",
            "Export to Markdown/PDF or upload selected text, tables, and screenshots until the DOCX adapter preserves structure.",
        )
