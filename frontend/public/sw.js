/**
 * ResistIA v2.0 — Service Worker PWA
 * Stratégie : Cache First pour assets statiques
 *             Network First pour données API
 *             Offline fallback pour pages
 */

const CACHE_NAME      = 'resistia-v2-cache-v1'
const DATA_CACHE_NAME = 'resistia-v2-data-v1'

// Assets à mettre en cache immédiatement
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192.svg',
  '/icons/icon-512.svg',
]

// URLs d'API à mettre en cache (network first)
const API_URLS = [
  '/api/dashboard',
  '/api/pathogenes',
  '/api/pays',
]

// ── Installation ──────────────────────────────────────
self.addEventListener('install', event => {
  console.log('[SW] Installation ResistIA Brain PWA...')
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Cache des assets statiques')
        return cache.addAll(STATIC_ASSETS)
      })
      .then(() => {
        console.log('[SW] ✅ Assets mis en cache')
        return self.skipWaiting()
      })
      .catch(err => console.log('[SW] Erreur cache:', err))
  )
})

// ── Activation ────────────────────────────────────────
self.addEventListener('activate', event => {
  console.log('[SW] Activation ResistIA Brain PWA...')
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name =>
            name !== CACHE_NAME && name !== DATA_CACHE_NAME
          )
          .map(name => {
            console.log('[SW] Suppression ancien cache:', name)
            return caches.delete(name)
          })
      )
    }).then(() => {
      console.log('[SW] ✅ Service Worker actif')
      return self.clients.claim()
    })
  )
})

// ── Interception des requêtes ─────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event
  const url = new URL(request.url)

  // Ignorer les requêtes non-HTTP
  if (!request.url.startsWith('http')) return

  // Ignorer les extensions de développement
  if (url.hostname === 'localhost' &&
      request.url.includes('hot-update')) return

  // ── Stratégie API : Network First ──────────────────
  if (url.pathname.startsWith('/api/') ||
      url.hostname.includes('cdn.jsdelivr.net')) {
    event.respondWith(networkFirst(request))
    return
  }

  // ── Stratégie Assets : Cache First ─────────────────
  if (request.destination === 'image' ||
      request.destination === 'font'  ||
      request.destination === 'style' ||
      request.destination === 'script') {
    event.respondWith(cacheFirst(request))
    return
  }

  // ── Stratégie Navigation : Network First + Fallback ─
  if (request.mode === 'navigate') {
    event.respondWith(navigationHandler(request))
    return
  }

  // Par défaut : network first
  event.respondWith(networkFirst(request))
})

// ── Fonctions de stratégie ────────────────────────────

async function cacheFirst(request) {
  const cached = await caches.match(request)
  if (cached) return cached
  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME)
      cache.put(request, response.clone())
    }
    return response
  } catch {
    return new Response('Ressource non disponible hors ligne', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    })
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(DATA_CACHE_NAME)
      cache.put(request, response.clone())
    }
    return response
  } catch {
    const cached = await caches.match(request)
    if (cached) return cached
    return new Response(JSON.stringify({
      error: 'Hors ligne',
      message: 'Données non disponibles sans connexion',
      offline: true
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

async function navigationHandler(request) {
  try {
    const response = await fetch(request)
    return response
  } catch {
    const cached = await caches.match('/')
    if (cached) return cached
    return new Response(offlinePage(), {
      headers: { 'Content-Type': 'text/html' }
    })
  }
}

function offlinePage() {
  return `
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <title>ResistIA — Hors ligne</title>
      <style>
        * { margin:0; padding:0; box-sizing:border-box }
        body {
          background:#0A0F1E; color:#E8F4FD;
          font-family:Inter,sans-serif;
          display:flex; align-items:center;
          justify-content:center; height:100vh;
          text-align:center;
        }
        .container { max-width:400px; padding:40px 20px }
        .icon { font-size:64px; margin-bottom:24px }
        h1 { font-size:24px; color:#00D4FF;
             margin-bottom:12px; font-weight:700 }
        p { color:rgba(148,163,184,0.7);
            font-size:15px; line-height:1.6;
            margin-bottom:24px }
        .badge {
          display:inline-block; padding:8px 20px;
          background:rgba(0,212,255,0.1);
          border:1px solid rgba(0,212,255,0.2);
          border-radius:12px; color:#00D4FF;
          font-size:13px; font-weight:600
        }
        .tip {
          margin-top:20px; padding:12px 16px;
          background:rgba(255,255,255,0.03);
          border:1px solid rgba(255,255,255,0.08);
          border-radius:12px; font-size:13px;
          color:rgba(148,163,184,0.5)
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">🧬</div>
        <h1>ResistIA Brain hors ligne</h1>
        <p>
          Vous n'avez pas de connexion internet.
          Les données déjà chargées restent accessibles.
        </p>
        <div class="badge">⚡ Mode hors ligne actif</div>
        <div class="tip">
          ResistIA synchronisera automatiquement les données
          dès que la connexion sera rétablie.
        </div>
      </div>
    </body>
    </html>
  `
}

// ── Gestion des messages ──────────────────────────────
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
  if (event.data?.type === 'GET_CACHE_STATUS') {
    caches.keys().then(names => {
      event.ports[0].postMessage({
        caches: names,
        status: 'active'
      })
    })
  }
})

// ── Sync en arrière-plan ──────────────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'sync-antibiogrammes') {
    console.log('[SW] Sync antibiogrammes en arrière-plan')
    event.waitUntil(syncAntibiogrammes())
  }
})

async function syncAntibiogrammes() {
  const cache = await caches.open(DATA_CACHE_NAME)
  const keys  = await cache.keys()
  console.log(`[SW] ${keys.length} entrées à synchroniser`)
}