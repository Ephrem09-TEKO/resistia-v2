"""
ResistIA v2.0 — Modèle 10 : SimBio 🧬
ResistIA Brain 🧠 — Simulateur Physiologique & Pharmacologique
Simule l'effet d'une nouvelle molécule sur :
- Souris (Mus musculus) et Rat (Rattus norvegicus)
- Humain selon région OMS et pays (194 pays)
Sur 5 stades d'évolution de l'infection
"""

import sys
import os
sys.path.insert(0, 'C:\\ResistIA_v2')

import pandas as pd
import numpy as np
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

MODEL_DIR = "C:\\ResistIA_v2\\models"
os.makedirs(f"{MODEL_DIR}/simbio", exist_ok=True)

np.random.seed(42)

# ─────────────────────────────────────────────
# MODULE A — PHYSIOLOGIE DE RÉFÉRENCE
# Sources : données calibrées sur littérature
# scientifique publiée (PubMed, WHO, JAX Labs)
# ─────────────────────────────────────────────

PHYSIOLOGIE_SOURIS = {
    "espece":             "Mus musculus",
    "nom_commun":         "Souris de laboratoire",
    "poids_g":            (20, 30),        # grammes
    "temperature_c":      (36.5, 38.0),    # °C
    "fc_bpm":             (310, 840),      # fréquence cardiaque bpm
    "fr_rpm":             (80, 230),       # fréquence respiratoire /min
    "pression_sys_mmhg":  (95, 125),       # pression systolique
    "pression_dia_mmhg":  (67, 90),        # pression diastolique
    # Hématologie
    "globules_blancs_gL": (1.8, 10.7),     # G/L (leucocytes)
    "neutrophiles_pct":   (10, 40),        # % des GB
    "lymphocytes_pct":    (55, 85),        # %
    "hemoglobine_gL":     (110, 170),      # g/L
    "plaquettes_gL":      (900, 1600),     # G/L
    # Biochimie
    "glycemie_mmolL":     (3.9, 11.1),     # mmol/L
    "creatinine_umolL":   (18, 53),        # µmol/L (fonction rénale)
    "alanine_transf_UL":  (17, 77),        # ALT U/L (fonction hépatique)
    "proteines_totales":  (48, 72),        # g/L
    "crp_mgL":            (0, 5),          # CRP mg/L (inflammation)
    # Immunologie
    "tnf_alpha_pgmL":     (0, 15),         # TNF-α pg/mL
    "il6_pgmL":           (0, 10),         # IL-6 pg/mL
    "il1b_pgmL":          (0, 8),          # IL-1β pg/mL
    # Microbiologie
    "charge_bacterienne": 0,               # UFC/mL (sain = 0)
}

PHYSIOLOGIE_RAT = {
    "espece":             "Rattus norvegicus",
    "nom_commun":         "Rat de laboratoire",
    "poids_g":            (150, 400),
    "temperature_c":      (35.9, 37.5),
    "fc_bpm":             (250, 450),
    "fr_rpm":             (70, 115),
    "pression_sys_mmhg":  (88, 130),
    "pression_dia_mmhg":  (58, 90),
    "globules_blancs_gL": (4.0, 20.0),
    "neutrophiles_pct":   (10, 35),
    "lymphocytes_pct":    (60, 90),
    "hemoglobine_gL":     (120, 180),
    "plaquettes_gL":      (500, 1300),
    "glycemie_mmolL":     (3.9, 8.9),
    "creatinine_umolL":   (27, 80),
    "alanine_transf_UL":  (17, 45),
    "proteines_totales":  (56, 76),
    "crp_mgL":            (0, 5),
    "tnf_alpha_pgmL":     (0, 20),
    "il6_pgmL":           (0, 15),
    "il1b_pgmL":          (0, 10),
    "charge_bacterienne": 0,
}

# Profils physiologiques humains par région OMS
# Sources : WHO Global Health Observatory, GLASS 2022
PHYSIOLOGIE_HUMAIN_BASE = {
    "temperature_c":      (36.1, 37.2),
    "fc_bpm":             (60, 100),
    "fr_rpm":             (12, 20),
    "pression_sys_mmhg":  (90, 120),
    "pression_dia_mmhg":  (60, 80),
    "globules_blancs_gL": (4.0, 11.0),
    "neutrophiles_pct":   (40, 70),
    "lymphocytes_pct":    (20, 45),
    "hemoglobine_gL":     (120, 175),
    "plaquettes_gL":      (150, 400),
    "glycemie_mmolL":     (3.9, 6.1),
    "creatinine_umolL":   (44, 106),
    "alanine_transf_UL":  (7, 40),
    "proteines_totales":  (60, 80),
    "crp_mgL":            (0, 5),
    "tnf_alpha_pgmL":     (0, 15),
    "il6_pgmL":           (0, 7),
    "il1b_pgmL":          (0, 5),
    "charge_bacterienne": 0,
}

