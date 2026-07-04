# Architecture

Source2Study has one shared engine and multiple entry points.

```text
CLI / Web UI / MCP / Agent Skill
-> source adapters
-> intake report
-> source ledger
-> evidence ledger
-> evidence index
-> generation modes
-> exporter
-> quality gates
```

v0.2 adds reliability artifacts:

```text
manifest.json
.source2study/cache/
outputs/study_pack_<mode>.json
outputs/citation_report_<mode>.json
```

## Engine Boundary

Adapters handle source-specific extraction. Everything after adapters should operate on normalized `SourceRecord` and `EvidenceRecord` data.

This keeps platform changes from leaking into generation, rendering, and quality checks.

## Source Fidelity First

The first step is source intake, not generation.

```text
Intake -> Preserve -> Inspect -> Extract -> Verify -> Generate
```

Every source should produce an `IntakeReport` that records detected assets, extraction quality, warnings, errors, fallback options, and next safe actions. If intake is `blocked`, later stages must stop. If intake is `fail`, later stages stop unless the user explicitly accepts degraded processing. If intake is `degraded`, generated packs must label the risk.

## MVP Modules

- `adapters/`: source-specific ingestion with safe fallbacks.
- `models/`: serializable source, evidence, and study-pack models.
- `intake.py`: source fidelity reports, summaries, and intake quality gates.
- `indexing/`: `EvidenceIndex` and lightweight retrieval.
- `generation/`: deterministic first-pass pack writer and verifier.
- `exporters/`: Markdown, minimal DOCX, simple PDF, wiki, and mindmap.
- `ocr/`, `asr/`, `video/`: optional local OCR, ASR, and keyframe helpers.
- `safety/`: redaction, permission checks, copyright-oriented output policy.
- `cli.py`: user-facing local workflow.
- `mcp/`: restricted agent tool wrappers around the CLI workflow; no shell, arbitrary paths, arbitrary URLs, cookies, login state, or platform bypasses.

## Quality Gates

The MVP blocks completion when:

- source ledger is empty
- evidence ledger is empty
- generated sections lack evidence IDs
- evidence references are missing
- obvious secrets appear in evidence text
- generated pack citations point to missing evidence IDs
- evidence records lack a source or usable location
- public-share mode tries to use restricted or unknown evidence
- intake status is blocked
- intake status is failed and the user did not pass `--allow-degraded`

`validate --pack` produces a machine-readable citation report. `generate` writes the same report next to the generated pack.

Future gates should compare rendered PDF/DOCX against Markdown to ensure citations survive export.

## Agent Tool Boundary

MCP and skill integrations are entry points, not privileged backdoors. They should call the same policy, intake, generation, validation, and eval code paths as the CLI.

The allowed agent workflow is:

```text
policy_check -> inspect_local -> ingest_local -> build_index -> generate_pack -> validate_pack -> run_eval
```

Tool responses should contain paths, report status, warnings, and metrics. They should not return large source text or sensitive local paths.
