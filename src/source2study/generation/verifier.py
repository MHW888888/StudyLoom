from __future__ import annotations

from dataclasses import dataclass, field

from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.study_pack import StudyPack


@dataclass(frozen=True)
class VerificationReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class StudyPackVerifier:
    def verify(self, pack: StudyPack, index: EvidenceIndex) -> VerificationReport:
        errors: list[str] = []
        warnings: list[str] = []
        if not index.sources:
            errors.append("source ledger is empty")
        if not index.evidence:
            errors.append("evidence ledger is empty")
        for section in pack.sections:
            if not section.evidence_ids:
                errors.append(f"section '{section.title}' has no evidence references")
        missing = index.validate_references(pack.evidence_ids())
        if missing:
            errors.append(f"missing evidence references: {', '.join(missing)}")
        if any(record.confidence < 0.75 for record in index.evidence.values()):
            warnings.append("low-confidence evidence is present")
        return VerificationReport(ok=not errors, errors=errors, warnings=warnings)
