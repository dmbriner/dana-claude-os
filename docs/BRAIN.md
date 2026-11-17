# The shared brain

Skills usually start cold: each one forgets who you are and has to be told again. Here, every skill and agent reads one shared folder first, `private/` at the repo root, so a fact written down once is used everywhere.

| File | What's in it | Read by |
|---|---|---|
| `profile.json` | Name, school line, contact details, Notion database IDs, calendar IDs, folder paths, scheduling hours | almost everything |
| `story.md` | Background, experience, talking points, style rules | cover-letter, coffee-chat-prep, apply-online |
| `email-voice.md` | How emails should sound | email-assistant |
| `email-learned.md` | Lessons learned from how drafts were edited | email-assistant |
| `email-drafts-log.md` | What was drafted, so edits can be compared | email-assistant |
| `cache/` | Job postings already seen, SEC lookups | career-tools, market-tools |

`private/` is git-ignored. `profile.example.json` at the repo root shows the shape of `profile.json`, and `plugins/personal-admin/skills/email-assistant/email-voice.example.md` shows the voice file.

## How a skill finds it
Skills are symlinked into `~/.claude/skills/`. A skill resolves its own symlink, walks up to the folder that has `.claude-plugin/marketplace.json` (the repo root), and opens `private/` from there. Python scripts do the same with:

```python
ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / ".claude-plugin" / "marketplace.json").exists())
```

## Learning loops
Two parts of the system learn from corrections and write them back:
- **email-assistant** compares each draft with what was actually sent and adds the difference to `email-learned.md`.
- **itc-research** logs corrections to `corrections-log.md` in the Equity Research folder, and `house-style-curator` turns them into `house-style.md` updates.
