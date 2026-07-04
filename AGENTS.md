# AGENTS.md

Source2Study is a source-grounded learning-pack engine, not a crawler or a generic summarizer.

Highest priority: Source Fidelity First. Inspect, preserve, extract, and verify user-provided material before generating. Do not silently drop images, tables, slides, timestamps, speaker notes, OCR confidence, or source structure.

## Project Rules

- Keep generated study claims tied to evidence records.
- Default to safe, local-first behavior. Downloads, cookies, ASR, private sources, and copyrighted full-content processing must be opt-in.
- Do not add platform scraping that bypasses login, paywalls, DRM, anti-bot protections, or access controls.
- Keep source adapters thin. Normalize all extracted material into source and evidence ledgers.
- Generate and respect intake reports. Block `blocked` intake, and do not ignore degraded extraction warnings.
- Preserve previous outputs unless the user explicitly asks to overwrite them.
- Add tests for grounding, authorization failure, export, and cache/resume behavior when changing the pipeline.
- Keep `manifest.json`, cache keys, and citation reports reproducible when changing adapters or generation.
- Agent/MCP entry points must stay minimal and auditable. Do not expose shell execution, arbitrary URL fetches, arbitrary local path reads, cookies, login state, browser profiles, platform bypasses, or bulk scraping.
- MCP tools must respect workspace allowlists, intake quality gates, redaction, citation validation, learning-quality verification, and eval suites.

## MVP Scope

The first runnable scope is:

- local PDF/text/Markdown files
- local GitHub-style directories
- ordinary webpages when network access is explicitly allowed
- local video subtitle files or companion transcript files
- Markdown, DOCX, and simple PDF export

Xiaohongshu, WeChat public accounts, paid course platforms, cookies, ASR, and heavy OCR are adapter-planned but not default MVP behavior.

## Verification

Run:

```bash
pip install -e .
python -m unittest discover -s tests
python -m source2study.cli --help
source2study policy check https://www.bilibili.com/video/BV123
python evals/run_eval.py --suite standard_demo
```
