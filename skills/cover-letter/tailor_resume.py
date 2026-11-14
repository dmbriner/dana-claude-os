"""Tailor a resume .docx without touching its formatting. Usage: python3 -I tailor.py base.docx spec.json out.docx
spec: {"replace": {prefix: new_text or null(delete)}, "drop_sections": [heading prefix], "add_after": {prefix: [new bullet texts]}}
New bullets copy the formatting of the GPA bullet.
"""
import json, re, sys, zipfile
base, specf, out = sys.argv[1:4]
spec = json.load(open(specf))
with zipfile.ZipFile(base) as z:
    files = {n: z.read(n) for n in z.namelist()}
x = files["word/document.xml"].decode()
bs = x.index('<w:body>') + len('<w:body>'); be = x.index('<w:sectPr', bs)
paras = re.findall(r'<w:p[ >].*?</w:p>|<w:p/>', x[bs:be], re.S)
def txt(p): return ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p)).replace('&amp;', '&').strip()
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')
def rebuild(p, new):
    ppr = re.search(r'<w:pPr>.*?</w:pPr>', p, re.S).group(0)
    rpr = re.search(r'<w:r[ >][^<]*?(<w:rPr>.*?</w:rPr>)', p, re.S).group(1)
    head = p[:p.index('>') + 1]
    return f'{head}{ppr}<w:r>{rpr}<w:t xml:space="preserve">{esc(new)}</w:t></w:r></w:p>'
bullet_tpl = next(p for p in paras if txt(p).startswith('Cumulative GPA'))
# drop whole sections (heading through blank lines before next non-bullet heading)
for sec in spec.get("drop_sections", []):
    i = next(i for i, p in enumerate(paras) if txt(p).startswith(sec))
    j = i + 1
    while j < len(paras) and (txt(paras[j]) == '' or 'numPr' in paras[j] or j == i + 1):
        j += 1
    # keep one trailing blank structure: remove i..j-1 but leave the blanks before next heading
    k = j
    while k - 1 > i and txt(paras[k - 1]) == '':
        k -= 1
    del paras[i:j]
    paras[i:i] = []
out_p = []; used = set()
for p in paras:
    t = txt(p); hit = None
    for k in spec.get("replace", {}):
        if t.startswith(k): hit = k
    if hit is not None:
        used.add(hit)
        if spec["replace"][hit] is None: continue
        p = rebuild(p, spec["replace"][hit])
    out_p.append(p)
    for k, adds in spec.get("add_after", {}).items():
        if t.startswith(k):
            used.add(k)
            for a in adds: out_p.append(rebuild(bullet_tpl, a))
missing = set(spec.get("replace", {})) | set(spec.get("add_after", {}))
missing -= used
if missing: print("WARNING not matched:", missing)
x = x[:bs] + ''.join(out_p) + x[be:]
files["word/document.xml"] = x.encode()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items(): z.writestr(n, b)
print("wrote", out)
