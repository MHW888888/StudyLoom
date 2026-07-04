from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(value)]


@dataclass(frozen=True)
class LearnerProfile:
    goal: str = "Build a source-grounded learning pack."
    current_level: str = "beginner"
    time_budget: str = "not specified"
    preferred_style: str = "clear, structured, evidence-grounded"
    output_depth: str = "detailed"
    use_case: str = "self_study"
    deadline: str | None = None
    domain_background: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)
    must_include: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "current_level": self.current_level,
            "time_budget": self.time_budget,
            "preferred_style": self.preferred_style,
            "output_depth": self.output_depth,
            "use_case": self.use_case,
            "deadline": self.deadline,
            "domain_background": self.domain_background,
            "avoid": self.avoid,
            "must_include": self.must_include,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnerProfile":
        return cls(
            goal=str(data.get("goal") or cls.goal),
            current_level=str(data.get("current_level") or data.get("level") or "beginner"),
            time_budget=str(data.get("time_budget") or "not specified"),
            preferred_style=str(data.get("preferred_style") or data.get("style") or "clear, structured, evidence-grounded"),
            output_depth=str(data.get("output_depth") or "detailed"),
            use_case=str(data.get("use_case") or "self_study"),
            deadline=data.get("deadline"),
            domain_background=_as_list(data.get("domain_background")),
            avoid=_as_list(data.get("avoid")),
            must_include=_as_list(data.get("must_include")),
        )

    @classmethod
    def from_json_file(cls, path: Path) -> "LearnerProfile":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def merge_overrides(
        self,
        goal: str | None = None,
        level: str | None = None,
        time_budget: str | None = None,
        use_case: str | None = None,
        style: str | None = None,
        must_include: list[str] | None = None,
        avoid: list[str] | None = None,
    ) -> "LearnerProfile":
        return LearnerProfile(
            goal=goal or self.goal,
            current_level=level or self.current_level,
            time_budget=time_budget or self.time_budget,
            preferred_style=style or self.preferred_style,
            output_depth=self.output_depth,
            use_case=use_case or self.use_case,
            deadline=self.deadline,
            domain_background=list(self.domain_background),
            avoid=_as_list(avoid) or list(self.avoid),
            must_include=_as_list(must_include) or list(self.must_include),
        )


def default_profile() -> LearnerProfile:
    return LearnerProfile()
