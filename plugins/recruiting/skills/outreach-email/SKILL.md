---
name: outreach-email
description: Draft a cold or warm networking email from Dana to someone at a finance firm (alumni, referral, friend-of-a-friend) in Dana's formal outreach format, with 3 offered times and the right resume attached, saved as a draft in the Kenan-Flagler Mail.app account. Use when Dana says "draft an email to <name>", "email <name> at <firm>", "reach out to <name>", "cold email", or "make the draft" for a person in Notion People.
---

# Outreach email

Drafts one networking email per person, saves it in Dana's **Kenan-Flagler** inbox (Mail.app) as a draft, and never sends it.

Load from the repo root (resolve this file's symlink, walk up to `.claude-plugin/marketplace.json`):
- `private/profile.json`: Notion IDs (`notion.people`), `calendars`, `career_root`, `school_line`, `outreach_sender` and `outreach_mail_account` (the Mail.app account for drafts).
- `private/email-voice.md` and `private/email-learned.md`: voice rules and past corrections.

## 1. Check before drafting
Follow `email-assistant` step 3b for each person:
1. **Already emailed?** Search Gmail (`search_threads` on name and address) and Mail.app (`plugins/personal-admin/skills/scheduling/mail.sh search "<last name>"`). If a thread exists, this is a follow-up, not outreach. Say so and stop.
2. **Still at that firm?** Read the person's Notion People page. If the email on file is at an old employer's domain (e.g. their old bank's domain for someone now in PE), it will bounce. Tell Dana and don't draft until there's a current address.
3. **Event coming up?** Check Career & Finance for the next 4 weeks for an event at that firm. If one is coming, wait until after it.

## 2. Times
Use the `scheduling` skill: exactly 3 windows, the soonest available, on different days, in ET. Skip any window Dana can't realistically send in time for (e.g. tomorrow when the address isn't known yet).

## 3. Write it in Dana's format
Formal and plain. **No questions anywhere in the email.** No casual phrases ("I'd love to", "quick call", "day to day", "in case it's helpful", "so much", exclamation points). No "so" as a connector. Use this template, changing only the bracketed parts:

```
Subject: UNC Kenan-Flagler Student Interested in [Private Equity / Investment Banking] at [Firm]

Hi [First name],

I hope you are well. My name is Dana Briner, and I am a sophomore at UNC Kenan-Flagler studying Business Administration. [Connection line: "I recently came across your profile in the alumni database." / "I am a friend of [Name]'s." / "[Name] suggested I reach out."] [Optional: "I recently applied to [Firm]'s [program]."] I am very interested in [private equity / investment banking / the field] at [Firm] and would like to hear about your experience working there. Please let me know if you might have time for a brief call in the next few weeks.

My availability (ET) is as follows, but I am happy to work around your schedule:

- [Day M/D H:MM AM - H:MM PM]
- [Day M/D H:MM AM - H:MM PM]
- [Day M/D H:MM AM - H:MM PM]

I have attached my resume for your reference as well. I look forward to hearing from you. Thank you for your time.

Best,
Dana
```

- The interest line names the firm: "I am very interested in private equity at KKR," not "I saw you're on the PE team."
- Don't name portfolio companies or deals unless Dana asks for a specific hook.
- Show Dana the text in chat before or while saving the draft.

## 4. Resume
**The file name must never name a different firm.** The recipient sees the attachment name, so `Resume_Roark 2028.pdf` going to someone at Permira tells them the resume was made for Roark. Pick in this order:
1. The resume from Dana's application to *that same firm*: `<career_root>/Recruitment/Firms/<Firm>/Applications/<program>/*.pdf`.
2. A version tailored to *that same firm* in `<career_root>/Core Assets/Resumes/`.
3. Otherwise, the newest general PDF with no firm in the name (e.g. `Core Assets/Resumes/Versions/Dana Briner Resume <date>.pdf`). If the only recent PDF has another firm in its name, ask Dana. Don't attach it.
Attach the PDF, never the .docx. Before saving, check that the attachment name contains the recipient's firm or no firm at all.

## 5. Save the draft (Kenan-Flagler, Mail.app)
Run with `osascript - "<resume path>"`, putting the body in a variable:

```applescript
tell application "Mail"
  set msg to make new outgoing message with properties {subject:"<subject>", content:theBody, sender:"<outreach_sender>", visible:false}
  tell msg to make new to recipient at end of to recipients with properties {address:"<email>", name:"<Full Name>"}
  tell content of msg to make new attachment with properties {file name:(POSIX file resPath) as alias} at after last paragraph
  delay 2
  save msg
  close msg saving yes
end tell
```

Then confirm it landed: list `messages of mailbox "Drafts"` of account "Kenan-Flagler" whose subject matches, and check the attachment count is 1.

## 6. Afterward
- Create `CC: <Full Name>` holds on the Reference calendar for the 3 windows (free/transparent, no reminders, `notificationLevel: NONE`).
- Leave the People Status alone until Dana sends it. When Dana says it's sent: Status → Contacted, Date Contacted → today.
- If Dana edits the draft before sending, add the difference to `private/email-learned.md`.

## Rules
- Never send. Drafts only.
- Never guess an email address or a company's email format.
- One email per person. Don't CC anyone unless Dana asks.
