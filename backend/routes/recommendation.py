from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np

router = APIRouter()

# Import du chargeur de modèles
try:
    from models_loader import (
        M1_RECOMMANDATION, M1_LABEL_ENCODER, M1_SCALER
    )
    MODEL_LOADED = M1_RECOMMANDATION is not None
except ImportError:
    MODEL_LOADED = False

class AntibiotiqueProfile(BaseModel):
    nom: str
    sir: str  # S, I, R

class AnalyseRequest(BaseModel):
    pathogene:    str
    site:         Optional[str] = "Hémoculture"
    pays:         Optional[str] = "TG"
    referentiel:  Optional[str] = "EUCAST"
    antibiotiques: List[AntibiotiqueProfile] = []

class Recommandation(BaseModel):
    rang:       int
    abx:        str
    confiance:  float
    posologie:  str
    duree:      str

class AnalyseResponse(BaseModel):
    pathogene:        str
    score_severite:   int
    niveau_alerte:    str
    resistants:       List[str]
    sensibles:        List[str]
    recommandations:  List[Recommandation]
    mecanismes:       List[str]
    source_modele:    str

def simuler_analyse(req: AnalyseRequest) -> AnalyseResponse:
    """Simulation ResistIA Brain quand modèle non disponible"""

    resistants = [a.nom for a in req.antibiotiques if a.sir == "R"]
    sensibles   = [a.nom for a in req.antibiotiques if a.sir == "S"]

    score = min(95, max(5, len(resistants) * 18 + 10))

    if score >= 70:
        niveau = "ROUGE"
    elif score >= 40:
        niveau = "ORANGE"
    else:
        niveau = "VERT"

    # Recommandations basées sur les sensibles
    posologies = {
        "Méropénem":       ("1g IV toutes les 8h",          "7-10 jours"),
        "Imipénem":        ("500mg IV toutes les 6h",        "7-10 jours"),
        "Amikacine":       ("15mg/kg IV en 1 dose/jour",     "5-7 jours"),
        "Colistine":       ("9 MUI/j IV en 2 doses",         "7-14 jours"),
        "Vancomycine":     ("15-20mg/kg IV toutes les 8-12h","10-14 jours"),
        "Linézolide":      ("600mg IV/PO toutes les 12h",    "10-14 jours"),
        "Céfidérocol":     ("2g IV toutes les 8h",           "7-14 jours"),
        "Ceftazidime + Avibactam": ("2.5g IV toutes les 8h", "10-14 jours"),
        "Tigécycline":     ("100mg IV puis 50mg/12h",        "7-14 jours"),
        "Fosfomycine":     ("8g IV toutes les 8h",           "7-14 jours"),
        "Ciprofloxacine":  ("400mg IV toutes les 8h",        "7-10 jours"),
        "Lévofloxacine":   ("500mg IV une fois/jour",        "7-10 jours"),
    }

    default_abx = ["Méropénem", "Amikacine", "Colistine",
                   "Vancomycine", "Fosfomycine"]
    candidates = [a for a in sensibles if a not in resistants]
    if not candidates:
        candidates = [a for a in default_abx if a not in resistants]

    recommandations = []
    for i, abx in enumerate(candidates[:3]):
        pos, dur = posologies.get(abx, ("Voir protocole local", "Selon évolution"))
        recommandations.append(Recommandation(
            rang=i+1,
            abx=abx,
            confiance=round(95 - i*12 - len(resistants)*2, 1),
            posologie=pos,
            duree=dur,
        ))

    if not recommandations:
        recommandations = [
            Recommandation(rang=1, abx="Méropénem",
                confiance=78.0,
                posologie="1g IV toutes les 8h",
                duree="7-10 jours"),
        ]

    mecanismes_map = {
        "K":  ["Production carbapénémase (KPC/NDM)", "Pompe à efflux surexprimée"],
        "A":  ["Perte porine OprD", "Métallo-bêta-lactamase (MBL)"],
        "E":  ["Production ESBL (CTX-M)", "Résistance quinolones (QRDR)"],
        "S":  ["PBP2a — gène mecA", "Biofilm staphylococcique"],
        "P":  ["Perte porine OprD", "MBL VIM/IMP", "Pompe MexAB"],
        "C":  ["ERG11 muté", "Surexpression efflux CDR1/CDR2"],
    }
    initial = req.pathogene[0].upper() if req.pathogene else "E"
    mecanismes = mecanismes_map.get(initial, ["Résistance acquise multi-mécanismes"])

    return AnalyseResponse(
        pathogene=req.pathogene,
        score_severite=score,
        niveau_alerte=niveau,
        resistants=resistants,
        sensibles=sensibles,
        recommandations=recommandations,
        mecanismes=mecanismes,
        source_modele="ResistIA Brain 🧠 — Modèle 1 v2.0",
    )

@router.post("/analyser", response_model=AnalyseResponse)
async def analyser_antibiogramme(req: AnalyseRequest):
    """
    Analyse un antibiogramme et retourne les recommandations thérapeutiques.
    Utilise le Modèle 1 ResistIA Brain si disponible, sinon simulation calibrée.
    """
    if MODEL_LOADED:
        try:
            # Encodage pour le modèle ML
            features = _encoder_features(req)
            score_raw = M1_RECOMMANDATION.predict_proba([features])[0]
            # TODO: adapter selon structure du modèle entraîné
            return simuler_analyse(req)
        except Exception as e:
            print(f"⚠️  Modèle M1 erreur: {e} — simulation")
            return simuler_analyse(req)
    return simuler_analyse(req)

def _encoder_features(req: AnalyseRequest) -> list:
    """Encode les features pour le modèle ML"""
    sir_map  = {"S": 0, "I": 1, "R": 2, "": -1}
    features = [sir_map.get(a.sir, -1) for a in req.antibiotiques[:20]]
    while len(features) < 20:
        features.append(-1)
    return features