import json
import re

LIST_CHANNELS = {
    "html": "html",
    "script": "script",
    "scripts": "script",
    "scriptSrc": "script",
    "header": "header",
    "cookie": "cookie",
    "dns_mx": "dns_mx",
    "dns_txt": "dns_txt",
    "dns_cname": "dns_cname",
}

OBJECT_CHANNELS = {"headers", "cookies", "dns"}
AMBIGUOUS_CHANNELS = {"js", "meta"}

CASE_INSENSITIVE = {
    "header", "cookie", "headers", "cookies",
    "dns", "dns_mx", "dns_txt", "dns_cname",
}

OBJECT_SOURCES = {
    "headers": "header_values",
    "cookies": "cookie_values",
    "js": "js_values",
    "meta": "meta_values",
}


def _patterns(value):
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def _compile(pattern, flags):
    return re.compile(pattern, flags)


def _normalize_tech(raw):
    list_patterns = {}
    object_patterns = {}
    for key, value in raw.items():
        flags = re.IGNORECASE if key in CASE_INSENSITIVE else 0
        if key in LIST_CHANNELS:
            channel = LIST_CHANNELS[key]
            list_patterns.setdefault(channel, []).extend(
                _compile(p, flags) for p in _patterns(value)
            )
        elif key in OBJECT_CHANNELS or key in AMBIGUOUS_CHANNELS:
            if isinstance(value, dict):
                for name, pat in value.items():
                    object_patterns.setdefault(key, []).append(
                        (name, _compile(pat or "", flags))
                    )
            else:
                list_patterns.setdefault(key, []).extend(
                    _compile(p, flags) for p in _patterns(value)
                )
    return list_patterns, object_patterns


def parse_fingerprints(data):
    technologies = data.get("technologies", data)
    return {tech: _normalize_tech(raw) for tech, raw in technologies.items()}


def load_fingerprints(path):
    with open(path, encoding="utf-8") as f:
        return parse_fingerprints(json.load(f))


def _get(mapping, name):
    if not mapping:
        return None
    if name in mapping:
        return mapping[name]
    return mapping.get(name.lower())


class Matcher:
    def __init__(self, fingerprints):
        self.fingerprints = fingerprints

    def match(self, signals):
        detected = set()
        for tech, (list_patterns, object_patterns) in self.fingerprints.items():
            if self._matches(list_patterns, object_patterns, signals):
                detected.add(tech)
        return detected

    def _matches(self, list_patterns, object_patterns, signals):
        for channel, patterns in list_patterns.items():
            values = signals.get(channel, [])
            if any(p.search(v) for p in patterns for v in values):
                return True
        for channel, checks in object_patterns.items():
            for name, pattern in checks:
                if self._object_match(channel, name, pattern, signals):
                    return True
        return False

    def _object_match(self, channel, name, pattern, signals):
        if channel == "dns":
            values = signals.get("dns_" + name.lower(), [])
            return any(pattern.search(v) for v in values)
        value = _get(signals.get(OBJECT_SOURCES[channel], {}), name)
        return value is not None and pattern.search(value)
