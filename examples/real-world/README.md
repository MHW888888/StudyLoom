# Real-World Examples Policy

This directory is for instructions and sanitized reproduction notes only.

Do not commit:

- real user files
- private course materials
- paid course exports
- copyrighted full books or slides
- cookies
- tokens
- API keys
- login sessions
- browser profiles
- private local paths
- raw screenshots containing personal data

For real-world alpha testing, keep the source files outside the repository and record anonymized results in `docs/real-world-validation-results.md`.

When a bug needs a repository fixture, create a synthetic fixture that reproduces the structure of the problem without copying private content. For example:

- a tiny DOCX with one nested table instead of a real company handout
- a two-slide PPTX with fake speaker notes instead of a paid lecture deck
- a short Markdown export with placeholder text instead of a real social post
- a generated screenshot with dummy OCR text instead of a real user screen

Use this workflow:

```powershell
source2study inspect "PATH_TO_LOCAL_SAMPLE" --workspace ".\workspace\real-world-sample"
source2study ingest --workspace ".\workspace\real-world-sample" --source "PATH_TO_LOCAL_SAMPLE"
source2study build-index ".\workspace\real-world-sample"
source2study generate ".\workspace\real-world-sample" --mode beginner --output ".\workspace\real-world-sample\outputs\beginner.md"
source2study validate ".\workspace\real-world-sample" --pack ".\workspace\real-world-sample\outputs\study_pack_beginner_full.json"
```

If intake is `degraded` or `fail`, do not hide that status. The degraded or failed intake result is the useful alpha finding.
