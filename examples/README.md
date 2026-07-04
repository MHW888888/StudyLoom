# Demo Workflow

Run this from the repository root after `pip install -e .`:

```bash
source2study ingest \
  --workspace examples/workspace \
  --source examples/demo_sources/notes.md \
  --source examples/demo_sources/mini_repo \
  --source examples/demo_sources/lecture.vtt

source2study build-index examples/workspace

source2study generate examples/workspace \
  --mode beginner \
  --output examples/workspace/outputs/beginner.md

source2study validate examples/workspace \
  --pack examples/workspace/outputs/study_pack_beginner_full.json
```

Expected artifacts:

- `examples/workspace/manifest.json`
- `examples/workspace/evidence_index.json`
- `examples/workspace/outputs/beginner.md`
- `examples/workspace/outputs/study_pack_beginner_full.json`
- `examples/workspace/outputs/citation_report_beginner_full.json`
- `examples/workspace/outputs/learning_quality_report_beginner_full.json`

## Low-Risk Ingestion Demo

This demo covers saved social/article pages, browser current-page capture, screenshot/OCR sidecar text, and user-uploaded subtitles:

```bash
source2study ingest \
  --workspace examples/workspace-low-risk \
  --source examples/low_risk_sources/wechat_article.html \
  --source examples/low_risk_sources/xhs_note.json \
  --source examples/low_risk_sources/zhihu_page.html \
  --source examples/low_risk_sources/browser_capture.json \
  --source examples/low_risk_sources/slide.png \
  --source examples/low_risk_sources/course.srt

source2study generate examples/workspace-low-risk \
  --mode beginner \
  --output examples/workspace-low-risk/outputs/beginner.md

source2study validate examples/workspace-low-risk \
  --pack examples/workspace-low-risk/outputs/study_pack_beginner_full.json
```

No cookies, login sessions, media downloads, request signatures, or platform crawlers are used.

## Personalized Demo

The personalized demo uses one source set and four learner profiles:

```bash
source2study ingest \
  --workspace examples/workspace-personalized \
  --source examples/personalized/sources

source2study generate examples/workspace-personalized \
  --mode beginner \
  --profile examples/personalized/profiles/beginner.json \
  --output examples/workspace-personalized/outputs/beginner.md

source2study generate examples/workspace-personalized \
  --mode exam \
  --profile examples/personalized/profiles/exam.json \
  --output examples/workspace-personalized/outputs/exam.md

source2study generate examples/workspace-personalized \
  --mode developer \
  --profile examples/personalized/profiles/developer.json \
  --output examples/workspace-personalized/outputs/developer.md

source2study generate examples/workspace-personalized \
  --mode creator \
  --profile examples/personalized/profiles/creator.json \
  --output examples/workspace-personalized/outputs/creator.md
```

Each pack writes a citation report and a learning quality report.

## PDF Sidecar Demo

v0.6 keeps PDF export basic but always writes a same-name Markdown sidecar first:

```bash
source2study generate examples/workspace-personalized \
  --mode beginner \
  --profile examples/personalized/profiles/beginner.json \
  --output examples/workspace-personalized/outputs/beginner.pdf
```

Expected artifacts:

- `examples/workspace-personalized/outputs/beginner.pdf`
- `examples/workspace-personalized/outputs/beginner.md`
