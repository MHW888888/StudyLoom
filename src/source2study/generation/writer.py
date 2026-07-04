from __future__ import annotations

from source2study.generation.personalized_writer import PersonalizedStudyPackWriter
from source2study.generation.planner import section_plan
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.evidence import EvidenceRecord
from source2study.models.study_pack import StudyMode, StudyPack, StudySection
from source2study.personalization.learner_profile import LearnerProfile, default_profile


class StudyPackWriter:
    def build(self, index: EvidenceIndex, mode: StudyMode, language: str = "zh", profile: LearnerProfile | None = None) -> StudyPack:
        if profile is not None:
            return PersonalizedStudyPackWriter().build(index, mode=mode, profile=profile, language=language)
        if mode in {
            StudyMode.REVIEW,
            StudyMode.DEVELOPER,
            StudyMode.CREATOR,
            StudyMode.RESEARCH,
        }:
            return PersonalizedStudyPackWriter().build(index, mode=mode, profile=default_profile(), language=language)
        if not index.evidence:
            raise ValueError("Cannot generate a study pack without evidence records.")

        all_evidence = list(index.evidence.values())
        title = self._title(index, mode)
        sections: list[StudySection] = []
        for title_part, purpose in section_plan(mode):
            selected = self._select_evidence(all_evidence, purpose, limit=4)
            sections.append(self._section(title_part, purpose, selected, mode))

        limitations = []
        if any(record.confidence < 0.75 for record in all_evidence):
            limitations.append("Some evidence has low confidence and should be reviewed manually.")
        return StudyPack(title=title, mode=mode, language=language, sections=sections, limitations=limitations)

    def _title(self, index: EvidenceIndex, mode: StudyMode) -> str:
        source_titles = [source.title for source in index.sources.values()]
        if not source_titles:
            return f"Source2Study {mode.value} Pack"
        first = source_titles[0]
        suffix = " and related sources" if len(source_titles) > 1 else ""
        return f"{first}{suffix} - {mode.value}"

    def _select_evidence(self, evidence: list[EvidenceRecord], purpose: str, limit: int) -> list[EvidenceRecord]:
        terms = purpose.lower().split()
        scored = []
        for record in evidence:
            text = record.text.lower()
            score = sum(1 for term in terms if term in text)
            scored.append((score, record))
        scored.sort(key=lambda item: (item[0], item[1].confidence), reverse=True)
        selected = [record for _, record in scored[:limit]]
        return selected or evidence[:limit]

    def _section(
        self,
        title: str,
        purpose: str,
        evidence: list[EvidenceRecord],
        mode: StudyMode,
    ) -> StudySection:
        evidence_lines = []
        for record in evidence:
            summary = record.text.strip().replace("\n", " ")
            if len(summary) > 260:
                summary = summary[:257].rstrip() + "..."
            evidence_lines.append(f"- {summary} [{record.citation()}]")

        if mode == StudyMode.BEGINNER_FULL:
            lead = "Start from the source-backed basics before adding extra theory."
        elif mode == StudyMode.DEEP_ANALYSIS:
            lead = "Use the evidence below as the traceable base for deeper comparison."
        else:
            lead = "Use these evidence-backed points as the working notes."
        body = f"Generator note: {lead}\n\nPurpose: {purpose}.\n\n" + "\n".join(evidence_lines)
        return StudySection(title=title, body=body, evidence_ids=[record.evidence_id for record in evidence])
