from __future__ import annotations

import base64
import logging
import os
import re

import httpx

log = logging.getLogger(__name__)

_API_BASE = "https://api.github.com"
_README_MAX_CHARS = 3000


def _parse_repo(url: str) -> tuple[str, str] | None:
    m = re.match(r"https?://github\.com/([^/]+)/([^/?#]+)", url)
    if not m:
        return None
    return m.group(1), m.group(2).removesuffix(".git")


def _headers() -> dict:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def scrape_github_repo(url: str) -> str:
    parsed = _parse_repo(url)
    if not parsed:
        log.debug("github_scraper: could not parse repo from %s", url)
        return ""
    owner, repo = parsed

    try:
        with httpx.Client(headers=_headers(), timeout=10.0, follow_redirects=True) as client:
            meta_resp = client.get(f"{_API_BASE}/repos/{owner}/{repo}")
            meta_resp.raise_for_status()
            meta = meta_resp.json()

            readme_text = ""
            try:
                readme_resp = client.get(f"{_API_BASE}/repos/{owner}/{repo}/readme")
                readme_resp.raise_for_status()
                raw = base64.b64decode(readme_resp.json()["content"]).decode("utf-8", errors="replace")
                readme_text = raw[:_README_MAX_CHARS] + ("…" if len(raw) > _README_MAX_CHARS else "")
            except Exception as exc:
                log.debug("github_scraper: no README for %s/%s: %s", owner, repo, exc)

        lines = [
            f"Repository: {owner}/{repo}",
            f"Description: {meta.get('description') or 'N/A'}",
            f"Stars: {meta.get('stargazers_count', 0)}  Forks: {meta.get('forks_count', 0)}",
            f"Language: {meta.get('language') or 'N/A'}",
        ]
        if meta.get("topics"):
            lines.append(f"Topics: {', '.join(meta['topics'])}")
        if readme_text:
            lines.append(f"\nREADME (excerpt):\n{readme_text}")

        return "\n".join(lines)
    except Exception as exc:
        log.warning("github_scraper: %s → %s", url, exc)
        return ""
