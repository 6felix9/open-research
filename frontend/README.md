# Frontend

Single-page React 19 + Tailwind v4 app for Open Research. It collects the brief (sponsors, theme, interests, stack), streams results from the backend over SSE, and renders the live research log and the final ranked idea cards.

## Quick Start

```bash
npm install
npm run dev      # dev server on :5173 (proxies /api → :8080)
npm run build    # tsc + vite build → dist/
npm run lint     # eslint
```

The dev server proxies `/api/*` to `http://localhost:8080` (configured in `vite.config.ts`), so run the backend alongside it — see [`../backend/README.md`](../backend/README.md). Or run the full stack with `docker compose up` from the repo root.

## Architecture

All application state lives in `src/App.tsx`; there is no external state library. On Run, `App.tsx` POSTs the brief to `/api/research/stream` and reads the SSE response with a small `fetch` reader in `src/sse.ts` (`EventSource` can't POST or send headers). On load it calls `GET /api/config`; if the server has no OpenAI key, the sidebar shows a key field and the key is sent in an `X-OpenAI-Key` header, kept in `sessionStorage` only.

### Render state machine

`runState: 'idle' | 'running' | 'done' | 'error'` drives the main content area:

```
idle    → <EmptyState />       placeholder, no interaction
running → <ResearchScreen />   live log + progress bar
error   → <ResearchScreen />   same view; header reads "Research failed"
done    → <IdeaCards />        results grid
```

`<LogSlideover />` is always mounted and toggled by `showLog`.

### SSE events

| Event | Action |
|---|---|
| `log` | Append a `LogEntry` to `logs` |
| `synergy` | Set `synergyText` |
| `ideas` | Replace the `ideas` array |
| `done` | Close the stream; `runState = 'error'` if any log is `error && final`, else `'done'` |

## Project Structure

```
frontend/src/
├── main.tsx              # mounts <App /> into #root
├── App.tsx               # all state, SSE handling, layout
├── data.ts               # static data (SPONSORS, INTERESTS, …) + TS interfaces
├── index.css             # design system: OKLCH tokens, fonts, animations
└── components/
    ├── Sidebar.tsx       # brief input: sponsors, theme, advanced options
    ├── EmptyState.tsx    # idle placeholder
    ├── ResearchScreen.tsx# live log + progress while running
    ├── IdeaCards.tsx     # results grid with filters/sort + IdeaCard
    ├── LogSlideover.tsx  # slide-in full log overlay
    ├── LogRow.tsx        # one log line (shared by screen + slideover)
    └── Compare.tsx       # stub (returns null) — reserved for a compare view
```

`data.ts` holds only static data and TypeScript interfaces (`Sponsor`, `Idea`, `LogEntry`); logs, ideas, and synergy text are runtime state in `App.tsx`. The `Idea` / `LogEntry` interfaces mirror the backend Pydantic models in `backend/agents/synthesizer.py`.

See [`AGENTS.md`](AGENTS.md) for the full component guide, state inventory, design system, and Tailwind conventions.
