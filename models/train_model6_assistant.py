"""
ResistIA v2.0 — Modèle 6 : Assistant Clinique Conversationnel
ResistIA Brain 🧠
Assistant intelligent capable de répondre à des questions
médicales sur la résistance aux antibiotiques en langage naturel
"""

import sys
import os
sys.path.insert(0, 'C:\\ResistIA_v2')

import pandas as pd
import numpy as np
import joblib
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

DATA_DIR  = "C:\\ResistIA_v2\\data\\synthetic"
MODEL_DIR = "C:\\ResistIA_v2\\models"


# ─────────────────────────────────────────────
# 1. BASE DE CONNAISSANCES AMR
# ─────────────────────────────────────────────

BASE_CONNAISSANCES = [
    # ── Mécanismes de résistance ──
    {
        "id": "meca_esbl",
        "question": "Qu'est-ce qu'une ESBL ?",
        "mots_cles": ["esbl", "beta-lactamase", "spectre élargi",
                      "bêta-lactamase", "blaCTX", "céphalosporine résistance"],
        "reponse": (
            "Les ESBL (Extended-Spectrum Beta-Lactamases) sont des enzymes "
            "produites par certaines bactéries Gram-négatives (E. coli, "
            "K. pneumoniae) qui détruisent la plupart des pénicillines et "
            "céphalosporines. Les carbapénèmes (imipénem, méropénem) restent "
            "généralement actifs. Les gènes impliqués : blaCTX-M, blaTEM, blaSHV."
        ),
        "categorie": "mecanisme"
    },
    {
        "id": "meca_kpc",
        "question": "Qu'est-ce qu'une carbapénémase KPC ?",
        "mots_cles": ["kpc", "carbapénémase", "carbapenemase",
                      "résistance carbapénème", "blaKPC"],
        "reponse": (
            "KPC (Klebsiella pneumoniae Carbapenemase) est une enzyme qui "
            "détruit les carbapénèmes, les antibiotiques de dernier recours. "
            "Les souches KPC+ sont souvent multirésistantes. Options "
            "thérapeutiques limitées : ceftazidime-avibactam, céfidérocol, "
            "colistine. Gène responsable : blaKPC."
        ),
        "categorie": "mecanisme"
    },
    {
        "id": "meca_mrsa",
        "question": "Comment fonctionne la résistance SARM à la méticilline ?",
        "mots_cles": ["sarm", "mrsa", "méticilline", "mecA",
                      "staphylocoque résistant", "oxacilline",
                      "staphylococcus aureus résistant",
                      "qu est ce que le sarm", "sarm definition"],
        "reponse": (
            "Le SARM (Staphylococcus aureus Résistant à la Méticilline) "
            "possède le gène mecA qui code une protéine PBP2a avec faible "
            "affinité pour tous les bêta-lactamines. Traitement : vancomycine, "
            "linézolide, daptomycine. Le SARM est classé pathogène PRIORITÉ "
            "HAUTE par l'OMS."
        ),
        "categorie": "mecanisme"
    },
    {
        "id": "meca_ndm",
        "question": "Qu'est-ce que NDM-1 ?",
        "mots_cles": ["ndm", "ndm-1", "new delhi", "métallo",
                      "metallo-beta-lactamase", "blaNDM"],
        "reponse": (
            "NDM-1 (New Delhi Metallo-beta-lactamase) est une enzyme "
            "métallo-bêta-lactamase qui hydrolyse presque tous les "
            "antibiotiques bêta-lactamines y compris les carbapénèmes. "
            "Découverte en 2008 en Inde, elle s'est répandue mondialement. "
            "Peu d'options : aztréonam-avibactam, céfidérocol, colistine."
        ),
        "categorie": "mecanisme"
    },
    # ── Pathogènes ──
    {
        "id": "patho_acinetobacter",
        "question": "Pourquoi Acinetobacter baumannii est-il dangereux ?",
        "mots_cles": ["acinetobacter", "baumannii", "acb",
                      "résistance totale", "pan-résistant"],
        "reponse": (
            "A. baumannii est classé PRIORITÉ CRITIQUE par l'OMS. Il peut "
            "développer une résistance à pratiquement tous les antibiotiques "
            "disponibles (pan-résistance). Il survit longtemps sur les "
            "surfaces hospitalières. Mécanismes : OXA-carbapénémases, "
            "efflux pumps, méthylases. Options très limitées : colistine, "
            "tigécycline, céfidérocol."
        ),
        "categorie": "pathogene"
    },
    {
        "id": "patho_candida_auris",
        "question": "Qu'est-ce que Candida auris ?",
        "mots_cles": ["candida auris", "c. auris", "champignon résistant",
                      "levure multirésistante", "fongique"],
        "reponse": (
            "Candida auris est un champignon émergent classé PRIORITÉ CRITIQUE "
            "par l'OMS (2022). Il est naturellement résistant au fluconazole "
            "(>90% des souches). Peut développer une résistance aux "
            "échinocandines et à l'amphotéricine B. Difficile à identifier "
            "au laboratoire. Touche principalement les patients immunodéprimés."
        ),
        "categorie": "pathogene"
    },
    {
        "id": "patho_tb",
        "question": "Qu'est-ce que la tuberculose MDR ?",
        "mots_cles": ["tuberculose", "tb", "mdr", "xdr",
                      "mycobacterium tuberculosis", "bk résistant"],
        "reponse": (
            "La TB-MDR (Multi-Drug Resistant) est résistante à l'isoniazide "
            "ET la rifampicine, les deux antibiotiques de première ligne. "
            "La TB-XDR (Extensively Drug Resistant) est de plus résistante "
            "aux fluoroquinolones. Traitement TB-MDR : 18-24 mois avec "
            "bédaquiline, délamanid, linézolide. L'OMS estime 450 000 cas "
            "de TB-MDR par an dans le monde."
        ),
        "categorie": "pathogene"
    },
    # ── Thérapeutique ──
    {
        "id": "therap_allergie_betalact",
        "question": "Quel antibiotique pour patient allergique bêta-lactamines ?",
        "mots_cles": ["allergie", "bêta-lactamine", "penicilline allergie",
                      "alternative allergie", "intolérance pénicilline"],
        "reponse": (
            "En cas d'allergie aux bêta-lactamines confirmée : "
            "Pour infections à Gram+ : vancomycine, linézolide, daptomycine. "
            "Pour infections à Gram- : fluoroquinolones (si sensible), "
            "aminosides, aztréonam (pas de résistance croisée avec pénicillines). "
            "Note : 80-90% des patients se disant allergiques ne le sont pas "
            "vraiment — une désensibilisation peut être envisagée."
        ),
        "categorie": "therapeutique"
    },
    {
        "id": "therap_meningite",
        "question": "Quel traitement pour méningite bactérienne ?",
        "mots_cles": ["méningite", "meningite", "lcr", "céphalée",
                      "raideur nuque", "purpura", "méningocoque"],
        "reponse": (
            "Méningite bactérienne : URGENCE médicale. "
            "Traitement empirique : ceftriaxone 2g IV toutes les 12h "
            "(adulte). Si suspicion Listeria (>50 ans, immunodéprimé) : "
            "ajouter amoxicilline 2g IV/4h. "
            "Si résistance connue : adapter selon antibiogramme. "
            "Dexaméthasone 0.15mg/kg IV à débuter avant ou avec antibiotique."
        ),
        "categorie": "therapeutique"
    },
    {
        "id": "therap_itu",
        "question": "Quel antibiotique pour infection urinaire ?",
        "mots_cles": ["infection urinaire", "itu", "cystite", "pyélonéphrite",
                      "ecbu", "urine", "brûlure miction"],
        "reponse": (
            "Cystite non compliquée : nitrofurantoïne 100mg x2/j 5j ou "
            "fosfomycine trométamol 3g dose unique. "
            "Pyélonéphrite légère-modérée : fluoroquinolone orale 7j "
            "(si sensible) ou ceftriaxone IM/IV. "
            "Si résistance : adapter à l'antibiogramme. "
            "Éviter amoxicilline (résistance >50% en Afrique subsaharienne)."
        ),
        "categorie": "therapeutique"
    },
    {
        "id": "therap_dernier_recours",
        "question": "Quels sont les antibiotiques de dernier recours ?",
        "mots_cles": ["dernier recours", "last resort", "colistine",
                      "vancomycine", "linézolide", "carbapénème",
                      "cefiderocol", "reserve antibiotics"],
        "reponse": (
            "Antibiotiques de dernier recours (OMS — Access/Watch/Reserve) : "
            "RESERVE : colistine, polymyxine B, céfidérocol, aztréonam-avibactam, "
            "imipénem-relebactam, ceftazidime-avibactam. "
            "À n'utiliser qu'en cas d'absence d'alternative documentée. "
            "Leur utilisation excessive accélère l'émergence de résistances."
        ),
        "categorie": "therapeutique"
    },
    # ── Épidémiologie ──
    {
        "id": "epid_amr_monde",
        "question": "Quelle est la situation mondiale de la résistance aux antibiotiques ?",
        "mots_cles": ["situation mondiale", "épidémiologie amr",
                      "résistance monde", "décès amr", "charge mondiale"],
        "reponse": (
            "Selon l'OMS et le rapport GLASS 2022 : "
            "1,27 million de décès directement attribuables à l'AMR en 2019. "
            "4,95 millions de décès associés à l'AMR. "
            "Sans action, projection de 10 millions de décès/an d'ici 2050. "
            "Régions les plus touchées : Afrique subsaharienne et Asie du Sud. "
            "Pathogènes les plus meurtriers : E. coli, S. aureus, K. pneumoniae."
        ),
        "categorie": "epidemiologie"
    },
    {
        "id": "epid_afrique",
        "question": "Quelle est la situation de l'AMR en Afrique ?",
        "mots_cles": ["afrique", "afro", "subsaharienne", "amr afrique",
                      "résistance afrique", "ecowas", "cedeao"],
        "reponse": (
            "L'Afrique subsaharienne est la région OMS la plus touchée par "
            "l'AMR avec un taux de mortalité attribuable de 24/100 000 hab. "
            "Facteurs aggravants : accès limité aux antibiotiques de qualité, "
            "automédication, manque de laboratoires, climat favorisant les "
            "infections. Résistances préoccupantes : E. coli aux "
            "fluoroquinolones (>40%), K. pneumoniae aux céphalosporines 3G (>35%)."
        ),
        "categorie": "epidemiologie"
    },
    # ── Prévention ──
    {
        "id": "prev_bon_usage",
        "question": "Comment prévenir la résistance aux antibiotiques ?",
        "mots_cles": ["prévention", "bon usage", "stewardship",
                      "antibioprophylaxie", "éviter résistance"],
        "reponse": (
            "Stratégies de prévention de l'AMR : "
            "1. Prescrire uniquement si infection bactérienne prouvée/probable. "
            "2. Choisir l'antibiotique à spectre le plus étroit possible. "
            "3. Respecter la durée minimale efficace. "
            "4. Pratiquer l'antibiothérapie guidée par l'antibiogramme. "
            "5. Hygiène des mains et mesures de contrôle des infections. "
            "6. Vaccination pour réduire les infections bactériennes."
        ),
        "categorie": "prevention"
    },
]

