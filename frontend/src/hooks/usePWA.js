import { useState, useEffect } from 'react'

export function usePWA() {
  const [isOnline, setIsOnline]           = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  )
  const [swStatus, setSwStatus]           = useState('idle')
  const [installPrompt, setInstallPrompt] = useState(null)
  const [isInstalled, setIsInstalled]     = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    // Enregistrement Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js', { scope: '/' })
        .then(registration => {
          setSwStatus('registered')
          registration.addEventListener('updatefound', () => {
            const nw = registration.installing
            nw?.addEventListener('statechange', () => {
              if (nw.state === 'installed' && navigator.serviceWorker.controller) {
                setSwStatus('update-available')
              }
            })
          })
        })
        .catch(() => setSwStatus('error'))
    }

    const handleOnline  = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    window.addEventListener('online',  handleOnline)
    window.addEventListener('offline', handleOffline)

    const handleInstallPrompt = (e) => {
      e.preventDefault()
      setInstallPrompt(e)
    }
    window.addEventListener('beforeinstallprompt', handleInstallPrompt)

    if (window.matchMedia?.('(display-mode: standalone)').matches) {
      setIsInstalled(true)
    }

    return () => {
      window.removeEventListener('online',  handleOnline)
      window.removeEventListener('offline', handleOffline)
      window.removeEventListener('beforeinstallprompt', handleInstallPrompt)
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
    } catch (e) {
      console.log('[PWA] Install error:', e)
    }
  }

  const updateApp = () => {
    navigator.serviceWorker?.controller?.postMessage({ type: 'SKIP_WAITING' })
    window.location.reload()
  }

  return { isOnline, swStatus, isInstalled, installPrompt, installApp, updateApp }
}