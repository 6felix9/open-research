export interface Sponsor {
  id: string;
  name: string;
  color: string;
  blurb: string;
}

export interface Idea {
  id: string;
  title: string;
  pitch: string;
  stack: string[];
  match: number;
  breakdown: { sponsor: number; interest: number; novelty: number };
  difficulty: 1 | 2 | 3;
  priorArt: { title: string; meta: string; url: string };
  why: string;
  risks: string;
  demoMoment: string;
}

export interface LogEntry {
  id: string;
  step: string;
  text?: string;
  quote?: string;
  sub?: string;
  requires?: string;
  final?: boolean;
}

export const SPONSORS: Sponsor[] = [
  { id: "groq",       name: "Groq",        color: "var(--s-1)", blurb: "Sub-100ms inference; rewards latency-sensitive UX" },
  { id: "anthropic",  name: "Anthropic",   color: "var(--s-2)", blurb: "Long-context + tool use; computer-use beta available" },
  { id: "modal",      name: "Modal",       color: "var(--s-3)", blurb: "Serverless GPUs; spin H100s on per-request basis" },
  { id: "supabase",   name: "Supabase",    color: "var(--s-4)", blurb: "pgvector + realtime + auth; ships fast for full apps" },
  { id: "vercel",     name: "Vercel",      color: "var(--s-5)", blurb: "Edge functions, AI SDK, streaming UI primitives" },
  { id: "elevenlabs", name: "ElevenLabs",  color: "var(--s-6)", blurb: "Realtime voice agents; rewards conversation demos" },
  { id: "mistral",    name: "Mistral",     color: "var(--s-7)", blurb: "OSS models; bonus for fine-tunes and self-hosted" },
  { id: "pinecone",   name: "Pinecone",    color: "var(--s-8)", blurb: "Hosted vector DB; serverless tier this season" },
];

export const INTERESTS: string[] = [
  "agents", "voice", "multimodal", "RAG", "fine-tuning",
  "evals", "browser-automation", "robotics", "vision",
  "code-gen", "synthetic-data", "small-models", "embeddings",
  "audio-gen", "video-gen", "structured-output", "memory",
  "tool-use", "MCP", "spatial", "AR", "music",
  "education", "developer-tools", "creative", "health",
  "accessibility", "climate", "finance", "open-source",
];

export const TEAM_SKILLS: string[] = ["frontend", "backend", "ML", "design", "infra", "mobile"];
export const TIME_BUDGET: string[] = ["24h", "36h", "48h"];

export const LOG_ENTRIES: Array<{ entry: LogEntry; state: "done" | "running" | "idle"; displayText: string; startedAt: number; }> = [
  {
    entry: { id: "parse", step: "01 · INTAKE" },
    state: "done",
    displayText: 'Parsing brief: "tools that make creative work feel less lonely" with seed → "no seed". Locked 5 interest tags and 4 sponsors.',
    startedAt: Date.now() - 38000,
  },
  {
    entry: { id: "sponsors", step: "02 · SPONSOR LANDSCAPE" },
    state: "done",
    displayText: "Mapping each sponsor's incentive structure against the brief…",
    startedAt: Date.now() - 35000,
  },
  {
    entry: { id: "groq-insight", step: "03 · INSIGHT", quote: "Groq tends to reward latency-sensitive flows — anything where a conversational loop or a real-time decision is the demo moment. Pair with voice or live data and the prize odds spike." },
    state: "done",
    displayText: "Groq tends to reward latency-sensitive flows — anything where a conversational loop or a real-time decision is the demo moment. Pair with voice or live data and the prize odds spike.",
    startedAt: Date.now() - 32000,
  },
  {
    entry: { id: "prior-art", step: "04 · PRIOR ART SCAN" },
    state: "done",
    displayText: 'Searching Devpost, HF Spaces, Show HN and recent winners. Filtering for projects that align to "tools that make creative work feel less lonely" but leave headroom.',
    startedAt: Date.now() - 28000,
  },
  {
    entry: { id: "anthropic-insight", step: "05 · INSIGHT", quote: "Long-context plus Computer Use is being underused in hackathon submissions — judges have seen six chatbots. A computer-use agent that finishes a real task on screen is still rare." },
    state: "done",
    displayText: "Long-context plus Computer Use is being underused in hackathon submissions — judges have seen six chatbots. A computer-use agent that finishes a real task on screen is still rare.",
    startedAt: Date.now() - 24000,
  },
  {
    entry: { id: "synthesize", step: "06 · SYNTHESIS" },
    state: "done",
    displayText: "Generating idea seeds — biasing toward (a) tight 48h scope, (b) at least one sponsor where you're stack-compatible, (c) one moment of demo theatre.",
    startedAt: Date.now() - 20000,
  },
  {
    entry: { id: "rank", step: "07 · RANKING" },
    state: "done",
    displayText: "Scoring 14 candidates on novelty × sponsor-fit × buildability × demo legibility. Discarding 6 below threshold.",
    startedAt: Date.now() - 14000,
  },
  {
    entry: { id: "ship", step: "08 · COMPLETE", final: true },
    state: "done",
    displayText: "8 ideas ready. Ordered by composite match. Prior-art links attached where citable.",
    startedAt: Date.now() - 8000,
  },
];

