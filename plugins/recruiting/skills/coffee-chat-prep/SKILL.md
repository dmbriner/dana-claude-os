---
name: coffee-chat-prep
description: Prep Dana for a networking coffee chat or call with someone at a finance firm. Researches the person, their group, the firm, the group's recent deals and market, and writes a prep brief onto the person's page in Dana's Notion People database. Use when Dana says "prep me for", "coffee chat with", "call with <name>", or runs /coffee-chat-prep <name>.
---

# Coffee chat prep

This skill gets Dana ready for a 20–30 minute coffee chat or call with one person.

First load `private/profile.json` (Notion IDs, `career_root`) and `private/story.md` (background and talking points) from the repo root. Resolve this file's symlink to find the root.

Input: a person's name, a Notion People page link, or a LinkedIn URL. If the name matches several People rows, ask which one.

## 1. Pull what Dana already has (Notion)

- **People** database: `notion.people` in profile.json. Find the person's page and read everything on it: role, firm, the email thread or log, Call Date, Connection, Source, notes.
- Follow the **Firm** relation to their row in the **Firms** database (`notion.firms`) and read its Key Takeaways and Recruiting Timeline.
- Check **Opportunities** (`notion.opportunities`) for any role Dana has open or applied to at that firm.
- Dana's background lives in the Notion page "Resume" (search for it) and the **Behaviorals** database. Use these for the "your story" section. Never invent experience.

## 1b. Pull Dana's own files (iCloud "Career & Finance" folder)

Root: `career_root` in profile.json. Read whatever applies before searching the web:

- `Recruitment/Firms/<Firm>/`: Dana's saved research on that firm (PDFs of firm pages, supplementals, earnings decks), plus `Calls/` and `Research/` subfolders where they exist.
- `Markets/`: Dana's market-research library. This includes GS Insights, BlackRock Investment Institute, KKR Insights, Bank of America Institute, JPM Eye on the Market, Federal Reserve Board, Deutsche Bank Corporate Bank, and `2026/` by month. Use the most recent pieces that touch the person's market, and cite them by file name. These are "Dana's sources": connect them to the person's group wherever they fit.
- `Recruitment/Networking/`: guides such as IB_Networking_Bible.pdf and Email+Guide+for+IB+Recruitment.pdf. Use them for etiquette, question style, and follow-up norms.
- `Recruitment/Investment Banking/Claude Notes/`: Dana's technical and fit notes. Use them to suggest which technicals to brush up on for that group.

Files may be iCloud placeholders. If a file can't be read, skip it and say so.

## 2. Research (web)

First read the `research-sources` skill (`plugins/recruiting/skills/research-sources/SKILL.md`): it lists where to look up the person and their group's deals (Krugman Insights, FINRA BrokerCheck, SEC EDGAR, and more) and how to reach each one.

Use WebSearch and WebFetch (or a web-fetch agent). Open the pages you cite; a search snippet alone is not a source. Prefer the firm's own site, press releases, SEC filings, and reputable financial press (Bloomberg, Reuters, WSJ, FT, PE Hub, PitchBook news, Secondaries Investor, Mergermarket summaries).

Cover, in this order of importance:

1. **The person.** Their title, group, how long they've been there, prior firms, school (UNC or Exeter overlap matters), any articles, panels, podcasts, or deal announcements that name them. LinkedIn pages usually can't be fetched; use what Dana pasted or what public sources say.
2. **Their group.** What the group does day to day, who its clients are, how it's organized, its leaders, how it ranks (league tables, awards), and how a junior person there spends their time.
3. **Recent deals and transactions from the last 12–18 months, emphasizing their group.** For each one: date, parties, size, the group's role, and a source link. Say "deal the person worked on" ONLY when a source names them. Otherwise say "deal by their group."
4. **Their market right now.** The 3–5 biggest things happening in that person's market: volumes, pricing, fundraising, regulation, notable competitor moves. For example, for secondaries: GP-led continuation vehicle volume, LP portfolio sale pricing as a % of NAV, and the largest recent funds. Connect each trend to what it means for their group.
5. **Open roles tied to them.** Find the firm's current student postings, especially in the person's group: summer analyst roles for 2027 and 2028, sophomore and early-insight programs, and off-cycle internships. Check:
   - the firm's own careers or campus page (Greenhouse, Workday, tal.net, Oracle)
   - freehire (the `mcp__freehire__search_jobs` tool) when it's available
   - Dana's Notion Opportunities

   Read each relevant job description. Pull out what the group does, the skills it asks for, the deadline, and the program length. Connect each posting to the person's work, to Dana's experience, and to questions to ask. For example: "The posting says analysts model GP-led continuation vehicles; ask how much of the team's 2026 volume was GP-led versus LP portfolio sales."
6. **Big firm updates.** Leadership changes, earnings highlights for the relevant segment, acquisitions, reorganizations, new offices, layoffs or hiring news, all within about 12 months.

Every fact gets a source link and a date. If something can't be confirmed, label it unverified or leave it out.

## 3. Write the brief onto the person's Notion page

Insert at the TOP of their People page a section titled `## Coffee Chat Prep – <Month D, YYYY>`, kept skimmable (about one screen):

- **30-second read:** who they are, what their group does, and the one thing to know going in.
- **About them:** short bullets.
- **Their group:** short bullets.
- **Recent deals (group-first):** a table with Date · Deal · Size · Role · Source.
- **Open roles and what they ask for:** each relevant posting with its link, deadline, the 2–3 key requirements, and how Dana matches them.
- **What's happening in their market:** 3–5 bullets, each with "why it matters to them."
- **Firm news:** 2–4 bullets.
- **Connecting to Dana:** 2–3 honest links between their work and Dana's real experience. Draw only from `private/story.md`. Plus a one-line tailored version of Dana's "why this field" story.
- **Questions to ask:** 6–8 specific questions drawn from the research (deal-specific, market-specific, role and day-to-day, recruiting), never generic. Mark the 3 best.
- **Avoid:** anything not to bring up, like questions answered on the firm's website, or topics that are confidential or sensitive.
- **Sources:** links to every page used.

Also save a copy as a Word file at `<career_root>/Recruitment/Firms/<Firm>/Calls/<Person> – Coffee Chat Prep <YYYY-MM-DD>.docx`. Create the folders if needed. To make it, write an HTML file in the scratchpad, then run `textutil -convert docx -output <path> <html>`.

Update the person's properties if new facts were found (Role & About, Location, Level, Type). Change only fields that are empty or clearly wrong, and never overwrite Dana's notes.

## 4. Reply in chat

Give a 3–4 line summary: the single most useful thing to know, the best question to ask, and a link to the Notion page. If the chat is soon, also offer a draft confirmation email, and after the chat, a thank-you note in Dana's voice.

## Rules

- Never contact anyone, send email, or submit anything. This skill researches and writes to Notion only.
- Dana's own words and notes on a page are never deleted or reworded.
- Write plainly and specifically. Use numbers, names, and dates, not adjectives.
