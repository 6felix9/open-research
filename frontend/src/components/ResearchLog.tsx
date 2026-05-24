import { LOG_ENTRIES, SYNERGY_TEXT } from '../data'

interface LogRowProps {
  state: 'done' | 'running' | 'idle'
  step: string
  text?: string
  quote?: string
}

function LogRow({ state, step, text, quote }: LogRowProps) {
  return (
    <div className="log-row" data-state={state}>
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
      </div>
    </div>
  )
}

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
        {LOG_ENTRIES.map(({ entry, state, displayText }) => (
          <LogRow
            key={entry.id}
            state={state}
            step={entry.step.replace(/^\d+ · /, '')}
            text={entry.quote ? undefined : displayText}
            quote={entry.quote ? displayText : undefined}
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
