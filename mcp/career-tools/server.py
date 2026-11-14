"""career-tools: an MCP server for finance recruiting.

Jobs straight from target firms' careers feeds, Federal Reserve releases, FRED data, and news search.
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
from mcp_stdio import Server  # noqa: E402

FIRMS = HERE / "firms.json"
CACHE = Path(os.environ.get("CAREER_TOOLS_CACHE", HERE.parents[1] / "private" / "cache" / "jobs-seen.json"))

srv = Server("career-tools", "0.1.0")


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
    found, errors = jobs.many(fs, student_only)
    words = query.lower().split()
    found = [j for j in found if all(w in (j["title"] + " " + j["location"]).lower() for w in words)]
    return {"count": len(found), "firms_checked": len(fs), "jobs": found, "errors": errors}


@srv.tool("Return student postings that appeared since the last time this was run (first run marks everything as seen "
          "and returns it all). Use for the daily careers check.",
          {"firms": {"type": "array", "items": {"type": "string"}}})
def new_postings(firms: list | None = None):
    seen = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    found, errors = jobs.many(pick(load_firms(), firms))
    today = date.today().isoformat()
    new = [j for j in found if j["url"] not in seen]
    for j in new:
        seen[j["url"]] = today
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(seen, indent=0))
    return {"new": len(new), "jobs": new, "errors": errors}


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


if __name__ == "__main__":
    srv.run()
