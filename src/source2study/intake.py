from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from source2study.adapters.base import AdapterResult
from source2study.adapters.utils import stable_id, utc_now
from source2study.models.intake_report import DetectedAssets, ExtractionQuality, IntakeReport
from source2study.models.source import SourceRecord


LOW_CONFIDENCE_THRESHOLD = 0.75


def intake_reports_dir(workspace: Path) -> Path:
    return workspace / "intake_reports"


def intake_summary_path(workspace: Path) -> Path:
    return workspace / "intake_report.json"


def report_from_adapter_result(result: AdapterResult, warnings: list[str] | None = None) -> IntakeReport:
    source = result.source
    evidence = result.evidence
    warning_items = _fidelity_warnings(list(warnings or []) + list(result.warnings))
    low_confidence = [record.evidence_id for record in evidence if record.confidence < LOW_CONFIDENCE_THRESHOLD]
    if low_confidence:
        warning_items.append("Low-confidence evidence detected: " + ", ".join(low_confidence[:5]))
    if source.source_type == "transcript":
        warning_items.append("Video body was not processed; this intake is based on user-provided transcript/subtitle segments.")
    if source.source_type == "document" and source.source_url_or_path.lower().endswith(".pdf"):
        warning_items.append("PDF images, tables, and layout are not fully parsed by the basic text extractor.")

    assets = _detected_assets(source, evidence)
    quality = _quality(source, evidence, assets)
    status = "degraded" if warning_items or low_confidence else "pass"
    return IntakeReport(
        source_id=source.source_id,
        source_type=source.source_type,
        source_path_or_url=source.source_url_or_path,
        source_title=source.title,
        status=status,
        detected_assets=assets,
        extraction_quality=quality,
        warnings=list(dict.fromkeys(warning_items)),
        fallback_options=_fallbacks(source),
        next_safe_actions=["build_evidence_index", "generate_learning_pack"],
        created_at=utc_now(),
    )


def blocked_report(source_value: str, source_type: str, reason: str, fallbacks: list[str]) -> IntakeReport:
    return IntakeReport(
        source_id=stable_id("src_blocked", source_value),
        source_type=source_type or "blocked_source",
        source_path_or_url=source_value,
        source_title=Path(source_value).name or source_value,
        status="blocked",
        warnings=[],
        errors=[reason],
        fallback_options=fallbacks,
        next_safe_actions=["provide_user_export", "upload_transcript_or_screenshot", "run_policy_check"],
        created_at=utc_now(),
    )


def failed_report(source_value: str, source_type: str, reason: str, fallbacks: list[str], *, degraded: bool = False) -> IntakeReport:
    status = "degraded" if degraded else "fail"
    return IntakeReport(
        source_id=stable_id("src_failed", source_value),
        source_type=source_type or "unknown",
        source_path_or_url=source_value,
        source_title=Path(source_value).name or source_value,
        status=status,
        warnings=[reason] if degraded else [],
        errors=[] if degraded else [reason],
        fallback_options=fallbacks,
        next_safe_actions=["provide_clearer_source", "upload_html_pdf_markdown_or_screenshot"],
        created_at=utc_now(),
    )


def write_intake_report(workspace: Path, report: IntakeReport) -> None:
    intake_reports_dir(workspace).mkdir(parents=True, exist_ok=True)
    (intake_reports_dir(workspace) / f"{report.source_id}.json").write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    reports = {item.source_id: item for item in load_intake_reports(workspace)}
    reports[report.source_id] = report
    write_intake_summary(workspace, list(reports.values()))


def load_intake_reports(workspace: Path) -> list[IntakeReport]:
    directory = intake_reports_dir(workspace)
    if not directory.exists():
        return []
    reports: list[IntakeReport] = []
    for path in sorted(directory.glob("*.json")):
        reports.append(IntakeReport.from_dict(json.loads(path.read_text(encoding="utf-8"))))
    return reports


def load_intake_summary(workspace: Path) -> dict[str, Any] | None:
    path = intake_summary_path(workspace)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_intake_summary(workspace: Path, reports: list[IntakeReport]) -> None:
    statuses = [report.status for report in reports]
    if any(status == "blocked" for status in statuses):
        status = "blocked"
    elif any(status == "fail" for status in statuses):
        status = "fail"
    elif any(status == "degraded" for status in statuses):
        status = "degraded"
    else:
        status = "pass"
    summary = {
        "status": status,
        "created_at": utc_now(),
        "source_count": len(reports),
        "warnings": [warning for report in reports for warning in report.warnings],
        "errors": [error for report in reports for error in report.errors],
        "next_safe_actions": sorted({action for report in reports for action in report.next_safe_actions}),
        "sources": [report.to_dict() for report in reports],
    }
    intake_summary_path(workspace).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def enforce_intake_gate(workspace: Path, *, allow_degraded: bool = False) -> dict[str, Any] | None:
    summary = load_intake_summary(workspace)
    if summary is None:
        return None
    status = summary.get("status")
    if status == "blocked":
        raise PermissionError("source intake is blocked: " + "; ".join(summary.get("errors", [])))
    if status == "fail" and not allow_degraded:
        raise ValueError("source intake failed; rerun with --allow-degraded only if you accept unreliable extraction.")
    return summary


def _detected_assets(source: SourceRecord, evidence) -> DetectedAssets:
    text_blocks = sum(1 for record in evidence if record.text.strip())
    screenshots = sum(1 for record in evidence if record.media.screenshot_path)
    ocr_regions = sum(1 for record in evidence if record.kind == "ocr" or record.metadata.get("ocr_confidence") is not None)
    transcript_segments = sum(1 for record in evidence if record.location.timestamp_start or record.source_type == "transcript")
    images = int(source.available_metadata.get("images_count") or screenshots)
    return DetectedAssets(
        text_blocks=text_blocks,
        images=images,
        tables=0,
        slides=0,
        speaker_notes=0,
        video_segments=0,
        transcript_segments=transcript_segments,
        screenshots=screenshots,
        ocr_regions=ocr_regions,
    )


def _quality(source: SourceRecord, evidence, assets: DetectedAssets) -> ExtractionQuality:
    min_confidence = min((record.confidence for record in evidence), default=0.0)
    text_quality = "high" if evidence and min_confidence >= 0.85 else "medium" if evidence else "not_available"
    if min_confidence < LOW_CONFIDENCE_THRESHOLD:
        text_quality = "low"
    ocr_quality = "not_needed"
    if assets.ocr_regions:
        ocr_quality = "high" if min_confidence >= 0.85 else "medium" if min_confidence >= LOW_CONFIDENCE_THRESHOLD else "low"
    transcript_quality = "medium" if source.source_type == "transcript" else "not_needed"
    return ExtractionQuality(
        text=text_quality,
        images="high" if assets.images or assets.screenshots else "not_supported",
        tables="not_supported",
        layout="medium" if source.source_type in {"webpage", "browser_capture", "document"} else "not_supported",
        ocr=ocr_quality,
        transcript=transcript_quality,
    )


def _fallbacks(source: SourceRecord) -> list[str]:
    if source.capability and source.capability.fallbacks:
        return list(source.capability.fallbacks)
    return ["provide a clearer local export", "upload screenshots/OCR sidecars", "paste manual notes"]


def _fidelity_warnings(items: list[str]) -> list[str]:
    operational = {
        "cache hit",
        "Cloned public GitHub repository.",
        "Reused cached git clone.",
    }
    return [item for item in items if item not in operational]
