"""Builds the static, animated SVGs used by the profile README.

    python scripts/build.py

Writes assets/<name>-dark.svg and assets/<name>-light.svg.
"""
from __future__ import annotations

import json
import math
import random
import re
from pathlib import Path

from content import (EDUCATION, HERO_CHIPS, HOT_TOOLS, LEAD, LINKS as LINK_ITEMS, LLMSLIM, PROJECTS,
                     RECOGNITION, TICKER, TOOLS, WORK)
from svgkit import THEMES, Svg, ease_css, f, grain, measure, pill, sphere_points, wrap

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
EASE = ease_css()
LIVE_PATH = ASSETS / "live.json"


def load_live() -> dict:
    """Facts derived from the GitHub and PyPI APIs by refresh.py (empty if it never ran)."""
    try:
        return json.loads(LIVE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def fill(template: str, live: dict) -> str | None:
    """Fill {placeholders} in content strings; None when a needed live value is missing."""
    ll = live.get("llmslim", {})
    vals = {"merged_orgs": ", ".join(live.get("merged_orgs", [])[:4]).upper(), "prs": live.get("prs"),
            "merged": live.get("merged"), "orgs": live.get("orgs"), "version": ll.get("version"),
            "downloads_week": ll.get("downloads_week")}
    if any(vals.get(k) in (None, "", 0) for k in re.findall(r"{(\w+)}", template)):
        return None
    return template.format(**vals)


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

def token_sphere(svg: Svg, cx, cy, R, *, T=28.0, tilt=0.36, seed=11, hot=0.11, delay_in=0.5):
    """A dotted globe that spins in 3D using only CSS keyframes.

    Each dot runs three in-phase sine animations: x (sin), y and depth (cos),
    which is exactly what an orthographic projection of a spinning sphere is.
    """
    t = svg.t
    rnd = random.Random(seed)
    ease = "cubic-bezier(.37,0,.63,1)"
    rings = sphere_points(n_rings=15, n_eq=38)
    css = [
        f".sz{{transform-box:fill-box;transform-origin:center;animation:sz {T}s {ease} infinite}}"
        "@keyframes sz{0%,100%{transform:scale(.34);opacity:.12}50%{transform:scale(1);opacity:1}}"
    ]
    dots = []
    for k, (lat, n, off) in enumerate(rings):
        r = R * math.cos(lat)
        a = r * math.sin(tilt)
        y0 = cy - R * math.sin(lat) * math.cos(tilt)
        css.append(
            f"@keyframes x{k}{{0%,100%{{transform:translateX({f(-r)}px)}}50%{{transform:translateX({f(r)}px)}}}}"
            f"@keyframes y{k}{{0%,100%{{transform:translateY({f(-a)}px)}}50%{{transform:translateY({f(a)}px)}}}}"
            f".x{k}{{animation:x{k} {T}s {ease} infinite}}.y{k}{{animation:y{k} {T}s {ease} infinite}}"
        )
        for j in range(n):
            theta = 2 * math.pi * j / n + off
            t0 = (theta + math.pi / 2) / (2 * math.pi) * T
            dx = -(t0 % T)
            dz = -((t0 + T / 4) % T)
            is_hot = rnd.random() < hot
            fill = t["accent"] if is_hot else t["dot"]
            rr = 3.1 if is_hot else 2.15
            dots.append(
                f'<g transform="translate({f(cx)} {f(y0)})"><g class="x{k}" style="animation-delay:{dx:.2f}s">'
                f'<g class="y{k}" style="animation-delay:{dz:.2f}s"><circle r="{rr}" fill="{fill}" class="sz" '
                f'style="animation-delay:{dz:.2f}s"/></g></g></g>'
            )
    svg.style("".join(css))
    svg.style(
        f".globe{{animation:globeIn 1.6s {EASE} {delay_in}s both}}"
        "@keyframes globeIn{from{opacity:0;transform:scale(.86)}to{opacity:1;transform:scale(1)}}"
        f".globe{{transform-box:view-box;transform-origin:{f(cx)}px {f(cy)}px}}"
        f".breathe{{transform-box:view-box;transform-origin:{f(cx)}px {f(cy)}px;"
        f"animation:breathe 9s {ease} infinite}}"
        "@keyframes breathe{0%,100%{transform:scale(1)}50%{transform:scale(.93)}}"
    )
    # orbit ring + satellites
    rx, ry, rot = R * 1.32, R * 1.32 * 0.24, -12
    orbit = (f"M {f(cx - rx)} {f(cy)} a {f(rx)} {f(ry)} 0 1 0 {f(2 * rx)} 0 "
             f"a {f(rx)} {f(ry)} 0 1 0 {f(-2 * rx)} 0")
    ring = (f'<g transform="rotate({rot} {f(cx)} {f(cy)})">'
            f'<path d="{orbit}" fill="none" stroke="{t["line2"]}" stroke-width="1" stroke-dasharray="2 5"/>'
            f'<circle r="4.5" fill="{t["accent"]}"><animateMotion dur="14s" repeatCount="indefinite" path="{orbit}"/></circle>'
            f'<circle r="2.6" fill="{t["ink"]}" opacity=".7"><animateMotion dur="14s" begin="-7s" repeatCount="indefinite" path="{orbit}"/></circle>'
            f"</g>")
    halo = f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R + 26)}" fill="none" stroke="{t["line"]}" stroke-width="1"/>'
    svg.add(f'<g class="globe">{halo}<g class="breathe">{"".join(dots)}</g>{ring}</g>')


def ticker(svg: Svg, y, h, items, *, speed=38.0):
    t = svg.t
    size, ls, gap = 12.5, 1.6, 26
    xs, x = [], 0.0
    for it in items:
        xs.append(x)
        x += measure(it, "mono", size, ls) + gap * 2 + 6
    loop_w = x
    cy = y + h / 2
    parts = []
    for rep in (0, 1):
        for it, x0 in zip(items, xs):
            bx = x0 + rep * loop_w
            parts.append(svg.text(bx, cy + size * 0.36, it, "mono", size, t["muted"], ls=ls))
            dx = bx + measure(it, "mono", size, ls) + gap + 3
            parts.append(f'<rect x="{f(dx - 3)}" y="{f(cy - 3)}" width="6" height="6" fill="{t["accent"]}" '
                         f'transform="rotate(45 {f(dx)} {f(cy)})"/>')
    dur = loop_w / speed
    svg.style(f".tick{{animation:tick {dur:.1f}s linear infinite}}"
              f"@keyframes tick{{from{{transform:translateX(0)}}to{{transform:translateX(-{f(loop_w)}px)}}}}")
    svg.add(f'<g clip-path="url(#tickclip)"><g class="tick">{"".join(parts)}</g></g>')
    svg.defs_add(f'<clipPath id="tickclip"><rect x="0" y="{f(y)}" width="{svg.w}" height="{f(h)}"/></clipPath>')


