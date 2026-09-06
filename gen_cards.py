#!/usr/bin/env python3
"""Generate the themed SVG asset set for the GitHub profile README.

Palette and type mirror the portfolio at nishcodes.com:
  bg #09090b, mint #00ffc8, violet #7850ff, cyan #00d4ff, wide-tracked mono
  microlabels, heavy sans display, and `// nn` section eyebrows.

Everything in assets/ is generated. Edit a content dict below and re-run
`python gen_cards.py`; use **double asterisks** to accent a metric.
"""
import html, os

# ------------------------------------------------------------------ tokens
BG_TOP, BG_BOT = "#0c0c12", "#09090b"
MINT, VIOLET, CYAN = "#00ffc8", "#7850ff", "#00d4ff"
MINT_TXT, VIOLET_TXT = "#7dffb2", "#c7a7ff"
WHITE, DIM, MUTED = "#ffffff", "#a3a3b2", "#6c6c7d"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"


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


def tokenize(runs):
    """Split styled runs into whitespace-delimited tokens.

    A token keeps its own fragments, so '(**95% hit rate**,' stays one word
    instead of gaining spaces around the bold segment.
    """
    tokens, cur = [], []
    for text, bold in runs:
        parts = text.split(" ")
        for i, part in enumerate(parts):
            if i > 0:
                if cur:
                    tokens.append(cur)
                cur = []
            if part:
                cur.append((part, bold))
    if cur:
        tokens.append(cur)
    return tokens


def wrap_runs(runs, max_chars):
    """Word-wrap styled runs; returns lines, each a list of tokens."""
    lines, cur, cur_len = [], [], 0
    for tok in tokenize(runs):
        tl = sum(len(t) for t, _ in tok)
        add = tl + (1 if cur else 0)
        if cur and cur_len + add > max_chars:
            lines.append(cur)
            cur, cur_len = [tok], tl
        else:
            cur.append(tok)
            cur_len += add
    if cur:
        lines.append(cur)
    return lines


def spaced(line):
    """Flatten a line to (text, bold) fragments, re-inserting word spaces."""
    frags = []
    for i, tok in enumerate(line):
        for j, (t, b) in enumerate(tok):
            piece = (" " + t) if (i > 0 and j == 0) else t
            if frags and frags[-1][1] == b:
                frags[-1] = (frags[-1][0] + piece, b)
            else:
                frags.append((piece, b))
    return frags


def plain(runs):
    return "".join(t for t, _ in runs)


# ------------------------------------------------------------------ chrome
def panel_defs(uid, w, h, r):
    """Shared background: grid, corner glows, gradient edge, rounded clip."""
    return f"""<defs>
  <linearGradient id="{uid}bg" x1="0" y1="0" x2="0" y2="{h}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOT}"/>
  </linearGradient>
  <linearGradient id="{uid}edge" x1="0" y1="0" x2="{w}" y2="{h}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{MINT}" stop-opacity="0.55"/>
    <stop offset="0.5" stop-color="{VIOLET}" stop-opacity="0.40"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity="0.30"/>
  </linearGradient>
  <linearGradient id="{uid}bar" x1="0" y1="0" x2="46" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{MINT}"/><stop offset="1" stop-color="{VIOLET}"/>
  </linearGradient>
  <pattern id="{uid}grid" width="22" height="22" patternUnits="userSpaceOnUse">
    <path d="M22 0H0V22" fill="none" stroke="{MINT}" stroke-opacity="0.045" stroke-width="1"/>
  </pattern>
  <radialGradient id="{uid}gm" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
    gradientTransform="translate({w - 30} 10) rotate(122) scale({int(h * 0.95)} 220)">
    <stop offset="0" stop-color="{MINT}" stop-opacity="0.16"/>
    <stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="{uid}gv" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
    gradientTransform="translate(20 {h - 10}) rotate(-62) scale({int(h * 0.9)} 240)">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.20"/>
    <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="{uid}clip"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}"/></clipPath>
</defs>"""


