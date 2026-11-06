# AGENTS.md

Design decisions that aren't obvious from the code. For product intent and UI principles, see `PRODUCT.md`.

## Decisions

- **Fail loudly, no fallbacks.** All five API keys are required and there are no mock or degraded paths. Mock output looked plausible and hid broken integrations, so it was deleted. Don't reintroduce fallbacks; surface the error instead.
- **Prior art sources are Devpost and GitHub only.** X/Twitter was tried and dropped: Exa results were junk and scraping X needs login and a headless browser. An unknown source type raises rather than falling back to a broad search.
- **Research and ideation are separate.** Agents with tools gather context; the synthesizer has no tools and only reasons over what was gathered. Keep it that way so ideas stay traceable to retrieved evidence.
- **Ideas must find a gap, not clone.** Synthesis is told to be novel relative to prior art, and `stack` is restricted to the sponsors the user picked.
- **A partial run is still useful.** One sponsor failing is a warning and the pipeline continues; only a synthesis failure is fatal. The log's amber `!` vs red `×` encodes this distinction.
- **ChromaDB is used as a key-value cache, not a vector store.** Sponsor profiles are expensive to build and their docs change slowly, so they are cached for 7 days. Embeddings are dummies; don't add semantic search on top without rethinking this.
- **Pydantic models are the schema source of truth.** The TypeScript types are mirrored by hand, so change both together.
- **The frontend stays dependency-light.** No component library, and all state lives in `App.tsx`.

## Known weak spots

- `match` and its `breakdown` are produced by the LLM, not computed. Treat them as a rough ordering, not a metric.
- Sponsor profiles are truncated heavily before synthesis, so scraped detail is mostly lost.
- `depth` is accepted but unused.
