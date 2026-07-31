#!/usr/bin/env python3
"""Generate themed SVG project cards for the GitHub profile README.
Palette matches the profile banner: indigo #4F46E5 -> violet #A78BFA -> magenta #EC4899.

To add a project: append a dict to CARDS, add its slug to a ROWS pair, run this
script, and commit the new SVG in assets/. Use **double asterisks** to bold text.
"""
import html, os

W, PAD = 420, 24
INNER = W - 2 * PAD
CW11, CW10 = 6.6, 6.0          # approx mono char widths at 11px / 10px
LH = 17                         # bullet line height
MAX_CHARS = int((INNER - 16) / CW11)  # wrap budget for bullet text (indented)

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

CARDS = [
    dict(slug="relay", emoji="⚡", name="Relay", date="Jul 2026",
         tagline="LLM Cost Gateway",
         chips=["Python", "FastAPI", "Redis Stack", "PostgreSQL", "Prometheus", "Grafana", "Docker"],
         bullets=[
             "OpenAI-compatible gateway with local-embedding semantic caching (**95% hit rate**, 2.5% false hits) and complexity-based routing — **91%** less simulated API spend over 67k requests.",
             "Lua token buckets, per-team budgets & circuit-breaker failover held **zero dropped requests** through outage drills at **3.6 ms** p50 overhead.",
         ], footer="live demo + repo →"),
    dict(slug="argus", emoji="🔭", name="Argus", date="May 2026",
         tagline="LLM Evaluation Platform",
         chips=["Python", "FastAPI", "PostgreSQL", "Streamlit", "GitHub Actions", "HDBSCAN"],
         bullets=[
             "End-to-end tracing for multi-step LLM chains; auto-mines prod traces into eval sets via HDBSCAN + LLM labeling — **143 cases at 92% precision**.",
             "80-case adversarial benchmark, six-flag safety judge & paired McNemar CI gate flagged **every injected regression** pre-merge; root-cause analyzer at **81%** accuracy.",
         ], footer="live demo + repo →"),
    dict(slug="cue", emoji="🧠", name="Cue", date="Feb 2026",
         tagline="AI Workspace Agent",
         chips=["Gemini", "React", "MongoDB Atlas", "MCP"],
         bullets=[
             "Chrome extension pairing Gemini with MongoDB Atlas to forecast a user's **next five tasks** from browsing history, surfaced in a real-time React dashboard.",
             "MCP orchestration across **9+ Google Workspace tools**, plus a multimodal scribe producing meeting summaries and highlight reels.",
         ], footer="view repo →"),
    dict(slug="divdash", emoji="📊", name="DIVDASH", date="Oct 2023",
         tagline="Diversity & Inclusion Analytics",
         chips=["React", "Node.js", "Firebase", "TensorFlow", "AWS Bedrock"],
         bullets=[
             "D&I metrics dashboard with Bedrock-powered generative insights and NLP summaries.",
             "Real-time, multilingual visualizations — decision-making **30% faster**.",
         ], footer="view repo →"),
    dict(slug="disha", emoji="🎓", name="DISHA", date="Aug 2024",
         tagline="Student-Mentor Platform",
         chips=["Dart", "Flutter", "AWS SageMaker"],
         bullets=[
             "Connected **2,000+ students** with **500+ verified professionals** via ML matching on SageMaker.",
             "**5,000+ questions** answered with multimedia responses from experts across domains.",
         ], footer="view repo →"),
    dict(slug="aid", emoji="🤟", name="AID", date="Jan 2023",
         tagline="Assistive Interface for the Deaf",
         chips=["Flutter", "TensorFlow", "Firebase", "Blender"],
         bullets=[
             "Speech-to-sign model at **92% accuracy** — voice becomes real-time animated hand gestures via Blender.",
             "Built to assist the hearing-impaired in public settings.",
         ], footer="🔒 private repo"),
]

# Cards sharing a row get a matched height.
ROWS = [("relay", "argus"), ("cue", "divdash"), ("disha", "aid")]


def esc(s):
    return html.escape(s, quote=True)


def parse_bold(text):
    """Split '**bold** normal' into [(segment, is_bold), ...]."""
    runs, bold = [], False
    for part in text.split("**"):
        if part:
            runs.append((part, bold))
        bold = not bold
    return runs


