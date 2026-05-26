"""
ResistIA Brain — Chargeur de modèles
Charge tous les modèles joblib en mémoire au démarrage
"""

import joblib
import os
import numpy as np
from pathlib import Path

# Chemin vers les modèles entraînés
MODELS_DIR = Path(__file__).parent.parent.parent / "models"

def load_model(filename: str):
    """Charge un modèle joblib avec gestion d'erreur"""
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

# ── Chargement de tous les modèles ───────────────────
print("\n🧠 ResistIA Brain — Chargement des modèles...\n")

M1_RECOMMANDATION = load_model("recommendation/model_recommendation.joblib")
M1_LABEL_ENCODER  = load_model("recommendation/label_encoder.joblib")
M1_SCALER         = load_model("recommendation/scaler.joblib")

M2_SEVERITE       = load_model("severite/model_severite.joblib")
M2_SCALER         = load_model("severite/scaler_severite.joblib")

M3_PREDICTION     = load_model("prediction/model_prediction.joblib")
M3_SCALER         = load_model("prediction/scaler_prediction.joblib")
M3_LABEL_ENC      = load_model("prediction/label_encoder_prediction.joblib")

M4_ANOMALIES      = load_model("anomalies/model_anomalies.joblib")
M4_SCALER         = load_model("anomalies/scaler_anomalies.joblib")

M6_VECTORIZER     = load_model("assistant/tfidf_vectorizer.joblib")
M6_CLASSIFIER     = load_model("assistant/classifier_assistant.joblib")

M7_DRUG_L1        = load_model("drug_discovery/model_drug_l1.joblib")
M8_DRUG_L2        = load_model("drug_discovery/model_drug_l2.joblib")
M9_DRUG_L3        = load_model("drug_discovery/model_drug_l3.joblib")

M10_SIMBIO        = load_model("simbio/model_simbio.joblib")
M10_MODIFICATEURS = load_model("simbio/modificateurs_194pays.joblib")

print("\n🚀 ResistIA Brain prêt !\n")