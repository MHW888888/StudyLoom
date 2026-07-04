import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from source2study.adapters.base import SourceRequest
from source2study.adapters.docx_adapter import DocxAdapter
from source2study.adapters.pptx_adapter import PptxAdapter
from source2study.cli import main
from source2study.intake import intake_summary_path


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


class OfficeAdapterTests(unittest.TestCase):
    def test_docx_adapter_extracts_headings_tables_comments_and_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lesson.docx"
            _write_minimal_docx(path)
            result = DocxAdapter().ingest(SourceRequest(str(path), Path(tmp) / "workspace"))

        self.assertEqual(result.source.source_type, "docx")
        self.assertTrue(any(record.kind == "heading" for record in result.evidence))
        self.assertTrue(any(record.kind == "table" for record in result.evidence))
        self.assertEqual(result.source.available_metadata["tables_count"], 1)
        self.assertEqual(result.source.available_metadata["images_count"], 1)
        self.assertGreaterEqual(len(result.warnings), 1)

    def test_pptx_adapter_extracts_slide_text_and_speaker_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "deck.pptx"
            _write_minimal_pptx(path)
            result = PptxAdapter().ingest(SourceRequest(str(path), Path(tmp) / "workspace"))

        self.assertEqual(result.source.source_type, "pptx")
        self.assertEqual(result.source.available_metadata["slides_count"], 2)
        self.assertEqual(result.source.available_metadata["speaker_notes_count"], 1)
        self.assertTrue(any(record.kind == "slide_text" for record in result.evidence))
        self.assertTrue(any(record.kind == "speaker_note" for record in result.evidence))

    def test_cli_intake_summary_records_office_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "deck.pptx"
            workspace = Path(tmp) / "workspace"
            _write_minimal_pptx(path)
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(path)]), 0)
            summary = json.loads(intake_summary_path(workspace).read_text(encoding="utf-8"))

        source = summary["sources"][0]
        self.assertEqual(source["source_type"], "pptx")
        self.assertEqual(source["detected_assets"]["slides"], 2)
        self.assertEqual(source["detected_assets"]["speaker_notes"], 1)
        self.assertGreaterEqual(len(source["warnings"]), 1)


def _write_minimal_docx(path: Path) -> None:
    document = f"""<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Gradient Descent Lesson</w:t></w:r></w:p>
    <w:p><w:r><w:t>EvidenceIndex keeps source-backed learning claims traceable.</w:t></w:r></w:p>
    <w:tbl>
      <w:tr><w:tc><w:p><w:r><w:t>Concept</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Purpose</w:t></w:r></w:p></w:tc></w:tr>
      <w:tr><w:tc><w:p><w:r><w:t>Citation verifier</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Checks evidence ids</w:t></w:r></w:p></w:tc></w:tr>
    </w:tbl>
  </w:body>
</w:document>
"""
    comments = f"""<?xml version="1.0" encoding="UTF-8"?>
<w:comments xmlns:w="{W_NS}"><w:comment><w:p><w:r><w:t>Teacher note for review.</w:t></w:r></w:p></w:comment></w:comments>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)
        archive.writestr("word/comments.xml", comments)
        archive.writestr("word/media/image1.png", b"fake image bytes")


def _write_minimal_pptx(path: Path) -> None:
    slide1 = f"""<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="{A_NS}">
  <p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>Source Fidelity First</a:t></a:r></a:p><a:p><a:r><a:t>Inspect before generating.</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>
</p:sld>
"""
    slide2 = f"""<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="{A_NS}">
  <p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>EvidenceIndex</a:t></a:r></a:p><a:p><a:r><a:t>Citations point back to source records.</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>
</p:sld>
"""
    notes1 = f"""<?xml version="1.0" encoding="UTF-8"?>
<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="{A_NS}">
  <p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>Speaker note: pause for a source audit checkpoint.</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>
</p:notes>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("ppt/slides/slide1.xml", slide1)
        archive.writestr("ppt/slides/slide2.xml", slide2)
        archive.writestr("ppt/notesSlides/notesSlide1.xml", notes1)
        archive.writestr("ppt/media/image1.png", b"fake image bytes")
        archive.writestr("ppt/charts/chart1.xml", "<chart/>")


if __name__ == "__main__":
    unittest.main()
