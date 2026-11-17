---
name: morning-note
description: >
  This skill should be used when Dana asks for a morning note, meeting prep, or a summary of
  overnight developments across her coverage — "morning note", "what happened overnight", "prep me
  for the morning meeting". Produces a tight, opinionated summary for the daily meeting, not a full
  research note.
metadata:
  version: "0.1.0"
---

# Morning note

Draft a concise morning-meeting note covering overnight developments across Dana's coverage names and watchlist.

## Steps

1. Read `house-style.md` for tone, but keep this format tight — this is meeting prep, not a full research note. Aim for a page or less.
2. Check for overnight news, earnings, or filings on covered names (the tickers with folders under `Equity Research/`) and anything flagged as due today by `task-radar`.
3. For each item worth mentioning: one or two sentences on what happened, one sentence on why it matters to the position or thesis, and — if relevant — a specific trade idea or watch item.
4. Flag anything that needs a decision today (e.g., an earnings reaction, a thesis-break condition that just triggered).

## Format

- Short header with the date
- Bulleted by ticker or theme, tightest version of the news possible
- End with "Today's action items" if anything needs a decision or follow-up

Do not save this to a permanent note file unless Dana asks — it's meant to be read and acted on, not archived like a research note.
