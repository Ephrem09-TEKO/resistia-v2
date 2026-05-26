import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import ParticlesBg from '../shared/ParticlesBg'
import PWABanner from '../shared/PWABanner'

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="min-h-screen bg-night relative overflow-hidden">
      <ParticlesBg />
      <PWABanner />
      <div className="fixed inset-0 opacity-30 pointer-events-none z-0"
        style={{ backgroundImage:'radial-gradient(circle at 1px 1px, rgba(0,212,255,0.08) 1px, transparent 0)', backgroundSize:'40px 40px' }} />
      <div className="fixed inset-0 pointer-events-none z-0"
        style={{ background:'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,212,255,0.08), transparent)' }} />
      <div className="relative z-10 flex h-screen">
        <Sidebar open={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
        <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300
          ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
          <TopBar sidebarOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
          <main className="flex-1 overflow-y-auto p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}