# Modificateurs physiologiques par région OMS
# Tiennent compte : nutrition, prévalence maladies chroniques,
# conditions environnementales, accès aux soins
MODIFICATEURS_REGION = {
    "AFRO": {
        "hemoglobine_factor":   0.88,  # anémie fréquente
        "glycemie_factor":      1.05,  # légère hyperglycémie
        "proteines_factor":     0.92,  # malnutrition protéique
        "gb_factor":            1.10,  # infections fréquentes → GB plus élevés
        "creatinine_factor":    0.95,  # petite stature moyenne
        "pression_sys_factor":  1.02,  # HTA fréquente
        "immunite_baseline":    0.85,  # immunité de base légèrement réduite
        "resilience_infection": 0.80,  # résistance aux infections réduite
    },
    "AMRO": {
        "hemoglobine_factor":   0.97,
        "glycemie_factor":      1.12,  # obésité + diabète fréquents
        "proteines_factor":     1.00,
        "gb_factor":            0.98,
        "creatinine_factor":    1.05,  # insuffisance rénale chronique
        "pression_sys_factor":  1.08,  # HTA + obésité
        "immunite_baseline":    0.92,
        "resilience_infection": 0.90,
    },
    "EMRO": {
        "hemoglobine_factor":   0.92,
        "glycemie_factor":      1.08,
        "proteines_factor":     0.96,
        "gb_factor":            1.05,
        "creatinine_factor":    1.02,
        "pression_sys_factor":  1.05,
        "immunite_baseline":    0.88,
        "resilience_infection": 0.83,
    },
    "EURO": {
        "hemoglobine_factor":   1.00,
        "glycemie_factor":      1.03,
        "proteines_factor":     1.00,
        "gb_factor":            1.00,
        "creatinine_factor":    1.00,
        "pression_sys_factor":  1.02,
        "immunite_baseline":    1.00,
        "resilience_infection": 1.00,
    },
    "SEARO": {
        "hemoglobine_factor":   0.90,
        "glycemie_factor":      1.06,
        "proteines_factor":     0.93,
        "gb_factor":            1.08,
        "creatinine_factor":    0.92,
        "pression_sys_factor":  1.03,
        "immunite_baseline":    0.86,
        "resilience_infection": 0.82,
    },
    "WPRO": {
        "hemoglobine_factor":   0.98,
        "glycemie_factor":      1.04,
        "proteines_factor":     0.98,
        "gb_factor":            1.02,
        "creatinine_factor":    0.98,
        "pression_sys_factor":  1.01,
        "immunite_baseline":    0.97,
        "resilience_infection": 0.95,
    },
}

# Modificateurs supplémentaires par pays
# (quelques pays représentatifs — extensible à 194)
MODIFICATEURS_PAYS = {
    "TG": {"region":"AFRO", "malnutrition":0.15, "paludisme":0.45,
           "tb_prevalence":0.08, "vih_prevalence":0.025,
           "acces_soins":0.40, "eau_potable":0.65},
    "SN": {"region":"AFRO", "malnutrition":0.12, "paludisme":0.38,
           "tb_prevalence":0.07, "vih_prevalence":0.030,
           "acces_soins":0.55, "eau_potable":0.72},
    "NG": {"region":"AFRO", "malnutrition":0.20, "paludisme":0.55,
           "tb_prevalence":0.10, "vih_prevalence":0.033,
           "acces_soins":0.35, "eau_potable":0.58},
    "GH": {"region":"AFRO", "malnutrition":0.10, "paludisme":0.42,
           "tb_prevalence":0.06, "vih_prevalence":0.020,
           "acces_soins":0.60, "eau_potable":0.78},
    "CI": {"region":"AFRO", "malnutrition":0.18, "paludisme":0.48,
           "tb_prevalence":0.09, "vih_prevalence":0.025,
           "acces_soins":0.45, "eau_potable":0.68},
    "FR": {"region":"EURO", "malnutrition":0.00, "paludisme":0.00,
           "tb_prevalence":0.01, "vih_prevalence":0.002,
           "acces_soins":0.98, "eau_potable":1.00},
    "DE": {"region":"EURO", "malnutrition":0.00, "paludisme":0.00,
           "tb_prevalence":0.01, "vih_prevalence":0.001,
           "acces_soins":0.99, "eau_potable":1.00},
    "IN": {"region":"SEARO","malnutrition":0.22, "paludisme":0.30,
           "tb_prevalence":0.20, "vih_prevalence":0.005,
           "acces_soins":0.55, "eau_potable":0.72},
    "CN": {"region":"WPRO", "malnutrition":0.02, "paludisme":0.01,
           "tb_prevalence":0.06, "vih_prevalence":0.001,
           "acces_soins":0.85, "eau_potable":0.95},
    "US": {"region":"AMRO", "malnutrition":0.00, "paludisme":0.00,
           "tb_prevalence":0.003,"vih_prevalence":0.004,
           "acces_soins":0.85, "eau_potable":0.99},
    "BR": {"region":"AMRO", "malnutrition":0.05, "paludisme":0.08,
           "tb_prevalence":0.04, "vih_prevalence":0.005,
           "acces_soins":0.75, "eau_potable":0.87},
    "SA": {"region":"EMRO", "malnutrition":0.01, "paludisme":0.02,
           "tb_prevalence":0.01, "vih_prevalence":0.001,
           "acces_soins":0.95, "eau_potable":0.97},
}

# ─────────────────────────────────────────────
# MODULE B — STADES D'INFECTION
# ─────────────────────────────────────────────

