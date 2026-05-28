import asyncio
import logging

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

log = logging.getLogger(__name__)
from ..agents.sponsor_profiler import profile_sponsor_task
from ..agents.prior_art import research_prior_art_task
from ..agents.synthesizer import synthesize_task
from ..core.cache import cache_profile, get_cached_profile
from ..core.stream import sse

router = APIRouter()


def _parse_csv(value: str) -> list[str]:
    seen = set()
    items = []
    for raw_item in value.split(","):
        item = raw_item.strip()
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            items.append(item)
    return items


async def _generate(sponsors: str, interests: str, theme: str, seed: str, skills: str, time_budget: str, depth: int):
    sponsor_names = _parse_csv(sponsors)
    log.info(
        "research: request — sponsors=%s, interests=%s, theme=%r, seed=%r, skills=%s, budget=%s, depth=%d",
        sponsor_names, _parse_csv(interests), theme or "none", seed or "none",
        _parse_csv(skills), time_budget or "unset", depth,
    )
    sponsor_profiles = {}

    yield sse(
        "log",
        {
            "id": "parse",
            "step": "01 · INTAKE",
            "text": "Parsing brief with locked interest tags and sponsors.",
        },
    )

    if sponsor_names:
        yield sse(
            "log",
            {
                "id": "sponsor-landscape",
                "step": "02 · SPONSOR LANDSCAPE",
                "text": f"Checking sponsor profile cache for {len(sponsor_names)} sponsor(s).",
            },
        )
    else:
        yield sse(
            "log",
            {
                "id": "sponsor-landscape",
                "step": "02 · SPONSOR LANDSCAPE",
                "text": "No sponsors selected. Skipping Phase 1 sponsor profiling.",
            },
        )

    profile_tasks = {}
    for sponsor_name in sponsor_names:
        try:
            cached_profile = get_cached_profile(sponsor_name)
        except Exception as exc:
            cached_profile = None
            yield sse(
                "log",
                {
                    "id": f"{sponsor_name.lower()}-cache-error",
                    "step": "02 · SPONSOR LANDSCAPE",
                    "text": f"{sponsor_name}: cache unavailable ({exc}). Profiling dynamically.",
                },
            )

        if cached_profile:
            sponsor_profiles[sponsor_name] = cached_profile
            yield sse(
                "log",
                {
                    "id": f"{sponsor_name.lower()}-cache-hit",
                    "step": "02 · SPONSOR LANDSCAPE",
                    "text": f"{sponsor_name}: cache hit. Reusing stored sponsor profile.",
                },
            )
        else:
            yield sse(
                "log",
                {
                    "id": f"{sponsor_name.lower()}-profile-start",
                    "step": "02 · SPONSOR LANDSCAPE",
                    "text": f"{sponsor_name}: cache miss. Launching sponsor profiler agent.",
                },
            )
            task = asyncio.create_task(profile_sponsor_task(sponsor_name))
            profile_tasks[task] = sponsor_name

    while profile_tasks:
        done, _ = await asyncio.wait(profile_tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            sponsor_name = profile_tasks.pop(task)
            try:
                profile = task.result()
            except Exception as exc:
                yield sse(
                    "log",
                    {
                        "id": f"{sponsor_name.lower()}-profile-error",
                        "step": "02 · SPONSOR LANDSCAPE",
                        "text": f"{sponsor_name}: sponsor profiler failed ({exc}).",
                    },
                )
                continue

            sponsor_profiles[sponsor_name] = profile
            yield sse(
                "log",
                {
                    "id": f"{sponsor_name.lower()}-profile-complete",
                    "step": "02 · SPONSOR LANDSCAPE",
                    "text": f"{sponsor_name}: sponsor profile generated.",
                },
            )

            try:
                cache_profile(sponsor_name, profile)
            except Exception as exc:
                yield sse(
                    "log",
                    {
                        "id": f"{sponsor_name.lower()}-cache-write-error",
                        "step": "02 · SPONSOR LANDSCAPE",
                        "text": f"{sponsor_name}: profile generated but cache write failed ({exc}).",
                    },
                )
            else:
                yield sse(
                    "log",
                    {
                        "id": f"{sponsor_name.lower()}-cache-write",
                        "step": "02 · SPONSOR LANDSCAPE",
                        "text": f"{sponsor_name}: profile saved to cache.",
                    },
                )

    # Phase 2: Prior Art Scan
    prior_art_summaries: dict[str, str] = {}
    if sponsor_profiles:
        yield sse(
            "log",
            {
                "id": "prior-art-start",
                "step": "04 · PRIOR ART SCAN",
                "text": f"Searching Devpost and X for prior art across {len(sponsor_profiles)} sponsor(s).",
            },
        )

        prior_art_tasks: dict[asyncio.Task[str], str] = {}
        for sponsor_name, profile in sponsor_profiles.items():
            task = asyncio.create_task(research_prior_art_task(sponsor_name, profile))
            prior_art_tasks[task] = sponsor_name

        while prior_art_tasks:
            done, _ = await asyncio.wait(prior_art_tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                sponsor_name = prior_art_tasks.pop(task)
                try:
                    summary = task.result()
                except Exception as exc:
                    yield sse(
                        "log",
                        {
                            "id": f"{sponsor_name.lower()}-prior-art-error",
                            "step": "04 · PRIOR ART SCAN",
                            "text": f"{sponsor_name}: prior art scan failed ({exc}). Continuing without it.",
                        },
                    )
                    continue

                prior_art_summaries[sponsor_name] = summary
                yield sse(
                    "log",
                    {
                        "id": f"{sponsor_name.lower()}-prior-art-done",
                        "step": "04 · PRIOR ART SCAN",
                        "text": f"{sponsor_name}: prior art patterns extracted.",
                    },
                )

    # Phase 3: Synthesis
    yield sse(
        "log",
        {
            "id": "synthesize",
            "step": "05 · SYNTHESIS",
            "text": "Generating idea seeds from sponsor profiles and prior art.",
        },
    )

    interest_list = _parse_csv(interests)
    skill_list = _parse_csv(skills)

    try:
        result = await synthesize_task(
            sponsors=sponsor_names,
            interests=interest_list,
            theme=theme,
            seed=seed,
            skills=skill_list,
            time_budget=time_budget,
            sponsor_profiles=sponsor_profiles,
            prior_art_summaries=prior_art_summaries,
        )
        synergy_text = result.synergy
        ideas_payload = [idea.model_dump() for idea in result.ideas]
    except Exception as exc:
        yield sse(
            "log",
            {
                "id": "synthesize-error",
                "step": "05 · SYNTHESIS",
                "text": f"Synthesis failed ({exc}). No ideas generated.",
                "final": True,
            },
        )
        yield sse("done", {})
        return

    yield sse("synergy", {"text": synergy_text})

    n_ideas = len(ideas_payload)
    yield sse(
        "log",
        {
            "id": "complete",
            "step": "06 · COMPLETE",
            "text": f"{n_ideas} idea{'s' if n_ideas != 1 else ''} ready. Ordered by composite match score.",
            "final": True,
        },
    )

    yield sse("ideas", ideas_payload)
    yield sse("done", {})


@router.get("/research/stream")
async def stream_research(
    sponsors: str = "",
    interests: str = "",
    theme: str = "",
    seed: str = "",
    skills: str = "",
    time_budget: str = "",
    depth: int = 1,
):
    return EventSourceResponse(
        _generate(sponsors, interests, theme, seed, skills, time_budget, depth)
    )
