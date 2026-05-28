from __future__ import annotations

import os

from .mock_search import mock_search_prior_art


def has_api_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


_SPONSOR_PROFILES: dict[str, str] = {
    "groq": """# Groq

## Developer Docs & APIs
- Inference API: OpenAI-compatible REST (`https://api.groq.com/openai/v1`)
- Models: LLaMA 3 (8B/70B), Mixtral 8x7B, Gemma 7B; Whisper large-v3 for transcription
- Speciality: LPU (Language Processing Unit) — sub-100ms TTFT, ~500 tok/s sustained
- Generous free tier; hackathon API keys available on request

## Past Hackathon Tracks
- "Groq Speed Track" at ETH Denver '24 — prizes for latency-sensitive demos
- MLH "Best Use of Groq" — $500–$1,000 credits
- Prize language: "most compelling real-time application", "best voice or conversational demo"

## Canonical Use Cases
- Real-time voice assistants with sub-second response loops
- Live code completion in IDEs where latency is the product
- Streaming agents requiring fast decision loops
- Real-time commentary / narration over live data feeds

## What Wins
The demo must make the audience *feel* the speed — voice loops, live completions, or any flow where 300ms of latency would noticeably break the experience. Pairing Groq with ElevenLabs TTS for a full voice loop is the canonical winning stack.

## Sources
- https://console.groq.com/docs
""",

    "anthropic": """# Anthropic / Claude

## Developer Docs & APIs
- Claude 3.5 Sonnet: best speed/capability balance; Claude 3 Opus: 200k context window
- Computer Use (beta): Claude controls a real browser/desktop autonomously via Playwright
- Citations API: grounded responses with inline source references
- OpenAI-compatible SDK available

## Past Hackathon Tracks
- "Best Use of Claude" at YC AI Hackathon '24 — $2,500
- "Computer Use Track" at SF Hacks '24
- Prize language: "most novel use of long context", "most interpretable AI application"

## Canonical Use Cases
- Autonomous computer-use agents that navigate real UIs on-screen
- Long-document synthesis with citations (legal, research, medical)
- Multi-step reasoning chains with transparent audit trails
- Codebase-wide analysis and refactoring

## What Wins
Judges from Anthropic are explicit: chatbots are penalized. Computer Use + a real workflow automation (navigating a live portal on stage) or a 200k-context use case that would be impossible with smaller windows wins. Interpretability and citeable outputs are differentiators.

## Sources
- https://docs.anthropic.com
""",

    "modal": """# Modal

## Developer Docs & APIs
- `@app.function()` decorator: run any Python function on cloud GPU/CPU
- GPU options: A10G, A100, H100 (per-second billing, no idle cost)
- Auto-scaling: 0 → 1,000 containers in ~1 second
- Built-in: cron jobs, webhooks, async task queues, shared volumes

## Past Hackathon Tracks
- "Modal Infrastructure Award" at HackMIT '24 — $1,000 + credits
- "Best Scale Demo" category: horizontal parallelism
- Prize language: "most impressive use of parallel compute", "best MLOps innovation"

## Canonical Use Cases
- Parallel batch processing: images, documents, test mutations
- Fine-tuning pipelines with dynamic GPU allocation
- Scheduled ML jobs (nightly embeddings refresh, model eval)
- Serverless inference endpoints that auto-scale to traffic

## What Wins
Scale as a product feature. "We processed 1M images in 4 minutes" or "500 parallel test containers" with a live fan-out visualization in Modal's dashboard. Concrete numbers + live dashboard = the winning demo moment.

## Sources
- https://modal.com/docs
""",

    "supabase": """# Supabase

## Developer Docs & APIs
- Postgres + pgvector + Auth + Realtime + Storage + Edge Functions
- pgvector: semantic similarity search directly in Postgres
- Realtime: broadcast, presence, and Postgres change streams over WebSocket
- Free tier: 500MB DB, 1GB storage, 50k MAU

## Past Hackathon Tracks
- Launch Week Hackathon (recurring) — $1,500–$5,000 per category
- "Best Use of pgvector" and "Best Realtime App" as separate prize categories
- Prize language: "most creative use of Supabase primitives", "best full-stack project"

## Canonical Use Cases
- Semantic search with pgvector + embedding model
- Real-time collaborative apps (multiplayer cursors, live documents)
- Auth + database + vector search in a single weekend project
- RAG with Postgres as the source of truth

## What Wins
Projects combining multiple Supabase primitives (e.g., pgvector + Realtime) consistently outperform single-feature projects. Visible real-time collaboration during the demo — multiple cursors, live updates — is a reliable judge hook.

## Sources
- https://supabase.com/docs
""",

    "vercel": """# Vercel

## Developer Docs & APIs
- Hosting: Git-connected deploys, per-PR preview URLs
- Edge Functions: runs at 500+ PoPs globally, sub-10ms overhead
- AI SDK: `useChat`, `useCompletion`, streaming RSC helpers for Next.js
- Next.js App Router: Server Components, streaming, partial rendering

## Past Hackathon Tracks
- Next.js Conf Hackathon '24 — prizes for performance and developer experience
- MLH "Best Frontend" at multiple events — Vercel credits + swag
- Prize language: "best performance", "most polished developer experience"

## Canonical Use Cases
- Globally-deployed streaming AI chat via the Vercel AI SDK
- Design-to-code pipelines with instant preview deployment
- Performance-first LLM frontends with measurable TTFB
- Edge-rendered personalization with AI

## What Wins
Measurable performance ("47ms globally" shown on a live latency map) and polish. Sending judges a preview URL *before* the pitch is a documented winning move — they arrive already engaged. Vercel + Next.js App Router + Groq is a recognized high-velocity stack.

## Sources
- https://vercel.com/docs
- https://sdk.vercel.ai/docs
""",

    "elevenlabs": """# ElevenLabs

## Developer Docs & APIs
- TTS: 29 languages, 1,000+ voices, real-time streaming (<300ms first chunk)
- Voice Cloning: instant (30s sample) or professional (3h+ training)
- Multi-speaker: separate audio tracks per speaker in one request
- Free tier: 10k characters/month

## Past Hackathon Tracks
- "Best Voice Application" at Product Hunt Makers Hackathon '24
- MLH "Best Use of ElevenLabs" — $500 credits
- Prize language: "most emotionally resonant voice experience", "best audio-first application"

## Canonical Use Cases
- Conversational voice agents with natural, low-latency responses
- Audiobook and podcast generation
- Interactive voice characters in games or interactive fiction
- Accessibility tools for visually impaired users

## What Wins
The voice *is* the demo. Judges physically react when audio plays. Projects using cloned voices (not default TTS voices) and multi-speaker conversations with distinct personalities consistently win. Paired with Groq for a full sub-second voice loop, this stack is essentially unbeatable for real-time audio demos.

## Sources
- https://elevenlabs.io/docs
""",

    "mistral": """# Mistral

## Developer Docs & APIs
- Models: Mistral 7B, Mixtral 8x7B (MoE), Mistral Large, Codestral
- Fine-tuning API: LoRA fine-tuning on custom datasets
- Open weights: downloadable GGUF/HF formats for local/on-device use
- OpenAI-compatible API; function calling and JSON mode supported

## Past Hackathon Tracks
- "Best Use of Open Source LLM" at HealthHack EU '24
- GitLab Hackathon: "Best Fine-tuned Model" category
- Prize language: "most cost-efficient deployment", "best domain-specific fine-tune"

## Canonical Use Cases
- On-device / private deployments (HIPAA, GDPR, air-gapped environments)
- Domain-specific fine-tunes (legal clause detection, medical coding, code style)
- Cost-efficient high-volume inference (10x cheaper than GPT-4 class models)
- Offline-capable mobile or desktop applications

## What Wins
Privacy and cost are the differentiated angles. "Runs fully on-device, no data leaves the hospital" wins regulated-industry tracks. Fine-tuning demos that show a measurable quality improvement over the base model score well with technical judges.

## Sources
- https://docs.mistral.ai
""",

    "pinecone": """# Pinecone

## Developer Docs & APIs
- Serverless vector database (no infrastructure to manage)
- Hybrid search: dense + sparse vectors in a single query
- Namespaces for multi-tenant data isolation
- Free tier: 1M vectors, 1 index
- Metadata filtering, upsert, delete, and fetch operations

## Past Hackathon Tracks
- "Best RAG Application" at LegalHack '24 — $1,000 + credits
- Zendesk Hackathon: "Best Knowledge Base Integration"
- Prize language: "best retrieval quality", "most novel use of semantic search"

## Canonical Use Cases
- RAG pipelines with LLM-grounded, cited responses
- Semantic search over large document collections
- Recommendation systems based on content similarity
- Persistent agent / NPC memory with semantic recall

## What Wins
The retrieval quality delta is the demo moment. Show a query that fails keyword search but succeeds semantically, side-by-side. NPC memory in games, cross-lingual retrieval, and multi-modal search (text + image in the same index) are underexplored winning areas.

## Sources
- https://docs.pinecone.io
""",
}

