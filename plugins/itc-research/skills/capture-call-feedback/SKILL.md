---
name: capture-call-feedback
description: >
  This skill should be used when Dana pastes a transcript or summary of a call with her PM (Bob) or
  says things like "here's what Bob said on our call", "log this feedback", "Bob wants me to do X for
  the [ticker] earnings call", or "update my house style with this". Extracts style feedback and
  action items from the conversation, appends them to the living house-style guide and to Dana's ITC
  Brag Book, creates Notion tasks for action items, and adds calendar events for anything with a hard
  date.
metadata:
  version: "0.1.1"
---

# Capture call feedback

Turn a pasted call transcript or summary (typically with Dana's PM, referred to as Bob) into three things: an update to the living house style, a logged feedback entry, and concrete tasks/calendar events.

This is the mechanism that makes the rest of this plugin get better over time — treat every transcript as new signal about how Dana's notes should improve, not just a one-off task list.

## Steps

1. Read the pasted transcript/summary carefully. Separate it into three categories:
   - **Style feedback**: guidance about how notes should be written, analyzed, or structured going forward (e.g., "add relative valuation," "separate facts from conclusions," "go further on thesis-break conditions").
   - **One-off action items**: specific tasks tied to a particular note, ticker, or deadline (e.g., "add a Coach-standalone valuation to the Tapestry note," "mark the next earnings call on the calendar").
   - **General context**: anything else worth remembering but that isn't feedback or a task.

2. **Update the living house style.** `house-style.md` lives locally in Dana's Investors Trust > Equity Research folder on her Desktop — not Google Drive or any other connector. If this session doesn't already have access to that folder, call `request_cowork_directory` for it before doing anything else; only tell Dana the update is blocked if she declines that request. Once accessible, open `house-style.md` (create it from `references/house-style-seed.md` in this skill if it doesn't exist yet). Add or sharpen the relevant section(s) with the new style feedback — translate the feedback into a durable rule written the way the existing sections are written, don't just append raw quotes. If feedback contradicts an existing rule, update the rule rather than leaving both.

3. **Log the feedback.** Append a row to the "Feedback log" table at the bottom of `house-style.md`, and also append matching rows to Dana's `ITC Brag Book.xlsx` (also a local file in her Investors Trust folder — same folder-access note as step 2 applies): positive/complimentary feedback goes on the "Feedback" sheet, constructive criticism goes on the "Criticisms" sheet, following the existing column structure in that workbook (Date, Source, Criticism/Feedback, Action Taken, Status). Use the xlsx skill to edit the workbook in place — do not overwrite other sheets or rows.

4. **Create Notion tasks.** For every one-off action item identified in step 1, create a task in Dana's Notion workspace (use the notion-api skill / connected Notion tools). Include enough context in the task (ticker, what's being asked, source call) that it's actionable without re-reading the transcript.

5. **Add calendar events.** If any item has a specific date attached (an earnings call, a deadline, a meeting), create a Google Calendar event for it (use the connected calendar tools) rather than only logging it as a task. Confirm the date/time with Dana if the transcript is ambiguous about it.

6. Summarize back to Dana in plain language: what was added to house style, what got logged, which Notion tasks were created, and which calendar events were added. Keep this summary short — she was on the call, she doesn't need the transcript repeated back to her.

## Notes

- If the transcript doesn't clearly attribute a piece of feedback to the PM/Bob vs. general conversation, ask rather than guessing at attribution in the Brag Book.
- Don't create a Notion task for style feedback that has no concrete deliverable — that goes into house-style.md only.
- If Notion or Calendar tools aren't connected/authorized, tell Dana plainly what couldn't be created and why, rather than silently skipping it.
