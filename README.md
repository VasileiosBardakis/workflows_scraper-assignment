# Technographic Detector

A small command-line tool that, given a list of domains, figures out which
technologies each one uses by looking at publicly visible signals - response
headers, script tags, cookies, DNS records, meta tags, and inline JavaScript.
No headless browser, no paid APIs.

## What it does

For every domain in an input file it:

1. fetches the homepage over HTTPS/HTTP, following redirects,
2. looks up the apex domain's MX, TXT and CNAME records,
3. extracts signals from headers, `<script src>` tags, cookies, meta tags and
   `window.*` globals,
4. matches those signals against a fingerprint database,
5. writes the results as JSON.

## Install

Requires python v3.9+.

```
pip install -r requirements.txt
```

## Usage

```
python main.py
```

By default it reads `domains.txt` and writes `output.json`. All paths and the
concurrency level can be overridden:

```
python main.py --domains domains.txt --output output.json --concurrency 10
```

The output is a single JSON object mapping each domain to the technologies
detected:

```json
{
  "stripe.com": ["Google Workspace", "Stripe"],
  "notion.so": ["Cloudflare"]
}
```

## Testing (Optional)

```
python -m unittest discover -s tests -t .
```

A small test suite (matcher, signals, fetcher, DNS) is included. It wasn't part
of the assignment, but it's cheap insurance for keeping the tool production-ready.

## Architecture

Small, single-purpose modules that form a pipeline:

- `fetcher.py` - async HTTP fetch (`httpx`)
- `dns_lookup.py` - async DNS lookups (`dnspython`)
- `signals.py` - turns a response + DNS results into a flat signal map
- `matcher.py` - loads fingerprints and matches signals
- `scanner.py` - ties it together with bounded concurrency
- `main.py` - CLI entrypoint

## Design decisions

- **Async + bounded concurrency.** Every network operation is async, and a
  semaphore caps the number of in-flight requests. That's what lets 20 domains
  finish in a few seconds instead of minutes, without hammering servers.
- **Fail soft, always.** Timeouts, DNS failures and bot-blocks are logged and
  skipped, never fatal. A domain that can't be scanned just shows up as `[]`.
- **DNS on the apex domain.** `www.` is stripped before lookups, since MX/TXT
  records live on the apex.
- **Static signals, not a browser.** `window.*` globals are detected with a
  regex rather than executing the page, per the constraint.

## Notes

### Requirement inconsistencies

A few things I noticed while implementing against the spec, collected here:

- **"Wappalyzer format" vs. the format actually provided.** The spec says to
  use the same pattern format as Wappalyzer, but the provided subset uses a
  simplified channel model (`header`, `cookie`, `dns_txt`, etc. as regex lists)
  instead of Wappalyzer's object format (`headers`/`cookies`/`dns`/`js`/`meta`
  as name-to-value maps). The matcher accepts both dialects, so the supplied
  subset works unchanged and further Wappalyzer-format fingerprints can be
  added without code changes.

- **Google Analytics 4 can never match as specified.** The GA4 patterns
  (`google-analytics\.com/g/collect`, `gtag\(`) are inline-JS/network-endpoint
  patterns, but the spec defines the `script` channel as `<script src>`
  attributes, where neither pattern can appear - so GA4 is never detected.
  In Wappalyzer's real format these belong to the `scripts` (inline JS source)
  channel. I kept the fingerprints exactly as provided rather than
  second-guessing the spec.

- **Salesforce CNAME on the apex domain.** The spec asks for CNAME lookups on
  the apex, but an apex domain cannot carry CNAME records (RFC - it already
  holds SOA/NS), so `dns_cname` is always empty and the Salesforce fingerprint
  can never match. Salesforce CNAMEs only exist on subdomains (e.g. `www`).
  Implemented as specified.


### Other notes

**Run-to-run variance.** Results can differ slightly between runs. Scanning
the live web means soft-blocks, rate limiting, A/B tests and geo-redirects
change what a homepage serves at any given moment, so a domain may show fewer
(or no) detections on one run and more on the next. `output.json` is a
point-in-time snapshot, not a stable fingerprint.
