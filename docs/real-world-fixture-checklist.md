# Real-World Fixture Checklist

Use this checklist for human alpha testing. Synthetic fixtures prove the pipeline shape; real fixtures reveal extraction gaps, formatting loss, and degraded-source behavior.

Do not commit private, copyrighted, paid-course, credentialed, or user-sensitive materials. Keep test files local unless they are explicitly cleared for public sharing.

## Word / DOCX

Test at least one file with:

- title and nested headings
- normal paragraphs
- tables with multiple rows and columns
- comments or teacher notes
- headers and footers
- embedded images
- tracked changes or unusual formatting, if available

Expected check: `inspect -> ingest -> build-index -> generate -> validate` should preserve text evidence and warn where image pixels or complex layout are not fully parsed.

## PowerPoint / PPTX

Test at least one deck with:

- slide titles
- body text
- images
- charts or SmartArt
- speaker notes
- lecture-script style notes

Expected check: slides and speaker notes should become evidence; images/charts should be counted and warned when not structurally extracted.

## PDF

Test:

- native-text textbook or paper
- scanned PDF
- table-heavy PDF
- image-heavy PDF
- complex multi-column layout

Expected check: native text should extract; scanned/complex pages should be degraded or require OCR rather than silently passing as complete.

## Video

Test local, user-authorized media only:

- video with user-provided subtitle file
- video with slide changes
- video where interval keyframes are useful
- course clip where screenshots need OCR sidecar

Expected check: the project should not download platform videos. Local keyframe extraction should be optional and report unavailable if ffmpeg is missing.

## Audio

Test local, user-authorized files:

- `.mp3`
- `.wav`
- `.m4a`

Expected check: ASR is optional. If Whisper CLI is missing, the command should return structured `unavailable`; if present, transcript quality should be reviewed before evidence is treated as strong.

## WeChat Public Article

Test:

- user-saved HTML
- user-saved PDF
- browser current-page capture JSON

Expected check: no cookies, no account-history crawl, no simulated login, no Fiddler replay. Extraction should keep title, author/date when available, source path/URL, and warnings.

## Xiaohongshu

Test:

- user-exported Markdown
- user-exported JSON
- screenshot plus OCR sidecar

Expected check: no login-state scraping, no media downloading, no batch collection. Screenshots/OCR should carry confidence and warnings.

## Zhihu

Test:

- saved public HTML
- browser current-page capture JSON

Expected check: no App signature reverse engineering, no `x-zse` bypass, no account scraping. If the saved page lacks body text, intake should be degraded.

## Pass Criteria

A real fixture is useful when it records:

- source type
- source path or URL
- intake status
- extraction warnings
- evidence count
- validation result
- notes from human review

Record failing samples as issues with sanitized metadata and reproduction steps, not private source files.
