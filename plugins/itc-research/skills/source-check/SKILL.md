---
name: source-check
description: >
  Fact-check and source every number and claim in a model, note, pitch, or chat answer before Dana
  sends it. Opens the actual file (Excel Online/OneDrive/SharePoint in Chrome, local .xlsx, Notion
  page, deck), traces each figure to a primary source (SEC filing, press release, Cap IQ, the cited
  article), and returns a claim-by-claim table: Verified / Partly verified / Unverified / Wrong, with
  links. Use when Dana says "source check", "check the sources", "make sure this is right", "where did
  you get X", "verify this before I send it", or a teammate asks where a number came from.
metadata:
  version: "0.1.0"
---

# Source check

The goal: every number Dana sends can be traced to something a reader can click and confirm. Say plainly what you could and couldn't confirm. Never upgrade a guess to "verified".

## 1. Collect the claims

- List every claim being checked: what Dana or a teammate asked about, plus anything else load-bearing in the same answer (prices, share counts, multiples, rates, balance-sheet lines, comps, deal terms).
- Pull Dana's notes first. Search Notion for the deal or ticker (task pages under Dana's Dashboard / Tasks often hold "Model Changes" pages with the reasoning and sources). Notes say what was claimed and where it supposedly came from. They are not proof.

## 2. Check the file itself

- **Shared Excel (OneDrive/SharePoint link):** ask Dana for the link if it isn't in the notes. Open it in a new Claude-in-Chrome tab. Jump with the Name Box (type a cell, press Return) and take screenshots of the input block, debt schedule, S&U, and returns. **Read only, never edit**: it's usually someone else's file and teammates may be in it live.
- **Local .xlsx:** unzip and grep `xl/sharedStrings.xml` and `xl/worksheets/*.xml` (openpyxl may not be installed).
- For each claim, record the cell, its value, and its label. Flag:
  - labels that don't match the math (e.g. a column headed "x EBITDA" holding x TBV values)
  - stale dates or prices
  - hardcodes where a link is expected
  - per-share × shares that a reader could mistake for market cap

## 3. Trace to primary sources (best first)

1. **SEC filings:** the 10-Q/10-K balance sheet and cover page (share count), and the earnings press release (Ex. 99.1). Recompute derived figures yourself. Example: TBV = common equity − goodwill − intangibles, then divide by shares.
2. **Cap IQ / FactSet:** cite the screen (e.g. "Cap IQ Quick Comps, pulled 11/17").
3. **The cited article itself.** Fetch it. If it's paywalled or returns 403, say so. A search-engine snippet is weaker evidence: label it "partly verified (snippet)".
4. **Market or industry ranges:** law-firm, bank, or advisory reports. Use them to bracket an assumption, not to prove a deal-specific number.

Use the `web-fetch` agent for pages and WebSearch for finding them. Run independent fetches in parallel. Ignore AI-rewrite aggregators (allmind.ai and similar) and undated stat sites.

## 4. Report

Give one table, worst problems first:

| Claim | In the file (cell → value) | Source & link | Status | Note |
|---|---|---|---|---|

- Status is **Verified**, **Partly verified**, **Unverified**, or **Wrong**.
- After the table, list the fixes to the file, in order of impact.
- If a teammate asked, add a short reply Dana can paste, with sources linked.
- Offer to add a "Sources" section to the Notion task page. Write to Notion only if Dana says yes.

## Rules

- Never claim a source says something you didn't read. If you saw it only in your own notes or a summary, say that.
- Mention source dates when they matter: a price is as of a close; an article can be months old.
- If the model has changed since the notes were written, check the model, and say the notes are stale.
