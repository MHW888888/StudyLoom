from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseDocsTests(unittest.TestCase):
    def test_release_files_exist(self):
        required = [
            "README.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "docs/release-checklist.md",
            "docs/fresh-clone-validation.md",
            "docs/real-world-fixture-checklist.md",
            "docs/alpha-risk-report.md",
            "docs/github-release-steps.md",
            "docs/release-notes/v1.5.1-alpha.md",
            ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/adapter_request.md",
            ".github/ISSUE_TEMPLATE/template_request.md",
            ".github/ISSUE_TEMPLATE/compliance_concern.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
        ]
        for item in required:
            self.assertTrue((ROOT / item).exists(), item)

    def test_readme_has_release_homepage_sections(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in [
            "source-grounded personalized learning pack generator",
            "Source Fidelity",
            "3 Minute Quickstart",
            "Low-Risk Import Demo",
            "Personalized Learning Pack Demo",
            "MCP / Agent Tools",
            "Known Limitations",
            "License",
        ]:
            self.assertIn(phrase, text)
        self.assertIn("source2study 的第一步不是总结", text)
        self.assertNotIn("\u9428", text)

    def test_hardening_docs_name_real_world_alpha_risks(self):
        checklist = (ROOT / "docs" / "real-world-fixture-checklist.md").read_text(encoding="utf-8")
        for phrase in ["Word / DOCX", "PowerPoint / PPTX", "WeChat Public Article", "Xiaohongshu", "Zhihu"]:
            self.assertIn(phrase, checklist)
        risk_report = (ROOT / "docs" / "alpha-risk-report.md").read_text(encoding="utf-8")
        for phrase in ["DOCX / PPTX Complex Structure", "OCR / ASR Tool Availability", "Eval Metrics Are Rule-Based"]:
            self.assertIn(phrase, risk_report)
        release_steps = (ROOT / "docs" / "github-release-steps.md").read_text(encoding="utf-8")
        self.assertIn("v1.0.0-alpha.0", release_steps)
        self.assertIn("v1.5.0-alpha.0", release_steps)

    def test_adapter_request_rejects_high_risk_methods(self):
        text = (ROOT / ".github" / "ISSUE_TEMPLATE" / "adapter_request.md").read_text(encoding="utf-8").lower()
        for phrase in ["cookies", "login bypass", "paywall bypass", "drm bypass", "anti-bot", "signature"]:
            self.assertIn(phrase, text)

    def test_sample_outputs_exist_and_show_source_fidelity(self):
        output_dir = ROOT / "examples" / "outputs"
        for name in [
            "beginner.md",
            "exam.md",
            "developer.md",
            "creator.md",
            "degraded-warning.md",
            "citation_report_sample.json",
            "learning_quality_report_sample.json",
            "eval_report_sample.json",
            "intake_report_sample.json",
        ]:
            self.assertTrue((output_dir / name).exists(), name)
        degraded = (output_dir / "degraded-warning.md").read_text(encoding="utf-8").lower()
        self.assertIn("source intake summary", degraded)
        self.assertIn("low confidence evidence", degraded)


if __name__ == "__main__":
    unittest.main()
