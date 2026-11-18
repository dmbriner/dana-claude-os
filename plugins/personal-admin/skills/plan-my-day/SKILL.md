---
name: plan-my-day
description: Turn a messy brain dump into Notion tasks and a realistic day of 25-minute focus blocks on Dana's calendar, each with a phone alert, a first tiny step, and a link to the task. Always catches up first on blocks that already passed (yesterday evening, this morning) so nothing silently falls off. Use when Dana says "plan my day", "plan tomorrow", "here's everything I need to do", "brain dump", "dump:", "what should I work on", "I don't know where to start", "I didn't do anything this morning", "I'm behind", "redo my day", "start over", or runs /plan-my-day. Also use for "wrap up my day" (end-of-day check-in) and "move this block".
---

# Plan my day

Dana has ADHD and jumps between tasks. The goal is to get everything out of their head, pick a realistic amount for today, and make each block easy to start. The plan should be short and kind, never a lecture.

**Plans slip. That's expected, not a failure.** Never assume a past block happened. Every run starts by catching up, and missed work goes back into the pool without guilt.

Load `private/profile.json` from the repo root (resolve this file's symlink, walk up to `.claude-plugin/marketplace.json`). Use `notion.tasks` and `calendars` from it. Focus blocks live on `calendars.focus`, or `calendars.personal` if there's no focus calendar.

**Delegate the legwork.** When the `day-planner` agent (personal-admin plugin) is available, dispatch it for steps 0 to 3 in `draft` mode. It returns the catch-up list, the draft plan, and the questions. Ask Dana the questions here (one AskUserQuestion call), then dispatch it again in `apply` mode with the answers. If the agent isn't available, do the steps yourself.

## 0. Catch up first (every run)
Before planning anything:
- Get the current time (`date`).
- List events on the focus calendar from the **last wrap-up or 2 days back, whichever is later**, through the end of today. Save the response as JSON and run `missed_blocks.py <file>`. It groups 🎯 Focus blocks by Notion task into `passed`, `running`, and `upcoming_today`.
- For every task in `passed` and `running`, check its Status in the same single Notion query as step 2. **Done** means nothing to do. **Not done** means it might be missed.
- Ask Dana once, with checkboxes: "These blocks already passed. Which did you actually do (even partly)?" List each task once with its time ("Investors Trust prep, Tue 6:20–7:15, 2 blocks"). Don't ask about tasks already marked Done.
- For checked tasks: mark Done, or set them In progress if partly done. Unchecked tasks are **carry-over**, and they go into today's pool ahead of new items.
- On each carry-over task page, add one line at the top, below `First tiny step:`: `↩️ Moved from <date>`. If the page now has **2 or more** of those lines, the task is too big or too vague. Before rescheduling it, make the first tiny step smaller, split it into a smaller task, or ask "still want this, or drop it?"
- Leave past focus events alone (they no longer ping). Future blocks for carry-over tasks get moved or deleted in step 4, not here.

### Restart mode
When Dana says the morning (or the day so far) didn't happen ("I didn't do anything", "I'm behind", "start over"):
- Treat **now** as the start of the day. Run step 0 for everything that has passed.
- Keep future blocks that already fit. Rebuild only around them. Don't reshuffle what's still on track.
- If carry-over plus today's must-dos is more than the free time, triage out loud in one short list: what stays today (anything with a deadline in the next 48 hours first), what moves to tomorrow, and what Dana could drop.

## 1. Capture the dump
Pull every to-do out of Dana's message, however messy. For each one:
- **Check Notion Tasks first** (one SQL query on open tasks). If a matching open task exists, update it (Do Date, Effort, Priority) instead of creating a duplicate. If the query shows exact duplicates (same name, not Done), list them in one line and offer to merge them.
- Otherwise create it in Tasks with: Name (short, verb first), Area, Kind, Priority, **Effort (min)** in multiples of 25, **Do Date** (when Dana plans to do it), **Deadline** only if there's a real external due date, and relations (Class, Firm, Person, Opportunity) when obvious.
- Put a `First tiny step:` line at the top of each task page: one physical action that takes under 2 minutes ("open PS10 and do question 1 only"). For study tasks, also put the material itself on the page (a short explainer plus practice questions), so starting means only reading.
- Anything that needs another skill gets that skill: thank-you or outreach email → `outreach-email` / `email-assistant` (draft only, never send); coffee chat → `coffee-chat-prep`; event email → `add-event`; times to offer → `scheduling`.

## 2. See the real day
- If it's evening, plan tonight lightly and put the real plan on tomorrow.
- List events from **every** calendar in `profile.calendars` for the planning window, including `canvas` (assignment due dates) and `assignments`. Booked events and classes are busy. Reference-calendar holds are not.
- **Flag conflicts** (two events at once) in one line each, and ask which one Dana is going to. Don't fix them silently.
- Pull open Tasks with Do Date ≤ the planning day, or Deadline within 7 days. Canvas due dates count as deadlines: put them on the matching task.
- Overdue tasks that aren't carry-over from step 0 (Do Date in the past, not Done, no focus block): give the count and the top 3 by deadline in one line, and ask "today, spread over this week, or drop?" Never bulk-change them without asking.

## 3. Build the plan
- Find free windows with `plugins/personal-admin/skills/scheduling/free_windows.py`. Existing future focus blocks count as busy unless they're for a carry-over task being reordered.
- Use 25-minute blocks with 5 minutes between them, and a 10-minute break after every 2 blocks. A 50-minute task becomes two blocks ("round 1 of 2").
- Order: deadlines first, then carry-over, then hardest work in the morning. Put email and admin first thing (it clears the head) and low-energy reading at night.
- **Cap the day at about 6 to 8 blocks**, counting blocks already on the calendar. In restart mode, cap at what's left: roughly one block per free hour. If there's more, say what's moving to tomorrow. A plan Dana can finish beats a full one.
- Show the plan as one small table per day (When | Block), with an emoji per block type: ✉️ email, 📐 math, 📊 finance class, 🎤 behaviorals, 📖 reading/technicals, 🔎 research. Mark new blocks in **bold** and existing ones as *(on calendar)*.
- Ask once whether to put it on the calendar (skip the question if Dana already said yes this session).

## 4. Put it on the calendar
For each new block, create an event on the focus calendar:
- Title `🎯 Focus: <task>`, `colorId: "3"` (purple), one popup reminder at 0 minutes (the phone ping at the start is the motivation cue).
- Description: the first tiny step, then the Notion task link (and the Canvas or file link if there is one). The link is what lets step 0 match the block to its task next time, so never leave it out.
- Future blocks for a task that moved to another day: move them (update the time), don't duplicate them.
- Never invite anyone, and never put focus blocks on Career & Finance or UNC.

## 5. Wrap up my day
When Dana says "wrap up", "done for today", or "what did I get done":
- Run step 0 for today. That covers the checkbox question, Done marking, carry-over, and `↩️ Moved` lines. Then ask once about the carry-over: tomorrow, later, or drop. Update Do Date.
- Delete today's unused focus events only if Dana says to.
- End with one encouraging line about what got done. Nothing about what didn't.

## Keep it cheap
- One Notion query for open tasks (it also covers the step-0 status check), one list call per calendar, one batch create for new tasks.
- If the chat is already long, suggest a fresh chat for big study blocks (deal breakdowns, mock interviews). Put that suggestion in the block's first tiny step.