_PRIOR_ART_SUMMARIES: dict[str, str] = {
    "groq": """**Winning problem categories**
Real-time voice assistants (VoiceBlitz, LiveCoach), latency-first developer tools (FlowState IDE), and live multiplayer consumer apps (TriviaLive). The unifying thread: the *product is the speed* — demos where 300ms of added latency would break the experience.

**Technical crux**
Groq is the inference backbone in a real-time loop: Whisper STT → Groq LLM → ElevenLabs TTS. VoiceBlitz achieved sub-100ms end-to-end by streaming tokens directly into TTS before generation is complete. FlowState streamed completions into a VS Code buffer token-by-token.

**Judge/community signals**
MLH judges noted "the crowd gasped" at Groq voice demos. X engagement peaks at 800–1,200 likes for clips showing measurable latency numbers. @hackathonhunter: "If you're building on Groq, the demo moment IS the latency. Show it, don't describe it."
""",

    "anthropic": """**Winning problem categories**
Autonomous computer-use agents completing real workflows on screen (ClaimBot navigating insurance portals), long-context synthesis with citations (ResearchPilot on 200-page PDFs), and meeting-to-action pipelines (MeetingMind → Linear tasks). Common thread: Claude doing something a human would need to manually click through.

**Technical crux**
Computer Use integrates Claude 3.5 Sonnet + Playwright: Claude receives a screenshot, decides the next click/type action, Playwright executes it. Long-context projects feed entire document corpora directly into the 200k window without chunking. Citations API grounds every claim with inline source references.

**Judge/community signals**
@swyx: "Genuine surprise at ClaimBot's live portal navigation." Anthropic judges have publicly stated they are "tired of chatbots." @aigrant: "Three Claude projects that impressed — all three used citations." Interpretability and computer-use agency are the two explicitly rewarded differentiators.
""",

    "supabase": """**Winning problem categories**
Semantic search replacing keyword search (TalentGraph, ShopSense), real-time collaborative tools with visible multiplayer (CoWrite), and personal memory assistants with natural-language query (MemoryLane). Projects using 3+ Supabase primitives in one coherent demo consistently outperform single-feature entries.

**Technical crux**
pgvector + embedding model (OpenAI/Cohere) is the standard retrieval stack. TalentGraph benchmarked pgvector recall vs. Pinecone and presented the results. CoWrite implemented CRDT-like conflict resolution over Supabase Realtime. ShopSense showed the semantic gap: "cozy winter vibes" → exact product match.

**Judge/community signals**
@supabase: "pgvector + Realtime is the winning combo." @theo: "Supabase is the only backend that lets a solo dev ship auth + DB + realtime + vector search in 24h." Visible real-time collaboration during the demo presentation is called out specifically by judges as a differentiator.
""",

    "elevenlabs": """**Winning problem categories**
Character voice apps with emotional resonance (StoryTeller), realistic voice-persona simulators for training (SalesVoice), multi-speaker automated content generation (PodcastGhost), and accessibility tools (AccessAudio). The voice must feel like a *character*, not a TTS engine.

**Technical crux**
Voice cloning (30s sample → custom voice) is the differentiated integration — not the default TTS voices. PodcastGhost used the multi-speaker API with two distinct voice profiles in a single request. SalesVoice chained Groq (low-latency transcript → response) + ElevenLabs streaming TTS for a sub-second voice loop.

**Judge/community signals**
@amasad: "Press play and people physically react." @elevenlabsio: "Emotional range is what separates winners from 'TTS with a robot voice'." @voiceaiweekly: "Multi-speaker is criminally underused — two AI agents talking in distinct voices is a demo that lands."
""",

    "modal": """**Winning problem categories**
Horizontal scale as the product feature (BatchVision: 1M images in 4 min), fine-tuning infrastructure with live job monitoring (FineTuneKit), parallel test mutation to map failure boundaries (TestFarm), and async background workers for time-sensitive data (VideoSummit). Scale must be *demonstrated*, not described.

**Technical crux**
The canonical pattern: `stub.function.map()` or `spawn()` to fan 100–1,000 containers in parallel, then show the Modal dashboard live. BatchVision mapped over an S3 bucket with 1,000 concurrent containers. TestFarm spawned mutation variants of a failing test suite and rendered the failure boundary as a 2D heatmap.

**Judge/community signals**
@chiphuyen called TestFarm "the most technically interesting hackathon project" of the year. @latentspace: "Modal winners say 'we did X in Y minutes using Z containers.'" @modal_labs: "The fan-out visualization in the dashboard is itself a demo moment." Concrete throughput numbers are essential.
""",

    "vercel": """**Winning problem categories**
Performance-measurable AI chat (EdgeChat: 47ms globally), AI-powered developer tools with instant deployment (ComponentForge: Figma → live URL in 30s), and self-improving documentation (LiveDocs). The Vercel preview URL is a meta-level winning pattern: judges arrive already engaged.

**Technical crux**
Vercel AI SDK (`useChat` with streaming) + Next.js App Router + Edge Functions is the canonical stack. EdgeChat used edge middleware to colocate inference near users and showed a live latency map. ComponentForge used ISR to deploy new components to a preview URL without a full rebuild.

**Judge/community signals**
@rauchg: "These projects ship things that used to require a backend team." @delba_oliveira: "Figma → deployed URL in 30 seconds — the feedback loop *is* the demo." @shadcn: "Send the judge a link before the presentation. If they've already clicked around, you start with a warmed-up audience."
""",

    "mistral": """**Winning problem categories**
On-device deployments in regulated industries where data cannot leave the network (PrivateMed for HIPAA hospitals), domain-specific fine-tunes with measurable quality deltas (CodeReviewBot), offline-capable mobile tools for low-connectivity environments (LinguaLocal), and cost-efficient multi-call analytics (AnalyticsCopilot).

**Technical crux**
Mistral 7B quantized (GGUF/llama.cpp) runs fully on-device — PrivateMed packaged it in a Docker container deployable to hospital VMs with zero internet egress. CodeReviewBot used Mistral's fine-tuning API on a dataset of annotated PRs from the target company. AnalyticsCopilot ran 10 LLM retry calls per SQL query; at Mistral's cost, this was economically viable.

**Judge/community signals**
@karpathy: "$5/mo VPS vs $50 of OpenAI credits per demo — the cost angle is real." @mistral_ai: "Fine-tuning is criminally underused at hackathons; teams that fine-tune outperform base-model prompters." Privacy framing wins in regulated-industry tracks; cost efficiency wins in consumer-scale tracks.
""",

    "pinecone": """**Winning problem categories**
Domain-specific RAG with citation quality (LegalMind: 10M legal documents), grounded customer-support agents (SupportGenius), multi-modal semantic search (VideoSearch: scene description → exact timestamp), and persistent NPC memory (PersonaEngine: characters remember past interactions).

**Technical crux**
Standard pipeline: chunk → embed (OpenAI/CLIP) → upsert to Pinecone → hybrid search (dense + sparse) → inject top-k into LLM context. LegalMind used hybrid search for 23% better recall on legal queries vs. dense-only. VideoSearch embedded video frames + ASR transcripts in the same index for cross-modal queries.

**Judge/community signals**
@pinecone: "Show the recall delta — benchmark vs. keyword search." @jerryjliu0: "NPC memory with Pinecone is 'not a chatbot, that's a character' — completely different experience." @weaviate_io: "VideoSearch was the most creative use — describing a scene in English and jumping to the timestamp is a product people would pay for."
""",
}

