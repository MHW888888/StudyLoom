import tempfile
import unittest
from pathlib import Path

from source2study.cli import main


class DemoWorkflowTests(unittest.TestCase):
    def test_demo_sources_generate_pack_and_report(self):
        root = Path(__file__).parents[1]
        sources = [
            root / "examples" / "demo_sources" / "notes.md",
            root / "examples" / "demo_sources" / "mini_repo",
            root / "examples" / "demo_sources" / "lecture.vtt",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "demo"
            args = ["ingest", "--workspace", str(workspace)]
            for source in sources:
                args.extend(["--source", str(source)])
            self.assertEqual(main(args), 0)
            output = workspace / "outputs" / "beginner.md"
            self.assertEqual(main(["generate", str(workspace), "--mode", "beginner", "--output", str(output)]), 0)
            pack = workspace / "outputs" / "study_pack_beginner_full.json"
            self.assertEqual(main(["validate", str(workspace), "--pack", str(pack)]), 0)
            self.assertTrue((workspace / "manifest.json").exists())
            self.assertTrue((workspace / "outputs" / "citation_report_beginner_full.json").exists())


if __name__ == "__main__":
    unittest.main()
