from __future__ import annotations

import asyncio
import json
import logging
import re
from pathlib import Path

import httpx

log = logging.getLogger(__name__)

CORPUS_DIR = Path(__file__).resolve().parents[1] / "corpus"
_MAX_CUSTOM_URLS = 5
_MAX_CUSTOM_CHARS = 6000


def load_sponsor(sponsor_id: str) -> dict | None:
    """Return the snapshot for a sponsor id, or None if there isn't one."""
    if not re.fullmatch(r"[a-z0-9-]+", sponsor_id):
        return None
    path = CORPUS_DIR / f"{sponsor_id}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text())


async def fetch_docs(urls: list[str]) -> str:
    """Fetch user-supplied docs pages as Markdown via Jina Reader (no key needed)."""

    async def one(client: httpx.AsyncClient, url: str) -> str:
        try:
            r = await client.get(f"https://r.jina.ai/{url}", headers={"Accept": "text/markdown"})
            r.raise_for_status()
            text = r.text.strip()
            return f"<!-- {url} -->\n{text[:_MAX_CUSTOM_CHARS]}" if text else ""
        except Exception as exc:
            log.warning("custom docs: %s -> %s", url, exc)
            return ""

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        chunks = await asyncio.gather(*(one(client, u) for u in urls[:_MAX_CUSTOM_URLS]))
    return "\n\n---\n\n".join(c for c in chunks if c)
