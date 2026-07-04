from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceRights:
    usage: str = "personal_learning"
    redistribution_allowed: bool = False
    copyright_status: str = "user_authorized_local_processing"

    def to_dict(self) -> dict[str, Any]:
        return {
            "usage": self.usage,
            "redistribution_allowed": self.redistribution_allowed,
            "copyright_status": self.copyright_status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceRights":
        return cls(
            usage=data.get("usage", "personal_learning"),
            redistribution_allowed=bool(data.get("redistribution_allowed", False)),
            copyright_status=data.get("copyright_status", "user_authorized_local_processing"),
        )


@dataclass(frozen=True)
class AdapterCapability:
    source_type: str
    availability: str
    supported_methods: list[str]
    required_authorization: list[str]
    expected_outputs: list[str]
    known_risks: list[str] = field(default_factory=list)
    fallbacks: list[str] = field(default_factory=list)
    last_verified: str = "runtime"
    risk_level: str = "unknown"
    default_enabled: bool = True
    allowed_methods: list[str] = field(default_factory=list)
    blocked_methods: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "availability": self.availability,
            "supported_methods": self.supported_methods,
            "required_authorization": self.required_authorization,
            "expected_outputs": self.expected_outputs,
            "known_risks": self.known_risks,
            "fallbacks": self.fallbacks,
            "last_verified": self.last_verified,
            "risk_level": self.risk_level,
            "default_enabled": self.default_enabled,
            "allowed_methods": self.allowed_methods,
            "blocked_methods": self.blocked_methods,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AdapterCapability":
        return cls(
            source_type=data["source_type"],
            availability=data.get("availability", "unknown"),
            supported_methods=data.get("supported_methods", []),
            required_authorization=data.get("required_authorization", []),
            expected_outputs=data.get("expected_outputs", []),
            known_risks=data.get("known_risks", []),
            fallbacks=data.get("fallbacks", []),
            last_verified=data.get("last_verified", "runtime"),
            risk_level=data.get("risk_level", "unknown"),
            default_enabled=bool(data.get("default_enabled", True)),
            allowed_methods=data.get("allowed_methods", []),
            blocked_methods=data.get("blocked_methods", []),
        )


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_type: str
    source_url_or_path: str
    title: str
    platform: str
    capture_time: str
    author_or_channel: str | None = None
    available_metadata: dict[str, Any] = field(default_factory=dict)
    transcript_source: str = "unknown"
    language: str = "unknown"
    duration_or_page_count: str | None = None
    files_created: list[str] = field(default_factory=list)
    hashes: dict[str, str] = field(default_factory=dict)
    known_failures: list[str] = field(default_factory=list)
    rights: SourceRights = field(default_factory=SourceRights)
    capability: AdapterCapability | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "source_url_or_path": self.source_url_or_path,
            "title": self.title,
            "author_or_channel": self.author_or_channel,
            "platform": self.platform,
            "capture_time": self.capture_time,
            "available_metadata": self.available_metadata,
            "transcript_source": self.transcript_source,
            "language": self.language,
            "duration_or_page_count": self.duration_or_page_count,
            "files_created": self.files_created,
            "hashes": self.hashes,
            "known_failures": self.known_failures,
            "rights": self.rights.to_dict(),
            "copyright_status": self.rights.copyright_status,
        }
        if self.capability:
            data["capability"] = self.capability.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceRecord":
        rights_data = data.get("rights") or {
            "copyright_status": data.get("copyright_status", "user_authorized_local_processing")
        }
        return cls(
            source_id=data["source_id"],
            source_type=data["source_type"],
            source_url_or_path=data["source_url_or_path"],
            title=data["title"],
            author_or_channel=data.get("author_or_channel"),
            platform=data.get("platform", "unknown"),
            capture_time=data["capture_time"],
            available_metadata=data.get("available_metadata", {}),
            transcript_source=data.get("transcript_source", "unknown"),
            language=data.get("language", "unknown"),
            duration_or_page_count=data.get("duration_or_page_count"),
            files_created=data.get("files_created", []),
            hashes=data.get("hashes", {}),
            known_failures=data.get("known_failures", []),
            rights=SourceRights.from_dict(rights_data),
            capability=AdapterCapability.from_dict(data["capability"]) if data.get("capability") else None,
        )
