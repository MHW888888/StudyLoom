from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from source2study import __version__  # noqa: E402
from source2study.cli import main as source2study_main  # noqa: E402
from source2study.models.study_pack import StudyPack  # noqa: E402
from source2study.workspace import citation_report_path, learning_quality_report_path, load_index, pack_json_path  # noqa: E402


DEFAULT_THRESHOLDS = {
    "intake_pass_rate": 0.8,
    "intake_fail_rate": 0.0,
    "blocked_source_count": 0.0,
    "low_confidence_evidence_rate": 0.2,
    "source_asset_coverage": 0.7,
    "missing_location_rate": 0.0,
    "degraded_output_disclosure": 1.0,
    "citation_coverage": 0.9,
    "missing_citation_rate": 0.0,
    "unsupported_claim_rate": 0.0,
    "concept_coverage": 0.7,
    "mode_fit": 0.75,
    "learner_profile_fit": 0.7,
    "quiz_presence": 1.0,
    "practice_task_presence": 1.0,
    "source_appendix_presence": 1.0,
    "policy_compliance": 1.0,
}

MAX_METRICS = {
    "intake_fail_rate",
    "blocked_source_count",
    "extraction_warning_count",
    "low_confidence_evidence_rate",
    "missing_location_rate",
    "missing_citation_rate",
    "unsupported_claim_rate",
}


@dataclass(frozen=True)
class GenerationCase:
    mode: str
    expected_file: str
    output_name: str
    profile: Path | None = None


SUITES = {
    "standard_demo": {
        "sources": [ROOT / "evals" / "fixtures" / "standard_sources" / "notes.md", ROOT / "evals" / "fixtures" / "standard_sources" / "mini_repo"],
        "generations": [GenerationCase("beginner", "beginner_expected.json", "beginner.md")],
        "threshold_overrides": {},
    },
    "personalized_demo": {
        "sources": [ROOT / "evals" / "fixtures" / "personalized_sources"],
        "generations": [
            GenerationCase("beginner", "beginner_expected.json", "beginner.md", ROOT / "examples" / "personalized" / "profiles" / "beginner.json"),
            GenerationCase("exam", "exam_expected.json", "exam.md", ROOT / "examples" / "personalized" / "profiles" / "exam.json"),
            GenerationCase("developer", "developer_expected.json", "developer.md", ROOT / "examples" / "personalized" / "profiles" / "developer.json"),
            GenerationCase("creator", "creator_expected.json", "creator.md", ROOT / "examples" / "personalized" / "profiles" / "creator.json"),
        ],
        "threshold_overrides": {},
    },
    "degraded_demo": {
        "sources": [ROOT / "evals" / "fixtures" / "degraded_sources" / "no_sidecar.png"],
        "generations": [GenerationCase("beginner", "degraded_expected.json", "degraded.md")],
        "threshold_overrides": {
            "intake_pass_rate": 0.0,
            "low_confidence_evidence_rate": 1.0,
            "source_asset_coverage": 1.0,
        },
    },
}


def run_suite(suite: str) -> dict[str, Any]:
    if suite not in SUITES:
        raise ValueError(f"Unsupported eval suite '{suite}'. Valid suites: {', '.join(sorted(SUITES))}")
    config = SUITES[suite]
    with tempfile.TemporaryDirectory(prefix=f"source2study_eval_{suite}_") as tmp:
        workspace = Path(tmp) / "workspace"
        ingest_args = ["ingest", "--workspace", str(workspace)]
        for source in config["sources"]:
            ingest_args.extend(["--source", str(source)])
        _run_cli(ingest_args)
        _run_cli(["build-index", str(workspace)])

        outputs: list[dict[str, Any]] = []
        for case in config["generations"]:
            output_path = workspace / "outputs" / case.output_name
            args = ["generate", str(workspace), "--mode", case.mode, "--output", str(output_path)]
            if case.profile:
                args.extend(["--profile", str(case.profile)])
            _run_cli(args)
            pack_path = _pack_path_for_case(workspace, case.mode)
            _run_cli(["validate", str(workspace), "--pack", str(pack_path)])
            outputs.append(_case_output(workspace, case, output_path, pack_path))

        return build_eval_report(suite, workspace, outputs, config.get("threshold_overrides", {}))


