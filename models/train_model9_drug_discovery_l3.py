"""
ResistIA v2.0 — Modèle 9 : Drug Discovery Niveau 3
ResistIA Brain 🧠 — Génération Moléculaire
Génère de NOUVELLES molécules antimicrobiennes optimisées
contre une bactérie résistante cible via algorithme évolutionnaire
Outputs : Top 10 molécules candidates + scores + rapport
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

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor

MODEL_DIR = "C:\\ResistIA_v2\\models"
os.makedirs(f"{MODEL_DIR}/drug_discovery", exist_ok=True)

np.random.seed(42)

# ─────────────────────────────────────────────
# ESPACE CHIMIQUE — Propriétés physicochimiques
# Basé sur la règle de Lipinski + contraintes AMR
# ─────────────────────────────────────────────

# Bornes de l'espace de recherche moléculaire
ESPACE_CHIMIQUE = {
    "mw":      (150,  600),   # Poids moléculaire (Da)
    "logp":    (-3.0, 5.0),   # Lipophilie
    "hbd":     (0,    5),     # Hydrogen Bond Donors
    "hba":     (0,    10),    # Hydrogen Bond Acceptors
    "tpsa":    (20,   200),   # Surface polaire topologique
    "n_rot":   (0,    12),    # Liaisons rotatives
    "n_rings": (1,    6),     # Nombre d'anneaux
    "n_arom":  (0,    4),     # Anneaux aromatiques
}

# Profils cibles par type de bactérie
PROFILS_CIBLES = {
    "gram_negatif": {
        "mw":   (300, 550),  "logp": (-2, 2),
        "hbd":  (1, 4),      "hba":  (4, 10),
        "tpsa": (60, 160),   "n_rot":(3, 8),
        "n_rings":(2,5),     "n_arom":(1,3),
    },
    "gram_positif": {
        "mw":   (200, 500),  "logp": (0, 4),
        "hbd":  (1, 4),      "hba":  (2, 8),
        "tpsa": (40, 130),   "n_rot":(2, 7),
        "n_rings":(1,4),     "n_arom":(1,3),
    },
    "fungi": {
        "mw":   (250, 500),  "logp": (1, 5),
        "hbd":  (0, 3),      "hba":  (3, 8),
        "tpsa": (40, 120),   "n_rot":(3, 9),
        "n_rings":(2,5),     "n_arom":(1,3),
    },
    "mycobacterium": {
        "mw":   (200, 480),  "logp": (0, 4),
        "hbd":  (1, 4),      "hba":  (3, 9),
        "tpsa": (60, 150),   "n_rot":(2, 8),
        "n_rings":(2,5),     "n_arom":(1,3),
    },
}

# ─────────────────────────────────────────────
# BASES DE DONNÉES DE RÉFÉRENCE
# ─────────────────────────────────────────────

MOLECULES_REFERENCE = [
    {"nom":"Ciprofloxacine","mw":331.3,"logp":0.28,"hbd":2,"hba":6,"tpsa":74.6,
     "n_rot":3,"n_rings":3,"n_arom":2,"activite":0.85,"cmi_ecoli":0.015,
     "cmi_kpneu":0.06,"cmi_paerug":0.25,"cmi_saureus":0.50,
     "toxicite_herg":0.25,"toxicite_hepato":0.20,"solubilite":0.65,"sa_score":2.8,"lipinski":1},
    {"nom":"Méropénem","mw":383.5,"logp":-0.75,"hbd":3,"hba":7,"tpsa":115.9,
     "n_rot":4,"n_rings":3,"n_arom":0,"activite":0.92,"cmi_ecoli":0.015,
     "cmi_kpneu":0.25,"cmi_paerug":0.50,"cmi_saureus":4.0,
     "toxicite_herg":0.15,"toxicite_hepato":0.20,"solubilite":0.70,"sa_score":4.5,"lipinski":1},
    {"nom":"Linézolide","mw":337.3,"logp":0.55,"hbd":2,"hba":5,"tpsa":88.4,
     "n_rot":4,"n_rings":3,"n_arom":1,"activite":0.88,"cmi_ecoli":8.0,
     "cmi_kpneu":8.0,"cmi_paerug":32.0,"cmi_saureus":1.0,
     "toxicite_herg":0.30,"toxicite_hepato":0.35,"solubilite":0.60,"sa_score":3.8,"lipinski":1},
    {"nom":"Fosfomycine","mw":138.1,"logp":-1.4,"hbd":2,"hba":4,"tpsa":71.3,
     "n_rot":1,"n_rings":1,"n_arom":0,"activite":0.72,"cmi_ecoli":8.0,
     "cmi_kpneu":32.0,"cmi_paerug":64.0,"cmi_saureus":32.0,
     "toxicite_herg":0.08,"toxicite_hepato":0.10,"solubilite":0.92,"sa_score":1.5,"lipinski":1},
    {"nom":"Tigécycline","mw":585.7,"logp":-0.5,"hbd":6,"hba":11,"tpsa":183.8,
     "n_rot":6,"n_rings":5,"n_arom":3,"activite":0.82,"cmi_ecoli":0.25,
     "cmi_kpneu":0.50,"cmi_paerug":8.0,"cmi_saureus":0.12,
     "toxicite_herg":0.28,"toxicite_hepato":0.25,"solubilite":0.55,"sa_score":5.2,"lipinski":0},
    {"nom":"Céfidérocol","mw":752.8,"logp":-2.5,"hbd":6,"hba":14,"tpsa":220.0,
     "n_rot":8,"n_rings":5,"n_arom":2,"activite":0.95,"cmi_ecoli":0.015,
     "cmi_kpneu":0.06,"cmi_paerug":0.12,"cmi_saureus":8.0,
     "toxicite_herg":0.12,"toxicite_hepato":0.15,"solubilite":0.50,"sa_score":6.5,"lipinski":0},
    {"nom":"Daptomycine","mw":1620.7,"logp":2.1,"hbd":10,"hba":15,"tpsa":280.0,
     "n_rot":18,"n_rings":3,"n_arom":1,"activite":0.92,"cmi_ecoli":32.0,
     "cmi_kpneu":32.0,"cmi_paerug":64.0,"cmi_saureus":0.25,
     "toxicite_herg":0.25,"toxicite_hepato":0.28,"solubilite":0.35,"sa_score":8.5,"lipinski":0},
    {"nom":"Aztréonam","mw":435.4,"logp":-2.1,"hbd":3,"hba":9,"tpsa":145.0,
     "n_rot":5,"n_rings":2,"n_arom":1,"activite":0.75,"cmi_ecoli":0.06,
     "cmi_kpneu":0.25,"cmi_paerug":2.0,"cmi_saureus":64.0,
     "toxicite_herg":0.15,"toxicite_hepato":0.18,"solubilite":0.60,"sa_score":4.8,"lipinski":1},
]

FEATURE_COLS = ["mw","logp","hbd","hba","tpsa",
                "n_rot","n_rings","n_arom","lipinski"]

# ─────────────────────────────────────────────
# 1. MODÈLE DE SCORING (basé sur Modèle 8)
# ─────────────────────────────────────────────

def construire_scoreur():
    """
    Construit un scoreur KNN entraîné sur les molécules
    de référence pour évaluer les nouvelles molécules générées
    """
    df = pd.DataFrame(MOLECULES_REFERENCE)
    X  = df[FEATURE_COLS].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    scoreurs = {}
    targets = {
        "activite":       df["activite"].values,
        "cmi_ecoli":      np.log1p(df["cmi_ecoli"].values),
        "cmi_kpneu":      np.log1p(df["cmi_kpneu"].values),
        "cmi_paerug":     np.log1p(df["cmi_paerug"].values),
        "cmi_saureus":    np.log1p(df["cmi_saureus"].values),
        "toxicite_herg":  df["toxicite_herg"].values,
        "toxicite_hepato":df["toxicite_hepato"].values,
        "solubilite":     df["solubilite"].values,
        "sa_score":       df["sa_score"].values,
    }
    for nom, y in targets.items():
        knn = KNeighborsRegressor(n_neighbors=3, weights="distance")
        knn.fit(X_scaled, y)
        scoreurs[nom] = knn

    return scoreurs, scaler


def scorer_molecule(props, scoreurs, scaler, profil_gram):
    """
    Calcule le score global d'une molécule candidate
    Score composite : activité, toxicité, ADME, Lipinski
    """
    lipinski = int(
        props["mw"] <= 500 and props["logp"] <= 5 and
        props["hbd"] <= 5 and props["hba"] <= 10
    )
    props["lipinski"] = lipinski

    X = np.array([[props[f] for f in FEATURE_COLS]])
    X_scaled = scaler.transform(X)

    activite      = float(np.clip(scoreurs["activite"].predict(X_scaled)[0], 0, 1))
    tox_herg      = float(np.clip(scoreurs["toxicite_herg"].predict(X_scaled)[0], 0, 1))
    tox_hepato    = float(np.clip(scoreurs["toxicite_hepato"].predict(X_scaled)[0], 0, 1))
    solubilite    = float(np.clip(scoreurs["solubilite"].predict(X_scaled)[0], 0, 1))
    sa_score      = float(np.clip(scoreurs["sa_score"].predict(X_scaled)[0], 1, 10))

    # CMI selon le gram
    if profil_gram == "gram_negatif":
        cmi_key = "cmi_ecoli"
    elif profil_gram == "fungi":
        cmi_key = "cmi_kpneu"
    else:
        cmi_key = "cmi_saureus"

    cmi_log = float(scoreurs[cmi_key].predict(X_scaled)[0])
    cmi_val = float(np.expm1(cmi_log))

    # Score CMI normalisé (plus bas = meilleur)
    score_cmi = float(np.clip(1.0 - (cmi_val / 64.0), 0, 1))

    # Score de synthétisabilité (SA Score inversé)
    score_sa = float(1.0 - (sa_score - 1) / 9.0)

    # Score global pondéré
    score_global = (
        activite    * 0.35 +
        score_cmi   * 0.25 +
        (1-tox_herg)* 0.15 +
        (1-tox_hepato)* 0.10 +
        solubilite  * 0.08 +
        score_sa    * 0.05 +
        lipinski    * 0.02
    )

    return {
        "score_global":     round(score_global * 100, 1),
        "activite":         round(activite * 100, 1),
        "cmi_mgL":          round(cmi_val, 3),
        "toxicite_herg":    round(tox_herg, 3),
        "toxicite_hepato":  round(tox_hepato, 3),
        "solubilite":       round(solubilite, 3),
        "sa_score":         round(sa_score, 2),
        "lipinski_ok":      lipinski,
        **{k: round(props[k], 3) for k in FEATURE_COLS if k != "lipinski"},
    }


# ─────────────────────────────────────────────
# 2. GÉNÉRATION PAR ALGORITHME ÉVOLUTIONNAIRE
# ─────────────────────────────────────────────

def generer_population_initiale(profil_cible, n=200):
    """
    Génère une population initiale de molécules
    dans l'espace chimique défini par le profil cible
    """
    bornes = PROFILS_CIBLES[profil_cible]
    population = []

    for _ in range(n):
        mol = {}
        for prop, (lo, hi) in bornes.items():
            if prop in ["hbd","hba","n_rot","n_rings","n_arom"]:
                mol[prop] = float(np.random.randint(int(lo), int(hi)+1))
            else:
                mol[prop] = float(np.random.uniform(lo, hi))
        population.append(mol)

    return population


def muter(molecule, profil_cible, taux_mutation=0.3):
    """
    Mute aléatoirement certaines propriétés d'une molécule
    (simule une modification chimique)
    """
    bornes = PROFILS_CIBLES[profil_cible]
    mutant = molecule.copy()

    for prop, (lo, hi) in bornes.items():
        if np.random.random() < taux_mutation:
            if prop in ["hbd","hba","n_rot","n_rings","n_arom"]:
                delta = np.random.randint(-1, 2)
                mutant[prop] = float(np.clip(mutant[prop] + delta, lo, hi))
            else:
                delta = np.random.normal(0, (hi - lo) * 0.1)
                mutant[prop] = float(np.clip(mutant[prop] + delta, lo, hi))

    return mutant


def croiser(mol1, mol2, profil_cible):
    """
    Croise deux molécules (comme en génétique)
    chaque propriété est héritée de l'un des parents
    """
    bornes = PROFILS_CIBLES[profil_cible]
    enfant = {}

    for prop in bornes.keys():
        lo, hi = bornes[prop]
        if np.random.random() < 0.5:
            enfant[prop] = mol1[prop]
        else:
            enfant[prop] = mol2[prop]

    return enfant


def algorithme_evolutionnaire(profil_gram, scoreurs, scaler,
                               n_generations=50, taille_pop=100,
                               n_elite=10):
    """
    Algorithme évolutionnaire pour générer des molécules optimisées :
    1. Génère une population initiale
    2. Évalue chaque molécule (score global)
    3. Sélectionne les meilleures (élite)
    4. Croise et mute pour créer la génération suivante
    5. Répète sur N générations
    """
    print(f"\n🧬 Algorithme évolutionnaire ({n_generations} générations, "
          f"pop={taille_pop})...")

    # Population initiale
    population = generer_population_initiale(profil_gram, n=taille_pop)

    meilleur_score = 0
    historique     = []

    for gen in range(n_generations):
        # Évaluation
        scores_pop = []
        for mol in population:
            try:
                res = scorer_molecule(mol.copy(), scoreurs, scaler, profil_gram)
                scores_pop.append((res["score_global"], mol, res))
            except:
                scores_pop.append((0, mol, {}))

        scores_pop.sort(key=lambda x: x[0], reverse=True)

        score_gen = scores_pop[0][0]
        historique.append(score_gen)

        if score_gen > meilleur_score:
            meilleur_score = score_gen

        # Affichage progression
        if gen % 10 == 0 or gen == n_generations - 1:
            print(f"  Génération {gen+1:>3}/{n_generations} — "
                  f"Meilleur score : {score_gen:.1f}% | "
                  f"Moyenne top-10 : "
                  f"{np.mean([s[0] for s in scores_pop[:10]]):.1f}%")

        # Sélection élite
        elite = [s[1] for s in scores_pop[:n_elite]]

        # Nouvelle génération
        nouvelle_pop = list(elite)  # garder l'élite

        while len(nouvelle_pop) < taille_pop:
            # Sélection par tournoi
            idx1 = np.random.randint(0, n_elite)
            idx2 = np.random.randint(0, n_elite)
            parent1 = elite[idx1]
            parent2 = elite[idx2]

            # Croisement
            enfant = croiser(parent1, parent2, profil_gram)

            # Mutation
            if np.random.random() < 0.7:
                enfant = muter(enfant, profil_gram)

            nouvelle_pop.append(enfant)

        population = nouvelle_pop

    # Résultats finaux
    resultats_finaux = []
    for mol in population:
        try:
            res = scorer_molecule(mol.copy(), scoreurs, scaler, profil_gram)
            resultats_finaux.append(res)
        except:
            pass

    resultats_finaux.sort(key=lambda x: x["score_global"], reverse=True)

    # Dédupliquer (garder molécules différentes)
    top_molecules = []
    for mol in resultats_finaux:
        est_doublon = any(
            abs(mol["mw"] - m["mw"]) < 5 and
            abs(mol["logp"] - m["logp"]) < 0.2
            for m in top_molecules
        )
        if not est_doublon:
            top_molecules.append(mol)
        if len(top_molecules) >= 10:
            break

    print(f"\n  ✅ {len(top_molecules)} molécules uniques générées")
    print(f"  🏆 Meilleur score atteint : {top_molecules[0]['score_global']}%")

    return top_molecules, historique

# ─────────────────────────────────────────────
# 3. GÉNÉRATION DE SMILES SIMPLIFIÉ
# ─────────────────────────────────────────────

def generer_smiles_approx(props):
    """
    Génère un SMILES approximatif basé sur les propriétés
    (simplifié — dans la vraie app, un modèle VAE/MolGPT
    génère le SMILES exact)
    """
    n_rings  = int(props.get("n_rings", 2))
    n_arom   = int(props.get("n_arom", 1))
    n_rot    = int(props.get("n_rot", 3))
    mw       = props.get("mw", 350)

    # Templates de base selon le type de molécule
    if n_arom >= 2 and mw < 400:
        smiles_base = "c1ccc(cc1)"
        if n_rings >= 3:
            smiles_base += "c2ccncc2"
        if n_rot >= 3:
            smiles_base += "CC(=O)N"
    elif n_arom == 1:
        smiles_base = "C1CC(=O)NC1"
        if n_rings >= 2:
            smiles_base += "C2CCNCC2"
    else:
        smiles_base = "CC(C)(C)C(=O)"
        for _ in range(min(n_rot, 4)):
            smiles_base += "CC"
        smiles_base += "N"

    return smiles_base


# ─────────────────────────────────────────────
# 4. AFFICHAGE ET RAPPORT
# ─────────────────────────────────────────────

def afficher_resultats(top_molecules, bacterie_nom, profil_gram):
    print(f"\n{'='*70}")
    print(f"  💊 TOP 10 MOLÉCULES GÉNÉRÉES POUR : {bacterie_nom}")
    print(f"{'='*70}")
    print(f"\n  {'#':<4} {'Score':>6} {'Activité':>9} {'CMI':>8} "
          f"{'hERG':>6} {'Hépa':>6} {'Sol.':>6} "
          f"{'SA':>5} {'Lip':>5} {'MW':>7} {'LogP':>6}")
    print(f"  {'-'*80}")

    for i, mol in enumerate(top_molecules, 1):
        lip_icon = "✅" if mol["lipinski_ok"] else "❌"
        herg_icon = "✅" if mol["toxicite_herg"] < 0.3 else "⚠️"
        score_icon = "🟢" if mol["score_global"] >= 65 else ("🟡" if mol["score_global"] >= 45 else "🔴")

        print(f"  {i:<4} {score_icon}{mol['score_global']:>5.1f}%"
              f"  {mol['activite']:>7.1f}%"
              f"  {mol['cmi_mgL']:>7.3f}"
              f"  {herg_icon}{mol['toxicite_herg']:>4.3f}"
              f"  {mol['toxicite_hepato']:>5.3f}"
              f"  {mol['solubilite']:>5.3f}"
              f"  {mol['sa_score']:>4.1f}"
              f"  {lip_icon}"
              f"  {mol['mw']:>6.1f}"
              f"  {mol['logp']:>5.2f}")

    print(f"\n  📋 Légende :")
    print(f"     Score   = Score global de la molécule (0-100%)")
    print(f"     Activité= Probabilité d'activité antimicrobienne")
    print(f"     CMI     = Concentration Minimale Inhibitrice (mg/L)")
    print(f"     hERG    = Toxicité cardiaque (< 0.3 = ✅)")
    print(f"     Hépa    = Toxicité hépatique")
    print(f"     Sol.    = Solubilité (> 0.5 = ✅)")
    print(f"     SA      = Score de synthétisabilité (1=facile, 10=difficile)")
    print(f"     Lip     = Règle de Lipinski (drug-likeness)")


def afficher_meilleure_molecule(top_molecules, bacterie_nom):
    best = top_molecules[0]
    print(f"\n{'='*70}")
    print(f"  🏆 MEILLEURE MOLÉCULE CANDIDATE")
    print(f"{'='*70}")
    print(f"\n  Cible         : {bacterie_nom}")
    print(f"  Score global  : {best['score_global']}%")
    print(f"  Activité      : {best['activite']}%")
    print(f"  CMI prédite   : {best['cmi_mgL']} mg/L")
    print(f"\n  Propriétés physicochimiques :")
    print(f"  {'─'*45}")
    print(f"  Poids moléculaire  : {best['mw']:.1f} Da")
    print(f"  LogP (lipophilie)  : {best['logp']:.2f}")
    print(f"  HBD / HBA          : {int(best['hbd'])} / {int(best['hba'])}")
    print(f"  TPSA               : {best['tpsa']:.1f} Å²")
    print(f"  Liaisons rotatives : {int(best['n_rot'])}")
    print(f"  Anneaux / Arom.    : {int(best['n_rings'])} / {int(best['n_arom'])}")
    print(f"\n  Profil de sécurité :")
    print(f"  {'─'*45}")
    herg_status   = "✅ Faible" if best["toxicite_herg"] < 0.3 else "⚠️ Élevé"
    hepato_status = "✅ Faible" if best["toxicite_hepato"] < 0.3 else "⚠️ Élevé"
    sol_status    = "✅ Bonne" if best["solubilite"] >= 0.5 else "⚠️ Faible"
    sa_status     = "✅ Facile" if best["sa_score"] <= 4 else ("🟡 Modéré" if best["sa_score"] <= 6 else "🔴 Difficile")
    lip_status    = "✅ Conforme" if best["lipinski_ok"] else "❌ Non conforme"
    print(f"  Toxicité cardiaque : {herg_status} ({best['toxicite_herg']:.3f})")
    print(f"  Toxicité hépatique : {hepato_status} ({best['toxicite_hepato']:.3f})")
    print(f"  Solubilité         : {sol_status} ({best['solubilite']:.3f})")
    print(f"  Synthétisabilité   : {sa_status} (SA={best['sa_score']:.1f})")
    print(f"  Règle de Lipinski  : {lip_status}")

    smiles = generer_smiles_approx(best)
    print(f"\n  SMILES approx. : {smiles}")
    print(f"  (SMILES exact généré par VAE/MolGPT en production)")


# ─────────────────────────────────────────────
# 5. SAUVEGARDE
# ─────────────────────────────────────────────

def sauvegarder(scoreurs, scaler, top_molecules_dict):
    print("\n💾 Sauvegarde du modèle...")
    joblib.dump(scoreurs, f"{MODEL_DIR}/drug_discovery/model9_scoreurs.joblib")
    joblib.dump(scaler,   f"{MODEL_DIR}/drug_discovery/model9_scaler.joblib")

    with open(f"{MODEL_DIR}/drug_discovery/model9_molecules_generees.json",
              "w", encoding="utf-8") as f:
        json.dump(top_molecules_dict, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Modèle sauvegardé dans : {MODEL_DIR}/drug_discovery/")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("  ResistIA Brain 🧠 — Modèle 9 : Drug Discovery Niv.3")
    print("  Génération Moléculaire par Algorithme Évolutionnaire")
    print("=" * 70)

    # Construction du scoreur
    print("\n🔧 Construction du scoreur moléculaire...")
    scoreurs, scaler = construire_scoreur()
    print("  ✅ Scoreur prêt")

    # 3 cas de génération
    cas_generation = [
        {
            "bacterie": "Klebsiella pneumoniae KPC (Gram-négatif CRITIQUE)",
            "profil":   "gram_negatif",
        },
        {
            "bacterie": "Staphylococcus aureus SARM (Gram-positif HAUTE priorité)",
            "profil":   "gram_positif",
        },
        {
            "bacterie": "Candida auris (Fungi CRITIQUE)",
            "profil":   "fungi",
        },
    ]

    resultats_complets = {}

    for cas in cas_generation:
        print(f"\n\n{'#'*70}")
        print(f"  🎯 CIBLE : {cas['bacterie']}")
        print(f"{'#'*70}")

        top_mols, historique = algorithme_evolutionnaire(
            profil_gram   = cas["profil"],
            scoreurs      = scoreurs,
            scaler        = scaler,
            n_generations = 60,
            taille_pop    = 150,
            n_elite       = 15,
        )

        afficher_resultats(top_mols, cas["bacterie"], cas["profil"])
        afficher_meilleure_molecule(top_mols, cas["bacterie"])

        resultats_complets[cas["bacterie"]] = {
            "profil":      cas["profil"],
            "top10":       top_mols,
            "historique":  historique,
        }

    sauvegarder(scoreurs, scaler, resultats_complets)

    print("\n" + "=" * 70)
    print("  ✅ Modèle 9 terminé !")
    print("  🧠 ResistIA Brain — 9/9 modèles entraînés !")
    print("=" * 70)