---
name: compare-contrast-note
description: >
  This skill should be used when Dana asks to compare two tickers, test whether a concern about one
  name transfers to another, or decide between two positions — e.g. "compare $A and $B", "write a
  compare/contrast note on X vs Y", or "does the [ticker] thesis apply to [ticker] too". Produces an
  ITC compare note in Dana's house style built around one standing question, not a side-by-side dump.
metadata:
  version: "0.1.0"
---

# Compare / contrast research note

Write an Investors Trust Company internal research note comparing two tickers against one standing question, in Dana's house style.

## Before drafting

1. Read `house-style.md` from Dana's Investors Trust > Equity Research folder (create it from `references/house-style-seed.md` in this skill if missing).
2. Nail down the single standing question the comparison answers before writing — e.g. "does the risk that broke down Company A's multiple also apply to Company B," or "which of these two deserves the Approved List slot." A compare note is not two single-ticker notes stapled together.
3. Gather sources for both names: 10-Ks, 10-Qs, most recent transcripts, investor materials. Check `FactSet Data/<TICKER>` and `Equity Research/<TICKER>` for each ticker first.

## Structure

1. Masthead + title framing the comparison as a question or tension (not "$A vs $B")
2. Byline, sources line
3. Overview: state the standing question and where the note comes down
4. "What each company does" section, kept tied to what's relevant to the standing question — not a full business-model dump for both
5. Sections working through the standing question point by point, drawing on both names
6. Valuation: compare each company's current multiple to its own history as well as to the other, using relative valuation methods (not DCF alone)
7. Risk section covering both names
8. "My Read" with an explicit call on the standing question
9. "Thesis-break conditions" — specific and falsifiable, for whichever position the note argues for

## Save the file

Name it `YYYY-MM-DD_ITC_<TICKERA>v<TICKERB>Note_DanaBriner_v01.docx`, saved to `Equity Research/Research Notes/Compare Notes/`.

## Before delivering

Suggest running `itc-reviewer` on the draft.
