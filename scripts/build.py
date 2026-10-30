"""Builds every SVG used by the profile README.

    python scripts/build.py

Writes assets/<name>-dark.svg and assets/<name>-light.svg from content.py and assets/live.json.
Design: monochrome Geist, hairline borders, real logos, one orange accent, matching yashvardhan.tech.
"""
from __future__ import annotations

import json
from pathlib import Path

from content import (CONTACT, EDUCATION, EMAIL, INTRO, LEAD, LINKS, LLMSLIM, NAME, PROJECTS, RECOGNITION, STACK,
                     STATUS, WORK)
from logos import LOGOS, path_for
from svgkit import THEMES, Svg, data_uri, dot_grid, f, logo_tile, measure, rich_lines, wrap

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SHOTS = ASSETS / "shots"
STACK_DIR = ASSETS / "stack"
LIVE_PATH = ASSETS / "live.json"
EASE = "cubic-bezier(.2,.7,.1,1)"
W = 1200

# Lucide icons (ISC licence), 24x24 stroke paths.
ICONS = {
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20a14.5 14.5 0 0 0 0-20M2 12h20"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z"/>'
                '<rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
            '<path d="M14 2v4a2 2 0 0 0 2 2h4M16 13H8M16 17H8M10 9H8"/>',
    "arrow": '<path d="M7 7h10v10M7 17 17 7"/>',
}


