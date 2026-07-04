from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


IntakeStatus = Literal["pass", "degraded", "fail", "blocked"]


@dataclass(frozen=True)
class DetectedAssets:
    text_blocks: int = 0
    images: int = 0
    tables: int = 0
    slides: int = 0
    speaker_notes: int = 0
    video_segments: int = 0
    transcript_segments: int = 0
    screenshots: int = 0
    ocr_regions: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "text_blocks": self.text_blocks,
            "images": self.images,
            "tables": self.tables,
            "slides": self.slides,
            "speaker_notes": self.speaker_notes,
            "video_segments": self.video_segments,
            "transcript_segments": self.transcript_segments,
            "screenshots": self.screenshots,
            "ocr_regions": self.ocr_regions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DetectedAssets":
        return cls(**{field_name: int(data.get(field_name, 0) or 0) for field_name in cls().to_dict()})


@dataclass(frozen=True)
class ExtractionQuality:
    text: str = "not_available"
    images: str = "not_supported"
    tables: str = "not_supported"
    layout: str = "not_supported"
    ocr: str = "not_needed"
    transcript: str = "not_needed"

    def to_dict(self) -> dict[str, str]:
        return {
            "text": self.text,
            "images": self.images,
            "tables": self.tables,
            "layout": self.layout,
            "ocr": self.ocr,
            "transcript": self.transcript,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExtractionQuality":
        return cls(
            text=str(data.get("text", "not_available")),
            images=str(data.get("images", "not_supported")),
            tables=str(data.get("tables", "not_supported")),
            layout=str(data.get("layout", "not_supported")),
            ocr=str(data.get("ocr", "not_needed")),
            transcript=str(data.get("transcript", "not_needed")),
        )


@dataclass(frozen=True)
class IntakeReport:
    source_id: str
    source_type: str
    source_path_or_url: str
    source_title: str
    status: IntakeStatus
    detected_assets: DetectedAssets = field(default_factory=DetectedAssets)
    extraction_quality: ExtractionQuality = field(default_factory=ExtractionQuality)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    fallback_options: list[str] = field(default_factory=list)
    next_safe_actions: list[str] = field(default_factory=list)
    created_at: str = ""

    @property
    def ok_for_generation(self) -> bool:
        return self.status in {"pass", "degraded"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "source_path_or_url": self.source_path_or_url,
            "source_title": self.source_title,
            "status": self.status,
            "detected_assets": self.detected_assets.to_dict(),
            "extraction_quality": self.extraction_quality.to_dict(),
            "warnings": self.warnings,
            "errors": self.errors,
            "fallback_options": self.fallback_options,
            "next_safe_actions": self.next_safe_actions,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IntakeReport":
        return cls(
            source_id=data["source_id"],
            source_type=data["source_type"],
            source_path_or_url=data["source_path_or_url"],
            source_title=data.get("source_title", data["source_id"]),
            status=data.get("status", "fail"),
            detected_assets=DetectedAssets.from_dict(data.get("detected_assets", {})),
            extraction_quality=ExtractionQuality.from_dict(data.get("extraction_quality", {})),
            warnings=list(data.get("warnings", [])),
            errors=list(data.get("errors", [])),
            fallback_options=list(data.get("fallback_options", [])),
            next_safe_actions=list(data.get("next_safe_actions", [])),
            created_at=str(data.get("created_at", "")),
        )
