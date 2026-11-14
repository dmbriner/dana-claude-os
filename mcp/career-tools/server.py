"""career-tools: an MCP server for finance recruiting.

Jobs straight from target firms' careers feeds (with full descriptions), the SimplifyJobs list, market and
deal news, bank research, Federal Reserve releases, FRED and Treasury data, and full text of any page or PDF.
Run: python3 -I server.py   (Claude Code launches it; see README.md)
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # -I drops the script dir; add it back explicitly

import feeds  # noqa: E402
import jobs  # noqa: E402
import research  # noqa: E402
from mcp_stdio import Server  # noqa: E402

FIRMS = HERE / "firms.json"
CACHE = Path(os.environ.get("CAREER_TOOLS_CACHE", HERE.parents[1] / "private" / "cache" / "jobs-seen.json"))

srv = Server("career-tools", "0.2.0")

BROWSER_NOTE = ("These firms' careers sites only render in a browser: read each careers_url with TinyFish "
                "fetch_content (links=true), then call job_details on any posting link.")


def load_firms():
    return json.loads(FIRMS.read_text())


def pick(firms, names):
    if not names:
        return firms
    want = [n.lower() for n in names]
    return [f for f in firms if any(w in f["name"].lower() for w in want)]


@srv.tool("List the target firms this server checks, with category and job system.",
          {"category": {"type": "string", "description": "Optional filter, e.g. 'Regional bank'"}})
def list_firms(category: str = ""):
    fs = [f for f in load_firms() if category.lower() in f["category"].lower()]
    return [{"name": f["name"], "category": f["category"], "ats": f["ats"]} for f in fs]


@srv.tool("Search current job postings at the target firms, read live from each firm's careers feed. "
          "By default returns only student programs (internships, summer analyst, sophomore/insight programs).",
          {"query": {"type": "string", "description": "Words that must all appear in the title or location, e.g. 'restructuring new york'"},
           "firms": {"type": "array", "items": {"type": "string"}, "description": "Optional firm names (partial match); default all"},
           "category": {"type": "string", "description": "Optional category filter"},
           "student_only": {"type": "boolean", "description": "Default true"}})
def search_jobs(query: str = "", firms: list | None = None, category: str = "", student_only: bool = True):
    fs = [f for f in pick(load_firms(), firms) if category.lower() in f["category"].lower()]
    found, errors, browser = jobs.many(fs, student_only)
    words = query.lower().split()
    found = [j for j in found if all(w in (j["title"] + " " + j["location"]).lower() for w in words)]
    out = {"count": len(found), "firms_checked": len(fs), "jobs": found, "errors": errors}
    if browser:
        out.update(needs_browser=browser, needs_browser_note=BROWSER_NOTE)
    return out


@srv.tool("Return student postings that appeared since the last time this was run (first run marks everything as seen "
          "and returns it all). Use for the daily careers check.",
          {"firms": {"type": "array", "items": {"type": "string"}}})
def new_postings(firms: list | None = None):
    seen = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    found, errors, browser = jobs.many(pick(load_firms(), firms))
    today = date.today().isoformat()
    new = [j for j in found if j["url"] not in seen]
    for j in new:
        seen[j["url"]] = today
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(seen, indent=0))
    out = {"new": len(new), "jobs": new, "errors": errors}
    if browser:
        out.update(needs_browser=browser, needs_browser_note=BROWSER_NOTE)
    return out


@srv.tool("Full details for one job posting: complete description, location, posted and closing dates, any deadline "
          "sentences, and the apply link. Works for Workday, Greenhouse, Lever, Ashby, SmartRecruiters, and Oracle links; "
          "other links get a best-effort page read.",
          {"url": {"type": "string", "description": "The posting URL from search_jobs, new_postings, or simplify_jobs"}})
def job_details(url: str):
    return jobs.job_details(url)


@srv.tool("Search the SimplifyJobs community internship list (thousands of companies, updated daily). It is mostly "
          "tech, so finance_only keeps finance-looking titles; it fills gaps like Goldman Sachs, whose own site needs a browser.",
          {"query": {"type": "string", "description": "Words that must all appear in company, title, or location"},
           "company": {"type": "string", "description": "Optional company name (partial match)"},
           "finance_only": {"type": "boolean", "description": "Default true"},
           "year": {"type": "integer", "description": "Internship summer, default 2027"},
           "limit": {"type": "integer", "description": "Default 50"}})
def simplify_jobs(query: str = "", company: str = "", finance_only: bool = True, year: int = 2027, limit: int = 50):
    rows = jobs.simplify(query, company, finance_only, year, limit)
    return {"count": len(rows), "jobs": rows}


@srv.tool("Add a firm by pasting its careers-page URL. Detects Workday, Greenhouse, Lever, Ashby, or SmartRecruiters "
          "automatically, tests the feed, and saves it.",
          {"name": {"type": "string"}, "careers_url": {"type": "string"},
           "category": {"type": "string", "description": "e.g. 'Elite boutique', 'Hedge fund', 'Private equity / alternatives'"}})
def add_firm(name: str, careers_url: str, category: str = "Other"):
    ats, board = jobs.detect(careers_url)
    firm = {"name": name, "category": category, "ats": ats, "board": board}
    test = jobs.firm_jobs(firm, student_only=False)  # raises if the feed doesn't work
    fs = [f for f in load_firms() if f["name"].lower() != name.lower()] + [firm]
    FIRMS.write_text(json.dumps(fs, indent=1, ensure_ascii=False) + "\n")
    student = [j for j in test if jobs.STUDENT.search(j["title"])]
    return {"added": firm, "total_postings_seen": len(test), "student_postings": student[:10],
            "note": "html = generic page scan; less reliable than an API feed" if ats == "html" else ""}


@srv.tool("Federal Reserve releases from federalreserve.gov RSS feeds.",
          {"kind": {"type": "string", "enum": ["press", "monetary", "speeches", "testimony", "h41", "all"]},
           "days": {"type": "number", "description": "Look back this many days (default 3)"}})
def fed_releases(kind: str = "all", days: float = 3):
    return feeds.fed(kind, days)


@srv.tool("Latest values of an economic data series from FRED (St. Louis Fed). Common IDs: DGS2, DGS10 (Treasury yields), "
          "T10Y2Y (2s10s spread), FEDFUNDS, SOFR, CPIAUCSL (CPI), UNRATE, PAYEMS (payrolls), BAMLH0A0HYM2 (HY spread), "
          "BAMLC0A0CM (IG spread), VIXCLS, DCOILWTICO (WTI).",
          {"series_id": {"type": "string"}, "points": {"type": "integer", "description": "Default 10"}})
def econ_series(series_id: str, points: int = 10):
    return feeds.fred(series_id, points)


@srv.tool("Official daily Treasury yield curve (1 month to 30 years), most recent days first.",
          {"days": {"type": "integer", "description": "Default 5"}})
def treasury_yields(days: int = 5):
    return feeds.treasury_yields(days)


@srv.tool("Search recent news (Google News). Good for firm news, deals, and topics like 'continuation vehicle'.",
          {"query": {"type": "string"}, "days": {"type": "integer", "description": "Default 2"},
           "limit": {"type": "integer", "description": "Default 15"}})
def search_news(query: str, days: int = 2, limit: int = 15):
    return feeds.news(query, days, limit)


@srv.tool("Recent news for target firms, one search per firm.",
          {"firms": {"type": "array", "items": {"type": "string"}, "description": "Default: all target firms"},
           "days": {"type": "integer", "description": "Default 2"}})
def firm_news(firms: list | None = None, days: int = 2):
    out = {}
    for f in pick(load_firms(), firms):
        items = feeds.news(f'"{f["name"]}"', days, 5)
        if items:
            out[f["name"]] = items
    return out


@srv.tool("Market headlines with links, by source. Sources: nyt_business, nyt_dealbook, ft_markets, ft_companies, "
          "yahoo_finance, wsj, reuters (WSJ and Reuters come through Google News). Links open with the reader's own logins.",
          {"sources": {"type": "array", "items": {"type": "string"}, "description": "Default: all"},
           "days": {"type": "number", "description": "Look back this many days (default 1)"},
           "limit": {"type": "integer", "description": "Per source, default 10"}})
def market_news(sources: list | None = None, days: float = 1, limit: int = 10):
    return feeds.market_news(sources, days, limit)


@srv.tool("Yahoo Finance headlines for one ticker.",
          {"ticker": {"type": "string"}, "days": {"type": "number", "description": "Default 3"},
           "limit": {"type": "integer", "description": "Default 15"}})
def ticker_news(ticker: str, days: float = 3, limit: int = 15):
    return feeds.ticker_news(ticker, days, limit)


@srv.tool("Recent deal announcements: the PR Newswire M&A wire, deal headlines from the press, and new SEC filings "
          "that contain a merger agreement.",
          {"days": {"type": "number", "description": "Default 2"}, "limit": {"type": "integer", "description": "Per section, default 25"},
           "include_filings": {"type": "boolean", "description": "Default true"}})
def recent_deals(days: float = 2, limit: int = 25, include_filings: bool = True):
    return feeds.recent_deals(days, limit, include_filings)


@srv.tool("Deals a firm advised on or did recently. Combines news coverage with the firm's own transaction "
          "announcements where it publishes them (Evercore). Use for coffee chat prep.",
          {"firm": {"type": "string"}, "days": {"type": "integer", "description": "Default 120"},
           "limit": {"type": "integer", "description": "Default 15"}})
def firm_deals(firm: str, days: int = 120, limit: int = 15):
    out = {"news": feeds.firm_deals(firm, days, limit)}
    own = research.research([firm], days, limit, kind="deals")
    if own:
        out["firm_announcements"] = own
    return out


@srv.tool("SEC EDGAR full-text search over filings, e.g. 'agreement and plan of merger' or a company name.",
          {"query": {"type": "string", "description": "Exact phrase to find"},
           "forms": {"type": "string", "description": "Comma-separated form types, default 8-K"},
           "days": {"type": "integer", "description": "Default 7"}, "limit": {"type": "integer", "description": "Default 20"}})
def sec_filings(query: str, forms: str = "8-K", days: int = 7, limit: int = 20):
    return feeds.edgar_search(query, forms, days, limit)


@srv.tool("New research and insights from banks and investment firms' own sites (Goldman Sachs, JPMorgan, Morgan "
          "Stanley, PIMCO, Apollo, BofA Institute, and more). Each item has a link; PDFs are flagged. Firms marked "
          "read_with=tinyfish block automated requests: read their url with TinyFish fetch_content. kind='news' "
          "returns firm press releases (Evercore, Moelis, PJT) instead.",
          {"firms": {"type": "array", "items": {"type": "string"}, "description": "Default: all research sources"},
           "days": {"type": "integer", "description": "Look back this many days (default 7)"},
           "limit": {"type": "integer", "description": "Per firm, default 10"},
           "kind": {"type": "string", "enum": ["research", "news", "deals", "all"]}})
def bank_research(firms: list | None = None, days: int = 7, limit: int = 10, kind: str = "research"):
    return research.research(firms, days, limit, kind)


@srv.tool("Full text of a web page or PDF: a research piece, press release, filing, or a firm's 'about' or group page. "
          "If little text comes back the page needs a browser; use TinyFish fetch_content.",
          {"url": {"type": "string"}, "max_chars": {"type": "integer", "description": "Default 20000"}})
def read_document(url: str, max_chars: int = 20000):
    return research.read_document(url, max_chars)


if __name__ == "__main__":
    srv.run()
