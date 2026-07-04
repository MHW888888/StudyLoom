from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from source2study.models.evidence import EvidenceRecord
from source2study.models.source import SourceRecord


@dataclass
class EvidenceIndex:
    sources: dict[str, SourceRecord] = field(default_factory=dict)
    evidence: dict[str, EvidenceRecord] = field(default_factory=dict)

    def add_source(self, source: SourceRecord) -> None:
        self.sources[source.source_id] = source

    def add_evidence(self, record: EvidenceRecord) -> None:
        if record.source_id not in self.sources:
            raise ValueError(f"Evidence {record.evidence_id} references unknown source {record.source_id}")
        self.evidence[record.evidence_id] = record

    def add_records(self, source: SourceRecord, records: list[EvidenceRecord]) -> None:
        self.add_source(source)
        for record in records:
            self.add_evidence(record)

    def search(self, query: str, limit: int = 8) -> list[EvidenceRecord]:
        terms = [term.lower() for term in query.split() if term.strip()]
        if not terms:
            return list(self.evidence.values())[:limit]
        scored: list[tuple[int, EvidenceRecord]] = []
        for record in self.evidence.values():
            text = record.text.lower()
            score = sum(text.count(term) for term in terms)
            if score:
                scored.append((score, record))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [record for _, record in scored[:limit]]

    def validate_references(self, evidence_ids: set[str]) -> list[str]:
        return sorted(evidence_id for evidence_id in evidence_ids if evidence_id not in self.evidence)

    def to_dict(self) -> dict:
        return {
            "sources": [source.to_dict() for source in self.sources.values()],
            "evidence": [record.to_dict() for record in self.evidence.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EvidenceIndex":
        index = cls()
        for source_data in data.get("sources", []):
            index.add_source(SourceRecord.from_dict(source_data))
        for evidence_data in data.get("evidence", []):
            index.add_evidence(EvidenceRecord.from_dict(evidence_data))
        return index

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def read(cls, path: Path) -> "EvidenceIndex":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))
