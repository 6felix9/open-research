import { LOG_ENTRIES, SYNERGY_TEXT } from '../data'

interface LogRowProps {
  state: 'done' | 'running' | 'idle'
  step: string
  text?: string
  quote?: string
  sub?: string
  tool: string
  timestamp: string
}

function LogRow({ state, step, text, quote, sub, tool, timestamp }: LogRowProps) {
  return (
    <div className="log-row" data-state={state}>
      <div className="log-row__time">{timestamp}</div>
      <div className="log-row__icon">
        <span className="log-icon" data-state={state} />
      </div>
      <div className="log-row__body">
        <div className="log-row__step">{step}</div>
        {quote != null ? (
          <div className="log-row__quote">"{quote}"</div>
        ) : (
          <div className="log-row__text">{text}</div>
        )}
        {sub && state !== 'idle' && (
          <div className="log-row__sub">
            {sub.split(' · ').map((part, i) => <span key={i}>{part}</span>)}
          </div>
        )}
      </div>
      <div className="log-row__tool">{tool}</div>
    </div>
  )
}

function fmtTime(msFromStart: number) {
  const s = Math.floor(msFromStart / 1000)
  const m = Math.floor(s / 60).toString().padStart(2, '0')
  const sec = (s % 60).toString().padStart(2, '0')
  return `${m}:${sec}.00`
}

const SESSION_START = Date.now() - 40000

export default function ResearchLog() {
  return (
    <section className="log-pane">
      <div className="pane-header">
        <div className="pane-header__left">
          <div className="pane-title">
            <span className="dot-led" data-state="done" />
            Research log
          </div>
        </div>
        <div className="pane-header__right">
          <span className="status-text">{LOG_ENTRIES.length} steps</span>
        </div>
      </div>
      <div className="thin-progress" data-state="done">
        <span style={{ width: '100%' }} />
      </div>
      <div className="log">
        {LOG_ENTRIES.map(({ entry, state, displayText, startedAt }) => (
          <LogRow
            key={entry.id}
            state={state}
            step={entry.step}
            text={entry.quote ? undefined : displayText}
            quote={entry.quote ? displayText : undefined}
            sub={entry.id === 'sponsors' ? 'Reading sponsor prizes · API docs · last year\'s winners' : undefined}
            tool={entry.id.split('-')[0]}
            timestamp={fmtTime(startedAt - SESSION_START)}
          />
        ))}
        <div className="synergy">
          <span className="synergy__icon">⌖</span>
          <div>
            <div className="synergy__label">Sponsor synergy detected</div>
            <div>{SYNERGY_TEXT}</div>
          </div>
        </div>
      </div>
    </section>
  )
}
