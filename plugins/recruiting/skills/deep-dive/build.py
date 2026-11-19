"""Build a deep-dive dossier page from a JSON data file.

Usage: python3 -I build.py <dossier.json> <out.html>

Fills assets/dossier.html with the data, then checks the data:
- every [n] citation and src number points to a real entry in sources
- every source has a URL
- the minimums for a full deep dive (see SKILL.md "Quality bar")
Prints warnings; exits 1 only if the JSON is broken or a citation points nowhere.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
data_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
raw = data_path.read_text()
data = json.loads(raw)

src_ns = {str(s.get("n")) for s in data.get("sources", [])}
cited = set(re.findall(r"\[(\d+)\]", raw))

def walk(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "src" and v not in (None, ""):
                for n in (v if isinstance(v, list) else [v]):
                    cited.add(str(n))
            else:
                walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)
walk(data)

errors, warnings = [], []
dangling = sorted(cited - src_ns, key=lambda s: int(s) if s.isdigit() else 0)
if dangling:
    errors.append(f"citations with no matching source: {dangling}")
for s in data.get("sources", []):
    if not s.get("url"):
        warnings.append(f"source {s.get('n')} has no URL")

mode = data.get("meta", {}).get("mode", "")
deals = data.get("deals", [])
mins = {
    "sources": (len(data.get("sources", [])), 25),
    "deals listed": (len(deals), 12),
    "deals with full breakdowns": (sum(1 for d in deals if d.get("deep")), 4),
    "drill cards": (len(data.get("drill", [])), 40),
    "questions": (len(data.get("questions", [])), 10),
    "charts": (len(data.get("charts", [])), 3),
    "market trends": (len(data.get("market", [])), 4),
}
if mode in ("person", "panel"):
    people = data.get("people") or ([data["person"]] if data.get("person") else [])
    mins["career timeline rows"] = (min((len(p.get("timeline", [])) for p in people), default=0), 2)
for name, (have, need) in mins.items():
    if have < need:
        warnings.append(f"quality bar: {name} = {have} (target {need}+)")

template = (HERE / "assets" / "dossier.html").read_text()
title = data.get("meta", {}).get("title", "Deep Dive")
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = template.replace("{{TITLE}}", title.replace("<", "&lt;")).replace("/*DOSSIER_JSON*/", blob)
out_path.write_text(html)

for w in warnings:
    print("WARN:", w)
for e in errors:
    print("ERROR:", e)
print(f"wrote {out_path} ({len(html)//1024} KB)")
sys.exit(1 if errors else 0)
