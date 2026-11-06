from __future__ import annotations

import logging
import os
import time
from typing import Literal

from openai import AsyncOpenAI
from pydantic import BaseModel

log = logging.getLogger(__name__)

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")


class Breakdown(BaseModel):
    sponsor: int
    interest: int
    novelty: int


class PriorArtRef(BaseModel):
    title: str
    meta: str
    url: str


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
entries, generate 5–8 original hackathon idea briefs ranked by match score.

Rules:
- `stack` must only contain sponsor IDs from the provided sponsor list (lowercase).
- `breakdown` ranges: sponsor fit 25–40, interest fit 20–30, novelty 20–25. Set `match` to their sum,
  so `match` always lands between 65 and 95. Use the full range to separate strong ideas from weak ones.
  Order ideas from highest to lowest `match`.
- `difficulty`: 1=easy (fits 24h, frontend/backend skills), 2=medium, 3=hard (ML/infra heavy or 48h+).
  Scale difficulty to the team's stated skills and time budget.
- `priorArt` must be copied verbatim (title, meta, url) from one entry in the PRIOR ART lists.
  Pick the entry closest to the idea. Never invent a project.
- Ideas must be novel relative to the prior art — don't clone a winning project, find the gap.
- `why` should cite specific sponsor capabilities from the profiles that make this idea viable *right now*.
- `demoMoment` must describe a single, concrete, show-don't-tell moment (30 seconds max).
- `synergy` is 1–2 sentences describing the most interesting sponsor combination across the ideas.
- `id` values: "i1", "i2", … in match order.
"""


def _build_prompt(
    sponsors: list[str],
    interests: list[str],
    theme: str,
    seed: str,
    skills: list[str],
    time_budget: str,
    corpus: dict[str, dict],
    custom_docs: str,
) -> str:
    context = []
    for sponsor_id, snap in corpus.items():
        lines = [f"### {snap['name']} (id: {sponsor_id}, snapshot {snap['updated']})", snap["profile"], "", "PRIOR ART:"]
        for p in snap["prior_art"]:
            lines.append(f"- {p['title']} | {p['meta']} | {p['url']}\n  {p['excerpt']}")
        context.append("\n".join(lines))
    if custom_docs:
        context.append(f"### User-supplied docs\n{custom_docs}")

    return f"""
USER BRIEF
----------
Sponsors (use only these IDs in stack): {', '.join(sponsors) or 'none'}
Interests: {', '.join(interests) or 'none'}
Theme: {theme or 'none'}
Seed idea / constraint: {seed or 'none'}
Team skills: {', '.join(skills) or 'not specified'}
Time budget: {time_budget or 'not specified'}

SPONSOR RESEARCH
----------------
{chr(10).join(context) or 'No research data available.'}

Generate 5–8 original hackathon ideas following the output schema.
"""


def _finalize(result: SynthesisResult, corpus: dict[str, dict]) -> SynthesisResult:
    """Make the model's output trustworthy where code can: citations, scores, order, ids."""
    refs = {
        p["url"]: PriorArtRef(title=p["title"], meta=p["meta"], url=p["url"])
        for snap in corpus.values()
        for p in snap["prior_art"]
    }
    for idea in result.ideas:
        ref = refs.get(idea.priorArt.url)
        if ref:
            idea.priorArt = ref
        else:
            log.warning("synthesizer: %r cited a prior-art url not in the corpus", idea.title)
            idea.priorArt.url = "#"
        b = idea.breakdown
        idea.match = min(100, b.sponsor + b.interest + b.novelty)
    result.ideas.sort(key=lambda i: -i.match)
    for n, idea in enumerate(result.ideas, 1):
        idea.id = f"i{n}"
    return result


async def synthesize_task(
    *,
    api_key: str,
    sponsors: list[str],
    interests: list[str],
    theme: str,
    seed: str,
    skills: list[str],
    time_budget: str,
    corpus: dict[str, dict],
    custom_docs: str,
) -> SynthesisResult:
    log.info("synthesizer: starting (sponsors=%s, corpus=%d, custom_docs=%d chars)", sponsors, len(corpus), len(custom_docs))
    prompt = _build_prompt(sponsors, interests, theme, seed, skills, time_budget, corpus, custom_docs)
    client = AsyncOpenAI(api_key=api_key)
    t0 = time.perf_counter()
    completion = await client.chat.completions.parse(
        model=MODEL,
        messages=[{"role": "system", "content": INSTRUCTIONS}, {"role": "user", "content": prompt}],
        response_format=SynthesisResult,
    )
    message = completion.choices[0].message
    if message.parsed is None:
        raise RuntimeError(message.refusal or "model returned no structured output")
    result = _finalize(message.parsed, corpus)
    log.info("synthesizer: done in %.1fs (%d ideas)", time.perf_counter() - t0, len(result.ideas))
    return result
