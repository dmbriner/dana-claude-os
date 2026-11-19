---
name: outreach-audit
description: Daily networking audit. Checks which outreach emails Dana actually sent against the times offered on the Reference calendar and the drafts still sitting unsent, picks the top people to email today, rebuilds their drafts with fresh times, and emails Dana a to-send list with the drafted emails. Use when Dana says "who should I reach out to today", "audit my outreach", "what did I actually send", "who did I not email", "outreach to-send", or runs /outreach-audit. Meant to run every morning.
---

# Outreach audit

Finds everyone Dana meant to email but didn't, ranks the top few for today, makes their drafts ready to send, and emails Dana one list. **Never sends anything to anyone except Dana.**

Load from the repo root (walk up to `.claude-plugin/marketplace.json`): `private/profile.json` (`calendars`, `notion.people`, `career_root`, `outreach_sender`, `outreach_mail_account`) and `private/email-voice.md`. Follow the `outreach-email` skill for format, resume, and draft mechanics.

## 1. Audit what was actually sent
Look back 3 days (7 on Mondays).
- **Mail.app sent and drafts:** for accounts Kenan-Flagler, UNC, Investors Title and iCloud, list `messages of mailbox` for every mailbox whose name contains "Sent", plus "Drafts", with `date sent > cutoff`. Record the date, recipients (name and address), subject, and attachment count. Dana replies from iCloud too.
- **Gmail:** `search_threads` with `in:sent newer_than:3d`. Ignore the Daily Recruiting Brief.
- **Reference calendar** (`calendars.reference`): every `CC: <names>` hold from today through 2 weeks out. Each name there was offered times in some draft.

## 2. Classify each person
| Bucket | Test |
|---|---|
| Sent | Appears as a recipient in a Sent folder |
| Unsent draft | Has a draft in Drafts but nothing in Sent |
| Held, never drafted | Has CC holds but no draft and nothing sent. Check Notion People for an address |
| Blocked | No usable address (blank, or an old employer's domain), so the draft can't go out |

Also catch drafts with **no recipient** (thank-you notes typed but never addressed) and look up the address in Notion People.

## 3. Pick today's top 5
Rank the unsent ones by:
1. Fit with Dana's interests (read the `career-interests` memory: consumer/luxury, PE, secondaries, multi-asset credit).
2. Notion Priority = High.
3. Time-sensitivity: thank-you notes after an event go first, and stale drafts offering times that already passed.
4. **Stagger by firm:** no more than 2 people from the same firm or group per day. The rest go on the "Tomorrow" list.

## 4. Rebuild their drafts
- Fresh times from the `scheduling` skill: 3 windows on different days, the soonest available after today, in ET (recipient's zone if different). Check booked meetings that only live in email, like interviews confirmed in a thread ("Let's do 10:30am").
- Rewrite in the `outreach-email` template (old drafts often use "would love to" or questions, so fix them). Newest general resume PDF with no firm in the file name.
- Save new Kenan-Flagler drafts and verify each landed with 1 attachment.
- Deleting old drafts is blocked, so list the superseded ones in the email for Dana to trash.
- Add `CC: <names>` holds on Reference (free, no reminders, `notificationLevel: NONE`). Move any hold whose time changed.

## 5. Email Dana
Send from Gmail to Dana's iCloud address (the same address that gets the Daily Recruiting Brief). Subject: `Outreach To-Send – <Weekday>, <Month D>`. Sections:
1. What you actually sent (by day)
2. Send today: a table of the top 5 with one line on why, and "drafts ready in Kenan-Flagler › Drafts"
3. The drafted emails: one in full, then the interest line for each of the others
4. Tomorrow (staggered)
5. Blocked, needs you (bad addresses, LinkedIn-only, duplicates to trash)

## Rules
- Only email Dana. Never send outreach.
- Never guess an address.
- Don't change Notion Status until Dana says something was sent (then Status → Contacted, Date Contacted → today).
