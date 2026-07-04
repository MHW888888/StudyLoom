from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from source2study.indexing.evidence_index import EvidenceIndex


STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "between",
    "could",
    "every",
    "from",
    "have",
    "into",
    "learning",
    "notes",
    "only",
    "source",
    "study",
    "that",
    "their",
    "there",
    "this",
    "through",
    "user",
    "with",
    "without",
}

KNOWN_PHRASES = [
    "gradient descent",
    "learning rate",
    "loss function",
    "evidence index",
    "browser capture",
    "citation verifier",
    "study pack",
    "source ledger",
    "ocr text",
]


@dataclass(frozen=True)
class ConceptNode:
    concept: str
    importance: str
    difficulty: str
    prerequisites: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    common_misconceptions: list[str] = field(default_factory=list)
    recommended_treatment: str = "concept_card_with_evidence"

    def to_dict(self) -> dict[str, Any]:
        return {
            "concept": self.concept,
            "importance": self.importance,
            "difficulty": self.difficulty,
            "prerequisites": self.prerequisites,
            "evidence_ids": self.evidence_ids,
            "common_misconceptions": self.common_misconceptions,
            "recommended_treatment": self.recommended_treatment,
        }


@dataclass(frozen=True)
class ConceptGraph:
    nodes: list[ConceptNode]

    def to_dict(self) -> dict[str, Any]:
        return {"nodes": [node.to_dict() for node in self.nodes]}

    def evidence_ids(self) -> list[str]:
        ids: list[str] = []
        for node in self.nodes:
            ids.extend(node.evidence_ids)
        return list(dict.fromkeys(ids))


class ConceptGraphBuilder:
    def build(self, index: EvidenceIndex, limit: int = 8) -> ConceptGraph:
        phrase_counts: Counter[str] = Counter()
        evidence_by_concept: dict[str, list[str]] = defaultdict(list)
        for record in index.evidence.values():
            text = record.text.lower()
            for phrase in KNOWN_PHRASES:
                if phrase in text:
                    phrase_counts[phrase] += text.count(phrase)
                    evidence_by_concept[phrase].append(record.evidence_id)
            for term in self._terms(text):
                phrase_counts[term] += 1
                evidence_by_concept[term].append(record.evidence_id)

        nodes: list[ConceptNode] = []
        for rank, (concept, count) in enumerate(phrase_counts.most_common(limit), start=1):
            evidence_ids = list(dict.fromkeys(evidence_by_concept[concept]))[:4]
            nodes.append(
                ConceptNode(
                    concept=concept,
                    importance="core" if rank <= 3 else "supporting",
                    difficulty=self._difficulty(concept, count),
                    prerequisites=self._prerequisites(concept),
                    evidence_ids=evidence_ids,
                    common_misconceptions=self._misconceptions(concept),
                    recommended_treatment=self._treatment(concept),
                )
            )
        if not nodes and index.evidence:
            first = next(iter(index.evidence.values()))
            nodes.append(
                ConceptNode(
                    concept=first.source_type,
                    importance="core",
                    difficulty="low",
                    evidence_ids=[first.evidence_id],
                    common_misconceptions=["Assuming a generated summary is reliable without checking source evidence."],
                )
            )
        return ConceptGraph(nodes=nodes)

    def _terms(self, text: str) -> list[str]:
        words = re.findall(r"[a-z][a-z0-9_-]{3,}", text)
        return [word for word in words if word not in STOPWORDS][:80]

    def _difficulty(self, concept: str, count: int) -> str:
        if concept in {"gradient descent", "loss function", "citation verifier"}:
            return "medium"
        if len(concept) > 14 or count <= 1:
            return "medium"
        return "low"

    def _prerequisites(self, concept: str) -> list[str]:
        if concept == "gradient descent":
            return ["function", "derivative", "loss function"]
        if concept == "learning rate":
            return ["gradient descent", "iteration"]
        if concept == "loss function":
            return ["model prediction", "error"]
        if concept in {"browser capture", "evidence index", "citation verifier"}:
            return ["source ledger", "evidence record"]
        return ["source context"]

    def _misconceptions(self, concept: str) -> list[str]:
        if concept == "gradient descent":
            return [
                "Assuming gradient descent always finds the global optimum.",
                "Confusing learning rate with iteration count.",
            ]
        if concept == "browser capture":
            return ["Treating current-page capture as permission for account-history crawling."]
        if concept == "evidence index":
            return ["Assuming a claim is grounded when it has no evidence id."]
        return ["Skipping source evidence and treating generated notes as standalone truth."]

    def _treatment(self, concept: str) -> str:
        if concept in {"gradient descent", "learning rate", "loss function"}:
            return "visual_explanation_with_step_by_step_example"
        if concept in {"browser capture", "evidence index", "citation verifier"}:
            return "workflow_diagram_with_evidence_card"
        return "concept_card_with_example"