def build_eval_report(suite: str, workspace: Path, outputs: list[dict[str, Any]], threshold_overrides: dict[str, float] | None = None) -> dict[str, Any]:
    thresholds = dict(DEFAULT_THRESHOLDS)
    thresholds.update(threshold_overrides or {})
    metrics = compute_metrics(workspace, outputs)
    issues = _threshold_issues(metrics, thresholds)
    return {
        "status": "pass" if not issues else "fail",
        "source2study_version": __version__,
        "suite": suite,
        "metrics": metrics,
        "thresholds": thresholds,
        "issues": issues,
        "cases": [
            {
                "mode": item["case"].mode,
                "expected": item["case"].expected_file,
                "output": item["output_name"],
                "citation_status": item["citation_report"].get("status"),
                "learning_quality_status": item["learning_report"].get("status"),
            }
            for item in outputs
        ],
    }


def compute_metrics(workspace: Path, outputs: list[dict[str, Any]]) -> dict[str, float]:
    index = load_index(workspace)
    intake_summary = _read_json(workspace / "intake_report.json")
    sources = intake_summary.get("sources", []) if intake_summary else []
    total_sources = max(1, len(sources))
    pass_count = sum(1 for item in sources if item.get("status") == "pass")
    degraded_count = sum(1 for item in sources if item.get("status") == "degraded")
    fail_count = sum(1 for item in sources if item.get("status") == "fail")
    blocked_count = sum(1 for item in sources if item.get("status") == "blocked")
    warning_count = sum(len(item.get("warnings", [])) for item in sources)
    evidence = list(index.evidence.values())
    low_confidence = [record for record in evidence if record.confidence < 0.75]
    missing_location = [record for record in evidence if not _has_location(record) or not record.source_id or record.source_id not in index.sources]

    section_count = sum(len(item["pack"].sections) for item in outputs)
    sections_with_citations = sum(1 for item in outputs for section in item["pack"].sections if section.evidence_ids)
    citation_summaries = [item["citation_report"].get("summary", {}) for item in outputs]
    citation_total = sum(int(summary.get("citations", 0)) for summary in citation_summaries)
    missing_citations = sum(int(summary.get("missing_citations", 0)) for summary in citation_summaries)
    unsupported_claims = sum(int(summary.get("unsupported_claims", 0)) for summary in citation_summaries)

    metric_values = {
        "intake_pass_rate": _ratio(pass_count, total_sources),
        "intake_degraded_rate": _ratio(degraded_count, total_sources),
        "intake_fail_rate": _ratio(fail_count, total_sources),
        "blocked_source_count": float(blocked_count),
        "extraction_warning_count": float(warning_count),
        "low_confidence_evidence_rate": _ratio(len(low_confidence), len(evidence)),
        "source_asset_coverage": _average(_source_asset_coverage(sources, item["expected"]) for item in outputs),
        "missing_location_rate": _ratio(len(missing_location), len(evidence)),
        "degraded_output_disclosure": _degraded_output_disclosure(intake_summary, outputs),
        "citation_coverage": _ratio(sections_with_citations, section_count),
        "missing_citation_rate": _ratio(missing_citations, citation_total),
        "unsupported_claim_rate": _ratio(unsupported_claims, section_count),
        "concept_coverage": _average(concept_coverage(item["output_text"], item["expected"]) for item in outputs),
        "mode_fit": _average(mode_fit(item["output_text"], item["expected"]) for item in outputs),
        "learner_profile_fit": _average(learner_profile_fit(item["output_text"], item["pack"]) for item in outputs),
        "quiz_presence": _average(_presence(item["output_text"], item["expected"].get("requires_quiz", False), "quiz") for item in outputs),
        "practice_task_presence": _average(_presence(item["output_text"], item["expected"].get("requires_practice_task", False), "practice task") for item in outputs),
        "source_appendix_presence": _average(_presence(item["output_text"], item["expected"].get("requires_source_appendix", True), "source appendix") for item in outputs),
        "policy_compliance": _average(policy_compliance(item["output_text"], item["expected"], sources) for item in outputs),
    }
    return {key: round(value, 4) for key, value in metric_values.items()}


def concept_coverage(output_text: str, expected: dict[str, Any]) -> float:
    concepts = expected.get("required_concepts", [])
    if not concepts:
        return 1.0
    normalized = _normalize(output_text)
    matched = sum(1 for concept in concepts if _normalize(str(concept)) in normalized)
    return _ratio(matched, len(concepts))


def mode_fit(output_text: str, expected: dict[str, Any]) -> float:
    required = expected.get("required_sections", []) + expected.get("required_blocks", [])
    if not required:
        return 1.0
    normalized = _normalize(output_text)
    matched = sum(1 for item in required if _normalize(str(item)) in normalized)
    return _ratio(matched, len(required))


