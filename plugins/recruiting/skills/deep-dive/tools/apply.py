"""apply.py dossier.json coach.json fixes.json out.json : merge coach output, apply fact-check fixes, cut Wrong items with new==null."""
import json, re, sys
D = json.load(open(sys.argv[1])); C = json.load(open(sys.argv[2])); F = json.load(open(sys.argv[3])); out = sys.argv[4]
log = []
# --- fixes
def resolve(path):
    toks = re.findall(r"[^.\[\]]+|\[\d+\]", path); obj = D
    for t in toks[:-1]:
        obj = obj[int(t.strip("[]"))] if (t.startswith("[") or t.isdigit()) else obj[t]
    last = toks[-1]; return obj, (int(last.strip("[]")) if (last.startswith("[") or last.isdigit()) else last)
fx = F if isinstance(F, list) else F.get("fixes", [])
cuts = []
for f in fx:
    p = f.get("path"); new = f.get("new"); old = f.get("old")
    if not p or (new is None and f.get("verdict", "").lower() != "wrong"): continue
    try:
        obj, k = resolve(p); cur = obj[k]
        if new is None: cuts.append((obj, k)); log.append(f"CUT {p}"); continue
        if isinstance(cur, str) and isinstance(old, str) and old and old in cur and isinstance(new, str) and old != cur:
            obj[k] = cur.replace(old, new)
        else:
            obj[k] = new
        log.append(f"FIX {p}")
    except Exception as e:
        log.append(f"SKIP {p}: {e}")
for obj, k in sorted(cuts, key=lambda t: -(t[1] if isinstance(t[1], int) else 0)):
    try:
        if isinstance(obj, list): obj.pop(k)
        else: obj.pop(k, None)
    except Exception as e: log.append(f"CUTFAIL {k}: {e}")
# --- coach
if C.get("drill"):
    D["drill"] = C["drill"] if C.get("replace_drill") else D.get("drill", []) + C["drill"]
for k in ("questions", "angles"):
    if C.get(k): D[k] = C[k]
import difflib
deep = [d for d in D.get("deals", []) if d.get("deep")]
for dp in C.get("deal_pitches", []):
    if not deep: break
    best = max(deep, key=lambda d: difflib.SequenceMatcher(None, dp.get("name","").lower(), d.get("name","").lower()).ratio())
    best["pitch"] = dp.get("pitch", best.get("pitch")); best["qa"] = dp.get("qa") or best.get("qa")
if C.get("video") and D.get("assessment"):
    D["assessment"]["video"] = C["video"]
extra = {k: C[k] for k in ("tmay", "why_secondaries", "call_plan", "practice_plan") if k in C}
pb = []
if "call_plan" in C: pb.append({"title": "Call plan", "items": C["call_plan"] if isinstance(C["call_plan"], list) else [C["call_plan"]]})
if "tmay" in C: pb.append({"title": "Tell me about yourself", "text": C["tmay"]})
if "why_secondaries" in C: pb.append({"title": "Why secondaries?", "text": C["why_secondaries"]})
pp = C.get("practice_plan")
if pp:
    if isinstance(pp, list):
        for i, b in enumerate(pp):
            if isinstance(b, dict):
                pb.append({"title": b.get("title") or b.get("block") or f"Practice block {i+1}", "text": b.get("first_tiny_step") and ("First tiny step: " + b["first_tiny_step"]), "items": b.get("steps") or b.get("items") or [v for kk, v in b.items() if kk not in ("title","block","first_tiny_step") and isinstance(v, str)]})
            else: pb.append({"title": f"Practice block {i+1}", "text": str(b)})
    else: pb.append({"title": "Practice plan", "text": str(pp)})
if C.get("avoid"): pb.append({"title": "Don't say (accuracy traps)", "items": C["avoid"]})
if isinstance(C.get("playbook"), list):  # coach may return finished playbook entries
    have = {p.get("title") for p in pb}
    pb += [p for p in C["playbook"] if isinstance(p, dict) and p.get("title") not in have]
if pb: D["playbook"] = pb + D.get("playbook", [])
json.dump(D, open(out, "w"), ensure_ascii=False, indent=1)
print("\n".join(log)); print(f"fixes applied/cut: {sum(1 for l in log if l[:3] in ('FIX','CUT'))}, skipped: {sum(1 for l in log if l.startswith('SKIP'))}")
