"""Live check of every career-tools tool, through the real MCP protocol (the same way Claude calls them).

Run: python3 -I mcp/career-tools/smoke_test.py
Each line prints OK or FAIL with a short sample. Network access is required; nothing is written except caches.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

SERVER = Path(__file__).resolve().parent / "server.py"


class Client:
    def __init__(self):
        self.p = subprocess.Popen([sys.executable, "-I", str(SERVER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True)
        self.n = 0
        self.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "smoke", "version": "1"}})

    def rpc(self, method, params=None):
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}}) + "\n")
        self.p.stdin.flush()
        return json.loads(self.p.stdout.readline())["result"]

    def call(self, name, **args):
        r = self.rpc("tools/call", {"name": name, "arguments": args})
        text = r["content"][0]["text"]
        if r.get("isError"):
            raise RuntimeError(text[:200])
        return json.loads(text) if text[:1] in "[{" else text


def first_url(x):
    if isinstance(x, dict):
        for k in ("url", "apply_url"):
            if isinstance(x.get(k), str) and x[k].startswith("http"):
                return x[k]
        for v in x.values():
            u = first_url(v)
            if u:
                return u
    if isinstance(x, list):
        for v in x:
            u = first_url(v)
            if u:
                return u
    return ""


def main():
    c = Client()
    tools = [t["name"] for t in c.rpc("tools/list")["tools"]]
    print(f"{len(tools)} tools: {', '.join(tools)}\n")
    found = {}

    def check(label, fn, summary):
        t = time.time()
        try:
            r = fn()
            print(f"OK   {label:28} {time.time() - t:5.1f}s  {summary(r)}")
            return r
        except Exception as e:
            print(f"FAIL {label:28} {time.time() - t:5.1f}s  {type(e).__name__}: {str(e)[:150]}")

    jobs = check("search_jobs (all firms)", lambda: c.call("search_jobs"),
                 lambda r: f"{r['count']} student postings from {r['firms_checked']} firms; "
                           f"errors: {list(r['errors']) or 'none'}; browser-only: {[b['firm'] for b in r.get('needs_browser', [])]}")
    if jobs and jobs["jobs"]:
        for want in ("greenhouse", "myworkdayjobs", "oraclecloud"):
            j = next((j for j in jobs["jobs"] if want in j["url"]), None)
            if j:
                check(f"job_details ({want})", lambda j=j: c.call("job_details", url=j["url"]),
                      lambda r: f"{r.get('title')!r}: {len(r.get('description') or '')} chars, posted {r.get('posted')}, "
                                f"closes {r.get('closes')}, deadlines {r.get('deadline_mentions')}")
    check("simplify_jobs (Goldman)", lambda: c.call("simplify_jobs", company="Goldman", limit=5),
          lambda r: f"{r['count']} rows, e.g. {r['jobs'][0]['title'][:50] if r['jobs'] else '-'}")
    check("market_news", lambda: c.call("market_news", days=1, limit=5),
          lambda r: ", ".join(f"{k}={len(v)}" for k, v in r.items() if k != "errors") + f"; errors: {r.get('errors', 'none')}")
    check("ticker_news (GS)", lambda: c.call("ticker_news", ticker="GS"), lambda r: f"{len(r)} headlines")
    deals = check("recent_deals", lambda: c.call("recent_deals", days=2, limit=10),
                  lambda r: ", ".join(f"{k}={len(v) if isinstance(v, list) else v}" for k, v in r.items()))
    check("firm_deals (Evercore)", lambda: c.call("firm_deals", firm="Evercore", days=60, limit=5),
          lambda r: f"news={len(r['news'])}, own announcements="
                    f"{sum(x.get('count', 0) for x in r.get('firm_announcements', []))}")
    check("sec_filings", lambda: c.call("sec_filings", query="agreement and plan of merger", days=5, limit=5),
          lambda r: f"{len(r)} filings, e.g. {r[0]['company'][:50] if r else '-'}")
    res = check("bank_research", lambda: c.call("bank_research", days=7, limit=3),
                lambda r: "; ".join(f"{x['firm']}={x.get('count', x.get('read_with') or 'ERR ' + x.get('error', ''))}" for x in r))
    check("bank_research (news)", lambda: c.call("bank_research", kind="news", days=30, limit=3),
          lambda r: "; ".join(f"{x['firm']}={x.get('count', x.get('error'))}" for x in r))
    gs_pdf = next((i["url"] for x in res or [] for i in x.get("items", []) if i.get("pdf")), "")
    page = next((i["url"] for x in res or [] for i in x.get("items", []) if not i.get("pdf")), "")
    for label, url in (("read_document (pdf)", gs_pdf), ("read_document (page)", page),
                       ("read_document (deal wire)", first_url((deals or {}).get("press_releases")))):
        if url:
            check(label, lambda url=url: c.call("read_document", url=url, max_chars=300),
                  lambda r: f"{r['chars']} chars: {r['title'][:60]!r}")
    check("fed_releases", lambda: c.call("fed_releases", days=7), lambda r: f"{len(r)} items")
    check("econ_series (DGS10)", lambda: c.call("econ_series", series_id="DGS10", points=2),
          lambda r: str(r["observations"][-1]))
    check("treasury_yields", lambda: c.call("treasury_yields", days=1), lambda r: str(r["rows"][0])[:90])
    check("search_news", lambda: c.call("search_news", query="private credit", days=2, limit=5), lambda r: f"{len(r)} items")
    c.p.terminate()


if __name__ == "__main__":
    main()
