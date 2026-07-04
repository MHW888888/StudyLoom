# Public Alpha Triage

Use this guide to classify public alpha feedback. The goal is to separate source fidelity problems from output quality problems and compliance problems before deciding what to fix.

## Triage Principles

- Ask for reproduction steps, not private source files.
- Prefer `source2study inspect` output over screenshots of private content.
- Do not request cookies, tokens, browser profiles, private headers, paid course files, or login sessions.
- If a report involves copyrighted or sensitive material, ask for an anonymized synthetic fixture.
- Record whether the issue appears before or after `EvidenceIndex`; early intake problems have higher priority because every later output depends on them.

## Categories

### Source Fidelity Bug

Use when StudyLoom misidentifies or fails to preserve core material structure.

Priority:

- P0 if source content is silently dropped and output looks complete.
- P1 if intake warns correctly but the source is common and important.
- P2 if it affects unusual formatting and is already disclosed.

Needed information:

- source type
- sanitized `intake_report.json`
- expected assets
- detected assets
- extraction warnings
- minimal synthetic fixture if possible

### Extraction Degradation

Use when the source is partly understood but images, tables, notes, layout, subtitles, OCR regions, or keyframes are incomplete.

Priority:

- P1 for common Word/PPT/PDF structures.
- P2 for optional OCR/ASR/keyframe limitations.

Needed information:

- command sequence
- intake status
- warning text
- whether degradation was disclosed in generated output

### Citation Grounding Bug

Use when generated claims point to missing, wrong, or insufficient evidence.

Priority:

- P0 if unsupported claims are presented as verified facts.
- P1 if citation links are wrong but claims are plausible.

Needed information:

- generated pack path or sanitized excerpt
- citation report
- evidence ids involved
- expected evidence

### Learning Quality Issue

Use when the output is source-grounded but not helpful for the target learner.

Priority:

- P1 if the selected mode or persona is clearly ignored.
- P2 if wording, examples, or structure need improvement.

Needed information:

- mode
- LearnerProfile
- learning quality report
- human notes about what was confusing or missing

### Output Formatting Bug

Use when Markdown, DOCX, PDF, wiki, or mindmap output is malformed.

Priority:

- P1 if the file cannot open or critical sections disappear.
- P2 if layout is ugly but content is present.

Needed information:

- output format
- command
- renderer/viewer used
- small output excerpt or screenshot with private data removed

### Template Quality Issue

Use when a template pack does not fit its intended use case.

Priority:

- P1 if a required block is missing.
- P2 if the template needs better wording, sequencing, or examples.

Needed information:

- template id
- mode
- source type
- generated output notes

### OCR / ASR / Keyframe Issue

Use for optional local OCR, local ASR, or local video keyframe problems.

Priority:

- P1 if installed tools fail without structured error.
- P2 for low-confidence recognition quality or interval-keyframe limitations.

Needed information:

- local tool availability
- command output
- confidence values
- whether a transcript, sidecar, or screenshot workaround exists

### MCP Safety Issue

Use for agent tool boundary problems.

Priority:

- P0 if a tool exposes shell, arbitrary file read, credentials, cookies, or arbitrary URL fetch.
- P1 if redaction or workspace allowlist behavior is wrong.

Needed information:

- MCP tool name
- request payload with secrets removed
- response payload with secrets removed
- expected policy decision

### Compliance Concern

Use for copyright, privacy, platform terms, credential leakage, or unsafe scraping requests.

Priority:

- P0 for credential exposure or bypass functionality.
- P1 for unclear redistribution or privacy risks.

Needed information:

- affected source type
- public/private status
- what content may be sensitive
- whether output was intended for personal use or public sharing

### Adapter Request

Use when someone asks for a new source type or platform path.

Priority:

- P1 for low-risk local exports used by many users.
- P2 for niche but compliant local formats.
- Reject requests for cookies, login bypass, paywall bypass, DRM bypass, anti-bot bypass, signature reverse engineering, or bulk account crawling.

Needed information:

- source type
- low-risk import path
- user authorization model
- sample export format
- expected evidence locations

## Default First Response

Ask reporters to run:

```powershell
source2study inspect "PATH_TO_SAMPLE" --workspace ".\workspace\issue-repro"
```

Then ask for sanitized:

- intake status
- detected assets
- warnings/errors
- source type
- command sequence

Do not ask them to upload private materials.
