"""word.py dossier.json out.html dossier_url : simple printable HTML for textutil -> docx."""
import json, re, sys, html as H
d = json.load(open(sys.argv[1])); out = sys.argv[2]; url = sys.argv[3]
S = {s["n"]: s for s in d.get("sources", [])}
def t(x):
    x = H.escape(x or "")
    x = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", x)
    return re.sub(r"\[(\d+)\]", r"<sup>[\1]</sup>", x)
o = [f"<html><head><meta charset='utf-8'><style>body{{font-family:Calibri,Arial;font-size:11pt}} h1{{font-size:18pt}} h2{{font-size:14pt;border-bottom:1px solid #999}} td,th{{border:1px solid #bbb;padding:3px;font-size:9.5pt;vertical-align:top}} table{{border-collapse:collapse;width:100%}}</style></head><body>"]
m = d["meta"]; o.append(f"<h1>{t(m['title'])}</h1><p>{t(m.get('subtitle',''))}<br>{t(m.get('purpose',''))} · {t(m['date'])}<br>Interactive dossier: <a href='{url}'>{url}</a></p>")
o.append("<h2>TL;DR</h2><ul>" + "".join(f"<li>{t(x)}</li>" for x in d.get("tldr", [])) + "</ul>")
if d.get("kpis"): o.append("<h2>Key numbers</h2><table><tr><th>Metric</th><th>Value</th><th>Note</th></tr>" + "".join(f"<tr><td>{t(k['label'])}</td><td><b>{t(k['value'])}</b></td><td>{t(k.get('note',''))}</td></tr>" for k in d["kpis"]) + "</table>")
A = d.get("assessment")
if A:
    o.append(f"<h2>Assessment & video (due {t(A.get('due',''))})</h2><ul>" + "".join(f"<li><b>{t(f['k'])}:</b> {t(f['v'])}</li>" for f in A.get("facts", [])) + "</ul><p><b>How to take them</b></p><ul>" + "".join(f"<li>{t(x)}</li>" for x in A.get("strategy", [])) + "</ul>")
    for v in A.get("video", []): o.append(f"<p><b>Q: {t(v['q'])}</b><br>{t(v.get('a',''))}<br><i>{t(v.get('tip',''))}</i></p>")
for b in d.get("playbook", []):
    o.append(f"<h2>{t(b['title'])}</h2>" + (f"<p>{t(b['text'])}</p>" if b.get("text") else "") + ("<ul>" + "".join(f"<li>{t(i)}</li>" for i in b.get("items") or []) + "</ul>" if b.get("items") else ""))
P = d.get("person")
if P:
    o.append(f"<h2>{t(P['name'])}</h2><p>{t(P.get('summary',''))}</p><table><tr><th>Dates</th><th>Firm</th><th>Role</th></tr>" + "".join(f"<tr><td>{t(r.get('dates',''))}</td><td>{t(r.get('firm',''))}</td><td>{t(r.get('role',''))}</td></tr>" for r in P.get("timeline", [])) + "</table>")
F = d.get("firm")
if F: o.append(f"<h2>{t(F.get('name','The firm'))}</h2><p>{t(F.get('summary',''))}</p><ul>" + "".join(f"<li><b>{t(s['k'])}:</b> {t(s['v'])}</li>" for s in F.get("snapshot", [])) + "</ul>")
G = d.get("group")
if G: o.append(f"<h2>{t(G.get('name','The group'))}</h2><p>{t(G.get('summary',''))}</p>")
o.append("<h2>Deals</h2><table><tr><th>Date</th><th>Deal</th><th>Size</th><th>Role</th></tr>" + "".join(f"<tr><td>{t(x.get('date',''))}</td><td>{t(x['name'])}</td><td>{t(x.get('size',''))}</td><td>{t(x.get('role',''))}</td></tr>" for x in d.get("deals", [])) + "</table>")
for x in d.get("deals", []):
    if x.get("deep"):
        o.append(f"<h3>{t(x['name'])}</h3><p>{t(x.get('overview',''))}</p>" + (f"<p><b>Pitch:</b> {t(x['pitch'])}</p>" if x.get("pitch") else "") + "".join(f"<p><b>{t(q['q'])}</b> {t(q['a'])}</p>" for q in x.get("qa") or []))
o.append("<h2>Market</h2>" + "".join(f"<p><b>{t(m['trend'])}.</b> {t(m.get('detail',''))} <i>Why it matters:</i> {t(m.get('why',''))}</p>" for m in d.get("market", [])))
o.append("<h2>Questions to ask</h2><ol>" + "".join(f"<li>{'★ ' if q.get('star') else ''}{t(q['q'])}<br><i>{t(q.get('why',''))}</i></li>" for q in sorted(d.get("questions", []), key=lambda q: not q.get("star"))) + "</ol>")
o.append("<h2>Practice cards</h2>" + "".join(f"<p><b>{i+1}. {t(c['q'])}</b> <i>({t(c.get('topic',''))})</i><br>{t(c['a'])}</p>" for i, c in enumerate(d.get("drill", []))))
o.append("<h2>Still missing</h2><ul>" + "".join(f"<li><b>{t(g['what'])}</b> → {t(g.get('where',''))}</li>" for g in d.get("gaps", [])) + "</ul>")
o.append("<h2>Sources</h2><ol>" + "".join(f"<li>{t(s['title'])} · {t(s.get('publisher',''))} · {t(s.get('date',''))} · <a href='{H.escape(s.get('url',''))}'>{H.escape(s.get('url',''))}</a></li>" for s in d.get("sources", [])) + "</ol></body></html>")
open(out, "w").write("".join(o)); print("ok", out)
