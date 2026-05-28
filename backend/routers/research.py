import asyncio
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from ..agents.sponsor_profiler import profile_sponsor_task
from ..core.cache import cache_profile, get_cached_profile
from ..core.stream import sse

router = APIRouter()

_LOGS = [
    {"id": "parse", "step": "01 · INTAKE", "text": 'Parsing brief with locked interest tags and sponsors.'},
    {"id": "sponsors", "step": "02 · SPONSOR LANDSCAPE", "text": "Mapping each sponsor's incentive structure against the brief…"},
    {"id": "groq-insight", "step": "03 · INSIGHT", "quote": "Groq tends to reward latency-sensitive flows — anything where a conversational loop or a real-time decision is the demo moment. Pair with voice or live data and the prize odds spike."},
    {"id": "prior-art", "step": "04 · PRIOR ART SCAN", "text": "Searching Devpost, HF Spaces, Show HN and recent winners. Filtering for projects that align to brief but leave headroom."},
    {"id": "anthropic-insight", "step": "05 · INSIGHT", "quote": "Long-context plus Computer Use is being underused in hackathon submissions — judges have seen six chatbots. A computer-use agent that finishes a real task on screen is still rare."},
    {"id": "synthesize", "step": "06 · SYNTHESIS", "text": "Generating idea seeds — biasing toward tight scope, sponsor stack-compatibility, and one moment of demo theatre."},
    {"id": "rank", "step": "07 · RANKING", "text": "Scoring 14 candidates on novelty × sponsor-fit × buildability × demo legibility. Discarding 6 below threshold."},
    {"id": "ship", "step": "08 · COMPLETE", "text": "8 ideas ready. Ordered by composite match. Prior-art links attached where citable.", "final": True},
]

_SYNERGY = "Three of your selected sponsors (Groq + ElevenLabs + Supabase) tend to combine in winning entries — the realtime voice triangle. 2 of the top 5 ideas use this stack."

