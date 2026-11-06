import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import EmptyState from './components/EmptyState'
import ResearchScreen from './components/ResearchScreen'
import IdeaCards from './components/IdeaCards'
import LogSlideover from './components/LogSlideover'
import type { LogEntry, Idea } from './data'
import { readSse } from './sse'

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
  const [config, setConfig] = useState<{ reachable: boolean; serverKey: boolean } | null>(null)
  const [apiKey, setApiKey] = useState(() => {
    try { return sessionStorage.getItem('openai_key') ?? '' } catch { return '' }
  })

  const [logs, setLogs] = useState<LogEntry[]>([])
  const [synergyText, setSynergyText] = useState('')
  const [ideas, setIdeas] = useState<Idea[]>([])

  useEffect(() => {
    fetch('/api/config')
      .then(res => {
        if (!res.ok) throw new Error('Backend config check failed')
        return res.json()
      })
      .then(data => setConfig({ reachable: true, serverKey: !!data.server_key }))
      .catch(() => setConfig({ reachable: false, serverKey: false }))
  }, [])

  const updateApiKey = (key: string) => {
    setApiKey(key)
    try { sessionStorage.setItem('openai_key', key) } catch { /* storage unavailable */ }
  }

  const addCustomSponsorUrl = (url: string) => setCustomSponsorUrls(prev => [...prev, url])
  const removeCustomSponsorUrl = (url: string) => setCustomSponsorUrls(prev => prev.filter(u => u !== url))

  const handleRun = async () => {
    setLogs([])
    setSynergyText('')
    setIdeas([])
    setRunState('running')
    setShowLog(false)

    const fail = (text: string) => {
      setLogs([{ id: '0', step: '00 · CONFIG', text, final: true, error: true }])
      setRunState('error')
    }

    let res: Response
    try {
      res = await fetch('/api/research/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey.trim() && { 'X-OpenAI-Key': apiKey.trim() }),
        },
        body: JSON.stringify({
          sponsors: [...selectedSponsors],
          interests: [...selectedInterests],
          theme,
          seed,
          skills: [...skills],
          time_budget: timeBudget,
          custom_sponsor_urls: customSponsorUrls,
        }),
      })
    } catch {
      fail('Cannot start: the research backend is not reachable. This deployment is frontend-only.')
      return
    }
    if (!res.ok || !res.body) {
      const detail = await res.json().then(d => d.detail).catch(() => null)
      fail(`Cannot start: ${typeof detail === 'string' ? detail : `request failed (${res.status})`}`)
      return
    }

    let finished = false
    let fatal = false
    try {
      await readSse(res.body, (event, raw) => {
        const data = JSON.parse(raw)
        switch (event) {
          case 'log':
            if (data.error && data.final) fatal = true
            setLogs(prev => [...prev, data])
            break
          case 'synergy':
            setSynergyText(data.text)
            break
          case 'ideas':
            setIdeas(data)
            break
          case 'done':
            finished = true
            break
        }
      })
    } catch {
      /* connection dropped mid-stream; handled below */
    }
    setRunState(finished && !fatal ? 'done' : 'error')
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
    <div className="grid grid-cols-[340px_1fr] max-[1100px]:grid-cols-[300px_1fr] h-dvh gap-0">
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
        config={config}
        apiKey={apiKey}
        setApiKey={updateApiKey}
      />
      <main className="flex flex-col min-h-0 bg-bg-0">
        {renderMainContent()}
      </main>
      <LogSlideover open={showLog} onClose={() => setShowLog(false)} logs={logs} synergyText={synergyText} />
    </div>
  )
}

export default App
