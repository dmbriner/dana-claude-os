"""Bank and investment-firm research: new pieces from each firm's own site, and full text of any page or PDF.

Most firms publish a sitemap with a date for every page, so new research shows up without scraping the
site. Firms that block automated requests are marked "tinyfish": this server returns their page URL
and Claude reads it with the TinyFish connector (fetch_content) instead.
"""
from __future__ import annotations

import json
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from http_util import cached, fetch
from text import html_to_text, pdf_to_text, title_of

SOURCES = Path(__file__).resolve().parent / "research.json"
LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>(?:\s*<lastmod>\s*([^<\s]+)\s*</lastmod>)?", re.S)


def load_sources():
    return json.loads(SOURCES.read_text())


def _sitemap_urls(url: str, depth: int = 0, child_filter: str = ""):
    xml = cached(url, hours=6, timeout=30).decode("utf-8", "replace")
    locs = LOC.findall(xml)
    if "<sitemapindex" in xml[:2000] and depth < 2:
        kids = [l for l, _ in locs if not child_filter or re.search(child_filter, l)]
        out = []
        with ThreadPoolExecutor(max_workers=4) as ex:
            for part in ex.map(lambda k: _safe(_sitemap_urls, k, depth + 1, child_filter), kids):
                out += part
        return out
    return locs


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception:
        return []


def _title_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.rstrip("/")
    slug = path.split("/")[-1]
    if slug.lower() in ("transcript.pdf", "report.pdf", "index.html", "index"):
        slug = path.split("/")[-2]
    slug = re.sub(r"\.(html?|pdf)$", "", slug, flags=re.I)
    return re.sub(r"[-_]+", " ", slug).strip().capitalize()


def _section(url: str, src: dict) -> str:
    for pat in src.get("include", []):
        if pat in url:
            rest = url.split(pat, 1)[1].split("/")
            return (pat.strip("/") + ("/" + rest[0] if len(rest) > 1 else "")).strip("/")
    return ""


def firm_research(src: dict, days: int, limit: int):
    if src["method"] == "tinyfish":
        return {"firm": src["firm"], "read_with": "tinyfish", "url": src["url"],
                "note": "This site blocks automated requests. Read the URL with TinyFish fetch_content (links=true)."}
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    inc, exc = src.get("include", []), src.get("exclude", [])
    items = []
    for loc, mod in _sitemap_urls(src["sitemap"], child_filter=src.get("child_sitemaps", "")):
        if not mod or mod[:10] < cutoff:
            continue
        if inc and not any(p in loc for p in inc):
            continue
        if any(p in loc for p in exc):
            continue
        items.append({"title": _title_from_url(loc), "url": loc, "updated": mod[:10],
                      "section": _section(loc, src), "pdf": loc.lower().endswith(".pdf")})
    items.sort(key=lambda x: x["updated"], reverse=True)
    return {"firm": src["firm"], "count": len(items), "items": items[:limit]}


def research(firms: list | None = None, days: int = 7, limit: int = 10, kind: str = "research"):
    """kind: "research" (insights and reports), "deals" (a firm's own transaction announcements), "news" (firm press)."""
    srcs = [s for s in load_sources() if kind in ("all", s.get("kind", "research"))]
    if firms:
        want = [f.lower() for f in firms]
        srcs = [s for s in srcs if any(w in s["firm"].lower() for w in want)]
    with ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(lambda s: _wrap(s, days, limit), srcs))
    return res


def _wrap(src, days, limit):
    try:
        return firm_research(src, days, limit)
    except Exception as e:
        return {"firm": src["firm"], "error": f"{type(e).__name__}: {e}"[:160],
                "fallback": "Read the firm's research page with TinyFish fetch_content", "url": src.get("url", "")}


def read_document(url: str, max_chars: int = 20000):
    """Plain text of a web page or PDF (research piece, press release, filing, firm 'about' page)."""
    data = fetch(url, timeout=30)
    is_pdf = data[:5] == b"%PDF-" or url.lower().split("?")[0].endswith(".pdf")
    if is_pdf:
        body, title = pdf_to_text(data), _title_from_url(url)
    else:
        page = data.decode("utf-8", "replace")
        body, title = html_to_text(page), title_of(page)
    out = {"url": url, "title": title, "type": "pdf" if is_pdf else "html", "chars": len(body),
           "text": body[:max_chars], "truncated": len(body) > max_chars}
    if len(body) < 500:
        out["note"] = "Little text came back; the page probably needs a browser. Read it with TinyFish fetch_content."
    return out
