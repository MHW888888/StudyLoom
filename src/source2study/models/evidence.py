from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from source2study.models.source import SourceRights


@dataclass(frozen=True)
class EvidenceLocation:
    timestamp_start: str | None = None
    timestamp_end: str | None = None
    page: int | None = None
    section: str | None = None
    path: str | None = None
    line_start: int | None = None
    line_end: int | None = None

    def label(self) -> str:
        if self.timestamp_start or self.timestamp_end:
            return f"{self.timestamp_start or '?'}-{self.timestamp_end or '?'}"
        if self.page is not None:
            return f"p. {self.page}"
        if self.path:
            if self.line_start:
                end = self.line_end or self.line_start
                return f"{self.path}:{self.line_start}-{end}"
            return self.path
        return self.section or "unknown location"

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "page": self.page,
            "section": self.section,
            "path": self.path,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceLocation":
        return cls(
            timestamp_start=data.get("timestamp_start"),
            timestamp_end=data.get("timestamp_end"),
            page=data.get("page"),
            section=data.get("section"),
            path=data.get("path"),
            line_start=data.get("line_start"),
            line_end=data.get("line_end"),
        )


@dataclass(frozen=True)
class EvidenceMedia:
    screenshot_path: str | None = None
    ocr_text: str | None = None
    visual_description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "screenshot_path": self.screenshot_path,
            "ocr_text": self.ocr_text,
            "visual_description": self.visual_description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceMedia":
        return cls(
            screenshot_path=data.get("screenshot_path"),
            ocr_text=data.get("ocr_text"),
            visual_description=data.get("visual_description"),
        )


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source_id: str
    source_type: str
    text: str
    location: EvidenceLocation
    kind: str = "text"
    media: EvidenceMedia = field(default_factory=EvidenceMedia)
    confidence: float = 1.0
    rights: SourceRights = field(default_factory=SourceRights)
    used_in_outputs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def citation(self) -> str:
        return f"{self.evidence_id} ({self.source_id}, {self.location.label()})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "kind": self.kind,
            "text": self.text,
            "location": self.location.to_dict(),
            "media": self.media.to_dict(),
            "confidence": self.confidence,
            "rights": self.rights.to_dict(),
            "used_in_outputs": self.used_in_outputs,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceRecord":
        return cls(
            evidence_id=data["evidence_id"],
            source_id=data["source_id"],
            source_type=data["source_type"],
            kind=data.get("kind", "text"),
            text=data["text"],
            location=EvidenceLocation.from_dict(data.get("location", {})),
            media=EvidenceMedia.from_dict(data.get("media", {})),
            confidence=float(data.get("confidence", 1.0)),
            rights=SourceRights.from_dict(data.get("rights", {})),
            used_in_outputs=data.get("used_in_outputs", []),
            metadata=data.get("metadata", {}),
        )
