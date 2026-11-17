# ITC Equity Research — House Style (seed)

This is the starting version of Dana's house style, seeded from her actual ITC notes (APH single-ticker note, APH vs. TEL compare note, RDDT/TKO/MTCH/WLY screening note) and from the Feedback/Criticisms sheets in her `ITC Brag Book.xlsx`.

Skills in this plugin should copy this file to `house-style.md` inside Dana's Investors Trust > Equity Research folder the first time it's needed, then read and update that copy going forward — this seed file itself should not be edited at runtime.

## Note structure

- Masthead: "INVESTORS TRUST COMPANY — INTERNAL RESEARCH NOTE"
- Title states the tension/debate, not a neutral label — plus a one-line subhead sharpening it further.
- Byline: "Dana Briner | Month Year"
- Sources line naming exactly what was used (10-Ks, 10-Qs, transcripts, FactSet, dates covered).
- "Overview" section states the position and the central analytical question up front.
- Numbered body sections, each resolving one piece of the central question.
- "My Read" section near the end: an explicit, first-person verdict, not a hedge.
- "Thesis-break conditions" as the final section: specific, measurable, falsifiable triggers.

## Fact / opinion separation

- Every factual claim traces to a named source.
- Distinguish "management says X" from "the record independently supports X."
- Quote management directly when characterizing their own framing.

## Valuation

- Don't lean on a single DCF — pair it with relative valuation.
- Include absolute forward P/E versus the market (~17x, forward earnings, weight next full year's estimates).
- Include peer/relative comps and justify why each chosen multiple fits the business (e.g. EV/EBITDA for capex-heavy names).
- Compare the current multiple to the company's own trailing 5-year average, not just to peers.

## Risk sections

- Risks get their own explicit section, never implicit in the narrative.
- Separate the central-question risk from secondary risks.
- If a risk is genuinely unresolved or unquantifiable, say so plainly instead of forcing a verdict.

## Testing management claims

- Never accept a management explanation at face value — test it against the filed record.
- Call out when management has not addressed something it plausibly should have.

## Thesis-break conditions

- Specific and falsifiable: a number, a threshold, a named metric, over a stated period.
- Avoid vague language like "if fundamentals deteriorate."

## File naming & filing convention

- `YYYY-MM-DD_ITC_<TICKER>[vTICKER]<NoteType>_DanaBriner_v0N.docx`
- Single-ticker notes → `Equity Research/Research Notes/Single-Ticker Notes/`
- Compare notes → `Equity Research/Research Notes/Compare Notes/`
- Screening notes → `Equity Research/Research Notes/Screening Notes/`
- Bump the version suffix rather than overwriting a prior draft.

## Feedback log

Appended by `capture-call-feedback`. Starts empty in this seed — real entries accumulate in the copy inside Dana's Equity Research folder.

| Date | Source | Feedback | Action taken | Status |
|---|---|---|---|---|
