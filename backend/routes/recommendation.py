from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
import numpy as np
import pandas as pd

router = APIRouter()

try:
    from models_loader import (
        M1_XGB, M1_LE_PATHO, M1_LE_TARGET,
        M1_ABX_COLS, M1_FEATURES
    )
    MODEL_LOADED = M1_XGB is not None
except Exception:
    MODEL_LOADED = False


class AntibiotiqueProfile(BaseModel):
    nom: str
    sir: str


class AnalyseRequest(BaseModel):
    pathogene: str
    site: Optional[str] = "Hémoculture"
    pays: Optional[str] = "TG"
    referentiel: Optional[str] = "EUCAST"
    antibiotiques: List[AntibiotiqueProfile] = Field(default_factory=list)


class Recommandation(BaseModel):
    rang: int
    abx: str
    confiance: float
    posologie: str
    duree: str


class AnalyseResponse(BaseModel):
    pathogene: str
    score_severite: int
    niveau_alerte: str
    resistants: List[str]
    sensibles: List[str]
    recommandations: List[Recommandation]
    mecanismes: List[str]
    source_modele: str


POSOLOGIES = {
    "Méropénem": ("1g IV toutes les 8h", "7-10 jours"),
    "Imipénem": ("500mg IV toutes les 6h", "7-10 jours"),
    "Imipénem + Relebactam": ("1.25g IV toutes les 6h", "7-14 jours"),
    "Amikacine": ("15mg/kg IV en 1 dose/jour", "5-7 jours"),
    "Colistine": ("9 MUI/j IV en 2 doses", "7-14 jours"),
    "Vancomycine": ("15-20mg/kg IV toutes les 8-12h", "10-14 jours"),
    "Linézolide": ("600mg IV/PO toutes les 12h", "10-14 jours"),
    "Céfidérocol": ("2g IV toutes les 8h", "7-14 jours"),
    "Ceftazidime + Avibactam": ("2.5g IV toutes les 8h", "10-14 jours"),
    "Tigécycline": ("100mg IV puis 50mg/12h", "7-14 jours"),
    "Fosfomycine": ("8g IV toutes les 8h", "7-14 jours"),
    "Ciprofloxacine": ("400mg IV toutes les 8h", "7-10 jours"),
    "Lévofloxacine": ("500mg IV 1 fois/jour", "7-10 jours"),
    "Daptomycine": ("6-8mg/kg IV 1 fois/jour", "10-14 jours"),
    "Ceftriaxone": ("2g IV 1 fois/jour", "7-14 jours"),
    "Nitrofurantoïne": ("100mg PO toutes les 6h", "5-7 jours"),
}


MECANISMES = {
    "Klebsiella": [
        "Production carbapénémase (KPC/NDM)",
        "Pompe à efflux surexprimée",
        "Perte porine OmpK35/36",
    ],
    "Acinetobacter": [
        "Métallo-bêta-lactamase (MBL)",
        "Perte porine OprD",
        "Pompe AdeABC",
    ],
    "Escherichia": [
        "Production ESBL (CTX-M-15)",
        "Résistance quinolones (QRDR)",
        "Gène MCR colistine",
    ],
    "Staphylococcus": [
        "PBP2a — gène mecA (SARM)",
        "Biofilm staphylococcique",
        "VISA/VRSA émergents",
    ],
    "Pseudomonas": [
        "Perte porine OprD",
        "MBL VIM/IMP",
        "Pompe MexAB-OprM surexprimée",
    ],
    "Candida": [
        "ERG11 muté (azolés)",
        "Surexpression efflux CDR1/CDR2",
        "FKS muté (échinocandines)",
    ],
    "Mycobacterium": [
        "Mutation katG/inhA (isoniazide)",
        "Mutation rpoB (rifampicine)",
        "MDR/XDR/TDR",
    ],
}


def normalize_sir(value: str) -> str:
    """Normalise S/I/R pour éviter les erreurs de casse ou d'espaces."""
    if value is None:
        return ""
    return str(value).strip().upper()


def get_mecanismes(pathogene: str) -> list:
    for key, val in MECANISMES.items():
        if key.lower() in pathogene.lower():
            return val

    return ["Résistance acquise multi-mécanismes"]


