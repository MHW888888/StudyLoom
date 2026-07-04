# Fresh Clone Validation

Use this checklist after pushing StudyLoom to GitHub. The goal is to prove that a new user can clone the repository, install the package, run the quickstart, and execute the quality gates without depending on the original Codex workspace.

## 1. Clone Into A Clean Directory

```powershell
git clone https://github.com/mhw888888/StudyLoom.git
cd StudyLoom
```

If the repository is private, authenticate with GitHub first. Do not copy any `.source2study`, `workspace`, `tmp`, `.venv`, or cache directory from another checkout.

## 2. Create A Fresh Environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

The base install should not require Tesseract, Whisper, ffmpeg, browser profiles, cookies, or network access.

## 3. Quick CLI Smoke

```powershell
source2study --help
source2study inspect --help
python mcp/server.py --list-tools
```

Expected result: each command exits successfully and lists local, restricted tools only.

## 4. Standard Quickstart

Run the README standard demo exactly as written:

```powershell
source2study ingest `
  --workspace ./workspace/standard-demo `
  --source ./examples/demo_sources/notes.md `
  --source ./examples/demo_sources/mini_repo `
  --source ./examples/demo_sources/lecture.vtt

source2study build-index ./workspace/standard-demo
source2study generate ./workspace/standard-demo --mode beginner --output ./workspace/standard-demo/outputs/beginner.md
source2study validate ./workspace/standard-demo --pack ./workspace/standard-demo/outputs/study_pack_beginner_full.json
```

Check that these files exist:

- `workspace/standard-demo/intake_report.json`
- `workspace/standard-demo/evidence_index.json`
- `workspace/standard-demo/outputs/beginner.md`
- `workspace/standard-demo/outputs/citation_report_beginner_full.json`

## 5. Eval Suites

```powershell
python evals/run_eval.py --suite standard_demo
python evals/run_eval.py --suite personalized_demo
python evals/run_eval.py --suite degraded_demo
```

Expected result: each suite prints a passing `eval_report.json`. A degraded suite may include warnings, but it must disclose degraded intake in the generated output.

## 6. Optional Extension Smokes

These commands should degrade gracefully if optional local tools are missing:

```powershell
source2study ocr ./examples/low_risk_sources/slide.png
source2study asr inspect
source2study keyframes inspect
source2study templates list
```

Do not install optional tools just to make the fresh-clone baseline pass.

## 7. Cleanup

```powershell
Remove-Item -Recurse -Force .\workspace, .\tmp, .\.source2study -ErrorAction SilentlyContinue
```

Runtime workspaces, caches, eval outputs, and temporary artifacts should not appear in `git status`.
