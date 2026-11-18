---
name: open-threads
description: Show every open thread Dana has parked with /side-note (the 🔁 tasks in Notion), oldest first, so they can schedule, do, or drop each one. Use when Dana types /open-threads, "show my open threads", "what have I parked", or "what am I forgetting".
---

# Open threads

Load `private/profile.json` from the repo root (resolve this file's symlink, walk up to `.claude-plugin/marketplace.json`) and use `notion.tasks`.

1. Run **one** SQL query on that Tasks data source only (querying several sources at once needs a Business plan): open tasks (`Status` is not `Done`) whose Name starts with `🔁`, ordered by `createdTime`. Return Name, createdTime, Do Date, and url.
2. Show a numbered list: name, days parked, and the Do Date if there is one. Keep it to one line each.
3. Ask once: "Schedule, do, or drop any of these?" Then:
   - **done / drop** → set Status `Done` (for a drop, add "(dropped)" to the end of the name)
   - **schedule** → set Do Date, and offer a focus block through `plan-my-day`
4. Nothing else: no research and no extra lookups.
