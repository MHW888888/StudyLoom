# Changelog

## v1.5.0-alpha.0 - Alpha Extension Line

### Added

- v1.1 DOCX/PPTX OpenXML intake:
  - DOCX headings, body text, tables, comments, footnotes, headers/footers, and image counts.
  - PPTX slide text, speaker notes, slide counts, image counts, and chart counts.
- v1.2 source-grounded Wiki and MindMap exporters:
  - `source2study wiki build`
  - `source2study graph export --format markmap|mermaid|json`
  - Evidence ids required on concept pages and graph nodes.
- v1.3 hardened browser current-page extension:
  - sanitized HTML export
  - form/script/style removal
  - token/header/private-key pattern redaction
  - risk warnings and schema metadata
- v1.4 optional local OCR/ASR/keyframe helpers:
  - `source2study ocr`
  - `source2study asr inspect|transcribe`
  - `source2study keyframes inspect|extract`
  - local-only Tesseract, Whisper CLI, and ffmpeg integrations when installed
- v1.5 template packs:
  - exam review
  - teacher lecture
  - developer project
  - creator script
  - enterprise training
  - `source2study templates list|show|copy`

### Safety

- No new platform scraping was added.
- OCR, ASR, and keyframes are local-only optional helpers.
- Browser extension still does not request cookies, history, storage, or login-session permissions.

## v1.0.0-alpha.0 - Public Alpha

Public alpha release of **StudyLoom / source2study**.

### Added

- Source Fidelity First workflow with `IntakeReport` and `source2study inspect`.
- Low-risk local ingestion for Markdown/text, local repos, saved HTML exports, browser capture JSON, screenshots/OCR sidecars, and transcripts.
- `EvidenceIndex`, source ledger, evidence ledger, manifest, cache, and citation reports.
- Personalized learning packs with `LearnerProfile`, `ConceptGraph`, and `LearningPackSpec`.
- Markdown, structured DOCX, and basic PDF output.
- Citation verifier, learning-quality verifier, and deterministic eval suites.
- Restricted MCP/agent tools with workspace allowlists and redaction.
- Release-ready README, examples, issue templates, contributing guide, security policy, code of conduct, and release checklist.

### Safety

- No cookies or login sessions.
- No paywall, DRM, anti-bot, CAPTCHA, or signature bypass.
- No default Bilibili/YouTube video download.
- No arbitrary shell, arbitrary file-read, or arbitrary URL-fetch MCP tools.

### Known Limitations

- DOCX/PPTX real structural extraction is planned after v1.0.
- Wiki/MindMap export is planned as an optional source-grounded extension.
- PDF export is basic; Markdown remains canonical.
- OCR/ASR/keyframe pipelines are optional future work.

### Next

- `v1.1`: real DOCX/PPTX extraction.
- `v1.2`: source-grounded Wiki and MindMap extension.
- `v1.3`: browser extension hardening.
