from __future__ import annotations

from source2study.design.layout_blocks import LearningBlockRenderer
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.knowledge.concept_graph import ConceptGraph, ConceptGraphBuilder
from source2study.models.study_pack import StudyMode, StudyPack, StudySection
from source2study.personalization.learner_profile import LearnerProfile
from source2study.personalization.pack_spec import LearningPackSpec, LearningPackSpecBuilder


class PersonalizedStudyPackWriter:
    def __init__(self) -> None:
        self.spec_builder = LearningPackSpecBuilder()
        self.graph_builder = ConceptGraphBuilder()
        self.blocks = LearningBlockRenderer()

    def build(self, index: EvidenceIndex, mode: StudyMode, profile: LearnerProfile, language: str = "zh") -> StudyPack:
        if not index.evidence:
            raise ValueError("Cannot generate a study pack without evidence records.")
        graph = self.graph_builder.build(index)
        spec = self.spec_builder.build(profile, mode)
        evidence_ids = self._section_evidence(graph, index)
        sections = self._sections(index, graph, spec, profile, evidence_ids)
        limitations = []
        if any(record.confidence < 0.75 for record in index.evidence.values()):
            limitations.append("Some evidence has low confidence and should be reviewed manually.")
        title = self._title(index, spec, profile)
        return StudyPack(
            title=title,
            mode=mode,
            language=language,
            sections=sections,
            limitations=limitations,
            metadata={
                "learner_profile": profile.to_dict(),
                "learning_pack_spec": spec.to_dict(),
                "concept_graph": graph.to_dict(),
                "personalized": True,
            },
        )

    def _sections(
        self,
        index: EvidenceIndex,
        graph: ConceptGraph,
        spec: LearningPackSpec,
        profile: LearnerProfile,
        evidence_ids: list[str],
    ) -> list[StudySection]:
        sections: list[StudySection] = []
        for item in spec.structure:
            body = self._body(item, index, graph, spec, profile)
            sections.append(StudySection(title=item, body=body, evidence_ids=evidence_ids))
        return sections

    def _body(
        self,
        item: str,
        index: EvidenceIndex,
        graph: ConceptGraph,
        spec: LearningPackSpec,
        profile: LearnerProfile,
    ) -> str:
        normalized = item.lower()
        if "outcome" in normalized:
            return self.blocks.learning_outcomes(profile, graph)
        if "map" in normalized:
            return self.blocks.learning_map(spec, graph)
        if "prerequisite" in normalized:
            return self.blocks.prerequisite_patch(graph)
        if "concept" in normalized or "definition" in normalized:
            return self.blocks.concept_cards(graph, index)
        if "misconception" in normalized or "trap" in normalized:
            return self.blocks.misconception_box(graph)
        if "quiz" in normalized or "question" in normalized or "answer" in normalized:
            return self.blocks.quiz_block(graph, index)
        if "practice" in normalized or "project" in normalized or "homework" in normalized:
            return self.blocks.practice_task(spec, graph)
        if "evidence" in normalized or "source comparison" in normalized or "code" in normalized:
            return self.blocks.evidence_cards(graph, index)
        if "summary" in normalized or "high-frequency" in normalized:
            return self.blocks.summary_sheet(graph)
        if "appendix" in normalized:
            return self.blocks.source_appendix(index)
        if "hook" in normalized:
            top = graph.nodes[0].concept if graph.nodes else "this topic"
            return f"Opening hook: Why does `{top}` matter for {profile.goal}? Start with the learner's problem, then reveal the source-backed answer."
        if "debug" in normalized:
            return "Debug checklist:\n- Re-check source evidence.\n- Identify the exact concept that failed.\n- Compare your result against the practice task."
        if "storyline" in normalized:
            return "Storyline:\n1. Start with the problem.\n2. Introduce the key concept.\n3. Show one evidence-backed example.\n4. End with a checkpoint question."
        if "open question" in normalized:
            return "Open questions:\n- Which claims need deeper sources?\n- Which concepts require a stronger prerequisite patch?\n- Which evidence records are low confidence?"
        return self.blocks.evidence_cards(graph, index)

    def _section_evidence(self, graph: ConceptGraph, index: EvidenceIndex) -> list[str]:
        ids = graph.evidence_ids()
        if ids:
            return ids[:8]
        return list(index.evidence.keys())[:4]

    def _title(self, index: EvidenceIndex, spec: LearningPackSpec, profile: LearnerProfile) -> str:
        source_titles = [source.title for source in index.sources.values()]
        topic = source_titles[0] if source_titles else "Source2Study"
        suffix = " and related sources" if len(source_titles) > 1 else ""
        return f"{topic}{suffix} - {spec.pack_type} for {profile.use_case}"
