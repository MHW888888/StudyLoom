import tempfile
import unittest
from pathlib import Path

from source2study.adapters.base import AdapterError, SourceRequest
from source2study.adapters.browser_capture_adapter import BrowserCaptureAdapter
from source2study.adapters.screenshot_ocr_adapter import ScreenshotOcrAdapter
from source2study.adapters.transcript_adapter import TranscriptAdapter
from source2study.cli import main
from source2study.workspace import load_index


FIXTURES = Path(__file__).parent / "fixtures"


class LowRiskIngestionTests(unittest.TestCase):
    def test_browser_capture_current_page_json_builds_evidence(self):
        fixture = FIXTURES / "browser_capture" / "article.browser_capture.json"
        with tempfile.TemporaryDirectory() as tmp:
            result = BrowserCaptureAdapter().ingest(SourceRequest(str(fixture), Path(tmp)))
        self.assertEqual(result.source.source_type, "browser_capture")
        self.assertTrue(result.source.available_metadata["user_initiated_capture"])
        self.assertEqual(result.source.available_metadata["capture_method"], "current_page_dom")
        self.assertGreaterEqual(len(result.evidence), 1)
        self.assertTrue(result.evidence[0].metadata["user_initiated_capture"])

    def test_browser_capture_rejects_cookies_and_bulk_history(self):
        adapter = BrowserCaptureAdapter()
        for fixture in [
            FIXTURES / "browser_capture" / "bad_cookies.browser_capture.json",
            FIXTURES / "browser_capture" / "bad_bulk.browser_capture.json",
        ]:
            with self.subTest(fixture=fixture.name), tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(AdapterError):
                    adapter.ingest(SourceRequest(str(fixture), Path(tmp)))

    def test_screenshot_ocr_sidecar_builds_low_risk_evidence(self):
        fixture = FIXTURES / "screenshots" / "slide.png"
        with tempfile.TemporaryDirectory() as tmp:
            result = ScreenshotOcrAdapter().ingest(SourceRequest(str(fixture), Path(tmp)))
        self.assertEqual(result.source.source_type, "screenshot_ocr")
        self.assertEqual(result.source.available_metadata["capture_method"], "screenshot_ocr")
        self.assertGreater(result.evidence[0].metadata["ocr_confidence"], 0.5)
        self.assertTrue(result.evidence[0].media.screenshot_path.endswith("slide.png"))

    def test_transcript_import_builds_timestamped_evidence(self):
        fixture = FIXTURES / "transcripts" / "bilibili.srt"
        with tempfile.TemporaryDirectory() as tmp:
            result = TranscriptAdapter().ingest(SourceRequest(str(fixture), Path(tmp)))
        self.assertEqual(result.source.source_type, "transcript")
        self.assertEqual(result.source.available_metadata["capture_method"], "user_uploaded_transcript")
        self.assertTrue(any(record.location.timestamp_start for record in result.evidence))

    def test_cli_source_type_routes_generic_saved_html(self):
        fixture = Path(__file__).parents[1] / "examples" / "low_risk_sources" / "wechat_article.html"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["ingest", str(fixture), "--source-type", "wechat_html", "--workspace", str(workspace)]), 0)
            index = load_index(workspace)
        self.assertEqual(len(index.sources), 1)
        self.assertEqual(next(iter(index.sources.values())).source_type, "wechat_public_article")


if __name__ == "__main__":
    unittest.main()
