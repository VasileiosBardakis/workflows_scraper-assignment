import asyncio
import logging

from dns_lookup import lookup as dns_lookup
from fetcher import fetch, make_client
from signals import extract

log = logging.getLogger(__name__)


async def _scan_one(domain, matcher, client, sem):
    async with sem:
        dns, response = await asyncio.gather(
            dns_lookup(domain),
            fetch(domain, client),
        )
        return matcher.match(extract(response, dns))


async def scan_domains(domains, matcher, concurrency=10):
    sem = asyncio.Semaphore(concurrency)
    async with make_client() as client:
        tasks = [_scan_one(d, matcher, client, sem) for d in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    out = {}
    for domain, techs in zip(domains, results):
        if isinstance(techs, Exception):
            log.warning("scan failed for %s: %s", domain, techs)
            techs = set()
        out[domain] = sorted(techs)
    return out
