---
name: deep-dive
description: The most comprehensive research Dana can get on a firm, a group, a person, or a deal. A team of specialist agents (person, firm, deal, market researchers, then an interview coach and a fact-checker) builds an interactive web dossier, a Notion page, a Word copy, and a deep-dive email. Use when Dana says "deep dive on <name/firm/deal>", "I have an interview at <firm>, help me understand it", "what does <firm> do", "find everything on", "I want to see everything", "deal prep for <firm>", "break down <deal>", or runs /deep-dive. Every request gets the full treatment. Lighter versions: coffee-chat-prep (one-screen brief), research-sources (quick lookup).
---

# Deep dive

Every deep dive is the maximum version. It's comprehensive, sourced, and beautiful, and nothing is held back to save time. One run produces:

1. an **interactive web dossier** (an Artifact): tombstones for every deal, charts, a team map, and a flashcard drill
2. a **Notion page** that links to everything
3. a **Word copy** in iCloud
4. a **Deep Dive email** to Dana, separate from the Daily Recruiting Brief

First load `private/profile.json` (Notion IDs, `career_root`, `newsletter_to`) and `private/story.md` from the repo root. To find the root, resolve this file's symlink, then walk up to `.claude-plugin/marketplace.json`.

## 1. Pick the mode

Read Dana's message and pick one mode. Ask only if the firm or person is ambiguous.

