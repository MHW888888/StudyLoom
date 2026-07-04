import tempfile
import unittest
from pathlib import Path

from source2study.adapters.base import SourceRequest
from source2study.adapters.wechat_public_article_adapter import WeChatPublicArticleAdapter
from source2study.adapters.xhs_export_adapter import XhsExportAdapter
from source2study.adapters.zhihu_public_page_adapter import ZhihuPublicPageAdapter
from source2study.indexing.evidence_index import EvidenceIndex


FIXTURES = Path(__file__).parent / "fixtures"


class PlannedAdapterTests(unittest.TestCase):
    def test_wechat_user_export_fixture_builds_evidence_index(self):
        result = self._ingest(WeChatPublicArticleAdapter(), FIXTURES / "wechat" / "article.wechat.html")
        index = EvidenceIndex()
        index.add_records(result.source, result.evidence)
        self.assertEqual(result.source.source_type, "wechat_public_article")
        self.assertGreaterEqual(len(index.evidence), 1)
        self.assertEqual(result.source.available_metadata["extraction_method"], "user_uploaded_html")
        self.assertIn("cookie_replay", result.source.capability.blocked_methods)

    def test_xhs_markdown_export_fixture_builds_evidence_index(self):
        result = self._ingest(XhsExportAdapter(), FIXTURES / "xhs" / "note.xhs.md")
        index = EvidenceIndex()
        index.add_records(result.source, result.evidence)
        self.assertEqual(result.source.source_type, "xiaohongshu_export")
        self.assertGreaterEqual(len(index.evidence), 1)
        self.assertIn("user_uploaded_markdown", result.source.capability.allowed_methods)

    def test_xhs_json_export_can_emit_ocr_placeholder_evidence(self):
        result = self._ingest(XhsExportAdapter(), FIXTURES / "xhs" / "note.xhs.json")
        index = EvidenceIndex()
        index.add_records(result.source, result.evidence)
        kinds = {record.kind for record in index.evidence.values()}
        self.assertIn("ocr_placeholder", kinds)

    def test_zhihu_public_page_fixture_builds_evidence_index(self):
        result = self._ingest(ZhihuPublicPageAdapter(), FIXTURES / "zhihu" / "question.zhihu.html")
        index = EvidenceIndex()
        index.add_records(result.source, result.evidence)
        self.assertEqual(result.source.source_type, "zhihu_public_page")
        self.assertGreaterEqual(len(index.evidence), 1)
        self.assertIn("signature_bypass", result.source.capability.blocked_methods)

    def _ingest(self, adapter, fixture: Path):
        with tempfile.TemporaryDirectory() as tmp:
            request = SourceRequest(str(fixture), Path(tmp))
            self.assertTrue(adapter.can_handle(request))
            return adapter.ingest(request)


if __name__ == "__main__":
    unittest.main()
