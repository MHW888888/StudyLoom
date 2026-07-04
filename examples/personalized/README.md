# Personalized Demo

This demo uses the same sources to generate different learning packs for different user goals.

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

Each generation writes:

- `study_pack_<mode>.json`
- `citation_report_<mode>.json`
- `learning_quality_report_<mode>.json`
- the requested Markdown output
