from __future__ import annotations

import asyncio
import logging
import time

from agents import Agent, Runner

from ..core.fallback import fallback_sponsor_profile, has_api_key
from ..core.fetch_urls import fetch_url_contents
from ..core.search import search_web_tool, search_web_urls

log = logging.getLogger(__name__)


INSTRUCTIONS = """
You are an expert developer-relations researcher for hackathon builders.

For the requested sponsor, search the web and produce a concise but evidence-backed
Markdown profile. Focus on what helps a builder decide whether and how to use this
sponsor in a hackathon project.

Include these sections:
1. Developer docs and main APIs/capabilities
2. Past hackathon tracks, prize language, or judging criteria
3. Canonical or hero use cases the sponsor showcases
4. What they appear to reward in winning projects
5. Source links

Prefer concrete evidence over broad marketing claims. If exact prize criteria are not
available, say so and summarize the nearest public evidence you found.
"""


sponsor_profiler_agent = Agent(
    name="SponsorProfiler",
    instructions=INSTRUCTIONS,
    tools=[search_web_tool],
)


async def profile_sponsor_task(sponsor: str, custom_urls: list[str] | None = None) -> str:
    if not has_api_key():
        log.info("sponsor_profiler [%s]: no API key — using fallback profile", sponsor)
        return fallback_sponsor_profile(sponsor)

    if custom_urls:
        log.info("sponsor_profiler [%s]: fetching %d custom URL(s)", sponsor, len(custom_urls))
        docs_content = await fetch_url_contents(custom_urls)
        prompt = (
            f"Custom documentation provided by the user:\n\n{docs_content}\n\n"
            f"Build a sponsor profile for {sponsor!r} using the documentation above. "
            "Also include past hackathon tracks, prize language, judging criteria, and source links where available."
        )
    else:
        urls = await asyncio.to_thread(
            search_web_urls, f"{sponsor} developer documentation official docs"
        )
        docs_content = await fetch_url_contents(urls) if urls else ""
        if docs_content:
            log.info("sponsor_profiler [%s]: pre-fetched %d URL(s) via DDG+Firecrawl", sponsor, len(urls))
            prompt = (
                f"Documentation fetched from the web:\n\n{docs_content}\n\n"
                f"Build a sponsor profile for {sponsor!r} using the documentation above. "
                "Also include past hackathon tracks, prize language, judging criteria, and source links where available."
            )
        else:
            log.info("sponsor_profiler [%s]: pre-fetch yielded nothing — agent will search directly", sponsor)
            prompt = (
                f"Build a sponsor profile for {sponsor!r}. "
                "Search for official docs, recent hackathon prize pages, examples, and developer-facing use cases."
            )

    log.info("sponsor_profiler [%s]: starting agent", sponsor)
    t0 = time.perf_counter()
    result = await Runner.run(sponsor_profiler_agent, prompt)
    profile = str(result.final_output)
    log.info("sponsor_profiler [%s]: done in %.1fs (%d chars)", sponsor, time.perf_counter() - t0, len(profile))
    return profile
