---
name: flag-correction
description: >
  This skill should be used whenever Dana flags that something Claude produced or a workflow step was
  wrong or should be done differently — "this is wrong about X", "actually it should be Y", "no, do it
  like this instead", or any correction about a note, model, Asset Sheet, Approved List package, or
  other ITC deliverable, in any Cowork session. Logs the correction immediately to a running
  corrections log so it accumulates across sessions, without waiting for a formal review.
metadata:
  version: "0.1.1"
---

# Flag correction

Capture an ad hoc correction the moment Dana makes it, so nothing gets lost between sessions.

## Steps

1. When Dana corrects something — a wrong assumption, a formatting choice, a "no, do it like this" — identify: what deliverable/skill it relates to (ticker, note type, Asset Sheet, Approved List package, etc.), what was wrong, and what the correct approach is. Ask a brief clarifying question only if the correction is genuinely ambiguous; otherwise capture it and move on without interrupting her flow.
2. `corrections-log.md` lives locally in Dana's Investors Trust > Equity Research folder on her Desktop — not Google Drive or any other connector. If this session doesn't already have access to that folder, call `request_cowork_directory` for it before doing anything else; only tell Dana the log is blocked if she declines that request. Once accessible, append one row to `corrections-log.md` (create the file with a header row if it doesn't exist): `Date | Deliverable/Skill | What was wrong | Correct approach | Looks like a durable rule? (yes/no/unsure) | Incorporated?`.
3. Do this quickly — a one-line confirmation ("logged") is enough. Don't stop to re-explain the whole logging mechanism every time; Dana already knows how this works.
4. If the correction is about something time-sensitive (e.g. a deadline, a specific date), also flag it the way `capture-call-feedback` would — offer a calendar event or Notion task rather than letting a dated action item sit only in the log.

## What this does NOT do

This skill only logs. It does not rewrite `house-style.md` or any skill's instructions on its own — that synthesis step belongs to the `house-style-curator` agent, which Dana runs periodically (or at the end of a session) to turn accumulated corrections into real updates.
