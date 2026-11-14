# career-tools (MCP server)

An MCP server that gives Claude live finance-recruiting and market data. It's pure Python standard library: no packages, no API keys, no logins.

| Tool | Source | What it returns |
|---|---|---|
| `search_jobs` | Each firm's own careers feed (Workday, Greenhouse, Lever, Ashby, SmartRecruiters, or a page scan) | Live student postings: internships, summer analyst, sophomore and insight programs |
| `new_postings` | Same | Only the postings that appeared since the last check |
| `add_firm` | — | Paste a careers URL; it detects the job system, tests the feed, and saves the firm |
| `list_firms` | `firms.json` | The firm list |
| `fed_releases` | federalreserve.gov RSS | Press releases, monetary policy, speeches, testimony, H.4.1 |
| `econ_series` | FRED | Any series: yields, spreads, CPI, payrolls, VIX |
| `treasury_yields` | home.treasury.gov | The official daily yield curve |
| `search_news` / `firm_news` | Google News RSS | Recent articles on any topic or firm |

## Add a firm
Ask Claude: "add Moelis, here's their careers page: <url>". Or edit `firms.json` directly:
```json
{"name": "Moelis", "category": "Elite boutique", "ats": "workday", "board": "<tenant>.wd1.myworkdayjobs.com/<site>"}
```
Add an optional `"title_filter"` regex to keep only some roles (for example, finance roles at a luxury house).

## Connect it to Claude Code
```
claude mcp add --scope user career-tools -- /usr/bin/python3 -I "/path/to/mcp/career-tools/server.py"
```

## How it works
- `mcp_stdio.py`: a ~100-line MCP implementation (JSON-RPC 2.0 over stdin/stdout).
- `jobs.py`: one adapter per applicant tracking system, plus a student-program filter. The adapter approach follows [freehire](https://github.com/strelov1/freehire) (MIT).
- `feeds.py`: Fed RSS, FRED, Treasury, and Google News.
- Firms are checked in parallel (6 at a time) with polite retries. Seen postings are cached in `private/cache/` (git-ignored).

Only public feeds are used. Nothing logs in, applies, or gets around a paywall.
