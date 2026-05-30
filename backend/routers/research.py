"""
research.py — sole public API endpoint for the Open Research pipeline.

GET /api/research/stream returns a Server-Sent Events stream driven by the
_generate() async generator below. All three pipeline phases run inside that
generator; the client receives live log events as each step completes, then
a final `ideas` event with the ranked results.

Phase flow (sequential, phases 1 & 2 parallel per-sponsor internally):
  01 · INTAKE            — parse and validate input
  02 · SPONSOR LANDSCAPE — profile each sponsor (Phase 1)
  04 · PRIOR ART SCAN    — scan Devpost/X per sponsor (Phase 2)
  05 · SYNTHESIS         — generate ranked idea briefs (Phase 3)
  06 · COMPLETE          — emit ideas + done
"""

import asyncio
import logging
import os

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

log = logging.getLogger(__name__)
from ..agents.sponsor_profiler import profile_sponsor_task
from ..agents.prior_art import research_prior_art_task
from ..agents.synthesizer import synthesize_task
from ..core.cache import cache_profile, get_cached_profile, normalize_sponsor_name
from ..core.stream import sse

router = APIRouter()

_REQUIRED_KEYS = ["OPENAI_API_KEY", "EXA_API_KEY", "FIRECRAWL_API_KEY", "JINA_API_KEY", "GITHUB_TOKEN"]


@router.get("/config/keys")
async def get_config_keys() -> dict[str, bool]:
    return {k: bool(os.getenv(k)) for k in _REQUIRED_KEYS}


def _url_matches_sponsor(url: str, sponsor_name: str) -> bool:
    """Return True if url's hostname suggests it belongs to sponsor_name.

    Strips common subdomains (www, docs, api, …) then checks whether the
    remaining root token appears inside the normalized sponsor name or vice
    versa.  Used to decide whether a user-supplied custom URL is likely
    documentation for the current sponsor, so we can serve a cached profile
    instead of re-scraping.

    Examples:
        "https://docs.supabase.com/..."  + "Supabase"  → True
        "https://platform.openai.com/"  + "Groq"       → False
    """
    from urllib.parse import urlparse
    try:
        hostname = urlparse(url).hostname or ""
    except Exception:
        return False
    parts = hostname.split(".")
    # Strip common subdomains so "docs.supabase.com" → ["supabase", "com"]
    skip = {"www", "docs", "api", "developers", "dev", "help", "support"}
    while parts and parts[0] in skip:
        parts = parts[1:]
    root = normalize_sponsor_name(parts[0]) if parts else ""
    norm_sponsor = normalize_sponsor_name(sponsor_name)
    return bool(root) and (root in norm_sponsor or norm_sponsor in root)


def _parse_csv(value: str) -> list[str]:
    """Split a comma-separated string into a deduplicated list, preserving order.

    Deduplication is case-insensitive but the original casing is kept.
    Empty tokens (e.g. from a trailing comma) are dropped.
    """
    seen = set()
    items = []
    for raw_item in value.split(","):
        item = raw_item.strip()
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            items.append(item)
    return items


