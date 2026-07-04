# Browser Capture

Browser capture is a low-risk import path for difficult sources such as WeChat public-account articles, Xiaohongshu notes, Zhihu pages, and other pages the user can already view.

It is not a crawler. It exports only the current page after a user action.

## JSON Protocol

```json
{
  "source_type": "browser_capture",
  "platform": "wechat",
  "title": "Article title",
  "author": "Author",
  "published_at": "2026-07-04",
  "url": "https://example.invalid/current-page",
  "content_html": "<article>...</article>",
  "text": "Visible page text...",
  "images": [],
  "capture_method": "current_page_dom",
  "user_initiated_capture": true
}
```

Import it with:

```bash
source2study ingest ./browser-captures/article.browser_capture.json \
  --source-type browser_capture \
  --workspace ./workspace/browser-capture
```

## Validation Rules

The adapter rejects captures that contain:

- cookies
- headers
- authorization tokens
- localStorage or sessionStorage
- account history
- multiple captured pages

The adapter requires:

- `capture_method: current_page_dom`
- user-initiated capture metadata
- readable text or HTML

## Extension Skeleton

The `browser-extension/` folder contains a minimal Manifest V3 example:

- `manifest.json`
- `content-script.js`
- `export-current-page.js`

The extension sends a message to the current tab, extracts visible DOM text and basic metadata, and downloads a local `.browser_capture.json` file. It does not export cookies, headers, tokens, storage, or history.