def wrap_runs(runs, max_chars):
    """Word-wrap styled runs; returns list of lines, each a list of (text, bold)."""
    words = []
    for text, bold in runs:
        for w in text.split(" "):
            if w:
                words.append((w, bold))
    lines, cur, cur_len = [], [], 0
    for w, bold in words:
        add = len(w) + (1 if cur else 0)
        if cur and cur_len + add > max_chars:
            lines.append(cur)
            cur, cur_len = [(w, bold)], len(w)
        else:
            cur.append((w, bold))
            cur_len += add
    if cur:
        lines.append(cur)
    merged_lines = []
    for line in lines:
        merged = []
        for w, bold in line:
            if merged and merged[-1][1] == bold:
                merged[-1] = (merged[-1][0] + " " + w, bold)
            else:
                merged.append((w, bold))
        merged_lines.append(merged)
    return merged_lines


def layout_chips(chips):
    """Return rows of (label, x, w) plus total height used."""
    rows, cur, x = [], [], PAD
    for label in chips:
        w = round(len(label) * CW10) + 18
        if cur and x + w > W - PAD:
            rows.append(cur)
            cur, x = [], PAD
        cur.append((label, x, w))
        x += w + 8
    if cur:
        rows.append(cur)
    return rows, len(rows) * 22 + (len(rows) - 1) * 8


def measure(card):
    _, chip_h = layout_chips(card["chips"])
    n_lines = sum(len(wrap_runs(parse_bold(b), MAX_CHARS)) for b in card["bullets"])
    gaps = (len(card["bullets"]) - 1) * 7
    # title(58) + tagline(24) + chips + gap(24) + bullets + bottom pad(20)
    return 58 + 24 + chip_h + 24 + n_lines * LH + gaps + 20


def _spaced(line):
    """Re-insert single spaces between merged runs of a line."""
    return [(t if i == 0 else " " + t, b) for i, (t, b) in enumerate(line)]


