"""Refreshes the live parts of the profile README.

    GITHUB_TOKEN=... python scripts/refresh.py

* assets/logos/gh-<owner>.png     official GitHub avatar of every organisation I contributed to
* README.md                       the PR list between the OSS markers
* assets/live.json                derived facts that build.py and readme.py read: merged organisations
                                  for the hero ticker, LLMSlim version and downloads, awesome-list
                                  listings, and brand-new public repos for the "fresh" cards
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from collections import OrderedDict
from pathlib import Path

from content import AUTO_EXCLUDE, FRESH_MAX, PROJECTS
from fingerprint import fingerprint
from logos import fetch_avatar

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("GH_USER", "Thanatos9404")

# Owner -> how the organisation is shown. Anything not listed shows the owner as is.
ORGS = {
    "NVIDIA": "NVIDIA", "NVIDIA-NeMo": "NVIDIA",
    "microsoft": "Microsoft", "AzureAD": "Microsoft",
    "facebook": "Meta", "facebookresearch": "Meta", "meta-pytorch": "Meta", "Instagram": "Meta", "meta": "Meta",
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
    "uber-go": "Uber", "ossf": "OpenSSF", "glue-viz": "glue", "pysal": "PySAL", "corazawaf": "Coraza",
    "DataDog": "Datadog", "milvus-io": "Milvus", "cadence-workflow": "Cadence",
    "radareorg": "radare2", "speced": "Bikeshed", "davila7": "Claude Code Templates",
}
# Well-known names first, then everything else by the stars of the repos I contributed to.
BRANDS = ["NVIDIA", "Microsoft", "Google", "Meta", "AWS", "IBM", "Tesla", "Uber", "Mozilla", "Capital One",
          "Apache", "OpenTelemetry", "Jupyter", "Prometheus", "Pydantic", "Docling", "Mozilla.ai", "ModelScope",
          "Pyodide", "Containers"]
# Which GitHub account's avatar stands in for a grouped organisation's logo.
LOGO_OWNER = {"NVIDIA": "NVIDIA", "Microsoft": "microsoft", "Google": "google", "Meta": "facebookresearch",
              "AWS": "aws", "IBM": "IBM", "Tesla": "teslamotors", "Uber": "uber", "Jupyter": "jupyter"}
# Curated lists where the PR only adds LLMSlim to a list are left out of the wall.
SKIP_REPO = re.compile(r"awesome", re.I)
SKIP_OWNERS = {"vansh-nagar", "KalyanKS-NLP", "kimtth"}


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


EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D]+")


def clean(text: str) -> str:
    """House style: no emojis and no em or en dashes in anything shown on the profile."""
    text = EMOJI.sub("", text)
    text = re.sub(r"\s*[\u2014\u2013]\s*", ", ", text)
    return re.sub(r"\s+", " ", text).strip()


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
                "title": clean(it["title"]), "url": it["html_url"], "created": it["created_at"][:10],
                "merged_at": ((it.get("pull_request") or {}).get("merged_at") or "")[:10],
                "status": "merged" if merged else ("open" if it["state"] == "open" else "closed"),
            })
        if len(data["items"]) < 100:
            break
        page += 1
    return prs


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
            g["name"] = clean(cached(f"/users/{owner}").get("name") or owner) or owner
    rank = lambda g: BRANDS.index(g["name"]) if g["name"] in BRANDS else len(BRANDS)
    out.sort(key=lambda g: (0 if g["merged"] else 1, rank(g), -g["stars"], -len(g["prs"]), g["name"].lower()))
    return out


def readme_block(groups) -> str:
    total = sum(len(g["prs"]) for g in groups)
    merged = sum(g["merged"] for g in groups)
    lines = ["<details>", f"<summary><b>All {total} pull requests</b> ({merged} merged), grouped by organisation"
                          "</summary>", ""]
    for g in groups:
        tally = f"{g['merged']} merged of {len(g['prs'])}" if g["merged"] else f"{len(g['prs'])} in review"
        lines += [f"**{g['name']}** &nbsp;<sub>{tally}</sub>", ""]
        for p in g["prs"]:
            title = p["title"].replace("[", "(").replace("]", ")").replace("|", "/")
            lines.append(f"- `{p['status']}` [{title}]({p['url']}) <sub>{p['full']}#{p['number']}</sub>")
        lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


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
    """Curated lists and integration catalogues that accepted LLMSlim (one entry per repo).

    kind "list": an "Add LLMSlim to ..." entry in a curated list.
    kind "integration": LLMSlim shipped inside someone else's product (a plugin catalogue, an extension store).
    """
    known = {"NousResearch/hermes-agent": "Hermes Agent plugin catalog", "raycast/extensions": "Raycast Store"}
    out: dict[str, dict] = {}
    for p in prs:
        if p["status"] != "merged" or p["owner"] == USER or not re.search(r"llmslim", p["title"], re.I):
            continue
        if p["full"] in out:
            continue
        name = re.sub(r"[-_]+", " ", p["repo"]).strip()
        acr = {"llm": "LLM", "ai": "AI", "mcp": "MCP", "rag": "RAG", "cli": "CLI", "openai": "OpenAI", "llmops": "LLMOps"}
        name = " ".join(acr.get(w.lower()) or (w if any(c.isupper() for c in w) else w.capitalize())
                        for w in name.split())
        is_list = bool(re.search(r"awesome|toolkit|notes|resources|list", p["repo"], re.I)
                       or re.match(r"add\b.*\bto\b", p["title"], re.I))
        repo = cached(f"/repos/{p['full']}")
        out[p["full"]] = {"name": known.get(p["full"], name), "full": p["full"],
                          "url": repo.get("html_url") or f"https://github.com/{p['full']}",
                          "kind": "integration" if p["full"] in known or not is_list else "list",
                          "owner": clean(cached(f"/users/{p['owner']}").get("name") or p["owner"]),
                          "stars": repo.get("stargazers_count") or 0}
    return sorted(out.values(), key=lambda x: -x["stars"])


def write_live(prs, groups):
    prev = {}
    if LIVE.exists():
        try:
            prev = json.loads(LIVE.read_text(encoding="utf-8"))
        except ValueError:
            prev = {}
    merged_groups = [g for g in groups if g["merged"]]
    for g in groups:
        g["logo_owner"] = LOGO_OWNER.get(g["name"], g["prs"][0]["owner"])
        fetch_avatar(g["logo_owner"])
    live = {
        "repos": sum(len(g["repos"]) for g in groups),
        "org_list": [{"name": g["name"], "logo": g["logo_owner"], "merged": g["merged"], "prs": len(g["prs"]),
                      "open": g["open"], "stars": g["stars"]} for g in groups],
        "prs": sum(len(g["prs"]) for g in groups),
        "merged": sum(g["merged"] for g in groups),
        "orgs": len(groups),
        "merged_orgs": [g["name"] for g in merged_groups],
        "review_orgs": [g["name"] for g in groups if not g["merged"]][:6],
        "listed_in": listings(prs),
        "llmslim": fetch_llmslim(prev.get("llmslim", {})),
        "fresh": fetch_fresh(),
    }
    try:  # what the 15-minute check compares against (see fingerprint.py)
        live["fingerprint"] = fingerprint()
    except Exception:
        live["fingerprint"] = prev.get("fingerprint", "")
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
    live = write_live(prs, groups)
    update_readme(readme_block(groups))
    print(f"{live['prs']} PRs, {live['merged']} merged, {live['orgs']} orgs, "
          f"merged at {', '.join(live['merged_orgs'][:8])}..., {len(live['fresh'])} fresh repos")


if __name__ == "__main__":
    main()
