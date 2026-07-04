# StudyLoom / source2study

**StudyLoom** is the public project name. `source2study` is the Python package and CLI.

`source2study` is a source-grounded personalized learning pack generator. It helps users turn their own learning or work materials into traceable, personalized, reviewable study/work packs.

source2study 的第一步不是总结，而是资料保真提取。用户给 Word、PDF、PPT、视频、网页、截图、字幕或导出内容后，系统先检查和提取资料，再基于证据链生成个性化学习包。

It is not a generic video summarizer. It is not a crawler. It is not a tool for bypassing platform controls.

## Core Idea

```mermaid
flowchart LR
  A["User-provided sources"] --> B["Inspect / IntakeReport"]
  B --> C["EvidenceIndex"]
  C --> D["Personalized LearningPackSpec"]
  D --> E["Markdown / DOCX / basic PDF"]
  E --> F["Citation + Learning Quality Reports"]
  F --> G["Eval Suites + Restricted Agent Tools"]
```

Quality line:

```text
Source Fidelity -> Evidence Quality -> Citation Grounding -> Learning Quality -> Output Fit -> Restricted Agent Tools
```

## 3 Minute Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .

source2study ingest \
  --workspace ./workspace/demo \
  --source ./examples/demo_sources/notes.md \
  --source ./examples/demo_sources/mini_repo \
  --source ./examples/demo_sources/lecture.vtt

source2study build-index ./workspace/demo

source2study generate ./workspace/demo \
  --mode beginner \
  --output ./workspace/demo/outputs/beginner.md

source2study validate ./workspace/demo \
  --pack ./workspace/demo/outputs/study_pack_beginner_full.json
```

Open:

- `workspace/demo/outputs/beginner.md`
- `workspace/demo/intake_report.json`
- `workspace/demo/outputs/citation_report_beginner_full.json`
- `workspace/demo/outputs/learning_quality_report_beginner_full.json`

## Why StudyLoom Exists

Many tools summarize one video or transcript. StudyLoom is designed for a different job:

- inspect user-provided materials before generation
- preserve evidence with source, location, confidence, and rights metadata
- generate different learning packs for different users and goals
- verify citation grounding and learning quality
- keep agent/MCP tools restricted and auditable

The learning-pack design borrows from active recall, quizzes, flashcards, study guides, paper-to-course workflows, and compact agent skills. See [docs/personalized-learning.md](docs/personalized-learning.md), [docs/learning-mode-patterns.md](docs/learning-mode-patterns.md), and [docs/mcp-agent-tools.md](docs/mcp-agent-tools.md).

## Demos

### Standard Demo

```bash
source2study ingest \
  --workspace ./workspace/standard-demo \
  --source ./examples/demo_sources/notes.md \
  --source ./examples/demo_sources/mini_repo \
  --source ./examples/demo_sources/lecture.vtt

source2study build-index ./workspace/standard-demo
source2study generate ./workspace/standard-demo --mode beginner --output ./workspace/standard-demo/outputs/beginner.md
source2study validate ./workspace/standard-demo --pack ./workspace/standard-demo/outputs/study_pack_beginner_full.json
```

### Low-Risk Import Demo

```bash
source2study ingest \
  --workspace ./workspace/low-risk-demo \
  --source ./examples/low_risk_sources/wechat_article.html \
  --source ./examples/low_risk_sources/xhs_note.json \
  --source ./examples/low_risk_sources/zhihu_page.html \
  --source ./examples/low_risk_sources/browser_capture.json \
  --source ./examples/low_risk_sources/slide.png \
  --source ./examples/low_risk_sources/course.srt

source2study build-index ./workspace/low-risk-demo
source2study generate ./workspace/low-risk-demo --mode beginner --output ./workspace/low-risk-demo/outputs/beginner.md
```

This demo may produce low-confidence OCR warnings. That is expected: low-confidence evidence must be disclosed instead of treated as a strong fact.

### Personalized Learning Pack Demo

```bash
source2study ingest --workspace ./workspace/personalized-demo --source ./examples/personalized/sources
source2study build-index ./workspace/personalized-demo

