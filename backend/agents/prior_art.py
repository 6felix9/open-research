from __future__ import annotations

from agents import Agent, Runner

from ..core.mock_search import mock_search_prior_art_tool


INSTRUCTIONS = """
You are a hackathon prior-art analyst. Given a sponsor name and their developer profile,
search both Devpost and X (Twitter) for past hackathon projects that used this sponsor.

Steps:
1. Call mock_search_prior_art with source_type="devpost" to get Devpost project listings.
2. Call mock_search_prior_art with source_type="x" to get X/Twitter posts and hype signals.
3. Synthesize a concise Markdown summary covering exactly these three points:

   **Winning problem categories** — What real-world problems do winning projects solve?
   **Technical crux** — How was this sponsor's technology integrated at its core?
   **Judge/community signals** — What reactions, metrics, or quotes indicate what impresses judges?

Keep the summary under 300 words. Be specific — quote project names and stats where available.
"""


prior_art_agent = Agent(
    name="PriorArtResearcher",
    instructions=INSTRUCTIONS,
    tools=[mock_search_prior_art_tool],
)


async def research_prior_art_task(sponsor_name: str, sponsor_profile: str) -> str:
    prompt = (
        f"Sponsor: {sponsor_name}\n\n"
        f"Sponsor profile summary:\n{sponsor_profile[:800]}\n\n"
        "Search Devpost and X for prior hackathon projects that used this sponsor, "
        "then produce the three-point prior-art summary."
    )
    result = await Runner.run(prior_art_agent, prompt)
    return str(result.final_output)
