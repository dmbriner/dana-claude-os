# Dossier JSON schema

`build.py` fills `assets/dossier.html` with one JSON file shaped like this. Every field is optional: a missing section is simply not shown, which is how firm-only mode hides the person section.

## How text and citations work

- Text fields accept `**bold**` and `[n]` citations.
- `src` fields take a source number or a list of them.
- Every `n` must exist in `sources`.

## Top-level shape

```json
{
  "meta": {
    "title": "Citi Media & Telecom",
    "subtitle": "One line on what this dossier is for",
    "date": "Nov 19, 2026",
    "mode": "firm | person | panel | deal",
    "purpose": "Superday Dec 3",
    "tags": ["IB", "TMT", "New York"],
    "slug": "citi-mt-2026-11-19",
    "notion_url": "https://..."
  },
  "kpis": [{"label": "IB fees 2025", "value": "$4.1bn", "note": "+18% YoY", "src": 3}],
  "tldr": ["5 bullets, each with a citation [3]"],

  "person": {"name": "", "title": "", "group": "", "location": "", "summary": "",
    "licenses": ["SIE", "Series 79"],
    "timeline": [{"dates": "2024–", "firm": "", "role": "", "note": "", "src": 1}],
    "education": [{"school": "", "detail": "", "src": 2}],
    "team_lead": {"name": "", "title": ""},
    "team": [{"name": "", "title": "", "note": "", "is_subject": true}],
    "deals_named": ["text with [n]"],
    "appearances": [{"date": "", "text": "", "src": 4}],
    "hooks": [""],
    "overlap": [""]},
  "people": ["same shape as person, used instead of person in panel mode"],

  "firm": {"name": "", "summary": "",
    "snapshot": [{"k": "HQ", "v": "", "src": 1}],
    "strategy": [""],
    "news": [{"date": "", "text": "", "src": 1}],
    "competitors": [{"name": "", "edge": "", "src": 1}]},

  "group": {"name": "", "summary": "",
    "coverage": [""],
    "leaders": [{"name": "", "title": "", "note": "", "src": 1}],
    "structure": "",
    "junior_life": "",
    "rankings": [{"table": "", "rank": "", "prior": "", "note": "", "src": 1}]},

  "charts": [
    {"section": "firm | group | deals | market | deal-<index>", "type": "bar",
     "title": "", "unit": "", "series": [{"label": "", "value": 1.2, "display": "$1.2bn"}],
     "note": "", "src": 1},
    {"section": "firm", "type": "line", "title": "",
     "points": [{"x": "Dec 25", "y": 61.2}], "marks": [{"x": "Mar 26", "label": "Deal announced"}],
     "src": 1}
  ],

  "deals": [{"name": "", "date": "", "type": "M&A | ECM | DCM | LevFin | PE",
    "size": "", "role": "", "status": "", "headline": "", "person_named": false,
    "src": 1, "deep": true,
    "overview": "",
    "terms": [{"k": "", "v": "", "src": 1}],
    "valuation": [{"k": "", "v": "", "src": 1}],
    "advisors": [{"role": "", "firms": [""], "people": [""], "src": 1}],
    "timeline": [{"date": "", "text": "", "src": 1}],
    "rationale": [""],
    "proceeds": "",
    "reaction": [""],
    "angle": "",
    "pitch": "",
    "qa": [{"q": "", "a": ""}],
    "opinion": ""}],

  "market": [{"trend": "", "detail": "", "why": "", "src": 1}],

  "recruiting": {"facts": [{"k": "", "v": "", "src": 1}],
    "format": [""],
    "postings": [{"role": "", "location": "", "deadline": "", "url": "", "notes": ""}],
    "comp": ""},

  "angles": {"why_firm": [""], "why_group": [""], "links": [""]},
  "questions": [{"q": "", "star": true, "why": ""}],
  "drill": [{"q": "", "a": "", "topic": "Firm | Group | Deals | Market | Technicals | Fit"}],
  "gaps": [{"what": "", "where": ""}],
  "sources": [{"n": 1, "title": "", "publisher": "", "date": "", "url": ""}]
}
```

## How fields render

- **Tombstones:** the deal list shows every deal as a tombstone. Deals with `"deep": true` also get a full breakdown card, and clicking a tombstone opens its card.
- **Team map:** in `team`, the entry with `"is_subject": true` (the person themselves) is highlighted.
- **Drill:** the drill is an interactive flashcard deck. It remembers which cards were marked "got it," per browser.
