"""merge.py out.json part1.json part2.json ... : renumber sources (dedupe by URL), remap [n] and src, concat lists."""
import json, re, sys
out, parts = sys.argv[1], sys.argv[2:]
sources, by_url, merged = [], {}, {}
def norm(u): return (u or "").strip().rstrip("/").lower().replace("https://","").replace("http://","").replace("www.","")
for p in parts:
    d = json.load(open(p)); m = {}
    for s in d.pop("sources", []):
        key = norm(s.get("url")) or ("title:" + s.get("title", ""))
        if key not in by_url:
            n = len(sources) + 1; s2 = dict(s); s2["n"] = n; sources.append(s2); by_url[key] = n
        m[str(s["n"])] = by_url[key]
    def fix(x):
        if isinstance(x, str):
            return re.sub(r"\[(\d+)\]", lambda g: f"[{m.get(g.group(1), 'X'+g.group(1))}]", x)
        if isinstance(x, list): return [fix(v) for v in x]
        if isinstance(x, dict):
            o = {}
            for k, v in x.items():
                if k == "src" and v not in (None, ""):
                    vs = v if isinstance(v, list) else [v]
                    nv = [m.get(str(n), "X"+str(n)) for n in vs]
                    o[k] = nv if isinstance(v, list) else nv[0]
                else: o[k] = fix(v)
            return o
        return x
    d = fix(d)
    for k, v in d.items():
        if isinstance(v, list): merged.setdefault(k, []).extend(v)
        elif k not in merged: merged[k] = v
        elif isinstance(v, dict) and isinstance(merged[k], dict):
            for kk, vv in v.items():
                if kk not in merged[k] or not merged[k][kk]: merged[k][kk] = vv
merged["sources"] = sources
bad = re.findall(r"\[X\d+\]|\"X\d+\"", json.dumps(merged))
json.dump(merged, open(out, "w"), ensure_ascii=False, indent=1)
print(f"{out}: {len(sources)} sources; unresolved refs: {len(bad)}", {k: len(v) for k, v in merged.items() if isinstance(v, list)})
