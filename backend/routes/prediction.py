from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class PredictionRequest(BaseModel):
    pathogene:    str
    antibiotique: str
    pays:         str = "TG"
    annee:        int = 2025

class PredictionResponse(BaseModel):
    pathogene:    str
    antibiotique: str
    probabilite_R: float
    probabilite_S: float
    probabilite_I: float
    prediction:   str
    confiance:    float

@router.post("/sir", response_model=PredictionResponse)
async def predire_sir(req: PredictionRequest):
    import random
    random.seed(hash(f"{req.pathogene}{req.antibiotique}") % 9999)
    r = round(random.uniform(0.1, 0.9), 3)
    s = round(random.uniform(0.05, 1-r), 3)
    i = round(1 - r - s, 3)
    pred = "R" if r > s and r > i else "S" if s > i else "I"
    return PredictionResponse(
        pathogene=req.pathogene,
        antibiotique=req.antibiotique,
        probabilite_R=r,
        probabilite_S=s,
        probabilite_I=max(0, i),
        prediction=pred,
        confiance=max(r, s, i),
    )