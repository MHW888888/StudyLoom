import tempfile
import unittest
import zipfile
from pathlib import Path

from source2study.exporters.docx import write_docx
from source2study.exporters.pdf import write_pdf
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import SourceRecord
from source2study.models.study_pack import StudyMode, StudyPack, StudySection


def sample_pack_and_index():
    index = EvidenceIndex()
    source = SourceRecord("src_1", "document", "notes.md", "Notes", "local", "2026-07-04T00:00:00Z")
    record = EvidenceRecord("ev_1", "src_1", "document", "Optimization evidence", EvidenceLocation(page=1))
    index.add_records(source, [record])
    pack = StudyPack("Test Pack", StudyMode.QUICK_FRAMEWORK, "en", [StudySection("Intro", "Body", ["ev_1"])])
    return pack, index


class ExportFormatTests(unittest.TestCase):
    def test_docx_is_zip_with_document_xml(self):
        pack, index = sample_pack_and_index()
        with tempfile.TemporaryDirectory() as tmp:
            out = write_docx(pack, index, Path(tmp) / "pack.docx")
            with zipfile.ZipFile(out) as archive:
                self.assertIn("word/document.xml", archive.namelist())
                self.assertIn("word/styles.xml", archive.namelist())
                document = archive.read("word/document.xml").decode("utf-8")
        self.assertIn('w:pStyle w:val="Heading1"', document)
        self.assertIn("Table Of Contents", document)
        self.assertIn("Citation Card", document)

    def test_pdf_has_pdf_header(self):
        pack, index = sample_pack_and_index()
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = Path(tmp) / "pack.pdf"
            out = write_pdf(pack, index, pdf_path)
            self.assertTrue(out.read_bytes().startswith(b"%PDF-1.4"))
            markdown_sidecar = pdf_path.with_suffix(".md")
            self.assertTrue(markdown_sidecar.exists())
            self.assertIn("Source Appendix", markdown_sidecar.read_text(encoding="utf-8"))

    def test_exporter_templates_are_present(self):
        root = Path(__file__).parents[1]
        for name in ["markdown.yaml", "docx.yaml", "pdf.yaml"]:
            with self.subTest(name=name):
                self.assertTrue((root / "templates" / "exporters" / name).exists())


if __name__ == "__main__":
    unittest.main()
