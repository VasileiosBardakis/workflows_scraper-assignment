import asyncio
import unittest

from fetcher import Response, fetch, make_client


class TestFetcher(unittest.TestCase):
    def run_async(self, coro):
        return asyncio.run(coro)

    def test_fetch_success(self):
        async def go():
            client = make_client()
            try:
                return await fetch("stripe.com", client)
            finally:
                await client.aclose()

        resp = self.run_async(go())
        self.assertIsInstance(resp, Response)
        self.assertEqual(resp.status, 200)
        self.assertTrue(resp.body)
        self.assertIn("content-type", {k.lower() for k in resp.headers})

    def test_fetch_nonexistent_domain_returns_none(self):
        async def go():
            client = make_client()
            try:
                return await fetch("this-domain-does-not-exist-12345.invalid", client)
            finally:
                await client.aclose()

        self.assertIsNone(self.run_async(go()))


if __name__ == "__main__":
    unittest.main()
