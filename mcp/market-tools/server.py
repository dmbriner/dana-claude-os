"""market-tools: an MCP server for market data and company financials.

Yahoo Finance prices (the data yfinance reads) and SEC EDGAR filings and reported financials.
Pure standard library. Run: python3 -I server.py   (Claude Code launches it; see README.md)
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # -I drops the script dir; add it back explicitly
sys.path.insert(1, str(HERE.parent / "career-tools"))  # shared MCP plumbing

import sec  # noqa: E402
import yahoo  # noqa: E402
from mcp_stdio import Server  # noqa: E402

srv = Server("market-tools", "0.1.0")
TICKERS = {"type": "array", "items": {"type": "string"}, "description": "Tickers, e.g. ['GS', 'MS', 'EVR']"}


@srv.tool("Live quotes for one or more tickers: price, daily change, day range, volume, 52-week range and "
          "distance from the 52-week high. Works for stocks, ETFs, indices (^GSPC, ^VIX), FX (EURUSD=X), "
          "futures (CL=F) and crypto (BTC-USD).",
          {"tickers": TICKERS})
def quote(tickers: list):
    return yahoo.many(yahoo.quote, tickers)


@srv.tool("Total-return performance table for one or more tickers: 1W, 1M, 3M, 6M, YTD, 1Y, 3Y, 5Y "
          "(dividend-adjusted), plus 1-year annualized volatility and max drawdown. Use for comparing a peer set.",
          {"tickers": TICKERS})
def performance(tickers: list):
    return yahoo.many(yahoo.performance, tickers)


@srv.tool("Daily/weekly/monthly or intraday price history (OHLC, adjusted close, volume) plus dividends and splits.",
          {"ticker": {"type": "string"},
           "range": {"type": "string", "enum": yahoo.RANGES, "description": "Default 1y"},
           "interval": {"type": "string", "enum": yahoo.INTERVALS,
                        "description": "Default 1d. Intraday intervals only work for short ranges (1m: 5d max)."}})
def price_history(ticker: str, range: str = "1y", interval: str = "1d"):  # noqa: A002 - matches the tool's input name
    c = yahoo.chart(ticker, range, interval)
    ev = c["events"]
    return {"ticker": c["meta"].get("symbol"), "currency": c["meta"].get("currency"), "count": len(c["rows"]),
            "rows": c["rows"],
            "dividends": sorted((v for v in ev.get("dividends", {}).values()), key=lambda d: d["date"]),
            "splits": [v.get("splitRatio") for v in ev.get("splits", {}).values()]}


@srv.tool("Find a ticker from a company name, e.g. 'Lazard' or 'Moelis'.",
          {"query": {"type": "string"}, "limit": {"type": "integer", "description": "Default 8"}})
def search_ticker(query: str, limit: int = 8):
    return yahoo.search(query, limit)


@srv.tool("List a company's SEC filings with direct links. Filter by form, e.g. ['10-K'], ['10-Q','10-K'], "
          "['8-K'] (8-K items: 2.02 = earnings release, 1.01 = material agreement, 5.02 = executive change), "
          "['DEF 14A'] proxy, ['S-1'], ['SC 13D'], ['4'] insider trades.",
          {"ticker": {"type": "string", "description": "Ticker or CIK"},
           "forms": {"type": "array", "items": {"type": "string"}},
           "limit": {"type": "integer", "description": "Default 15"}})
def sec_filings(ticker: str, forms: list | None = None, limit: int = 15):
    return sec.filings(ticker, forms, limit)


@srv.tool("Reported financials from SEC XBRL data for US filers: revenue, gross profit, operating income, D&A, "
          "EBITDA (op. income + D&A), net income, diluted EPS and shares, operating cash flow, capex, free cash "
          "flow, buybacks, dividends, cash, debt, net debt, equity, with margins and revenue growth. "
          "Values in raw USD. Good for comps, model inputs and trend checks.",
          {"ticker": {"type": "string", "description": "Ticker or CIK"},
           "period": {"type": "string", "enum": ["annual", "quarterly"], "description": "Default annual"},
           "count": {"type": "integer", "description": "How many periods, newest first. Default 5"},
           "items": {"type": "array", "items": {"type": "string", "enum": list(sec.LINE_ITEMS)},
                     "description": "Optional subset of line items; default all"}})
def sec_financials(ticker: str, period: str = "annual", count: int = 5, items: list | None = None):
    return sec.financials(ticker, period, count, items)


@srv.tool("Any single XBRL tag's reported history for a company, for line items sec_financials doesn't cover "
          "(e.g. 'InterestAndDividendIncomeOperating' for a bank, 'ShareBasedCompensation', "
          "'ResearchAndDevelopmentExpense'). Use taxonomy 'dei' for 'EntityCommonStockSharesOutstanding'.",
          {"ticker": {"type": "string"}, "tag": {"type": "string"},
           "taxonomy": {"type": "string", "description": "Default us-gaap"},
           "count": {"type": "integer", "description": "Default 12"}})
def sec_concept(ticker: str, tag: str, taxonomy: str = "us-gaap", count: int = 12):
    return sec.concept(ticker, tag, taxonomy, count)


if __name__ == "__main__":
    srv.run()
