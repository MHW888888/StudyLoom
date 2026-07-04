import json
import tempfile
import unittest
from pathlib import Path

from source2study.cli import main
from source2study.generation.learning_quality_verifier import LearningQualityVerifier
from source2study.generation.modes import resolve_mode
from source2study.generation.writer import StudyPackWriter
from source2study.knowledge.concept_graph import ConceptGraphBuilder
from source2study.personalization.learner_profile import LearnerProfile
from source2study.personalization.pack_spec import LearningPackSpecBuilder
from source2study.workspace import learning_quality_report_path, load_index


class PersonalizationTests(unittest.TestCase):
    def test_learner_profile_json_and_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.json"
            path.write_text(
                json.dumps(
                    {
                        "goal": "learn gradient descent",
                        "current_level": "beginner",
                        "time_budget": "2 hours",
                        "use_case": "self_study",
                        "must_include": ["quiz"],
                    }
                ),
                encoding="utf-8",
            )
            profile = LearnerProfile.from_json_file(path).merge_overrides(level="intermediate", style="concise")
        self.assertEqual(profile.goal, "learn gradient descent")
        self.assertEqual(profile.current_level, "intermediate")
        self.assertEqual(profile.preferred_style, "concise")
        self.assertIn("quiz", profile.must_include)

    def test_pack_spec_supports_personas(self):
        builder = LearningPackSpecBuilder()
        for mode, persona in [("beginner", "beginner"), ("exam", "exam"), ("developer", "developer"), ("creator", "creator"), ("research", "research")]:
            with self.subTest(mode=mode):
                profile = LearnerProfile(use_case=persona)
                spec = builder.build(profile, resolve_mode(mode))
                self.assertEqual(spec.persona, persona)
                self.assertIn("Source Appendix", spec.structure)

    def test_concept_graph_and_personalized_pack_pass_quality(self):
        index = self._index_from_personalized_fixture()
        profile = LearnerProfile(goal="Build a tiny gradient descent project", use_case="developer", current_level="intermediate")
        mode = resolve_mode("developer")
        graph = ConceptGraphBuilder().build(index)
        pack = StudyPackWriter().build(index, mode=mode, language="zh", profile=profile)
        spec = LearningPackSpecBuilder().build(profile, mode)
        report = LearningQualityVerifier().verify(pack, profile=profile, spec=spec, graph=graph)
        titles = [section.title for section in pack.sections]
        self.assertTrue(graph.nodes)
        self.assertIn("Project Map", titles)
        self.assertIn("Practice Task", titles)
        self.assertEqual(report.status, "pass")
        self.assertTrue(pack.metadata["personalized"])

    def test_cli_generate_writes_learning_quality_report(self):
        source_dir = Path(__file__).parents[1] / "examples" / "personalized" / "sources"
        profile = Path(__file__).parents[1] / "examples" / "personalized" / "profiles" / "beginner.json"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(source_dir)]), 0)
            output = workspace / "outputs" / "beginner.md"
            self.assertEqual(main(["generate", str(workspace), "--mode", "beginner", "--profile", str(profile), "--output", str(output)]), 0)
            self.assertTrue(learning_quality_report_path(workspace, "beginner_full").exists())
            self.assertIn("Personalization", output.read_text(encoding="utf-8"))

    def _index_from_personalized_fixture(self):
        source_dir = Path(__file__).parents[1] / "examples" / "personalized" / "sources"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(source_dir)]), 0)
            return load_index(workspace)


if __name__ == "__main__":
    unittest.main()
