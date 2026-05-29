from __future__ import annotations

import logging
import os
from html.parser import HTMLParser

import httpx

log = logging.getLogger(__name__)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            stripped = data.strip()
            if stripped:
                self._chunks.append(stripped)

    def text(self) -> str:
        return "\n".join(self._chunks)


async def fetch_url_contents(urls: list[str]) -> str:
    """Fetch URLs and return concatenated Markdown content.

    Uses Firecrawl when FIRECRAWL_API_KEY is set; falls back to httpx + HTML stripping.
    """
    api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    chunks: list[str] = []

    if api_key:
        try:
            from firecrawl import FirecrawlApp  # type: ignore[import]
            app = FirecrawlApp(api_key=api_key)
            for url in urls:
                try:
                    result = app.scrape_url(url, formats=["markdown"])
                    md = (result.markdown or "").strip() if hasattr(result, "markdown") else (result.get("markdown") or "").strip()
                    if md:
                        chunks.append(f"<!-- {url} -->\n\n{md}")
                        log.info("fetch_urls: firecrawl scraped %s (%d chars)", url, len(md))
                    else:
                        log.warning("fetch_urls: firecrawl returned empty content for %s", url)
                except Exception as exc:
                    log.warning("fetch_urls: firecrawl failed for %s (%s), skipping", url, exc)
            if chunks:
                return "\n\n---\n\n".join(chunks)
        except ImportError:
            log.warning("fetch_urls: firecrawl-py not installed, falling back to httpx")

    # Fallback: plain httpx fetch + HTML text extraction
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        for url in urls:
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; OpenResearch/1.0)"})
                resp.raise_for_status()
                parser = _TextExtractor()
                parser.feed(resp.text)
                text = parser.text().strip()
                if text:
                    chunks.append(f"<!-- {url} -->\n\n{text}")
                    log.info("fetch_urls: httpx fetched %s (%d chars)", url, len(text))
            except Exception as exc:
                log.warning("fetch_urls: httpx failed for %s (%s), skipping", url, exc)

    return "\n\n---\n\n".join(chunks)
