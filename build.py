#!/usr/bin/env python3
"""
Six Thinkers — build script.

Generates a static site containing all six 'AI Warrior' thinker courses
as HTML, driven from courses.json.

Structure produced:
  index.html                          — Hub landing page (all 6 thinkers)
  <slug>/index.html                   — Per-course index (lesson list)
  <slug>/lesson-N.html                — Per-lesson page (title, teaser, CTAs)
  assets/style.css                    — Shared design system
  courses.json                        — Source of truth (committed)

Every lesson page carries two CTAs:
  1. Ko-fi (donate)   — https://ko-fi.com/thekiwidialectic
  2. Substack (read on Substack, subscribe, discuss) — the lesson's Substack URL
"""
import json
import re
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent
COURSES_PATH = ROOT / "courses.json"
EPISODES_PATH = ROOT / "episodes.json"

KOFI_URL = "https://ko-fi.com/thekiwidialectic"
SUBSTACK_HOME = "https://kiwidialectic.substack.com"
CALENDAR_URL = "https://robertmccallnz.github.io/kiwidialecticcalendar-/github-calendar-connector.html"
REPO_URL = "https://github.com/robertmccallnz/six-thinkers"

# Palette per thinker — one accent colour each. Dark background stays consistent.
THINKERS = {
    "gramsci-for-aotearoa": {
        "display": "Gramsci",
        "subtitle": "for Aotearoa",
        "accent": "#d7261e",   # red star
        "eyebrow": "01 · Hegemony",
        "kaupapa": "Power, hegemony, institutions, and counter-power from below.",
    },
    "kropotkin-mutual-aid": {
        "display": "Kropotkin",
        "subtitle": "& Mutual Aid",
        "accent": "#e8a83a",   # kōura gold
        "eyebrow": "02 · Cooperation",
        "kaupapa": "Cooperation, survival, working-class care, and socialist practice.",
    },
    "graeber-debt-bullshit-jobs-direct-democracy": {
        "display": "Graeber",
        "subtitle": "Debt · Bullshit Jobs · Direct Democracy",
        "accent": "#4fa3b8",   # tāmure teal
        "eyebrow": "03 · Anthropology",
        "kaupapa": "Debt as a tool of power, work made meaningless by design, and how ordinary people run things without bosses.",
    },
    "freire-mo-aotearoa": {
        "display": "Freire",
        "subtitle": "mō Aotearoa · Pedagogy of the Algorithm",
        "accent": "#8fbf5e",   # kākāriki green
        "eyebrow": "04 · Pedagogy",
        "kaupapa": "Paulo Freire's pedagogy of the oppressed, refitted for the age of generative AI and Aotearoa's own kura kaupapa Māori.",
    },
    "gilles-deleuze": {
        "display": "Deleuze",
        "subtitle": "Rhizomes · Assemblages · Lines of Flight",
        "accent": "#b47ee0",   # purple / heke
        "eyebrow": "05 · Rhizome",
        "kaupapa": "Rhizomes, assemblages, and lines of flight — Deleuze's ideas for those who teach, create, and organise.",
    },
    "bakunin-mo-aotearoa": {
        "display": "Bakunin",
        "subtitle": "mō Aotearoa · Tangi o te Tāheke",
        "accent": "#e06f4f",   # tāheke orange
        "eyebrow": "06 · Federation",
        "kaupapa": "Federalist, anti-authoritarian socialism — the man Marx feared, read for Aotearoa.",
    },
}

ORDER = list(THINKERS.keys())


