import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from source2study.asr.local import inspect_local_asr, run_local_asr
from source2study.cli import main
from source2study.ocr.simple_placeholder import read_sidecar_or_placeholder
from source2study.video.keyframes import extract_interval_keyframes, inspect_keyframe_engine


FIXTURES = Path(__file__).parent / "fixtures"


class LocalOcrAsrTests(unittest.TestCase):
    def test_ocr_prefers_user_sidecar_text(self):
        image = FIXTURES / "screenshots" / "slide.png"
        result = read_sidecar_or_placeholder(image)
        self.assertEqual(result.engine, "sidecar_text")
        self.assertIn("Evidence index pipeline", result.text)

    def test_ocr_cli_writes_output(self):
        image = FIXTURES / "screenshots" / "slide.png"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "slide.ocr.txt"
            self.assertEqual(main(["ocr", str(image), "--output", str(output)]), 0)
            self.assertIn("Evidence index pipeline", output.read_text(encoding="utf-8"))

    def test_asr_inspect_is_safe_without_network_or_media_download(self):
        status = inspect_local_asr()
        self.assertIn("available", status)
        self.assertIn("engine", status)
        self.assertIn("optional", status["note"].lower())

    def test_asr_unavailable_returns_structured_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "sample.wav"
            media.write_bytes(b"not real audio")
            with patch("source2study.asr.local.shutil.which", return_value=None):
                result = run_local_asr(media)
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.engine, "unavailable")
        self.assertGreaterEqual(len(result.warnings), 1)

    def test_ocr_missing_optional_engine_returns_low_confidence_placeholder(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "slide.png"
            image.write_bytes(b"not real image")
            with patch("source2study.ocr.simple_placeholder.run_tesseract_if_available", return_value=None):
                result = read_sidecar_or_placeholder(image)
        self.assertEqual(result.engine, "placeholder")
        self.assertLess(result.confidence, 0.5)

    def test_keyframe_inspect_is_local_optional(self):
        status = inspect_keyframe_engine()
        self.assertIn("available", status)
        self.assertIn("engine", status)
        self.assertIn("local-only", status["note"])

    def test_keyframe_missing_optional_engine_returns_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "sample.mp4"
            media.write_bytes(b"not real video")
            with patch("source2study.video.keyframes.shutil.which", return_value=None):
                result = extract_interval_keyframes(media, Path(tmp) / "frames")
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.engine, "unavailable")
        self.assertGreaterEqual(len(result.warnings), 1)


if __name__ == "__main__":
    unittest.main()
