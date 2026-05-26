"""
ResistIA v2.0 — Modèle 4 : Détection d'Anomalies
ResistIA Brain 🧠
Détecte automatiquement les profils de résistance inhabituels :
- Erreur de laboratoire (saisie incorrecte)
- Émergence nouvelle de résistance jamais vue
"""

import sys
import os
sys.path.insert(0, 'C:\\ResistIA_v2')

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

DATA_DIR  = "C:\\ResistIA_v2\\data\\synthetic"
MODEL_DIR = "C:\\ResistIA_v2\\models"

# Seuils d'anomalie par pathogène — résistances biologiquement impossibles
# Ex: Streptocoque A n'est JAMAIS résistant à la pénicilline
RESISTANCES_IMPOSSIBLES = {
    "Streptococcus pyogenes":  ["penicilline", "amoxicilline"],
    "Listeria monocytogenes":  ["ceftriaxone", "cefotaxime"],
    "Stenotrophomonas maltophilia": ["imipenem", "meropenem"],
}

# Seuils d'alerte : si résistance > seuil habituel + X%, c'est une anomalie
SEUIL_ANOMALIE_PCT = 25.0  # écart de 25% par rapport à la médiane mondiale


# ─────────────────────────────────────────────
# 1. CHARGEMENT
# ─────────────────────────────────────────────

def charger_donnees():
    print("\n📂 Chargement des données...")
    df_taux  = pd.read_csv(f"{DATA_DIR}/taux_resistance_mondiaux.csv")
    df_patho = pd.read_csv(f"{DATA_DIR}/ref_pathogenes.csv")
    print(f"  ✅ Taux de résistance : {len(df_taux):,} lignes")
    return df_taux, df_patho


# ─────────────────────────────────────────────
# 2. CONSTRUCTION DU DATASET AVEC LABELS ANOMALIE
# ─────────────────────────────────────────────

def construire_dataset(df_taux, df_patho):
    print("\n🔧 Construction du dataset...")

    # Calcul de la médiane mondiale par pathogène-antibiotique
    mediane_mondiale = df_taux.groupby(
        ["pathogene","antibiotique"]
    )["taux_resistance_pct"].median().reset_index()
    mediane_mondiale.columns = ["pathogene","antibiotique","mediane_mondiale"]

    df = df_taux.merge(mediane_mondiale,
                       on=["pathogene","antibiotique"], how="left")

    # Calcul de l'écart à la médiane
    df["ecart_mediane"] = abs(
        df["taux_resistance_pct"] - df["mediane_mondiale"]
    )

    # Label anomalie — 3 types
    def labelliser(row):
        patho = row["pathogene"]
        abx   = row["antibiotique"]
        taux  = row["taux_resistance_pct"]

        # Type 1 : résistance biologiquement impossible
        if patho in RESISTANCES_IMPOSSIBLES:
            if abx in RESISTANCES_IMPOSSIBLES[patho] and taux > 30:
                return 1

        # Type 2 : écart trop important à la médiane mondiale
        if row["ecart_mediane"] > SEUIL_ANOMALIE_PCT:
            return 1

        # Type 3 : résistance > 90% sur antibiotique de dernier recours
        abx_dl = ["imipenem","meropenem","colistine","vancomycine",
                  "linezolide","cefiderocol"]
        if abx in abx_dl and taux > 90:
            return 1

        return 0

    print("  ⏳ Labellisation des anomalies...")
    df["is_anomalie"] = df.apply(labelliser, axis=1)

    # Stats anomalies
    n_anomalies = df["is_anomalie"].sum()
    pct = n_anomalies / len(df) * 100
    print(f"  ✅ Anomalies détectées : {n_anomalies:,} ({pct:.1f}%)")
    print(f"  ✅ Normal             : {len(df)-n_anomalies:,} ({100-pct:.1f}%)")

    # Merger infos pathogènes
    df_patho_slim = df_patho[
        ["nom_scientifique","eskape","gram"]
    ].rename(columns={"nom_scientifique":"pathogene"})
    df = df.merge(df_patho_slim, on="pathogene", how="left")
    df["eskape"] = df["eskape"].fillna(False)
    df["gram"]   = df["gram"].fillna("non_applicable")

    # Encodeurs
    le_patho  = LabelEncoder()
    le_region = LabelEncoder()
    le_ref    = LabelEncoder()
    le_abx    = LabelEncoder()

    df["pathogene_enc"]  = le_patho.fit_transform(df["pathogene"])
    df["region_enc"]     = le_region.fit_transform(df["region_oms"])
    df["referentiel_enc"]= le_ref.fit_transform(df["referentiel"])
    df["abx_enc"]        = le_abx.fit_transform(df["antibiotique"])
    df["eskape_enc"]     = df["eskape"].astype(int)
    df["gram_enc"]       = df["gram"].map(
        {"negatif":0,"positif":1,"variable":2,"non_applicable":3}
    ).fillna(0)
    df["who_enc"]        = df["classification_who"].map(
        {"CRITICAL":2,"HIGH":1,"MEDIUM":0}
    ).fillna(0)

    feature_cols = [
        "pathogene_enc","region_enc","referentiel_enc",
        "abx_enc","eskape_enc","gram_enc","who_enc",
        "taux_resistance_pct","ecart_mediane","annee"
    ]

    X = df[feature_cols]
    y = df["is_anomalie"]

    print(f"  ✅ Features : {len(feature_cols)}")

    return X, y, feature_cols, le_patho, le_region, le_ref, le_abx, df

