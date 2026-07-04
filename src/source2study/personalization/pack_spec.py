from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from source2study.models.study_pack import StudyMode
from source2study.personalization.learner_profile import LearnerProfile


@dataclass(frozen=True)
class LearningPackSpec:
    pack_type: str
    persona: str
    tone: str
    structure: list[str]
    engagement_devices: list[str]
    evidence_requirement: str = "every_core_claim"
    required_blocks: list[str] = field(default_factory=list)
    quiz_required: bool = True
    practice_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "pack_type": self.pack_type,
            "persona": self.persona,
            "tone": self.tone,
            "structure": self.structure,
            "engagement_devices": self.engagement_devices,
            "evidence_requirement": self.evidence_requirement,
            "required_blocks": self.required_blocks,
            "quiz_required": self.quiz_required,
            "practice_required": self.practice_required,
        }


class LearningPackSpecBuilder:
    def build(self, profile: LearnerProfile, mode: StudyMode) -> LearningPackSpec:
        persona = self._persona(profile, mode)
        specs = {
            "beginner": LearningPackSpec(
                pack_type="beginner_project",
                persona="beginner",
                tone="clear and encouraging",
                structure=[
                    "Learning Outcomes",
                    "Learning Map",
                    "Prerequisite Patch",
                    "Concept Cards",
                    "Evidence Walkthrough",
                    "Checkpoint Quiz",
                    "Practice Task",
                    "Source Appendix",
                ],
                engagement_devices=["opening_hook", "progress_checkpoints", "worked_examples", "reflection_questions"],
                required_blocks=["learning_map", "prerequisite_patch", "concept_card", "quiz_block", "source_appendix"],
                quiz_required=True,
                practice_required=True,
            ),
            "review": LearningPackSpec(
                pack_type="review_sheet",
                persona="review",
                tone="concise and focused",
                structure=[
                    "Learning Outcomes",
                    "Learning Map",
                    "High-Frequency Concepts",
                    "Misconception Box",
                    "Checkpoint Quiz",
                    "Summary Sheet",
                    "Source Appendix",
                ],
                engagement_devices=["retrieval_practice", "memory_prompts", "contrast_tables"],
                required_blocks=["concept_card", "misconception_box", "quiz_block", "source_appendix"],
                quiz_required=True,
            ),
            "exam": LearningPackSpec(
                pack_type="exam_review",
                persona="exam",
                tone="precise and exam-oriented",
                structure=[
                    "Learning Outcomes",
                    "Learning Map",
                    "High-Frequency Concepts",
                    "Definitions And Traps",
                    "Checkpoint Quiz",
                    "Answer Guide",
                    "Source Appendix",
                ],
                engagement_devices=["retrieval_practice", "trap_questions", "answer_templates"],
                required_blocks=["concept_card", "misconception_box", "quiz_block", "source_appendix"],
                quiz_required=True,
            ),
            "developer": LearningPackSpec(
                pack_type="developer_project",
                persona="developer",
                tone="practical and implementation-oriented",
                structure=[
                    "Learning Outcomes",
                    "Project Map",
                    "Concept Cards",
                    "Code And Evidence Path",
                    "Practice Task",
                    "Debug Checklist",
                    "Source Appendix",
                ],
                engagement_devices=["minimal_demo", "debug_prompts", "implementation_checkpoints"],
                required_blocks=["learning_map", "concept_card", "practice_task", "source_appendix"],
                quiz_required=False,
                practice_required=True,
            ),
            "creator": LearningPackSpec(
                pack_type="creator_script",
                persona="creator",
                tone="engaging and audience-aware",
                structure=[
                    "Learning Outcomes",
                    "Opening Hook",
                    "Learning Map",
                    "Concept Cards",
                    "Storyline And Examples",
                    "Audience Questions",
                    "Source Appendix",
                ],
                engagement_devices=["opening_hook", "storyline", "audience_questions"],
                required_blocks=["learning_map", "concept_card", "evidence_card", "source_appendix"],
                quiz_required=False,
            ),
            "teacher": LearningPackSpec(
                pack_type="teacher_notes",
                persona="teacher",
                tone="instructional and classroom-ready",
                structure=[
                    "Learning Outcomes",
                    "Lesson Map",
                    "Prerequisite Patch",
                    "Concept Cards",
                    "In-Class Questions",
                    "Homework",
                    "Source Appendix",
                ],
                engagement_devices=["classroom_questions", "homework", "board_plan"],
                required_blocks=["learning_map", "prerequisite_patch", "concept_card", "quiz_block", "source_appendix"],
                quiz_required=True,
                practice_required=True,
            ),
            "research": LearningPackSpec(
                pack_type="research_brief",
                persona="research",
                tone="careful and comparative",
                structure=[
                    "Learning Outcomes",
                    "Concept Map",
                    "Source Comparison",
                    "Definitions And Caveats",
                    "Open Questions",
                    "Source Appendix",
                ],
                engagement_devices=["source_comparison", "caveat_prompts", "open_questions"],
                required_blocks=["concept_card", "evidence_card", "source_appendix"],
                quiz_required=False,
            ),
        }
        return specs[persona]

    def _persona(self, profile: LearnerProfile, mode: StudyMode) -> str:
        use_case = profile.use_case.lower().replace("-", "_")
        level = profile.current_level.lower()
        if use_case in {"exam", "interview", "exam_review"}:
            return "exam"
        if use_case in {"developer", "project", "coding"}:
            return "developer"
        if use_case in {"creator", "blogger", "script"}:
            return "creator"
        if use_case in {"teacher", "training", "lecture"}:
            return "teacher"
        if use_case in {"research", "paper", "deep_research"}:
            return "research"
        mode_map = {
            StudyMode.BEGINNER_FULL: "beginner",
            StudyMode.QUICK_FRAMEWORK: "review",
            StudyMode.DEEP_ANALYSIS: "research",
            StudyMode.EXAM_REVIEW: "exam",
            StudyMode.PROJECT_PRACTICE: "developer",
            StudyMode.TEACHER_NOTES: "teacher",
            StudyMode.REVIEW: "review",
            StudyMode.DEVELOPER: "developer",
            StudyMode.CREATOR: "creator",
            StudyMode.RESEARCH: "research",
        }
        if level in {"zero", "beginner", "new"}:
            return mode_map.get(mode, "beginner")
        return mode_map.get(mode, "review")
