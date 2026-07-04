from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AgentSkillStructureTests(unittest.TestCase):
    def test_codex_and_claude_skills_encode_safe_workflow(self):
        for path in [
            ROOT / "skills" / "codex" / "source2study" / "SKILL.md",
            ROOT / "skills" / "claude" / "source2study" / "SKILL.md",
        ]:
            text = path.read_text(encoding="utf-8")
            lower = text.lower()
            self.assertIn("description:", text)
            self.assertIn("source fidelity first", lower)
            self.assertIn("source2study_inspect_local", text)
            self.assertIn("source2study_validate_pack", text)
            self.assertIn("source2study_run_eval", text)
            self.assertIn("not a crawler", lower)
            self.assertIn("do not", lower)
            self.assertNotIn("provide cookies", lower)
            self.assertNotIn("bypass login", lower.replace("login bypass", "login_bypass"))

    def test_agent_metadata_exists(self):
        self.assertTrue((ROOT / "agents" / "openai.yaml").exists())
        self.assertTrue((ROOT / "agents" / "claude.yaml").exists())


if __name__ == "__main__":
    unittest.main()
