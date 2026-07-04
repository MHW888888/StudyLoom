import tempfile
import unittest
from pathlib import Path

from source2study.adapters.base import SourceRequest
from source2study.adapters.pdf_adapter import PdfAdapter
from source2study.cli import ADAPTERS


class AdapterContractTests(unittest.TestCase):
    def test_all_adapters_declare_v03_contract_fields(self):
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter.__class__.__name__):
                contract = adapter.contract()
                self.assertTrue(contract["name"])
                self.assertTrue(contract["source_types"])
                self.assertIn(contract["risk_level"], {"low", "medium", "high", "unknown"})
                self.assertIsInstance(contract["default_enabled"], bool)
                self.assertTrue(contract["allowed_methods"])
                self.assertTrue(contract["blocked_methods"])
                self.assertTrue(contract["fallback_options"])

                capability = adapter.capability()
                self.assertEqual(capability.risk_level, adapter.risk_level)
                self.assertEqual(capability.default_enabled, adapter.default_enabled)
                self.assertTrue(capability.allowed_methods)
                self.assertTrue(capability.blocked_methods)

    def test_adapter_policy_check_attaches_contract_metadata(self):
        fixture = Path(__file__).parent / "fixtures" / "sample_notes.md"
        with tempfile.TemporaryDirectory() as tmp:
            request = SourceRequest(str(fixture), Path(tmp))
            decision = PdfAdapter().policy_check(request)
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.source_type, "document")
        self.assertEqual(decision.risk_level, "low")
        self.assertIn("user_uploaded_markdown", decision.allowed_methods)


if __name__ == "__main__":
    unittest.main()
