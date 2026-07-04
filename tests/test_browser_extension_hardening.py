import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class BrowserExtensionHardeningTests(unittest.TestCase):
    def test_manifest_keeps_current_page_export_minimal(self):
        manifest = json.loads((ROOT / "browser-extension" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "1.3.0")
        self.assertIn("activeTab", manifest["permissions"])
        self.assertIn("downloads", manifest["permissions"])
        self.assertNotIn("cookies", manifest["permissions"])
        self.assertNotIn("history", manifest["permissions"])

    def test_content_script_sanitizes_and_redacts(self):
        text = (ROOT / "browser-extension" / "content-script.js").read_text(encoding="utf-8")
        self.assertIn("redactSensitive", text)
        self.assertIn("sanitizeHtml", text)
        self.assertIn("schema_version: \"1.3.0\"", text)
        self.assertIn("risk_warnings", text)
        self.assertIn("form, input, textarea, select, button", text)
        self.assertNotIn("document.cookie", text)
        self.assertNotIn("localStorage", text)
        self.assertNotIn("sessionStorage", text)

    def test_export_filename_uses_studyloom_prefix(self):
        text = (ROOT / "browser-extension" / "export-current-page.js").read_text(encoding="utf-8")
        self.assertIn("studyloom-", text)
        self.assertIn(".browser_capture.json", text)


if __name__ == "__main__":
    unittest.main()
