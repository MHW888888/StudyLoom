from __future__ import annotations

from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.models.source import AdapterCapability


class PptxAdapter(SourceAdapter):
    name = "pptx_deck"
    source_types = ("pptx",)
    risk_level = "low"
    default_enabled = False
    allowed_methods = ("planned_user_uploaded_pptx",)
    blocked_methods = ("silent_slide_loss", "silent_speaker_note_loss", "chart_data_loss")
    source_type_aliases = ("ppt", "pptx", "slides", "slide_deck")

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        return path.exists() and path.is_file() and path.suffix.lower() in {".pptx", ".ppt"}

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="pptx",
            availability="planned",
            supported_methods=["planned_user_uploaded_pptx"],
            required_authorization=["user_authorized_local_processing"],
            expected_outputs=["slides", "titles", "body text", "images", "charts", "speaker notes"],
            known_risks=["slide image loss", "speaker note loss", "chart data not parsed yet", "animation order not preserved yet"],
            fallbacks=["export slides to PDF", "upload speaker notes", "upload slide screenshots with OCR sidecars"],
            risk_level=self.risk_level,
            default_enabled=self.default_enabled,
            allowed_methods=list(self.allowed_methods),
            blocked_methods=list(self.blocked_methods),
        )

    def ingest(self, request: SourceRequest) -> AdapterResult:
        raise AdapterError(
            "PPTX intake is planned but not implemented yet.",
            "Export slides to PDF/Markdown or upload screenshots plus speaker notes until the PPTX adapter preserves slide structure.",
        )
