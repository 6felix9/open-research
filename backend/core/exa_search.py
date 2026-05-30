from __future__ import annotations

import logging
import os

from exa_py import Exa

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
    else:
        # X/Twitter is often paywalled; cast a wider net for community signals
        query = f"{sponsor_name} hackathon developer community award winner"
        kwargs = dict(num_results=5, contents={"highlights": True})

    log.debug("exa_search [%s/%s]: query=%r", sponsor_name, source_type, query)
    results = exa.search(query, **kwargs)

    lines: list[str] = []
    for r in results.results:
        lines.append(f"Title: {r.title}\nURL: {r.url}")
        highlights = getattr(r, "highlights", None)
        if highlights:
            lines.append("Highlights:\n" + "\n".join(f"  - {h}" for h in highlights))
        lines.append("")

    return "\n".join(lines).strip() or "No results found."