# The original 8 static ideas, re-used for zero-key fallback synthesis.
# Defined lazily to avoid circular imports with synthesizer.py.
def _build_fallback_ideas() -> list:
    from ..agents.synthesizer import Breakdown, IdeaBrief, PriorArtRef
    return [
        IdeaBrief(
            id="i1",
            title="Standup, but it's an agent that already ran it",
            pitch="Voice agent dials each teammate at their preferred hour, holds a 90-second async standup, transcribes blockers into a Linear-style board, and posts the digest to Slack before the human standup would have started.",
            stack=["groq", "elevenlabs", "supabase"],
            match=94,
            breakdown=Breakdown(sponsor=38, interest=34, novelty=22),
            difficulty=2,
            priorArt=PriorArtRef(title="Bumblebee — async voice retros for distributed teams", meta="Devpost · MLH Fellowship Showcase '24 · 312★", url="#"),
            why="Three sponsors stack cleanly: Groq does the latency floor, ElevenLabs sells the demo, Supabase carries state. Cross-checked against 4 standup tools — none use a real outbound voice loop.",
            risks="Telephony auth is finicky. Have a fallback to browser-mic if Twilio numbers don't come through.",
            demoMoment="Live-call a judge's phone during the pitch. They hear the agent. They answer.",
        ),
        IdeaBrief(
            id="i2",
            title="Receipt-driven warranty agent",
            pitch="Snap a photo of any receipt. The agent extracts the SKU, looks up the warranty terms, files a calendar entry for the expiry, and offers to draft the claim email the day before something breaks down.",
            stack=["anthropic", "modal"],
            match=87,
            breakdown=Breakdown(sponsor=30, interest=32, novelty=25),
            difficulty=2,
            priorArt=PriorArtRef(title="Stash — automated proof-of-purchase wallet", meta="Hacker News · 2023 · YC W23 batch", url="#"),
            why="Computer-use angle: the agent actually navigates the manufacturer's claim form on demo. That's the moment.",
            risks="OCR on creased receipts is a long tail. Cache the 50 most common retailers.",
            demoMoment="On stage, agent files a real warranty claim against a $3 mug. Watch the form fill itself.",
        ),
        IdeaBrief(
            id="i3",
            title="PR-review agent that explains itself in the diff",
            pitch="GitHub app. On every PR it leaves inline comments backed by a graph of the codebase — but each comment links to the exact training examples or docs that informed the suggestion. Auditable AI review.",
            stack=["anthropic", "pinecone", "vercel"],
            match=82,
            breakdown=Breakdown(sponsor=32, interest=30, novelty=20),
            difficulty=3,
            priorArt=PriorArtRef(title="Greptile · CodeRabbit — automated PR review", meta="Devpost YC AI '24 · 4 finalists", url="#"),
            why="The 'cite your sources' angle is what's missing in the space. Judges from Anthropic care about interpretability.",
            risks="Building the codebase graph eats time. Use tree-sitter + cache aggressively.",
            demoMoment="Click a comment → side panel scrolls to the exact 12 lines that informed it. The 'aha'.",
        ),
        IdeaBrief(
            id="i4",
            title="A debugger that runs your code in 1000 alternate universes",
            pitch="Pin a failing test. The agent forks the repo across Modal containers, mutates input combinatorially, and shows you the failure boundary as a 2D heatmap. Not 'what broke' — 'where the cliff is.'",
            stack=["modal", "anthropic"],
            match=79,
            breakdown=Breakdown(sponsor=28, interest=28, novelty=23),
            difficulty=3,
            priorArt=PriorArtRef(title="Hypothesis · property-based testing", meta="PyCon talk · 2023 · OSS adoption growing", url="#"),
            why="Modal's per-request GPUs make this economically possible. Hard to demo casually — but the heatmap is gorgeous.",
            risks="Combinatorial explosion. Need a smart pruning strategy or you'll burn through credits.",
            demoMoment="Heatmap renders live. A coastline of failure. Audience leans in.",
        ),
        IdeaBrief(
            id="i5",
            title="Voice-first onboarding for any SaaS",
            pitch="Drop a script tag. First-time users hear a real voice greet them by context and walk them through setup as a 60-second conversation instead of a 12-step tour.",
            stack=["elevenlabs", "vercel", "groq"],
            match=76,
            breakdown=Breakdown(sponsor=30, interest=26, novelty=20),
            difficulty=2,
            priorArt=PriorArtRef(title="Userpilot · Pendo — guided product tours", meta="G2 category · $200M+ ARR space", url="#"),
            why="Conversational onboarding is the next category. Three sponsor stack lights up.",
            risks="Voice in B2B is contentious. Make it opt-in and toggleable, not in-your-face.",
            demoMoment="Live demo: visit a fake SaaS, the agent greets the judge by name from the QR they scanned.",
        ),
        IdeaBrief(
            id="i6",
            title="Synthetic users for usability tests",
            pitch="Upload your Figma. The agent simulates 30 personas — each with their own goals, accessibility needs, and friction tolerance — clicking through the prototype and writing heatmap-style critiques.",
            stack=["anthropic", "modal", "pinecone"],
            match=73,
            breakdown=Breakdown(sponsor=26, interest=27, novelty=20),
            difficulty=3,
            priorArt=PriorArtRef(title="Maze · UserTesting — remote usability testing", meta="Devpost · multiple AI-UX projects '24", url="#"),
            why="Replaces a real-money process. Demo is visual. Computer-use clicks through your Figma prototype on stage.",
            risks="Persona fidelity matters — generic personas will read as fake. Ground them in real survey data.",
            demoMoment="Upload audience's own Figma, replay 5 personas trying to check out. Two get stuck on the same modal.",
        ),
        IdeaBrief(
            id="i7",
            title="Background-research worker that ships citations to your inbox",
            pitch="An always-on Modal worker watching your calendar. 30 min before each meeting it scrapes attendees' recent writing, pinned posts, and one surprising public fact — delivered as a one-pager with footnotes.",
            stack=["modal", "mistral", "supabase"],
            match=71,
            breakdown=Breakdown(sponsor=27, interest=24, novelty=20),
            difficulty=2,
            priorArt=PriorArtRef(title="Clay · Common Room — relationship intelligence", meta="Y Combinator '23 · prod-market fit", url="#"),
            why="Open-source model angle keeps it cheap. Mistral fine-tune on summary style is a credible prize hook.",
            risks="Privacy optics. Hard-cap to public data and put consent gating front and center.",
            demoMoment="Pull up a one-pager about a judge using only their public footprint. Land one specific detail.",
        ),
        IdeaBrief(
            id="i8",
            title="Music-theory tutor that hears you play",
            pitch="Browser-only. Pick an instrument, play. The agent listens, transcribes the line, and explains what scale you're improvising in — and what one note would surprise you. Built for learners who can't read sheet music.",
            stack=["groq", "vercel"],
            match=68,
            breakdown=Breakdown(sponsor=24, interest=24, novelty=20),
            difficulty=2,
            priorArt=PriorArtRef(title="Yousician · Soundslice — interactive music ed", meta="Indie space · multiple winners at MIT MusicHack", url="#"),
            why="Latency is the product. Groq wins or this doesn't ship. Vercel's streaming primitives make the UI feel alive.",
            risks="Pitch detection in noisy rooms is hard. Demo in a treated room or use a direct line-in.",
            demoMoment="Play 4 bars. The screen highlights the implied chord. Suggests the surprising note. You play it.",
        ),
    ]