def brackets(w, h, inset=13, arm=17, op="0.5"):
    """HUD corner brackets, drawn inside the rounded border."""
    a, i = arm, inset
    x2, y2 = w - i, h - i
    d = [
        f"M{i},{i + a} L{i},{i} L{i + a},{i}",
        f"M{x2 - a},{i} L{x2},{i} L{x2},{i + a}",
        f"M{i},{y2 - a} L{i},{y2} L{i + a},{y2}",
        f"M{x2 - a},{y2} L{x2},{y2} L{x2},{y2 - a}",
    ]
    return "".join(
        f'<path d="{p}" fill="none" stroke="{MINT}" stroke-opacity="{op}" '
        f'stroke-width="1.5" stroke-linecap="square"/>' for p in d
    )


def panel_body(uid, w, h, r):
    return (
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="url(#{uid}bg)"/>'
        f'<g clip-path="url(#{uid}clip)">'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="url(#{uid}grid)"/>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="url(#{uid}gm)"/>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="url(#{uid}gv)"/>'
        f'</g>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="none" '
        f'stroke="#ffffff" stroke-opacity="0.09" stroke-width="1"/>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="none" '
        f'stroke="url(#{uid}edge)" stroke-width="1.4"/>'
        + brackets(w, h)
    )


def pulse_dot(cx, cy, color=MINT, r=3.2):
    return (
        f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r + 3.5}" fill="{color}" fill-opacity="0.14">'
        f'<animate attributeName="r" values="{r};{r + 5};{r}" dur="2.8s" repeatCount="indefinite"/>'
        f'<animate attributeName="fill-opacity" values="0.22;0;0.22" dur="2.8s" repeatCount="indefinite"/>'
        f'</circle>'
        f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" fill="{color}">'
        f'<animate attributeName="opacity" values="1;0.35;1" dur="2.8s" repeatCount="indefinite"/>'
        f'</circle>'
    )


# ------------------------------------------------------------------- cards
W, PAD = 420, 24
INNER = W - 2 * PAD
CW11, CW10 = 6.6, 6.0          # approx mono char widths at 11px / 10px
LH = 17                         # bullet line height
MAX_CHARS = int((INNER - 16) / CW11)

Y_ID, Y_NAME, Y_BAR, Y_TAG, Y_CHIPS = 30, 62, 72, 96, 110

CARDS = [
    dict(slug="relay", emoji="⚡", name="Relay", date="Jul 2026",
         tagline="LLM Cost Gateway",
         chips=["Python", "FastAPI", "Redis Stack", "PostgreSQL", "Prometheus", "Grafana", "Docker"],
         bullets=[
             "OpenAI-compatible gateway with local-embedding semantic caching (**95% hit rate**, 2.5% false hits) and complexity-based routing — **91%** less simulated API spend over 67k requests.",
             "Lua token buckets, per-team budgets & circuit-breaker failover held **zero dropped requests** through outage drills at **3.6 ms** p50 overhead.",
         ], footer="live demo + repo →"),
    dict(slug="argus", emoji="\U0001f52d", name="Argus", date="May 2026",
         tagline="LLM Evaluation Platform",
         chips=["Python", "FastAPI", "PostgreSQL", "Streamlit", "GitHub Actions", "HDBSCAN"],
         bullets=[
             "End-to-end tracing for multi-step LLM chains; auto-mines prod traces into eval sets via HDBSCAN + LLM labeling — **143 cases at 92% precision**.",
             "80-case adversarial benchmark, six-flag safety judge & paired McNemar CI gate flagged **every injected regression** pre-merge; root-cause analyzer at **81%** accuracy.",
         ], footer="live demo + repo →"),
    dict(slug="cue", emoji="\U0001f9e0", name="Cue", date="Feb 2026",
         tagline="AI Workspace Agent",
         chips=["Gemini", "React", "MongoDB Atlas", "MCP"],
         bullets=[
             "Chrome extension pairing Gemini with MongoDB Atlas to forecast a user's **next five tasks** from browsing history, surfaced in a real-time React dashboard.",
             "MCP orchestration across **9+ Google Workspace tools**, plus a multimodal scribe producing meeting summaries and highlight reels.",
         ], footer="view repo →"),
    dict(slug="divdash", emoji="\U0001f4ca", name="DIVDASH", date="Oct 2023",
         tagline="Diversity & Inclusion Analytics",
         chips=["React", "Node.js", "Firebase", "TensorFlow", "AWS Bedrock"],
         bullets=[
             "D&I metrics dashboard with Bedrock-powered generative insights and NLP summaries.",
             "Real-time, multilingual visualizations — decision-making **30% faster**.",
         ], footer="view repo →"),
    dict(slug="disha", emoji="\U0001f393", name="DISHA", date="Aug 2024",
         tagline="Student-Mentor Platform",
         chips=["Dart", "Flutter", "AWS SageMaker"],
         bullets=[
             "Connected **2,000+ students** with **500+ verified professionals** via ML matching on SageMaker.",
             "**5,000+ questions** answered with multimedia responses from experts across domains.",
         ], footer="view repo →"),
    dict(slug="aid", emoji="\U0001f91f", name="AID", date="Jan 2023",
         tagline="Assistive Interface for the Deaf",
         chips=["Flutter", "TensorFlow", "Firebase", "Blender"],
         bullets=[
             "Speech-to-sign model at **92% accuracy** — voice becomes real-time animated hand gestures via Blender.",
             "Built to assist the hearing-impaired in public settings.",
         ], footer="\U0001f512 private repo"),
]

