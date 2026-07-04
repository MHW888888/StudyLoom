# Roadmap

Source2Study is moving from local MVP toward a public alpha. The project stays anchored on:

```text
Source Fidelity -> Evidence Quality -> Citation Grounding -> Learning Quality -> Output Fit -> Restricted Agent Tools
```

## Completed Pre-Alpha Milestones

### v0.1 MVP Skeleton

- Source and evidence data models
- Local document, repo, webpage, and transcript ingestion foundations
- Basic study-pack generation
- Markdown, DOCX, and simple PDF export

### v0.2 Reliability And Grounding

- Workspace manifest
- Cache and reproducible ledgers
- Citation verifier
- Policy engine
- Blocked-source tests

### v0.3 Adapter Research And Contracts

- `SourceAdapter` contract
- Adapter capability metadata
- Risk levels, allowed methods, blocked methods, fallbacks
- Capability matrix for PDF, GitHub, webpages, local video, Bilibili, YouTube, Xiaohongshu, WeChat, Zhihu, and paid courses
- Mock fixtures and blocked-path tests

### v0.4 Low-Risk Real Ingestion

- Saved WeChat HTML import
- Xiaohongshu Markdown/JSON export import
- Saved Zhihu HTML import
- Browser current-page capture JSON
- Screenshot/OCR sidecar path
- Transcript/subtitle import
- No cookies, login bypass, paywall bypass, DRM bypass, anti-bot bypass, or signature reverse engineering

### v0.5 Personalized Learning Pack

- `LearnerProfile`
- `LearningPackSpec`
- Rule-based `ConceptGraph`
- Beginner, review, exam, developer, creator, teacher, and research modes
- Template blocks for learning maps, concept cards, prerequisite patches, misconception boxes, quizzes, practice tasks, evidence cards, and source appendix
- Learning-quality reports

### v0.6 Output Design And Document Experience

- Markdown cover, table of contents, learning goals, learning map, chapter objectives, citation cards, one-page review, and source appendix
- Structured DOCX output
- Basic PDF with Markdown sidecar
- Exporter templates

### v0.6.5 Source Fidelity Hardening

- `Source Fidelity First`
- `IntakeReport`
- `source2study inspect`
- Intake quality gate before build/generate
- Degraded output labeling
- DOCX/PPTX planned placeholder contracts

### v0.7 Evaluation And Benchmarking

- `evals/` runner
- Standard, personalized, and degraded eval suites
- Source fidelity, evidence quality, citation grounding, learning quality, output fit, and policy compliance metrics
- Deterministic rule-based baseline without required LLM judge

### v0.8 MCP / Agent Tooling Hardening

- Restricted MCP tool schemas and wrappers
- Workspace allowlist
- Redaction for secrets and sensitive paths
- Minimal stdio server
- Codex / Claude skill instructions
- MCP smoke tests and skill structure checks

### v0.9 Release Preparation

- Public README rewrite
- Curated example outputs
- Issue templates and PR template
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- Release checklist
- Repository hygiene and sample-output rules

## Public Alpha

### v1.0 Public Alpha

- Initialize the project as a Git repository
- Commit the public alpha release
- Tag `v1.0.0-alpha.0`
- Write `CHANGELOG.md` and GitHub release notes
- Run a clean README quickstart check
- Keep Wiki/MindMap out of the core release and document it as a later extension

Current v1.0 alpha packages the pre-alpha work into a release-ready GitHub project.

## Completed Alpha Extensions

### v1.1 DOCX / PPTX Real Extraction

- Real DOCX heading/body/table/image/comment extraction
- Real PPTX slide/title/body/image/speaker-note extraction
- Source fidelity reports for complex layouts
- Conservative OpenXML parser without mandatory external dependencies

### v1.2 Wiki And MindMap Extension

- Source-grounded personal wiki export
- Markmap, Mermaid, and JSON concept graph export
- Evidence IDs on wiki pages and mind-map nodes
- No Wikipedia crawling or unsupported generated knowledge

### v1.3 Browser Extension Hardening

- Current-page capture UX
- Better DOM cleanup
- Image capture metadata
- No cookies, storage, headers, or bulk history
- Redaction and risk warnings for common credential-like patterns

### v1.4 Optional Local ASR / OCR Pipeline

- Explicitly enabled local ASR
- Optional OCR engine integrations
- Confidence tracking
- Keyframe and screenshot evidence cards
- Local-only ffmpeg keyframe helper
- No platform video download

### v1.5 Template Marketplace / Template Packs

- Technical project guide
- Exam review pack
- Creator script pack
- Teacher handout pack
- Enterprise training pack
- Template pack CLI list/show/copy

### v1.5.1 Alpha Hardening

- Fresh clone validation checklist
- Real-world fixture checklist
- Alpha risk report
- GitHub release steps for baseline and experimental alpha tags
- Optional-tool degradation notes
- Template-pack quality gate smoke tests

## Future Milestones

### v1.6 Richer PDF / Typst / Pandoc Export

- Better Chinese PDF path
- Optional Pandoc or Typst workflow
- Rich citation and evidence cards
- Layout QA guidance

### v1.7 Deeper Complex PDF And Office Fidelity

- Scanned PDF OCR integration
- Table structure recovery
- PPT chart data extraction
- DOCX tracked-change modeling

### v1.8 Optional Video Learning Pipeline

- Scene-change and slide-change detection
- Keyframe OCR into EvidenceIndex
- ASR segment alignment
- Low-confidence ASR/OCR review workflow

### v2.0 Hosted Or Team Workflows

- Queue-based processing
- Team workspaces
- Admin policy controls
- Private deployment mode

## Experimental Platform Adapters

Real platform adapters belong after v1.0 and must remain explicit opt-in. They must follow the same requirements as every adapter:

- capability matrix
- policy rule
- user authorization
- fixture
- acceptance test
- blocked-path test
- intake report
- evidence records with source/location/confidence
- eval coverage

They must not use cookies, login bypass, paywall bypass, DRM bypass, anti-bot bypass, request-signature reverse engineering, or bulk account-history crawling.