def icon(name, x, y, size, color, width=1.8):
    s = size / 24
    return (f'<g transform="translate({f(x)} {f(y)}) scale({f(s)})" fill="none" stroke="{color}" '
            f'stroke-width="{f(width / s)}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def load_live() -> dict:
    try:
        return json.loads(LIVE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def reveal(s: Svg):
    s.style(f".rv{{animation:rv .9s {EASE} both}}"
            "@keyframes rv{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}"
            ".fd{animation:fd 1s ease both}@keyframes fd{from{opacity:0}to{opacity:1}}")


def card(s: Svg, x, y, w, h, r=20, fill=None):
    t = s.t
    s.add(f'<rect x="{f(x + .5)}" y="{f(y + .5)}" width="{f(w - 1)}" height="{f(h - 1)}" rx="{r}" '
          f'fill="{fill or t["surface"]}" stroke="{t["line"]}"/>')


def label(s: Svg, x, y, text, color=None, anchor="start", size=11.5):
    return s.text(x, y, text, "mono-m", size, color or s.t["muted"], anchor=anchor, ls=2)


def clip_text(text, font, size, max_w):
    if measure(text, font, size) <= max_w:
        return text
    while text and measure(text + "...", font, size) > max_w:
        text = text[:-1]
    return text.rstrip(" ,.:;") + "..."


def gray2(t):
    return "#8A8A8A" if t["name"] == "dark" else "#A3A3A3"


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

def hero(t):
    H = 500
    live = load_live()
    s = Svg(W, H, t, "Yashvardhan Thanvi",
            "Founder of LLMSlim, the open-source context layer for production AI agents, backed by 15 startup "
            "programs. Runs AMEYOR, an AI and software studio. Previously AI/ML research at DRDO. Available for "
            "freelance work, Jaipur, India.")
    reveal(s)
    card(s, 0, 0, W, H, r=24)
    dot_grid(s, 560, 0, 640, H, gap=15, r=1, opacity=.22 if t["name"] == "dark" else .16, fade_cx=.62, fade_cy=.5,
             uid="hg")

    mark = LOGOS / "mark.svg"
    if mark.exists():
        inv = ' style="filter:invert(1)"' if t["name"] == "light" else ""
        s.add(f'<image href="{data_uri(mark)}" x="44" y="38" width="34" height="29"{inv}/>')
    s.add(s.text(88, 59, "Yashvardhan Thanvi", "sans-sb", 15, t["ink"]))

    s.style("@keyframes pulse{0%{transform:scale(1);opacity:.6}100%{transform:scale(3.2);opacity:0}}"
            ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}")
    x = 48
    for i, txt in enumerate(STATUS):
        dot = 18 if i == 0 else 0
        w = measure(txt, "mono", 12, .4) + 28 + dot
        s.add(f'<g class="fd" style="animation-delay:{.1 + i * .1:.1f}s">'
              f'<rect x="{f(x + .5)}" y="104.5" width="{f(w - 1)}" height="29" rx="14.5" fill="{t["surface2"]}" '
              f'stroke="{t["line2"]}"/>'
              + (f'<circle cx="{f(x + 17)}" cy="119" r="3.5" fill="#22C55E" class="pulse"/>'
                 f'<circle cx="{f(x + 17)}" cy="119" r="3.5" fill="#22C55E"/>' if dot else "")
              + s.text(x + 14 + dot, 123.5, txt, "mono", 12, t["body"], ls=.4) + "</g>")
        x += w + 10

    s.add('<g class="rv" style="animation-delay:.15s">'
          + s.text(44, 232, NAME[0], "sans-b", 88, t["ink"], ls=-3.6) + "</g>")
    s.add('<g class="rv" style="animation-delay:.25s">'
          + s.text(44, 322, NAME[1], "sans-b", 88, gray2(t), ls=-3.6) + "</g>")

    runs = [(txt, "sans-m" if em else "sans", t["ink"] if em else t["body"]) for txt, em in INTRO]
    lines = rich_lines(runs, 18, 560)
    s.add('<g class="rv" style="animation-delay:.4s">'
          + "".join(s.tspan_text(48, 378 + i * 28, ln, size=18) for i, ln in enumerate(lines)) + "</g>")

    # terminal (dark in both themes, like the portfolio)
    tx, ty, tw, th = 676, 120, 476, 300
    bg, bar, edge = "#0B0B0B", "#141414", "#262626"
    s.defs_add(f'<clipPath id="term"><rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="14"/></clipPath>')
    s.add(f'<g class="rv" style="animation-delay:.3s"><g clip-path="url(#term)">'
          f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="{bg}"/>'
          f'<rect x="{tx}" y="{ty}" width="{tw}" height="38" fill="{bar}"/>'
          f'<line x1="{tx}" y1="{ty + 38}" x2="{tx + tw}" y2="{ty + 38}" stroke="{edge}"/></g>'
          f'<rect x="{tx + .5}" y="{ty + .5}" width="{tw - 1}" height="{th - 1}" rx="14" fill="none" stroke="{edge}"/>'
          + "".join(f'<circle cx="{tx + 22 + i * 18}" cy="{ty + 19}" r="5.5" fill="#333333"/>' for i in range(3))
          + s.text(tx + tw / 2, ty + 24, "yash@jaipur: ~", "mono", 12, "#8A8A8A", anchor="middle") + "</g>")

    version = live.get("llmslim", {}).get("version", "")
    merged = live.get("merged")
    merged_orgs = [o["name"] for o in live.get("org_list", []) if o.get("merged")]
    lines = [("cmd", "whoami"), ("out", "founder @ LLMSlim + AMEYOR · AI engineer")]
    if version:
        lines += [("cmd", "pip show llmslim | grep Version"), ("out", f"Version: {version}")]
    if merged:
        tail = f"   # {', '.join(merged_orgs[:3])} and {len(merged_orgs) - 3} more" if len(merged_orgs) > 3 else ""
        lines += [("cmd", "gh search prs --author=@me --merged | wc -l"), ("out", f"{merged}{tail}")]
    lines.append(("cur", ""))

    size, lh, x0, y0 = 13, 26, tx + 22, ty + 74
    cw = measure("m", "mono", size)
    t0, parts = .9, []
    for i, (kind, txt) in enumerate(lines):
        y = y0 + i * lh
        if kind == "cmd":
            text = s.tspan_text(x0, y, [("› ", "mono-m", "#FF7A3D"), (txt, "mono", "#EDEDED")], size=size)
            width = measure("› " + txt, "mono", size) + 8
            dur = max(.35, len(txt) * .028)
            # A cover slides right in steps to "type" the command. Static renderers show the text uncovered.
            parts.append(f'{text}<rect x="{f(x0 - 2)}" y="{f(y - 16)}" width="{f(width + 4)}" height="22" '
                         f'fill="{bg}" transform="translate({f(width + 4)} 0)" '
                         f'style="animation:ty{i} {dur:.2f}s steps({len(txt) + 2}) {t0:.2f}s both"/>')
            s.style(f"@keyframes ty{i}{{from{{transform:translateX(0)}}to{{transform:translateX({f(width + 4)}px)}}}}")
            t0 += dur + .25
        elif kind == "out":
            parts.append(f'<g style="animation:fd .2s linear {t0:.2f}s both">'
                         + s.text(x0 + 2 * cw, y, clip_text(txt, "mono", size, tw - 66), "mono", size, "#A1A1A1")
                         + "</g>")
            t0 += .35
        else:
            parts.append(s.text(x0, y, "›", "mono-m", size, "#FF7A3D")
                         + f'<rect x="{f(x0 + cw * 1.6)}" y="{f(y - 13)}" width="{f(cw)}" height="17" fill="#EDEDED" '
                           f'style="animation:blink 1.1s steps(1) {t0:.2f}s infinite"/>')
    s.style("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}")
    s.add(f'<g class="rv" style="animation-delay:.3s"><g clip-path="url(#term)">{"".join(parts)}</g></g>')
    return s


# ---------------------------------------------------------------------------
# Link buttons
# ---------------------------------------------------------------------------

def link_pill(t, text, icon_name, primary):
    h, size = 48, 15.5
    w = round(46 + measure(text, "sans-m", size) + 20)
    s = Svg(w, h, t, text)
    if primary:
        fill, stroke, color = t["button"], t["button"], t["on_button"]
    else:
        fill, stroke, color = t["surface"], t["line2"], t["ink"]
    s.add(f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{(h - 1) / 2}" fill="{fill}" stroke="{stroke}"/>')
    s.add(icon(icon_name, 18, 15, 18, color))
    s.add(s.text(46, h / 2 + size * .36, text, "sans-m", size, color))
    return s


# ---------------------------------------------------------------------------
# "Pull requests merged at" logo strip
# ---------------------------------------------------------------------------

def merged_strip(t):
    live = load_live()
    orgs = [o for o in live.get("org_list", []) if o.get("merged")]
    shown = orgs[:10]
    H = 186
    s = Svg(W, H, t, "Pull requests merged at " + ", ".join(o["name"] for o in orgs),
            f"{live.get('merged', 0)} merged pull requests across {len(orgs)} organisations.")
    reveal(s)
    head = (f"{live.get('merged', 0)} PULL REQUESTS MERGED ACROSS {len(orgs)} ORGANISATIONS, INCLUDING"
            if orgs else "OPEN SOURCE")
    tl = measure(head, "mono-m", 11.5, 2) + 48
    s.add(f'<line x1="0" y1="20" x2="{f((W - tl) / 2)}" y2="20" stroke="{t["line"]}"/>'
          f'<line x1="{f((W + tl) / 2)}" y1="20" x2="{W}" y2="20" stroke="{t["line"]}"/>')
    s.add(label(s, W / 2, 24, head, anchor="middle"))
    n = len(shown)
    if not n:
        return s
    step, size = 116, 60
    x0 = (W - (n - 1) * step) / 2
    for i, o in enumerate(shown):
        cx = x0 + i * step
        s.add(f'<g class="rv" style="animation-delay:{.1 + i * .06:.2f}s">'
              + logo_tile(s, cx - size / 2, 56, size, LOGOS / f"gh-{o['logo']}.png", o["name"], uid=f"m{i}")
              + s.text(cx, 146, clip_text(o["name"], "sans-m", 13.5, step - 10), "sans-m", 13.5, t["body"],
                       anchor="middle")
              + s.text(cx, 166, f"{o['merged']} merged", "mono", 11, t["muted"], anchor="middle") + "</g>")
    return s


# ---------------------------------------------------------------------------
# LLMSlim
# ---------------------------------------------------------------------------

def llmslim_card(t):
    H = 640
    live = load_live()
    L = LLMSLIM
    ll = live.get("llmslim", {})
    s = Svg(W, H, t, "LLMSlim: " + L["tagline"],
            L["about"] + " " + "; ".join(f"{b} {a} ({c})" for b, a, c in L["stats"])
            + ". Backed by " + ", ".join(L["program_names"]) + ".")
    reveal(s)
    card(s, 0, 0, W, H, r=24)
    if t["name"] == "dark":
        s.defs_add('<radialGradient id="lg" cx=".82" cy=".22" r=".55">'
                   f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity=".10"/>'
                   f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>')
        s.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#lg)"/>')

    # 3D render (LLMSlim's own asset), floating gently
    img = SHOTS / "llmslim-3d.jpg"
    ix, iy, iw, ih = 624, 40, 536, 300
    s.defs_add(f'<clipPath id="core"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="16"/></clipPath>')
    s.style("@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}"
            ".float{animation:float 7s ease-in-out infinite}")
    if img.exists():
        s.add(f'<g class="fd" style="animation-delay:.2s"><g class="float"><g clip-path="url(#core)">'
              f'<image href="{data_uri(img)}" x="{ix}" y="{iy}" width="{iw}" height="{ih}" '
              f'preserveAspectRatio="xMidYMid slice"/></g>'
              f'<rect x="{ix + .5}" y="{iy + .5}" width="{iw - 1}" height="{ih - 1}" rx="16" fill="none" '
              f'stroke="{t["line2"]}"/></g></g>')

    x0 = 48
    s.add('<g class="rv" style="animation-delay:.05s">'
          + logo_tile(s, x0, 46, 52, path_for("llmslim"), "LLMSlim", uid="ll")
          + s.text(x0 + 68, 84, "LLMSlim", "sans-b", 38, t["ink"], ls=-1.4))
    if ll.get("version"):
        vx = x0 + 68 + measure("LLMSlim", "sans-b", 38, -1.4) + 14
        vt = f"v{ll['version']}"
        vw = measure(vt, "mono", 12) + 20
        s.add(f'<rect x="{f(vx + .5)}" y="62.5" width="{f(vw - 1)}" height="25" rx="12.5" fill="{t["surface2"]}" '
              f'stroke="{t["line2"]}"/>' + s.text(vx + 10, 79, vt, "mono", 12, t["body"]))
    s.add("</g>")
    s.add('<g class="rv" style="animation-delay:.12s">' + s.text(x0, 146, L["tagline"], "sans-sb", 22, t["ink"])
          + "".join(s.text(x0, 182 + i * 26, ln, "sans", 16.5, t["body"])
                    for i, ln in enumerate(wrap(L["about"], "sans", 16.5, 540)[:3])) + "</g>")
    cmd = "pip install llmslim"
    bw = measure("$ " + cmd, "mono-m", 15) + 44
    s.add('<g class="rv" style="animation-delay:.2s">'
          f'<rect x="{x0 + .5}" y="272.5" width="{f(bw)}" height="45" rx="10" fill="{t["surface2"]}" '
          f'stroke="{t["line2"]}"/>'
          + s.tspan_text(x0 + 20, 300, [("$ ", "mono-m", t["accent"]), (cmd, "mono-m", t["ink"])], size=15)
          + label(s, x0, 346, L["facts"]) + "</g>")

    by = 384
    s.add(f'<line x1="{x0}" y1="{by}" x2="{W - x0}" y2="{by}" stroke="{t["line"]}"/>')
    cw = (W - 2 * x0) / 4
    for i, (big, lab, src) in enumerate(L["stats"]):
        x = x0 + i * cw + (0 if i == 0 else 24)
        if i:
            s.add(f'<line x1="{f(x0 + i * cw)}" y1="{by + 26}" x2="{f(x0 + i * cw)}" y2="{by + 112}" '
                  f'stroke="{t["line"]}"/>')
        s.add(f'<g class="rv" style="animation-delay:{.3 + i * .07:.2f}s">'
              + s.text(x, by + 66, big, "sans-b", 42, t["ink"], ls=-1.6)
              + s.text(x + 1, by + 94, lab, "sans-m", 14.5, t["body"])
              + s.text(x + 1, by + 114, src, "mono", 11, t["muted"], ls=.8) + "</g>")

    py = 528
    s.add(f'<line x1="{x0}" y1="{py}" x2="{W - x0}" y2="{py}" stroke="{t["line"]}"/>')
    s.add(label(s, x0, py + 34, f"BACKED BY {len(L['programs'])} STARTUP PROGRAMS"))
    meta = []
    if ll.get("downloads_week"):
        meta.append(f"{ll['downloads_week']:,} DOWNLOADS LAST WEEK")
    lists = [x for x in live.get("listed_in", []) if x.get("kind", "list") == "list"]
    if lists:
        meta.append(f"LISTED IN {len(lists)} CURATED LISTS")
    if meta:
        s.add(label(s, W - x0, py + 34, "  ·  ".join(meta), anchor="end"))
    size, gap = 40, 9
    for i, key in enumerate(L["programs"]):
        s.add(f'<g class="rv" style="animation-delay:{.45 + i * .03:.2f}s">'
              + logo_tile(s, x0 + i * (size + gap), py + 52, size, path_for(key), L["program_names"][i], uid=f"p{i}")
              + "</g>")
    return s


# ---------------------------------------------------------------------------
# Project cards
# ---------------------------------------------------------------------------

def project_card(t, p):
    w, h = 590, 412
    s = Svg(w, h, t, f"{p['name']}: {p['line']}")
    reveal(s)
    card(s, 0, 0, w, h, r=18)
    ix, iy, iw, ih = 10, 10, w - 20, 320
    s.defs_add(f'<clipPath id="shot"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="11"/></clipPath>')
    img = SHOTS / f"{p['shot']}.jpg"
    if img.exists():
        s.add(f'<g class="fd"><g clip-path="url(#shot)"><image href="{data_uri(img)}" x="{ix}" y="{iy}" '
              f'width="{iw}" height="{ih}" preserveAspectRatio="xMidYMid slice"/></g>'
              f'<rect x="{ix + .5}" y="{iy + .5}" width="{iw - 1}" height="{ih - 1}" rx="11" fill="none" '
              f'stroke="{t["line"]}"/></g>')
    tag = p["tag"]
    tw = measure(tag, "mono-m", 10.5, 1.4) + 22
    s.add(f'<rect x="24" y="24" width="{f(tw)}" height="24" rx="12" fill="#000000" fill-opacity=".62"/>'
          + s.text(35, 40, tag, "mono-m", 10.5, "#FFFFFF", ls=1.4))
    s.add('<g class="rv" style="animation-delay:.1s">'
          + s.text(24, 368, p["name"], "sans-sb", 22, t["ink"], ls=-.4)
          + s.text(24, 393, clip_text(p["line"], "sans", 15, w - 110), "sans", 15, t["body"])
          + f'<circle cx="{w - 40}" cy="379" r="17.5" fill="{t["surface2"]}" stroke="{t["line2"]}"/>'
          + icon("arrow", w - 48, 371, 16, t["ink"]) + "</g>")
    return s


# ---------------------------------------------------------------------------
# Open source logo wall
# ---------------------------------------------------------------------------

def oss_wall(t):
    live = load_live()
    orgs = live.get("org_list", [])
    cols, gap, th, max_tiles = 4, 16, 84, 20
    tw = (W - (cols - 1) * gap) / cols
    shown = orgs if len(orgs) <= max_tiles else orgs[:max_tiles - 1]
    rest = orgs[len(shown):]
    rows = -(-(len(shown) + (1 if rest else 0)) // cols)
    band = 128
    H = band + gap + rows * (th + gap) - gap
    s = Svg(W, H, t, f"{live.get('prs', 0)} pull requests to {live.get('orgs', 0)} organisations, "
                     f"{live.get('merged', 0)} merged",
            "Organisations: " + ", ".join(f"{o['name']} ({o['merged']} merged of {o['prs']})" for o in orgs))
    reveal(s)
    card(s, 0, 0, W, band, r=20)
    cells = [(live.get("prs", 0), "pull requests"), (live.get("merged", 0), "merged"),
             (live.get("orgs", 0), "organisations"), (live.get("repos", 0), "repositories")]
    cw = (W - 96) / 4
    for i, (n, lab) in enumerate(cells):
        x = 48 + i * cw
        if i:
            s.add(f'<line x1="{f(x - 24)}" y1="34" x2="{f(x - 24)}" y2="94" stroke="{t["line"]}"/>')
        s.add(f'<g class="rv" style="animation-delay:{.05 + i * .06:.2f}s">'
              + s.text(x, 74, f"{n:,}", "sans-b", 44, t["accent"] if i == 1 else t["ink"], ls=-1.6)
              + s.text(x + 2, 100, lab, "sans", 14.5, t["muted"]) + "</g>")
    for k, o in enumerate(shown):
        r, c = divmod(k, cols)
        x, y = c * (tw + gap), band + gap + r * (th + gap)
        card(s, x, y, tw, th, r=16)
        plural = "S" if o["prs"] != 1 else ""
        sub = f"{o['merged']} MERGED · {o['prs']} PR{plural}" if o["merged"] else f"{o['prs']} PR{plural} IN REVIEW"
        s.add(f'<g class="rv" style="animation-delay:{.15 + k * .03:.2f}s">'
              + logo_tile(s, x + 18, y + 18, 48, LOGOS / f"gh-{o['logo']}.png", o["name"], uid=f"o{k}")
              + s.text(x + 80, y + 40, clip_text(o["name"], "sans-sb", 16, tw - 96), "sans-sb", 16, t["ink"])
              + s.text(x + 80, y + 61, sub, "mono", 11, t["accent"] if o["merged"] else t["muted"], ls=1)
              + "</g>")
    if rest:
        k = len(shown)
        r, c = divmod(k, cols)
        x, y = c * (tw + gap), band + gap + r * (th + gap)
        card(s, x, y, tw, th, r=16, fill=t["surface2"])
        names = ", ".join(o["name"] for o in rest)
        s.add(s.text(x + 22, y + 40, f"+{len(rest)} more", "sans-sb", 16, t["ink"])
              + s.text(x + 22, y + 61, clip_text(names, "mono", 11, tw - 40), "mono", 11, t["muted"]))
    return s


# ---------------------------------------------------------------------------
# Recognition
# ---------------------------------------------------------------------------

def recognition(t):
    gap = 16
    cw, ch = (W - gap) / 2, 112
    rows = -(-len(RECOGNITION) // 2)
    H = rows * (ch + gap) - gap
    s = Svg(W, H, t, "Recognition", " ".join(f"{a} ({d}): {b}" for _, a, b, d in RECOGNITION))
    reveal(s)
    for k, (logo, title, detail, year) in enumerate(RECOGNITION):
        r, c = divmod(k, 2)
        x, y = c * (cw + gap), r * (ch + gap)
        card(s, x, y, cw, ch, r=18)
        lines = wrap(detail, "sans", 14, cw - 92 - 28)[:2]
        s.add(f'<g class="rv" style="animation-delay:{.05 + k * .05:.2f}s">'
              + logo_tile(s, x + 20, y + 28, 56, path_for(logo), title, uid=f"r{k}")
              + s.text(x + 92, y + 44, clip_text(title, "sans-sb", 17, cw - 92 - 70), "sans-sb", 17, t["ink"])
              + s.text(x + cw - 22, y + 44, year, "mono", 11.5, t["muted"], anchor="end", ls=1)
              + "".join(s.text(x + 92, y + 68 + i * 20, ln, "sans", 14, t["body"]) for i, ln in enumerate(lines))
              + "</g>")
    return s


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

def experience(t):
    gap = 16
    cw = (W - gap) / 2
    ch = 64 + len(LEAD) * 58 + 8
    H = ch + gap + 96
    s = Svg(W, H, t, "Experience",
            " ".join(f"{o}, {r}, {w.lower()}." for _, o, r, w, _ in WORK)
            + " " + " ".join(f"{o}, {r}." for _, o, r, _ in LEAD))
    reveal(s)
    card(s, 0, 0, cw, ch, r=20)
    card(s, cw + gap, 0, cw, ch, r=20)
    s.add(label(s, 28, 44, "WORK"))
    for i, (logo, org, role, when, note) in enumerate(WORK):
        y = 72 + i * 118
        lines = wrap(note, "sans", 13.5, cw - 96 - 28)[:2]
        s.add(f'<g class="rv" style="animation-delay:{.05 + i * .07:.2f}s">'
              + logo_tile(s, 28, y, 48, path_for(logo), org.split(",")[0], uid=f"w{i}")
              + s.text(92, y + 18, clip_text(org, "sans-sb", 16, cw - 92 - 130), "sans-sb", 16, t["ink"])
              + s.text(cw - 28, y + 18, when, "mono", 11, t["muted"], anchor="end", ls=1)
              + s.text(92, y + 40, role, "sans", 14.5, t["body"])
              + "".join(s.text(92, y + 64 + j * 19, ln, "sans", 13.5, t["muted"]) for j, ln in enumerate(lines))
              + "</g>")
    x0 = cw + gap
    s.add(label(s, x0 + 28, 44, "COMMUNITY AND LEADERSHIP"))
    for i, (logo, org, role, when) in enumerate(LEAD):
        y = 66 + i * 58
        s.add(f'<g class="rv" style="animation-delay:{.1 + i * .05:.2f}s">'
              + logo_tile(s, x0 + 28, y, 40, path_for(logo), org, uid=f"c{i}")
              + s.text(x0 + 84, y + 17, clip_text(org, "sans-sb", 15, cw - 84 - 90), "sans-sb", 15, t["ink"])
              + s.text(x0 + cw - 28, y + 17, when, "mono", 11, t["muted"], anchor="end", ls=1)
              + s.text(x0 + 84, y + 36, role, "sans", 13.5, t["body"])
              + (f'<line x1="{x0 + 84}" y1="{y + 50}" x2="{x0 + cw - 28}" y2="{y + 50}" stroke="{t["line"]}"/>'
                 if i < len(LEAD) - 1 else "")
              + "</g>")
    logo, school, degree, score, score_label, years = EDUCATION
    ey = ch + gap
    card(s, 0, ey, W, 96, r=20)
    s.add('<g class="rv" style="animation-delay:.4s">'
          + logo_tile(s, 24, ey + 20, 56, path_for(logo), school, uid="edu")
          + s.text(96, ey + 44, school, "sans-sb", 17, t["ink"])
          + s.text(96, ey + 68, degree, "sans", 14.5, t["body"])
          + s.text(W - 28, ey + 52, score, "sans-b", 34, t["ink"], anchor="end", ls=-1)
          + s.text(W - 28 - measure(score, "sans-b", 34, -1) - 12, ey + 50, score_label, "mono", 11, t["muted"],
                   anchor="end", ls=1.4)
          + s.text(W - 28, ey + 74, years, "mono", 11, t["muted"], anchor="end", ls=1.4) + "</g>")
    return s


# ---------------------------------------------------------------------------
# Stack (skill-icons, MIT)
# ---------------------------------------------------------------------------

def stack_icon(name, theme_name):
    for cand in (f"{name}-{'Dark' if theme_name == 'dark' else 'Light'}.svg", f"{name}.svg"):
        p = STACK_DIR / cand
        if p.exists():
            return p
    return None


def stack(t):
    size, gap = 64, 18
    H = len(STACK) * size + (len(STACK) - 1) * gap + 8
    s = Svg(W, H, t, "Stack", ", ".join(sum(STACK, [])))
    reveal(s)
    k = 0
    for r, row in enumerate(STACK):
        total = len(row) * size + (len(row) - 1) * gap
        x0 = (W - total) / 2
        for i, name in enumerate(row):
            p = stack_icon(name, t["name"])
            if not p:
                continue
            s.add(f'<g class="rv" style="animation-delay:{.03 * k:.2f}s"><image href="{data_uri(p)}" '
                  f'x="{f(x0 + i * (size + gap))}" y="{4 + r * (size + gap)}" width="{size}" height="{size}"/></g>')
            k += 1
    return s


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

def contact(t):
    H = 290
    C = CONTACT
    s = Svg(W, H, t, f"{C['title'][0]} {C['title'][1]}", f"{C['body']} {C['button']} or email {EMAIL}.")
    reveal(s)
    card(s, 0, 0, W, H, r=24)
    dot_grid(s, 600, 0, 600, H, gap=15, r=1, opacity=.2 if t["name"] == "dark" else .14, fade_cx=.7, fade_cy=.5,
             uid="cg")
    s.add('<g class="rv" style="animation-delay:.05s">'
          + s.text(48, 104, C["title"][0], "sans-b", 44, t["ink"], ls=-1.6)
          + s.text(48, 156, C["title"][1], "sans-b", 44, gray2(t), ls=-1.6) + "</g>")
    s.add('<g class="rv" style="animation-delay:.15s">'
          + "".join(s.text(48, 204 + i * 26, ln, "sans", 16.5, t["body"])
                    for i, ln in enumerate(wrap(C["body"], "sans", 16.5, 600)[:2])) + "</g>")
    bw = measure(C["button"], "sans-m", 16) + 96
    bx, by = W - 48 - bw, 100
    s.add('<g class="rv" style="animation-delay:.25s">'
          f'<rect x="{f(bx)}" y="{by}" width="{f(bw)}" height="54" rx="27" fill="{t["button"]}"/>'
          + icon("calendar", bx + 22, by + 17, 20, t["on_button"])
          + s.text(bx + 54, by + 33, C["button"], "sans-m", 16, t["on_button"])
          + icon("arrow", bx + bw - 38, by + 19, 16, t["on_button"])
          + s.text(bx + bw / 2, by + 92, f"or write to {EMAIL}", "mono", 12.5, t["muted"], anchor="middle")
          + "</g>")
    return s


# ---------------------------------------------------------------------------

def jobs():
    out = {"hero": hero, "merged": merged_strip, "llmslim": llmslim_card, "oss": oss_wall,
           "recognition": recognition, "experience": experience, "stack": stack, "contact": contact}
    for _, key, text, ic, primary in LINKS:
        out[key] = (lambda th, a=(text, ic, primary): link_pill(th, *a))
    for p in PROJECTS:
        out[f"p-{p['shot']}"] = (lambda th, a=p: project_card(th, a))
    return out


def main(only: list[str] | None = None):
    for name, fn in jobs().items():
        if only and name not in only:
            continue
        for tname, theme in THEMES.items():
            svg = fn(theme)
            out = ASSETS / f"{name}-{tname}.svg"
            svg.save(out)
            print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1024:.0f} KB  {svg.w}x{svg.h}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