async def _generate(sponsors: str, interests: str, theme: str, seed: str, skills: str, time_budget: str, depth: int, custom_sponsor_urls: str = ""):
    """Async generator that drives the full three-phase research pipeline.

    Yields SSE-formatted dicts (via `sse()`) as each step completes so the
    client receives live progress without waiting for the full run.

    Phase 1 — Sponsor Profiling
        All sponsor profile tasks are launched concurrently with
        asyncio.create_task before any are awaited.  Results are collected
        with asyncio.wait(FIRST_COMPLETED) so a log event fires as soon as
        each individual profile is ready rather than waiting for the slowest.

        Cache logic (per sponsor):
          - No custom URLs → check ChromaDB; hit = skip agent task entirely.
          - Custom URLs provided + hostname matches sponsor → check ChromaDB;
            hit = skip scraping, use cached profile.
          - Custom URLs provided but no match, or cache miss → spawn
            profile_sponsor_task(sponsor, custom_url_list).
        All generated profiles (custom or not) are written back to ChromaDB.

    Phase 2 — Prior Art Scan
        Same concurrency pattern as Phase 1.  Skipped entirely if Phase 1
        produced no profiles.

    Phase 3 — Synthesis
        Single sequential call.  Skipped if synthesis raises; emits error log
        + done in that case so the client can clean up.
    """
    sponsor_names = _parse_csv(sponsors)
    log.info(
        "research: request — sponsors=%s, interests=%s, theme=%r, seed=%r, skills=%s, budget=%s, depth=%d",
        sponsor_names, _parse_csv(interests), theme or "none", seed or "none",
        _parse_csv(skills), time_budget or "unset", depth,
    )
    sponsor_profiles = {}

    # ------------------------------------------------------------------ #
    # 01 · INTAKE                                                          #
    # ------------------------------------------------------------------ #
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

    # ------------------------------------------------------------------ #
    # 02 · SPONSOR LANDSCAPE  (Phase 1)                                   #
    # Launch all profile tasks before awaiting any of them so they run    #
    # concurrently.  profile_tasks maps Task → sponsor_name for lookup    #
    # when results come in.                                                #
    # ------------------------------------------------------------------ #
    custom_url_list = _parse_csv(custom_sponsor_urls)
    profile_tasks = {}
    for sponsor_name in sponsor_names:
        if custom_url_list:
            # If any custom URL looks like it belongs to this sponsor, try
            # the cache before committing to a Firecrawl scrape.
            matching_urls = [u for u in custom_url_list if _url_matches_sponsor(u, sponsor_name)]
            if matching_urls:
                try:
                    cached_profile = get_cached_profile(sponsor_name)
                except Exception:
                    cached_profile = None
                if cached_profile:
                    sponsor_profiles[sponsor_name] = cached_profile
                    yield sse(
                        "log",
                        {
                            "id": f"{sponsor_name.lower()}-cache-hit",
                            "step": "02 · SPONSOR LANDSCAPE",
                            "text": f"{sponsor_name}: custom URL matches cached sponsor — using fresh cache.",
                        },
                    )
                    continue
            # No matching cache entry — scrape the custom URLs directly.
            yield sse(
                "log",
                {
                    "id": f"{sponsor_name.lower()}-profile-start",
                    "step": "02 · SPONSOR LANDSCAPE",
                    "text": f"{sponsor_name}: custom docs provided — scraping {len(custom_url_list)} URL(s).",
                },
            )
            task = asyncio.create_task(profile_sponsor_task(sponsor_name, custom_url_list))
            profile_tasks[task] = sponsor_name
            continue

        # Standard path: check ChromaDB, skip the agent task on a fresh hit.
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

    # Drain completed tasks one at a time so we can emit log events as each
    # profile finishes rather than waiting for the full batch.
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

            # Write back to cache regardless of whether custom URLs were used.
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

    # ------------------------------------------------------------------ #
    # 04 · PRIOR ART SCAN  (Phase 2)                                      #
    # Same concurrency pattern as Phase 1.  Skipped if no profiles.       #
    # ------------------------------------------------------------------ #
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

    # ------------------------------------------------------------------ #
    # 05 · SYNTHESIS  (Phase 3)                                           #
    # Single sequential call — no parallelism needed here.                #
    # ------------------------------------------------------------------ #
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


@router.get("/config/keys")
async def get_config_keys():
    """Return whether each required API key/token is configured in the environment."""
    return {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "EXA_API_KEY": bool(os.getenv("EXA_API_KEY")),
        "FIRECRAWL_API_KEY": bool(os.getenv("FIRECRAWL_API_KEY")),
        "JINA_API_KEY": bool(os.getenv("JINA_API_KEY")),
        "GITHUB_TOKEN": bool(os.getenv("GITHUB_TOKEN")),
    }


@router.get("/research/stream")
async def stream_research(
    sponsors: str = "",
    interests: str = "",
    theme: str = "",
    seed: str = "",
    skills: str = "",
    time_budget: str = "",
    depth: int = 1,
    custom_sponsor_urls: str = "",
):
    """Stream the research pipeline as Server-Sent Events.

    Validates required params and API keys, then hands off to _generate()
    which yields SSE dicts consumed by EventSourceResponse.
    """
    if not _parse_csv(sponsors):
        raise HTTPException(status_code=422, detail="sponsors is required")
    if not theme.strip():
        raise HTTPException(status_code=422, detail="theme is required")

    required_keys = ["OPENAI_API_KEY", "EXA_API_KEY", "FIRECRAWL_API_KEY", "JINA_API_KEY", "GITHUB_TOKEN"]
    missing_keys = [k for k in required_keys if not os.getenv(k)]
    if missing_keys:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required environment variables: {', '.join(missing_keys)}"
        )

    return EventSourceResponse(
        _generate(sponsors, interests, theme, seed, skills, time_budget, depth, custom_sponsor_urls)
    )
