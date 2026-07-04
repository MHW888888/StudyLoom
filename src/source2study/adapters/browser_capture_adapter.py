from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from source2study.adapters.article_utils import html_to_text_and_title
from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, read_text_lossy, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class BrowserCaptureAdapter(SourceAdapter):
    name = "browser_capture"
    source_types = ("browser_capture",)
    risk_level = "medium"
    default_enabled = True
    allowed_methods = ("browser_extension_current_page", "current_page_dom", "user_saved_browser_capture_json")
    blocked_methods = ("cookie_replay", "account_history_bulk_crawl", "login_bypass", "anti_bot_bypass", "raw_headers")
    source_type_aliases = ("browser_capture", "browser_current_page", "current_page_dom")

    forbidden_keys = {
        "cookie",
        "cookies",
        "headers",
        "authorization",
        "token",
        "access_token",
        "refresh_token",
        "localstorage",
        "sessionstorage",
        "session_storage",
        "private_headers",
    }

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        if not path.exists() or not path.is_file() or path.suffix.lower() != ".json":
            return False
        if request.source_type and self.matches_source_type(request.source_type):
            return True
        name = path.name.lower()
        if "browser_capture" in name or "current_page" in name:
            return True
        try:
            data = json.loads(read_text_lossy(path))
        except json.JSONDecodeError:
            return False
        return data.get("source_type") == "browser_capture" or data.get("capture_method") == "current_page_dom"

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="browser_capture",
            availability="medium",
            supported_methods=["browser_extension_current_page", "user_saved_browser_capture_json"],
            required_authorization=["user_initiated_current_page_capture"],
            expected_outputs=["page text", "title", "author", "source URL", "capture metadata"],
            known_risks=["private visible page content", "copyright", "extension must not export cookies or headers"],
            fallbacks=["upload_saved_html", "paste_markdown", "screenshot_ocr"],
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
        try:
            data = json.loads(read_text_lossy(path))
        except json.JSONDecodeError as exc:
            raise AdapterError("Browser capture JSON is not valid.", "Export the current page as browser_capture JSON.") from exc
        self._validate_capture(data)

        capture_method = str(data.get("capture_method") or "")
        platform = str(data.get("platform") or "browser")
        source_url = str(data.get("url") or str(path))
        html = str(data.get("content_html") or "")
        text = str(data.get("text") or "")
        html_text, html_title = html_to_text_and_title(html, str(data.get("title") or path.stem)) if html else ("", str(data.get("title") or path.stem))
        text = text or html_text
        title = str(data.get("title") or html_title or path.stem)
        if not text.strip():
            raise AdapterError("Browser capture has no readable text.", "Export visible page text or upload screenshots for OCR.")

        source_id = stable_id("src_browser", str(path) + source_url)
        source = SourceRecord(
            source_id=source_id,
            source_type="browser_capture",
            source_url_or_path=source_url,
            title=title,
            author_or_channel=str(data.get("author") or "") or None,
            platform=platform,
            capture_time=utc_now(),
            transcript_source="browser_capture",
            language=str(data.get("language") or "unknown"),
            duration_or_page_count=str(len(text)),
            files_created=[str(path)],
            hashes={"content": file_sha256(path)},
            available_metadata={
                "capture_file": str(path),
                "capture_method": capture_method,
                "published_at": data.get("published_at"),
                "images_count": len(data.get("images") or []),
                "user_initiated_capture": True,
                "policy": decision.to_dict(),
            },
            capability=self.capability(),
        )
        evidence = [
            EvidenceRecord(
                evidence_id=f"ev_{source_id}_{index}",
                source_id=source_id,
                source_type="browser_capture",
                text=chunk,
                location=EvidenceLocation(section=f"browser capture chunk {index}", path=path.name),
                confidence=0.9,
                metadata={
                    "capture_method": capture_method,
                    "user_initiated_capture": True,
                    "source_title": title,
                    "source_url_or_path": source_url,
                    "platform": platform,
                },
            )
            for index, chunk in enumerate(split_paragraphs(text), start=1)
        ]
        return AdapterResult(source=source, evidence=evidence)

    def _validate_capture(self, data: dict[str, Any]) -> None:
        capture_method = str(data.get("capture_method") or "")
        if capture_method not in {"current_page_dom", "browser_current_page"}:
            raise AdapterError("Browser capture must use current_page_dom.", "Export only the currently visible page.")
        if data.get("user_initiated_capture") is False:
            raise AdapterError("Browser capture must be user initiated.", "Use a current-page export initiated by the user.")
        for key in self._iter_keys(data):
            normalized = key.lower().replace("-", "_")
            if normalized in self.forbidden_keys:
                raise AdapterError("Browser capture contains forbidden private session data.", "Remove cookies, headers, tokens, and storage data.")
        for bulk_key in ("captures", "items", "history", "account_history"):
            value = data.get(bulk_key)
            if isinstance(value, list) and len(value) > 1:
                raise AdapterError("Browser capture must not contain bulk history data.", "Export only the current page.")

    def _iter_keys(self, value: Any):
        if isinstance(value, dict):
            for key, child in value.items():
                yield str(key)
                yield from self._iter_keys(child)
        elif isinstance(value, list):
            for item in value:
                yield from self._iter_keys(item)
