import asyncio
import unittest

from dns_lookup import lookup


class TestDnsLookup(unittest.TestCase):
    def run_async(self, coro):
        return asyncio.run(coro)

    def test_mx_google_workspace(self):
        r = self.run_async(lookup("gmail.com"))
        self.assertTrue(any("google.com" in x for x in r["dns_mx"]))

    def test_mx_microsoft_365(self):
        r = self.run_async(lookup("microsoft.com"))
        self.assertTrue(any("outlook.com" in x for x in r["dns_mx"]))

    def test_txt_hubspot(self):
        r = self.run_async(lookup("hubspot.com"))
        self.assertTrue(any("hubspot-developer-verification" in x for x in r["dns_txt"]))

    def test_nonexistent_domain_returns_empty(self):
        r = self.run_async(lookup("this-domain-does-not-exist-12345.invalid"))
        self.assertEqual(r, {"dns_mx": [], "dns_txt": [], "dns_cname": []})


if __name__ == "__main__":
    unittest.main()
