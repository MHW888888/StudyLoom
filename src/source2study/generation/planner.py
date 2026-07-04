from __future__ import annotations

from source2study.models.study_pack import StudyMode


def section_plan(mode: StudyMode) -> list[tuple[str, str]]:
    plans = {
        StudyMode.BEGINNER_FULL: [
            ("Learning Goal", "what problem this material helps solve"),
            ("Prerequisites", "missing concepts and vocabulary"),
            ("Plain Explanation", "beginner-friendly explanation"),
            ("Worked Example", "minimal concrete example"),
            ("Common Misconceptions", "likely mistakes and traps"),
            ("Review Questions", "short self-check questions"),
        ],
        StudyMode.QUICK_FRAMEWORK: [
            ("Topic Map", "main structure and sequence"),
            ("Key Concepts", "core terms and relationships"),
            ("Minimum Viable Understanding", "what to remember first"),
            ("Watch Or Read First", "recommended source order"),
        ],
        StudyMode.DEEP_ANALYSIS: [
            ("Concept Relationships", "deeper links across evidence"),
            ("Source Comparison", "agreement, tension, or missing context"),
            ("Formal Details", "definitions, assumptions, and caveats"),
            ("Further Work", "what needs deeper source material"),
        ],
        StudyMode.EXAM_REVIEW: [
            ("High-Frequency Concepts", "review focus"),
            ("Trap List", "common exam and interview traps"),
            ("Practice Questions", "questions with evidence-backed answers"),
        ],
        StudyMode.PROJECT_PRACTICE: [
            ("Project Goal", "hands-on outcome"),
            ("Milestones", "implementation steps"),
            ("Evidence-Linked Hints", "hints tied to sources"),
            ("Review Rubric", "how to check the work"),
        ],
        StudyMode.TEACHER_NOTES: [
            ("Lecture Outline", "teaching order"),
            ("Board Plan", "what to write or show"),
            ("In-Class Questions", "discussion prompts"),
            ("Homework", "follow-up tasks"),
        ],
        StudyMode.REVIEW: [
            ("High-Frequency Concepts", "review focus"),
            ("Misconception Box", "common mistakes"),
            ("Checkpoint Quiz", "retrieval practice"),
            ("Summary Sheet", "fast review"),
        ],
        StudyMode.DEVELOPER: [
            ("Project Map", "implementation path"),
            ("Concept Cards", "technical concepts"),
            ("Practice Task", "hands-on work"),
            ("Debug Checklist", "likely implementation issues"),
        ],
        StudyMode.CREATOR: [
            ("Opening Hook", "audience motivation"),
            ("Storyline", "teaching sequence"),
            ("Concept Cards", "explainable concepts"),
            ("Audience Questions", "engagement prompts"),
        ],
        StudyMode.RESEARCH: [
            ("Concept Map", "core concepts and prerequisites"),
            ("Source Comparison", "source agreement and gaps"),
            ("Definitions And Caveats", "precise claims"),
            ("Open Questions", "further inquiry"),
        ],
    }
    return plans[mode]