# ─────────────────────────────────────────────
# 3. ENTRAÎNEMENT — DEUX APPROCHES COMBINÉES
# ─────────────────────────────────────────────

def entrainer_modele(X, y):
    print("\n🤖 Entraînement du modèle de détection d'anomalies...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Approche 1 : Isolation Forest (non-supervisé)
    # Détecte les anomalies sans avoir besoin de labels
    print("  ⏳ Isolation Forest...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.05,  # on estime ~5% d'anomalies
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_train_scaled)

    # Isolation Forest retourne -1 (anomalie) ou 1 (normal)
    # On convertit en 0/1
    y_pred_iso = iso_forest.predict(X_test_scaled)
    y_pred_iso = (y_pred_iso == -1).astype(int)

    acc_iso = (y_pred_iso == y_test.values).mean()
    print(f"     Isolation Forest Accuracy : {acc_iso*100:.1f}%")

    # Approche 2 : XGBoost supervisé
    print("  ⏳ XGBoost supervisé...")

    # Gérer le déséquilibre des classes
    n_normal   = (y_train == 0).sum()
    n_anomalie = (y_train == 1).sum()
    scale_pos  = n_normal / n_anomalie if n_anomalie > 0 else 1

    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos,  # compenser le déséquilibre
        random_state=42,
        n_jobs=-1,
        verbosity=0,
        eval_metric="logloss"
    )
    xgb.fit(X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False)

    y_pred_xgb = xgb.predict(X_test)
    acc_xgb = (y_pred_xgb == y_test.values).mean()
    print(f"     XGBoost Accuracy          : {acc_xgb*100:.1f}%")

    # Combinaison des deux : vote majoritaire
    y_pred_final = ((y_pred_iso + y_pred_xgb) >= 1).astype(int)
    acc_final = (y_pred_final == y_test.values).mean()

    print(f"\n  📊 Résultats combinés :")
    print(f"     Accuracy finale : {acc_final*100:.1f}%")
    print(f"     Exemples test   : {len(y_test):,}")
    print(f"\n  📋 Rapport détaillé :")
    print(classification_report(y_test, y_pred_final,
                                target_names=["Normal","Anomalie"]))

    return xgb, iso_forest, scaler, X_test, y_test


# ─────────────────────────────────────────────
# 4. SAUVEGARDE
# ─────────────────────────────────────────────

def sauvegarder(xgb, iso_forest, scaler, feature_cols,
                le_patho, le_region, le_ref, le_abx):
    print("\n💾 Sauvegarde des modèles...")

    joblib.dump(xgb,          f"{MODEL_DIR}/model4_xgb.joblib")
    joblib.dump(iso_forest,   f"{MODEL_DIR}/model4_isoforest.joblib")
    joblib.dump(scaler,       f"{MODEL_DIR}/model4_scaler.joblib")
    joblib.dump(feature_cols, f"{MODEL_DIR}/model4_features.joblib")
    joblib.dump(le_patho,     f"{MODEL_DIR}/model4_le_patho.joblib")
    joblib.dump(le_region,    f"{MODEL_DIR}/model4_le_region.joblib")
    joblib.dump(le_ref,       f"{MODEL_DIR}/model4_le_ref.joblib")
    joblib.dump(le_abx,       f"{MODEL_DIR}/model4_le_abx.joblib")

    print(f"  ✅ Modèles sauvegardés dans : {MODEL_DIR}")


# ─────────────────────────────────────────────
# 5. TEST DE DÉTECTION
# ─────────────────────────────────────────────