# ─────────────────────────────────────────────
# 2. CLASSIFICATION DES INTENTIONS
# ─────────────────────────────────────────────

INTENTIONS = {
    "mecanisme":      ["mécanisme", "comment fonctionne", "résistance comment",
                       "gène", "enzyme", "pourquoi résistant"],
    "pathogene":      ["bactérie", "pathogène", "germe", "microbe",
                       "champignon", "parasite", "dangereux"],
    "therapeutique":  ["traitement", "antibiotique", "quel abx", "prescrire",
                       "allergie", "posologie", "dose"],
    "epidemiologie":  ["taux", "prévalence", "pays", "région", "monde",
                       "afrique", "statistique", "décès"],
    "prevention":     ["prévention", "éviter", "bon usage", "stewardship",
                       "hygiène", "vaccin"],
    "resistance_taux":["taux de résistance", "résistance en", "pourcentage",
                       "données", "statistiques résistance"],
}

def classifier_intention(question):
    """Identifie le type de question posée"""
    question_lower = question.lower()
    scores = {}
    for intention, mots in INTENTIONS.items():
        score = sum(1 for mot in mots if mot in question_lower)
        scores[intention] = score
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "general"


# ─────────────────────────────────────────────
# 3. MOTEUR DE RECHERCHE SÉMANTIQUE
# ─────────────────────────────────────────────