source2study generate ./workspace/personalized-demo --mode beginner --profile ./examples/personalized/profiles/beginner.json --output ./workspace/personalized-demo/outputs/beginner.md
source2study generate ./workspace/personalized-demo --mode exam --profile ./examples/personalized/profiles/exam.json --output ./workspace/personalized-demo/outputs/exam.md
source2study generate ./workspace/personalized-demo --mode developer --profile ./examples/personalized/profiles/developer.json --output ./workspace/personalized-demo/outputs/developer.md
source2study generate ./workspace/personalized-demo --mode creator --profile ./examples/personalized/profiles/creator.json --output ./workspace/personalized-demo/outputs/creator.md
```

### Eval Demo

```bash
python evals/run_eval.py --suite standard_demo
python evals/run_eval.py --suite personalized_demo
python evals/run_eval.py --suite degraded_demo
```

The eval baseline checks source fidelity, evidence quality, citation grounding, learning quality, output fit, and policy compliance.

## Example Outputs

Curated small samples live in [examples/outputs](examples/outputs):

- [beginner.md](examples/outputs/beginner.md)
- [exam.md](examples/outputs/exam.md)
- [developer.md](examples/outputs/developer.md)
- [creator.md](examples/outputs/creator.md)
- [degraded-warning.md](examples/outputs/degraded-warning.md)
- [intake_report_sample.json](examples/outputs/intake_report_sample.json)
- [citation_report_sample.json](examples/outputs/citation_report_sample.json)
- [learning_quality_report_sample.json](examples/outputs/learning_quality_report_sample.json)
- [eval_report_sample.json](examples/outputs/eval_report_sample.json)

## Supported Sources

| Source | Current path | Status |
|---|---|---|
| Markdown/text | local file | supported |
| PDF | local file, basic text extraction | supported with optional `pypdf` |
| local GitHub-style repo | local directory | supported |
| ordinary webpage | explicit `--allow-network` only | cautious support |
| saved WeChat HTML | user-saved local HTML | supported |
| Xiaohongshu export | user-exported Markdown/JSON | supported |
| saved Zhihu HTML | user-saved local HTML | supported |
| browser capture | current-page JSON export | supported |
| screenshot OCR | image plus optional `.ocr.txt` sidecar | supported, confidence labeled |
| transcript/subtitle | `.srt`, `.vtt`, `.txt` | supported |
| DOCX/PPTX | planned placeholder contracts | planned real extraction |
| Bilibili/YouTube video | user-provided transcript/screenshot only | direct download blocked by default |
| paid course platforms | user-authorized local exports only | no bypass |

See [docs/source-capability-matrix.md](docs/source-capability-matrix.md).

## Output Modes

- `beginner`: zero-base guide with prerequisites, concept cards, misconceptions, and checks
- `review`: review sheet and recall prompts
- `exam`: exam/interview definitions, traps, and questions
- `developer`: project learning path, code map, and practice tasks
- `creator`: creator/script structure with hooks and talking points
- `teacher`: lecture notes, class plan, assignment ideas
- `research`: research-oriented definitions, tensions, and extension reading

The same source can produce different packs because the generator uses `LearnerProfile`, `ConceptGraph`, and `LearningPackSpec`.

## CLI Overview

```text
source2study inspect SOURCE --workspace WORKSPACE [--source-type TYPE] [--allow-network]
source2study ingest [SOURCE ...] --workspace WORKSPACE [--source SOURCE ...] [--source-type TYPE] [--allow-network]
source2study build-index WORKSPACE [--allow-degraded]
source2study generate WORKSPACE --mode MODE --output PATH [--profile PROFILE_JSON] [--goal GOAL] [--level LEVEL] [--time-budget TIME] [--use-case USE_CASE] [--style STYLE] [--share-mode personal|public_share] [--allow-degraded]
source2study validate WORKSPACE [--pack PACK_JSON] [--share-mode personal|public_share]
source2study policy check SOURCE [--allow-network]
```

## MCP / Agent Tools

Agents can call StudyLoom only through a restricted, auditable tool surface:

- `source2study_policy_check`
- `source2study_inspect_local`
- `source2study_ingest_local`
- `source2study_build_index`
- `source2study_generate_pack`
- `source2study_generate_personalized_pack`
- `source2study_validate_pack`
- `source2study_run_eval`

Smoke check:

```bash
python mcp/server.py --list-tools
```

Default MCP behavior:

- workspace allowlist only
- network disabled
- structured errors
- redacted responses
- no large raw source text returned

See [docs/mcp-agent-tools.md](docs/mcp-agent-tools.md).

## Safety And Compliance

StudyLoom does not promise to scrape everything.

It does not accept:

- cookies or cookie replay
- login sessions or browser profiles
- private headers or tokens
- bulk account-history crawling
- paywall bypass
- DRM bypass
- anti-bot or CAPTCHA bypass
- request-signature reverse engineering
- arbitrary shell execution through agent tools
- arbitrary local file reads through agent tools
- arbitrary URL fetching through agent tools

When direct extraction is unavailable, use exported files, screenshots, browser current-page capture, transcripts, or manual notes.

See [docs/compliance.md](docs/compliance.md) and [SECURITY.md](SECURITY.md).

## Installation Notes

### Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### Windows Paths

Use quoted paths when directories contain spaces:

```bash
source2study inspect "C:\Users\you\Documents\lesson notes.md" --workspace ".\workspace\demo"
```

### Clean Runtime Files

```powershell
Remove-Item -Recurse -Force .\workspace, .\tmp, .\.source2study -ErrorAction SilentlyContinue
```

Do not commit runtime workspaces or caches.

### PDF Boundary

Markdown is the canonical output. The current PDF exporter is a basic smoke renderer and writes a Markdown sidecar first. Production-grade Chinese PDF layout, fonts, and richer print design are future work. See [docs/pdf-export.md](docs/pdf-export.md).

## Project Structure

```text
src/source2study/
  adapters/          source-specific low-risk import paths
  models/            source, evidence, intake, and study-pack data models
  indexing/          EvidenceIndex and chunking
  personalization/   LearnerProfile and LearningPackSpec
  knowledge/         rule-based ConceptGraph
  generation/        writers, citation verifier, learning-quality verifier
  exporters/         Markdown, DOCX, basic PDF
  safety/            policy, permissions, redaction
