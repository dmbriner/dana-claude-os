#!/usr/bin/env python3
"""Compute open time windows from busy events. Standard library only.

Input: a JSON file (or stdin with "-") shaped like
  {"from": "2026-11-17", "to": "2026-11-20",            # inclusive dates
   "events": [
     {"start": "2026-11-17T09:30:00-05:00", "end": "2026-11-17T10:45:00-05:00",
      "label": "BUSI408", "kind": "busy"},               # booked: blocks time
     {"start": "...", "end": "...", "label": "CC: Jane Doe", "kind": "offer"}  # offered, not accepted: does NOT block
   ]}

Copy start/end exactly as the calendar API returns them, WITH their UTC offset
(e.g. -05:00). Ignore the event's separate "timeZone" field: the offset is the truth.
All-day events and events marked "transparent"/free should be left out or given kind "free".

Settings (day_start, day_end, min_window_minutes, buffer_minutes, home_tz) come from
private/profile.json -> "scheduling", and can be overridden with flags.

Output: open windows per day in home_tz, optionally also in a second zone (--also America/Los_Angeles),
with any "offer" holds that overlap each window listed so Dana can see what's double-offered.
"""
import argparse
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]


def load_settings():
    try:
        return json.loads((ROOT / "private" / "profile.json").read_text()).get("scheduling", {})
    except FileNotFoundError:
        return {}


def hm(s):
    h, m = s.split(":")
    return time(int(h), int(m))


def fmt(dt):
    return dt.strftime("%-I:%M %p").replace(":00 ", " ")


SHORT = {"America/New_York": "ET", "America/Chicago": "CT", "America/Denver": "MT",
         "America/Los_Angeles": "PT", "Europe/London": "UK"}


def main():
    s = load_settings()
    ap = argparse.ArgumentParser()
    ap.add_argument("events_json")
    ap.add_argument("--day-start", default=s.get("day_start", "08:00"))
    ap.add_argument("--day-end", default=s.get("day_end", "21:00"))
    ap.add_argument("--min", type=int, default=s.get("min_window_minutes", 30))
    ap.add_argument("--buffer", type=int, default=s.get("buffer_minutes", 15))
    ap.add_argument("--tz", default=s.get("home_tz", "America/New_York"))
    ap.add_argument("--also", help="second time zone to show, e.g. America/Los_Angeles")
    ap.add_argument("--skip-weekends", action="store_true")
    a = ap.parse_args()

    data = json.load(sys.stdin if a.events_json == "-" else open(a.events_json))
    tz = ZoneInfo(a.tz)
    also = ZoneInfo(a.also) if a.also else None
    buf = timedelta(minutes=a.buffer)

    busy, offers = [], []
    for e in data["events"]:
        if e.get("kind", "busy") == "free":
            continue
        st, en = datetime.fromisoformat(e["start"]), datetime.fromisoformat(e["end"])
        if st.tzinfo is None or en.tzinfo is None:
            sys.exit(f"event {e.get('label')!r} has no UTC offset; copy start/end with their offset")
        st, en = st.astimezone(tz), en.astimezone(tz)
        (offers if e.get("kind") == "offer" else busy).append((st, en, e.get("label", "")))

    d, last = date.fromisoformat(data["from"]), date.fromisoformat(data["to"])
    while d <= last:
        if a.skip_weekends and d.weekday() >= 5:
            d += timedelta(days=1)
            continue
        cur = datetime.combine(d, hm(a.day_start), tz)
        day_end = datetime.combine(d, hm(a.day_end), tz)
        blocks = sorted((max(st - buf, cur), min(en + buf, day_end), lab)
                        for st, en, lab in busy if st < day_end + buf and en > cur - buf)
        windows = []
        for st, en, _ in blocks:
            if st > cur:
                windows.append((cur, st))
            cur = max(cur, en)
        if day_end > cur:
            windows.append((cur, day_end))
        windows = [w for w in windows if (w[1] - w[0]) >= timedelta(minutes=a.min)]

        print(d.strftime("%a %-m/%-d"))
        if not windows:
            print("  (no open windows)")
        for ws, we in windows:
            line = f"  {fmt(ws)} - {fmt(we)} {SHORT.get(a.tz, a.tz)}"
            if also:
                line += f"   ({fmt(ws.astimezone(also))} - {fmt(we.astimezone(also))} {SHORT.get(a.also, a.also)})"
            ov = [lab for st, en, lab in offers if st < we and en > ws]
            if ov:
                line += "   [also offered to: " + ", ".join(sorted(set(ov))) + "]"
            print(line)
        d += timedelta(days=1)


if __name__ == "__main__":
    main()