CSS = """
:root {
  --bg: #0a0a0a;
  --bg-2: #121212;
  --bg-3: #1a1a1a;
  --fg: #f4ecd8;
  --muted: #9c8c5c;
  --line: #2a2418;
  --kōura: #e8a83a;
  --red: #d7261e;
  --accent: var(--accent-course, #d7261e);
  --text-sm: 14px;
  --text-lg: 18px;
  --text-xl: 22px;
  --text-2xl: 30px;
  --text-3xl: 44px;
  --text-4xl: 62px;
  --shell: 1120px;
  --pad: 24px;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--fg);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 17px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
h1, h2, h3, h4 {
  font-family: 'Bebas Neue', 'Oswald', 'Helvetica Neue', Arial, sans-serif;
  letter-spacing: .06em;
  font-weight: 500;
  line-height: 1.1;
  margin: 0 0 .4em 0;
}
h1 { font-size: var(--text-4xl); }
h2 { font-size: var(--text-3xl); }
h3 { font-size: var(--text-2xl); }
h4 { font-size: var(--text-xl); }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .8em; letter-spacing: .1em; text-transform: uppercase; }

.wrap {
  max-width: var(--shell);
  margin: 0 auto;
  padding: 0 var(--pad);
}
.shell { max-width: var(--shell); margin: 0 auto; padding: 0 var(--pad); }

/* Header */
.site-nav {
  border-bottom: 1px solid var(--line);
  background: var(--bg);
  position: sticky; top: 0; z-index: 20;
  backdrop-filter: blur(6px);
}
.site-nav .row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 0;
}
.site-nav a { color: var(--fg); font-size: 14px; margin-left: 20px; }
.site-nav a.active { color: var(--accent); }
.brand { font-family: 'Bebas Neue', sans-serif; letter-spacing: .18em; font-size: 20px; color: var(--fg); }
.brand span { color: var(--accent); }

/* Hero */
.hero { padding: 80px 0 60px; border-bottom: 1px solid var(--line); }
.hero .eyebrow { color: var(--accent); letter-spacing: .12em; font-family: ui-monospace, monospace; font-size: 13px; text-transform: uppercase; margin-bottom: 20px; }
.hero h1 { max-width: 20ch; }
.hero .kaupapa { max-width: 60ch; color: var(--muted); font-size: var(--text-lg); margin-top: 24px; }

/* Grid of cards */
.grid {
  display: grid;
  gap: 22px;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  padding: 60px 0;
}
.card {
  border: 1px solid var(--line);
  padding: 28px;
  background: var(--bg-2);
  transition: border-color .2s, transform .2s;
}
.card:hover { border-color: var(--accent); transform: translateY(-2px); }
.card .no { color: var(--accent); font-family: ui-monospace, monospace; font-size: 13px; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 14px; }
.card h3 { font-size: var(--text-xl); margin-bottom: 8px; }
.card p { color: var(--muted); font-size: 15px; margin: 0 0 18px 0; }
.card .card-link { color: var(--accent); font-size: 14px; font-weight: 600; }

/* Lesson list */
.lessons { padding: 40px 0 80px; }
.lesson-row {
  display: grid;
  grid-template-columns: 60px 1fr auto;
  gap: 24px;
  padding: 20px 0;
  border-bottom: 1px solid var(--line);
  align-items: baseline;
}
.lesson-row .n { color: var(--accent); font-family: ui-monospace, monospace; font-size: 13px; }
.lesson-row h3 { font-size: 20px; margin: 0 0 6px 0; font-family: 'Inter', sans-serif; letter-spacing: 0; font-weight: 600; }
.lesson-row p { color: var(--muted); font-size: 14px; margin: 0; }
.lesson-row a.read { color: var(--accent); font-size: 14px; font-weight: 600; white-space: nowrap; }

/* Lesson page */
.lesson {
  max-width: 68ch;
  padding: 60px 0;
}
.lesson .crumbs { color: var(--muted); font-size: 14px; margin-bottom: 30px; }
.lesson .crumbs a { color: var(--muted); }
.lesson h1 { font-family: 'Inter', sans-serif; font-weight: 700; font-size: 34px; letter-spacing: -0.01em; line-height: 1.2; margin-bottom: 20px; }
.lesson .teaser { color: var(--muted); font-size: 19px; line-height: 1.6; margin-bottom: 40px; padding-bottom: 30px; border-bottom: 1px solid var(--line); }
.lesson .body { font-size: 17px; line-height: 1.8; }
.lesson .body p { margin: 0 0 1.2em 0; }
.lesson .placeholder {
  border: 1px dashed var(--line);
  padding: 30px;
  color: var(--muted);
  font-size: 15px;
  margin: 20px 0 40px;
  background: var(--bg-2);
}
.lesson .placeholder strong { color: var(--fg); }

/* CTAs */
.ctas {
  display: flex; flex-wrap: wrap; gap: 14px;
  padding: 30px 0;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  margin: 40px 0;
}
.btn {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 14px 22px;
  font-family: 'Bebas Neue', sans-serif;
  letter-spacing: .12em;
  font-size: 15px;
  border: 1px solid var(--accent);
  color: var(--fg);
  background: transparent;
  transition: background .2s, color .2s;
}
.btn:hover { background: var(--accent); color: var(--bg); text-decoration: none; }
.btn.kofi { border-color: var(--kōura); }
.btn.kofi:hover { background: var(--kōura); color: var(--bg); }
.btn.substack { border-color: var(--fg); }
.btn.substack:hover { background: var(--fg); color: var(--bg); }
.ctas .note { color: var(--muted); font-size: 13px; margin: 0; width: 100%; }

/* Pager */
.pager {
  display: flex; justify-content: space-between;
  padding: 30px 0;
  border-top: 1px solid var(--line);
}
.pager a { color: var(--fg); font-family: 'Bebas Neue', sans-serif; letter-spacing: .12em; font-size: 15px; }
.pager .placeholder { color: var(--line); }

/* Footer */
footer.site-footer {
  border-top: 1px solid var(--line);
  padding: 50px 0 40px;
  color: var(--muted);
  font-size: 14px;
  background: var(--bg-2);
  margin-top: 80px;
}
.site-footer .row { display: flex; flex-wrap: wrap; gap: 30px; justify-content: space-between; align-items: flex-start; }
.site-footer h4 { color: var(--fg); font-size: 14px; letter-spacing: .12em; margin: 0 0 12px 0; }
.site-footer a { color: var(--muted); display: block; margin: 4px 0; }
.site-footer a:hover { color: var(--accent); }
.site-footer .copy { color: var(--muted); font-size: 13px; margin-top: 30px; opacity: .7; }

/* Responsive */
@media (max-width: 700px) {
  :root { --text-4xl: 40px; --text-3xl: 32px; --text-2xl: 24px; --text-xl: 19px; }
  .site-nav a { margin-left: 12px; font-size: 13px; }
  .lesson-row { grid-template-columns: 40px 1fr; }
  .lesson-row a.read { grid-column: 2; padding-top: 6px; }
  .hero { padding: 50px 0 40px; }
}
""".strip()


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{root}assets/style.css">
{style_var}
</head>
<body>"""


def nav(root, active=None):
    def item(key, label, href):
        cls = ' class="active"' if active == key else ''
        return f'<a href="{root}{href}"{cls}>{label}</a>'
    links = [
        item('home', 'Six Thinkers', 'index.html'),
        item('gramsci', 'Gramsci', 'gramsci-for-aotearoa/index.html'),
        item('kropotkin', 'Kropotkin', 'kropotkin-mutual-aid/index.html'),
        item('graeber', 'Graeber', 'graeber-debt-bullshit-jobs-direct-democracy/index.html'),
        item('freire', 'Freire', 'freire-mo-aotearoa/index.html'),
        item('deleuze', 'Deleuze', 'gilles-deleuze/index.html'),
        item('bakunin', 'Bakunin', 'bakunin-mo-aotearoa/index.html'),
    ]
    return f"""<nav class="site-nav">
  <div class="shell row">
    <a href="{root}index.html" class="brand">SIX <span>THINKERS</span></a>
    <div>{''.join(links)}</div>
  </div>
