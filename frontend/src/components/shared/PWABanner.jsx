import { motion, AnimatePresence } from 'framer-motion'
import { Download, RefreshCw, WifiOff, X } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function PWABanner() {
  const [isOnline, setIsOnline]           = useState(true)
  const [swStatus, setSwStatus]           = useState('idle')
  const [installPrompt, setInstallPrompt] = useState(null)
  const [isInstalled, setIsInstalled]     = useState(false)
  const [dismissed, setDismissed]         = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    setIsOnline(navigator.onLine)

    const handleOnline  = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    window.addEventListener('online',  handleOnline)
    window.addEventListener('offline', handleOffline)

    const handlePrompt = (e) => {
      e.preventDefault()
      setInstallPrompt(e)
    }
    window.addEventListener('beforeinstallprompt', handlePrompt)

    if (window.matchMedia?.('(display-mode: standalone)').matches) {
      setIsInstalled(true)
    }

    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then(reg => {
        reg.addEventListener('updatefound', () => {
          const nw = reg.installing
          nw?.addEventListener('statechange', () => {
            if (nw.state === 'installed' && navigator.serviceWorker.controller) {
              setSwStatus('update-available')
            }
          })
        })
      }).catch(() => {})
    }

    return () => {
      window.removeEventListener('online',  handleOnline)
      window.removeEventListener('offline', handleOffline)
      window.removeEventListener('beforeinstallprompt', handlePrompt)
    }
  }, [])

  const installApp = async () => {
    if (!installPrompt) return
    try {
      installPrompt.prompt()
      const { outcome } = await installPrompt.userChoice
      if (outcome === 'accepted') {
        setIsInstalled(true)
        setInstallPrompt(null)
      }
    } catch (e) {}
  }

  const updateApp = () => {
    navigator.serviceWorker?.controller?.postMessage({ type:'SKIP_WAITING' })
    window.location.reload()
  }

  return (
    <>
      <AnimatePresence>
        {!isOnline && (
          <motion.div
            initial={{ y:-60, opacity:0 }}
            animate={{ y:0,   opacity:1 }}
            exit={{ y:-60,    opacity:0 }}
            className="fixed top-0 left-0 right-0 z-50 flex items-center
              justify-center gap-3 bg-amr/90 backdrop-blur-md py-2 px-4
              border-b border-amr/30 text-night text-sm font-semibold">
            <WifiOff size={16} />
            Mode hors ligne — Données en cache disponibles
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {swStatus === 'update-available' && !dismissed && (
          <motion.div
            initial={{ y:80, opacity:0 }}
            animate={{ y:0,  opacity:1 }}
            exit={{ y:80,    opacity:0 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50
              glass-strong border border-cyan/30 flex items-center gap-4
              px-5 py-3 rounded-2xl shadow-[0_0_30px_rgba(0,212,255,0.2)]
              max-w-sm w-[calc(100%-2rem)]">
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">
                Mise à jour disponible
              </p>
              <p className="text-xs text-blue-200/50">
                ResistIA v2.0 — nouvelle version prête
              </p>
            </div>
            <button onClick={updateApp}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan/10
                border border-cyan/20 rounded-xl text-cyan text-xs
                font-semibold hover:bg-cyan/20 transition-all">
              <RefreshCw size={12} />
              Mettre à jour
            </button>
            <button onClick={() => setDismissed(true)}
              className="text-blue-200/30 hover:text-white transition-colors p-1">
              <X size={14} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {installPrompt && !isInstalled && !dismissed && (
          <motion.div
            initial={{ y:80, opacity:0 }}
            animate={{ y:0,  opacity:1 }}
            exit={{ y:80,    opacity:0 }}
            transition={{ delay:3 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50
              glass-strong border border-violet/30 flex items-center gap-4
              px-5 py-3 rounded-2xl shadow-[0_0_30px_rgba(123,47,255,0.2)]
              max-w-sm w-[calc(100%-2rem)]">
            <div className="p-2 rounded-xl bg-violet/10 border border-violet/20">
              <Download size={18} className="text-violet" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">Installer ResistIA</p>
              <p className="text-xs text-blue-200/50">
                Accès offline · Rapide · Sans navigateur
              </p>
            </div>
            <button onClick={installApp}
              className="px-3 py-1.5 bg-gradient-to-r from-violet to-cyan
                text-night text-xs font-bold rounded-xl hover:opacity-90
                transition-all">
              Installer
            </button>
            <button onClick={() => setDismissed(true)}
              className="text-blue-200/30 hover:text-white transition-colors p-1">
              <X size={14} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}