def construire_moteur_recherche():
    """Construit un index TF-IDF sur la base de connaissances"""
    print("\n🔧 Construction du moteur de recherche sémantique...")

    # Combiner question + mots-clés pour l'indexation
    corpus = []
    for doc in BASE_CONNAISSANCES:
        texte = doc["question"] + " " + " ".join(doc["mots_cles"])
        corpus.append(texte)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        analyzer="word"
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    print(f"  ✅ {len(BASE_CONNAISSANCES)} documents indexés")
    print(f"  ✅ Vocabulaire : {len(vectorizer.vocabulary_)} termes")

    return vectorizer, tfidf_matrix


def rechercher_reponse(question, vectorizer, tfidf_matrix, top_k=3):
    """Trouve les réponses les plus pertinentes à une question"""
    question_vec  = vectorizer.transform([question.lower()])
    similarites   = cosine_similarity(question_vec, tfidf_matrix)[0]
    top_indices   = np.argsort(similarites)[::-1][:top_k]

    resultats = []
    for idx in top_indices:
        if similarites[idx] > 0.01:  # seuil minimum de pertinence
            resultats.append({
                "document":   BASE_CONNAISSANCES[idx],
                "score":      similarites[idx],
            })
    return resultats


# ─────────────────────────────────────────────
# 4. ENRICHISSEMENT AVEC DONNÉES ÉPIDÉMIO
# ─────────────────────────────────────────────

