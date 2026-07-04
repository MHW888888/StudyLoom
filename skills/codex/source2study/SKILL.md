---
name: source2study
description: Use Source2Study to create source-grounded personalized learning packs from allowlisted local sources with Source Fidelity First, citation verification, learning-quality checks, and restricted MCP/CLI workflows. Do not use for crawling, cookie handling, login bypass, paywall bypass, DRM bypass, anti-bot bypass, or arbitrary file/URL access.
---

# Source2Study

Source2Study is not a crawler, not a generic video summarizer, and not a raw document converter. It is a source-grounded personalized learning-pack generator.

Use the project CLI or the restricted Source2Study MCP tools rather than reimplementing the pipeline.

## Workflow

1. Confirm the user has authorization for each source.
2. Prefer local files, user exports, transcript files, screenshots/OCR sidecars, and browser current-page capture JSON.
3. Run `source2study policy check` or `source2study_policy_check`.
4. Run `source2study inspect` or `source2study_inspect_local` before ingestion.
5. Review `intake_report.json`; blocked/fail intake must not be forced through.
6. Run `source2study ingest` or `source2study_ingest_local` into an allowlisted workspace.
7. Run `source2study build-index` or `source2study_build_index`.
8. Read or ask for `LearnerProfile` before personalized generation.
9. Run `source2study generate` or `source2study_generate_personalized_pack`.
10. Run citation validation with `source2study validate --pack <study_pack_json>` or `source2study_validate_pack`.
11. For personalized output, check `learning_quality_report_<mode>.json`.
12. Before demos or releases, run `python evals/run_eval.py --suite ...` or `source2study_run_eval`.
13. Report artifact paths, `manifest.json`, intake report, citation report, learning-quality report, source/evidence counts, warnings, and known limitations.

## Source Fidelity First

The first step is not summarization. It is source intake: preserve, inspect, extract, and verify the material before generation. Do not silently lose Word/PDF/PPT tables, images, speaker notes, timestamps, screenshots, OCR confidence, or source structure.

If a source is `degraded`, disclose the extraction risk to the user. If a source is `blocked` or `fail`, stop and ask for a safer user-provided export, transcript, screenshot, or browser capture.

Generated content must come from `EvidenceIndex`. Do not invent unextracted source material.

## Restricted MCP Tools

Use only these agent tools when MCP is available:

- `source2study_policy_check`
- `source2study_inspect_local`
- `source2study_ingest_local`
- `source2study_build_index`
- `source2study_generate_pack`
- `source2study_generate_personalized_pack`
- `source2study_validate_pack`
- `source2study_run_eval`

The tools must respect workspace allowlists, intake quality gates, redaction, and structured error reporting.

## Boundaries

- Do not ask for cookies or tokens.
- Do not use or request browser profiles, login sessions, private headers, localStorage, or sessionStorage.
- Do not bypass paywalls, DRM, login gates, or anti-bot protections.
- Do not do batch platform collection, account-history crawling, or request-signature reverse engineering.
- Do not use arbitrary shell execution, arbitrary local path reads, or arbitrary URL fetching through Source2Study.
- Do not claim Bilibili, Xiaohongshu, or WeChat crawling is implemented by default.
- Use uploads, transcripts, screenshots, or local browser capture as safer fallbacks.
