# Analyse Complète — Assistant Matanne

> **Date**: 2 Avril 2026
> **Scope**: Backend (FastAPI/Python) + Frontend (Next.js 16) + SQL + Tests + Docs + Intégrations
> **Objectif**: Audit exhaustif, plan d'action structuré, axes d'amélioration et innovations

---

## Table des matières

1. [Métriques globales](#1-métriques-globales)
2. [Inventaire par module](#2-inventaire-par-module)
3. [Bugs et problèmes détectés](#3-bugs-et-problèmes-détectés)
4. [Gaps et fonctionnalités manquantes](#4-gaps-et-fonctionnalités-manquantes)
5. [Consolidation SQL](#5-consolidation-sql)
6. [Interactions intra-modules](#6-interactions-intra-modules)
7. [Interactions inter-modules existantes](#7-interactions-inter-modules-existantes)
8. [Interactions inter-modules manquantes](#8-interactions-inter-modules-manquantes)
9. [Opportunités IA](#9-opportunités-ia)
10. [Jobs automatiques (CRON)](#10-jobs-automatiques-cron)
11. [Notifications — WhatsApp, Email, Push](#11-notifications--whatsapp-email-push)
12. [Mode Admin manuel](#12-mode-admin-manuel)
13. [Tests — Couverture et manques](#13-tests--couverture-et-manques)
14. [Documentation — État et manques](#14-documentation--état-et-manques)
15. [UI/UX — Améliorations et modernisation](#15-uiux--améliorations-et-modernisation)
16. [Nettoyage legacy et rétrocompatibilité](#16-nettoyage-legacy-et-rétrocompatibilité)
17. [Nommage des fichiers et commentaires](#17-nommage-des-fichiers-et-commentaires)
18. [Simplification du flux utilisateur](#18-simplification-du-flux-utilisateur)
19. [Innovations et axes d'amélioration](#19-innovations-et-axes-damelioration)
20. [Plan d'action structuré](#20-plan-daction-structuré)

---

## 1. Métriques globales

| Métrique | Valeur |
|---|---|
| Routes API | 49 fichiers, ~400+ endpoints |
| Schémas Pydantic | 28 fichiers |
| Modèles ORM | 32 fichiers, ~180 classes |
| Tables SQL | 156 |
| Services backend | 100+ fichiers |
| Services IA (BaseAIService) | 38 services |
| CRON Jobs | 51 planifiés |
| Pages frontend | ~95 pages + 5 layouts |
| Composants UI (shadcn/ui) | 29 |
| Composants domaine | ~80 |
| Clients API frontend | 28 fichiers |
| Hooks React | 15 |
| Stores Zustand | 7 |
| Types TypeScript | 15 fichiers |
| Tests backend | 74+ fichiers, ~500+ fonctions |
| Tests frontend | 71+ fichiers |
| Documentation | 42+ fichiers |
| Bridges inter-modules | 23 fichiers |

---

## 2. Inventaire par module

### Cuisine

| Couche | Fichiers | Détail |
|---|---|---|
| Routes | 4 | recettes, courses, batch_cooking, anti_gaspillage |
| Schémas | 4 | Correspondance 1:1 |
| Modèles | 2 | recettes (7 classes), courses/inventaire (8 classes) |
| Services | 40+ | recettes/ (17), planning/ (15), courses/ (7), suggestions/ (27) |
| Services IA | 7 | Suggestions, import, enrichissement, batch cooking IA, versions Jules |
| Pages frontend | 17 | Hub + recettes CRUD + planning + courses + inventaire + nutrition + batch |
| Inter-modules | 8 | jardin→recettes, péremption→recettes, batch→inventaire, etc. |
| CRON | 5 | Recipe of the day, anti-gaspillage, seasonal, prediction courses |
| Tests | OK | Bonne couverture routes + services |

### Famille

| Couche | Fichiers | Détail |
|---|---|---|
| Routes | 4 | famille, famille_activites, famille_budget, famille_jules |
| Modèles | 1 | 11 classes (profils enfants, activités, budget, jours spéciaux...) |
| Services | 15+ | jules_ai, weekend_ai, soiree_ai, budget_ai, resume_hebdo |
| Services IA | 8 | Jules, Budget, Achats, Weekend, Soirée, Résumé, Versions recettes |
| Pages frontend | 13 | Hub + Jules + routines + budget + contacts + documents + timeline + voyages |
| Inter-modules | 9 | weekend→courses, budget→anomalie, voyages→budget, meteo→activités |
| CRON | 8 | Rappels famille, anniversaires, Garmin sync, calendrier scolaire |
| Tests | OK | Couverture correcte |

### Maison

| Couche | Fichiers | Détail |
|---|---|---|
| Routes | 5 | maison, maison_projets, maison_jardin, maison_entretien, maison_finances |
| Modèles | 4 | 35+ classes (projets, routines, jardin, meubles, diagnostics, énergie...) |
| Services | 50+ | CRUD (8), IA mixins (4), catalogue, visualisation, conseiller |
| Services IA | 7 | Entretien, diagnostics photo, énergie anomalies, conseiller, jardin |
| Pages frontend | 17 | Hub + travaux + charges + ménage + jardin + meubles + 3D + diagnostics |
| Inter-modules | 5 | entretien→courses, jardin→entretien, charges→énergie, diagnostics→IA |
| CRON | 14 | Rappels maison, entretien saisonnier, énergie, jardin, rapports |
| Tests | OK | Couverture correcte |

### Jeux

| Couche | Fichiers | Détail |
|---|---|---|
| Routes | 5 | jeux, jeux_paris, jeux_loto, jeux_euromillions, jeux_dashboard |
| Modèles | 1 | 22 classes (equipes, matchs, paris, tirages, grilles, bankroll...) |
| Services | 12+ | euromillions_ia, ai_service, stats, backtest |
| Services IA | 2 | EuromillionsIA, JeuxAI |
| Pages frontend | 7 | Hub + paris + loto + euromillions + bankroll + performance |
| CRON | 3 | Sync tirages, résultats, budget jeux |
| Tests | OK | Tests phases T/U/W |

### IA Avancée

| Couche | Fichiers | Détail |
|---|---|---|
| Routes | 2 | ia_avancee, ia_phase_b (à renommer) |
| Services | 10+ | Service principal (11 méthodes), bridges, router |
| Pages frontend | 15 | Suggestions proactives, diagnostic plante, analyse photo/document, prévisions, etc. |
| Tests | Tests phase B existants |

### Outils

| Couche | Fichiers | Détail |
|---|---|---|
| Routes | 3 | utilitaires, assistant, automations |
| Services | 12 | chat_ai, automations_engine, assistant_proactif, briefing_matinal, export, import, meteo, OCR |
| Pages frontend | 10+ | Chat IA, notes, convertisseur, minuteur, météo, Google Assistant, automations |
| CRON | 0 | Aucun cron dédié (à corriger) |

### Habitat

| Couche | Fichiers | Détail |
|---|---|---|
| Routes | 1 | habitat |
| Services | 5+ | plans_ai_service, deco_service, scenarios |
| Pages frontend | 6 | Hub + veille immo + marché + scénarios + plans + déco |
| CRON | 1 | Veille habitat |

### Dashboard

| Couche | Fichiers | Détail |
|---|---|---|
| Routes | 1 | dashboard (20 endpoints) |
| Services | 3 | service, resume_famille_ia, anomalies_financieres |
| Pages frontend | 1 | Dashboard principal avec widgets DnD |
| CRON | 4 | Charges dashboard, scores, nutrition hebdo, points |

---

## 3. Bugs et problèmes détectés

### Vrais bugs

| # | Problème | Fichier | Sévérité |
|---|---|---|---|
| B1 | `audit_output.txt` — fichier encodé en UTF-16, illisible, artefact legacy | racine | Faible |
| B2 | `jeux.py.bak` — fichier backup oublié dans les routes | `src/api/routes/jeux.py.bak` | Faible |
| B3 | Champs legacy dans modèle `planning.py` (ligne 45: "legacy, remplacé par statut") encore présents | `src/core/models/planning.py` | Moyenne |
| B4 | Champs legacy dans modèle `jeux.py` (lignes 216, 248, 765: compat tests legacy) | `src/core/models/jeux.py` | Moyenne |
| B5 | Validators legacy dans `phase_b.py` schéma (ligne 37/45: "_legacy_single_article") | `src/api/schemas/phase_b.py` | Moyenne |
| B6 | `TODO(P1-06)` non résolu — remplacer par API officielle Supabase | `src/services/core/utilisateur/auth_token.py` L44 | Haute |
| B7 | Aliases rétrocompatibilité Sprint 12 A3 dans 10+ services — code mort si plus aucun appelant | Multiple services | Moyenne |
| B8 | Page `cuisine/courses/scan-ticket/` — OCR désactivé par préférence, page encore accessible | Frontend | Faible |
| B9 | Page `jeux/ocr-ticket/` — même problème, page accessible pour rien | Frontend | Faible |

### Problèmes d'architecture

| # | Problème | Impact |
|---|---|---|
| A1 | Fichiers nommés par phase/sprint (13 fichiers) — opaque pour un nouveau lecteur | Maintenabilité |
| A2 | Route `innovations.py` — nom fourre-tout, ne décrit pas la fonctionnalité | Clarté |
| A3 | Commentaires contenant des noms de phase dans le code source (~100 occurrences) | Maintenabilité |
| A4 | Modèle `notifications_sprint_e.py` — nommé par sprint au lieu du domaine | Clarté |
| A5 | 2 fichiers décorateurs avec noms différents : `test_decorators.py` ET `test_decorateurs.py` | Confusion |
| A6 | `scripts/_archive/` — scripts legacy gardés "au cas où" | Propreté |
| A7 | Certains modules Event Bus ne publient aucun événement (Famille, Jeux, Dashboard) | Couplage |

---

## 4. Gaps et fonctionnalités manquantes

### Pages frontend sans vraie utilité

| Page | Problème | Action |
|---|---|---|
| `cuisine/courses/scan-ticket/` | OCR désactivé (préf. utilisateur) | Supprimer |
| `jeux/ocr-ticket/` | OCR désactivé | Supprimer |
| `innovations/` | Nom opaque, contenu mélangé (pilot mode, family score, journal) | Renommer & restructurer |
| `famille/gamification/` | Limité au sport/Garmin uniquement | Clarifier scope dans l'UI |

### Backend gaps

| Gap | Module | Description |
|---|---|---|
| G1 | Inventaire | Pas de service IA dédié (prédiction stock, rotation FIFO, seuils intelligents) |
| G2 | Planning | Pas de service IA propre (tout via mixins dans suggestions) |
| G3 | Outils | Aucun CRON job (briefing matinal non planifié ?) |
| G4 | Gamification | Modèles présents mais service minimal (PointsUtilisateur, BadgeUtilisateur) |
| G5 | Event Bus | Famille, Jeux, Dashboard ne publient aucun événement |
| G6 | Notifications | Pas de WhatsApp pour suggestions recettes, diagnostics maison, activités weekend |
| G7 | OCR factures | Service existe mais page/flow utilisateur incomplet |

### Manques inter-modules

| Pont manquant | Modules | Description |
|---|---|---|
| IM1 | Inventaire → Budget | Pas de tracking coût/ingrédient pour prévision budget alimentation |
| IM2 | Planning → Jardin | Pas de feedback loop (ingrédients jardin non utilisés → ajustement production) |
| IM3 | Santé adultes → Cuisine | Données Garmin existantes, non liées aux suggestions nutritionnelles adultes |
| IM4 | Entretien → Budget | Pas de suivi des dépenses artisans/maintenance dans le budget maison |
| IM5 | Planning → Courses | Pas de validation post-achat (acheté vs planifié → apprentissage substitutions) |
| IM6 | Dashboard → Modules | Dashboard read-only, pas d'actions rapides bidirectionnelles |
| IM7 | Chat IA → Events | Contexte chat reconstruit manuellement, pas événementiel |

---

## 5. Consolidation SQL

### État actuel

```
sql/
├── INIT_COMPLET.sql              ← Généré automatiquement (~5000 lignes)
├── schema/                       ← 18 fichiers source (01-99)
│   ├── 01_extensions.sql
│   ├── 02_functions.sql
│   ├── ...
│   ├── 16_seed_data.sql
│   ├── 17_migrations_absorbees.sql  ← Migrations historiques absorbées
│   └── 99_footer.sql
└── migrations/                   ← 6 fichiers (V003-V008) + README
    ├── V003__sprint13_canaux_notifications.sql
    ├── V004__logs_securite_admin_only.sql
    ├── V005__phase2_sql_consolidation.sql
    ├── V006__phase7_jobs_automations.sql
    ├── V007__module_habitat.sql
    └── V008__phase4_features_manquantes.sql
```

### Problèmes identifiés

| # | Problème | Action |
|---|---|---|
| S1 | Fichier `17_migrations_absorbees.sql` — contient le texte des anciennes migrations gardé par historique | Supprimer (l'historique est dans git) |
| S2 | Dossier `migrations/` avec 6 fichiers V003-V008 déjà absorbés dans `schema/` | Supprimer (dev mode, pas besoin de versioning) |
| S3 | Noms de migrations contiennent "sprint13", "phase2", "phase7", "phase4" | Opaque |
| S4 | `INIT_COMPLET.sql` est regénéré automatiquement → OK, rien à changer | — |
| S5 | 156 tables — vérifier si certaines sont inutilisées (gamification minimale, contrats non voulus) | Audit à faire |

### Tables potentiellement à supprimer

| Table | Raison |
|---|---|
| `contrats` | Utilisateur pas intéressé par les alertes contrats |
| `garanties` | Aucun intérêt pour les garanties (préf. explicite) |
| `incidents_sav` | Lié aux garanties → à supprimer |
| Tables gamification au-delà du sport | Gamification limitée au sport/Garmin uniquement |

### Plan SQL

1. Supprimer `sql/migrations/` (les migrations sont absorbées, on est en dev)
2. Supprimer `sql/schema/17_migrations_absorbees.sql`
3. Audit des tables inutilisées (contrats, garanties, SAV)
4. Regénérer `INIT_COMPLET.sql` après nettoyage
5. Garder le workflow `schema/ → regenerate_init.py → INIT_COMPLET.sql`

---

## 6. Interactions intra-modules

### Cuisine (flux interne bien connecté)

```
Recettes ──→ Planning ──→ Courses ──→ Inventaire
    ↑            │            │            │
    │            ↓            ↓            ↓
    ←── Suggestions IA   Prédictions    Péremption
    ←── Batch Cooking                   Anti-gaspillage
    ←── Import URL/PDF
```

### Famille (flux interne)

```
Profils famille ──→ Jules (développement) ──→ Nutrition adaptée
        │               │
        ↓               ↓
    Activités ←──── Weekend IA ──→ Suggestions sorties
        │
        ↓
    Budget famille ──→ Anomalies IA ──→ Alertes
    Anniversaires ──→ Rappels
    Documents ──→ Expirations
```

### Maison (flux interne)

```
Projets ──→ Tâches ──→ Entretien routinier
    │           │            │
    ↓           ↓            ↓
Artisans    Fiche IA    Diagnostics IA (photo)
    │                        │
    ↓                        ↓
Devis comparatif        Recommandations artisans
                             │
Jardin ──→ Zones → Plantes → Alertes météo
Énergie ──→ Compteurs → Anomalies IA
Meubles ──→ Inventaire maison
```

### Jeux (flux interne)

```
Paris sportifs ──→ Bankroll ──→ P&L ──→ Dashboard jeux
Loto ──→ Tirages ──→ Statistiques ──→ Heatmaps
Euromillions ──→ IA prédiction ──→ Grilles
```

---

## 7. Interactions inter-modules existantes

### Carte des 23 bridges existants

```
CUISINE ←──────────────────────────────→ FAMILLE
  │  jardin→recettes                        │  jules→nutrition
  │  péremption→recettes                    │  weekend→courses
  │  batch→inventaire                       │  budget→anomalie
  │  inventaire→planning                    │  voyages→budget
  │  saison→menu                            │  meteo→activités
  │  planning→voyage                        │  garmin→health
  │  courses→budget                         │  documents→notifications
  │                                         │  documents→calendrier
  │                                         │  budget→jeux (séparé)
  │                                         │  anniversaires→budget
  ↓                                         ↓
MAISON ←────────────────────────────────→ UTILITAIRES
  │  entretien→courses                      │  chat→contexte tous modules
  │  jardin→entretien
  │  charges→énergie
  │  énergie→cuisine
  │  diagnostics→IA
```

### Ponts qui fonctionnent bien

| Pont | Flow | Qualité |
|---|---|---|
| Jardin → Recettes | Récolte jardin → suggestions recettes semaine suivante | Excellent |
| Péremption → Recettes | Ingrédients bientôt périmés → recettes adaptées | Excellent |
| Weekend → Courses | Activités weekend → fournitures shopping | Bon |
| Budget → Anomalies | Dépassement +30% → alerte proactive | Bon |
| Jules → Nutrition | Courbes croissance → portions/nutriments adaptés | Excellent |
| Entretien → Courses | Tâches ménage → produits à acheter | Bon |
| Chat IA → Contexte | Agrège données tous modules pour chat contextuel | Bon |

---

## 8. Interactions inter-modules manquantes

### Haute priorité

| # | Pont manquant | Modules | Description | Valeur |
|---|---|---|---|---|
| NIM1 | Inventaire → Budget alimentation | Inventaire ↔ Famille:Budget | Tracker le coût/ingrédient pour prévoir le budget nourriture | Prévision budget alimentaire basée sur consommation réelle |
| NIM2 | Planning → Jardin (boucle retour) | Planning ↔ Maison:Jardin | Les ingrédients jardin non utilisés en planning → ajuster la production | Moins de gaspillage jardin |
| NIM3 | Garmin/Santé → Cuisine adultes | Famille:Garmin ↔ Cuisine | Niveaux d'activité → recommandations nutritionnelles adultes | Nutrition personnalisée au-delà de Jules |
| NIM4 | Dashboard → Actions rapides | Dashboard ↔ Tous | "Anomalie budget détectée" → clic → action directe dans le module | Réactivité utilisateur |

### Priorité moyenne

| # | Pont manquant | Modules | Description |
|---|---|---|---|
| NIM5 | Entretien → Budget maison | Maison:Entretien ↔ Famille:Budget | Dépenses artisans/maintenance trackées dans le budget |
| NIM6 | Courses → Planning (validation post-achat) | Cuisine:Courses ↔ Cuisine:Planning | Ce qui a été acheté vs planifié → apprentissage des substitutions |
| NIM7 | Inventaire → Rotation FIFO | Inventaire | Suivi premier-entré/premier-sorti pour la conservation |
| NIM8 | Chat IA → Event Bus | Utilitaires:Chat ↔ Core:Events | Contexte chat mis à jour automatiquement via événements |

---

## 9. Opportunités IA

### AI existante (38 services BaseAIService)

| Module | Services IA | Fonctionnalités |
|---|---|---|
| Cuisine | 7 | Suggestions recettes, import intelligent, enrichissement, batch cooking IA, versions Jules |
| Famille | 8 | Jules développement, budget anomalies, achats Vinted, weekend, soirée, résumé hebdo |
| Maison | 7 | Entretien, diagnostics photo (Pixtral), énergie anomalies, conseiller, jardin, fiche tâche |
| Core/Outils | 8 | Chat IA, assistant proactif, briefing matinal, suggestions cross-module, prévisions budget |
| Dashboard | 2 | Résumé famille IA, anomalies financières |
| Jeux | 2 | Euromillions IA, Jeux AI |
| Habitat | 2 | Plans IA, déco suggestions |
| Rapports | 1 | Bilan mensuel |
| Intégrations | 2 | Multimodal (images), factures OCR |

### IA manquante — à ajouter

| # | Service IA proposé | Module | Fonctionnalité |
|---|---|---|---|
| IA1 | `InventaireAIService` | Inventaire | Prédiction de consommation, seuils de réapprovisionnement intelligents, rotation FIFO |
| IA2 | `PlanningAIService` dédié | Planning | Optimisation nutritionnelle des repas, scoring de variété, suggestions de simplification semaine chargée |
| IA3 | `HabitudesAIService` | Core | Analyse des habitudes (routines respectées, tendances), suggestions personnalisées |
| IA4 | `ProjetsMaisonAIService` | Maison:Projets | Estimation complexité/timeline de projets, budget prévisionnel, matching artisans |
| IA5 | `MeteoImpactAIService` | Core | Impact météo cross-module (jardin + activités + recettes + énergie en un seul service) |
| IA6 | `NutritionFamilleAIService` | Cuisine/Famille | Extension Jules → toute la famille, basé sur Garmin + recettes planifiées |
| IA7 | Enrichissement contexte chat via événements | Utilitaires | Chat IA avec contexte temps-réel (event-driven au lieu de requêtes DB) |

---

## 10. Jobs automatiques (CRON)

### Inventaire complet des 51 jobs

| Heure | Job | Module | Type |
|---|---|---|---|
| 01:00 | `backup_donnees_critiques` | Core | Backup |
| 02:00 | `nettoyage_cache_7j` | Core | Nettoyage |
| 03:00 | `enrichissement_catalogues` (mensuel) | Maison | IA |
| 03:30 | `purge_logs_anciens_mensuelle` | Core | Nettoyage |
| 05:30 | `sync_calendrier_scolaire` | Famille | Sync |
| 05:45 | `sync_routines_planning` | Maison | Sync |
| 06:00 | `alertes_peremption_48h` | Inventaire | Alerte |
| 06:00 | `alerte_stock_bas` | Inventaire | Alerte |
| 06:00 | `garmin_sync_matinal` | Famille | Sync |
| 06:00 | `rappels_jardin_saisonniers` | Maison | Rappel |
| 06:15 | `sync_recoltes_inventaire` | Maison | Sync |
| 06:30 | `sync_voyages_calendrier` | Famille | Sync |
| 07:00 | `rappels_famille` (anniversaires, docs, crèche, jalons) | Famille | Alerte |
| 07:00 | `veille_emploi` | Innovations | Veille |
| 07:15 | `suggestions_activites_meteo` | Famille | IA |
| 07:30 | `sync_charges_dashboard` | Dashboard | Sync |
| 07:30 | `digest_whatsapp_matinal` | Notifications | Push |
| 08:00 | `anniversaires_j30` | Famille | Alerte |
| 08:00 | `rappels_maison` (entretien, contrats) | Maison | Alerte |
| 08:00 | `resume_jardin_saisonnier` (mensuel) | Maison | Rapport |
| 08:15 | `rapport_mensuel_budget` | Famille | Rapport |
| 08:30 | `rappels_generaux` (inventaire, repas du soir) | Core | Alerte |
| 09:00 | `digest_ntfy` | Notifications | Push |
| 09:00 | `push_quotidien` | Notifications | Push |
| 09:00 | `controle_contrats_garanties` (mensuel) | Maison | Alerte |
| 09:15 | `check_garanties_expirant` | Maison | Alerte |
| 09:30 | `rapport_maison_mensuel` | Maison | Rapport |
| 11:30 | `recette_du_jour_push` | Cuisine | Push |
| 12:00 | `astuce_anti_gaspillage` | Cuisine | Astuce |
| 12:15 | `sync_veille_habitat` | Maison | Sync |
| 18:00 | `alertes_energie` | Maison | Alerte |
| 18:00 | `push_contextuel_soir` | Notifications | Push |
| 18:00 | `rappel_courses` | Notifications | Alerte |
| 20:00 | `alertes_budget_seuil` | Famille | Alerte |
| 20:00 | `sync_jeux_budget` | Jeux | Sync |
| 22:00 | `sync_tirages_loto_euromillions` (mar/ven) | Jeux | Sync |
| 22:15 | `resultat_tirage_loto` (mar/ven) | Jeux | Rapport |
| 23:00 | `sync_google_calendar` | Famille | Sync |
| 5 min | `automations_runner` | Core | Runner |
| 3h | `stock_critique_zero` | Inventaire | Alerte |
| 2h | `digest_notifications_queue` | Notifications | Push |
| Lun 6:00 | `entretien_saisonnier` | Maison | Tâche |
| Dim 4:00 | `backup_auto_hebdo_json` | Core | Backup |
| Dim 18:00 | `rapport_budget_hebdo` | Famille | Rapport |
| Dim 19:00 | `planning_semaine_si_vide` | Cuisine | Auto-plan |
| Dim 20:00 | `score_bien_etre_hebdo` | Dashboard | Score |
| Dim 20:00 | `analyse_nutrition_hebdo` | Cuisine | Analyse |
| Dim 20:00 | `points_famille_hebdo` | Dashboard | Score |
| Dim 20:30 | `resume_hebdo_ia` | IA | Résumé |
| Dim 20:30 | `recap_weekend_dimanche_soir` | Famille | Résumé |
| Ven 16:00 | `prediction_courses_weekly` | Cuisine | Prédiction |
| Ven 17:00 | `score_weekend` | Dashboard | Score |
| Lun 9:00 | `resume_hebdo` | IA | Rapport |
| Mensuel 1er, 3:00 | `nouveau_recette_saison` | Cuisine | IA |
| Trimestriel, 1er 6:00 | `tache_jardin_saisonniere` | Maison | Tâche |

### CRON jobs à retirer (préférences utilisateur)

| Job | Raison |
|---|---|
| `controle_contrats_garanties` | Pas intéressé par les contrats/garanties |
| `check_garanties_expirant` | Garanties : aucun intérêt |

### CRON jobs manquants à ajouter

| Job proposé | Module | Schedule | Description |
|---|---|---|---|
| `job_expiration_recettes_suggestion` | Cuisine | Quotidien 10:00 | Ingrédients expirant → push recette adaptée |
| `job_stock_prediction_reapprovisionnement` | Inventaire | Hebdo lun 8:00 | Prédiction des articles à racheter cette semaine |
| `job_variete_repas_alerte` | Planning | Dim 17:00 | Alerte si planning semaine trop monotone |
| `job_tendances_activites_famille` | Famille | Hebdo dim 19:30 | Analyse tendances engagement activités |
| `job_energie_peak_detection` | Maison | Quotidien 19:00 | Détection pics de consommation énergie |
| `job_nutrition_adultes_weekly` | Cuisine/Famille | Dim 20:15 | Bilan nutritionnel adultes (via Garmin) |
| `job_briefing_matinal_push` | Outils | Quotidien 7:00 | Push du briefing matinal IA |
| `job_jardin_feedback_planning` | Maison/Cuisine | Hebdo dim 18:30 | Récoltes jardin non utilisées → feedback |

---

## 11. Notifications — WhatsApp, Email, Push

### Canaux actifs

| Canal | Technologie | État |
|---|---|---|
| **Push web** | VAPID protocol (navigateur) | Actif |
| **ntfy** | ntfy.sh HTTP topic | Actif |
| **Email** | Resend API | Actif |
| **WhatsApp** | WhatsApp Business API | Actif |

### Notifications WhatsApp existantes

| Feature | Déclencheur | Description |
|---|---|---|
| Digest matinal | CRON 07:30 | Repas du jour + tâches + péremptions |
| Liste courses partagée | À la demande | Shopping list via WhatsApp |
| Rappel activité Jules | Événement | Notification activité Jules |
| Résultats paris | Événement | Résultats paris sportifs |
| Rappel courses soir | CRON 18:00 | Articles restants à acheter |

### WhatsApp manquant — à ajouter

| # | Notification WhatsApp proposée | Déclencheur | Contenu |
|---|---|---|---|
| WA1 | Suggestion recette du jour | CRON 11:30 | Recette adaptée au stock + saison |
| WA2 | Alerte diagnostic maison | Événement | Résultat diagnostic + recommandation artisan |
| WA3 | Résumé weekend suggestions | CRON ven 18:00 | Activités suggérées pour le weekend |
| WA4 | Alerte budget dépassement | Événement | Dépassement catégorie budget |
| WA5 | Bilan nutrition semaine | CRON dim 20:30 | Résumé nutritionnel simplifié |
| WA6 | Rappel entretien maison | CRON selon tâche | Tâche maintenance à faire aujourd'hui |
| WA7 | Commande vocale rapide | À la demande | "Ajoute lait à la liste de courses" via WhatsApp |

### Email manquant

| # | Email proposé | Fréquence | Contenu |
|---|---|---|---|
| EM1 | Rapport mensuel famille complet | Mensuel 1er, 9:00 | PDF : budget + nutrition + maison + jardin + Jules |
| EM2 | Rapport trimestriel maison | Trimestriel | État projets + énergie + jardin + entretien |

---

## 12. Mode Admin manuel

### État actuel

Le mode admin est **bien développé** avec les fonctionnalités suivantes :

| Fonctionnalité | Route | Frontend |
|---|---|---|
| Audit logs | `GET /admin/audit-logs` | Page admin/logs |
| CRON : lister jobs | `GET /admin/jobs` | Page admin/jobs |
| CRON : lancer manuellement | `POST /admin/jobs/{id}/run` | Bouton "Run Now" |
| CRON : dry run | `POST /admin/jobs/{id}/run?dry_run=true` | Toggle dry run |
| CRON : logs exécution | `GET /admin/jobs/{id}/logs` | Historique |
| Notifications : test | `POST /admin/notifications/test` | Page admin/notifications |
| Cache : stats | `GET /admin/cache/stats` | Page admin/cache |
| Cache : purge | `POST /admin/cache/clear` | Bouton purge |
| Services health | `GET /admin/services/health` | Page admin/services |
| DB cohérence | `GET /admin/db/coherence` | — |
| Utilisateurs | `GET /admin/users` | Page admin/utilisateurs |
| WhatsApp test | — | Page admin/whatsapp-test |
| Feature flags | — | Page admin/feature-flags |
| IA métriques | — | Page admin/ia-metrics |
| Event bus monitor | — | Page admin/events |
| Console API | — | Page admin/console |
| SQL views | — | Page admin/sql-views |

### Améliorations admin proposées

| # | Amélioration | Description |
|---|---|---|
| ADM1 | Dashboard admin unifié | Vue unique : santé services + derniers jobs + alertes + métriques IA |
| ADM2 | Bouton "Lancer tous les jobs du matin" | Exécuter groupé les jobs 06:00-09:00 en un clic |
| ADM3 | Mode "simuler une journée" | Lancer séquentiellement tous les jobs d'une journée type (dry run) |
| ADM4 | Log temps-réel (WebSocket) | Stream des logs d'exécution en direct dans la console admin |
| ADM5 | Comparer résultats dry run vs vraie exécution | Tableau comparatif pour valider avant prod |
| ADM6 | Export audit logs en PDF | Rapport audit téléchargeable |
| ADM7 | Panneau admin flottant (déjà créé côté front) | S'assurer qu'il est invisible pour l'utilisateur normal |

### Visibilité utilisateur

Le panneau admin (`panneau-admin-flottant.tsx`) est déjà un composant séparé. **Vérifier** :
- Qu'il est protégé par `require_role("admin")` côté backend
- Qu'il est conditionnel au rôle admin côté frontend
- Qu'il n'apparaît dans aucune navigation utilisateur standard

---

## 13. Tests — Couverture et manques

### État actuel

| Zone | Fichiers test | Couverture estimée | Qualité |
|---|---|---|---|
| Routes API | 48 fichiers | ~85% des endpoints | Bonne |
| Services cuisine | 8+ fichiers | ~70% | Bonne |
| Services famille | 5+ fichiers | ~65% | Correcte |
| Services maison | 3+ fichiers | ~50% | À compléter |
| Services jeux | 3 fichiers | ~60% | Correcte |
| Core (cache, events, config) | 19 fichiers | ~80% | Bonne |
| Frontend (Vitest) | 71+ fichiers | ~40% | À compléter |
| E2E (Playwright) | Minimal | ~10% | Insuffisant |
| Benchmarks | 1+ fichier | N/A | Présent |
| Load tests | 1+ fichier | N/A | Présent |

### Fichiers test à renommer (noms avec phase/sprint)

| Fichier actuel | Nouveau nom proposé |
|---|---|
| `test_phase_b.py` | `test_ia_avancee.py` |
| `test_cron_phase8.py` | `test_cron_notifications.py` |
| `test_cron_phase_d.py` | `test_cron_backup_rotation.py` |
| `test_notif_dispatcher_phase8.py` | `test_notif_dispatcher.py` |
| `test_gamification_phase9.py` | `test_gamification.py` |
| `test_jeux_phases_tuw.py` | `test_jeux_avances.py` |
| `test_sprint_d_event_subscribers.py` | `test_event_subscribers.py` |

### Tests manquants à créer

| # | Test | Module | Priorité |
|---|---|---|---|
| T1 | Tests inter-modules (23 bridges) | Cross-module | Haute |
| T2 | Tests E2E parcours cuisine complet (recette → planning → courses → inventaire) | E2E | Haute |
| T3 | Tests E2E parcours famille (Jules → nutrition → planning) | E2E | Haute |
| T4 | Tests services maison (projets, jardin, énergie) | Maison | Moyenne |
| T5 | Tests notifications multi-canal (WhatsApp, email, push, ntfy) | Notifications | Moyenne |
| T6 | Tests event bus end-to-end (publication → subscriber → action) | Events | Moyenne |
| T7 | Tests frontend composants domaine | Frontend | Moyenne |
| T8 | Tests visuels (Playwright screenshots) pour chaque page | Frontend | Basse |
| T9 | Tests de charge par module | Performance | Basse |
| T10 | Consolider `test_decorators.py` et `test_decorateurs.py` en un seul fichier | Core | Haute |

---

## 14. Documentation — État et manques

### État actuel (42+ fichiers)

| Catégorie | Fichiers | État |
|---|---|---|
| Architecture & API | ARCHITECTURE, API_REFERENCE, API_SCHEMAS, MODULES, SERVICES_REFERENCE | À jour |
| Base de données | ERD_SCHEMA, DATA_MODEL, SQLALCHEMY_SESSION_GUIDE | À jour |
| Infrastructure | DEPLOYMENT, MONITORING, SECURITY, PERFORMANCE, REDIS_SETUP | À jour |
| Admin | ADMIN_GUIDE, ADMIN_RUNBOOK | À jour |
| Fonctionnel | CRON_JOBS, NOTIFICATIONS, AUTOMATIONS, EVENT_BUS, INTER_MODULES | À jour |
| Tests | TESTING, TESTING_ADVANCED | À jour |
| Frontend | FRONTEND_ARCHITECTURE, DESIGN_SYSTEM, UI_COMPONENTS | À jour |
| Guides modules | guides/cuisine, famille, maison, jeux, planning, outils, dashboard | À jour |
| User guide | docs/user-guide/ | Présent |
| Intégrations | WHATSAPP_SETUP, WHATSAPP_COMMANDS, GOOGLE_ASSISTANT_SETUP, GARMIN | À jour |
| Dev | DEVELOPER_SETUP, CONTRIBUTING, TROUBLESHOOTING, MIGRATION_GUIDE | À jour |
| Historique | CHANGELOG_MODULES, ROADMAP | À mettre à jour |

### Documentation à nettoyer

| Fichier | Problème | Action |
|---|---|---|
| `CHANGELOG_MODULES.md` | Références phases/sprints historiques | Reformater par module sans noms de phase |
| `ROADMAP.md` | Références sprints 1-10 historiques | Mettre à jour avec le nouveau plan |
| `HABITAT_MODULE.md` | Référence "Phase 10" | Retirer référence phase |
| `GAMIFICATION.md` | Décrit une gamification étendue (rejetée) | Réduire scope au sport/Garmin uniquement |
| `audit_output.txt` | Fichier binaire illisible à la racine | Supprimer |
| Documents avec "phase" dans les titres de sections | ~5 fichiers | Remplacer par nom de domaine fonctionnel |

### Documentation manquante

| # | Document | Contenu |
|---|---|---|
| D1 | `docs/INTER_MODULES_GUIDE.md` | Guide développeur pour créer un nouveau bridge inter-module |
| D2 | `docs/AI_INTEGRATION_GUIDE.md` | Comment créer un nouveau service IA (BaseAIService pattern) |
| D3 | `docs/CRON_DEVELOPMENT.md` | Comment ajouter un nouveau job CRON |
| D4 | `docs/USER_FLOWS.md` | Parcours utilisateur documentés (cuisine, famille, maison) |
| D5 | Mise à jour `ROADMAP.md` | Roadmap alignée sur ce nouveau plan |

---

## 15. UI/UX — Améliorations et modernisation

### Forces actuelles

| Aspect | État | Détail |
|---|---|---|
| Design system | shadcn/ui (29 composants) | Cohérent, moderne |
| Responsive | Desktop + Tablet + Mobile | Bottom nav, sidebar colapsable |
| Loading states | 13 loading.tsx | Skeletons, loaders |
| Error boundaries | 13 error.tsx | Par module |
| Charts | Recharts + D3 | 6 composants graphiques |
| 3D | Three.js + @react-three | Plan 3D maison |
| Animations | Framer Motion | Transitions |
| DnD | @dnd-kit | Dashboard widgets drag & drop |
| PWA | Service worker + install | Installable |
| Offline | Bandeau hors-ligne + sync | Détection + file d'attente |
| Accessibilité | Radix UI base | Sémantique, clavier |

### Améliorations UI proposées

#### Visualisations 2D/3D

| # | Amélioration | Module | Description |
|---|---|---|---|
| UI1 | Timeline interactive famille | Famille | Frise chronologique zoomable : jalons Jules, anniversaires, voyages, événements |
| UI2 | Carte thermique planning repas | Cuisine | Heatmap nutritionnel sur le mois (carences, excès, variété) |
| UI3 | Vue jardin 2D interactive | Maison:Jardin | Plan du jardin avec zones cliquables, état des plantes, prochaines actions |
| UI4 | Graphe réseau inter-modules | Admin | Visualisation force-directed des connexions entre modules (déjà un composant `graphe-reseau-modules.tsx`) |
| UI5 | Dashboard glissières temporelles | Dashboard | Slider pour comparer les métriques mois par mois |
| UI6 | Treemap budget interactif | Famille:Budget | Treemap cliquable des catégories de dépenses avec drill-down |
| UI7 | Graphe Sankey des flux financiers | Famille:Budget | Revenus → catégories → sous-catégories |
| UI8 | Vue calendrier énergie | Maison:Énergie | Calendrier coloré par consommation jour/jour |
| UI9 | Radar nutritionnel famille | Cuisine/Famille | Radar chart : protéines, glucides, lipides, fibres, vitamines — toute la famille |
| UI10 | Animation batch cooking étapes | Cuisine:Batch | Vue timeline des étapes batch cooking avec progression animée |

#### UX et simplification

| # | Amélioration | Description |
|---|---|---|
| UX1 | Onboarding guidé | Tour interactif (~5 étapes) pour nouveaux utilisateurs — composant `tour-onboarding.tsx` déjà créé |
| UX2 | Actions rapides desde dashboard | Boutons flottants : "Ajouter course", "Planifier repas", "Nouvelle tâche" |
| UX3 | Recherche globale améliorée | `menu-commandes.tsx` (Ctrl+K) avec résultats plus riches (aperçu recettes, preview tâches) |
| UX4 | Undo/Redo sur actions destructives | Toast avec bouton "Annuler" pour suppressions |
| UX5 | Raccourcis clavier par page | N pour nouveau, E pour éditer, S pour sauvegarder, Suppr pour supprimer |
| UX6 | Bulk actions sur les listes | Sélection multiple + actions groupées (supprimer, déplacer, compléter) |
| UX7 | Filtres avancés en sidebar | Panneau latéral de filtres pour recettes, courses, tâches |
| UX8 | Dark mode peaufiné | Vérifier cohérence graphiques/charts en mode sombre |
| UX9 | Auto-save brouillons | Sauvegarde automatique des formulaires en cours |
| UX10 | Swipe gestures mobiles | Déjà `swipeable-item.tsx` — étendre à toutes les listes |

---

## 16. Nettoyage legacy et rétrocompatibilité

### Fichiers à supprimer

| Fichier | Type | Raison |
|---|---|---|
| `src/api/routes/jeux.py.bak` | Backup | Artefact de refactoring |
| `audit_output.txt` | Artefact | Fichier binaire illisible |
| `sql/schema/17_migrations_absorbees.sql` | SQL legacy | Historique git suffit |
| `sql/migrations/` (tout le dossier) | Migrations absorbées | Dev mode, pas besoin de versioning |
| `scripts/_archive/rename_factory_functions.py` | Script one-shot | Terminé, historique dans git |
| `scripts/_archive/split_jeux_routes.py` | Script one-shot | Terminé, historique dans git |

### Code legacy à retirer

| Code | Fichier | Action |
|---|---|---|
| Champs `legacy` dans Planning | `src/core/models/planning.py` L45 | Supprimer le champ obsolète |
| Champs `legacy` dans Jeux | `src/core/models/jeux.py` L216, 248, 765 | Supprimer les propriétés compat |
| Validators legacy dans Phase B | `src/api/schemas/phase_b.py` L37, 45 | Supprimer le support ancien format |
| Format cache legacy `.cache` | `src/core/caching/file.py` L153 | Supprimer cleanup pickle |
| Patterns legacy invalidation | `src/core/caching/invalidation_listener.py` L55 | Simplifier |
| Aliases Sprint 12 A3 | 10+ services | Audit des appelants puis suppression |
| CRON garanties/contrats | `jobs.py`, `jobs_schedule.py` | Supprimer (préf. utilisateur) |

### Tables SQL à supprimer

| Table | Raison |
|---|---|
| `contrats` | Pas intéressé par les alertes contrats |
| `garanties` | Aucun intérêt pour les garanties |
| `incidents_sav` | Lié aux garanties |
| Tables gamification étendues (si au-delà sport/Garmin) | Gamification limitée |

---

## 17. Nommage des fichiers et commentaires

### Fichiers à renommer (retirer noms de phase/sprint)

| Fichier actuel | Nouveau nom | Type |
|---|---|---|
| `src/api/routes/ia_phase_b.py` | `src/api/routes/ia_bridges.py` | Route |
| `src/api/routes/innovations.py` | `src/api/routes/fonctionnalites_avancees.py` | Route |
| `src/api/schemas/phase_b.py` | `src/api/schemas/ia_bridges.py` | Schéma |
| `src/api/schemas/innovations.py` | `src/api/schemas/fonctionnalites_avancees.py` | Schéma |
| `src/core/models/notifications_sprint_e.py` | `src/core/models/notifications_historique.py` | Modèle |
| `src/services/core/cron/jobs_phase_d.py` | `src/services/core/cron/jobs_backup.py` | Service |
| `src/services/core/cron/jobs_sprint_e.py` | `src/services/core/cron/jobs_notifications.py` | Service |
| `frontend/src/app/(app)/innovations/` | `frontend/src/app/(app)/avance/` | Page |
| `frontend/src/bibliotheque/api/innovations.ts` | `frontend/src/bibliotheque/api/avance.ts` | API client |
| `frontend/src/bibliotheque/api/phase-b.ts` | `frontend/src/bibliotheque/api/ia-bridges.ts` | API client |
| `tests/test_phase_b.py` | `tests/test_ia_avancee.py` | Test |
| `tests/services/test_cron_phase8.py` | `tests/services/test_cron_notifications.py` | Test |
| `tests/services/test_cron_phase_d.py` | `tests/services/test_cron_backup.py` | Test |
| `tests/services/test_notif_dispatcher_phase8.py` | `tests/services/test_notif_dispatcher.py` | Test |
| `tests/services/test_gamification_phase9.py` | `tests/services/test_gamification.py` | Test |
| `tests/services/test_jeux_phases_tuw.py` | `tests/services/test_jeux_avances.py` | Test |
| `tests/services/core/test_sprint_d_event_subscribers.py` | `tests/services/core/test_event_subscribers.py` | Test |

### Commentaires à mettre à jour

**Objectif** : Retirer toute mention de "Phase X", "Sprint Y" des commentaires code source.

| Pattern à chercher | Remplacement | Fichiers estimés |
|---|---|---|
| `# Phase A` / `Phase B` / ... | Description fonctionnelle de ce que fait le code | ~100 occurrences |
| `# Sprint 6` / `Sprint 12` / ... | Retirer ou remplacer par contexte fonctionnel | ~30 occurrences |
| `Sprint 12 A3` dans aliases | Retirer la mention et l'alias si plus d'appelant | ~10 services |
| `Phase 10` dans docstrings | Retirer | ~5 fichiers |

### Fichier fourre-tout à restructurer

| Fichier | Problème | Solution |
|---|---|---|
| `src/api/routes/innovations.py` | ~30 endpoints de nature différente (pilot mode, family score, journal, PDF) | Distribuer dans les modules concernés ou renommer en `fonctionnalites_avancees.py` |
| `src/services/innovations/service.py` | Service monolithique | Séparer par fonctionnalité ou regrouper dans les services existants |
| `src/api/routes/admin.py` | ~65 endpoints (le plus gros fichier) | OK car c'est admin, mais envisager un split par sous-domaine (admin_cron, admin_cache, admin_audit) |

---

## 18. Simplification du flux utilisateur

### Principes

1. **L'utilisateur ne voit jamais la complexité** — pas de Phase A/B, pas d'innovations, pas de bridges visibles
2. **Actions en 1-3 clics max** — les flux principaux doivent être rapides
3. **L'IA travaille en arrière-plan** — suggestions proactives, pas de configuration manuelle
4. **Notifications intelligentes** — pas de spam, digest groupés, canal préféré auto-détecté
5. **Mode admin invisible** — panneau flottant accessible uniquement par rôle admin, jamais dans la nav

### Flux simplifiés à implémenter

| Flux | Étapes utilisateur | Travail IA en coulisses |
|---|---|---|
| **Planifier la semaine** | 1. Ouvrir Planning → 2. "Générer ma semaine" → 3. Valider/modifier | IA analyse stock, saison, historique préférences, météo, Jules |
| **Faire les courses** | 1. Clic "Liste de courses" → 2. Ajouter si besoin → 3. Valider | Générée auto depuis planning + stock bas + prédictions |
| **Après les courses** | 1. Scanner ou cocher "acheté" | Inventaire mis à jour, budget actualisé, prédictions ajustées |
| **Entretien maison** | 1. Voir tâches du jour (push) → 2. Marquer fait | IA planifie selon saison, historique, météo |
| **Suivi Jules** | 1. Ouvrir Jules → 2. Voir dashboard | Jalons auto-détectés, nutrition adaptée, courbes OMS |
| **Budget** | 1. Ouvrir Budget → voir statut | Catégorisation auto, alertes anomalies, prévisions |
| **Jardin** | 1. Ouvrir Jardin → voir tâches | Alertes météo, saisons, récoltes → auto-suggestion recettes |

### Pages frontend à supprimer ou masquer

| Page | Action | Raison |
|---|---|---|
| `cuisine/courses/scan-ticket/` | Supprimer | OCR désactivé (préf.) |
| `jeux/ocr-ticket/` | Supprimer | OCR désactivé (préf.) |
| `innovations/` | Redistribuer contenu vers modules concernés | Pas un module autonome pour l'utilisateur |

---

## 19. Innovations et axes d'amélioration

### Axes identifiés automatiquement

| # | Axe | Module | Description | Effort |
|---|---|---|---|---|
| IN1 | **Apprentissage des préférences** | Core | Système qui apprend les goûts, habitudes, rythmes de la famille au fil du temps | Moyen |
| IN2 | **Score de bien-être familial** | Dashboard | Indicateur composite : nutrition + activités + budget + maison + Jules | Faible |
| IN3 | **Mode saison** | Tous modules | Adaptation automatique cross-modules selon la saison (recettes, jardin, entretien, activités, énergie) | Moyen |
| IN4 | **Intelligence contextuelle météo** | Tous modules | Un seul service météo qui impacte jardin + activités + recettes + énergie + entretien | Moyen |
| IN5 | **Rapport PDF mensuel unifié** | Rapports | Un seul PDF mensuel : résumé famille + budget + nutrition + maison + jardin + Jules | Faible |
| IN6 | **Quick actions depuis n'importe où** | UI | Barre d'action universelle : "Ajoute tomates à la liste" sans changer de page | Faible |
| IN7 | **Mode tablette optimisé** | UI | Dashboard tablette spécifique (widget-tablette existe déjà) avec vue magazine | Moyen |
| IN8 | **Historique familial timeline** | Famille | Frise chronologique des événements marquants (jalons Jules, voyages, projets terminés) | Moyen |
| IN9 | **Planification automatique hebdo complète** | Core | Dim soir : auto-build planning repas + courses + tâches ménage + jardin en un bloc | Élevé |
| IN10 | **Mode vacances** | Tous modules | Toggle "En vacances" qui adapte courses (mini), suspend entretien, active checklist voyage | Faible |
| IN11 | **Insights IA proactifs** | Core | Push quotidien de 1-2 insights (pas de spam) : "Tu n'as pas mangé de poisson depuis 2 semaines" | Moyen |
| IN12 | **Tableau de bord énergie temps-réel** | Maison | Si compteur Linky connecté : visualisation en temps réel de la conso | Élevé |
| IN13 | **Suggestions batch cooking intelligentes** | Cuisine | IA qui propose un plan batch cooking optimal basé sur planning de la semaine | Moyen |
| IN14 | **Journal automatique** | Famille | Journal de bord auto-alimenté par les actions (repas, activités, événements) | Faible |
| IN15 | **Comparateur de prix automatique** | Cuisine/Courses | Veille prix automatique sur les ingrédients fréquents (API scraping) | Élevé |
| IN16 | **Assistant WhatsApp conversationnel** | Notifications | Répondre aux messages WhatsApp : "Oui", "Non", "Ajoute X" → actions dans l'app | Élevé |
| IN17 | **Cartes de synthèse partageables** | Export | Générer une carte visuelle partageable (image) pour recette, planning, etc. | Moyen |

---

## 20. Plan d'action structuré

### Phase 1 — Nettoyage et stabilisation (priorité immédiate)

| # | Tâche | Effort | Impact |
|---|---|---|---|
| 1.1 | Supprimer fichiers legacy (jeux.py.bak, audit_output.txt, archive scripts) | Très faible | Propreté |
| 1.2 | Supprimer sql/migrations/ et 17_migrations_absorbees.sql | Faible | Propreté SQL |
| 1.3 | Audit et suppression tables SQL inutilisées (garanties, contrats, SAV) | Faible | Cohérence |
| 1.4 | Renommer les 17 fichiers avec noms de phase/sprint (voir §17) | Moyen | Maintenabilité |
| 1.5 | Retirer ~100 commentaires de phase/sprint dans le code source | Moyen | Maintenabilité |
| 1.6 | Supprimer code legacy (champs planning, jeux, validators phase_b, cache pickle) | Moyen | Propreté |
| 1.7 | Supprimer aliases rétrocompat Sprint 12 A3 (après audit appelants) | Moyen | Propreté |
| 1.8 | Supprimer CRON garanties/contrats | Faible | Préf. utilisateur |
| 1.9 | Supprimer pages frontend OCR (scan-ticket courses + jeux) | Faible | Propreté |
| 1.10 | Consolider test_decorators.py + test_decorateurs.py | Faible | Propreté tests |
| 1.11 | Restructurer innovations.py (routes + services) | Moyen | Clarté |
| 1.12 | Résoudre TODO(P1-06) auth_token.py (API Supabase officielle) | Moyen | Qualité |
| 1.13 | Regénérer INIT_COMPLET.sql après nettoyage | Faible | SQL propre |

### Phase 2 — Tests et documentation

| # | Tâche | Effort | Impact |
|---|---|---|---|
| 2.1 | Tests inter-modules (23 bridges) | Élevé | Fiabilité |
| 2.2 | Tests E2E parcours cuisine (recette → planning → courses → inventaire) | Élevé | Confiance |
| 2.3 | Tests E2E parcours famille (Jules → nutrition → planning) | Moyen | Confiance |
| 2.4 | Tests services maison (projets, jardin, énergie) | Moyen | Couverture |
| 2.5 | Tests notifications multi-canal | Moyen | Fiabilité |
| 2.6 | Tests event bus end-to-end | Moyen | Fiabilité |
| 2.7 | Renommer tests phase/sprint (7 fichiers) | Faible | Clarté |
| 2.8 | Nettoyer docs CHANGELOG/ROADMAP des refs phase | Faible | Clarté |
| 2.9 | Rédiger docs manquants (inter-modules guide, AI guide, CRON guide, user flows) | Moyen | Documentation |
| 2.10 | Mettre à jour GAMIFICATION.md (scope sport/Garmin uniquement) | Faible | Précision |

### Phase 3 — Interactions inter-modules et IA

| # | Tâche | Effort | Impact |
|---|---|---|---|
| 3.1 | Bridge Inventaire → Budget alimentation (NIM1) | Moyen | Budget précis |
| 3.2 | Bridge Planning → Jardin feedback loop (NIM2) | Moyen | Moins de gaspillage |
| 3.3 | Bridge Garmin/Santé → Cuisine adultes (NIM3) | Moyen | Nutrition personnalisée |
| 3.4 | Dashboard → Actions rapides bidirectionnelles (NIM4) | Moyen | Réactivité |
| 3.5 | Bridge Entretien → Budget maison (NIM5) | Faible | Suivi dépenses |
| 3.6 | Nouveau service `InventaireAIService` (IA1) | Moyen | Prédiction stock |
| 3.7 | Nouveau service `PlanningAIService` dédié (IA2) | Moyen | Optimisation repas |
| 3.8 | Service `MeteoImpactAIService` cross-module (IA5) | Moyen | Cohérence météo |
| 3.9 | Enrichir Event Bus (Famille, Jeux, Dashboard publient des événements) | Moyen | Couplage lâche |
| 3.10 | Chat IA → contexte event-driven (IA7) | Faible | Fraîcheur contexte |

### Phase 4 — CRON, notifications et automatisations

| # | Tâche | Effort | Impact |
|---|---|---|---|
| 4.1 | Ajouter 8 CRON jobs manquants (voir §10) | Moyen | Automatisation |
| 4.2 | WhatsApp : 7 nouvelles notifications (voir §11) | Moyen | Communication |
| 4.3 | Email : rapport mensuel et trimestriel | Faible | Rapports |
| 4.4 | Améliorations admin (ADM1-ADM7) | Moyen | Testabilité |
| 4.5 | Mode "simuler une journée" admin | Faible | Debug |
| 4.6 | Log temps-réel WebSocket admin | Moyen | Monitoring |

### Phase 5 — UI/UX et modernisation

| # | Tâche | Effort | Impact |
|---|---|---|---|
| 5.1 | Timeline interactive famille (UI1) | Élevé | Visualisation |
| 5.2 | Heatmap planning nutritionnel (UI2) | Moyen | Visualisation |
| 5.3 | Vue jardin 2D interactive (UI3) | Élevé | UX |
| 5.4 | Treemap budget interactif + Sankey (UI6, UI7) | Moyen | Visualisation |
| 5.5 | Calendrier énergie (UI8) | Moyen | Visualisation |
| 5.6 | Radar nutritionnel famille (UI9) | Faible | Visualisation |
| 5.7 | Quick actions universelles (UX2, IN6) | Moyen | UX |
| 5.8 | Recherche globale enrichie (UX3) | Moyen | UX |
| 5.9 | Undo/Redo sur suppressions (UX4) | Moyen | UX |
| 5.10 | Auto-save brouillons (UX9) | Moyen | UX |
| 5.11 | Dark mode peaufiné charts (UX8) | Faible | UI |
| 5.12 | Bulk actions listes (UX6) | Moyen | UX |

### Phase 6 — Innovations

| # | Tâche | Effort | Impact |
|---|---|---|---|
| 6.1 | Mode saison cross-module (IN3) | Moyen | Cohérence |
| 6.2 | Mode vacances (IN10) | Faible | UX |
| 6.3 | Insights IA proactifs quotidiens (IN11) | Moyen | Engagement |
| 6.4 | Journal automatique (IN14) | Faible | Mémoire familiale |
| 6.5 | Rapport PDF mensuel unifié (IN5) | Faible | Rapports |
| 6.6 | Planification hebdo complète automatique (IN9) | Élevé | Automation |
| 6.7 | Score de bien-être familial (IN2) | Faible | Dashboard |
| 6.8 | Apprentissage préférences (IN1) | Moyen | Personnalisation |
| 6.9 | Suggestions batch cooking intelligentes (IN13) | Moyen | Cuisine |
| 6.10 | Cartes visuelles partageables (IN17) | Moyen | Export |
| 6.11 | Mode tablette magazine (IN7) | Moyen | UI tablette |
| 6.12 | WhatsApp conversationnel (IN16) | Élevé | Communication |
| 6.13 | Comparateur prix auto (IN15) | Élevé | Budget |

---

## Résumé des priorités

| Priorité | Phase | Focus | Tâches |
|---|---|---|---|
| IMMÉDIATE | Phase 1 | Nettoyage, propreté codebase | 13 tâches |
| HAUTE | Phase 2 | Tests, documentation | 10 tâches |
| HAUTE | Phase 3 | Inter-modules, IA | 10 tâches |
| MOYENNE | Phase 4 | CRON, notifications, admin | 6 tâches |
| MOYENNE | Phase 5 | UI/UX modernisation | 12 tâches |
| BASSE | Phase 6 | Innovations | 13 tâches |

**Total : 64 tâches structurées en 6 phases progressives.**

> Ce document remplace entièrement l'ancienne analyse et le planning d'implémentation.
> Les phases sont nommées par sujet, pas par numéro arbitraire.
> Aucune tâche ne concerne les migrations ou le versioning (mode dev).
