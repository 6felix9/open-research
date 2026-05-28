from __future__ import annotations

import logging
import warnings

from agents import function_tool

try:
    from ddgs import DDGS
except ImportError:  # pragma: no cover - fallback for older local environments
    from duckduckgo_search import DDGS


warnings.filterwarnings("ignore", message=r"This package .*duckduckgo_search.*", category=RuntimeWarning)

log = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for current sponsor docs, hackathon prizes, and examples."""
    log.info("search_web: %r (max_results=%d)", query, max_results)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with DDGS() as ddgs:
                results = list(ddgs.text(query, backend="html", max_results=max_results))
    except Exception as exc:
        return f"Search failed for {query!r}: {exc}"

    if not results:
        log.info("search_web: no results for %r", query)
        return f"No search results found for {query!r}."

    log.info("search_web: %d result(s) for %r", len(results), query)
    for r in results:
        title = r.get("title") or "Untitled"
        url = r.get("href") or r.get("url") or "No URL"
        log.info("  → %s  %s", title, url)

    formatted_results = []
    for index, result in enumerate(results, start=1):
        title = result.get("title") or "Untitled"
        url = result.get("href") or result.get("url") or "No URL"
        snippet = result.get("body") or result.get("snippet") or "No snippet"
        formatted_results.append(f"{index}. {title}\nURL: {url}\nSnippet: {snippet}")

    return "\n\n".join(formatted_results)


search_web_tool = function_tool(search_web)
