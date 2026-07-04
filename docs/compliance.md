# Compliance And Safety

Source2Study is designed for authorized learning workflows.

## Defaults

- Network access is off unless `--allow-network` is passed.
- Cookies, private headers, tokens, localStorage, and sessionStorage are not accepted by the CLI or browser-capture adapter.
- ASR is not enabled by default.
- Full copyrighted text output is not enabled.
- Platform-specific crawling that bypasses access controls is out of scope.

Use `source2study policy check SOURCE` to inspect whether a source is allowed before ingestion. The policy engine is shared by the CLI and should be reused by future Web UI and MCP entry points.

## MCP And Agent Tools

Agent integrations must use the same policy engine, intake quality gate, citation verifier, learning-quality verifier, and eval suites as the CLI.

The restricted MCP tools only accept allowlisted local paths by default. They must not expose:

- arbitrary URL fetching
- arbitrary local file reads
- shell execution
- cookies or tokens
- login sessions
- browser profiles
- private headers
- bulk platform crawling
- paywall bypass
- DRM bypass
- anti-bot bypass
- request-signature reverse engineering

MCP responses should return paths, status, metrics, and warnings rather than large source text. Responses must redact secrets and sensitive user paths.

## Public Sharing

Public-sharing outputs should prefer:

- links
- timestamps
- page references
- short excerpts
- source-grounded generated explanation

Avoid publishing full transcripts, full book text, paid-course material, or large screenshot sets without permission.

Use `--share-mode public_share` during generation or validation to apply stricter citation checks for public outputs.

## Difficult Sources

For WeChat public accounts, Xiaohongshu, Zhihu, paid courses, and login-gated content, prefer:

1. user-uploaded PDF/HTML/Markdown/screenshots
2. local browser capture with explicit user action
3. self-owned or explicitly authorized account exports
4. manual fallback with source links

Do not build the product around "grab everything." Build it around lawful, auditable, user-authorized evidence.

## Browser Capture

Browser capture is limited to the current visible page. A valid capture must use `capture_method: current_page_dom` and `user_initiated_capture: true`.

The capture file must not include:

- cookies
- raw request or response headers
- authorization tokens
- browser storage
- account-history lists
- bulk captures

## Screenshot/OCR

Screenshot/OCR is a fallback path for difficult sources. OCR text must carry confidence metadata. If OCR text is provided through a sidecar file, the evidence uses that text with medium confidence. If OCR is unavailable, the adapter emits a low-confidence placeholder rather than pretending text was recognized.
