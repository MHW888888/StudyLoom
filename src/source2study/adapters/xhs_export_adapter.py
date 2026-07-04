from __future__ import annotations

import json
from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, read_text_lossy, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceMedia, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class XhsExportAdapter(SourceAdapter):
    name = "xhs_user_export"
    source_types = ("xiaohongshu_export",)
    risk_level = "medium"
    default_enabled = True
    allowed_methods = ("user_uploaded_markdown", "user_uploaded_json", "browser_extension_current_page", "screenshot_ocr")
    blocked_methods = ("cookie_replay", "account_history_bulk_crawl", "login_bypass", "anti_bot_bypass", "media_download")
    source_type_aliases = ("xhs", "xhs_export", "xiaohongshu", "xiaohongshu_export")

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        name = path.name.lower()
        explicit_type = request.source_type and self.matches_source_type(request.source_type)
        return path.exists() and path.is_file() and (explicit_type or ".xhs." in name or "xhs" in name or "xiaohongshu" in name)

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="xiaohongshu_export",
            availability="medium_to_low",
            supported_methods=["user_export", "browser_extension_current_page", "screenshot_ocr"],
            required_authorization=["public_content_or_user_authorized_export"],
            expected_outputs=["note text", "image OCR placeholders", "source ledger"],
            known_risks=["login state", "anti-bot protections", "content copyright", "unstable surfaces"],
            fallbacks=["upload_markdown", "upload_json_export", "upload_screenshots_for_ocr", "paste_manual_notes"],
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
        text, title, metadata = self._load_export(path)
        if not text:
            raise AdapterError("No readable Xiaohongshu export text found.", "Upload Markdown/JSON/screenshots.")

        source_id = stable_id("src_xhs", str(path))
        source = SourceRecord(
            source_id=source_id,
            source_type="xiaohongshu_export",
            source_url_or_path=str(path),
            title=title,
            author_or_channel=metadata.get("author"),
            platform="xiaohongshu_export",
            capture_time=utc_now(),
            transcript_source="user_export",
            language="unknown",
            duration_or_page_count=str(len(text)),
            hashes={"content": file_sha256(path)},
            available_metadata={
                **metadata,
                "capture_method": metadata["extraction_method"],
                "policy": decision.to_dict(),
            },
            capability=self.capability(),
        )
        evidence: list[EvidenceRecord] = []
        for index, chunk in enumerate(split_paragraphs(text), start=1):
            evidence.append(
                EvidenceRecord(
                    evidence_id=f"ev_{source_id}_{index}",
                    source_id=source_id,
                    source_type="xiaohongshu_export",
                    text=chunk,
                    location=EvidenceLocation(section=f"note chunk {index}", path=path.name),
                    confidence=0.85,
                    metadata={
                        "capture_method": metadata["extraction_method"],
                        "extraction_method": metadata["extraction_method"],
                        "source_title": title,
                        "source_url_or_path": metadata.get("source_url") or str(path),
                    },
                )
            )
        if metadata.get("ocr_placeholder"):
            evidence.append(
                EvidenceRecord(
                    evidence_id=f"ev_{source_id}_ocr_placeholder",
                    source_id=source_id,
                    source_type="xiaohongshu_export",
                    text=metadata["ocr_placeholder"],
                    location=EvidenceLocation(section="screenshot OCR placeholder", path=path.name),
                    kind="ocr_placeholder",
                    media=EvidenceMedia(ocr_text=metadata["ocr_placeholder"], visual_description="User-provided image OCR placeholder."),
                    confidence=0.5,
                    metadata={
                        "capture_method": "screenshot_ocr_placeholder",
                        "extraction_method": "screenshot_ocr_placeholder",
                        "ocr_confidence": 0.5,
                        "source_title": title,
                        "source_url_or_path": metadata.get("source_url") or str(path),
                    },
                )
            )
        return AdapterResult(source=source, evidence=evidence)

    def _load_export(self, path: Path) -> tuple[str, str, dict[str, str]]:
        raw = read_text_lossy(path)
        if path.suffix.lower() == ".json":
            data = json.loads(raw)
            title = str(data.get("title") or path.stem)
            content = str(data.get("content") or data.get("text") or "")
            tags = data.get("tags") or []
            tag_text = " ".join(f"#{tag}" for tag in tags)
            text = "\n\n".join(part for part in [title, content, tag_text] if part)
            metadata = {
                "author": str(data.get("author") or ""),
                "source_url": str(data.get("source_url") or ""),
                "extraction_method": "user_uploaded_json",
            }
            if data.get("ocr_placeholder"):
                metadata["ocr_placeholder"] = str(data["ocr_placeholder"])
            return text, title, metadata

        title = path.stem
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                break
        return raw, title, {"author": "", "source_url": "", "extraction_method": "user_uploaded_markdown"}
