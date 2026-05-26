from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import re

router = APIRouter()

BASE_REPONSES = {
    "esbl": {
        "reponse": (
            "Les ESBL (Extended-Spectrum Beta-Lactamases) sont des enzymes produites "
            "par E. coli et K. pneumoniae qui hydrolysent la plupart des pénicillines "
            "et céphalosporines. Les gènes impliqués sont blaCTX-M, blaTEM, blaSHV. "
            "Traitement : carbapénèmes (imipénem, méropénem) en première intention. "
            "En Afrique subsaharienne, 35-55% des E. coli cliniques sont ESBL+"
        ),
        "sources": ["EUCAST 2025", "OMS GLASS 2024"],
        "confiance": 0.97,
    },
    "sarm|mrsa|meticilline": {
        "reponse": (
            "Le SARM (S. aureus Résistant à la Méticilline) possède le gène mecA "
            "codant PBP2a, conférant une résistance à toutes les bêta-lactamines. "
            "Traitement de choix : vancomycine 15-20mg/kg IV. "
            "Alternatives : linézolide, daptomycine, téicoplanine. "
            "Prévalence mondiale : 20-30% des S. aureus cliniques."
        ),
        "sources": ["CLSI 2025", "IDSA Guidelines"],
        "confiance": 0.96,
    },
    "carbapenem|kpc|ndm|oxa": {
        "reponse": (
            "Les entérobactéries productrices de carbapénémases (EPC) sont classées "
            "PRIORITÉ CRITIQUE par l'OMS. Types principaux : KPC (K. pneumoniae), "
            "NDM (Klebsiella, E. coli), OXA-48 (K. pneumoniae). "
            "Options thérapeutiques limitées : ceftazidime-avibactam, "
            "imipénem-relebactam, céfidérocol, colistine en dernier recours."
        ),
        "sources": ["EUCAST 2025", "OMS 2024"],
        "confiance": 0.95,
    },
    "togo|afrique|afro|lomé": {
        "reponse": (
            "En Afrique de l'Ouest (région AFRO), les taux de résistance sont parmi "
            "les plus élevés au monde. Au Togo, E. coli résistant à la ciprofloxacine "
            "atteint 68.8%. Les carbapénémases émergent progressivement. "
            "Référentiel recommandé : EUCAST pour les pays francophones. "
            "Le projet ResistIA couvre 47 pays AFRO avec données calibrées GLASS/OMS."
        ),
        "sources": ["GLASS OMS 2024", "ResistIA AFRO 2025"],
        "confiance": 0.92,
    },
    "prevention|stewardship|prescrire": {
        "reponse": (
            "Les 5 piliers de l'antibiotic stewardship : "
            "1) Prescrire uniquement si infection bactérienne documentée. "
            "2) Guider le traitement par l'antibiogramme (désescalade). "
            "3) Utiliser le spectre le plus étroit possible. "
            "4) Respecter la durée minimale efficace. "
            "5) Hygiène des mains stricte en milieu de soins."
        ),
        "sources": ["OMS AMR Action Plan 2024"],
        "confiance": 0.98,
    },
    "dernier recours|reserve|colistine|cefiderocol": {
        "reponse": (
            "Antibiotiques de catégorie RÉSERVE (OMS AWaRe) : "
            "colistine, polymyxine B, céfidérocol, aztréonam-avibactam, "
            "imipénem-relebactam, ceftazidime-avibactam. "
            "À n'utiliser qu'en l'absence totale d'alternative documentée par "
            "l'antibiogramme, sous supervision d'un infectiologue."
        ),
        "sources": ["OMS AWaRe 2023", "EUCAST 2025"],
        "confiance": 0.99,
    },
}

def get_reponse(question: str) -> dict:
    q = question.lower()
    for pattern, data in BASE_REPONSES.items():
        if any(re.search(p, q) for p in pattern.split("|")):
            return data
    return {
        "reponse": (
            "Je suis ResistIA Brain 🧠, spécialisé en résistance aux antibiotiques. "
            "Je peux vous répondre sur les mécanismes de résistance (ESBL, SARM, "
            "carbapénémases), les stratégies thérapeutiques, les données "
            "épidémiologiques par région OMS, et l'antibiotic stewardship. "
            "Posez-moi une question plus spécifique pour une réponse ciblée."
        ),
        "sources": ["ResistIA Brain v2.0"],
        "confiance": 0.75,
    }

class ChatRequest(BaseModel):
    question: str
    contexte: Optional[str] = None

class ChatResponse(BaseModel):
    reponse:   str
    sources:   list
    confiance: float
    modele:    str

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """ResistIA Brain Chat — Modèle 6"""
    result = get_reponse(req.question)
    return ChatResponse(
        reponse=result["reponse"],
        sources=result["sources"],
        confiance=result["confiance"],
        modele="ResistIA Brain 🧠 — Modèle 6 NLP v2.0",
    )