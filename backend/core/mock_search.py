from __future__ import annotations

from agents import function_tool

# TODO: Replace mock searches with the new discovery and scraping pipeline:
#       - Use Exa AI to semantically search for prior art URLs across Devpost, GitHub, and Twitter.
#       - Once URLs are discovered, route them to individual tools:
#         * Devpost URLs: Retrieve and scrape using Jina Reader.
#         * GitHub URLs: Fetch repository metadata/code via the GitHub REST API.
#         * Twitter (X) URLs: Scrape via Scrapling StealthyFetcher (https://github.com/D4Vinci/Scrapling), mocked for now.

# TODO: Once the discovery and scraping pipeline is fully implemented, remove all the mocked 
#       hallucinated data structures below (_DEVPOST_DATA, _X_DATA, and associated generic templates).

_DEVPOST_DATA: dict[str, str] = {

    "groq": """
Devpost prior art for Groq:

1. "VoiceBlitz" — Real-time voice assistant with sub-100ms response loop.
   Stack: Groq (LLaMA-3 inference), Whisper STT, ElevenLabs TTS.
   Outcome: 1st place, Groq Speed Track, ETH Denver '24.
   URL: https://devpost.com/software/voiceblitz

2. "LiveCoach" — Sports commentary agent that narrates live game feeds.
   Stack: Groq, GPT-4o vision, WebSocket streams.
   Outcome: Finalist, Groq API track, HackMIT '24.
   URL: https://devpost.com/software/livecoach

3. "FlowState" — IDE plugin that generates code completions inline as you type,
   with zero perceptible latency.
   Stack: Groq (Mixtral), VS Code extension API.
   Outcome: Winner, Developer Tools category, AI Hack Week '24.
   URL: https://devpost.com/software/flowstate-ide

4. "TriviaLive" — Multiplayer trivia game where the AI host improvises questions
   in real time based on the audience's chat.
   Stack: Groq, Supabase Realtime, Next.js.
   Outcome: 2nd place, Consumer Apps, Buildspace S5.
   URL: https://devpost.com/software/trivialive
""",

    "anthropic": """
Devpost prior art for Anthropic / Claude:

1. "ClaimBot" — Computer-use agent that navigates insurance claim portals end-to-end,
   filling forms and uploading documents without human intervention.
   Stack: Claude 3.5 Sonnet (computer use), Playwright, FastAPI.
   Outcome: 1st place, Anthropic Computer Use Track, SF Hacks '24.
   URL: https://devpost.com/software/claimbot

2. "ResearchPilot" — Long-context research assistant that ingests 200-page PDFs and
   produces structured literature reviews with inline citations.
   Stack: Claude 3 Opus, Pinecone, Streamlit.
   Outcome: Winner, Developer Productivity, HackAI '24.
   URL: https://devpost.com/software/researchpilot

3. "MeetingMind" — Agent that joins Zoom calls, takes notes, and autonomously
   creates follow-up tasks in Linear.
   Stack: Claude 3.5 Sonnet, AssemblyAI, Linear API.
   Outcome: Finalist, Enterprise AI, YC AI Hackathon '24.
   URL: https://devpost.com/software/meetingmind

4. "DocAudit" — Legal document reviewer that flags risky clauses and cross-references
   case law, with source citations for every finding.
   Stack: Claude 3 Opus (200k context), LangChain, React.
   Outcome: 2nd place, Legal Tech, LawHacks '24.
   URL: https://devpost.com/software/docaudit
""",

    "supabase": """
Devpost prior art for Supabase:

1. "TalentGraph" — Hiring platform using pgvector to match candidates to roles via
   semantic similarity on resumes and job descriptions.
   Stack: Supabase (pgvector, Auth, Edge Functions), OpenAI embeddings, SvelteKit.
   Outcome: 1st place, Supabase Launch Week Hackathon '24.
   URL: https://devpost.com/software/talentgraph

2. "CoWrite" — Real-time collaborative writing tool with AI suggestions, built on
   Supabase Realtime for conflict-free multiplayer edits.
   Stack: Supabase Realtime, GPT-4o, Tiptap editor, Vercel.
   Outcome: Winner, Collaboration Tools, Supabase Hackathon #5.
   URL: https://devpost.com/software/cowrite

3. "MemoryLane" — Personal memory journal that stores voice notes, transcribes them,
   and lets users query their past with natural language.
   Stack: Supabase Storage + pgvector, Whisper, Next.js.
   Outcome: Community Choice, Supabase Hackathon #6.
   URL: https://devpost.com/software/memorylane

4. "ShopSense" — E-commerce search that understands vague queries like "cozy winter
   vibes under $50" using semantic vector search.
   Stack: Supabase pgvector, OpenAI embeddings, Shopify API, React.
   Outcome: Finalist, E-commerce AI, ShopifyDev Hackathon '24.
   URL: https://devpost.com/software/shopsense
""",

    "elevenlabs": """
Devpost prior art for ElevenLabs:

1. "StoryTeller" — Interactive bedtime story app where the AI narrates a unique story
   each night in a chosen character voice, adapting to the child's responses.
   Stack: ElevenLabs TTS, GPT-4o, React Native.
   Outcome: 1st place, Consumer AI, Product Hunt Makers Hackathon '24.
   URL: https://devpost.com/software/storyteller-ai

2. "SalesVoice" — Outbound sales training simulator with a realistic AI prospect
   voice that responds naturally and grades the salesperson's pitch.
   Stack: ElevenLabs (voice cloning), Groq, Twilio, FastAPI.
   Outcome: Winner, Sales Tech, RevGenius Hackathon '24.
   URL: https://devpost.com/software/salesvoice

3. "PodcastGhost" — Generates full podcast episodes from bullet-point outlines,
   with two distinct AI hosts in natural conversation.
   Stack: ElevenLabs (multi-speaker), GPT-4o, Vercel, S3.
   Outcome: Finalist, Media & Content, HackMedia '24.
   URL: https://devpost.com/software/podcastghost

4. "AccessAudio" — Browser extension that reads any webpage aloud in the user's
   preferred cloned voice, including images via alt-text description.
   Stack: ElevenLabs, Claude, Chrome Extension API.
   Outcome: 2nd place, Accessibility, a11yHacks '24.
   URL: https://devpost.com/software/accessaudio
""",

    "modal": """
Devpost prior art for Modal:

1. "BatchVision" — Bulk image processing pipeline that classifies, tags, and resizes
   1M+ product images overnight using parallel Modal containers.
   Stack: Modal (GPU), CLIP, Pillow, FastAPI.
   Outcome: 1st place, Infrastructure & Scale, Modal Hackathon '24.
   URL: https://devpost.com/software/batchvision

2. "FineTuneKit" — No-code fine-tuning UI that spins up Modal GPU jobs for
   LoRA training and hot-swaps the new model into a live demo endpoint.
   Stack: Modal, Hugging Face, Gradio, React.
   Outcome: Winner, MLOps, MLH Local Hack Day '24.
   URL: https://devpost.com/software/finetunekit

3. "TestFarm" — Property-based testing harness that forks 500 Modal containers to
   explore edge cases in parallel and visualizes the failure boundary.
   Stack: Modal, Hypothesis, Pytest, Plotly.
   Outcome: Finalist, Developer Tools, HackMIT '24.
   URL: https://devpost.com/software/testfarm

4. "VideoSummit" — Async video summarization service that processes a full day of
   Zoom recordings in under 5 minutes using Modal's auto-scaling.
   Stack: Modal (Whisper + Claude), S3, FastAPI, Next.js.
   Outcome: 2nd place, Productivity, Notion Hackathon '24.
   URL: https://devpost.com/software/videosummit
""",

    "vercel": """
Devpost prior art for Vercel:

1. "EdgeChat" — Global AI chat app with <50ms TTFB worldwide, leveraging Vercel
   Edge Functions and streaming RSC for instant perceived response.
   Stack: Vercel AI SDK, Next.js App Router, Groq, Upstash.
   Outcome: 1st place, Performance, Next.js Conf Hackathon '24.
   URL: https://devpost.com/software/edgechat

2. "DeployPilot" — Natural-language deployment assistant that lets teams describe
   infra changes in plain English and previews them before merge.
   Stack: Vercel, Next.js, Claude, GitHub Actions.
   Outcome: Winner, DevOps AI, GitHub Universe Hackathon '24.
   URL: https://devpost.com/software/deploypilot

3. "ComponentForge" — AI design-to-code tool that converts Figma frames to
   production Next.js components, deployed to a preview URL instantly.
   Stack: Vercel, Next.js, OpenAI vision, Figma API.
   Outcome: Finalist, Design Engineering, Figma Config Hackathon '24.
   URL: https://devpost.com/software/componentforge

4. "LiveDocs" — Documentation site that rewrites itself based on user confusion
   signals (scroll depth, copy-paste, time-on-page).
   Stack: Vercel Analytics, Next.js, GPT-4o, Posthog.
   Outcome: 2nd place, Developer Experience, DocsFest '24.
   URL: https://devpost.com/software/livedocs
""",

    "mistral": """
Devpost prior art for Mistral:

1. "PrivateMed" — On-device clinical note summarizer using a quantized Mistral model,
   so no patient data leaves the hospital network.
   Stack: Mistral (local via llama.cpp), FastAPI, React, Docker.
   Outcome: 1st place, Healthcare AI, HealthHack EU '24.
   URL: https://devpost.com/software/privatemed

2. "CodeReviewBot" — PR reviewer fine-tuned on a company's internal style guide
   using Mistral's fine-tuning API, posted as GitHub comments.
   Stack: Mistral fine-tune, GitHub API, Vercel, Next.js.
   Outcome: Winner, Enterprise Dev Tools, GitLab Hackathon '24.
   URL: https://devpost.com/software/codereviewbot

3. "LinguaLocal" — Offline translation app for field workers in low-connectivity
   regions, running Mistral 7B fully on-device.
   Stack: Mistral (GGUF), React Native, expo-sqlite.
   Outcome: Finalist, Social Impact, Devfolio Hackathon '24.
   URL: https://devpost.com/software/lingualocal

4. "AnalyticsCopilot" — Natural-language BI layer over Postgres: ask a question,
   get SQL + chart. Uses Mistral for fast low-cost query generation.
   Stack: Mistral, Supabase, Apache ECharts, FastAPI.
   Outcome: 2nd place, Data & Analytics, DataHack '24.
   URL: https://devpost.com/software/analyticscopilot
""",

    "pinecone": """
Devpost prior art for Pinecone:

1. "LegalMind" — RAG-powered legal research tool that surfaces relevant case law
   from a 10M-document Pinecone index with source citations.
   Stack: Pinecone, OpenAI embeddings, Claude, Next.js.
   Outcome: 1st place, Legal AI, LegalHack '24.
   URL: https://devpost.com/software/legalmind

2. "SupportGenius" — Customer support agent grounded in a company's entire
   knowledge base via Pinecone, with escalation routing.
   Stack: Pinecone, GPT-4o, Twilio, FastAPI, React.
   Outcome: Winner, Customer Experience, Zendesk Hackathon '24.
   URL: https://devpost.com/software/supportgenius

3. "VideoSearch" — Semantic video search: describe a scene in words and jump
   to the exact timestamp across a library of recordings.
   Stack: Pinecone, CLIP embeddings, Whisper, Next.js.
   Outcome: Finalist, Media Tech, HackVideo '24.
   URL: https://devpost.com/software/videosearch

4. "PersonaEngine" — Dynamic NPC system for games that stores character memories
   in Pinecone and retrieves relevant context before each dialogue turn.
   Stack: Pinecone, Mistral, Unity, FastAPI.
   Outcome: 2nd place, Gaming AI, GameJam AI '24.
   URL: https://devpost.com/software/personaengine
""",
}

