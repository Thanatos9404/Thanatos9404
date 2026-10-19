"""Refreshes the live parts of the profile README.

    GITHUB_TOKEN=... python scripts/refresh.py

* assets/oss-{dark,light}.svg     pull requests to other people's repos, grouped by org
* assets/skyline-{dark,light}.svg 3D contribution skyline for the last 12 months
* README.md                       the PR list between the OSS markers
* assets/live.json                derived facts that build.py and readme.py read: merged organisations
                                  for the hero ticker, LLMSlim version and downloads, awesome-list
                                  listings, and brand-new public repos for the "fresh" cards
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import subprocess
import urllib.parse
import urllib.request
from collections import OrderedDict
from pathlib import Path

from build import EASE, card_bg, mix, reveal_css
from content import AUTO_EXCLUDE, FRESH_MAX, PROJECTS
from svgkit import THEMES, Svg, f, measure

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("GH_USER", "Thanatos9404")

# Owner -> how the organisation is shown. Anything not listed shows the owner as is.
ORGS = {
    "NVIDIA": "NVIDIA", "NVIDIA-NeMo": "NVIDIA",
    "microsoft": "Microsoft", "AzureAD": "Microsoft",
    "facebook": "Meta", "facebookresearch": "Meta", "meta-pytorch": "Meta", "Instagram": "Meta",
    "aws": "AWS", "awslabs": "AWS", "aws-cloudformation": "AWS",
    "google-ai-edge": "Google", "google": "Google",
    "IBM": "IBM", "docling-project": "Docling",
    "mozilla-ai": "Mozilla.ai", "capitalone": "Capital One", "apache": "Apache",
    "pydantic": "Pydantic", "modelscope": "ModelScope", "open-telemetry": "OpenTelemetry",
    "crewAIInc": "crewAI", "deepset-ai": "deepset", "python-pillow": "Pillow", "pnggroup": "libpng",
    "nltk": "NLTK", "astropy": "Astropy", "scikit-hep": "Scikit-HEP",
    "googleapis": "Google", "mozilla": "Mozilla", "jupyter": "Jupyter", "jupyter-server": "Jupyter",
    "jupyterlab": "Jupyter", "pyodide": "Pyodide", "prometheus": "Prometheus", "uber": "Uber",
    "containers": "Containers", "sleuthkit": "The Sleuth Kit", "quodlibet": "Quod Libet",
    "nesquena": "Hermes WebUI", "teslamotors": "Tesla", "helm": "Helm", "valyala": "fasthttp",
    "uber-go": "Uber", "ossf": "OpenSSF", "glue-viz": "glue",
}
# Well-known names first, then everything else by the stars of the repos I contributed to.
BRANDS = ["NVIDIA", "Microsoft", "Google", "Meta", "AWS", "IBM", "Tesla", "Uber", "Mozilla", "Capital One",
          "Apache", "OpenTelemetry", "Jupyter", "Prometheus", "Pydantic", "Docling", "Mozilla.ai", "ModelScope",
          "Pyodide", "Containers"]
# Curated lists where the PR only adds LLMSlim to a list are left out of the wall.
SKIP_REPO = re.compile(r"awesome", re.I)
SKIP_OWNERS = {"vansh-nagar"}


def token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


_CACHE: dict[str, dict] = {}


def cached(url: str) -> dict:
    if url not in _CACHE:
        try:
            _CACHE[url] = api(url)
        except Exception:  # a missing repo or a rate limit should never break the refresh
            _CACHE[url] = {}
    return _CACHE[url]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile-refresh"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def short(n: int) -> str:
    return f"{n / 1000:.1f}K".replace(".0K", "K") if n >= 1000 else str(n)


def api(url: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        url if url.startswith("http") else f"https://api.github.com{url}",
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {token()}", "Accept": "application/vnd.github+json",
                 "User-Agent": f"{USER}-profile-refresh"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def fetch_prs() -> list[dict]:
    q = urllib.parse.quote(f"author:{USER} type:pr -user:{USER}")
    prs, page = [], 1
    while page <= 5:
        data = api(f"/search/issues?q={q}&per_page=100&page={page}&sort=created&order=desc")
        for it in data["items"]:
            owner, repo = it["repository_url"].split("/")[-2:]
            merged = bool((it.get("pull_request") or {}).get("merged_at"))
            prs.append({
                "owner": owner, "repo": repo, "full": f"{owner}/{repo}", "number": it["number"],
                "title": it["title"].strip(), "url": it["html_url"], "created": it["created_at"][:10],
                "merged_at": ((it.get("pull_request") or {}).get("merged_at") or "")[:10],
                "status": "merged" if merged else ("open" if it["state"] == "open" else "closed"),
            })
        if len(data["items"]) < 100:
            break
        page += 1
    return prs


def fetch_calendar() -> dict:
    query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
      totalContributions weeks{contributionDays{date contributionCount contributionLevel weekday}}}}}}"""
    data = api("https://api.github.com/graphql", {"query": query, "variables": {"login": USER}})
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def group_prs(prs):
    groups: dict[str, dict] = {}
    for p in prs:
        if SKIP_REPO.search(p["repo"]) or p["owner"] in SKIP_OWNERS:
            continue
        name = ORGS.get(p["owner"], p["owner"])
        g = groups.setdefault(name, {"name": name, "prs": [], "repos": OrderedDict()})
        g["prs"].append(p)
        g["repos"][p["repo"]] = True
    for g in groups.values():
        g["merged"] = sum(p["status"] == "merged" for p in g["prs"])
        g["open"] = sum(p["status"] == "open" for p in g["prs"])
        g["prs"].sort(key=lambda p: ({"merged": 0, "open": 1, "closed": 2}[p["status"]], p["created"]))
    out = list(groups.values())
    for g in out:
        g["stars"] = sum(cached(f"/repos/{full}").get("stargazers_count") or 0 for full in {p["full"] for p in g["prs"]})
        owner = g["prs"][0]["owner"]
        if owner not in ORGS:  # unknown organisation: use its GitHub display name
            g["name"] = (cached(f"/users/{owner}").get("name") or owner).strip()
    rank = lambda g: BRANDS.index(g["name"]) if g["name"] in BRANDS else len(BRANDS)
    out.sort(key=lambda g: (0 if g["merged"] else 1, rank(g), -g["stars"], -len(g["prs"]), g["name"].lower()))
    return out


