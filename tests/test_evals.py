import unittest

from evals.run_eval import concept_coverage, mode_fit, policy_compliance, run_suite


class EvalTests(unittest.TestCase):
    def test_eval_report_schema_and_standard_metrics(self):
        report = run_suite("standard_demo")
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["source2study_version"], "1.5.0a0")
        self.assertEqual(report["suite"], "standard_demo")
        for key in [
            "intake_pass_rate",
            "low_confidence_evidence_rate",
            "source_asset_coverage",
            "citation_coverage",
            "missing_citation_rate",
            "concept_coverage",
            "mode_fit",
            "learner_profile_fit",
            "policy_compliance",
        ]:
            self.assertIn(key, report["metrics"])

    def test_degraded_eval_tracks_source_fidelity_disclosure(self):
        report = run_suite("degraded_demo")
        metrics = report["metrics"]
        self.assertEqual(report["status"], "pass")
        self.assertEqual(metrics["intake_degraded_rate"], 1.0)
        self.assertEqual(metrics["low_confidence_evidence_rate"], 1.0)
        self.assertEqual(metrics["source_asset_coverage"], 1.0)
        self.assertEqual(metrics["degraded_output_disclosure"], 1.0)
        self.assertEqual(metrics["missing_location_rate"], 0.0)

    def test_personalized_eval_confirms_mode_and_profile_fit(self):
        report = run_suite("personalized_demo")
        metrics = report["metrics"]
        self.assertEqual(report["status"], "pass")
        self.assertGreaterEqual(metrics["mode_fit"], 0.75)
        self.assertGreaterEqual(metrics["learner_profile_fit"], 0.7)
        self.assertEqual(len(report["cases"]), 4)

    def test_concept_coverage_and_mode_fit_helpers(self):
        expected = {
            "required_concepts": ["EvidenceIndex", "citation verifier"],
            "required_sections": ["Source Intake Summary", "Learning Map"],
            "required_blocks": ["practice_task"],
        }
        text = "Source Intake Summary\nLearning Map\nThe EvidenceIndex works with a citation verifier and practice task."
        self.assertEqual(concept_coverage(text, expected), 1.0)
        self.assertEqual(mode_fit(text, expected), 1.0)

    def test_policy_compliance_detects_forbidden_patterns(self):
        expected = {"forbidden_patterns": ["cookie replay", "paywall bypass"]}
        self.assertEqual(policy_compliance("Use local exports only.", expected, []), 1.0)
        self.assertEqual(policy_compliance("Try cookie replay.", expected, []), 0.0)
        self.assertEqual(policy_compliance("Safe output", expected, [{"status": "blocked", "errors": []}]), 0.0)


if __name__ == "__main__":
    unittest.main()
