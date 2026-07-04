from __future__ import annotations

from urllib.parse import urlparse

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.capability import blocked_platform_capability
from source2study.models.source import AdapterCapability


class BilibiliAdapter(SourceAdapter):
    name = "bilibili_planned"
    source_types = ("video",)
    risk_level = "high"
    default_enabled = False
    allowed_methods = ("user_uploaded_transcript", "local_video_file", "manual_fallback")
    blocked_methods = ("cookie_replay", "login_bypass", "anti_bot_bypass", "bulk_video_download")
    source_type_aliases = ("bilibili", "bilibili_url")

    def can_handle(self, request: SourceRequest) -> bool:
        parsed = urlparse(request.value)
        return "bilibili.com" in parsed.netloc.lower()

    def capability(self) -> AdapterCapability:
        return blocked_platform_capability("video", "bilibili")

    def ingest(self, request: SourceRequest) -> AdapterResult:
        raise AdapterError(
            "Direct Bilibili extraction is not implemented in the MVP.",
            "Provide subtitles, a local video file, or exported transcript material.",
        )
