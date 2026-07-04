from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mcp.schemas import list_tools
from mcp.tools import (
    McpToolConfig,
    call_tool,
    source2study_build_index,
    source2study_generate_personalized_pack,
    source2study_ingest_local,
    source2study_inspect_local,
    source2study_policy_check,
    source2study_run_eval,
)
from source2study.safety.redaction import sanitize_for_response


class McpToolTests(unittest.TestCase):
    def test_tool_schema_exposes_only_restricted_tools(self):
        names = {tool["name"] for tool in list_tools()}
        self.assertEqual(
            names,
            {
                "source2study_policy_check",
                "source2study_inspect_local",
                "source2study_ingest_local",
                "source2study_build_index",
                "source2study_generate_pack",
                "source2study_generate_personalized_pack",
                "source2study_validate_pack",
                "source2study_run_eval",
            },
        )
        forbidden = {"shell_exec", "arbitrary_url_fetch", "cookie_import", "bulk_platform_crawl"}
        self.assertFalse(names & forbidden)

    def test_policy_check_returns_blocked_for_direct_platform_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = McpToolConfig(allowed_workspaces=(Path(tmp).resolve(),), root=Path(tmp).resolve())
            result = source2study_policy_check("https://www.bilibili.com/video/BV123", config=cfg)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("policy", result)

    def test_inspect_and_ingest_require_allowlisted_local_sources(self):
        with tempfile.TemporaryDirectory() as allowed, tempfile.TemporaryDirectory() as outside:
            allowed_root = Path(allowed).resolve()
            outside_root = Path(outside).resolve()
            source = allowed_root / "notes.md"
            source.write_text("# EvidenceIndex\n\nA policy engine keeps source adapters safe.", encoding="utf-8")
            outside_source = outside_root / "outside.md"
            outside_source.write_text("outside", encoding="utf-8")
            workspace = allowed_root / "workspace"
            cfg = McpToolConfig(allowed_workspaces=(allowed_root,), root=allowed_root)

            inspect = source2study_inspect_local(str(workspace), str(source), config=cfg)
            self.assertIn(inspect["status"], {"pass", "degraded"})
            self.assertIn("intake_summary_path", inspect)

            ingest = source2study_ingest_local(str(workspace), [str(source)], config=cfg)
            self.assertEqual(ingest["status"], "pass")
            self.assertIn("evidence_ledger_path", ingest)

            rejected = source2study_ingest_local(str(workspace), [str(outside_source)], config=cfg)
            self.assertEqual(rejected["status"], "fail")
            self.assertIn("allowlist", rejected["error"]["message"])

    def test_blocked_url_is_not_ingested(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            cfg = McpToolConfig(allowed_workspaces=(root,), root=root)
            result = source2study_ingest_local(str(root / "workspace"), ["https://example.com/page"], config=cfg)
        self.assertEqual(result["status"], "fail")
        self.assertIn("Network access is disabled", result["error"]["message"])

    def test_generate_personalized_pack_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            source = root / "notes.md"
            source.write_text(
                "# Source adapter\n\nEvidenceIndex, citation verifier, policy engine, and IntakeReport support safe learning packs.",
                encoding="utf-8",
            )
            workspace = root / "workspace"
            cfg = McpToolConfig(allowed_workspaces=(root,), root=root)

            self.assertEqual(source2study_ingest_local(str(workspace), [str(source)], config=cfg)["status"], "pass")
            self.assertEqual(source2study_build_index(str(workspace), config=cfg)["status"], "pass")
            generated = source2study_generate_personalized_pack(
                str(workspace),
                "developer",
                {
                    "goal": "Learn the project safely",
                    "current_level": "beginner",
                    "time_budget": "1 hour",
                    "use_case": "developer",
                    "preferred_style": "structured",
                    "must_include": ["practice task"],
                },
                config=cfg,
            )
            self.assertEqual(generated["status"], "pass")
            for key in ("pack_path", "output_path", "citation_report_path", "learning_quality_report_path"):
                self.assertIn(key, generated)

    def test_run_eval_smoke_and_call_tool_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            cfg = McpToolConfig(allowed_workspaces=(root,), root=root)
            result = source2study_run_eval("standard_demo", config=cfg)
            self.assertEqual(result["status"], "pass")
            self.assertIn("metrics", result)

            listed = call_tool("tools/list", {}, config=cfg)
            self.assertEqual(listed["status"], "pass")
            self.assertTrue(listed["tools"])

    def test_response_redaction_removes_secrets_and_browser_paths(self):
        sample_secret = "redactiontestvalue1234567890"
        cookie_value = "session" + "id=abc123"
        payload = sanitize_for_response(
            {
                "authorization": "Authorization: " + "Bearer " + sample_secret,
                "header": "coo" + "kie: " + cookie_value,
                "path": "C:\\Users\\alice\\AppData\\Local\\Google\\Chrome\\User " + "Data\\Default",
            }
        )
        serialized = str(payload)
        self.assertNotIn(sample_secret, serialized)
        self.assertNotIn(cookie_value, serialized)
        self.assertNotIn("Chrome\\User Data", serialized)


if __name__ == "__main__":
    unittest.main()
