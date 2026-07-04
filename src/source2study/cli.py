from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from source2study.adapters.base import AdapterError, SourceRequest
from source2study.adapters.bilibili_adapter import BilibiliAdapter
from source2study.adapters.browser_capture_adapter import BrowserCaptureAdapter
from source2study.adapters.docx_adapter import DocxAdapter
from source2study.adapters.github_adapter import GitHubAdapter
from source2study.adapters.local_video_adapter import LocalVideoAdapter
from source2study.adapters.pdf_adapter import PdfAdapter
from source2study.adapters.pptx_adapter import PptxAdapter
from source2study.adapters.screenshot_ocr_adapter import ScreenshotOcrAdapter
from source2study.adapters.transcript_adapter import TranscriptAdapter
from source2study.adapters.webpage_adapter import WebpageAdapter
from source2study.adapters.wechat_html_adapter import WeChatHtmlAdapter
from source2study.adapters.xhs_export_adapter import XhsExportAdapter
from source2study.adapters.zhihu_html_adapter import ZhihuHtmlAdapter
from source2study.asr.local import inspect_local_asr, run_local_asr
from source2study.cache import CacheStore, cache_key
from source2study.config import SourcePolicy
from source2study.exporters.docx import write_docx
from source2study.exporters.mindmap import export_mindmap, validate_mindmap_text
from source2study.exporters.markdown import write_markdown
from source2study.exporters.pdf import write_pdf
from source2study.exporters.wiki import validate_wiki, write_wiki
from source2study.generation.citation_verifier import CitationVerifier
from source2study.generation.learning_quality_verifier import LearningQualityVerifier
from source2study.generation.modes import resolve_mode
from source2study.generation.verifier import StudyPackVerifier
from source2study.generation.writer import StudyPackWriter
from source2study.intake import (
    blocked_report,
    enforce_intake_gate,
    failed_report,
    load_intake_summary,
    report_from_adapter_result,
    write_intake_report,
)
from source2study.knowledge.concept_graph import ConceptGraphBuilder
from source2study.manifest import (
    load_manifest,
    record_cache,
    record_job,
    record_output,
    record_source,
    record_validation,
    write_manifest,
)
from source2study.models.study_pack import StudyPack
from source2study.ocr.simple_placeholder import read_sidecar_or_placeholder
from source2study.personalization.learner_profile import LearnerProfile, default_profile
from source2study.personalization.pack_spec import LearningPackSpecBuilder
from source2study.safety.policy import PolicyEngine
from source2study.templates import copy_all_template_packs, copy_template_pack, list_template_packs, load_template_pack
from source2study.video.keyframes import extract_interval_keyframes, inspect_keyframe_engine
from source2study.workspace import (
    citation_report_path,
    ensure_workspace,
    learning_quality_report_path,
    load_index,
    pack_json_path,
    write_ledgers,
)


