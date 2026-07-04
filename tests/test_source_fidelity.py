import json
import tempfile
import unittest
from pathlib import Path

from source2study.cli import main
from source2study.intake import intake_summary_path


FIXTURES = Path(__file__).parent / "fixtures"


class SourceFidelityTests(unittest.TestCase):
    def test_inspect_writes_intake_report_without_index(self):
        fixture = FIXTURES / "sample_notes.md"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["inspect", str(fixture), "--workspace", str(workspace)]), 0)
            summary = json.loads(intake_summary_path(workspace).read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "pass")
            self.assertGreater(summary["sources"][0]["detected_assets"]["text_blocks"], 0)
            self.assertFalse((workspace / "evidence_index.json").exists())

    def test_degraded_screenshot_ocr_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "no_sidecar.png"
            image.write_bytes(b"not a real image, but enough for local intake smoke")
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(image)]), 0)
            summary = json.loads(intake_summary_path(workspace).read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "degraded")
        self.assertEqual(summary["sources"][0]["extraction_quality"]["ocr"], "low")
        self.assertIn("Low-confidence evidence", " ".join(summary["warnings"]))

    def test_blocked_source_blocks_build_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["inspect", "https://www.bilibili.com/video/BV123", "--workspace", str(workspace)]), 1)
            self.assertEqual(main(["build-index", str(workspace)]), 2)
            summary = json.loads(intake_summary_path(workspace).read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "blocked")

    def test_transcript_intake_records_timestamp_segments(self):
        fixture = FIXTURES / "transcripts" / "lecture.vtt"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(fixture)]), 0)
            summary = json.loads(intake_summary_path(workspace).read_text(encoding="utf-8"))
        source = summary["sources"][0]
        self.assertEqual(source["source_type"], "transcript")
        self.assertGreater(source["detected_assets"]["transcript_segments"], 0)
        self.assertEqual(summary["status"], "degraded")

    def test_browser_capture_without_body_is_degraded_on_inspect(self):
        with tempfile.TemporaryDirectory() as tmp:
            capture = Path(tmp) / "empty.browser_capture.json"
            capture.write_text(
                json.dumps(
                    {
                        "source_type": "browser_capture",
                        "capture_method": "current_page_dom",
                        "user_initiated_capture": True,
                        "platform": "wechat",
                        "title": "Empty page",
                        "url": "https://example.test/empty",
                        "text": "",
                        "content_html": "",
                        "images": [],
                    }
                ),
                encoding="utf-8",
            )
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["inspect", str(capture), "--workspace", str(workspace)]), 0)
            summary = json.loads(intake_summary_path(workspace).read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "degraded")
        self.assertIn("no readable text", " ".join(summary["warnings"]).lower())

    def test_generate_output_contains_intake_summary(self):
        fixture = FIXTURES / "sample_notes.md"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            output = workspace / "outputs" / "guide.md"
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(fixture)]), 0)
            self.assertEqual(main(["generate", str(workspace), "--mode", "beginner", "--output", str(output)]), 0)
            text = output.read_text(encoding="utf-8")
        self.assertIn("## Source Intake Summary", text)
        self.assertIn("Intake status: `pass`", text)

    def test_docx_pptx_planned_contracts_are_documented(self):
        root = Path(__file__).parents[1]
        docs = (root / "docs" / "source-fidelity.md").read_text(encoding="utf-8")
        adapters = (root / "docs" / "source-adapters.md").read_text(encoding="utf-8")
        self.assertIn("DOCX", docs)
        self.assertIn("PPTX", docs)
        self.assertIn("DocxAdapter", adapters)
        self.assertIn("PptxAdapter", adapters)


if __name__ == "__main__":
    unittest.main()
