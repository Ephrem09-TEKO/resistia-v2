"""
ResistIA v2.0 — Extension SimBio aux 194 pays
Génère automatiquement les profils physiologiques
pour les 194 pays en interpolant depuis :
- Les modificateurs régionaux OMS
- Les données de notre ref_pays.csv
- Les indicateurs de santé OMS (calibrés)
"""

import sys
import os
sys.path.insert(0, 'C:\\ResistIA_v2')

import pandas as pd
import numpy as np
import joblib

DATA_DIR  = "C:\\ResistIA_v2\\data\\synthetic"
MODEL_DIR = "C:\\ResistIA_v2\\models"

# ─────────────────────────────────────────────
# INDICATEURS DE SANTÉ PAR PROFIL DE RÉSISTANCE
# Source : calibration OMS/UNICEF/World Bank
# ─────────────────────────────────────────────

INDICATEURS_PAR_PROFIL = {
    "low": {
        "malnutrition":    0.01,
        "paludisme":       0.00,
        "tb_prevalence":   0.008,
        "vih_prevalence":  0.002,
        "acces_soins":     0.95,
        "eau_potable":     0.99,
        "esperance_vie":   80.0,
        "mortalite_inf":   0.004,
    },
    "medium": {
        "malnutrition":    0.06,
        "paludisme":       0.05,
        "tb_prevalence":   0.03,
        "vih_prevalence":  0.008,
        "acces_soins":     0.75,
        "eau_potable":     0.88,
        "esperance_vie":   73.0,
        "mortalite_inf":   0.015,
    },
    "high": {
        "malnutrition":    0.14,
        "paludisme":       0.28,
        "tb_prevalence":   0.07,
        "vih_prevalence":  0.020,
        "acces_soins":     0.52,
        "eau_potable":     0.72,
        "esperance_vie":   65.0,
        "mortalite_inf":   0.045,
    },
    "very_high": {
        "malnutrition":    0.24,
        "paludisme":       0.52,
        "tb_prevalence":   0.14,
        "vih_prevalence":  0.035,
        "acces_soins":     0.32,
        "eau_potable":     0.55,
        "esperance_vie":   58.0,
        "mortalite_inf":   0.080,
    },
}

# Modificateurs régionaux OMS (repris de SimBio)
MODIFICATEURS_REGION = {
    "AFRO":  {"immunite_baseline":0.85,"resilience_infection":0.80,
               "hemoglobine_factor":0.88,"glycemie_factor":1.05,
               "proteines_factor":0.92,"gb_factor":1.10,
               "creatinine_factor":0.95,"pression_sys_factor":1.02},
    "AMRO":  {"immunite_baseline":0.92,"resilience_infection":0.90,
               "hemoglobine_factor":0.97,"glycemie_factor":1.12,
               "proteines_factor":1.00,"gb_factor":0.98,
               "creatinine_factor":1.05,"pression_sys_factor":1.08},
    "EMRO":  {"immunite_baseline":0.88,"resilience_infection":0.83,
               "hemoglobine_factor":0.92,"glycemie_factor":1.08,
               "proteines_factor":0.96,"gb_factor":1.05,
               "creatinine_factor":1.02,"pression_sys_factor":1.05},
    "EURO":  {"immunite_baseline":1.00,"resilience_infection":1.00,
               "hemoglobine_factor":1.00,"glycemie_factor":1.03,
               "proteines_factor":1.00,"gb_factor":1.00,
               "creatinine_factor":1.00,"pression_sys_factor":1.02},
    "SEARO": {"immunite_baseline":0.86,"resilience_infection":0.82,
               "hemoglobine_factor":0.90,"glycemie_factor":1.06,
               "proteines_factor":0.93,"gb_factor":1.08,
               "creatinine_factor":0.92,"pression_sys_factor":1.03},
    "WPRO":  {"immunite_baseline":0.97,"resilience_infection":0.95,
               "hemoglobine_factor":0.98,"glycemie_factor":1.04,
               "proteines_factor":0.98,"gb_factor":1.02,
               "creatinine_factor":0.98,"pression_sys_factor":1.01},
}

