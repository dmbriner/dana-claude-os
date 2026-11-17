---
name: approved-list-package
description: >
  This skill should be used when Dana needs an Approved List package built or updated for the
  Investment Strategy Committee — "build the approved list package for [ticker]", "update the ALC
  package for [ticker]", or "get [ticker] ready for Investment Strategy Committee". Produces the
  one-page snapshot format Dana already uses (price/valuation header, numbered Investment Thesis,
  numbered Issues/Concerns, multi-year financial snapshot, analyst ratings) condensed from her
  existing research rather than researched from scratch.
metadata:
  version: "0.1.0"
---

# Approved List package

Build (or refresh) the one-page Approved List package Dana submits to the Investment Strategy Committee, in the format already established by her prior packages (e.g. `VTRS_Approved_List_Package_v2.pdf` in her Equity Research folder).

## Don't re-research — condense

This package should draw on work that already exists, not duplicate it:

1. Look for the most recent single-ticker note on this name in `Equity Research/Research Notes/Single-Ticker Notes/` and the most recent model in `Equity Research/Models/`. If neither exists, tell Dana and offer to run `single-ticker-note` first rather than improvising thin research.
2. Pull header stats (current price, price target, 52-week high/low, market cap, 3-yr beta, operating margin, pre-tax margin, ROE, EPS by year, PEG, P/E, long-term growth, FCF/total debt, debt/total cap, dividend yield, analyst buy/hold/sell counts) from FactSet data already saved under `FactSet Data/<TICKER>/` where available; only pull fresh data for anything missing.
3. Pull a 3-year financial snapshot (revenue, gross income, EBITDA and margin, EBIT and margin, net income and margin, diluted EPS, cash & ST investments, total assets, total liabilities) from the same FactSet sources or the model.

## Structure (match the existing format)

1. Header block: company name, ticker, date, current price, price target, 52-week range, market cap, beta, margin/ROE stats, earnings by year, PEG/P/E/growth, FCF/debt, div yield, analyst ratings tally
2. **Investment Thesis** — 3-5 numbered points, condensed from the central analytical question and supporting sections of the existing single-ticker note. Keep each point to 2-3 sentences; this is a summary for a committee, not the full note.
3. **Issues/Concerns** — numbered points condensed from the note's risk section, kept to the items that actually matter for a purchase decision.
4. Multi-year financial snapshot table (5-yr average plus the last 3 fiscal years, actual and estimated as available).
5. Price chart reference if the source data includes one; otherwise note current price vs. 52-week range in text.

## Output

Produce this as a single-page PDF (use the pdf skill) unless Dana asks for pptx or xlsx instead. Name it `<TICKER>_Approved_List_Package_v0N.pdf` and save alongside the existing packages in `Equity Research/` (or `Equity Research/<TICKER>/` if that ticker has its own subfolder).

## After building

Ask Dana whether this package is going to a specific Investment Strategy Committee date. If so, offer to add that date to her calendar and to `catalyst-calendar.md` via `thesis-catalyst-tracker`, and log the submission in `thesis-log.md` for the ticker so the decision is tracked alongside the rest of the thesis history.
