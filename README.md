# Open Research

An agentic ideation tool for hackathons. You give it your sponsors, your interests, and your stack. It does three hours of research in under a minute and hands you an opinionated shortlist — ranked ideas with rationale, prior art citations, and a concrete demo moment. Not a brainstorm. A brief you can commit to.

---

## What it does

Most hackathon ideation is wasted time: generic ideas that don't use sponsors well, prize tracks you didn't know existed, wheel-reinventing that a quick Devpost search would have prevented. Open Research fixes the research layer — the part that takes the most time and produces the least signal when done manually.

The pipeline has three phases, each streaming progress to the frontend in real time:

**Phase 1 — Sponsor Profiling** (parallel)

One agent per sponsor. Each one searches for the sponsor's developer docs, past hackathon tracks, prize criteria, and canonical use cases. The goal is understanding what a sponsor *actually rewards*, not just what their landing page says. Results are cached — if you've run Supabase before, Phase 1 for Supabase is instant.

**Phase 2 — Prior Art**

Searches Devpost and GitHub for past projects that used each sponsor. Extracts the pattern: what problem category won, what the technical crux was, what made judges or the community care. This is the part most people skip and most often regret skipping.

**Phase 3 — Synthesis**

Cross-references your interests and stack against sponsor capabilities and winning patterns. Generates 5–8 idea briefs, each with:
- A one-line idea
- Why this sponsor scores you points specifically
- A prior art reference (what proved the pattern works)
- The technical crux (what you'd actually have to build)
- Feasibility given your stated stack

---

## Architecture

```
[User Input]
  Sponsors: [Browserbase, Supabase, Groq]
  Interests: WebRTC, real-time apps
  Stack: Python, React
  Theme: "AI productivity tools"
        │
        ▼
┌─────────────────────────────────────────┐
│    PHASE 1: Sponsor Profiling           │
│           (parallel agents)             │
│                                         │
│  Agent(Browserbase) → profile + prizes  │
│  Agent(Supabase)    → profile + prizes  │
│  Agent(Groq)        → profile + prizes  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│    PHASE 2: Prior Art Research          │
│                                         │
│  Search Devpost + GitHub per sponsor    │
│  Extract: problem category, tech used,  │
│           judge/community signals       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│    PHASE 3: Synthesis                   │
│                                         │
│  user interests ∩ sponsor capabilities  │
│  ∩ winning patterns → ranked briefs     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
            [Rendered Briefs]
```

### Tech stack

| Layer | Choice | Reason |
|---|---|---|
| Frontend | React + Vite | Fast dev loop, SSE works cleanly |
| Backend | FastAPI | Fits the Python agent layer, native async, SSE is first-class |
| Agents | OpenAI Agents SDK | Parallel agent dispatch, web search built in |
| Sponsor cache | ChromaDB | Stores reusable sponsor profiles with TTL-based refresh |
| Job state | Request-local memory | Session-scoped, doesn't need durability |
| Infra | Docker Compose | Runs frontend, backend, and ChromaDB locally |

---

## The streaming UX

The pipeline takes 30–60 seconds. A spinner is wrong — it turns the research into a black box and erodes trust. Instead, the frontend renders events as they arrive from the SSE stream:

```
→ Profiling Browserbase...
→ Browserbase: 3 past prize tracks, hero use case is browser automation
→ Profiling Supabase...
→ Searching Devpost for Supabase winners...
→ Found 12 relevant past projects
→ Synthesizing ideas...
→ [idea brief 1]
→ [idea brief 2]
   ...
```

Watching the reasoning unfold is part of the value. You see *why* an idea was recommended, not just that it was. The log is product, not progress theater.

---

## Sponsor profile cache

Profiling a sponsor is the most expensive step and the most reusable. Once a sponsor is profiled, the result is stored in ChromaDB with the sponsor name as metadata. The next run that includes the same sponsor skips Phase 1 entirely. Cache invalidation is weekly by default, or on-demand.

Over time this builds a sponsor knowledge base that compounds by skipping repeat profiling work for sponsors you have already researched. The current cache stores profiles by normalized sponsor name with a placeholder embedding; it is not a semantic similarity index.

---

## Running locally

```bash
# Backend
pip install -r backend/requirements.txt
uvicorn backend.main:app --port 8080 --reload

# Frontend
cd frontend
npm install
npm run dev
```

Docker Compose covers the frontend, backend, and ChromaDB for full-stack local development:

```bash
docker compose up
```

---

## Project structure

```
open-research/
├── backend/
│   ├── agents/
│   │   ├── sponsor_profiler.py   # per-sponsor parallel agents
│   │   ├── prior_art.py          # Devpost + GitHub prior-art search
│   │   └── synthesizer.py        # cross-ref + brief generation
│   ├── routers/
│   │   └── research.py           # config preflight + SSE endpoint
│   └── main.py
├── frontend/
│   └── src/
│       # input form, streaming log panel, brief cards
├── PRODUCT.md                    # brand, design principles, user profile
└── docker-compose.yml
```
