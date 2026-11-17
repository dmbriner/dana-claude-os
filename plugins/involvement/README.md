# involvement

Manages Dana's extracurricular/organization commitments. Designed to grow — each org gets its own subagent under this plugin over time.

## Components

- **Agents**
  - `alpha-phi` — Dana's Alpha Phi chapter work, currently scoped to her Director of Academics duties: CARES/GPA check-in emails, GPA roster upkeep, Notion task tracking for chapter academics, and study hours/tutoring coordination. Built to absorb course-data import once that responsibility starts.

## Setup

No dedicated MCP server is bundled — `alpha-phi` uses whatever Notion connector is already authorized in the session, plus the standard file/xlsx tools. If Notion isn't connected, authorize it via claude.ai connector settings.

## Usage

Ask for chapter/academics work directly (e.g. "draft the CARES check-in emails") and Claude will delegate to the `alpha-phi` subagent.

## Roadmap

Future orgs Dana is involved in can be added as additional subagents under `agents/`, following the same pattern as `alpha-phi`.

## Install

```
/plugin install involvement --marketplace dmbriner/dana-claude-os
```
