# Contributing

Thanks for helping improve Source2Study.

Source2Study is a source-grounded personalized learning-pack generator, not a crawler. Contributions should improve source fidelity, evidence quality, personalized learning structure, export quality, safety, or reproducibility.

## Development Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Run checks:

```bash
python -m unittest discover -s tests
python -m compileall -q src evals mcp
source2study --help
source2study inspect --help
```

Run evals:

```bash
python evals/run_eval.py --suite standard_demo
python evals/run_eval.py --suite personalized_demo
python evals/run_eval.py --suite degraded_demo
```

## Adapter Contribution Rules

New adapters must include:

- capability matrix entry
- policy rule or documented policy decision
- small non-private fixture
- acceptance test
- blocked-path test
- `IntakeReport` coverage
- evidence records with source, location, confidence, and rights metadata
- eval coverage when the adapter affects generated output
- docs update

Do not submit an adapter that only "can scrape." The adapter must preserve source fidelity and fail safely.

## Source Fidelity Requirements

Adapters must not silently lose images, tables, slides, speaker notes, timestamps, OCR confidence, screenshots, page numbers, or source structure. If the current implementation cannot parse an asset, it should preserve what it can and emit a warning.

## Citation Requirements

Generated learning packs should be built from `EvidenceIndex`. Major claims, concept cards, examples, and source appendix entries should trace back to evidence IDs.

## Eval Requirements

Any change that affects generation, evidence records, intake reports, citation reports, learning-quality reports, or templates should include or update tests and eval expected files.

## MCP Tool Safety Rules

MCP and agent tools must not expose:

- shell execution
- arbitrary URL fetching
- arbitrary local file reads
- cookies or cookie replay
- login sessions or browser profiles
- private headers
- paywall, DRM, anti-bot, or signature bypass
- bulk platform crawling

Agent tools should return status, report paths, warnings, and metrics rather than large source text.

## Documentation Requirements

Update README or docs when you change:

- CLI commands
- source adapters
- safety policy
- learning modes or templates
- eval metrics
- MCP tools
- export behavior

## Contributions We Do Not Accept

- bypassing login, paywalls, DRM, anti-bot systems, or request signatures
- importing cookies, browser profiles, tokens, or private headers
- bulk crawling account history
- committing private content, paid course material, or copyrighted full text as fixtures
- agent tools that expose raw shell, filesystem, or network access
- broad refactors that do not improve user-visible quality or verification
