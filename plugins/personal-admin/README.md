# personal-admin

General life-admin agent for Dana — the catch-all for day-to-day organizing work that doesn't belong to Alpha Phi (`involvement`), recruiting (`recruiting`), ITC (`itc-research`), or coursework (`academics`). Its two skills are shared: `email-assistant` and `scheduling` are also used by the recruiting tools.

## Components

- **Agents**
  - `personal-admin` — daily/weekly task and calendar rundowns, ad hoc task/event creation, and file/desktop organization on request.
  - `day-planner` — the legwork behind `plan-my-day`. In `draft` mode (read-only) it catches up on focus blocks that already passed, reads every calendar and open task, and returns a plan plus questions. In `apply` mode it writes Dana's answers to Notion and the calendar.
- **Skills**
  - `plan-my-day` — turns a brain dump into Notion tasks and 25-minute focus blocks on the calendar, each with a phone ping, a first tiny step, and the task link. Every run starts by catching up on blocks that already passed (`missed_blocks.py`), so a skipped evening or morning rolls into the new plan instead of disappearing. Has a restart mode for "I'm behind", and flags tasks that keep slipping. Also does the end-of-day wrap-up.
  - `email-assistant` — triages the inbox, drafts replies in Dana's voice as Gmail drafts (never sends), updates Notion application statuses, and learns from edits. Adapted from [claude-email-assistant](https://github.com/marian-kamenistak/claude-email-assistant).
  - `scheduling` — real availability across every calendar and inbox; offered times stay open until accepted; keeps the Reference calendar of holds in sync. `free_windows.py` does the time-zone math.

## Setup

Uses whatever Notion and Google Calendar connectors are already authorized in the session, plus standard file tools. No dedicated MCP server is bundled.

## Scope note

Dana's existing scheduled tasks (daily Notion plan, desktop organizer, portfolio review, IB technicals quiz) are left untouched by this plugin. Converting any of them into on-demand skills is flagged as a separate, later piece of work.

## Usage

Ask directly — e.g. "what's on my plate today," "organize my desktop," "add this to my calendar."

## Install

```
/plugin install personal-admin --marketplace dmbriner/dana-claude-os
```
