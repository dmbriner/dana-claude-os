---
name: deep-dive
description: Run a full internet deep dive on a person, their firm and group, and their deals, using three specialist agents in parallel (person-researcher, firm-researcher, deal-researcher), and build one comprehensive Notion dossier with everything in one place. Use when Dana says "deep dive on <name/firm/deal>", "find everything on", "I want to see everything", "comprehensive prep", "deal prep for <firm>", or runs /deep-dive. Lighter versions: coffee-chat-prep (one-screen brief) and research-sources (quick lookup).
---

# Deep dive: person + firm + deals

This is the comprehensive version: everything there is to know, on one Notion page, sourced. Use it before interviews, superdays, and important calls. For a quick one-screen brief, use `coffee-chat-prep` instead.

First load `private/profile.json` (Notion IDs, `career_root`) and `private/story.md` from the repo root (resolve this file's symlink, then walk up to `.claude-plugin/marketplace.json`).

## 1. Scope it

From Dana's message, work out:
- **Person(s):** zero or more. A superday panel means one per interviewer.
- **Firm and group.**
- **Deals:** any named deals, or a Krugman Insights or other link.
- **Window:** default the last 18 months.
- **Why:** coffee chat, interview, superday, or curiosity. This changes what to emphasize.

Pull what Dana already has: the Notion People page(s), the Firms page, Opportunities, the iCloud `Recruitment/Firms/<Firm>/` folder, and any earlier coffee-chat-prep or interview-prep brief. Pass all of it to the agents so they don't start cold.

Ask Dana only if the person or firm is ambiguous. Otherwise go.

## 2. Dispatch the specialists in parallel

Send these in one message so they run at the same time. Give each one the scope, what Dana already has, and the reason for the dive.

- `person-researcher`: one per person.
- `firm-researcher`: the firm plus the group.
- `deal-researcher`: the group's deal list for the window, plus full cards for named deals or the top 3 to 5. Tell it which people are involved, so it can flag any deal that names them.

While they run, read anything Dana pasted (bios, links) yourself.

## 3. Check and merge

- **Cross-check:** where the agents disagree (titles, dates, deal sizes), check the primary source and keep the right one.
- **Connect the threads:** mark which deals the person is named on, which deals happened in their group while they were there, and how the firm's strategy shows up in the deals.
- **Gaps:** collect them into one "Still missing / where to look" list (e.g. LinkedIn, Capital IQ or PitchBook through UNC, or asking the person).
- **Wrong numbers:** if a number can't be sourced, cut it.

## 4. Build the Notion dossier

Create one page titled `Deep Dive – <Person or Firm Group> – <Month D, YYYY>`:
- With a person: a child page under their People page.
- Firm only: under the firm's Firms page.

Use toggles for long sections so it stays navigable, and a Lucide-style line icon (never a colored Notion icon).

1. **TL;DR:** 5 bullets, the things to know if Dana reads nothing else.
2. **The person:** career timeline table, education and activities, licenses, deals named to them, team map, public appearances, hooks, overlap with Dana.
3. **The firm:** snapshot table, segment financials, strategy and news timeline, competitors.
4. **The group:** coverage, leaders, structure, rankings, what juniors do.
5. **Deal list:** a table with Date · Deal · Type · Size · Firm's role · Person named? · Status · Source.
6. **Deal breakdowns:** one toggle per major deal with the full card (terms, valuation, advisors by role, timeline, rationale, use of proceeds, market reaction, interview angles).
7. **Market backdrop:** 3 to 5 trends, each with why it matters.
8. **Recruiting:** program, timeline, open postings, interview format, comp.
9. **Your angles:** why this firm, why this group, and 2 to 3 honest links to Dana's experience from `story.md`.
10. **Questions to ask:** 8 to 12, with the best 3 starred.
11. **Interview drill:** the likely questions on this firm and its deals, with short answers, so Dana can quiz herself.
12. **Still missing / where to look.**
13. **Sources:** numbered, with dates.

Also:
- Update empty or outdated properties on the People and Firms rows (Role & About, Level, Location, Key Takeaways). Never overwrite Dana's notes.
- Save a .docx copy to `<career_root>/Recruitment/Firms/<Firm>/Research/Deep Dive – <name> <YYYY-MM-DD>.docx`: write HTML in the scratchpad, then run `textutil -convert docx`.

## 5. Reply in chat

Give a 4 to 5 line summary: the most important finding, the deal to know cold, the best question, the biggest gap, and the Notion link.

## Getting better over time

- A source that worked unusually well: add it to `research-sources`.
- A section Dana says she never reads, or wants more of: update this file.
- Commit and push changes to the repo.

## Rules

- Read only. Never contact anyone, sign up, pay, or submit anything.
- Every fact has a source. Nothing is invented. Say "the person worked on it" only when a source names them.
- No personal data in this skill file.
