"""
ResistIA v2.0 — Modèle 2 : Score de Sévérité AMR
ResistIA Brain 🧠
Calcule un score de 0 à 100 indiquant la dangerosité
d'une souche bactérienne résistante + niveau d'alerte
"""

import sys
import os
sys.path.insert(0, 'C:\\ResistIA_v2')

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import warnings
warnings.filterwarnings('ignore')

DATA_DIR  = "C:\\ResistIA_v2\\data\\synthetic"
MODEL_DIR = "C:\\ResistIA_v2\\models"

# Poids de criticité OMS par catégorie de pathogène
POIDS_CRITICITE = {
    "CRITICAL": 1.0,
    "HIGH":     0.75,
    "MEDIUM":   0.50,
}

# Poids des antibiotiques de dernier recours
ABX_DERNIERE_LIGNE = [
    "imipenem", "meropenem", "colistine", "vancomycine",
    "linezolide", "daptomycine", "tigecycline", "cefiderocol",
    "bedaquiline", "delamanid"
]


# ─────────────────────────────────────────────
# 1. CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────

def charger_donnees():
    print("\n📂 Chargement des données...")

    df_taux  = pd.read_csv(f"{DATA_DIR}/taux_resistance_mondiaux.csv")
    df_patho = pd.read_csv(f"{DATA_DIR}/ref_pathogenes.csv")

    print(f"  ✅ Taux de résistance : {len(df_taux):,} lignes")
    print(f"  ✅ Pathogènes         : {len(df_patho)}")

    return df_taux, df_patho


# ─────────────────────────────────────────────
# 2. CALCUL DU SCORE DE SÉVÉRITÉ
# ─────────────────────────────────────────────

def calculer_score_severite(df_taux, df_patho):
    """
    Score de sévérité = combinaison pondérée de :
    1. Taux de résistance moyen toutes classes
    2. Taux de résistance aux antibiotiques de dernier recours
    3. Criticité OMS du pathogène
    4. Nombre d'antibiotiques avec résistance > 50%
    """
    print("\n🧮 Calcul des scores de sévérité...")

    # Fusionner avec les infos pathogènes
    df = df_taux.merge(
        df_patho[["nom_scientifique","classification_who","eskape"]],
        left_on="pathogene", right_on="nom_scientifique", how="left"
    )

    # Pivot : une ligne par pays-pathogène-année
    df_pivot = df.pivot_table(
        index=["code_pays","pathogene","region_oms",
               "referentiel","annee"],
        columns="antibiotique",
        values="taux_resistance_pct",
        aggfunc="mean"
    ).reset_index()

    # Rajouter classification_who et eskape après le pivot
    infos_patho = df_patho[["nom_scientifique",
                             "classification_who","eskape"]].drop_duplicates()
    df_pivot = df_pivot.merge(
        infos_patho, left_on="pathogene",
        right_on="nom_scientifique", how="left"
    ).drop(columns=["nom_scientifique"])

    df_pivot["classification_who"] = df_pivot["classification_who"].fillna("MEDIUM")
    df_pivot["eskape"] = df_pivot["eskape"].fillna(False)

    abx_cols = [c for c in df_pivot.columns
                if c not in ["code_pays","pathogene","region_oms",
                             "referentiel","annee",
                             "classification_who","eskape"]]

    df_pivot[abx_cols] = df_pivot[abx_cols].fillna(
        df_pivot[abx_cols].median()
    )

    # Composante 1 : taux moyen de résistance (0-100)
    df_pivot["score_resistance_moy"] = df_pivot[abx_cols].mean(axis=1)

    # Composante 2 : résistance aux ABX de dernier recours
    abx_dl = [a for a in ABX_DERNIERE_LIGNE if a in abx_cols]
    df_pivot["score_derniere_ligne"] = df_pivot[abx_dl].mean(axis=1)

    # Composante 3 : criticité OMS
    df_pivot["poids_criticite"] = df_pivot["classification_who"].map(
        POIDS_CRITICITE
    ).fillna(0.5)

    # Composante 4 : nombre d'ABX avec résistance > 50%
    df_pivot["nb_abx_resistants"] = (
        df_pivot[abx_cols] > 50
    ).sum(axis=1)
    nb_max = df_pivot["nb_abx_resistants"].max()
    df_pivot["score_nb_resistants"] = (
        df_pivot["nb_abx_resistants"] / nb_max * 100
    )

    # Composante 5 : bonus ESKAPE
    df_pivot["bonus_eskape"] = df_pivot["eskape"].apply(
        lambda x: 10 if x else 0
    )

    # Score final pondéré (0-100)
    df_pivot["score_severite"] = (
        df_pivot["score_resistance_moy"]   * 0.35 +
        df_pivot["score_derniere_ligne"]   * 0.30 +
        df_pivot["poids_criticite"] * 100  * 0.20 +
        df_pivot["score_nb_resistants"]    * 0.10 +
        df_pivot["bonus_eskape"]           * 0.05
    ).clip(0, 100).round(1)

    # Niveau d'alerte
    def niveau_alerte(score):
        if score >= 60: return "ROUGE"
        elif score >= 30: return "ORANGE"
        else: return "VERT"

    df_pivot["niveau_alerte"] = df_pivot["score_severite"].apply(
        niveau_alerte
    )

    print(f"  ✅ Dataset : {len(df_pivot):,} exemples")
    print(f"\n  📊 Distribution des niveaux d'alerte :")
    dist = df_pivot["niveau_alerte"].value_counts()
    for niveau, count in dist.items():
        pct = count / len(df_pivot) * 100
        print(f"     {niveau:<8} : {count:,} ({pct:.1f}%)")

    return df_pivot, abx_cols

