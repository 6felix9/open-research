# Backend

FastAPI backend for Open Research. It loads pre-built sponsor snapshots, makes one structured OpenAI call to generate ranked hackathon ideas, and streams progress to the frontend over SSE.

## Quick Start

```bash
# Recommended: handles venv, deps, and port cleanup automatically
./backend/start.sh

# Manual (run from repo root)
pip install -r backend/requirements.txt
uvicorn backend.main:app --port 8080 --reload

# Tests (offline, no keys needed)
pytest backend/tests
```

The only key is `OPENAI_API_KEY` in `.env.local` at the repo root. It is optional if each request supplies its own key (see below).

## API

### `GET /api/config`

```json
{ "server_key": true }
```

Whether the server has its own `OPENAI_API_KEY`. The frontend uses it to decide whether to ask the user for a key.

### `POST /api/research/stream`

JSON body, SSE response. All progress, results and errors arrive as events on this one connection.

| Field | Type | Required | Notes |
|---|---|---|---|
| `sponsors` | `list[str]` | Yes | Sponsor ids, e.g. `["groq", "supabase"]` |
| `theme` | `str` | Yes | Hackathon theme description |
| `interests` | `list[str]` | No | Interest tags |
| `seed` | `str` | No | Optional seed idea or constraint |
| `skills` | `list[str]` | No | Team skill tags |
| `time_budget` | `str` | No | `"24h"`, `"36h"`, or `"48h"` |
| `custom_sponsor_urls` | `list[str]` | No | Docs URLs to read and add as context (max 5) |

**Key handling:** the `X-OpenAI-Key` header is used if present, otherwise the server's `OPENAI_API_KEY`. The key is never logged or stored. Returns 422 if `sponsors` or `theme` is missing, or if no key is available.

### SSE Event Protocol

| Event | Payload | Notes |
|---|---|---|
| `log` | `{id, step, text, final?, error?}` | Progress; `step` is `"NN · LABEL"`; `error` alone is a warning, `error` + `final` is fatal |
| `synergy` | `{text}` | One-line sponsor synergy insight |
| `ideas` | `IdeaBrief[]` | Final ranked idea list |
| `done` | `{}` | Stream complete |

## Structure

```
backend/
├── main.py                 # App entrypoint, loads env files, mounts router
├── routers/research.py     # GET /api/config + POST /api/research/stream
├── agents/synthesizer.py   # Prompt, LLM call, Pydantic models, post-processing
├── core/
│   ├── corpus.py           # Snapshot loading + user-supplied docs fetch (Jina Reader, keyless)
│   └── stream.py           # SSE serialization helper
├── corpus/                 # Committed per-sponsor snapshots (built by scripts/refresh_corpus.py)
└── tests/test_pipeline.py  # Offline tests: corpus, post-processing, API
```

## Pipeline

1. **Intake and snapshots.** Each requested sponsor id loads `corpus/<id>.json` (profile plus Devpost and GitHub prior art). A sponsor with no snapshot is a warning, not a failure. If there is no research data at all, the run ends with a fatal error.
2. **Custom docs.** Any `custom_sponsor_urls` are fetched via Jina Reader and added to the prompt as extra context.
3. **Synthesis.** One `chat.completions.parse` call with `SynthesisResult` as the schema. Then, in code:
   - each idea's `priorArt` is replaced with the matching corpus entry by URL; a URL not in the corpus becomes `"#"`
   - `match` is recomputed as the sum of `breakdown`
   - ideas are re-sorted by `match` and re-numbered `i1, i2, …`

## Pydantic Models

All in `agents/synthesizer.py`. The TypeScript interfaces in `frontend/src/data.ts` mirror them by hand.

```
Breakdown        sponsor: int, interest: int, novelty: int
PriorArtRef      title: str, meta: str, url: str
IdeaBrief        id, title, pitch, stack: list[str], match: int,
                 breakdown: Breakdown, difficulty: int (1–3),
                 priorArt: PriorArtRef, why: str, risks: str, demoMoment: str
SynthesisResult  synergy: str, ideas: list[IdeaBrief]
```

## Environment Variables

| Variable | Required | Default | Notes |
|---|---|---|---|
| `OPENAI_API_KEY` | No* | — | *Required unless every request sends `X-OpenAI-Key` |
| `OPENAI_MODEL` | No | `gpt-5.4-mini` | Model for synthesis (and for `scripts/refresh_corpus.py`) |

Loaded from `.env` and `.env.local` in the current working directory and one directory up.
