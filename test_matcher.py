import os
import unittest

from matcher import Matcher, load_fingerprints

FINGERPRINTS_PATH = os.path.join(os.path.dirname(__file__), "fingerprints.json")


class TestLoadFingerprints(unittest.TestCase):
    def test_loads_all_technologies(self):
        fps = load_fingerprints(FINGERPRINTS_PATH)
        self.assertEqual(len(fps), 16)
        self.assertIn("HubSpot", fps)
        self.assertIn("Hotjar", fps)


class TestMatch(unittest.TestCase):
    def setUp(self):
        self.matcher = Matcher(load_fingerprints(FINGERPRINTS_PATH))

    def match(self, **channels):
        return self.matcher.match(channels)

    def test_script(self):
        self.assertIn("HubSpot", self.match(script=["//js.hs-scripts.com/123.js"]))

    def test_header_case_insensitive(self):
        self.assertIn("Cloudflare", self.match(header=["CF-Ray"]))

    def test_cookie(self):
        self.assertIn("Intercom", self.match(cookie=["intercom-session-123"]))

    def test_html(self):
        self.assertIn("WordPress", self.match(html=["... /wp-content/ ..."]))

    def test_dns_mx(self):
        self.assertIn("Google Workspace", self.match(dns_mx=["aspmx.l.google.com"]))

    def test_dns_txt(self):
        self.assertIn("SendGrid", self.match(dns_txt=["v=spf1 include:sendgrid.net"]))

    def test_dns_cname(self):
        self.assertIn("Salesforce", self.match(dns_cname=["foo.salesforce.com"]))

    def test_no_signals(self):
        self.assertEqual(self.match(), set())

    def test_multiple_technologies(self):
        result = self.match(
            script=["js.stripe.com/v3"],
            dns_mx=["aspmx.l.google.com"],
        )
        self.assertIn("Stripe", result)
        self.assertIn("Google Workspace", result)


if __name__ == "__main__":
    unittest.main()
