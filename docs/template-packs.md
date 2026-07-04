# Template Packs

Template packs define reusable learning-product shapes. They do not bypass source fidelity, citation verification, or learning-quality checks.

## Commands

```bash
source2study templates list
source2study templates show exam-review
source2study templates copy developer-project --workspace ./workspace/demo
source2study templates copy all --workspace ./workspace/demo
```

## Built-In Packs

- `exam-review`: definitions, traps, quiz, and one-page review.
- `teacher-lecture`: lesson goals, teaching sequence, activities, homework, and assessment.
- `developer-project`: repo map, minimal demo, practice task, and debugging checklist.
- `creator-script`: hook, story arc, visual beats, and public-share caution.
- `enterprise-training`: role scenarios, workflow steps, action checklist, and manager review questions.

## Contribution Rules

A new template pack must include:

- stable `id`
- target `use_case`
- target `mode`
- required blocks
- output bias
- safety notes

It must not request cookies, login sessions, paywall bypass, DRM bypass, signature reverse engineering, or unsupported source claims.
