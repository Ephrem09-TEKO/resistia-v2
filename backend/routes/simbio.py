from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import math

router = APIRouter()

ESPECES = {
    "souris": {"poids": 0.025, "t_half": 0.7,  "vd": 0.6},
    "rat":    {"poids": 0.25,  "t_half": 1.6,  "vd": 0.65},
    "humain": {"poids": 70,    "t_half": 5.3,  "vd": 0.7},
}

PAYS_IMMUNITE = {
    "TG": 0.770, "FR": 0.967, "IN": 0.727,
    "US": 0.910, "NG": 0.735, "CN": 0.920,
}

class SimBioRequest(BaseModel):
    molecule_nom:    str
    molecule_activite: float = 0.85
    molecule_cmi:    float = 1.0
    espece:          str   = "humain"
    pays:            str   = "TG"
    stade_infection: int   = 0

class PKPoint(BaseModel):
    h:             int
    concentration: float
    cmi:           float

class StadeResult(BaseModel):
    stade:     str
    efficacite: float
    temps_h:   int

class SimBioResponse(BaseModel):
    score_global:  float
    recommandation: str
    mecanisme:     str
    courbe_pk:     List[PKPoint]
    stades:        List[StadeResult]
    t_half:        float

@router.post("/simuler", response_model=SimBioResponse)
async def simuler(req: SimBioRequest):
    esp   = ESPECES.get(req.espece, ESPECES["humain"])
    immun = PAYS_IMMUNITE.get(req.pays, 0.75)
    t_half = esp["t_half"]

    courbe = [
        PKPoint(
            h=h,
            concentration=round(req.molecule_activite *
                math.exp(-0.693 * h / t_half) * 100, 2),
            cmi=round(req.molecule_cmi * 100, 2),
        )
        for h in range(25)
    ]

    STADES = ["Colonisation","Infection légère","Infection modérée",
              "Infection sévère","Sepsis critique"]

    stades = []
    for i, nom in enumerate(STADES):
        eff = max(40, round(
            (req.molecule_activite * 0.4 +
             immun * 0.3 +
             max(0, 1 - req.molecule_cmi / 3) * 0.2 +
             max(0, 1 - i * 0.1) * 0.1) * 100, 1
        ))
        stades.append(StadeResult(
            stade=nom,
            efficacite=eff,
            temps_h=24 + i * 48,
        ))

    score = round(
        sum(s.efficacite for s in stades[:3]) / 3, 1
    )

    if score >= 75:
        reco = "✅ Recommandé pour tests laboratoire"
    elif score >= 55:
        reco = "⚠️ Tests supplémentaires nécessaires"
    else:
        reco = "❌ Reformuler la molécule"

    return SimBioResponse(
        score_global=score,
        recommandation=reco,
        mecanisme="Inhibition protéique (ribosome 30S/50S)",
        courbe_pk=courbe,
        stades=stades,
        t_half=t_half,
    )