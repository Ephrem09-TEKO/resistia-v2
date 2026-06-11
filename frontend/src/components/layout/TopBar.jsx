import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Bell, Search, Globe2, Menu, Wifi, WifiOff } from 'lucide-react'

const TITLES = {
  '/':          { title:'Tableau de bord',  sub:'Vue globale de la résistance aux antibiotiques' },
  '/analyse':   { title:'Analyser',         sub:'Saisir un antibiogramme et obtenir une recommandation' },
  '/bacteries': { title:'Base bactérienne', sub:'Explorer les profils de résistance par pathogène' },
  '/carte':     { title:'Carte mondiale',   sub:'Surveillance épidémiologique en temps réel' },
  '/discovery': { title:'Drug Discovery',  sub:'Repositionnement moléculaire et génération de molécules' },
  '/simbio':    { title:'SimBio 🧬',        sub:"Simuler l'effet d'une molécule sur un organisme vivant" },
  '/assistant': { title:'Brain Chat',       sub:'Poser une question à ResistIA Brain 🧠' },
}

export default function TopBar({ onToggle }) {
  const { pathname } = useLocation()
  const info = TITLES[pathname] || TITLES['/']
  const [online, setOnline]           = useState(navigator.onLine)
  const [apiConnected, setApiConnected] = useState(false)

  useEffect(() => {
  const handleOnline  = () => setOnline(true)
  const handleOffline = () => setOnline(false)
  window.addEventListener('online',  handleOnline)
  window.addEventListener('offline', handleOffline)

  // Health check avec retry
  const checkBrain = async () => {
    const API = import.meta.env.VITE_API_URL
      || 'https://diano09-resistia-brain-api.hf.space'

    for (let i = 0; i < 5; i++) {
      try {
        const res  = await fetch(`${API}/api/health`)
        const ct   = res.headers.get('content-type') || ''
        if (ct.includes('application/json') && res.ok) {
          const data = await res.json()
          if (data?.status === 'healthy') {
            setApiConnected(true)
            return
          }
        }
      } catch {}
      await new Promise(r => setTimeout(r, 3000))
    }
    setApiConnected(false)
  }

  checkBrain()

  return () => {
    window.removeEventListener('online',  handleOnline)
    window.removeEventListener('offline', handleOffline)
  }
}, [])

  return (
    <header className="h-16 flex items-center justify-between px-6
      border-b border-cyan/10 bg-night-800/80 backdrop-blur-xl shrink-0">

      {/* Gauche */}
      <div className="flex items-center gap-4">
        <button onClick={onToggle}
          className="p-1.5 rounded-lg text-blue-200/50 hover:text-cyan
            hover:bg-cyan/5 transition-all lg:hidden">
          <Menu size={18} />
        </button>
        <div>
          <h1 className="font-bold text-white text-lg leading-none">
            {info.title}
          </h1>
          <p className="text-blue-200/50 text-xs mt-0.5 hidden sm:block">
            {info.sub}
          </p>
        </div>
      </div>

      {/* Droite */}
      <div className="flex items-center gap-3">

        {/* Barre de recherche */}
        <div className="hidden md:flex items-center gap-2 glass px-3 py-2 w-48">
          <Search size={14} className="text-blue-200/40" />
          <input placeholder="Rechercher..."
            className="bg-transparent text-sm text-blue-200/70
              placeholder-blue-200/30 outline-none w-full" />
        </div>

        {/* Statut réseau */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs
          ${online
            ? 'bg-bio/10 text-bio border border-bio/20'
            : 'bg-amr/10 text-amr border border-amr/20'}`}>
          {online ? <Wifi size={12} /> : <WifiOff size={12} />}
          <span className="hidden sm:block">
            {online ? 'En ligne' : 'Hors ligne'}
          </span>
        </div>

        {/* Statut API Brain */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs
          ${apiConnected
            ? 'bg-violet/10 text-violet border border-violet/20'
            : 'bg-white/5 text-blue-200/30 border border-white/10'}`}>
          <span className="hidden sm:block">
            {apiConnected ? '🧠 Brain actif' : '🧠 Brain local'}
          </span>
        </div>

        {/* Région */}
        <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg
          glass text-xs text-blue-200/60">
          <Globe2 size={12} />
          <span className="hidden sm:block">AFRO</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg glass
          text-blue-200/60 hover:text-cyan transition-all">
          <Bell size={16} />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full
            bg-danger animate-pulse" />
        </button>
      </div>
    </header>
  )
}