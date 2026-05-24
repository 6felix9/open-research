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
    <div className="idea">
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

const ORDER = [...IDEAS]

export default function IdeaCards() {
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
          <span className="ideas-toolbar__sort-label">Sort</span>
          <div className="segmented" style={{ padding: 2 }}>
            {([['match', 'match'], ['diff', 'effort'], ['order', 'stream']] as [SortType, string][]).map(([id, label]) => (
              <button key={id} aria-pressed={sort === id} onClick={() => setSort(id)}>
                {label}
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
            isExpanded={expanded.has(idea.id)}
            onExpand={() => toggle(setExpanded, idea.id)}
          />
        ))}
      </div>
    </section>
  )
}