_SYNERGY_BY_STACK: list[tuple[frozenset[str], str]] = [
    (
        frozenset({"groq", "elevenlabs", "supabase"}),
        "Groq + ElevenLabs + Supabase form the real-time voice triangle — sub-100ms inference, natural TTS, and persistent state. 2 of the top 5 ideas use this stack.",
    ),
    (
        frozenset({"groq", "elevenlabs"}),
        "Groq + ElevenLabs is the canonical voice stack: Groq's LPU keeps inference under 100ms and ElevenLabs TTS streams the first audio chunk in <300ms — the combined latency is imperceptible.",
    ),
    (
        frozenset({"anthropic", "modal"}),
        "Anthropic's computer-use agent + Modal's parallel GPU containers unlock a class of autonomous demos that would be too slow or too expensive on any other stack.",
    ),
    (
        frozenset({"anthropic", "pinecone"}),
        "Claude's 200k context + Pinecone's semantic retrieval creates an interpretable RAG stack — Claude cites exactly which retrieved chunks informed each response.",
    ),
    (
        frozenset({"modal", "mistral"}),
        "Modal's auto-scaling containers + Mistral's open weights let you fine-tune and serve a private model in the same demo — no data leaves your infrastructure.",
    ),
    (
        frozenset({"supabase", "pinecone"}),
        "Supabase pgvector for transactional queries + Pinecone for high-recall semantic search gives you the best of both worlds: ACID guarantees and ANN retrieval in one pipeline.",
    ),
    (
        frozenset({"vercel", "groq"}),
        "Vercel's edge network + Groq's LPU inference eliminates two layers of latency: the network hop and the model step. The result is a frontend that feels instantaneous.",
    ),
]