def enrichir_avec_donnees(question, df_taux, df_pays):
    """
    Si la question concerne les taux de résistance,
    on interroge directement notre base de données
    """
    question_lower = question.lower()
    reponse_data   = None

    # Détection des entités dans la question
    pathogenes_connus = {
        "e. coli": "Escherichia coli",
        "escherichia": "Escherichia coli",
        "klebsiella": "Klebsiella pneumoniae",
        "k. pneumoniae": "Klebsiella pneumoniae",
        "staphylocoque": "Staphylococcus aureus",
        "s. aureus": "Staphylococcus aureus",
        "pseudomonas": "Pseudomonas aeruginosa",
        "acinetobacter": "Acinetobacter baumannii",
        "candida auris": "Candida auris",
        "tuberculose": "Mycobacterium tuberculosis",
    }

    pays_connus = {
        "togo": "TG", "sénégal": "SN", "nigeria": "NG",
        "ghana": "GH", "france": "FR", "inde": "IN",
        "maroc": "MA", "tunisie": "TN", "côte d'ivoire": "CI",
    }

    abx_connus = {
        "ciprofloxacine": "ciprofloxacine",
        "ampicilline": "ampicilline",
        "ceftriaxone": "ceftriaxone",
        "imipénem": "imipenem",
        "méropénem": "meropenem",
        "colistine": "colistine",
        "vancomycine": "vancomycine",
    }

    patho_trouve = None
    pays_trouve  = None
    abx_trouve   = None

    for key, val in pathogenes_connus.items():
        if key in question_lower:
            patho_trouve = val
            break

    for key, val in pays_connus.items():
        if key in question_lower:
            pays_trouve = val
            break

    for key, val in abx_connus.items():
        if key in question_lower:
            abx_trouve = val
            break

    # Si on a trouvé des entités, interroger la base
    if patho_trouve and abx_trouve:
        filtre = (
            (df_taux["pathogene"] == patho_trouve) &
            (df_taux["antibiotique"] == abx_trouve) &
            (df_taux["annee"] == 2025)
        )
        if pays_trouve:
            filtre = filtre & (df_taux["code_pays"] == pays_trouve)

        df_filtre = df_taux[filtre]

        if len(df_filtre) > 0:
            taux_moy = df_filtre["taux_resistance_pct"].mean()
            region   = df_filtre["region_oms"].iloc[0]
            pays_nom = df_filtre["pays_fr"].iloc[0] if pays_trouve else "monde"

            reponse_data = (
                f"D'après la base ResistIA (données 2025) : "
                f"Le taux de résistance de {patho_trouve} à {abx_trouve} "
                f"{'au ' + pays_nom if pays_trouve else 'dans la région ' + region} "
                f"est de {taux_moy:.1f}%."
            )
            if taux_moy > 50:
                reponse_data += " ⚠️ Résistance majoritaire — cet antibiotique est probablement inefficace."
            elif taux_moy > 20:
                reponse_data += " ⚠️ Résistance intermédiaire — utiliser avec précaution."
            else:
                reponse_data += " ✅ Résistance faible — antibiotique probablement efficace."

    return reponse_data


