import argparse
import asyncio
import json
import logging
import sys
import time

from matcher import Matcher, load_fingerprints
from scanner import scan_domains


def read_domains(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"error: domains file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return list(dict.fromkeys(lines))


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

    start = time.perf_counter()
    results = asyncio.run(scan_domains(domains, matcher, args.concurrency))
    elapsed = time.perf_counter() - start

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    rate = len(results) / elapsed if elapsed > 0 else 0
    detections = sum(len(v) for v in results.values())
    print(f"Scanned {len(results)} domains in {elapsed:.2f}s "
          f"(concurrency={args.concurrency}, {rate:.1f} domains/s)")
    print(f"Detected {detections} technologies")
    print(f"Wrote results to {args.output}")


if __name__ == "__main__":
    main()
