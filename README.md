# Dana's Claude OS

A personal operating system for [Claude](https://claude.com/claude-code) built by a finance student. Recruiting, equity research, inbox and calendar, school, and student-org work are installable plugins. They share one private context folder, so every tool knows the same things about you and they can hand work to each other.

## Plugins

| Plugin | What's inside |
|---|---|
| [**recruiting**](plugins/recruiting) | `cover-letter` (letter + tailored resume + filed packet), `apply-online` (fills Workday/Greenhouse/Oleeo/Lever in Chrome), `coffee-chat-prep` (sourced prep brief on a contact and their group), `add-event` (event email → calendar with QR code), and a `career-finance` agent that routes to all of them |
| [**itc-research**](plugins/itc-research) | 11 equity-research skills (ticker, compare, screening, and earnings notes, thesis tracker, Approved List package) and three agents: researcher, reviewer, and a house-style curator that learns from corrections |
| [**personal-admin**](plugins/personal-admin) | `email-assistant` (triage, drafts in your voice, never sends, learns from edits), `scheduling` (real availability across every calendar and inbox), and a `personal-admin` planning agent |
| [**involvement**](plugins/involvement) | `alpha-phi` agent for a Director of Academics role: GPA check-ins, roster upkeep, Notion tasks |
| [**academics**](plugins/academics) | Coursework agent, growing a skill per class |
| [**workflow-miner**](plugins/workflow-miner) | Reads past sessions, finds manual work you keep repeating, and drafts new skills |

## Plugins by other people I use

Linked from their original repos, not copied: investment-banking, equity-research, financial-analysis, notion, google-drive, pdf-viewer, productivity, canva, superpowers, skill-creator, obsidian. Full list, install steps, and what I turned off: [docs/STACK.md](docs/STACK.md).

## Also in this repo

| Part | What it does |
|---|---|
| [`mcp/career-tools`](mcp/career-tools) | MCP server: live student postings from each firm's own careers feed, Fed releases, FRED, Treasury yields, news search. Pure Python stdlib, no API keys. |
| [`mcp/market-tools`](mcp/market-tools) | MCP server: quotes, performance, price history, SEC filings and XBRL financials. |
| [`routines/daily-brief.md`](routines/daily-brief.md) | Weekday 7am cloud routine: checks ~120 firms' careers pages, logs new programs to Notion, and emails a newsletter (markets, Fed, bank research, interview technicals, deals). |
| [`notion/schema.md`](notion/schema.md) | The Notion databases behind it all: Firms, Opportunities, People, Tasks, Technicals Bank. |
| [`CLAUDE.md`](CLAUDE.md) | The router: which plugin handles which request, and the rules for adding new ones. |
| [`docs/BRAIN.md`](docs/BRAIN.md) | How the shared private context works. |

## How it fits together

```
                 CLAUDE.md (router, loaded every session)
                              │
   ┌──────────────┬───────────┼─────────────┬──────────────┐
recruiting   itc-research  personal-admin  involvement   academics …
   │              │           │
   └──── calls ───┴── calls ──┘     MCP: career-tools, market-tools
                              │
                 private/  (shared brain, git-ignored)
```

## Install

**Claude Code or Cowork** (any plugin):
```
/plugin marketplace add dmbriner/dana-claude-os
/plugin install recruiting@dana-claude-os
```

Installed plugins are copied into Claude's plugin cache, so the agents and ITC skills work anywhere, but skills that read `private/` (cover-letter, coffee-chat-prep, apply-online, email-assistant, scheduling) need the cloned setup below.

**Use it as your own system:** clone the repo, copy `profile.example.json` to `private/profile.json`, write `private/story.md`, and symlink the skills you want into `~/.claude/skills/` (`ln -s "$PWD/plugins/recruiting/skills/cover-letter" ~/.claude/skills/`). Requires macOS, Python 3 (no extra packages), and Microsoft Word for PDF export.

See [docs/ROADMAP.md](docs/ROADMAP.md) for what's next.