STADES_INFECTION = {
    0: {
        "nom":         "Stade 0 — Colonisation",
        "duree_h":     "0 à 6h",
        "description": "Le germe pénètre l'organisme. Pas de symptômes visibles. Multiplication initiale.",
        "charge_ufc":  (1e2, 1e4),      # UFC/mL
        "modificateurs": {
            "temperature":    +0.3,      # fièvre légère
            "gb_factor":       1.2,      # légère leucocytose
            "crp_factor":      2.0,      # CRP commence à monter
            "tnf_factor":      3.0,
            "il6_factor":      2.5,
            "fc_factor":       1.05,     # légère tachycardie
            "pression_factor": 0.98,
            "hemoglobine_factor": 1.00,
            "creatinine_factor":  1.00,
            "alt_factor":         1.00,
        }
    },
    1: {
        "nom":         "Stade 1 — Infection légère",
        "duree_h":     "6 à 24h",
        "description": "Symptômes discrets. Fièvre légère. Réponse immunitaire en cours.",
        "charge_ufc":  (1e4, 1e6),
        "modificateurs": {
            "temperature":    +1.5,
            "gb_factor":       1.8,
            "crp_factor":      8.0,
            "tnf_factor":      8.0,
            "il6_factor":      6.0,
            "fc_factor":       1.15,
            "pression_factor": 0.95,
            "hemoglobine_factor": 0.97,
            "creatinine_factor":  1.05,
            "alt_factor":         1.10,
        }
    },
    2: {
        "nom":         "Stade 2 — Infection modérée",
        "duree_h":     "24 à 72h",
        "description": "Symptômes nets. Fièvre marquée. Début d'atteinte organique.",
        "charge_ufc":  (1e6, 1e8),
        "modificateurs": {
            "temperature":    +2.5,
            "gb_factor":       2.5,
            "crp_factor":      20.0,
            "tnf_factor":      15.0,
            "il6_factor":      12.0,
            "fc_factor":       1.30,
            "pression_factor": 0.90,
            "hemoglobine_factor": 0.92,
            "creatinine_factor":  1.20,
            "alt_factor":         1.40,
        }
    },
    3: {
        "nom":         "Stade 3 — Infection sévère",
        "duree_h":     "72 à 120h",
        "description": "Syndrome inflammatoire majeur. Atteinte rénale et hépatique.",
        "charge_ufc":  (1e8, 1e10),
        "modificateurs": {
            "temperature":    +3.5,
            "gb_factor":       3.5,
            "crp_factor":      60.0,
            "tnf_factor":      30.0,
            "il6_factor":      25.0,
            "fc_factor":       1.50,
            "pression_factor": 0.80,
            "hemoglobine_factor": 0.85,
            "creatinine_factor":  1.80,
            "alt_factor":         2.50,
        }
    },
    4: {
        "nom":         "Stade 4 — Sepsis / État critique",
        "duree_h":     ">120h",
        "description": "Défaillance multi-organique. État critique. Risque vital immédiat.",
        "charge_ufc":  (1e10, 1e12),
        "modificateurs": {
            "temperature":    +4.0,
            "gb_factor":       0.4,      # leucopénie paradoxale
            "crp_factor":      150.0,
            "tnf_factor":      80.0,
            "il6_factor":      60.0,
            "fc_factor":       1.80,
            "pression_factor": 0.65,     # choc septique
            "hemoglobine_factor": 0.72,
            "creatinine_factor":  3.50,  # insuffisance rénale aiguë
            "alt_factor":         5.00,  # cytolyse hépatique
        }
    },
}

# Mécanismes d'action des antibiotiques
MECANISMES_ACTION = {
    "inhibition_paroi":        "Inhibe la synthèse de la paroi bactérienne (PBP) → lyse osmotique",
    "inhibition_proteique":    "Inhibe la synthèse protéique bactérienne (ribosomes 30S/50S)",
    "inhibition_adn":          "Inhibe la topoisomérase/gyrase → blocage réplication ADN",
    "disruption_membranaire":  "Désorganise la membrane cytoplasmique → fuite ionique létale",
    "inhibition_metabolique":  "Inhibe les voies métaboliques essentielles (folates, etc.)",
    "chelation_fer":           "Chélate le fer essentiel à la croissance bactérienne (siderophore)",
}

# Association mécanisme → classe d'antibiotique
MECANISME_PAR_PROPRIETE = {
    # Basé sur MW, logP, n_rings pour prédire le mécanisme
    "haut_mw_haut_hba":    "inhibition_paroi",        # pénicillines, céphalosporines
    "bas_mw_bas_hba":      "inhibition_metabolique",  # sulfonamides, fosfomycine
    "moyen_mw_haut_arom":  "inhibition_adn",          # fluoroquinolones
    "haut_mw_bas_logp":    "disruption_membranaire",  # colistine, daptomycine
    "moyen_mw_moyen_hba":  "inhibition_proteique",    # aminosides, macrolides
    "haut_mw_chelation":   "chelation_fer",           # céfidérocol
}


# ─────────────────────────────────────────────
# MODULE A — FONCTIONS PHYSIOLOGIQUES
# ─────────────────────────────────────────────

def get_physiologie_saine(espece, pays=None, region=None):
    """
    Retourne les constantes physiologiques normales
    pour l'espèce et le contexte géographique donnés
    """
    if espece == "souris":
        base = PHYSIOLOGIE_SOURIS.copy()
        # Valeurs moyennes
        return {k: np.mean(v) if isinstance(v, tuple) else v
                for k, v in base.items()}

    elif espece == "rat":
        base = PHYSIOLOGIE_RAT.copy()
        return {k: np.mean(v) if isinstance(v, tuple) else v
                for k, v in base.items()}

    elif espece == "humain":
        base = {k: np.mean(v) if isinstance(v, tuple) else v
                for k, v in PHYSIOLOGIE_HUMAIN_BASE.items()}

        # Appliquer modificateurs région OMS
        if region and region in MODIFICATEURS_REGION:
            mod = MODIFICATEURS_REGION[region]
            base["hemoglobine_gL"]      *= mod["hemoglobine_factor"]
            base["glycemie_mmolL"]      *= mod["glycemie_factor"]
            base["proteines_totales"]   *= mod["proteines_factor"]
            base["globules_blancs_gL"]  *= mod["gb_factor"]
            base["creatinine_umolL"]    *= mod["creatinine_factor"]
            base["pression_sys_mmhg"]   *= mod["pression_sys_factor"]
            base["_immunite_baseline"]   = mod["immunite_baseline"]
            base["_resilience"]          = mod["resilience_infection"]

        # Appliquer modificateurs pays
        if pays and pays in MODIFICATEURS_PAYS:
            p = MODIFICATEURS_PAYS[pays]
            # Malnutrition → réduit protéines et hémoglobine
            base["proteines_totales"]  *= (1 - p["malnutrition"] * 0.3)
            base["hemoglobine_gL"]     *= (1 - p["malnutrition"] * 0.15)
            # Paludisme → anémie + splénomégalie
            base["hemoglobine_gL"]     *= (1 - p["paludisme"] * 0.10)
            base["plaquettes_gL"]      *= (1 - p["paludisme"] * 0.15)
            # VIH → immunodépression
            base["globules_blancs_gL"] *= (1 - p["vih_prevalence"] * 5)
            base["_immunite_baseline"]  = base.get("_immunite_baseline", 1.0) * (1 - p["vih_prevalence"] * 3)
            base["_acces_soins"]        = p["acces_soins"]

        return base

    else:
        raise ValueError(f"Espèce inconnue : {espece}")