def learner_profile_fit(output_text: str, pack: StudyPack) -> float:
    profile = pack.metadata.get("learner_profile", {}) if pack.metadata else {}
    checks: list[bool] = []
    normalized = _normalize(output_text)
    for key in ("goal", "current_level", "use_case"):
        value = profile.get(key)
        if value:
            checks.append(_normalize(str(value)) in normalized)
    for item in profile.get("must_include", []) or []:
        checks.append(_normalize(str(item)) in normalized)
    for item in profile.get("avoid", []) or []:
        checks.append(_normalize(str(item)) not in normalized)
    return _ratio(sum(1 for check in checks if check), len(checks)) if checks else 1.0


def policy_compliance(output_text: str, expected: dict[str, Any], intake_sources: list[dict[str, Any]]) -> float:
    normalized = output_text.lower()
    forbidden = [str(item).lower() for item in expected.get("forbidden_patterns", [])]
    forbidden_hits = [item for item in forbidden if item in normalized]
    blocked_sources = [item for item in intake_sources if item.get("status") == "blocked"]
    risky_errors = []
    for item in intake_sources:
        risky_errors.extend(str(error).lower() for error in item.get("errors", []))
    risk_hits = [pattern for pattern in forbidden if any(pattern in error for error in risky_errors)]
    return 0.0 if forbidden_hits or blocked_sources or risk_hits else 1.0


def _case_output(workspace: Path, case: GenerationCase, output_path: Path, pack_path: Path) -> dict[str, Any]:
    pack = StudyPack.from_dict(_read_json(pack_path))
    mode = pack.mode.value
    return {
        "case": case,
        "output_name": output_path.name,
        "output_text": output_path.read_text(encoding="utf-8"),
        "pack": pack,
        "citation_report": _read_json(citation_report_path(workspace, mode)),
        "learning_report": _read_json(learning_quality_report_path(workspace, mode)),
        "expected": _read_json(ROOT / "evals" / "expected" / case.expected_file),
    }


def _run_cli(args: list[str]) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = source2study_main(args)
    if code != 0:
        raise RuntimeError(
            "source2study command failed: "
            + " ".join(args)
            + f"\nstdout:\n{stdout.getvalue()}\nstderr:\n{stderr.getvalue()}"
        )


def _pack_path_for_case(workspace: Path, mode: str) -> Path:
    mode_map = {
        "beginner": "beginner_full",
        "exam": "exam_review",
        "developer": "developer",
        "creator": "creator",
    }
    return pack_json_path(workspace, mode_map[mode])


def _source_asset_coverage(sources: list[dict[str, Any]], expected: dict[str, Any]) -> float:
    expected_assets = expected.get("expected_assets", {})
    required = [key for key, value in expected_assets.items() if value is True]
    if not required:
        return 1.0
    totals = {}
    for source in sources:
        assets = source.get("detected_assets", {})
        for key, value in assets.items():
            totals[key] = totals.get(key, 0) + int(value or 0)
    matched = sum(1 for key in required if totals.get(key, 0) > 0)
    return _ratio(matched, len(required))


def _degraded_output_disclosure(intake_summary: dict[str, Any], outputs: list[dict[str, Any]]) -> float:
    status = intake_summary.get("status") if intake_summary else "unknown"
    if status != "degraded":
        return 1.0
    checks = []
    for item in outputs:
        text = item["output_text"].lower()
        checks.append("source intake summary" in text and ("degraded" in text or "extraction warnings" in text or "low confidence evidence" in text))
    return _ratio(sum(1 for check in checks if check), len(checks))


def _threshold_issues(metrics: dict[str, float], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    issues = []
    for metric, threshold in thresholds.items():
        if metric not in metrics:
            continue
        value = metrics[metric]
        if metric in MAX_METRICS:
            failed = value > threshold
            message = f"{metric}={value} exceeds max threshold {threshold}"
        else:
            failed = value < threshold
            message = f"{metric}={value} is below threshold {threshold}"
        if failed:
            issues.append({"level": "error", "type": "threshold", "metric": metric, "message": message})
    return issues


def _presence(output_text: str, required: bool, phrase: str) -> float:
    if not required:
        return 1.0
    return 1.0 if _normalize(phrase) in _normalize(output_text) else 0.0


def _has_location(record) -> bool:
    location = record.location
    return bool(location.timestamp_start or location.timestamp_end or location.page is not None or location.path or location.section)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ratio(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 1.0
    return float(numerator) / float(denominator)


def _average(values) -> float:
    items = list(values)
    if not items:
        return 1.0
    return sum(items) / len(items)


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Source2Study eval suites.")
    parser.add_argument("--suite", choices=sorted(SUITES), default="personalized_demo")
    parser.add_argument("--output", default="eval_report.json")
    args = parser.parse_args(argv)
    report = run_suite(args.suite)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "suite": args.suite, "output": str(output), "metrics": report["metrics"]}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
