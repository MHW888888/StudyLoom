# Learning Mode Patterns

This note records release-prep research observations without copying third-party implementation.

## Useful Patterns From Neighboring Projects

- Interactive learning packs often combine structured notes, quizzes, flashcards, and review schedules instead of stopping at summaries.
- Lecture study-guide prompts commonly ask for outlines, key concepts, definitions, formulas, exam questions, clarification gaps, and connections to prior topics.
- Paper-reading skills often work best when they separate the source audit, concept explanation, evidence references, and final note structure.
- Paper-to-course style skills show the value of output-specific templates: course page, slide deck, notes, quiz, visual elements, and offline artifacts.
- Agent skill repositories emphasize concise `SKILL.md` instructions, supporting references/scripts, clear trigger descriptions, and quality over bulk-generated skills.

## Source2Study Adaptation

Source2Study should keep these ideas, but route them through its own gates:

```text
Source Fidelity -> EvidenceIndex -> LearningPackSpec -> Verifiers -> Eval
```

## Template Families

Future template packs can include:

- beginner onboarding
- exam/interview review
- developer project guide
- creator script
- teacher lecture handout
- research paper deep-read
- enterprise training guide

Each template should declare:

- target user
- expected time budget
- required blocks
- citation requirements
- quiz or practice requirements
- source appendix requirements
- eval thresholds

## Skill File Guidelines

Skill files should:

- state when to use the skill and when not to use it
- keep the main workflow short
- point to scripts and references instead of embedding everything
- require source inspection before generation
- require validation after generation
- explicitly reject unsafe requests

## What Not To Copy

- broad "scrape any platform" positioning
- hidden credentials or cookie workflows
- unverified generated claims
- long prompt-only workflows that bypass evidence ledgers
- generated skills without real usage or tests
