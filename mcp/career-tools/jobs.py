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

from http_util import cached, fetch, get_json
from text import deadlines, html_to_text, title_of

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


def oracle(board: str):
    """Oracle Recruiting Cloud (JPMorgan). board = "<host>.fa.oraclecloud.com/<siteNumber>"."""
    host, site = board.split("/", 1)
    seen, out = set(), []
    for term in ("intern", "summer analyst", "analyst program", "early careers"):
        q = urllib.parse.quote(f'"{term}"')
        api = (f"https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList"
               f"&finder=findReqs;siteNumber={site},keyword={q},limit=50,offset=0")
        for r in (get_json(api).get("items") or [{}])[0].get("requisitionList", []):
            if r["Id"] in seen:
                continue
            seen.add(r["Id"])
            out.append({"title": r["Title"], "location": r.get("PrimaryLocation", ""),
                        "url": f"https://{host}/hcmUI/CandidateExperience/en/sites/{site}/job/{r['Id']}",
                        "posted": r.get("PostedDate", "")})
    return out


class NeedsBrowser(Exception):
    """The firm's careers site only renders in a browser. Read it with TinyFish (fetch_content) instead."""


def browser_only(url: str):
    raise NeedsBrowser(url)


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
            "smartrecruiters": smartrecruiters, "workday": workday, "oracle": oracle, "html": html_links,
            "tinyfish": browser_only}


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
    if "oraclecloud.com" in host and "sites" in parts:
        return "oracle", f"{u.netloc}/{parts[parts.index('sites') + 1]}"
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
    """Check firms in parallel (6 at a time). Returns (jobs, errors, needs_browser)."""
    jobs, errors, browser = [], {}, []

    def one(f):
        try:
            return f, firm_jobs(f, student_only), None
        except NeedsBrowser as e:
            return f, [], e
        except Exception as e:
            return f, [], f"{type(e).__name__}: {e}"[:160]

    with ThreadPoolExecutor(max_workers=6) as ex:
        for f, js, err in ex.map(one, firms):
            jobs += js
            if isinstance(err, NeedsBrowser):
                browser.append({"firm": f["name"], "careers_url": str(err)})
            elif err:
                errors[f["name"]] = err
    return jobs, errors, browser


# ---------- full posting details ----------

def _clean(h: str) -> str:
    return html_to_text(html.unescape(h or ""))


