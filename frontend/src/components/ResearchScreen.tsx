import { useEffect, useRef, useState } from 'react'
import { LOG_ENTRIES, SYNERGY_TEXT } from '../data'
import LogRow from './LogRow'

export default function ResearchScreen() {
  const [visibleCount, setVisibleCount] = useState(1)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setVisibleCount(prev => {
        if (prev >= LOG_ENTRIES.length) {
          clearInterval(intervalRef.current!)
          return prev
        }
        return prev + 1
      })
    }, 480)
    return () => clearInterval(intervalRef.current!)
  }, [])

  const progress = Math.min((visibleCount / LOG_ENTRIES.length) * 100, 100)
  const isDone = visibleCount >= LOG_ENTRIES.length

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <div className="flex items-center justify-between py-[14px] px-[24px] bg-bg-1 border-b border-line-0 shrink-0">
        <div className="flex items-center gap-[12px]">
          <img src="/image.png" className="w-[28px] h-[28px] object-contain rounded-[6px] opacity-85 theme-invert-img" alt="" />
          <span className="font-mono text-[11px] tracking-[0.22em] uppercase text-ink-2">
            {isDone ? 'Research complete' : 'Researching…'}
          </span>
        </div>
        <span className="w-[7px] h-[7px] rounded-full bg-pending data-[state=running]:bg-amber-theme data-[state=running]:shadow-[0_0_0_4px_var(--amber-glow)] data-[state=running]:animate-pulse-slow data-[state=done]:bg-done" data-state={isDone ? 'done' : 'running'} />
      </div>

      <div className="h-[2px] bg-line-0 shrink-0 relative overflow-hidden">
        <span className="block h-full bg-amber-theme transition-[width] duration-[400ms] ease-out shadow-[0_0_8px_var(--amber-glow)]" style={{ width: `${progress}%` }} />
      </div>

      <div className="flex-1 overflow-y-auto py-[24px] px-0 pb-[40px] [&::-webkit-scrollbar]:w-[8px] [&::-webkit-scrollbar-thumb]:bg-line-1 [&::-webkit-scrollbar-thumb]:rounded-[4px]">
        <div className="max-w-[780px] mx-auto px-[32px] py-0">
          {LOG_ENTRIES.map(({ entry, displayText }, i) => {
            const state = i < visibleCount - 1 ? 'done' : i === visibleCount - 1 ? 'running' : 'idle'
            return (
              <LogRow
                key={entry.id}
                state={state}
                step={entry.step.replace(/^\d+ · /, '')}
                text={entry.quote ? undefined : displayText}
                quote={entry.quote ? displayText : undefined}
                animate={i === visibleCount - 1}
                variant="screen"
              />
            )
          })}
          {isDone && (
            <div className="flex items-start gap-[12px] p-[12px_14px] bg-[linear-gradient(90deg,color-mix(in_oklch,var(--amber)_10%,var(--bg-1)),var(--bg-1))] border border-[color-mix(in_oklch,var(--amber)_25%,var(--line-0))] rounded-md text-[12px] text-ink-1 mt-[8px] mr-[20px] mb-[8px] ml-[-16px]">
              <span className="font-serif text-[20px] text-amber-theme leading-none pt-[2px]">⌖</span>
              <div>
                <div className="font-mono text-[9.5px] tracking-[0.22em] uppercase text-amber-theme mb-[2px]">Sponsor synergy detected</div>
                <div>{SYNERGY_TEXT}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
