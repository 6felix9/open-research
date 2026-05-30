from __future__ import annotations

import logging
import os

import httpx

log = logging.getLogger(__name__)

_JINA_BASE = "https://r.jina.ai/"
_MAX_CHARS = 6000
# Strip nav/header chrome so truncation hits actual project content
_REMOVE_SELECTORS = "header,nav,footer,.navbar,.nav,.menu,.header,.footer,script,style"


def scrape_url(url: str) -> str:
    headers = {
        "Accept": "text/markdown",
        "X-Return-Format": "markdown",
        "X-Remove-Selector": _REMOVE_SELECTORS,
    }
    api_key = os.getenv("JINA_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        r = httpx.get(f"{_JINA_BASE}{url}", headers=headers, timeout=10.0, follow_redirects=True)
        r.raise_for_status()
        text = r.text.strip()
        return text[:_MAX_CHARS] + ("…" if len(text) > _MAX_CHARS else "")
    except Exception as exc:
        log.warning("jina_scraper: %s → %s", url, exc)
        return ""
