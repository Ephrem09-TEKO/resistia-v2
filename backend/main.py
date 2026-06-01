"""
ResistIA v2.0 — Backend FastAPI
Point d'entrée principal — 10 modèles IA
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from routes import (
    recommendation,
    severite,
    prediction,
    anomalies,
    assistant,
    drug_discovery,
    simbio,
    dashboard,
)

# ── Application ───────────────────────────────────────
app = FastAPI(
    title="ResistIA Brain API 🧠",
    description="API de la plateforme mondiale de résistance aux antibiotiques",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — autoriser le frontend React ───────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://resistia-v2.vercel.app",
    "https://Diano09-resistia-brain-api.hf.space",
    "*",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────
app.include_router(dashboard.router,      prefix="/api/dashboard",      tags=["Dashboard"])
app.include_router(recommendation.router, prefix="/api/recommendation",  tags=["Modèle 1 — Recommandation"])
app.include_router(severite.router,       prefix="/api/severite",        tags=["Modèle 2 — Sévérité"])
app.include_router(prediction.router,     prefix="/api/prediction",      tags=["Modèle 3 — Prédiction"])
app.include_router(anomalies.router,      prefix="/api/anomalies",       tags=["Modèle 4 — Anomalies"])
app.include_router(assistant.router,      prefix="/api/assistant",       tags=["Modèle 6 — Assistant"])
app.include_router(drug_discovery.router, prefix="/api/drug-discovery",  tags=["Modèles 7-8-9 — Drug Discovery"])
app.include_router(simbio.router,         prefix="/api/simbio",          tags=["Modèle 10 — SimBio"])

# ── Health check ──────────────────────────────────────
@app.get("/")
async def root():
    return {
        "app":     "ResistIA Brain API 🧠",
        "version": "2.0.0",
        "status":  "running",
        "modeles": 10,
        "docs":    "/docs",
    }

@app.get("/api/health")
async def health():
    return {
        "status":  "healthy",
        "brain":   "active",
        "modeles": {
            "M1_recommandation": "✅",
            "M2_severite":       "✅",
            "M3_prediction":     "✅",
            "M4_anomalies":      "✅",
            "M5_vision":         "✅",
            "M6_assistant":      "✅",
            "M7_drug_L1":        "✅",
            "M8_drug_L2":        "✅",
            "M9_drug_L3":        "✅",
            "M10_simbio":        "✅",
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )