from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.evidence import EvidenceRecord
from source2study.models.study_pack import StudyPack
from source2study.safety.redaction import find_secrets


@dataclass(frozen=True)
class CitationIssue:
    level: str
    type: str
    message: str
    section: str | None = None
    evidence_id: str | None = None
    source_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "type": self.type,
            "message": self.message,
            "section": self.section,
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
        }


@dataclass(frozen=True)
class CitationReport:
    status: str
    summary: dict[str, int]
    issues: list[CitationIssue] = field(default_factory=list)

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
            "summary": self.summary,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path


class CitationVerifier:
    def __init__(self, max_excerpt_chars: int = 500, public_max_excerpt_chars: int = 220):
        self.max_excerpt_chars = max_excerpt_chars
        self.public_max_excerpt_chars = public_max_excerpt_chars

    def verify(
        self,
        index: EvidenceIndex,
        pack: StudyPack | None = None,
        share_mode: str = "personal",
    ) -> CitationReport:
        issues: list[CitationIssue] = []
        cited_ids: list[str] = []
        section_count = 0
        unsupported_claims = 0
        copyright_warnings = 0

        if not index.sources:
            issues.append(CitationIssue("error", "empty_source_ledger", "Source ledger is empty."))
        if not index.evidence:
            issues.append(CitationIssue("error", "empty_evidence_ledger", "Evidence ledger is empty."))

        for record in index.evidence.values():
            issues.extend(self._check_record(record, index, share_mode))

        if pack is not None:
            section_count = len(pack.sections)
            for section in pack.sections:
                if not section.evidence_ids:
                    issues.append(
                        CitationIssue(
                            "error",
                            "section_without_evidence",
                            f"Section '{section.title}' has no evidence references.",
                            section=section.title,
                        )
                    )
                for evidence_id in section.evidence_ids:
                    cited_ids.append(evidence_id)
                    if evidence_id not in index.evidence:
                        issues.append(
                            CitationIssue(
                                "error",
                                "missing_evidence",
                                f"Citation {evidence_id} does not exist in EvidenceIndex.",
                                section=section.title,
                                evidence_id=evidence_id,
                            )
                        )
                unsupported_claims += self._count_unsupported_claims(section.body)

        for evidence_id in sorted(set(cited_ids)):
            record = index.evidence.get(evidence_id)
            if record is None:
                continue
            limit = self.public_max_excerpt_chars if share_mode == "public_share" else self.max_excerpt_chars
            if len(record.text) > limit:
                copyright_warnings += 1
                issues.append(
                    CitationIssue(
                        "warning",
                        "long_excerpt",
                        f"Citation {evidence_id} references text longer than {limit} characters.",
                        evidence_id=evidence_id,
                        source_id=record.source_id,
                    )
                )
            if share_mode == "public_share":
                status = record.rights.copyright_status.lower()
                if status in {"blocked", "restricted", "unknown"}:
                    issues.append(
                        CitationIssue(
                            "error",
                            "restricted_public_share",
                            f"Citation {evidence_id} has copyright status '{record.rights.copyright_status}' and cannot be used for public sharing.",
                            evidence_id=evidence_id,
                            source_id=record.source_id,
                        )
                    )

        if unsupported_claims:
            issues.append(
                CitationIssue(
                    "warning",
                    "unsupported_claims",
                    f"{unsupported_claims} claim-like sentence(s) do not contain inline evidence citations.",
                )
            )

        errors = sum(1 for issue in issues if issue.level == "error")
        warnings = sum(1 for issue in issues if issue.level == "warning")
        status = "fail" if errors else "warn" if warnings else "pass"
        summary = {
            "sections": section_count,
            "citations": len(cited_ids),
            "missing_citations": sum(1 for issue in issues if issue.type == "missing_evidence"),
            "unsupported_claims": unsupported_claims,
            "copyright_warnings": copyright_warnings,
            "errors": errors,
            "warnings": warnings,
        }
        return CitationReport(status=status, summary=summary, issues=issues)

    def _check_record(self, record: EvidenceRecord, index: EvidenceIndex, share_mode: str) -> list[CitationIssue]:
        issues: list[CitationIssue] = []
        if not record.evidence_id:
            issues.append(CitationIssue("error", "missing_evidence_id", "Evidence record is missing evidence_id."))
        if not record.source_id or record.source_id not in index.sources:
            issues.append(
                CitationIssue(
                    "error",
                    "missing_source",
                    f"Evidence {record.evidence_id} references missing source {record.source_id}.",
                    evidence_id=record.evidence_id,
                    source_id=record.source_id,
                )
            )
        if not self._has_location(record):
            issues.append(
                CitationIssue(
                    "error",
                    "missing_location",
                    f"Evidence {record.evidence_id} has no timestamp, page, path, or section location.",
                    evidence_id=record.evidence_id,
                    source_id=record.source_id,
                )
            )
        if find_secrets(record.text):
            issues.append(
                CitationIssue(
                    "error",
                    "secret_in_evidence",
                    f"Evidence {record.evidence_id} appears to contain a secret.",
                    evidence_id=record.evidence_id,
                    source_id=record.source_id,
                )
            )
        if record.confidence < 0.75:
            issues.append(
                CitationIssue(
                    "warning",
                    "low_confidence_evidence",
                    f"Evidence {record.evidence_id} has low confidence and should not be treated as a strong fact.",
                    evidence_id=record.evidence_id,
                    source_id=record.source_id,
                )
            )
        if share_mode == "public_share" and record.media.screenshot_path:
            issues.append(
                CitationIssue(
                    "warning",
                    "screenshot_public_share_review",
                    f"Screenshot for {record.evidence_id} requires rights review before public sharing.",
                    evidence_id=record.evidence_id,
                    source_id=record.source_id,
                )
            )
        return issues

    def _has_location(self, record: EvidenceRecord) -> bool:
        location = record.location
        return any(
            [
                location.timestamp_start or location.timestamp_end,
                location.page is not None,
                location.path,
                location.section,
            ]
        )

    def _count_unsupported_claims(self, body: str) -> int:
        count = 0
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(
                (
                    "-",
                    "Purpose:",
                    "Generator note:",
                    "Evidence:",
                    "Goal:",
                    "Current level:",
                    "Time budget:",
                    "After this pack",
                    "Learning route:",
                    "Retrieval rule:",
                    "Practice task:",
                    "Creator task:",
                    "Storyline:",
                    "Debug checklist:",
                    "Open questions:",
                )
            ):
                continue
            if re.search(r"\bev_[A-Za-z0-9_]+\b", stripped):
                continue
            for sentence in re.split(r"(?<=[.!?。！？])\s+", stripped):
                sentence = sentence.strip()
                if not sentence:
                    continue
                if re.search(r"\b(is|are|must|should|will|cannot|can)\b", sentence, flags=re.IGNORECASE):
                    count += 1
        return count
