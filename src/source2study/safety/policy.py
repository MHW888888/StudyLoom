from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from source2study.config import SourcePolicy


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    safe_alternatives: list[str] = field(default_factory=list)
    source_type: str = "unknown"
    risk_level: str = "unknown"
    allowed_methods: list[str] = field(default_factory=list)
    blocked_methods: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "safe_alternatives": self.safe_alternatives,
            "source_type": self.source_type,
            "risk_level": self.risk_level,
            "allowed_methods": self.allowed_methods,
            "blocked_methods": self.blocked_methods,
        }


class PolicyEngine:
    blocked_platforms = {
        "bilibili.com": "Direct extraction from Bilibili is blocked in the MVP.",
        "xiaohongshu.com": "Direct extraction from Xiaohongshu/RedNote is blocked in the MVP.",
        "xhslink.com": "Direct extraction from Xiaohongshu/RedNote short links is blocked in the MVP.",
        "mp.weixin.qq.com": "Direct extraction from WeChat public account articles is blocked in the MVP.",
        "zhihu.com": "Direct extraction from Zhihu is blocked in the MVP.",
        "youtube.com": "Direct YouTube video extraction is blocked in the MVP.",
        "youtu.be": "Direct YouTube video extraction is blocked in the MVP.",
    }

    disallowed_method_patterns = {
        "cookie_replay": ["cookie_replay", "cookie=", "cookies=", "fiddler", "request_cookie", "raw_cookie"],
        "account_history_bulk_crawl": ["bulk_history", "history_crawl", "account_history_bulk_crawl", "bulk_screenshot_crawl"],
        "login_bypass": ["login_bypass", "bypass_login", "session_replay", "raw_headers", "private_headers"],
        "paywall_bypass": ["paywall_bypass", "bypass_paywall", "paid_course_crawl"],
        "drm_bypass": ["drm_bypass", "bypass_drm", "decrypt_drm", "screen_recording_drm_bypass"],
        "anti_bot_bypass": ["anti_bot_bypass", "captcha_bypass", "bypass_anti_bot"],
        "signature_bypass": ["signature_bypass", "x-zse-96", "x_zse_96", "reverse_signature", "signature_reverse_engineering"],
    }

    safe_upload_alternatives = [
        "Upload a transcript file.",
        "Upload a saved HTML/PDF/Markdown copy that you are allowed to use.",
        "Use local files only.",
        "Provide screenshots or manual notes for local processing.",
    ]

    def check_source(self, value: str, policy: SourcePolicy, adapter: Any | None = None) -> PolicyDecision:
        normalized = value.lower()
        for method, patterns in self.disallowed_method_patterns.items():
            if any(pattern in normalized for pattern in patterns):
                return self._with_adapter_metadata(
                    PolicyDecision(
                        False,
                        f"{method} is not allowed for Source2Study adapters.",
                        self.safe_upload_alternatives,
                        source_type="blocked_method",
                        risk_level="high",
                        blocked_methods=[method],
                    ),
                    adapter,
                )

        path = Path(value)
        if path.exists():
            return self._with_adapter_metadata(
                PolicyDecision(True, "Local user-provided source is allowed.", source_type="local"),
                adapter,
            )

        parsed = urlparse(value)
        host = parsed.netloc.lower()
        if parsed.scheme in {"http", "https"}:
            for blocked_host, reason in self.blocked_platforms.items():
                if blocked_host in host:
                    return self._with_adapter_metadata(
                        PolicyDecision(
                            False,
                            reason,
                            self.safe_upload_alternatives,
                            source_type="blocked_platform",
                            risk_level="high",
                        ),
                        adapter,
                    )
            if not policy.allow_network:
                return self._with_adapter_metadata(
                    PolicyDecision(
                        False,
                        "Network ingestion is disabled by default.",
                        ["Save the page locally as HTML/PDF/Markdown.", "Rerun with --allow-network for public sources."],
                        source_type="network",
                        risk_level="medium",
                    ),
                    adapter,
                )
            return self._with_adapter_metadata(
                PolicyDecision(True, "Public network source allowed by explicit --allow-network.", source_type="network"),
                adapter,
            )

        return self._with_adapter_metadata(
            PolicyDecision(
                False,
                "Source type is not recognized by the MVP policy engine.",
                ["Provide a local PDF/text/Markdown/HTML file, local repo directory, or transcript file."],
                source_type="unknown",
            ),
            adapter,
        )

    def _with_adapter_metadata(self, decision: PolicyDecision, adapter: Any | None) -> PolicyDecision:
        if adapter is None:
            return decision
        allowed_methods = list(getattr(adapter, "allowed_methods", ())) or decision.allowed_methods
        blocked_methods = list(getattr(adapter, "blocked_methods", ())) or decision.blocked_methods
        safe_alternatives = decision.safe_alternatives or list(adapter.fallback_options())
        source_types = list(getattr(adapter, "source_types", ()))
        source_type = source_types[0] if decision.source_type in {"local", "network", "unknown"} and source_types else decision.source_type
        return PolicyDecision(
            allowed=decision.allowed,
            reason=decision.reason,
            safe_alternatives=safe_alternatives,
            source_type=source_type,
            risk_level=getattr(adapter, "risk_level", decision.risk_level),
            allowed_methods=allowed_methods,
            blocked_methods=blocked_methods,
        )


def public_output_notice(policy: SourcePolicy) -> str:
    if policy.allow_full_copyrighted_text_output:
        return "Full copyrighted text output was explicitly enabled; review rights before sharing."
    return "Public sharing should prefer links, timestamps, short excerpts, and generated explanation."
