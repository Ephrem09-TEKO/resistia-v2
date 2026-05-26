from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AnomalieRequest(BaseModel):
    taux_resistance: float
    pathogene:       str
    antibiotique:    str
    pays:            str = "TG"
    annee:           int = 2025

class AnomalieResponse(BaseModel):
    est_anomalie:     bool
    score_anomalie:   float
    type_anomalie:    str
    explication:      str

@router.post("/detecter", response_model=AnomalieResponse)
async def detecter_anomalie(req: AnomalieRequest):
    seuils = {
        "E. coli":             {"Imipénem": 5, "Méropénem": 5},
        "K. pneumoniae":       {"Colistine": 5, "Imipénem": 20},
        "S. aureus":           {"Vancomycine": 3, "Linézolide": 2},
        "P. aeruginosa":       {"Colistine": 8},
    }
    seuil = seuils.get(req.pathogene, {}).get(req.antibiotique, 50)
    est_anomalie = req.taux_resistance > seuil * 1.5
    score = min(1.0, req.taux_resistance / (seuil * 2)) if seuil > 0 else 0.5
    return AnomalieResponse(
        est_anomalie=est_anomalie,
        score_anomalie=round(score, 3),
        type_anomalie="Résistance inhabituelle" if est_anomalie else "Normal",
        explication=(
            f"Taux {req.taux_resistance}% dépasse le seuil attendu de {seuil}%"
            if est_anomalie else
            f"Taux {req.taux_resistance}% dans la fourchette normale"
        ),
    )