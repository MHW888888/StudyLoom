import tempfile
import unittest
from pathlib import Path

from source2study.exporters.markdown import write_markdown
from source2study.generation.modes import StudyMode
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import SourceRecord
from source2study.models.study_pack import StudyPack, StudySection


class MarkdownExporterTests(unittest.TestCase):
    def test_markdown_preserves_evidence_ids(self):
        index = EvidenceIndex()
        source = SourceRecord("src_1", "document", "notes.md", "Notes", "local", "2026-07-04T00:00:00Z")
        record = EvidenceRecord("ev_1", "src_1", "document", "Optimization evidence", EvidenceLocation(page=1))
        index.add_records(source, [record])
        pack = StudyPack("Test Pack", StudyMode.BEGINNER_FULL, "en", [StudySection("Intro", "Body", ["ev_1"])])
        with tempfile.TemporaryDirectory() as tmp:
            out = write_markdown(pack, index, Path(tmp) / "pack.md")
            text = out.read_text(encoding="utf-8")
        self.assertIn("`ev_1`", text)
        self.assertIn("## Cover", text)
        self.assertIn("## Table Of Contents", text)
        self.assertIn("## Learning Goals", text)
        self.assertIn("Chapter objective:", text)
        self.assertIn("#### Citation Card", text)
        self.assertIn("## One-Page Review", text)
        self.assertIn("## Source Appendix", text)
        self.assertIn("Source Ledger", text)


if __name__ == "__main__":
    unittest.main()
