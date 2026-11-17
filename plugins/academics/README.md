# academics

Dana's own coursework agent — assignments, readings, and class-specific work.

## Components

- **Agents**
  - `academics` — handles class coursework, starting with FREN112. Built to grow: as a class's work repeats enough to warrant it, it can get its own dedicated skill under this plugin instead of living only in the agent's general instructions.

## Setup

Uses whatever Notion and Google Calendar connectors are already authorized in the session for assignment tracking. No dedicated MCP server is bundled.

## Usage

Ask directly — e.g. "help with my FREN112 journal," "what assignments do I have due this week."

## Roadmap

Add class-specific skills under `skills/` as patterns repeat (mirrors how `involvement` is structured to grow with more org subagents).

## Install

```
/plugin install academics --marketplace dmbriner/dana-claude-os
```
