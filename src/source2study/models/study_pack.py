from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StudyMode(str, Enum):
    BEGINNER_FULL = "beginner_full"
    QUICK_FRAMEWORK = "quick_framework"
    DEEP_ANALYSIS = "deep_analysis"
    EXAM_REVIEW = "exam_review"
    PROJECT_PRACTICE = "project_practice"
    TEACHER_NOTES = "teacher_notes"
    REVIEW = "review"
    DEVELOPER = "developer"
    CREATOR = "creator"
    RESEARCH = "research"


MODE_ALIASES = {
    "beginner": StudyMode.BEGINNER_FULL,
    "beginner_full": StudyMode.BEGINNER_FULL,
    "framework": StudyMode.QUICK_FRAMEWORK,
    "quick_framework": StudyMode.QUICK_FRAMEWORK,
    "deep-dive": StudyMode.DEEP_ANALYSIS,
    "deep_analysis": StudyMode.DEEP_ANALYSIS,
    "review": StudyMode.REVIEW,
    "exam": StudyMode.EXAM_REVIEW,
    "exam_review": StudyMode.EXAM_REVIEW,
    "project": StudyMode.PROJECT_PRACTICE,
    "project_practice": StudyMode.PROJECT_PRACTICE,
    "developer": StudyMode.DEVELOPER,
    "creator": StudyMode.CREATOR,
    "research": StudyMode.RESEARCH,
    "teacher-notes": StudyMode.TEACHER_NOTES,
    "teacher_notes": StudyMode.TEACHER_NOTES,
}


def resolve_mode(value: str) -> StudyMode:
    try:
        return MODE_ALIASES[value]
    except KeyError as exc:
        valid = ", ".join(sorted(MODE_ALIASES))
        raise ValueError(f"Unsupported mode '{value}'. Valid modes: {valid}") from exc


@dataclass(frozen=True)
class StudySection:
    title: str
    body: str
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "body": self.body, "evidence_ids": self.evidence_ids}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StudySection":
        return cls(title=data["title"], body=data["body"], evidence_ids=data.get("evidence_ids", []))


@dataclass(frozen=True)
class StudyPack:
    title: str
    mode: StudyMode
    language: str
    sections: list[StudySection]
    limitations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def evidence_ids(self) -> set[str]:
        ids: set[str] = set()
        for section in self.sections:
            ids.update(section.evidence_ids)
        return ids

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "mode": self.mode.value,
            "language": self.language,
            "sections": [section.to_dict() for section in self.sections],
            "limitations": self.limitations,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StudyPack":
        mode_value = data.get("mode", StudyMode.BEGINNER_FULL.value)
        return cls(
            title=data["title"],
            mode=StudyMode(mode_value),
            language=data.get("language", "unknown"),
            sections=[StudySection.from_dict(section) for section in data.get("sections", [])],
            limitations=data.get("limitations", []),
            metadata=data.get("metadata", {}),
        )