# Cards sharing a row get a matched height.
ROWS = [("relay", "argus"), ("cue", "divdash"), ("disha", "aid")]


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
    gaps = (len(card["bullets"]) - 1) * 8
    first = Y_CHIPS + chip_h + 28
    return first + (n_lines - 1) * LH + gaps + 20


def build_card(card, H, index):
    uid = f"c{index}"
    label = f'{card["name"]} — {card["tagline"]}. ' + " ".join(
        plain(parse_bold(b)) for b in card["bullets"]
    )
    s = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}">',
        panel_defs(uid, W, H, 15),
        panel_body(uid, W, H, 15),
    ]

    # HUD id + live date stamp
    s.append(f'<text x="{PAD}" y="{Y_ID}" font-family="{MONO}" font-size="9.5" '
             f'letter-spacing="2.4" fill="{MINT}" fill-opacity="0.75">'
             f'PRJ_{index:02d}</text>')
    date_w = len(card["date"]) * 6.3
    s.append(pulse_dot(W - PAD - date_w - 13, Y_ID - 4))
    s.append(f'<text x="{W - PAD}" y="{Y_ID}" text-anchor="end" font-family="{MONO}" '
             f'font-size="10" letter-spacing="0.6" fill="{MUTED}">{esc(card["date"])}</text>')

    # name + accent bar + tagline
    s.append(f'<text x="{PAD}" y="{Y_NAME}" font-family="{SANS}" font-size="21" '
             f'font-weight="700" letter-spacing="-0.4" fill="{WHITE}">'
             f'{esc(card["emoji"] + "  " + card["name"])}</text>')
    s.append(f'<rect x="{PAD}" y="{Y_BAR}" width="46" height="3" rx="1.5" fill="url(#{uid}bar)"/>')
    s.append(f'<text x="{PAD}" y="{Y_TAG}" font-family="{MONO}" font-size="10.5" '
             f'letter-spacing="1.6" fill="{DIM}">{esc(card["tagline"].upper())}</text>')

    # chips: first one mint (primary stack), rest violet
    chip_rows, chip_h = layout_chips(card["chips"])
    y, n = Y_CHIPS, 0
    for row in chip_rows:
        for lab, x, w in row:
            acc, txt = (MINT, MINT_TXT) if n == 0 else (VIOLET, VIOLET_TXT)
            s.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="6" '
                     f'fill="{acc}" fill-opacity="0.09" stroke="{acc}" stroke-opacity="0.30"/>')
            s.append(f'<text x="{x + w / 2:.0f}" y="{y + 15}" text-anchor="middle" '
                     f'font-family="{MONO}" font-size="10" fill="{txt}">{esc(lab)}</text>')
            n += 1
        y += 30

    # bullets, metrics called out in mint
    y = Y_CHIPS + chip_h + 28
    for bullet in card["bullets"]:
        for i, line in enumerate(wrap_runs(parse_bold(bullet), MAX_CHARS)):
            if i == 0:
                cx, cy = PAD + 4, y - 4
                s.append(f'<path d="M{cx},{cy - 3.4} L{cx + 3.4},{cy} L{cx},{cy + 3.4} '
                         f'L{cx - 3.4},{cy} Z" fill="{MINT}"/>')
            tspans = "".join(
                f'<tspan fill="{MINT}" font-weight="700">{esc(t)}</tspan>' if b else esc(t)
                for t, b in spaced(line)
            )
            s.append(f'<text x="{PAD + 16}" y="{y}" font-family="{MONO}" '
                     f'font-size="11" fill="{DIM}">{tspans}</text>')
            y += LH
        y += 8

    s.append("</svg>")
    return "\n".join(s)


