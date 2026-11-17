---
name: earnings-update
description: >
  This skill should be used when Dana asks for an earnings preview or post-earnings update on a
  covered name — "preview [ticker] earnings", "[ticker] just reported, write it up", "earnings
  update for [ticker]", or after Dana pastes an earnings call transcript for a name she covers.
  Produces a beat/miss and guidance-focused update in Dana's house style, and flags anything to
  calendar for the next print.
metadata:
  version: "0.1.0"
---

# Earnings preview / update

Write a pre- or post-earnings note for a covered ticker.

## Before drafting

1. Read `house-style.md` from the Equity Research folder.
2. Determine whether this is a preview (before the print) or an update (after). For a preview, set out what to watch and what would move the stock. For an update, lead with beat/miss vs. guidance and consensus, then work through what changed in the thesis.
3. Pull the most recent transcript, filing, and guidance history from `FactSet Data/<TICKER>` if available.

## Structure — post-earnings update

1. Masthead + title stating the headline result and its read-through, not just "$TICKER Q2 results"
2. Overview: beat/miss vs. guidance and consensus, and whether the thesis is intact, strengthened, or challenged
3. Segment/numbers detail relevant to the thesis (not a rehash of every line item)
4. Guidance change and what it implies
5. Updated "My Read" and thesis-break conditions if they've moved

## Structure — preview

1. Title framing what's actually at stake this print
2. Key metrics/guidance to watch, and the specific evidence that would move each side of the debate
3. Scenario framing (beat/inline/miss) tied to what each would mean for the thesis

## After drafting

If the note references anything with a hard date (next print, an analyst day, a lockup expiry), flag it to Dana and offer to add it to her calendar and to the catalyst list maintained by `thesis-catalyst-tracker`.

## Save the file

`YYYY-MM-DD_ITC_<TICKER>EarningsNote_DanaBriner_v01.docx` in `Equity Research/Research Notes/Earnings Notes/` (create that subfolder if it doesn't exist yet).
