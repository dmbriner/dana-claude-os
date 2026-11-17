---
name: apply-online
description: Fill out an online job application (Workday, Greenhouse, Oleeo/tal.net, Lever) in Chrome for one of Dana's internship applications, using saved answers and the application packet already in the firm's folder. Use when Dana says "apply to <role>", "fill out the application", "open the browser and apply", or "continue the <firm> application".
---

# Fill an online application

Paths are relative to the repo root (this file is `skills/apply-online/SKILL.md`; resolve symlinks to find it).

## 0. Load before touching the browser
- `private/application-answers.md`: every standard answer (contact, eligibility, education, work history), school-picker quirks, and the list of fields that are always Dana's call. **If a form asks something not in this file, ask Dana (AskUserQuestion, batched), then append the answer under "Learned answers".**
- `private/profile.json`: `career_root` and Notion IDs.
- The packet: `<career_root>/Recruitment/Firms/<Firm>/Applications/<Role>/` should hold the tailored resume (.pdf and .docx) and cover letter. If it's missing, run the `cover-letter` skill first.
- The Notion Opportunities row for the role (check whether it's already Submitted, so nothing gets applied to twice).

## 1. Check the resume before uploading
Follow the resume rules in memory (`resume-full-page`): one page, filled to the bottom, matching the Fidelity 11-16-26 layout (10.5 pt, about 1.2 line spacing), with no line holding only one or two words. Export with Word through AppleScript and render to PNG to check. If you change it, back up the old file to `Core Assets/Resumes/Versions` first.

## 2. Browser rules (learned the hard way on Workday)
- Open a new tab, decline non-essential cookies, then use the posting's **Apply** button.
- **Sign-in is Dana's.** Stop at the sign-in page and say so; continue once Dana says they're in. "Use My Last Application" only helps if this tenant has a previous application under the same email.
- **Text fields:** click the field, then type. Prefer `find` refs over coordinates.
- **Dropdowns (Workday buttons):** `form_input` doesn't work, and batched coordinate clicks pick the wrong row because the page scrolls when a menu opens. Open the dropdown, take a **full-resolution** screenshot, click the option, then confirm the value. Go one dropdown at a time.
- **Search pickers** (school, field of study, "how did you hear"): type a short query and press Enter. If nothing matches, try a shorter name, then "Other".
- **Dates:** type digits straight into the MM/YYYY box (e.g. `102026`).
- **Files:** use `file_upload` on the hidden file-input ref. Never click "Select files", because it opens a native picker.
- **Back on Workday** can open a "Discard Application?" dialog when the current page has unsaved edits. Click **Continue** (never Discard), **Save and Continue** first, then go back.
- **Prefilled forms (Oracle/Lazard, returning applicants):** fields and attachments carry over from the last application. Before typing, press cmd+a in each text field so you replace the value instead of appending to it. Remove the old resume and cover letter (the Remove button can need two clicks), then upload the new files. Close the "AI Work Summary" pop-up with Cancel.
- After every page, read `get_page_text` and fix anything blank or wrong before moving on. `get_page_text` doesn't show text-input values; check those with a zoomed screenshot.
- Add every school in `application-answers.md` (including high school) and every job, with bullets from the tailored resume, even when the resume is attached.

## 3. Stop before Dana-only steps
Leave voluntary self-ID, consent and terms checkboxes, and **Submit** to Dana. Report what was entered page by page and what's left.

## 4. After Dana submits
- Notion Opportunities: Stage → Submitted, and Submitted → today.
- Append any new answers or form quirks to `private/application-answers.md` (and generic quirks to section 2 above).
- Close the tabs you opened.