# -------------------------------------------------------------- experience
EW, EPAD, EGUT = 880, 26, 34
ELH, ECW = 18, 6.9
EMAX = int((EW - EPAD - EGUT - EPAD) / ECW)

EXPERIENCE = [
    dict(slug="orix", company="ORIX", role="Forward Deployed AI Engineer Intern",
         period="May 2026 — Present", live=True,
         body="Partnered with operations, lending, and portfolio teams to take AI products from "
              "requirements to delivery. Built an Azure document platform feeding an "
              "**85,000+ document** knowledge base, a grounded RAG agent, and Databricks Genie "
              "analytics that reduced query authoring from **10 min to under 20 sec**, while "
              "hardening refresh, indexing, access, and deployment workflows."),
    dict(slug="nomura-swe", company="Nomura", role="Software Engineer",
         period="Jul 2024 — Jul 2025", live=False,
         body="Owned an Angular to React migration of a 40+ page portal with **84% faster** loads "
              "for 200+ daily users. Built an auto-onboarding service cutting application setup "
              "from **3 weeks to 5 min**. Modeled 100+ applications as a Neo4j graph and reduced "
              "API latency by **20%**."),
    dict(slug="nomura-intern", company="Nomura", role="SDE Intern",
         period="Jan 2024 — Jun 2024", live=False,
         body="Implemented Pact Broker contract testing across services and increased coverage "
              "from **48% to 83%**. Rebuilt the portal with 20+ reusable components adopted by "
              "teams supporting 1,000+ users."),
    dict(slug="tcs", company="TCS", role="SDE Intern",
         period="May 2023 — Jul 2023", live=False,
         body="Built a medical imaging pipeline over MRI and CT volumes with **98.5% detection "
              "accuracy** on 2-3 mm lesions. Created a Blender nasal reconstruction across 22 "
              "regions for an AR/VR simulator that was **70% faster** than the synchronous build."),
]


def build_exp(job, index):
    uid = f"e{index}"
    lines = wrap_runs(parse_bold(job["body"]), EMAX)
    H = 96 + len(lines) * ELH + 16
    tx = EPAD + EGUT
    label = f'{job["company"]}, {job["role"]}, {job["period"]}. {plain(parse_bold(job["body"]))}'

    s = [
        f'<svg width="{EW}" height="{H}" viewBox="0 0 {EW} {H}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}">',
        panel_defs(uid, EW, H, 14),
        panel_body(uid, EW, H, 14),
    ]

    # timeline rail down the gutter, node level with the company name
    rail = EPAD + 8
    s.append(f'<line x1="{rail}" y1="26" x2="{rail}" y2="{H - 26}" stroke="{VIOLET}" '
             f'stroke-opacity="0.35" stroke-width="1.5" stroke-dasharray="2 5"/>')
    s.append(pulse_dot(rail, 46, MINT if job["live"] else VIOLET, 4))

    # company + role
    s.append(f'<text x="{tx}" y="{40}" font-family="{SANS}" font-size="20" font-weight="700" '
             f'letter-spacing="-0.3" fill="{WHITE}">{esc(job["company"])}</text>')
    s.append(f'<text x="{tx}" y="{62}" font-family="{MONO}" font-size="11.5" '
             f'letter-spacing="1.5" fill="{MINT}">{esc(job["role"].upper())}</text>')

    # period pill, right aligned; the live role carries a pulsing mint dot
    acc, txt = (MINT, MINT_TXT) if job["live"] else (VIOLET, VIOLET_TXT)
    lead = 26 if job["live"] else 13
    pw = round(len(job["period"]) * 6.2) + lead + 13
    px = EW - EPAD - pw
    s.append(f'<rect x="{px}" y="26" width="{pw}" height="24" rx="7" fill="{acc}" '
             f'fill-opacity="0.10" stroke="{acc}" stroke-opacity="0.34"/>')
    if job["live"]:
        s.append(pulse_dot(px + 14, 38, MINT, 3))
    s.append(f'<text x="{px + lead}" y="42" font-family="{MONO}" font-size="10.5" '
             f'letter-spacing="0.4" fill="{txt}">{esc(job["period"])}</text>')

    y = 96
    for line in lines:
        tspans = "".join(
            f'<tspan fill="{MINT}" font-weight="700">{esc(t)}</tspan>' if b else esc(t)
            for t, b in spaced(line)
        )
        s.append(f'<text x="{tx}" y="{y}" font-family="{MONO}" font-size="11.5" '
                 f'fill="{DIM}">{tspans}</text>')
        y += ELH

    s.append("</svg>")
    return "\n".join(s)