# ---------------------------------------------------------------------------
# Open source wall
# ---------------------------------------------------------------------------

def clip(text, font, size, max_w):
    if measure(text, font, size) <= max_w:
        return text
    while text and measure(text + "...", font, size) > max_w:
        text = text[:-1]
    return text.rstrip(" ,.:;") + "..."


def oss_svg(theme, prs, groups):
    t = theme
    W, gap = 1200, 16
    cols, tile_h, max_tiles = 4, 150, 16
    shown = groups[:max_tiles] if len(groups) <= max_tiles else groups[:max_tiles - 1]
    rest = groups[len(shown):]
    rows = math.ceil((len(shown) + (1 if rest else 0)) / cols)
    merged = [p for p in prs if p["status"] == "merged" and not SKIP_REPO.search(p["repo"])]
    merged.sort(key=lambda p: p["merged_at"], reverse=True)
    recent = merged[:5]
    stats_h = 150
    list_h = 70 + len(recent) * 50 if recent else 0
    H = stats_h + gap + rows * (tile_h + gap) + list_h
    total = sum(len(g["prs"]) for g in groups)
    n_merged = sum(g["merged"] for g in groups)
    n_open = sum(g["open"] for g in groups)
    n_repos = sum(len(g["repos"]) for g in groups)
    s = Svg(W, H, t, f"{total} pull requests to {n_repos} repositories across {len(groups)} organisations, "
                     f"{n_merged} merged",
            "Organisations: " + ", ".join(f"{g['name']} ({len(g['prs'])})" for g in groups))
    reveal_css(s)
    ink, body, muted, acc = t["ink"], t["body"], t["muted"], t["accent"]

    # stats strip
    card_bg(s, 0, 0, W, stats_h, glow=True)
    cells = [(str(total), "pull requests opened"), (str(n_merged), "merged so far"),
             (str(n_open), "in review"), (str(len(groups)), "organisations"), (str(n_repos), "repositories")]
    cw = (W - 80) / len(cells)
    for i, (big, label) in enumerate(cells):
        x = 40 + i * cw
        color = acc if i == 1 else ink
        s.add(f'<g class="rv" style="animation-delay:{.05 + i * .08:.2f}s">'
              + s.text(x, 92, big, "serif", 64, color, ls=-1)
              + s.text(x + 2, 122, label, "sans", 15, muted) + "</g>")
        if i:
            s.add(f'<line x1="{f(x - 20)}" y1="38" x2="{f(x - 20)}" y2="118" stroke="{t["line"]}"/>')

    # org tiles
    tw = (W - gap * (cols - 1)) / cols
    s.style("@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}"
            ".sq{transform-box:fill-box;transform-origin:center;animation:pop .5s cubic-bezier(.2,.9,.3,1.4) both}")
    for k, g in enumerate(shown):
        r, c = divmod(k, cols)
        x, y = c * (tw + gap), stats_h + gap + r * (tile_h + gap)
        card_bg(s, x, y, tw, tile_h, r=22)
        repos = ", ".join(g["repos"].keys())
        s.add(f'<g class="rv" style="animation-delay:{.2 + k * .05:.2f}s">'
              + s.text(x + 24, y + 44, g["name"], "sans-sb", 20, ink)
              + s.text(x + 24, y + 68, clip(repos, "mono", 11.5, tw - 48), "mono", 11.5, muted)
              + "</g>")
        sx = x + 24
        for j, p in enumerate(g["prs"][:12]):
            if p["status"] == "merged":
                sq = f'<rect x="{f(sx)}" y="{y + 92}" width="14" height="14" rx="3" fill="{acc}"/>'
            elif p["status"] == "open":
                sq = f'<rect x="{f(sx + .75)}" y="{y + 92.75}" width="12.5" height="12.5" rx="3" fill="none" stroke="{body}" stroke-width="1.5"/>'
            else:
                sq = f'<rect x="{f(sx)}" y="{y + 92}" width="14" height="14" rx="3" fill="{t["line2"]}"/>'
            s.add(f'<g class="sq" style="animation-delay:{.5 + k * .05 + j * .04:.2f}s">{sq}</g>')
            sx += 20
        if len(g["prs"]) > 12:
            s.add(s.text(sx + 2, y + 104, f"+{len(g['prs']) - 12}", "mono", 11, muted))
        label = f"{len(g['prs'])} PR{'S' if len(g['prs']) != 1 else ''}" + (f" · {g['merged']} MERGED" if g["merged"] else "")
        s.add(s.text(x + 24, y + 132, label, "mono", 11, acc if g["merged"] else muted, ls=1.4))
        if g.get("stars", 0) >= 100:
            s.add(s.text(x + tw - 24, y + 132, f"{short(g['stars'])} STARS", "mono", 11, muted, anchor="end", ls=1.4))

    if rest:
        k = len(shown)
        r, c = divmod(k, cols)
        x, y = c * (tw + gap), stats_h + gap + r * (tile_h + gap)
        card_bg(s, x, y, tw, tile_h, r=22)
        names = ", ".join(g["name"] for g in rest)
        lines = []
        for word in names.split(" "):
            if lines and measure(lines[-1] + " " + word, "mono", 11.5) <= tw - 48:
                lines[-1] += " " + word
            elif len(lines) < 3:
                lines.append(word)
            else:  # third line is full: end it after the last whole name instead of skipping ahead
                lines[2] = lines[2].rsplit(",", 1)[0] + ", ..." if "," in lines[2] else lines[2] + " ..."
                break
        if len(lines) == 3:
            lines[2] = clip(lines[2], "mono", 11.5, tw - 48)
        s.add(f'<g class="rv" style="animation-delay:{.2 + k * .05:.2f}s">'
              + s.text(x + 22, y + 58, f"+{len(rest)}", "serif", 46, ink, ls=-1)
              + s.text(x + 24 + measure(f"+{len(rest)}", "serif", 46, -1) + 10, y + 56, "more organisations", "sans", 14.5,
                       muted)
              + "".join(s.text(x + 24, y + 88 + i * 18, ln, "mono", 11.5, muted) for i, ln in enumerate(lines))
              + "</g>")

    # recently merged
    if recent:
        y0 = stats_h + gap + rows * (tile_h + gap)
        card_bg(s, 0, y0, W, list_h - 0, r=22)
        s.add(s.text(28, y0 + 42, "RECENTLY MERGED", "mono-m", 12, acc, ls=2.2))
        legend_x = W - 28
        for label, kind in (("closed", "c"), ("in review", "o"), ("merged", "m")):
            lw = measure(label, "mono", 11.5, 1)
            s.add(s.text(legend_x, y0 + 42, label, "mono", 11.5, muted, anchor="end", ls=1))
            bx = legend_x - lw - 20
            if kind == "m":
                s.add(f'<rect x="{f(bx)}" y="{y0 + 31}" width="12" height="12" rx="3" fill="{acc}"/>')
            elif kind == "o":
                s.add(f'<rect x="{f(bx + .75)}" y="{y0 + 31.75}" width="10.5" height="10.5" rx="3" fill="none" stroke="{body}" stroke-width="1.5"/>')
            else:
                s.add(f'<rect x="{f(bx)}" y="{y0 + 31}" width="12" height="12" rx="3" fill="{t["line2"]}"/>')
            legend_x = bx - 22
        for i, p in enumerate(recent):
            y = y0 + 84 + i * 50
            repo = f"{p['full']}#{p['number']}"
            rw = 330
            s.add(f'<g class="rv" style="animation-delay:{.6 + i * .08:.2f}s">'
                  + (f'<line x1="28" y1="{y - 30}" x2="{W - 28}" y2="{y - 30}" stroke="{t["line"]}"/>' if i else "")
                  + s.text(28, y, clip(repo, "mono-m", 13, rw - 20), "mono-m", 13, acc)
                  + s.text(28 + rw, y, clip(p["title"], "sans", 16, W - 28 - rw - 140), "sans", 16, body)
                  + s.text(W - 28, y, dt.date.fromisoformat(p["merged_at"]).strftime("%d %b %Y").upper(), "mono", 11.5,
                           muted, anchor="end", ls=1.2)
                  + "</g>")
    return s


