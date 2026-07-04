# Alpha Risk Report

StudyLoom v1.5 is an experimental alpha extension line. It is feature-complete for the planned v1.1 through v1.5 scope, but it still needs real-world validation before being described as stable.

## Highest-Risk Areas

### DOCX / PPTX Complex Structure

Current extraction uses conservative OpenXML parsing. It captures many useful text structures, but it does not fully reconstruct:

- Word tracked changes
- floating text boxes
- complex nested tables
- image pixels or diagrams
- equation objects
- SmartArt
- full slide layout
- chart data semantics

Risk: a generated pack may miss visually important teaching material unless intake warnings are reviewed.

### OCR / ASR Tool Availability

OCR, ASR, and keyframes depend on local optional tools:

- Tesseract for OCR improvement
- Whisper CLI for local ASR
- ffmpeg for local interval keyframes

Risk: users may expect automatic media understanding. Missing tools intentionally return degraded or unavailable results.

### Video Keyframe Quality

The current keyframe helper is interval-based, not scene-change or slide-change based.

Risk: it may miss important slide transitions or capture redundant frames.

### Chinese PDF Output

Markdown is canonical. Basic PDF export exists, but production-grade Chinese typography, page layout, font embedding, and complex screenshot cards remain future work.

Risk: Markdown/DOCX may be more reliable than PDF for Chinese-heavy study packs.

### Browser Capture Compatibility

The browser extension sanitizes the current page and strips risky elements.

Risk: complex sites may store meaningful content in scripts, shadow DOM, canvas, lazy-loaded regions, or hidden tabs that are intentionally not captured.

### Template Pack Output Quality

Template packs encode structure and quality gates, not expert human pedagogy.

Risk: generated outputs still need review for audience fit, tone, examples, and real teaching value.

### Eval Metrics Are Rule-Based

Eval suites check source fidelity, evidence quality, citation grounding, and output fit with deterministic rules.

Risk: passing eval is not a substitute for human review of correctness, helpfulness, style, or domain expertise.

## Release Recommendation

Publish `v1.5.0-alpha.0` as **Experimental Alpha Extensions**, not as the recommended stable version. Use `v1.0.0-alpha.0` as the Public Alpha baseline and invite testers to try v1.5 only when they understand the alpha boundaries.

## Required Human Testing Before Beta

Before beta, test at least:

- one real Word lecture note
- one real PPT course deck
- one real textbook PDF
- one local course video plus subtitle
- one saved WeChat article
- one Xiaohongshu export or screenshot set
- one saved Zhihu page

Each sample should pass through `inspect -> ingest -> build-index -> generate -> validate -> eval`, with warnings reviewed by a human.
