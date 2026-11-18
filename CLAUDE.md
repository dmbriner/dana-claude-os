# Dana's Claude OS

This repo (`~/dana-claude-os`, GitHub `dmbriner/dana-claude-os`) holds every skill, agent, plugin, and MCP server Dana has built. This file is linked to `~/.claude/CLAUDE.md`, so it loads in every session.

## Which tool handles what

Check this table before doing a task by hand.

| Request | Use | Plugin |
|---|---|---|
| Cover letter, tailored resume, application packet | `cover-letter` skill | recruiting |
| Fill out an online application | `apply-online` skill | recruiting |
| Prep for a coffee chat or call | `coffee-chat-prep` skill | recruiting |
| Interview prep: firm, deals, technicals, behaviorals, mock interview | `interview-prep` skill | recruiting |
| Event email → Career & Finance calendar | `add-event` skill | recruiting |
| Recruiting prep, technicals, personal finance (general) | `career-finance` agent | recruiting |
| Check email, triage, draft a reply | `email-assistant` skill | personal-admin |
| When am I free, offer times, calendar holds | `scheduling` skill | personal-admin |
| Brain dump, plan my day, focus blocks, wrap up my day | `plan-my-day` skill | personal-admin |
| Park a tangent to come back to (/side-note) | `side-note` skill | personal-admin |
| Organize files, general life admin | `personal-admin` agent | personal-admin |
| ITC note, model, screen, earnings update | `itc-researcher` agent + ITC skills | itc-research |
| Review a research draft | `itc-reviewer` agent | itc-research |
| Alpha Phi academics work | `alpha-phi` agent | involvement |
| Coursework, assignments | `academics` agent | academics |
| "What do I keep doing by hand?" | `workflow-miner` agent | workflow-miner |
| Live job postings, Fed, FRED, Treasury, news | `career-tools` MCP | mcp/career-tools |
| Quotes, price history, SEC filings | `market-tools` MCP | mcp/market-tools |

## Shared brain

All skills read the same private context, so none of them starts cold. It lives in `private/` at the repo root: `profile.json` (Notion IDs, calendar IDs, paths), `story.md` (background and talking points), and the email voice and learned-edits files. `private/` is git-ignored and actually lives in iCloud (`Personal Admin/Claude/Assistant Private`). See `docs/BRAIN.md`.

## Rules for changing this repo

- **Every new skill, agent, or plugin goes here**, whether it was made in Claude Code or Cowork. File it under the right `plugins/<area>/` (skills in `skills/<name>/SKILL.md`, agents in `agents/<name>.md`), add a row to the table above, then commit and push.
- **Plugins by other people that Dana keeps** are linked, never copied: add an entry to `.claude-plugin/marketplace.json` with a `git-subdir` or `url` source pointing to the original repo, and a row in `docs/STACK.md`. Names starting with `claude-` aren't allowed there, so list those in STACK.md only. When Dana turns a plugin off, move it to the "Turned off" list in STACK.md.
- A new area of life gets a new plugin: make `plugins/<area>/.claude-plugin/plugin.json` and add it to `.claude-plugin/marketplace.json`.
- Skills are symlinked into `~/.claude/skills/<name>`, so edits take effect right away.
- **No personal data in tracked files**: no emails, phone numbers, Notion or calendar IDs, or other people's names. Put those in `private/profile.json` and point to them. Run `git grep -nE '@[a-z0-9-]+\.(com|edu)|[0-9a-f]{32}'` before every commit.
- Scripts find the repo root by walking up to `.claude-plugin/marketplace.json`, so they survive folder moves.
- Commit with the noreply email already set in the repo's git config.
