# ANALYSE COMPLÈTE — Assistant Matanne

**Date d'audit** : 29 mars 2026
**Portée** : Backend (FastAPI/Python), Frontend (Next.js/TypeScript), SQL, Tests, Documentation, IA, Automatisations
**Objectif** : Audit exhaustif — bugs, gaps, interactions inter-modules, opportunités IA/jobs/notifications, plan d'amélioration

---

## Table des matières

1. [Vue d'ensemble & Métriques globales](#1-vue-densemble--métriques-globales)
2. [Architecture par module](#2-architecture-par-module)
3. [Audit SQL — Schéma & Consolidation](#3-audit-sql--schéma--consolidation)
4. [Bugs & Risques détectés](#4-bugs--risques-détectés)
5. [Gaps fonctionnels par module](#5-gaps-fonctionnels-par-module)
6. [Interactions intra-module (existantes)](#6-interactions-intra-module-existantes)
7. [Interactions inter-modules (existantes)](#7-interactions-inter-modules-existantes)
8. [Interactions inter-modules manquantes](#8-interactions-inter-modules-manquantes)
9. [Opportunités IA — Où ajouter de l'intelligence](#9-opportunités-ia--où-ajouter-de-lintelligence)
10. [Jobs automatiques & Cron](#10-jobs-automatiques--cron)
11. [Notifications — WhatsApp, Email, Push](#11-notifications--whatsapp-email-push)
12. [Mode Admin (lancer manuellement)](#12-mode-admin-lancer-manuellement)
13. [Moteur d'automatisation](#13-moteur-dautomatisation)
14. [Audit des Tests](#14-audit-des-tests)
15. [Audit de la Documentation](#15-audit-de-la-documentation)
16. [Organisation du code & Dette technique](#16-organisation-du-code--dette-technique)
17. [Axes d'amélioration & Innovation](#17-axes-damélioration--innovation)
18. [Plan d'action priorisé](#18-plan-daction-priorisé)
19. [Nouveau module — Projet Habitat](#19-nouveau-module--projet-habitat-déménagement--agrandissement--déco--jardin)

---

## 1. Vue d'ensemble & Métriques globales

### Inventaire complet

| Dimension | Quantité | État |
|-----------|----------|------|
| **Pages frontend** | 57 pages (+ 2 auth) | ✅ Toutes implémentées |
| **Routes API** | 300+ endpoints (36 fichiers routeurs) | ✅ Complet |
| **Schémas Pydantic** | 150+ classes (23 fichiers) | ⚠️ 8 classes stub (`pass`) |
| **Modèles SQLAlchemy** | 80+ modèles (30 fichiers) | ✅ Complet |
| **Tables SQL** | 150+ tables | ✅ Complet |
| **Services métier** | 100+ services (factory pattern) | ✅ Complet |
| **Fichiers de tests** | 186 fichiers | ⚠️ Gaps sur admin/cron/intégrations |
| **Cron jobs** | 19 tâches planifiées | ✅ Fonctionnel |
| **Documentation** | 25 fichiers markdown | ⚠️ Guides modules datés |
| **Composants UI** | 29 shadcn/ui + 40 spécialisés | ✅ Complet |
| **Hooks React** | 12 hooks custom | ✅ Complet |
| **Stores Zustand** | 4 stores + 3 tests | ✅ Minimal mais suffisant |
| **Clients API frontend** | 23 fichiers | ⚠️ Manque `admin.ts` |

### Score par dimension

| Dimension | Score | Commentaire |
|-----------|-------|-------------|
| Architecture | 9/10 | Excellente modularité, factory pattern, lazy loading |
| Sécurité | 9/10 | JWT, RBAC, RLS, rate limiting, CORS |
| Typage | 8/10 | Pydantic v2 + SQLAlchemy 2.0 + TypeScript, mais 30+ `# type: ignore` |
| Tests | 6/10 | 186 fichiers mais gaps critiques (admin 40%, cron 60%, WhatsApp 20%) |
| Documentation | 6/10 | Architecture à jour, guides modules datés de 1-2 sprints |
| Couverture IA | 7/10 | 11 services avec IA, 10+ candidats sans |
| Inter-modules | 5/10 | 7 interactions actives, 8 manquantes identifiées |
| Notifications | 6/10 | 4 canaux (ntfy, push, email, WhatsApp) mais sans failover unifié |
| Automatisations | 4/10 | Moteur basique (1 trigger, 2 actions), pas d'historique |

---

## 2. Architecture par module

### 2.1 Module Cuisine (12 services, 11 pages, 25+ endpoints)

| Couche | Fichiers | État |
|--------|----------|------|
| **Routes** | `recettes.py`, `courses.py`, `planning.py`, `inventaire.py`, `batch_cooking.py`, `suggestions.py`, `anti_gaspillage.py` | ✅ |
| **Services** | recettes, courses, planning, suggestions, batch_cooking, nutrition_enrichment, import_recettes, recurrence, rappels, photo_frigo, prediction_peremption, prediction_courses | ✅ |
| **Modèles** | Recette, Ingredient, Etape, ListeCourses, ArticleCourses, Planning, Repas, ArticleInventaire, SessionBatchCooking | ✅ |
| **Pages frontend** | Hub + recettes (list/detail/create) + courses + planning + inventaire + batch-cooking + anti-gaspillage + nutrition + scan-ticket | ✅ |
| **Tests** | `tests/services/recettes/` (5), `tests/services/planning/` (8), `tests/services/batch_cooking/` (3), `tests/services/inventaire/` (2) | ⚠️ Manque anti-gaspillage |

### 2.2 Module Famille (23 services, 18 pages, 18+ endpoints)

| Couche | Fichiers | État |
|--------|----------|------|
| **Routes** | `famille.py` (route monolithique avec sous-routes enfants, activités, jalons, santé, budget, anniversaires) | ✅ |
| **Services** | jules, jules_ai, activites, anniversaires, budget, budget_ai, calendrier, contacts, carnet_sante, documents, evenements, routines, sante, suivi_perso, weekend, weekend_ai, voyage, achats_ia, rappels_famille, resume_hebdo, soiree_ai, version_recette_jules, checklists_anniversaire | ✅ |
| **Modèles** | ProfilEnfant, Jalon, ActiviteFamille, BudgetFamille, AnniversaireFamille, EvenementFamilial, Voyage, etc. | ✅ |
| **Pages frontend** | Hub + jules + activites + routines + budget + weekend + album + anniversaires + contacts + documents + calendrier + gamification + garmin + journal + config + timeline + voyages | ✅ |
| **Tests** | Couverture partielle — manque tests unitaires pour budget_ai, achats_ia, soiree_ai | ⚠️ |

### 2.3 Module Maison (15+ services, 17 pages, 35+ endpoints)

| Couche | Fichiers | État |
|--------|----------|------|
| **Routes** | `maison.py` (route monolithique : projets, entretien, jardin, artisans, contrats, cellier, dévis, diagnostics, énergie) | ✅ |
| **Services** | projets, entretien, jardin, artisans, cellier, visualisation_maison, devis, nuisibles_crud, devis_crud, entretien_saisonnier_crud, releves_crud, conseiller_maison, catalogue_entretien | ✅ |
| **Modèles** | Projet, TacheProjet, Routine, ElementJardin, Meuble, StockMaison, Contrat, Artisan, DiagnosticMaison, etc. (25+ modèles) | ✅ |
| **Pages frontend** | Hub + travaux + jardin + menage + finances + charges + provisions + artisans + equipements + contrats + diagnostics + documents + meubles + visualisation + energie | ✅ |

### 2.4 Module Jeux (12+ services, 6 pages, 40+ endpoints)

| Couche | Fichiers | État |
|--------|----------|------|
| **Routes** | `jeux.py` (paris CRUD, loto, euromillions, predictions, stats, backtest, KPIs) | ✅ |
| **Services** | paris_crud, loto_crud, euromillions_crud, prediction, backtest, jeux_ai, sync, scheduler, loto_data, football_data, responsable_gaming, series | ✅ |
| **Modèles** | Equipe, Match, PariSportif, TirageLoto, GrilleLoto, StatistiquesLoto, SerieJeux, AlerteJeux, ConfigurationJeux | ✅ |
| **Pages frontend** | Hub + paris + loto + euromillions + performance + ocr-ticket | ✅ |

### 2.5 Module Outils (8 pages, services variés)

| Couche | Fichiers | État |
|--------|----------|------|
| **Routes** | `utilitaires.py` (notes, journal, contacts, liens, mdp, énergie), `assistant.py` (chat IA) | ✅ |
| **Services** | notes, journal, contacts, liens, mots_de_passe, energie, chat_ia, ocr, meteo, image_generator | ✅ |
| **Pages frontend** | Hub + chat-ia + assistant-vocal + automations + convertisseur + meteo + minuteur + notes + nutritionniste | ✅ |

### 2.6 Dashboard & Admin

| Couche | Fichiers | État |
|--------|----------|------|
| **Routes** | `dashboard.py`, `admin.py` | ✅ |
| **Services** | accueil_data, score_bien_etre, resume_famille_ia, points_famille, anomalies_financieres | ✅ |
| **Pages frontend** | Dashboard principal, Admin (audit/jobs/notifications/services/users) | ✅ |
| **Documentation** | Admin : aucune doc | ❌ |

---

## 3. Audit SQL — Schéma & Consolidation

### 3.1 Structure actuelle

Le fichier `sql/INIT_COMPLET.sql` (~4 500 lignes) contient :

| Section | Contenu | Lignes approx. |
|---------|---------|-----------------|
| Part 1 | Extensions + schema versioning | 1-200 |
| Part 2 | Table `schema_migrations` | 200-250 |
| Part 3 | 45+ tables autonomes (sans FK) | 250-1500 |
| Part 4 | 30+ tables avec FK | 1500-2500 |
| Part 5A | Tables maison (jardin, tâches) | 2500-2900 |
| Part 5B | Extensions jeux (euromillions, bankroll) | 2900-3200 |
| Part 5C | Extensions maison (contrats, artisans, garanties) | 3200-3600 |
| Part 5D | Utilitaires (notes, journal, contacts, énergie) | 3600-3900 |
| Part 6 | Triggers (auto-update `modifie_le`) | 3900-4100 |
| Part 7 | Vues + fonctions helper | 4100-4400 |
| Part 8 | Requêtes analytics/reporting | 4400-4500 |

### 3.2 Inventaire des tables par domaine

| Domaine | Tables | Exemples |
|---------|--------|----------|
| **Cuisine** | 15 | `recettes`, `ingredients`, `etapes`, `listes_courses`, `articles_courses`, `plannings`, `repas_planning`, `inventaire`, `batch_cooking_sessions` |
| **Famille** | 20 | `profils_enfants`, `jalons`, `activites_famille`, `budgets_famille`, `anniversaires_famille`, `evenements_familiaux`, `vaccins`, `documents_famille` |
| **Maison** | 25 | `projets_maison`, `taches_projets`, `zones_jardin`, `plantes_jardin`, `contrats`, `artisans`, `garanties`, `diagnostics_maison`, `meubles` |
| **Jeux** | 15 | `jeux_matchs`, `jeux_paris_sportifs`, `jeux_tirages_loto`, `jeux_grilles_loto`, `jeux_equipes`, `jeux_bankroll`, `jeux_series` |
| **Finances** | 8 | `depenses`, `budgets_mensuels`, `factures`, `depenses_maison` |
| **Planning/Calendrier** | 8 | `evenements_planning`, `calendriers_externes`, `evenements_calendrier`, `voyages` |
| **Gamification** | 3 | `points_utilisateurs`, `badges_utilisateurs`, `jeux_bankroll_historique` |
| **Santé/Garmin** | 5 | `garmin_tokens`, `activites_garmin`, `resumes_quotidiens_garmin`, `journaux_alimentaires` |
| **Notifications** | 5 | `abonnements_push`, `preferences_notifications`, `webhooks_abonnements`, `historique_actions` |
| **Admin/Sécurité** | 5 | `logs_securite`, `etats_persistants`, `automations` |
| **Utilitaires** | 8 | `notes_memos`, `journal_bord`, `contacts_utiles`, `liens_favoris`, `mots_de_passe_maison`, `releves_energie` |
| **TOTAL** | **~150** | |

### 3.3 Problèmes de cohérence SQL détectés

| # | Problème | Sévérité | Tables concernées |
|---|---------|----------|-------------------|
| S1 | **Typage `user_id` incohérent** : UUID dans certaines tables, VARCHAR dans d'autres, INTEGER dans d'autres | 🔴 HAUTE | Multi-tables |
| S2 | **Doublon legacy** `liste_courses` vs `listes_courses` — table legacy non nettoyée | 🟡 MOYENNE | Courses |
| S3 | **FK CASCADE incohérent** : mix de `ON DELETE SET NULL` et `ON DELETE CASCADE` sans logique claire | 🟡 MOYENNE | Divers |
| S4 | **Champs JSONB non typés** : `preferences_utilisateurs`, `preferences_home` stockent des JSON sans validation SQL | 🟢 BASSE | Preferences |
| S5 | **4 migrations absorbées** dans INIT_COMPLET mais encore référencées dans `schema_migrations` | 🟢 BASSE | Migrations |

### 3.4 Plan de consolidation SQL (sans migration/versioning)

> **Contexte** : En dev, pas de migration formelle. Tout doit être regroupé dans `INIT_COMPLET.sql`.

**Actions recommandées** :

1. **Standardiser `user_id`** → UUID partout (type `UUID DEFAULT gen_random_uuid()`)
2. **Nettoyer tables legacy** → Supprimer `liste_courses` (ancienne), garder `listes_courses`
3. **Uniformiser CASCADE** → Convention : `CASCADE` pour les enfants forts (ingrédients d'une recette), `SET NULL` pour les références faibles (artisan d'un contrat)
4. **Ajouter contraintes CHECK** → Valider les enums côté SQL (pas juste côté Pydantic)
5. **Documenter les vues** → Les 5 vues SQL sont utiles mais non documentées
6. **Ajouter les index manquants** → Certaines jointures fréquentes (planning ↔ recette, courses ↔ inventaire) n'ont pas d'index composites

### 3.5 Vues SQL existantes

| Vue | Usage | Exploitée ? |
|-----|-------|-------------|
| `v_objets_a_remplacer` | Objets à remplacer (priorité) | ⚠️ Pas dans le frontend |
| `v_temps_par_activite_30j` | Temps par activité (30 jours) | ⚠️ Pas dans le frontend |
| `v_budget_travaux_par_piece` | Budget travaux par pièce | ⚠️ Pas dans le frontend |
| `v_taches_jour` | Tâches du jour (jointure zones/pièces) | ✅ Utilisée dans dashboard |
| `v_charge_semaine` | Charge de travail hebdomadaire | ⚠️ Pas dans le frontend |

**Gap** : 4 vues SQL créées mais jamais exploitées côté frontend. Opportunité de les exposer dans le dashboard.

---

## 4. Bugs & Risques détectés

### 4.1 Bugs critiques (P0)

| # | Bug | Localisation | Impact |
|---|-----|-------------|--------|
| B1 | **Import `ActiviteFamille` cassé** dans `recherche.py` — le modèle a été renommé/déplacé lors d'un refactoring | `src/api/routes/recherche.py` | ❌ Recherche globale plantée |
| B2 | **Cron job référence `liste_courses`** (ancienne table) au lieu de `articles_courses` dans `_job_rappel_courses_ntfy` | `src/services/core/cron/jobs.py` | ❌ Rappel courses ne fonctionne pas |

### 4.2 Bugs importants (P1)

| # | Bug | Localisation | Impact |
|---|-----|-------------|--------|
| B3 | **30+ `# type: ignore`** masquent des erreurs de typage potentielles | services/jeux/, services/maison/ | ⚠️ Bugs runtime possibles |
| B4 | **8 schémas Pydantic `pass`** (classes vides) — réponses API potentiellement incomplètes | `src/api/schemas/utilitaires.py`, `documents.py` | ⚠️ API retourne des réponses vides |
| B5 | **Hardcodé `items` fallback** dans le parser IA — si le JSON n'a pas de clé attendue, il cherche `items` par défaut | `src/core/ai/parser.py` | ⚠️ Parsing IA incorrect silencieux |
| B6 | **Hardcodé `USER_ID="matanne"`** dans certains cron jobs au lieu de boucler sur tous les users | `src/services/core/cron/jobs.py` | ⚠️ Multi-user impossible |

### 4.3 Bugs mineurs (P2)

| # | Bug | Localisation | Impact |
|---|-----|-------------|--------|
| B7 | **Race condition** sur `_verrou_tokens` (Lock global) dans `partage_recettes.py` | `src/services/cuisine/partage_recettes.py` | ⚠️ Si concurrent |
| B8 | **50+ stubs `pass`** dans les services — fonctions déclarées mais non implémentées | Divers services | 🟡 Fonctionnalités muettes |
| B9 | **Erreurs WebSocket silencieuses** — logged mais pas re-essayées | `src/api/websocket_courses.py` | 🟡 Déconnexion silencieuse |
| B10 | **Dashboard alertes avalées** — exceptions dans l'agrégation multi-module → `[]` retourné silencieusement | `src/services/dashboard/service.py` | 🟡 Alertes manquantes |
| B11 | **Frontend guards admin manquants** — pages admin visibles sans vérification `role !== "admin"` côté React | `frontend/src/app/(app)/admin/` | 🟡 UI visible (API protégée) |
| B12 | **20+ violations accessibilité** — ARIA attributes incorrects dans switch/checkbox/slider shadcn | `frontend/src/composants/ui/` | 🟡 WCAG non conforme |

### 4.4 Tableau récapitulatif

| Priorité | Nombre | Action |
|----------|--------|--------|
| P0 — Bloquant | 2 | Fix immédiat (B1, B2) |
| P1 — Important | 4 | Sprint correctif (B3-B6) |
| P2 — Mineur | 6 | Backlog (B7-B12) |
| **Total** | **12** | |

---

## 5. Gaps fonctionnels par module

### 5.1 Cuisine

| Gap | Description | Priorité |
|-----|-------------|----------|
| G-CUI-1 | **Anti-gaspillage → recettes auto** : les items proches de la péremption ne déclenchent pas automatiquement des suggestions de recettes | HAUTE |
| G-CUI-2 | **Batch cooking → courses auto** : une session batch cooking ne génère pas automatiquement la liste de courses | MOYENNE |
| G-CUI-3 | **Nutrition tracking continu** : pas de suivi nutritionnel sur la semaine (juste par recette individuelle) | MOYENNE |
| G-CUI-4 | **Import recettes depuis photo** : la photo du frigo détecte les ingrédients mais ne propose pas d'importer les recettes correspondantes en un clic | BASSE |
| G-CUI-5 | **Historique des plannings** : pas de visualisation des plannings passés pour détecter les patterns | BASSE |

### 5.2 Famille

| Gap | Description | Priorité |
|-----|-------------|----------|
| G-FAM-1 | **Routines → Planning** : les routines familiales ne bloquent pas de créneaux dans le planning. **Diagnostic** : `TacheRoutine.heure_prevue` (HH:MM, string) n'est jamais croisé avec `Repas.type_repas` (enum petit_déjeuner/déjeuner/goûter/dîner). `ServicePlanningUnifie._charger_routines()` regroupe toutes les routines sous la clé générique `"routine_quotidienne"` sans distinction par jour/heure. Il manque : (1) mapper `heure_prevue` vers un `type_repas` ou créneau horaire, (2) vérifier les conflits lors de la création de repas, (3) un cron job pour synchroniser quotidiennement. | HAUTE |
| G-FAM-2 | **Budget → Dashboard intégré** : le budget famille n'est pas agrégé avec le budget maison dans un budget global | MOYENNE |
| G-FAM-3 | **Rappels anniversaires → déclencher achat cadeau** : pas de lien entre anniversaire et suggestions cadeaux IA | MOYENNE |

### 5.3 Maison

| Gap | Description | Priorité |
|-----|-------------|----------|
| G-MAI-1 | **Énergie → anomalies IA** : collecte de données sans analyse (pas de détection d'anomalies de consommation) | HAUTE |
| G-MAI-2 | **Jardin → météo proactive** : les alertes météo existent mais ne déclenchent pas d'actions (arrosage, protection) | MOYENNE |
| G-MAI-3 | **Vues SQL non exploitées** : 4 vues SQL (`v_objets_a_remplacer`, `v_budget_travaux_par_piece`, etc.) créées mais jamais affichées | MOYENNE |
| G-MAI-5 | **Maintenance prédictive** : les tâches d'entretien sont statiques au lieu d'apprendre les patterns saisonniers | BASSE |

### 5.4 Jeux

| Gap | Description | Priorité |
|-----|-------------|----------|
| G-JEU-1 | **Pertes → budget** : les pertes aux paris ne sont pas reflétées dans le module budget/finances | HAUTE |
| G-JEU-2 | **Bankroll management** : le concept existe en DB mais pas de page frontend dédiée | MOYENNE |
| G-JEU-3 | **Alertes responsable gaming** : les seuils existent mais les notifications ne sont pas connectées aux canaux (WhatsApp/email) | MOYENNE |

### 5.5 Outils

| Gap | Description | Priorité |
|-----|-------------|----------|
| G-OUT-1 | **Notes → tags/catégories** : pas de système de tags pour organiser les notes | MOYENNE |
| G-OUT-2 | **Chat IA → contexte multi-module** : le chat IA ne connaît pas le contexte de l'utilisateur (planning, inventaire, etc.) | HAUTE |
| G-OUT-3 | **Minuteur → intégration recettes** : le minuteur existe mais n'est pas lié aux étapes de recettes | MOYENNE |

### 5.6 Dashboard

| Gap | Description | Priorité |
|-----|-------------|----------|
| G-DASH-1 | **Vue budgétaire unifiée** : pas d'agrégation budget famille + maison + jeux | HAUTE |
| G-DASH-2 | **Score bien-être** : calculé côté service mais pas affiché de manière interactive | MOYENNE |
| G-DASH-3 | **Widgets configurables** : pas de personnalisation de la disposition des widgets | BASSE |

---

## 6. Interactions intra-module (existantes)

Ce sont les interactions **à l'intérieur** d'un même module qui fonctionnent déjà :

### Cuisine (intra)
| Interaction | Flux | État |
|-------------|------|------|
| Recettes → Planning | Catalogue recettes → planifier la semaine | ✅ |
| Planning → Courses | Planning repas → générer liste courses automatiquement | ✅ |
| Inventaire → Anti-gaspillage | Items périmés → alertes anti-gaspillage | ✅ Partiel |
| Recettes → Batch cooking | Sélection recettes → session batch cooking | ✅ |
| Suggestions IA → Planning | IA suggère des recettes → insertion dans le planning | ✅ |
| Photo frigo → Suggestions | Analyse photo → ingrédients détectés → suggestions recettes | ✅ |

### Famille (intra)
| Interaction | Flux | État |
|-------------|------|------|
| Jules (enfant) → Jalons | Suivi développement → jalons atteints | ✅ |
| Jules → Recettes adaptées | Portions enfant ajustées automatiquement | ✅ |
| Budget → Achats | Suivi achats → impact sur budget famille | ✅ |
| Anniversaires → Checklists | Anniversaire créé → checklist auto-générée | ✅ |
| Weekend IA → Activités | Suggestions IA de weekend → activités planifiées | ✅ |

### Maison (intra)
| Interaction | Flux | État |
|-------------|------|------|
| Projets → Tâches | Projet créé → décomposition en tâches | ✅ |
| Entretien → Calendrier | Tâche entretien → planification récurrente | ✅ |
| Artisans → Contrats | Artisan sélectionné → contrat/devis lié | ✅ |
| Diagnostics → Projets | Diagnostic détecté → projet de réparation suggéré | ✅ |

### Jeux (intra)
| Interaction | Flux | État |
|-------------|------|------|
| Paris → Stats | Paris placés → statistiques de performance | ✅ |
| Predictions IA → Paris | IA prédit résultats → aide à la décision | ✅ |
| Backtest → Stratégies | Backtesting historique → validation stratégies | ✅ |
| Séries → Alertes | Détection patterns → alertes jeu responsable | ✅ |

---

## 7. Interactions inter-modules (existantes)

Ce sont les interactions **entre modules différents** qui fonctionnent déjà :

| # | Source → Destination | Mécanisme | État |
|---|---------------------|-----------|------|
| IM-1 | **Planning Cuisine → Courses** | Auto-génération de la liste de courses depuis le planning semaine | ✅ Complet |
| IM-2 | **Famille (Jules) → Cuisine** | Portions enfant dans les recettes, versions recettes adaptées | ✅ Complet |
| IM-3 | **Maison Entretien → Planning** | Tâches entretien saisonnier intégrées au planning général | ✅ Complet |
| IM-4 | **Dashboard ← Tous les modules** | Agrégation en lecture seule depuis cuisine, famille, maison, jeux | ✅ Complet |
| IM-5 | **Gamification ← Multi-module** | Points et badges accordés pour actions dans cuisine, famille, maison | ✅ Complet |
| IM-6 | **Cron jobs → Notifications** | 19 jobs planifiés déclenchent des notifications cross-module | ✅ Complet |
| IM-7 | **Planning → Voyage** | Service dédié `inter_module_planning_voyage.py` pour synchroniser | ✅ Complet |

---

## 8. Interactions inter-modules manquantes

Ces interactions **n'existent pas encore** mais apporteraient beaucoup de valeur :

### Priorité HAUTE

| # | Interaction | Bénéfice | Complexité |
|---|------------|----------|------------|
| IM-8 | **Jeux (pertes/gains) → Budget/Finances** | Les résultats de paris impactent automatiquement le budget global. Alerte si seuil de perte atteint | Moyenne |
| IM-9 | **Inventaire péremption → Recettes suggestions** | Items proches d'expirer → IA suggère des recettes pour les utiliser → auto-ajout au planning | Faible |
| IM-10 | **Routines famille → Planning général** | Les routines récurrentes (école, activités) bloquent des créneaux dans le planning central | Moyenne |
| IM-11 | **Chat IA contexte → Tous modules** | Le chat IA connaît le planning, l'inventaire, le budget, la météo pour des réponses contextuelles | Élevée |

### Priorité MOYENNE

| # | Interaction | Bénéfice | Complexité |
|---|------------|----------|------------|
| IM-12 | **Jardin récoltes → Cuisine inventaire** | Récoltes du jardin auto-ajoutées à l'inventaire → suggestions de recettes saisonnières | Faible |
| IM-13 | **Énergie → Batch cooking** | Optimiser les sessions batch cooking pour les heures creuses (tarif énergie) | Moyenne |
| IM-14 | **Météo → Activités famille** | Météo défavorable → suggestions automatiques d'activités intérieur | Faible |
| IM-15 | **Push ↔ WhatsApp failover** | Si push échoue → fallback WhatsApp. Préférences de canal unifiées | Moyenne |

### Priorité BASSE

| # | Interaction | Bénéfice | Complexité |
|---|------------|----------|------------|
| IM-16 | **Garmin santé → Nutrition** | Données d'activité physique → ajuster les suggestions nutritionnelles | Élevée |
| IM-18 | **Maintenance prédictive → Budget maison** | Prédire les coûts de maintenance à venir basés sur l'historique | Élevée |
| IM-19 | **Predictions courses → Auto-commande** | Prédictions d'achat → pré-remplir la liste de courses automatiquement | Moyenne |

---

## 9. Opportunités IA — Où ajouter de l'intelligence

### 9.1 Services avec IA (existants) — 11 services

| Service | Usage IA | Modèle |
|---------|----------|--------|
| `BaseAIService` | Fondation : rate limiting, cache, parsing, streaming | Mistral |
| `ChatAIService` | Chat conversationnel multi-contexte | Mistral |
| `BilanMensuelService` | Résumé mensuel IA de la famille | Mistral |
| `ResumeFamilleIAService` | Résumé hebdomadaire famille | Mistral |
| `AnomaliesFinancieresService` | Détection anomalies budget | Mistral |
| `JulesAIService` | Suggestions développement enfant | Mistral |
| `WeekendAIService` | Suggestions activités weekend | Mistral |
| `SoireeAIService` | Suggestions soirées couple | Mistral |
| `JeuxAIService` | Prédictions paris sportifs | Mistral |
| `ConseillierMaisonService` | Conseils entretien maison | Mistral |
| `ProjetsService` | Estimation projets par IA | Mistral |

### 9.2 Services SANS IA qui en bénéficieraient — 10 candidats

| # | Service | Enrichissement IA proposé | Impact |
|---|---------|--------------------------|--------|
| IA-1 | **NutritionEnrichmentService** | Actuellement OpenFoodFacts uniquement → Ajouter détection carences nutritionnelles + suggestions de recettes compensatoires | 🔴 HAUTE |
| IA-2 | **ServicePredictionCourses** | Statistique pure → Apprendre **pourquoi** les items sont achetés (saison, invités, événements) | 🔴 HAUTE |
| IA-3 | **ServicePredictionPeremption** | Règles statiques → Apprendre les patterns de consommation réels du ménage | 🟡 MOYENNE |
| IA-4 | **RappelsIntelligentsService** | Règles hardcodées → Apprendre les préférences de timing de notification de l'utilisateur | 🟡 MOYENNE |
| IA-5 | **ServiceConflits** | Détection de conflits rule-based → Générer des solutions créatives de résolution | 🟡 MOYENNE |
| IA-6 | **OcrService** | Texte brut → Extraire noms de recettes et auto-importer | 🟡 MOYENNE |
| IA-7 | **EnergieService** | Collecte uniquement → Prédiction anomalies de consommation + alertes | 🟡 MOYENNE |
| IA-8 | **MeteoService** | Données météo seules → Suggestions d'activités contextuelles | 🟢 BASSE |
| IA-9 | **ChecklistVoyageService** | Checklists statiques → Checklists personnalisées par IA (destination, saison, famille) | 🟢 BASSE |
| IA-10 | **NotificationsMaisonService** | Templates alerts → Prédire les urgences maintenance proactivement | 🟢 BASSE |

### 9.3 Nouvelles fonctionnalités IA possibles

| # | Fonctionnalité | Module(s) | Description |
|---|---------------|-----------|-------------|
| IA-NEW-1 | **Assistant multi-contexte** | Outils + Tous | Chat IA qui connaît le planning, l'inventaire, le budget, la météo. "Que faire pour le dîner ce soir avec ce qu'il reste dans le frigo et le budget serré ?" |
| IA-NEW-2 | **Recommandation budget** | Finances | IA analyse les dépenses sur 3 mois et recommande des optimisations catégorie par catégorie |
| IA-NEW-3 | **Planificateur de semaine complet** | Planning | IA génère la semaine entière : repas + activités + tâches maison + courses, en tenant compte de la météo et du budget |
| IA-NEW-4 | **Coach bien-être familial** | Famille | Score bien-être calculé par IA avec recommandations personnalisées (sommeil, activité, nutrition) |
| IA-NEW-5 | **Détection de tendances** | Dashboard | IA détecte des patterns sur 3-6 mois : "Vous dépensez 30% de plus en hiver", "Jules progresse plus vite en motricité" |
| IA-NEW-6 | **Génération d'images recettes** | Cuisine | Génération d'illustrations pour les recettes sans photo (Mistral Pixtral ou DALL-E) |
| IA-NEW-7 | **OCR intelligent factures** | Maison | OCR + IA pour extraire catégorie, montant, récurrence depuis une photo de facture |

---

## 10. Jobs automatiques & Cron

### 10.1 Jobs existants (19)

| Job ID | Fréquence | Heure | Fonction | Module |
|--------|-----------|-------|----------|--------|
| `rappels_famille` | Quotidien | 07:00 | Rappels anniversaires, documents, école | Famille |
| `rappels_maison` | Quotidien | 08:00 | Rappels garanties, contrats, entretien | Maison |
| `rappels_generaux` | Quotidien | 08:30 | Alertes inventaire, rappel repas du jour | Cuisine |
| `peremptions_alert` | Quotidien | 09:00 | Produits proches péremption | Cuisine |
| `sync_garmin` | Quotidien | 06:00 | Sync données santé Garmin | Famille |
| `push_contextuel_soir` | Quotidien | 18:00 | Push notifications résumé soirée | Multi |
| `rappel_courses` | Quotidien | 18:00 | Rappel panier courses (ntfy + WhatsApp) | Cuisine |
| `rappel_routes` | Quotidien | 19:00 | Rappels routes/trajets | Planning |
| `resume_hebdo` | Hebdo | Dim 19:00 | Résumé hebdomadaire par email | Multi |
| `entretien_saisonnier` | Hebdo | Lun 06:00 | Vérification entretien saisonnier | Maison |
| `scores_gamification_reset` | Hebdo | Lun 00:00 | Reset points hebdomadaires | Gamification |
| `archiver_documents` | Hebdo | Ven 22:00 | Archivage documents anciens | Famille |
| `check_alertes_jeux` | Toutes les 6h | :00,:06,:12,:18 | Alertes séries/jeu responsable | Jeux |
| `sync_calendrier_externe` | Toutes les 4h | :15 | Sync Google/Outlook | Calendrier |
| `nettoyage_cache` | Horaire | :00 | Purge cache expiré | Core |
| `webhook_retry` | Toutes les 30min | :00,:30 | Retry webhooks échoués | Core |
| `backup_quotidien` | Quotidien | 02:00 | Backup base de données | Admin |
| `optimiser_db` | Hebdo | Sam 03:00 | VACUUM, ANALYZE | Admin |
| `rapport_mensuel_budget` | Mensuel | 1er, 20:00 | Rapport budget mensuel | Finances |

### 10.2 Jobs manquants (propositions)

| # | Job proposé | Fréquence | Module | Bénéfice |
|---|------------|-----------|--------|----------|
| JOB-1 | **`prediction_courses_weekly`** | Hebdo, Dim 10:00 | Cuisine | Pré-remplir la liste de courses de la semaine basé sur l'historique |
| JOB-2 | **`sync_jeux_budget`** | Quotidien, 22:00 | Jeux → Finances | Synchroniser gains/pertes dans le budget |
| JOB-3 | **`analyse_nutrition_hebdo`** | Hebdo, Dim 20:00 | Cuisine | Résumé nutritionnel de la semaine + carences |
| JOB-4 | **`alertes_energie`** | Quotidien, 07:00 | Maison | Détection consommation anormale (vs historique) |
| JOB-5 | **`nettoyage_logs`** | Hebdo, Dim 04:00 | Admin | Purger logs audit > 90 jours |
| JOB-6 | **`check_garmin_anomalies`** | Quotidien, 08:00 | Famille | Alertes si pas d'activité depuis 3 jours |
| JOB-7 | **`resume_jardin_saisonnier`** | Mensuel, 1er, 08:00 | Maison | Résumé IA des actions jardin du mois + recommandations |
| JOB-8 | **`expiration_documents`** | Quotidien, 09:00 | Famille | Rappel documents à renouveler (carte identité, assurance, etc.) |

### 10.3 Problèmes détectés sur les jobs

| # | Problème | Impact |
|---|---------|--------|
| J1 | **USER_ID hardcodé "matanne"** dans certains jobs → mono-utilisateur | 🔴 Multi-user impossible |
| J2 | **Pas d'historique d'exécution** → impossible de savoir si un job a échoué la nuit dernière | 🔴 Pas de monitoring |
| J3 | **Pas de gestion d'erreur riche** → exceptions loggées mais pas re-tentées | 🟡 Jobs silencieusement échoués |
| J4 | **Pas de notification d'échec** → si un job plante, personne n'est prévenu | 🟡 Pas d'alerte |
| J5 | **Pas de métriques de durée** → impossible d'identifier les jobs lents | 🟢 Optimisation impossible |

---

## 11. Notifications — WhatsApp, Email, Push

### 11.1 Canaux existants

| Canal | Module | État | Limitations |
|-------|--------|------|-------------|
| **ntfy.sh** | `src/services/core/notifications/` | ✅ Production | Aucune |
| **Web Push (VAPID)** | `src/services/core/notifications/` | ✅ Production | Fallback mémoire si DB indisponible |
| **Email (Resend)** | `src/services/core/notifications/` | ✅ Production | Préférences email pas connectées à l'UI |
| **WhatsApp (Meta API)** | `src/api/routes/webhooks_whatsapp.py` | ⚠️ Partiel | Réception OK, envoi incertain, pas de rate limiting |

### 11.2 Gaps notifications

| # | Gap | Description | Priorité |
|---|-----|-------------|----------|
| N1 | **Pas de failover entre canaux** | Si push échoue, pas de fallback vers WhatsApp ou email | HAUTE |
| N2 | **Préférences unifiées manquantes** | L'utilisateur ne peut pas choisir "WhatsApp pour les urgences, email pour les résumés" | HAUTE |
| N3 | **WhatsApp envoi non confirmé** | L'intégration webhook est en place mais l'envoi actif de messages n'est pas validé | MOYENNE |
| N4 | **Pas de SMS** | Pas de canal SMS comme fallback ultime | BASSE |
| N5 | **Pas de throttling notifications** | Risque de spam si plusieurs modules notifient en même temps | MOYENNE |
| N6 | **Pas de digest** | Pas d'option "résumer les notifications toutes les 2h" au lieu de notifier en temps réel | BASSE |

### 11.3 Plan notification idéal

```
                    ┌─────────────────────┐
                    │  Événement module    │
                    │  (ex: péremption)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  NotifDispatcher     │
                    │  (routing + prefs)   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼─────┐  ┌──────▼──────┐  ┌──────▼──────┐
     │   Push/ntfy  │  │  WhatsApp   │  │   Email     │
     │  (urgences)  │  │  (digest)   │  │  (résumés)  │
     └──────┬───────┘  └──────┬──────┘  └──────┬──────┘
            │                 │                 │
            └────────►  Failover Chain  ◄───────┘
```

### 11.4 Événements à notifier par canal

| Événement | Push | WhatsApp | Email | Fréquence |
|-----------|------|----------|-------|-----------|
| Péremption J-2 | ✅ | - | - | Quotidien |
| Rappel courses | ✅ | ✅ | - | Quotidien |
| Résumé hebdo | - | ✅ | ✅ | Hebdomadaire |
| Alerte jeu responsable | ✅ | ✅ | - | Immédiat |
| Rapport budget mensuel | - | - | ✅ | Mensuel |
| Anniversaire J-7 | ✅ | ✅ | - | Ponctuel |
| Tâche entretien urgente | ✅ | ✅ | - | Immédiat |
| Échec cron job (admin) | ✅ | ✅ | ✅ | Immédiat |
| Document expirant | ✅ | - | ✅ | J-30, J-7 |
| Récolte jardin prête | ✅ | - | - | Quotidien |

---

## 12. Mode Admin (lancer manuellement)

### 12.1 Fonctionnalités admin existantes

| Endpoint | Action | Déclenchement | État |
|----------|--------|---------------|------|
| `POST /api/v1/admin/jobs/{id}/run` | Lancer un cron job manuellement | Manuel (bouton) | ✅ |
| `POST /api/v1/admin/notifications/test` | Tester un canal de notification | Manuel | ✅ |
| `POST /api/v1/admin/cache/clear` | Vider le cache L1+L3 | Manuel | ✅ |
| `POST /api/v1/admin/users/{id}/disable` | Désactiver un compte | Manuel | ✅ |
| `GET /api/v1/admin/audit-logs` | Consulter les logs d'audit | Lecture | ✅ |
| `GET /api/v1/admin/services/health` | État de santé des services | Lecture | ✅ |
| `GET /api/v1/admin/db/coherence` | Check cohérence base | Lecture | ✅ |

### 12.2 Fonctionnalités admin manquantes

| # | Fonctionnalité | Description | Priorité |
|---|---------------|-------------|----------|
| ADM-1 | **Dashboard admin dédié** | Vue consolidée : derniers logs, jobs statut, health checks, cache stats — tout sur une page | HAUTE |
| ADM-2 | **Lancer n'importe quel service manuellement** | Bouton "Run" pour chaque service (pas juste les cron jobs) — utile quand tu testes | HAUTE |
| ADM-3 | **Mode dry-run** | Exécuter un job/service en mode simulation sans écriture en DB | HAUTE |
| ADM-4 | **Historique exécutions jobs** | Table `job_executions` avec start, end, status, error, durée | HAUTE |
| ADM-5 | **Toggle feature flags** | Activer/désactiver des fonctionnalités depuis l'admin sans redéployer | MOYENNE |
| ADM-6 | **Voir/modifier les configurations** | Éditer les paramètres (rate limits, seuils IA, etc.) depuis l'UI | MOYENNE |
| ADM-7 | **Forcer re-sync** | Bouton pour forcer la synchronisation Garmin, Google Calendar, etc. | MOYENNE |
| ADM-8 | **SQL query viewer** (lecture seule) | Exécuter des SELECT depuis l'admin pour debug | BASSE |
| ADM-9 | **Seed data** | Bouton pour injecter des données de test (dev uniquement) | BASSE |
| ADM-10 | **Export complet DB** | Télécharger un dump complet de la base en JSON/CSV | BASSE |

### 12.3 Principe de visibilité admin

> **Règle** : Les fonctionnalités admin sont **invisibles** pour l'utilisateur normal.
> - Les pages `/admin/*` ne sont pas dans la sidebar standard
> - Le header admin n'apparaît que si `role === "admin"`
> - En dev (`ENVIRONMENT=development`), un bouton discret dans le footer permet d'accéder à l'admin
> - Aucun lien direct vers `/admin` dans la navigation mobile

**Implémentation frontend nécessaire** :
```tsx
// Dans barre-laterale.tsx
{utilisateur?.role === 'admin' && (
  <SidebarGroup label="Administration">
    <SidebarItem href="/admin" icon={Shield} />
  </SidebarGroup>
)}
```

---

## 13. Moteur d'automatisation

### 13.1 État actuel

Le moteur d'automatisation dans `src/services/utilitaires/automations_engine.py` est **basique** :

| Caractéristique | État |
|-----------------|------|
| **Triggers supportés** | 1 seul : `stock_bas` (item sous seuil) |
| **Actions supportées** | 2 : `ajouter_courses`, `notifier` |
| **Historique exécutions** | ❌ Aucun |
| **Mode dry-run** | ❌ Absent |
| **Planification par règle** | ❌ Fréquence fixe globale |
| **Rollback** | ❌ Fire-and-forget |
| **Interface frontend** | ✅ Page automation existe |

### 13.2 Plan d'extension du moteur

#### Triggers à ajouter

| Trigger | Description | Module source |
|---------|-------------|---------------|
| `peremption_proche` | Item à J-N de la date de péremption | Cuisine/Inventaire |
| `budget_depassement` | Budget dépasse le seuil défini | Finances |
| `meteo_alerte` | Conditions météo défavorables | Maison/Jardin |
| `anniversaire_proche` | Anniversaire dans N jours | Famille |
| `tache_en_retard` | Tâche non complétée après la date prévue | Maison/Planning |
| `garmin_inactivite` | Pas d'activité Garmin depuis N jours | Famille/Santé |
| `document_expiration` | Document expire dans N jours | Famille |
| `recette_sans_photo` | Recette créée sans image depuis N jours | Cuisine |

#### Actions à ajouter

| Action | Description | Module cible |
|--------|-------------|-------------|
| `generer_liste_courses` | Créer/compléter la liste de courses | Cuisine |
| `suggerer_recette` | Proposer une recette via push | Cuisine |
| `creer_tache_maison` | Créer une tâche d'entretien | Maison |
| `envoyer_whatsapp` | Envoyer un message WhatsApp | Notifications |
| `envoyer_email` | Envoyer un email formaté | Notifications |
| `ajouter_au_planning` | Insérer un repas/activité dans le planning | Planning |
| `mettre_a_jour_budget` | Créer une entrée de dépense | Finances |
| `generer_rapport_pdf` | Générer et envoyer un rapport | Export |
| `archiver` | Archiver un élément | Multi |

#### Architecture cible

```
AutomationEngine
├── TriggerRegistry        # Enregistre les triggers disponibles
│   ├── StockBasTrigger
│   ├── PeremptionTrigger
│   ├── BudgetTrigger
│   └── ...
├── ActionRegistry         # Enregistre les actions disponibles
│   ├── AjouterCoursesAction
│   ├── NotifierAction
│   ├── SuggererRecetteAction
│   └── ...
├── RuleEngine             # Évalue les règles
│   ├── evaluate_conditions()
│   ├── execute_actions()
│   └── dry_run()
├── ExecutionHistory       # Historique + métriques
│   ├── log_execution()
│   ├── get_history()
│   └── get_stats()
└── Scheduler              # Planification par règle
    ├── schedule_rule()
    └── unschedule_rule()
```

---

## 14. Audit des Tests

### 14.1 Inventaire

| Catégorie | Fichiers | Tests (est.) | Couverture |
|-----------|----------|-------------|------------|
| API routes | ~25 | ~100 | 70% |
| Services cuisine | 18 | ~80 | 80% |
| Services famille | 8 | ~30 | 50% |
| Services maison | 5 | ~20 | 40% |
| Services jeux | 10 | ~40 | 60% |
| Core (config, db, cache, ai) | ~80 | ~200 | 85% |
| Modèles ORM | 18 | ~50 | 90% |
| SQL schéma | 2 | ~10 | Sur le schéma uniquement |
| Benchmarks | 5 | ~15 | Performance |
| Load tests | 3 | ~5 | Charge |
| **TOTAL** | **~186** | **~550** | **~65%** |

### 14.2 Couverture par zone critique

| Zone | Couverture | Objectif | Gap |
|------|-----------|---------|-----|
| Auth/JWT | 70% | 95% | Manque edge cases (token expiré, 2FA) |
| Cron jobs | 60% | 90% | Manque gestion erreurs, retry, notifications d'échec |
| Admin routes | 40% | 85% | Manque ACL complet, opérations sensibles |
| WhatsApp/webhook | 20% | 80% | Réception testée, envoi non testé |
| Garmin sync | 30% | 75% | Token refresh, erreurs API non testés |
| Multi-user | 10% | 70% | Aucun test d'accès concurrent |
| WebSocket | 30% | 70% | Reconnexion, messages perdus non testés |
| Moteur automations | 20% | 80% | Un seul trigger testé |

### 14.3 Tests manquants prioritaires

| # | Test | Catégorie | Priorité |
|---|------|-----------|----------|
| T1 | **Tests admin ACL** — vérifier qu'un user non-admin ne peut pas accéder aux endpoints admin | API | 🔴 |
| T2 | **Tests cron error handling** — job qui plante → vérifie le logging + retry | Services | 🔴 |
| T3 | **Tests WhatsApp send** — mock Meta API → vérifier le formatage du message | Intégration | 🔴 |
| T4 | **Tests multi-user isolation** — 2 users ne voient pas les données de l'autre | Core | 🔴 |
| T5 | **Tests moteur automations** — triggers + actions + historique | Services | 🟡 |
| T6 | **Tests WebSocket reconnexion** — déconnexion → reconnexion automatique | API | 🟡 |
| T7 | **Tests inter-modules** — planning → courses → inventaire flow complet | E2E | 🟡 |
| T8 | **Tests schéma Pydantic ↔ TypeScript** — vérifier l'alignement frontend/backend | Cross | 🟡 |
| T9 | **Tests performance cron** — durée exécution de chaque job | Benchmark | 🟢 |
| T10 | **Tests notifications failover** — push échoue → fallback email | Intégration | 🟢 |

### 14.4 Infrastructure de test à améliorer

| Amélioration | État actuel | Cible |
|-------------|-------------|-------|
| **Coverage report automatique** | Manuel (`python manage.py test_coverage`) | CI/CD avec seuil 80% |
| **Mutation testing** | Absent | mutmut ou cosmic-ray pour détecter tests faibles |
| **Contract testing** | Absent | Pact ou Schemathesis pour valider API contracts |
| **Visual regression** | Absent | Percy ou Chromatic pour screenshots UI |
| **Snapshot testing** | Absent | Pour les réponses API JSON complexes |

---

## 15. Audit de la Documentation

### 15.1 Inventaire docs existantes

| Document | Contenu | État | À faire |
|----------|---------|------|---------|
| `docs/ARCHITECTURE.md` | Architecture technique complète | ✅ À jour | - |
| `docs/API_REFERENCE.md` | Référence API par endpoint | ⚠️ Partiel | Ajouter endpoints récents |
| `docs/MODULES.md` | Vue d'ensemble des modules | ⚠️ Partiel | Mettre à jour post-sprint 14 |
| `docs/SERVICES_REFERENCE.md` | Services et factories | ⚠️ Daté | Régénérer depuis le code |
| `docs/ERD_SCHEMA.md` | Schéma entité-relation | ✅ À jour | - |
| `docs/PATTERNS.md` | Patterns de code | ✅ À jour | - |
| `docs/DEPLOYMENT.md` | Guide de déploiement | ✅ À jour | - |
| `docs/MIGRATION_GUIDE.md` | Guide de migration | ✅ À jour | - |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | Gestion sessions DB | ✅ À jour | - |
| `docs/REDIS_SETUP.md` | Configuration Redis | ✅ À jour | - |
| `docs/UI_COMPONENTS.md` | Composants frontend | ⚠️ Partiel | Ajouter nouveaux composants |

### 15.2 Guides modules

| Guide | Couverture | Manque |
|-------|-----------|--------|
| `docs/guides/cuisine/README.md` | 85% | Batch cooking flow, anti-gaspillage IA |
| `docs/guides/famille/README.md` | 75% | Jules IA, gamification, Garmin |
| `docs/guides/maison/README.md` | 70% | Artisans, diagnostics, énergie |
| `docs/guides/jeux/README.md` | 80% | Bankroll management, séries alertes |
| `docs/guides/planning/README.md` | 80% | Sync calendrier, voyages |
| `docs/guides/dashboard/README.md` | 60% | Widgets, cross-module metrics |
| `docs/guides/outils/README.md` | 75% | Automations, assistant vocal |
| `docs/guides/utilitaires/README.md` | ✅ 95% | Complet |

### 15.3 Documentation manquante

| # | Document | Priorité | Contenu attendu |
|---|---------|----------|-----------------|
| DOC-1 | **`docs/ADMIN_RUNBOOK.md`** | 🔴 HAUTE | Guide opérationnel : comment lancer les jobs, vider le cache, gérer les users, diagnostiquer |
| DOC-2 | **`docs/CRON_JOBS.md`** | 🔴 HAUTE | Liste des 19 jobs, horaires, dépendances, troubleshooting |
| DOC-3 | **`docs/NOTIFICATIONS.md`** | 🟡 MOYENNE | Canaux disponibles, configuration, préférences, failover |
| DOC-4 | **`docs/INTER_MODULES.md`** | 🟡 MOYENNE | Cartographie des interactions entre modules |
| DOC-5 | **`docs/AI_SERVICES.md`** | 🟡 MOYENNE | Services IA, prompts, rate limits, cache strategy |
| DOC-6 | **`docs/AUTOMATIONS.md`** | 🟢 BASSE | Moteur d'automatisation, triggers, actions, règles |
| DOC-7 | **`docs/TROUBLESHOOTING.md`** | 🟢 BASSE | Erreurs courantes, solutions, FAQ développeur |
| DOC-8 | **`docs/DEVELOPER_SETUP.md`** | 🟢 BASSE | Installation dev complète pas-à-pas |

---

## 16. Organisation du code & Dette technique

### 16.1 Points forts de l'architecture

| Aspect | Détail | Score |
|--------|--------|-------|
| **Modularité** | Services isolés, factory pattern, lazy loading | 9/10 |
| **Patterns cohérents** | `@service_factory`, `@gerer_exception_api`, `executer_avec_session` | 9/10 |
| **Typage fort** | Pydantic v2. SQLAlchemy 2.0 `Mapped[]`, TypeScript strict | 8/10 |
| **Résilience** | Circuit breaker, retry, rate limiting, fallback | 8/10 |
| **Cache multi-niveaux** | L1 mémoire → L3 fichier + ETag HTTP + TanStack Query | 8/10 |
| **Sécurité** | JWT + RBAC + RLS + CORS + rate limiting + security headers | 9/10 |

### 16.2 Dette technique identifiée

| # | Dette | Sévérité | Effort |
|---|-------|----------|--------|
| DT-1 | **30+ `# type: ignore`** — masquent des erreurs potentielles. Remplacer par `cast()` ou corriger les types | 🟡 MOYENNE | 2-3h |
| DT-2 | **50+ stubs `pass`** — fonctions déclarées non implémentées | 🟡 MOYENNE | 4-6h |
| DT-3 | **8 schémas Pydantic vides** — classes `pass` dans `schemas/utilitaires.py`, `documents.py` | 🟡 MOYENNE | 1h |
| DT-4 | **Route monolithique `maison.py`** — 35+ endpoints dans un seul fichier | 🟢 BASSE | 2h (split en sous-routeurs) |
| DT-5 | **Route monolithique `famille.py`** — 18+ endpoints dans un seul fichier | 🟢 BASSE | 2h |
| DT-6 | **Client API admin manquant** frontend — pages admin utilisent `clientApi` directement | 🟢 BASSE | 30min |
| DT-7 | **Types TypeScript incomplets** — `batch-cooking.ts`, `anti-gaspillage.ts` sont minimaux | 🟢 BASSE | 1h |
| DT-8 | **Accessibilité frontend** — 20+ violations ARIA dans les composants shadcn | 🟢 BASSE | 2-3h |
| DT-9 | **Pas de lint SQL** — `INIT_COMPLET.sql` n'est pas validé par un linter | 🟢 BASSE | Setup 1h |
| DT-10 | **Pas de pre-commit hooks** — formatage/linting non automatisé au commit | 🟢 BASSE | 30min |

### 16.3 Organisation des fichiers — Recommandations

| Actuel | Recommandation | Raison |
|--------|---------------|--------|
| `src/api/routes/maison.py` (35+ endpoints) | Split en `routes/maison/projets.py`, `routes/maison/entretien.py`, etc. | Maintenabilité |
| `src/api/routes/famille.py` (18+ endpoints) | Split en `routes/famille/enfants.py`, `routes/famille/budget.py`, etc. | Maintenabilité |
| `sql/INIT_COMPLET.sql` (4500 lignes) | Garder tel quel (un seul fichier = source de vérité dev) | Déjà bien structuré en sections |
| Frontend `composants/` flat | Organiser en sous-dossiers par module (déjà partiellement fait) | Clarté |

---

## 17. Axes d'amélioration & Innovation

### 17.1 Innovations techniques

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| INNO-1 | **Mode hors-ligne (PWA)** | Service Worker + IndexedDB pour fonctionner sans connexion (courses, notes, minuteur) | 🔴 HAUTE |
| INNO-2 | **Sync temps réel multi-device** | WebSocket pour tous les modules (pas juste courses) — synchronisation en direct entre téléphone et tablette | 🟡 MOYENNE |
| INNO-3 | **Commandes vocales** | L'assistant vocal existant pourrait commander : "Ajoute du lait à la liste", "Qu'est-ce qu'on mange ce soir ?" | 🟡 MOYENNE |
| INNO-4 | **Widget mobile natif** | PWA widgets ou notifications interactives (bouton "J'ai fait les courses" directement dans la notification) | 🟡 MOYENNE |
| INNO-5 | **Data export/import famille** | Export complet en JSON pour sauvegarde ou partage entre familles (recettes, plannings) | 🟢 BASSE |

### 17.2 Innovations fonctionnelles

| # | Innovation | Description | Module |
|---|-----------|-------------|--------|
| INNO-6 | **Planificateur IA semaine complète** | Un bouton : IA génère plannings repas + activités + tâches maison + courses, tenant compte du budget, de la météo, des préférences | Multi |
| INNO-7 | **Mode "invités"** | Planning repas adapté quand on reçoit des invités (portions, allergies, courses supplémentaires) | Cuisine |
| INNO-8 | **Comparateur de prix** | Intégration API supermarchés pour comparer les prix de la liste de courses | Cuisine |
| INNO-9 | **Journal de bord augmenté** | Journal familial avec photos, humeur, météo, activités réalisées — généré automatiquement à partir des données | Famille |
| INNO-10 | **Bilan financier annuel** | Rapport IA de fin d'année : tendances, économies réalisées, recommandations pour l'année suivante | Finances |
| INNO-11 | **Carte interactive maison** | Vue 3D/plan de la maison avec les équipements, les tâches en cours, les garanties par pièce | Maison |
| INNO-13 | **Suivi écologique** | Score éco calculé : gaspillage alimentaire, consommation énergie, déplacements — avec objectifs et badges | Multi |
| INNO-14 | **Calendrier scolaire intégré** | Import automatique du calendrier scolaire selon la zone → cron qui ajuste les plannings vacances | Famille |
| INNO-15 | **Mode "urgence"** | Si un ingrédient manque au dernier moment → IA propose un remplacement + adapte la recette | Cuisine |

### 17.3 Améliorations UX

| # | Amélioration | Description |
|---|-------------|-------------|
| UX-1 | **Onboarding interactif** | Tour guidé au premier lancement (composant `tour-onboarding.tsx` existe mais peu utilisé) |
| UX-2 | **Raccourcis clavier** | Cmd+K (recherche globale) existe — ajouter Cmd+N (nouveau), Cmd+P (planning), etc. |
| UX-3 | **Drag & drop planning** | Glisser-déposer les repas dans le planning de la semaine |
| UX-4 | **Thème saisonnier** | Adapter le thème couleur en fonction de la saison (spring green, summer gold, etc.) |
| UX-5 | **Dark mode adaptatif** | Bascule automatique dark mode selon l'heure (18h-7h) |

---

## 18. Plan d'action priorisé

### Phase 1 — Stabilisation (Sprint Correctif)

> Objectif : Zéro bugs critiques, base solide pour développer.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 1.1 | Fix B1 : Import `ActiviteFamille` dans `recherche.py` | 15min | 🔴 P0 |
| 1.2 | Fix B2 : Cron job `liste_courses` → `articles_courses` | 15min | 🔴 P0 |
| 1.3 | Fix B6 : Supprimer USER_ID hardcodé dans les cron jobs | 1h | 🔴 P0 |
| 1.4 | Compléter les 8 schémas Pydantic `pass` (B4) | 1h | 🟡 P1 |
| 1.5 | Remplacer les 30 `# type: ignore` critiques (B3) | 2h | 🟡 P1 |
| 1.6 | Ajouter guards admin frontend (B11) | 30min | 🟡 P1 |
| 1.7 | Fix parser IA fallback hardcodé (B5) | 30min | 🟡 P1 |

### Phase 2 — SQL Consolidation

> Objectif : Schéma SQL propre, cohérent, sans migration.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 2.1 | Standardiser `user_id` → UUID partout | 2h | 🔴 |
| 2.2 | Nettoyer tables legacy (doublon courses) | 30min | 🟡 |
| 2.3 | Uniformiser CASCADE vs SET NULL | 1h | 🟡 |
| 2.4 | Ajouter index manquants (jointures fréquentes) | 1h | 🟡 |
| 2.5 | Documenter les vues SQL dans INIT_COMPLET | 30min | 🟢 |
| 2.6 | Ajouter contraintes CHECK pour enums | 1h | 🟢 |

### Phase 3 — Tests & Qualité

> Objectif : Couverture ≥ 80% sur les zones critiques.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 3.1 | Tests admin ACL (T1) | 2h | 🔴 |
| 3.2 | Tests cron error handling (T2) | 2h | 🔴 |
| 3.3 | Tests WhatsApp send (T3) | 1h | 🔴 |
| 3.4 | Tests multi-user isolation (T4) | 3h | 🔴 |
| 3.5 | Tests moteur automations (T5) | 2h | 🟡 |
| 3.6 | Tests inter-modules E2E (T7) | 3h | 🟡 |
| 3.7 | Setup coverage CI/CD avec seuil | 1h | 🟡 |
| 3.8 | Tests WebSocket reconnexion (T6) | 1h | 🟢 |

### Phase 4 — Documentation

> Objectif : Tout est documenté, à jour, trouvable.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 4.1 | Créer `docs/ADMIN_RUNBOOK.md` (DOC-1) | 2h | 🔴 |
| 4.2 | Créer `docs/CRON_JOBS.md` (DOC-2) | 1h | 🔴 |
| 4.3 | Mettre à jour les guides modules (cuisine, famille, maison, jeux) | 4h | 🟡 |
| 4.4 | Créer `docs/NOTIFICATIONS.md` (DOC-3) | 1h | 🟡 |
| 4.5 | Créer `docs/INTER_MODULES.md` (DOC-4) | 1h | 🟡 |
| 4.6 | Régénérer `docs/SERVICES_REFERENCE.md` | 2h | 🟢 |

### Phase 5 — Interactions inter-modules

> Objectif : Les modules communiquent et se renforcent mutuellement.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 5.1 | IM-9 : Inventaire péremption → Suggestions recettes | 3h | 🔴 |
| 5.2 | IM-8 : Jeux pertes/gains → Budget/Finances | 4h | 🔴 |
| 5.3 | IM-10 : Routines famille → Planning général | 4h | 🟡 |
| 5.4 | IM-12 : Jardin récoltes → Cuisine inventaire | 2h | 🟡 |
| 5.5 | IM-14 : Météo → Activités famille | 2h | 🟡 |
| 5.6 | IM-15 : Push ↔ WhatsApp failover | 3h | 🟡 |
| 5.7 | IM-11 : Chat IA contexte multi-module | 6h | 🟢 |

### Phase 6 — IA & Intelligence

> Objectif : L'IA est partout où elle apporte de la valeur. 

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 6.1 | IA-1 : Nutrition → détection carences + suggestions | 4h | 🔴 |
| 6.2 | IA-2 : Prédiction courses intelligente (avec contexte) | 4h | 🔴 |
| 6.3 | IA-NEW-1 : Assistant multi-contexte | 8h | 🟡 |
| 6.4 | IA-7 : Énergie → anomalies IA | 3h | 🟡 |
| 6.5 | IA-NEW-3 : Planificateur semaine complète | 8h | 🟡 |
| 6.6 | IA-3 : Prédiction péremption (apprentissage patterns) | 4h | 🟢 |
| 6.7 | IA-NEW-5 : Détection de tendances (3-6 mois) | 6h | 🟢 |

### Phase 7 — Jobs & Automatisations

> Objectif : Jobs fiables avec historique, moteur d'automatisation riche.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 7.1 | Table `job_executions` + historique automatique | 3h | 🔴 |
| 7.2 | Notification d'échec job → admin (push + email) | 1h | 🔴 |
| 7.3 | Ajouter les 8 jobs manquants (JOB-1 à JOB-8) | 6h | 🟡 |
| 7.4 | Étendre le moteur d'automatisation (10 triggers, 9 actions) | 8h | 🟡 |
| 7.5 | Mode dry-run pour jobs et automations | 2h | 🟡 |
| 7.6 | Métriques durée de chaque job | 1h | 🟢 |

### Phase 8 — Notifications & Communications

> Objectif : Notifications fiables, multi-canal, avec préférences utilisateur.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 8.1 | Finaliser WhatsApp envoi (confirmer/implémenter) | 3h | 🔴 |
| 8.2 | Préférences unifiées par canal et par type | 3h | 🔴 |
| 8.3 | Failover push → WhatsApp → email | 2h | 🟡 |
| 8.4 | Throttling & digest (regroupement notifications) | 3h | 🟡 |
| 8.5 | Mapper événements → canaux (tableau §11.4) | 2h | 🟡 |

### Phase 9 — Mode Admin Complet

> Objectif : Un admin peut tout contrôler sans toucher au code.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 9.1 | Dashboard admin consolidé (ADM-1) | 4h | 🔴 |
| 9.2 | Lancer tout service manuellement (ADM-2) | 3h | 🔴 |
| 9.3 | Mode dry-run (ADM-3) | 2h | 🟡 |
| 9.4 | Feature flags (ADM-5) | 3h | 🟡 |
| 9.5 | Forcer re-sync externes (ADM-7) | 1h | 🟡 |
| 9.6 | SQL query viewer read-only (ADM-8) | 3h | 🟢 |
| 9.7 | Seed data dev (ADM-9) | 2h | 🟢 |

### Phase 10 — Innovation & UX

> Objectif : Différenciation, expérience utilisateur supérieure.

| # | Action | Effort | Priorité |
|---|--------|--------|----------|
| 10.1 | INNO-1 : Mode hors-ligne (PWA + IndexedDB) | 16h | 🟡 |
| 10.2 | INNO-6 : Planificateur IA semaine complète | 8h | 🟡 |
| 10.3 | INNO-3 : Commandes vocales enrichies | 4h | 🟡 |
| 10.4 | UX-3 : Drag & drop planning | 4h | 🟡 |
| 10.5 | INNO-7 : Mode invités | 4h | 🟢 |
| 10.6 | INNO-13 : Suivi écologique | 6h | 🟢 |
| 10.7 | INNO-14 : Calendrier scolaire auto | 3h | 🟢 |

---

## 19. Nouveau module — Projet Habitat (Déménagement / Agrandissement / Déco / Jardin)

> **Contexte** : Réflexion sur un 2ème enfant → hésitation entre déménager, faire un agrandissement, ou rester et aménager. Besoin d'un outil pour centraliser la recherche immobilière, la conception de plans, la décoration intérieure et l'aménagement du jardin (2600 m², en pente, tout en longueur).

### 19.1 Vue d'ensemble du module

Le module **Projet Habitat** est un hub central avec 5 sous-modules :

| Sous-module | Description | Écrans |
|-------------|-------------|--------|
| **🏠 Scénarios** | Comparer les 3 options (déménager, agrandir, rester+aménager) avec scoring multicritère | Hub + comparateur |
| **🔍 Veille Immo** | Recherche de maisons avec alertes automatiques sur les annonces correspondantes | Critères, résultats, alertes |
| **📐 Plans & Visu 3D** | Dessiner/importer des plans (intérieur + extérieur), visualisation 3D, suggestions IA | Éditeur plan, vue 3D, galerie |
| **🎨 Déco & Meubles** | Design intérieur par pièce, palette couleurs, sélection meubles avec budget | Pièces, moodboards, budget |
| **🌳 Paysagisme** | Aménagement du jardin (2600 m², pente), plantations, zones, budget | Plan jardin, zones, plantes |

### 19.2 Architecture technique proposée

```
# Backend
src/core/models/habitat_projet.py       # Modèles ORM (Scenario, CritereImmo, Plan, Piece, ZoneJardin)
src/api/routes/habitat.py               # Routes API REST
src/api/schemas/habitat.py              # Schémas Pydantic
src/services/habitat/                   # Services métier
├── scenarios_service.py                # Comparaison scénarios
├── veille_immo_service.py              # Scraping + alertes annonces
├── plans_service.py                    # Gestion plans 2D/3D
├── deco_service.py                     # Déco intérieure, meubles
├── paysagisme_service.py               # Jardin, plantations
└── habitat_ia_service.py               # IA transversale (estimation, suggestions)

# Frontend
frontend/src/app/(app)/habitat/
├── page.tsx                            # Hub projet habitat
├── scenarios/page.tsx                  # Comparateur de scénarios
├── veille-immo/page.tsx                # Recherche + alertes annonces
├── plans/page.tsx                      # Éditeur de plans + visu 3D
├── deco/page.tsx                       # Design intérieur par pièce
└── jardin/page.tsx                     # Aménagement paysager

# SQL
sql/migrations/xxx_habitat_projet.sql   # Tables dédiées
```

### 19.3 Sous-module : Scénarios — Comparateur de décision

**Objectif** : Aider à prendre la décision déménager vs agrandir vs rester en pondérant des critères objectifs.

**Modèle de données** :
```sql
CREATE TABLE habitat_scenarios (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,          -- "Déménager", "Agrandir", "Rester + rénover"
    description TEXT,
    budget_estime DECIMAL(12,2),         -- Budget total estimé
    surface_finale_m2 DECIMAL(8,2),
    nb_chambres INTEGER,
    score_global DECIMAL(5,2),           -- Score calculé 0-100
    avantages JSONB DEFAULT '[]',
    inconvenients JSONB DEFAULT '[]',
    notes TEXT,
    statut VARCHAR(50) DEFAULT 'brouillon',  -- brouillon, actif, archive
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE habitat_criteres (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES habitat_scenarios(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,           -- "Proximité école", "Budget", "Surface jardin"
    poids DECIMAL(3,2) DEFAULT 1.0,      -- Pondération du critère (0.0-1.0)
    note DECIMAL(3,1),                   -- Note 0-10
    commentaire TEXT
);
```

**Fonctionnalités** :
- Créer N scénarios (déménager 3 pièces, 4 pièces, agrandir extension, agrandir surélévation, rester)
- Définir des critères pondérés (budget, surface, localisation, écoles, transports…)
- Score automatique = Σ(note × poids) / Σ(poids)
- Comparaison visuelle en colonnes (radar chart, barres)
- **IA** : Suggérer les critères pertinents en fonction du contexte (2ème enfant, budget estimé)

### 19.4 Sous-module : Veille Immobilière — Alertes annonces

**Objectif** : Monitorer les annonces immobilières correspondant à vos critères et alerter quand une bonne affaire apparaît.

**Stratégie technique** :

| Approche | API/Source | Faisabilité | Description |
|----------|-----------|-------------|-------------|
| **Scraping structuré** | LeBonCoin, SeLoger, PAP, Bien'ici | ⚠️ ToS compliqués | Risque de blocage, maintenance lourde |
| **API immobilières** | DVF (données publiques), API Castorus | ✅ Légal | Données de vente réelles (historique, prix au m²) |
| **Agrégateurs open** | OpenDataSoft DVF, data.gouv.fr | ✅ Légal & gratuit | Historique de ventes, pas d'annonces temps réel |
| **Alertes email parsing** | Gmail API / scraping email | ✅ Faisable | Créer des alertes sur les sites → parser les emails reçus |
| **Services de veille** | Jinka, Castorus | ✅ API disponible | Services tiers spécialisés veille immo |

**Architecture recommandée** (approche hybride) :
1. **Critères de recherche** stockés en DB (ville, budget min/max, surface min, nb pièces, terrain min, etc.)
2. **Cron job quotidien** qui :
   - Interroge l'API DVF (Demandes de Valeurs Foncières) pour les prix de référence du secteur
   - Parse les emails d'alertes des sites d'annonces (SeLoger, LeBonCoin, PAP) via IMAP ou Gmail API
   - Compare chaque annonce détectée aux critères → scoring de pertinence
3. **Alerting** : Push + WhatsApp quand score ≥ seuil configurable
4. **Historique** : Tracker les annonces vues, favorites, contactées, visitées

**Modèle de données** :
```sql
CREATE TABLE habitat_criteres_immo (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL DEFAULT 'Recherche principale',
    ville VARCHAR(200),
    code_postal VARCHAR(10),
    rayon_km INTEGER DEFAULT 10,
    budget_min DECIMAL(12,2),
    budget_max DECIMAL(12,2),
    surface_min_m2 DECIMAL(8,2),
    surface_terrain_min_m2 DECIMAL(10,2),
    nb_pieces_min INTEGER,
    nb_chambres_min INTEGER,
    type_bien VARCHAR(50),               -- maison, appartement, terrain
    criteres_supplementaires JSONB,      -- garage, piscine, plain-pied, etc.
    seuil_alerte DECIMAL(5,2) DEFAULT 0.7, -- Score min pour notification
    actif BOOLEAN DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE habitat_annonces (
    id SERIAL PRIMARY KEY,
    critere_id INTEGER REFERENCES habitat_criteres_immo(id),
    source VARCHAR(100) NOT NULL,        -- "seloger", "leboncoin", "pap", "dvf"
    url_annonce VARCHAR(500),
    titre VARCHAR(500),
    prix DECIMAL(12,2),
    surface_m2 DECIMAL(8,2),
    surface_terrain_m2 DECIMAL(10,2),
    nb_pieces INTEGER,
    ville VARCHAR(200),
    code_postal VARCHAR(10),
    photos JSONB DEFAULT '[]',
    description_brute TEXT,
    score_pertinence DECIMAL(5,2),       -- Score calculé par rapport aux critères
    statut VARCHAR(50) DEFAULT 'nouveau', -- nouveau, vu, favori, contacte, visite, rejete
    prix_m2_secteur DECIMAL(8,2),        -- Prix au m² de référence DVF
    ecart_prix_pct DECIMAL(5,2),         -- % d'écart par rapport au prix marché
    notes TEXT,
    detectee_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Fonctionnalités UI** :
- Formulaire de critères de recherche (ville, budget, surface, terrain, pièces…)
- Dashboard annonces avec scoring et tri par pertinence
- Badge "Bonne affaire" si prix < prix_m2_secteur × surface - 10%
- Carte interactive des annonces (Leaflet/Mapbox)
- Pipeline de statut : Nouveau → Vu → Favori → Contacté → Visité → Rejeté / Offre
- Historique des prix DVF du secteur (graphique d'évolution)

### 19.5 Sous-module : Plans & Visualisation 3D

**Objectif** : Créer/importer des plans de maison et visualiser en 3D, pour explorer des options d'agrandissement ou de réaménagement.

**Stack technique** :

| Composant | Bibliothèque | Rôle |
|-----------|-------------|------|
| **Éditeur de plan 2D** | [Konva.js](https://konvajs.org/) + react-konva | Dessiner murs, pièces, portes, fenêtres sur canvas |
| **Visualisation 3D** | [Three.js](https://threejs.org/) + @react-three/fiber | Extrusion des plans 2D en 3D, navigation orbitale |
| **Import de plans** | Upload image/PDF → calibration manuelle | Tracer par-dessus un plan existant |
| **IA estimation** | Mistral | Estimer coûts de travaux à partir du plan |

**Modèle de données** :
```sql
CREATE TABLE habitat_plans (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES habitat_scenarios(id) ON DELETE SET NULL,
    nom VARCHAR(200) NOT NULL,
    type_plan VARCHAR(50) NOT NULL,       -- 'interieur', 'extension', 'jardin'
    donnees_plan JSONB NOT NULL,          -- Définition vectorielle (murs, pièces, cotes)
    image_fond_url VARCHAR(500),          -- Image de fond importée (plan existant)
    surface_totale_m2 DECIMAL(8,2),
    budget_estime DECIMAL(12,2),
    notes TEXT,
    version INTEGER DEFAULT 1,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE habitat_pieces (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES habitat_plans(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,            -- "Chambre bébé", "Bureau", "Salon"
    type_piece VARCHAR(50),               -- chambre, salon, cuisine, sdb, bureau, rangement
    surface_m2 DECIMAL(6,2),
    position_x DECIMAL(8,2),
    position_y DECIMAL(8,2),
    largeur DECIMAL(8,2),
    longueur DECIMAL(8,2),
    hauteur_plafond DECIMAL(4,2) DEFAULT 2.50,
    couleur_mur VARCHAR(7),               -- Hex code
    sol_type VARCHAR(50),                 -- parquet, carrelage, moquette
    meubles JSONB DEFAULT '[]',           -- Liste de meubles placés
    notes TEXT
);
```

**Fonctionnalités** :
- Éditeur de plan 2D : dessiner des murs, placer des pièces, ajouter des cotes
- Import d'un plan existant (photo/scan) comme fond → tracer par-dessus
- Visualisation 3D interactive (rotation orbitale) à partir du plan 2D
- Versioning des plans (v1, v2… pour comparer avant/après extension)
- **IA** : "Estimer le coût de cette extension de 25m²" → Mistral avec contexte local (prix au m² travaux de la région)
- Galerie de plans sauvegardés

### 19.6 Sous-module : Décoration & Meubles

**Objectif** : Concevoir la décoration intérieure pièce par pièce, avec palette de couleurs, sélection de meubles et suivi du budget (sortir enfin des cartons et des murs blancs !).

**Fonctionnalités** :
- **Par pièce** : créer un "projet déco" pour chaque pièce
- **Moodboard** : collecter des inspirations (images uploadées, URLs Pinterest)
- **Palette couleurs** : générer une palette harmonieuse (complémentaire, analogique…) — lib `chroma-js` ou IA
- **Catalogue meubles** : ajouter des meubles souhaités avec prix, dimensions, lien achat, priorité
- **Budget déco** : budget global → réparti par pièce → suivi des achats effectifs vs prévisionnel
- **IA suggestions** : "Propose-moi une palette pour un salon cosy de 20m² avec du parquet chêne"
- **Checklist emménagement** : liste de ce qu'il faut acheter par priorité (essentiel, confort, cosmétique)

**Modèle de données** :
```sql
CREATE TABLE habitat_projets_deco (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER REFERENCES habitat_pieces(id) ON DELETE SET NULL,
    nom_piece VARCHAR(200) NOT NULL,
    style VARCHAR(100),                   -- scandinave, industriel, bohème, moderne, classique
    palette_couleurs JSONB DEFAULT '[]',  -- [{nom, hex, role}]
    inspirations JSONB DEFAULT '[]',      -- [{url, image_url, description}]
    budget_prevu DECIMAL(10,2),
    budget_depense DECIMAL(10,2) DEFAULT 0,
    statut VARCHAR(50) DEFAULT 'idee',    -- idee, en_cours, termine
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE habitat_meubles_souhaites (
    id SERIAL PRIMARY KEY,
    projet_deco_id INTEGER REFERENCES habitat_projets_deco(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100),               -- canapé, table, rangement, luminaire, textile
    dimensions VARCHAR(200),              -- "L180 x P90 x H85 cm"
    prix_estime DECIMAL(10,2),
    prix_reel DECIMAL(10,2),
    url_achat VARCHAR(500),
    image_url VARCHAR(500),
    magasin VARCHAR(200),
    priorite VARCHAR(20) DEFAULT 'moyen', -- essentiel, haut, moyen, bas
    achete BOOLEAN DEFAULT FALSE,
    date_achat DATE,
    notes TEXT
);
```

### 19.7 Sous-module : Paysagisme — Aménagement jardin

**Objectif** : Concevoir l'aménagement du jardin de 2600 m² (terrain en pente, tout en longueur) avec zones fonctionnelles, plantations, et budget.

**Fonctionnalités** :
- **Plan jardin** : canvas 2D avec le contour du terrain (forme allongée, pente indiquée)
- **Zones fonctionnelles** : potager, pelouse, terrasse, aire de jeux, haie, verger, compost, piscine éventuelle…
- **Catalogue plantes** : sélection depuis le catalogue existant (`data/reference/plantes_catalogue.json`) + nouvelles entrées
- **Gestion de la pente** : visualisation du dénivelé, suggestions de terrasses/murets de soutènement
- **Budget paysagisme** : estimation par zone (terrassement, plantations, clôture, arrosage)
- **IA** : "Propose un aménagement pour un jardin en pente de 2600m² orienté sud avec 2 enfants en bas âge" → plan de zones + estimations
- **Intégration module Jardin existant** : lier les zones du plan paysager aux fiches plantes du module maison/jardin

**Modèle de données** :
```sql
CREATE TABLE habitat_zones_jardin (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES habitat_plans(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,            -- "Potager", "Aire de jeux", "Terrasse haute"
    type_zone VARCHAR(100),               -- potager, pelouse, terrasse, jeux, verger, haie, compost
    surface_m2 DECIMAL(8,2),
    altitude_relative DECIMAL(4,2),       -- Dénivelé par rapport au point bas (en mètres)
    position_x DECIMAL(8,2),
    position_y DECIMAL(8,2),
    largeur DECIMAL(8,2),
    longueur DECIMAL(8,2),
    plantes JSONB DEFAULT '[]',           -- [{nom, quantite, prix_unitaire}]
    amenagements JSONB DEFAULT '[]',      -- [{type, description, cout}]
    budget_estime DECIMAL(10,2),
    notes TEXT
);
```

### 19.8 Intégrations avec les modules existants

| Module existant | Interaction | Direction |
|----------------|-------------|-----------|
| **Maison/Projets** | Les travaux d'agrandissement → projets maison (suivi chantier, artisans) | Habitat → Maison |
| **Maison/Jardin** | Les zones jardin du plan → fiches plantes existantes (entretien, arrosage) | Habitat ↔ Jardin |
| **Maison/Finances** | Le budget habitat (déco, travaux, jardin) → agrégé dans les finances maison | Habitat → Finances |
| **Dashboard** | Widget "Projet Habitat" : avancement global, prochaines actions, budget restant | Habitat → Dashboard |
| **Famille/Budget** | Gros achats meubles/déco → suivi dans le budget famille | Habitat → Famille |
| **IA Chat** | Contexte habitat disponible pour le chat IA multi-module | Habitat → Chat IA |
| **Notifications** | Alertes annonces immobilières → Push/WhatsApp | Habitat → Notifications |

### 19.9 IA — Opportunités spécifiques

| # | Opportunité IA | Description |
|---|---------------|-------------|
| HAB-IA-1 | **Estimation budget travaux** | À partir du plan + type de travaux → estimation réaliste (coût/m² régional) |
| HAB-IA-2 | **Suggestions déco** | Palette couleurs + style → suggestions meubles, matériaux, agencement |
| HAB-IA-3 | **Analyse annonce** | Résumé automatique d'une annonce + scoring + comparaison au marché |
| HAB-IA-4 | **Plan jardin intelligent** | Contraintes (pente, orientation, budget, enfants) → proposition de zones |
| HAB-IA-5 | **Architecte virtuel** | "J'ai 30m² de plus, comment les répartir ?" → propositions d'agencement |
| HAB-IA-6 | **Comparateur prix meubles** | Nom du meuble → recherche des meilleurs prix en ligne |

### 19.10 Plan d'implémentation

| Phase | Contenu | Effort estimé | Priorité |
|-------|---------|---------------|----------|
| **H1** | Tables SQL + modèles ORM + schémas Pydantic + routes API CRUD | 6h | 🔴 |
| **H2** | Hub frontend + page Scénarios (comparateur) | 4h | 🔴 |
| **H3** | Veille Immo : critères + cron parsing emails + alertes | 8h | 🔴 |
| **H4** | Éditeur de plan 2D (Konva.js) + sauvegarde JSONB | 10h | 🟡 |
| **H5** | Visualisation 3D (Three.js / @react-three/fiber) | 8h | 🟡 |
| **H6** | Déco & Meubles : projets par pièce, moodboard, budget | 6h | 🟡 |
| **H7** | Paysagisme : plan jardin canvas + zones + catalogue plantes | 8h | 🟡 |
| **H8** | IA : estimations budget, suggestions déco, analyse annonces | 6h | 🟢 |
| **H9** | Intégrations inter-modules (projets, jardin, finances, dashboard) | 4h | 🟢 |
| **H10** | Carte interactive annonces (Leaflet) + historique DVF | 4h | 🟢 |

### 19.11 Dépendances npm/pip à ajouter

| Package | Usage | Côté |
|---------|-------|------|
| `react-konva` + `konva` | Éditeur de plan 2D canvas | Frontend |
| `@react-three/fiber` + `@react-three/drei` + `three` | Visualisation 3D | Frontend |
| `chroma-js` | Manipulation de couleurs (palettes) | Frontend |
| `react-leaflet` + `leaflet` | Carte interactive annonces | Frontend |
| `imaplib` (stdlib) ou `imap-tools` | Parsing emails alertes immo | Backend |
| `beautifulsoup4` | Parsing HTML des emails d'alertes | Backend |

---

## Annexe A — Tableau de synthèse des fichiers clés

### Backend

| Fichier | Rôle | État |
|---------|------|------|
| `src/api/main.py` | Point d'entrée FastAPI | ✅ |
| `src/api/routes/` (36 fichiers) | Routeurs REST | ✅ |
| `src/api/schemas/` (23 fichiers) | Schémas Pydantic | ⚠️ 8 stubs |
| `src/api/dependencies.py` | Auth JWT + RBAC | ✅ |
| `src/core/models/` (30 fichiers) | Modèles SQLAlchemy | ✅ |
| `src/core/ai/` | Client Mistral + cache + resilience | ✅ |
| `src/core/caching/` | Cache L1/L3 | ✅ |
| `src/core/db/` | Engine + sessions + migrations | ✅ |
| `src/services/core/cron/jobs.py` | 19 cron jobs | ⚠️ Bugs B2, B6 |
| `src/services/core/registry.py` | Service factory registry | ✅ |

### Frontend

| Fichier | Rôle | État |
|---------|------|------|
| `frontend/src/app/(app)/` | 57 pages applicatives | ✅ |
| `frontend/src/bibliotheque/api/` | 23 clients API | ⚠️ Manque admin.ts |
| `frontend/src/types/` | 13 fichiers types TS | ⚠️ batch-cooking minimal |
| `frontend/src/crochets/` | 12 hooks React | ✅ |
| `frontend/src/magasins/` | 4 stores Zustand | ✅ |
| `frontend/src/composants/ui/` | 29 shadcn/ui | ⚠️ 20 violations ARIA |
| `frontend/src/composants/disposition/` | 17 composants layout | ✅ |

### Infrastructure

| Fichier | Rôle | État |
|---------|------|------|
| `sql/INIT_COMPLET.sql` | Schéma DB complet | ⚠️ Incohérences S1-S5 |
| `tests/` (186 fichiers) | Suite de tests | ⚠️ Couverture 65% |
| `docs/` (25 fichiers) | Documentation | ⚠️ Guides datés |
| `pyproject.toml` | Config Python/tools | ✅ |
| `pytest.ini` | Config tests | ✅ |
| `.github/workflows/` | CI/CD | ✅ |

---

## Annexe B — Checklist review avant implémentation

Avant de commencer chaque phase, vérifier :

- [ ] Les tests existants passent (`pytest --tb=short`)
- [ ] Le frontend build (`cd frontend && npx next build`)
- [ ] Pas de régressions sur les endpoints critiques
- [ ] La doc est mise à jour avant de merge
- [ ] Le `INIT_COMPLET.sql` est cohérent avec les modèles SQLAlchemy
- [ ] Les nouveaux endpoints ont des schémas Pydantic + types TypeScript
- [ ] Les nouveaux services utilisent `@service_factory`
- [ ] Les nouveaux cron jobs ont des tests unitaires
- [ ] Les interactions inter-modules utilisent le bus d'événements (pas d'appels directs)
- [ ] Le mode admin est invisible pour l'utilisateur standard

---

*Rapport généré le 29 mars 2026 — Audit exhaustif de l'application Assistant Matanne*
*Prochaine mise à jour recommandée : après chaque phase du plan d'action*
