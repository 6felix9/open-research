import { useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import ResearchLog from './components/ResearchLog'
import IdeaCards from './components/IdeaCards'

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
  const [runState] = useState<'idle' | 'running' | 'done'>('done')

  return (
    <div className="app">
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
        onRun={() => {}}
      />
      <main className="right">
        <ResearchLog />
        <IdeaCards />
      </main>


    </div>
  )
}

export default App
