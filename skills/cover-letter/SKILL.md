---
name: cover-letter
description: Write and file a one-page cover letter for one of Dana's finance internship applications, in Dana's own voice and exact .docx format, then save the full submission packet (letter .docx and .pdf, tailored resume, other required files) into the firm's Applications folder and log the links in Notion. Use when Dana asks for a cover letter, application packet, or "do the application for <firm>".
---

# Cover letter + application packet

Paths below are relative to the repo root (this file is `skills/cover-letter/SKILL.md`; resolve symlinks to find it).

## 0. Load the private context (never skip)
- `private/profile.json`: name, contact block, letter template, career folder root (`career_root`), base resume, transcript, and Notion database IDs.
- `private/story.md`: the applicant's experience, approved talking points, and style rules. Every fact in a letter must come from here or from the Notion "Resume" page.

## 1. Read before writing
- **The posting:** fetch the job URL (for Workday, use the `/wday/cxs/<tenant>/<site>/job/...` JSON endpoint). Note requirements, class year, deadline, and required files (cover letter, transcript, questions with character limits).
- **Voice:** model on the canonical letters named in `story.md`.

## 2. Structure
1. "I am writing to express my strong interest in the <program> position in <group/city>." School, major, and minor. One specific line on why this firm.
2. Origin of the interest (see `story.md`), then the most relevant experience, with specifics.
3. A second experience and what the applicant most enjoys.
4. Why this group: tie 2–3 facts from the posting or firm to real experience.
5. Standard close: "I would welcome the opportunity to discuss my qualifications with you and learn more about <Firm> at your earliest convenience. My resume is attached, and I can be reached at <phone> or via email at <email>. Thank you very much for your time and consideration."

Plain, specific sentences. No invented facts. Follow every rule in `story.md`.

## 3. Build the .docx
- Write a spec like `example-spec.json` (date, address starting "Recruiting Team", salutation, body paragraphs). The script adds the contact block and signature from `profile.json`.
- `python3 -I skills/cover-letter/mkletter.py spec.json out.docx`
- Export a PDF with Microsoft Word through AppleScript:
  ```
  with timeout of 45 seconds
  tell application "Microsoft Word"
    open (POSIX file "<docx>")
    delay 3
    save as active document file name "<pdf>" file format format PDF
    close active document saving no
  end tell
  end timeout
  ```
- Count pages: `python3 -I -c "import re,sys;d=open(sys.argv[1],'rb').read();print(len(re.findall(rb'/Type\s*/Page[^s]',d)))" <pdf>`. **It must be exactly 1.** If it runs over, trim the least important clause and rebuild.

## 3b. Tailor the resume (always)
- Start from `base_resume` in `profile.json` (check for a newer file by modified date).
- Write a spec `{"replace": {"<bullet prefix>": "new text" | null}, "drop_sections": ["<heading>"], "add_after": {"<bullet prefix>": ["new bullet"]}}` and run `python3 -I skills/cover-letter/tailor_resume.py base.docx spec.json out.docx`. It warns about any prefix it didn't match.
- Rewrite bullets around the role using only true facts; follow the per-sector rules in `story.md`.
- Export to PDF, confirm 1 page, and save as `<Last> <First>_Resume_<Firm> <YYYY>` (.docx and .pdf) in the application folder, plus a copy in `<career_root>/Core Assets/Resumes`.

## 4. File the packet
- Folder: `<career_root>/Recruitment/Firms/<Firm>/Applications/<Short Firm> <Program> Summer <YYYY>/`.
- Put in: the letter (.docx and .pdf), the tailored resume (.docx and .pdf), the transcript if requested, any answer docs trimmed to the character limit (count them), and a note of anything still missing.
- Copy the letter .docx to `<career_root>/Core Assets/Cover Letters/Versions/<Firm – Program>/`.

## 5. Log it in Notion
In the Opportunities row: URL = posting; Stage = In progress; Priority if relevant. Add a "Links" section with the posting and the folder path. Create the row if missing, linked to the Firms row.

## 6. Reply
List what's in the folder, what's left for the applicant to do, and the deadline.
