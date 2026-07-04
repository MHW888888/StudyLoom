# Source Adapter Research And Roadmap

This note tracks when and how Source2Study should add platform-specific source adapters.

## Timing

Do not add high-risk platform crawling before reliability gates are stable.

Recommended order:

```text
v0.2 Reliability & Grounding
  manifest, cache, policy engine, citation reports, demo workflow

v0.3 Adapter Research & Contracts
  source capability matrix, adapter test harness, policy rules, mock fixtures

v0.4 Low-Risk Real Ingestion
  saved WeChat HTML, Xiaohongshu Markdown/JSON export, saved Zhihu HTML,
  browser current-page capture JSON, screenshot/OCR sidecar text,
  Bilibili/YouTube/course subtitle imports

v1.0+ Experimental Adapters
  opt-in platform-specific adapters behind explicit flags, no cookies in cloud,
  no bypass of login/paywall/DRM/anti-bot controls
```

## Lessons From GitHub Projects

### Multi-platform crawlers

MediaCrawler is useful for learning adapter architecture, platform capability matrices, Playwright-based flows, Web UI ideas, and resume-oriented crawling design.

Do not copy its default posture into Source2Study. Source2Study is a learning-pack generator, not a social-media crawler. Login state, QR login, proxy pools, and large-scale crawling should remain outside default behavior.

Reference:

```text
https://github.com/NanmiCoder/MediaCrawler
```

### Xiaohongshu / RedNote

XHS-Downloader and ReaJason/xhs show common Xiaohongshu patterns:

- note URL parsing
- note metadata extraction
- image/video file handling
- optional cookie/browser integration
- duplicate/download cache ideas
- CLI and API surfaces

Source2Study should not default to downloading RedNote media. The safe adapter should start with:

```text
user_export:
  screenshots, saved HTML, Markdown, copied text, local images/video

local_browser_capture:
  user clicks "send current page to Source2Study"

manual_fallback:
  preserve URL and ask for user-provided evidence
```

References:

```text
https://github.com/JoeanAmier/XHS-Downloader
https://github.com/ReaJason/xhs
```

### WeChat public account articles

There are two very different patterns:

1. Safer public-article parsing, with no cookies and no anti-bot bypass.
2. Fiddler/cookie/request replay flows for history and comments.

Source2Study should follow pattern 1 first. The MCP-style WeChat article reader is a good reference because it explicitly limits itself to publicly accessible article URLs, avoids cookies/login sessions, and documents anti-bypass constraints.

The Fiddler/cookie approach is useful mainly as a warning: it can involve rapidly expiring cookies and request parameters, manual packet capture, and comment endpoints. That does not belong in default Source2Study behavior.

References:

```text
https://github.com/jj-cheng25/weixin-articles-mcp
https://github.com/hzhu212/wechat-mp-crawler
```

### Zhihu

Zhihu has public-page and reverse-engineering approaches. Projects that calculate or bypass request signatures are not suitable for Source2Study default adapters.

Start with:

```text
user_export:
  saved HTML, PDF, Markdown, screenshots

public_page:
  only if readable without login or bypass

manual_fallback:
  source URL plus user-provided excerpts/screenshots
```

Avoid:

```text
signature bypass
reverse-engineered app APIs
cookie/token handling
login-gated batch crawling
```

Reference:

```text
https://github.com/lostjay/zhihu_android_crawler
```

## Source2Study Adapter Acceptance Checklist

Before adding a real adapter:

```text
1. Has a capability record.
2. Has policy-engine approval rules.
3. Has a blocked-source test.
4. Has a user-export fixture.
5. Emits SourceRecord and EvidenceRecord only.
6. Does not leak cookies, tokens, private headers, or signed URLs.
7. Has rate limits or bounded work.
8. Fails closed with safe alternatives.
9. Writes manifest and cache entries.
10. Passes citation verifier with generated demo output.
```

## v0.3 Completed Work Items

```text
1. Add source capability matrix file.
2. Add adapter acceptance tests.
3. Add mock fixtures for xhs_export, zhihu_export, wechat_public_article.
4. Add policy rules for xhs / zhihu / wechat states:
   blocked_direct, allowed_user_export, allowed_public_page, allowed_local_browser.
5. Add placeholder adapters that accept only user-exported files first.
6. Keep direct platform extraction behind experimental flags only after review.
```

## v0.4 Completed Work Items

```text
1. Add local import adapters for saved WeChat HTML, Xiaohongshu Markdown/JSON, and saved Zhihu HTML.
2. Add BrowserCaptureAdapter for current-page JSON.
3. Add ScreenshotOcrAdapter with sidecar OCR text and ocr_confidence metadata.
4. Add TranscriptAdapter for user-uploaded SRT/VTT/transcript text.
5. Add browser-extension skeleton that exports current-page JSON only.
6. Add acceptance tests for allowed local imports and blocked cookie/bulk paths.
```

## Recommended v1.0+ Boundary

```text
1. Keep direct platform adapters explicit opt-in.
2. Verify each live adapter with small fixture-like tests and policy receipts.
3. Do not add cookies, proxy pools, login bypass, paywall bypass, DRM bypass, anti-bot bypass, or signature reverse engineering.
4. Prefer public captions, official/public metadata, local browser capture, and user exports.
```

The goal is not "scrape everything". The goal is "authorized source material becomes traceable evidence".