# TODO: X (Twitter) scraping will remain mocked for now as part of the new discovery pipeline.
#       When ready, replace this with Scrapling StealthyFetcher (https://github.com/D4Vinci/Scrapling) to bypass Twitter login and rate-limiting blocks.



_X_DATA: dict[str, str] = {
    "groq": """
X (Twitter) posts about Groq at hackathons:

1. @yxzhang_dev: "Just demoed VoiceBlitz at ETH Denver — the crowd gasped when the
   agent responded before I finished speaking. That's Groq doing sub-100ms inference.
   Nothing else comes close for latency-sensitive demos. 🔥"
   Likes: 847, Retweets: 203

2. @MLHofficial: "The Groq Speed Track at HackMIT had the most visceral demos we've
   seen this year. Real-time voice + Groq = judges leaning forward every single time."
   Likes: 1.2k, Retweets: 314

3. @buildwithgroq: "Pro tip for hackathons: pair Groq with ElevenLabs TTS. The combined
   latency is so low it feels like talking to a person. Judges notice."
   Likes: 623, Retweets: 189

4. @hackathonhunter: "Groq winners at the last 5 events I've judged: all of them had
   a live voice loop in the demo. If you're building on Groq, the demo moment IS the
   latency. Show it, don't describe it."
   Likes: 412, Retweets: 97
""",

    "anthropic": """
X (Twitter) posts about Anthropic / Claude at hackathons:

1. @swyx: "The Computer Use track at SF Hacks was genuinely surprising. The ClaimBot
   team literally navigated a live insurance portal on stage. Judges had not seen that
   before. That's the frontier of what Claude can do."
   Likes: 2.1k, Retweets: 567

2. @AnthropicAI: "Loved seeing the creative long-context projects at HackAI. ResearchPilot
   showed what 200k tokens actually unlocks — not just 'chat with your PDF' but real
   structured synthesis. That's the bar we want to see cleared."
   Likes: 1.8k, Retweets: 445

3. @jxnl: "If you're building on Claude for a hackathon, stop making chatbots.
   Long context + computer use is still wide open. The judges have seen six chatbots.
   They haven't seen an agent that actually *does something on screen*."
   Likes: 934, Retweets: 278

4. @aigrant: "Three ClaudeAPI projects at YC AI Hackathon that impressed:
   all three used citations/sources in their outputs. Interpretability is
   a signal Anthropic judges look for. Ground your claims."
   Likes: 756, Retweets: 201
""",

    "supabase": """
X (Twitter) posts about Supabase at hackathons:

1. @kiwicopple: "Every Launch Week hackathon we see a wave of pgvector projects, but
   TalentGraph was different — they actually benchmarked recall quality vs. Pinecone
   and presented the results. That level of rigor wins."
   Likes: 1.4k, Retweets: 389

2. @supabase: "Our hackathon winners keep using the same combo: pgvector for semantic
   search + Realtime for live updates. The two together unlock a class of apps that
   feels genuinely novel."
   Likes: 987, Retweets: 267

3. @theo: "Supabase is the only backend that lets a solo hackathon dev ship auth +
   database + realtime + vector search in 24 hours. It's not fair to teams
   who choose anything else."
   Likes: 2.3k, Retweets: 612

4. @iamrasengan: "If you use Supabase Realtime in your hackathon demo and it's actually
   collaborative (multiple cursors, live updates, etc.) — that visual moment is worth
   extra points. Judges love seeing real multiplayer."
   Likes: 543, Retweets: 145
""",

    "elevenlabs": """
X (Twitter) posts about ElevenLabs at hackathons:

1. @elevenlabsio: "StoryTeller at Product Hunt Makers won because the voice *felt*
   like a real narrator. The emotional range of cloned voices is what separates
   ElevenLabs projects from 'TTS with a robot voice' demos."
   Likes: 1.6k, Retweets: 421

2. @amasad: "ElevenLabs demos have a built-in 'wow' moment that other sponsor stacks
   don't: press play and people physically react. Use that. Make the voice the demo."
   Likes: 1.1k, Retweets: 298

3. @hackathon_judge: "Saw four ElevenLabs projects this weekend. The one that won
   had cloned a recognizable voice as the AI host. The others used default voices.
   Authenticity of the voice = authenticity of the demo."
   Likes: 489, Retweets: 134

4. @voiceaiweekly: "Pro tip: ElevenLabs multi-speaker is underused at hackathons.
   Two AI agents talking to each other in distinct voices is a demo that lands.
   PodcastGhost got a standing ovation at HackMedia '24 for exactly this."
   Likes: 367, Retweets: 89
""",

    "modal": """
X (Twitter) posts about Modal at hackathons:

1. @erikbern: "Modal is the only infra sponsor where the winning projects tend to be
   about *scale* as a feature. BatchVision processed a million images in 4 minutes
   on stage. That's a demo, not a prototype."
   Likes: 892, Retweets: 234

2. @modal_labs: "Hackathon tip: spin up 100 Modal containers in your demo. The
   horizontal scale visualization — watching jobs fan out in the dashboard — is
   a better demo moment than showing an inference result."
   Likes: 743, Retweets: 198

3. @chiphuyen: "TestFarm was the most technically interesting hackathon project I've
   seen this year. Using Modal to parallelize property-based testing isn't obvious —
   it required real engineering insight. That's what wins."
   Likes: 1.3k, Retweets: 356

4. @latentspace: "Modal winners tend to solve the same class of problem: 'this would
   take hours on a single machine.' If your project can say 'we did X in Y minutes
   using Z containers,' you're in contention."
   Likes: 567, Retweets: 151
""",

    "vercel": """
X (Twitter) posts about Vercel at hackathons:

1. @leeerob: "EdgeChat won because they could say '47ms globally' and prove it live
   with a latency map. Performance is a feature. Measure it, show it."
   Likes: 1.7k, Retweets: 451

2. @rauchg: "The hackathon projects built on Next.js App Router + Vercel AI SDK this
   year are shipping things that used to require a backend team. The combo is a
   genuine force multiplier for solo builders."
   Likes: 2.4k, Retweets: 632

3. @delba_oliveira: "ComponentForge demoed Figma → deployed URL in under 30 seconds.
   That's what instant previews on Vercel unlock — the feedback loop becomes the demo."
   Likes: 934, Retweets: 247

4. @shadcn: "Vercel's hackathon winners consistently use one trick: the preview URL.
   Send the judge a link before the presentation. If they've already clicked around,
   you start the pitch with a warmed-up audience."
   Likes: 1.2k, Retweets: 318
""",

    "mistral": """
X (Twitter) posts about Mistral at hackathons:

1. @arthurmensch: "PrivateMed won HealthHack EU because they addressed the real
   constraint: hospital data stays on-prem. On-device Mistral isn't a compromise —
   it's the right architecture for regulated industries."
   Likes: 1.1k, Retweets: 289

2. @mistral_ai: "Hackathon insight: our fine-tuning API is criminally underused.
   Teams that fine-tune on domain-specific data outperform teams prompting base
   models. The gap is larger than most expect."
   Likes: 876, Retweets: 231

3. @karpathy: "Mistral's efficiency angle is a real differentiator at hackathons.
   'We ran this on a $5/mo VPS' is a compelling story when your competitor is
   burning $50 of OpenAI credits per demo."
   Likes: 2.8k, Retweets: 743

4. @latentspace: "AnalyticsCopilot showed what cheap, fast inference unlocks:
   they could afford to run 10 LLM calls per SQL query for retry/refinement.
   Cost efficiency = more calls = better outputs."
   Likes: 634, Retweets: 168
""",

    "pinecone": """
X (Twitter) posts about Pinecone at hackathons:

1. @pinecone: "LegalMind won because retrieval quality was genuinely better than
   keyword search — they showed a side-by-side. If you're using Pinecone, benchmark
   your recall. The delta is your demo."
   Likes: 987, Retweets: 261

2. @jerryjliu0: "The PersonaEngine project at GameJam AI was brilliant — using
   Pinecone for NPC memory means characters *remember* past interactions. That's
   not a chatbot, that's a character."
   Likes: 1.4k, Retweets: 378

3. @hardmaru: "Vector search demos need one thing to land: a query that would fail
   with keyword search but succeeds semantically. SupportGenius showed this live.
   Judges immediately got the value prop."
   Likes: 723, Retweets: 192

4. @weaviate_io: "VideoSearch at HackVideo was the most creative Pinecone use I've
   seen — describing a scene in plain English and jumping to the timestamp. That's
   a product people would actually pay for."
   Likes: 512, Retweets: 136
""",
}

