import { useState } from 'react'
import { SPONSORS, INTERESTS, TEAM_SKILLS, TIME_BUDGET } from '../data'

interface SidebarProps {
  selectedSponsors: Set<string>
  toggleSponsor: (id: string) => void
  selectedInterests: Set<string>
  toggleInterest: (tag: string) => void
  theme: string
  setTheme: (v: string) => void
  seed: string
  setSeed: (v: string) => void
  skills: Set<string>
  toggleSkill: (s: string) => void
  timeBudget: string
  setTimeBudget: (v: string) => void
  depth: number
  setDepth: (v: number) => void
  runState: 'idle' | 'running' | 'done' | 'error'
  onRun: () => void
  customSponsorUrls: string[]
  addCustomSponsorUrl: (url: string) => void
  removeCustomSponsorUrl: (url: string) => void
  config: { reachable: boolean; serverKey: boolean } | null
  apiKey: string
  setApiKey: (v: string) => void
}

const DEPTH_LABELS = ['S', 'M', 'L', 'XL']
const DEPTH_NAMES = ['shallow', 'balanced', 'deep', 'obsessive']

export default function Sidebar({
  selectedSponsors, toggleSponsor,
  selectedInterests, toggleInterest,
  theme, setTheme,
  seed, setSeed,
  skills, toggleSkill,
  timeBudget, setTimeBudget,
  depth, setDepth,
  runState, onRun,
  customSponsorUrls, addCustomSponsorUrl, removeCustomSponsorUrl,
  config, apiKey, setApiKey,
}: SidebarProps) {
  const [urlInput, setUrlInput] = useState('')

  const submitUrl = () => {
    const trimmed = urlInput.trim()
    if (!trimmed) return
    addCustomSponsorUrl(trimmed)
    setUrlInput('')
  }

  const needsKey = !!config?.reachable && !config.serverKey
  const ready = config === null || (config.reachable && (config.serverKey || !!apiKey.trim()))

  return (
    <aside className="grid grid-rows-[auto_1fr_auto] bg-bg-1 border-r border-line-0 min-h-0">
      <div className="pt-[18px] px-[20px] pb-[14px] border-b border-dashed border-line-0 flex items-center gap-[12px]">
        <img src="/image.png" className="w-[28px] h-[28px] shrink-0 object-contain rounded-[6px] theme-invert-img" alt="" />
        <div>
          <div className="font-serif text-[22px] text-ink-0 tracking-[0.2px] leading-none">Open Research</div>
          <div className="font-mono text-[10px] text-ink-3 tracking-[0.18em] uppercase mt-[4px]">agentic hackathon ideation</div>
        </div>
      </div>

      <div className="overflow-y-auto pt-[18px] px-[20px] pb-[12px] flex flex-col gap-[22px] min-h-0 [scrollbar-gutter:stable] [scrollbar-width:thin] [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-thumb]:bg-line-1 [&::-webkit-scrollbar-thumb]:rounded-[3px]">
        <div className="flex flex-col gap-[10px]">
          <div className="flex items-baseline justify-between gap-[8px]">
            <div className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3">Sponsors <span className="text-amber-theme normal-case tracking-normal">*</span></div>
            <div className="font-mono text-[10px] text-ink-4 tracking-[0.05em]">{selectedSponsors.size}/{SPONSORS.length}</div>
          </div>
          <div className="flex flex-wrap gap-[6px]">
            {SPONSORS.map(s => (
              <button
                key={s.id}
                className="group inline-flex items-center gap-[7px] pt-[5px] pr-[10px] pb-[5px] pl-[8px] rounded-full bg-bg-2 border border-line-0 text-ink-1 text-[12px] font-sans cursor-pointer transition-all duration-[120ms] ease-out select-none hover:border-line-1 hover:bg-bg-3 aria-pressed:bg-[color-mix(in_oklch,var(--c)_16%,var(--bg-2))] aria-pressed:border-[color-mix(in_oklch,var(--c)_45%,var(--line-1))] aria-pressed:text-ink-0"
                style={{ '--c': s.color } as React.CSSProperties}
                aria-pressed={selectedSponsors.has(s.id)}
                onClick={() => toggleSponsor(s.id)}
                title={s.blurb}
              >
                <span className="w-[8px] h-[8px] rounded-full bg-[var(--c,var(--ink-3))] shadow-[0_0_0_1px_oklch(0_0_0/0.2)] group-aria-pressed:shadow-[0_0_0_1px_oklch(0_0_0/0.2),0_0_0_3px_color-mix(in_oklch,var(--c)_30%,transparent)]" />
                {s.name}
              </button>
            ))}
            {customSponsorUrls.map(url => {
              let label = url
              try { label = new URL(url).hostname } catch { /* ignore invalid URL */ }
              return (
                <span key={url} className="inline-flex items-center gap-[7px] pt-[5px] pr-[10px] pb-[5px] pl-[8px] rounded-full bg-bg-2 border border-line-0 text-ink-1 text-[12px] font-sans select-none cursor-default" title={url}>
                  <span className="w-[8px] h-[8px] rounded-full bg-ink-3 shadow-[0_0_0_1px_oklch(0_0_0/0.2)]" />
                  {label}
                  <button className="bg-none border-none text-ink-3 cursor-pointer text-[14px] leading-none pl-[2px] opacity-60 transition-opacity duration-[120ms] hover:opacity-100 hover:text-ink-0" onClick={() => removeCustomSponsorUrl(url)} title="Remove">×</button>
                </span>
              )
            })}
          </div>
          <div className="flex gap-[6px] items-center">
            <input
              className="flex-1 font-mono text-[11px] text-ink-1 bg-bg-0 border border-line-0 rounded-[6px] py-[5px] px-[9px] outline-none transition-colors duration-[120ms] min-w-0 placeholder-ink-4 focus:border-line-1"
              type="url"
              placeholder="Paste sponsor docs URL…"
              value={urlInput}
              onChange={e => setUrlInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') submitUrl() }}
            />
            <button className="font-mono text-[10.5px] tracking-[0.08em] uppercase py-[5px] px-[10px] rounded-[6px] border border-line-0 bg-bg-2 text-ink-2 cursor-pointer transition-all duration-[120ms] shrink-0 hover:enabled:border-line-1 hover:enabled:text-ink-0 hover:enabled:bg-bg-3 disabled:opacity-35 disabled:cursor-not-allowed" onClick={submitUrl} disabled={!urlInput.trim()}>Add</button>
          </div>
        </div>

        <div className="flex flex-col gap-[10px]">
          <div className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3">Theme <span className="text-amber-theme normal-case tracking-normal">*</span></div>
          <div className="flex flex-col gap-[6px]">
            <textarea
              className="bg-bg-0 border border-line-0 rounded-md text-ink-0 font-sans text-[13px] py-[9px] px-[11px] outline-none resize-none transition-all duration-[120ms] ease-out placeholder-ink-4 focus:border-amber-dim focus:shadow-[0_0_0_3px_var(--amber-glow)]"
              rows={2}
              placeholder="e.g. tools that make creative work less lonely"
              value={theme}
              onChange={e => setTheme(e.target.value)}
            />
          </div>
        </div>

        <details className="group border-t border-dashed border-line-0 pt-[14px] mt-[4px]">
          <summary className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3 cursor-pointer list-none flex items-center justify-between select-none [&::-webkit-details-marker]:hidden after:content-['›'] after:text-[14px] after:transition-transform after:duration-[200ms] group-open:after:rotate-90">Advanced</summary>
          <div className="flex flex-col gap-[22px] pt-[16px]">
            <div className="flex flex-col gap-[10px]">
              <div className="flex items-baseline justify-between gap-[8px]">
                <div className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3">Tech interests</div>
                <div className="font-mono text-[10px] text-ink-4 tracking-[0.05em]">{selectedInterests.size} on</div>
              </div>
              <div className="flex flex-wrap gap-[5px]">
                {INTERESTS.map(tag => (
                  <button
                    key={tag}
                    className="font-mono text-[11px] py-[4px] px-[8px] rounded-[4px] border border-line-0 bg-transparent text-ink-2 cursor-pointer transition-all duration-[120ms] ease-out select-none hover:text-ink-0 hover:border-line-1 aria-pressed:bg-ink-0 aria-pressed:text-bg-0 aria-pressed:border-ink-0"
                    aria-pressed={selectedInterests.has(tag)}
                    onClick={() => toggleInterest(tag)}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-[10px]">
              <div className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3">Seed idea (optional)</div>
              <div className="flex flex-col gap-[6px]">
                <textarea
                  className="bg-bg-0 border border-line-0 rounded-md text-ink-0 font-sans text-[13px] py-[9px] px-[11px] outline-none resize-none transition-all duration-[120ms] ease-out placeholder-ink-4 focus:border-amber-dim focus:shadow-[0_0_0_3px_var(--amber-glow)]"
                  rows={3}
                  placeholder="A loose hunch or constraint — the agent will branch from it."
                  value={seed}
                  onChange={e => setSeed(e.target.value)}
                />
              </div>
            </div>

            <div className="flex flex-col gap-[10px]">
              <div className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3">Team skills</div>
              <div className="flex flex-wrap gap-[5px]">
                {TEAM_SKILLS.map(s => (
                  <button
                    key={s}
                    className="font-mono text-[11px] py-[4px] px-[8px] rounded-[4px] border border-line-0 bg-transparent text-ink-2 cursor-pointer transition-all duration-[120ms] ease-out select-none hover:text-ink-0 hover:border-line-1 aria-pressed:bg-ink-0 aria-pressed:text-bg-0 aria-pressed:border-ink-0"
                    aria-pressed={skills.has(s)}
                    onClick={() => toggleSkill(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-[10px]">
              <div className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3">Time budget</div>
              <div className="grid grid-flow-col auto-cols-fr bg-bg-0 border border-line-0 rounded-md p-[2px] gap-[2px]">
                {TIME_BUDGET.map(t => (
                  <button
                    key={t}
                    className="bg-transparent border-0 font-mono text-[11px] text-ink-2 py-[6px] px-[4px] rounded-[4px] cursor-pointer tracking-[0.04em] aria-pressed:bg-bg-2 aria-pressed:text-ink-0"
                    aria-pressed={timeBudget === t}
                    onClick={() => setTimeBudget(t)}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-[10px]">
              <div className="flex items-baseline justify-between gap-[8px]">
                <div className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3">Research depth</div>
                <div className="font-mono text-[10px] text-ink-4 tracking-[0.05em]">{DEPTH_NAMES[depth]}</div>
              </div>
              <div className="grid grid-flow-col auto-cols-fr bg-bg-0 border border-line-0 rounded-md p-[2px] gap-[2px]">
                {DEPTH_LABELS.map((label, i) => (
                  <button
                    key={label}
                    className="bg-transparent border-0 font-mono text-[11px] text-ink-2 py-[6px] px-[4px] rounded-[4px] cursor-pointer tracking-[0.04em] aria-pressed:bg-bg-2 aria-pressed:text-ink-0"
                    aria-pressed={depth === i}
                    onClick={() => setDepth(i)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </details>
      </div>

      <div className="border-t border-dashed border-line-0 pt-[14px] px-[20px] pb-[18px] bg-bg-1 flex flex-col gap-[10px]">
        {config && !config.reachable && (
          <div className="text-[11.5px] p-[10px_12px] bg-[color-mix(in_oklch,var(--s-1)_8%,var(--bg-0))] border border-[color-mix(in_oklch,var(--s-1)_25%,var(--line-0))] rounded-[6px] text-ink-2 font-mono leading-[1.4] mb-[4px]">
            <div className="text-ink-0 font-sans font-medium mb-[4px] text-[12px] flex items-center gap-[6px]">
              <span className="w-[6px] h-[6px] rounded-full bg-[oklch(0.6_0.2_25)] animate-pulse" />
              Backend not reachable
            </div>
            <p className="text-[10px] text-ink-3">Research runs on a backend that isn't available here. Start it locally to run research.</p>
          </div>
        )}
        {needsKey && (
          <div className="flex flex-col gap-[6px] mb-[4px]">
            <label htmlFor="openai-key" className="font-mono text-[10px] tracking-[0.22em] uppercase text-ink-3">OpenAI API key <span className="text-amber-theme normal-case tracking-normal">*</span></label>
            <input
              id="openai-key"
              className="font-mono text-[11px] text-ink-1 bg-bg-0 border border-line-0 rounded-[6px] py-[6px] px-[9px] outline-none transition-colors duration-[120ms] placeholder-ink-4 focus:border-line-1"
              type="password"
              autoComplete="off"
              placeholder="sk-…"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
            />
            <p className="font-mono text-[10px] text-ink-4 leading-[1.5]">Sent with each request to run the research. Kept in this tab only; the server never stores it.</p>
          </div>
        )}
        <button
          className="flex items-center justify-between gap-[8px] py-[12px] px-[16px] rounded-md border border-amber-dim bg-[linear-gradient(180deg,color-mix(in_oklch,var(--amber)_20%,var(--bg-2)),var(--bg-2))] text-ink-0 font-sans text-[13px] font-medium cursor-pointer transition-all duration-[140ms] ease-out text-left tracking-[0.01em] w-full hover:enabled:bg-[linear-gradient(180deg,color-mix(in_oklch,var(--amber)_30%,var(--bg-2)),color-mix(in_oklch,var(--amber)_10%,var(--bg-2)))] hover:enabled:shadow-[0_0_0_3px_var(--amber-glow)] active:enabled:translate-y-[1px] data-[state=running]:border-amber-theme data-[state=running]:bg-bg-2 data-[state=running]:text-ink-0 data-[state=running]:cursor-progress disabled:opacity-40 disabled:cursor-not-allowed"
          data-state={runState}
          onClick={onRun}
          disabled={runState === 'running' || selectedSponsors.size === 0 || !theme.trim() || !ready}
        >
          <span>
            {runState === 'running' ? 'Researching…' : (runState === 'done' || runState === 'error') ? 'Run again' : 'Research ideas'}
          </span>
          <span className="font-mono text-[13px] text-amber-theme">→</span>
        </button>
        {runState !== 'running' && (selectedSponsors.size === 0 || !theme.trim()) && (
          <p className="font-mono text-[10px] text-ink-4 text-center">
            {selectedSponsors.size === 0 ? 'Select at least one sponsor' : 'Add a theme'} to continue
          </p>
        )}
      </div>
    </aside>
  )
}
