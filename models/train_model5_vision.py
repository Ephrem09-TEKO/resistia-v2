"""
ResistIA v2.0 — Modèle 5 : Lecteur de Boîte de Pétri
ResistIA Brain 🧠
Analyse une photo de boîte de Pétri, détecte les disques
antibiotiques, mesure les zones d'inhibition et classe S/I/R
"""

import sys
import os
sys.path.insert(0, 'C:\\ResistIA_v2')

import numpy as np
import pandas as pd
import joblib
import cv2
from PIL import Image, ImageDraw, ImageFont
from skimage import measure, morphology, color
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

DATA_DIR  = "C:\\ResistIA_v2\\data\\synthetic"
MODEL_DIR = "C:\\ResistIA_v2\\models"
os.makedirs(f"{MODEL_DIR}/vision", exist_ok=True)

# ─────────────────────────────────────────────────────────────
# BREAKPOINTS EUCAST 2024 — Diamètre zones d'inhibition (mm)
# Format : {antibiotique: (seuil_S, seuil_R)}
# S si diamètre >= seuil_S
# R si diamètre < seuil_R
# I si entre les deux
# ─────────────────────────────────────────────────────────────
BREAKPOINTS_EUCAST = {
    "ampicilline":                    (14, 14),
    "amoxicilline_ac_clavulanique":   (19, 19),
    "piperacilline_tazobactam":       (18, 18),
    "cefotaxime":                     (20, 17),
    "ceftriaxone":                    (20, 17),
    "ceftazidime":                    (19, 16),
    "cefepime":                       (21, 18),
    "imipenem":                       (22, 16),
    "meropenem":                      (22, 16),
    "ertapenem":                      (22, 19),
    "ciprofloxacine":                 (25, 22),
    "levofloxacine":                  (20, 17),
    "gentamicine":                    (15, 15),
    "amikacine":                      (18, 15),
    "tobramycine":                    (18, 15),
    "trimethoprime_sulfamethoxazole": (14, 11),
    "vancomycine":                    (12, 12),
    "linezolide":                     (21, 21),
    "colistine":                      (11, 11),
    "oxacilline":                     (22, 22),
    "azithromycine":                  (18, 14),
    "erythromycine":                  (22, 18),
    "clindamycine":                   (19, 19),
    "tetracycline":                   (18, 15),
    "doxycycline":                    (20, 17),
    "rifampicine":                    (20, 17),
    "nitrofurantoine":                (15, 12),
    "fosfomycine":                    (16, 13),
    "chloramphenicol":                (18, 18),
}

BREAKPOINTS_CLSI = {
    "ampicilline":                    (17, 14),
    "amoxicilline_ac_clavulanique":   (18, 14),
    "piperacilline_tazobactam":       (21, 18),
    "cefotaxime":                     (26, 23),
    "ceftriaxone":                    (23, 20),
    "ceftazidime":                    (18, 15),
    "cefepime":                       (18, 15),
    "imipenem":                       (23, 20),
    "meropenem":                      (23, 20),
    "ciprofloxacine":                 (21, 16),
    "levofloxacine":                  (19, 16),
    "gentamicine":                    (15, 13),
    "amikacine":                      (17, 15),
    "trimethoprime_sulfamethoxazole": (16, 11),
    "vancomycine":                    (15, 15),
    "linezolide":                     (21, 21),
    "oxacilline":                     (13, 13),
    "azithromycine":                  (18, 14),
    "erythromycine":                  (23, 14),
    "tetracycline":                   (19, 15),
    "nitrofurantoine":                (17, 15),
    "chloramphenicol":                (18, 13),
}


def interpreter_sir(diametre_mm, antibiotique, referentiel="EUCAST"):
    """
    Interprète un diamètre de zone d'inhibition en S/I/R
    selon le référentiel EUCAST ou CLSI
    """
    bp = BREAKPOINTS_EUCAST if referentiel == "EUCAST" else BREAKPOINTS_CLSI
    if antibiotique not in bp:
        # Règle générale si ABX non trouvé
        if diametre_mm >= 20: return "S"
        elif diametre_mm >= 15: return "I"
        else: return "R"

    seuil_s, seuil_r = bp[antibiotique]
    if diametre_mm >= seuil_s:  return "S"
    elif diametre_mm < seuil_r: return "R"
    else:                        return "I"

# ─────────────────────────────────────────────
# 2. SIMULATION DE DONNÉES D'ANTIBIOGRAMMES
#    (en attendant de vraies photos de boîtes)
# ─────────────────────────────────────────────

