"""Tiny SVG toolkit for the profile README.

Every SVG embeds its own font subset (only the glyphs it uses), so the
images render the same on github.com, the mobile app and anywhere else an
<img> can't fetch web fonts.
"""
from __future__ import annotations

import base64
import io
import math
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONT_DIR = Path(__file__).parent / "fonts"

# key: (file, wght instance or None, css family, css weight, css style)
FONTS = {
    "serif": ("InstrumentSerif-Regular.ttf", None, "Instrument Serif", 400, "normal"),
    "serif-i": ("InstrumentSerif-Italic.ttf", None, "Instrument Serif", 400, "italic"),
    "sans": ("Geist-Variable.ttf", 400, "Geist", 400, "normal"),
    "sans-m": ("Geist-Variable.ttf", 500, "Geist", 500, "normal"),
    "sans-sb": ("Geist-Variable.ttf", 600, "Geist", 600, "normal"),
    "sans-b": ("Geist-Variable.ttf", 700, "Geist", 700, "normal"),
    "mono": ("GeistMono-Variable.ttf", 400, "Geist Mono", 400, "normal"),
    "mono-m": ("GeistMono-Variable.ttf", 500, "Geist Mono", 500, "normal"),
}

THEMES = {
    # Monochrome, Geist-first, to match yashvardhan.tech. Orange is used sparingly.
    "dark": {
        "name": "dark",
        "bg": "#000000",
        "surface": "#0A0A0A",
        "surface2": "#111111",
        "line": "#1F1F1F",
        "line2": "#2E2E2E",
        "ink": "#EDEDED",
        "body": "#A1A1A1",
        "muted": "#7C7C7C",
        "faint": "#4D4D4D",
        "accent": "#FF7A3D",
        "accent_soft": "#FFB18A",
        "on_accent": "#0A0A0A",
        "dot": "#EDEDED",
        "button": "#EDEDED",
        "on_button": "#0A0A0A",
    },
    "light": {
        "name": "light",
        "bg": "#FFFFFF",
        "surface": "#FFFFFF",
        "surface2": "#FAFAFA",
        "line": "#EAEAEA",
        "line2": "#DEDEDE",
        "ink": "#0A0A0A",
        "body": "#4D4D4D",
        "muted": "#6F6F6F",
        "faint": "#B3B3B3",
        "accent": "#E8601F",
        "accent_soft": "#F4A47C",
        "on_accent": "#FFFFFF",
        "dot": "#0A0A0A",
        "button": "#0A0A0A",
        "on_button": "#FFFFFF",
    },
}


@lru_cache(maxsize=None)
def _font(key: str) -> TTFont:
    file, wght, *_ = FONTS[key]
    font = TTFont(FONT_DIR / file, recalcTimestamp=False)
    if wght is not None and "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": wght}, updateFontNames=False)
    return font


@lru_cache(maxsize=None)
def _metrics(key: str):
    font = _font(key)
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    return cmap, hmtx, upm


def measure(text: str, font: str, size: float, ls: float = 0.0) -> float:
    """Advance width of `text` in px (no kerning; close enough for layout)."""
    cmap, hmtx, upm = _metrics(font)
    w = 0
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            g = cmap.get(ord("?"))
        w += hmtx[g][0]
    return w * size / upm + ls * max(len(text) - 1, 0)


def wrap(text: str, font: str, size: float, max_w: float) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if measure(trial, font, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _subset_b64(key: str, chars: set[str]) -> str:
    font = _font(key)
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    f = TTFont(buf, recalcTimestamp=False)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "tnum"]
    opts.hinting = False
    opts.desubroutinize = True
    opts.name_IDs = []
    opts.notdef_outline = False
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)) + " ")
    sub.subset(f)
    out = io.BytesIO()
    f.flavor = "woff2"
    f.save(out)
    return base64.b64encode(out.getvalue()).decode()