</nav>"""


def ctas_block(substack_url, note=None):
    default_note = (
        'Read the full lesson on Substack. If this course helps you, '
        f'kick a koha into the tin — every dollar keeps this work free for everyone else.'
    )
    return f"""<div class="ctas">
  <a class="btn substack" href="{escape(substack_url)}" target="_blank" rel="noopener">Read on Substack →</a>
  <a class="btn kofi" href="{KOFI_URL}" target="_blank" rel="noopener">☕ Koha via Ko-fi</a>
  <p class="note">{escape(note or default_note)}</p>
</div>"""


def footer():
    return f"""<footer class="site-footer">
  <div class="shell">
    <div class="row">
      <div>
        <h4>SIX THINKERS</h4>
        <a href="{SUBSTACK_HOME}" target="_blank">The Kiwi Dialectic on Substack</a>
        <a href="{KOFI_URL}" target="_blank">Support on Ko-fi</a>
        <a href="{CALENDAR_URL}" target="_blank">Course calendar</a>
      </div>
      <div>
        <h4>OTHER COURSES</h4>
        <a href="https://robertmccallnz.github.io/ai-warrior/" target="_blank">AI Warrior</a>
        <a href="https://robertmccallnz.github.io/ai-literacy-for-families/" target="_blank">AI Literacy for Families</a>
        <a href="https://robertmccallnz.github.io/cooperative-aotearoa/" target="_blank">Cooperatives in Aotearoa</a>
        <a href="https://te-pa.org" target="_blank">Te Pā Tūwatawata</a>
      </div>
      <div>
        <h4>OPEN</h4>
        <a href="https://robertmccallnz.github.io/kd-dialogues/" target="_blank">kd-dialogues · audio site</a>
        <a href="https://github.com/robertmccallnz/kd-dialogues" target="_blank">kd-dialogues · repo (dialogues live here)</a>
        <a href="{REPO_URL}" target="_blank">six-thinkers · repo</a>
        <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank">CC BY-SA 4.0</a>
      </div>
    </div>
    <p class="copy">© The Kiwi Dialectic · Made in Ōtepoti Dunedin · Train the mind. Arm the class.</p>
  </div>
