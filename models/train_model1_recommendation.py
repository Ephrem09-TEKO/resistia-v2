"""
ResistIA v2.0 — Modèle 1 : Recommandation Thérapeutique
ResistIA Brain 🧠
Entraînement d'un modèle Gradient Boosting pour recommander
le meilleur antibiotique selon le profil de résistance
"""

import sys
import os
sys.path.insert(0, 'C:\\ResistIA_v2')

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (classification_report,
                             accuracy_score, top_k_accuracy_score)
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

DATA_DIR  = "C:\\ResistIA_v2\\data\\synthetic"
MODEL_DIR = "C:\\ResistIA_v2\\models"
os.makedirs(MODEL_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────

def charger_donnees():
    print("\n📂 Chargement des données...")

    df_taux = pd.read_csv(f"{DATA_DIR}/taux_resistance_mondiaux.csv")
    df_pays = pd.read_csv(f"{DATA_DIR}/ref_pays.csv")
    df_patho = pd.read_csv(f"{DATA_DIR}/ref_pathogenes.csv")

    print(f"  ✅ Taux de résistance : {len(df_taux):,} lignes")
    print(f"  ✅ Pays               : {len(df_pays)}")
    print(f"  ✅ Pathogènes         : {len(df_patho)}")

    return df_taux, df_pays, df_patho


# ─────────────────────────────────────────────
# 2. CONSTRUCTION DU DATASET D'ENTRAÎNEMENT
# ─────────────────────────────────────────────

def construire_dataset(df_taux, df_pays, df_patho):
    """
    Pour chaque combinaison pays-pathogène-année,
    on crée un vecteur de features et on identifie
    le meilleur antibiotique (celui avec le taux
    de résistance le plus bas = le plus efficace).
    """
    print("\n🔧 Construction du dataset d'entraînement...")

    # Pivot : une ligne par pays-pathogène-année
    # colonnes = antibiotiques, valeurs = taux de résistance
    df_pivot = df_taux.pivot_table(
        index=["code_pays", "pathogene", "region_oms",
               "referentiel", "annee"],
        columns="antibiotique",
        values="taux_resistance_pct",
        aggfunc="mean"
    ).reset_index()

    # Remplir les valeurs manquantes par la médiane de la colonne
    abx_cols = [c for c in df_pivot.columns
                if c not in ["code_pays","pathogene",
                              "region_oms","referentiel","annee"]]
    df_pivot[abx_cols] = df_pivot[abx_cols].fillna(
        df_pivot[abx_cols].median()
    )

    # Cible : antibiotique avec le taux de résistance le plus bas
    # (= le plus susceptible d'être efficace)
    df_pivot["meilleur_abx"] = df_pivot[abx_cols].idxmin(axis=1)

    # Encoder les variables catégorielles
    le_patho  = LabelEncoder()
    le_region = LabelEncoder()
    le_ref    = LabelEncoder()

    df_pivot["pathogene_enc"]  = le_patho.fit_transform(df_pivot["pathogene"])
    df_pivot["region_enc"]     = le_region.fit_transform(df_pivot["region_oms"])
    df_pivot["referentiel_enc"]= le_ref.fit_transform(df_pivot["referentiel"])

    # Features = profils de résistance + variables contextuelles
    feature_cols = abx_cols + ["pathogene_enc","region_enc",
                                "referentiel_enc","annee"]

    X = df_pivot[feature_cols]
    y = df_pivot["meilleur_abx"]

    # Encoder la cible
    le_target = LabelEncoder()
    y_enc = le_target.fit_transform(y)

    print(f"  ✅ Dataset : {len(X):,} exemples")
    print(f"  ✅ Features : {len(feature_cols)}")
    print(f"  ✅ Classes (antibiotiques) : {len(le_target.classes_)}")

    return X, y_enc, feature_cols, le_patho, le_region, le_ref, le_target, abx_cols

# ─────────────────────────────────────────────
# 3. ENTRAÎNEMENT DU MODÈLE
# ─────────────────────────────────────────────

def entrainer_modele(X, y_enc, n_classes):
    print("\n🤖 Entraînement du modèle XGBoost...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42
    )

    modele = XGBClassifier(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )

    modele.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )

    # Évaluation
    y_pred = modele.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)

    # Top-3 accuracy (le bon ABX est dans le top 3 recommandé)
    y_proba = modele.predict_proba(X_test)
    top3    = top_k_accuracy_score(y_test, y_proba, k=3,
                                   labels=np.arange(n_classes))

    print(f"\n  📊 Résultats :")
    print(f"     Accuracy Top-1  : {acc*100:.1f}%")
    print(f"     Accuracy Top-3  : {top3*100:.1f}%")
    print(f"     Exemples test   : {len(y_test):,}")

    return modele, X_test, y_test


# ─────────────────────────────────────────────
# 4. SAUVEGARDE DU MODÈLE ET DES ENCODEURS
# ─────────────────────────────────────────────