def readme_block(groups) -> str:
    total = sum(len(g["prs"]) for g in groups)
    lines = ["<details>", f"<summary><b>All {total} pull requests</b>, by organisation</summary>", ""]
    for g in groups:
        lines.append(f"**{g['name']}**")
        lines.append("")
        for p in g["prs"]:
            title = p["title"].replace("[", "(").replace("]", ")").replace("|", "/")
            lines.append(f"- `{p['status']}` [{title}]({p['url']}) <sub>{p['full']}#{p['number']}</sub>")
        lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3D contribution skyline
# ---------------------------------------------------------------------------

def streaks(days):
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, cur)
    current = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            current += 1
        elif d is days[-1]:
            continue  # today may still be empty
        else:
            break
    return longest, current


def skyline_svg(theme, cal):
    t = theme
    dark = t["name"] == "dark"
    W, H = 1200, 460
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    total = cal["totalContributions"]
    longest, current = streaks(days)
    best = max(days, key=lambda d: d["contributionCount"])
    month = days[-1]["date"][:7]
    this_month = sum(d["contributionCount"] for d in days if d["date"].startswith(month))
    s = Svg(W, H, t, f"{total} contributions in the last year",
            f"Longest streak {longest} days, current streak {current} days, busiest day "
            f"{best['contributionCount']} contributions on {best['date']}.")
    reveal_css(s)
    card_bg(s, 0, 0, W, H, r=30, glow=True)
    ink, body, muted, acc = t["ink"], t["body"], t["muted"], t["accent"]

    # left column
    x0 = 48
    s.add('<g class="rv" style="animation-delay:.05s">'
          + s.text(x0, 70, "LAST 12 MONTHS", "mono-m", 12.5, acc, ls=2.4)
          + s.text(x0 - 4, 170, f"{total:,}", "serif", 104, ink, ls=-2.5)
          + s.text(x0, 204, "contributions on GitHub", "sans", 18, body) + "</g>")
    rows = [("LONGEST STREAK", f"{longest} days"), ("CURRENT STREAK", f"{current} days"),
            ("THIS MONTH", f"{this_month} contributions"),
            ("BUSIEST DAY", f"{best['contributionCount']} on {dt.date.fromisoformat(best['date']).strftime('%d %b')}")]
    for i, (k, v) in enumerate(rows):
        y = 262 + i * 44
        s.add(f'<g class="rv" style="animation-delay:{.15 + i * .07:.2f}s">'
              f'<line x1="{x0}" y1="{y - 26}" x2="{x0 + 290}" y2="{y - 26}" stroke="{t["line"]}"/>'
              + s.text(x0, y, k, "mono", 11.5, muted, ls=1.6)
              + s.text(x0 + 290, y, v, "sans-m", 16, ink, anchor="end") + "</g>")

    # skyline
    ox, oy = 448, 138
    ax, ay, bx, by = 13.1, 3.0, -5.6, 7.6
    P = lambda u, v, z=0: (ox + u * ax + v * bx, oy + u * ay + v * by - z)
    ramp = (["#2A2420", "#5B3524", "#9A4A26", "#D6612B", "#FF7A3D"] if dark
            else ["#E6DED7", "#F7CDB2", "#F2A174", "#EC7A3F", "#E0581A"])
    lvl = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    maxc = max(1, max(d["contributionCount"] for d in days))
    shade = "#000000" if dark else "#3A2A20"
    cells = []
    for i, w in enumerate(cal["weeks"]):
        for d in w["contributionDays"]:
            cells.append((i, d["weekday"], d))
    cells.sort(key=lambda c: (c[1], c[0]))
    g = .16
    parts = []
    for i, wd, d in cells:
        c = d["contributionCount"]
        h = 2.5 if c == 0 else 6 + 104 * math.sqrt(c / maxc)
        col = ramp[lvl.get(d["contributionLevel"], 0)]
        right, front = mix(col, shade, .28 if dark else .18), mix(col, shade, .5 if dark else .32)
        u0, u1, v0, v1 = i + g, i + 1 - g, wd + g, wd + 1 - g
        top = [P(u0, v0, h), P(u1, v0, h), P(u1, v1, h), P(u0, v1, h)]
        rf = [P(u1, v0, h), P(u1, v1, h), P(u1, v1), P(u1, v0)]
        ff = [P(u0, v1, h), P(u1, v1, h), P(u1, v1), P(u0, v1)]
        pts = lambda a: " ".join(f"{f(x)},{f(y)}" for x, y in a)
        poly = (f'<polygon points="{pts(ff)}" fill="{front}"/><polygon points="{pts(rf)}" fill="{right}"/>'
                f'<polygon points="{pts(top)}" fill="{col}"/>')
        if c:
            delay = .3 + i * .022 + wd * .03
            parts.append(f'<g class="b" style="animation-delay:{delay:.2f}s">{poly}</g>')
        else:
            parts.append(poly)
    s.style(f".b{{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1s {EASE} both}}"
            "@keyframes grow{from{transform:scaleY(.03)}to{transform:none}}")
    s.add(f'<g>{"".join(parts)}</g>')

    # month labels along the front edge
    seen = set()
    for i, w in enumerate(cal["weeks"]):
        first = w["contributionDays"][0]["date"]
        m = first[:7]
        if m in seen or i == 0:
            seen.add(m)
            continue
        seen.add(m)
        if dt.date.fromisoformat(first).day <= 7:
            x, y = P(i + .5, 7.9)
            s.add(s.text(x, y + 14, dt.date.fromisoformat(first).strftime("%b").upper(), "mono", 10.5, muted,
                         anchor="middle", ls=1.2))
    # today marker
    li = len(cal["weeks"]) - 1
    lwd = cal["weeks"][-1]["contributionDays"][-1]["weekday"]
    tx, ty = P(li + .5, lwd + .5, 3)
    s.style("@keyframes ring{0%{transform:scale(1);opacity:.8}100%{transform:scale(4.5);opacity:0}}"
            ".ring{transform-box:fill-box;transform-origin:center;animation:ring 2s ease-out infinite}")
    s.add(f'<circle class="ring" cx="{f(tx)}" cy="{f(ty)}" r="4" fill="none" stroke="{acc}" stroke-width="1.5"/>'
          f'<circle cx="{f(tx)}" cy="{f(ty)}" r="3" fill="{acc}"/>')
    return s


