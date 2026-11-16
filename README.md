# Investment Banking Assistant

A personal recruiting and research system for finance internship recruiting, built on [Claude Code](https://claude.com/claude-code). It runs a daily markets newsletter, tracks job postings and applications in Notion, and builds tailored application packets.

## What it does

| Module | Runs | What it does |
|---|---|---|
| **Daily brief** (`routines/daily-brief.md`) | Weekdays 7am ET, in the cloud | Checks careers pages at ~120 target firms and logs new student programs to Notion. Then emails a newsletter with market prices, Fed and economic releases, research from major banks and asset managers, top stories, a concept of the day, 5 interview technicals with answers, firm news, and recent deals. |
| **Cover letter + packet** (`skills/cover-letter`) | On request | Reads the posting, writes a one-page letter in the applicant's voice by cloning a real letter's formatting, tailors the resume bullet by bullet, exports PDFs through Word, checks the page count, and files everything into the firm's application folder. |
| **Email assistant** (`skills/email-assistant`) | On request | Triages the inbox, updates application statuses in Notion from confirmation, interview, and rejection emails, drafts replies in the applicant's voice as Gmail drafts (never sends), and learns from how drafts get edited. Adapted from [claude-email-assistant](https://github.com/marian-kamenistak/claude-email-assistant). |
| **career-tools MCP server** (`mcp/career-tools`) | Always available to Claude | Custom tools for live student postings from each firm's own careers feed, Fed releases, FRED and Treasury data, and news search. Pure Python standard library, no API keys. |
| **Scheduling** (`skills/scheduling`) | On request, and before any email with times | Checks every calendar and every inbox (Gmail plus Mail.app, Sent included) to find open windows. Booked events count as busy, times offered to someone else stay open until accepted. Keeps a calendar of offered times in sync and does time-zone math in a script, not in its head. |
| **Coffee chat prep** (`skills/coffee-chat-prep`) | On request | Researches a contact, their group's recent deals, their market, and open roles, then writes a one-screen prep brief with sourced facts and specific questions. |

Notion is the database behind all of them: Firms, Opportunities, People, Tasks, and a Technicals Bank (see `notion/schema.md`).

## How it's built

- **Skills** are folders of plain-English instructions plus small Python scripts. Claude Code follows them when a request matches. They're symlinked into `~/.claude/skills/`, so edits here take effect immediately.
- **Routines** are scheduled Claude Code agents that run in the cloud with Notion and Gmail connectors. `routines/render.py` fills a prompt template with private settings.
- **Personal data stays local.** Names, contact details, Notion IDs, and the applicant's story live in `private/` (git-ignored), along with all .docx and .pdf files. `profile.example.json` shows the shape.

## Setup

1. Copy `profile.example.json` to `private/profile.json` and fill it in. Write `private/story.md` with your experience and style rules.
2. Link the skills: `ln -s "$PWD/skills/cover-letter" ~/.claude/skills/cover-letter` (same for each skill).
3. In Claude Code, run `/cover-letter <firm>` or `/coffee-chat-prep <name>`.

Requires macOS with Microsoft Word (for PDF export) and Python 3, with no extra packages.

See [docs/ROADMAP.md](docs/ROADMAP.md) for what's next.
