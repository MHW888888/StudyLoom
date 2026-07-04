from __future__ import annotations

import json
from pathlib import Path

from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.evidence import EvidenceRecord
from source2study.models.source import SourceRecord


def ensure_workspace(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / "sources").mkdir(exist_ok=True)
    (path / "outputs").mkdir(exist_ok=True)
    (path / ".source2study").mkdir(exist_ok=True)
    return path


def index_path(workspace: Path) -> Path:
    return workspace / "evidence_index.json"


def source_ledger_path(workspace: Path) -> Path:
    return workspace / "source_ledger.json"


def evidence_ledger_path(workspace: Path) -> Path:
    return workspace / "evidence_ledger.json"


def pack_json_path(workspace: Path, mode: str) -> Path:
    return workspace / "outputs" / f"study_pack_{mode}.json"


def citation_report_path(workspace: Path, mode: str | None = None) -> Path:
    suffix = f"_{mode}" if mode else ""
    return workspace / "outputs" / f"citation_report{suffix}.json"


def learning_quality_report_path(workspace: Path, mode: str | None = None) -> Path:
    suffix = f"_{mode}" if mode else ""
    return workspace / "outputs" / f"learning_quality_report{suffix}.json"


def load_index(workspace: Path) -> EvidenceIndex:
    path = index_path(workspace)
    if path.exists():
        return EvidenceIndex.read(path)
    sources_file = source_ledger_path(workspace)
    evidence_file = evidence_ledger_path(workspace)
    index = EvidenceIndex()
    if sources_file.exists():
        for source_data in json.loads(sources_file.read_text(encoding="utf-8")):
            index.add_source(SourceRecord.from_dict(source_data))
    if evidence_file.exists():
        for evidence_data in json.loads(evidence_file.read_text(encoding="utf-8")):
            index.add_evidence(EvidenceRecord.from_dict(evidence_data))
    return index


def write_ledgers(workspace: Path, index: EvidenceIndex) -> None:
    ensure_workspace(workspace)
    source_ledger_path(workspace).write_text(
        json.dumps([source.to_dict() for source in index.sources.values()], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    evidence_ledger_path(workspace).write_text(
        json.dumps([record.to_dict() for record in index.evidence.values()], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    index.write(index_path(workspace))