</footer>
</body>
</html>"""


def style_var(accent):
    return f'<style>:root {{ --accent-course: {accent}; }}</style>'


def slugify_lesson(title, idx):
    # Simple, deterministic filenames
    return f"lesson-{idx:02d}.html"


def lesson_display_title(title):
    """Strip 'Lesson N:' prefix for h1 clarity, keeping the meat."""
    return title


def write_page(path: Path, html: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html + "\n")


def build_hub(data):
    """Root index.html — landing page listing all six thinkers."""
    title = "Six Thinkers — The Kiwi Dialectic"
    desc = "Six thinkers refitted for the algorithmic century — Gramsci, Kropotkin, Graeber, Freire, Deleuze, Bakunin. Free HTML courses from The Kiwi Dialectic. Train the mind. Arm the class."

    cards = []
    for slug in ORDER:
        t = THINKERS[slug]
        course = next((c for c in data['courses'] if c['slug'] == slug), None)
        lessons_n = len(course['lessons']) if course else 0
        status = course.get('status', 'Upcoming') if course else 'Upcoming'
        cards.append(f"""      <a class="card" href="{slug}/index.html" style="--accent-course: {t['accent']};">
        <div class="no">{escape(t['eyebrow'])} · {escape(status)}</div>
        <h3>{escape(t['display'])}</h3>
        <p style="color:var(--fg);opacity:.85;font-family:'Bebas Neue',sans-serif;letter-spacing:.06em;font-size:15px;margin-bottom:14px">{escape(t['subtitle'])}</p>
        <p>{escape(t['kaupapa'])}</p>
        <span class="card-link">{lessons_n} {'lessons' if lessons_n != 1 else 'lesson'} →</span>
      </a>""")

    # ---- Audio episodes section ------------------------------------------
    episode_cards = []
    if EPISODES_PATH.exists():
        eps = json.loads(EPISODES_PATH.read_text()).get('episodes', [])
        for ep in eps:
            cast_line = ' · '.join(escape(c) for c in ep.get('cast', []))
            episode_cards.append(f"""    <article style="background:rgba(245,236,216,.04);border:1px solid rgba(255,255,255,.08);padding:18px 20px;margin-bottom:16px;border-radius:2px">
      <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:6px">
        <span style="color:var(--muted);font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.1em">EP {escape(ep.get('number',''))}</span>
        <span style="color:var(--muted);font-size:13px">{cast_line}</span>
        <span style="color:var(--muted);font-size:13px;margin-left:auto">{escape(ep.get('runtime',''))}</span>
      </div>
      <h3 style="font-family:'Bebas Neue',sans-serif;letter-spacing:.02em;font-size:22px;line-height:1.15;margin:0 0 4px">{escape(ep.get('title',''))}</h3>
      <p style="opacity:.75;margin:0 0 12px;font-size:15px">{escape(ep.get('subtitle',''))}</p>
      <img src="{escape(ep.get('waveform_url',''))}" alt="Waveform" loading="lazy" style="width:100%;display:block;background:#f5ecd8;border:1px solid rgba(255,255,255,.08);margin-bottom:8px">
      <audio controls preload="none" style="width:100%">
        <source src="{escape(ep.get('mp3_url',''))}" type="audio/mpeg">
        Your browser cannot play this audio. <a href="{escape(ep.get('mp3_url',''))}">Download the mp3</a>.
      </audio>
    </article>""")
    episodes_html = '\n'.join(episode_cards) if episode_cards else '<p style="opacity:.6"><em>No episodes yet.</em></p>'

    html = HEAD.format(
        title=title,
        desc=desc,
        root='',
        style_var='<style>:root { --accent-course: #d7261e; }</style>',
    )
    html += nav(root='', active='home')
    html += f"""
