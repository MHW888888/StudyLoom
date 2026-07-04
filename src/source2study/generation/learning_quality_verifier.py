from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from source2study.knowledge.concept_graph import ConceptGraph
from source2study.models.study_pack import StudyPack
from source2study.personalization.learner_profile import LearnerProfile
from source2study.personalization.pack_spec import LearningPackSpec


@dataclass(frozen=True)
class LearningQualityIssue:
    level: str
    type: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"level": self.level, "type": self.type, "message": self.message}


@dataclass(frozen=True)
class LearningQualityReport:
    status: str
    persona_fit: float
    difficulty_fit: float
    citation_coverage: float
    concept_coverage: float
    engagement_score: float
    issues: list[LearningQualityIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.status != "fail"

    @property
    def errors(self) -> list[str]:
        return [issue.message for issue in self.issues if issue.level == "error"]

    @property
    def warnings(self) -> list[str]:
        return [issue.message for issue in self.issues if issue.level == "warning"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "persona_fit": self.persona_fit,
            "difficulty_fit": self.difficulty_fit,
            "citation_coverage": self.citation_coverage,
            "concept_coverage": self.concept_coverage,
            "engagement_score": self.engagement_score,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path


class LearningQualityVerifier:
    def verify(
        self,
        pack: StudyPack,
        profile: LearnerProfile,
        spec: LearningPackSpec,
        graph: ConceptGraph,
    ) -> LearningQualityReport:
        issues: list[LearningQualityIssue] = []
        body = "\n".join(section.title + "\n" + section.body for section in pack.sections).lower()
        section_titles = [section.title.lower() for section in pack.sections]

        if not graph.nodes:
            issues.append(LearningQualityIssue("error", "empty_concept_graph", "Concept graph is empty."))
        if not any("map" in title for title in section_titles):
            issues.append(LearningQualityIssue("error", "missing_learning_map", "Pack is missing a learning map."))
        if not any("appendix" in title for title in section_titles):
            issues.append(LearningQualityIssue("error", "missing_source_appendix", "Pack is missing a source appendix."))
        if spec.quiz_required and "quiz" not in body and "question" not in body:
            issues.append(LearningQualityIssue("error", "missing_quiz", "Persona spec requires a quiz or questions."))
        if spec.practice_required and "practice" not in body and "task" not in body and "homework" not in body:
            issues.append(LearningQualityIssue("error", "missing_practice", "Persona spec requires a practice task."))
        if profile.current_level.lower() in {"beginner", "zero", "new"} and "prerequisite" not in body:
            issues.append(LearningQualityIssue("warning", "missing_prerequisite_patch", "Beginner profile should include prerequisite support."))

        persona_fit = self._persona_fit(profile, spec)
        difficulty_fit = 1.0 if profile.current_level.lower() not in {"beginner", "zero", "new"} or "prerequisite" in body else 0.65
        citation_coverage = self._citation_coverage(pack)
        concept_coverage = self._concept_coverage(body, graph)
        engagement_score = self._engagement_score(body, spec)

        if citation_coverage < 1.0:
            issues.append(LearningQualityIssue("error", "citation_gap", "Every section should carry evidence references."))
        if concept_coverage < 0.6:
            issues.append(LearningQualityIssue("warning", "low_concept_coverage", "Too few extracted concepts appear in the pack."))
        if engagement_score < 0.5:
            issues.append(LearningQualityIssue("warning", "low_engagement", "Pack has weak quiz/practice/reflection support."))

        errors = sum(1 for issue in issues if issue.level == "error")
        warnings = sum(1 for issue in issues if issue.level == "warning")
        status = "fail" if errors else "warn" if warnings else "pass"
        return LearningQualityReport(
            status=status,
            persona_fit=persona_fit,
            difficulty_fit=difficulty_fit,
            citation_coverage=citation_coverage,
            concept_coverage=concept_coverage,
            engagement_score=engagement_score,
            issues=issues,
        )

    def _persona_fit(self, profile: LearnerProfile, spec: LearningPackSpec) -> float:
        use_case = profile.use_case.lower()
        if spec.persona in use_case or use_case in {spec.persona, "self_study"}:
            return 0.9
        return 0.75

    def _citation_coverage(self, pack: StudyPack) -> float:
        if not pack.sections:
            return 0.0
        covered = sum(1 for section in pack.sections if section.evidence_ids)
        return covered / len(pack.sections)

    def _concept_coverage(self, body: str, graph: ConceptGraph) -> float:
        if not graph.nodes:
            return 0.0
        covered = sum(1 for node in graph.nodes if node.concept.lower() in body)
        return covered / len(graph.nodes)

    def _engagement_score(self, body: str, spec: LearningPackSpec) -> float:
        signals = ["quiz", "question", "practice", "task", "reflection", "checkpoint", "homework"]
        score = sum(1 for signal in signals if signal in body) / 4
        if spec.engagement_devices:
            score += 0.15
        return min(score, 1.0)
