---
name: interview-prep
description: Build and run Dana's full prep for a finance interview (PE, IB, AM, secondaries) in five parts (the firm, how it makes money, its deals, technicals, behaviorals), saved as one Notion prep page and scheduled as 25-minute focus blocks. Use when Dana says "prep me for my <firm> interview", "I have an interview with <firm>", "help me prepare for <firm>", "quiz me", "mock interview", "practice behaviorals", "walk me through <firm>'s deals", or runs /interview-prep <firm>.
---

# Interview prep

Interviewers test five things. Prep each one in order, and save everything on **one Notion page** so Dana always knows where it lives. Dana has ADHD: each part should be one or two 25-minute blocks, with a first tiny step, never a wall of text.

Load from the repo root (resolve this file's symlink and walk up to `.claude-plugin/marketplace.json`):
- `private/profile.json`: Notion IDs and calendars
- `private/story.md`: Dana's background, material, and rules. **Never invent experience.** Where a story is missing, leave a prompt for Dana to fill in.
- `private/story-bank.md`: behavioral stories Dana has already practiced (create it the first time)

## 0. Set up
- Find the firm in Notion **Firms** and the people in **People**. If `coffee-chat-prep` already wrote a brief on someone's People page, reuse it and don't redo the research.
- Ask only what you can't find: interview date and time, format (phone, Zoom, superday), the interviewer's name, and the role.
- Create or open the prep page as a child of the firm's Opportunity row (or the Firms row if there isn't one), titled `Interview Prep – <Firm> – <date>`. Add the date to the Opportunity's Tasks.

## The five parts (one section each on the prep page)

### 1. The firm (25 min)
A 30-second summary Dana could say out loud: what it does, its size (AUM and fund), strategy, sectors, offices, leadership, recent news. Sources linked. Include a "don't confuse with" line if there's a look-alike firm.

### 2. How it makes money (25 min)
Explain the business model in plain words: who the LPs are, the fund and its size, deal size, control vs. minority, the value-creation playbook (operations team, add-ons, pricing), how it exits. For PE: what makes this firm's edge different from its peers. End with "what this means for an intern": the work you'd actually do.

### 3. The deals (25 min per 2 to 3 deals)
A table of every deal you can source, then one card per major deal:
- **What:** buyer, seller, business, date, price, and multiple if disclosed (say "not disclosed" rather than guessing)
- **Why the seller sold** and **why the firm bought**
- **How it was done:** structure (carve-out, take-private, add-on), financing if known, advisors
- **How you'd value it:** the method and the key numbers or assumptions (for a carve-out: segment EBITDA − standalone costs = pro forma EBITDA; separation costs in uses)
- **Value creation and risks**
- **Questions they might ask you** about it ("why would you pay that multiple?", "what would you fix first?") with a short answer to each
For depth on a big deal, suggest a fresh chat in the block's first tiny step to save usage.

### 4. Technicals (25 min blocks)
Pick by firm type. PE: LBO walkthrough, sources and uses, IRR and MOIC math, why leverage boosts returns, the three statements and how they link, EBITDA adjustments, plus the firm's strategy (carve-outs: TSAs, standalone costs, carve-out financials). IB: accounting, EV vs. equity value, DCF, comps, M&A accretion and dilution. Write 5 to 10 questions with model answers, then quiz Dana one question at a time and score each in the Notion **Technicals Bank**. Missed questions come back first next time.

### 5. Behaviorals (2 × 25 min minimum)
Draft from `story.md` only: tell me about yourself (90 seconds), why this field, why this strategy, why this firm (with one line from Dana's own conversations with the firm), plus STAR stories for responsibility, a pitch, teamwork or conflict, failure, and strengths and weaknesses. Mark anything missing as a prompt to fill in. Add 3 smart questions to ask at the end. Once Dana has practiced a story, save the final version in `private/story-bank.md`, so the next interview starts from it.

## Practice mode
"Quiz me" or "mock interview": act as the interviewer. Ask one question at a time, wait for Dana's answer, then give one strength, one fix, and a 1-to-10 score. Mix behaviorals, technicals, and the firm's deals the way a real interview would. End with the 3 weakest answers and put them on tomorrow's plan.

## Schedule it
Hand the blocks to `plan-my-day`: behaviorals and the firm first, then deals, technicals spread out (spaced repetition beats cramming), and a final mock interview block the day before. Each block's first tiny step goes on the calendar event.

## Rules
- Facts need sources. Undisclosed numbers stay undisclosed.
- Follow `story.md` rules (BitGo only for fintech, FIG, or deal-structuring roles, and so on).
- Keep the prep page skimmable: headers per part, short bullets, the answers Dana will say written in Dana's plain voice.
