import tempfile
import unittest
from pathlib import Path

from source2study.adapters.base import SourceRequest
from source2study.adapters.pdf_adapter import PdfAdapter


class PdfAdapterTests(unittest.TestCase):
    def test_text_file_ingest_builds_evidence(self):
        fixture = Path(__file__).parent / "fixtures" / "sample_notes.md"
        with tempfile.TemporaryDirectory() as tmp:
            result = PdfAdapter().ingest(SourceRequest(str(fixture), Path(tmp)))
        self.assertEqual(result.source.source_type, "document")
        self.assertGreaterEqual(len(result.evidence), 1)
        self.assertIn("gradient descent", result.evidence[0].text.lower())


if __name__ == "__main__":
    unittest.main()
