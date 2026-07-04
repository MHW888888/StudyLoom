from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import read_text_lossy, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.parts.append(text)

    def text(self) -> str:
        return "\n\n".join(self.parts)


class WebpageAdapter(SourceAdapter):
    name = "ordinary_webpage"
    source_types = ("webpage",)
    risk_level = "medium"
    default_enabled = True
    allowed_methods = ("public_page", "user_exported_html")
    blocked_methods = ("login_bypass", "paywall_bypass", "anti_bot_bypass", "cookie_replay")
    source_type_aliases = ("web", "webpage", "html")

    def can_handle(self, request: SourceRequest) -> bool:
        parsed = urlparse(request.value)
        path = Path(request.value)
        return parsed.scheme in {"http", "https"} or (path.exists() and path.suffix.lower() in {".html", ".htm"})

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="webpage",
            availability="medium",
            supported_methods=["public_page", "user_export"],
            required_authorization=["public_content_or_user_export"],
            expected_outputs=["article text", "source URL", "section chunks"],
            known_risks=["dynamic pages", "copyright", "blocked extraction"],
            fallbacks=["upload HTML/PDF/Markdown/screenshots"],
            risk_level=self.risk_level,
            default_enabled=self.default_enabled,
            allowed_methods=list(self.allowed_methods),
            blocked_methods=list(self.blocked_methods),
        )

    def ingest(self, request: SourceRequest) -> AdapterResult:
        html, title, source_path = self._load_html(request)
        parser = _TextHTMLParser()
        parser.feed(html)
        text = parser.text()
        if not text:
            raise AdapterError("No readable webpage text found.", "Upload HTML/PDF/Markdown/screenshots.")

        source_id = stable_id("src_web", request.value)
        source = SourceRecord(
            source_id=source_id,
            source_type="webpage",
            source_url_or_path=request.value,
            title=title,
            platform="web",
            capture_time=utc_now(),
            transcript_source="public_page" if source_path is None else "user_export",
            language="unknown",
            duration_or_page_count=str(len(text)),
            capability=self.capability(),
        )
        evidence = [
            EvidenceRecord(
                evidence_id=f"ev_{source_id}_{index}",
                source_id=source_id,
                source_type="webpage",
                text=chunk,
                location=EvidenceLocation(section=f"html chunk {index}"),
                confidence=0.85,
            )
            for index, chunk in enumerate(split_paragraphs(text), start=1)
        ]
        return AdapterResult(source=source, evidence=evidence)

    def _load_html(self, request: SourceRequest) -> tuple[str, str, Path | None]:
        path = Path(request.value)
        if path.exists():
            return read_text_lossy(path), path.stem, path.resolve()
        if not request.policy.allow_network:
            raise AdapterError(
                "Webpage URL ingestion requires explicit network authorization.",
                "Save the page as HTML or rerun with --allow-network.",
            )
        req = Request(request.value, headers={"User-Agent": "source2study/0.1"})
        with urlopen(req, timeout=20) as response:
            raw = response.read()
            content_type = response.headers.get_content_charset() or "utf-8"
        return raw.decode(content_type, errors="replace"), request.value, None
