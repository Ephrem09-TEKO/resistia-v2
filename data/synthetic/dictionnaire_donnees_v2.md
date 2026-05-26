# ResistIA v2.0 — Dictionnaire de Données
*Généré le 2026-04-18 | 33 champs*

| # | Champ | Description | Type | Valeurs / Notes |
|---|-------|-------------|------|-----------------|
| 1 | `code_pays` | Code ISO 3166-1 alpha-2 | `CHAR(2)` | Ex: TG, FR, IN |
| 2 | `pays_fr` | Nom du pays en français | `VARCHAR` | Ex: Togo |
| 3 | `continent` | Continent | `VARCHAR` | Afrique, Amériques, Asie, Europe, Océanie |
| 4 | `region_oms` | Région OMS | `VARCHAR` | AFRO, AMRO, EMRO, EURO, SEARO, WPRO |
| 5 | `referentiel` | Référentiel de lecture | `VARCHAR` | EUCAST ou CLSI |
| 6 | `annee` | Année du prélèvement | `SMALLINT` | 2015 à 2025 |
| 7 | `pathogene_id` | Identifiant pathogène | `INTEGER` | FK → ref_pathogenes |
| 8 | `pathogene` | Nom scientifique du pathogène | `VARCHAR` | Ex: Escherichia coli |
| 9 | `categorie` | Catégorie du pathogène | `VARCHAR` | GRAM_NEG, GRAM_POS, FUNGI, MYCOBACT, ANAEROBE, PARASITE, ATYPIQUE |
| 10 | `classification_who` | Criticité OMS | `VARCHAR` | CRITICAL, HIGH, MEDIUM |
| 11 | `eskape` | Appartenance ESKAPE | `BOOLEAN` | TRUE/FALSE |
| 12 | `genes_resistance` | Gènes de résistance | `TEXT` | Ex: blaKPC, mecA, NDM-1 |
| 13 | `mecanismes` | Mécanismes de résistance | `TEXT` | Ex: ESBL, KPC, Efflux pump |
| 14 | `site_prelevement` | Site anatomique de prélèvement | `VARCHAR` | Ex: Hémoculture, Liquide de chyle |
| 15 | `antibiotique` | Nom DCI de l'antibiotique | `VARCHAR` | Ex: ceftriaxone, imipenem |
| 16 | `code_atc` | Code ATC | `VARCHAR` | Ex: J01DD04 |
| 17 | `classe` | Classe thérapeutique | `VARCHAR` | Ex: CEPHALOSPORINE_3G, CARBAPENEM |
| 18 | `spectre` | Spectre d'activité | `VARCHAR` | large, intermediaire, etroit |
| 19 | `derniere_ligne` | Antibiotique de dernier recours | `BOOLEAN` | Ex: colistine, vancomycine |
| 20 | `nouvelle_molecule` | Molécule récente | `BOOLEAN` | Ex: Cefiderocol, Bedaquiline |
| 21 | `resultat_sir` | Résultat antibiogramme | `CHAR(1)` | S=Sensible, I=Intermédiaire, R=Résistant |
| 22 | `taux_resistance_pct` | Taux de résistance agrégé (%) | `DECIMAL` | 0.0 à 99.9 |
| 23 | `diametre_mm` | Zone d'inhibition (mm) | `DECIMAL` | Méthode Kirby-Bauer |
| 24 | `tranche_age` | Tranche d'âge patient (anonymisé) | `VARCHAR` | neonat, pediatrique, adulte, senior |
| 25 | `genre` | Genre patient | `CHAR(1)` | M, F |
| 26 | `source_donnees` | Source de l'enregistrement | `VARCHAR` | GLASS, WHONET, EARS-Net, SYNTHETIC, USER_IMPORT |
| 27 | `latitude` | Latitude géographique | `DECIMAL` | WGS84 |
| 28 | `longitude` | Longitude géographique | `DECIMAL` | WGS84 |
| 29 | `is_ecowas` | Membre ECOWAS | `BOOLEAN` | 15 pays membres CEDEAO |
| 30 | `resistance_profile` | Profil épidémio régional | `VARCHAR` | low, medium, high, very_high |
| 31 | `score_severite` | Score de sévérité AMR (0-100) | `DECIMAL` | Calculé par ResistIA Brain 🧠 |
| 32 | `niveau_alerte` | Niveau d'alerte | `VARCHAR` | VERT, ORANGE, ROUGE |
| 33 | `version_dataset` | Version du dataset | `VARCHAR` | v2.0 |

## Sources de calibration
- GLASS 2022 (WHO) — taux de résistance mondiaux
- EARS-Net 2022 (ECDC) — Europe
- WHONET — données hospitalières
- Africa-AMR / INESS — Afrique subsaharienne

## Couverture
- **194 pays** | **42 pathogènes** | **82 antibiotiques**
- **2015–2025** (11 années) | **15 sites de prélèvement**