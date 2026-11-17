# recruiting

Finance internship recruiting.

## Agent
- `career-finance`: top-level delegate for recruiting prep, applications, networking follow-up, and personal finance. It has a routing table, so it calls the skills below (and the `personal-admin` and `itc-research` plugins) instead of starting from scratch.

## Skills
| Skill | What it does |
|---|---|
| `cover-letter` | Writes a one-page letter by cloning a real letter's formatting, tailors the resume bullet by bullet, exports PDFs through Word, and files the packet. |
| `apply-online` | Fills Workday, Greenhouse, Oleeo, and Lever applications in Chrome, using saved answers and the packet already in the firm's folder. |
| `coffee-chat-prep` | Researches a contact, their group's deals, and their market, then writes a one-screen prep brief. |
| `add-event` | Turns a recruiting-event email into a calendar event with location, links, and the check-in QR code. |

Each skill loads shared context from `private/` at the repo root (see `docs/BRAIN.md`).

## Install

```
/plugin install recruiting --marketplace dmbriner/dana-claude-os
```
