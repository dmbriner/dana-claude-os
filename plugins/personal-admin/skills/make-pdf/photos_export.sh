#!/bin/bash
# Export photos from the Photos app (originals, so HEIC stays full quality) into a folder,
# ready for make_pdf.py. Photos asks for Automation permission the first time.
#   photos_export.sh <outdir> --selection              # whatever is selected in Photos right now
#   photos_export.sh <outdir> --album "Album name"
#   photos_export.sh <outdir> --since "2026-11-19 08:00" [--until "2026-11-19 09:00"]
#   photos_export.sh <outdir> --last 12                 # the 12 most recent photos
set -euo pipefail
out="$1"; shift; mkdir -p "$out"
mode="${1:-}"; arg="${2:-}"; until_arg=""
[ "${3:-}" = "--until" ] && until_arg="${4:-}"
as_date() { # "YYYY-MM-DD HH:MM" -> AppleScript date built from components (locale-proof)
  python3 -c "import sys,datetime as d;t=d.datetime.strptime(sys.argv[1].strip(),'%Y-%m-%d %H:%M' if ':' in sys.argv[1] else '%Y-%m-%d');print(f'set {sys.argv[2]} to current date\nset year of {sys.argv[2]} to {t.year}\nset day of {sys.argv[2]} to 1\nset month of {sys.argv[2]} to {t.month}\nset day of {sys.argv[2]} to {t.day}\nset time of {sys.argv[2]} to {t.hour*3600+t.minute*60}')" "$1" "$2"
}
case "$mode" in
  --selection) pick='set theItems to selection';;
  --album)     pick="set theItems to media items of album \"$arg\"";;
  --last)      pick="set allItems to media items
set n to count of allItems
set k to $arg
if k > n then set k to n
set theItems to items (n - k + 1) thru n of allItems";;
  --since)     d1=$(as_date "$arg" d1); d2=""; cond="date of m ≥ d1"
               if [ -n "$until_arg" ]; then d2=$(as_date "$until_arg" d2); cond="$cond and date of m ≤ d2"; fi
               pick="$d1
$d2
set theItems to {}
repeat with m in (media items)
  if $cond then set end of theItems to m
end repeat";;
  *) echo "usage: photos_export.sh <outdir> --selection | --album NAME | --since 'YYYY-MM-DD HH:MM' [--until ...] | --last N" >&2; exit 2;;
esac
osascript <<OSA
tell application "Photos"
$pick
if (count of theItems) is 0 then error "No photos matched."
export theItems to (POSIX file "$out") with using originals
end tell
OSA
# set aside iCloud placeholders that never downloaded (tiny files, not real photos)
mkdir -p "$out/_placeholders"
find "$out" -maxdepth 1 -type f -size -2k -exec mv {} "$out/_placeholders/" \; -print | sed 's/^/placeholder (not downloaded from iCloud): /' >&2 || true
rmdir "$out/_placeholders" 2>/dev/null || true
find "$out" -maxdepth 1 -type f | wc -l | xargs -I{} echo "exported {} files to $out"
