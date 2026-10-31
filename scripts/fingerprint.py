"""Cheap change detection for the README (standard library only).

    GITHUB_TOKEN=... python scripts/fingerprint.py           # prints the current fingerprint
    GITHUB_TOKEN=... python scripts/fingerprint.py --check   # prints "changed" or "same" vs assets/live.json

The fingerprint moves when a pull request to someone else's repo is opened, merged or closed, when a public
repo is created, or when LLMSlim ships a release. It costs four GitHub API calls and one PyPI call, so the
workflow can run it every 15 minutes and rebuild only when something actually happened.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("GH_USER", "Thanatos9404")


def _token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def _get(url: str, auth: bool = True):
    headers = {"User-Agent": f"{USER}-profile-fingerprint", "Accept": "application/vnd.github+json"}
    if auth:
        headers["Authorization"] = f"Bearer {_token()}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
        return json.load(r)


def _count(query: str) -> int:
    q = urllib.parse.quote(query)
    return _get(f"https://api.github.com/search/issues?q={q}&per_page=1")["total_count"]


def fingerprint() -> str:
    base = f"author:{USER} type:pr -user:{USER}"
    parts = [f"prs={_count(base)}", f"merged={_count(base + ' is:merged')}", f"open={_count(base + ' is:open')}"]
    user = _get(f"https://api.github.com/users/{USER}")
    newest = _get(f"https://api.github.com/users/{USER}/repos?sort=created&per_page=1&type=owner")
    parts += [f"repos={user.get('public_repos')}", f"newest={newest[0]['name'] if newest else ''}"]
    try:
        parts.append("llmslim=" + _get("https://pypi.org/pypi/llmslim/json", auth=False)["info"]["version"])
    except Exception:
        parts.append("llmslim=?")
    return ";".join(parts)


def stored() -> str:
    try:
        return json.loads((ROOT / "assets" / "live.json").read_text(encoding="utf-8")).get("fingerprint", "")
    except (OSError, ValueError):
        return ""


if __name__ == "__main__":
    fp = fingerprint()
    if "--check" in sys.argv:
        old = stored()
        print("changed" if fp != old else "same")
        print(f"now:    {fp}", file=sys.stderr)
        print(f"stored: {old}", file=sys.stderr)
    else:
        print(fp)
