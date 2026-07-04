import json
import tempfile
import unittest
from pathlib import Path

from source2study.adapters.utils import utc_now
from source2study.cli import main
from source2study.exporters.mindmap import export_mindmap, validate_mindmap_text
from source2study.exporters.wiki import validate_wiki, write_wiki
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import SourceRecord
from source2study.workspace import write_ledgers


class WikiMindmapTests(unittest.TestCase):
    def test_wiki_exporter_writes_evidence_backed_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = _sample_index()
            output = write_wiki(index, Path(tmp) / "wiki")
            validation = validate_wiki(output, index)
            page_text = (output / "concepts" / "evidence-index.md").read_text(encoding="utf-8")

        self.assertEqual(validation["status"], "pass")
        self.assertIn("ev_sample_1", page_text)
        self.assertIn("Source Evidence", page_text)

    def test_mindmap_exports_markmap_mermaid_and_json_with_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = _sample_index()
            for export_format, suffix in [("markmap", "md"), ("mermaid", "mmd"), ("json", "json")]:
                path = export_mindmap(index, Path(tmp) / f"concept.{suffix}", export_format)
                text = path.read_text(encoding="utf-8")
                self.assertEqual(validate_mindmap_text(text)["status"], "pass")
                self.assertIn("ev_sample_1", text)
            data = json.loads((Path(tmp) / "concept.json").read_text(encoding="utf-8"))
        self.assertTrue(any(edge["relation"] == "supported_by" for edge in data["edges"]))

    def test_cli_wiki_and_graph_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            write_ledgers(workspace, _sample_index())
            self.assertEqual(main(["wiki", "build", str(workspace)]), 0)
            self.assertEqual(main(["graph", "export", str(workspace), "--format", "mermaid"]), 0)
            self.assertTrue((workspace / "wiki" / "index.md").exists())
            self.assertTrue((workspace / "visuals" / "concept_graph.mmd").exists())


def _sample_index() -> EvidenceIndex:
    index = EvidenceIndex()
    source = SourceRecord(
        source_id="src_sample",
        source_type="document",
        source_url_or_path="sample.md",
        title="Sample",
        platform="fixture",
        capture_time=utc_now(),
    )
    index.add_source(source)
    for idx, text in enumerate(
        [
            "Evidence Index keeps claims traceable to source records.",
            "Citation verifier checks generated sections against evidence ids.",
        ],
        start=1,
    ):
        index.add_evidence(
            EvidenceRecord(
                evidence_id=f"ev_sample_{idx}",
                source_id="src_sample",
                source_type="document",
                text=text,
                location=EvidenceLocation(section=f"fixture {idx}", path="sample.md"),
                confidence=0.95,
            )
        )
    return index


if __name__ == "__main__":
    unittest.main()
