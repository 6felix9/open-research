import { useState, useEffect } from 'react'
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
  const [runState, setRunState] = useState<'idle' | 'running' | 'done' | 'error'>('idle')
  const [showLog, setShowLog] = useState(false)
  const [customSponsorUrls, setCustomSponsorUrls] = useState<string[]>([])
  const [keysConfig, setKeysConfig] = useState<Record<string, boolean> | null>(null)

  const [logs, setLogs] = useState<LogEntry[]>([])
  const [synergyText, setSynergyText] = useState('')
  const [ideas, setIdeas] = useState<Idea[]>([])

  useEffect(() => {
    fetch('/api/config/keys')
      .then(res => {
        if (!res.ok) throw new Error('Backend config check failed')
        return res.json()
      })
      .then(data => setKeysConfig(data))
      .catch(err => {
        console.error('Failed to fetch keys config:', err)
        setKeysConfig({
          OPENAI_API_KEY: false,
          EXA_API_KEY: false,
          FIRECRAWL_API_KEY: false,
          JINA_API_KEY: false,
          GITHUB_TOKEN: false
        })
      })
  }, [])

  const addCustomSponsorUrl = (url: string) => setCustomSponsorUrls(prev => [...prev, url])
  const removeCustomSponsorUrl = (url: string) => setCustomSponsorUrls(prev => prev.filter(u => u !== url))

  const handleRun = async () => {
    setLogs([])
    setSynergyText('')
    setIdeas([])
    setRunState('running')
    setShowLog(false)

    try {
      const res = await fetch('/api/config/keys')
      const keys: Record<string, boolean> = await res.json()
      const missing = Object.entries(keys).filter(([, ok]) => !ok).map(([k]) => k)
      if (missing.length > 0) {
        setLogs([{ id: '0', step: '00 · CONFIG', text: `Cannot start: missing API keys — ${missing.join(', ')}.`, final: true, error: true }])
        setRunState('error')
        return
      }
    } catch {
      setLogs([{ id: '0', step: '00 · CONFIG', text: 'Cannot start: the research backend is not reachable. This deployment is frontend-only.', final: true, error: true }])
      setRunState('error')
      return
    }

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
      setLogs(prev => {
        const hasFatalError = prev.some(l => l.error && l.final)
        setRunState(hasFatalError ? 'error' : 'done')
        return prev
      })
    })

    es.onerror = () => {
      es.close()
      setRunState('error')
    }
  }

  const renderMainContent = () => {
    switch (runState) {
      case 'idle':
        return <EmptyState />
      case 'running':
      case 'error':
        return <ResearchScreen logs={logs} synergyText={synergyText} runState={runState} />
      case 'done':
        return <IdeaCards ideas={ideas} onViewLog={showLog ? undefined : () => setShowLog(true)} />
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
        keysConfig={keysConfig}
      />
      <main className="flex flex-col min-h-0 bg-bg-0">
        {renderMainContent()}
      </main>
      <LogSlideover open={showLog} onClose={() => setShowLog(false)} logs={logs} synergyText={synergyText} />
    </div>
  )
}

export default App