mcp/                 restricted MCP tool schemas and server
evals/               deterministic benchmark suites
examples/            demo sources, profiles, and curated outputs
skills/              Codex and Claude skill packages
docs/                architecture, compliance, source fidelity, roadmap
```

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

New adapters must include a capability matrix entry, policy rule, fixture, tests, `IntakeReport`, evidence records with source/location/confidence, and eval coverage. A PR that only adds "can scrape this site" code is not enough.

## Known Limitations

- DOCX/PPTX real structural extraction is planned but not fully implemented.
- Wiki/MindMap export is planned for a later extension, not part of v1.0.
- PDF export is basic; Markdown is the canonical source.
- OCR is currently a lightweight sidecar/placeholder path unless optional engines are added later.
- ASR and video keyframe extraction are not default behavior.
- Direct Bilibili/YouTube/Xiaohongshu/WeChat/Zhihu crawling is not a default feature.
- Eval metrics are deterministic rule checks, not a full human quality judgment.

## Roadmap

- `v1.0`: Public Alpha release, tag, release notes, clean install test
- `v1.1`: real DOCX/PPTX extraction
- `v1.2`: source-grounded Wiki and MindMap extension
- `v1.3`: browser extension hardening
- `v1.4`: optional local OCR/ASR pipeline behind explicit permission
- `v1.5`: template marketplace / template packs
- `v2.0`: hosted or team workflows

Experimental platform adapters belong after `v1.0` and must keep the same low-risk, user-authorized boundaries.

## License

MIT. See [LICENSE](LICENSE).
