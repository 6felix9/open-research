import { useState } from 'react'
import Sidebar from './components/Sidebar'
import EmptyState from './components/EmptyState'
import ResearchScreen from './components/ResearchScreen'
import IdeaCards from './components/IdeaCards'
import LogSlideover from './components/LogSlideover'
import type { LogEntry, Idea } from './data'

function toggleSet<T>(prev: Set<T>, val: T): Set<T> {
  const next = new Set(prev)
  if (next.has(val)) next.delete(val)
  else next.add(val)
  return next
}

function App() {
  const [selectedSponsors, setSelectedSponsors] = useState(new Set<string>())
  const [selectedInterests, setSelectedInterests] = useState(new Set<string>())
  const [theme, setTheme] = useState("")
  const [seed, setSeed] = useState("")
  const [skills, setSkills] = useState(new Set<string>())
  const [timeBudget, setTimeBudget] = useState('36h')
  const [depth, setDepth] = useState(1)
  const [runState, setRunState] = useState<'idle' | 'running' | 'done'>('idle')
  const [showLog, setShowLog] = useState(false)
  const [customSponsorUrls, setCustomSponsorUrls] = useState<string[]>([])

  const [logs, setLogs] = useState<LogEntry[]>([])
  const [synergyText, setSynergyText] = useState('')
  const [ideas, setIdeas] = useState<Idea[]>([])

  const addCustomSponsorUrl = (url: string) => setCustomSponsorUrls(prev => [...prev, url])
  const removeCustomSponsorUrl = (url: string) => setCustomSponsorUrls(prev => prev.filter(u => u !== url))

  const handleRun = () => {
    setLogs([])
    setSynergyText('')
    setIdeas([])
    setRunState('running')
    setShowLog(false)

    const params = new URLSearchParams({
      sponsors: [...selectedSponsors].join(','),
      interests: [...selectedInterests].join(','),
      theme,
      seed,
      skills: [...skills].join(','),
      time_budget: timeBudget,
      depth: String(depth),
      custom_sponsor_urls: customSponsorUrls.join(','),
    })

    const es = new EventSource(`/api/research/stream?${params}`)

    es.addEventListener('log', e => {
      setLogs(prev => [...prev, JSON.parse(e.data)])
    })

    es.addEventListener('synergy', e => {
      setSynergyText(JSON.parse(e.data).text)
    })

    es.addEventListener('ideas', e => {
      setIdeas(JSON.parse(e.data))
    })

    es.addEventListener('done', () => {
      es.close()
      setRunState('done')
    })

    es.onerror = () => {
      es.close()
      setRunState('idle')
    }
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
        {runState === 'running' && <ResearchScreen logs={logs} synergyText={synergyText} />}
        {runState === 'done' && <IdeaCards ideas={ideas} onViewLog={showLog ? undefined : () => setShowLog(true)} />}
      </main>
      <LogSlideover open={showLog} onClose={() => setShowLog(false)} logs={logs} synergyText={synergyText} />
    </div>
  )
}

export default App
