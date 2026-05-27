---
title: ResistIA Brain API
emoji: 🧬
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# ResistIA Brain API 🧠

API FastAPI de la plateforme mondiale de lutte contre la résistance aux antibiotiques.

## Endpoints principaux

- `GET /` — Health check
- `GET /api/health` — Statut des 10 modèles IA
- `GET /api/dashboard/stats` — Statistiques globales
- `POST /api/recommendation/analyser` — Analyse antibiogramme
- `POST /api/assistant/chat` — ResistIA Brain Chat
- `POST /api/drug-discovery/generer` — Drug Discovery
- `POST /api/simbio/simuler` — SimBio simulation

## Documentation interactive

`/docs` — Swagger UI
`/redoc` — ReDoc