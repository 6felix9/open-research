from __future__ import annotations

from agents import Agent, Runner

from ..core.search import search_web_tool


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


async def profile_sponsor_task(sponsor: str) -> str:
    prompt = (
        f"Build a sponsor profile for {sponsor!r}. "
        "Search for official docs, recent hackathon prize pages, examples, and developer-facing use cases."
    )
    result = await Runner.run(sponsor_profiler_agent, prompt)
    return str(result.final_output)
