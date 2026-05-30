interface LogRowProps {
  state: 'done' | 'running' | 'idle' | 'error' | 'warning'
  step: string
  text?: string
  quote?: string
  animate?: boolean
  variant?: 'compact' | 'screen'
}

export default function LogRow({ state, step, text, quote, animate, variant = 'compact' }: LogRowProps) {
  const isScreen = variant === 'screen'
  
  return (
    <div 
      className={`group grid grid-cols-[18px_1fr] gap-[12px] items-start border-l-2 border-transparent transition-all duration-300
        data-[state=running]:border-amber-theme data-[state=running]:bg-[linear-gradient(90deg,var(--amber-glow),transparent_40%)]
        data-[state=idle]:opacity-[0.42]
        ${isScreen ? 'py-[10px] px-0 pl-[14px] ml-[-16px] rounded-r-[6px]' : 'py-[7px] px-[20px]'}
        ${animate ? 'animate-entry-in' : ''}
      `}
      data-state={state} 
      data-animate={animate ? 'true' : undefined}
    >
      <div className="flex items-center justify-center pt-[3px]">
        <span
          className="w-[10px] h-[10px] rounded-full border border-line-1 bg-bg-1 relative shrink-0
            data-[state=done]:bg-done data-[state=done]:border-done
            data-[state=done]:after:content-[''] data-[state=done]:after:absolute data-[state=done]:after:left-[2px] data-[state=done]:after:top-[1px] data-[state=done]:after:w-[3px] data-[state=done]:after:h-[5px] data-[state=done]:after:border-r-[1.5px] data-[state=done]:after:border-r-bg-0 data-[state=done]:after:border-b-[1.5px] data-[state=done]:after:border-b-bg-0 data-[state=done]:after:rotate-45
            data-[state=running]:bg-amber-theme data-[state=running]:border-amber-theme data-[state=running]:animate-pulse-icon
            data-[state=idle]:bg-bg-0 data-[state=idle]:border-dashed
            data-[state=error]:bg-[var(--error)] data-[state=error]:border-[var(--error)]
            data-[state=error]:before:content-[''] data-[state=error]:before:absolute data-[state=error]:before:w-[1.5px] data-[state=error]:before:h-[7px] data-[state=error]:before:bg-bg-0 data-[state=error]:before:left-[4px] data-[state=error]:before:top-[1.5px] data-[state=error]:before:rotate-45
            data-[state=error]:after:content-[''] data-[state=error]:after:absolute data-[state=error]:after:w-[1.5px] data-[state=error]:after:h-[7px] data-[state=error]:after:bg-bg-0 data-[state=error]:after:left-[4px] data-[state=error]:after:top-[1.5px] data-[state=error]:after:-rotate-45
            data-[state=warning]:bg-amber-dim data-[state=warning]:border-amber-dim
            data-[state=warning]:after:content-['!'] data-[state=warning]:after:absolute data-[state=warning]:after:left-[3px] data-[state=warning]:after:top-[-0.5px] data-[state=warning]:after:text-[8px] data-[state=warning]:after:leading-none data-[state=warning]:after:text-bg-0 data-[state=warning]:after:font-bold
          "
          data-state={state} 
        />
      </div>
      <div className="min-w-0">
        <div className={`text-ink-3 uppercase mb-[1px] font-mono text-[10px] ${isScreen ? 'tracking-[0.22em]' : 'tracking-[0.18em]'}`}>
          {step}
        </div>
        {quote != null ? (
          <div className={`font-serif italic text-ink-1 pl-[10px] border-l border-line-1 mt-[4px] ${isScreen ? 'text-[13px] leading-[1.6]' : 'text-[14px] leading-[1.45]'}`}>
            "{quote}"
          </div>
        ) : (
          <div className={`text-ink-0 font-sans whitespace-pre-wrap break-words group-data-[state=idle]:text-ink-3 ${isScreen ? 'text-[13px] leading-[1.6]' : 'text-[12.5px] leading-[1.5]'}`}>
            {text}
          </div>
        )}
      </div>
    </div>
  )
}
