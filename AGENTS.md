# AGENTS.md

Design decisions that aren't obvious from the code. For product intent and UI principles, see `PRODUCT.md`.

## Decisions

- **One runtime key, by design.** The app needs only an OpenAI key, and users can supply their own per request (header, never a URL or storage on the server). Live scraping used to need five keys; it was removed so the project is easy to run and host. Don't add a runtime dependency that needs another key.
- **Research is done offline, not per request.** Sponsor docs change slowly, so `scripts/refresh_corpus.py` builds committed snapshots in `backend/corpus/` and a run is a single LLM call. The cost is staleness between refreshes. If a sponsor needs fresher data, refresh the snapshot; don't reintroduce live scraping into the request path.
- **The corpus is the only source of citations.** The model must cite prior art from the corpus, and the backend rewrites each citation from the corpus by URL (unknown URLs become `#`). Don't trust model-written titles or links.
- **Scores are computed, not trusted.** `match` is recomputed as the sum of `breakdown` and ideas are re-sorted in code. Treat the breakdown values themselves as a rough model judgement.
- **Prior art sources are Devpost and GitHub only.** X/Twitter was tried and dropped: results were junk and scraping X needs login and a headless browser.
- **Ideas must find a gap, not clone.** Synthesis is told to be novel relative to prior art, and `stack` is restricted to the sponsors the user picked.
- **A partial run is still useful.** A sponsor with no snapshot, or unreadable custom docs, is a warning (amber `!`) and the run continues. Only "no research data at all" or a synthesis failure is fatal (red `×`).
- **The stream is a POST read with `fetch`, not `EventSource`.** The OpenAI key has to travel in a header, which `EventSource` can't send and a query string must never carry.
- **Pydantic models are the schema source of truth.** The TypeScript types are mirrored by hand, so change both together.
- **The frontend stays dependency-light.** No component library, and all state lives in `App.tsx`.

## Known weak spots

- Snapshots are only as fresh as their last refresh.
- `depth` exists in the UI but nothing uses it.
- Custom docs URLs are fetched live through Jina Reader's keyless tier, so they can be rate-limited.
