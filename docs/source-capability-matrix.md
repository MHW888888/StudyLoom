# Source Capability Matrix

Source2Study does not promise to scrape every platform. It promises controlled, authorized ingestion paths that can emit evidence records and fall back safely when extraction is blocked.

## Version Stages

| Stage | Goal | Scope |
|---|---|---|
| v0.3 | Research, contracts, capability matrix, mock fixtures, policy gates | Define how sources may connect without implementing high-risk live crawling. |
| v0.4 | Low-risk real ingestion | User uploads, local exports, browser-extension current-page capture JSON, screenshot/OCR sidecar text, uploaded transcripts. |
| v0.5 | Personalized learning experience | Learner profiles, concept graphs, learning-pack specs, template blocks, and learning quality reports. |
| v0.6 | Output design and document experience | Product-like Markdown, richer basic DOCX, PDF Markdown sidecars, and exporter templates. |
| v0.6.5 | Source fidelity hardening | Intake reports, inspect command, intake gates, degraded output labeling, planned DOCX/PPTX contracts. |
| v1.0+ | Experimental adapters | Explicitly enabled, low-frequency, user-authorized adapters with no cookie replay, paywall bypass, DRM bypass, anti-bot bypass, or signature bypass. |

## Matrix

| Source | v0.3 handling | v0.4 candidate capability | v1.0+ experimental boundary | Blocked by default |
|---|---|---|---|---|
| PDF / local documents | Implemented; page/text evidence, contract metadata, cache and manifest. | OCR for scanned pages and figure/table extraction. | Better layout parsing and confidence labels. | Pirated book download, DRM bypass, paid-source redistribution. |
| DOCX / Word | Planned placeholder contract; default ingest is blocked to avoid silent structure loss. | Future user-uploaded Word extraction with headings, tables, images, comments, footnotes, headers/footers. | Rich Word structure extraction only after fidelity tests. | Silent table/image/comment loss, macro execution, hidden private content leakage. |
| PPTX / slides | Planned placeholder contract; default ingest is blocked to avoid silent slide/note/chart loss. | Future slide extraction with titles, bodies, images, charts, speaker notes. | Rich slide structure extraction only after fidelity tests. | Silent speaker-note loss, chart data loss, animation/order confusion. |
| GitHub repo | Implemented for local directories and public clone with `--allow-network`; no tokens are passed. | Public REST/API metadata and selected file import. | Private repos only through explicit local/user-authorized exports with secret redaction. | Token-in-URL handling, credentialed bulk clone, secret leakage. |
| Ordinary webpage | Implemented for local HTML and public pages with `--allow-network`. | Metadata extraction, cleaner article parsing, browser current-page capture. | Site-specific parsers only where stable and lawful. | Login bypass, paywall bypass, anti-bot bypass, cookie replay. |
| Local video/audio | Implemented only for user-provided transcripts or companion subtitles. | Uploaded `.srt`, `.vtt`, and explicit transcript `.txt` handled by `TranscriptAdapter`; local companion subtitle still supported. | Optional ASR and scene/slide-aware screenshots behind explicit permissions. | Default ASR, bulk media download, DRM bypass. |
| Bilibili | Planned/blocked; contract and policy fallback only. | User-uploaded transcript/subtitle, local video transcript, browser-captured current page JSON where authorized. | Optional public-caption adapter if lawful and stable. | Cookie replay, login bypass, anti-bot bypass, bulk video download. |
| YouTube | Planned/blocked for direct video extraction in policy. | User-uploaded transcript/subtitle, local video transcript, browser-captured current page JSON where authorized. | Optional caption-first adapter with runtime verification. | Bulk video download, DRM/paywall bypass, region/login bypass. |
| Xiaohongshu / RedNote | Planned user-export adapter implemented for mock Markdown/JSON fixtures. | User-export Markdown/JSON, browser current-page JSON, screenshot/OCR import. | Low-frequency public-page adapter only if it avoids cookies and anti-bot bypass. | Cookie replay, account history crawl, login bypass, anti-bot bypass, media download. |
| WeChat public account | Planned user-export HTML adapter implemented for mock fixtures. | User-saved HTML, browser current-page JSON, screenshot/OCR import, PDF/Markdown through document adapter. | Self-owned/authorized account export integration. | Fiddler/cookie replay, bulk history crawling, login bypass, anti-bot bypass. |
| Zhihu | Planned user-export/public-page fixture adapter implemented. | User-saved HTML, browser current-page JSON, screenshot/OCR import. | Carefully scoped public-page adapter only if no signature or app API bypass is needed. | `x-zse-96` reverse engineering, signature bypass, cookie replay, login bypass. |
| Paid courses | Policy-only in v0.3; local user-provided material may be ingested by document/video adapters. | User-authorized notes, exported slides, transcript files, screenshots for personal study. | Institution/self-owned course exports with rights metadata. | Paywall bypass, DRM bypass, recording circumvention, redistribution of paid materials. |

## Adapter Acceptance Rules

Every source adapter must declare:

```text
name
source_types
risk_level
default_enabled
allowed_methods
blocked_methods
can_handle(source)
policy_check(source)
extract(source, workspace)
fallback_options(source)
```

Every generated source ledger entry should preserve:

```text
source_type
platform
transcript_source or extraction_method
capability record
risk_level
allowed_methods
blocked_methods
fallbacks
capture_method
```

## Fallback Promise

When direct extraction is unavailable, Source2Study should offer one or more safe alternatives:

- upload saved PDF, HTML, Markdown, transcript, or screenshots
- paste manual notes
- use a local browser extension to send only the current page
- process local files for personal study
- keep the source link in the manifest and mark extraction as blocked
