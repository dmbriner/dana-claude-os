"""Fill a routine prompt template with values from private/profile.json and print it.
Usage: python3 -I routines/render.py routines/daily-brief.md > /tmp/prompt.txt
The rendered prompt is what gets pasted into (or pushed to) the scheduled cloud routine.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = json.load(open(ROOT / "private" / "profile.json"))
values = {
    "FIRST_NAME": p["name"].split()[0],
    "SCHOOL_LINE": p.get("school_line", "college student"),
    "NEWSLETTER_TO": p["newsletter_to"],
    "NOTION_FIRMS": p["notion"]["firms"],
    "NOTION_OPPORTUNITIES": p["notion"]["opportunities"],
    "NOTION_PEOPLE": p["notion"]["people"],
    "NOTION_TECHNICALS": p["notion"]["technicals_bank"],
}
text = open(sys.argv[1]).read()
missing = set(re.findall(r"{{(\w+)}}", text)) - set(values)
if missing:
    sys.exit(f"missing values: {sorted(missing)}")
print(re.sub(r"{{(\w+)}}", lambda m: values[m.group(1)], text), end="")