def simuler_mesures_boite(n_samples=10000):
    """
    Simule des mesures de zones d'inhibition comme si
    elles provenaient de photos de boîtes de Pétri analysées.
    Chaque enregistrement = un disque antibiotique mesuré.
    """
    print("\n🔬 Simulation des mesures de zones d'inhibition...")

    np.random.seed(42)
    antibiotiques = list(BREAKPOINTS_EUCAST.keys())
    referentiels  = ["EUCAST", "CLSI"]
    records       = []

    for _ in range(n_samples):
        abx = np.random.choice(antibiotiques)
        ref = np.random.choice(referentiels)
        bp  = BREAKPOINTS_EUCAST if ref == "EUCAST" else BREAKPOINTS_CLSI

        if abx in bp:
            seuil_s, seuil_r = bp[abx]
        else:
            seuil_s, seuil_r = 20, 15

        # Simuler le vrai SIR
        vrai_sir = np.random.choice(["S","I","R"], p=[0.55, 0.15, 0.30])

        # Simuler le diamètre selon le SIR
        if vrai_sir == "S":
            diametre = np.random.normal(seuil_s + 4, 3)
        elif vrai_sir == "I":
            diametre = np.random.normal((seuil_s + seuil_r) / 2, 2)
        else:
            diametre = np.random.normal(seuil_r - 4, 3)

        diametre = max(6.0, min(40.0, round(diametre, 1)))

        # Features de vision simulées
        # (dans la vraie app, ces features viennent de l'image)
        circularite    = np.random.normal(0.85, 0.08)  # qualité du cercle
        contraste      = np.random.normal(0.72, 0.12)  # netteté des bords
        bruit_image    = np.random.normal(0.05, 0.02)  # bruit de fond
        luminosite_moy = np.random.normal(180, 25)     # luminosité zone

        # Label = SIR interprété
        sir_predit = interpreter_sir(diametre, abx, ref)

        records.append({
            "antibiotique":    abx,
            "referentiel":     ref,
            "diametre_mm":     diametre,
            "circularite":     max(0.0, min(1.0, circularite)),
            "contraste":       max(0.0, min(1.0, contraste)),
            "bruit_image":     max(0.0, min(0.2, bruit_image)),
            "luminosite_moy":  luminosite_moy,
            "seuil_s":         seuil_s,
            "seuil_r":         seuil_r,
            "ecart_seuil_s":   diametre - seuil_s,
            "ecart_seuil_r":   diametre - seuil_r,
            "sir":             sir_predit,
            "vrai_sir":        vrai_sir,
        })

    df = pd.DataFrame(records)
    print(f"  ✅ {len(df):,} mesures simulées")
    print(f"\n  📊 Distribution SIR :")
    for sir, count in df["sir"].value_counts().items():
        print(f"     {sir} : {count:,} ({count/len(df)*100:.1f}%)")

    return df


# ─────────────────────────────────────────────
# 3. ENTRAÎNEMENT DU MODÈLE DE CLASSIFICATION
# ─────────────────────────────────────────────

def entrainer_modele(df):
    print("\n🤖 Entraînement du modèle de classification SIR...")

    le_abx = LabelEncoder()
    le_ref = LabelEncoder()
    le_sir = LabelEncoder()

    df["abx_enc"] = le_abx.fit_transform(df["antibiotique"])
    df["ref_enc"] = le_ref.fit_transform(df["referentiel"])
    y             = le_sir.fit_transform(df["sir"])

    feature_cols = [
        "abx_enc","ref_enc","diametre_mm",
        "circularite","contraste","bruit_image",
        "luminosite_moy","seuil_s","seuil_r",
        "ecart_seuil_s","ecart_seuil_r"
    ]

    X = df[feature_cols]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modele = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    modele.fit(X_train, y_train)

    y_pred = modele.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)

    print(f"\n  📊 Résultats :")
    print(f"     Accuracy : {acc*100:.1f}%")
    print(f"     Exemples test : {len(y_test):,}")
    print(f"\n  📋 Rapport détaillé :")
    print(classification_report(y_test, y_pred,
                                target_names=le_sir.classes_))

    return modele, feature_cols, le_abx, le_ref, le_sir


# ─────────────────────────────────────────────
# 4. GÉNÉRATEUR D'IMAGE TEST (boîte de Pétri simulée)
# ─────────────────────────────────────────────

def generer_image_test():
    """
    Génère une image simulée de boîte de Pétri
    avec 6 disques antibiotiques et leurs zones d'inhibition
    """
    print("\n🎨 Génération d'une image test de boîte de Pétri...")

    # Créer image circulaire (boîte de Pétri)
    taille = 600
    img    = np.ones((taille, taille, 3), dtype=np.uint8) * 240

    # Fond de la boîte (gélosa)
    cv2.circle(img, (300, 300), 270, (220, 200, 160), -1)
    cv2.circle(img, (300, 300), 270, (100, 80, 50), 3)

    # 6 disques antibiotiques avec zones d'inhibition différentes
    disques = [
        {"pos": (160, 160), "rayon_zone": 55, "rayon_disque": 15,
         "abx": "ceftriaxone",   "sir": "S", "diametre": 28.0},
        {"pos": (300, 120), "rayon_zone": 35, "abx": "ciprofloxacine",
         "sir": "I", "diametre": 20.0, "rayon_disque": 15},
        {"pos": (440, 160), "rayon_zone": 18, "abx": "ampicilline",
         "sir": "R", "diametre": 10.0, "rayon_disque": 15},
        {"pos": (160, 440), "rayon_zone": 60, "abx": "imipenem",
         "sir": "S", "diametre": 32.0, "rayon_disque": 15},
        {"pos": (300, 470), "rayon_zone": 25, "abx": "gentamicine",
         "sir": "I", "diametre": 17.0, "rayon_disque": 15},
        {"pos": (440, 440), "rayon_zone": 45, "abx": "colistine",
         "sir": "S", "diametre": 24.0, "rayon_disque": 15},
    ]

    for d in disques:
        # Zone d'inhibition (claire)
        cv2.circle(img, d["pos"], d["rayon_zone"], (245, 240, 220), -1)
        cv2.circle(img, d["pos"], d["rayon_zone"], (180, 160, 120), 2)
        # Disque antibiotique (foncé)
        cv2.circle(img, d["pos"], d["rayon_disque"], (40, 40, 80), -1)
        cv2.circle(img, d["pos"], d["rayon_disque"], (20, 20, 60), 2)

    # Sauvegarder
    img_path = f"{MODEL_DIR}/vision/test_petri.png"
    cv2.imwrite(img_path, img)
    print(f"  ✅ Image sauvegardée : {img_path}")

    return img, disques


