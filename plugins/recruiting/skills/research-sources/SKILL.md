---
name: research-sources
description: Dana's playbook of where to look things up about people in finance (bankers, PE/AM investors, alumni) and the deals they and their groups have worked on, with what each source gives and how to reach it. Use when Dana says "look up <name>", "who is <name>", "what deals has <name> / <group> done", "find info on", "search up", or pastes a profile link; and read it before the research steps of coffee-chat-prep, outreach-email, interview-prep, and source-check. Also use when Dana says "add this source" or shares a new site worth searching.
---

# Research sources: people and deals

This is the list of places to search, in order, when Dana needs facts about a person or a deal. Other skills (coffee-chat-prep, interview-prep, outreach-email, source-check) use it for their research steps. Used on its own, it does a quick lookup and saves what it finds to the person's Notion People page.

## How to use the list

1. Start with Dana's own sources (section A). They're free, already verified, and often have things the web doesn't.
2. Then work down sections B (people) and C (deals). Stop once each fact has a solid source. Not every source needs to be checked.
3. Open every page you cite. A search snippet is not a source. Fetch pages with WebFetch or a `web-fetch` agent. Use TinyFish (`search`, `fetch_content`) when a page is JS-rendered. Use Chrome (`mcp__claude-in-chrome__*`, Dana's logged-in browser) for pages behind a login Dana has, such as LinkedIn or Heels Engage. In Chrome, only read pages; never message, connect, or follow anyone.
4. Label each fact with its source and date. Say "deal the person worked on" ONLY when a source names the person. Otherwise say "deal by their group" or "deal by the firm."
5. When sources disagree (for example an old club bio vs. a current title), trust the newest dated source and note the older one.

## A. Dana's own sources (check first)

| Source | What it gives | How |
|---|---|---|
| Notion **People** / **Firms** / **Opportunities** | Everything Dana has logged: role, connection, notes, call history | IDs in `private/profile.json` |
| Career & Finance iCloud folder | Saved firm research, call notes, market library | `career_root` in profile.json; `Recruitment/Firms/<Firm>/` |
| Email threads | What the person said, their signature (title, group, phone) | Gmail + Mail.app (see `email-accounts-map` memory) |
| UNC alumni databases (UFS alumni database, Heels Engage, iModules) | Title, firm, class year, sometimes bio | Dana's login, via Chrome or ask Dana to paste |
| Bios Dana pastes | Event speaker bios, old club bios (often show school, internships, interests) | Save them to the People page word for word |

## B. People

| Source | What it gives | How / URL pattern | Notes |
|---|---|---|---|
| **Krugman Insights** | Current title, firm, seniority, function, colleagues at the firm (with titles and groups), firm's recent deals | `krugmaninsights.com/professionals/<id>-<slug>`. Find it by searching `site:krugmaninsights.com "<name>"` | Listing is public. The "Connect" profile layer may be gated. Deals shown on a profile are the **firm's**, not the person's. Colleague list is great for mapping a group. |
| **FINRA BrokerCheck** | Registered bankers: full employment history with dates, licenses (SIE, 7, 63, 79), disclosures | `brokercheck.finra.org`: search by name + firm | Most IB analysts and associates are registered. This is the best free source for exact start dates and prior firms. |
| **SEC IAPD** | Investment adviser reps (PE, AM, wealth): employment history, licenses | `adviserinfo.sec.gov` | Use for buy-side people. |
| **Firm website** | Official bio, title, group, sometimes deals and education | Firm's "Our team" / "People" pages; `site:<firm domain> "<name>"` | Senior people mostly. Juniors rarely have bios. |
| **LinkedIn** | Title history, school, activities | Usually can't be fetched. Use Chrome if Dana is logged in (read only), or use what Dana pastes | Never message or connect. |
| **The Org** | Org charts, reporting lines | `theorg.com/org/<firm>` | Spotty for banks, decent for smaller funds. |
| **Press releases** | Names on deal announcements, promotions, hires | PR Newswire, Business Wire, GlobeNewswire: search `"<name>" "<firm>"` | Promotions news often lists whole classes of MDs. |
| **Trade press** | Hires, moves, quotes, panels | Financial News, eFinancialCareers, PE Hub, Bloomberg, Reuters, WSJ, IFR / GlobalCapital (capital markets) | Paywalled articles: use the headline and lede only, and say so. |
| **School and club pages** | Undergrad activities, internships, interests | UNC student org pages (Kenan-Flagler PMT, finance clubs, Senate), Daily Tar Heel, Exeter pages | Usually old. Use for talking points, not current role. |
| **Events and podcasts** | Speaker bios, what they've said publicly | Conference speaker pages, YouTube, podcasts, Handshake / firm event pages | |

## C. Deals

| Source | What it gives | How / URL pattern | Notes |
|---|---|---|---|
| **Krugman Insights Deal Tracker** | Firm deals: date, issuer, product (ECM/DCM/M&A), size, sector, country, headline naming the banks | `krugmaninsights.com/firms/<Firm>/deals`, `krugmaninsights.com/deals?firms=<Firm>`, deal pages at `/deals/<ecm|dcm|...>/<slug>` | Firm level. Filter by sector to match the person's group (e.g. Healthcare, TMT). |
| **SEC EDGAR** | Underwriters (S-1, 424B prospectuses), M&A advisors and the "Background of the Merger" story (DEFM14A, S-4, SC TO), 8-K announcements | `market-tools` MCP (`sec_filings`), or full-text search at `sec.gov/edgar/search` with `"<firm>" "financial advisor"` | Primary source, the most reliable. Bankers are rarely named, but the group's role is. |
| **Company and firm press releases** | Deal terms, advisors paragraph ("Citi is serving as financial advisor") | Company IR pages; PR Newswire / Business Wire; search `"<firm>" "served as financial advisor" <sector>` | |
| **Law firm deal announcements** | Advisor lists and sometimes banker names | Law firm news pages; Global Legal Chronicle | Good for mid-market M&A. |
| **Trade press** | Deal coverage, league table rankings | Reuters, Bloomberg, WSJ, FT, PE Hub, Mergermarket summaries, PitchBook news, IFR, GlobalCapital, Secondaries Investor | |
| **League tables** | Group rankings by product and sector | LSEG / Dealogic tables quoted in press; firm earnings decks | |
| **News MCPs** | Recent firm headlines | `career-tools` MCP (`firm_news`, `search_news`) | Then open the article itself. |
| **Paid databases via UNC** | Full deal lists, advisors, banker credits | Capital IQ, PitchBook, Bloomberg terminal (Kenan-Flagler) | Claude can't reach these. Tell Dana exactly what to look up there if it would fill a gap. |

## When used on its own ("look up <name>")

1. Find the person in Notion People. If they have no page, ask before creating one.
2. Search the sources above in order. Aim for: current title and group, start date, prior firms and internships, school, 3 to 5 deals by their group (with the person's own deals marked if a source names them), and 2 to 3 talking points.
3. Update the People page: fill empty or clearly outdated properties (Role & About, Location, Level, Type), and add a `## Background` section with sources. Never delete or reword Dana's notes.
4. Reply in chat with a 3 to 4 line summary and the page link, and list any gaps a paid database could fill.

## Adding a source

When Dana shares a new site ("this is a great website"), or a search turns up a source that worked well, add a row to the right table above with what it gives, its URL pattern, and its access notes (public, partly gated, login). Check the URL pattern by fetching one real page first. Commit and push the change to the repo.

## Rules

- Read only. Never contact anyone, send a connection request, or sign up for a site.
- No personal data in this file (no names, emails, or IDs). Real lookups go to Notion only.
- Don't pay for or subscribe to anything. If a page is gated, use what's public and say so.
