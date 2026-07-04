---
name: source2study
description: Use Source2Study to turn authorized allowlisted local sources into source-grounded personalized study packs with Source Fidelity First, citation reports, learning-quality reports, and restricted MCP/CLI workflows. Do not use for crawling, cookies, login bypass, paywall bypass, DRM bypass, anti-bot bypass, or arbitrary file/URL access.
---

# Source2Study

Source2Study is not a crawler and not a generic video summarizer. Use the local `source2study` CLI or restricted MCP tools to create source-grounded personalized learning packs.

Source Fidelity First: inspect, preserve, extract, and verify user-provided material before generation. Use `source2study inspect` or `source2study_inspect_local` before ingestion, and review `intake_report.json` before trusting generated output.

Workflow:

1. Check source policy.
2. Inspect local source fidelity.
3. Ingest only allowlisted local sources.
4. Build the evidence index.
5. Read or request `LearnerProfile` for personalized packs.
6. Generate the pack.
7. Run citation validation.
8. Run learning-quality verification for personalized output.
9. Run eval suites before demo or release claims.

If intake is degraded, disclose the risk. If intake is blocked or failed, stop and request a safer user export, transcript, screenshot/OCR sidecar, or browser current-page capture.

Allowed MCP tools:

- `source2study_policy_check`
- `source2study_inspect_local`
- `source2study_ingest_local`
- `source2study_build_index`
- `source2study_generate_pack`
- `source2study_generate_personalized_pack`
- `source2study_validate_pack`
- `source2study_run_eval`

Do not handle cookies, tokens, browser profiles, login sessions, private headers, paywalls, DRM, anti-bot bypasses, account-history crawls, signature reverse engineering, arbitrary shell execution, arbitrary local path reads, or arbitrary URL fetching. Prefer user-provided files, exported HTML/PDF/Markdown, transcripts, screenshots, or local browser capture.