def fallback_sponsor_profile(sponsor_name: str) -> str:
    key = sponsor_name.lower().strip()
    return _SPONSOR_PROFILES.get(key, f"# {sponsor_name}\n\nNo pre-made profile available.\n")


def fallback_prior_art_summary(sponsor_name: str) -> str:
    key = sponsor_name.lower().strip()
    if key in _PRIOR_ART_SUMMARIES:
        return _PRIOR_ART_SUMMARIES[key]
    devpost = mock_search_prior_art(sponsor_name, "devpost")
    x_posts = mock_search_prior_art(sponsor_name, "x")
    return (
        "**Winning problem categories**\nSee Devpost listings below.\n\n"
        f"**Technical crux**\n{devpost[:500]}\n\n"
        f"**Judge/community signals**\n{x_posts[:400]}\n"
    )


def fallback_synthesis(
    sponsors: list[str],
    interests: list[str],
    theme: str,
    seed: str,
    skills: list[str],
    time_budget: str,
) -> object:
    from ..agents.synthesizer import SynthesisResult

    ideas = _build_fallback_ideas()
    sponsor_set = {s.lower() for s in sponsors}

    if sponsor_set:
        matched = [
            idea for idea in ideas
            if sponsor_set & {s.lower() for s in idea.stack}
        ]
        selected = matched if matched else ideas
    else:
        selected = ideas

    # Re-number IDs to be contiguous
    reindexed = [idea.model_copy(update={"id": f"i{i}"}) for i, idea in enumerate(selected, 1)]

    synergy = _pick_synergy(sponsor_set)
    return SynthesisResult(synergy=synergy, ideas=reindexed)


def _pick_synergy(sponsor_set: set[str]) -> str:
    for sponsors, text in _SYNERGY_BY_STACK:
        if sponsors & sponsor_set:
            return text
    if sponsor_set:
        names = ", ".join(sorted(sponsor_set)).title()
        return f"Your selected sponsors ({names}) offer complementary capabilities — combine them for a demo that no single-sponsor project can match."
    return "Select sponsors to unlock stack-specific synergy insights."