export const SYNERGY_TEXT = "Three of your selected sponsors (Groq + ElevenLabs + Supabase) tend to combine in winning entries — the realtime voice triangle. 2 of the top 5 ideas use this stack.";

export const IDEAS: Idea[] = [
  {
    id: "i1",
    title: "Standup, but it's an agent that already ran it",
    pitch: "Voice agent dials each teammate at their preferred hour, holds a 90-second async standup, transcribes blockers into a Linear-style board, and posts the digest to Slack before the human standup would have started.",
    stack: ["groq", "elevenlabs", "supabase"],
    match: 94,
    breakdown: { sponsor: 38, interest: 34, novelty: 22 },
    difficulty: 2,
    priorArt: {
      title: "Bumblebee — async voice retros for distributed teams",
      meta: "Devpost · MLH Fellowship Showcase '24 · 312★",
      url: "#",
    },
    why: "Three sponsors stack cleanly: Groq does the latency floor, ElevenLabs sells the demo, Supabase carries state. Cross-checked against 4 standup tools — none use a real outbound voice loop.",
    risks: "Telephony auth is finicky. Have a fallback to browser-mic if Twilio numbers don't come through.",
    demoMoment: "Live-call a judge's phone during the pitch. They hear the agent. They answer.",
  },
  {
    id: "i2",
    title: "Receipt-driven warranty agent",
    pitch: "Snap a photo of any receipt. The agent extracts the SKU, looks up the warranty terms, files a calendar entry for the expiry, and offers to draft the claim email the day before something breaks down.",
    stack: ["anthropic", "modal"],
    match: 87,
    breakdown: { sponsor: 30, interest: 32, novelty: 25 },
    difficulty: 2,
    priorArt: {
      title: "Stash — automated proof-of-purchase wallet",
      meta: "Hacker News · 2023 · YC W23 batch",
      url: "#",
    },
    why: "Computer-use angle: the agent actually navigates the manufacturer's claim form on demo. That's the moment.",
    risks: "OCR on creased receipts is a long tail. Cache the 50 most common retailers.",
    demoMoment: "On stage, agent files a real warranty claim against a $3 mug. Watch the form fill itself.",
  },
  {
    id: "i3",
    title: "PR-review agent that explains itself in the diff",
    pitch: "GitHub app. On every PR it leaves inline comments backed by a graph of the codebase — but each comment links to the exact training examples or docs that informed the suggestion. Auditable AI review.",
    stack: ["anthropic", "pinecone", "vercel"],
    match: 82,
    breakdown: { sponsor: 32, interest: 30, novelty: 20 },
    difficulty: 3,
    priorArt: {
      title: "Greptile · CodeRabbit — automated PR review",
      meta: "Devpost YC AI '24 · 4 finalists",
      url: "#",
    },
    why: "The 'cite your sources' angle is what's missing in the space. Judges from Anthropic care about interpretability.",
    risks: "Building the codebase graph eats time. Use tree-sitter + cache aggressively.",
    demoMoment: "Click a comment → side panel scrolls to the exact 12 lines that informed it. The 'aha'.",
  },
  {
    id: "i4",
    title: "A debugger that runs your code in 1000 alternate universes",
    pitch: "Pin a failing test. The agent forks the repo across Modal containers, mutates input combinatorially, and shows you the failure boundary as a 2D heatmap. Not 'what broke' — 'where the cliff is.'",
    stack: ["modal", "anthropic"],
    match: 79,
    breakdown: { sponsor: 28, interest: 28, novelty: 23 },
    difficulty: 3,
    priorArt: {
      title: "Hypothesis · property-based testing",
      meta: "PyCon talk · 2023 · OSS adoption growing",
      url: "#",
    },
    why: "Modal's per-request GPUs make this economically possible. Hard to demo casually — but the heatmap is gorgeous.",
    risks: "Combinatorial explosion. Need a smart pruning strategy or you'll burn through credits.",
    demoMoment: "Heatmap renders live. A coastline of failure. Audience leans in.",
  },
  {
    id: "i5",
    title: "Voice-first onboarding for any SaaS",
    pitch: "Drop a script tag. First-time users hear a real voice greet them by context (where they came from, what they clicked) and walks them through setup as a 60-second conversation instead of a 12-step tour.",
    stack: ["elevenlabs", "vercel", "groq"],
    match: 76,
    breakdown: { sponsor: 30, interest: 26, novelty: 20 },
    difficulty: 2,
    priorArt: {
      title: "Userpilot · Pendo — guided product tours",
      meta: "G2 category · $200M+ ARR space",
      url: "#",
    },
    why: "Conversational onboarding is the next category. Three sponsor stack lights up.",
    risks: "Voice in B2B is contentious. Make it opt-in and toggleable, not in-your-face.",
    demoMoment: "Live demo: visit a fake SaaS, the agent greets the judge by name from the QR they scanned.",
  },
  {
    id: "i6",
    title: "Synthetic users for usability tests",
    pitch: "Upload your Figma. The agent simulates 30 personas — each with their own goals, accessibility needs, and friction tolerance — clicking through the prototype and writing heatmap-style critiques.",
    stack: ["anthropic", "modal", "pinecone"],
    match: 73,
    breakdown: { sponsor: 26, interest: 27, novelty: 20 },
    difficulty: 3,
    priorArt: {
      title: "Maze · UserTesting — remote usability testing",
      meta: "Devpost · multiple AI-UX projects '24",
      url: "#",
    },
    why: "Replaces a real-money process. Demo is visual. Computer-use clicks through your Figma prototype on stage.",
    risks: "Persona fidelity matters — generic personas will read as fake. Ground them in real survey data.",
    demoMoment: "Upload audience's own Figma, replay 5 personas trying to check out. Two get stuck on the same modal.",
  },
  {
    id: "i7",
    title: "Background-research worker that ships citations to your inbox",
    pitch: "An always-on Modal worker watching your calendar. 30 min before each meeting it scrapes the attendees' recent writing, pinned posts, and one surprising public fact — delivered as a one-pager with footnotes.",
    stack: ["modal", "mistral", "supabase"],
    match: 71,
    breakdown: { sponsor: 27, interest: 24, novelty: 20 },
    difficulty: 2,
    priorArt: {
      title: "Clay · Common Room — relationship intelligence",
      meta: "Y Combinator '23 · prod-market fit",
      url: "#",
    },
    why: "Open-source model angle keeps it cheap. Mistral fine-tune on summary style is a credible prize hook.",
    risks: "Privacy optics. Hard-cap to public data and put consent gating front and center.",
    demoMoment: "Pull up a one-pager about a judge using only their public footprint. Land one specific detail.",
  },
  {
    id: "i8",
    title: "Music-theory tutor that hears you play",
    pitch: "Browser-only. Pick an instrument, play. The agent listens, transcribes the line, and explains what scale you're improvising in — and what one note would surprise you. Built for learners who can't read sheet music.",
    stack: ["groq", "vercel"],
    match: 68,
    breakdown: { sponsor: 24, interest: 24, novelty: 20 },
    difficulty: 2,
    priorArt: {
      title: "Yousician · Soundslice — interactive music ed",
      meta: "Indie space · multiple winners at MIT MusicHack",
      url: "#",
    },
    why: "Latency is the product. Groq wins or this doesn't ship. Vercel's streaming primitives make the UI feel alive.",
    risks: "Pitch detection in noisy rooms is hard. Demo in a treated room or use a direct line-in.",
    demoMoment: "Play 4 bars. The screen highlights the implied chord. Suggests the surprising note. You play it.",
  },
];
