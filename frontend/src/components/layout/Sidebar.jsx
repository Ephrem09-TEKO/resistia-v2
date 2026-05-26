import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, FlaskConical, Globe, Microscope,
  Pill, Dna, Bot, ChevronLeft, ChevronRight, Activity
} from 'lucide-react'

const NAV = [
  { to:'/',           icon:LayoutDashboard, label:'Tableau de bord',  badge:null },
  { to:'/analyse',    icon:Microscope,      label:'Analyser',          badge:'NEW' },
  { to:'/bacteries',  icon:FlaskConical,    label:'Base bactérienne',  badge:null },
  { to:'/carte',      icon:Globe,           label:'Carte mondiale',    badge:null },
  { to:'/discovery',  icon:Pill,            label:'Drug Discovery',    badge:'AI' },
  { to:'/simbio',     icon:Dna,             label:'SimBio 🧬',         badge:'AI' },
  { to:'/assistant',  icon:Bot,             label:'Brain Chat',        badge:null },
]

export default function Sidebar({ open, onToggle }) {
  return (
    <aside className={`fixed left-0 top-0 h-full z-20 flex flex-col
      transition-all duration-300 ease-in-out
      ${open ? 'w-64' : 'w-16'}
      bg-night-800 border-r border-cyan/10`}>

      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-cyan/10 shrink-0">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan to-violet
            flex items-center justify-center shrink-0 glow-cyan">
            <Activity size={16} className="text-night" />
          </div>
          {open && (
            <div className="overflow-hidden whitespace-nowrap">
              <p className="font-bold text-white text-sm leading-none">ResistIA</p>
              <p className="text-cyan text-xs mt-0.5">v2.0 Brain 🧠</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 overflow-y-auto overflow-x-hidden">
        <div className="space-y-1 px-2">
          {NAV.map(({ to, icon: Icon, label, badge }) => (
            <NavLink key={to} to={to} end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl
                 transition-all duration-200 group relative
                 ${isActive
                   ? 'bg-cyan/10 text-cyan border border-cyan/20'
                   : 'text-blue-200/60 hover:text-white hover:bg-white/5'
                 }`
              }>
              <Icon size={18} className="shrink-0" />
              {open && (
                <span className="text-sm font-medium whitespace-nowrap flex-1">
                  {label}
                </span>
              )}
              {open && badge && (
                <span className={`text-xs px-1.5 py-0.5 rounded-md font-bold
                  ${badge === 'NEW'
                    ? 'bg-bio/20 text-bio'
                    : 'bg-violet/20 text-violet'}`}>
                  {badge}
                </span>
              )}
              {/* Tooltip quand sidebar fermée */}
              {!open && (
                <div className="absolute left-full ml-2 px-2 py-1 rounded-md
                  bg-night-700 text-white text-xs whitespace-nowrap
                  opacity-0 group-hover:opacity-100 transition-opacity
                  pointer-events-none border border-cyan/10 z-50">
                  {label}
                </div>
              )}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Footer sidebar */}
      <div className="p-3 border-t border-cyan/10 shrink-0">
        {open && (
          <div className="glass p-3 mb-3">
            <p className="text-xs text-blue-200/50 mb-1">Données</p>
            <p className="text-xs font-mono text-cyan">194 pays · 42 pathogènes</p>
            <p className="text-xs font-mono text-cyan">10 modèles IA actifs</p>
          </div>
        )}
        <button onClick={onToggle}
          className="w-full flex items-center justify-center p-2 rounded-lg
            text-blue-200/40 hover:text-cyan hover:bg-cyan/5
            transition-all duration-200">
          {open
            ? <ChevronLeft size={16} />
            : <ChevronRight size={16} />}
        </button>
      </div>
    </aside>
  )
}