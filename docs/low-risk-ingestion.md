# Low-Risk Real Ingestion

v0.4 turns the adapter contract into real local import paths while keeping high-risk crawling out of the default product.

## Allowed Paths

| Path | Adapter | Notes |
|---|---|---|
| Saved WeChat HTML | `WeChatHtmlAdapter` | User-provided local HTML only. |
| Xiaohongshu Markdown/JSON export | `XhsExportAdapter` | Reads local export text and optional OCR placeholder text. |
| Saved Zhihu HTML | `ZhihuHtmlAdapter` | User-provided public-page HTML only. |
| Browser current-page JSON | `BrowserCaptureAdapter` | Current visible page, user initiated, no cookies or headers. |
| Screenshot/OCR | `ScreenshotOcrAdapter` | Reads user image and optional `.ocr.txt` sidecar. |
| Transcript/subtitle | `TranscriptAdapter` | Reads `.srt`, `.vtt`, or explicit transcript `.txt`. |

## Examples

```bash
source2study ingest \
  --workspace examples/workspace-low-risk \
  --source examples/low_risk_sources/wechat_article.html \
  --source examples/low_risk_sources/xhs_note.json \
  --source examples/low_risk_sources/zhihu_page.html \
  --source examples/low_risk_sources/browser_capture.json \
  --source examples/low_risk_sources/slide.png \
  --source examples/low_risk_sources/course.srt
```

For generic filenames, force the adapter:

```bash
source2study ingest ./exports/article.html \
  --source-type wechat_html \
  --workspace ./workspace/wechat
```

## Required Metadata

Every v0.4 low-risk adapter writes:

- `capture_method`
- source title
- source URL or local path
- adapter capability
- risk level
- allowed methods
- blocked methods

Screenshot/OCR evidence also writes:

- `image_path`
- `ocr_confidence`
- `ocr_engine`
- region metadata

Browser-capture evidence also writes:

- `user_initiated_capture: true`
- `capture_method: current_page_dom`
- platform

## Out Of Scope

v0.4 does not implement:

- cookies or cookie replay
- login bypass
- paywall bypass
- DRM bypass
- anti-bot bypass
- request-signature reverse engineering
- account-history bulk crawling
- default video download
- default ASR
