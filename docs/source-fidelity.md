# Source Fidelity First

Source2Study starts with source fidelity. It first inspects and preserves user-provided Word, PDF, PPT, video, webpage, transcript, screenshot, and exported content before generating any learning pack.

第一步不是总结，而是资料保真提取。

## Principle

The pipeline is:

```text
Intake -> Preserve -> Inspect -> Extract -> Verify -> Generate
```

Generation must only use material that entered `EvidenceIndex`. If source intake is unreliable, the generated pack must be marked degraded or blocked.

## Intake Checklist

| Source | Intake must inspect | Current support |
|---|---|---|
| Markdown/text/PDF | text blocks, page availability, extraction warnings | Text and Markdown are supported; PDF text requires optional `pypdf`; images/tables/layout are not fully parsed yet. |
| DOCX/Word | headings, body text, tables, images, comments, footnotes, headers/footers | Planned placeholder contract only. No silent DOCX extraction. |
| PPTX/slides | slide count, titles, body text, images, charts, speaker notes, animation/order hints | Planned placeholder contract only. No silent PPTX extraction. |
| Webpage/HTML | title, readable body, links, images, extraction method | Local HTML and explicit public-page fetch are supported. |
| Browser capture | title, URL, visible text/HTML, images, user-initiated capture | Current-page JSON is supported; cookies, headers, tokens, and bulk history are blocked. |
| Transcript/subtitle | segments, timestamps, source file, missing video context | SRT/VTT/TXT transcript import is supported; video body is marked not processed. |
| Screenshot/OCR | image path, OCR text, OCR confidence, visual evidence | Screenshot plus optional `.ocr.txt` sidecar is supported; placeholder OCR is low confidence. |
| Video/course links | subtitles, ASR, keyframes, slide changes, OCR, timestamps | Direct video extraction remains blocked by default. User-provided transcripts/screenshots are the safe path. |

## Status Rules

- `pass`: useful evidence was extracted and no material warning was detected.
- `degraded`: extraction succeeded but some content is incomplete, low confidence, or context-limited.
- `fail`: extraction did not produce reliable evidence.
- `blocked`: policy, authorization, platform, paywall, login, DRM, anti-bot, or unsupported planned-adapter boundary prevents processing.

## Degraded Examples

- OCR confidence is below the threshold.
- A transcript was imported but the original video/visual content was not processed.
- PDF text was extracted, but images, tables, or layout were not parsed.
- Browser capture is missing readable body text.
- A complex chart is preserved only as an image or nearby text.

## Hard Boundaries

Source2Study must not:

- silently drop images, tables, slides, speaker notes, page numbers, timestamps, screenshots, or key structure
- pretend extraction succeeded when it failed
- treat low-confidence OCR/ASR as strong evidence
- generate content from source material that did not enter `EvidenceIndex`
- bypass login, paywalls, DRM, anti-bot protections, signatures, or access controls

## User Recovery Paths

When intake is degraded or failed, ask the user for safer source material:

- saved HTML/PDF/Markdown
- clearer screenshot plus OCR sidecar
- transcript or subtitle file
- exported slide PDF
- copied table text
- manual notes
- browser current-page capture JSON

## Evaluation

v0.7 treats source fidelity as the first evaluation stage. Eval reports read `intake_report.json`, `intake_reports/*.json`, `EvidenceIndex`, generated Markdown, citation reports, and learning quality reports.

Important source-fidelity metrics:

- `intake_pass_rate`
- `intake_degraded_rate`
- `intake_fail_rate`
- `blocked_source_count`
- `extraction_warning_count`
- `low_confidence_evidence_rate`
- `source_asset_coverage`
- `missing_location_rate`
- `degraded_output_disclosure`

The purpose is to catch regressions where generation still runs but the source was not actually preserved or extracted reliably.

## Agent Tooling

v0.8 keeps Source Fidelity First at the MCP boundary. Agent tools must run policy and inspect before ingestion, must honor intake gates, and must disclose degraded sources in generated output.

The restricted MCP layer may return intake report paths, evidence counts, citation report paths, learning-quality report paths, warnings, and eval metrics. It must not return large raw source content, cookies, tokens, browser profiles, login state, arbitrary local file contents, or arbitrary URL fetch results.
