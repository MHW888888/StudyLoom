from __future__ import annotations

from dataclasses import dataclass, field

from source2study.generation.citation_verifier import CitationVerifier
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.study_pack import StudyPack
from source2study.safety.redaction import find_secrets


@dataclass(frozen=True)
class QualityReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, int] = field(default_factory=dict)


def validate_index(index: EvidenceIndex, pack: StudyPack | None = None, share_mode: str = "personal") -> QualityReport:
    errors: list[str] = []
    warnings: list[str] = []
    if not index.sources:
        errors.append("source ledger is empty")
    if not index.evidence:
        errors.append("evidence ledger is empty")
    for record in index.evidence.values():
        if record.source_id not in index.sources:
            errors.append(f"evidence {record.evidence_id} references missing source {record.source_id}")
        if record.confidence < 0.75:
            warnings.append(f"evidence {record.evidence_id} has low confidence")
        if find_secrets(record.text):
            errors.append(f"evidence {record.evidence_id} appears to contain a secret")
    metrics = {
        "sources_processed": len(index.sources),
        "evidence_records": len(index.evidence),
        "transcript_chars": sum(len(record.text) for record in index.evidence.values()),
    }
    citation_report = CitationVerifier().verify(index, pack=pack, share_mode=share_mode)
    for issue in citation_report.issues:
        if issue.level == "error":
            errors.append(issue.message)
        elif issue.level == "warning":
            warnings.append(issue.message)
    metrics.update(citation_report.summary)
    return QualityReport(ok=not errors, errors=errors, warnings=warnings, metrics=metrics)
