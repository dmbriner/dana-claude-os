---
name: side-note
description: Park a random, off-topic thought Dana wants to come back to later, without derailing the current task. Use when Dana types /side-note <thing>, "side note:", "park this", or "remind me later about". Also use for "/side-note list" or "what side notes do I have" (show the parked ones) and "/side-note done <thing>".
---

# Side note

Dana has ADHD, and tangents come up mid-task. This skill saves the tangent in a few seconds so Dana can get back to what they were doing. It has to be fast and cheap.

Load `private/profile.json` from the repo root (resolve this file's symlink, walk up to `.claude-plugin/marketplace.json`) and use `notion.tasks`.

## Save (`/side-note <thing>`)
- Make **one** Notion create call in Tasks: Name `🔁 <thing>` (short, verb first if it's a to-do), Status `Not started`, Area guessed from the words (default Personal). Leave Do Date empty unless Dana gave a time. Don't look anything up first.
- Reply in one line: `Parked: <thing>.` Then go straight back to whatever you were doing before. Don't start working on the side note.

## List (`/side-note list`)
- One SQL query: open Tasks whose Name starts with `🔁`, oldest first.
- Show a numbered list with how many days each has been parked. Ask once: "Want to schedule, do, or drop any of these?"

## Done (`/side-note done <thing or number>`)
- Mark that task Done. Reply in one line.

## Circle back
When `plan-my-day` builds a plan or wraps up a day, it can run the list step so parked side notes get a slot or get dropped.
