---
name: add-event
description: Turn a recruiting/networking event email (registration confirmation, RSVP, panel or info-session invite) into an event on Dana's Career & Finance Google calendar, with location, details, links, and the check-in QR code attached. Use when Dana says "add this event to my calendar", "put the <firm> event on my calendar", "add the QR code", or runs /add-event. Emails WITH a .ics invite are already handled automatically by ~/Scripts/email-alerts/events.py, so check the calendar first.
---

# Add an event email to the calendar

Keep this cheap: one Gmail search, one read, one calendar check, one write.

1. **Find the email.** `search_threads` with the firm/event name, `newer_than:30d`. Read only the one thread with `get_thread` (PLAIN_TEXT unless you need image names).
2. **Check for it already.** `list_events` on Career & Finance (ID in `private/profile.json` → `calendars.career_finance`; find the repo root by resolving this file's symlink) for that day. The local script may have added it (description starts "Added automatically from:"), or Dana may have a bare placeholder on Personal (primary).
   - If it's on Career & Finance, `update_event` it instead of creating a new one.
   - If it's only on Personal, create it on Career & Finance, then delete the Personal copy with `notificationLevel: NONE`, and tell Dana you did.
3. **QR code (if the email has one).** `download_gmail_attachment` for the `qr*.png` file. Copy the saved file into the scratchpad. Upload it with `Google_Drive__create_file`, passing `base64Content` as a file reference `sha256:<hash>:<scratchpad path>`; the tool-results path is rejected. Never hand-type base64, because it corrupts the image. Check that the Drive `fileSize` matches the downloaded size. Also save a copy to `Career & Finance/Recruitment/Events/<YYYY-MM-DD> <Title>/QR code.png`.
4. **Write the event.** Title "<Firm> <Event name>". Include the full venue address as the location. Add reminders 1 day before and 1 hour before. Attach the Drive QR with `attachments`. The description (HTML ok) covers:
   - registration status and date
   - what the event is and who attends
   - what Dana registered for and which resume she submitted, if known
   - recruiter contact
   - people she has met from that firm (check recent emails or Notion People)
   - links to the event page, the confirmation email (`https://mail.google.com/mail/u/0/#all/<threadId>`), and the QR code
5. **Report** in 3 to 5 lines: the event, calendar, what's attached, and anything moved or deleted.

Never invent details; only use what's in the email or Dana's records.
