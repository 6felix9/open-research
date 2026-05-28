import { LOG_ENTRIES, SYNERGY_TEXT } from '../data'
import LogRow from './LogRow'

interface ResearchLogProps {
  onClose?: () => void
}

export default function ResearchLog({ onClose }: ResearchLogProps) {
  return (
    <section className="grid grid-rows-[auto_1px_1fr] min-h-0 max-h-[38%] flex-[0_0_auto] border-b border-line-0">
      <div className="flex items-center justify-between gap-[16px] p-[12px_20px] border-b border-line-0 bg-bg-1">
        <div className="flex items-center gap-[14px]">
          <div className="font-mono text-[11px] tracking-[0.22em] uppercase text-ink-2 flex items-center gap-[8px]">
            <span className="w-[7px] h-[7px] rounded-full bg-pending data-[state=running]:bg-amber-theme data-[state=running]:shadow-[0_0_0_4px_var(--amber-glow)] data-[state=running]:animate-pulse-slow data-[state=done]:bg-done" data-state="done" />
            Research log
          </div>
        </div>
        <div className="flex items-center gap-[18px] font-mono text-[10.5px] text-ink-3">
          <span className="tracking-[0.18em] uppercase text-[10px] text-ink-3">{LOG_ENTRIES.length} steps</span>
          {onClose && (
            <button className="bg-none border-none text-[16px] leading-none text-ink-3 cursor-pointer px-[2px] py-0 opacity-60 transition-all duration-[120ms] hover:opacity-100 hover:text-ink-0" onClick={onClose} title="Hide log">×</button>
          )}
        </div>
      </div>
      <div className="group h-[1px] w-full bg-line-0 relative overflow-hidden" data-state="done">
        <span className="absolute inset-[0_auto_0_0] bg-amber-theme transition-[width] duration-[240ms] ease-out group-data-[state=running]:shadow-[0_0_8px_var(--amber-glow)]" style={{ width: '100%' }} />
      </div>
      <div className="overflow-y-auto pt-[8px] px-0 pb-[14px] font-mono text-[12px] [&::-webkit-scrollbar]:w-[8px] [&::-webkit-scrollbar-thumb]:bg-line-1 [&::-webkit-scrollbar-thumb]:rounded-[4px]">
        {LOG_ENTRIES.map(({ entry, state, displayText }) => (
          <LogRow
            key={entry.id}
            state={state}
            step={entry.step.replace(/^\d+ · /, '')}
            text={entry.quote ? undefined : displayText}
            quote={entry.quote ? displayText : undefined}
          />
        ))}
        <div className="flex items-start gap-[12px] p-[12px_14px] bg-[linear-gradient(90deg,color-mix(in_oklch,var(--amber)_10%,var(--bg-1)),var(--bg-1))] border border-[color-mix(in_oklch,var(--amber)_25%,var(--line-0))] rounded-md text-[12px] text-ink-1 mt-[6px] mx-[20px] mb-[8px]">
          <span className="font-serif text-[20px] text-amber-theme leading-none pt-[2px]">⌖</span>
          <div>
            <div className="font-mono text-[9.5px] tracking-[0.22em] uppercase text-amber-theme mb-[2px]">Sponsor synergy detected</div>
            <div>{SYNERGY_TEXT}</div>
          </div>
        </div>
      </div>
    </section>
  )
}
