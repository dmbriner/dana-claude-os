"""Build a one-page cover letter .docx by cloning a template letter (same fonts, margins, layout).
Personal details (name, contact block, template path) come from private/profile.json.
Usage: python3 -I mkletter.py spec.json out.docx
spec: {"date": str, "address": [lines], "salutation": str, "body": [paragraphs], "size": 21 (half-points, optional)}
"""
import json, os, sys, zipfile, re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".claude-plugin" / "marketplace.json").exists())
PROFILE = json.load(open(ROOT / "private" / "profile.json"))
TPL = os.path.expanduser(PROFILE["letter_template"])
NAME = PROFILE["name"]

spec = json.load(open(sys.argv[1]))
out = sys.argv[2]
sz = str(spec.get("size", 21))
after = str(spec.get("after", 160))

def rpr(bold=False):
    return ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
            + ('<w:b/>' if bold else '') + f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>')

def para(lines, right=False, bold_first=False):
    ppr = '<w:pPr>' + f'<w:spacing w:after="{after}" w:line="259" w:lineRule="auto"/>' + ('<w:jc w:val="right"/>' if right else '') + rpr() + '</w:pPr>'
    runs = ''
    for i, ln in enumerate(lines):
        br = '<w:br/>' if i else ''
        runs += f'<w:r>{rpr(bold_first and i == 0)}{br}<w:t xml:space="preserve">{escape(ln)}</w:t></w:r>'
    return f'<w:p>{ppr}{runs}</w:p>'

with zipfile.ZipFile(TPL) as z:
    files = {n: z.read(n) for n in z.namelist()}
doc = files["word/document.xml"].decode("utf-8")

paras = [para([NAME, PROFILE["city"], PROFILE["phone"], PROFILE["email"]], right=True, bold_first=True),
         para([spec["date"]]),
         para(spec["address"]),
         para([spec["salutation"]])]
paras += [para([p]) for p in spec["body"]]
paras += [para(["Sincerely,"]), para([NAME])]

sect = re.search(r'<w:sectPr.*?</w:sectPr>', doc, re.S).group(0)
body_start = doc.index('<w:body>') + len('<w:body>')
body_end = doc.index('</w:body>')
doc = doc[:body_start] + ''.join(paras) + sect + doc[body_end:]
files["word/document.xml"] = doc.encode("utf-8")

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items():
        z.writestr(n, b)
print("wrote", out)