_IDEAS = [
    {
        "id": "i1",
        "title": "Standup, but it's an agent that already ran it",
        "pitch": "Voice agent dials each teammate at their preferred hour, holds a 90-second async standup, transcribes blockers into a Linear-style board, and posts the digest to Slack before the human standup would have started.",
        "stack": ["groq", "elevenlabs", "supabase"],
        "match": 94,
        "breakdown": {"sponsor": 38, "interest": 34, "novelty": 22},
        "difficulty": 2,
        "priorArt": {"title": "Bumblebee — async voice retros for distributed teams", "meta": "Devpost · MLH Fellowship Showcase '24 · 312★", "url": "#"},
        "why": "Three sponsors stack cleanly: Groq does the latency floor, ElevenLabs sells the demo, Supabase carries state. Cross-checked against 4 standup tools — none use a real outbound voice loop.",
        "risks": "Telephony auth is finicky. Have a fallback to browser-mic if Twilio numbers don't come through.",
        "demoMoment": "Live-call a judge's phone during the pitch. They hear the agent. They answer.",
    },
    {
        "id": "i2",
        "title": "Receipt-driven warranty agent",
        "pitch": "Snap a photo of any receipt. The agent extracts the SKU, looks up the warranty terms, files a calendar entry for the expiry, and offers to draft the claim email the day before something breaks down.",
        "stack": ["anthropic", "modal"],
        "match": 87,
        "breakdown": {"sponsor": 30, "interest": 32, "novelty": 25},
        "difficulty": 2,
        "priorArt": {"title": "Stash — automated proof-of-purchase wallet", "meta": "Hacker News · 2023 · YC W23 batch", "url": "#"},
        "why": "Computer-use angle: the agent actually navigates the manufacturer's claim form on demo. That's the moment.",
        "risks": "OCR on creased receipts is a long tail. Cache the 50 most common retailers.",
        "demoMoment": "On stage, agent files a real warranty claim against a $3 mug. Watch the form fill itself.",
    },
    {
        "id": "i3",
        "title": "PR-review agent that explains itself in the diff",
        "pitch": "GitHub app. On every PR it leaves inline comments backed by a graph of the codebase — but each comment links to the exact training examples or docs that informed the suggestion. Auditable AI review.",
        "stack": ["anthropic", "pinecone", "vercel"],
        "match": 82,
        "breakdown": {"sponsor": 32, "interest": 30, "novelty": 20},
        "difficulty": 3,
        "priorArt": {"title": "Greptile · CodeRabbit — automated PR review", "meta": "Devpost YC AI '24 · 4 finalists", "url": "#"},
        "why": "The 'cite your sources' angle is what's missing in the space. Judges from Anthropic care about interpretability.",
        "risks": "Building the codebase graph eats time. Use tree-sitter + cache aggressively.",
        "demoMoment": "Click a comment → side panel scrolls to the exact 12 lines that informed it. The 'aha'.",
    },
    {
        "id": "i4",
        "title": "A debugger that runs your code in 1000 alternate universes",
        "pitch": "Pin a failing test. The agent forks the repo across Modal containers, mutates input combinatorially, and shows you the failure boundary as a 2D heatmap. Not 'what broke' — 'where the cliff is.'",
        "stack": ["modal", "anthropic"],
        "match": 79,
        "breakdown": {"sponsor": 28, "interest": 28, "novelty": 23},
        "difficulty": 3,
        "priorArt": {"title": "Hypothesis · property-based testing", "meta": "PyCon talk · 2023 · OSS adoption growing", "url": "#"},
        "why": "Modal's per-request GPUs make this economically possible. Hard to demo casually — but the heatmap is gorgeous.",
        "risks": "Combinatorial explosion. Need a smart pruning strategy or you'll burn through credits.",
        "demoMoment": "Heatmap renders live. A coastline of failure. Audience leans in.",
    },
    {
        "id": "i5",
        "title": "Voice-first onboarding for any SaaS",
        "pitch": "Drop a script tag. First-time users hear a real voice greet them by context and walk them through setup as a 60-second conversation instead of a 12-step tour.",
        "stack": ["elevenlabs", "vercel", "groq"],
        "match": 76,
        "breakdown": {"sponsor": 30, "interest": 26, "novelty": 20},
        "difficulty": 2,
        "priorArt": {"title": "Userpilot · Pendo — guided product tours", "meta": "G2 category · $200M+ ARR space", "url": "#"},
        "why": "Conversational onboarding is the next category. Three sponsor stack lights up.",
        "risks": "Voice in B2B is contentious. Make it opt-in and toggleable, not in-your-face.",
        "demoMoment": "Live demo: visit a fake SaaS, the agent greets the judge by name from the QR they scanned.",
    },
    {
        "id": "i6",
        "title": "Synthetic users for usability tests",
        "pitch": "Upload your Figma. The agent simulates 30 personas — each with their own goals, accessibility needs, and friction tolerance — clicking through the prototype and writing heatmap-style critiques.",
        "stack": ["anthropic", "modal", "pinecone"],
        "match": 73,
        "breakdown": {"sponsor": 26, "interest": 27, "novelty": 20},
        "difficulty": 3,
        "priorArt": {"title": "Maze · UserTesting — remote usability testing", "meta": "Devpost · multiple AI-UX projects '24", "url": "#"},
        "why": "Replaces a real-money process. Demo is visual. Computer-use clicks through your Figma prototype on stage.",
        "risks": "Persona fidelity matters — generic personas will read as fake. Ground them in real survey data.",
        "demoMoment": "Upload audience's own Figma, replay 5 personas trying to check out. Two get stuck on the same modal.",
    },
    {
        "id": "i7",
        "title": "Background-research worker that ships citations to your inbox",
        "pitch": "An always-on Modal worker watching your calendar. 30 min before each meeting it scrapes attendees' recent writing, pinned posts, and one surprising public fact — delivered as a one-pager with footnotes.",
        "stack": ["modal", "mistral", "supabase"],
        "match": 71,
        "breakdown": {"sponsor": 27, "interest": 24, "novelty": 20},
        "difficulty": 2,
        "priorArt": {"title": "Clay · Common Room — relationship intelligence", "meta": "Y Combinator '23 · prod-market fit", "url": "#"},
        "why": "Open-source model angle keeps it cheap. Mistral fine-tune on summary style is a credible prize hook.",
        "risks": "Privacy optics. Hard-cap to public data and put consent gating front and center.",
        "demoMoment": "Pull up a one-pager about a judge using only their public footprint. Land one specific detail.",
    },
    {
        "id": "i8",
        "title": "Music-theory tutor that hears you play",
        "pitch": "Browser-only. Pick an instrument, play. The agent listens, transcribes the line, and explains what scale you're improvising in — and what one note would surprise you. Built for learners who can't read sheet music.",
        "stack": ["groq", "vercel"],
        "match": 68,
        "breakdown": {"sponsor": 24, "interest": 24, "novelty": 20},
        "difficulty": 2,
        "priorArt": {"title": "Yousician · Soundslice — interactive music ed", "meta": "Indie space · multiple winners at MIT MusicHack", "url": "#"},
        "why": "Latency is the product. Groq wins or this doesn't ship. Vercel's streaming primitives make the UI feel alive.",
        "risks": "Pitch detection in noisy rooms is hard. Demo in a treated room or use a direct line-in.",
        "demoMoment": "Play 4 bars. The screen highlights the implied chord. Suggests the surprising note. You play it.",
    },
]


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

    yield sse(
        "log",
        {
            "id": "phase-1-complete",
            "step": "03 · PHASE 1 COMPLETE",
            "text": f"{len(sponsor_profiles)} sponsor profile(s) ready. Downstream idea generation is still using the Phase 1 mock payload.",
            "final": True,
        },
    )

    yield sse("synergy", {"text": _SYNERGY})
    await asyncio.sleep(0.3)

    yield sse("ideas", _IDEAS)
    await asyncio.sleep(0.1)

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
