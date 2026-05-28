import { useState } from 'react'
import { IDEAS, SPONSORS, type Idea } from '../data'

function getSponsor(id: string) {
  return SPONSORS.find(s => s.id === id)!
}

function ExpandIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 8h10M8 3v10"/>
    </svg>
  )
}

function CollapseIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 8h10"/>
    </svg>
  )
}

interface IdeaCardProps {
  idea: Idea
  isExpanded: boolean
  onExpand: () => void
}

function IdeaCard({ idea, isExpanded, onExpand }: IdeaCardProps) {
  return (
    <div className="bg-bg-1 border border-line-0 rounded-lg p-[16px_16px_14px] flex flex-col gap-[12px] relative transition-all duration-[200ms] ease-out hover:border-line-1 focus-within:border-amber-dim focus-within:shadow-[0_0_0_1px_var(--amber-glow)]">
      <div className="grid grid-cols-[auto_1fr_auto] gap-[12px] items-start">
        <div className="relative group/ring">
          <div className="w-[44px] h-[44px] rounded-full relative shrink-0 bg-[conic-gradient(var(--amber)_calc(var(--pct)*1%),var(--bg-3)_0)] before:content-[''] before:absolute before:inset-[3px] before:bg-bg-1 before:rounded-full" style={{ '--pct': idea.match } as React.CSSProperties}>
            <div className="absolute inset-0 grid place-items-center font-mono text-[12px] text-ink-0 font-medium">{idea.match}</div>
          </div>
          <div className="absolute bottom-[calc(100%+8px)] left-[-8px] bg-bg-2 border border-line-1 rounded-[6px] p-[10px_12px] font-mono text-[11px] text-ink-1 whitespace-nowrap opacity-0 pointer-events-none transition-opacity duration-[120ms] ease-out z-10 shadow-[0_8px_24px_oklch(0_0_0/0.4)] group-hover/ring:opacity-100">
            <div className="grid grid-cols-[auto_auto] gap-[18px] py-[1px] px-0"><span>sponsor fit</span><b className="text-ink-0 font-medium">+{idea.breakdown.sponsor}</b></div>
            <div className="grid grid-cols-[auto_auto] gap-[18px] py-[1px] px-0"><span>interest overlap</span><b className="text-ink-0 font-medium">+{idea.breakdown.interest}</b></div>
            <div className="grid grid-cols-[auto_auto] gap-[18px] py-[1px] px-0"><span>novelty</span><b className="text-ink-0 font-medium">+{idea.breakdown.novelty}</b></div>
          </div>
        </div>
        <div>
          <div className="font-serif text-[18px] leading-[1.2] text-ink-0">{idea.title}</div>
          <div className="text-ink-1 text-[12.5px] leading-[1.5] mt-[4px]">{idea.pitch}</div>
        </div>
        <div className="flex gap-[4px] shrink-0">
          <button className="w-[28px] h-[28px] rounded-[5px] border border-transparent bg-transparent text-ink-3 cursor-pointer grid place-items-center transition-all duration-[120ms] ease-out hover:text-ink-0 hover:border-line-1 hover:bg-bg-2 aria-pressed:text-amber-theme aria-pressed:border-amber-dim aria-pressed:bg-amber-glow [&_svg]:w-[14px] [&_svg]:h-[14px]" onClick={onExpand} title="Expand">
            {isExpanded ? <CollapseIcon /> : <ExpandIcon />}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-[5px]">
        {idea.stack.map(id => {
          const s = getSponsor(id)
          return (
            <span key={id} className="inline-flex items-center gap-[5px] py-[3px] pr-[8px] pb-[3px] pl-[6px] font-mono text-[10.5px] rounded-[4px] bg-bg-2 border border-line-0 text-ink-1 tracking-[0.02em]" style={{ '--c': s.color } as React.CSSProperties}>
              <span className="w-[6px] h-[6px] rounded-full bg-[var(--c,var(--ink-3))]" />
              {s.name}
            </span>
          )
        })}
      </div>

      <a className="flex items-start gap-[10px] p-[10px_12px] bg-bg-0 border border-line-0 rounded-md text-[11.5px] no-underline text-ink-1 transition-all duration-[140ms] ease-out hover:border-amber-dim hover:bg-[color-mix(in_oklch,var(--amber)_6%,var(--bg-0))]" href={idea.priorArt.url} onClick={e => e.preventDefault()}>
        <div>
          <div className="font-mono text-[9.5px] text-ink-3 tracking-[0.22em] uppercase mb-[2px]">Prior art · validates direction</div>
          <div className="text-ink-0 text-[12px] font-sans leading-[1.35]">{idea.priorArt.title}</div>
          <div className="font-mono text-[10px] text-ink-3 mt-[2px]">{idea.priorArt.meta}</div>
        </div>
        <span className="font-mono text-ink-3 ml-auto self-center shrink-0">↗</span>
      </a>

      <div className="flex justify-between items-center font-mono text-[10px] text-ink-3 tracking-[0.05em] mt-[2px]">
        <span className="flex gap-[4px]">
          {[0, 1, 2].map(i => (
            <span key={i} className={`w-[24px] h-[3px] rounded-[2px] ${i < idea.difficulty ? 'bg-amber-theme' : 'bg-bg-3'}`} />
          ))}
        </span>
      </div>

      {isExpanded && (
        <div className="border-t border-dashed border-line-0 pt-[12px] mt-[4px] grid gap-[10px] text-[12px] text-ink-1">
          <div className="grid grid-cols-[84px_1fr] gap-[10px]">
            <div className="font-mono text-[9.5px] tracking-[0.18em] uppercase text-ink-3 pt-[2px]">Why now</div>
            <div className="text-ink-1 leading-[1.5]">{idea.why}</div>
          </div>
          <div className="grid grid-cols-[84px_1fr] gap-[10px]">
            <div className="font-mono text-[9.5px] tracking-[0.18em] uppercase text-ink-3 pt-[2px]">Risks</div>
            <div className="text-ink-1 leading-[1.5]">{idea.risks}</div>
          </div>
          <div className="grid grid-cols-[84px_1fr] gap-[10px]">
            <div className="font-mono text-[9.5px] tracking-[0.18em] uppercase text-ink-3 pt-[2px]">Demo moment</div>
            <div className="text-ink-1 leading-[1.5]">{idea.demoMoment}</div>
          </div>
        </div>
      )}
    </div>
  )
}

