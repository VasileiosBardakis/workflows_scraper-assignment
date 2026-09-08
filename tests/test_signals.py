import unittest

from fetcher import Response
from signals import extract

HTML = """<html><head>
<meta name="generator" content="WordPress">
<script src="//js.hs-scripts.com/123.js"></script>
<script>window.intercomSettings = {app_id: 'x'};</script>
</head><body><script src="/assets/app.js"></script></body></html>"""


def make_response():
    return Response(
        url="https://example.com",
        status=200,
        headers={"cf-ray": "abc", "x-stripe-x": "1"},
        cookies={"intercom-session": "v"},
        body=HTML,
    )


DNS = {"dns_mx": ["aspmx.l.google.com"], "dns_txt": [], "dns_cname": []}


class TestExtract(unittest.TestCase):
    def setUp(self):
        self.signals = extract(make_response(), DNS)

    def test_headers_are_names(self):
        self.assertIn("cf-ray", self.signals["header"])
        self.assertIn("x-stripe-x", self.signals["header"])

    def test_cookies_are_names(self):
        self.assertIn("intercom-session", self.signals["cookie"])

    def test_script_srcs(self):
        self.assertIn("//js.hs-scripts.com/123.js", self.signals["script"])
        self.assertIn("/assets/app.js", self.signals["script"])

    def test_html_body(self):
        self.assertEqual(self.signals["html"], [HTML])

    def test_meta(self):
        self.assertIn("WordPress", self.signals["meta"])
        self.assertIn("generator", self.signals["meta"])

    def test_js_globals(self):
        self.assertIn("intercomSettings", self.signals["js"])

    def test_dns_passthrough(self):
        self.assertEqual(self.signals["dns_mx"], ["aspmx.l.google.com"])

    def test_none_response_returns_dns(self):
        self.assertEqual(extract(None, DNS), DNS)


if __name__ == "__main__":
    unittest.main()
