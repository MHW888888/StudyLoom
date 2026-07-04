import tempfile
import unittest
from pathlib import Path

from source2study.adapters.base import AdapterError, SourceRequest
from source2study.adapters.bilibili_adapter import BilibiliAdapter


class BlockedSourceTests(unittest.TestCase):
    def test_bilibili_direct_extraction_is_blocked_in_mvp(self):
        with tempfile.TemporaryDirectory() as tmp:
            request = SourceRequest("https://www.bilibili.com/video/BV123", Path(tmp))
            with self.assertRaises(AdapterError) as ctx:
                BilibiliAdapter().ingest(request)
        self.assertIn("Provide subtitles", ctx.exception.fallback)


if __name__ == "__main__":
    unittest.main()
