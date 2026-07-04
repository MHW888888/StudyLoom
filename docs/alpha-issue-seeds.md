# Alpha Issue Seeds

These are suggested GitHub issues for organizing public alpha validation. Create them manually or with `gh issue create` after the repository is ready. Do not attach private materials to these issues.

## [Alpha] Real-world DOCX/PPTX validation

Goal:

- Validate conservative Office extraction against real lecture notes, handouts, and slide decks.

Validation materials:

- one real DOCX with headings, tables, comments, headers/footers, and images
- one real PPTX with slide text, images, charts, and speaker notes

Commands:

```powershell
source2study inspect "sample.docx" --workspace ".\workspace\alpha-docx"
source2study ingest --workspace ".\workspace\alpha-docx" --source "sample.docx"
source2study build-index ".\workspace\alpha-docx"
source2study generate ".\workspace\alpha-docx" --mode teacher --output ".\workspace\alpha-docx\outputs\teacher.md"
source2study validate ".\workspace\alpha-docx" --pack ".\workspace\alpha-docx\outputs\study_pack_teacher.json"
```

Acceptance criteria:

- intake status is `pass` or correctly `degraded`
- extracted headings/tables/notes are represented as evidence
- missing visual/chart semantics are warned, not hidden
- generated pack includes Source Intake Summary and Source Appendix

## [Alpha] Real-world PDF and scanned PDF validation

Goal:

- Validate native PDF extraction and degraded handling for scanned or complex-layout PDFs.

Validation materials:

- native text PDF
- scanned/image PDF
- table-heavy PDF
- image-heavy PDF

Commands:

```powershell
source2study inspect "sample.pdf" --workspace ".\workspace\alpha-pdf"
source2study ingest --workspace ".\workspace\alpha-pdf" --source "sample.pdf"
source2study build-index ".\workspace\alpha-pdf"
source2study generate ".\workspace\alpha-pdf" --mode review --output ".\workspace\alpha-pdf\outputs\review.md"
source2study validate ".\workspace\alpha-pdf" --pack ".\workspace\alpha-pdf\outputs\study_pack_review.json"
```

Acceptance criteria:

- native text is extracted with page/source metadata
- scanned/complex pages are marked degraded or require OCR
- no generated output pretends missing tables/images were fully parsed

## [Alpha] Local video/audio validation

Goal:

- Validate local transcript, optional ASR, and optional keyframe workflows without platform downloading.

Validation materials:

- local course video with user-provided subtitles
- local audio file
- local video where interval keyframes are useful

Commands:

```powershell
source2study ingest --workspace ".\workspace\alpha-media" --source "lecture.srt"
source2study asr inspect "lecture.mp4"
source2study keyframes inspect "lecture.mp4"
source2study build-index ".\workspace\alpha-media"
source2study generate ".\workspace\alpha-media" --mode beginner --output ".\workspace\alpha-media\outputs\beginner.md"
```

Acceptance criteria:

- no platform video is downloaded
- missing local tools return structured unavailable status
- transcript evidence carries timestamps
- low-confidence ASR/OCR is not treated as strong fact

## [Alpha] Browser capture validation

Goal:

- Validate current-page browser capture for saved web materials without cookies or bulk crawling.

Validation materials:

- saved WeChat article
- saved Zhihu page
- Xiaohongshu Markdown/JSON export or screenshot OCR
- ordinary article page captured with browser JSON

Commands:

```powershell
source2study inspect "browser_capture.json" --workspace ".\workspace\alpha-browser"
source2study ingest --workspace ".\workspace\alpha-browser" --source "browser_capture.json"
source2study build-index ".\workspace\alpha-browser"
source2study generate ".\workspace\alpha-browser" --mode creator --output ".\workspace\alpha-browser\outputs\creator.md"
```

Acceptance criteria:

- title, URL, text, and capture method are recorded
- empty body text becomes degraded
- no cookies, browser profiles, local storage, or login sessions are requested

## [Alpha] Template quality review

Goal:

- Check whether template packs produce useful structures for real users.

Validation materials:

- one source set for exam review
- one source set for teacher notes
- one source set for developer project learning
- one source set for creator script planning

Commands:

```powershell
source2study templates list
source2study generate ".\workspace\alpha-template" --mode exam --output ".\workspace\alpha-template\outputs\exam.md"
source2study generate ".\workspace\alpha-template" --mode developer --output ".\workspace\alpha-template\outputs\developer.md"
```

Acceptance criteria:

- template-specific required blocks appear
- Source Intake Summary and Source Appendix are present
- human reviewer says the structure fits the intended use case

## [Alpha] Source fidelity regression tracker

Goal:

- Keep a single tracker for silent data loss, wrong source metadata, or missing warnings across all source types.

Validation materials:

- any source that regresses after a change

Commands:

```powershell
source2study inspect "sample" --workspace ".\workspace\regression"
source2study validate ".\workspace\regression"
```

Acceptance criteria:

- every regression includes source type, intake status, expected assets, detected assets, and whether warnings were disclosed
- no regression is fixed only in the generator if the real issue is intake
