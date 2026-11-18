#!/usr/bin/env python3
"""Find focus blocks whose time has passed, so plan-my-day can catch up before planning.

Standard library only.

Input: a JSON file (or "-" for stdin) holding the calendar API's events list for the
focus calendar, covering the look-back window (default: last 2 days through end of today):
  {"now": "2026-11-18T10:39:00-05:00",          # optional; defaults to the real clock
   "events": [ ...events exactly as list_events returns them... ]}
A bare list of events also works.

Only events whose title starts with the focus prefix (default "🎯 Focus:") count.
Each block is tied to its Notion task by the first notion.so / notion.com link in
its description.

Output (JSON):
  {"now": ...,
   "passed":   [ {task_id, task_url, titles[], blocks, minutes, first_start, last_end} ],  # ended before now
   "running":  [ ...same shape... ],   # started, not ended
   "upcoming_today": [ ...same shape... ],
   "no_task_link": [ titles of focus blocks with no Notion link ]}
Grouped by task, so "Investors Trust prep (1 of 3)" + "(2 of 3)" become one entry with blocks=2.
The caller then checks each task's Status in Notion: Done = nothing to do; not Done = missed.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

NOTION = re.compile(r"https?://(?:app\.|www\.)?notion\.(?:so|com)/\S*?([0-9a-f]{32})", re.I)


def when(e, key):
    v = e.get(key, {})
    if "dateTime" in v:
        return datetime.fromisoformat(v["dateTime"].replace("Z", "+00:00"))
    return None  # all-day: not a focus block


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("events_json")
    ap.add_argument("--prefix", default="🎯 Focus:")
    ap.add_argument("--tz", default="America/New_York")
    a = ap.parse_args()

    raw = json.load(sys.stdin if a.events_json == "-" else open(a.events_json))
    events = raw if isinstance(raw, list) else raw.get("events", [])
    tz = ZoneInfo(a.tz)
    now = datetime.fromisoformat(raw["now"]) if isinstance(raw, dict) and raw.get("now") else datetime.now(tz)
    end_of_today = now.astimezone(tz).replace(hour=23, minute=59, second=59)

    buckets = {"passed": {}, "running": {}, "upcoming_today": {}}
    no_link = []
    for e in events:
        title = e.get("summary", "")
        if not title.startswith(a.prefix) or e.get("status") == "cancelled":
            continue
        s, en = when(e, "start"), when(e, "end")
        if not s or not en:
            continue
        if en <= now:
            b = "passed"
        elif s <= now:
            b = "running"
        elif s <= end_of_today:
            b = "upcoming_today"
        else:
            continue
        m = NOTION.search(e.get("description", "") or "")
        if not m:
            no_link.append(title)
            continue
        tid = m.group(1)
        g = buckets[b].setdefault(tid, {"task_id": tid, "task_url": m.group(0), "titles": [],
                                        "event_ids": [], "blocks": 0, "minutes": 0,
                                        "first_start": s, "last_end": en})
        g["titles"].append(title[len(a.prefix):].strip())
        g["event_ids"].append(e.get("id"))
        g["blocks"] += 1
        g["minutes"] += int((en - s) / timedelta(minutes=1))
        g["first_start"] = min(g["first_start"], s)
        g["last_end"] = max(g["last_end"], en)

    def out(d):
        rows = sorted(d.values(), key=lambda g: g["first_start"])
        for g in rows:
            g["first_start"] = g["first_start"].astimezone(tz).isoformat()
            g["last_end"] = g["last_end"].astimezone(tz).isoformat()
        return rows

    print(json.dumps({"now": now.astimezone(tz).isoformat(),
                      **{k: out(v) for k, v in buckets.items()},
                      "no_task_link": no_link}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