# ----------------------------------------------------------- section header
HDR_W, HDR_H = 880, 68

SECTIONS = [
    ("hdr-whoami", "whoami"),
    ("hdr-experience", "Where I've shipped"),
    ("hdr-stack", "Tools I reach for"),
    ("hdr-projects", "Things I've built"),
    ("hdr-snake", "A snake eating my contributions"),
]


def build_header(index, title):
    tw = 0.56 * 30 * len(title) + 22
    rule_x = min(tw, HDR_W - 120)
    return (
        f'<svg width="{HDR_W}" height="{HDR_H}" viewBox="0 0 {HDR_W} {HDR_H}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(title)}">'
        f'<defs><linearGradient id="hr" x1="{rule_x}" y1="0" x2="{HDR_W}" y2="0" '
        f'gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{MINT}" stop-opacity="0.55"/>'
        f'<stop offset="0.45" stop-color="{VIOLET}" stop-opacity="0.30"/>'
        f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient></defs>'
        f'<text x="2" y="20" font-family="{MONO}" font-size="11" letter-spacing="4.5" '
        f'fill="{MINT}">// {index:02d}</text>'
        f'<text x="0" y="54" font-family="{SANS}" font-size="30" font-weight="800" '
        f'letter-spacing="-0.6" fill="{WHITE}">{esc(title)}</text>'
        f'<line x1="{rule_x:.0f}" y1="45" x2="{HDR_W}" y2="45" stroke="url(#hr)" stroke-width="1.4"/>'
        f'</svg>'
    )


# ------------------------------------------------------------------ banner
BW, BH = 1200, 300
NAME_Y, NAME_SIZE = 196, 74


def _name_text(fill_first, fill_last, dx=0, dy=0, extra=""):
    return (
        f'<text x="{600 + dx}" y="{NAME_Y + dy}" text-anchor="middle" font-family="{SANS}" '
        f'font-size="{NAME_SIZE}" font-weight="800" letter-spacing="-1.5">'
        f'<tspan fill="{fill_first}">Nishant </tspan>'
        f'<tspan fill="{fill_last}">Chaudhary</tspan>{extra}</text>'
    )


