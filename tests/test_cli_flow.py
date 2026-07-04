import tempfile
import unittest
from pathlib import Path

from source2study.cli import main


class CliFlowTests(unittest.TestCase):
    def test_ingest_generate_validate_markdown(self):
        fixture = Path(__file__).parent / "fixtures" / "sample_notes.md"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(fixture)]), 0)
            self.assertEqual(main(["validate", str(workspace)]), 0)
            output = workspace / "outputs" / "guide.md"
            self.assertEqual(main(["generate", str(workspace), "--mode", "beginner", "--output", str(output)]), 0)
            self.assertTrue(output.exists())
            self.assertIn("Evidence", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
