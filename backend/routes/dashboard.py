from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import random

router = APIRouter()

@router.get("/stats")
async def get_stats():
    """Statistiques globales pour le Dashboard"""
    return {
        "pays_couverts":        194,
        "pathogenes_suivis":    42,
        "antibiotiques":        82,
        "modeles_actifs":       10,
        "antibiogrammes_total": 1088340,
        "taux_resistance_moyen": 32.4,
        "anomalies_detectees":  32024,
        "deces_amr_an":         1270000,
        "derniere_maj":         "2025-05-21",
    }

@router.get("/tendance")
async def get_tendance():
    """Données d'évolution de la résistance 2015-2025"""
    return [
        {"annee": str(y),
         "afro":  round(28 + (y-2015)*1.0, 1),
         "searo": round(30 + (y-2015)*1.2, 1),
         "amro":  round(22 + (y-2015)*0.7, 1),
         "euro":  round(18 + (y-2015)*0.5, 1)}
        for y in range(2015, 2026)
    ]

@router.get("/alertes")
async def get_alertes():
    """Alertes AMR actives"""
    return [
        {
            "niveau":    "ROUGE",
            "pathogene": "K. pneumoniae KPC",
            "pays":      "Grèce — EURO",
            "detail":    "Résistance colistine 95% détectée",
            "temps":     "2h",
        },
        {
            "niveau":    "ROUGE",
            "pathogene": "Candida auris MDR",
            "pays":      "Inde — SEARO",
            "detail":    "Émergence souche pan-résistante",
            "temps":     "5h",
        },
        {
            "niveau":    "ORANGE",
            "pathogene": "E. coli MCR+",
            "pays":      "Nigeria — AFRO",
            "detail":    "Profil MCR+KPC inhabituel signalé",
            "temps":     "8h",
        },
        {
            "niveau":    "ORANGE",
            "pathogene": "A. baumannii XDR",
            "pays":      "Irak — EMRO",
            "detail":    "Augmentation rapide +18% en 30 jours",
            "temps":     "12h",
        },
        {
            "niveau":    "VERT",
            "pathogene": "S. aureus SARM",
            "pays":      "France — EURO",
            "detail":    "Taux stable dans les normes EARS-Net",
            "temps":     "1j",
        },
    ]