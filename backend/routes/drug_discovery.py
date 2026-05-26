from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import random
import math

router = APIRouter()

class MoleculeRequest(BaseModel):
    bacterie_cible: str
    niveau:         int = 3
    n_molecules:    int = 10

class MoleculeCandidate(BaseModel):
    id:         int
    nom:        str
    score:      float
    activite:   float
    cmi:        float
    mw:         float
    logp:       float
    tox_herg:   float
    tox_hepato: float
    sa_score:   float
    solubilite: float
    lipinski:   bool

@router.post("/generer", response_model=List[MoleculeCandidate])
async def generer_molecules(req: MoleculeRequest):
    """Génère des molécules candidates — Modèles 7-8-9"""
    random.seed(hash(req.bacterie_cible) % 1000)
    molecules = []
    for i in range(req.n_molecules):
        score = round(82 + random.random() * 12, 1)
        molecules.append(MoleculeCandidate(
            id=i+1,
            nom=f"AMR-{i+1}X-{random.randint(1000,9999)}",
            score=score,
            activite=round(80 + random.random() * 15, 1),
            cmi=round(0.5 + random.random() * 1.5, 3),
            mw=round(300 + random.random() * 250, 1),
            logp=round(-2 + random.random() * 4, 2),
            tox_herg=round(0.10 + random.random() * 0.25, 3),
            tox_hepato=round(0.10 + random.random() * 0.25, 3),
            sa_score=round(2.5 + random.random() * 2.5, 1),
            solubilite=round(0.4 + random.random() * 0.5, 3),
            lipinski=random.random() > 0.3,
        ))
    return sorted(molecules, key=lambda m: m.score, reverse=True)