# ---------------------------------------------------------------------------
# Derived facts for the static sections (assets/live.json)
# ---------------------------------------------------------------------------

LIVE = ROOT / "assets" / "live.json"


def nice(text: str) -> str:
    """Repo descriptions may contain dashes the house style avoids."""
    text = re.sub(r"\s*[\u2014\u2013]\s*", ", ", text.strip())
    return re.sub(r"\s+", " ", text)


def split_description(repo: str, desc: str):
    """'RuleDost: does X. Build With AI 2026.' -> ('RuleDost', 'Does X.', 'Build With AI 2026')."""
    desc = nice(desc)
    name = repo
    m = re.match(r"^([^:,.]{2,40})\s*[:,]\s+(.*)$", desc)
    if m and re.sub(r"[^a-z0-9]", "", m.group(1).lower()) == re.sub(r"[^a-z0-9]", "", repo.lower()):
        name, desc = m.group(1).strip(), m.group(2)
    parts = re.split(r"(?<=[.!?])\s+", desc)
    tag = ""
    if len(parts) > 1 and len(parts[-1]) <= 80 and re.search(r"hackathon|challenge|summit|202\d", parts[-1], re.I):
        tag = parts.pop().rstrip(".")
        tag = re.sub(r"\s*\([^)]*\)", "", tag).split(",")[0].strip()  # "X Hackathon 2026 (City), Track D" -> "X Hackathon 2026"
    body = " ".join(parts).strip()
    return name, (body[:1].upper() + body[1:]) if body else "", tag