def job_details(url: str) -> dict:
    """Full description, dates, and apply link for one posting URL, read from the job system's own API."""
    u = urllib.parse.urlparse(url)
    host, parts = u.netloc.lower(), [p for p in u.path.split("/") if p]
    d = {"url": url, "apply_url": url}
    if "myworkdayjobs.com" in host:
        if parts and re.fullmatch(r"[a-z]{2}-[A-Za-z]{2}", parts[0]):
            parts = parts[1:]
        site, rest = parts[0], "/".join(parts[1:])
        info = get_json(f"https://{u.netloc}/wday/cxs/{host.split('.')[0]}/{site}/{rest}")["jobPostingInfo"]
        d.update(title=info.get("title"), location=info.get("location"), posted=info.get("startDate"),
                 closes=info.get("endDate"), time_type=info.get("timeType"),
                 apply_url=info.get("externalUrl") or url, description=_clean(info.get("jobDescription")))
    elif "greenhouse.io" in host:
        board = parse_q(u, "for") or parts[0]
        jid = parse_q(u, "gh_jid") or parts[parts.index("jobs") + 1]
        j = get_json(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{jid}")
        d.update(title=j.get("title"), location=(j.get("location") or {}).get("name"),
                 posted=(j.get("first_published") or j.get("updated_at") or "")[:10],
                 apply_url=j.get("absolute_url") or url, description=_clean(j.get("content")))
    elif "lever.co" in host:
        j = get_json(f"https://api.lever.co/v0/postings/{parts[0]}/{parts[1]}")
        lists = "\n\n".join(f"{x['text']}\n" + html_to_text(x.get("content", "")) for x in j.get("lists", []))
        d.update(title=j.get("text"), location=(j.get("categories") or {}).get("location"),
                 apply_url=j.get("applyUrl") or url,
                 description="\n\n".join(filter(None, [j.get("descriptionPlain"), lists, j.get("additionalPlain")])))
    elif "ashbyhq.com" in host:
        board, jid = parts[0], parts[1]
        j = next(x for x in get_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}")["jobs"]
                 if x["jobUrl"].rstrip("/").endswith(jid) or x.get("id") == jid)
        d.update(title=j["title"], location=j.get("location"), posted=(j.get("publishedAt") or "")[:10],
                 apply_url=j.get("applyUrl") or url, description=j.get("descriptionPlain") or _clean(j.get("descriptionHtml")))
    elif "smartrecruiters.com" in host:
        j = get_json(f"https://api.smartrecruiters.com/v1/companies/{parts[0]}/postings/{parts[1].split('-')[0]}")
        secs = (j.get("jobAd") or {}).get("sections") or {}
        d.update(title=j.get("name"), location=(j.get("location") or {}).get("city"), posted=(j.get("releasedDate") or "")[:10],
                 description="\n\n".join(_clean(v.get("text")) for v in secs.values() if isinstance(v, dict)))
    elif "oraclecloud.com" in host and "job" in parts:
        site, jid = parts[parts.index("sites") + 1], parts[parts.index("job") + 1]
        j = get_json(f"https://{u.netloc}/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true"
                     f"&finder=ById;Id=%22{jid}%22,siteNumber={site}")["items"][0]
        body = "\n\n".join(_clean(j.get(k)) for k in ("ExternalDescriptionStr", "ExternalResponsibilitiesStr",
                                                         "ExternalQualificationsStr", "CorporateDescriptionStr") if j.get(k))
        d.update(title=j.get("Title"), location=j.get("PrimaryLocation"), posted=(j.get("ExternalPostedStartDate") or "")[:10],
                 closes=(j.get("ExternalPostedEndDate") or "")[:10] or None, description=body)
    else:
        page = fetch(url).decode("utf-8", "replace")
        d.update(title=title_of(page), description=html_to_text(page))
    desc = d.get("description") or ""
    d["deadline_mentions"] = deadlines(desc)
    if len(desc) < 400:
        d["needs_browser"] = True
        d["note"] = "Little text came back; the page probably needs a browser. Read it with TinyFish fetch_content."
    return d


# ---------- SimplifyJobs community list (all companies, mostly tech; finance via keyword) ----------

SIMPLIFY = "https://raw.githubusercontent.com/SimplifyJobs/Summer{year}-Internships/dev/.github/scripts/listings.json"
FINANCE = re.compile(r"investment bank|banking|summer analyst|private equity|finance|capital markets|\bM&A\b|restructuring|"
                     r"asset management|equity research|sales (?:and|&) trading|wealth|credit|quant", re.I)


def simplify(query: str = "", company: str = "", finance_only: bool = True, year: int = 2027, limit: int = 50):
    rows = json.loads(cached(SIMPLIFY.format(year=year), hours=12, timeout=60))
    words = query.lower().split()
    out = []
    for r in sorted(rows, key=lambda r: r.get("date_posted", 0), reverse=True):
        if not (r.get("active") and r.get("is_visible", True)):
            continue
        hay = f"{r['company_name']} {r['title']} {' '.join(r.get('locations', []))}".lower()
        if company and company.lower() not in r["company_name"].lower():
            continue
        if finance_only and not FINANCE.search(r["title"]):
            continue
        if not all(w in hay for w in words):
            continue
        out.append({"firm": r["company_name"], "title": r["title"], "location": "; ".join(r.get("locations", [])),
                    "url": r["url"].replace("?embed=true", ""), "terms": r.get("terms"),
                    "posted": _date(r.get("date_posted")), "source": "SimplifyJobs"})
        if len(out) >= limit:
            break
    return out


def _date(ts):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts else ""
