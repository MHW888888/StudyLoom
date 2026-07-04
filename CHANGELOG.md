# Changelog

## v1.5.2-alpha.0 - Real-World Material Validation

### Added

- Public alpha real-world validation results template.
- Real-world example policy that prevents private materials from entering the repository.
- Public alpha triage guide for source fidelity, extraction, citation, learning quality, formatting, template, OCR/ASR/keyframe, MCP safety, compliance, and adapter request issues.
- Alpha issue seed guide for organizing real-world validation work.

### Hardened

- README now has a Public Alpha Validation section.
- README Chinese intro is checked for mojibake regressions.
- Release docs tests now require the real-world validation and triage documents.

### Safety

- No new ingestion features or platform scraping.
- Real-world validation records must stay anonymized and must not include private source files, cookies, tokens, browser profiles, API keys, or private course materials.

## v1.5.1-alpha.0 - Alpha Hardening

### Added

- Fresh clone validation checklist for proving the GitHub repository works outside the original workspace.
- Real-world fixture checklist for Word, PPT, PDF, local media, WeChat, Xiaohongshu, and Zhihu alpha testing.
- Alpha risk report for DOCX/PPTX complexity, optional OCR/ASR/keyframes, browser capture compatibility, template quality, and deterministic eval limits.
- GitHub release steps for publishing `v1.0.0-alpha.0` as the baseline and `v1.5.0-alpha.0` as experimental extensions.

### Hardened

- README now documents optional local-tool degradation for Tesseract, Whisper CLI, and ffmpeg.
- Template-pack exported READMEs now explicitly require `Source Intake Summary`, `Source Appendix`, and citation validation.

### Safety

- No new platform scraping or high-risk adapter work.
- Optional media helpers remain local-only and explicit.

## v1.5.0-alpha.0 - Alpha Extension Line

Experimental alpha extension release. Use `v1.0.0-alpha.0` as the public baseline; use this line for testing the expanded local extraction and output capabilities.

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
