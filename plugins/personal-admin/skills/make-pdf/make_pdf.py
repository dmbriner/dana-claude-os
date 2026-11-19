#!/usr/bin/env python3
"""make_pdf.py: turn anything into a clean, searchable PDF.

Inputs (files, folders or globs, mixed freely):
  photos/scans  .jpg .jpeg .png .heic .heif .tif .tiff .webp .bmp .gif
  Office        .doc .docx .ppt .pptx .xls .xlsx .odt .odp .ods .rtf .txt .csv .html .htm
  Markdown      .md
  Apple iWork   .pages .key .numbers   (exported through the app itself)
  PDFs          .pdf  (merged as-is; scanned pages get an OCR text layer)

Photos of paper pages are "scanned": the page is found, cropped, perspective-corrected,
turned upright, shadows removed, then laid on a Letter page with an invisible OCR text
layer, so the PDF is searchable and copyable.

Examples
  make_pdf.py IMG_0564.heic IMG_0565.heic -o "07 Piper - Small Caps (2026-07-27).pdf"
  make_pdf.py ~/Desktop/photos/ -o out.pdf --order date
  make_pdf.py deck.pptx memo.docx notes.md -o packet.pdf --title "Packet"
  make_pdf.py scanned.pdf --ocr-only -o scanned-searchable.pdf
  make_pdf.py *.heic -o out.pdf --rotate 3:180 --nocrop 5 --enhance gray

Always writes ~/.cache/make-pdf/previews/<name>.preview.jpg (contact sheet of every page)
so the result can be checked without cluttering the destination folder.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = Path.home() / ".cache" / "make-pdf"
TOOL = CACHE / "pdftool"
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

IMG = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff", ".webp", ".bmp", ".gif"}
OFFICE = {".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".odt", ".odp", ".ods", ".rtf",
          ".txt", ".csv", ".html", ".htm"}
IWORK = {".pages": "Pages", ".key": "Keynote", ".numbers": "Numbers"}
LETTER = (612.0, 792.0)
A4 = (595.28, 841.89)


def log(*a):
    print(*a, file=sys.stderr)


def need(mod, pipname=None):
    try:
        return __import__(mod)
    except ImportError:
        sys.exit(f"Missing Python package '{pipname or mod}'. Run: python3 -m pip install --user "
                 f"pillow pillow-heif opencv-python-headless numpy img2pdf pypdf 'reportlab<4.1'")


# ---------------------------------------------------------------- swift helper
def ensure_tool():
    src = HERE / "pdftool.swift"
    if TOOL.exists() and TOOL.stat().st_mtime >= src.stat().st_mtime:
        return str(TOOL)
    CACHE.mkdir(parents=True, exist_ok=True)
    sdks = ["MacOSX.sdk"] + sorted(
        (p.name for p in Path("/Library/Developer/CommandLineTools/SDKs").glob("MacOSX*.sdk")),
        reverse=True)
    tried = [None] + [f"/Library/Developer/CommandLineTools/SDKs/{s}" for s in sdks]
    for sdk in tried:  # newest SDK can be ahead of the installed swiftc; fall back until one builds
        cmd = ["swiftc", "-O", str(src), "-o", str(TOOL)] + (["-sdk", sdk] if sdk else [])
        if subprocess.run(cmd, capture_output=True).returncode == 0:
            return str(TOOL)
    log("warning: could not compile the OCR helper (need Xcode Command Line Tools); OCR and "
        "auto-rotate are off")
    return None


def ocr_images(paths):
    tool = ensure_tool()
    if not tool or not paths:
        return [{"lines": []} for _ in paths]
    out = []
    for i in range(0, len(paths), 20):
        r = subprocess.run([tool, "ocr"] + [str(p) for p in paths[i:i + 20]],
                           capture_output=True, text=True)
        try:
            out += json.loads(r.stdout)
        except Exception:
            out += [{"lines": []} for _ in paths[i:i + 20]]
    return out


def ocr_score(res):
    return sum(len(l["text"]) * l["conf"] for l in res.get("lines", []))


# ---------------------------------------------------------------- image loading
def load_image(path):
    PIL = need("PIL", "pillow")
    from PIL import Image, ImageOps
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    p = Path(path)
    if p.stat().st_size < 2048:
        raise ValueError(f"{p.name} is only {p.stat().st_size} bytes, so it is a placeholder, not a "
                         f"photo (unfinished Photos/iCloud export). Re-export it, or run "
                         f"photos_export.sh.")
    try:
        im = Image.open(p)
        im = ImageOps.exif_transpose(im)
    except Exception:
        tmp = Path(tempfile.mkdtemp()) / (p.stem + ".jpg")  # macOS fallback
        subprocess.run(["sips", "-s", "format", "jpeg", str(p), "--out", str(tmp)], capture_output=True)
        im = Image.open(tmp)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, "white")
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    return im.convert("RGB")


# ---------------------------------------------------------------- document scanning
def order_pts(pts):
    np = need("numpy")
    pts = np.array(pts, dtype="float32").reshape(4, 2)
    s, d = pts.sum(1), np.diff(pts, axis=1).ravel()
    return np.array([pts[s.argmin()], pts[d.argmin()], pts[s.argmax()], pts[d.argmax()]], "float32")


import itertools


def fill_holes(m):
    cv2, np = need("cv2"), need("numpy")
    h,w=m.shape; ff=m.copy(); mask=np.zeros((h+2,w+2),np.uint8)
    pad=cv2.copyMakeBorder(m,1,1,1,1,cv2.BORDER_CONSTANT,0)
    mk=np.zeros((h+4,w+4),np.uint8); cv2.floodFill(pad,mk,(0,0),255)
    return m | cv2.bitwise_not(pad[1:-1,1:-1])
def best_quad(hull_pts):
    cv2 = need("cv2")
    pts=hull_pts.reshape(-1,2).astype('float32')
    if len(pts)>16:
        peri=cv2.arcLength(pts.reshape(-1,1,2),True)
        for eps in (0.005,0.01,0.015,0.02,0.03):
            ap=cv2.approxPolyDP(pts.reshape(-1,1,2),eps*peri,True).reshape(-1,2)
            if len(ap)<=16: pts=ap.astype('float32'); break
    if len(pts)<4: return None
    best=None
    for c in itertools.combinations(range(len(pts)),4):
        q=pts[list(c)]; a=cv2.contourArea(q)
        if best is None or a>best[0]: best=(a,q)
    return best[1]
def find_page_cv(bgr):
    """Fallback page finder: paper = flat, bright, unsaturated region; holes (the print) filled."""
    cv2, np = need("cv2"), need("numpy")
    h,w=bgr.shape[:2]; k=800/max(h,w); s=cv2.resize(bgr,(int(w*k),int(h*k)),interpolation=cv2.INTER_AREA)
    A=s.shape[0]*s.shape[1]
    hsv=cv2.cvtColor(s,cv2.COLOR_BGR2HSV); g=cv2.cvtColor(s,cv2.COLOR_BGR2GRAY)
    sat=cv2.GaussianBlur(hsv[:,:,1],(0,0),2).astype('float32'); v=hsv[:,:,2].astype('float32')
    lap=cv2.GaussianBlur(np.abs(cv2.Laplacian(cv2.GaussianBlur(g,(3,3),0),cv2.CV_32F)),(0,0),2)
    vthr=0.55*np.percentile(v,97)
    flat=((lap<3.0)&(sat<40)&(v>vthr)).astype('uint8')*255
    flat=cv2.morphologyEx(flat,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    filled=fill_holes(flat)
    K=max(9,int(max(s.shape[:2])/40))
    filled=cv2.morphologyEx(filled,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(K,K)))
    n,lab,st,cen=cv2.connectedComponentsWithStats(filled)
    best=None
    for i in range(1,n):
        a=st[i,cv2.CC_STAT_AREA]
        if a<0.12*A: continue
        cx,cy=cen[i]; d=np.hypot(cx/s.shape[1]-.5,cy/s.shape[0]-.5)
        sc=a*(1-0.8*d)
        if best is None or sc>best[0]: best=(sc,i)
    if best is None: return None
    comp=(lab==best[1]).astype('uint8')*255
    cnts,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    c=max(cnts,key=cv2.contourArea)
    quad=best_quad(cv2.convexHull(c))
    return None if quad is None else order_pts(quad / k)


def vision_quads(jpgs):
    """Apple Vision document segmentation (same detector as the Notes scanner)."""
    tool = ensure_tool()
    if not tool:
        return [None] * len(jpgs)
    out = []
    for i in range(0, len(jpgs), 20):
        r = subprocess.run([tool, "doc"] + [str(p) for p in jpgs[i:i + 20]], capture_output=True, text=True)
        try:
            out += json.loads(r.stdout)
        except Exception:
            out += [{}] * len(jpgs[i:i + 20])
    return out


def warp(bgr, quad):
    cv2, np = need("cv2"), need("numpy")
    tl, tr, br, bl = quad
    W = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    H = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
    M = cv2.getPerspectiveTransform(quad, np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]],
                                                   "float32"))
    return cv2.warpPerspective(bgr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def enhance(bgr, mode):
    cv2, np = need("cv2"), need("numpy")
    if mode == "none":
        return bgr
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    if mode == "bw":
        g = cv2.GaussianBlur(gray, (3, 3), 0)
        return cv2.cvtColor(cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                  cv2.THRESH_BINARY, 31, 15), cv2.COLOR_GRAY2BGR)
    # estimate paper brightness (removes shadows / uneven light) and divide it out
    h, w = gray.shape
    ks = max(15, (min(h, w) // 25) | 1)
    bg = cv2.dilate(gray, np.ones((ks, ks), np.uint8))
    bg = cv2.GaussianBlur(bg, (0, 0), ks)
    bg = np.maximum(bg.astype("float32"), 1)
    out = np.clip(bgr.astype("float32") * (245.0 / bg[:, :, None]), 0, 255)
    # levels: lift paper to white, deepen ink a little
    lo = np.percentile(out, 1.0)
    out = np.clip((out - lo) * 255.0 / max(250 - lo, 1), 0, 255)
    out = (255 * (out / 255.0) ** 1.15).astype("uint8")
    if mode == "gray":
        return cv2.cvtColor(cv2.cvtColor(out, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    return out


def trim_border(bgr, frac=0.008):
    h, w = bgr.shape[:2]
    dy, dx = int(h * frac), int(w * frac)
    return bgr[dy:h - dy, dx:w - dx]


# ---------------------------------------------------------------- PDF page builders
def page_size(paper, iw, ih):
    if paper == "fit":
        return (612.0, 612.0 * ih / iw) if iw <= ih else (792.0, 792.0 * ih / iw)
    pw, ph = LETTER if paper == "letter" else A4
    return (pw, ph) if ih >= iw else (ph, pw)


def draw_text_layer(c, lines, x0, y0, w, h):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    for l in lines:
        t = l["text"].encode("latin-1", "replace").decode("latin-1")
        if not t.strip():
            continue
        bx, by, bw, bh = l["box"]
        x, y, tw, th = x0 + bx * w, y0 + by * h, bw * w, bh * h
        fs = max(th * 0.85, 1)
        sw = stringWidth(t, "Helvetica", fs) or 1
        to = c.beginText()
        to.setTextRenderMode(3)  # invisible
        to.setFont("Helvetica", fs)
        to.setHorizScale(max(1, min(1000, 100.0 * tw / sw)))
        to.setTextOrigin(x, y + th * 0.18)
        to.textLine(t)
        c.drawText(to)


def image_pages_pdf(items, out_pdf, paper, margin_in):
    """items: list of (jpg_path, (w,h), ocr_result). Writes one PDF."""
    need("reportlab", "reportlab<4.1")
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(out_pdf))
    m = margin_in * 72
    for jpg, (iw, ih), res in items:
        pw, ph = page_size(paper, iw, ih)
        c.setPageSize((pw, ph))
        s = min((pw - 2 * m) / iw, (ph - 2 * m) / ih)
        dw, dh = iw * s, ih * s
        x0, y0 = (pw - dw) / 2, (ph - dh) / 2
        c.drawImage(str(jpg), x0, y0, dw, dh)
        draw_text_layer(c, res.get("lines", []), x0, y0, dw, dh)
        c.showPage()
    c.save()


# ---------------------------------------------------------------- converters
def convert_office(path, outdir):
    if not os.path.exists(SOFFICE):
        sys.exit("LibreOffice not found at /Applications/LibreOffice.app (needed for Office files).")
    prof = Path(tempfile.mkdtemp(prefix="lo-profile-"))
    subprocess.run([SOFFICE, f"-env:UserInstallation=file://{prof}", "--headless",
                    "--convert-to", "pdf", "--outdir", str(outdir), str(path)],
                   capture_output=True, timeout=300)
    shutil.rmtree(prof, ignore_errors=True)
    pdf = Path(outdir) / (Path(path).stem + ".pdf")
    if not pdf.exists():
        raise RuntimeError(f"LibreOffice could not convert {Path(path).name}")
    return pdf


def convert_iwork(path, outdir):
    app = IWORK[Path(path).suffix.lower()]
    pdf = Path(outdir) / (Path(path).stem + ".pdf")
    script = f'''
    set inF to POSIX file "{path}"
    set outF to POSIX file "{pdf}"
    tell application "{app}"
        set d to open inF
        export d to outF as PDF
        close d saving no
    end tell'''
    subprocess.run(["osascript", "-e", script], capture_output=True, timeout=300)
    if not pdf.exists():
        raise RuntimeError(f"{app} could not export {Path(path).name}")
    return pdf


def md_to_html(text, title):
    import html
    out, in_list, in_code = [], None, False
    def inline(s):
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"(?<!\*)\*(?!\s)(.+?)\*", r"<i>\1</i>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            if in_code:
                out.append("</pre>")
            else:
                out.append("<pre>")
            in_code = not in_code
            i += 1
            continue
        if in_code:
            out.append(html.escape(ln))
            i += 1
            continue
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            rows = [ln]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            cells = [[inline(c.strip()) for c in r.strip().strip("|").split("|")] for r in rows]
            out.append("<table><tr>" + "".join(f"<th>{c}</th>" for c in cells[0]) + "</tr>" +
                       "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in cells[1:]) +
                       "</table>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        lm = re.match(r"^\s*([-*+]|\d+\.)\s+(.*)", ln)
        if lm:
            tag = "ol" if lm.group(1)[0].isdigit() else "ul"
            if in_list != tag:
                if in_list:
                    out.append(f"</{in_list}>")
                out.append(f"<{tag}>")
                in_list = tag
            out.append(f"<li>{inline(lm.group(2))}</li>")
        else:
            if in_list:
                out.append(f"</{in_list}>")
                in_list = None
            if m:
                n = len(m.group(1))
                out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            elif re.match(r"^\s*(---|\*\*\*)\s*$", ln):
                out.append("<hr>")
            elif ln.strip():
                out.append(f"<p>{inline(ln)}</p>")
        i += 1
    if in_list:
        out.append(f"</{in_list}>")
    css = ("body{font-family:Arial,Helvetica,sans-serif;font-size:11pt;line-height:1.35}"
           "table{border-collapse:collapse}td,th{border:1px solid #999;padding:3px 6px}"
           "pre{font-family:Menlo,monospace;font-size:9pt;background:#f4f4f4}")
    return f"<html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{css}</style></head><body>{''.join(out)}</body></html>"


def convert_md(path, outdir):
    html_path = Path(outdir) / (Path(path).stem + ".html")
    html_path.write_text(md_to_html(Path(path).read_text(errors="replace"), Path(path).stem))
    return convert_office(html_path, outdir)


# ---------------------------------------------------------------- PDF utilities
def pdf_needs_ocr(page):
    try:
        return len((page.extract_text() or "").strip()) < 20
    except Exception:
        return True


def ocr_existing_pdf(pdf_path, work, dpi=200):
    """Add an invisible text layer to pages that have no text. Original pages are kept."""
    from pypdf import PdfReader, PdfWriter
    need("reportlab", "reportlab<4.1")
    from reportlab.pdfgen import canvas
    tool = ensure_tool()
    reader = PdfReader(str(pdf_path))
    targets = [i for i, p in enumerate(reader.pages) if pdf_needs_ocr(p)]
    if not tool or not targets:
        return Path(pdf_path), 0
    rdir = Path(work) / ("render-" + Path(pdf_path).stem)
    r = subprocess.run([tool, "render", str(pdf_path), str(rdir), str(dpi)], capture_output=True, text=True)
    pngs = {d["page"] - 1: d["png"] for d in json.loads(r.stdout or "[]")}
    res = dict(zip(targets, ocr_images([pngs[i] for i in targets if i in pngs])))
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i in res and res[i].get("lines"):
            page.transfer_rotation_to_content()
            mb = page.mediabox
            ov = Path(work) / f"ov-{i}.pdf"
            c = canvas.Canvas(str(ov), pagesize=(float(mb.width), float(mb.height)))
            draw_text_layer(c, res[i]["lines"], 0, 0, float(mb.width), float(mb.height))
            c.save()
            from pypdf import Transformation
            page.merge_transformed_page(PdfReader(str(ov)).pages[0],
                                        Transformation().translate(float(mb.left), float(mb.bottom)))
        writer.add_page(page)
    out = Path(work) / (Path(pdf_path).stem + "-ocr.pdf")
    with open(out, "wb") as f:
        writer.write(f)
    return out, len(res)


def contact_sheet(pdf_path, out_jpg, work):
    from PIL import Image, ImageDraw
    tool = ensure_tool()
    if not tool:
        return None
    rdir = Path(work) / "preview"
    r = subprocess.run([tool, "render", str(pdf_path), str(rdir), "40"], capture_output=True, text=True)
    pages = json.loads(r.stdout or "[]")
    if not pages:
        return None
    thumbs = [Image.open(p["png"]).convert("RGB") for p in pages]
    tw = 260
    thumbs = [t.resize((tw, int(t.height * tw / t.width))) for t in thumbs]
    cols = min(6, len(thumbs))
    rows = [thumbs[i:i + cols] for i in range(0, len(thumbs), cols)]
    rh = [max(t.height for t in r) + 36 for r in rows]
    sheet = Image.new("RGB", (cols * (tw + 16) + 16, sum(rh) + 16), (90, 90, 90))
    d = ImageDraw.Draw(sheet)
    y = 16
    for ri, r in enumerate(rows):
        for ci, t in enumerate(r):
            x = 16 + ci * (tw + 16)
            sheet.paste(t, (x, y + 20))
            d.text((x, y + 4), f"p{ri * cols + ci + 1}", fill=(255, 255, 255))
        y += rh[ri]
    sheet.save(out_jpg, quality=80)
    return out_jpg


# ---------------------------------------------------------------- main
def natural_key(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(p))]


def photo_date(p):
    try:
        from PIL import Image
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            pass
        ex = Image.open(p).getexif()
        v = ex.get_ifd(0x8769).get(36867) or ex.get(306)
        if v:
            return v
    except Exception:
        pass
    return "%020.6f" % os.path.getmtime(p)


def expand(inputs, order):
    files = []
    for a in inputs:
        a = os.path.expanduser(a)
        if os.path.isdir(a):
            found = [str(p) for p in Path(a).iterdir() if p.is_file() and not p.name.startswith(".")]
            found = [f for f in found if Path(f).suffix.lower() in IMG | OFFICE | set(IWORK) | {".pdf", ".md"}]
            files += sorted(found, key=natural_key)
        elif any(ch in a for ch in "*?["):
            files += sorted(glob.glob(a), key=natural_key)
        elif os.path.exists(a):
            files.append(a)
        else:
            log(f"skip: {a} not found")
    if order == "name":
        files.sort(key=natural_key)
    elif order == "date":
        files.sort(key=photo_date)
    return files


def parse_pagemap(s, cast=str):
    m = {}
    for part in (s or "").split(","):
        if not part.strip():
            continue
        if ":" in part:
            k, v = part.split(":", 1)
            m[int(k)] = cast(v)
        else:
            m[int(part)] = True
    return m


def process_images(paths, args, work, first_page_no):
    """Scan a run of consecutive images into one PDF. Returns (pdf, report rows)."""
    cv2, np = need("cv2", "opencv-python-headless"), need("numpy")
    rot = parse_pagemap(args.rotate, int)
    nocrop = parse_pagemap(args.nocrop)
    rows, items = [], []
    imgs = []
    for p in paths:
        im = load_image(p)
        bgr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        h, w = bgr.shape[:2]
        k = 1600.0 / max(h, w)
        small = Path(work) / f"det-{len(imgs):04d}.jpg"
        cv2.imwrite(str(small), cv2.resize(bgr, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA))
        imgs.append((p, bgr, small))
    vq = vision_quads([x[2] for x in imgs]) if args.mode != "photo" else [{}] * len(imgs)
    for j, ((p, bgr, small), vres) in enumerate(zip(imgs, vq)):
        n = first_page_no + j
        row = {"page": n, "file": Path(p).name}
        mode = args.mode
        h, w = bgr.shape[:2]
        if mode != "photo" and not nocrop.get(n):
            quad = None
            if vres.get("quad") and vres.get("conf", 0) >= 0.5:
                q = (np.array(vres["quad"], "float32") * np.array([w, h], "float32")).astype("float32")
                if cv2.contourArea(q) > 0.15 * w * h:
                    quad, row["crop"] = order_pts(q), f"page found (Vision {vres['conf']:.2f})"
            if quad is None:
                quad = find_page_cv(bgr)
                if quad is not None:
                    row["crop"] = "page found (fallback detector, check it)"
            if quad is not None:
                if args.pad:
                    c = quad.mean(0)
                    quad = (c + (quad - c) * (1 + args.pad)).astype("float32")
                    quad[:, 0] = quad[:, 0].clip(0, w - 1)
                    quad[:, 1] = quad[:, 1].clip(0, h - 1)
                bgr = trim_border(warp(bgr, quad), 0.004)
            else:
                row["crop"] = "no page edge found (kept full photo)"
        else:
            row["crop"] = "off"
        if mode != "photo":
            bgr = enhance(bgr, args.enhance)
        # orientation
        turns = {0: None, 90: cv2.ROTATE_90_COUNTERCLOCKWISE, 180: cv2.ROTATE_180, 270: cv2.ROTATE_90_CLOCKWISE}
        if n in rot:
            k = rot[n] % 360
            if turns.get(k) is not None:
                bgr = cv2.rotate(bgr, turns[k])
            row["rotate"] = f"{k}° (manual)"
        h, w = bgr.shape[:2]
        s = min(1.0, args.max_px / max(h, w))
        if s < 1:
            bgr = cv2.resize(bgr, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        jpg = Path(work) / f"page-{n:04d}.jpg"
        cv2.imwrite(str(jpg), bgr, [cv2.IMWRITE_JPEG_QUALITY, args.quality])
        items.append([jpg, row])
    # auto-rotate + OCR
    if not args.no_ocr or not args.no_autorotate:
        res = ocr_images([it[0] for it in items])
        for it, r in zip(items, res):
            jpg, row = it
            if not args.no_autorotate and "rotate" not in row:
                ls = r.get("lines", [])
                if ls:
                    # Vision reads sideways text but its boxes come back tall and thin
                    from PIL import Image
                    W, H = Image.open(jpg).size
                    tall = sum(1 for l in ls if l["box"][3] * H > l["box"][2] * W * 1.2 and len(l["text"]) > 3)
                    sideways = tall > 0.5 * max(1, sum(1 for l in ls if len(l["text"]) > 3))
                else:
                    sideways = False
                cands = [90, 270, 0, 180] if sideways else [0, 180]
                img = cv2.imread(str(jpg))
                tmp = []
                for k in cands:
                    t = Path(work) / f"{jpg.stem}-r{k}.jpg"
                    cv2.imwrite(str(t), img if k == 0 else cv2.rotate(img, turns[k]), [cv2.IMWRITE_JPEG_QUALITY, 70])
                    tmp.append(t)
                scores = [ocr_score(x) for x in ocr_images(tmp)]
                best = cands[scores.index(max(scores))] if max(scores) > 0 else 0
                if best != 0 and max(scores) > 1.15 * scores[cands.index(0)]:
                    cv2.imwrite(str(jpg), cv2.rotate(img, turns[best]), [cv2.IMWRITE_JPEG_QUALITY, args.quality])
                    row["rotate"] = f"{best}° (auto)"
                    r.clear()
                    r.update(ocr_images([jpg])[0])
            if args.no_ocr:
                r["lines"] = []
            row["ocr_chars"] = sum(len(l["text"]) for l in r.get("lines", []))
            it.append(r)
    else:
        for it in items:
            it.append({"lines": []})
    from PIL import Image
    built = [(jpg, Image.open(jpg).size, r) for jpg, row, r in items]
    out = Path(work) / f"images-{first_page_no:04d}.pdf"
    image_pages_pdf(built, out, args.paper, args.margin)
    return out, [row for _, row, _ in items]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out", required=True, help="output PDF path")
    ap.add_argument("--title", help="PDF title metadata (default: output file name)")
    ap.add_argument("--order", choices=["given", "name", "date"], default="given",
                    help="page order: as given (default), natural file name, or photo date taken")
    ap.add_argument("--mode", choices=["scan", "photo"], default="scan",
                    help="scan = find+crop+clean the paper page (default); photo = keep the picture as is")
    ap.add_argument("--enhance", choices=["color", "gray", "bw", "none"], default="color",
                    help="scan cleanup: color (default, keeps charts), gray, bw (text only), none")
    ap.add_argument("--paper", choices=["letter", "a4", "fit"], default="letter")
    ap.add_argument("--margin", type=float, default=0.0, help="page margin in inches for image pages")
    ap.add_argument("--rotate", help="manual turns by output page: '3:90,5:180' (counter-clockwise)")
    ap.add_argument("--pad", type=float, default=0.01,
                    help="grow the detected page outline by this fraction (0.02 = 2%%) if crops cut text")
    ap.add_argument("--nocrop", help="output pages to leave uncropped: '2,4'")
    ap.add_argument("--no-ocr", action="store_true", help="skip the searchable text layer")
    ap.add_argument("--no-autorotate", action="store_true")
    ap.add_argument("--ocr-only", action="store_true",
                    help="PDF inputs only get a text layer on scanned pages (this is also the default for PDFs)")
    ap.add_argument("--max-px", type=int, default=2400, help="longest side of page images (≈220 dpi)")
    ap.add_argument("--quality", type=int, default=82, help="JPEG quality for page images")
    ap.add_argument("--split", action="store_true", help="one PDF per input instead of one merged PDF")
    ap.add_argument("--no-bookmarks", action="store_true")
    ap.add_argument("--keep-work", action="store_true", help="keep the temp folder (debug)")
    args = ap.parse_args()

    from pypdf import PdfReader, PdfWriter
    files = expand(args.inputs, args.order)
    if not files:
        sys.exit("No input files.")
    out = Path(os.path.expanduser(args.out))
    if out.suffix.lower() != ".pdf":
        out = out.with_suffix(".pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="make-pdf-"))

    if args.split:
        base = [a for a in sys.argv[1:] if a not in args.inputs]
        for f in files:
            o = out.parent / (Path(f).stem + ".pdf")
            cmd = [sys.executable, __file__, f, "-o", str(o)] + [x for x in base if x not in ("--split", "-o", "--out", str(args.out))]
            subprocess.run(cmd)
        return

    # group consecutive images so they become one scanned run
    groups = []
    for f in files:
        ext = Path(f).suffix.lower()
        kind = "img" if ext in IMG else "pdf" if ext == ".pdf" else "md" if ext == ".md" else \
            "iwork" if ext in IWORK else "office" if ext in OFFICE else None
        if kind is None:
            log(f"skip: {Path(f).name} (unsupported type {ext})")
            continue
        if kind == "img" and groups and groups[-1][0] == "img":
            groups[-1][1].append(f)
        else:
            groups.append((kind, [f]))

    writer = PdfWriter()
    report, page_no, ocr_added = [], 1, 0
    for kind, fs in groups:
        try:
            if kind == "img":
                pdf, rows = process_images(fs, args, work, page_no)
                report += rows
                label = Path(fs[0]).stem if len(fs) == 1 else f"{Path(fs[0]).stem} – {Path(fs[-1]).stem}"
            else:
                f = fs[0]
                pdf = {"pdf": lambda x, w: Path(x), "md": convert_md, "iwork": convert_iwork,
                       "office": convert_office}[kind](f, work)
                if not args.no_ocr:
                    pdf, n = ocr_existing_pdf(pdf, work)
                    ocr_added += n
                label = Path(f).stem
                report.append({"page": page_no, "file": Path(f).name, "converted": kind})
            r = PdfReader(str(pdf))
            start = len(writer.pages)
            for p in r.pages:
                writer.add_page(p)
            if not args.no_bookmarks and len(groups) > 1:
                writer.add_outline_item(label, start)
            page_no = len(writer.pages) + 1
        except Exception as e:
            log(f"ERROR on {', '.join(Path(x).name for x in fs)}: {e}")
            report.append({"file": ", ".join(Path(x).name for x in fs), "error": str(e)})

    if not writer.pages:
        sys.exit("Nothing was converted.")
    writer.add_metadata({"/Title": args.title or out.stem, "/Producer": "make-pdf"})
    try:
        writer.compress_identical_objects()
    except Exception:
        pass
    with open(out, "wb") as fh:
        writer.write(fh)
    (CACHE / "previews").mkdir(parents=True, exist_ok=True)
    prev = contact_sheet(out, str(CACHE / "previews" / (out.stem + ".preview.jpg")), work)
    if not args.keep_work:
        shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({"pdf": str(out), "pages": len(writer.pages),
                      "size_mb": round(out.stat().st_size / 1e6, 2),
                      "preview": prev, "ocr_pages_added_to_pdfs": ocr_added,
                      "pages_detail": report}, indent=1))


if __name__ == "__main__":
    main()