def build_banner():
    burst = ('<animate attributeName="opacity" values="0;0;0.85;0;0.6;0" '
             'keyTimes="0;0.88;0.905;0.93;0.95;1" dur="4.5s" repeatCount="indefinite"/>')
    return f"""<svg width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Nishant Chaudhary - Discover, Build, Demo, Iterate, Ship">
<defs>
  <linearGradient id="bbg" x1="0" y1="0" x2="0" y2="{BH}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#0d0d14"/><stop offset="1" stop-color="{BG_BOT}"/>
  </linearGradient>
  <linearGradient id="bname" x1="570" y1="0" x2="940" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{MINT}"/><stop offset="1" stop-color="{VIOLET}"/>
  </linearGradient>
  <linearGradient id="brule" x1="0" y1="0" x2="{BW}" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{MINT}" stop-opacity="0"/>
    <stop offset="0.28" stop-color="{MINT}" stop-opacity="0.9"/>
    <stop offset="0.62" stop-color="{VIOLET}" stop-opacity="0.9"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="bgrid" width="44" height="44" patternUnits="userSpaceOnUse">
    <path d="M44 0H0V44" fill="none" stroke="{MINT}" stroke-opacity="0.10" stroke-width="1"/>
  </pattern>
  <radialGradient id="bfade" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#ffffff" stop-opacity="1"/>
    <stop offset="0.55" stop-color="#ffffff" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="bglowM" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
    gradientTransform="translate(210 40) rotate(58) scale(420 260)">
    <stop offset="0" stop-color="{MINT}" stop-opacity="0.15"/>
    <stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="bglowV" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
    gradientTransform="translate(1010 270) rotate(-118) scale(430 280)">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.22"/>
    <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <mask id="bmask"><rect width="{BW}" height="{BH}" fill="url(#bfade)"/></mask>
  <clipPath id="bandA"><rect x="0" y="142" width="{BW}" height="22"/></clipPath>
  <clipPath id="bandB"><rect x="0" y="168" width="{BW}" height="30"/></clipPath>
</defs>
<rect width="{BW}" height="{BH}" fill="url(#bbg)"/>
<g mask="url(#bmask)">
  <g><rect x="-44" y="-44" width="{BW + 88}" height="{BH + 88}" fill="url(#bgrid)"/>
    <animateTransform attributeName="transform" type="translate" from="0 0" to="44 44"
      dur="9s" repeatCount="indefinite"/></g>
</g>
<rect width="{BW}" height="{BH}" fill="url(#bglowM)"/>
<rect width="{BW}" height="{BH}" fill="url(#bglowV)"/>
{brackets(BW, BH, inset=22, arm=34, op="0.55")}
<text x="600" y="112" text-anchor="middle" font-family="{MONO}" font-size="13"
  letter-spacing="6" fill="{MINT}">&lt; HELLO WORLD /&gt;</text>
{_name_text(WHITE, "url(#bname)")}
<g clip-path="url(#bandA)">{_name_text(MINT, MINT, dx=-4, dy=-2, extra=burst)}</g>
<g clip-path="url(#bandB)">{_name_text(VIOLET, VIOLET, dx=5, dy=2, extra=burst)}</g>
<text x="600" y="244" text-anchor="middle" font-family="{MONO}" font-size="12.5"
  letter-spacing="5" fill="{DIM}">DISCOVER &#8226; BUILD &#8226; DEMO &#8226; ITERATE &#8226; SHIP</text>
<line x1="0" y1="{BH - 3}" x2="{BW}" y2="{BH - 3}" stroke="url(#brule)" stroke-width="3"/>
</svg>"""


def build_footer():
    return f"""<svg width="{BW}" height="140" viewBox="0 0 {BW} 140" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="">
<defs>
  <linearGradient id="fbg" x1="0" y1="0" x2="0" y2="140" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{BG_BOT}"/><stop offset="1" stop-color="#0d0d14"/>
  </linearGradient>
  <linearGradient id="frule" x1="0" y1="0" x2="{BW}" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="0.35" stop-color="{VIOLET}" stop-opacity="0.9"/>
    <stop offset="0.7" stop-color="{MINT}" stop-opacity="0.9"/>
    <stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="fgrid" width="44" height="44" patternUnits="userSpaceOnUse">
    <path d="M44 0H0V44" fill="none" stroke="{VIOLET}" stroke-opacity="0.10" stroke-width="1"/>
  </pattern>
  <radialGradient id="ffade" cx="0.5" cy="0" r="0.85">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.7"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </radialGradient>
  <mask id="fmask"><rect width="{BW}" height="140" fill="url(#ffade)"/></mask>
</defs>
<rect width="{BW}" height="140" fill="url(#fbg)"/>
<g mask="url(#fmask)"><rect width="{BW}" height="140" fill="url(#fgrid)"/></g>
<line x1="0" y1="2" x2="{BW}" y2="2" stroke="url(#frule)" stroke-width="3"/>
<text x="600" y="82" text-anchor="middle" font-family="{MONO}" font-size="11"
  letter-spacing="5.5" fill="{DIM}" fill-opacity="0.75">NISHCODES.COM</text>
</svg>"""


