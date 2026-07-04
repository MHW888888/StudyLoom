from __future__ import annotations

from source2study.models.source import AdapterCapability


def blocked_platform_capability(source_type: str, platform: str) -> AdapterCapability:
    return AdapterCapability(
        source_type=source_type,
        availability="low",
        supported_methods=["manual_fallback", "user_export"],
        required_authorization=["user_exported_material"],
        expected_outputs=["source link", "user-provided transcript or screenshots"],
        known_risks=[
            "platform access may require login or app context",
            "content copyright and redistribution restrictions",
            "adapter intentionally avoids bypassing access controls",
        ],
        fallbacks=["upload PDF/HTML/Markdown/screenshots", "provide transcript manually"],
        last_verified="runtime",
        risk_level="high",
        default_enabled=False,
        allowed_methods=["manual_fallback", "user_export"],
        blocked_methods=["cookie_replay", "login_bypass", "anti_bot_bypass", "bulk_media_download"],
    )
