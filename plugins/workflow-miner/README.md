# Workflow Miner

Scans your past Cowork session transcripts for manual work you've repeated, keeps a running log of automation opportunities, and — unlike a pure observer — closes the loop where it safely can: fixing small config mismatches on its own, drafting real proposed fixes to your own skills/agents for approval, and drafting new-skill specs when a pattern keeps showing up with nothing built to cover it.

## What's included

One agent: **workflow-miner**. Dispatch it by asking things like:

- "what have I been doing manually over and over lately"
- "mine my sessions for patterns"
- "workflow audit"
- "was any of that something I've done before"

It reads your recent session list and transcripts (via Cowork's built-in session tools), checks them against a findings log it maintains (`workflow-findings.md`), and reports only what's new or changed — evidence-backed, tied to the actual sessions it came from.

## How it handles a finding

Every genuine repeat gets sorted into one of three tiers:

1. **Auto-fixed.** Small, safe config/description mismatches (e.g. a scheduled task's stored description doesn't match what it actually does) get corrected directly — no approval needed, reported as done.
2. **Proposed.** If the actual instructions of one of your own custom plugins (`itc-workbench`, `workflow-miner` itself) look wrong or incomplete, it drafts the specific before/after change and a ready-to-install `.plugin` file, but waits for your go-ahead before you install it. Third-party plugins never get silently touched — those become a plain recommendation instead.
3. **New-skill candidate.** If the same manual pattern keeps recurring with no skill covering it at all, it drafts a name, description, trigger phrases, and rough scope — enough to hand to `skill-creator` once you approve the idea.

## Setting up a recurring audit

This agent doesn't schedule itself. To get a periodic check, ask Claude to create a scheduled task whose prompt dispatches this agent, for example:

> "Schedule a weekly task that runs the workflow-miner agent and reports anything new."

## Findings log

The agent looks for `workflow-findings.md` in your connected folder first; if none is connected, it uses the current session's outputs folder instead (which won't persist between sessions — connect a folder for a durable, cross-session log, and the agent will keep flagging this until you do). Entries are appended, not overwritten, so the file builds a history: new findings, recurrence counts, tier, status (proposed/approved/applied/resolved/dismissed), and the actual drafted fix or skill spec for anything beyond a Tier 1 auto-fix.

## Boundaries

This agent only auto-applies genuinely low-risk config fixes. It never changes what a skill or agent actually does, never touches third-party plugins, and never installs a rebuilt plugin on your behalf — you always get the final click on anything beyond reconciling a description to match reality.

## Install

```
/plugin install workflow-miner --marketplace dmbriner/dana-claude-os
```
