"""Turn web pages and PDFs into plain text (standard library, plus pdftotext when installed)."""
from __future__ import annotations

import html
import re
import shutil
import subprocess
import tempfile

DROP = re.compile(r"<(script|style|noscript|svg|nav|header|footer|form|aside|iframe)\b.*?</\1\s*>", re.S | re.I)
MAIN = re.compile(r"<(article|main)\b[^>]*>(.*?)</\1\s*>", re.S | re.I)
BLOCK = re.compile(r"</?(p|div|br|li|ul|ol|h[1-6]|tr|section|table)\b[^>]*>", re.I)


def html_to_text(page: str) -> str:
    """Readable text from an HTML page: drops scripts and navigation, prefers <article>/<main>."""
    page = DROP.sub(" ", page)
    m = max(MAIN.findall(page), key=lambda x: len(x[1]), default=None)
    body = m[1] if m and len(m[1]) > 800 else page
    body = BLOCK.sub("\n", body)
    body = html.unescape(re.sub(r"<[^>]+>", " ", body))
    lines = [re.sub(r"[ \t\xa0]+", " ", ln).strip() for ln in body.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(ln for ln in lines if ln)).strip()


def title_of(page: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", page, re.S | re.I)
    return html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""


def pdf_to_text(data: bytes) -> str:
    """Needs the `pdftotext` command (poppler). On a Mac: `brew install poppler`."""
    exe = shutil.which("pdftotext")
    if not exe:
        raise RuntimeError("pdftotext is not installed (brew install poppler); open the PDF link directly instead")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data)
        f.flush()
        r = subprocess.run([exe, "-layout", f.name, "-"], capture_output=True, timeout=60)
    return r.stdout.decode("utf-8", "replace").strip()


DEADLINE = re.compile(
    r"[^.\n]{0,60}\b(deadline|apply by|applications? (?:close|closes|are due|due|will close)|closing date|"
    r"accepting applications (?:until|through))\b[^.\n]{0,100}", re.I)


def deadlines(text: str) -> list:
    """Sentences in a job description that mention an application deadline."""
    seen, out = set(), []
    for m in DEADLINE.finditer(text):
        s = m.group(0).strip(" :-")
        if s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out[:3]
