---
name: single-ticker-note
description: >
  This skill should be used when Dana asks to write an ITC single-ticker research note, a deep dive
  on one company, an initiation writeup, or says things like "write a note on $TICKER", "deep dive on
  [company]", or "draft a research note for [ticker]". Produces a full single-ticker note in Dana's
  ITC house style: a central analytical question, sourced fact/opinion separation, valuation against
  the company's own history, and falsifiable thesis-break conditions.
metadata:
  version: "0.1.0"
---

# Single-ticker research note

Write an Investors Trust Company internal research note on one ticker, in Dana's house style.

## Before drafting

1. Read the house style. Look for `house-style.md` in Dana's Investors Trust > Equity Research folder (the folder that also contains "Research Notes", "Models", and "FactSet Data" subfolders). If it does not exist yet, copy `references/house-style-seed.md` from this skill into that location as `house-style.md`, then read it.
2. Identify the central analytical question for this ticker before writing anything. Do not start from "what does this company do" — start from the specific tension or debate that makes this name worth a note right now (a valuation gap, a disputed growth driver, a management claim worth testing). If the tension isn't obvious, ask Dana what prompted the note, or look at FactSet data / filings / transcripts already saved for this ticker.
3. Gather sources: 10-Ks, 10-Qs, the most recent earnings transcript, investor day materials, and FactSet data. Check `FactSet Data/<TICKER>` and `Equity Research/<TICKER>` first before searching the web — Dana often already has the primary sources saved there.

## Structure (house-style.md is the source of truth if it has evolved since this was written)

1. Masthead: "INVESTORS TRUST COMPANY — INTERNAL RESEARCH NOTE"
2. Title stating the tension/debate, not a neutral label, plus a one-line subhead sharpening it
3. Byline: "Dana Briner | [Month Year]"
4. Sources line
5. Overview: state the position and central question up front
6. Numbered body sections, each resolving one piece of the central question
7. Valuation section: pair relative valuation (forward P/E vs. market, peer comps, EV/EBITDA where capex-heavy) with the company's own 5-year historical multiple range — never rely on DCF alone
8. Risk section: separate the central-question risk from secondary risks; state plainly when something is genuinely unresolved rather than forcing a verdict
9. "My Read": an explicit first-person verdict, not a hedge
10. "Thesis-break conditions": specific, measurable, falsifiable triggers

## Sourcing discipline

Every factual claim needs a named source. Distinguish "management says X" from "the record independently supports X." Quote management directly when characterizing their own framing. Before finalizing, independently test at least one material management claim against the filed record rather than repeating it.

## Save the file

Name it `YYYY-MM-DD_ITC_<TICKER>ResearchNote_DanaBriner_v01.docx` (bump the version if a draft already exists for this ticker/date) and save it to `Equity Research/Research Notes/Single-Ticker Notes/`. Use the docx skill to produce the file.

## Before delivering

Suggest running the `itc-reviewer` agent on the draft before Dana sends it, especially if this is a first draft.
