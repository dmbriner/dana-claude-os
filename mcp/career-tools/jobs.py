"""Fetch job postings straight from firms' public applicant-tracking-system (ATS) feeds.

Each adapter returns a list of {"title", "location", "url", "posted"} dicts. The approach (public
CXS/board APIs, one adapter per ATS) follows freehire (https://github.com/strelov1/freehire, MIT).
"""
from __future__ import annotations

import html
import json
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from http_util import fetch, get_json

# Words that mark a student / early-careers posting.
STUDENT = re.compile(
    r"\b(intern(ship)?s?|summer|sophomore|freshman|first[- ]year|insight|discovery|early careers?|"
    r"campus|undergrad(uate)?|launchpad|2027|2028|off[- ]cycle|co-?op|spring week|programme|program)\b",
    re.I,
)
SENIOR = re.compile(r"\b(vice president|vp|director|managing director|senior|principal|associate director|lead)\b", re.I)


def greenhouse(board: str):
    d = get_json(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs")
    return [
        {"title": j["title"], "location": (j.get("location") or {}).get("name", ""),
         "url": j["absolute_url"], "posted": j.get("updated_at", "")[:10]}
        for j in d.get("jobs", [])
    ]


def lever(board: str):
    d = get_json(f"https://api.lever.co/v0/postings/{board}?mode=json")
    return [
        {"title": j["text"], "location": (j.get("categories") or {}).get("location", ""),
         "url": j["hostedUrl"], "posted": ""}
        for j in d
    ]


def ashby(board: str):
    d = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}")
    return [
        {"title": j["title"], "location": j.get("location", ""), "url": j["jobUrl"],
         "posted": (j.get("publishedAt") or "")[:10]}
        for j in d.get("jobs", [])
    ]


def smartrecruiters(board: str):
    d = get_json(f"https://api.smartrecruiters.com/v1/companies/{board}/postings?limit=100&q=intern")
    return [
        {"title": j["name"], "location": (j.get("location") or {}).get("city", ""),
         "url": f"https://jobs.smartrecruiters.com/{board}/{j['id']}", "posted": (j.get("releasedDate") or "")[:10]}
        for j in d.get("content", [])
    ]


class SiteDown(Exception):
    pass


def workday(board: str):
    """board = "<tenant>.wdN.myworkdayjobs.com/<site>". Searches student keywords, since big banks list thousands of jobs."""
    host, site = board.split("/", 1)
    tenant = host.split(".")[0]
    api = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    seen, out = set(), []
    for term in ("intern", "summer analyst", "analyst program", "early careers"):
        for offset in range(0, 100, 20):
            raw = fetch(api, {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": term})
            if raw.lstrip()[:1] == b"<":
                raise SiteDown("Workday is down for maintenance right now; try again later")
            d = json.loads(raw)
            posts = d.get("jobPostings") or []
            for j in posts:
                path = j.get("externalPath", "")
                if path in seen:
                    continue
                seen.add(path)
                out.append({"title": j.get("title", ""), "location": j.get("locationsText", ""),
                            "url": f"https://{host}/{site}{path}", "posted": j.get("postedOn", "")})
            if len(posts) < 20:
                break
    return out


def html_links(url: str):
    """Fallback for career pages without an API (e.g. tal.net boards): pull job-looking links."""
    page = fetch(url).decode("utf-8", "replace")
    out, seen = [], set()
    for href, text in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S | re.I):
        title = html.unescape(re.sub(r"<[^>]+>", " ", text)).strip()
        title = re.sub(r"\s+", " ", title)
        if len(title) < 8 or not re.search(r"analyst|intern|summer|associate|program", title, re.I):
            continue
        full = urllib.parse.urljoin(url, html.unescape(href))
        if full in seen:
            continue
        seen.add(full)
        out.append({"title": title, "location": "", "url": full, "posted": ""})
    return out


ADAPTERS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby,
            "smartrecruiters": smartrecruiters, "workday": workday, "html": html_links}


def detect(careers_url: str):
    """Work out (ats, board) from a careers-page URL so adding a firm is one step."""
    u = urllib.parse.urlparse(careers_url if "://" in careers_url else "https://" + careers_url)
    host, parts = u.netloc.lower(), [p for p in u.path.split("/") if p]
    if "myworkdayjobs.com" in host:
        site = next((p for p in parts if not re.fullmatch(r"[a-z]{2}-[A-Z]{2}|[a-z]{2}-[a-z]{2}", p) and p != "wday"), "")
        if parts[:1] == ["wday"]:  # already a cxs URL: /wday/cxs/<tenant>/<site>/jobs
            site = parts[3]
        return "workday", f"{u.netloc}/{site}"
    if "greenhouse.io" in host:
        b = parse_q(u, "for") or (parts[0] if parts else "")
        if parts[:2] == ["v1", "boards"]:
            b = parts[2]
        return "greenhouse", b
    if "lever.co" in host:
        return "lever", parts[-2] if parts[:1] == ["v0"] else parts[0]
    if "ashbyhq.com" in host:
        return "ashby", parts[-1] if "posting-api" in parts else parts[0]
    if "smartrecruiters.com" in host:
        return "smartrecruiters", parts[0]
    return "html", careers_url


def parse_q(u, key):
    return (urllib.parse.parse_qs(u.query).get(key) or [""])[0]


def firm_jobs(firm: dict, student_only: bool = True):
    jobs = ADAPTERS[firm["ats"]](firm["board"])
    if student_only:
        jobs = [j for j in jobs if STUDENT.search(j["title"]) and not SENIOR.search(j["title"])]
    if firm.get("title_filter"):  # e.g. finance-only roles at a luxury house
        keep = re.compile(firm["title_filter"], re.I)
        jobs = [j for j in jobs if keep.search(j["title"])]
    for j in jobs:
        j["firm"] = firm["name"]
    return jobs


def many(firms: list, student_only: bool = True):
    """Check firms in parallel (6 at a time). Returns (jobs, errors)."""
    jobs, errors = [], {}

    def one(f):
        try:
            return f["name"], firm_jobs(f, student_only), None
        except Exception as e:
            return f["name"], [], f"{type(e).__name__}: {e}"[:160]

    with ThreadPoolExecutor(max_workers=6) as ex:
        for name, js, err in ex.map(one, firms):
            jobs += js
            if err:
                errors[name] = err
    return jobs, errors
