# Source Adapters

Adapters must emit a capability record, a source ledger entry, and evidence records.

Source Fidelity First: adapters must not silently drop meaningful source structure. If an adapter cannot preserve important assets such as tables, images, slides, speaker notes, timestamps, comments, or OCR confidence, it should emit an intake warning, mark the source degraded, or stay planned/blocked until fidelity tests exist.

## Capability Fields

```text
source_type
availability
supported_methods
required_authorization
expected_outputs
known_risks
fallbacks
last_verified
risk_level
default_enabled
allowed_methods
blocked_methods
```

## v0.3 Adapter Contract

Each adapter must expose:

```text
can_handle(source)
policy_check(source)
extract(source, workspace)
fallback_options(source)
```

`ingest()` remains the internal method that returns a source record plus evidence records. `extract()` is a thin contract method for tools that only need evidence records.

## MVP Adapters

| Adapter | Status | Notes |
|---|---|---|
| PDF/text/Markdown | Implemented | PDF requires optional `pypdf`; text/Markdown work without dependencies. |
| DOCX/Word (`DocxAdapter`) | Planned placeholder | Must eventually preserve headings, body text, tables, images, comments, footnotes, headers, and footers. Default ingest is blocked until structure can be reported safely. |
| PPTX/slides (`PptxAdapter`) | Planned placeholder | Must eventually preserve slide order, titles, body text, images, charts, speaker notes, and relevant animation/order hints. Default ingest is blocked until structure can be reported safely. |
| Local GitHub-style directory | Implemented | Reads README, docs, examples, tests, manifests, and small text files. |
| Public GitHub URL | Implemented behind `--allow-network` | Uses shallow `git clone`; no tokens are passed. |
| Webpage | Implemented behind `--allow-network` or local HTML | Basic HTML text extraction only. |
| Local video/audio transcript | Implemented | Requires `.vtt`, `.srt`, or `.txt` transcript; no ASR yet. |
| Bilibili URL | Blocked by design in MVP | User should provide subtitles, transcript, or local file. |
| WeChat public article export | Implemented in v0.4 | Reads saved local WeChat-style HTML only; no direct crawling. |
| Xiaohongshu export | Implemented in v0.4 | Reads saved Markdown/JSON exports; no media download. |
| Zhihu public page export | Implemented in v0.4 | Reads saved local Zhihu-style HTML only; no signature bypass. |
| Browser capture | Implemented in v0.4 | Reads local current-page JSON; rejects cookies, headers, tokens, storage, and bulk captures. |
| Screenshot/OCR | Implemented in v0.4 | Reads local image and optional `.ocr.txt` sidecar; records `ocr_confidence`. |
| Transcript import | Implemented in v0.4 | Reads user-uploaded `.srt`, `.vtt`, or explicit transcript `.txt`; no video download. |

See `docs/source-capability-matrix.md` for the full staged matrix.

## Adapter Rule

Do not silently switch to weak extraction. If extraction is blocked or unsupported, return a fallback that tells the user what material to provide.

Adapters should be called after the shared policy engine approves a source. Keep high-risk platform decisions in policy first, then let adapters handle source-specific extraction.

## Forbidden Defaults

Adapters must not default to:

- cookie replay
- account-history bulk crawling
- login bypass
- paywall bypass
- DRM bypass
- anti-bot bypass
- request-signature bypass
- unrestricted media download
