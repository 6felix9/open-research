export default function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-[16px] p-[48px_32px] text-center">
      <img src="/image.png" className="w-[64px] h-[64px] object-contain rounded-[14px] opacity-70 theme-invert-img" alt="" />
      <div className="font-serif text-[30px] text-ink-1 tracking-[0.3px] mt-[4px]">Open Research</div>
      <div className="font-mono text-[12px] text-ink-3 leading-[1.7] tracking-[0.04em] max-w-[340px]">
        Pick your sponsors, describe your theme,<br />
        and press <em className="not-italic text-ink-2">Research ideas</em> to get started.
      </div>
    </div>
  )
}