def simuler_infection(physiologie_saine, stade, germe_props):
    """
    Modifie les constantes physiologiques selon le stade d'infection
    """
    mod  = STADES_INFECTION[stade]["modificateurs"]
    phys = physiologie_saine.copy()

    # Virulence du germe (CRITICAL = 1.3x, HIGH = 1.1x, MEDIUM = 1.0x)
    virulence = {"CRITICAL": 1.30, "HIGH": 1.10, "MEDIUM": 1.00}.get(
        germe_props.get("who", "HIGH"), 1.10
    )

    phys["temperature_c"]      += mod["temperature"] * virulence
    phys["globules_blancs_gL"] *= mod["gb_factor"]
    phys["crp_mgL"]            *= mod["crp_factor"] * virulence
    phys["tnf_alpha_pgmL"]     *= mod["tnf_factor"] * virulence
    phys["il6_pgmL"]           *= max(1, mod["il6_factor"] * virulence)
    phys["fc_bpm"]             *= mod["fc_factor"]
    phys["pression_sys_mmhg"]  *= mod["pression_factor"]
    phys["hemoglobine_gL"]     *= mod["hemoglobine_factor"]
    phys["creatinine_umolL"]   *= mod["creatinine_factor"]
    phys["alanine_transf_UL"]  *= mod["alt_factor"]

    # Charge bactérienne
    lo, hi = STADES_INFECTION[stade]["charge_ufc"]
    phys["charge_bacterienne"]  = np.random.uniform(lo, hi)

    # Résilience réduit l'impact selon le profil de l'hôte
    resilience = phys.get("_resilience", 1.0)
    phys["temperature_c"] = physiologie_saine["temperature_c"] + (
        phys["temperature_c"] - physiologie_saine["temperature_c"]
    ) * (2 - resilience)

    return phys

# ─────────────────────────────────────────────
# MODULE C — SIMULATION PHARMACOLOGIQUE (PK/PD)
# ─────────────────────────────────────────────

def predire_mecanisme(props_molecule):
    """
    Prédit le mécanisme d'action le plus probable
    basé sur les propriétés physicochimiques
    """
    mw   = props_molecule.get("mw", 350)
    logp = props_molecule.get("logp", 0)
    hba  = props_molecule.get("hba", 6)
    arom = props_molecule.get("n_arom", 2)

    if mw > 600 and logp < -1:
        return "disruption_membranaire"
    elif mw > 500 and hba > 10:
        return "inhibition_paroi"
    elif arom >= 2 and mw < 450 and logp > 0:
        return "inhibition_adn"
    elif mw < 250 and hba < 5:
        return "inhibition_metabolique"
    elif mw > 700 and hba > 12:
        return "chelation_fer"
    else:
        return "inhibition_proteique"


def simuler_pk(props_molecule, espece, dose_mgkg=10):
    """
    Simule la pharmacocinétique (PK) :
    Comment la molécule se distribue dans l'organisme
    Paramètres PK basés sur règle de Lipinski et propriétés
    """
    mw   = props_molecule.get("mw", 350)
    logp = props_molecule.get("logp", 1)
    hbd  = props_molecule.get("hbd", 2)
    tpsa = props_molecule.get("tpsa", 80)
    sa   = props_molecule.get("sa_score", 3.5)

    # Absorption orale (F%) — Lipinski
    if mw <= 500 and logp <= 5 and hbd <= 5 and tpsa <= 140:
        absorption = max(0.2, 0.9 - (mw/500)*0.2 - (tpsa/140)*0.1)
    else:
        absorption = 0.3  # IV si hors Lipinski

    # Volume de distribution (L/kg)
    vd = 0.5 + logp * 0.3 + (1 - tpsa/200) * 0.5
    vd = max(0.1, min(10, vd))

    # Demi-vie (heures)
    if espece == "souris":
        t_half = max(0.5, 2.0 - mw/500 + logp*0.3)
    elif espece == "rat":
        t_half = max(1.0, 3.0 - mw/500 + logp*0.4)
    else:  # humain
        t_half = max(2.0, 6.0 - mw/600 + logp*0.5 + (1-absorption)*2)

    # Concentration max (Cmax) en µg/mL
    poids_kg = {"souris": 0.025, "rat": 0.25, "humain": 70}[espece]
    cmax = (dose_mgkg * poids_kg * absorption) / (vd * poids_kg) * 1000

    # Clairance rénale
    clearance_renale = max(0.1, (1 - logp/10) * 0.7)

    # Pénétration tissulaire
    penetration = min(1.0, (logp + 3) / 8 + absorption * 0.3)

    return {
        "absorption_pct":      round(absorption * 100, 1),
        "volume_distrib_Lkg":  round(vd, 2),
        "demi_vie_h":          round(t_half, 1),
        "cmax_ugmL":           round(cmax, 2),
        "clearance_renale":    round(clearance_renale, 2),
        "penetration_tissu":   round(penetration, 2),
        "voie_admin":          "Orale" if absorption > 0.5 else "IV recommandée",
    }