# ─────────────────────────────────────────────
# 3. CONSTRUCTION DU DATASET ET ENTRAÎNEMENT
# ─────────────────────────────────────────────

def entrainer_modele(df_pivot, abx_cols):
    print("\n🤖 Entraînement du modèle XGBoost Regressor...")

    # Encodeurs
    le_patho  = LabelEncoder()
    le_region = LabelEncoder()
    le_ref    = LabelEncoder()
    le_who    = LabelEncoder()

    df_pivot["pathogene_enc"]       = le_patho.fit_transform(df_pivot["pathogene"])
    df_pivot["region_enc"]          = le_region.fit_transform(df_pivot["region_oms"])
    df_pivot["referentiel_enc"]     = le_ref.fit_transform(df_pivot["referentiel"])
    df_pivot["classification_enc"]  = le_who.fit_transform(
        df_pivot["classification_who"].fillna("MEDIUM")
    )
    df_pivot["eskape_enc"] = df_pivot["eskape"].astype(int)

    feature_cols = (abx_cols +
                    ["pathogene_enc","region_enc","referentiel_enc",
                     "classification_enc","eskape_enc","annee"])

    X = df_pivot[feature_cols]
    y = df_pivot["score_severite"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modele = XGBRegressor(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )

    modele.fit(X_train, y_train,
               eval_set=[(X_test, y_test)],
               verbose=False)

    y_pred = modele.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    r2     = r2_score(y_test, y_pred)

    print(f"\n  📊 Résultats :")
    print(f"     MAE (erreur moyenne) : {mae:.2f} points")
    print(f"     R² (qualité du fit)  : {r2:.4f}")
    print(f"     Exemples test        : {len(y_test):,}")

    return modele, feature_cols, le_patho, le_region, le_ref, le_who


# ─────────────────────────────────────────────
# 4. SAUVEGARDE
# ─────────────────────────────────────────────

def sauvegarder(modele, feature_cols, abx_cols,
                le_patho, le_region, le_ref, le_who):
    print("\n💾 Sauvegarde du modèle...")

    joblib.dump(modele,       f"{MODEL_DIR}/model2_xgb.joblib")
    joblib.dump(feature_cols, f"{MODEL_DIR}/model2_features.joblib")
    joblib.dump(abx_cols,     f"{MODEL_DIR}/model2_abx_cols.joblib")
    joblib.dump(le_patho,     f"{MODEL_DIR}/model2_le_patho.joblib")
    joblib.dump(le_region,    f"{MODEL_DIR}/model2_le_region.joblib")
    joblib.dump(le_ref,       f"{MODEL_DIR}/model2_le_ref.joblib")
    joblib.dump(le_who,       f"{MODEL_DIR}/model2_le_who.joblib")

    print(f"  ✅ Modèle sauvegardé dans : {MODEL_DIR}")


# ─────────────────────────────────────────────
# 5. TEST DE PRÉDICTION
# ─────────────────────────────────────────────

def tester_prediction(modele, feature_cols, abx_cols,
                      le_patho, le_region, le_ref, le_who, df_taux):
    print("\n🔬 Tests de prédiction — 3 cas cliniques :")

    cas = [
        {
            "label":    "K. pneumoniae résistante aux carbapénèmes — Grèce",
            "pathogene":"Klebsiella pneumoniae",
            "region":   "EURO",
            "ref":      "EUCAST",
            "who":      "CRITICAL",
            "eskape":   1,
            "annee":    2025,
            "resistances": {
                "imipenem": 85, "meropenem": 82,
                "ciprofloxacine": 90, "gentamicine": 78,
                "ceftriaxone": 98, "amikacine": 45,
            }
        },
        {
            "label":    "E. coli — infection urinaire simple — Togo",
            "pathogene":"Escherichia coli",
            "region":   "AFRO",
            "ref":      "EUCAST",
            "who":      "HIGH",
            "eskape":   0,
            "annee":    2025,
            "resistances": {
                "ampicilline": 65, "ciprofloxacine": 42,
                "trimethoprime_sulfamethoxazole": 55,
                "ceftriaxone": 12, "imipenem": 2,
            }
        },
        {
            "label":    "Candida auris — infection systémique — Inde",
            "pathogene":"Candida auris",
            "region":   "SEARO",
            "ref":      "CLSI",
            "who":      "CRITICAL",
            "eskape":   0,
            "annee":    2025,
            "resistances": {
                "fluconazole": 95, "voriconazole": 45,
                "caspofungine": 12, "amphotericine_b": 8,
            }
        },
    ]

    for cas_test in cas:
        vecteur = pd.DataFrame(columns=feature_cols)
        vecteur.loc[0] = 0.0

        # Remplir les résistances
        for abx, taux in cas_test["resistances"].items():
            if abx in feature_cols:
                vecteur.loc[0, abx] = float(taux)

        # Variables contextuelles
        try:
            vecteur.loc[0,"pathogene_enc"] = le_patho.transform(
                [cas_test["pathogene"]])[0]
        except: pass
        try:
            vecteur.loc[0,"region_enc"] = le_region.transform(
                [cas_test["region"]])[0]
        except: pass
        try:
            vecteur.loc[0,"referentiel_enc"] = le_ref.transform(
                [cas_test["ref"]])[0]
        except: pass
        try:
            vecteur.loc[0,"classification_enc"] = le_who.transform(
                [cas_test["who"]])[0]
        except: pass

        vecteur.loc[0,"eskape_enc"] = float(cas_test["eskape"])
        vecteur.loc[0,"annee"]      = float(cas_test["annee"])
        vecteur = vecteur.fillna(0.0).astype(float)

        score = modele.predict(vecteur)[0]
        score = round(float(np.clip(score, 0, 100)), 1)

        if score >= 60:   alerte = "🔴 ROUGE"
        elif score >= 30: alerte = "🟡 ORANGE"
        else:             alerte = "🟢 VERT"

        print(f"\n  Cas : {cas_test['label']}")
        print(f"     Score de sévérité : {score}/100")
        print(f"     Niveau d'alerte   : {alerte}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ResistIA Brain 🧠 — Modèle 2 : Score de Sévérité")
    print("=" * 60)

    df_taux, df_patho = charger_donnees()

    df_pivot, abx_cols = calculer_score_severite(df_taux, df_patho)

    (modele, feature_cols, le_patho,
     le_region, le_ref, le_who) = entrainer_modele(df_pivot, abx_cols)

    sauvegarder(modele, feature_cols, abx_cols,
                le_patho, le_region, le_ref, le_who)

    tester_prediction(modele, feature_cols, abx_cols,
                      le_patho, le_region, le_ref, le_who, df_taux)

    print("\n" + "=" * 60)
    print("  ✅ Modèle 2 terminé !")
    print("=" * 60)