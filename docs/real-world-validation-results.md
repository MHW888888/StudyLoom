# Real-World Validation Results

This file is the public alpha log for real material validation. Do not commit private source files, paid course files, user data, cookies, tokens, browser profiles, or copyrighted full materials. Record anonymized results and reproduction notes only.

Use one section per material. If a failure needs a reproducible fixture, create a small synthetic fixture that preserves the structure of the bug without including private content.

## Result Template

```text
Material type:
Source description:
Privacy status:
Command sequence:
Intake status:
Detected assets:
Extraction warnings:
Generated output path:
Citation report status:
Learning quality report status:
Eval status:
Human review notes:
Issue category:
Follow-up task:
```

## Validation Command Sequence

Prefer this sequence for every real sample:

```powershell
source2study inspect "PATH_OR_EXPORT" --workspace ".\workspace\real-world-sample"
source2study ingest --workspace ".\workspace\real-world-sample" --source "PATH_OR_EXPORT"
source2study build-index ".\workspace\real-world-sample"
source2study generate ".\workspace\real-world-sample" --mode beginner --output ".\workspace\real-world-sample\outputs\beginner.md"
source2study validate ".\workspace\real-world-sample" --pack ".\workspace\real-world-sample\outputs\study_pack_beginner_full.json"
```

For persona-specific validation, add a profile:

```powershell
source2study generate ".\workspace\real-world-sample" --mode developer --profile ".\examples\personalized\profiles\developer.json" --output ".\workspace\real-world-sample\outputs\developer.md"
```

## Records

### Sample 001

```text
Material type:
Source description:
Privacy status:
Command sequence:
Intake status:
Detected assets:
Extraction warnings:
Generated output path:
Citation report status:
Learning quality report status:
Eval status:
Human review notes:
Issue category:
Follow-up task:
```

## Issue Categories

- source fidelity bug
- extraction degradation
- citation grounding bug
- learning quality issue
- output formatting bug
- template quality issue
- OCR/ASR/keyframe issue
- MCP safety issue
- compliance concern
- adapter request

## Review Rule

Passing automated validation is not enough for real-world readiness. Every real sample needs human notes about whether the output is actually useful, readable, and faithful to the source.