def fetch_fresh() -> list[dict]:
    featured = {p["repo"].lower() for p in PROJECTS} | {x.lower() for x in AUTO_EXCLUDE}
    cutoff = (dt.date.today() - dt.timedelta(days=60)).isoformat()
    out = []
    for r in cached(f"/users/{USER}/repos?per_page=100&type=owner&sort=created") or []:
        if not isinstance(r, dict) or r.get("fork") or r.get("archived") or r.get("private"):
            continue
        if r["name"].lower() in featured or not r.get("description") or r["created_at"][:10] < cutoff:
            continue
        name, body, tag = split_description(r["name"], r["description"])
        if not body:
            continue
        out.append({"repo": r["name"], "name": name, "desc": body, "tag": tag, "url": r["html_url"],
                    "homepage": r.get("homepage") or "", "language": r.get("language") or "",
                    "stars": r.get("stargazers_count") or 0, "created": r["created_at"][:10]})
    out.sort(key=lambda x: x["created"], reverse=True)
    return out[:FRESH_MAX]


def fetch_llmslim(prev: dict) -> dict:
    out = dict(prev)
    try:
        out["version"] = fetch_json("https://pypi.org/pypi/llmslim/json")["info"]["version"]
    except Exception:
        pass
    try:
        out["downloads_week"] = fetch_json("https://pypistats.org/api/packages/llmslim/recent")["data"]["last_week"]
    except Exception:
        pass
    stars = cached(f"/repos/{USER}/llmslim").get("stargazers_count")
    if stars is not None:
        out["stars"] = stars
    return out


