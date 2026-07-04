# Browser Extension Hardening

The browser extension is a low-risk current-page export helper. It is not a crawler and it does not export browser credentials.

## Guarantees

- User-initiated current-page capture only.
- No cookies permission.
- No history permission.
- No browser profile export.
- No localStorage/sessionStorage export.
- Form controls, scripts, styles, iframes, and hidden elements are removed from exported HTML.
- Common token/header/private-key patterns are redacted from exported text and HTML.
- Exported JSON includes `schema_version`, `captured_at`, `sanitizer`, and `risk_warnings`.

## Non-Goals

- Account history crawling.
- Batch export.
- Login/session replay.
- Paywall, DRM, anti-bot, or signature bypass.
- Downloading platform media.

## Recommended Workflow

1. User opens a page they are allowed to process.
2. User clicks the StudyLoom extension.
3. The extension downloads one `.browser_capture.json` file.
4. `source2study ingest` imports that local JSON.
5. Intake and citation verifiers run before any learning pack is trusted.
