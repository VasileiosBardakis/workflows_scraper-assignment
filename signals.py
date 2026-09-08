import re

from bs4 import BeautifulSoup

WINDOW_GLOBAL = re.compile(
    r"window(?:\.(\w+)|\s*\[\s*['\"](\w+)['\"]\s*\])\s*=\s*(.+?)(?:;|\n|$)"
)


def extract(response, dns):
    if response is None:
        return dict(dns)

    headers = response.headers
    cookies = response.cookies
    signals = {
        "header": list(headers),
        "header_values": {k.lower(): v for k, v in headers.items()},
        "cookie": list(cookies),
        "cookie_values": dict(cookies),
    }

    if response.body:
        signals["html"] = [response.body]
        soup = BeautifulSoup(response.body, "html.parser")
        signals["script"] = [
            tag["src"] for tag in soup.find_all("script") if tag.get("src")
        ]
        meta = []
        meta_values = {}
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property")
            content = tag.get("content")
            if name and content:
                meta_values[name] = content
            if content:
                meta.append(content)
            if name:
                meta.append(name)
        signals["meta"] = meta
        signals["meta_values"] = meta_values
        js = []
        js_values = {}
        for a, b, rhs in WINDOW_GLOBAL.findall(response.body):
            name = a or b
            js.append(name)
            js_values[name] = rhs
        signals["js"] = js
        signals["js_values"] = js_values

    signals.update(dns)
    return signals
