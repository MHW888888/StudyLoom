# Personalized Learning Experience

v0.5 upgrades Source2Study from source import plus summarization into a source-grounded personalized learning-pack generator.

## Pipeline

```text
Source -> EvidenceIndex -> ConceptGraph -> LearnerProfile
-> LearningPackSpec -> Personalized StudyPack -> Quality Reports
```

## LearnerProfile

Profiles describe who the pack is for:

```json
{
  "goal": "Understand gradient descent and build a small demo",
  "current_level": "beginner",
  "time_budget": "3 hours",
  "preferred_style": "plain explanation and exercises",
  "use_case": "self_study",
  "must_include": ["prerequisites", "quiz", "practice task"],
  "avoid": ["too many formulas"]
}
```

Use a profile file:

```bash
source2study generate ./workspace/demo \
  --mode beginner \
  --profile examples/personalized/profiles/beginner.json \
  --output ./workspace/demo/outputs/beginner.md
```

Or pass lightweight CLI overrides:

```bash
source2study generate ./workspace/demo \
  --mode developer \
  --goal "Build a small project" \
  --level intermediate \
  --time-budget "2 hours" \
  --use-case developer \
  --style "code path and debug checklist"
```

## Pack Types

| Mode | Persona | Focus |
|---|---|---|
| `beginner` | beginner | Learning map, prerequisites, concept cards, quiz, practice task. |
| `review` | review | High-frequency concepts, misconceptions, quiz, summary sheet. |
| `exam` | exam | Definitions, traps, checkpoint quiz, answer guide. |
| `developer` | developer | Project map, code/evidence path, practice task, debug checklist. |
| `creator` | creator | Opening hook, storyline, concept cards, audience questions. |
| `teacher` | teacher | Lesson map, prerequisite patch, in-class questions, homework. |
| `research` | research | Concept map, source comparison, caveats, open questions. |

## Learning Quality Gate

Every personalized generation writes:

```text
outputs/learning_quality_report_<mode>.json
```

The report checks:

- persona fit
- difficulty fit
- citation coverage
- concept coverage
- engagement score
- quiz/practice/source appendix presence when required

Citation verifier still checks evidence grounding. Learning quality verifier checks whether the pack is useful for the intended learner.
