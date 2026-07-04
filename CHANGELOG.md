# Changelog

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
