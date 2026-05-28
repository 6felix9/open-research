from __future__ import annotations

from typing import Literal

from agents import Agent, Runner
from pydantic import BaseModel

from ..core.fallback import fallback_synthesis, has_api_key


class Breakdown(BaseModel):
    sponsor: int
    interest: int
    novelty: int


class PriorArtRef(BaseModel):
    title: str
    meta: str
    url: str = "#"


class IdeaBrief(BaseModel):
    id: str
    title: str
    pitch: str
    stack: list[str]
    match: int
    breakdown: Breakdown
    difficulty: Literal[1, 2, 3]
    priorArt: PriorArtRef
    why: str
    risks: str
    demoMoment: str


class SynthesisResult(BaseModel):
    synergy: str
    ideas: list[IdeaBrief]


INSTRUCTIONS = """
You are a hackathon idea synthesizer. Given user preferences, sponsor profiles, and prior-art
summaries, generate 5–8 original hackathon idea briefs ranked by match score.

Rules:
- `stack` must only contain sponsor IDs from the provided sponsor list (lowercase).
- `breakdown.sponsor + breakdown.interest + breakdown.novelty` must equal `match` exactly.
- `match` range: 65–95. Order ideas from highest to lowest.
- `difficulty`: 1=easy (fits 24h, frontend/backend skills), 2=medium, 3=hard (ML/infra heavy or 48h+).
  Scale difficulty to the team's stated skills and time budget.
- `priorArt.title` must reference a real-sounding project from the prior-art data provided.
- `priorArt.meta` should include platform (Devpost / HN / X), year, and one metric (stars, prize, rank).
- Ideas must be novel relative to the prior art — don't clone a winning project, find the gap.
- `why` should cite specific sponsor capabilities that make this idea viable *right now*.
- `demoMoment` must describe a single, concrete, show-don't-tell moment (30 seconds max).
- `synergy` is 1–2 sentences describing the most interesting sponsor combination across the ideas.
- `id` values: "i1", "i2", … in match-score order.
"""


synthesizer_agent = Agent(
    name="Synthesizer",
    instructions=INSTRUCTIONS,
    output_type=SynthesisResult,
)


async def synthesize_task(
    sponsors: list[str],
    interests: list[str],
    theme: str,
    seed: str,
    skills: list[str],
    time_budget: str,
    sponsor_profiles: dict[str, str],
    prior_art_summaries: dict[str, str],
) -> SynthesisResult:
    if not has_api_key():
        return fallback_synthesis(sponsors, interests, theme, seed, skills, time_budget)  # type: ignore[return-value]
    profiles_block = "\n\n".join(
        f"### {name}\n{text[:600]}" for name, text in sponsor_profiles.items()
    ) or "No sponsor profiles available."

    prior_art_block = "\n\n".join(
        f"### {name} prior art\n{text}" for name, text in prior_art_summaries.items()
    ) or "No prior-art data available."

    prompt = f"""
USER BRIEF
----------
Sponsors (use only these IDs in stack): {', '.join(sponsors) or 'none'}
Interests: {', '.join(interests) or 'none'}
Theme: {theme or 'none'}
Seed idea / constraint: {seed or 'none'}
Team skills: {', '.join(skills) or 'not specified'}
Time budget: {time_budget or 'not specified'}

SPONSOR PROFILES
----------------
{profiles_block}

PRIOR ART SUMMARIES
-------------------
{prior_art_block}

Generate 5–8 original hackathon ideas following the output schema.
"""
    result = await Runner.run(synthesizer_agent, prompt)
    return result.final_output
