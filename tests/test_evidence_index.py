import unittest

from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import SourceRecord


class EvidenceIndexTests(unittest.TestCase):
    def test_add_and_validate_references(self):
        index = EvidenceIndex()
        source = SourceRecord(
            source_id="src_1",
            source_type="document",
            source_url_or_path="notes.md",
            title="Notes",
            platform="local",
            capture_time="2026-07-04T00:00:00Z",
        )
        record = EvidenceRecord(
            evidence_id="ev_1",
            source_id="src_1",
            source_type="document",
            text="Gradient descent updates parameters.",
            location=EvidenceLocation(page=1),
        )
        index.add_records(source, [record])
        self.assertEqual(index.validate_references({"ev_1"}), [])
        self.assertEqual(index.validate_references({"missing"}), ["missing"])
        self.assertEqual(index.search("gradient")[0].evidence_id, "ev_1")


if __name__ == "__main__":
    unittest.main()
