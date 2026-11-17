---
name: approved-list-email
description: >
  Use when Dana wants to condense a completed single-ticker research note (and its Asset Sheet /
  Approved List package) into the short "Team," email that requests adding a ticker to the Approved
  List — "draft the approved list email for X", "summarize this note as an email to add X to the
  approved list", "write the RL/WLY/etc. approved list email". Also use when Dana asks to punch up
  or find better phrasing for a specific line in one of these emails.
metadata:
  version: "0.1.0"
---

# Approved List email

Condense an existing single-ticker research note (plus its Asset Sheet / Approved List package, if
further PM guidance has been given on it) into the short email Dana sends to the group to request
adding a ticker to the Approved List. This is a distillation exercise, not new research — don't add
analysis or numbers the note doesn't already support.

## Before drafting

1. Find the underlying single-ticker note in `Equity Research/Research Notes/Single-Ticker Notes/`
   (or wherever Dana points) and read it in full. A note in Dana's house style already contains two
   documents in one: the numbered analytical body (sections 1-7ish) is the deep-dive backup, and the
   "My Read" section near the end is *already* the condensed, first-person verdict — that section is
   the seed for this email's recommendation stance and closing paragraph, not something to re-derive
   from scratch. Pull the supporting bullets from the body sections it draws on, not from every
   section evenly.
2. The email's content and *emphasis* follow the note's own central analytical question — not a
   separate call or model-build conversation about how the note/model was put together, even if that
   conversation happened right before this request. If Dana has since gotten follow-up PM guidance
   specific to this ticker (an email, a call), fold in anything that changes a number or the
   recommendation itself, but don't let a working conversation about model mechanics leak into the
   email's content.
3. Check the Notion "Approved List Email Examples (Reference)" page (under the Investors Trust
   Company page) for precedent emails (BTSG, VTRS, TPR, JBL, RL) before drafting from scratch.
4. If Dana or the PM has given a one-off instruction for this specific ticker (e.g. "round the
   target," "put valuation last"), apply it to this email only — don't treat it as a new default
   rule unless the same instruction has come up more than once.

## Length

Target roughly 400-600 words, matching BTSG's length (Bob's own example) — a few bullets and a short
close, not a re-summary of the whole note. If a first draft comes out closer to a full note's length,
cut it down before showing it to Dana rather than presenting the long version as the draft.

## Structure

- Subject line: `TICKER — Approved List`
- Open with "Team," then, in the same or next sentence, the recommendation stance: initiate now,
  add now but wait for a macro-driven pullback/dislocation, or "worth considering." State it plainly
  and pair it with a single, brief valuation data point if the note supports one (e.g. "at 20x
  forward earnings after a strong run," "$352 and 22.4x forward earnings"). This opening line is
  normally the *only* place valuation appears — it's a timing signal for the recommendation, not a
  separate analytical section. Only give valuation its own detailed bullet (multiples, bear/base/
  bull) if the underlying note itself goes deep on valuation (e.g. JBL's did), or if the PM has
  specifically asked for it to be broken out and placed last (as with WLY).
- Optionally lead into bullets with "A few things to know about the company:" — fine to keep or cut;
  the bullets can speak for themselves without it.
- 4-5 bullets, each drawn from a distinct part of the note, roughly in this order:
  1. What the business is / the anchor of the model.
  2. The execution track record — a specific multi-year strategy and the hard evidence it's
     working (consecutive quarters of a metric, basis-point margin expansion, beating a stated
     target).
  3. The growth engine, usually geographic or segment-based, with real growth-rate numbers.
  4. The central debate — name it explicitly ("the key debate is X" / "the central question is Y"),
     state the bear read, then management's counter and the evidence for it.
  5. The main risk, quantified and specific, not generic risk-factor boilerplate.
- Close with one tight paragraph that names the thesis type plainly (e.g. "this is a compounder, not
  a turnaround") and restates the recommendation/entry logic. For "wait for a pullback"
  recommendations, frame the trigger as macro-driven weakness or dislocation, not a change in the
  fundamental thesis — see the phrasing bank below.
- Sign off "Best," then Dana's name; include the full title/contact block (Equity Research Intern,
  Investors Trust Company, email, phone, LinkedIn) unless Dana says otherwise for that email.

## Voice

- First-person "I" throughout, even for collective recommendations ("I think we should initiate," "I
  don't think we should do anything with it right now"). Never "we/our/we're" to describe Dana's own
  work — not "we've built," "our price target," "we're sending this" — always "I've built," "my
  price target," "I'm sending this."
- Confident and plain, not hedged. State the debate and take a side ("I find it credible that...")
  rather than presenting both cases neutrally.

## Phrasing bank — recommending a pullback/dislocation entry

When Dana asks to punch up the "wait for a better entry" line, offer a short menu of options from
crisp to more analytical, and recommend one with a one-line reason for the word choice, rather than
picking silently:

- "...so we can move when we get a better entry."
- "...so we're positioned to move on any macro-driven pullback rather than doing the work under
  pressure."
- "...so we can take advantage of any macro-driven dislocation without scrambling to do the work
  first."

"Dislocation" is precise (price moved away from intrinsic value, not that the thesis broke) and
"without scrambling to do the work first" signals good process instincts to a PM — that combination
is usually the strongest option when in doubt, but let Dana pick the tone she wants.

## If Dana wants it shorter

Some requests call for a much tighter version: thesis in two short paragraphs, three bullet
"pillars" instead of four to five, one valuation line, one-sentence recommendation. Offer this as an
alternative length, not a replacement default — the fuller 4-5 bullet structure above is Dana's
established house style (matches BTSG, VTRS, TPR, JBL, RL) and should stay the default unless she
asks for the short version specifically.

## After drafting

Save/insert the draft into the relevant Notion task page (or wherever the note and Approved List
package live) rather than only showing it in chat, matching how prior drafts (JBL, RL, WLY) were
stored alongside their source materials.