ADAPTERS = [
    BilibiliAdapter(),
    BrowserCaptureAdapter(),
    ScreenshotOcrAdapter(),
    TranscriptAdapter(),
    WeChatHtmlAdapter(),
    XhsExportAdapter(),
    ZhihuHtmlAdapter(),
    DocxAdapter(),
    PptxAdapter(),
    GitHubAdapter(),
    PdfAdapter(),
    WebpageAdapter(),
    LocalVideoAdapter(),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="source2study", description="Generate source-grounded learning packs.")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="inspect source fidelity before ingestion")
    inspect.add_argument("source")
    inspect.add_argument("--workspace", default="./workspace/default")
    inspect.add_argument("--source-type")
    inspect.add_argument("--authorization", default="personal_learning")
    inspect.add_argument("--allow-network", action="store_true")

    ingest = sub.add_parser("ingest", help="ingest sources into a workspace")
    ingest.add_argument("sources", nargs="*", help="source paths or URLs")
    ingest.add_argument("--workspace", default="./workspace/default")
    ingest.add_argument("--source", action="append")
    ingest.add_argument("--source-type", action="append", help="optional adapter source type; pass once for all sources or once per source")
    ingest.add_argument("--authorization", default="personal_learning")
    ingest.add_argument("--allow-network", action="store_true")
    ingest.add_argument("--no-cache", action="store_true")

    build_index = sub.add_parser("build-index", help="rebuild evidence index from ledgers")
    build_index.add_argument("workspace")
    build_index.add_argument("--allow-degraded", action="store_true")

    generate = sub.add_parser("generate", help="generate a learning pack")
    generate.add_argument("workspace")
    generate.add_argument("--mode", default="beginner")
    generate.add_argument("--language", default="zh")
    generate.add_argument("--output")
    generate.add_argument("--share-mode", choices=["personal", "public_share"], default="personal")
    generate.add_argument("--allow-degraded", action="store_true")
    generate.add_argument("--profile", help="JSON learner profile file")
    generate.add_argument("--goal")
    generate.add_argument("--level")
    generate.add_argument("--time-budget")
    generate.add_argument("--use-case")
    generate.add_argument("--style")
    generate.add_argument("--must-include", action="append")
    generate.add_argument("--avoid", action="append")

    validate = sub.add_parser("validate", help="validate source and evidence ledgers")
    validate.add_argument("workspace")
    validate.add_argument("--pack")
    validate.add_argument("--share-mode", choices=["personal", "public_share"], default="personal")
    validate.add_argument("--report")

    policy = sub.add_parser("policy", help="inspect source safety policy")
    policy_sub = policy.add_subparsers(dest="policy_command", required=True)
    policy_check = policy_sub.add_parser("check", help="check whether a source is allowed")
    policy_check.add_argument("source")
    policy_check.add_argument("--allow-network", action="store_true")

    wiki = sub.add_parser("wiki", help="build source-grounded wiki exports")
    wiki_sub = wiki.add_subparsers(dest="wiki_command", required=True)
    wiki_build = wiki_sub.add_parser("build", help="build a personal learning wiki from EvidenceIndex")
    wiki_build.add_argument("workspace")
    wiki_build.add_argument("--output-dir")

    graph = sub.add_parser("graph", help="export source-grounded concept maps")
    graph_sub = graph.add_subparsers(dest="graph_command", required=True)
    graph_export = graph_sub.add_parser("export", help="export ConceptGraph as markmap, mermaid, or json")
    graph_export.add_argument("workspace")
    graph_export.add_argument("--format", choices=["markmap", "mermaid", "json"], default="markmap")
    graph_export.add_argument("--output")

    ocr = sub.add_parser("ocr", help="run optional local OCR for a user-provided image")
    ocr.add_argument("image")
    ocr.add_argument("--output", help="write OCR text to this sidecar file")

    asr = sub.add_parser("asr", help="inspect or run optional local ASR for user-provided media")
    asr_sub = asr.add_subparsers(dest="asr_command", required=True)
    asr_inspect = asr_sub.add_parser("inspect", help="check whether local ASR is available")
    asr_inspect.add_argument("media", nargs="?")
    asr_transcribe = asr_sub.add_parser("transcribe", help="transcribe local media with an installed local ASR engine")
    asr_transcribe.add_argument("media")
    asr_transcribe.add_argument("--output", help="write transcript text to this file")

    keyframes = sub.add_parser("keyframes", help="inspect or extract local video keyframes with optional ffmpeg")
    keyframes_sub = keyframes.add_subparsers(dest="keyframes_command", required=True)
    keyframes_inspect = keyframes_sub.add_parser("inspect", help="check whether local keyframe extraction is available")
    keyframes_inspect.add_argument("video", nargs="?")
    keyframes_extract = keyframes_sub.add_parser("extract", help="extract interval keyframes from a local video")
    keyframes_extract.add_argument("video")
    keyframes_extract.add_argument("--output-dir", required=True)
    keyframes_extract.add_argument("--interval-seconds", type=int, default=30)

    templates = sub.add_parser("templates", help="list, show, or copy learning template packs")
    templates_sub = templates.add_subparsers(dest="templates_command", required=True)
    templates_sub.add_parser("list", help="list available template packs")
    templates_show = templates_sub.add_parser("show", help="show one template pack")
    templates_show.add_argument("template_id")
    templates_copy = templates_sub.add_parser("copy", help="copy a template pack into a workspace")
    templates_copy.add_argument("template_id", help="template id or 'all'")
    templates_copy.add_argument("--workspace", required=True)
    templates_copy.add_argument("--output-dir")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "ingest":
            return cmd_ingest(args)
        if args.command == "inspect":
            return cmd_inspect(args)
        if args.command == "build-index":
            return cmd_build_index(args)
        if args.command == "generate":
            return cmd_generate(args)
        if args.command == "validate":
            return cmd_validate(args)
        if args.command == "policy":
            return cmd_policy(args)
        if args.command == "wiki":
            return cmd_wiki(args)
        if args.command == "graph":
            return cmd_graph(args)
        if args.command == "ocr":
            return cmd_ocr(args)
        if args.command == "asr":
            return cmd_asr(args)
        if args.command == "templates":
            return cmd_templates(args)
        if args.command == "keyframes":
            return cmd_keyframes(args)
    except (AdapterError, ValueError, PermissionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        fallback = getattr(exc, "fallback", None)
        if fallback:
            print(f"fallback: {fallback}", file=sys.stderr)
        return 2
    return 0


def cmd_ingest(args) -> int:
    workspace = ensure_workspace(Path(args.workspace))
    policy = SourcePolicy(allow_network=args.allow_network)
    index = load_index(workspace)
    manifest = load_manifest(workspace)
    cache = CacheStore(workspace)
    policy_engine = PolicyEngine()
    warnings: list[str] = []
    values = list(args.sources) + list(args.source or [])
    if not values:
        raise ValueError("ingest requires at least one source path, URL, or --source value.")
    source_types = args.source_type or []
    if source_types and len(source_types) not in {1, len(values)}:
        raise ValueError("--source-type must be passed once for all sources or once per source.")
    for source_index, value in enumerate(values):
        source_type = source_types[source_index] if len(source_types) == len(values) else (source_types[0] if source_types else None)
        decision = policy_engine.check_source(value, policy)
        if not decision.allowed:
            write_intake_report(workspace, blocked_report(value, decision.source_type, decision.reason, decision.safe_alternatives))
            record_source(manifest, None, decision.source_type, value, "blocked", "policy", error=decision.reason)
            record_job(manifest, "ingest", "blocked", {"source": value})
            write_manifest(workspace, manifest)
            raise AdapterError(decision.reason, "; ".join(decision.safe_alternatives))
        request = SourceRequest(value=value, workspace=workspace, policy=policy, authorization=args.authorization, source_type=source_type)
        candidates = [candidate for candidate in ADAPTERS if candidate.matches_source_type(source_type)]
        adapter = next((candidate for candidate in candidates if candidate.can_handle(request)), None)
        if adapter is None:
            write_intake_report(
                workspace,
                failed_report(
                    value,
                    source_type or "unknown",
                    "No adapter can handle source.",
                    ["Provide PDF/text/HTML/local repo/subtitle/screenshot/browser-capture file."],
                ),
            )
            record_source(manifest, None, "unknown", value, "failed", "none", error="No adapter can handle source.")
            write_manifest(workspace, manifest)
            hint = f"No adapter can handle source with --source-type {source_type}: {value}" if source_type else f"No adapter can handle source: {value}"
            raise AdapterError(hint, "Provide PDF/text/HTML/local repo/subtitle/screenshot/browser-capture file.")
        adapter_decision = adapter.policy_check(request)
        if not adapter_decision.allowed:
            write_intake_report(workspace, blocked_report(value, adapter_decision.source_type, adapter_decision.reason, adapter_decision.safe_alternatives))
            record_source(manifest, None, adapter_decision.source_type, value, "blocked", adapter.__class__.__name__, error=adapter_decision.reason)
            record_job(manifest, "ingest", "blocked", {"source": value})
            write_manifest(workspace, manifest)
            raise AdapterError(adapter_decision.reason, "; ".join(adapter_decision.safe_alternatives))
        key = cache_key(adapter, request)
        result = None if args.no_cache else cache.get(key)
        cache_hit = result is not None
        if result is None:
            try:
                result = adapter.ingest(request)
            except AdapterError as exc:
                write_intake_report(workspace, failed_report(value, adapter.source_types[0], str(exc), adapter.fallback_options(value)))
                raise
            if not args.no_cache:
                cache.put(key, result)
        write_intake_report(workspace, report_from_adapter_result(result))
        record_cache(manifest, cache_hit)
        index.add_records(result.source, result.evidence)
        write_ledgers(workspace, index)
        record_source(manifest, result.source.source_id, result.source.source_type, value, "indexed", adapter.__class__.__name__, key)
        record_job(manifest, "ingest", "complete", {"source": value, "cache_hit": cache_hit})
        write_manifest(workspace, manifest)
        warnings.extend(result.warnings)
    print(json.dumps({"workspace": str(workspace), "sources": len(index.sources), "evidence": len(index.evidence), "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0


def cmd_inspect(args) -> int:
    workspace = ensure_workspace(Path(args.workspace))
    policy = SourcePolicy(allow_network=args.allow_network)
    value = args.source
    policy_engine = PolicyEngine()
    decision = policy_engine.check_source(value, policy)
    if not decision.allowed:
        report = blocked_report(value, decision.source_type, decision.reason, decision.safe_alternatives)
        write_intake_report(workspace, report)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 1

    request = SourceRequest(value=value, workspace=workspace, policy=policy, authorization=args.authorization, source_type=args.source_type)
    candidates = [candidate for candidate in ADAPTERS if candidate.matches_source_type(args.source_type)]
    adapter = next((candidate for candidate in candidates if candidate.can_handle(request)), None)
    if adapter is None:
        report = failed_report(
            value,
            args.source_type or "unknown",
            "No adapter can handle source.",
            ["Provide PDF/text/HTML/local repo/subtitle/screenshot/browser-capture file."],
        )
        write_intake_report(workspace, report)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 1

    adapter_decision = adapter.policy_check(request)
    if not adapter_decision.allowed:
        report = blocked_report(value, adapter_decision.source_type, adapter_decision.reason, adapter_decision.safe_alternatives)
        write_intake_report(workspace, report)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 1
    try:
        result = adapter.ingest(request)
    except AdapterError as exc:
        degraded = "no readable text" in str(exc).lower()
        report = failed_report(value, adapter.source_types[0], str(exc), adapter.fallback_options(value), degraded=degraded)
        write_intake_report(workspace, report)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0 if degraded else 1
    report = report_from_adapter_result(result)
    write_intake_report(workspace, report)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.ok_for_generation else 1


def cmd_build_index(args) -> int:
    workspace = ensure_workspace(Path(args.workspace))
    enforce_intake_gate(workspace, allow_degraded=args.allow_degraded)
    index = load_index(workspace)
    manifest = load_manifest(workspace)
    write_ledgers(workspace, index)
    record_job(manifest, "build-index", "complete", {"sources": len(index.sources), "evidence": len(index.evidence)})
    write_manifest(workspace, manifest)
    print(json.dumps({"workspace": str(workspace), "sources": len(index.sources), "evidence": len(index.evidence)}, indent=2))
    return 0


def cmd_generate(args) -> int:
    workspace = ensure_workspace(Path(args.workspace))
    intake_summary = enforce_intake_gate(workspace, allow_degraded=args.allow_degraded)
    index = load_index(workspace)
    manifest = load_manifest(workspace)
    mode = resolve_mode(args.mode)
    profile = _resolve_profile(args)
    pack = StudyPackWriter().build(index, mode=mode, language=args.language, profile=profile)
    _attach_intake_metadata(pack, intake_summary)
    report = StudyPackVerifier().verify(pack, index)
    if not report.ok:
        record_job(manifest, "generate", "failed", {"mode": mode.value, "errors": report.errors})
        write_manifest(workspace, manifest)
        raise ValueError("generation failed quality gate: " + "; ".join(report.errors))

    citation_report = CitationVerifier().verify(index, pack=pack, share_mode=args.share_mode)
    report_path = citation_report_path(workspace, mode.value)
    citation_report.write(report_path)
    pack_path = pack_json_path(workspace, mode.value)
    pack_path.write_text(json.dumps(pack.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    if not citation_report.ok:
        record_validation(manifest, citation_report.status, report_path, citation_report.summary)
        record_job(manifest, "generate", "failed", {"mode": mode.value, "errors": citation_report.errors})
        write_manifest(workspace, manifest)
        raise ValueError("generation failed citation gate: " + "; ".join(citation_report.errors))

    concept_graph = ConceptGraphBuilder().build(index)
    pack_spec = LearningPackSpecBuilder().build(profile, mode)
    learning_report = LearningQualityVerifier().verify(pack, profile=profile, spec=pack_spec, graph=concept_graph)
    learning_report_path = learning_quality_report_path(workspace, mode.value)
    learning_report.write(learning_report_path)
    if not learning_report.ok:
        record_validation(manifest, learning_report.status, learning_report_path, {"errors": len(learning_report.errors)})
        record_job(manifest, "generate", "failed", {"mode": mode.value, "errors": learning_report.errors})
        write_manifest(workspace, manifest)
        raise ValueError("generation failed learning quality gate: " + "; ".join(learning_report.errors))

    output = Path(args.output) if args.output else workspace / "outputs" / f"learning_pack_{mode.value}.md"
    suffix = output.suffix.lower()
    if suffix == ".docx":
        written = write_docx(pack, index, output)
    elif suffix == ".pdf":
        written = write_pdf(pack, index, output)
    else:
        written = write_markdown(pack, index, output)
    record_validation(manifest, citation_report.status, report_path, citation_report.summary)
    record_validation(manifest, learning_report.status, learning_report_path, learning_report.to_dict())
    record_output(manifest, mode.value, suffix.lstrip(".") or "md", written, "complete", report_path)
    record_job(manifest, "generate", "complete", {"mode": mode.value, "output": str(written)})
    write_manifest(workspace, manifest)
    print(
        json.dumps(
            {
                "output": str(written),
                "pack": str(pack_path),
                "citation_report": str(report_path),
                "learning_quality_report": str(learning_report_path),
                "mode": mode.value,
                "warnings": report.warnings + citation_report.warnings + learning_report.warnings + _intake_warnings(intake_summary),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_validate(args) -> int:
    workspace = ensure_workspace(Path(args.workspace))
    index = load_index(workspace)
    manifest = load_manifest(workspace)
    pack = None
    if args.pack:
        pack = StudyPack.from_dict(json.loads(Path(args.pack).read_text(encoding="utf-8")))
    report = CitationVerifier().verify(index, pack=pack, share_mode=args.share_mode)
    report_path = Path(args.report) if args.report else citation_report_path(workspace, "validate")
    report.write(report_path)
    record_validation(manifest, report.status, report_path, report.summary)
    record_job(manifest, "validate", report.status, {"pack": args.pack, "share_mode": args.share_mode})
    write_manifest(workspace, manifest)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.ok else 1


def cmd_policy(args) -> int:
    if args.policy_command != "check":
        raise ValueError(f"Unsupported policy command: {args.policy_command}")
    decision = PolicyEngine().check_source(args.source, SourcePolicy(allow_network=args.allow_network))
    print(json.dumps(decision.to_dict(), ensure_ascii=False, indent=2))
    return 0 if decision.allowed else 1


def cmd_wiki(args) -> int:
    if args.wiki_command != "build":
        raise ValueError(f"Unsupported wiki command: {args.wiki_command}")
    workspace = ensure_workspace(Path(args.workspace))
    index = load_index(workspace)
    if not index.evidence:
        raise ValueError("Cannot build wiki: EvidenceIndex is empty.")
    output_dir = Path(args.output_dir) if args.output_dir else workspace / "wiki"
    written = write_wiki(index, output_dir)
    validation = validate_wiki(written, index)
    print(json.dumps({"status": validation["status"], "wiki": str(written), "issues": validation["issues"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "pass" else 1


def cmd_graph(args) -> int:
    if args.graph_command != "export":
        raise ValueError(f"Unsupported graph command: {args.graph_command}")
    workspace = ensure_workspace(Path(args.workspace))
    index = load_index(workspace)
    if not index.evidence:
        raise ValueError("Cannot export graph: EvidenceIndex is empty.")
    extension = {"markmap": "md", "mermaid": "mmd", "json": "json"}[args.format]
    output = Path(args.output) if args.output else workspace / "visuals" / f"concept_graph.{extension}"
    written = export_mindmap(index, output, args.format)
    validation = validate_mindmap_text(written.read_text(encoding="utf-8"))
    print(json.dumps({"status": validation["status"], "graph": str(written), "format": args.format, "issues": validation["issues"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "pass" else 1


def cmd_ocr(args) -> int:
    image = Path(args.image)
    if not image.exists() or not image.is_file():
        raise ValueError(f"OCR image does not exist: {image}")
    result = read_sidecar_or_placeholder(image)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result.text, encoding="utf-8")
    print(json.dumps({"status": "pass" if result.text else "fail", "engine": result.engine, "confidence": result.confidence, "output": args.output, "text_preview": result.text[:200]}, ensure_ascii=False, indent=2))
    return 0


def cmd_asr(args) -> int:
    if args.asr_command == "inspect":
        payload = inspect_local_asr()
        if getattr(args, "media", None):
            media = Path(args.media)
            payload["media_exists"] = media.exists() and media.is_file()
            payload["media"] = str(media)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.asr_command != "transcribe":
        raise ValueError(f"Unsupported asr command: {args.asr_command}")
    media = Path(args.media)
    if not media.exists() or not media.is_file():
        raise ValueError(f"ASR media file does not exist: {media}")
    result = run_local_asr(media)
    if args.output and result.text:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result.text, encoding="utf-8")
    print(json.dumps(result.to_dict() | {"output": args.output}, ensure_ascii=False, indent=2))
    return 0 if result.status == "pass" else 1


def cmd_templates(args) -> int:
    if args.templates_command == "list":
        packs = list_template_packs()
        print(json.dumps({"count": len(packs), "templates": packs}, ensure_ascii=False, indent=2))
        return 0
    if args.templates_command == "show":
        print(json.dumps(load_template_pack(args.template_id), ensure_ascii=False, indent=2))
        return 0
    if args.templates_command != "copy":
        raise ValueError(f"Unsupported templates command: {args.templates_command}")
    workspace = ensure_workspace(Path(args.workspace))
    output_dir = Path(args.output_dir) if args.output_dir else None
    if args.template_id == "all":
        written = copy_all_template_packs(workspace, output_dir)
    else:
        written = copy_template_pack(args.template_id, workspace, output_dir)
    print(json.dumps({"status": "pass", "path": str(written)}, ensure_ascii=False, indent=2))
    return 0


def cmd_keyframes(args) -> int:
    if args.keyframes_command == "inspect":
        payload = inspect_keyframe_engine()
        if getattr(args, "video", None):
            video = Path(args.video)
            payload["video_exists"] = video.exists() and video.is_file()
            payload["video"] = str(video)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.keyframes_command != "extract":
        raise ValueError(f"Unsupported keyframes command: {args.keyframes_command}")
    video = Path(args.video)
    if not video.exists() or not video.is_file():
        raise ValueError(f"Video file does not exist: {video}")
    result = extract_interval_keyframes(video, Path(args.output_dir), args.interval_seconds)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.status == "pass" else 1


def _resolve_profile(args) -> LearnerProfile:
    profile = LearnerProfile.from_json_file(Path(args.profile)) if getattr(args, "profile", None) else default_profile()
    return profile.merge_overrides(
        goal=getattr(args, "goal", None),
        level=getattr(args, "level", None),
        time_budget=getattr(args, "time_budget", None),
        use_case=getattr(args, "use_case", None),
        style=getattr(args, "style", None),
        must_include=getattr(args, "must_include", None),
        avoid=getattr(args, "avoid", None),
    )


def _attach_intake_metadata(pack: StudyPack, summary: dict | None) -> None:
    if not summary:
        return
    pack.metadata["intake_summary"] = {
        "status": summary.get("status"),
        "source_count": summary.get("source_count"),
        "warnings": summary.get("warnings", []),
        "errors": summary.get("errors", []),
        "sources": [
            {
                "source_id": item.get("source_id"),
                "source_type": item.get("source_type"),
                "source_title": item.get("source_title"),
                "status": item.get("status"),
                "detected_assets": item.get("detected_assets", {}),
                "extraction_quality": item.get("extraction_quality", {}),
                "warnings": item.get("warnings", []),
            }
            for item in summary.get("sources", [])
        ],
    }
    if summary.get("status") != "pass":
        message = "Source intake is degraded; review Source Intake Summary before relying on this pack."
        if message not in pack.limitations:
            pack.limitations.append(message)


def _intake_warnings(summary: dict | None) -> list[str]:
    if not summary:
        return []
    warnings = list(summary.get("warnings", []))
    if summary.get("status") not in {None, "pass"}:
        warnings.append(f"source intake status is {summary.get('status')}")
    return warnings


if __name__ == "__main__":
    raise SystemExit(main())
