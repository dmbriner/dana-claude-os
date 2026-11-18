---
name: plan-my-day
description: Turn a messy brain dump into Notion tasks and a realistic day of 25-minute focus blocks on Dana's calendar, each with a phone alert, a first tiny step, and a link to the task. Use when Dana says "plan my day", "plan tomorrow", "here's everything I need to do", "brain dump", "dump:", "what should I work on", "I don't know where to start", or runs /plan-my-day. Also use for "wrap up my day" (end-of-day check-in) and "move this block".
---

# Plan my day

Dana has ADHD and jumps between tasks. The goal is to get everything out of their head, pick a realistic amount for today, and make each block easy to start. The plan should be short and kind, never a lecture.

Load `private/profile.json` from the repo root (resolve this file's symlink, walk up to `.claude-plugin/marketplace.json`). Use `notion.tasks` and `calendars` from it.

## 1. Capture the dump
Pull every to-do out of Dana's message, however messy. For each one:
- **Check Notion Tasks first** (one SQL query on open tasks). If a matching open task exists, update it (Do Date, Effort, Priority) instead of creating a duplicate.
- Otherwise create it in Tasks with: Name (short, verb first), Area, Kind, Priority, **Effort (min)** in multiples of 25, **Do Date** (when Dana plans to do it), **Deadline** only if there's a real external due date, and relations (Class, Firm, Person, Opportunity) when obvious.
- Put a `First tiny step:` line at the top of each task page: one physical action that takes under 2 minutes ("open PS10 and do question 1 only"). For study tasks, also put the material itself on the page (a short explainer plus practice questions), so starting means only reading.
- Anything that needs another skill gets that skill: thank-you or outreach email → `email-assistant` (draft only, never send); coffee chat → `coffee-chat-prep`; event email → `add-event`; times to offer → `scheduling`.

## 2. See the real day
- Get the current time (`date`). If it's evening, plan tonight lightly and put the real plan on tomorrow.
- List events from **every** calendar in `profile.calendars` for the planning window, including `canvas` (assignment due dates) and `assignments`. Booked events and classes are busy. Reference-calendar holds are not.
- **Flag conflicts** (two events at once) in one line each, and ask which one Dana is going to. Don't fix them silently.
- Pull open Tasks with Do Date ≤ the planning day, or Deadline within 7 days. Canvas due dates count as deadlines: put them on the matching task.
- Overdue tasks (Do Date in the past, not Done): list them in one short line and ask "today, later this week, or drop?" Never bulk-change them without asking.

## 3. Build the plan
- Find free windows with `plugins/personal-admin/skills/scheduling/free_windows.py`.
- Use 25-minute blocks with 5 minutes between them, and a 10-minute break after every 2 blocks. A 50-minute task becomes two blocks ("round 1 of 2").
- Order by deadline first, then hardest work in the morning, email and admin first thing (it clears the head), and low-energy reading at night.
- **Cap the day at about 6 to 8 blocks.** If there's more, say what's moving to tomorrow. A plan Dana can finish beats a full one.
- Show the plan as one small table per day (When | Block), with an emoji per block type: ✉️ email, 📐 math, 📊 finance class, 🎤 behaviorals, 📖 reading/technicals, 🔎 research.
- Ask once whether to put it on the calendar (skip the question if Dana already said yes this session).

## 4. Put it on the calendar
For each block, create an event on `calendars.focus` (fall back to `calendars.personal` if there's no focus calendar):
- Title `🎯 Focus: <task>`, `colorId: "3"` (purple), one popup reminder at 0 minutes (the phone ping at the start is the motivation cue).
- Description: the first tiny step, then the Notion task link (and the Canvas or file link if there is one).
- Never invite anyone, and never put focus blocks on Career & Finance or UNC.

## 5. Wrap up my day
When Dana says "wrap up", "done for today", or "what did I get done":
- List today's focus blocks and ask which ones got done (one question with checkboxes).
- Mark those tasks Done. For the rest, ask once: tomorrow, later, or drop. Then update Do Date.
- Delete today's unused focus events only if Dana says to.
- End with one encouraging line about what got done. Nothing about what didn't.

## Keep it cheap
- One Notion query for open tasks, one list call per calendar, one batch create for new tasks.
- If the chat is already long, suggest a fresh chat for big study blocks (deal breakdowns, mock interviews). Put that suggestion in the block's first tiny step.