def calculer_efficacite_stade(props_molecule, physiologie_infectee,
                               physiologie_saine, stade, espece,
                               props_germe, pk_params):
    """
    Calcule l'efficacité de la molécule à un stade donné
    en tenant compte de :
    - La charge bactérienne
    - L'état physiologique de l'hôte
    - Les paramètres PK
    - La virulence du germe
    """
    # Score d'activité de base (Modèle 8)
    activite_base = props_molecule.get("activite", 0.75)

    # Facteur PK : absorption × pénétration × Cmax
    cmi = props_molecule.get("cmi_mgL", 1.0)
    facteur_pk = min(1.0, (pk_params["cmax_ugmL"] / max(cmi, 0.001)) *
                    pk_params["penetration_tissu"] *
                    (pk_params["absorption_pct"] / 100))
    facteur_pk = max(0.1, min(1.5, facteur_pk))

    # Facteur immunité hôte
    immunite = physiologie_saine.get("_immunite_baseline", 1.0)
    # Aux stades avancés, immunité effondrée
    immunite_stade = immunite * max(0.1, 1 - stade * 0.15)

    # Facteur charge bactérienne (plus haute = plus difficile)
    charge = physiologie_infectee["charge_bacterienne"]
    facteur_charge = max(0.3, 1.0 - np.log10(max(charge, 1)) / 12)

    # Facteur résistance du germe au stade
    resistances = props_germe.get("resistances", {})
    # Vérifier si la molécule est dans la liste des résistances connues
    nom_mol = props_molecule.get("nom", "").lower()
    est_resistante = any(r in nom_mol for r in resistances)
    facteur_resistance = 0.2 if est_resistante else 1.0

    # Score d'efficacité final
    efficacite = (
        activite_base * 0.35 +
        facteur_pk    * 0.30 +
        immunite_stade* 0.15 +
        facteur_charge* 0.15 +
        facteur_resistance * 0.05
    )

    # Réduction de la charge bactérienne prédite
    if efficacite > 0.7:
        reduction_log = 3.0 + (efficacite - 0.7) * 5
    elif efficacite > 0.5:
        reduction_log = 1.0 + (efficacite - 0.5) * 10
    else:
        reduction_log = efficacite * 2

    charge_apres = max(0, charge / (10 ** reduction_log))

    # Temps pour élimination complète (h)
    if efficacite > 0.8:
        temps_elimination = round(np.log10(max(charge, 1)) / efficacite * 8, 1)
    elif efficacite > 0.5:
        temps_elimination = round(np.log10(max(charge, 1)) / efficacite * 16, 1)
    else:
        temps_elimination = 999  # pas d'élimination

    return {
        "efficacite_pct":      round(efficacite * 100, 1),
        "facteur_pk":          round(facteur_pk, 3),
        "immunite_stade":      round(immunite_stade, 3),
        "facteur_charge":      round(facteur_charge, 3),
        "charge_avant_UFC":    round(charge, 0),
        "charge_apres_UFC":    round(charge_apres, 0),
        "reduction_log":       round(reduction_log, 2),
        "temps_elimination_h": temps_elimination,
    }


def evaluer_securite_organes(physiologie_infectee, pk_params,
                              props_molecule, espece):
    """
    Évalue l'impact de la molécule sur chaque organe
    """
    tox_herg   = props_molecule.get("toxicite_herg", 0.2)
    tox_hepato = props_molecule.get("toxicite_hepato", 0.2)
    mw         = props_molecule.get("mw", 350)
    clearance  = pk_params["clearance_renale"]

    # Rein : fonction rénale actuelle × clearance rénale
    creat_actuel = physiologie_infectee["creatinine_umolL"]
    if espece == "humain":
        creat_normal = 75
    elif espece == "rat":
        creat_normal = 53
    else:
        creat_normal = 35
    fnr = creat_actuel / creat_normal  # > 1 = atteinte rénale
    impact_renal = min(1.0, (1 - clearance) * fnr * 0.5 + clearance * 0.3)

    # Foie : ALT actuel + toxicité hépatique molécule
    alt_actuel = physiologie_infectee["alanine_transf_UL"]
    alt_normal = {"souris": 47, "rat": 31, "humain": 23}[espece]
    fnl = alt_actuel / alt_normal
    impact_hepatique = min(1.0, tox_hepato * fnl * 0.6)

    # Cœur : toxicité hERG
    impact_cardiaque = min(1.0, tox_herg * 1.2)

    # Score sécurité global (0=très sûr, 1=très toxique)
    score_toxicite = (
        impact_renal    * 0.35 +
        impact_hepatique* 0.35 +
        impact_cardiaque* 0.30
    )

    return {
        "impact_renal":      round(impact_renal, 3),
        "impact_hepatique":  round(impact_hepatique, 3),
        "impact_cardiaque":  round(impact_cardiaque, 3),
        "score_toxicite":    round(score_toxicite, 3),
        "securite_globale":  "✅ Sûr" if score_toxicite < 0.3
                             else ("⚠️ Prudence" if score_toxicite < 0.6
                             else "❌ Toxique"),
    }


# ─────────────────────────────────────────────
# MODULE D — SIMULATION COMPLÈTE
# ─────────────────────────────────────────────

