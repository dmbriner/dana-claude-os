# itc-research

Equity-research workbench for ITC (a student investment club). Split out of the old `career-finance` Cowork plugin, which also replaces the standalone `itc-workbench` plugin.

## Agents
- `itc-researcher`: writes a full note, model, or package end to end.
- `itc-reviewer`: checks a draft against house style before it goes out, the way a PM would.
- `house-style-curator`: turns accumulated corrections into house-style updates and proposes skill changes for approval.

## Skills
`single-ticker-note`, `compare-contrast-note`, `screening-note`, `earnings-update`, `morning-note`, `thesis-catalyst-tracker`, `approved-list-package`, `approved-list-email`, `capture-call-feedback`, `task-radar`, `flag-correction`.

## Setup
The skills expect a connected Equity Research folder (Research Notes, Models, FactSet Data, the club's brag book), plus Notion and Google Calendar. The living `house-style.md` and `corrections-log.md` live in that folder, not in this repo. `references/house-style-seed.md` is the starting point.

## Works with
- `market-tools` MCP server (`mcp/market-tools`) for quotes, price history, and SEC filings.
- The `recruiting` plugin's `career-finance` agent routes research requests here.

## Install

```
/plugin install itc-research --marketplace dmbriner/dana-claude-os
```
