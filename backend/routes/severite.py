from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

try:
    from models_loader import M2_SEVERITE, M2_SCALER
    MODEL_LOADED = M2_SEVERITE is not None
except ImportError:
    MODEL_LOADED = False

class SeveriteRequest(BaseModel):
    pathogene:      str
    site:           str
    nb_resistances: int
    age_patient:    Optional[int]  = 45
    immunodeprime:  Optional[bool] = False
    pays:           Optional[str]  = "TG"

class SeveriteResponse(BaseModel):
    score:         float
    niveau:        str
    mortalite_est: float
    icu_requis:    bool
    duree_hospit:  str
    urgence:       str

@router.post("/calculer", response_model=SeveriteResponse)
async def calculer_severite(req: SeveriteRequest):
    """Calcule le score de sévérité AMR — Modèle 2"""

    base = req.nb_resistances * 15
    if req.immunodeprime:
        base += 20
    if req.age_patient and req.age_patient > 65:
        base += 10
    if req.site in ["Hémoculture", "LCR"]:
        base += 25
    score = min(100, max(5, base))

    if score >= 75:
        niveau, mortalite, icu = "CRITIQUE", 45.0, True
        duree, urgence = "> 21 jours", "Réanimation immédiate"
    elif score >= 50:
        niveau, mortalite, icu = "ÉLEVÉ", 22.0, True
        duree, urgence = "14-21 jours", "Hospitalisation urgente"
    elif score >= 30:
        niveau, mortalite, icu = "MODÉRÉ", 8.0, False
        duree, urgence = "7-14 jours", "Hospitalisation standard"
    else:
        niveau, mortalite, icu = "FAIBLE", 2.0, False
        duree, urgence = "< 7 jours", "Ambulatoire possible"

    return SeveriteResponse(
        score=round(score, 1),
        niveau=niveau,
        mortalite_est=mortalite,
        icu_requis=icu,
        duree_hospit=duree,
        urgence=urgence,
    )