# ------------------------------------------------------- terminal + closing
def build_termbar(w=880, h=40, title="nishant@github: ~"):
    lights = "".join(
        f'<circle cx="{22 + i * 20}" cy="{h / 2:.0f}" r="5.5" fill="{c}"/>'
        for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])
    )
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(title)}">'
        f'<path d="M0,{h} L0,12 Q0,0 12,0 L{w - 12},0 Q{w},0 {w},12 L{w},{h} Z" fill="#111118"/>'
        f'<path d="M0,{h} L0,12 Q0,0 12,0 L{w - 12},0 Q{w},0 {w},12 L{w},{h}" fill="none" '
        f'stroke="#ffffff" stroke-opacity="0.10" stroke-width="1"/>'
        f'{lights}'
        f'<text x="{w / 2:.0f}" y="{h / 2 + 4:.0f}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="11" letter-spacing="1.2" fill="{MUTED}">{esc(title)}</text>'
        f'<text x="{w - 20}" y="{h / 2 + 4:.0f}" text-anchor="end" font-family="{MONO}" '
        f'font-size="10.5" letter-spacing="2" fill="{MINT}" fill-opacity="0.65">PY</text>'
        f'</svg>'
    )


def build_closing(text="Got an idea worth building? My inbox is open. 🚀"):
    w, h = 880, 76
    tw = len(text) * 9.1                 # approx mono advance at 15px
    x0 = (w - (24 + tw + 13)) / 2        # centre the whole prompt + caret group
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(text)}">'
        f'<defs><linearGradient id="cl" x1="0" y1="0" x2="{w}" y2="0" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{MINT}" stop-opacity="0.10"/>'
        f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0.10"/></linearGradient></defs>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="url(#cl)" '
        f'stroke="{MINT}" stroke-opacity="0.28" stroke-width="1.2"/>'
        f'<text x="{x0:.0f}" y="{h / 2 + 6:.0f}" font-family="{MONO}" font-size="15" '
        f'font-weight="700" fill="{MINT}">&gt;</text>'
        f'<text x="{x0 + 24:.0f}" y="{h / 2 + 6:.0f}" font-family="{MONO}" font-size="15" '
        f'fill="{WHITE}">{esc(text)}</text>'
        f'<rect x="{x0 + 24 + tw + 4:.0f}" y="{h / 2 - 9:.0f}" width="9" height="19" fill="{MINT}">'
        f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" '
        f'repeatCount="indefinite"/></rect>'
        f'</svg>'
    )


# ----------------------------------------------------------------- buttons
# GitHub renders README SVGs as non-interactive <img>, so each clickable
# region has to be its own file wrapped in its own <a>.
# HALF = two buttons under one card (24% width each); FULL = one (48%).
HALF, FULL = 211, 420
BTN_H = 46

BUTTONS = [
    ("btn-relay-demo",   HALF, "LIVE DEMO",  "↗", "demo"),
    ("btn-relay-repo",   HALF, "SOURCE",     "→", "repo"),
    ("btn-argus-demo",   HALF, "LIVE DEMO",  "↗", "demo"),
    ("btn-argus-repo",   HALF, "SOURCE",     "→", "repo"),
    ("btn-cue-repo",     FULL, "VIEW SOURCE ON GITHUB", "→", "repo"),
    ("btn-divdash-repo", FULL, "VIEW SOURCE ON GITHUB", "→", "repo"),
    ("btn-disha-repo",   FULL, "VIEW SOURCE ON GITHUB", "→", "repo"),
    ("btn-aid-private",  FULL, "PRIVATE REPOSITORY",    "\U0001f512", "muted"),
]

ACCENTS = {
    "demo":  dict(accent=MINT, text=MINT, fill_op="0.10", stroke_op="0.50"),
    "repo":  dict(accent=VIOLET, text=VIOLET_TXT, fill_op="0.10", stroke_op="0.42"),
    "muted": dict(accent="#6c6c7d", text=MUTED, fill_op="0.07", stroke_op="0.32"),
}

# Header call-to-action pills that replace the shields.io badges.
CTAS = [
    ("btn-portfolio", 300, "NISHCODES.COM", "↗", "solid"),
    ("btn-linkedin",  230, "LINKEDIN", "→", "cyan"),
    ("btn-email",     210, "SAY HI", "→", "violet"),
]

CTA_STYLES = {
    "cyan":   dict(accent=CYAN, text="#8fe8ff"),
    "violet": dict(accent=VIOLET, text="#d4bfff"),
}


