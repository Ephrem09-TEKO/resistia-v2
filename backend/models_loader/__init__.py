"""
ResistIA Brain — Chargeur de modèles
Chemins adaptés à la vraie structure C:\ResistIA_v2\models\
"""

import joblib
import os
from pathlib import Path

MODELS_DIR = Path(__file__).parent.parent / "models"

def load_model(filename: str):
    path = MODELS_DIR / filename
    if path.exists():
        try:
            model = joblib.load(path)
            print(f"✅ {filename} chargé")
            return model
        except Exception as e:
            print(f"⚠️  {filename} — erreur: {e}")
            return None
    else:
        print(f"⚠️  {filename} introuvable — mode simulation")
        return None

MODELS_DIR = Path(__file__).parent.parent / "models"

# Debug — affiche le chemin réel au démarrage
print(f"📂 MODELS_DIR = {MODELS_DIR}")
print(f"📂 Existe: {MODELS_DIR.exists()}")
if MODELS_DIR.exists():
    fichiers = list(MODELS_DIR.rglob("*.joblib"))
    print(f"📂 {len(fichiers)} fichiers .joblib trouvés")
    for f in fichiers[:5]:
        print(f"   → {f.name}")


print("\n🧠 ResistIA Brain — Chargement des modèles...\n")

# ── Modèle 1 — Recommandation ─────────────────────────
M1_XGB         = load_model("model1_xgb.joblib")
M1_LE_PATHO    = load_model("model1_le_patho.joblib")
M1_LE_TARGET   = load_model("model1_le_target.joblib")
M1_LE_REF      = load_model("model1_le_ref.joblib")
M1_LE_REGION   = load_model("model1_le_region.joblib")
M1_ABX_COLS    = load_model("model1_abx_cols.joblib")
M1_FEATURES    = load_model("model1_features.joblib")

# ── Modèle 2 — Sévérité ──────────────────────────────
M2_XGB         = load_model("model2_xgb.joblib")
M2_LE_PATHO    = load_model("model2_le_patho.joblib")
M2_LE_REF      = load_model("model2_le_ref.joblib")
M2_LE_REGION   = load_model("model2_le_region.joblib")
M2_LE_WHO      = load_model("model2_le_who.joblib")
M2_FEATURES    = load_model("model2_features.joblib")

# ── Modèle 3 — Prédiction SIR ────────────────────────
M3_XGB         = load_model("model3_xgb.joblib")
M3_LE_PATHO    = load_model("model3_le_patho.joblib")
M3_LE_ABX      = load_model("model3_le_abx.joblib")
M3_LE_SIR      = load_model("model3_le_sir.joblib")
M3_LE_REF      = load_model("model3_le_ref.joblib")
M3_LE_REGION   = load_model("model3_le_region.joblib")
M3_FEATURES    = load_model("model3_features.joblib")

# ── Modèle 4 — Anomalies ─────────────────────────────
M4_XGB         = load_model("model4_xgb.joblib")
M4_ISOFOREST   = load_model("model4_isoforest.joblib")
M4_SCALER      = load_model("model4_scaler.joblib")
M4_LE_PATHO    = load_model("model4_le_patho.joblib")
M4_LE_ABX      = load_model("model4_le_abx.joblib")
M4_LE_REF      = load_model("model4_le_ref.joblib")
M4_LE_REGION   = load_model("model4_le_region.joblib")
M4_FEATURES    = load_model("model4_features.joblib")

# ── Modèle 5 — Vision Pétri ──────────────────────────
M5_RF          = load_model("model5_rf.joblib")
M5_LE_ABX      = load_model("model5_le_abx.joblib")
M5_LE_SIR      = load_model("model5_le_sir.joblib")
M5_LE_REF      = load_model("model5_le_ref.joblib")
M5_BP_CLSI     = load_model("model5_bp_clsi.joblib")
M5_BP_EUCAST   = load_model("model5_bp_eucast.joblib")
M5_FEATURES    = load_model("model5_features.joblib")

# ── Modèle 6 — Assistant NLP ─────────────────────────
M6_TFIDF       = load_model("model6_tfidf.joblib")
M6_VECTORIZER  = load_model("model6_vectorizer.joblib")
M6_KB          = load_model("model6_kb.joblib")

# ── Modèles 7-8-9 — Drug Discovery ───────────────────
M7_REPO        = load_model("drug_discovery/model7_repositionnement.joblib")
M7_LE_GRAM     = load_model("drug_discovery/model7_le_gram.joblib")
M7_LE_PROFIL   = load_model("drug_discovery/model7_le_profil.joblib")
M7_LE_WHO      = load_model("drug_discovery/model7_le_who.joblib")
M7_FEATURES    = load_model("drug_discovery/model7_features.joblib")

M8_MODELE_A    = load_model("drug_discovery/model8_modele_A.joblib")
M8_MODELE_B    = load_model("drug_discovery/model8_modele_B.joblib")
M8_MODELE_C    = load_model("drug_discovery/model8_modele_C.joblib")
M8_MODELE_D    = load_model("drug_discovery/model8_modele_D.joblib")
M8_SCALER      = load_model("drug_discovery/model8_scaler.joblib")
M8_FEATURES    = load_model("drug_discovery/model8_features.joblib")

M9_SCOREURS    = load_model("drug_discovery/model9_scoreurs.joblib")
M9_SCALER      = load_model("drug_discovery/model9_scaler.joblib")

# ── Modèle 10 — SimBio ───────────────────────────────
M10_EFFICACITE  = load_model("simbio/model10_efficacite.joblib")
M10_TOXICITE    = load_model("simbio/model10_toxicite.joblib")
M10_SCALER      = load_model("simbio/model10_scaler.joblib")
M10_FEATURES    = load_model("simbio/model10_features.joblib")
M10_MOD_PAYS    = load_model("simbio/mod_pays.joblib")
M10_MOD_REGION  = load_model("simbio/mod_region.joblib")
M10_PHYSIO_H    = load_model("simbio/physio_humain.joblib")
M10_PHYSIO_R    = load_model("simbio/physio_rat.joblib")
M10_PHYSIO_S    = load_model("simbio/physio_souris.joblib")
M10_STADES      = load_model("simbio/stades_infection.joblib")
M10_MODIF_194   = load_model("simbio/modificateurs_194pays.joblib")

print("\n🚀 ResistIA Brain prêt !\n")