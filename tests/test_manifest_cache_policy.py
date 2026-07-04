import json
import tempfile
import unittest
from pathlib import Path

from source2study.cli import main
from source2study.manifest import manifest_path


class ManifestCachePolicyTests(unittest.TestCase):
    def test_ingest_records_manifest_and_cache_hit(self):
        fixture = Path(__file__).parent / "fixtures" / "sample_notes.md"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(fixture)]), 0)
            self.assertEqual(main(["ingest", "--workspace", str(workspace), "--source", str(fixture)]), 0)
            manifest = json.loads(manifest_path(workspace).read_text(encoding="utf-8"))
        self.assertGreaterEqual(manifest["cache"]["misses"], 1)
        self.assertGreaterEqual(manifest["cache"]["hits"], 1)
        self.assertTrue(any(source["status"] == "indexed" for source in manifest["sources"]))

    def test_policy_blocks_bilibili_direct_extraction(self):
        result = main(["policy", "check", "https://www.bilibili.com/video/BV123"])
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
