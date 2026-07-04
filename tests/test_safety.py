import unittest

from source2study.safety.redaction import find_secrets, redact_paths, redact_secrets, sanitize_for_response


class SafetyTests(unittest.TestCase):
    def test_detects_and_redacts_tokens(self):
        sample_secret = "redactiontestvalue1234567890"
        text = "Authorization: " + "Bearer " + sample_secret
        self.assertTrue(find_secrets(text))
        self.assertIn("[REDACTED_SECRET]", redact_secrets(text))
        self.assertNotIn(sample_secret, redact_secrets(text))

    def test_redacts_cookie_headers_and_browser_profile_paths(self):
        cookie_value = "session" + "id=abc123"
        payload = "coo" + "kie: " + cookie_value
        self.assertNotIn(cookie_value, redact_secrets(payload))
        path = "C:\\Users\\alice\\AppData\\Local\\Google\\Chrome\\User " + "Data\\Default"
        self.assertIn("[REDACTED_BROWSER_PROFILE]", redact_paths(path))

    def test_sanitize_for_response_redacts_nested_values(self):
        sample_secret = "redactiontestvalue1234567890"
        response = sanitize_for_response({"headers": {"authorization": "Bearer " + sample_secret}})
        self.assertNotIn(sample_secret, str(response))


if __name__ == "__main__":
    unittest.main()
