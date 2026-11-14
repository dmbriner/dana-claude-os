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
