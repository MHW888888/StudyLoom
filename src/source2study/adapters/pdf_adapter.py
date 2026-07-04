from __future__ import annotations

from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, read_text_lossy, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class PdfAdapter(SourceAdapter):
    """Ingest user-provided PDFs and text-like files.

    The MVP treats text and Markdown files as page-one document sources. Real PDF
    text extraction uses optional pypdf when available.
    """

    name = "pdf_document"
    source_types = ("document",)
    risk_level = "low"
    default_enabled = True
    allowed_methods = ("user_uploaded_pdf", "user_uploaded_text", "user_uploaded_markdown", "text_extraction")
    blocked_methods = ("pirated_book_download", "drm_bypass", "paywall_bypass")
    source_type_aliases = ("pdf", "document", "markdown", "text")
    suffixes = {".pdf", ".txt", ".md", ".markdown"}

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        return path.exists() and path.is_file() and path.suffix.lower() in self.suffixes

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="document",
            availability="high",
            supported_methods=["user_export", "text_extraction", "optional_pypdf"],
            required_authorization=["user_authorized_local_processing"],
            expected_outputs=["page-aware text evidence", "source ledger"],
            known_risks=["copyright boundaries", "scanned PDFs require OCR not yet implemented"],
            fallbacks=["upload text/Markdown export", "provide screenshots for OCR roadmap"],
            risk_level=self.risk_level,
            default_enabled=self.default_enabled,
            allowed_methods=list(self.allowed_methods),
            blocked_methods=list(self.blocked_methods),
        )

    def ingest(self, request: SourceRequest) -> AdapterResult:
        path = Path(request.value).resolve()
        source_id = stable_id("src_doc", str(path))
        pages = self._extract_pages(path)
        if not any(page.strip() for _, page in pages):
            raise AdapterError("No extractable text found.", "Provide OCR text, Markdown, or screenshots.")

        source = SourceRecord(
            source_id=source_id,
            source_type="document",
            source_url_or_path=str(path),
            title=path.stem,
            platform="local_file",
            capture_time=utc_now(),
            transcript_source="manual" if path.suffix.lower() != ".pdf" else "pdf_text",
            language="unknown",
            duration_or_page_count=str(len(pages)),
            hashes={"content": file_sha256(path)},
            capability=self.capability(),
        )

        evidence: list[EvidenceRecord] = []
        for page_number, page_text in pages:
            for index, chunk in enumerate(split_paragraphs(page_text), start=1):
                evidence.append(
                    EvidenceRecord(
                        evidence_id=f"ev_{source_id}_{page_number}_{index}",
                        source_id=source_id,
                        source_type="document",
                        text=chunk,
                        location=EvidenceLocation(page=page_number, section=f"chunk {index}"),
                        confidence=0.9 if path.suffix.lower() == ".pdf" else 1.0,
                    )
                )
        return AdapterResult(source=source, evidence=evidence)

    def _extract_pages(self, path: Path) -> list[tuple[int, str]]:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md", ".markdown"}:
            return [(1, read_text_lossy(path))]
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError as exc:
            raise AdapterError(
                "PDF text extraction requires the optional pypdf dependency.",
                "Install source2study[pdf] or provide a text/Markdown export.",
            ) from exc

        reader = PdfReader(str(path))
        pages: list[tuple[int, str]] = []
        for idx, page in enumerate(reader.pages, start=1):
            pages.append((idx, page.extract_text() or ""))
        return pages