# ─────────────────────────────────────────────
# 5. ASSISTANT PRINCIPAL
# ─────────────────────────────────────────────

def assistant_repondre(question, vectorizer, tfidf_matrix,
                       df_taux, df_pays):
    """
    Génère une réponse complète à une question médicale
    """
    intention = classifier_intention(question)

    # D'abord chercher dans les données épidémio si pertinent
    reponse_data = None
    if intention in ["resistance_taux", "epidemiologie"]:
        reponse_data = enrichir_avec_donnees(question, df_taux, df_pays)

    # Chercher dans la base de connaissances
    resultats = rechercher_reponse(question, vectorizer, tfidf_matrix)

    reponse_finale = []

    if reponse_data:
        reponse_finale.append(reponse_data)

    if resultats:
        meilleur = resultats[0]
        if meilleur["score"] > 0.05:
            reponse_finale.append(meilleur["document"]["reponse"])

    if not reponse_finale:
        reponse_finale.append(
            "Je n'ai pas trouvé de réponse précise à votre question dans ma "
            "base de connaissances. Reformulez votre question ou consultez "
            "les guidelines EUCAST/CLSI pour des informations actualisées."
        )

    return {
        "question":   question,
        "intention":  intention,
        "reponse":    " | ".join(reponse_finale),
        "confiance":  resultats[0]["score"] if resultats else 0.0,
        "sources":    [r["document"]["id"] for r in resultats[:2]]
    }


# ─────────────────────────────────────────────
# 6. SAUVEGARDE
# ─────────────────────────────────────────────

def sauvegarder(vectorizer, tfidf_matrix):
    print("\n💾 Sauvegarde du modèle...")
    joblib.dump(vectorizer,   f"{MODEL_DIR}/model6_vectorizer.joblib")
    joblib.dump(tfidf_matrix, f"{MODEL_DIR}/model6_tfidf.joblib")
    joblib.dump(BASE_CONNAISSANCES, f"{MODEL_DIR}/model6_kb.joblib")
    print(f"  ✅ Modèle sauvegardé dans : {MODEL_DIR}")


# ─────────────────────────────────────────────
# 7. TEST DE L'ASSISTANT
# ─────────────────────────────────────────────

def tester_assistant(vectorizer, tfidf_matrix, df_taux, df_pays):
    print("\n🤖 Test de l'Assistant Clinique ResistIA Brain 🧠")
    print("=" * 60)

    questions = [
        "Qu'est-ce qu'une ESBL et comment y faire face ?",
        "Quel antibiotique pour un patient allergique aux pénicillines ?",
        "Quel est le taux de résistance de E. coli à la ciprofloxacine au Togo ?",
        "Quels sont les antibiotiques de dernier recours ?",
        "Quelle est la situation de l'AMR en Afrique ?",
        "Comment prévenir la résistance aux antibiotiques ?",
        "Qu'est-ce que le SARM ?",
    ]

    for question in questions:
        print(f"\n  ❓ {question}")
        reponse = assistant_repondre(
            question, vectorizer, tfidf_matrix, df_taux, df_pays
        )
        print(f"  💬 {reponse['reponse'][:200]}...")
        print(f"     [Intention: {reponse['intention']} | "
              f"Confiance: {reponse['confiance']:.2f}]")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ResistIA Brain 🧠 — Modèle 6 : Assistant Clinique")
    print("=" * 60)

    print("\n📂 Chargement des données...")
    df_taux = pd.read_csv(f"{DATA_DIR}/taux_resistance_mondiaux.csv")
    df_pays = pd.read_csv(f"{DATA_DIR}/ref_pays.csv")
    print(f"  ✅ Taux de résistance : {len(df_taux):,} lignes")
    print(f"  ✅ Pays               : {len(df_pays)}")

    vectorizer, tfidf_matrix = construire_moteur_recherche()

    sauvegarder(vectorizer, tfidf_matrix)

    tester_assistant(vectorizer, tfidf_matrix, df_taux, df_pays)

    print("\n" + "=" * 60)
    print("  ✅ Modèle 6 terminé !")
    print("=" * 60)