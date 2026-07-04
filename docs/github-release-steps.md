# GitHub Release Steps

Use this after the local repository is clean and verification passes.

## 1. Create Empty GitHub Repository

Create:

```text
Owner: mhw888888
Repository: StudyLoom
Visibility: Public or Private
```

Do not initialize with README, `.gitignore`, or LICENSE because the local repository already has them.

## 2. Confirm Local Remote

```powershell
git remote -v
git status
git log --oneline --decorate -3
git tag -l
```

If needed:

```powershell
git remote set-url origin https://github.com/mhw888888/StudyLoom.git
```

## 3. Push Main And Tags

```powershell
git push -u origin main --tags
```

If GitHub returns `Repository not found`, check that the repository exists, the owner/name are correct, and the current Git credentials have access.

## 4. Create Public Alpha Baseline Release

Tag:

```text
v1.0.0-alpha.0
```

Title:

```text
StudyLoom v1.0.0-alpha.0 - Public Alpha Baseline
```

Description source:

```text
docs/release-notes/v1.0.0-alpha.md
```

Positioning: recommended first demo baseline.

## 5. Create Experimental Alpha Extensions Release

Tag:

```text
v1.5.0-alpha.0
```

Title:

```text
StudyLoom v1.5.0-alpha.0 - Experimental Alpha Extensions
```

Description source:

```text
docs/release-notes/v1.5.0-alpha.md
```

Positioning: experimental extension line for DOCX/PPTX, Wiki/MindMap, browser capture hardening, local OCR/ASR/keyframes, and template packs.

## 6. Known Limitations To Include

- DOCX/PPTX extraction is conservative and not full layout reconstruction.
- OCR/ASR/keyframes are optional local tools.
- Video keyframes are interval-based.
- PDF output is basic; Markdown remains canonical.
- Browser capture is current-page only.
- Eval is deterministic and does not replace human quality review.
- No high-risk platform scraping is included.

## 7. Post-Release Smoke Test

In a fresh directory:

```powershell
git clone https://github.com/mhw888888/StudyLoom.git
cd StudyLoom
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
source2study --help
source2study inspect --help
python evals/run_eval.py --suite standard_demo
python mcp/server.py --list-tools
```

Do not call the release complete until the fresh clone passes.