def build_button(name, width, label, glyph, accent):
    a = ACCENTS[accent]
    x, w = 4, width - 8
    h = BTN_H - 10
    uid = name.replace("-", "")
    return (
        f'<svg width="{width}" height="{BTN_H}" viewBox="0 0 {width} {BTN_H}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}">'
        f'<defs><linearGradient id="{uid}f" x1="{x}" y1="5" x2="{x + w}" y2="{5 + h}" '
        f'gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{a["accent"]}" stop-opacity="{a["fill_op"]}"/>'
        f'<stop offset="1" stop-color="{a["accent"]}" stop-opacity="0.03"/>'
        f'</linearGradient></defs>'
        f'<rect x="{x}" y="5" width="{w}" height="{h}" rx="9" fill="url(#{uid}f)" '
        f'stroke="{a["accent"]}" stroke-opacity="{a["stroke_op"]}" stroke-width="1.3"/>'
        f'<rect x="{x}" y="5" width="3" height="{h}" rx="1.5" fill="{a["accent"]}" '
        f'fill-opacity="0.55"/>'
        f'<text x="{x + w / 2:.0f}" y="{BTN_H / 2 + 4:.0f}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="11.5" font-weight="600" letter-spacing="1.6" '
        f'fill="{a["text"]}">{esc(label)}  {esc(glyph)}</text>'
        f'</svg>'
    )


def build_cta(name, width, label, glyph, style):
    h, x, w = 54, 3, 0
    w = width - 6
    bh = h - 8
    uid = name.replace("-", "")
    if style == "solid":
        return (
            f'<svg width="{width}" height="{h}" viewBox="0 0 {width} {h}" fill="none" '
            f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}">'
            f'<defs><linearGradient id="{uid}g" x1="{x}" y1="0" x2="{x + w}" y2="{h}" '
            f'gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{MINT}"/><stop offset="1" stop-color="#00d4a0"/>'
            f'</linearGradient></defs>'
            f'<rect x="{x}" y="4" width="{w}" height="{bh}" rx="10" fill="url(#{uid}g)"/>'
            f'<text x="{x + w / 2:.0f}" y="{h / 2 + 5:.0f}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="2" '
            f'fill="#09090b">{esc(label)}  {esc(glyph)}</text>'
            f'</svg>'
        )
    s = CTA_STYLES[style]
    return (
        f'<svg width="{width}" height="{h}" viewBox="0 0 {width} {h}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}">'
        f'<rect x="{x}" y="4" width="{w}" height="{bh}" rx="10" fill="{s["accent"]}" '
        f'fill-opacity="0.11" stroke="{s["accent"]}" stroke-opacity="0.60" stroke-width="1.4"/>'
        f'<text x="{x + w / 2:.0f}" y="{h / 2 + 5:.0f}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="13" font-weight="600" letter-spacing="2" '
        f'fill="{s["text"]}">{esc(label)}  {esc(glyph)}</text>'
        f'</svg>'
    )


# -------------------------------------------------------------------- main
def write(path, svg):
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  {path}  ({len(svg):,} bytes)")


def main():
    os.makedirs("assets", exist_ok=True)

    print("banner + footer")
    write("assets/banner.svg", build_banner())
    write("assets/footer.svg", build_footer())
    write("assets/term-bar.svg", build_termbar())
    write("assets/closing.svg", build_closing())

    print("section headers")
    for i, (name, title) in enumerate(SECTIONS, start=1):
        write(f"assets/{name}.svg", build_header(i, title))

    print("call-to-action pills")
    for name, width, label, glyph, style in CTAS:
        write(f"assets/{name}.svg", build_cta(name, width, label, glyph, style))

    print("experience panels")
    for i, job in enumerate(EXPERIENCE, start=1):
        write(f"assets/exp-{job['slug']}.svg", build_exp(job, i))

    print("project cards")
    by_slug = {c["slug"]: c for c in CARDS}
    order = {c["slug"]: i for i, c in enumerate(CARDS, start=1)}
    for row in ROWS:
        H = max(measure(by_slug[s]) for s in row)
        for slug in row:
            write(f"assets/card-{slug}.svg", build_card(by_slug[slug], H, order[slug]))

    print("project buttons")
    for name, width, label, glyph, accent in BUTTONS:
        write(f"assets/{name}.svg", build_button(name, width, label, glyph, accent))


if __name__ == "__main__":
    main()
