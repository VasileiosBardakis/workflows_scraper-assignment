import asyncio
import logging

import dns.resolver

log = logging.getLogger(__name__)

RECORD_TYPES = {
    "dns_mx": "MX",
    "dns_txt": "TXT",
    "dns_cname": "CNAME",
}


def _apex(domain):
    return domain[4:] if domain.lower().startswith("www.") else domain


def _lookup(domain, rdtype):
    try:
        answers = dns.resolver.resolve(domain, rdtype, lifetime=5)
    except Exception:
        return []
    if rdtype == "MX":
        return [str(r.exchange).rstrip(".") for r in answers]
    if rdtype == "CNAME":
        return [str(r.target).rstrip(".") for r in answers]
    return ["".join(s.decode(errors="ignore") if isinstance(s, bytes) else s
                    for s in r.strings) for r in answers]


async def lookup(domain):
    apex = _apex(domain)
    results = {}
    for channel, rdtype in RECORD_TYPES.items():
        results[channel] = await asyncio.to_thread(_lookup, apex, rdtype)
    return results
