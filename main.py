import argparse
import asyncio
import json
import logging

from matcher import Matcher, load_fingerprints
from scanner import scan_domains


def read_domains(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser(description="Detect technologies used by domains.")
    parser.add_argument("--domains", default="domains.txt")
    parser.add_argument("--fingerprints", default="fingerprints.json")
    parser.add_argument("--output", default="output.json")
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")

    domains = read_domains(args.domains)
    matcher = Matcher(load_fingerprints(args.fingerprints))
    results = asyncio.run(scan_domains(domains, matcher, args.concurrency))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Wrote results for {len(results)} domains to {args.output}")


if __name__ == "__main__":
    main()