| Mode | Trigger | Who runs |
|---|---|---|
| **firm**: understand a firm for an interview | "I have an interview at Citi", "what does Evercore do", "deep dive on Citi M&T" | firm + deal + market researchers |
| **person**: one person, plus their firm and group | "deep dive on <name>", coffee chat or call prep | person + firm + deal + market researchers |
| **panel**: superday interviewers | a list of names at one firm | one person-researcher per name + firm + deal + market |
| **deal**: one deal from every angle | a deal name or a Krugman deal link | deal (5+ related deals as context) + market + firm (the bank's role) |

Firm mode is the default when only a firm is named. It answers the questions an interviewer will test:
- What does the firm do, and how does it make money?
- What does this group do?
- What deals has it done, and what's the market like?
- Why do you want to be here?

If no group is named, cover the firm's main banking groups briefly, then go deep on the one tied to Dana's open Opportunity at that firm, or ask which one.

Before dispatching, gather what Dana already has and pass it to every agent:
- Notion People, Firms, and Opportunities
- `Recruitment/Firms/<Firm>/` in iCloud
- earlier coffee-chat-prep or interview-prep briefs

## 2. Wave 1: research in parallel

Send all of these in ONE message so they run at the same time. Give each agent:
- the mode
- the scope (firm, group, people, deals, window: default last 18 months)
- the purpose (interview date, call)
- everything Dana already has
- the path to `assets/schema.md`, so it returns JSON in the right shape alongside its Markdown

The agents:
- `person-researcher`: one per person (person and panel modes).
- `firm-researcher`: the firm and the group.
- `deal-researcher`: the full deal list and 5+ full breakdowns. Tell it the people's names, so it flags any deal that names them.
- `market-researcher`: trends plus chart data (stock price, volumes, multiples).

While they run, read anything Dana pasted yourself, and start the JSON file at `<scratchpad>/deep-dive/<slug>.json`.

## 3. Merge

Combine the agents' JSON into one dossier file:
- Renumber sources into one list and remove duplicate URLs.
- Settle any conflicts between agents using the primary source.
- Mark `person_named` on deals that name the person.
- Write `kpis` (the 4 to 6 numbers that define this firm or group) and `tldr` (5 bullets) yourself.

## 4. Wave 2: coach and fact-check in parallel

Send both in one message:
- `interview-coach`: give it the merged JSON path. It returns `drill`, `questions`, `angles`, and the polished deal `pitch` and `qa` text.
- `fact-checker`: give it the merged JSON path. It returns a verification table and the edits.

Apply the coach's output and every fact-checker fix. Cut anything marked Wrong. Then build the page:

```
python3 -I <skill dir>/build.py <slug>.json <scratchpad>/deep-dive/<slug>.html
```

Fix every ERROR. For each WARN under the quality bar, go back and fill the gap (dispatch the relevant agent again with a narrow ask), unless the material truly doesn't exist. If it doesn't, add that to `gaps`.

## Quality bar (every run)

- 25+ sources, all opened. Filings and firm releases come first.
- 12+ deals listed, and 4+ with full breakdowns. Deal mode: every angle of the one deal, plus 5 related deals.
- 3+ charts. Always include the firm's share price over 12 months when it's public, its revenue by segment, and the group's or sector's deal volume.
- 4+ market trends, each with a number and "why it matters."
- 40+ drill cards across all topics, and 10+ questions to ask with the best 3 starred.
- Person modes: a full career timeline with dates, a team map, and hooks.
- A gaps list naming exactly where to look (Capital IQ or PitchBook via UNC, LinkedIn, or ask them).
- Zero unsourced numbers.

## 5. Publish

1. **Web dossier.** Publish `<slug>.html` with the Artifact tool:
   - `icon`: "briefcase"
   - `description`: one sentence on what it covers
   - the page title is the firm and group or the person's name, e.g. "Citi Media & Telecom" or "<Person> · <Firm>"

   It's private to Dana by default. Don't share it.
2. **Notion.** Create `Deep Dive – <Title> – <Month D, YYYY>`:
   - Where: under the person's People page (person modes), or under the firm's Firms page (firm and deal modes).
   - Icon: a Lucide-style line icon.
   - Content: the dossier link at the top, then TL;DR, KPIs, the deal table, the questions, the gaps, and toggles holding the full breakdowns and sources.
   - **Every question is a toggle** (Dana's ask, 2026-11-19): questions to ask, deal Q&A, and drill cards each go in their own toggle with the question as the title and the answer or "why ask" note inside, in Notion and in the web dossier (the template already does this).
   - Update empty or outdated properties on People and Firms rows (Role & About, Level, Location, Key Takeaways). Never overwrite Dana's notes.
3. **Word copy.** Save it to `<career_root>/Recruitment/Firms/<Firm>/Research/Deep Dive – <Title> <YYYY-MM-DD>.docx` (write HTML, then run `textutil -convert docx`).
4. **Audio briefing (optional).** If the `notebooklm` skill works in this session, load the dossier and its top sources into a notebook and generate an Audio Overview for Dana to listen to on the way to the interview. Skip it silently if NotebookLM isn't set up.
5. **Email.** See below.

## 6. The Deep Dive email

Send it with the Gmail connector to `newsletter_to` in profile.json and to no one else. This is Dana's own inbox, the same as the Daily Recruiting Brief, but a separate email.

**Subject:** `Deep Dive – <Title> – <Weekday, Month D>`

HTML if supported, otherwise clean plain text, built to read on a phone:

1. **Header:** title, mode, purpose and date, and three links (web dossier, Notion page, Word file).
2. **In 30 seconds:** the TL;DR bullets.
3. **The numbers:** the KPI table.
4. **Deals to know cold:** the top 5 deals as a table (Date · Deal · Size · Role), each with a one-line "why it matters."
5. **The person** (person modes): current role, path in 3 lines, and the best hook.
6. **Market in 3 lines.**
7. **Your 3 best questions.**
8. **Practice now:** 5 drill questions, then "Answers below," then the answers.
9. **Still missing:** the top gaps and where to look.
10. **Footer:** the source count and the fact-check result (e.g. "62 sources · 148 figures checked · 3 corrected").

Every item links to its source or to the dossier. Nothing goes in the email that isn't in the dossier.

## 7. Reply in chat

Give 4 to 5 lines: the most important finding, the deal to know cold, the best question, the biggest gap, and the links. Keep it short; everything else is in the dossier.

## Getting better

- A source that worked well: add it to `research-sources`.
- Dana says a section is useless, or wants more of something: change this file or the template.
- Commit and push repo changes.

## Rules

- Read only on the web. Never contact anyone, sign up, pay, or submit anything. The only email sent goes to Dana's own `newsletter_to` address.
- Every fact has a source. Nothing is invented. Say "the person worked on it" only when a source names them.
- No personal data in this skill's files.
