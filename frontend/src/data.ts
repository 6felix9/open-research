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
  error?: boolean;
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

