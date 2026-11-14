# career-tools (MCP server)

An MCP server that gives Claude live finance-recruiting and market data. Pure Python standard library: no packages, no API keys, no logins. `read_document` also uses `pdftotext` for PDFs when it's installed (`brew install poppler`).

## Tools

**Jobs**

| Tool | Source | Returns |
|---|---|---|
| `search_jobs` | Each firm's own careers feed (Workday, Greenhouse, Lever, Ashby, SmartRecruiters, Oracle, or a page scan) | Live student postings: internships, summer analyst, sophomore and insight programs |
| `new_postings` | Same | Only postings that appeared since the last check |
| `job_details` | The posting's job system | Full description, location, posted and closing dates, deadline sentences, apply link |
| `simplify_jobs` | [SimplifyJobs](https://github.com/SimplifyJobs) community list | Postings at thousands of companies; fills gaps such as Goldman Sachs |
| `add_firm` / `list_firms` | `firms.json` | Paste a careers URL; it detects the job system, tests the feed, and saves the firm |

**News, deals, and research**

| Tool | Source | Returns |
|---|---|---|
| `market_news` | NYT Business and DealBook, FT, Yahoo Finance, plus WSJ and Reuters through Google News | Headlines with links (open them with your own logins) |
| `ticker_news` | Yahoo Finance | Headlines for one ticker |
| `recent_deals` | PR Newswire M&A wire, press headlines, SEC merger agreements | New deal announcements |
| `firm_deals` | News, plus the firm's own transaction announcements (Evercore) | Deals a firm advised on or did |
| `sec_filings` | SEC EDGAR full-text search | Filings that contain a phrase |
| `bank_research` | Firms' sitemaps (`research.json`) | New research from Goldman Sachs, JPMorgan, Morgan Stanley, PIMCO, Apollo, and BofA Institute; firm press releases from Evercore, Moelis, and PJT |
| `read_document` | Any URL | Full text of a page or PDF |

**Macro**

| Tool | Source | Returns |
|---|---|---|
| `fed_releases` | federalreserve.gov RSS | Press releases, monetary policy, speeches, testimony, H.4.1 |
| `econ_series` | FRED | Any series: yields, spreads, CPI, payrolls, VIX |
| `treasury_yields` | home.treasury.gov | The official daily yield curve |
| `search_news` / `firm_news` | Google News | Recent articles on any topic or firm |

## Sites that need a browser

Some sites refuse automated requests or only render in a browser. Rather than fail, the tools say so:

- `search_jobs` lists them under `needs_browser` (Goldman Sachs, Morgan Stanley, Moelis). Firms with `"ats": "tinyfish"` in `firms.json` work this way.
- `bank_research` marks them `read_with: tinyfish` (Blackstone, Carlyle, KKR, Lazard, BlackRock).
- `job_details` and `read_document` add `needs_browser` when little text comes back.

Claude then reads those URLs with the TinyFish connector's `fetch_content`, which runs a real browser, at most $0.001 a page. This server can't call TinyFish itself, because TinyFish is a claude.ai connector.

## Add a firm

Ask Claude: "add Moelis, here's their careers page: <url>". Or edit `firms.json` directly:
```json
{"name": "Moelis", "category": "Elite boutique", "ats": "workday", "board": "<tenant>.wd1.myworkdayjobs.com/<site>"}
```
`ats` is one of `workday`, `greenhouse`, `lever`, `ashby`, `smartrecruiters`, `oracle`, `html`, or `tinyfish`. Add an optional `"title_filter"` regex to keep only some roles (for example, finance roles at a luxury house).

To add a research source, add an entry to `research.json` with the firm's sitemap and the URL paths that hold its research. Run `python3 -I mcp/career-tools/smoke_test.py` afterward.

## Connect it to Claude Code

The repo's `.mcp.json` registers the server for any Claude Code session opened in this repo, including cloud sessions. To use it from anywhere on your Mac:
```
claude mcp add --scope user career-tools -- /usr/bin/python3 -I "/path/to/mcp/career-tools/server.py"
```

## Test it

```
python3 -I mcp/career-tools/smoke_test.py
```
This starts the server the way Claude does, calls every tool against live sources, and prints OK or FAIL for each. Workday sites go down for maintenance on some weekends; those firms show up under `errors` until they're back.

## How it works

- `mcp_stdio.py`: a ~100-line MCP implementation (JSON-RPC 2.0 over stdin/stdout).
- `jobs.py`: one adapter per job system, a student-program filter, full-posting details, and the SimplifyJobs list. The adapter approach follows [freehire](https://github.com/strelov1/freehire) (MIT).
- `feeds.py`: news, deals, SEC EDGAR, Fed RSS, FRED, and Treasury.
- `research.py` and `research.json`: firm research from sitemaps, and page/PDF text.
- `text.py`: HTML and PDF to plain text, and deadline detection.
- Firms are checked in parallel (6 at a time) with polite retries. Seen postings and large files (sitemaps, the Simplify list) are cached in `private/cache/` (git-ignored).

Only public feeds are used. Nothing logs in, applies, or gets around a paywall.