def listings(prs) -> list[dict]:
    """Curated lists and integration catalogues that accepted LLMSlim."""
    out = []
    for p in prs:
        if p["status"] == "merged" and re.search(r"llmslim", p["title"], re.I):
            name = re.sub(r"[-_]+", " ", p["repo"]).strip()
            name = " ".join(w if w.isupper() or any(c.isupper() for c in w[1:]) else w.capitalize() for w in name.split())
            out.append({"name": name, "full": p["full"], "url": p["url"],
                        "stars": cached(f"/repos/{p['full']}").get("stargazers_count") or 0})
    out.sort(key=lambda x: -x["stars"])
    return out


def write_live(prs, groups):
    prev = {}
    if LIVE.exists():
        try:
            prev = json.loads(LIVE.read_text(encoding="utf-8"))
        except ValueError:
            prev = {}
    merged_groups = [g for g in groups if g["merged"]]
    live = {
        "prs": sum(len(g["prs"]) for g in groups),
        "merged": sum(g["merged"] for g in groups),
        "orgs": len(groups),
        "merged_orgs": [g["name"] for g in merged_groups],
        "review_orgs": [g["name"] for g in groups if not g["merged"]][:6],
        "listed_in": listings(prs),
        "llmslim": fetch_llmslim(prev.get("llmslim", {})),
        "fresh": fetch_fresh(),
    }
    LIVE.write_text(json.dumps(live, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return live


def update_readme(block: str):
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    new = re.sub(r"(<!-- OSS:START -->)(.*?)(<!-- OSS:END -->)", lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}",
                 text, flags=re.S)
    if new != text:
        path.write_text(new, encoding="utf-8", newline="\n")


def main():
    prs = fetch_prs()
    groups = group_prs(prs)
    cal = fetch_calendar()
    for name, theme in THEMES.items():
        oss_svg(theme, prs, groups).save(ROOT / "assets" / f"oss-{name}.svg")
        skyline_svg(theme, cal).save(ROOT / "assets" / f"skyline-{name}.svg")
    update_readme(readme_block(groups))
    live = write_live(prs, groups)
    print(f"{len(prs)} PRs, {len(groups)} orgs, {cal['totalContributions']} contributions, "
          f"merged at {', '.join(live['merged_orgs'])}, {len(live['fresh'])} fresh repos")


if __name__ == "__main__":
    main()
