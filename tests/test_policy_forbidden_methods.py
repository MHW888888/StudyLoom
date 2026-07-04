import unittest
from pathlib import Path

from source2study.config import SourcePolicy
from source2study.safety.policy import PolicyEngine


FIXTURES = Path(__file__).parent / "fixtures"


class PolicyForbiddenMethodTests(unittest.TestCase):
    def test_user_export_fixtures_are_allowed(self):
        for fixture in [
            FIXTURES / "sample_notes.md",
            FIXTURES / "wechat" / "article.wechat.html",
            FIXTURES / "xhs" / "note.xhs.md",
            FIXTURES / "xhs" / "note.xhs.json",
            FIXTURES / "zhihu" / "question.zhihu.html",
            FIXTURES / "browser_capture" / "article.browser_capture.json",
            FIXTURES / "screenshots" / "slide.png",
            FIXTURES / "transcripts" / "bilibili.srt",
        ]:
            with self.subTest(fixture=fixture.name):
                decision = PolicyEngine().check_source(str(fixture), SourcePolicy())
                self.assertTrue(decision.allowed)

    def test_direct_high_risk_platform_urls_are_blocked(self):
        for source in [
            "https://www.xiaohongshu.com/explore/mock",
            "https://mp.weixin.qq.com/s/mock",
            "https://www.zhihu.com/question/123",
            "https://www.youtube.com/watch?v=mock",
        ]:
            with self.subTest(source=source):
                decision = PolicyEngine().check_source(source, SourcePolicy(allow_network=True))
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.source_type, "blocked_platform")

    def test_forbidden_extraction_methods_are_blocked(self):
        cases = {
            "source2study://wechat/cookie_replay": "cookie_replay",
            "source2study://wechat/account_history_bulk_crawl": "account_history_bulk_crawl",
            "source2study://xhs/login_bypass": "login_bypass",
            "source2study://course/paywall_bypass": "paywall_bypass",
            "source2study://course/drm_bypass": "drm_bypass",
            "source2study://xhs/anti_bot_bypass": "anti_bot_bypass",
            "https://www.zhihu.com/question/123?x-zse-96=mock": "signature_bypass",
            "source2study://browser/raw_headers": "login_bypass",
            "source2study://zhihu/signature_reverse_engineering": "signature_bypass",
            "source2study://screenshots/bulk_screenshot_crawl": "account_history_bulk_crawl",
        }
        for source, method in cases.items():
            with self.subTest(method=method):
                decision = PolicyEngine().check_source(source, SourcePolicy(allow_network=True))
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.source_type, "blocked_method")
                self.assertIn(method, decision.blocked_methods)


if __name__ == "__main__":
    unittest.main()
