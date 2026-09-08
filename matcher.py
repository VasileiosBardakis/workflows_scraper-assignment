import json
import re
from pathlib import Path

CASE_INSENSITIVE_CHANNELS = {"header", "cookie"}


def load_fingerprints(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {
        tech: {
            channel: [re.compile(p, re.IGNORECASE if channel in CASE_INSENSITIVE_CHANNELS else 0)
                      for p in patterns]
            for channel, patterns in channels.items()
        }
        for tech, channels in data.items()
    }


class Matcher:
    def __init__(self, fingerprints):
        self.fingerprints = fingerprints

    def match(self, signals):
        detected = set()
        for tech, channels in self.fingerprints.items():
            for channel, patterns in channels.items():
                values = signals.get(channel, [])
                if any(p.search(v) for p in patterns for v in values):
                    detected.add(tech)
                    break
        return detected
