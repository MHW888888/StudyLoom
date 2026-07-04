import tempfile
import unittest
from pathlib import Path

from source2study.generation.citation_verifier import CitationVerifier
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import SourceRecord
from source2study.models.study_pack import StudyMode, StudyPack, StudySection


class CitationVerifierTests(unittest.TestCase):
    def test_missing_evidence_fails(self):
        index = EvidenceIndex()
        source = SourceRecord("src_1", "document", "notes.md", "Notes", "local", "2026-07-04T00:00:00Z")
        record = EvidenceRecord("ev_1", "src_1", "document", "Grounded text", EvidenceLocation(page=1))
        index.add_records(source, [record])
        pack = StudyPack("Pack", StudyMode.BEGINNER_FULL, "en", [StudySection("Intro", "Body", ["ev_missing"])])

        report = CitationVerifier().verify(index, pack=pack)

        self.assertEqual(report.status, "fail")
        self.assertEqual(report.summary["missing_citations"], 1)

    def test_report_write_is_machine_readable(self):
        report = CitationVerifier().verify(EvidenceIndex())
        with tempfile.TemporaryDirectory() as tmp:
            path = report.write(Path(tmp) / "report.json")
            text = path.read_text(encoding="utf-8")
        self.assertIn('"status"', text)
        self.assertIn('"issues"', text)


if __name__ == "__main__":
    unittest.main()
