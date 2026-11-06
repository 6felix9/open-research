"""Rebuild the sponsor snapshot corpus in backend/corpus/<sponsor-id>.json.

Maintainer tool, not part of the running app. For each sponsor it:
  1. reads the official docs (Jina Reader, no key needed) and has the LLM write a profile,
  2. finds past Devpost projects (DuckDuckGo search -> Jina Reader),
  3. finds hackathon-style GitHub repos (GitHub search API).

Needs OPENAI_API_KEY (profile summaries only). GITHUB_TOKEN is optional and only raises rate limits.

    pip install -r scripts/requirements.txt
    python scripts/refresh_corpus.py            # all sponsors
    python scripts/refresh_corpus.py supabase   # just one

A sponsor that fails keeps its previous snapshot untouched.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import httpx
from ddgs import DDGS
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "backend" / "corpus"
load_dotenv(ROOT / ".env.local")
load_dotenv(ROOT / ".env")

# Keep in sync with SPONSORS in frontend/src/data.ts.
SPONSORS: dict[str, tuple[str, str]] = {
    "groq": ("Groq", "https://console.groq.com/docs/overview"),
    "anthropic": ("Anthropic", "https://docs.claude.com/en/docs/intro"),
    "modal": ("Modal", "https://modal.com/docs/guide"),
    "supabase": ("Supabase", "https://supabase.com/docs"),
    "vercel": ("Vercel", "https://vercel.com/docs"),
    "elevenlabs": ("ElevenLabs", "https://elevenlabs.io/docs/overview/intro"),
    "mistral": ("Mistral", "https://docs.mistral.ai/"),
    "pinecone": ("Pinecone", "https://docs.pinecone.io/guides/get-started/overview"),
}

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
DEVPOST_PROJECTS = 4
DEVPOST_FETCH_LIMIT = 9  # pages to read while looking for DEVPOST_PROJECTS that mention the sponsor
GITHUB_REPOS = 4
JINA_DELAY_S = 3.5  # keyless Jina Reader allows roughly 20 requests/minute

http = httpx.Client(timeout=30, follow_redirects=True)
_last_jina = 0.0

PROFILE_PROMPT = """You are a developer-relations researcher for hackathon builders.
From the documentation below, write a concise Markdown profile of {name} (under 350 words) with:
- **Capabilities and APIs** a builder can use in a weekend
- **Hero use cases** the sponsor showcases
- **What it rewards** in hackathon projects (judge signals, if the docs hint at any)
- **Recent or notable features** worth building on right now
Stick to what the documentation supports. Do not invent prize details.

DOCUMENTATION
-------------
{docs}
"""


def jina_read(url: str) -> str:
    global _last_jina
    wait = JINA_DELAY_S - (time.monotonic() - _last_jina)
    if wait > 0:
        time.sleep(wait)
    _last_jina = time.monotonic()
    headers = {"Accept": "text/markdown", "X-Return-Format": "markdown"}
    for attempt in range(2):
        r = http.get(f"https://r.jina.ai/{url}", headers=headers)
        if r.status_code == 429 and attempt == 0:
            time.sleep(20)
            continue
        r.raise_for_status()
        return r.text.strip()
    return ""


def devpost_body(md: str) -> str:
    """Pull the project write-up out of a Devpost page, dropping nav chrome and link/image markup."""
    body = md.split("Markdown Content:", 1)[-1]
    start = re.search(r"^#+\s*(Inspiration|What it does|About the project)", body, re.M | re.I)
    if start:
        body = body[start.start():]
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)           # images
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)        # links -> text
    body = re.sub(r"^\s*[*-]?\s*$", "", body, flags=re.M)
    return re.sub(r"\s+", " ", body).strip()


def devpost_entries(name: str) -> list[dict]:
    hits = DDGS().text(f"site:devpost.com/software {name} hackathon", max_results=15)
    urls: list[str] = []
    for h in hits:
        url = h.get("href", "")
        if "devpost.com/software/" in url and url not in urls:
            urls.append(url)
    entries = []
    for url in urls[:DEVPOST_FETCH_LIMIT]:
        try:
            md = jina_read(url)
        except Exception as exc:
            print(f"    devpost skip {url}: {exc}")
            continue
        if name.lower() not in md.lower():
            continue  # search is fuzzy; keep only projects that actually mention the sponsor
        title = re.search(r"^Title:\s*(.+)$", md, re.M)
        body = devpost_body(md)
        entries.append({
            "source": "devpost",
            "title": (title.group(1) if title else url).replace(" | Devpost", "").strip(),
            "url": url,
            "meta": "Devpost",
            "excerpt": body[:900],
        })
        if len(entries) >= DEVPOST_PROJECTS:
            break
    return entries


def gh_get(url: str, **kwargs) -> httpx.Response:
    """GitHub GET. GITHUB_TOKEN is optional; if it is rejected, retry unauthenticated."""
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        r = http.get(url, headers={**headers, "Authorization": f"Bearer {token}"}, **kwargs)
        if r.status_code != 401:
            return r
        print("    GITHUB_TOKEN was rejected (401); continuing without it")
        os.environ.pop("GITHUB_TOKEN")
    return http.get(url, headers=headers, **kwargs)


def github_entries(name: str) -> list[dict]:
    r = gh_get(
        "https://api.github.com/search/repositories",
        params={"q": f"{name} hackathon", "sort": "stars", "per_page": GITHUB_REPOS},
    )
    r.raise_for_status()
    entries = []
    for repo in r.json().get("items", []):
        readme = ""
        rr = gh_get(f"https://api.github.com/repos/{repo['full_name']}/readme")
        if rr.status_code == 200:
            readme = base64.b64decode(rr.json()["content"]).decode("utf-8", "replace")
        excerpt = f"{repo.get('description') or ''} {readme}"
        meta = f"GitHub · {repo['stargazers_count']}★" + (f" · {repo['language']}" if repo.get("language") else "")
        entries.append({
            "source": "github",
            "title": repo["full_name"],
            "url": repo["html_url"],
            "meta": meta,
            "excerpt": re.sub(r"\s+", " ", excerpt)[:600].strip(),
        })
    return entries


def refresh(sponsor_id: str, client: OpenAI) -> None:
    name, docs_url = SPONSORS[sponsor_id]
    print(f"{name}")
    docs = jina_read(docs_url)[:14000]
    if not docs:
        raise RuntimeError("docs came back empty")
    profile = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROFILE_PROMPT.format(name=name, docs=docs)}],
    ).choices[0].message.content.strip()
    prior_art = devpost_entries(name) + github_entries(name)
    print(f"    {len(profile)} char profile, {len(prior_art)} prior-art entries")
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    out = {
        "id": sponsor_id,
        "name": name,
        "updated": date.today().isoformat(),
        "docs_url": docs_url,
        "profile": profile,
        "prior_art": prior_art,
    }
    (CORPUS_DIR / f"{sponsor_id}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")


def main(argv: list[str]) -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is required (set it in .env.local).")
        return 1
    targets = argv or list(SPONSORS)
    unknown = [t for t in targets if t not in SPONSORS]
    if unknown:
        print(f"Unknown sponsor id(s): {', '.join(unknown)}. Known: {', '.join(SPONSORS)}")
        return 1
    client = OpenAI()
    failed = []
    for sponsor_id in targets:
        try:
            refresh(sponsor_id, client)
        except Exception as exc:
            print(f"    FAILED, keeping previous snapshot: {exc}")
            failed.append(sponsor_id)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