def f(x: float) -> str:
    """Compact number formatting for SVG attributes."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Svg:
    def __init__(self, w: int, h: int, theme: dict, title: str, desc: str = ""):
        self.w, self.h, self.t = w, h, theme
        self.title, self.desc = title, desc
        self.parts: list[str] = []
        self.defs: list[str] = []
        self.css: list[str] = []
        self.used: dict[str, set[str]] = defaultdict(set)

    # -- building blocks -------------------------------------------------
    def add(self, raw: str):
        self.parts.append(raw)

    def defs_add(self, raw: str):
        self.defs.append(raw)

    def style(self, css: str):
        self.css.append(css)

    def use_font(self, font: str, text: str):
        self.used[font].update(text)

    def text(self, x, y, s, font="sans", size=16, fill=None, anchor="start",
             ls=0.0, cls="", attrs="", opacity=None) -> str:
        self.use_font(font, s)
        fill = fill or self.t["ink"]
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        l = f' letter-spacing="{f(ls)}"' if ls else ""
        o = f' opacity="{f(opacity)}"' if opacity is not None else ""
        c = f"f-{font}" + (f" {cls}" if cls else "")
        return (f'<text x="{f(x)}" y="{f(y)}" class="{c}" font-size="{f(size)}" '
                f'fill="{fill}"{a}{l}{o}{attrs}>{escape(s)}</text>')

    def tspan_text(self, x, y, runs, size=16, anchor="start", cls="", attrs="") -> str:
        """runs: list of (text, font, fill). Single line, mixed fonts."""
        spans = []
        for s, font, fill in runs:
            self.use_font(font, s)
            spans.append(f'<tspan class="f-{font}" fill="{fill}">{escape(s)}</tspan>')
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        c = f' class="{cls}"' if cls else ""
        return f'<text x="{f(x)}" y="{f(y)}" font-size="{f(size)}"{a}{c}{attrs}>{"".join(spans)}</text>'

    # -- output ----------------------------------------------------------
    def font_css(self) -> str:
        rules = []
        for key, chars in sorted(self.used.items()):
            _, _, fam, wght, style = FONTS[key]
            b64 = _subset_b64(key, chars)
            rules.append(
                f"@font-face{{font-family:'{fam} {key}';src:url(data:font/woff2;base64,{b64}) "
                f"format('woff2');font-weight:{wght};font-style:{style}}}"
                f".f-{key}{{font-family:'{fam} {key}','{fam}',system-ui,sans-serif;"
                f"font-weight:{wght};font-style:{style}}}"
            )
        return "".join(rules)

    def render(self) -> str:
        css = self.font_css() + "".join(self.css)
        css += ("@media (prefers-reduced-motion:reduce){*,*::before,*::after{"
                "animation-duration:0s!important;animation-delay:0s!important;"
                "animation-iteration-count:1!important}}")
        title = escape(self.title)
        desc = f"<desc>{escape(self.desc)}</desc>" if self.desc else ""
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="t">'
            f'<title id="t">{title}</title>{desc}<style>{css}</style>{defs}'
            f'{"".join(self.parts)}</svg>'
        )

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")


# -- shared visual pieces ---------------------------------------------------

def rounded_frame(svg: Svg, x, y, w, h, r=28, fill=None, stroke=None, sw=1, extra=""):
    fill = fill or svg.t["surface"]
    s = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke else ""
    svg.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(r)}" fill="{fill}"{s}{extra}/>')


def grain(svg: Svg, fid="grain", opacity=0.06, freq=0.9):
    svg.defs_add(
        f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" stitchTiles="stitch"/>'
        f'<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 {opacity} 0"/>'
        f"</filter>"
    )


def pill(svg: Svg, x, y, label, font="mono", size=13, pad_x=14, h=30, ls=0.6,
         fill=None, stroke=None, color=None, dot=None, cls="") -> float:
    """Draws a pill and returns its width."""
    t = svg.t
    tw = measure(label, font, size, ls)
    dot_w = 16 if dot else 0
    w = tw + pad_x * 2 + dot_w
    st = f' stroke="{stroke or t["line2"]}" stroke-width="1"' if stroke is not False else ""
    c = f' class="{cls}"' if cls else ""
    out = [f"<g{c}>",
           f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{h}" rx="{h / 2}" fill="{fill or "none"}"{st}/>']
    if dot:
        out.append(f'<circle cx="{f(x + pad_x + 3)}" cy="{f(y + h / 2)}" r="3.5" fill="{dot}"/>')
    out.append(svg.text(x + pad_x + dot_w, y + h / 2 + size * 0.36, label, font, size,
                        color or t["body"], ls=ls))
    out.append("</g>")
    svg.add("".join(out))
    return w


def ease_css() -> str:
    return "cubic-bezier(.2,.7,.1,1)"


def sphere_points(n_rings=13, n_eq=34, lat_max=78):
    """Latitude rings for a dotted globe: (lat_rad, n_dots, ring_offset)."""
    rings = []
    for k in range(n_rings):
        lat = math.radians(-lat_max + 2 * lat_max * k / (n_rings - 1))
        n = max(4, round(n_eq * math.cos(lat)))
        rings.append((lat, n, (k * 0.61) % (2 * math.pi)))
    return rings


# -- images -------------------------------------------------------------------

def data_uri(path: Path) -> str:
    """Embed a local image so the SVG needs no network (GitHub serves SVGs as isolated images)."""
    path = Path(path)
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml",
            ".webp": "image/webp"}[path.suffix.lower()]
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def logo_tile(svg: "Svg", x, y, size, path: Path | None, label: str = "", r: float | None = None, uid: str = "") -> str:
    """A rounded-square logo tile. Falls back to a lettermark when no image exists."""
    t = svg.t
    r = size * 0.24 if r is None else r
    cid = f"lt{uid or abs(hash((x, y, size, str(path)))) % 10**8}"
    svg.defs_add(f'<clipPath id="{cid}"><rect x="{f(x)}" y="{f(y)}" width="{f(size)}" height="{f(size)}" rx="{f(r)}"/></clipPath>')
    border = f'<rect x="{f(x + .5)}" y="{f(y + .5)}" width="{f(size - 1)}" height="{f(size - 1)}" rx="{f(r)}" fill="none" stroke="{t["line2"]}"/>'
    if path and Path(path).exists():
        return (f'<g clip-path="url(#{cid})"><rect x="{f(x)}" y="{f(y)}" width="{f(size)}" height="{f(size)}" fill="#FFFFFF"/>'
                f'<image href="{data_uri(path)}" x="{f(x)}" y="{f(y)}" width="{f(size)}" height="{f(size)}" '
                f'preserveAspectRatio="xMidYMid slice"/></g>{border}')
    letters = "".join(w[0] for w in label.split()[:2]).upper() if " " in label else label[:4].upper()
    fs = size * (0.26 if len(letters) > 2 else 0.38)
    svg.use_font("mono-m", letters)
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(size)}" height="{f(size)}" rx="{f(r)}" fill="{t["surface2"]}"/>{border}'
            f'<text x="{f(x + size / 2)}" y="{f(y + size / 2 + fs * .36)}" class="f-mono-m" font-size="{f(fs)}" '
            f'fill="{t["ink"]}" text-anchor="middle" letter-spacing="{f(fs * .06)}">{escape(letters)}</text>')


def rich_lines(runs, size, max_w):
    """Wrap mixed-style runs [(text, font, fill)] into lines of runs."""
    words = []  # (word, font, fill, preceded by a space)
    gap = False  # did the text so far end with a space?
    for text, font, fill in runs:
        for i, w in enumerate(text.split(" ")):
            if w:
                words.append((w, font, fill, i > 0 or gap or not words))
                gap = False
            elif i > 0:
                gap = True
        gap = gap or text.endswith(" ")
    lines, cur, cur_w = [], [], 0.0
    for w, font, fill, spaced in words:
        sep = " " if (cur and spaced) else ""
        add = measure(sep + w, font, size)
        if cur and spaced and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w, sep = [], 0.0, ""
            add = measure(w, font, size)
        cur.append((sep + w, font, fill))
        cur_w += add
    if cur:
        lines.append(cur)
    return lines


def dot_grid(svg: "Svg", x, y, w, h, gap=14, r=1.0, opacity=.35, fade_cx=.75, fade_cy=.5, uid="dg"):
    """Subtle dot matrix that fades out radially, like the portfolio hero."""
    t = svg.t
    svg.defs_add(
        f'<pattern id="{uid}p" x="{f(x)}" y="{f(y)}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
        f'<circle cx="{gap / 2}" cy="{gap / 2}" r="{r}" fill="{t["dot"]}"/></pattern>'
        f'<radialGradient id="{uid}g" cx="{fade_cx}" cy="{fade_cy}" r=".6">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        f'</radialGradient><mask id="{uid}m"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="url(#{uid}g)"/></mask>')
    svg.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="url(#{uid}p)" mask="url(#{uid}m)" '
            f'opacity="{opacity}"/>')
