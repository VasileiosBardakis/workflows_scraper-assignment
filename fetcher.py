import logging

import httpx

log = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; TechnographicDetector/1.0)"
TIMEOUT = 10.0


class Response:
    __slots__ = ("url", "status", "headers", "cookies", "body")

    def __init__(self, url, status, headers, cookies, body):
        self.url = url
        self.status = status
        self.headers = headers
        self.cookies = cookies
        self.body = body


def make_client():
    return httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})


async def fetch(domain, client):
    for scheme in ("https", "http"):
        url = domain if "://" in domain else f"{scheme}://{domain}/"
        try:
            r = await client.get(url, follow_redirects=True)
            cookies = {}
            for resp in [*r.history, r]:
                cookies.update(dict(resp.cookies.items()))
            return Response(
                url=str(r.url),
                status=r.status_code,
                headers=dict(r.headers.items()),
                cookies=cookies,
                body=r.text,
            )
        except httpx.HTTPError as e:
            log.warning("fetch failed for %s (%s): %s", domain, scheme, e)
            continue
    log.warning("could not fetch %s", domain)
    return None