# Ajustements spécifiques par continent
# Pour affiner l'interpolation au-delà de la région
AJUSTEMENTS_CONTINENT = {
    "Afrique":   {"malnutrition_bonus":0.05, "paludisme_bonus":0.10,
                  "acces_soins_malus":0.05},
    "Asie":      {"malnutrition_bonus":0.02, "paludisme_bonus":0.03,
                  "acces_soins_malus":0.02},
    "Amériques": {"malnutrition_bonus":0.01, "paludisme_bonus":0.01,
                  "acces_soins_malus":0.00},
    "Europe":    {"malnutrition_bonus":0.00, "paludisme_bonus":0.00,
                  "acces_soins_malus":0.00},
    "Océanie":   {"malnutrition_bonus":0.01, "paludisme_bonus":0.00,
                  "acces_soins_malus":0.01},
}


def interpoler_profil_pays(row):
    """
    Génère le profil complet d'un pays en interpolant
    depuis son profil de résistance + région OMS + continent
    """
    profil    = row["resistance_profile"]
    region    = row["region_oms"]
    continent = row["continent"]
    code      = row["code_iso2"]

    # Base depuis le profil de résistance
    base = INDICATEURS_PAR_PROFIL[profil].copy()

    # Modificateurs régionaux
    mod_reg = MODIFICATEURS_REGION.get(region, MODIFICATEURS_REGION["EURO"])

    # Ajustements continent
    adj_cont = AJUSTEMENTS_CONTINENT.get(continent, {
        "malnutrition_bonus":0.0,
        "paludisme_bonus":0.0,
        "acces_soins_malus":0.0
    })

    # Appliquer ajustements continent
    base["malnutrition"]  += adj_cont["malnutrition_bonus"]
    base["paludisme"]     += adj_cont["paludisme_bonus"]
    base["acces_soins"]   -= adj_cont["acces_soins_malus"]

    # Ajouter bruit réaliste pour différencier les pays
    # d'un même profil (variance de ±15% autour de la valeur)
    np.random.seed(hash(code) % 2**31)
    for key in ["malnutrition","paludisme","tb_prevalence",
                "vih_prevalence","acces_soins","eau_potable"]:
        bruit = np.random.uniform(-0.15, 0.15) * base[key]
        base[key] = float(np.clip(base[key] + bruit, 0.0, 1.0))

    # Calcul des facteurs physiologiques dérivés
    base["immunite_baseline"]    = float(np.clip(
        mod_reg["immunite_baseline"] * (1 - base["vih_prevalence"] * 2)
        * (1 - base["malnutrition"] * 0.3), 0.3, 1.0))

    base["resilience_infection"] = float(np.clip(
        mod_reg["resilience_infection"] * (1 - base["malnutrition"] * 0.2)
        * (1 - base["paludisme"] * 0.15), 0.3, 1.0))

    base["hemoglobine_factor"]   = float(np.clip(
        mod_reg["hemoglobine_factor"]
        * (1 - base["malnutrition"] * 0.15)
        * (1 - base["paludisme"] * 0.10), 0.5, 1.1))

    base["glycemie_factor"]      = float(np.clip(
        mod_reg["glycemie_factor"], 0.9, 1.3))

    base["proteines_factor"]     = float(np.clip(
        mod_reg["proteines_factor"]
        * (1 - base["malnutrition"] * 0.3), 0.6, 1.1))

    base["gb_factor"]            = float(np.clip(
        mod_reg["gb_factor"]
        * (1 + base["paludisme"] * 0.1), 0.8, 1.5))

    base["creatinine_factor"]    = float(np.clip(
        mod_reg["creatinine_factor"], 0.8, 1.2))

    base["pression_sys_factor"]  = float(np.clip(
        mod_reg["pression_sys_factor"], 0.95, 1.2))

    # Métadonnées
    base["code_iso2"]   = code
    base["nom_fr"]      = row["nom_fr"]
    base["region_oms"]  = region
    base["continent"]   = continent
    base["referentiel"] = row["referentiel"]
    base["resistance_profile"] = profil
    base["latitude"]    = row["latitude"]
    base["longitude"]   = row["longitude"]

    return base


