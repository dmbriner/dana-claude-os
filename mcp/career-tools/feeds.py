"""Free news and macro sources: Federal Reserve RSS feeds, FRED data, and Google News search."""
from __future__ import annotations

import csv
import email.utils
import io
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from http_util import fetch

FED_FEEDS = {
    "press": "https://www.federalreserve.gov/feeds/press_all.xml",
    "monetary": "https://www.federalreserve.gov/feeds/press_monetary.xml",
    "speeches": "https://www.federalreserve.gov/feeds/speeches.xml",
    "testimony": "https://www.federalreserve.gov/feeds/testimony.xml",
    "h41": "https://www.federalreserve.gov/feeds/h41.xml",
}


def _when(s: str):
    try:
        d = email.utils.parsedate_to_datetime(s)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def rss(url: str, days: float, limit: int):
    root = ET.fromstring(fetch(url))
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out = []
    for it in root.iter("item"):
        when = _when(it.findtext("pubDate") or "")
        if when and when < cutoff:
            continue
        src = it.find("source")
        out.append({
            "title": (it.findtext("title") or "").strip(),
            "url": (it.findtext("link") or "").strip(),
            "date": when.strftime("%Y-%m-%d %H:%M UTC") if when else "",
            "source": src.text if src is not None else "",
        })
        if len(out) >= limit:
            break
    return out


def fed(kind: str = "press", days: float = 3, limit: int = 20):
    kinds = list(FED_FEEDS) if kind == "all" else [kind]
    out = []
    for k in kinds:
        for item in rss(FED_FEEDS[k], days, limit):
            item["feed"] = k
            out.append(item)
    return sorted(out, key=lambda x: x["date"], reverse=True)[:limit]


def fred(series_id: str, points: int = 10):
    """Latest observations of a FRED series via the public graph CSV (no API key needed)."""
    raw = fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={urllib.parse.quote(series_id)}", curl_first=True).decode()
    rows = [r for r in csv.reader(io.StringIO(raw))][1:]
    rows = [r for r in rows if len(r) == 2 and r[1] not in (".", "")]
    return {"series": series_id, "source": f"https://fred.stlouisfed.org/series/{series_id}",
            "observations": [{"date": d, "value": float(v)} for d, v in rows[-points:]]}


def news(query: str, days: int = 2, limit: int = 15):
    q = urllib.parse.quote(f"{query} when:{days}d")
    items = rss(f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en", days + 1, limit)
    for it in items:  # Google titles end with " - Source"; keep the source separately
        it["title"] = re.sub(r"\s+-\s+[^-]+$", "", it["title"]) if it["source"] else it["title"]
    return items


def treasury_yields(days: int = 5):
    """Daily Treasury par yield curve from home.treasury.gov (official, no key)."""
    from datetime import date
    y = date.today().year
    url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
           f"{y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={y}&page&_format=csv")
    rows = list(csv.DictReader(io.StringIO(fetch(url).decode())))
    return {"source": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve",
            "rows": rows[:days]}


# ---------- market news: headlines with links (open them with your own logins) ----------

NEWS = {
    "nyt_business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "nyt_dealbook": "https://rss.nytimes.com/services/xml/rss/nyt/DealBook.xml",
    "ft_markets": "https://www.ft.com/markets?format=rss",
    "ft_companies": "https://www.ft.com/companies?format=rss",
    # Yahoo retired its general feed; headlines on the S&P 500, Dow, and Nasdaq stand in for market news.
    "yahoo_finance": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC,%5EDJI,%5EIXIC&region=US&lang=en-US",
    # WSJ's own RSS stopped updating in Jan 2025; Reuters ended public RSS. Google News still indexes both.
    "wsj": "gnews:site:wsj.com (markets OR deal OR stocks OR bonds OR Fed)",
    "reuters": "gnews:site:reuters.com (markets OR deal OR merger OR stocks)",
}


def _gnews_url(q: str) -> str:
    return f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=en-US&gl=US&ceid=US:en"


def market_news(sources: list | None = None, days: float = 1, limit: int = 10):
    """Headlines per source. Returns {source: [items]} plus {"errors": {...}}."""
    out, errors = {}, {}
    for name in sources or list(NEWS):
        src = NEWS.get(name)
        if not src:
            errors[name] = f"unknown source; choose from {sorted(NEWS)}"
            continue
        url = _gnews_url(src[6:] + f" when:{max(1, int(days))}d") if src.startswith("gnews:") else src
        try:
            out[name] = rss(url, days + 0.5, limit)
        except Exception as e:
            errors[name] = f"{type(e).__name__}: {e}"[:160]
    if errors:
        out["errors"] = errors
    return out


def ticker_news(ticker: str, days: float = 3, limit: int = 15):
    """Yahoo Finance headlines for one ticker."""
    t = urllib.parse.quote(ticker.upper())
    return rss(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={t}&region=US&lang=en-US", days, limit)


# ---------- deals ----------

PRN_MA = "https://www.prnewswire.com/rss/financial-services-latest-news/acquisitions-mergers-and-takeovers-list.rss"
EDGAR_FTS = "https://efts.sec.gov/LATEST/search-index?q={q}&forms={forms}&dateRange=custom&startdt={start}&enddt={end}"


def edgar_search(query: str, forms: str = "8-K", days: int = 7, limit: int = 20):
    """SEC EDGAR full-text search (filings since 2001). Good for merger agreements and deal announcements."""
    from http_util import get_json
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    url = EDGAR_FTS.format(q=urllib.parse.quote(f'"{query}"'), forms=forms, start=start, end=end)
    hits = get_json(url).get("hits", {}).get("hits", [])
    out = []
    for h in hits[:limit]:
        s = h.get("_source", {})
        cik = (s.get("ciks") or [""])[0].lstrip("0")
        adsh = h.get("_id", "").split(":")[0]
        out.append({"company": "; ".join(s.get("display_names", [])), "form": s.get("form"), "filed": s.get("file_date"),
                    "items": s.get("items"),
                    "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{h['_id'].split(':')[1]}"
                    if cik and ":" in h.get("_id", "") else ""})
    return out


def recent_deals(days: float = 2, limit: int = 25, include_filings: bool = True):
    """Deal announcements: PR Newswire M&A wire, deal headlines from the press, and new SEC merger agreements."""
    out = {"press_releases": rss(PRN_MA, days, limit),
           "headlines": rss(_gnews_url(f'(acquire OR acquisition OR merger OR "to buy" OR "take private") '
                                       f'(billion OR million) when:{max(1, int(days))}d'), days + 0.5, limit)}
    if include_filings:
        try:
            out["sec_merger_agreements"] = edgar_search("agreement and plan of merger", "8-K", max(2, int(days) + 1), limit)
        except Exception as e:
            out["sec_merger_agreements"] = {"error": f"{type(e).__name__}: {e}"[:160]}
    return out


def firm_deals(firm: str, days: int = 120, limit: int = 15):
    """Recent deals a firm advised on or did: news where it appears as adviser, buyer, or seller."""
    q = (f'"{firm}" (advised OR adviser OR advisor OR "financial advisor" OR acquires OR acquisition OR '
         f'merger OR IPO OR "take private" OR financing) when:{days}d')
    return rss(_gnews_url(q), days + 1, limit)
