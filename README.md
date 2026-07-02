# Six Thinkers

Six thinkers refitted for the algorithmic century — **Gramsci, Kropotkin, Graeber, Freire, Deleuze, Bakunin**. Free HTML courses from The Kiwi Dialectic.

**Live at:** https://robertmccallnz.github.io/six-thinkers/
**Social Kit (free, CC BY-SA 4.0):** https://robertmccallnz.github.io/six-thinkers/social-kit/

## What this repo is

A static HTML course site for the six-thinker series that anchors the AI Warrior curriculum. Each course has a landing page and one HTML file per lesson. Every page carries two donation-friendly CTAs:

- **Read on Substack** → the original post, subscriber comments, and the discussion thread
- **☕ Koha via Ko-fi** → https://ko-fi.com/thekiwidialectic

## Structure

```
index.html                                             — Hub (six courses)
<slug>/index.html                                      — Per-course landing page
<slug>/lesson-NN.html                                  — Individual lesson pages
assets/style.css                                       — Shared design system
courses.json                                           — Source of truth
build.py                                               — Regenerates the site from courses.json
social-kit/                                            — Public social media kit (21 visuals + scripts)
```

## The six courses

| Slug | Thinker | Lessons | Status |
|---|---|---|---|
| `gramsci-for-aotearoa` | Gramsci | 7 | Live |
| `kropotkin-mutual-aid` | Kropotkin | 7 | Live |
| `graeber-debt-bullshit-jobs-direct-democracy` | Graeber | 7 | Live |
| `freire-mo-aotearoa` | Freire | 7 | Upcoming |
| `gilles-deleuze` | Deleuze | 1 | Upcoming |
| `bakunin-mo-aotearoa` | Bakunin | 7 | Upcoming |

**Total: 36 lesson pages + 6 course indexes + 1 hub.**

## Build

```bash
python3 build.py
```

Reads `courses.json`, writes every HTML file. No dependencies beyond stdlib.

To change lesson titles, teasers, or Substack links, edit `courses.json` and re-run `build.py`. To change design, edit the `CSS` constant at the top of `build.py`.

## Content status

Right now every lesson page contains title, teaser, and the two CTAs. The **full lesson bodies still live on Substack** and each page links there. Once bodies are ported into HTML, the Substack link will remain as the discussion / comment thread.

Recommended porting workflow:

1. Substack → Settings → Exports → download HTML export
2. For each lesson, drop the extracted `<article>` markup into a new `body_html` field in `courses.json`
3. Update `build.py` to render `body_html` in place of the placeholder block
4. Re-run `build.py`

## Ecosystem

- **Course calendar:** https://robertmccallnz.github.io/kiwidialecticcalendar-/
- **AI Warrior (parent series):** https://robertmccallnz.github.io/ai-warrior/
- **AI Literacy for Families:** https://robertmccallnz.github.io/ai-literacy-for-families/
- **Cooperatives in Aotearoa:** https://robertmccallnz.github.io/cooperative-aotearoa/
- **Te Pā Tūwatawata:** https://te-pa.org

## Licence

CC BY-SA 4.0. Share, remix, translate. The only thing you can't do is lock it up again.

Train the mind. Arm the class.
