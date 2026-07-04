from __future__ import annotations

from pathlib import Path

from source2study.adapters.article_utils import html_to_text_and_title
from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, read_text_lossy, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class WeChatPublicArticleAdapter(SourceAdapter):
    name = "wechat_public_article_user_export"
    source_types = ("wechat_public_article",)
    risk_level = "medium"
    default_enabled = True
    allowed_methods = ("user_uploaded_html", "user_uploaded_pdf", "paste_markdown", "browser_extension_current_page")
    blocked_methods = ("cookie_replay", "account_history_bulk_crawl", "login_bypass", "anti_bot_bypass")
    source_type_aliases = ("wechat", "wechat_html", "wechat_public_article", "wechat_public_article_html")

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        name = path.name.lower()
        explicit_type = request.source_type and self.matches_source_type(request.source_type)
        return path.exists() and path.is_file() and path.suffix.lower() in {".html", ".htm"} and (explicit_type or "wechat" in name)

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="wechat_public_article",
            availability="low_to_medium",
            supported_methods=["user_export", "public_article_fixture", "browser_extension_current_page"],
            required_authorization=["public_content_or_user_authorized_export"],
            expected_outputs=["article text", "title", "author when present", "source ledger"],
            known_risks=["copyright", "original-content notices", "login state", "anti-bot behavior"],
            fallbacks=["upload_saved_html", "upload_pdf", "paste_markdown", "screenshot_ocr"],
            last_verified="local_import",
            risk_level=self.risk_level,
            default_enabled=self.default_enabled,
            allowed_methods=list(self.allowed_methods),
            blocked_methods=list(self.blocked_methods),
        )

    def ingest(self, request: SourceRequest) -> AdapterResult:
        decision = self.policy_check(request)
        if not decision.allowed:
            raise AdapterError(decision.reason, "; ".join(decision.safe_alternatives))
        path = Path(request.value).resolve()
        html = read_text_lossy(path)
        text, title = html_to_text_and_title(html, path.stem)
        if not text:
            raise AdapterError("No readable WeChat article text found.", "Upload HTML/PDF/Markdown/screenshots.")

        source_id = stable_id("src_wechat", str(path))
        source = SourceRecord(
            source_id=source_id,
            source_type="wechat_public_article",
            source_url_or_path=str(path),
            title=title,
            platform="wechat_public_account",
            capture_time=utc_now(),
            transcript_source="user_export",
            language="unknown",
            duration_or_page_count=str(len(text)),
            hashes={"content": file_sha256(path)},
            available_metadata={
                "capture_method": "user_uploaded_html",
                "extraction_method": "user_uploaded_html",
                "policy": decision.to_dict(),
            },
            capability=self.capability(),
        )
        evidence = [
            EvidenceRecord(
                evidence_id=f"ev_{source_id}_{index}",
                source_id=source_id,
                source_type="wechat_public_article",
                text=chunk,
                location=EvidenceLocation(section=f"article chunk {index}", path=path.name),
                confidence=0.85,
                metadata={
                    "capture_method": "user_uploaded_html",
                    "extraction_method": "user_uploaded_html",
                    "source_title": title,
                    "source_url_or_path": str(path),
                },
            )
            for index, chunk in enumerate(split_paragraphs(text), start=1)
        ]
        return AdapterResult(source=source, evidence=evidence)
