---
name: make-pdf
description: Turn anything into a clean, searchable PDF. Photos of paper pages (HEIC/JPG from the iPhone or the Photos app) get cropped to the page, straightened, de-shadowed, turned upright and OCR'd, like a scanner app; Word, PowerPoint, Excel, Pages, Keynote, Numbers, Markdown, text, HTML and screenshots get converted; PDFs get merged, and scanned PDFs get a searchable text layer. Names and files the result in Dana's iCloud folders. Use when Dana says "make a PDF", "/make-pdf", "turn these into a PDF", "combine these", "scan these photos", "make this searchable", "put the pages in order", or drops photos of a reading/handout.
---

# Make PDF

Everything runs on the Mac. OCR uses Apple's own Vision framework, so no file leaves the computer.

Scripts are in this skill's folder (resolve the symlink at `~/.claude/skills/make-pdf`):
- `make_pdf.py`: the converter. `python3 make_pdf.py --help` shows every option.
- `photos_export.sh`: pulls photos out of the Photos app.
- `pdftool.swift`: Vision/PDFKit helper. It compiles itself to `~/.cache/make-pdf/pdftool` on first use. If the newest SDK doesn't match `swiftc`, it falls back to an older SDK automatically.

**Dependencies.** Install these once if an import fails:
`python3 -m pip install --user pillow pillow-heif opencv-python-headless numpy img2pdf pypdf "reportlab<4.1"`
(The system Python is 3.9, so pin reportlab below 4.1.) Office files need LibreOffice at `/Applications/LibreOffice.app`. Pages, Keynote and Numbers files are exported through those apps.

## 1. Gather the inputs
- **Files Dana names** (Desktop, Downloads, iCloud): use them directly. Folders and globs work too.
- **Photos app:** run `photos_export.sh <scratch dir> --selection`, or use `--album "Name"`, `--since "YYYY-MM-DD HH:MM" [--until ...]` or `--last N`. Photos asks for Automation permission once. Files under 2 KB are iCloud placeholders that never downloaded. They're not photos. They get set aside in `_placeholders/`. Tell Dana they need to download in Photos first, by opening them or turning on "Download Originals".
- **Group the pages into documents.** One reading = one PDF. When the photos cover several readings, look at them first and split them by title page, header or date. Sort by name with `--order name` or by time taken with `--order date`, then check the order against the page numbers printed on the pages.

## 2. Build
```
python3 make_pdf.py <inputs...> -o "<out>.pdf" [--title "..."] [options]
```
Defaults: scan mode (find the page, crop, straighten, clean, auto-rotate, OCR), color cleanup, Letter pages, 1% padding around the detected page, and bookmarks when several inputs are merged.

| Need | Option |
|---|---|
| Text-only page, smallest file | `--enhance bw` |
| Neutral gray look | `--enhance gray` |
| Keep the photo exactly as taken (screenshots, pictures) | `--mode photo` |
| A crop cut off text | `--pad 0.03` (all pages), or `--nocrop 4` (one page) |
| A page is sideways or upside down | `--rotate 3:90,5:180` (output page: degrees counter-clockwise) |
| Page size | `--paper a4` or `--paper fit` |
| Separate PDFs per file | `--split` |
| Make an existing scanned PDF searchable, unchanged otherwise | `--ocr-only` (pages that already have text are left alone) |
| Smaller file | `--max-px 1800 --quality 75` |

The script prints JSON with the page count, the file size, and the per-page crop method:
- "Vision" means Apple's detector.
- "grown to cover text" means the outline was widened because text near the middle of the photo fell outside it.
- "fallback" or "text block" means check that page.

It also reports rotation, characters of OCR text, and a `preview` path.

## 3. Check before handing it over (always)
- **Open the preview** (`~/.cache/make-pdf/previews/<name>.preview.jpg`, a contact sheet of every page) and look at it. Check:
  - each page is cropped to the paper
  - nothing is sideways
  - the order matches the printed page numbers
  - no page is missing or duplicated. People often photograph a page twice. Compare the printed page numbers, or the OCR text of neighbouring pages. Drop the extra from the build, and rename its photo `page N (duplicate photo).<ext>` instead of deleting it.
- For any page that looks off, render it larger and fix it, then rebuild with `--rotate`, `--nocrop` or `--pad`. Render with `~/.cache/make-pdf/pdftool render <pdf> <dir> 110`.
- **Spot-check that the text is searchable:** `python3 -c "from pypdf import PdfReader;print(PdfReader('<pdf>').pages[0].extract_text()[:300])"`.
- Photos of curled pages held in a hand can't be perfect: a fingertip or a curved edge may remain. Say so instead of claiming a perfect scan.

## 4. Name and file it
- **Names:** `NN Source - Title (YYYY-MM-DD).pdf`. NN is a two-digit sequence only when the file belongs to a numbered set, like a reading list. Use the date printed on the document; if only the month is known, use `YYYY-MM`. Example: `08 Piper Sandler - Focus on the Trend, ISM Cycle Likely to Expand Into 2027 (2026-03-02).pdf`.
- **Where to file it:** follow the iCloud layout in memory (`icloud-filing-layout`). Work readings go to the job's folder under `Career & Finance/Work History/<employer>/`. Market reports go to `Career & Finance/Markets/<Source>/<year>/`. Coursework goes under `Academics/...`. If the right place is unclear, ask once.
- **Originals:** move the source photos to `<dest>/_Source photos/<pdf name without .pdf>/`, named `page N.<ext>`, so they're kept but out of the way. Never delete originals. If a new PDF replaces an older one, move the old PDF to `Misc./_To Delete/<date> <label>/` and add a line to its `_undo-log.tsv`.
- Append each rename or move to `_rename-log.tsv` in the destination folder (old path, then new path).

## 5. Report
Tell Dana the file name and folder, page count, size, and whether the text is searchable. Flag any page with a weak crop, a missing page, or a placeholder photo that still needs downloading.