def simuler_molecule_complete(props_molecule, espece, germe_props,
                               pays=None, region=None, dose_mgkg=10):
    """
    Lance la simulation complète SimBio 🧬 :
    Physiologie saine → Infection → Traitement → Résultats
    """
    # A. Physiologie saine
    phys_saine = get_physiologie_saine(espece, pays=pays, region=region)

    # B. PK de la molécule
    pk = simuler_pk(props_molecule, espece, dose_mgkg)

    # C. Mécanisme d'action prédit
    mecanisme_key = predire_mecanisme(props_molecule)
    mecanisme_desc = MECANISMES_ACTION[mecanisme_key]

    # D. Simulation par stade
    resultats_stades = {}
    for stade in range(5):
        phys_infectee = simuler_infection(phys_saine, stade, germe_props)
        efficacite    = calculer_efficacite_stade(
            props_molecule, phys_infectee, phys_saine,
            stade, espece, germe_props, pk
        )
        securite = evaluer_securite_organes(
            phys_infectee, pk, props_molecule, espece
        )
        resultats_stades[stade] = {
            "stade_info":    STADES_INFECTION[stade],
            "physiologie":   phys_infectee,
            "efficacite":    efficacite,
            "securite":      securite,
        }

    # E. Stade optimal
    stade_optimal = max(
        resultats_stades,
        key=lambda s: resultats_stades[s]["efficacite"]["efficacite_pct"]
    )

    # F. Score global SimBio
    efficacites = [resultats_stades[s]["efficacite"]["efficacite_pct"]
                   for s in range(5)]
    score_simbio = round(np.mean(efficacites[:3]), 1)  # stades 0-2

    return {
        "espece":          espece,
        "pays":            pays or "N/A",
        "region":          region or "N/A",
        "germe":           germe_props.get("nom", "Inconnu"),
        "molecule":        props_molecule.get("nom", "Candidat"),
        "pk_params":       pk,
        "mecanisme_key":   mecanisme_key,
        "mecanisme_desc":  mecanisme_desc,
        "stades":          resultats_stades,
        "stade_optimal":   stade_optimal,
        "score_simbio":    score_simbio,
        "physiologie_saine": phys_saine,
    }

# ─────────────────────────────────────────────
# AFFICHAGE DES RÉSULTATS
# ─────────────────────────────────────────────

def afficher_resultats_simbio(sim):
    print(f"\n{'='*70}")
    print(f"  🧬 SimBio — Rapport de Simulation Pharmacologique")
    print(f"{'='*70}")
    print(f"  Molécule    : {sim['molecule']}")
    print(f"  Germe cible : {sim['germe']}")
    print(f"  Espèce      : {sim['espece'].capitalize()}")
    if sim['pays'] != "N/A":
        print(f"  Pays        : {sim['pays']}")
    if sim['region'] != "N/A":
        print(f"  Région OMS  : {sim['region']}")

    print(f"\n  ⚗️  Pharmacocinétique (PK) :")
    pk = sim["pk_params"]
    print(f"     Absorption        : {pk['absorption_pct']}%")
    print(f"     Volume distrib.   : {pk['volume_distrib_Lkg']} L/kg")
    print(f"     Demi-vie          : {pk['demi_vie_h']}h")
    print(f"     Cmax              : {pk['cmax_ugmL']} µg/mL")
    print(f"     Pénétration tissu : {pk['penetration_tissu']*100:.0f}%")
    print(f"     Voie recommandée  : {pk['voie_admin']}")

    print(f"\n  🔬 Mécanisme d'action prédit :")
    print(f"     {sim['mecanisme_key'].replace('_',' ').title()}")
    print(f"     → {sim['mecanisme_desc']}")

    print(f"\n  📊 Efficacité par stade d'infection :")
    print(f"  {'Stade':<35} {'Efficacité':>10} {'Charge avant':>14} "
          f"{'Réduction':>10} {'Temps élim.':>12}")
    print(f"  {'-'*82}")

    for stade, res in sim["stades"].items():
        nom_stade = STADES_INFECTION[stade]["nom"]
        eff       = res["efficacite"]["efficacite_pct"]
        charge    = res["efficacite"]["charge_avant_UFC"]
        red_log   = res["efficacite"]["reduction_log"]
        t_elim    = res["efficacite"]["temps_elimination_h"]

        eff_icon = "🟢" if eff >= 70 else ("🟡" if eff >= 50 else "🔴")
        stade_opt = " ⭐ OPTIMAL" if stade == sim["stade_optimal"] else ""

        charge_str = f"{charge:.1e}".replace("e+", "e")
        t_str = f"{t_elim}h" if t_elim < 999 else "Insuffisant"

        print(f"  {nom_stade:<35} {eff_icon}{eff:>7.1f}%  "
              f"{charge_str:>12} UFC  -{red_log:>5.1f} log  "
              f"{t_str:>10}{stade_opt}")

    print(f"\n  🛡️  Sécurité organique au stade optimal :")
    sec = sim["stades"][sim["stade_optimal"]]["securite"]
    print(f"     Rein      : {sec['impact_renal']:.3f}  "
          f"{'✅' if sec['impact_renal'] < 0.3 else '⚠️'}")
    print(f"     Foie      : {sec['impact_hepatique']:.3f}  "
          f"{'✅' if sec['impact_hepatique'] < 0.3 else '⚠️'}")
    print(f"     Cœur      : {sec['impact_cardiaque']:.3f}  "
          f"{'✅' if sec['impact_cardiaque'] < 0.3 else '⚠️'}")
    print(f"     Verdict   : {sec['securite_globale']}")

    print(f"\n  🏆 Score SimBio Global : {sim['score_simbio']}%")
    verdict = ("🟢 RECOMMANDÉ pour tests en laboratoire" if sim["score_simbio"] >= 65
               else "🟡 Tests supplémentaires nécessaires" if sim["score_simbio"] >= 45
               else "🔴 Non recommandé — reformuler la molécule")
    print(f"     {verdict}")

    stade_nom = STADES_INFECTION[sim["stade_optimal"]]["nom"]
    print(f"     Stade optimal d'intervention : {stade_nom}")
    print(f"     ({STADES_INFECTION[sim['stade_optimal']]['description']})")

    physio = sim["physiologie_saine"]
    print(f"\n  🩺 Constantes physiologiques (sain → stade optimal) :")
    stade_phys = sim["stades"][sim["stade_optimal"]]["physiologie"]
    params = [
        ("Température (°C)", "temperature_c"),
        ("FC (bpm)",          "fc_bpm"),
        ("Pression syst.",    "pression_sys_mmhg"),
        ("GB (G/L)",          "globules_blancs_gL"),
        ("CRP (mg/L)",        "crp_mgL"),
        ("Hémoglobine (g/L)", "hemoglobine_gL"),
        ("Créatinine (µmol)", "creatinine_umolL"),
        ("ALT (U/L)",         "alanine_transf_UL"),
        ("IL-6 (pg/mL)",      "il6_pgmL"),
    ]
    for label, key in params:
        if key in physio and key in stade_phys:
            val_saine = physio[key]
            val_infectee = stade_phys[key]
            delta = ((val_infectee - val_saine) / val_saine * 100)
            arrow = "↑" if delta > 0 else "↓"
            print(f"     {label:<22}: {val_saine:>7.1f} → "
                  f"{val_infectee:>7.1f}  ({arrow}{abs(delta):.0f}%)")


