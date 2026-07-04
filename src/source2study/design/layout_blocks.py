from __future__ import annotations

from source2study.indexing.evidence_index import EvidenceIndex
from source2study.knowledge.concept_graph import ConceptGraph, ConceptNode
from source2study.personalization.learner_profile import LearnerProfile
from source2study.personalization.pack_spec import LearningPackSpec


class LearningBlockRenderer:
    def learning_outcomes(self, profile: LearnerProfile, graph: ConceptGraph) -> str:
        concepts = ", ".join(node.concept for node in graph.nodes[:5]) or "the core source ideas"
        return "\n".join(
            [
                f"Goal: {profile.goal}",
                f"Current level: {profile.current_level}",
                f"Time budget: {profile.time_budget}",
                "",
                "After this pack, you should be able to:",
                f"1. Explain the core ideas: {concepts}.",
                "2. Point each major claim back to source evidence.",
                "3. Answer checkpoint questions without rereading the whole source.",
                "4. Choose a concrete next action for study, review, teaching, or practice.",
            ]
        )

    def learning_map(self, spec: LearningPackSpec, graph: ConceptGraph) -> str:
        nodes = graph.nodes[:5]
        if not nodes:
            return "Learning map is unavailable because no concepts were extracted."
        lines = ["Learning route:"]
        for index, node in enumerate(nodes, start=1):
            lines.append(f"{index}. {node.concept.title()} - {node.importance}, difficulty={node.difficulty}")
        lines.append("")
        lines.append("Use this map as a sequence, not as a pile of summaries.")
        return "\n".join(lines)

    def prerequisite_patch(self, graph: ConceptGraph) -> str:
        prereqs = []
        for node in graph.nodes[:5]:
            for item in node.prerequisites:
                if item not in prereqs:
                    prereqs.append(item)
        if not prereqs:
            return "No explicit prerequisite patch was detected."
        return "Before the main content, patch these prerequisites:\n" + "\n".join(f"- {item}" for item in prereqs)

    def concept_cards(self, graph: ConceptGraph, index: EvidenceIndex) -> str:
        cards = []
        for node in graph.nodes[:5]:
            cards.append(self.concept_card(node, index))
        return "\n\n".join(cards)

    def concept_card(self, node: ConceptNode, index: EvidenceIndex) -> str:
        evidence = self._evidence_lines(node.evidence_ids, index, limit=3)
        misconceptions = "\n".join(f"- {item}" for item in node.common_misconceptions[:2])
        return "\n".join(
            [
                f"Concept: {node.concept.title()}",
                f"Importance: {node.importance}",
                f"Difficulty: {node.difficulty}",
                f"Recommended treatment: {node.recommended_treatment}",
                "Prerequisites: " + (", ".join(node.prerequisites) if node.prerequisites else "none detected"),
                "",
                "Common misconceptions:",
                misconceptions or "- Not detected from the current evidence.",
                "",
                "Source evidence:",
                evidence,
            ]
        )

    def misconception_box(self, graph: ConceptGraph) -> str:
        lines = ["Common traps to watch:"]
        for node in graph.nodes[:5]:
            for item in node.common_misconceptions[:1]:
                lines.append(f"- {node.concept.title()}: {item}")
        return "\n".join(lines)

    def quiz_block(self, graph: ConceptGraph, index: EvidenceIndex) -> str:
        lines = ["Checkpoint quiz:"]
        for idx, node in enumerate(graph.nodes[:4], start=1):
            citation = node.evidence_ids[0] if node.evidence_ids else "not_verified"
            lines.append(f"{idx}. Explain `{node.concept}` in one sentence. Check against `{citation}`.")
        lines.append("")
        lines.append("Retrieval rule: answer before looking back at the evidence.")
        return "\n".join(lines)

    def practice_task(self, spec: LearningPackSpec, graph: ConceptGraph) -> str:
        top = graph.nodes[0].concept if graph.nodes else "the main concept"
        if spec.persona == "developer":
            return "\n".join(
                [
                    "Practice task:",
                    f"- Build a minimal demo that uses `{top}`.",
                    "- Write down the expected input, output, and one failure case.",
                    "- Verify your explanation against the cited evidence before extending it.",
                ]
            )
        if spec.persona == "creator":
            return "\n".join(
                [
                    "Creator task:",
                    f"- Turn `{top}` into a 60-second explanation.",
                    "- Start with a problem, show one example, then cite the source appendix.",
                ]
            )
        return "\n".join(
            [
                "Practice task:",
                f"- Teach `{top}` to an imaginary beginner.",
                "- Then answer the checkpoint quiz without rereading the notes.",
            ]
        )

    def evidence_cards(self, graph: ConceptGraph, index: EvidenceIndex) -> str:
        ids = []
        for node in graph.nodes[:5]:
            ids.extend(node.evidence_ids[:2])
        return self._evidence_lines(list(dict.fromkeys(ids)), index, limit=8)

    def source_appendix(self, index: EvidenceIndex) -> str:
        lines = ["Sources:"]
        for source in index.sources.values():
            lines.append(f"- `{source.source_id}`: {source.title} ({source.source_type}, {source.platform})")
        lines.append("")
        lines.append("Evidence index:")
        for record in list(index.evidence.values())[:20]:
            lines.append(f"- `{record.evidence_id}`: {record.location.label()}, confidence={record.confidence:.2f}")
        return "\n".join(lines)

    def summary_sheet(self, graph: ConceptGraph) -> str:
        lines = ["One-page review:"]
        for node in graph.nodes[:7]:
            lines.append(f"- {node.concept.title()}: {node.importance}, {node.difficulty}; prerequisites: {', '.join(node.prerequisites)}")
        return "\n".join(lines)

    def _evidence_lines(self, evidence_ids: list[str], index: EvidenceIndex, limit: int) -> str:
        lines = []
        for evidence_id in evidence_ids[:limit]:
            record = index.evidence.get(evidence_id)
            if record is None:
                continue
            excerpt = record.text.strip().replace("\n", " ")
            if len(excerpt) > 220:
                excerpt = excerpt[:217].rstrip() + "..."
            lines.append(f"- {excerpt} [{record.citation()}]")
        return "\n".join(lines) if lines else "- No evidence available."