_GENERIC_DEVPOST = """
Devpost prior art for {sponsor}:

1. "AI Assistant for {sponsor}" — Voice-driven workflow automation.
   Stack: {sponsor}, OpenAI, FastAPI, React.
   Outcome: Finalist, AI Tools category.
   URL: https://devpost.com/software/ai-assistant-{sponsor}

2. "DataBridge {sponsor}" — Semantic search over enterprise data using {sponsor} APIs.
   Stack: {sponsor}, Pinecone, Next.js.
   Outcome: 2nd place, Enterprise AI.
   URL: https://devpost.com/software/databridge-{sponsor}

3. "QuickDeploy {sponsor}" — One-click deployment scaffold for {sponsor}-powered apps.
   Stack: {sponsor}, Vercel, GitHub Actions.
   Outcome: Community Choice, Developer Tools.
   URL: https://devpost.com/software/quickdeploy-{sponsor}
"""

_GENERIC_X = """
X (Twitter) posts about {sponsor} at hackathons:

1. @hackathon_judge: "{sponsor} projects tend to win when they show a real workflow
   improvement, not just a demo. Build something you'd actually use."
   Likes: 312, Retweets: 78

2. @buildinpublic: "Used {sponsor} at the last hackathon — the docs are solid and
   the API is intuitive. Great choice for a 24-hour build."
   Likes: 245, Retweets: 61

3. @aiweekly: "Seeing more {sponsor} integrations at hackathons this year.
   The teams that win combine it with a strong UX, not just a technical demo."
   Likes: 189, Retweets: 44
"""


def mock_search_prior_art(sponsor_name: str, source_type: str) -> str:
    """
    Return mock Devpost or X/Twitter prior-art data for a given sponsor.

    Args:
        sponsor_name: Name of the sponsor (e.g. 'groq', 'supabase', 'elevenlabs')
        source_type: Either 'devpost' or 'x'
    """
    key = sponsor_name.lower().strip()
    if source_type == "devpost":
        return _DEVPOST_DATA.get(key, _GENERIC_DEVPOST.format(sponsor=sponsor_name))
    else:
        return _X_DATA.get(key, _GENERIC_X.format(sponsor=sponsor_name))


mock_search_prior_art_tool = function_tool(mock_search_prior_art)