def generer_tous_pays():
    print("=" * 60)
    print("  SimBio 🧬 — Extension aux 194 pays")
    print("=" * 60)

    # Charger la liste des pays
    print("\n📂 Chargement de ref_pays.csv...")
    df_pays = pd.read_csv(f"{DATA_DIR}/ref_pays.csv")
    print(f"  ✅ {len(df_pays)} pays chargés")

    # Générer les profils
    print("\n🔧 Génération des profils physiologiques...")
    profils = []
    for _, row in df_pays.iterrows():
        try:
            profil = interpoler_profil_pays(row)
            profils.append(profil)
        except Exception as e:
            print(f"  ⚠️ Erreur pour {row['code_iso2']} : {e}")

    df_profils = pd.DataFrame(profils)

    # Statistiques
    print(f"\n  ✅ {len(df_profils)} profils générés")
    print(f"\n  📊 Moyennes par région OMS :")
    cols_affich = ["immunite_baseline","resilience_infection",
                   "malnutrition","acces_soins","paludisme"]
    print(df_profils.groupby("region_oms")[cols_affich]
          .mean().round(3).to_string())

    # Sauvegarder CSV
    out_csv = f"{DATA_DIR}/simbio_profils_194pays.csv"
    df_profils.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\n  ✅ CSV sauvegardé : {out_csv}")

    # Sauvegarder comme dict pour SimBio (accès rapide par code pays)
    dict_pays = {}
    for _, row in df_profils.iterrows():
        code = row["code_iso2"]
        dict_pays[code] = {
            "region":              row["region_oms"],
            "malnutrition":        row["malnutrition"],
            "paludisme":           row["paludisme"],
            "tb_prevalence":       row["tb_prevalence"],
            "vih_prevalence":      row["vih_prevalence"],
            "acces_soins":         row["acces_soins"],
            "eau_potable":         row["eau_potable"],
            "esperance_vie":       row["esperance_vie"],
            "mortalite_inf":       row["mortalite_inf"],
            "immunite_baseline":   row["immunite_baseline"],
            "resilience_infection":row["resilience_infection"],
            "hemoglobine_factor":  row["hemoglobine_factor"],
            "glycemie_factor":     row["glycemie_factor"],
            "proteines_factor":    row["proteines_factor"],
            "gb_factor":           row["gb_factor"],
            "creatinine_factor":   row["creatinine_factor"],
            "pression_sys_factor": row["pression_sys_factor"],
        }

    out_joblib = f"{MODEL_DIR}/simbio/modificateurs_194pays.joblib"
    joblib.dump(dict_pays, out_joblib)
    print(f"  ✅ Dict joblib sauvegardé : {out_joblib}")

    # Vérification rapide — 5 pays représentatifs
    print(f"\n  🔍 Vérification — 5 pays représentatifs :")
    pays_test = ["TG","FR","IN","US","NG"]
    print(f"  {'Pays':<6} {'Région':<8} {'Immunité':>9} "
          f"{'Résilience':>11} {'Malnutr.':>9} "
          f"{'Accès soins':>12} {'Hb factor':>10}")
    print(f"  {'-'*68}")
    for code in pays_test:
        if code in dict_pays:
            p = dict_pays[code]
            nom = df_profils[df_profils["code_iso2"]==code]["nom_fr"].values[0]
            print(f"  {code:<6} {p['region']:<8} "
                  f"{p['immunite_baseline']:>9.3f} "
                  f"{p['resilience_infection']:>11.3f} "
                  f"{p['malnutrition']:>9.3f} "
                  f"{p['acces_soins']:>12.3f} "
                  f"{p['hemoglobine_factor']:>10.3f}  ({nom})")

    print(f"\n{'='*60}")
    print(f"  ✅ Extension SimBio — 194 pays opérationnels !")
    print(f"{'='*60}")

    return dict_pays, df_profils


if __name__ == "__main__":
    dict_pays, df_profils = generer_tous_pays()