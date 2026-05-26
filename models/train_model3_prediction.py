"""
ResistIA v2.0 — Modèle 3 : Antibiogramme Prédictif
ResistIA Brain 🧠
Prédit le profil S/I/R probable d'une bactérie AVANT
les résultats du laboratoire, basé sur le contexte
clinique et épidémiologique
"""

import sys
import os
sys.path.insert(0, 'C:\\ResistIA_v2')

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

DATA_DIR  = "C:\\ResistIA_v2\\data\\synthetic"
MODEL_DIR = "C:\\ResistIA_v2\\models"


# ─────────────────────────────────────────────
# 1. CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────

def charger_donnees():
    print("\n📂 Chargement des données...")

    df_taux  = pd.read_csv(f"{DATA_DIR}/taux_resistance_mondiaux.csv")
    df_patho = pd.read_csv(f"{DATA_DIR}/ref_pathogenes.csv")
    df_abx   = pd.read_csv(f"{DATA_DIR}/ref_antibiotiques.csv")

    print(f"  ✅ Taux de résistance : {len(df_taux):,} lignes")
    print(f"  ✅ Pathogènes         : {len(df_patho)}")
    print(f"  ✅ Antibiotiques      : {len(df_abx)}")

    return df_taux, df_patho, df_abx


# ─────────────────────────────────────────────
# 2. CONSTRUCTION DU DATASET
# ─────────────────────────────────────────────

def construire_dataset(df_taux, df_patho, df_abx):
    """
    Pour chaque combinaison pays-pathogène-antibiotique-année,
    on prédit si le résultat sera S, I ou R
    en utilisant uniquement le contexte (pas les résultats du labo)
    """
    print("\n🔧 Construction du dataset d'entraînement...")

    # Encodeurs
    le_patho  = LabelEncoder()
    le_region = LabelEncoder()
    le_ref    = LabelEncoder()
    le_abx    = LabelEncoder()
    le_sir    = LabelEncoder()

    df = df_taux.copy()

    
    # classification_who et categorie existent déjà dans df_taux
    # On merge uniquement eskape et gram qui sont absents
    df_patho_slim = df_patho[["nom_scientifique","eskape","gram"]].rename(
        columns={"nom_scientifique":"pathogene"}
    ).drop_duplicates(subset=["pathogene"])

    df = df_taux.merge(df_patho_slim, on="pathogene", how="left")

    df["classification_who"] = df["classification_who"].fillna("MEDIUM")
    df["eskape"]             = df["eskape"].fillna(False)
    df["gram"]               = df["gram"].fillna("non_applicable")
    df["categorie"]          = df["categorie"].fillna("GRAM_NEG")

    # Convertir le taux de résistance en S/I/R
    def taux_vers_sir(taux):
        if taux >= 50:   return "R"
        elif taux >= 20: return "I"
        else:            return "S"

    df["sir"] = df["taux_resistance_pct"].apply(taux_vers_sir)

    # Ajouter infos antibiotiques
    df = df.merge(
        df_abx[["nom_dci","classe","spectre",
                "derniere_ligne","nouvelle_molecule"]],
        left_on="antibiotique", right_on="nom_dci", how="left"
    ).drop(columns=["nom_dci"])

    # Encoder toutes les variables
    df["pathogene_enc"]  = le_patho.fit_transform(df["pathogene"])
    df["region_enc"]     = le_region.fit_transform(df["region_oms"])
    df["referentiel_enc"]= le_ref.fit_transform(df["referentiel"])
    df["abx_enc"]        = le_abx.fit_transform(df["antibiotique"])
    df["who_enc"]        = df["classification_who"].map(
        {"CRITICAL":2,"HIGH":1,"MEDIUM":0}
    ).fillna(0)
    df["eskape_enc"]     = df["eskape"].fillna(False).astype(int)
    df["gram_enc"]       = df["gram"].map(
        {"negatif":0,"positif":1,"variable":2,"non_applicable":3}
    ).fillna(0)
    df["categorie_enc"]  = LabelEncoder().fit_transform(
        df["categorie"].fillna("GRAM_NEG")
    )
    df["classe_enc"]     = LabelEncoder().fit_transform(
        df["classe"].fillna("AUTRE")
    )
    df["spectre_enc"]    = df["spectre"].map(
        {"etroit":0,"intermediaire":1,"large":2}
    ).fillna(1)
    df["derniere_ligne_enc"]   = df["derniere_ligne"].fillna(False).astype(int)
    df["nouvelle_molecule_enc"]= df["nouvelle_molecule"].fillna(False).astype(int)

    # Features contextuelles uniquement (pas les résultats labo)
    feature_cols = [
        "pathogene_enc","region_enc","referentiel_enc",
        "abx_enc","who_enc","eskape_enc","gram_enc",
        "categorie_enc","classe_enc","spectre_enc",
        "derniere_ligne_enc","nouvelle_molecule_enc","annee"
    ]

    X = df[feature_cols]
    y = le_sir.fit_transform(df["sir"])

    print(f"  ✅ Dataset    : {len(X):,} exemples")
    print(f"  ✅ Features   : {len(feature_cols)}")
    print(f"  ✅ Classes    : {list(le_sir.classes_)}")

    dist = pd.Series(df["sir"]).value_counts()
    print(f"\n  📊 Distribution S/I/R :")
    for sir, count in dist.items():
        pct = count/len(df)*100
        print(f"     {sir} : {count:,} ({pct:.1f}%)")

    return (X, y, feature_cols, le_patho, le_region,
            le_ref, le_abx, le_sir)

