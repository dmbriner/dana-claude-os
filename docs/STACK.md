# My plugin stack

Everything I run in Claude, in one place. My own plugins live in `plugins/`. Plugins by other people are **linked, not copied**: `.claude-plugin/marketplace.json` points to each one's original repo, so they stay up to date and keep their own licenses.

## Install everything on a new computer

```
/plugin marketplace add dmbriner/dana-claude-os
```
Then install any plugin below with `/plugin install <name>@dana-claude-os`. The two marked * install from their own marketplaces (their names start with `claude-`, which only Anthropic can use in a marketplace).

## What I use

| Plugin | By | What for |
|---|---|---|
| recruiting, itc-research, personal-admin, involvement, academics, workflow-miner | me | See the main README |
| investment-banking | Anthropic | CIMs, teasers, buyer lists, merger models, pitch decks |
| equity-research | Anthropic | Earnings, initiations, theses, catalysts, sectors |
| financial-analysis | Anthropic | DCF, LBO, comps, 3-statement, PowerPoint and Excel authoring |
| notion, google-drive | Anthropic | Connector skills |
| pdf-viewer, productivity | Anthropic | PDFs; tasks and memory |
| canva | Canva | Designs |
| superpowers | Jesse Vincent | Brainstorm, plan, debug, verify |
| skill-creator | Anthropic | Build and test skills |
| obsidian | Obsidian | Notes, bases, canvas |
| claude-md-management * | Anthropic | `/plugin marketplace add anthropics/claude-plugins-official`, then `/plugin install claude-md-management@claude-plugins-official` |
| claude-mem * | thedotmack | `/plugin marketplace add thedotmack/claude-mem`, then `/plugin install claude-mem@thedotmack` |

## Turned off (2026-11-17), and why

Each loaded skill costs usage at the start of every session, so these are off:

- **Not for me:** gws (Google Workspace CLI, 95 skills; connectors cover Gmail and Calendar), zoom-plugin, auth0, claude-for-msft-365-install, claude-tag-troubleshoot, claude-tag-data-viz, cowork-plugin-management, finance (accounting close and SOX), wealth-management, valuation-reviewer, data, desktop-commander, dropbox, mattpocock-skills, playwright
- **Need paid accounts I don't have:** daloopa, sp-global
- **Duplicates:** market-researcher, earnings-reviewer, model-builder (covered by financial-analysis and equity-research), itc-workbench (same as itc-research)
- **Longer answers:** learning-output-style, explanatory-output-style

Turn one back on with `claude plugin enable <name>@<marketplace>` (synced ones use `@synced`).

## Not on GitHub
- **mcpmarket-me**: was uploaded by hand to claude.ai and has no installable repo.