def build(card, H):
    s = []
    s.append(
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{esc(card["name"])} — {esc(card["tagline"])}">'
    )
    s.append(f"""<defs>
  <linearGradient id="border" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#4F46E5"/><stop offset="0.5" stop-color="#A78BFA"/><stop offset="1" stop-color="#EC4899"/>
  </linearGradient>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#171C28"/><stop offset="1" stop-color="#0F131B"/>
  </linearGradient>
  <linearGradient id="bar" x1="0" y1="0" x2="44" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#A78BFA"/><stop offset="1" stop-color="#EC4899"/>
  </linearGradient>
  <radialGradient id="glowV" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
    gradientTransform="translate({W - 40} 20) rotate(115) scale(190)">
    <stop offset="0" stop-color="#8B5CF6" stop-opacity="0.22"/><stop offset="1" stop-color="#8B5CF6" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glowM" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
    gradientTransform="translate(30 {H - 15}) rotate(-65) scale(170)">
    <stop offset="0" stop-color="#EC4899" stop-opacity="0.14"/><stop offset="1" stop-color="#EC4899" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="clip"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="15"/></clipPath>
</defs>""")
    s.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="15" fill="url(#bg)"/>')
    s.append(f'<g clip-path="url(#clip)">'
             f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" fill="url(#glowV)"/>'
             f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" fill="url(#glowM)"/></g>')
    s.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="15" '
             f'stroke="url(#border)" stroke-opacity="0.85" stroke-width="1.6"/>')

    # title + date + pulsing dot
    s.append(f'<text x="{PAD}" y="46" font-family="{SANS}" font-size="20" '
             f'font-weight="700" fill="#F0F6FC">{esc(card["emoji"] + "  " + card["name"])}</text>')
    date_w = len(card["date"]) * 6.3
    dot_x = W - PAD - date_w - 12
    s.append(f'<circle cx="{dot_x:.0f}" cy="40" r="3" fill="#A78BFA">'
             f'<animate attributeName="opacity" values="1;0.25;1" dur="2.6s" repeatCount="indefinite"/></circle>')
    s.append(f'<text x="{W - PAD}" y="44" text-anchor="end" font-family="{MONO}" '
             f'font-size="10.5" fill="#7D8590">{esc(card["date"])}</text>')
    s.append(f'<rect x="{PAD}" y="56" width="44" height="3" rx="1.5" fill="url(#bar)"/>')

    # tagline
    s.append(f'<text x="{PAD}" y="82" font-family="{MONO}" font-size="11" '
             f'fill="#9BA6B5">{esc(card["tagline"])}</text>')

    # chips
    chip_rows, chip_h = layout_chips(card["chips"])
    y = 96
    for row in chip_rows:
        for label, x, w in row:
            s.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="6" '
                     f'fill="#A78BFA" fill-opacity="0.10" stroke="#A78BFA" stroke-opacity="0.28"/>')
            s.append(f'<text x="{x + w / 2:.0f}" y="{y + 15}" text-anchor="middle" '
                     f'font-family="{MONO}" font-size="10" fill="#C9B8FF">{esc(label)}</text>')
        y += 30
    y = 96 + chip_h + 24

    # bullets
    for bullet in card["bullets"]:
        lines = wrap_runs(parse_bold(bullet), MAX_CHARS)
        first = True
        for line in lines:
            if first:
                s.append(f'<circle cx="{PAD + 4}" cy="{y - 4}" r="2.5" fill="#EC4899"/>')
                first = False
            tspans = "".join(
                f'<tspan fill="#E6EDF3" font-weight="700">{esc(t)}</tspan>' if b else esc(t)
                for t, b in _spaced(line)
            )
            s.append(f'<text x="{PAD + 16}" y="{y}" font-family="{MONO}" '
                     f'font-size="11" fill="#A9B4C0">{tspans}</text>')
            y += LH
        y += 7

    s.append("</svg>")
    return "\n".join(s)


# Button strips that sit flush under each card. Because GitHub renders README
# SVGs as non-interactive <img>, each clickable region must be its own file.
# HALF = two buttons under one card (24% width each); FULL = one button (48%).
HALF, FULL = 211, 420
BTN_H = 42

BUTTONS = [
    # (filename, width, label, accent, pad_left, pad_right)
    ("btn-relay-demo",   HALF, "◆  Live Demo  ↗", "demo", 4, 4),
    ("btn-relay-repo",   HALF, "◆  Source  →",    "repo", 4, 4),
    ("btn-argus-demo",   HALF, "◆  Live Demo  ↗", "demo", 4, 4),
    ("btn-argus-repo",   HALF, "◆  Source  →",    "repo", 4, 4),
    ("btn-cue-repo",     FULL, "◆  View Source on GitHub  →",     "repo", 4, 4),
    ("btn-divdash-repo", FULL, "◆  View Source on GitHub  →",     "repo", 4, 4),
    ("btn-disha-repo",   FULL, "◆  View Source on GitHub  →",     "repo", 4, 4),
    ("btn-aid-private",  FULL, "🔒  Private repository",          "muted", 4, 4),
]

ACCENTS = {
    "demo":  dict(stroke="#EC4899", text="#FBCFE8", fill="#EC4899", fill_op="0.12", stroke_op="0.55"),
    "repo":  dict(stroke="#A78BFA", text="#C9B8FF", fill="#A78BFA", fill_op="0.10", stroke_op="0.45"),
    "muted": dict(stroke="#6E7681", text="#8B949E", fill="#6E7681", fill_op="0.07", stroke_op="0.35"),
}


def build_button(width, label, accent, pl, pr):
    a = ACCENTS[accent]
    x = pl
    w = width - pl - pr
    cx = x + w / 2
    return (
        f'<svg width="{width}" height="{BTN_H}" viewBox="0 0 {width} {BTN_H}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}">'
        f'<rect x="{x}" y="4" width="{w}" height="{BTN_H - 10}" rx="9" '
        f'fill="{a["fill"]}" fill-opacity="{a["fill_op"]}" '
        f'stroke="{a["stroke"]}" stroke-opacity="{a["stroke_op"]}" stroke-width="1.4"/>'
        f'<text x="{cx:.1f}" y="{BTN_H / 2 + 4:.0f}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="12" font-weight="600" fill="{a["text"]}">{esc(label)}</text>'
        f'</svg>'
    )


def main():
    os.makedirs("assets", exist_ok=True)
    by_slug = {c["slug"]: c for c in CARDS}
    for row in ROWS:
        H = max(measure(by_slug[s]) for s in row)
        print(f"row {row}: height {H}px")
        for slug in row:
            svg = build(by_slug[slug], H)
            path = f"assets/card-{slug}.svg"
            with open(path, "w") as f:
                f.write(svg)
            print(f"  wrote {path} ({len(svg)} bytes)")

    for name, width, label, accent, pl, pr in BUTTONS:
        svg = build_button(width, label, accent, pl, pr)
        path = f"assets/{name}.svg"
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path} ({width}px)")


if __name__ == "__main__":
    main()