def hero(theme: dict) -> Svg:
    W, H = 1200, 620
    t = theme
    s = Svg(W, H, t, "Yashvardhan Thanvi, founder of LLMSlim",
            "AI engineer and open source builder from Jaipur, India. Available for freelance work.")
    dark = t["name"] == "dark"
    s.defs_add(f'<clipPath id="card"><rect width="{W}" height="{H}" rx="30"/></clipPath>')
    if dark:
        s.defs_add(
            '<radialGradient id="ember" cx="0.78" cy="1.05" r="0.62">'
            f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity=".20"/>'
            f'<stop offset=".55" stop-color="{t["accent"]}" stop-opacity=".04"/>'
            f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
        )
        bg = (f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
              f'<rect width="{W}" height="{H}" fill="url(#ember)"/>')
    else:
        s.defs_add(
            '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#9CC1E7"/><stop offset=".55" stop-color="#C9D6E4"/>'
            '<stop offset="1" stop-color="#EDDFD0"/></linearGradient>'
            '<filter id="cloud" x="-50%" y="-50%" width="200%" height="200%">'
            '<feGaussianBlur stdDeviation="34"/></filter>'
        )
        clouds = "".join(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#FFFFFF" opacity="{o}" class="cl{i % 2}"/>'
            for i, (cx, cy, rx, ry, o) in enumerate([
                (180, 520, 260, 70, .75), (520, 600, 340, 80, .8), (980, 560, 300, 90, .7),
                (1120, 140, 180, 40, .45), (640, 120, 160, 34, .35), (60, 250, 160, 40, .4)])
        )
        s.style("@keyframes drift{from{transform:translateX(-30px)}to{transform:translateX(30px)}}"
                ".cl0{animation:drift 24s ease-in-out infinite alternate}"
                ".cl1{animation:drift 31s ease-in-out infinite alternate-reverse}")
        bg = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
              f'<g filter="url(#cloud)">{clouds}</g>')
    grain(s, opacity=0.10 if dark else 0.07)
    s.add(f'<g clip-path="url(#card)">{bg}<rect width="{W}" height="{H}" filter="url(#grain)" opacity="1"/>')

    ink, body, muted = t["ink"], t["body"], t["muted"]
    if not dark:
        body, muted = "#3A3431", "#5C5552"

    # reveal animations
    s.style(
        f".rv{{animation:rv 1.1s {EASE} both}}"
        "@keyframes rv{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}"
        ".fd{animation:fd 1.2s ease both}@keyframes fd{from{opacity:0}to{opacity:1}}"
        "@keyframes pulse{0%{transform:scale(1);opacity:.55}100%{transform:scale(3.2);opacity:0}}"
        ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.2s ease-out infinite}"
    )

    # top bar
    s.add(f'<g class="fd" style="animation-delay:.1s">'
          + s.text(56, 64, "YASHVARDHAN.TECH", "mono-m", 12.5, muted, ls=2.2)
          + s.text(56 + measure("YASHVARDHAN.TECH", "mono-m", 12.5, 2.2) + 18, 64,
                   "/  JAIPUR, INDIA  /  26.91° N  75.79° E", "mono", 12.5, muted, ls=1.6, opacity=.75)
          + "</g>")
    label = "Available for freelance"
    lw = measure(label, "sans-m", 14.5) + 50
    px, py = W - 56 - lw, 42
    pill_fill = "rgba(255,255,255,.04)" if dark else "rgba(255,255,255,.55)"
    s.add(f'<g class="fd" style="animation-delay:.3s">'
          f'<rect x="{f(px)}" y="{py}" width="{f(lw)}" height="34" rx="17" fill="{pill_fill}" '
          f'stroke="{t["line2"] if dark else "rgba(26,22,21,.12)"}"/>'
          f'<circle cx="{f(px + 21)}" cy="{py + 17}" r="4" fill="{t["accent"]}" class="pulse"/>'
          f'<circle cx="{f(px + 21)}" cy="{py + 17}" r="4" fill="{t["accent"]}"/>'
          + s.text(px + 34, py + 22, label, "sans-m", 14.5, ink) + "</g>")

    # eyebrow + name
    x0 = 56
    s.add(f'<g class="rv" style="animation-delay:.15s">'
          f'<rect x="{x0}" y="148" width="22" height="2" fill="{t["accent"]}"/>'
          + s.text(x0 + 34, 153, "FOUNDER, LLMSLIM  ·  AI ENGINEER", "mono-m", 13, t["accent"], ls=2.4)
          + "</g>")
    s.add(f'<g class="rv" style="animation-delay:.3s">'
          + s.text(x0 - 4, 268, "Yashvardhan", "serif", 124, ink, ls=-2.5) + "</g>")
    w2 = measure("Thanvi", "serif-i", 124, -2.5)
    s.add(f'<g class="rv" style="animation-delay:.45s">'
          + s.text(x0 - 2, 378, "Thanvi", "serif-i", 124, ink, ls=-2.5)
          + f'<circle cx="{f(x0 + w2 + 12)}" cy="366" r="9" fill="{t["accent"]}"/>' + "</g>")

    # voice line (his own words, from yashvardhan.tech)
    lines = ["I make tools I want to use. Sometimes that means a smaller",
             "LLM prompt. Sometimes it means helping a farmer decide better."]
    s.add(f'<g class="rv" style="animation-delay:.65s">'
          + "".join(s.text(x0, 438 + i * 30, ln, "sans", 19.5, body) for i, ln in enumerate(lines))
          + "</g>")

    # chips
    cx = x0
    chips = HERO_CHIPS
    s.add('<g class="rv" style="animation-delay:.8s">')
    for c in chips:
        cx += pill(s, cx, 486, c, "mono", 12.5, pad_x=13, h=30, ls=.4,
                   fill=("rgba(255,255,255,.03)" if dark else "rgba(255,255,255,.5)"),
                   stroke=(t["line2"] if dark else "rgba(26,22,21,.14)"), color=body) + 8
    s.add("</g>")

    # globe
    token_sphere(s, 905, 290, 172, delay_in=.55)
    s.add(f'<g class="fd" style="animation-delay:1.4s">'
          + s.text(905, 516, "CONTEXT, COMPRESSED", "mono", 11, muted, anchor="middle", ls=3)
          + "</g>")

    # ticker band
    band_y = H - 64
    s.add(f'<rect x="0" y="{band_y}" width="{W}" height="64" fill="{"rgba(255,255,255,.02)" if dark else "rgba(255,255,255,.38)"}"/>'
          f'<line x1="0" y1="{band_y}" x2="{W}" y2="{band_y}" stroke="{t["line"] if dark else "rgba(26,22,21,.10)"}"/>')
    live = load_live()
    ticker(s, band_y, 64, [x for x in (fill(it, live) for it in TICKER) if x])
    s.add("</g>")
    if dark:
        s.add(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="30" fill="none" stroke="{t["line"]}"/>')
    return s


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def mix(c1: str, c2: str, k: float) -> str:
    """Blend two hex colours, k=0 -> c1, k=1 -> c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * k):02X}" for x, y in zip(a, b))


def reveal_css(s: Svg):
    s.style(
        f".rv{{animation:rv 1s {EASE} both}}"
        "@keyframes rv{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}"
        ".fd{animation:fd 1.1s ease both}@keyframes fd{from{opacity:0}to{opacity:1}}"
    )


def card_bg(s: Svg, x, y, w, h, r=26, glow=False):
    t = s.t
    s.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{r}" fill="{t["surface"]}" '
          f'stroke="{t["line"]}"/>')
    if glow and t["name"] == "dark":
        gid = f"glow{int(x)}{int(y)}"
        s.defs_add(f'<radialGradient id="{gid}" cx="0.85" cy="0" r="0.9">'
                   f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity=".10"/>'
                   f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>')
        s.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{r}" fill="url(#{gid})"/>')


# ---------------------------------------------------------------------------
# Section headers
# ---------------------------------------------------------------------------

HEADERS = {
    "h-building": ("01", "NOW BUILDING", [("Smaller context, ", "serif"), ("better", "serif-i"), (" answers.", "serif")],
                   "LLMSLIM · MIT · PYPI"),
    "h-work": ("02", "SELECTED WORK", [("Things I've ", "serif"), ("built", "serif-i"), (".", "serif")],
               "2026 HACKATHON SEASON"),
    "h-oss": ("03", "OPEN SOURCE", [("Pull requests to the tools ", "serif"), ("I use", "serif-i"), (".", "serif")],
              "UPDATED AUTOMATICALLY"),
    "h-proud": ("04", "RECOGNITION", [("A few ", "serif"), ("proud", "serif-i"), (" moments.", "serif")], ""),
    "h-path": ("05", "EXPERIENCE", [("Where I've worked ", "serif"), ("and led", "serif-i"), (".", "serif")], ""),
    "h-activity": ("06", "ACTIVITY", [("Shipping, ", "serif"), ("most", "serif-i"), (" days.", "serif")],
                   "LAST 12 MONTHS · 3D"),
    "h-tools": ("07", "TOOLBOX", [("On my ", "serif"), ("workbench", "serif-i"), (".", "serif")], ""),
}


def section_header(theme, num, eyebrow, runs, note):
    W, H = 1200, 132
    t = theme
    title = "".join(r[0] for r in runs)
    s = Svg(W, H, t, f"{num} {eyebrow.title()}: {title}")
    s.style(f".ln{{transform-box:fill-box;transform-origin:left center;"
            f"animation:ln 1.6s {EASE} .05s both}}@keyframes ln{{from{{transform:scaleX(0)}}to{{transform:none}}}}")
    reveal_css(s)
    s.add(f'<rect class="ln" x="0" y="14" width="{W}" height="1" fill="{t["line2"]}"/>')
    s.add(f'<rect class="ln" x="0" y="13" width="64" height="3" fill="{t["accent"]}"/>')
    s.add('<g class="fd" style="animation-delay:.15s">'
          + s.tspan_text(0, 52, [(num, "mono-m", t["accent"]), ("  /  ", "mono", t["faint"]),
                                 (eyebrow, "mono-m", t["muted"])], size=13, attrs=' letter-spacing="2.4"')
          + (s.text(W, 52, note, "mono", 12, t["muted"], anchor="end", ls=2) if note else "")
          + "</g>")
    s.add('<g class="rv" style="animation-delay:.25s">'
          + s.tspan_text(-2, 116, [(txt, font, t["ink"]) for txt, font in runs], size=58,
                         attrs=' letter-spacing="-1.2"')
          + "</g>")
    return s


# ---------------------------------------------------------------------------
# Link pills
# ---------------------------------------------------------------------------



def link_pill(theme, label, arrow, primary):
    t = theme
    size, h, pad = 17, 52, 24
    tw = measure(label, "sans-m", size) + 10 + measure(arrow, "sans-m", size)
    W = round(tw + pad * 2)
    s = Svg(W, h, t, label)
    if primary:
        fill, stroke, color, ac = t["accent"], t["accent"], t["on_accent"], t["on_accent"]
    else:
        fill, stroke, color, ac = t["surface"], t["line2"], t["ink"], t["accent"]
    s.add(f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="{(h - 1) / 2}" fill="{fill}" stroke="{stroke}"/>')
    s.add(s.text(pad, h / 2 + size * .36, label, "sans-m", size, color))
    s.add(s.text(W - pad, h / 2 + size * .36, arrow, "sans-m", size, ac, anchor="end"))
    return s


# ---------------------------------------------------------------------------
# LLMSlim feature card
# ---------------------------------------------------------------------------

def iso(x, y, z, ox, oy, c=0.866, sn=0.5):
    return ox + (x - y) * c, oy + (x + y) * sn - z


def slab(ox, oy, S, z, h, top, left, right):
    P = lambda x, y, zz: iso(x, y, zz, ox, oy)
    pts = lambda arr: " ".join(f"{f(a)},{f(b)}" for a, b in arr)
    zt = z + h
    t_ = [P(0, 0, zt), P(S, 0, zt), P(S, S, zt), P(0, S, zt)]
    r_ = [P(S, 0, zt), P(S, S, zt), P(S, S, z), P(S, 0, z)]
    l_ = [P(0, S, zt), P(S, S, zt), P(S, S, z), P(0, S, z)]
    return (f'<polygon points="{pts(l_)}" fill="{left}"/><polygon points="{pts(r_)}" fill="{right}"/>'
            f'<polygon points="{pts(t_)}" fill="{top}"/>')


def llmslim_card(theme):
    W, H = 1200, 820
    t = theme
    live = load_live()
    dark = t["name"] == "dark"
    s = Svg(W, H, t, "LLMSlim: the context layer for production AI agents",
            "Open source Python library. pip install llmslim. "
            + ", ".join(f"{big} {l1} ({l2})" for big, l1, l2 in LLMSLIM["stats"]) + ".")
    reveal_css(s)
    card_bg(s, 0, 0, W, H, r=30, glow=True)
    ink, body, muted = t["ink"], t["body"], t["muted"]
    x0 = 56

    s.add('<g class="rv" style="animation-delay:.1s">'
          + s.text(x0, 76, fill(LLMSLIM["eyebrow"], live) or "OPEN SOURCE  ·  MIT", "mono-m", 13, t["accent"],
                   ls=2.4) + "</g>")
    s.add('<g class="rv" style="animation-delay:.2s">'
          + s.text(x0 - 4, 176, "LLMSlim", "serif", 112, ink, ls=-2.5) + "</g>")
    s.add('<g class="rv" style="animation-delay:.3s">'
          + s.tspan_text(x0, 228, [("The context layer for ", "sans-m", ink), ("production AI agents.", "sans-m", ink)],
                         size=24) + "</g>")
    lines = wrap(LLMSLIM["about"], "sans", 18.5, 520)
    s.add('<g class="rv" style="animation-delay:.4s">'
          + "".join(s.text(x0, 278 + i * 29, ln, "sans", 18.5, body) for i, ln in enumerate(lines)) + "</g>")

    # terminal line
    ty = 278 + len(lines) * 29 + 30
    cmd = "pip install llmslim"
    cw = measure("$ " + cmd, "mono-m", 17) + 64
    s.style("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.cur{animation:blink 1.1s steps(1) infinite}")
    s.add(f'<g class="rv" style="animation-delay:.5s">'
          f'<rect x="{x0}" y="{ty}" width="{f(cw)}" height="54" rx="14" fill="{t["bg"] if dark else "#FFFFFF"}" stroke="{t["line2"]}"/>'
          + s.tspan_text(x0 + 22, ty + 33, [("$ ", "mono-m", t["accent"]), (cmd, "mono-m", ink)], size=17)
          + f'<rect class="cur" x="{f(x0 + 22 + measure("$ " + cmd, "mono-m", 17) + 4)}" y="{ty + 18}" width="9" height="20" fill="{t["accent"]}"/>'
          + "</g>")
    s.add('<g class="fd" style="animation-delay:.7s">'
          + s.text(x0, ty + 90, LLMSLIM["facts"], "mono", 11.5,
                   muted, ls=1.4) + "</g>")
    runs = []
    dl = live.get("llmslim", {}).get("downloads_week")
    if dl:
        runs.append((f"{dl:,} DOWNLOADS LAST WEEK", "mono", body))
    names = [x["name"].upper() for x in live.get("listed_in", [])]
    if names:
        runs += [("  ·  " if runs else "", "mono", t["faint"]), ("LISTED IN " + ", ".join(names), "mono", t["accent"])]
    if runs:
        s.add('<g class="fd" style="animation-delay:.8s">'
              + s.tspan_text(x0, ty + 113, [r for r in runs if r[0]], size=11.5, attrs=' letter-spacing="1.4"') + "</g>")

    # isometric compression animation
    S, gap, h = 150, 15, 9
    n = 14
    kept = [2, 6, 11]
    ox, oy = 870, 318
    c_top, c_l, c_r = ("#3D3530", "#211C19", "#2D2723") if dark else ("#FFFFFF", "#DDD3CA", "#ECE4DD")
    a_top, a_l, a_r = t["accent"], mix(t["accent"], "#000000", .42), mix(t["accent"], "#000000", .22)
    edge = t["line2"]
    css, slabs = [], []
    T = 9
    for i in range(n):
        z = i * gap
        if i in kept:
            j = kept.index(i)
            dy = (z - j * gap)  # how far it falls (screen units, down = +)
            css.append(f"@keyframes k{i}{{0%,22%{{transform:none}}48%,82%{{transform:translateY({f(dy)}px)}}"
                       f"96%,100%{{transform:none}}}}.k{i}{{animation:k{i} {T}s {EASE} infinite}}")
            slabs.append(f'<g class="k{i}">{slab(ox, oy, S, z, h, a_top, a_l, a_r)}</g>')
        else:
            st = 18 + i * 1.2
            css.append(f"@keyframes k{i}{{0%,{f(st)}%{{transform:none;opacity:1}}{f(st + 16)}%,84%{{transform:translate(70px,-34px);opacity:0}}"
                       f"97%,100%{{transform:none;opacity:1}}}}.k{i}{{animation:k{i} {T}s {EASE} infinite}}")
            slabs.append(f'<g class="k{i}">{slab(ox, oy, S, z, h, c_top, c_l, c_r)}</g>')
    s.style("".join(css))
    # floor shadow + outline
    P = lambda x, y, z: iso(x, y, z, ox, oy)
    fl = [P(-14, -14, 0), P(S + 14, -14, 0), P(S + 14, S + 14, 0), P(-14, S + 14, 0)]
    s.add(f'<polygon points="{" ".join(f"{f(a)},{f(b)}" for a, b in fl)}" fill="none" stroke="{edge}" stroke-dasharray="3 5"/>')
    s.add(f'<g class="fd" style="animation-delay:.6s">{"".join(slabs)}</g>')
    # labels synced with the loop
    s.style(f"@keyframes lin{{0%,24%{{opacity:1}}34%,86%{{opacity:0}}96%,100%{{opacity:1}}}}"
            f"@keyframes lout{{0%,44%{{opacity:0}}54%,82%{{opacity:1}}92%,100%{{opacity:0}}}}"
            f".lin{{animation:lin {T}s linear infinite}}.lout{{opacity:0;animation:lout {T}s linear infinite}}")
    lx = ox + S * .866 + 22
    ty_in = oy + S * .5 - (n - 1) * gap - h
    ty_out = oy + S * .5 - (len(kept) - 1) * gap - h
    s.add(f'<g class="lin"><line x1="{f(lx - 16)}" y1="{f(ty_in)}" x2="{f(lx + 6)}" y2="{f(ty_in)}" stroke="{muted}"/>'
          + s.text(lx + 14, ty_in + 4, LLMSLIM["tokens_in"], "mono-m", 22, ink)
          + s.text(lx + 14, ty_in + 26, "TOKENS IN", "mono", 11, muted, ls=2) + "</g>")
    s.add(f'<g class="lout"><line x1="{f(lx - 16)}" y1="{f(ty_out)}" x2="{f(lx + 6)}" y2="{f(ty_out)}" stroke="{t["accent"]}"/>'
          + s.text(lx + 14, ty_out + 4, LLMSLIM["tokens_out"], "mono-m", 22, t["accent"])
          + s.text(lx + 14, ty_out + 26, "TOKENS SENT", "mono", 11, muted, ls=2) + "</g>")

    # stats band
    by = 560
    s.add(f'<line x1="{x0}" y1="{by}" x2="{W - x0}" y2="{by}" stroke="{t["line"]}"/>')
    stats = LLMSLIM["stats"]
    cw = (W - 2 * x0) / 4
    for i, (big, l1, l2) in enumerate(stats):
        x = x0 + i * cw
        if i:
            s.add(f'<line x1="{f(x - 14)}" y1="{by + 26}" x2="{f(x - 14)}" y2="{by + 128}" stroke="{t["line"]}"/>')
        s.add(f'<g class="rv" style="animation-delay:{.8 + i * .1:.1f}s">'
              + s.text(x, by + 82, big, "serif", 62, ink, ls=-1)
              + s.text(x + 2, by + 112, l1, "sans-m", 15.5, body)
              + s.text(x + 2, by + 134, l2, "mono", 11.5, muted, ls=.6) + "</g>")

    # programs
    py_ = 746
    s.add(f'<line x1="{x0}" y1="712" x2="{W - x0}" y2="712" stroke="{t["line"]}"/>')
    progs = LLMSLIM["programs"]
    label = f"IN {len(progs)} STARTUP PROGRAMS"
    s.add('<g class="fd" style="animation-delay:1.2s">' + s.text(x0, py_, label, "mono-m", 12, t["accent"], ls=2.2))
    py_ += 34
    px = x0
    for i, p in enumerate(progs):
        s.add(s.text(px, py_, p, "sans-m", 15, body))
        px += measure(p, "sans-m", 15)
        if i < len(progs) - 1:
            s.add(f'<circle cx="{f(px + 8)}" cy="{py_ - 5}" r="1.6" fill="{t["faint"]}"/>')
            px += 16
    s.add("</g>")
    return s


# ---------------------------------------------------------------------------
# Project cards
# ---------------------------------------------------------------------------



def glyph(s: Svg, kind, gx, gy, uid):
    """84x84 animated line glyph, one per project."""
    t = s.t
    a, ln, fa = t["accent"], t["line2"], t["faint"]
    out = []
    if kind == "field":
        css = (f"@keyframes sc{uid}{{0%{{transform:translateX(0)}}100%{{transform:translateX(84px)}}}}"
               f".sc{uid}{{animation:sc{uid} 3.6s linear infinite}}"
               f"@keyframes hv{uid}{{0%,100%{{fill:{fa}}}6%{{fill:{a}}}40%{{fill:{fa}}}}}")
        for c in range(6):
            for r in range(5):
                cx, cy = gx + 10 + c * 13, gy + 16 + r * 13
                css += ""
                out.append(f'<rect x="{cx - 3}" y="{cy - 3}" width="6" height="6" rx="1.5" fill="{fa}" '
                           f'style="animation:hv{uid} 3.6s linear {c * .6:.1f}s infinite"/>')
        s.style(css)
        s.defs_add(f'<clipPath id="gc{uid}"><rect x="{gx}" y="{gy}" width="84" height="84"/></clipPath>')
        out.append(f'<g clip-path="url(#gc{uid})"><rect class="sc{uid}" x="{gx - 2}" y="{gy + 4}" width="2" height="76" fill="{a}"/></g>')
    elif kind == "trace":
        def wave(seed, amp, spike):
            rnd = random.Random(seed)
            pts, x = [], 0
            while x <= 168:
                y = 0 if x % 84 not in range(38, 50) else (spike if x % 84 == 44 else -spike * .5)
                pts.append(f"{x},{f(y + rnd.uniform(-amp, amp))}")
                x += 4
            return " ".join(pts)
        s.style(f"@keyframes tr{uid}{{to{{transform:translateX(-84px)}}}}.tr{uid}{{animation:tr{uid} 3.2s linear infinite}}")
        s.defs_add(f'<clipPath id="gc{uid}"><rect x="{gx}" y="{gy}" width="84" height="84"/></clipPath>')
        out.append(f'<g clip-path="url(#gc{uid})"><g class="tr{uid}">'
                   f'<polyline transform="translate({gx} {gy + 30})" points="{wave(1, 2.5, 10)}" fill="none" stroke="{fa}" stroke-width="1.6"/>'
                   f'<polyline transform="translate({gx} {gy + 58})" points="{wave(2, 2.5, 22)}" fill="none" stroke="{a}" stroke-width="1.8"/>'
                   f"</g></g>")
        out.append(f'<line x1="{gx}" y1="{gy + 44}" x2="{gx + 84}" y2="{gy + 44}" stroke="{ln}" stroke-dasharray="2 4"/>')
    elif kind == "twin":
        s.style(f"@keyframes tw{uid}{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.14)}}}}"
                f".tw{uid}{{transform-box:fill-box;transform-origin:center;animation:tw{uid} 2.8s ease-in-out infinite}}"
                f"@keyframes cv{uid}{{to{{stroke-dashoffset:-40}}}}.cv{uid}{{animation:cv{uid} 2.2s linear infinite}}")
        out.append(f'<circle cx="{gx + 22}" cy="{gy + 42}" r="18" fill="none" stroke="{fa}" stroke-width="1.6"/>'
                   f'<circle class="tw{uid}" cx="{gx + 62}" cy="{gy + 42}" r="18" fill="none" stroke="{a}" stroke-width="1.6" stroke-dasharray="3 3"/>'
                   f'<path class="cv{uid}" d="M{gx + 10} {gy + 44} q6 -14 12 0 t12 0 t12 0 t12 0 t12 0 t12 0" fill="none" stroke="{a}" stroke-width="1.6" stroke-dasharray="6 4"/>'
                   f'<line x1="{gx + 42}" y1="{gy + 14}" x2="{gx + 42}" y2="{gy + 70}" stroke="{ln}" stroke-dasharray="2 3"/>')
    elif kind == "merkle":
        nodes = {"r": (42, 14), "m1": (22, 42), "m2": (62, 42),
                 "l1": (12, 70), "l2": (32, 70), "l3": (52, 70), "l4": (72, 70)}
        edges = [("r", "m1"), ("r", "m2"), ("m1", "l1"), ("m1", "l2"), ("m2", "l3"), ("m2", "l4")]
        s.style(f"@keyframes mk{uid}{{0%,100%{{fill:{t['surface']};stroke:{fa}}}12%,55%{{fill:{a};stroke:{a}}}}}")
        for p, q in edges:
            (x1, y1), (x2, y2) = nodes[p], nodes[q]
            out.append(f'<line x1="{gx + x1}" y1="{gy + y1}" x2="{gx + x2}" y2="{gy + y2}" stroke="{ln}" stroke-width="1.4"/>')
        delays = {"l1": 0, "l2": .2, "l3": .4, "l4": .6, "m1": .9, "m2": 1.1, "r": 1.5}
        for k, (x, y) in nodes.items():
            sz = 9 if k == "r" else 7
            out.append(f'<rect x="{gx + x - sz / 2}" y="{gy + y - sz / 2}" width="{sz}" height="{sz}" rx="1.5" '
                       f'fill="{t["surface"]}" stroke="{fa}" stroke-width="1.4" '
                       f'style="animation:mk{uid} 4s ease {delays[k]}s infinite"/>')
    elif kind == "bridge":
        arc = f"M{gx + 6} {gy + 58} Q{gx + 42} {gy + 4} {gx + 78} {gy + 58}"
        out.append(f'<path d="{arc}" fill="none" stroke="{fa}" stroke-width="1.6"/>'
                   f'<line x1="{gx}" y1="{gy + 58}" x2="{gx + 84}" y2="{gy + 58}" stroke="{fa}" stroke-width="1.6"/>')
        for i in range(1, 8):
            x = gx + 6 + i * 9
            yy = gy + 58 - (1 - ((i * 9 - 36) / 36) ** 2) * 27
            out.append(f'<line x1="{f(x)}" y1="{f(yy)}" x2="{f(x)}" y2="{gy + 58}" stroke="{ln}" stroke-width="1"/>')
        out.append(f'<circle r="4" fill="{a}"><animateMotion dur="3s" repeatCount="indefinite" path="{arc}" '
                   f'keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></circle>')
    elif kind == "pulse":
        house = f"M{gx + 8} {gy + 40} L{gx + 42} {gy + 10} L{gx + 76} {gy + 40} L{gx + 76} {gy + 76} L{gx + 8} {gy + 76} Z"
        ecg = (f"M{gx + 14} {gy + 54} L{gx + 30} {gy + 54} L{gx + 35} {gy + 46} L{gx + 40} {gy + 64} "
               f"L{gx + 46} {gy + 34} L{gx + 51} {gy + 58} L{gx + 55} {gy + 54} L{gx + 70} {gy + 54}")
        s.style(f"@keyframes ec{uid}{{0%{{stroke-dashoffset:120}}60%,100%{{stroke-dashoffset:0}}}}"
                f".ec{uid}{{stroke-dasharray:120;animation:ec{uid} 2.4s ease-in-out infinite}}")
        out.append(f'<path d="{house}" fill="none" stroke="{fa}" stroke-width="1.6" stroke-linejoin="round"/>'
                   f'<path class="ec{uid}" d="{ecg}" fill="none" stroke="{a}" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round"/>')
    s.add("".join(out))


def project_card(theme, p, idx):
    W, H = 590, 400
    t = theme
    s = Svg(W, H, t, f"{p['name']}: {p['desc']}")
    reveal_css(s)
    card_bg(s, 0, 0, W, H, r=26)
    pad = 40
    s.add('<g class="fd" style="animation-delay:.1s">'
          + s.text(pad, 58, f"{idx:02d}", "mono-m", 12.5, t["muted"], ls=2)
          + s.text(pad + 34, 58, p["tag"], "mono-m", 12.5, t["accent"], ls=1.8) + "</g>")
    glyph(s, p["glyph"], W - pad - 84, 30, p["key"][:3])
    s.add('<g class="rv" style="animation-delay:.15s">'
          + s.text(pad - 2, 158, p["name"], "serif", 54, t["ink"], ls=-1) + "</g>")
    lines = wrap(p["desc"], "sans", 17.5, W - pad * 2)[:4]
    s.add('<g class="rv" style="animation-delay:.25s">'
          + "".join(s.text(pad, 200 + i * 27, ln, "sans", 17.5, t["body"]) for i, ln in enumerate(lines)) + "</g>")
    # bottom row
    by = H - 70
    s.add(f'<line x1="{pad}" y1="{by - 16}" x2="{W - pad}" y2="{by - 16}" stroke="{t["line"]}"/>')
    x = pad
    s.add('<g class="fd" style="animation-delay:.4s">')
    for st in p["stack"]:
        x += pill(s, x, by, st, "mono", 12, pad_x=11, h=28, ls=.3, fill="none", stroke=t["line2"], color=t["muted"]) + 7
    label = "LIVE + SOURCE" if p["live"] else "SOURCE"
    lw = measure(label, "mono-m", 11.5, 1.6)
    ax = W - pad
    s.add(s.text(ax - 40, by + 18.5, label, "mono-m", 11.5, t["muted"], anchor="end", ls=1.6))
    s.add(f'<circle cx="{ax - 16}" cy="{by + 14}" r="16" fill="{t["accent"]}"/>'
          + s.text(ax - 16, by + 20, "↗", "sans-m", 16, t["on_accent"], anchor="middle"))
    s.add("</g>")
    _ = lw
    return s


def fresh_card(theme, item, idx):
    """Auto-generated card for a brand-new public repo (data from refresh.py)."""
    W, H = 590, 312
    t = theme
    s = Svg(W, H, t, f"{item['name']}: {item['desc']}")
    reveal_css(s)
    card_bg(s, 0, 0, W, H, r=26)
    pad = 40
    import datetime as _dt
    when = "NEW  ·  " + _dt.date.fromisoformat(item["created"]).strftime("%d %b %Y").upper()
    ww = measure(when, "mono", 11.5, 1.6)
    tag = (item.get("tag") or "New repository").upper()
    while " " in tag and measure(tag, "mono-m", 12, 1.8) > W - pad * 2 - ww - 40:
        tag = tag.rsplit(" ", 1)[0].rstrip(" ,:;(")
    s.style("@keyframes pulse{0%{transform:scale(1);opacity:.55}100%{transform:scale(3);opacity:0}}"
            ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.2s ease-out infinite}")
    s.add('<g class="fd" style="animation-delay:.1s">'
          + s.text(pad, 56, tag, "mono-m", 12, t["accent"], ls=1.8)
          + f'<circle class="pulse" cx="{f(W - pad - ww - 12)}" cy="52" r="3.5" fill="{t["accent"]}"/>'
          + f'<circle cx="{f(W - pad - ww - 12)}" cy="52" r="3.5" fill="{t["accent"]}"/>'
          + s.text(W - pad, 56, when, "mono", 11.5, t["muted"], anchor="end", ls=1.6) + "</g>")
    s.add('<g class="rv" style="animation-delay:.15s">'
          + s.text(pad - 2, 122, item["name"], "serif", 46, t["ink"], ls=-.8) + "</g>")
    lines = wrap(item["desc"], "sans", 16.5, W - pad * 2)
    if len(lines) > 3:
        lines = lines[:3]
        while measure(lines[2] + "...", "sans", 16.5) > W - pad * 2:
            lines[2] = lines[2].rsplit(" ", 1)[0]
        lines[2] = lines[2].rstrip(",.;:") + "..."
    s.add('<g class="rv" style="animation-delay:.25s">'
          + "".join(s.text(pad, 160 + i * 25, ln, "sans", 16.5, t["body"]) for i, ln in enumerate(lines)) + "</g>")
    by = H - 62
    s.add(f'<line x1="{pad}" y1="{by - 16}" x2="{W - pad}" y2="{by - 16}" stroke="{t["line"]}"/>')
    x = pad
    s.add('<g class="fd" style="animation-delay:.4s">')
    for chip in [c for c in (item.get("language"), f"{item['stars']} stars" if item.get("stars") else "") if c]:
        x += pill(s, x, by, chip, "mono", 12, pad_x=11, h=28, ls=.3, fill="none", stroke=t["line2"], color=t["muted"]) + 7
    label = "LIVE + SOURCE" if item.get("homepage") else "SOURCE"
    ax = W - pad
    s.add(s.text(ax - 40, by + 18.5, label, "mono-m", 11.5, t["muted"], anchor="end", ls=1.6))
    s.add(f'<circle cx="{ax - 16}" cy="{by + 14}" r="16" fill="{t["accent"]}"/>'
          + s.text(ax - 16, by + 20, "↗", "sans-m", 16, t["on_accent"], anchor="middle") + "</g>")
    return s


def fresh_header(theme):
    W, H = 1200, 64
    t = theme
    s = Svg(W, H, t, "New on GitHub, picked up automatically")
    s.style(f".ln{{transform-box:fill-box;transform-origin:left center;"
            f"animation:ln 1.6s {EASE} .05s both}}@keyframes ln{{from{{transform:scaleX(0)}}to{{transform:none}}}}")
    s.add(f'<rect class="ln" x="0" y="14" width="{W}" height="1" fill="{t["line"]}"/>')
    s.add(s.tspan_text(0, 50, [("NEW ON GITHUB", "mono-m", t["accent"]), ("  ·  PICKED UP AUTOMATICALLY", "mono", t["muted"])],
                       size=12.5, attrs=' letter-spacing="2.2"'))
    s.add(s.text(W, 50, "LAST 60 DAYS", "mono", 12, t["muted"], anchor="end", ls=2))
    return s


# ---------------------------------------------------------------------------
# Recognition bento
# ---------------------------------------------------------------------------

def recognition(theme):
    W, gap = 1200, 16
    t = theme
    R = RECOGNITION
    tiles = R["tiles"]
    tile_rows = [tiles[i:i + 3] for i in range(0, len(tiles), 3)]
    rows = [300] + [206] * len(tile_rows)
    H = sum(rows) + gap * (len(rows) - 1)
    feat, side = R["feature"], R["side"]
    summary = "; ".join(["".join(x[0] for x in feat["title"]) + " (" + feat["eyebrow"].split("  ")[0] + ")",
                         f'{side["eyebrow"]} {side["title"]} {side["body"]}']
                        + [f"{b} {a}: {c}" for b, a, c in [(x[1], x[0], x[2]) for x in tiles]])
    s = Svg(W, H, t, "Recognition", summary)
    reveal_css(s)
    ink, body, muted, acc = t["ink"], t["body"], t["muted"], t["accent"]

    # feature tile
    aw = 776
    card_bg(s, 0, 0, aw, rows[0], glow=True)
    s.add('<g class="rv" style="animation-delay:.1s">'
          + s.text(36, 54, feat["eyebrow"], "mono-m", 12.5, acc, ls=2)
          + s.tspan_text(32, 134, [(txt, font, ink) for txt, font in feat["title"]], size=72,
                         attrs=' letter-spacing="-1.5"') + "</g>")
    lines = wrap(feat["body"], "sans", 17, aw - 72)[:3]
    s.add('<g class="rv" style="animation-delay:.2s">'
          + "".join(s.text(36, 180 + i * 26, ln, "sans", 17, body) for i, ln in enumerate(lines)) + "</g>")
    s.add('<g class="fd" style="animation-delay:.5s">'
          + s.text(36, rows[0] - 30, feat["foot"], "mono", 12, muted, ls=1.8) + "</g>")

    # side tile with an exoplanet transit and its light curve
    bx, bw = aw + gap, W - aw - gap
    card_bg(s, bx, 0, bw, rows[0])
    cx, cy = bx + bw - 96, 92
    s.style("@keyframes transit{0%{transform:translateX(-70px)}100%{transform:translateX(70px)}}"
            ".pl{animation:transit 5s linear infinite}"
            "@keyframes dip{0%,38%{transform:translateY(0)}46%,54%{transform:translateY(10px)}62%,100%{transform:translateY(0)}}"
            ".dp{animation:dip 5s ease-in-out infinite}")
    s.defs_add(f'<clipPath id="star"><circle cx="{cx}" cy="{cy}" r="40"/></clipPath>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="40" fill="{mix(acc, t["surface"], .25)}"/>'
          f'<circle cx="{cx}" cy="{cy}" r="52" fill="none" stroke="{t["line2"]}" stroke-dasharray="2 4"/>'
          f'<g clip-path="url(#star)"><circle class="pl" cx="{cx}" cy="{cy + 6}" r="9" fill="{t["surface"]}"/></g>')
    lx0, ly = bx + 36, 176
    s.add(f'<line x1="{lx0}" y1="{ly}" x2="{bx + bw - 36}" y2="{ly}" stroke="{t["line"]}"/>')
    s.add(f'<g class="dp"><circle cx="{f(lx0 + (bw - 72) / 2)}" cy="{ly}" r="3.5" fill="{acc}"/></g>')
    s.add('<g class="rv" style="animation-delay:.3s">'
          + s.text(bx + 36, 54, side["eyebrow"], "mono-m", 12.5, acc, ls=2)
          + s.text(bx + 34, 236, side["title"], "serif", 40, ink, ls=-.6)
          + s.text(bx + 34, 270, side["body"], "sans", 16, body) + "</g>")

    # tiles, three per row
    sw = (W - 2 * gap) / 3
    y = rows[0] + gap
    k = 0
    for ri, row in enumerate(tile_rows):
        for ci, (big, l1, l2) in enumerate(row):
            x = ci * (sw + gap)
            card_bg(s, x, y, sw, rows[ri + 1])
            s.add(f'<g class="rv" style="animation-delay:{.35 + k * .08:.2f}s">'
                  + s.text(x + 30, y + 96, big, "serif", 66, ink, ls=-1.2)
                  + f'<rect x="{f(x + 30)}" y="{y + 120}" width="26" height="2" fill="{acc}"/>'
                  + s.text(x + 30, y + 152, l1, "sans-m", 17, ink)
                  + s.text(x + 30, y + 176, l2, "sans", 14.5, muted) + "</g>")
            k += 1
        y += rows[ri + 1] + gap
    return s


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------



def experience(theme):
    W, H = 1200, 596
    t = theme
    s = Svg(W, H, t, "Experience",
            "DRDO SAG research intern 2026, founder of AMEYOR, Olinp Technologies intern 2025. AWS Student Builder "
            "Group Leader, GeeksforGeeks Campus Mantri, IIC Head, GDG coordinator, Google Gemini Student Ambassador.")
    reveal_css(s)
    ink, body, muted, acc = t["ink"], t["body"], t["muted"], t["accent"]
    gap = 16
    lw = 640
    card_bg(s, 0, 0, lw, H - 118)
    card_bg(s, lw + gap, 0, W - lw - gap, H - 118)
    card_bg(s, 0, H - 102, W, 102)

    # work timeline
    s.add(s.text(36, 52, "WORK", "mono-m", 12.5, acc, ls=2.4))
    s.style(f".tl{{transform-box:fill-box;transform-origin:top;animation:tl 1.6s {EASE} .2s both}}"
            "@keyframes tl{from{transform:scaleY(0)}to{transform:none}}")
    s.add(f'<rect class="tl" x="44" y="92" width="1.5" height="{(len(WORK) - 1) * 128}" fill="{t["line2"]}"/>')
    for i, (org, role, when, note) in enumerate(WORK):
        y = 96 + i * 128
        s.add(f'<g class="rv" style="animation-delay:{.25 + i * .15:.2f}s">'
              f'<circle cx="44.75" cy="{y - 4}" r="6" fill="{t["surface"]}" stroke="{acc}" stroke-width="2"/>'
              + s.text(72, y + 2, org, "sans-sb", 20, ink)
              + s.text(lw - 36, y + 2, when, "mono", 11.5, muted, anchor="end", ls=1.6)
              + s.text(72, y + 30, role, "sans", 16.5, body)
              + "".join(s.text(72, y + 58 + j * 23, ln, "sans", 15, muted)
                        for j, ln in enumerate(wrap(note, "sans", 15, lw - 120)[:2]))
              + "</g>")

    # leadership list
    x0 = lw + gap + 32
    rw = W - x0 - 32
    s.add(s.text(x0, 52, "LEADERSHIP & COMMUNITY", "mono-m", 12.5, acc, ls=2.4))
    for i, (org, role, when) in enumerate(LEAD):
        y = 100 + i * 54
        s.add(f'<g class="rv" style="animation-delay:{.3 + i * .07:.2f}s">'
              + s.text(x0, y, org, "sans-sb", 17, ink)
              + s.text(x0 + rw, y, when, "mono", 11, muted, anchor="end", ls=1.4)
              + s.text(x0, y + 23, role, "sans", 15, body)
              + (f'<line x1="{x0}" y1="{y + 39}" x2="{x0 + rw}" y2="{y + 39}" stroke="{t["line"]}"/>'
                 if i < len(LEAD) - 1 else "")
              + "</g>")

    # education strip
    ey = H - 102
    s.add('<g class="fd" style="animation-delay:.9s">'
          + s.text(36, ey + 44, "EDUCATION", "mono-m", 12.5, acc, ls=2.4)
          + s.tspan_text(36, ey + 76, [(EDUCATION["school"], "sans-sb", ink),
                                       ("   " + EDUCATION["degree"], "sans", body)], size=17)
          + s.text(W - 36, ey + 60, EDUCATION["score"], "serif", 44, ink, anchor="end")
          + s.text(W - 36 - measure(EDUCATION["score"], "serif", 44) - 12, ey + 60, EDUCATION["score_label"], "mono",
                   11.5, muted, anchor="end", ls=1.6)
          + s.text(W - 36, ey + 82, EDUCATION["years"], "mono", 11, muted, anchor="end", ls=1.6)
          + "</g>")
    return s


# ---------------------------------------------------------------------------
# Toolbox marquee
# ---------------------------------------------------------------------------



def toolbox(theme):
    W, H = 1200, 248
    t = theme
    s = Svg(W, H, t, "Toolbox", ", ".join(sum(TOOLS, [])))
    s.defs_add('<linearGradient id="fadeg" x1="0" x2="1" y1="0" y2="0">'
               '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/>'
               '<stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
               f'<mask id="fade"><rect width="{W}" height="{H}" fill="url(#fadeg)"/></mask>')
    rows = []
    for r, items in enumerate(TOOLS):
        y = 18 + r * 76
        xs, x = [], 0.0
        for it in items:
            xs.append(x)
            x += measure(it, "sans-m", 17) + 44 + 12
        loop = x
        g = []
        for rep in (0, 1, 2):
            for it, x0 in zip(items, xs):
                bx = x0 + rep * loop
                w = measure(it, "sans-m", 17) + 44
                hot = it in HOT_TOOLS
                g.append(f'<rect x="{f(bx)}" y="{y}" width="{f(w)}" height="52" rx="26" '
                         f'fill="{t["surface"]}" stroke="{t["accent"] if hot else t["line"]}"/>')
                g.append(s.text(bx + 22, y + 32, it, "sans-m", 17, t["ink"] if hot else t["body"]))
        dur = loop / (22 + r * 6)
        direction = "normal" if r % 2 == 0 else "reverse"
        s.style(f"@keyframes mq{r}{{from{{transform:translateX(0)}}to{{transform:translateX(-{f(loop)}px)}}}}"
                f".mq{r}{{animation:mq{r} {dur:.1f}s linear infinite {direction}}}")
        rows.append(f'<g class="mq{r}">{"".join(g)}</g>')
    s.add(f'<g mask="url(#fade)">{"".join(rows)}</g>')
    return s


# ---------------------------------------------------------------------------
# Contact / freelance card
# ---------------------------------------------------------------------------

def contact(theme):
    W, H = 1200, 404
    t = theme
    dark = t["name"] == "dark"
    s = Svg(W, H, t, "Available for freelance. Have something in mind? Let's build it.",
            "Python backends, retrieval systems, AI features and prototypes. Book a 30 minute call or email "
            "yashvt9404@gmail.com.")
    reveal_css(s)
    s.defs_add(f'<clipPath id="cc"><rect width="{W}" height="{H}" rx="30"/></clipPath>')
    if dark:
        s.defs_add('<radialGradient id="emb2" cx="0.1" cy="1.1" r="0.8">'
                   f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity=".22"/>'
                   f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>')
        bg = f'<rect width="{W}" height="{H}" fill="{t["surface"]}"/><rect width="{W}" height="{H}" fill="url(#emb2)"/>'
        ink, body, muted = t["ink"], t["body"], t["muted"]
    else:
        s.defs_add('<linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1">'
                   '<stop offset="0" stop-color="#EDDFD0"/><stop offset=".6" stop-color="#C9D6E4"/>'
                   '<stop offset="1" stop-color="#9CC1E7"/></linearGradient>')
        bg = f'<rect width="{W}" height="{H}" fill="url(#sky2)"/>'
        ink, body, muted = t["ink"], "#3A3431", "#5C5552"
    grain(s, "g2", opacity=0.08 if dark else 0.06)
    s.add(f'<g clip-path="url(#cc)">{bg}<rect width="{W}" height="{H}" filter="url(#g2)"/></g>')
    if dark:
        s.add(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="30" fill="none" stroke="{t["line"]}"/>')

    x0 = 56
    s.style("@keyframes pulse{0%{transform:scale(1);opacity:.55}100%{transform:scale(3.2);opacity:0}}"
            ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.2s ease-out infinite}")
    s.add('<g class="rv" style="animation-delay:.1s">'
          f'<circle cx="{x0 + 5}" cy="70" r="5" fill="{t["accent"]}" class="pulse"/>'
          f'<circle cx="{x0 + 5}" cy="70" r="5" fill="{t["accent"]}"/>'
          + s.text(x0 + 22, 75, "08  /  CONTACT  ·  AVAILABLE FOR FREELANCE", "mono-m", 13, t["accent"], ls=2.2)
          + "</g>")
    s.add('<g class="rv" style="animation-delay:.2s">'
          + s.text(x0 - 3, 178, "Have something in mind?", "serif", 78, ink, ls=-1.6) + "</g>")
    w = measure("Let's build it", "serif-i", 78, -1.6)
    s.add('<g class="rv" style="animation-delay:.32s">'
          + s.text(x0 - 3, 262, "Let's build it", "serif-i", 78, ink, ls=-1.6)
          + f'<circle cx="{f(x0 + w + 8)}" cy="252" r="7" fill="{t["accent"]}"/>' + "</g>")
    lines = wrap("Python backends, retrieval systems, AI features, and getting a prototype into someone's hands. "
                 "I usually reply within a day.", "sans", 18, 620)
    s.add('<g class="rv" style="animation-delay:.42s">'
          + "".join(s.text(x0, 316 + i * 28, ln, "sans", 18, body) for i, ln in enumerate(lines)) + "</g>")

    # right column: services + button
    rx = 820
    svc = ["PYTHON BACKENDS", "RAG + RETRIEVAL", "AI FEATURES", "PROTOTYPE TO PRODUCT"]
    for i, it in enumerate(svc):
        y = 128 + i * 40
        s.add(f'<g class="rv" style="animation-delay:{.4 + i * .08:.2f}s">'
              + s.text(rx, y, f"0{i + 1}", "mono", 12, muted, ls=1.6)
              + s.text(rx + 36, y, it, "mono-m", 13, ink, ls=1.8)
              + f'<line x1="{rx}" y1="{y + 15}" x2="{W - 56}" y2="{y + 15}" stroke="{t["line2"] if dark else "rgba(26,22,21,.12)"}"/>'
              + "</g>")
    label = "Book a 30 min call"
    bw = measure(label, "sans-m", 17) + 84
    by = 318
    s.add(f'<g class="rv" style="animation-delay:.8s">'
          f'<rect x="{rx}" y="{by}" width="{f(bw)}" height="56" rx="28" fill="{t["ink"]}"/>'
          + s.text(rx + 26, by + 34, label, "sans-m", 17, t["bg"] if dark else "#FFFFFF")
          + f'<circle cx="{f(rx + bw - 30)}" cy="{by + 28}" r="17" fill="{t["accent"]}"/>'
          + s.text(rx + bw - 30, by + 34, "↗", "sans-m", 16, t["on_accent"], anchor="middle")
          + "</g>")
    return s


BUILDERS = {
    "hero": hero,
    "llmslim": llmslim_card,
    "recognition": recognition,
    "experience": experience,
    "toolbox": toolbox,
    "contact": contact,
}


def main(only: list[str] | None = None):
    jobs = dict(BUILDERS)
    for key, (num, eb, runs, note) in HEADERS.items():
        jobs[key] = (lambda th, a=(num, eb, runs, note): section_header(th, *a))
    for _, key, label, arrow, primary in LINK_ITEMS:
        jobs[key] = (lambda th, a=(label, arrow, primary): link_pill(th, *a))
    for i, p in enumerate(PROJECTS, 1):
        jobs[f"p-{p['key']}"] = (lambda th, a=(p, i): project_card(th, *a))
    fresh = load_live().get("fresh", [])
    if fresh:
        jobs["h-fresh"] = fresh_header
    for i, item in enumerate(fresh, 1):
        jobs[f"f-{i}"] = (lambda th, a=(item, i): fresh_card(th, *a))
    if not only:  # drop cards for repos that aged out of the fresh list
        for old in ASSETS.glob("f-*-*.svg"):
            if int(old.name.split("-")[1]) > len(fresh):
                old.unlink()
    for name, fn in jobs.items():
        if only and name not in only and not any(name.startswith(o.rstrip("*")) for o in only if o.endswith("*")):
            continue
        for tname, theme in THEMES.items():
            svg = fn(theme)
            out = ASSETS / f"{name}-{tname}.svg"
            svg.save(out)
            print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1024:.1f} KB  {svg.w}x{svg.h}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