<section class="hero">
  <div class="shell">
    <p class="eyebrow">AI Warrior · The Thinkers Series</p>
    <h1>Six Thinkers.<br>One Working-Class<br>Toolkit.</h1>
    <p class="kaupapa">Gramsci, Kropotkin, Graeber, Freire, Deleuze, Bakunin — six thinkers refitted for the algorithmic century. Every course free to read here. Every course free to remix under CC BY-SA 4.0. If it helps you, throw a koha in the tin so it stays free for the next reader.</p>
    <div style="margin-top:32px">
      <a class="btn kofi" href="{KOFI_URL}" target="_blank" rel="noopener">☕ Koha via Ko-fi</a>
      <a class="btn substack" href="{SUBSTACK_HOME}" target="_blank" rel="noopener" style="margin-left:10px">Subscribe on Substack →</a>
    </div>
  </div>
</section>

<section class="shell" aria-label="Six Thinkers: Dialogues promo">
  <div style="max-width:960px;margin:48px auto 8px;padding:0 20px">
    <p class="eyebrow" style="margin-bottom:8px">Round One · Dialogues</p>
    <h2 style="font-family:'Bebas Neue',sans-serif;letter-spacing:.02em;font-size:34px;line-height:1.05;margin:0 0 12px">Six voices. One writing room.</h2>
    <p style="opacity:.85;margin:0 0 20px;max-width:640px">A pencil-sketch round-table where Gramsci opens, Kropotkin answers, Bakunin roars, Freire steadies, Deleuze cuts across, and Graeber lands the last word.</p>
    <video controls playsinline preload="metadata" poster="assets/portraits/gramsci.png"
           style="width:100%;max-width:960px;display:block;background:#1c1816;border:1px solid rgba(255,255,255,.08)">
      <source src="assets/video/six-thinkers-promo-16x9.mp4" type="video/mp4">
      Your browser can’t play the promo video. <a href="assets/video/six-thinkers-promo-16x9.mp4">Download the mp4</a>.
    </video>
    <p style="opacity:.65;font-size:14px;margin:10px 0 0">
      Also available:
      <a href="assets/video/six-thinkers-promo-9x16.mp4">9:16 (vertical)</a> ·
      <a href="assets/video/six-thinkers-promo-1x1.mp4">1:1 (square)</a> ·
      Source: <a href="https://github.com/robertmccallnz/kd-dialogues" target="_blank" rel="noopener">kd-dialogues</a>
    </p>
  </div>
</section>

<section class="shell" aria-label="kd-dialogues audio episodes">
  <div style="max-width:960px;margin:48px auto 8px;padding:0 20px">
    <p class="eyebrow" style="margin-bottom:8px">Round Two · Audio Episodes</p>
    <h2 style="font-family:'Bebas Neue',sans-serif;letter-spacing:.02em;font-size:34px;line-height:1.05;margin:0 0 12px">Long-form audio dialogues.</h2>
    <p style="opacity:.85;margin:0 0 24px;max-width:640px">The same thinkers, at length — plus contemporary voices they'd argue with. Two-to-six voices per episode. No music. No ads. Just the argument. Full catalogue and transcripts live at <a href="https://robertmccallnz.github.io/kd-dialogues/" style="color:var(--kōura);text-decoration:underline">kd-dialogues</a>.</p>
{episodes_html}
    <p style="opacity:.65;font-size:14px;margin:20px 0 0">
      Full catalogue, transcripts and sources: <a href="https://robertmccallnz.github.io/kd-dialogues/" target="_blank" rel="noopener" style="color:var(--kōura)">robertmccallnz.github.io/kd-dialogues</a> · Repo: <a href="https://github.com/robertmccallnz/kd-dialogues" target="_blank" rel="noopener">kd-dialogues</a>
    </p>
  </div>
</section>

<section class="shell">
  <div class="grid">
{chr(10).join(cards)}
  </div>
