import { useState } from 'react'
import { IDEAS, SPONSORS, type Idea } from '../data'

function getSponsor(id: string) {
  return SPONSORS.find(s => s.id === id)!
}

function PinIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.5 1.5l4 4-2 1-3 3 1 4-2-1.5L4 16l4.5-4.5L7 9.5l3-3 1-2z"/>
    </svg>
  )
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

function CompareIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="3" width="5" height="10" rx="1"/>
      <rect x="9" y="3" width="5" height="10" rx="1"/>
    </svg>
  )
}

interface IdeaCardProps {
  idea: Idea
  isPinned: boolean
  isExpanded: boolean
  onPin: () => void
  onExpand: () => void
}

function IdeaCard({ idea, isPinned, isExpanded, onPin, onExpand }: IdeaCardProps) {
  const DIFF_LABELS = ['', 'trivial', 'moderate', 'ambitious'] as const

  return (
    <div className={`idea ${isPinned ? 'is-pinned' : ''}`}>
      <div className="idea__head">
        <div className="ring__wrap">
          <div className="ring" style={{ '--pct': idea.match } as React.CSSProperties}>
            <div className="ring__val">{idea.match}</div>
          </div>
          <div className="ring__breakdown">
            <div className="bd-row"><span>sponsor fit</span><b>+{idea.breakdown.sponsor}</b></div>
            <div className="bd-row"><span>interest overlap</span><b>+{idea.breakdown.interest}</b></div>
            <div className="bd-row"><span>novelty</span><b>+{idea.breakdown.novelty}</b></div>
          </div>
        </div>
        <div>
          <div className="idea__title">{idea.title}</div>
          <div className="idea__pitch">{idea.pitch}</div>
        </div>
        <div className="idea__actions">
          <button className="icon-btn" title="Add to compare">
            <CompareIcon />
          </button>
          <button className="icon-btn" aria-pressed={isPinned} onClick={onPin} title="Pin">
            <PinIcon />
          </button>
          <button className="icon-btn" onClick={onExpand} title="Expand">
            {isExpanded ? <CollapseIcon /> : <ExpandIcon />}
          </button>
        </div>
      </div>

      <div className="idea__stack">
        {idea.stack.map(id => {
          const s = getSponsor(id)
          return (
            <span key={id} className="stack-chip" style={{ '--c': s.color } as React.CSSProperties}>
              <span className="stack-chip__dot" />
              {s.name}
            </span>
          )
        })}
      </div>

      <a className="idea__priorart" href={idea.priorArt.url} onClick={e => e.preventDefault()}>
        <div>
          <div className="idea__priorart__label">Prior art · validates direction</div>
          <div className="idea__priorart__title">{idea.priorArt.title}</div>
          <div className="idea__priorart__meta">{idea.priorArt.meta}</div>
        </div>
        <span className="idea__priorart__arrow">↗</span>
      </a>

      <div className="idea__footer">
        <span>
          build effort ·{' '}
          <span style={{ color: 'var(--ink-1)' }}>{DIFF_LABELS[idea.difficulty]}</span>
        </span>
        <span className="idea__diff">
          {[0, 1, 2].map(i => (
            <span key={i} className={`idea__diff__bar ${i < idea.difficulty ? 'on' : ''}`} />
          ))}
        </span>
      </div>

      {isExpanded && (
        <div className="idea__expand">
          <div className="idea__expand__row">
            <div className="idea__expand__label">Why now</div>
            <div className="idea__expand__val">{idea.why}</div>
          </div>
          <div className="idea__expand__row">
            <div className="idea__expand__label">Risks</div>
            <div className="idea__expand__val">{idea.risks}</div>
          </div>
          <div className="idea__expand__row">
            <div className="idea__expand__label">Demo moment</div>
            <div className="idea__expand__val">{idea.demoMoment}</div>
          </div>
        </div>
      )}
    </div>
  )
}

type FilterType = 'all' | 'highMatch' | 'easy' | 'pinned'
type SortType = 'match' | 'diff' | 'order'

export default function IdeaCards() {
  const [pinned, setPinned] = useState<Set<string>>(new Set())
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

  let shown = [...IDEAS]
  if (filter === 'pinned') shown = shown.filter(i => pinned.has(i.id))
  if (filter === 'highMatch') shown = shown.filter(i => i.match >= 80)
  if (filter === 'easy') shown = shown.filter(i => i.difficulty <= 2)
  if (sort === 'match') shown.sort((a, b) => b.match - a.match)
  if (sort === 'diff') shown.sort((a, b) => a.difficulty - b.difficulty)

  const filters: Array<{ id: FilterType; label: string; count: number }> = [
    { id: 'all',       label: 'All',       count: IDEAS.length },
    { id: 'highMatch', label: '≥80 match', count: IDEAS.filter(i => i.match >= 80).length },
    { id: 'easy',      label: 'Easy build', count: IDEAS.filter(i => i.difficulty <= 2).length },
    { id: 'pinned',    label: 'Pinned',    count: pinned.size },
  ]

  return (
    <section className="ideas-pane">
      <div className="ideas-toolbar">
        <div className="ideas-toolbar__filters">
          {filters.map(f => (
            <button
              key={f.id}
              className="filter-pill"
              aria-pressed={filter === f.id}
              onClick={() => setFilter(f.id)}
            >
              {f.label}
              <span className="filter-pill__count">{f.count}</span>
            </button>
          ))}
        </div>
        <div className="ideas-toolbar__right">
          <span style={{ color: 'var(--ink-4)', letterSpacing: '0.12em', fontSize: 9.5, textTransform: 'uppercase' }}>sort</span>
          <div className="segmented" style={{ padding: 2, maxWidth: 200 }}>
            {(['match', 'diff', 'order'] as SortType[]).map(o => (
              <button key={o} aria-pressed={sort === o} onClick={() => setSort(o)}>
                {o === 'diff' ? 'effort' : o}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="ideas-grid">
        {shown.map(idea => (
          <IdeaCard
            key={idea.id}
            idea={idea}
            isPinned={pinned.has(idea.id)}
            isExpanded={expanded.has(idea.id)}
            onPin={() => toggle(setPinned, idea.id)}
            onExpand={() => toggle(setExpanded, idea.id)}
          />
        ))}
      </div>
    </section>
  )
}
