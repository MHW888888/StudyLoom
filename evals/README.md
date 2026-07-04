# Source2Study Evals

The v0.7 eval system is deterministic by default. It does not require an LLM judge.

Quality is measured through this chain:

```text
Source Fidelity -> Evidence Quality -> Citation Grounding -> Learning Quality -> Output Fit
```

## Suites

```bash
python evals/run_eval.py --suite standard_demo
python evals/run_eval.py --suite personalized_demo
python evals/run_eval.py --suite degraded_demo
```

Each run creates a temporary workspace, runs the real Source2Study CLI pipeline, reads generated reports, computes metrics, writes `eval_report.json`, and removes the temporary workspace.

## Suites Included

- `standard_demo`: local notes plus a mini repo; checks intake, evidence, citations, and output structure.
- `personalized_demo`: one source set, four personas: beginner, exam, developer, creator.
- `degraded_demo`: low-confidence OCR fixture; checks degraded intake disclosure and low-confidence evidence reporting.

## Metrics

Source fidelity:

- `intake_pass_rate`
- `intake_degraded_rate`
- `intake_fail_rate`
- `blocked_source_count`
- `extraction_warning_count`
- `source_asset_coverage`
- `degraded_output_disclosure`

Evidence quality:

- `low_confidence_evidence_rate`
- `missing_location_rate`

Citation grounding:

- `citation_coverage`
- `missing_citation_rate`
- `unsupported_claim_rate`

Learning and output fit:

- `concept_coverage`
- `mode_fit`
- `learner_profile_fit`
- `quiz_presence`
- `practice_task_presence`
- `source_appendix_presence`
- `policy_compliance`

## References That Inspired The Shape

The implementation borrows ideas from common open-source eval patterns: fixtures and expected files, JSON result artifacts, threshold-based checks, and CI-friendly deterministic runs. It intentionally avoids adding those projects as runtime dependencies.
