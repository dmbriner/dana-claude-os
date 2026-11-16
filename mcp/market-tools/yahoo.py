"""Yahoo Finance public chart and search endpoints (the same data yfinance reads), on urllib only."""
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) market-tools/0.1"
BASE = "https://query1.finance.yahoo.com"
RANGES = ["1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"]
INTERVALS = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]


def _get(path: str, params: dict) -> dict:
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def chart(ticker: str, range_: str = "1y", interval: str = "1d") -> dict:
    data = _get(f"/v8/finance/chart/{urllib.parse.quote(ticker.upper())}",
                {"range": range_, "interval": interval, "includePrePost": "false", "events": "div,split"})
    err = data.get("chart", {}).get("error")
    if err:
        raise ValueError(f"{ticker}: {err.get('description') or err}")
    res = data["chart"]["result"][0]
    q = (res.get("indicators", {}).get("quote") or [{}])[0]
    adj = (res.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose")
    rows = []
    for i, ts in enumerate(res.get("timestamp") or []):
        close = (q.get("close") or [None])[i]
        if close is None:
            continue
        rows.append({
            "date": datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d" if interval in ("1d", "1wk", "1mo") else "%Y-%m-%d %H:%M"),
            "open": _r(q["open"][i]), "high": _r(q["high"][i]), "low": _r(q["low"][i]),
            "close": _r(close), "adj_close": _r(adj[i]) if adj else _r(close), "volume": q["volume"][i],
        })
    return {"meta": res["meta"], "rows": rows, "events": res.get("events", {})}


def quote(ticker: str) -> dict:
    c = chart(ticker, "1y", "1d")
    m, rows = c["meta"], c["rows"]
    price, prev = m.get("regularMarketPrice"), m.get("chartPreviousClose")
    # chartPreviousClose is the close before the 1y window; yesterday's close is the second-to-last row
    if len(rows) >= 2:
        prev = rows[-2]["close"] if rows[-1]["date"] == _today(m) else rows[-1]["close"]
    return {
        "ticker": m.get("symbol"), "name": m.get("longName") or m.get("shortName"),
        "exchange": m.get("fullExchangeName"), "currency": m.get("currency"),
        "price": _r(price), "prev_close": _r(prev),
        "change": _r(price - prev) if price and prev else None,
        "change_pct": _pct(price, prev),
        "day_low": _r(m.get("regularMarketDayLow")), "day_high": _r(m.get("regularMarketDayHigh")),
        "volume": m.get("regularMarketVolume"),
        "52w_low": _r(m.get("fiftyTwoWeekLow")), "52w_high": _r(m.get("fiftyTwoWeekHigh")),
        "pct_off_52w_high": _pct(price, m.get("fiftyTwoWeekHigh")),
        "as_of": datetime.fromtimestamp(m["regularMarketTime"], timezone.utc).isoformat() if m.get("regularMarketTime") else None,
    }


def performance(ticker: str) -> dict:
    """Total returns (dividend-adjusted) over standard windows, plus 1y volatility and max drawdown."""
    c = chart(ticker, "5y", "1d")
    rows = c["rows"]
    if not rows:
        raise ValueError(f"{ticker}: no price history")
    last = rows[-1]
    end = datetime.strptime(last["date"], "%Y-%m-%d")

    def back(days=None, ytd=False):
        if ytd:
            target = datetime(end.year - 1, 12, 31)
        else:
            target = end.fromordinal(end.toordinal() - days)
        prior = [r for r in rows if datetime.strptime(r["date"], "%Y-%m-%d") <= target]
        return _pct(last["adj_close"], prior[-1]["adj_close"]) if prior else None

    yr = [r["adj_close"] for r in rows if datetime.strptime(r["date"], "%Y-%m-%d") >= end.fromordinal(end.toordinal() - 365)]
    rets = [math.log(b / a) for a, b in zip(yr, yr[1:]) if a and b]
    vol = None
    if len(rets) > 20:
        mean = sum(rets) / len(rets)
        vol = round(math.sqrt(sum((x - mean) ** 2 for x in rets) / (len(rets) - 1)) * math.sqrt(252) * 100, 1)
    peak, mdd = 0.0, 0.0
    for p in yr:
        peak = max(peak, p)
        mdd = min(mdd, p / peak - 1)
    return {
        "ticker": c["meta"].get("symbol"), "price": last["close"], "as_of": last["date"],
        "1w_%": back(7), "1m_%": back(30), "3m_%": back(91), "6m_%": back(182), "ytd_%": back(ytd=True),
        "1y_%": back(365), "3y_%": back(365 * 3), "5y_%": back(365 * 5 - 5),
        "1y_vol_%": vol, "1y_max_drawdown_%": round(mdd * 100, 1),
    }


def search(query: str, limit: int = 8) -> list:
    data = _get("/v1/finance/search", {"q": query, "quotesCount": limit, "newsCount": 0})
    return [{"ticker": q.get("symbol"), "name": q.get("longname") or q.get("shortname"),
             "type": q.get("typeDisp"), "exchange": q.get("exchDisp"),
             "sector": q.get("sectorDisp"), "industry": q.get("industryDisp")}
            for q in data.get("quotes", [])]


def many(fn, tickers: list) -> dict:
    """Run fn over tickers in parallel; return successes and per-ticker errors."""
    out, errors = [], {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {t: ex.submit(fn, t) for t in tickers}
        for t, f in futs.items():
            try:
                out.append(f.result())
            except Exception as e:
                errors[t] = str(e)
    return {"results": out, "errors": errors}


def _today(meta) -> str:
    t = meta.get("regularMarketTime")
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") if t else ""


def _r(x, n=2):
    return round(x, n) if isinstance(x, (int, float)) else None


def _pct(a, b):
    return round((a / b - 1) * 100, 2) if a and b else None