# ─────────────────────────────────────────────
# 3. ENTRAÎNEMENT
# ─────────────────────────────────────────────

def entrainer_modele(X, y):
    print("\n🤖 Entraînement du modèle Ensemble (XGBoost + LightGBM + RandomForest)...")

    from sklearn.ensemble import RandomForestClassifier, VotingClassifier
    from lightgbm import LGBMClassifier

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Modèle 1 : XGBoost
    xgb = XGBClassifier(
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

    # Modèle 2 : LightGBM
    lgbm = LGBMClassifier(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )

    # Modèle 3 : Random Forest
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )

    # Ensemble par vote pondéré
    ensemble = VotingClassifier(
        estimators=[
            ("xgb",  xgb),
            ("lgbm", lgbm),
            ("rf",   rf),
        ],
        voting="soft",       # vote par probabilités
        weights=[3, 3, 2],   # XGB et LGBM ont plus de poids
        n_jobs=-1
    )

    print("  ⏳ Entraînement en cours (3 modèles)...")
    ensemble.fit(X_train, y_train)

    y_pred  = ensemble.predict(X_test)
    y_proba = ensemble.predict_proba(X_test)
    acc     = accuracy_score(y_test, y_pred)

    print(f"\n  📊 Résultats Ensemble :")
    print(f"     Accuracy : {acc*100:.1f}%")
    print(f"     Exemples test : {len(y_test):,}")
    print(f"\n  📋 Rapport détaillé :")
    print(classification_report(y_test, y_pred,
                                target_names=["I","R","S"]))

    return ensemble, X_test, y_test


# ─────────────────────────────────────────────
# 4. SAUVEGARDE
# ─────────────────────────────────────────────

def sauvegarder(modele, feature_cols, le_patho, le_region,
                le_ref, le_abx, le_sir):
    print("\n💾 Sauvegarde du modèle...")

    joblib.dump(modele,       f"{MODEL_DIR}/model3_xgb.joblib")
    joblib.dump(feature_cols, f"{MODEL_DIR}/model3_features.joblib")
    joblib.dump(le_patho,     f"{MODEL_DIR}/model3_le_patho.joblib")
    joblib.dump(le_region,    f"{MODEL_DIR}/model3_le_region.joblib")
    joblib.dump(le_ref,       f"{MODEL_DIR}/model3_le_ref.joblib")
    joblib.dump(le_abx,       f"{MODEL_DIR}/model3_le_abx.joblib")
    joblib.dump(le_sir,       f"{MODEL_DIR}/model3_le_sir.joblib")

    print(f"  ✅ Modèle sauvegardé dans : {MODEL_DIR}")


# ─────────────────────────────────────────────
# 5. TEST DE PRÉDICTION
# ─────────────────────────────────────────────

def tester_prediction(modele, feature_cols, le_patho,
                      le_region, le_ref, le_abx, le_sir):
    print("\n🔬 Test — Antibiogramme prédictif avant résultats labo :")
    print("   Contexte : Patient en sepsis — Hôpital de Lomé")
    print("   Suspicion : Klebsiella pneumoniae (hémoculture en cours)")
    print("   Région    : AFRO / EUCAST / 2025")

    antibiotiques_tester = [
        "ceftriaxone", "imipenem", "meropenem",
        "ciprofloxacine", "gentamicine", "amikacine",
        "colistine", "tigecycline"
    ]

    print(f"\n  💊 Profil de résistance prédit :")
    print(f"  {'Antibiotique':<35} {'SIR prédit':<12} {'Confiance'}")
    print(f"  {'-'*60}")

    for abx in antibiotiques_tester:
        vecteur = pd.DataFrame([{col: 0 for col in feature_cols}])
        vecteur = vecteur.astype(float)

        try:
            vecteur["pathogene_enc"] = float(
                le_patho.transform(["Klebsiella pneumoniae"])[0])
        except: pass
        try:
            vecteur["region_enc"] = float(
                le_region.transform(["AFRO"])[0])
        except: pass
        try:
            vecteur["referentiel_enc"] = float(
                le_ref.transform(["EUCAST"])[0])
        except: pass
        try:
            vecteur["abx_enc"] = float(
                le_abx.transform([abx])[0])
        except: pass

        vecteur["who_enc"]    = 2.0  # CRITICAL
        vecteur["eskape_enc"] = 1.0  # ESKAPE
        vecteur["gram_enc"]   = 0.0  # negatif
        vecteur["annee"]      = 2025.0

        proba  = modele.predict_proba(vecteur)[0]
        pred   = le_sir.classes_[np.argmax(proba)]
        conf   = np.max(proba) * 100

        emoji = {"R":"🔴","I":"🟡","S":"🟢"}.get(pred,"⚪")
        print(f"  {abx:<35} {emoji} {pred:<10} {conf:.1f}%")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ResistIA Brain 🧠 — Modèle 3 : Antibiogramme Prédictif")
    print("=" * 60)

    df_taux, df_patho, df_abx = charger_donnees()

    (X, y, feature_cols, le_patho, le_region,
     le_ref, le_abx, le_sir) = construire_dataset(
        df_taux, df_patho, df_abx
    )

    modele, X_test, y_test = entrainer_modele(X, y)

    sauvegarder(modele, feature_cols, le_patho, le_region,
                le_ref, le_abx, le_sir)

    tester_prediction(modele, feature_cols, le_patho,
                      le_region, le_ref, le_abx, le_sir)

    print("\n" + "=" * 60)
    print("  ✅ Modèle 3 terminé !")
    print("=" * 60)