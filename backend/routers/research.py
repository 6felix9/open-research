"""
research.py — public API for the Open Research pipeline.

GET  /api/config           tells the frontend whether the server has its own OpenAI key.
POST /api/research/stream  streams the pipeline as Server-Sent Events.

Pipeline (all per-sponsor research comes from the committed snapshot corpus, so a run is
one LLM call):
  01 · INTAKE            — validate the brief
  02 · SPONSOR LANDSCAPE — load each sponsor's snapshot (+ any user-supplied docs)
  03 · PRIOR ART SCAN    — report the prior art in those snapshots
  04 · SYNTHESIS         — generate ranked idea briefs
  05 · COMPLETE          — emit ideas + done
"""

import logging
import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from ..agents.synthesizer import synthesize_task
from ..core.corpus import fetch_docs, load_sponsor
from ..core.stream import sse

log = logging.getLogger(__name__)

router = APIRouter()


class ResearchRequest(BaseModel):
    sponsors: list[str]
    theme: str
    interests: list[str] = []
    seed: str = ""
    skills: list[str] = []
    time_budget: str = ""
    custom_sponsor_urls: list[str] = []


@router.get("/config")
async def get_config() -> dict[str, bool]:
    return {"server_key": bool(os.getenv("OPENAI_API_KEY"))}


async def _generate(req: ResearchRequest, sponsors: list[str], api_key: str):
    log.info("research: sponsors=%s, theme=%r, custom_urls=%d", sponsors, req.theme, len(req.custom_sponsor_urls))

    yield sse("log", {
        "id": "parse",
        "step": "01 · INTAKE",
        "text": "Parsing brief with locked interest tags and sponsors.",
    })

    # 02 · SPONSOR LANDSCAPE
    corpus: dict[str, dict] = {}
    for sponsor_id in sponsors:
        snap = load_sponsor(sponsor_id)
        if snap is None:
            yield sse("log", {
                "id": f"{sponsor_id}-profile-missing",
                "step": "02 · SPONSOR LANDSCAPE",
                "text": f"{sponsor_id}: no research snapshot available. Continuing without it.",
                "error": True,
            })
            continue
        corpus[sponsor_id] = snap
        yield sse("log", {
            "id": f"{sponsor_id}-profile",
            "step": "02 · SPONSOR LANDSCAPE",
            "text": f"{snap['name']}: sponsor profile loaded (snapshot {snap['updated']}).",
        })

    custom_docs = ""
    if req.custom_sponsor_urls:
        yield sse("log", {
            "id": "custom-docs",
            "step": "02 · SPONSOR LANDSCAPE",
            "text": f"Fetching {min(len(req.custom_sponsor_urls), 5)} user-supplied docs page(s).",
        })
        custom_docs = await fetch_docs(req.custom_sponsor_urls)
        if not custom_docs:
            yield sse("log", {
                "id": "custom-docs-error",
                "step": "02 · SPONSOR LANDSCAPE",
                "text": "Could not read any of the supplied docs URLs. Continuing without them.",
                "error": True,
            })

    if not corpus and not custom_docs:
        yield sse("log", {
            "id": "no-research",
            "step": "02 · SPONSOR LANDSCAPE",
            "text": "No research data for the selected sponsors. Nothing to synthesize.",
            "final": True,
            "error": True,
        })
        yield sse("done", {})
        return

    # 03 · PRIOR ART SCAN
    for sponsor_id, snap in corpus.items():
        counts: dict[str, int] = {}
        for p in snap["prior_art"]:
            counts[p["source"]] = counts.get(p["source"], 0) + 1
        found = ", ".join(f"{n} {src}" for src, n in counts.items()) or "no"
        yield sse("log", {
            "id": f"{sponsor_id}-prior-art",
            "step": "03 · PRIOR ART SCAN",
            "text": f"{snap['name']}: {found} prior-art project(s) on file.",
        })

    # 04 · SYNTHESIS
    yield sse("log", {
        "id": "synthesize",
        "step": "04 · SYNTHESIS",
        "text": "Generating idea seeds from sponsor profiles and prior art.",
    })

    try:
        result = await synthesize_task(
            api_key=api_key,
            sponsors=sponsors,
            interests=req.interests,
            theme=req.theme,
            seed=req.seed,
            skills=req.skills,
            time_budget=req.time_budget,
            corpus=corpus,
            custom_docs=custom_docs,
        )
    except Exception as exc:
        yield sse("log", {
            "id": "synthesize-error",
            "step": "04 · SYNTHESIS",
            "text": f"Synthesis failed ({exc}). No ideas generated.",
            "final": True,
            "error": True,
        })
        yield sse("done", {})
        return

    yield sse("synergy", {"text": result.synergy})

    n_ideas = len(result.ideas)
    yield sse("log", {
        "id": "complete",
        "step": "05 · COMPLETE",
        "text": f"{n_ideas} idea{'s' if n_ideas != 1 else ''} ready. Ordered by composite match score.",
        "final": True,
    })

    yield sse("ideas", [idea.model_dump() for idea in result.ideas])
    yield sse("done", {})


@router.post("/research/stream")
async def stream_research(req: ResearchRequest, x_openai_key: str | None = Header(default=None)):
    """Stream the research pipeline as Server-Sent Events.

    The OpenAI key comes from the X-OpenAI-Key header (bring-your-own-key) or, failing that,
    the server's OPENAI_API_KEY. It is never logged or stored.
    """
    sponsors = list(dict.fromkeys(s.strip().lower() for s in req.sponsors if s.strip()))
    if not sponsors:
        raise HTTPException(status_code=422, detail="sponsors is required")
    if not req.theme.strip():
        raise HTTPException(status_code=422, detail="theme is required")

    api_key = (x_openai_key or "").strip() or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=422,
            detail="No OpenAI API key: set OPENAI_API_KEY on the server or send your own in X-OpenAI-Key.",
        )

    return EventSourceResponse(_generate(req, sponsors, api_key))
