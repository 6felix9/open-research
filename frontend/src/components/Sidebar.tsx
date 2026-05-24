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
  runState: 'idle' | 'running' | 'done'
  onRun: () => void
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
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="brand-mark" />
        <div>
          <div className="brand-title">Open Research</div>
          <div className="brand-sub">agentic hackathon ideation</div>
        </div>
      </div>

      <div className="sidebar__scroll">
        <div className="section">
          <div className="section__header">
            <div className="section__label">Sponsors</div>
            <div className="section__meta">{selectedSponsors.size}/{SPONSORS.length}</div>
          </div>
          <div className="chips">
            {SPONSORS.map(s => (
              <button
                key={s.id}
                className="chip"
                style={{ '--c': s.color } as React.CSSProperties}
                aria-pressed={selectedSponsors.has(s.id)}
                onClick={() => toggleSponsor(s.id)}
                title={s.blurb}
              >
                <span className="chip__dot" />
                {s.name}
              </button>
            ))}
          </div>
        </div>

        <div className="section">
          <div className="section__header">
            <div className="section__label">Tech interests</div>
            <div className="section__meta">{selectedInterests.size} on</div>
          </div>
          <div className="tags">
            {INTERESTS.map(tag => (
              <button
                key={tag}
                className="tag"
                aria-pressed={selectedInterests.has(tag)}
                onClick={() => toggleInterest(tag)}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        <div className="section">
          <div className="section__label">Theme</div>
          <div className="field">
            <textarea
              rows={2}
              placeholder="e.g. tools that make creative work less lonely"
              value={theme}
              onChange={e => setTheme(e.target.value)}
            />
          </div>
        </div>

        <details className="advanced-toggle">
          <summary>Advanced</summary>
          <div className="advanced-toggle__body">
            <div className="section">
              <div className="section__label">Seed idea (optional)</div>
              <div className="field">
                <textarea
                  rows={3}
                  placeholder="A loose hunch or constraint — the agent will branch from it."
                  value={seed}
                  onChange={e => setSeed(e.target.value)}
                />
              </div>
            </div>

            <div className="section">
              <div className="section__label">Team skills</div>
              <div className="tags">
                {TEAM_SKILLS.map(s => (
                  <button
                    key={s}
                    className="tag"
                    aria-pressed={skills.has(s)}
                    onClick={() => toggleSkill(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="section">
              <div className="section__label">Time budget</div>
              <div className="segmented">
                {TIME_BUDGET.map(t => (
                  <button
                    key={t}
                    aria-pressed={timeBudget === t}
                    onClick={() => setTimeBudget(t)}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div className="section">
              <div className="section__header">
                <div className="section__label">Research depth</div>
                <div className="section__meta">{DEPTH_NAMES[depth]}</div>
              </div>
              <div className="segmented">
                {DEPTH_LABELS.map((label, i) => (
                  <button
                    key={label}
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

      <div className="sidebar__cta">
        <button
          className="run-btn"
          data-state={runState}
          onClick={onRun}
          disabled={runState === 'running'}
        >
          <span>
            {runState === 'running' ? 'Researching…' : runState === 'done' ? 'Run again' : 'Research ideas'}
          </span>
          <span className="run-btn__arrow">→</span>
        </button>
      </div>
    </aside>
  )
}