def tester_detection(xgb, iso_forest, scaler,
                     feature_cols, le_patho, le_region,
                     le_ref, le_abx, df_taux):
    print("\n🔬 Tests de détection d'anomalies :")

    # Médiane mondiale pour calcul ecart
    mediane_mondiale = df_taux.groupby(
        ["pathogene","antibiotique"]
    )["taux_resistance_pct"].median().to_dict()

    cas = [
        {
            "label":    "✅ CAS NORMAL — E. coli résistante ampicilline",
            "pathogene":"Escherichia coli",
            "abx":      "ampicilline",
            "region":   "AFRO",
            "ref":      "EUCAST",
            "taux":     58.0,
            "eskape":   0, "gram": 0, "who": 1,
            "annee":    2025
        },
        {
            "label":    "🚨 ANOMALIE — K. pneumoniae résistante colistine à 95%",
            "pathogene":"Klebsiella pneumoniae",
            "abx":      "colistine",
            "region":   "EURO",
            "ref":      "EUCAST",
            "taux":     95.0,
            "eskape":   1, "gram": 0, "who": 2,
            "annee":    2025
        },
        {
            "label":    "🚨 ANOMALIE — Streptocoque A résistant pénicilline",
            "pathogene":"Streptococcus pyogenes",
            "abx":      "penicilline",
            "region":   "AMRO",
            "ref":      "CLSI",
            "taux":     45.0,
            "eskape":   0, "gram": 1, "who": 0,
            "annee":    2025
        },
        {
            "label":    "✅ CAS NORMAL — S. aureus résistant oxacilline (SARM)",
            "pathogene":"Staphylococcus aureus",
            "abx":      "oxacilline",
            "region":   "EURO",
            "ref":      "EUCAST",
            "taux":     32.0,
            "eskape":   1, "gram": 1, "who": 1,
            "annee":    2025
        },
    ]

    for cas_test in cas:
        # Calcul écart médiane
        cle = (cas_test["pathogene"], cas_test["abx"])
        mediane = mediane_mondiale.get(cle, cas_test["taux"])
        ecart   = abs(cas_test["taux"] - mediane)

        vecteur = pd.DataFrame([{col: 0.0 for col in feature_cols}])

        try:
            vecteur["pathogene_enc"] = float(
                le_patho.transform([cas_test["pathogene"]])[0])
        except: pass
        try:
            vecteur["region_enc"] = float(
                le_region.transform([cas_test["region"]])[0])
        except: pass
        try:
            vecteur["referentiel_enc"] = float(
                le_ref.transform([cas_test["ref"]])[0])
        except: pass
        try:
            vecteur["abx_enc"] = float(
                le_abx.transform([cas_test["abx"]])[0])
        except: pass

        vecteur["eskape_enc"]          = float(cas_test["eskape"])
        vecteur["gram_enc"]            = float(cas_test["gram"])
        vecteur["who_enc"]             = float(cas_test["who"])
        vecteur["taux_resistance_pct"] = float(cas_test["taux"])
        vecteur["ecart_mediane"]       = float(ecart)
        vecteur["annee"]               = float(cas_test["annee"])

        # Prédiction XGBoost
        proba_xgb = xgb.predict_proba(vecteur)[0][1]
        pred_xgb  = int(proba_xgb > 0.5)

        # Prédiction Isolation Forest
        vecteur_scaled = scaler.transform(vecteur)
        pred_iso = int(iso_forest.predict(vecteur_scaled)[0] == -1)

        # Décision finale
        pred_final = int((pred_xgb + pred_iso) >= 1)
        confiance  = proba_xgb * 100

        statut = "🚨 ANOMALIE DÉTECTÉE" if pred_final == 1 else "✅ Profil normal"

        print(f"\n  {cas_test['label']}")
        print(f"     Taux résistance : {cas_test['taux']}%")
        print(f"     Écart médiane   : {ecart:.1f}%")
        print(f"     Résultat        : {statut}")
        print(f"     Confiance XGB   : {confiance:.1f}%")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ResistIA Brain 🧠 — Modèle 4 : Détection d'Anomalies")
    print("=" * 60)

    df_taux, df_patho = charger_donnees()

    (X, y, feature_cols, le_patho, le_region,
     le_ref, le_abx, df) = construire_dataset(df_taux, df_patho)

    xgb, iso_forest, scaler, X_test, y_test = entrainer_modele(X, y)

    sauvegarder(xgb, iso_forest, scaler, feature_cols,
                le_patho, le_region, le_ref, le_abx)

    tester_detection(xgb, iso_forest, scaler, feature_cols,
                     le_patho, le_region, le_ref, le_abx, df_taux)

    print("\n" + "=" * 60)
    print("  ✅ Modèle 4 terminé !")
    print("=" * 60)