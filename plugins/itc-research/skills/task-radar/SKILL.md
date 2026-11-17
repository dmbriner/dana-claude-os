---
name: task-radar
description: >
  This skill should be used when Dana asks what's outstanding, what she should be working on, "what's
  due", "what am I behind on", or "what should I pick up next". Scans her Equity Research folder,
  Notion tasks, and calendar to surface open research work and flag what's coming due.
metadata:
  version: "0.1.0"
---

# Task radar

Identify what ITC research work is outstanding and surface it in priority order.

## What to check

1. **Notion tasks**: query Dana's Notion workspace for open tasks (use the notion-api skill / connected Notion tools), especially any created by `capture-call-feedback`.
2. **Calendar**: check for upcoming earnings dates, meetings, or deadlines in the next two weeks (use the connected calendar tools).
3. **Catalyst calendar**: read `Equity Research/catalyst-calendar.md` if it exists (maintained by `thesis-catalyst-tracker`) for dated items.
4. **Draft state**: look for notes in `Equity Research/Research Notes/` that look unfinished (e.g., a `v01` with no PM feedback logged yet, or a ticker with a model but no note) versus names that were screened but never got a full single-ticker note.
5. **Thesis staleness**: check `thesis-log.md` files for tickers that haven't had an entry in a while relative to how often Dana typically updates them.

## Output

Present a short, prioritized list — soonest deadlines first, then anything overdue, then general open items. For each item: what it is, why it's on the list (source: Notion task / calendar / stale draft / etc.), and a suggested next step. Don't just dump every open item flatly; group by urgency and say plainly if nothing is time-sensitive right now.

If a source (Notion or Calendar) isn't connected, note that plainly rather than silently omitting it, since it means the picture is incomplete.
