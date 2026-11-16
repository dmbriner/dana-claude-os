# market-tools (MCP server)

An MCP server that gives Claude live market data and reported company financials. Like `career-tools`, it's pure Python standard library: no packages, no API keys, no rate-limited free tier.

| Tool | Source | What it returns |
|---|---|---|
| `quote` | Yahoo Finance | Price, daily change, day range, volume, 52-week range, % off the high. Stocks, ETFs, indices (`^GSPC`), FX (`EURUSD=X`), futures (`CL=F`), crypto |
| `performance` | Yahoo Finance | Dividend-adjusted returns over 1W–5Y, 1Y volatility, max drawdown, for a peer set |
| `price_history` | Yahoo Finance | OHLC, adjusted close, volume, dividends, splits; daily down to 1-minute |
| `search_ticker` | Yahoo Finance | Company name → ticker |
| `sec_filings` | SEC EDGAR | 10-K, 10-Q, 8-K (with item numbers), proxies, S-1s, Form 4s, with direct links |
| `sec_financials` | SEC XBRL company facts | Annual or quarterly revenue, margins, EBITDA, EPS, cash flow, FCF, buybacks, debt, net debt, equity |
| `sec_concept` | SEC XBRL | The history of any single reported tag (R&D, stock comp, bank-specific items) |

It reads the same Yahoo endpoints the `yfinance` package uses, without installing it.

## Connect it to Claude Code
```
claude mcp add --scope user market-tools -- /usr/bin/python3 -I "/path/to/mcp/market-tools/server.py"
```

## Settings (optional environment variables)
- `SEC_CONTACT_EMAIL`: SEC asks automated clients to identify themselves with a contact email. The default is a placeholder; set your own to follow SEC's policy exactly.
- `MARKET_TOOLS_CACHE`: where the SEC ticker list is cached for a day (default `private/cache/`, git-ignored).

## Caveats
- EBITDA is operating income + D&A as reported, not adjusted EBITDA.
- Quarterly SEC rows come from 10-Qs, so Q4 usually has no row of its own.
- Banks and insurers tag revenue differently; use `sec_concept` for their line items.
- Yahoo's endpoints are unofficial and occasionally change.

Shares `mcp_stdio.py` with `../career-tools`.
