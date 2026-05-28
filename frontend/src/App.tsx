import { useState } from 'react'
import Sidebar from './components/Sidebar'
import EmptyState from './components/EmptyState'
import ResearchScreen from './components/ResearchScreen'
import IdeaCards from './components/IdeaCards'
import LogSlideover from './components/LogSlideover'

function toggleSet<T>(prev: Set<T>, val: T): Set<T> {
  const next = new Set(prev)
  if (next.has(val)) next.delete(val)
  else next.add(val)
  return next
}

function App() {
  const [selectedSponsors, setSelectedSponsors] = useState(
    new Set(['groq', 'anthropic', 'elevenlabs', 'supabase'])
  )
  const [selectedInterests, setSelectedInterests] = useState(
    new Set(['agents', 'voice', 'tool-use', 'developer-tools', 'RAG'])
  )
  const [theme, setTheme] = useState("tools that make creative work feel less lonely")
  const [seed, setSeed] = useState("")
  const [skills, setSkills] = useState(new Set(['frontend', 'backend', 'ML']))
  const [timeBudget, setTimeBudget] = useState('36h')
  const [depth, setDepth] = useState(1)
  const [runState, setRunState] = useState<'idle' | 'running' | 'done'>('idle')
  const [showLog, setShowLog] = useState(false)
  const [customSponsorUrls, setCustomSponsorUrls] = useState<string[]>([])

  const addCustomSponsorUrl = (url: string) => setCustomSponsorUrls(prev => [...prev, url])
  const removeCustomSponsorUrl = (url: string) => setCustomSponsorUrls(prev => prev.filter(u => u !== url))

  const handleRun = () => {
    setRunState('running')
    setShowLog(false)
    setTimeout(() => setRunState('done'), 4000)
  }

  return (
    <div className="grid grid-cols-[340px_1fr] max-[1100px]:grid-cols-[300px_1fr] h-screen gap-0">
      <Sidebar
        selectedSponsors={selectedSponsors}
        toggleSponsor={id => setSelectedSponsors(prev => toggleSet(prev, id))}
        selectedInterests={selectedInterests}
        toggleInterest={tag => setSelectedInterests(prev => toggleSet(prev, tag))}
        theme={theme}
        setTheme={setTheme}
        seed={seed}
        setSeed={setSeed}
        skills={skills}
        toggleSkill={s => setSkills(prev => toggleSet(prev, s))}
        timeBudget={timeBudget}
        setTimeBudget={setTimeBudget}
        depth={depth}
        setDepth={setDepth}
        runState={runState}
        onRun={handleRun}
        customSponsorUrls={customSponsorUrls}
        addCustomSponsorUrl={addCustomSponsorUrl}
        removeCustomSponsorUrl={removeCustomSponsorUrl}
      />
      <main className="flex flex-col min-h-0 bg-bg-0">
        {runState === 'idle' && <EmptyState />}
        {runState === 'running' && <ResearchScreen />}
        {runState === 'done' && <IdeaCards onViewLog={showLog ? undefined : () => setShowLog(true)} />}
      </main>
      <LogSlideover open={showLog} onClose={() => setShowLog(false)} />
    </div>
  )
}

export default App
