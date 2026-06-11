/**
 * ResistIA v2.0 — Service API
 * Connecte le frontend React au backend FastAPI
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'https://diano09-resistia-brain-api.hf.space'

async function request(method, endpoint, body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body) options.body = JSON.stringify(body)

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, options)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    return await res.json()
  } catch (error) {
    console.warn(`[API] ${endpoint} — ${error.message} — mode simulation`)
    return null
  }
}

// ── Dashboard ─────────────────────────────────────────
export const apiDashboard = {
  getStats:    () => request('GET',  '/api/dashboard/stats'),
  getTendance: () => request('GET',  '/api/dashboard/tendance'),
  getAlertes:  () => request('GET',  '/api/dashboard/alertes'),
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

// ── Health check ──────────────────────────────────────
export const apiHealth = {
  check: () => request('GET', '/api/health'),
}