# ─────────────────────────────────────────────
# 5. ANALYSE D'UNE IMAGE (pipeline complet)
# ─────────────────────────────────────────────

def analyser_image(modele, feature_cols, le_abx, le_ref,
                   le_sir, disques_test, referentiel="EUCAST"):
    """
    Simule l'analyse complète d'une boîte de Pétri :
    mesure des diamètres + classification S/I/R
    """
    print(f"\n📸 Analyse de la boîte de Pétri ({referentiel}) :")
    print(f"  {'Antibiotique':<30} {'Diamètre':>10} {'SIR':>6} {'Confiance':>10}")
    print(f"  {'-'*60}")

    resultats = []
    for d in disques_test:
        abx      = d["abx"]
        diametre = d["diametre"]

        # Calculer les seuils
        bp = BREAKPOINTS_EUCAST if referentiel == "EUCAST" else BREAKPOINTS_CLSI
        seuil_s, seuil_r = bp.get(abx, (20, 15))

        # Construire le vecteur
        try:
            abx_enc = le_abx.transform([abx])[0]
        except:
            abx_enc = 0
        try:
            ref_enc = le_ref.transform([referentiel])[0]
        except:
            ref_enc = 0

        vecteur = pd.DataFrame([{
            "abx_enc":       float(abx_enc),
            "ref_enc":       float(ref_enc),
            "diametre_mm":   diametre,
            "circularite":   0.88,
            "contraste":     0.75,
            "bruit_image":   0.04,
            "luminosite_moy":182.0,
            "seuil_s":       float(seuil_s),
            "seuil_r":       float(seuil_r),
            "ecart_seuil_s": diametre - seuil_s,
            "ecart_seuil_r": diametre - seuil_r,
        }])

        proba    = modele.predict_proba(vecteur)[0]
        pred_enc = np.argmax(proba)
        pred_sir = le_sir.classes_[pred_enc]
        confiance= np.max(proba) * 100

        emoji = {"R":"🔴","I":"🟡","S":"🟢"}.get(pred_sir,"⚪")
        print(f"  {abx:<30} {diametre:>8.1f}mm "
              f"  {emoji}{pred_sir:>4}   {confiance:>8.1f}%")

        resultats.append({
            "antibiotique": abx,
            "diametre_mm":  diametre,
            "sir":          pred_sir,
            "confiance":    confiance
        })

    return resultats


# ─────────────────────────────────────────────
# 6. SAUVEGARDE
# ─────────────────────────────────────────────

def sauvegarder(modele, feature_cols, le_abx, le_ref, le_sir):
    print("\n💾 Sauvegarde du modèle...")

    joblib.dump(modele,       f"{MODEL_DIR}/model5_rf.joblib")
    joblib.dump(feature_cols, f"{MODEL_DIR}/model5_features.joblib")
    joblib.dump(le_abx,       f"{MODEL_DIR}/model5_le_abx.joblib")
    joblib.dump(le_ref,       f"{MODEL_DIR}/model5_le_ref.joblib")
    joblib.dump(le_sir,       f"{MODEL_DIR}/model5_le_sir.joblib")
    joblib.dump(BREAKPOINTS_EUCAST, f"{MODEL_DIR}/model5_bp_eucast.joblib")
    joblib.dump(BREAKPOINTS_CLSI,   f"{MODEL_DIR}/model5_bp_clsi.joblib")

    print(f"  ✅ Modèle sauvegardé dans : {MODEL_DIR}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ResistIA Brain 🧠 — Modèle 5 : Vision IA Boîte de Pétri")
    print("=" * 60)

    df = simuler_mesures_boite(n_samples=15000)

    modele, feature_cols, le_abx, le_ref, le_sir = entrainer_modele(df)

    sauvegarder(modele, feature_cols, le_abx, le_ref, le_sir)

    img, disques_test = generer_image_test()

    analyser_image(modele, feature_cols, le_abx, le_ref,
                   le_sir, disques_test, referentiel="EUCAST")

    print("\n" + "=" * 60)
    print("  ✅ Modèle 5 terminé !")
    print("=" * 60)
