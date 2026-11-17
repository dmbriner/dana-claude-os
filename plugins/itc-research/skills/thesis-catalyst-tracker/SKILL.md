---
name: thesis-catalyst-tracker
description: >
  This skill should be used when Dana wants to update or check a thesis on a covered name, review
  whether a thesis is still intact, or track upcoming catalysts — "update the thesis for [ticker]",
  "is my [ticker] thesis still intact", "what catalysts are coming up", or "add a catalyst for
  [ticker]". Maintains a running thesis and catalyst log per ticker rather than a one-off note.
metadata:
  version: "0.1.0"
---

# Thesis & catalyst tracker

Maintain a living thesis and catalyst record for Dana's covered names.

## Where it lives

Maintain `Equity Research/<TICKER>/thesis-log.md` per covered ticker (create the file the first time a thesis is logged for that name) and a shared `Equity Research/catalyst-calendar.md` across all names. If these don't exist yet, create them — don't ask permission to create a tracking file, just do it and tell Dana afterward.

## Updating a thesis

1. Read the existing `thesis-log.md` for the ticker if present, plus the most recent single-ticker or compare note for that name for context.
2. Append a dated entry: what changed, whether the thesis is intact/strengthened/challenged, and whether any thesis-break condition from the underlying note has moved closer to triggering.
3. If a thesis-break condition has actually triggered, say so plainly and flag it to Dana rather than softening it.

## Catalyst calendar

1. Track upcoming, dated events per ticker: next earnings date, analyst days, lockup expiries, regulatory decisions, Investment Strategy Committee dates, anything the PM has specifically flagged to watch.
2. When asked "what catalysts are coming up," read `catalyst-calendar.md` and return items sorted by date, flagging anything inside the next two weeks first.
3. When `capture-call-feedback`, `earnings-update`, or `approved-list-package` surfaces a new dated item, add it here and offer to also put it on Dana's calendar.

## Checking thesis intact-ness

When asked "is my thesis on X still intact," compare the current thesis-break conditions against the latest available data (news, filings, FactSet) before answering — don't just restate the old thesis.