# ─────────────────────────────────────────────
# GÉNÉRATION DU DATASET D'ENTRAÎNEMENT
# ─────────────────────────────────────────────

def generer_dataset_simbio(n=500):
    """
    Génère un dataset d'entraînement pour SimBio
    en simulant différentes combinaisons
    molécule × espèce × germe × stade
    """
    print("\n🔧 Génération du dataset SimBio...")

    molecules_test = [
        {"nom":"Candidat_A","mw":342,"logp":1.2,"hbd":3,"hba":6,"tpsa":88,
         "n_arom":2,"activite":0.78,"cmi_mgL":1.0,
         "toxicite_herg":0.18,"toxicite_hepato":0.22,"sa_score":3.1},
        {"nom":"Ciprofloxacine","mw":331,"logp":0.28,"hbd":2,"hba":6,"tpsa":74,
         "n_arom":2,"activite":0.85,"cmi_mgL":0.015,
         "toxicite_herg":0.25,"toxicite_hepato":0.20,"sa_score":2.8},
        {"nom":"Méropénem","mw":383,"logp":-0.75,"hbd":3,"hba":7,"tpsa":115,
         "n_arom":0,"activite":0.92,"cmi_mgL":0.05,
         "toxicite_herg":0.15,"toxicite_hepato":0.20,"sa_score":4.5},
        {"nom":"Candidat_B","mw":428,"logp":0.8,"hbd":2,"hba":8,"tpsa":102,
         "n_arom":2,"activite":0.82,"cmi_mgL":0.25,
         "toxicite_herg":0.15,"toxicite_hepato":0.18,"sa_score":3.8},
        {"nom":"Molécule_Faible","mw":620,"logp":6.2,"hbd":7,"hba":14,"tpsa":185,
         "n_arom":1,"activite":0.42,"cmi_mgL":16.0,
         "toxicite_herg":0.55,"toxicite_hepato":0.48,"sa_score":7.2},
    ]

    germes_test = [
        {"nom":"K. pneumoniae KPC","who":"CRITICAL","gram":"neg",
         "resistances":["ampicilline","ceftriaxone"]},
        {"nom":"S. aureus SARM","who":"HIGH","gram":"pos",
         "resistances":["oxacilline","ampicilline"]},
        {"nom":"E. coli ESBL","who":"HIGH","gram":"neg",
         "resistances":["ampicilline","ciprofloxacine"]},
    ]

    especes    = ["souris", "rat", "humain"]
    regions    = ["AFRO", "AMRO", "EURO", "SEARO", "EMRO", "WPRO"]
    records    = []

    for _ in range(n):
        mol    = molecules_test[np.random.randint(len(molecules_test))].copy()
        germe  = germes_test[np.random.randint(len(germes_test))]
        espece = especes[np.random.randint(len(especes))]
        stade  = np.random.randint(0, 5)
        region = regions[np.random.randint(len(regions))]

        mod_region = MODIFICATEURS_REGION[region]
        pk = simuler_pk(mol, espece)
        phys_saine    = get_physiologie_saine(espece, region=region)
        phys_infectee = simuler_infection(phys_saine, stade, germe)
        eff = calculer_efficacite_stade(
            mol, phys_infectee, phys_saine, stade, espece, germe, pk
        )
        sec = evaluer_securite_organes(phys_infectee, pk, mol, espece)

        records.append({
            "mw":              mol["mw"],
            "logp":            mol["logp"],
            "hbd":             mol["hbd"],
            "hba":             mol["hba"],
            "tpsa":            mol["tpsa"],
            "activite_base":   mol["activite"],
            "cmi_mgL":         mol["cmi_mgL"],
            "tox_herg":        mol["toxicite_herg"],
            "tox_hepato":      mol["toxicite_hepato"],
            "sa_score":        mol["sa_score"],
            "espece_enc":      {"souris":0,"rat":1,"humain":2}[espece],
            "stade":           stade,
            "who_enc":         {"CRITICAL":2,"HIGH":1,"MEDIUM":0}[germe["who"]],
            "gram_enc":        0 if germe["gram"]=="neg" else 1,
            "immunite_base":   mod_region["immunite_baseline"],
            "resilience":      mod_region["resilience_infection"],
            "absorption":      pk["absorption_pct"],
            "demi_vie":        pk["demi_vie_h"],
            "cmax":            pk["cmax_ugmL"],
            "penetration":     pk["penetration_tissu"],
            # Cibles
            "efficacite_pct":  eff["efficacite_pct"],
            "reduction_log":   eff["reduction_log"],
            "score_toxicite":  sec["score_toxicite"],
        })

    df = pd.DataFrame(records)
    print(f"  ✅ Dataset : {len(df):,} simulations générées")
    return df


