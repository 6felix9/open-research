from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from exa_py import Exa

from .github_scraper import scrape_github_repo
from .jina_scraper import scrape_url

log = logging.getLogger(__name__)


def has_exa_key() -> bool:
    return bool(os.getenv("EXA_API_KEY"))


def exa_search_prior_art(sponsor_name: str, source_type: str) -> str:
    exa = Exa(api_key=os.getenv("EXA_API_KEY"))

    if source_type == "devpost":
        query = f"{sponsor_name} hackathon project winning submission"
        kwargs: dict = dict(
            num_results=5,
            include_domains=["devpost.com"],
            contents={"highlights": True},
        )
    elif source_type == "github":
        query = f"{sponsor_name} hackathon project built-with"
        kwargs = dict(
            num_results=5,
            include_domains=["github.com"],
            contents={"highlights": True},
        )
    else:
        # X/Twitter is often paywalled; cast a wider net for community signals
        query = f"{sponsor_name} hackathon developer community award winner"
        kwargs = dict(num_results=5, contents={"highlights": True})

    log.debug("exa_search [%s/%s]: query=%r", sponsor_name, source_type, query)
    results = exa.search(query, **kwargs)

    # Enrich top 3 results with full content via the appropriate scraper
    scraped: dict[str, str] = {}
    if results.results and source_type in ("devpost", "github"):
        urls = [r.url for r in results.results[:3]]
        scraper = scrape_url if source_type == "devpost" else scrape_github_repo
        log.debug("exa_search [%s/%s]: enriching %d URLs", sponsor_name, source_type, len(urls))
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(scraper, u): u for u in urls}
            for fut in as_completed(futures):
                scraped[futures[fut]] = fut.result()

    lines: list[str] = []
    for r in results.results:
        lines.append(f"Title: {r.title}\nURL: {r.url}")
        content = scraped.get(r.url)
        if content:
            lines.append(f"Full content:\n{content}")
        else:
            highlights = getattr(r, "highlights", None)
            if highlights:
                lines.append("Highlights:\n" + "\n".join(f"  - {h}" for h in highlights))
        lines.append("")

    return "\n".join(lines).strip() or "No results found."
