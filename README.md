# Open Research

An agentic ideation tool for hackathons. You give it your sponsors, your interests, and your stack. It does three hours of research in under a minute and hands you an opinionated shortlist — ranked ideas with rationale, prior art citations, and a concrete demo moment. Not a brainstorm. A brief you can commit to.

---

## What it does

Most hackathon ideation is wasted time: generic ideas that don't use sponsors well, prize tracks you didn't know existed, wheel-reinventing that a quick Devpost search would have prevented. Open Research fixes the research layer — the part that takes the most time and produces the least signal when done manually.

The pipeline has three phases, each streaming progress to the frontend in real time:

**Phase 1 — Sponsor profiles**

Each sponsor has a committed snapshot in `backend/corpus/` built from its official developer docs: capabilities and APIs, hero use cases, what it rewards in hackathon projects, and what's new. The goal is understanding what a sponsor *actually rewards*, not just what their landing page says. You can also paste a docs URL to add your own context.

**Phase 2 — Prior art**

The same snapshots hold past Devpost projects and hackathon-style GitHub repos for each sponsor. Every idea must cite one of them, and the backend rewrites each citation from the corpus, so a cited project always exists. This is the part most people skip and most often regret skipping.

**Phase 3 — Synthesis**

One structured LLM call cross-references your interests and stack against sponsor capabilities and prior art. Generates 5–8 idea briefs, each with:
- A one-line idea
- Why this sponsor scores you points specifically
- A prior art reference (what proved the pattern works)
- The technical crux (what you'd actually have to build)
- Feasibility given your stated stack

Match scores are the sum of the three breakdown scores, computed in code rather than trusted from the model.

---

## Architecture

```
[User Input]
  Sponsors: [Groq, Supabase, Anthropic]
  Interests: agents, real-time apps
  Stack: Python, React
  Theme: "AI productivity tools"
        │
        ▼
┌─────────────────────────────────────────┐
│    PHASES 1–2: Load snapshots           │
│                                         │
│  backend/corpus/<sponsor>.json          │
│  profile + Devpost/GitHub prior art     │
│  (+ optional user-supplied docs URLs)   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│    PHASE 3: Synthesis (one LLM call)    │
│                                         │
│  user interests ∩ sponsor capabilities  │
│  ∩ prior art → ranked briefs            │
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
| LLM | OpenAI SDK, structured output | One call, schema-validated ideas; the only runtime key |
| Sponsor data | Committed JSON snapshots | No runtime scraping; refreshed offline by a script |
| Job state | Request-local memory | Session-scoped, doesn't need durability |
| Infra | Docker Compose | Runs frontend and backend locally |

---

## The streaming UX

The synthesis call takes a while. A spinner is wrong — it turns the research into a black box and erodes trust. Instead, the frontend renders events as they arrive from the SSE stream:

```
→ Groq: sponsor profile loaded (snapshot 2026-11-07)
→ Supabase: sponsor profile loaded (snapshot 2026-11-07)
→ Groq: 4 devpost, 4 github prior-art project(s) on file
→ Generating idea seeds from sponsor profiles and prior art
→ [idea brief 1]
→ [idea brief 2]
   ...
```

Watching the reasoning unfold is part of the value. You see *why* an idea was recommended, not just that it was. The log is product, not progress theater.

---

## Sponsor snapshot corpus

Researching a sponsor live is the most expensive and least reliable step, and sponsor docs change slowly. So the research is done ahead of time: `scripts/refresh_corpus.py` reads each sponsor's docs, finds past Devpost and GitHub projects, and writes `backend/corpus/<sponsor>.json`. Those files are committed, so a run needs no scraping keys and no database. Its only network call is the LLM (plus an optional keyless fetch if you paste custom docs URLs).

The trade-off is staleness: a snapshot is only as fresh as its last refresh (each file records its date). Re-run the script when you want newer data.

---

## Running locally

The app needs one key. Copy `.env.example` to `.env.local` in the repo root and set `OPENAI_API_KEY`. Or leave it unset and paste your own key into the sidebar; it is sent per request in a header, kept only in that browser tab, and never stored by the server.

```bash
# Backend (handles venv, deps, and port cleanup)
./backend/start.sh

# …or manually, from the repo root
pip install -r backend/requirements.txt
uvicorn backend.main:app --port 8080 --reload

# Frontend
cd frontend
npm install
npm run dev
```

Docker Compose runs the frontend and backend together:

```bash
docker compose up
```

To refresh the sponsor snapshots (maintainers only; needs `OPENAI_API_KEY`):

```bash
pip install -r scripts/requirements.txt
python scripts/refresh_corpus.py            # all sponsors
python scripts/refresh_corpus.py supabase   # just one
```

---

## Project structure

```
open-research/
├── backend/
│   ├── agents/
│   │   └── synthesizer.py        # prompt, LLM call, Pydantic models, citation grounding
│   ├── core/
│   │   └── corpus.py             # snapshot loading + user-supplied docs fetch
│   ├── corpus/                   # committed per-sponsor snapshots
│   ├── routers/
│   │   └── research.py           # config + SSE endpoint
│   └── main.py
├── scripts/
│   └── refresh_corpus.py         # rebuilds the snapshots
├── frontend/
│   └── src/
│       # input form, streaming log panel, brief cards
├── PRODUCT.md                    # brand, design principles, user profile
└── docker-compose.yml
```
