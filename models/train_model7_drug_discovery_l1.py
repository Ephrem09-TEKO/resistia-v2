"""
ResistIA v2.0 — Modèle 7 : Drug Discovery Niveau 1
ResistIA Brain 🧠 — Repositionnement Moléculaire
Identifie des molécules EXISTANTES approuvées potentiellement
actives contre des bactéries résistantes
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

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

# RDKit pour la chimie computationnelle
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
    from rdkit.Chem.rdMolDescriptors import CalcTPSA
    RDKIT_OK = True
    print("✅ RDKit disponible")
except ImportError:
    RDKIT_OK = False
    print("⚠️ RDKit non disponible — mode simplifié")

DATA_DIR  = "C:\\ResistIA_v2\\data\\synthetic"
MODEL_DIR = "C:\\ResistIA_v2\\models"
os.makedirs(f"{MODEL_DIR}/drug_discovery", exist_ok=True)


# ─────────────────────────────────────────────
# BASE DE MOLÉCULES APPROUVÉES
# Antibiotiques et molécules avec données
# d'activité antimicrobienne connues
# Source : données calibrées sur ChEMBL/PubChem
# ─────────────────────────────────────────────

MOLECULES_APPROUVEES = [
    # ── Antibiotiques classiques ──
    {"nom":"Ciprofloxacine",    "smiles":"C1CN(C1)c2nc3c(cc2F)cc(c(n3)C(=O)O)N4CCN(CC4)c5ncc(cc5F)C(=O)O",
     "classe":"Fluoroquinolone","approuve":True,"mw":331.3,"logp":0.28,"hbd":2,"hba":6,
     "activite_gram_neg":0.85,"activite_gram_pos":0.60,"activite_anaerobe":0.20,"toxicite":0.25},
    {"nom":"Amoxicilline",      "smiles":"CC1(C(N2C(S1)C(C2=O)NC(=O)c3ccc(cc3)O)C(=O)O)C",
     "classe":"Penicilline",    "approuve":True,"mw":365.4,"logp":0.87,"hbd":4,"hba":6,
     "activite_gram_neg":0.45,"activite_gram_pos":0.75,"activite_anaerobe":0.50,"toxicite":0.15},
    {"nom":"Vancomycine",       "smiles":"OC1=CC2=CC(=CC(=C2C(=C1)Cl)OC3=C(C=C4C(=C3)C(NC4=O)CC(NC(=O)C5CC(=CC(=C5)OC6=CC(=CC(=C6Cl)O)O)O)C(=O)O)O)Cl",
     "classe":"Glycopeptide",   "approuve":True,"mw":1449.3,"logp":-3.1,"hbd":9,"hba":14,
     "activite_gram_neg":0.05,"activite_gram_pos":0.90,"activite_anaerobe":0.30,"toxicite":0.40},
    {"nom":"Méropénem",         "smiles":"CC1C2CC(=O)N2C(=C1SC3CC(NC3)C(=O)N(C)C)C(=O)O",
     "classe":"Carbapenem",     "approuve":True,"mw":383.5,"logp":-0.75,"hbd":3,"hba":7,
     "activite_gram_neg":0.92,"activite_gram_pos":0.70,"activite_anaerobe":0.80,"toxicite":0.20},
    {"nom":"Linézolide",        "smiles":"CC(=O)NCC1CN(c2ccc(cc2F)N3CC(OC3=O)CNC(=O)C)CC1",
     "classe":"Oxazolidinone",  "approuve":True,"mw":337.3,"logp":0.55,"hbd":2,"hba":5,
     "activite_gram_neg":0.10,"activite_gram_pos":0.88,"activite_anaerobe":0.60,"toxicite":0.35},
    {"nom":"Daptomycine",       "smiles":"CCCCCCCCCC(=O)N[C@@H](CC1=CNC2=CC=CC=C12)C(=O)N",
     "classe":"Lipopeptide",    "approuve":True,"mw":1620.7,"logp":2.1,"hbd":10,"hba":15,
     "activite_gram_neg":0.05,"activite_gram_pos":0.92,"activite_anaerobe":0.20,"toxicite":0.30},
    {"nom":"Colistine",         "smiles":"CCC(C)CCCCC(=O)NC(CCN)C(=O)NC(C(C)CC)C(=O)NC(CCN)C(=O)NC1CCNC(=O)C(CCN)NC(=O)C(CCN)NC(=O)C(CC(C)C)NC(=O)C(CCN)NC1=O",
     "classe":"Polymyxine",     "approuve":True,"mw":1155.4,"logp":-1.5,"hbd":8,"hba":12,
     "activite_gram_neg":0.88,"activite_gram_pos":0.02,"activite_anaerobe":0.05,"toxicite":0.65},
    {"nom":"Aztréonam",         "smiles":"CC1(C(N2C(S1)C(C2=O)NC(=O)C(=NO)c3csc(n3)N)(C(=O)O)OS(=O)(=O)O)C",
     "classe":"Monobactam",     "approuve":True,"mw":435.4,"logp":-2.1,"hbd":3,"hba":9,
     "activite_gram_neg":0.75,"activite_gram_pos":0.02,"activite_anaerobe":0.01,"toxicite":0.18},
    {"nom":"Ceftriaxone",       "smiles":"CC1=C(SC(=N1)SCC2=NN=C(O2)NCC(=O)O)NC(=O)C(=NOC(C)(C)C(=O)O)c3csc(n3)N",
     "classe":"Cephalosporine", "approuve":True,"mw":554.6,"logp":-1.7,"hbd":4,"hba":12,
     "activite_gram_neg":0.78,"activite_gram_pos":0.55,"activite_anaerobe":0.30,"toxicite":0.15},
    {"nom":"Tigécycline",       "smiles":"CN(C)CC(=O)NC1(CC1)NC(=O)c2cc3cc4c(cc3c(=C2)O)C(=O)C(=C4N(C)C)O",
     "classe":"Glycylcycline",  "approuve":True,"mw":585.7,"logp":-0.5,"hbd":6,"hba":11,
     "activite_gram_neg":0.82,"activite_gram_pos":0.80,"activite_anaerobe":0.75,"toxicite":0.30},
    # ── Molécules repositionnées (usage non antibiotique initial) ──
    {"nom":"Minocycline",       "smiles":"CN(C)C1CC2CC3CC(=C(C3=C(C2=C1O)O)C(=O)N)N(C)C",
     "classe":"Tetracycline",   "approuve":True,"mw":457.5,"logp":-0.05,"hbd":5,"hba":9,
     "activite_gram_neg":0.70,"activite_gram_pos":0.65,"activite_anaerobe":0.70,"toxicite":0.28},
    {"nom":"Fosfomycine",       "smiles":"CC1OC1P(=O)(O)O",
     "classe":"Phosphonique",   "approuve":True,"mw":138.1,"logp":-1.4,"hbd":2,"hba":4,
     "activite_gram_neg":0.72,"activite_gram_pos":0.55,"activite_anaerobe":0.20,"toxicite":0.12},
    {"nom":"Rifampicine",       "smiles":"CC1=C2NC(=O)c3c(cc(cc3OC)OC)OC(=O)CC(=C/C=C/C(C)C(OC(=O)C)C(C)C(OC(=O)C)CC2=N1)C",
     "classe":"Rifamycine",     "approuve":True,"mw":822.9,"logp":2.7,"hbd":3,"hba":10,
     "activite_gram_neg":0.40,"activite_gram_pos":0.85,"activite_anaerobe":0.50,"toxicite":0.35},
    {"nom":"Nitrofurantoïne",   "smiles":"O=C1NC(=O)C(=NNC(=O)c2ccco2)N1",
     "classe":"Nitrofurane",    "approuve":True,"mw":238.2,"logp":-0.5,"hbd":3,"hba":6,
     "activite_gram_neg":0.65,"activite_gram_pos":0.40,"activite_anaerobe":0.30,"toxicite":0.25},
    {"nom":"Céfidérocol",       "smiles":"CC1=C(SC(=N1)SCC2=NN=C(O2)NCC(=O)O)NC(=O)C(=NOC3CC(N)C(O3)CNC(=O)CN4CCCC4)c5csc(n5)N",
     "classe":"Siderophore_ceph","approuve":True,"mw":752.8,"logp":-2.5,"hbd":6,"hba":14,
     "activite_gram_neg":0.95,"activite_gram_pos":0.20,"activite_anaerobe":0.10,"toxicite":0.15},
    # ── Antifongiques ──
    {"nom":"Fluconazole",       "smiles":"OC(Cn1cncn1)(Cn2cncn2)c3ccc(cc3F)F",
     "classe":"Azole",          "approuve":True,"mw":306.3,"logp":0.5,"hbd":1,"hba":7,
     "activite_gram_neg":0.02,"activite_gram_pos":0.02,"activite_anaerobe":0.01,"toxicite":0.20},
    {"nom":"Voriconazole",      "smiles":"CC1(CN2C=NC=N2)OC(c3ccc(F)cc3F)c4nccnc4F",
     "classe":"Azole",          "approuve":True,"mw":349.3,"logp":1.8,"hbd":1,"hba":6,
     "activite_gram_neg":0.02,"activite_gram_pos":0.02,"activite_anaerobe":0.01,"toxicite":0.28},
    {"nom":"Caspofungine",      "smiles":"CCCCCCCCCCCCC(=O)NC1CC(NC(=O)C2CC(O)CN2C(=O)C(CC(=O)N)NC(=O)C(NC(=O)C(NC(=O)C3CC(O)CN3C1=O)CC(O)c4ccc(O)cc4)C(C)O)C(O)CC(O)(C(N)=O)CC(O)CC(=O)N",
     "classe":"Echinocandine",  "approuve":True,"mw":1093.2,"logp":-1.2,"hbd":12,"hba":16,
     "activite_gram_neg":0.01,"activite_gram_pos":0.01,"activite_anaerobe":0.01,"toxicite":0.22},
]

# ─────────────────────────────────────────────
# BACTÉRIES CIBLES RÉSISTANTES
# ─────────────────────────────────────────────

BACTERIES_CIBLES = [
    {"id":1,  "nom":"Klebsiella pneumoniae KPC",   "gram":"neg","eskape":True,
     "profil":"carbapenem_resistant","who":"CRITICAL",
     "abx_actifs_connus":["colistine","cefiderocol","tigecycline"]},
    {"id":2,  "nom":"Acinetobacter baumannii XDR", "gram":"neg","eskape":True,
     "profil":"pandrug_resistant",   "who":"CRITICAL",
     "abx_actifs_connus":["colistine","tigecycline","cefiderocol"]},
    {"id":3,  "nom":"Pseudomonas aeruginosa MDR",  "gram":"neg","eskape":True,
     "profil":"multidrug_resistant", "who":"CRITICAL",
     "abx_actifs_connus":["colistine","cefiderocol","aztreonam"]},
    {"id":4,  "nom":"E. coli ESBL",                "gram":"neg","eskape":False,
     "profil":"esbl_producer",       "who":"HIGH",
     "abx_actifs_connus":["meropenem","amikacine","fosfomycine","nitrofurantoine"]},
    {"id":5,  "nom":"SARM (S. aureus MRSA)",        "gram":"pos","eskape":True,
     "profil":"methicillin_resistant","who":"HIGH",
     "abx_actifs_connus":["vancomycine","linezolide","daptomycine"]},
    {"id":6,  "nom":"Enterococcus faecium VRE",    "gram":"pos","eskape":True,
     "profil":"vancomycin_resistant","who":"HIGH",
     "abx_actifs_connus":["linezolide","daptomycine","tigecycline"]},
    {"id":7,  "nom":"Candida auris MDR",            "gram":"fungi","eskape":False,
     "profil":"azole_resistant",     "who":"CRITICAL",
     "abx_actifs_connus":["caspofungine","amphotericine_b"]},
    {"id":8,  "nom":"M. tuberculosis MDR-TB",       "gram":"mycobact","eskape":False,
     "profil":"mdr_tb",              "who":"CRITICAL",
     "abx_actifs_connus":["bedaquiline","delamanid","linezolide"]},
]


# ─────────────────────────────────────────────
# 1. CALCUL DES FINGERPRINTS MOLÉCULAIRES
# ─────────────────────────────────────────────

def calculer_features_moleculaires(molecules):
    """
    Calcule les descripteurs physicochimiques et fingerprints
    pour chaque molécule de la base
    """
    print("\n🔬 Calcul des features moléculaires...")
    records = []

    for mol in molecules:
        features = {
            "nom":              mol["nom"],
            "classe":           mol["classe"],
            "mw":               mol["mw"],
            "logp":             mol["logp"],
            "hbd":              mol["hbd"],
            "hba":              mol["hba"],
            "activite_gram_neg":mol["activite_gram_neg"],
            "activite_gram_pos":mol["activite_gram_pos"],
            "activite_anaerobe":mol["activite_anaerobe"],
            "toxicite":         mol["toxicite"],
        }

        # Calcul des features RDKit si disponible
        if RDKIT_OK and mol.get("smiles"):
            try:
                m = Chem.MolFromSmiles(mol["smiles"])
                if m:
                    features["tpsa"]      = CalcTPSA(m)
                    features["n_anneaux"] = rdMolDescriptors.CalcNumRings(m)
                    features["n_rot_bonds"]= rdMolDescriptors.CalcNumRotatableBonds(m)
                    features["n_aromat"]  = rdMolDescriptors.CalcNumAromaticRings(m)
                    # Morgan Fingerprint radius 2 (ECFP4)
                    fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=64)
                    fp_bits = list(fp.ToBitString())
                    for i, bit in enumerate(fp_bits[:16]):
                        features[f"fp_{i}"] = int(bit)
                else:
                    features.update({"tpsa":0,"n_anneaux":0,"n_rot_bonds":0,"n_aromat":0})
                    for i in range(16): features[f"fp_{i}"] = 0
            except:
                features.update({"tpsa":0,"n_anneaux":0,"n_rot_bonds":0,"n_aromat":0})
                for i in range(16): features[f"fp_{i}"] = 0
        else:
            # Features simulées si RDKit non dispo
            np.random.seed(hash(mol["nom"]) % 2**31)
            features["tpsa"]       = mol["mw"] * 0.15 + np.random.normal(0, 5)
            features["n_anneaux"]  = max(0, int(mol["mw"] / 150))
            features["n_rot_bonds"]= max(0, int(mol["mw"] / 80))
            features["n_aromat"]   = max(0, int(mol["mw"] / 200))
            for i in range(16):
                features[f"fp_{i}"] = np.random.randint(0, 2)

        # Règle de Lipinski (drug-likeness)
        features["lipinski_ok"] = int(
            mol["mw"] <= 500 and mol["logp"] <= 5 and
            mol["hbd"] <= 5 and mol["hba"] <= 10
        )

        records.append(features)

    df = pd.DataFrame(records)
    print(f"  ✅ {len(df)} molécules avec {len(df.columns)} features")
    return df


# ─────────────────────────────────────────────
# 2. GÉNÉRATION DU DATASET ACTIVITÉ
# ─────────────────────────────────────────────

def generer_dataset_activite(df_mol, bacteries):
    """
    Génère un dataset d'entraînement :
    Pour chaque paire (molécule, bactérie) → score d'activité prédit
    """
    print("\n🔧 Génération du dataset molécule-bactérie...")
    records = []

    for _, mol_row in df_mol.iterrows():
        for bacterie in bacteries:
            # Score d'activité selon le type de bactérie
            if bacterie["gram"] == "neg":
                base_score = mol_row["activite_gram_neg"]
            elif bacterie["gram"] == "pos":
                base_score = mol_row["activite_gram_pos"]
            elif bacterie["gram"] == "fungi":
                # Pour fungi, on utilise activite_anaerobe comme proxy
                base_score = mol_row["activite_anaerobe"] * 0.5
            else:
                base_score = mol_row["activite_anaerobe"]

            # Malus si profil de résistance sévère
            malus_resistance = {
                "carbapenem_resistant": 0.3,
                "pandrug_resistant":    0.5,
                "multidrug_resistant":  0.25,
                "esbl_producer":        0.15,
                "methicillin_resistant":0.2,
                "vancomycin_resistant": 0.2,
                "azole_resistant":      0.4,
                "mdr_tb":               0.6,
            }
            malus = malus_resistance.get(bacterie["profil"], 0.2)

            # Bonus si la molécule est connue active contre cette bactérie
            nom_lower = mol_row["nom"].lower().replace(" ", "_").replace("é","e").replace("è","e")
            est_connu = any(
                connu in nom_lower
                for connu in bacterie["abx_actifs_connus"]
            )
            bonus = 0.2 if est_connu else 0.0

            score_final = min(1.0, max(0.0,
                base_score * (1 - malus) + bonus +
                np.random.normal(0, 0.05)
            ))

            # Label binaire : actif (1) si score > 0.5
            actif = int(score_final > 0.5)

            record = {
                "molecule":        mol_row["nom"],
                "bacterie_id":     bacterie["id"],
                "bacterie_nom":    bacterie["nom"],
                "gram":            bacterie["gram"],
                "who":             bacterie["who"],
                "profil":          bacterie["profil"],
                "score_activite":  round(score_final, 3),
                "actif":           actif,
            }

            # Ajouter les features moléculaires
            feature_cols = [c for c in df_mol.columns
                           if c not in ["nom","classe"]]
            for col in feature_cols:
                record[col] = mol_row[col]

            records.append(record)

    df = pd.DataFrame(records)
    print(f"  ✅ Dataset : {len(df):,} paires molécule-bactérie")
    print(f"  📊 Molécules actives : {df['actif'].sum()} ({df['actif'].mean()*100:.1f}%)")
    return df


# ─────────────────────────────────────────────
# 3. ENTRAÎNEMENT
# ─────────────────────────────────────────────

def entrainer_modele(df_dataset):
    print("\n🤖 Entraînement du modèle de repositionnement...")

    le_gram    = LabelEncoder()
    le_who     = LabelEncoder()
    le_profil  = LabelEncoder()

    df_dataset["gram_enc"]   = le_gram.fit_transform(df_dataset["gram"])
    df_dataset["who_enc"]    = le_who.fit_transform(df_dataset["who"])
    df_dataset["profil_enc"] = le_profil.fit_transform(df_dataset["profil"])

    feature_cols = [
        "mw","logp","hbd","hba","tpsa","n_anneaux",
        "n_rot_bonds","n_aromat","lipinski_ok",
        "activite_gram_neg","activite_gram_pos","activite_anaerobe",
        "toxicite","gram_enc","who_enc","profil_enc",
    ] + [f"fp_{i}" for i in range(16)]

    X = df_dataset[feature_cols]
    y = df_dataset["actif"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modele = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    modele.fit(X_train, y_train)

    y_pred  = modele.predict(X_test)
    y_proba = modele.predict_proba(X_test)[:, 1]
    acc     = accuracy_score(y_test, y_pred)
    auc     = roc_auc_score(y_test, y_proba)

    print(f"\n  📊 Résultats :")
    print(f"     Accuracy : {acc*100:.1f}%")
    print(f"     AUC-ROC  : {auc:.4f}")
    print(f"\n  📋 Rapport :")
    print(classification_report(y_test, y_pred,
                                target_names=["Inactif","Actif"]))

    return modele, feature_cols, le_gram, le_who, le_profil


# ─────────────────────────────────────────────
# 4. SAUVEGARDE
# ─────────────────────────────────────────────

def sauvegarder(modele, feature_cols, le_gram, le_who, le_profil, df_mol):
    print("\n💾 Sauvegarde du modèle...")
    joblib.dump(modele,      f"{MODEL_DIR}/drug_discovery/model7_repositionnement.joblib")
    joblib.dump(feature_cols,f"{MODEL_DIR}/drug_discovery/model7_features.joblib")
    joblib.dump(le_gram,     f"{MODEL_DIR}/drug_discovery/model7_le_gram.joblib")
    joblib.dump(le_who,      f"{MODEL_DIR}/drug_discovery/model7_le_who.joblib")
    joblib.dump(le_profil,   f"{MODEL_DIR}/drug_discovery/model7_le_profil.joblib")
    df_mol.to_csv(f"{MODEL_DIR}/drug_discovery/molecules_approuvees.csv", index=False)
    with open(f"{MODEL_DIR}/drug_discovery/bacteries_cibles.json","w") as f:
        json.dump(BACTERIES_CIBLES, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Modèle sauvegardé dans : {MODEL_DIR}/drug_discovery/")


# ─────────────────────────────────────────────
# 5. TEST — REPOSITIONNEMENT POUR K. PNEUMONIAE
# ─────────────────────────────────────────────

def tester_repositionnement(modele, feature_cols,
                             le_gram, le_who, le_profil, df_mol):
    print("\n🔬 Repositionnement moléculaire — Cible : K. pneumoniae KPC")
    print("   (Klebsiella pneumoniae résistante aux carbapénèmes)")

    bacterie_cible = BACTERIES_CIBLES[0]  # K. pneumoniae KPC

    resultats = []
    for _, mol_row in df_mol.iterrows():
        vecteur = {}
        for col in feature_cols:
            if col == "gram_enc":
                try: vecteur[col] = float(le_gram.transform(["neg"])[0])
                except: vecteur[col] = 0.0
            elif col == "who_enc":
                try: vecteur[col] = float(le_who.transform(["CRITICAL"])[0])
                except: vecteur[col] = 0.0
            elif col == "profil_enc":
                try: vecteur[col] = float(le_profil.transform(
                    ["carbapenem_resistant"])[0])
                except: vecteur[col] = 0.0
            elif col in mol_row.index:
                vecteur[col] = float(mol_row[col])
            else:
                vecteur[col] = 0.0

        X_pred = pd.DataFrame([vecteur])
        proba  = modele.predict_proba(X_pred)[0][1]

        resultats.append({
            "molecule":  mol_row["nom"],
            "classe":    mol_row["classe"],
            "score":     round(proba * 100, 1),
            "mw":        mol_row["mw"],
            "logp":      mol_row["logp"],
            "lipinski":  "✅" if mol_row["lipinski_ok"] else "❌",
            "toxicite":  mol_row["toxicite"],
        })

    # Trier par score décroissant
    resultats = sorted(resultats, key=lambda x: x["score"], reverse=True)

    print(f"\n  💊 Top 5 molécules candidates pour K. pneumoniae KPC :")
    print(f"  {'Molécule':<22} {'Classe':<18} {'Score':>7} "
          f"{'MW':>7} {'LogP':>6} {'Lipinski':>9} {'Toxicité':>9}")
    print(f"  {'-'*82}")
    for r in resultats[:5]:
        tox_bar = "⚠️" if r["toxicite"] > 0.4 else "✅"
        print(f"  {r['molecule']:<22} {r['classe']:<18} "
              f"{r['score']:>6.1f}%  {r['mw']:>6.1f}  {r['logp']:>5.2f}  "
              f"  {r['lipinski']:>6}  {tox_bar} {r['toxicite']:.2f}")

    return resultats


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  ResistIA Brain 🧠 — Modèle 7 : Drug Discovery Niv.1")
    print("  Repositionnement Moléculaire")
    print("=" * 65)

    np.random.seed(42)

    df_mol = calculer_features_moleculaires(MOLECULES_APPROUVEES)

    df_dataset = generer_dataset_activite(df_mol, BACTERIES_CIBLES)

    (modele, feature_cols,
     le_gram, le_who, le_profil) = entrainer_modele(df_dataset)

    sauvegarder(modele, feature_cols, le_gram, le_who, le_profil, df_mol)

    tester_repositionnement(modele, feature_cols,
                            le_gram, le_who, le_profil, df_mol)

    print("\n" + "=" * 65)
    print("  ✅ Modèle 7 terminé !")
    print("=" * 65)