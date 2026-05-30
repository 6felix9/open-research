from __future__ import annotations

import logging
import time

from agents import Agent, Runner, function_tool

from ..core.exa_search import exa_search_prior_art

log = logging.getLogger(__name__)


INSTRUCTIONS = """
You are a hackathon prior-art analyst. Given a sponsor name and their developer profile,
search Devpost and GitHub for past hackathon projects that used this sponsor.

Steps:
1. Call search_prior_art with source_type="devpost" to get Devpost project listings.
2. Call search_prior_art with source_type="github" to get GitHub repo metadata and README excerpts.
3. Synthesize a concise Markdown summary covering exactly these three points:

   **Winning problem categories** — What real-world problems do winning projects solve?
   **Technical crux** — How was this sponsor's technology integrated at its core?
   **Judge/community signals** — What reactions, metrics, or quotes indicate what impresses judges?

Keep the summary under 300 words. Be specific — quote project names and stats where available.
"""


def search_prior_art(sponsor_name: str, source_type: str) -> str:
    """Search Devpost or GitHub for hackathon prior art for this sponsor."""
    return exa_search_prior_art(sponsor_name, source_type)


_search_prior_art_tool = function_tool(search_prior_art)

prior_art_agent = Agent(
    name="PriorArtResearcher",
    instructions=INSTRUCTIONS,
    tools=[_search_prior_art_tool],
)


async def research_prior_art_task(sponsor_name: str, sponsor_profile: str) -> str:
    log.info("prior_art [%s]: starting agent (profile: %d chars)", sponsor_name, len(sponsor_profile))
    prompt = (
        f"Sponsor: {sponsor_name}\n\n"
        f"Sponsor profile summary:\n{sponsor_profile[:800]}\n\n"
        "Search Devpost and GitHub for prior hackathon projects that used this sponsor, "
        "then produce the three-point prior-art summary."
    )
    t0 = time.perf_counter()
    result = await Runner.run(prior_art_agent, prompt)
    summary = str(result.final_output)
    log.info("prior_art [%s]: done in %.1fs (%d chars)", sponsor_name, time.perf_counter() - t0, len(summary))
    return summary
