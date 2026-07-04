import tempfile
import unittest
from pathlib import Path

from source2study.cli import main
from source2study.workspace import citation_report_path, learning_quality_report_path, pack_json_path


class PersonalizedDemoTests(unittest.TestCase):
    def test_same_sources_generate_multiple_personas(self):
        root = Path(__file__).parents[1]
        source_dir = root / "examples" / "personalized" / "sources"
        profiles = {
            "beginner": root / "examples" / "personalized" / "profiles" / "beginner.json",
            "exam": root / "examples" / "personalized" / "profiles" / "exam.json",
            "developer": root / "examples" / "personalized" / "profiles" / "developer.json",
            "creator": root / "examples" / "personalized" / "profiles" / "creator.json",
        }
        expected_modes = {
            "beginner": "beginner_full",
            "exam": "exam_review",
            "developer": "developer",
            "creator": "creator",
        }
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(source_dir)]), 0)
            for mode, profile in profiles.items():
                output = workspace / "outputs" / f"{mode}.md"
                self.assertEqual(main(["generate", str(workspace), "--mode", mode, "--profile", str(profile), "--output", str(output)]), 0)
                resolved_mode = expected_modes[mode]
                self.assertTrue(output.exists())
                self.assertTrue(pack_json_path(workspace, resolved_mode).exists())
                self.assertTrue(citation_report_path(workspace, resolved_mode).exists())
                self.assertTrue(learning_quality_report_path(workspace, resolved_mode).exists())
                self.assertEqual(main(["validate", str(workspace), "--pack", str(pack_json_path(workspace, resolved_mode))]), 0)


if __name__ == "__main__":
    unittest.main()
