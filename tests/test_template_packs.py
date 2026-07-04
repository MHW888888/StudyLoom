import tempfile
import unittest
from pathlib import Path

from source2study.cli import main
from source2study.templates import copy_template_pack, list_template_packs, load_template_pack


class TemplatePackTests(unittest.TestCase):
    def test_template_packs_cover_core_personas(self):
        packs = {pack["id"]: pack for pack in list_template_packs()}
        for template_id in ["exam-review", "teacher-lecture", "developer-project", "creator-script", "enterprise-training"]:
            self.assertIn(template_id, packs)
            self.assertGreaterEqual(len(packs[template_id]["required_blocks"]), 3)
            self.assertGreaterEqual(len(packs[template_id]["safety_notes"]), 1)

    def test_load_and_copy_template_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            target = copy_template_pack("developer-project", workspace)
            pack = load_template_pack("developer-project")
            self.assertEqual(pack["mode"], "developer")
            readme_path = target / "README.md"
            self.assertTrue((target / "pack.json").exists())
            self.assertTrue(readme_path.exists())
            readme = readme_path.read_text(encoding="utf-8")
            self.assertIn("Source Intake Summary", readme)
            self.assertIn("Source Appendix", readme)

    def test_cli_templates_list_show_and_copy_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["templates", "list"]), 0)
            self.assertEqual(main(["templates", "show", "exam-review"]), 0)
            self.assertEqual(main(["templates", "copy", "all", "--workspace", str(workspace)]), 0)
            self.assertTrue((workspace / "templates" / "exam-review" / "pack.json").exists())
            self.assertTrue((workspace / "templates" / "enterprise-training" / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
