from __future__ import annotations

from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceMedia, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord
from source2study.ocr.simple_placeholder import read_sidecar_or_placeholder


class ScreenshotOcrAdapter(SourceAdapter):
    name = "screenshot_ocr"
    source_types = ("screenshot_ocr",)
    risk_level = "medium"
    default_enabled = True
    allowed_methods = ("user_uploaded_screenshot", "sidecar_ocr_text", "placeholder_ocr")
    blocked_methods = ("screen_recording_drm_bypass", "paywall_bypass", "bulk_screenshot_crawl")
    source_type_aliases = ("screenshot", "screenshot_ocr", "image_ocr", "ocr_image")
    image_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        return path.exists() and path.is_file() and path.suffix.lower() in self.image_suffixes

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="screenshot_ocr",
            availability="medium",
            supported_methods=["user_uploaded_screenshot", "sidecar_ocr_text", "placeholder_ocr"],
            required_authorization=["user_authorized_local_processing"],
            expected_outputs=["image evidence", "OCR text when available", "ocr confidence"],
            known_risks=["OCR mistakes", "copyrighted screenshots", "private visible content"],
            fallbacks=["provide sidecar .ocr.txt", "paste manual notes", "upload HTML/PDF/Markdown instead"],
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
        ocr = read_sidecar_or_placeholder(path)
        source_id = stable_id("src_screenshot", str(path))
        source = SourceRecord(
            source_id=source_id,
            source_type="screenshot_ocr",
            source_url_or_path=str(path),
            title=path.stem,
            platform="local_image",
            capture_time=utc_now(),
            transcript_source="ocr_sidecar" if ocr.engine == "sidecar_text" else "ocr_placeholder",
            language="unknown",
            duration_or_page_count="1 image",
            files_created=[str(path)],
            hashes={"image": file_sha256(path)},
            available_metadata={
                "capture_method": "screenshot_ocr",
                "image_path": str(path),
                "ocr_engine": ocr.engine,
                "ocr_confidence": ocr.confidence,
                "policy": decision.to_dict(),
            },
            capability=self.capability(),
        )
        evidence = [
            EvidenceRecord(
                evidence_id=f"ev_{source_id}_ocr_1",
                source_id=source_id,
                source_type="screenshot_ocr",
                text=ocr.text,
                location=EvidenceLocation(section="screenshot OCR", path=path.name),
                kind="ocr",
                media=EvidenceMedia(
                    screenshot_path=str(path),
                    ocr_text=ocr.text,
                    visual_description="User-provided screenshot for OCR-backed learning evidence.",
                ),
                confidence=ocr.confidence,
                metadata={
                    "capture_method": "screenshot_ocr",
                    "image_path": str(path),
                    "ocr_confidence": ocr.confidence,
                    "ocr_engine": ocr.engine,
                    "source_title": path.stem,
                    "source_url_or_path": str(path),
                    "region": "full_image",
                },
            )
        ]
        return AdapterResult(source=source, evidence=evidence)