type FilterType = 'all' | 'highMatch' | 'easy' | 'pinned'
type SortType = 'match' | 'diff' | 'order'

const ORDER = [...IDEAS]

export default function IdeaCards({ onViewLog }: { onViewLog?: () => void }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [filter, setFilter] = useState<FilterType>('all')
  const [sort, setSort] = useState<SortType>('match')

  const toggle = (setter: React.Dispatch<React.SetStateAction<Set<string>>>, val: string) => {
    setter(prev => {
      const next = new Set(prev)
      if (next.has(val)) next.delete(val)
      else next.add(val)
      return next
    })
  }

  let shown = [...ORDER]
  if (filter === 'highMatch') shown = shown.filter(i => i.match >= 80)
  if (filter === 'easy') shown = shown.filter(i => i.difficulty <= 2)
  if (filter === 'pinned') shown = []
  if (sort === 'match') shown.sort((a, b) => b.match - a.match)
  if (sort === 'diff') shown.sort((a, b) => a.difficulty - b.difficulty)

  const filters: Array<{ id: FilterType; label: string; count: number }> = [
    { id: 'all',       label: 'All',       count: IDEAS.length },
    { id: 'highMatch', label: '≥80 Match', count: IDEAS.filter(i => i.match >= 80).length },
    { id: 'easy',      label: 'Easy Build', count: IDEAS.filter(i => i.difficulty <= 2).length },
    { id: 'pinned',    label: 'Pinned',    count: 0 },
  ]

  return (
    <section className="grid grid-rows-[auto_1fr] min-h-0 flex-1">
      <div className="flex items-center justify-between gap-[12px] p-[12px_20px] border-b border-line-0 bg-bg-1 flex-wrap">
        <div className="flex gap-[4px] flex-wrap">
          {filters.map(f => (
            <button
              key={f.id}
              className="font-mono text-[10.5px] tracking-[0.08em] uppercase text-ink-3 bg-transparent border border-line-0 rounded-[4px] py-[4px] px-[8px] cursor-pointer transition-all duration-[120ms] ease-out hover:text-ink-1 aria-pressed:bg-bg-2 aria-pressed:text-ink-0 aria-pressed:border-line-1"
              aria-pressed={filter === f.id}
              onClick={() => setFilter(f.id)}
            >
              {f.label}
              <span className="text-ink-4 ml-[4px]">{f.count}</span>
            </button>
          ))}
        </div>
        <div className="flex items-center gap-[8px] font-mono text-[11px] text-ink-3">
          {onViewLog && (
            <button className="font-mono text-[10px] tracking-[0.16em] uppercase text-ink-3 bg-transparent border border-line-0 rounded-[4px] py-[4px] px-[9px] cursor-pointer transition-all duration-[120ms] ease hover:text-ink-1 hover:border-line-1 hover:bg-bg-2" onClick={onViewLog}>View log</button>
          )}
          <span className="font-mono text-[10px] tracking-[0.18em] uppercase text-ink-3">Sort</span>
          <div className="grid grid-flow-col auto-cols-fr bg-bg-0 border border-line-0 rounded-md p-[2px] gap-[2px]" style={{ padding: 2 }}>
            {([['match', 'match'], ['diff', 'effort'], ['order', 'stream']] as [SortType, string][]).map(([id, label]) => (
              <button key={id} className="bg-transparent border-0 font-mono text-[11px] text-ink-2 py-[6px] px-[4px] rounded-[4px] cursor-pointer tracking-[0.04em] aria-pressed:bg-bg-2 aria-pressed:text-ink-0" aria-pressed={sort === id} onClick={() => setSort(id)}>
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="overflow-y-auto p-[16px_20px_28px] grid grid-cols-[repeat(auto-fill,minmax(360px,1fr))] gap-[14px] content-start [&::-webkit-scrollbar]:w-[8px] [&::-webkit-scrollbar-thumb]:bg-line-1 [&::-webkit-scrollbar-thumb]:rounded-[4px]">
        {shown.map(idea => (
          <IdeaCard
            key={idea.id}
            idea={idea}
            isExpanded={expanded.has(idea.id)}
            onExpand={() => toggle(setExpanded, idea.id)}
          />
        ))}
      </div>
    </section>
  )
}