def sauvegarder(modele, feature_cols, abx_cols,
                le_patho, le_region, le_ref, le_target):
    print("\n💾 Sauvegarde du modèle...")

    joblib.dump(modele,      f"{MODEL_DIR}/model1_xgb.joblib")
    joblib.dump(feature_cols,f"{MODEL_DIR}/model1_features.joblib")
    joblib.dump(abx_cols,    f"{MODEL_DIR}/model1_abx_cols.joblib")
    joblib.dump(le_patho,    f"{MODEL_DIR}/model1_le_patho.joblib")
    joblib.dump(le_region,   f"{MODEL_DIR}/model1_le_region.joblib")
    joblib.dump(le_ref,      f"{MODEL_DIR}/model1_le_ref.joblib")
    joblib.dump(le_target,   f"{MODEL_DIR}/model1_le_target.joblib")

    print(f"  ✅ Modèle sauvegardé dans : {MODEL_DIR}")
    print(f"  ✅ Fichiers créés :")
    for f in os.listdir(MODEL_DIR):
        taille = os.path.getsize(f"{MODEL_DIR}/{f}") / 1024
        print(f"     {f} ({taille:.0f} KB)")


# ─────────────────────────────────────────────
# 5. TEST DE PRÉDICTION
# ─────────────────────────────────────────────

def tester_prediction(modele, feature_cols, abx_cols,
                      le_patho, le_region, le_ref, le_target, df_taux):
    """
    Simule une recommandation pour un cas clinique réel :
    E. coli au Togo, résistante à ampicilline et ciprofloxacine
    """
    print("\n🔬 Test de prédiction — Cas clinique simulé :")
    print("   Pays     : Togo (AFRO / EUCAST)")
    print("   Pathogène: Escherichia coli")
    print("   Résistant: ampicilline (85%), ciprofloxacine (72%)")

    # Récupérer les taux moyens réels pour E. coli au Togo en 2025
    masque = (
        (df_taux["pathogene"] == "Escherichia coli") &
        (df_taux["code_pays"] == "TG") &
        (df_taux["annee"] == 2025)
    )
    df_ecoli_togo = df_taux[masque]

    # Construire le vecteur de features
    vecteur = pd.DataFrame(columns=feature_cols)
    vecteur.loc[0] = 0.0

    # Remplir avec les taux réels de la base
    for _, row in df_ecoli_togo.iterrows():
        abx = row["antibiotique"]
        if abx in feature_cols:
            vecteur.loc[0, abx] = row["taux_resistance_pct"]

    # Surcharger avec les résistances connues du cas clinique
    overrides = {
        "ampicilline": 85.0,
        "ciprofloxacine": 72.0,
    }
    for abx, taux in overrides.items():
        if abx in feature_cols:
            vecteur.loc[0, abx] = taux

    # Variables contextuelles
    try:
        vecteur.loc[0, "pathogene_enc"] = le_patho.transform(
            ["Escherichia coli"])[0]
    except:
        vecteur.loc[0, "pathogene_enc"] = 0
    try:
        vecteur.loc[0, "region_enc"] = le_region.transform(["AFRO"])[0]
    except:
        vecteur.loc[0, "region_enc"] = 0
    try:
        vecteur.loc[0, "referentiel_enc"] = le_ref.transform(["EUCAST"])[0]
    except:
        vecteur.loc[0, "referentiel_enc"] = 0
    vecteur.loc[0, "annee"] = 2025

    vecteur = vecteur.fillna(0).astype(float)

    # Prédiction Top-3
    proba    = modele.predict_proba(vecteur)[0]
    top3_idx = np.argsort(proba)[::-1][:3]

    # Filtrer uniquement les ABX pertinents pour les bactéries Gram-
    abx_gram_neg = [
        "amikacine", "amoxicilline_ac_clavulanique", "ampicilline",
        "aztreonam", "cefepime", "cefiderocol", "cefotaxime",
        "ceftazidime", "ceftriaxone", "ciprofloxacine", "colistine",
        "ertapenem", "fosfomycine", "gentamicine", "imipenem",
        "levofloxacine", "meropenem", "nitrofurantoine",
        "piperacilline_tazobactam", "tigecycline",
        "trimethoprime_sulfamethoxazole", "tobramycine"
    ]

    print("\n  💊 Recommandations ResistIA Brain 🧠 :")
    recommandations = []
    for idx in np.argsort(proba)[::-1]:
        abx_nom = le_target.classes_[idx]
        if abx_nom in abx_gram_neg:
            recommandations.append((abx_nom, proba[idx] * 100))
        if len(recommandations) == 3:
            break

    for rang, (abx_nom, confiance) in enumerate(recommandations, 1):
        print(f"     {rang}. {abx_nom:<45} (confiance : {confiance:.1f}%)")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ResistIA Brain 🧠 — Modèle 1 : Recommandation")
    print("=" * 60)

    df_taux, df_pays, df_patho = charger_donnees()

    (X, y_enc, feature_cols, le_patho,
     le_region, le_ref, le_target, abx_cols) = construire_dataset(
        df_taux, df_pays, df_patho
    )

    modele, X_test, y_test = entrainer_modele(X, y_enc, len(le_target.classes_))

    sauvegarder(modele, feature_cols, abx_cols,
                le_patho, le_region, le_ref, le_target)

    tester_prediction(modele, feature_cols, abx_cols,
                      le_patho, le_region, le_ref, le_target, df_taux)

    print("\n" + "=" * 60)
    print("  ✅ Modèle 1 terminé !")
    print("=" * 60)