def entrainer_modele_simbio(df):
    """
    Entraîne les modèles de prédiction SimBio
    """
    print("\n🤖 Entraînement des modèles SimBio...")

    feature_cols = [
        "mw","logp","hbd","hba","tpsa","activite_base","cmi_mgL",
        "tox_herg","tox_hepato","sa_score","espece_enc","stade",
        "who_enc","gram_enc","immunite_base","resilience",
        "absorption","demi_vie","cmax","penetration"
    ]

    X = df[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Modèle efficacité
    y_eff = df["efficacite_pct"].values
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_eff,
                                               test_size=0.2, random_state=42)
    mod_eff = GradientBoostingRegressor(
        n_estimators=300, max_depth=5,
        learning_rate=0.08, random_state=42
    )
    mod_eff.fit(X_tr, y_tr)
    mae_eff = mean_absolute_error(y_te, mod_eff.predict(X_te))
    r2_eff  = r2_score(y_te, mod_eff.predict(X_te))
    print(f"     Modèle Efficacité : MAE={mae_eff:.2f}% | R²={r2_eff:.4f}")

    # Modèle toxicité
    y_tox = df["score_toxicite"].values
    _, _, y_tr2, y_te2 = train_test_split(X_scaled, y_tox,
                                          test_size=0.2, random_state=42)
    mod_tox = GradientBoostingRegressor(
        n_estimators=200, max_depth=4,
        learning_rate=0.1, random_state=42
    )
    mod_tox.fit(X_tr, y_tr2)
    mae_tox = mean_absolute_error(y_te2, mod_tox.predict(X_te))
    r2_tox  = r2_score(y_te2, mod_tox.predict(X_te))
    print(f"     Modèle Toxicité   : MAE={mae_tox:.4f}  | R²={r2_tox:.4f}")

    return mod_eff, mod_tox, scaler, feature_cols


def sauvegarder_simbio(mod_eff, mod_tox, scaler, feature_cols):
    print("\n💾 Sauvegarde du Modèle 10 SimBio...")
    joblib.dump(mod_eff,      f"{MODEL_DIR}/simbio/model10_efficacite.joblib")
    joblib.dump(mod_tox,      f"{MODEL_DIR}/simbio/model10_toxicite.joblib")
    joblib.dump(scaler,       f"{MODEL_DIR}/simbio/model10_scaler.joblib")
    joblib.dump(feature_cols, f"{MODEL_DIR}/simbio/model10_features.joblib")
    joblib.dump(PHYSIOLOGIE_SOURIS,    f"{MODEL_DIR}/simbio/physio_souris.joblib")
    joblib.dump(PHYSIOLOGIE_RAT,       f"{MODEL_DIR}/simbio/physio_rat.joblib")
    joblib.dump(PHYSIOLOGIE_HUMAIN_BASE,f"{MODEL_DIR}/simbio/physio_humain.joblib")
    joblib.dump(MODIFICATEURS_REGION,  f"{MODEL_DIR}/simbio/mod_region.joblib")
    joblib.dump(MODIFICATEURS_PAYS,    f"{MODEL_DIR}/simbio/mod_pays.joblib")
    joblib.dump(STADES_INFECTION,      f"{MODEL_DIR}/simbio/stades_infection.joblib")
    print(f"  ✅ Tous les fichiers sauvegardés dans : {MODEL_DIR}/simbio/")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("  ResistIA Brain 🧠 — Modèle 10 : SimBio 🧬")
    print("  Simulateur Physiologique & Pharmacologique")
    print("=" * 70)

    # 1. Générer dataset et entraîner modèles
    df = generer_dataset_simbio(n=800)
    mod_eff, mod_tox, scaler, feature_cols = entrainer_modele_simbio(df)
    sauvegarder_simbio(mod_eff, mod_tox, scaler, feature_cols)

    # 2. Définir la molécule à tester (générée par Modèle 9)
    molecule_test = {
        "nom":            "Candidat_KPC_001 (généré par Modèle 9)",
        "mw":             417.0,
        "logp":           -1.42,
        "hbd":            4,
        "hba":            7,
        "tpsa":           91.9,
        "n_arom":         1,
        "activite":       0.887,
        "cmi_mgL":        1.007,
        "toxicite_herg":  0.226,
        "toxicite_hepato":0.247,
        "sa_score":       3.8,
    }

    germe_cible = {
        "nom":        "Klebsiella pneumoniae KPC",
        "who":        "CRITICAL",
        "gram":       "neg",
        "resistances":["ampicilline","ceftriaxone","ciprofloxacine"],
    }

    print("\n" + "="*70)
    print("  🧪 SIMULATIONS EN COURS...")
    print("="*70)

    # ── Simulation 1 : Souris ──
    print("\n▶ Simulation 1 : Souris (Mus musculus)")
    sim_souris = simuler_molecule_complete(
        molecule_test, "souris", germe_cible, dose_mgkg=50
    )
    afficher_resultats_simbio(sim_souris)

    # ── Simulation 2 : Rat ──
    print("\n▶ Simulation 2 : Rat (Rattus norvegicus)")
    sim_rat = simuler_molecule_complete(
        molecule_test, "rat", germe_cible, dose_mgkg=30
    )
    afficher_resultats_simbio(sim_rat)

    # ── Simulation 3 : Humain — AFRO (Togo) ──
    print("\n▶ Simulation 3 : Humain — Région AFRO / Togo")
    sim_togo = simuler_molecule_complete(
        molecule_test, "humain", germe_cible,
        pays="TG", region="AFRO", dose_mgkg=10
    )
    afficher_resultats_simbio(sim_togo)

    # ── Simulation 4 : Humain — EURO (France) ──
    print("\n▶ Simulation 4 : Humain — Région EURO / France")
    sim_france = simuler_molecule_complete(
        molecule_test, "humain", germe_cible,
        pays="FR", region="EURO", dose_mgkg=10
    )
    afficher_resultats_simbio(sim_france)

    # ── Simulation 5 : Humain — SEARO (Inde) ──
    print("\n▶ Simulation 5 : Humain — Région SEARO / Inde")
    sim_inde = simuler_molecule_complete(
        molecule_test, "humain", germe_cible,
        pays="IN", region="SEARO", dose_mgkg=10
    )
    afficher_resultats_simbio(sim_inde)

    print("\n" + "="*70)
    print("  ✅ Modèle 10 — SimBio 🧬 terminé !")
    print("  🧠 ResistIA Brain — 10/10 modèles opérationnels !")
    print("="*70)