def analyser_avec_modele(req: AnalyseRequest) -> AnalyseResponse:
    """Analyse avec le vrai modèle M1_XGB."""

    resistants = [
        a.nom for a in req.antibiotiques
        if normalize_sir(a.sir) == "R"
    ]

    sensibles = [
        a.nom for a in req.antibiotiques
        if normalize_sir(a.sir) == "S"
    ]

    try:
        # Préparer les features selon la structure du modèle
        abx_cols = list(M1_ABX_COLS) if M1_ABX_COLS else []

        # CORRECTION ICI :
        # ancien code incorrect : "":−1
        # bon code Python : "": -1
        sir_map = {
            "S": 0,
            "I": 1,
            "R": 2,
            "": -1,
        }

        # Créer vecteur SIR pour tous les antibiotiques fournis
        abx_sir = {
            a.nom: sir_map.get(normalize_sir(a.sir), -1)
            for a in req.antibiotiques
        }

        features_dict = {}

        for col in abx_cols:
            features_dict[col] = abx_sir.get(col, -1)

        X = pd.DataFrame([features_dict])

        # Sécuriser l'ordre des colonnes si M1_FEATURES existe
        if M1_FEATURES:
            for feature in M1_FEATURES:
                if feature not in X.columns:
                    X[feature] = -1

            X = X[M1_FEATURES]

        # Prédiction
        proba = M1_XGB.predict_proba(X)[0]
        pred_idx = int(proba.argmax())

        # Décoder la cible
        if M1_LE_TARGET:
            abx_recommande = M1_LE_TARGET.inverse_transform([pred_idx])[0]
        else:
            abx_recommande = sensibles[0] if sensibles else "Méropénem"

        confiance = round(float(proba[pred_idx]) * 100, 1)

        # Top 3 recommandations
        top3_idx = proba.argsort()[-3:][::-1]
        top3_scores = proba[top3_idx]

        recommandations = []

        for i, (idx, score) in enumerate(zip(top3_idx, top3_scores)):
            idx = int(idx)

            if M1_LE_TARGET:
                abx = M1_LE_TARGET.inverse_transform([idx])[0]
            else:
                fallback_abx = ["Méropénem", "Amikacine", "Colistine"]
                abx = sensibles[i] if i < len(sensibles) else fallback_abx[i]

            if abx in resistants:
                continue

            pos, dur = POSOLOGIES.get(
                abx,
                ("Voir protocole local", "Selon évolution"),
            )

            recommandations.append(
                Recommandation(
                    rang=len(recommandations) + 1,
                    abx=abx,
                    confiance=round(float(score) * 100, 1),
                    posologie=pos,
                    duree=dur,
                )
            )

            if len(recommandations) >= 3:
                break

    except Exception as e:
        print(f"⚠️ Erreur modèle M1: {e} — fallback simulation")
        return analyser_simulation(req)

    if not recommandations:
        return analyser_simulation(req)

    score = min(95, max(5, len(resistants) * 18 + 10))
    niveau = "ROUGE" if score >= 70 else "ORANGE" if score >= 40 else "VERT"

    return AnalyseResponse(
        pathogene=req.pathogene,
        score_severite=score,
        niveau_alerte=niveau,
        resistants=resistants,
        sensibles=sensibles,
        recommandations=recommandations,
        mecanismes=get_mecanismes(req.pathogene),
        source_modele="ResistIA Brain 🧠 — Modèle 1 XGBoost v2.0 (RÉEL)",
    )


def analyser_simulation(req: AnalyseRequest) -> AnalyseResponse:
    """Fallback simulation."""

    resistants = [
        a.nom for a in req.antibiotiques
        if normalize_sir(a.sir) == "R"
    ]

    sensibles = [
        a.nom for a in req.antibiotiques
        if normalize_sir(a.sir) == "S"
    ]

    score = min(95, max(5, len(resistants) * 18 + 10))
    niveau = "ROUGE" if score >= 70 else "ORANGE" if score >= 40 else "VERT"

    candidates = [a for a in sensibles if a not in resistants]

    if not candidates:
        candidates = ["Méropénem", "Amikacine", "Colistine"]

    recommandations = []

    for i, abx in enumerate(candidates[:3]):
        pos, dur = POSOLOGIES.get(
            abx,
            ("Voir protocole local", "Selon évolution"),
        )

        recommandations.append(
            Recommandation(
                rang=i + 1,
                abx=abx,
                confiance=round(95 - i * 12 - len(resistants) * 2, 1),
                posologie=pos,
                duree=dur,
            )
        )

    return AnalyseResponse(
        pathogene=req.pathogene,
        score_severite=score,
        niveau_alerte=niveau,
        resistants=resistants,
        sensibles=sensibles,
        recommandations=recommandations,
        mecanismes=get_mecanismes(req.pathogene),
        source_modele="ResistIA Brain 🧠 — Simulation calibrée v2.0",
    )


@router.post("/analyser", response_model=AnalyseResponse)
async def analyser_antibiogramme(req: AnalyseRequest):
    if MODEL_LOADED:
        return analyser_avec_modele(req)

    return analyser_simulation(req)