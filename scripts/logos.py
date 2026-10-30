"""Logo files used by the README visuals.

Every logo is stored as a square PNG in assets/logos/ and embedded into the SVGs at build time,
because GitHub renders README SVGs as isolated images that cannot load anything external.

* Organisations on GitHub: their official org avatar, fetched by refresh.py (gh-<owner>.png).
* Everything else: prepared once from the organisation's own site and committed here.
"""
from __future__ import annotations

import io
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "assets" / "logos"
SIZE = 112

# Named logos used by content.py (key -> file in assets/logos). Missing files fall back to a lettermark.
NAMED = {
    "llmslim": "llmslim.png", "krishyak": "krishyak.png", "ameyor": "ameyor.png", "mark": "mark.svg",
    "aws": "gh-aws.png", "google": "gh-google.png", "gdg": "gdg.png", "gfg": "gfg.svg", "oneplus": "gh-OnePlusOSS.png",
    "gssoc": "gssoc.png", "iic": "iic.png", "olinp": "olinp.png", "bit": "bit.png", "drdo": "drdo.png",
    "mybharat": "mybharat.png", "nasa": "gh-nasa.png", "iete": "iete.png", "producthunt": "gh-producthunt.png",
    "polaris": "gh-polaris-school-of-technology.png", "thoughtworks": "gh-thoughtworks.png", "sih": "sih.png",
    "hackerrank": "gh-hackerrank.png",
    # LLMSlim startup programs
    "openai": "gh-openai.png", "anthropic": "gh-anthropics.png", "mongodb": "gh-mongodb.png",
    "sarvam": "gh-sarvamai.png", "zoho": "gh-zoho.png", "auth0": "gh-auth0.png", "zendesk": "gh-zendesk.png",
    "mixpanel": "gh-mixpanel.png", "sentry": "gh-getsentry.png", "descope": "gh-descope.png",
    "pulumi": "gh-pulumi.png", "honeycomb": "gh-honeycombio.png", "exa": "gh-exa-labs.png", "neo4j": "gh-neo4j.png",
    "cartesia": "gh-cartesia-ai.png",
}


def path_for(key: str | None) -> Path | None:
    if not key:
        return None
    if key.startswith("gh:"):
        return LOGOS / f"gh-{key[3:]}.png"
    name = NAMED.get(key)
    return LOGOS / name if name else None


def square_png(data: bytes, mode: str = "cover", pad: float = .14, bg=(255, 255, 255, 255)) -> bytes:
    """Normalise any logo to a SIZE x SIZE PNG. 'contain' pads wide logos onto a white square."""
    from PIL import Image

    im = Image.open(io.BytesIO(data)).convert("RGBA")
    if mode == "contain":
        inner = int(SIZE * (1 - 2 * pad))
        im.thumbnail((inner, inner), Image.LANCZOS)
        canvas = Image.new("RGBA", (SIZE, SIZE), bg)
        canvas.alpha_composite(im, ((SIZE - im.width) // 2, (SIZE - im.height) // 2))
        im = canvas
    else:
        side = min(im.size)
        left, top = (im.width - side) // 2, (im.height - side) // 2
        im = im.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)
        flat = Image.new("RGBA", im.size, bg)
        flat.alpha_composite(im)
        im = flat
    out = io.BytesIO()
    im.convert("RGB").save(out, "PNG", optimize=True)
    return out.getvalue()


def fetch_avatar(owner: str, force: bool = False) -> Path | None:
    """Download a GitHub org/user avatar as a normalised PNG (cached in assets/logos)."""
    dest = LOGOS / f"gh-{owner}.png"
    if dest.exists() and not force:
        return dest
    try:
        req = urllib.request.Request(f"https://github.com/{owner}.png?size=160", headers={"User-Agent": "profile-readme"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        LOGOS.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(square_png(data))
        return dest
    except Exception:
        return None
