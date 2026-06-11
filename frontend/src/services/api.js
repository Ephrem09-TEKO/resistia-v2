const BASE_URL = import.meta.env.VITE_API_URL
  || 'https://diano09-resistia-brain-api.hf.space'

let spaceReady = false
let wakeUpPromise = null

async function ensureSpaceAwake() {
  if (spaceReady) return true
  if (wakeUpPromise) return wakeUpPromise

  wakeUpPromise = (async () => {
    for (let attempt = 1; attempt <= 5; attempt++) {
      try {
        const res = await fetch(`${BASE_URL}/api/health`, {
          method: 'GET',
          mode: 'cors',
          headers: { 'Accept': 'application/json' },
        })
        const ct = res.headers.get('content-type') || ''
        if (ct.includes('application/json') && res.ok) {
          console.log(`[API] ✅ Brain actif (tentative ${attempt})`)
          spaceReady = true
          wakeUpPromise = null
          return true
        }
        console.log(`[API] ⏳ Space en réveil... (${attempt}/5)`)
      } catch (e) {
        console.log(`[API] ⏳ Tentative ${attempt}/5 — ${e.message}`)
      }
      await new Promise(r => setTimeout(r, 3000 * attempt))
    }
    wakeUpPromise = null
    return false
  })()

  return wakeUpPromise
}

async function request(method, endpoint, body = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    mode: 'cors',
  }
  if (body) options.body = JSON.stringify(body)

  // Tente jusqu'à 3 fois
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const res = await fetch(`${BASE_URL}${endpoint}`, options)
      const ct = res.headers.get('content-type') || ''

      if (!ct.includes('application/json')) {
        if (attempt < 3) {
          console.log(`[API] ${endpoint} — HTML reçu, réveil en cours... (${attempt}/3)`)
          spaceReady = false
          await ensureSpaceAwake()
          continue
        }
        console.warn(`[API] ${endpoint} — Space indisponible — mode simulation`)
        return null
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      return await res.json()

    } catch (error) {
      if (attempt === 3) {
        console.warn(`[API] ${endpoint} — ${error.message} — mode simulation`)
        return null
      }
      await new Promise(r => setTimeout(r, 2000))
    }
  }
  return null
}

// ── Dashboard ─────────────────────────────────────────
export const apiDashboard = {
  getStats:    () => request('GET', '/api/dashboard/stats'),
  getTendance: () => request('GET', '/api/dashboard/tendance'),
  getAlertes:  () => request('GET', '/api/dashboard/alertes'),
}

// ── Recommandation (Modèle 1) ─────────────────────────
export const apiRecommandation = {
  analyser: (data) => request('POST', '/api/recommendation/analyser', data),
}

// ── Sévérité (Modèle 2) ───────────────────────────────
export const apiSeverite = {
  calculer: (data) => request('POST', '/api/severite/calculer', data),
}

// ── Prédiction (Modèle 3) ─────────────────────────────
export const apiPrediction = {
  predireSIR: (data) => request('POST', '/api/prediction/sir', data),
}

// ── Anomalies (Modèle 4) ──────────────────────────────
export const apiAnomalies = {
  detecter: (data) => request('POST', '/api/anomalies/detecter', data),
}

// ── Assistant (Modèle 6) ──────────────────────────────
export const apiAssistant = {
  chat: (question, contexte = null) =>
    request('POST', '/api/assistant/chat', { question, contexte }),
}

// ── Drug Discovery (Modèles 7-8-9) ───────────────────
export const apiDrugDiscovery = {
  generer: (data) => request('POST', '/api/drug-discovery/generer', data),
}

// ── SimBio (Modèle 10) ────────────────────────────────
export const apiSimBio = {
  simuler: (data) => request('POST', '/api/simbio/simuler', data),
}

// ── Health ────────────────────────────────────────────
export const apiHealth = {
  check: () => request('GET', '/api/health'),
}

// Préchauffe le Space au chargement de l'app
ensureSpaceAwake()