</section>
"""
    html += footer()
    write_page(ROOT / "index.html", html)
    print("  ✓ index.html")


def build_course_index(slug, course):
    t = THINKERS[slug]
    title = f"{t['display']} — Six Thinkers"
    desc = course.get('description', t['kaupapa'])

    rows = []
    for i, lesson in enumerate(course['lessons'], start=1):
        fname = slugify_lesson(lesson['title'], i)
        rows.append(f"""    <div class="lesson-row">
      <div class="n">{i:02d}</div>
      <div>
        <h3>{escape(lesson['title'])}</h3>
        <p>{escape(lesson.get('teaser', ''))}</p>
      </div>
      <a class="read" href="{fname}">Read →</a>
    </div>""")

    html = HEAD.format(title=title, desc=escape(desc), root='../', style_var=style_var(t['accent']))
    html += nav(root='../', active=t['display'].lower().split()[0])
    html += f"""
<section class="hero">
  <div class="shell">
    <p class="eyebrow">{escape(t['eyebrow'])} · {escape(course.get('status', 'Live'))}</p>
    <h1>{escape(t['display'])}<br><span style="color:var(--muted);font-size:.5em;letter-spacing:.06em">{escape(t['subtitle'])}</span></h1>
    <p class="kaupapa">{escape(desc)}</p>
    <div style="margin-top:32px">
      <a class="btn kofi" href="{KOFI_URL}" target="_blank" rel="noopener">☕ Koha via Ko-fi</a>
      <a class="btn substack" href="{escape(SUBSTACK_HOME)}" target="_blank" rel="noopener" style="margin-left:10px">Subscribe on Substack →</a>
    </div>
  </div>
</section>

<section class="lessons">
  <div class="shell">
{chr(10).join(rows)}
  </div>
</section>
"""
    html += footer()
    write_page(ROOT / slug / "index.html", html)
    print(f"  ✓ {slug}/index.html")


def build_lesson(slug, course, idx, lesson):
    t = THINKERS[slug]
    fname = slugify_lesson(lesson['title'], idx)
    title = f"{lesson['title']} — {t['display']}"
    desc = lesson.get('teaser', '')
    substack = lesson.get('substack_link') or lesson.get('link') or SUBSTACK_HOME

    # If a bodies/<slug>-lesson-NN.html file exists, inline it as the lesson body.
    body_file = ROOT / "bodies" / f"{slug}-lesson-{idx:02d}.html"
    if body_file.exists():
        body_content = body_file.read_text().strip()
        body_block = f'<div class="body">{body_content}</div>'
    else:
        body_block = """    <div class="placeholder">
      <strong>Full lesson body coming shortly.</strong><br>
      This lesson is currently published in full on Substack. Click <em>Read on Substack</em> below for the complete text.
      Once the HTML version lands here, the Substack link will remain as the discussion / comment thread.
    </div>"""

    lessons = course['lessons']
    prev_html = '<span class="placeholder">·</span>'
    next_html = '<span class="placeholder">·</span>'
    if idx > 1:
        prev_html = f'<a href="{slugify_lesson(lessons[idx-2]["title"], idx-1)}">← Previous</a>'
    if idx < len(lessons):
        next_html = f'<a href="{slugify_lesson(lessons[idx]["title"], idx+1)}">Next →</a>'

    html = HEAD.format(title=title, desc=escape(desc), root='../', style_var=style_var(t['accent']))
    html += nav(root='../', active=t['display'].lower().split()[0])
    html += f"""
<div class="shell">
  <article class="lesson">
    <div class="crumbs">
      <a href="../index.html">Six Thinkers</a> · <a href="index.html">{escape(t['display'])}</a> · Lesson {idx:02d}
    </div>
    <h1>{escape(lesson['title'])}</h1>
    <p class="teaser">{escape(lesson.get('teaser', ''))}</p>

{body_block}

{ctas_block(substack)}

    <div class="pager">
      {prev_html}
      {next_html}
    </div>
  </article>
</div>
"""
    html += footer()
    write_page(ROOT / slug / fname, html)


def main():
    data = json.loads(COURSES_PATH.read_text())
    # Filter to only our six thinkers
    data['courses'] = [c for c in data['courses'] if c['slug'] in THINKERS]

    # Write CSS
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "style.css").write_text(CSS + "\n")
    print("  ✓ assets/style.css")

    # Build hub
    build_hub(data)

    # Build each course
    for course in data['courses']:
        slug = course['slug']
        build_course_index(slug, course)
        for i, lesson in enumerate(course['lessons'], start=1):
            build_lesson(slug, course, i, lesson)
        print(f"  ✓ {slug}: {len(course['lessons'])} lesson pages")

    # Marker for GH Pages
    (ROOT / ".nojekyll").write_text("")
    print("\nDone.")


if __name__ == "__main__":
    main()
