# 🔍 ANALYSE COMPLÈTE — Assistant Matanne

> **Date** : 30 mars 2026  
> **Scope** : Audit 360° de l'application complète (Backend + Frontend + SQL + Tests + Docs + Infra)  
> **Objectif** : Détecter bugs, gaps, features manquantes, consolider SQL, planifier IA/automations/notifications, simplifier l'UX

---

## 📊 Tableau de bord projet

| Catégorie | Métrique | État |
|-----------|----------|------|
| **Tables SQL** | 143 tables, RLS, triggers, views | ✅ Solide |
| **Modèles ORM** | 31 fichiers, ~95% alignés SQL | ✅ |
| **Endpoints API** | 242+ endpoints REST (42 routers) | ✅ |
| **Services** | 60+ services (23 IA) | ✅ |
| **Pages Frontend** | 103 pages (App Router) | ⚠️ ~12 pages IA incomplètes |
| **Composants** | 105+ composants React | ✅ |
| **Tests Backend** | 70+ fichiers pytest | ⚠️ 9 routes non testées |
| **Tests Frontend** | 12 E2E + ~5 unit tests | ⚠️ Couverture unit faible |
| **Documentation** | 26 docs + 8 guides modules | ✅ 90% à jour |
| **Jobs CRON** | 38+ jobs APScheduler | ✅ Opérationnel |
| **Notifications** | 4 canaux (push/email/WhatsApp/ntfy) | ✅ |
| **PWA** | Service Worker + manifest + offline | ✅ |

---

## Table des matières

1. [Bugs et problèmes détectés](#1--bugs-et-problèmes-détectés)
2. [Gaps et features manquantes](#2--gaps-et-features-manquantes)
3. [Consolidation SQL](#3--consolidation-sql)
4. [Couverture de tests](#4--couverture-de-tests)
5. [Documentation — État et manques](#5--documentation--état-et-manques)
6. [Interactions intra-modules](#6--interactions-intra-modules)
7. [Interactions inter-modules](#7--interactions-inter-modules)
8. [Opportunités IA](#8--opportunités-ia)
9. [Jobs automatiques (CRON)](#9--jobs-automatiques-cron)
10. [Notifications — WhatsApp, Email, Push](#10--notifications--whatsapp-email-push)
11. [Mode Admin manuel](#11--mode-admin-manuel)
12. [Simplification du flux utilisateur](#12--simplification-du-flux-utilisateur)
13. [Organisation du code](#13--organisation-du-code)
14. [Axes d'innovation](#14--axes-dinnovation)
15. [Plan d'action priorisé](#15--plan-daction-priorisé)

---

## 1. 🐛 Bugs et problèmes détectés

### 🔴 Critiques

| # | Problème | Fichier | Impact |
|---|----------|---------|--------|
| B1 | **5 blocs `except: pass` silencieux** dans le webhook WhatsApp — erreurs avalées sans log | `src/api/routes/webhooks_whatsapp.py` (L621, 964, 984, 1008) | Messages WhatsApp perdus silencieusement |
| B2 | **`except: pass`** dans le endpoint auth — échec d'audit silencieux | `src/api/routes/auth.py` (L94) | Impossible de tracer les tentatives de login |
| B3 | **`except: pass`** dans l'export PDF — erreur masquée | `src/api/routes/export.py` (L204) | Exports PDF échouent sans feedback |
| B4 | **`except: pass`** dans les préférences — sauvegarde silencieuse | `src/api/routes/preferences.py` (L285) | Préférences non sauvegardées sans erreur |
| B5 | **Cache d'idempotence en mémoire** pour les courses — incompatible multi-instance | `src/api/routes/courses.py` | Doublons possibles si plusieurs workers |

### 🟡 Modérés

| # | Problème | Fichier | Impact |
|---|----------|---------|--------|
| B6 | **Pas de rate limiting sur endpoints admin** | `src/api/routes/admin.py` | Potentiel DoS sur les actions admin sensibles |
| B7 | **Rate limiting IA global** vs per-user — ambiguïté | `src/core/ai/rate_limit.py` | Un utilisateur peut consommer le quota de tous |
| B8 | **CORS avec origines par défaut** — devrait être strict en prod | `src/api/main.py` | Risque CORS en production |
| B9 | **Pas d'invalidation cache auto** quand les modèles sont modifiés directement en DB | `src/core/caching/` | Données stales possibles après update direct |
| B10 | **CSP avec `unsafe-inline`** pour scripts/styles dans `next.config.ts` | `frontend/next.config.ts` | Vulnérabilité XSS potentielle |

### 🟢 Mineurs

| # | Problème | Impact |
|---|----------|--------|
| B11 | Certaines pages frontend sans skeleton/loading pendant le fetch initial | UX dégradée (flash of empty content) |
| B12 | WebSocket hooks — nettoyage on unmount à vérifier | Fuite mémoire potentielle |
| B13 | Toast notifications auto-dismiss — pas extensible par l'utilisateur | Messages importants potentiellement ratés |
| B14 | Pas de retry auto sur erreurs DB transitoires | Erreurs intermittentes non récupérées |
| B15 | Auth WebSocket — documentation manquante sur la validation JWT | Confusion sur la sécurisation des WS |

### Actions correctives

```
Priorité 1 (immédiat) : B1-B4 — Remplacer tous les `except: pass` par des logs + raise/fallback
Priorité 2 (court terme) : B5-B9 — Rate limiting admin, per-user IA, CORS strict prod
Priorité 3 (moyen terme) : B10-B15 — CSP strict, skeletons, WS cleanup
```

---

## 2. 🧩 Gaps et features manquantes

### Backend — Endpoints/Services manquants

| # | Gap | Module | Effort | Priorité |
|---|-----|--------|--------|----------|
| G1 | **Dashboard personnalisable** — pas de CRUD widgets par utilisateur | Dashboard | M | 🔴 Haute |
| G2 | **Historique des modifications** (audit trail) pour recettes/planning | Cuisine | M | 🟡 Moyenne |
| G3 | **Mode collaboratif** courses temps réel — WebSocket implémenté mais UX basique | Courses | L | 🟡 Moyenne |
| G4 | **Import bulk recettes** — import CSV/JSON en masse | Cuisine | S | 🟢 Basse |
| G5 | **Scan ticket de caisse** → dépenses auto (OCR) | Famille | L | 🟡 Moyenne |
| G6 | **Comparateur de prix** — historique prix par article | Courses | L | 🟡 Moyenne |
| G7 | **Planning adaptatif** — ajuste automatiquement selon météo/saison | Planning | L | 🟢 Innovation |
| G8 | **Suivi énergie détaillé** — graphiques conso par appareil | Maison | M | 🟡 Moyenne |
| G9 | **Calendrier partagé famille** — sync Google/Apple Calendar bidirectionnelle | Planning | L | 🔴 Haute |
| G10 | **Mode hors-ligne enrichi** — sync différée des modifications | Global | XL | 🟡 Moyenne |

### Frontend — Pages incomplètes

| # | Page | État | Action requise |
|---|------|------|----------------|
| G11 | `/ia-avancee/suggestions-achats` | Routing existe, contenu minimal | Implémenter la page complète |
| G12 | `/ia-avancee/diagnostic-plante` | Lien dans le hub, pas de page fonctionnelle | Créer la page + connecter l'API |
| G13 | `/ia-avancee/planning-adaptatif` | Lien dans le hub, pas de page fonctionnelle | Créer la page + connecter l'API |
| G14 | `/ia-avancee/optimisation-stock` | Lien dans le hub, pas de page fonctionnelle | Créer la page + connecter l'API |
| G15 | `/ia-avancee/analyse-habitudes` | Lien dans le hub, pas de page fonctionnelle | Créer la page + connecter l'API |
| G16 | `/ia-avancee/conseiller-energie` | Lien dans le hub, incomplet | Finaliser la page |
| G17 | `/ia-avancee/prevision-courses` | Lien dans le hub, incomplet | Finaliser la page |
| G18 | `/ia-avancee/menu-equilibre` | Lien dans le hub, incomplet | Finaliser la page |
| G19 | `/ia-avancee/routine-optimale` | Lien dans le hub, incomplet | Finaliser la page |
| G20 | `/ia-avancee/bilan-financier` | Lien dans le hub, incomplet | Finaliser la page |
| G21 | `/ia-avancee/assistant-jardin` | Lien dans le hub, incomplet | Finaliser la page |
| G22 | `/ia-avancee/coach-bien-etre` | Lien dans le hub, incomplet | Finaliser la page |
| G23 | Plusieurs pages sans error boundary propre | `planning`, `habitat`, `ia-avancee` | Ajouter des error boundaries |
| G24 | Loading states (skeletons) manquants sur pages hub | `planning`, `habitat`, `maison` sous-pages | Ajouter `loading.tsx` |

### API Client ↔ Backend — Désalignements

| # | Problème | Action |
|---|----------|--------|
| G25 | `ia_avancee.ts` a 4 fonctions mais le hub référence 14 outils | Ajouter les 10 fonctions client manquantes |
| G26 | Endpoints admin riches côté backend, frontend admin basique | Enrichir les pages admin frontend |
| G27 | RGPD (export/suppression données) — client existe mais pas de page dédiée | Ajouter section RGPD dans `/parametres` |

---

## 3. 🗄️ Consolidation SQL

### État actuel

- **Fichier source** : `sql/INIT_COMPLET.sql` (~3000+ lignes)
- **Migrations** : `sql/migrations/` (V003 à V007)
- **Alembic** : Archivé intentionnellement (stratégie SQL-first)
- **Alignement ORM** : ~95% (31 fichiers modèles ↔ 143 tables)

### Problèmes identifiés

| # | Problème | Impact | Action |
|---|----------|--------|--------|
| S1 | **INIT_COMPLET.sql monolithique** (3000+ lignes) — difficile à naviguer | Maintenance | Découper en fichiers thématiques |
| S2 | **Tables utilitaires orphelines** — `notes_memos`, `presse_papier_entrees`, `releves_energie` sans ORM complet | Données inaccessibles | Créer/compléter les modèles ORM |
| S3 | **Pas de vérification auto** SQL ↔ ORM en CI | Dérives silencieuses possibles | Ajouter `test_schema_coherence.py` au CI |
| S4 | **Indexes manquants** potentiels sur colonnes fréquemment filtrées | Performance | Audit des queries lentes |
| S5 | **Migrations non versionnées** en dev — OK mais risque de conflits | Team dev | Documenter le workflow SQL-first |

### Plan de consolidation SQL (sans migrations/versioning)

```
Phase 1 — Découpage thématique du SQL
  sql/
  ├── INIT_COMPLET.sql          → Garde comme script unique d'init (régénéré)
  ├── schema/
  │   ├── 01_extensions.sql     → Extensions PostgreSQL
  │   ├── 02_functions.sql      → Fonctions et triggers
  │   ├── 03_cuisine.sql        → Tables cuisine (recettes, ingredients, planning, courses)
  │   ├── 04_famille.sql        → Tables famille (profils, activités, budget, santé)
  │   ├── 05_maison.sql         → Tables maison (projets, entretien, jardin, stocks)
  │   ├── 06_habitat.sql        → Tables habitat (scénarios, plans, veille)
  │   ├── 07_jeux.sql           → Tables jeux (paris, loto, euromillions)
  │   ├── 08_systeme.sql        → Tables système (logs, config, migrations)
  │   ├── 09_notifications.sql  → Tables notifications (push, webhooks)
  │   ├── 10_finances.sql       → Tables finances (dépenses, budgets)
  │   ├── 11_views.sql          → Toutes les vues
  │   ├── 12_indexes.sql        → Tous les index
  │   └── 13_rls_policies.sql   → Toutes les politiques RLS
  ├── seed/                     → Données de seed (référence)
  └── migrations/               → Garde tel quel

Phase 2 — Script de régénération
  scripts/db/regenerate_init.py → Concatène les fichiers schema/* → INIT_COMPLET.sql

Phase 3 — Validation CI
  tests/sql/test_schema_coherence.py → Vérifie l'alignement SQL ↔ ORM (existe déjà)
  Ajouter au pipeline CI
```

---

## 4. 🧪 Couverture de tests

### Backend — Tests par couche

| Couche | Fichiers | Tests | Couverture | État |
|--------|----------|-------|------------|------|
| **Core** (config, DB, cache, decorators) | 12 fichiers | ~100 tests | 90% | ✅ Solide |
| **Modèles ORM** | 22 fichiers | ~80 tests | 70% | ⚠️ Partiel |
| **Routes API** | 30 fichiers | ~150 tests | 77% | ⚠️ 9 routes non testées |
| **Services** | 20+ fichiers | ~100 tests | 90% | ✅ Solide |
| **Spécialisés** (contrats, perf, SQL) | 5 fichiers | ~30 tests | Variable | ✅ |
| **Total Backend** | **70+ fichiers** | **~460 tests** | **~75%** | ⚠️ |

### Routes API sans tests (9 routes)

| Route | Fichier | Priorité test |
|-------|---------|---------------|
| `dashboard` | `src/api/routes/dashboard.py` | 🔴 Haute |
| `famille_jules` | `src/api/routes/famille_jules.py` | 🔴 Haute |
| `famille_budget` | `src/api/routes/famille_budget.py` | 🟡 Moyenne |
| `famille_activites` | `src/api/routes/famille_activites.py` | 🟡 Moyenne |
| `maison_projets` | `src/api/routes/maison_projets.py` | 🟡 Moyenne |
| `maison_jardin` | `src/api/routes/maison_jardin.py` | 🟡 Moyenne |
| `maison_finances` | `src/api/routes/maison_finances.py` | 🟡 Moyenne |
| `maison_entretien` | `src/api/routes/maison_entretien.py` | 🟡 Moyenne |
| `partage` | `src/api/routes/partage.py` | 🟢 Basse |

### Frontend — Couverture tests

| Type | Fichiers | Couverture | État |
|------|----------|------------|------|
| **Unit (Vitest)** | ~5 fichiers (stores + API clients) | Faible (~20%) | 🔴 À renforcer |
| **E2E (Playwright)** | 12 fichiers | Bonne (smoke tests) | ✅ |
| **Visual Regression** | 1 fichier | Basique | ⚠️ |

### Plan d'amélioration tests

```
Objectif : 85% couverture backend, 50% frontend unit

Backend — Priorité 1 :
  ├── tests/api/test_routes_dashboard.py (CRUD dashboard + widgets)
  ├── tests/api/test_routes_famille_jules.py (profil, jalons, suggestions IA)
  ├── tests/api/test_routes_famille_budget.py (dépenses, budgets, historique)
  ├── tests/api/test_routes_maison_projets.py (projets, tâches, budget)
  └── tests/api/test_routes_partage.py (partage recettes, listes)

Backend — Priorité 2 :
  ├── tests/api/test_routes_famille_activites.py
  ├── tests/api/test_routes_maison_jardin.py
  ├── tests/api/test_routes_maison_finances.py
  └── tests/api/test_routes_maison_entretien.py

Frontend — Priorité 1 :
  ├── src/__tests__/hooks/ (tests des custom hooks : utiliser-api, utiliser-auth)
  ├── src/__tests__/components/ (composants critiques : formulaire-recette, sidebar)
  └── src/__tests__/pages/ (tests de rendering des pages hub)

Frontend — Priorité 2 :
  ├── E2E complets pour chaque module (pas juste smoke)
  └── Tests d'accessibilité (axe-core)
```

---

## 5. 📚 Documentation — État et manques

### Documents existants — État

| Document | Statut | Notes |
|----------|--------|-------|
| `docs/ARCHITECTURE.md` | ✅ À jour | Architecture complète FastAPI + Next.js |
| `docs/API_REFERENCE.md` | ✅ À jour | 242+ endpoints documentés |
| `docs/MODULES.md` | ✅ À jour | Carte fonctionnelle des modules |
| `docs/SERVICES_REFERENCE.md` | ✅ À jour | Tous les services documentés |
| `docs/ERD_SCHEMA.md` | ⚠️ À rafraîchir | Diagramme Mermaid à regenerer (143 tables) |
| `docs/PATTERNS.md` | ✅ À jour | Patterns résilience, cache, events |
| `docs/CRON_JOBS.md` | ✅ À jour | 38+ jobs documentés |
| `docs/NOTIFICATIONS.md` | ✅ À jour | 4 canaux, throttling, digest |
| `docs/INTER_MODULES.md` | ✅ À jour | 8+ flux inter-modules |
| `docs/AI_SERVICES.md` | ✅ À jour | 23 services IA documentés |
| `docs/AUTOMATIONS.md` | ✅ À jour | Engine If→Then |
| `docs/ADMIN_GUIDE.md` | ✅ À jour | Guide admin complet |
| `docs/ADMIN_RUNBOOK.md` | ✅ À jour | Procédures opérationnelles |
| `docs/DEPLOYMENT.md` | ✅ À jour | Railway + Vercel + Supabase |
| `docs/TROUBLESHOOTING.md` | ✅ À jour | FAQ technique |
| `docs/DEVELOPER_SETUP.md` | ✅ À jour | Setup local |
| `docs/TESTING_ADVANCED.md` | ✅ À jour | Mutation + contract testing |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | ⚠️ Peut être enrichi | Exemples SQLAlchemy 2.0+ |
| `docs/REDIS_SETUP.md` | ⚠️ Optionnel | Feature rarement utilisée |
| `docs/HABITAT_MODULE.md` | ✅ Nouveau | Module habitat complet |
| `docs/GAMIFICATION.md` | ✅ Nouveau | Badges sport + nutrition |
| `docs/WHATSAPP_SETUP.md` | ✅ À jour | Configuration Meta Cloud API |
| `docs/FRONTEND_ARCHITECTURE.md` | ✅ À jour | Architecture Next.js |
| `docs/UI_COMPONENTS.md` | ✅ À jour | Composants shadcn/ui |
| `docs/MIGRATION_GUIDE.md` | ✅ À jour | Workflow SQL-first |
| `docs/INDEX.md` | ✅ À jour | Index navigation |

### Documentation manquante

| # | Document manquant | Priorité | Contenu attendu |
|---|-------------------|----------|-----------------|
| D1 | **Guide module IA Avancée** | 🔴 Haute | Les 14 outils IA, endpoints, prompts, cache, limites |
| D2 | **Guide intégration Sentry** | 🟡 Moyenne | Setup DSN, sampling, error boundaries, replay |
| D3 | **Guide Docker production** | 🟡 Moyenne | Railway-specific, performance tuning, scaling |
| D4 | **Design System visuel** | 🟢 Basse | Specs visuels composants (couleurs, spacing, typo) |
| D5 | **Guide contribution** (CONTRIBUTING.md) | 🟡 Moyenne | Conventions, PR process, code review |
| D6 | **Changelog technique Phase 10** | 🟡 Moyenne | Détails techniques des innovations |
| D7 | **Guide PWA/Offline** | 🟢 Basse | Service Worker, cache strategies, sync |
| D8 | **Schéma d'architecture Mermaid** complet | 🟡 Moyenne | Diagramme architectural à jour |

### Guides modules — Couverture

| Module | Guide | État |
|--------|-------|------|
| 🍽️ Cuisine | `docs/guides/cuisine/README.md` + `batch_cooking.md` | ✅ Complet |
| 👶 Famille | `docs/guides/famille/README.md` | ✅ Complet |
| 🏡 Maison | `docs/guides/maison/README.md` | ✅ Complet |
| 📊 Dashboard | `docs/guides/dashboard/README.md` | ✅ Complet |
| 🎮 Jeux | `docs/guides/jeux/README.md` | ✅ Complet |
| 🛠️ Outils | `docs/guides/outils/README.md` | ✅ Complet |
| 📅 Planning | `docs/guides/planning/README.md` | ✅ Complet |
| 🏘️ Habitat | `docs/HABITAT_MODULE.md` | ✅ Complet |
| 🤖 IA Avancée | ❌ Manquant | 🔴 À créer |
| ⚙️ Admin | `docs/ADMIN_GUIDE.md` | ✅ Complet |

---

## 6. 🔗 Interactions intra-modules

### Flux internes par module

#### 🍽️ Cuisine (Recettes → Planning → Courses → Inventaire → Batch Cooking)

```
Recettes ──planifier──→ Planning ──générer──→ Liste Courses
    │                      │                      │
    │                      ▼                      ▼
    │               Batch Cooking           Inventaire
    │                      │                      │
    └──versions jules──────┘──décrémenter stock──→┘
```

| Flux | État | Action |
|------|------|--------|
| Recette → ajouter au planning | ✅ Implémenté | — |
| Planning → générer liste courses | ✅ Implémenté | — |
| Courses achetées → mettre à jour inventaire | ✅ Implémenté | — |
| Inventaire bas → suggestion recettes avec dispo | ⚠️ Partiel | Enrichir avec IA |
| Batch cooking → décrémenter stocks | ✅ Implémenté | — |
| Recette → version Jules (bébé) | ✅ Implémenté | — |
| Anti-gaspillage → suggestion recettes péremption | ✅ Implémenté | — |
| **MANQUANT** : Retour recette → ajuster suggestions futures | ❌ | Implémenter feedback loop IA |
| **MANQUANT** : Historique repas → éviter répétitions | ⚠️ Partiel | Algorithme de diversité |

#### 👶 Famille (Jules → Activités → Budget → Santé → Documents)

| Flux | État | Action |
|------|------|--------|
| Profil Jules → suggestions activités par âge | ✅ Implémenté | — |
| Activités → suivi jalons développement | ✅ Implémenté | — |
| Budget famille → suivi dépenses | ✅ Implémenté | — |
| Anniversaires → rappels + budget cadeaux | ✅ Implémenté | — |
| Documents → alertes expiration | ✅ Implémenté | — |
| Voyages → checklists + budget | ✅ Implémenté | — |
| **MANQUANT** : Jalons Jules → cours/activités recommandés | ❌ | IA recommandation |
| **MANQUANT** : Budget → alertes seuil dépassement | ⚠️ Partiel | Notification push |

#### 🏡 Maison (Projets → Entretien → Jardin → Énergie → Stocks)

| Flux | État | Action |
|------|------|--------|
| Projets → tâches → suivi avancement | ✅ Implémenté | — |
| Entretien préventif → calendrier tâches | ✅ Implémenté | — |
| Jardin → calendrier saisons → tâches | ✅ Implémenté | — |
| Stocks maison → alertes réapprovisionnement | ✅ Implémenté | — |
| Énergie → relevés compteurs → graphiques | ✅ Implémenté | — |
| **MANQUANT** : Entretien → devis artisans auto | ❌ | Lier artisans + estimations |
| **MANQUANT** : Projets terminés → mise à jour valeur bien | ❌ | Impact habitat |

#### 🎮 Jeux (Paris → Loto → EuroMillions → Bankroll → Performance)

| Flux | État | Action |
|------|------|--------|
| Analyse matchs → paris proposés | ✅ Implémenté | — |
| Backtest stratégies → scoring | ✅ Implémenté | — |
| Bankroll → limite mise responsable | ✅ Implémenté | — |
| Stats historiques → heatmaps numéros | ✅ Implémenté | — |
| **MANQUANT** : Résultats auto → P&L instantané | ⚠️ Cron existe | Affichage temps réel |
| **MANQUANT** : Série perdante → alerte jeu responsable | ⚠️ Partiel | Push notification |

---

## 7. 🔀 Interactions inter-modules

### Flux inter-modules existants (8 implémentés)

| # | Flux | Source → Cible | Fichier | Trigger |
|---|------|----------------|---------|---------|
| 1 | Péremption → Recettes | Inventaire → Cuisine | `inter_module_peremption_recettes.py` | Job/API |
| 2 | Total courses → Budget | Courses → Famille | `inter_module_courses_budget.py` | Save courses |
| 3 | Document expire → Alerte | Famille → Notifications | `inter_module_documents_notifications.py` | Job J-30/15/7/1 |
| 4 | Chat IA → Multi-contexte | Tous → Utilitaires | `inter_module_chat_contexte.py` | Chat appel |
| 5 | Batch cooking → Stock | Cuisine → Inventaire | `inter_module_batch_inventaire.py` | Fin session |
| 6 | Anniversaires → Budget | Famille → Famille | `inter_module_anniversaires_budget.py` | Auto |
| 7 | Voyages → Budget | Voyages → Famille | `inter_module_voyages_budget.py` | Save voyage |
| 8 | Mises jeux → Budget | Jeux → Famille | `inter_module_budget_jeux.py` | Mise placée |

### Flux inter-modules à implémenter (15 opportunités)

| # | Flux proposé | Source → Cible | Valeur | Effort |
|---|-------------|----------------|--------|--------|
| I1 | **Récolte jardin → Recettes saison** | Maison/Jardin → Cuisine | 🔴 Haute | M |
| I2 | **Garmin santé → Activités Jules** | Famille/Garmin → Famille/Jules | 🟡 Moyenne | M |
| I3 | **Anomalie énergie → Tâche entretien** | Maison/Énergie → Maison/Entretien | 🔴 Haute | S |
| I4 | **Budget dépassement → Alerte dashboard** | Famille/Budget → Dashboard | 🔴 Haute | S |
| I5 | **Météo → Planning repas adapté** | Outils/Météo → Cuisine/Planning | 🟡 Moyenne | M |
| I6 | **Météo → Tâches jardin urgentes** | Outils/Météo → Maison/Jardin | 🟡 Moyenne | S |
| I7 | **Projets terminés → Valeur bien habitat** | Maison/Projets → Habitat | 🟡 Moyenne | M |
| I8 | **Entretien artisan → Devis comparatif auto** | Maison/Entretien → Maison/Artisans | 🟡 Moyenne | M |
| I9 | **Inventaire → Courses prédictives** | Inventaire → Courses | 🔴 Haute | L |
| I10 | **Résultats paris → P&L famille** | Jeux → Famille/Budget | 🟡 Moyenne | S |
| I11 | **Routines santé → Briefing matinal** | Famille/Santé → Dashboard | 🟡 Moyenne | S |
| I12 | **Anniversaire → Suggestion cadeau IA** | Famille → IA Avancée | 🟢 Innovation | M |
| I13 | **Retour recette → Ajuster planning futur** | Cuisine → Planning | 🔴 Haute | M |
| I14 | **Contrats maison → Alertes renouvellement** | Maison/Contrats → Notifications | 🟡 Moyenne | S |
| I15 | **Score gamification → Récompenses famille** | Gamification → Famille | 🟢 Innovation | M |

### Event Bus — Événements non exploités

Le bus d'événements `EventBus` émet des événements `recette.*`, `stock.*`, `courses.*`, `entretien.*`, `planning.*`, `jeux.*` — mais les **seuls abonnés sont pour l'invalidation de cache**. 

**Opportunité** : Ajouter des abonnés pour déclencher les flux I1-I15 ci-dessus via le bus existant, sans coupler les services.

```python
# Exemple : Récolte jardin → Suggestions recettes
bus.souscrire("jardin.recolte", lambda evt: 
    get_suggestions_service().suggerer_recettes_saison(evt["plantes_recoltees"])
)
```

---

## 8. 🤖 Opportunités IA

### Services IA existants (23 services)

| Service | Module | Fonctionnalité |
|---------|--------|----------------|
| `ChatAIService` | Outils | Chat multi-contexte |
| `BriefingMatinalService` | Dashboard | Briefing quotidien personnalisé |
| `ServiceSuggestions` | Cuisine | Suggestions recettes |
| `ServiceVersionRecetteJules` | Famille | Adaptation recettes bébé |
| `WeekendAIService` | Famille | Idées weekend |
| `SoireeAIService` | Famille | Idées soirée couple |
| `JulesAIService` | Famille | Activités par âge |
| `ServiceResumeHebdo` | Famille | Résumé hebdo narratif |
| `AchatsIAService` | Famille | Suggestions cadeaux |
| `BilanMensuelService` | Rapports | Bilan financier |
| `ProjetsService` | Maison | Estimation projets |
| `JardinService` | Maison | Conseils saisonniers |
| `EntretienService` | Maison | Optimisation nettoyage |
| `FicheTacheService` | Maison | Fiches tâches ménage |
| `EnergieAnomaliesIAService` | Maison | Détection anomalies énergie |
| `ConseillierMaisonService` | Maison | Conseils contextuels |
| `DiagnosticsIAArtisansService` | Maison | Diagnostic pannes |
| `PlansHabitatAIService` | Habitat | Analyse plans |
| `DecoHabitatService` | Habitat | Concepts déco IA |
| `JeuxAIService` | Jeux | Analyse paris sportifs |
| `EuromillionsIAService` | Jeux | Stratégies numériques |
| `ServiceAnomaliesFinancieres` | Dashboard | Détection anomalies dépenses |
| `ResumeFamilleIAService` | Dashboard | Résumé multi-module |

### Nouvelles opportunités IA (14 propositions)

| # | Opportunité | Module | Description | Effort |
|---|-------------|--------|-------------|--------|
| IA1 | **Nutritionniste IA** | Cuisine | Analyse nutrition hebdo → recommandations ajustement (protéines, fibres, vitamines) | M |
| IA2 | **Coach budget IA** | Famille | Analyse tendances dépenses → suggestions économies avec benchmarks | M |
| IA3 | **Planificateur voyages IA** | Famille | Génération itinéraire + checklist + budget prévisionnel | L |
| IA4 | **Diagnostic plante photo** | Maison | Upload photo plante → diagnostic maladie + traitement (vision IA) | M |
| IA5 | **Optimiseur courses prédictif** | Courses | ML sur historique achats → liste courses pré-remplie | L |
| IA6 | **Assistant vocal enrichi** | Outils | Commandes vocales → actions multi-modules (ex: "ajoute du lait à la liste") | L |
| IA7 | **Résumé vocal quotidien** | Dashboard | TTS du briefing matinal → écoutable en voiture | M |
| IA8 | **Styliste déco personnalisé** | Habitat | Analyse photos pièces → suggestions déco personnalisées | L |
| IA9 | **Prédicteur pannes** | Maison | ML sur âge/usage appareils → maintenance préventive | M |
| IA10 | **Générateur menus événements** | Cuisine | Menu complet pour anniversaire/fête selon nb personnes + régimes | M |
| IA11 | **Analyseur ticket de caisse** | Famille | OCR ticket → catégorisation auto dépenses + détection promos | L |
| IA12 | **Comparateur recettes nutritionnel** | Cuisine | Comparer 2 recettes → différences nutritionnelles visuelles | S |
| IA13 | **Assistant devis travaux** | Maison | Description travaux → estimation prix + matériaux nécessaires | M |
| IA14 | **Coach routine bien-être** | Famille | Analyse habitudes → suggestions routines personnalisées selon Garmin | M |

### Architecture IA — Améliorations suggérées

```
Amélioration 1 : Rate limit per-user (pas global)
  → Chaque utilisateur a son propre quota IA
  → Empêche un user de bloquer tous les autres

Amélioration 2 : Cache sémantique enrichi
  → Utiliser embeddings pour matcher des prompts similaires (pas juste hash exact)
  → Réduire les appels IA de 30-40%

Amélioration 3 : Fallback model
  → Si Mistral down → fallback vers un modèle local (Ollama) ou autre provider
  → Circuit breaker déjà en place, ajouter le fallback

Amélioration 4 : Feedback loop
  → Stocker les retours utilisateurs (thumbs up/down) sur les suggestions IA
  → Utiliser comme contexte pour améliorer les prompts
```

---

## 9. ⏰ Jobs automatiques (CRON)

### Jobs existants (38+ planifiés)

#### Rappels & Alertes

| Job | Schedule | Description | Canal |
|-----|----------|-------------|-------|
| `rappels_famille` | 7h00 | Rappels activités/RDV du jour | push, ntfy |
| `rappels_maison` | 8h00 | Tâches entretien du jour | push, ntfy |
| `alertes_peremption_48h` | 6h00 | Produits expirant dans 48h | push, ntfy |
| `alertes_stocks_bas` | Lun 9h | Stocks sous seuil | push |
| `rappels_documents_expirants` | 8h30 | Documents J-30/15/7/1 | push, email |
| `rappels_vaccins` | 8h15 | Vaccins à planifier | push, email |
| `alertes_contrats` | 8h45 | Contrats à renouveler | push, email |

#### Notifications & Digests

| Job | Schedule | Description | Canal |
|-----|----------|-------------|-------|
| `push_quotidien` | 9h00 | Push quotidien résumé | push |
| `digest_ntfy` | 9h00 | Digest via ntfy | ntfy |
| `digest_whatsapp_matinal` | 7h30 | Briefing matinal WhatsApp | whatsapp |
| `digest_email_hebdo` | Lun 8h | Digest email hebdomadaire | email |
| `digest_notifications_queue` | /2h | Flush file de notifications | multi |

#### Rapports & Résumés

| Job | Schedule | Description |
|-----|----------|-------------|
| `resume_hebdo` | Lun 7h30 | Résumé hebdo IA narratif |
| `rapport_mensuel_budget` | 1er 8h15 | Bilan budget mensuel |
| `rapport_jardin` | Mer 20h | Rapport jardin hebdo |
| `bilan_mensuel_complet` | 1er 9h | Bilan multi-module |
| `score_weekend` | Ven 17h | Score préparation weekend |

#### Syncs & Scraping

| Job | Schedule | Description |
|-----|----------|-------------|
| `sync_calendrier_scolaire` | 5h30 | Sync vacances scolaires |
| `sync_google_calendar` | 23h | Sync calendrier Google |
| `sync_openfoodfacts` | Dim 3h | Sync données nutritionnelles |
| `sync_garmin` | 6h | Sync données Garmin |
| `scraping_paris_cotes` | /2h | Scraping cotes sportives |
| `scraping_paris_resultats` | 23h | Résultats matchs |
| `scraping_fdj_resultats` | 21h30 | Résultats Loto/EuroMillions |
| `backtest_grilles` | 22h | Backtest stratégies loto |
| `detection_value_bets` | /30min | Détection paris value |
| `analyse_series` | 9h | Analyse séries jeux |

#### Maintenance

| Job | Schedule | Description |
|-----|----------|-------------|
| `nettoyage_cache` | 3h | Purge cache périmé |
| `nettoyage_logs` | 4h | Rotation logs anciens |
| `automations_runner` | /5min | Exécution automations If→Then |
| `health_check_services` | /15min | Vérification santé services |
| `backup_etats_persistants` | 2h | Sauvegarde états |

### Jobs CRON à ajouter (8 propositions)

| # | Job proposé | Schedule | Description | Priorité |
|---|-------------|----------|-------------|----------|
| C1 | `prediction_courses_hebdo` | Dim 18h | Générer liste courses prédictive pour la semaine | 🔴 |
| C2 | `rapport_energie_mensuel` | 1er 10h | Rapport consommation énergie + comparaison mois précédent | 🟡 |
| C3 | `suggestions_recettes_saison` | 1er et 15 6h | Nouvelles recettes de saison à découvrir | 🟡 |
| C4 | `audit_securite_hebdo` | Dim 2h | Vérification intégrité données + logs suspects | 🟡 |
| C5 | `nettoyage_notifications_anciennes` | Dim 4h | Purger notifications > 90 jours | 🟢 |
| C6 | `mise_a_jour_scores_gamification` | Minuit | Recalculer scores/badges quotidiens | 🟡 |
| C7 | `alerte_meteo_jardin` | 7h | Alerte gel/canicule → protéger plantes | 🟡 |
| C8 | `resume_financier_semaine` | Ven 18h | Résumé dépenses de la semaine | 🟡 |

---

## 10. 📱 Notifications — WhatsApp, Email, Push

### Architecture actuelle

```
DispatcherNotifications (central)
├── ntfy.sh        → REST API → push notifications
├── Web Push       → VAPID protocol → navigateur
├── Email          → Resend API → Jinja2 templates
└── WhatsApp       → Meta Cloud API → webhook bidirectionnel
```

### État par canal

| Canal | État | Fonctionnalités | Manques |
|-------|------|-----------------|---------|
| **ntfy** | ✅ Opérationnel | Push simple, digest | — |
| **Web Push** | ✅ Opérationnel | Abonnement VAPID, notifications navigateur | Tests E2E push |
| **Email** | ✅ Opérationnel | 7 templates Jinja2 (reset pwd, vérif, digest, rapport, alerte, invitation, digest) | Template personnalisation |
| **WhatsApp** | ✅ Opérationnel | Webhook Meta, boutons interactifs (planning valider/modifier/régénérer) | Conversations enrichies |

### Améliorations notifications proposées

| # | Amélioration | Canal | Description | Effort |
|---|-------------|-------|-------------|--------|
| N1 | **WhatsApp : Flux courses** | WhatsApp | "Voici ta liste courses de la semaine" + bouton "Ajouter au panier" | M |
| N2 | **WhatsApp : Rappel activité Jules** | WhatsApp | "C'est l'heure de l'activité de Jules!" + suggestion | S |
| N3 | **WhatsApp : Résultats paris** | WhatsApp | "Match terminé : Paris SG 2-1 → Tu as gagné !" | S |
| N4 | **WhatsApp : Mode conversationnel** | WhatsApp | État machine plus riche — gestion multi-étapes | L |
| N5 | **Email : Newsletter hebdo** | Email | Template riche avec images, graphiques inline, call-to-action | M |
| N6 | **Email : Rapport budget PDF** | Email | PDF en pièce jointe (déjà généré, ajouter l'envoi) | S |
| N7 | **Push : Actions rapides** | Push | Notifications avec boutons d'action (ex: "Valider" / "Reporter") | M |
| N8 | **Push : Géolocalisation** | Push | Rappel courses quand proche d'un supermarché | L |
| N9 | **Préférences granulaires** | Tous | UI pour choisir par type d'événement quel canal utiliser | M |
| N10 | **Historique notifications** | Tous | Page "Centre de notifications" dans l'app | M |

### Mapping événements → canaux (existant + proposé)

| Événement | ntfy | Push | Email | WhatsApp | État |
|-----------|------|------|-------|----------|------|
| Péremption J-2 | ✅ | ✅ | — | — | Implémenté |
| Rappel courses | ✅ | ✅ | — | ✅ | Implémenté |
| Résumé hebdo | — | — | ✅ | ✅ | Implémenté |
| Échec cron job | ✅ | ✅ | ✅ | ✅ | Implémenté |
| Document expirant | ✅ | ✅ | ✅ | — | Implémenté |
| Rappel vaccin | — | ✅ | ✅ | — | Implémenté |
| **Liste courses semaine** | — | ✅ | — | ✅ | **À ajouter** |
| **Résultats paris** | ✅ | ✅ | — | ✅ | **À ajouter** |
| **Budget dépassé** | ✅ | ✅ | ✅ | ✅ | **À ajouter** |
| **Activité Jules** | — | ✅ | — | ✅ | **À ajouter** |
| **Alerte météo jardin** | ✅ | ✅ | — | — | **À ajouter** |
| **Contrat à renouveler** | — | ✅ | ✅ | — | **À ajouter** |

---

## 11. 🔧 Mode Admin manuel

### Fonctionnalités existantes

Le mode admin est complet avec :

| Feature | Endpoint | État |
|---------|----------|------|
| **Liste jobs** | `GET /api/v1/admin/jobs` | ✅ |
| **Trigger manuel** | `POST /api/v1/admin/jobs/{id}/run` | ✅ (rate limit 5/min) |
| **Dry run** | `POST /api/v1/admin/jobs/{id}/run?dry_run=true` | ✅ |
| **Logs jobs** | `GET /api/v1/admin/jobs/{id}/logs` | ✅ |
| **Audit logs** | `GET /api/v1/admin/audit-logs` | ✅ |
| **Stats audit** | `GET /api/v1/admin/audit-stats` | ✅ |
| **Export audit CSV** | `GET /api/v1/admin/audit-export` | ✅ |
| **Health check services** | `GET /api/v1/admin/services/health` | ✅ |
| **Test notifications** | `POST /api/v1/admin/notifications/test` | ✅ |
| **Stats cache** | `GET /api/v1/admin/cache/stats` | ✅ |
| **Purge cache** | `POST /api/v1/admin/cache/clear` | ✅ |
| **Liste users** | `GET /api/v1/admin/users` | ✅ |
| **Désactiver user** | `POST /api/v1/admin/users/{id}/disable` | ✅ |
| **Cohérence DB** | `GET /api/v1/admin/db/coherence` | ✅ |
| **Feature flags** | `GET/PUT /api/v1/admin/feature-flags` | ✅ |
| **Runtime config** | `GET/PUT /api/v1/admin/config` | ✅ |
| **Flow simulator** | `POST /api/v1/admin/simulate-flow` | ✅ |

### Améliorations mode admin proposées

| # | Amélioration | Description | Effort | Priorité |
|---|-------------|-------------|--------|----------|
| A1 | **Dashboard admin dédié** | Page admin avec graphiques : jobs exécutés, erreurs, usage IA, notifications | M | 🔴 |
| A2 | **Console IA admin** | Tester un prompt IA directement depuis l'admin → voir la réponse brute | S | 🟡 |
| A3 | **Seed data one-click** | Bouton pour peupler la DB avec données de test (dev only) | S | 🟡 |
| A4 | **Reset module** | Bouton pour vider les données d'un module spécifique (dev only) | S | 🟡 |
| A5 | **Export DB complet** | Export JSON/SQL complet de toutes les données utilisateur | M | 🟡 |
| A6 | **Import DB** | Import JSON/SQL pour restaurer un backup | M | 🟡 |
| A7 | **Monitoring temps réel** | WebSocket admin → métriques live (requêtes/s, erreurs, cache hits) | L | 🟢 |
| A8 | **Queue de notifications** | Voir et gérer la file d'attente des notifications pendantes | S | 🟡 |
| A9 | **Historique jobs paginated** | Vue paginée de tous les runs de jobs avec filtres | M | 🟡 |
| A10 | **Toggle maintenance mode** | Activer un mode maintenance qui affiche un bandeau utilisateur | S | 🟡 |

### Principe : Invisible pour l'utilisateur

L'admin est accessible via :
- `Depends(require_role("admin"))` côté API (protégé)
- Conditionnel dans la sidebar frontend (si `user.role === 'admin'`)
- Feature flag `admin.mode_test` pour activer des fonctions debug

**Amélioration proposée** : Ajouter un **panneau admin flottant** (overlay) activable par raccourci clavier (ex: `Ctrl+Shift+A`) qui n'apparaît **jamais** pour les utilisateurs normaux. Ce panneau afficherait :
- Boutons trigger jobs rapides
- Toggle feature flags
- Indicateur santé services
- Compteur quotas IA restants

---

## 12. 👤 Simplification du flux utilisateur

### Principes UX à appliquer

```
1. Maximum 3 clics pour toute action courante
2. Zéro configuration requise au premier lancement
3. L'IA fait le travail, l'utilisateur valide
4. Notifications proactives plutôt que consultation
5. Interface adaptative (mobile-first, contexte-sensitive)
```

### Flux à simplifier (10 améliorations UX)

| # | Flux actuel | Problème | Flux proposé | Effort |
|---|-------------|----------|--------------|--------|
| U1 | **Planifier repas** : Aller dans Planning → Choisir jour → Chercher recette → Sélectionner | 4 clics minimum | **1 clic** : Bouton "Planifier ma semaine" → IA génère → Valider ou ajuster | S |
| U2 | **Ajouter aux courses** : Naviguer vers Courses → Créer liste → Ajouter articles un par un | Fastidieux | **Auto** : Depuis le planning validé → "Générer courses" → Liste pré-remplie | S |
| U3 | **Consulter dépenses** : Aller dans Famille → Budget → Filtrer mois → Lire | Dispersé | **Dashboard** : Widget budget sur la page d'accueil avec tendance | S |
| U4 | **Trouver une recette** : Cuisine → Recettes → Filtres → Parcourir | Long | **Recherche globale** : Taper dans la barre de recherche → résultats instantanés | M |
| U5 | **Créer un projet maison** : Maison → Projets → Nouveau → Remplir formulaire complet | Formulaire lourd | **Wizard 3 étapes** : Nom → Type/Budget → Tâches suggérées par IA | M |
| U6 | **Vérifier l'inventaire** : Cuisine → Inventaire → Parcourir tout | Pas intuitif | **Alertes proactives** : Notifications quand stock bas → action directe depuis la notif | S |
| U7 | **Suivre Jules** : Famille → Jules → Onglets multiples | Navigation complexe | **Timeline Jules** : Vue chronologique unique avec jalons + activités + santé | M |
| U8 | **Gérer l'entretien** : Maison → Entretien → Voir tâches → Marquer fait | Pas engageant | **Checklist du jour** : Widget dashboard "Tâches du jour" avec swipe pour valider | S |
| U9 | **Consulter la météo** : Outils → Météo → Page dédiée | Détour | **Widget intégré** : Météo dans le header ou dashboard, adapte les suggestions | S |
| U10 | **Paramétrer notifications** : Paramètres → Section notifications → Toggle par type | Granularité floue | **Préférences par module** : Dans chaque module, option "Me notifier pour..." | M |

### Composants UX à ajouter

| # | Composant | Description | Impact |
|---|-----------|-------------|--------|
| UX1 | **Quick Actions FAB** | Bouton flottant avec actions rapides contextuelles (déjà existant, enrichir) | Navigation rapide |
| UX2 | **Command Palette** | `Cmd+K` pour naviguer/agir partout (déjà existant `menu-commandes.tsx`) | Power users |
| UX3 | **Onboarding tour** | Tour guidé au premier lancement (déjà existant `tour-onboarding.tsx`) | Découvrabilité |
| UX4 | **Empty states riches** | Quand un module est vide → message + CTA pour commencer | Engagement |
| UX5 | **Skeleton screens** | Loading skeletons sur toutes les pages (manquant sur certaines) | UX perçue |
| UX6 | **Swipe gestures mobile** | Swipe gauche/droite sur les items de liste (déjà existant, généraliser) | Mobile fluide |
| UX7 | **Cards drag & drop** | Réorganisation des widgets dashboard par glisser-déposer (existant via `grille-widgets.tsx`) | Personnalisation |
| UX8 | **Confirmations inline** | Toasts de confirmation au lieu de modals pour les actions simples | Moins intrusif |

---

## 13. 📁 Organisation du code

### Backend — État actuel

```
src/
├── api/                        ✅ Bien structuré
│   ├── routes/ (38 fichiers)   ⚠️ Certains très gros (>500 lignes)
│   ├── schemas/ (24 fichiers)  ✅ Bien organisé
│   ├── utils/                  ✅ 
│   ├── rate_limiting/          ✅
│   ├── dependencies.py         ✅
│   ├── auth.py                 ✅
│   └── main.py                 ✅
├── core/                       ✅ Excellent
│   ├── ai/ (5 fichiers)        ✅
│   ├── caching/ (4 fichiers)   ✅
│   ├── config/ (3 fichiers)    ✅
│   ├── db/ (4 fichiers)        ✅
│   ├── decorators/ (5 fichiers)✅
│   ├── models/ (31 fichiers)   ✅
│   ├── monitoring/             ✅
│   ├── resilience/             ✅
│   └── validation/             ✅
├── services/                   ✅ Bien modulaire
│   ├── core/ (base, events, cron, notifications) ✅
│   ├── cuisine/ (5+ fichiers)  ✅
│   ├── famille/ (6+ fichiers)  ✅
│   ├── maison/ (10+ fichiers)  ✅
│   ├── habitat/ (4 fichiers)   ✅
│   ├── jeux/ (5+ fichiers)     ✅
│   ├── inventaire/             ✅
│   ├── rapports/               ✅
│   ├── dashboard/              ✅
│   ├── utilitaires/            ✅
│   └── integrations/           ✅
```

### Points d'amélioration organisation

| # | Problème | Action | Effort |
|---|----------|--------|--------|
| O1 | **Routes volumineuses** — certains fichiers > 500 lignes | Découper en sous-modules (ex: `routes/maison/projets.py`, `routes/maison/entretien.py`) | M |
| O2 | **Imports circulaires potentiels** entre services | Auditer avec `importlib` ou `pylint` | S |
| O3 | **Schémas Pydantic** dupliqués entre `api/schemas/` et `core/validation/schemas/` | Unifier — `api/schemas/` pour la sérialisation API, `core/validation/` pour la validation business | M |
| O4 | **Tests dispersés** — structures différentes entre `tests/api/`, `tests/core/`, `tests/services/` | OK structurellement, mais nommer de façon cohérente | S |
| O5 | **Scripts utilitaires** — certains scripts archivés toujours présents | Déplacer `split_famille.py`, `split_maison.py` vers `scripts/archive/` | S |

### Frontend — État actuel

```
frontend/src/
├── app/(app)/               ✅ App Router bien structuré (103 pages)
├── app/(auth)/              ✅ Auth séparé
├── composants/
│   ├── ui/ (30 fichiers)    ✅ shadcn/ui complet
│   ├── disposition/ (18)    ✅ Layout riche
│   ├── cuisine/ (8)         ✅
│   ├── famille/ (9)         ✅
│   ├── jeux/ (13)           ✅
│   ├── maison/ (13)         ✅
│   ├── habitat/ (3)         ⚠️ Peu de composants pour un module riche
│   ├── planning/ (1)        ⚠️ Un seul composant
│   └── graphiques/ (3)      ✅
├── bibliotheque/api/ (25)   ✅ Clients API complets
├── crochets/ (13)           ✅ Hooks riches
├── magasins/ (4)            ✅ Stores Zustand
├── types/ (15)              ✅ TypeScript complet
└── fournisseurs/ (3)        ✅ Providers
```

### Points d'amélioration frontend

| # | Problème | Action | Effort |
|---|----------|--------|--------|
| O6 | **Composants habitat insuffisants** — 3 composants pour un module riche | Extraire des composants réutilisables depuis les pages | M |
| O7 | **Composants planning insuffisants** — 1 seul composant calendrier | Extraire timeline, week view, etc. | M |
| O8 | **Pages monolithiques** — certaines pages (paramètres) > 1200 lignes | Découper en composants nommés | M |
| O9 | **Tests unit frontend** — seulement ~5 fichiers | Plan de test : hooks, stores, composants critiques | L |
| O10 | **Pas de storybook** — composants UI non documentés visuellement | Optionnel mais recommandé pour la cohérence UI | L |

---

## 14. 💡 Axes d'innovation

### Innovations technologiques

| # | Innovation | Description | Impact | Effort |
|---|-----------|-------------|--------|--------|
| IN1 | **Mode famille multi-utilisateurs** | Chaque membre de la famille a son profil avec rôles (parent, enfant, invité) | 🔴 Transformant | XL |
| IN2 | **Synchronisation temps réel** | WebSocket sur tous les modules (pas juste courses) → édition collaborative | 🟡 Fort | L |
| IN3 | **Widget smartphone** | Widgets iOS/Android natifs (courses du jour, prochaine tâche, météo) via PWA | 🟡 Fort | L |
| IN4 | **Mode vocal complet** | "Hey Matanne, qu'est-ce qu'on mange ce soir ?" → réponse TTS | 🟢 Innovation | L |
| IN5 | **Scan & Go** | Scanner code-barres produit → ajouter auto à inventaire + infos nutrition | 🟡 Fort | M |
| IN6 | **Intégration IoT** | Capteurs maison (température, humidité, consommation) → dashboards | 🟢 Innovation | XL |
| IN7 | **Marketplace recettes** | Partager/importer des recettes depuis une communauté | 🟢 Innovation | L |
| IN8 | **Mode déconnecté enrichi** | IndexedDB + background sync → toutes les fonctions de base hors-ligne | 🟡 Fort | XL |

### Innovations UX

| # | Innovation | Description | Impact | Effort |
|---|-----------|-------------|--------|--------|
| IN9 | **Thèmes saisonniers** | L'interface s'adapte visuellement aux saisons (couleurs, illustrations) | 🟢 Fun | S |
| IN10 | **Gamification familiale** | Points/badges familiaux → classement famille ludique (en cours Phase 10) | 🟡 Fort | M |
| IN11 | **Mode focus** | Vue épurée "essentiel du jour" : 1 écran = météo + repas + tâches + rappels | 🔴 Transformant | M |
| IN12 | **Raccourcis Siri/Google Assistant** | Actions rapides via assistants vocaux natifs | 🟢 Innovation | M |
| IN13 | **QR code partage** | QR code sur l'écran pour partager une recette ou liste courses avec un invité | 🟢 Fun | S |
| IN14 | **Mode vacances** | Pause des notifications non essentielles + checklist voyage auto | 🟡 Fort | S |

### Innovations Data & IA

| # | Innovation | Description | Impact | Effort |
|---|-----------|-------------|--------|--------|
| IN15 | **Analytics familiales** | Tendances long terme : nutrition, dépenses, activités, énergie → graphiques | 🔴 Transformant | L |
| IN16 | **Prédictions ML** | Modèles prédictifs : courses de la semaine, dépenses du mois, pannes probables | 🟡 Fort | XL |
| IN17 | **Benchmark famille** | Comparer (anonymement) ses habitudes avec des moyennes nationales | 🟢 Innovation | L |
| IN18 | **Export Notion/Obsidian** | Exporter les données famille vers des outils tiers (journal, budget) | 🟢 Innovation | M |
| IN19 | **Intégration bancaire** | Sync avec banque via API (Plaid/Bridge) → dépenses auto-catégorisées | 🔴 Transformant | XL |
| IN20 | **Agent IA proactif** | L'IA suggère des actions avant que l'utilisateur ne demande (ex: "Il fait beau, promenez-vous au parc !") | 🟡 Fort | M |

---

## 15. 📋 Plan d'action priorisé

### Sprint A — Corrections critiques (bugs + qualité)

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | Corriger tous les `except: pass` (5 fichiers) | B1-B4 | S |
| 2 | Ajouter rate limiting endpoints admin | B6 | S |
| 3 | Rate limiting IA per-user | B7 | M |
| 4 | CORS strict en production | B8 | S |
| 5 | Skeletons/loading sur toutes les pages | B11, G24 | M |
| 6 | Vérifier nettoyage WebSocket hooks | B12 | S |
| 7 | Documenter auth WebSocket | B15 | S |

### Sprint B — Tests manquants

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | Tests dashboard route | T-Route | M |
| 2 | Tests famille_jules, famille_budget routes | T-Route | M |
| 3 | Tests maison_projets, maison_entretien routes | T-Route | M |
| 4 | Tests partage route | T-Route | S |
| 5 | Tests unit frontend (hooks, stores) | O9 | L |
| 6 | Schema coherence en CI | S3 | S |

### Sprint C — Pages IA Avancée

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | Finaliser les 12 pages IA avancée | G11-G22 | L |
| 2 | Ajouter les 10 fonctions client manquantes | G25 | M |
| 3 | Créer le guide module IA Avancée | D1 | M |
| 4 | Error boundaries sur toutes les pages | G23 | M |

### Sprint D — Inter-modules & Event Bus

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | Récolte jardin → Recettes saison | I1 | M |
| 2 | Anomalie énergie → Tâche entretien | I3 | S |
| 3 | Budget dépassement → Alerte dashboard | I4 | S |
| 4 | Inventaire → Courses prédictives | I9 | L |
| 5 | Retour recette → Ajuster planning futur | I13 | M |
| 6 | Contrats → Alertes renouvellement | I14 | S |
| 7 | Enrichir abonnés EventBus (pas juste cache) | Event Bus | M |

### Sprint E — Notifications enrichies

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | WhatsApp flux courses | N1 | M |
| 2 | WhatsApp rappel Jules | N2 | S |
| 3 | WhatsApp résultats paris | N3 | S |
| 4 | Préférences notifications granulaires | N9 | M |
| 5 | Centre de notifications dans l'app | N10 | M |
| 6 | Nouveaux jobs CRON (C1-C8) | C1-C8 | L |

### Sprint F — Admin & DX

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | Dashboard admin avec métriques | A1 | M |
| 2 | Console IA admin | A2 | S |
| 3 | Seed data one-click | A3 | S |
| 4 | Panneau admin flottant (Ctrl+Shift+A) | Admin | M |
| 5 | Toggle mode maintenance | A10 | S |

### Sprint G — UX & Simplification flux

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | Bouton "Planifier ma semaine" one-click | U1 | S |
| 2 | Génération courses auto depuis planning | U2 | S |
| 3 | Widget budget dashboard | U3 | S |
| 4 | Wizard création projet maison | U5 | M |
| 5 | Checklist du jour (widget dashboard) | U8 | S |
| 6 | Mode focus "essentiel du jour" | IN11 | M |
| 7 | Mode vacances | IN14 | S |

### Sprint H — Consolidation SQL & Organisation

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | Découper INIT_COMPLET.sql en fichiers thématiques | S1 | M |
| 2 | Script de régénération INIT_COMPLET | S1 | S |
| 3 | Compléter ORM pour tables orphelines | S2 | S |
| 4 | Déplacer scripts archivés | O5 | S |
| 5 | Documentation manquante (D1-D8) | D1-D8 | L |

### Sprint I — Innovations long terme

| # | Tâche | Réf | Effort |
|---|-------|-----|--------|
| 1 | Mode famille multi-utilisateurs | IN1 | XL |
| 2 | Analytics familiales long terme | IN15 | L |
| 3 | Agent IA proactif | IN20 | M |
| 4 | QR code partage | IN13 | S |
| 5 | Thèmes saisonniers | IN9 | S |

---

## 📎 Annexes

### A. Inventaire complet des fichiers

| Dossier | Fichiers Python | Fichiers TS/TSX | Total |
|---------|----------------|-----------------|-------|
| `src/api/` | ~45 | — | 45 |
| `src/core/` | ~55 | — | 55 |
| `src/services/` | ~80 | — | 80 |
| `tests/` | ~70 | — | 70 |
| `frontend/src/` | — | ~180 | 180 |
| **Total** | **~250** | **~180** | **~430** |

### B. Dépendances clés

**Backend** : FastAPI, SQLAlchemy 2.0, Pydantic v2, Mistral AI, APScheduler, httpx, WeasyPrint, Pillow

**Frontend** : Next.js 16, React 19, TanStack Query 5, Zustand 5, Zod 4, Tailwind CSS 4, Chart.js, Three.js, Recharts, Axios, Playwright

### C. Infrastructure

| Service | Rôle | Provider |
|---------|------|----------|
| Backend API | FastAPI (Python) | Railway |
| Frontend | Next.js (SSR) | Vercel |
| Database | PostgreSQL 16 | Supabase |
| Auth | JWT + Supabase Auth | Supabase |
| IA | Mistral AI API | Mistral |
| Notifications | ntfy, Resend, Meta | Multi |
| Monitoring | Sentry, Prometheus | Multi |
| CI/CD | GitHub Actions | GitHub |

### D. Variables d'environnement clés

```env
# Base
DATABASE_URL=postgresql://...
ENVIRONMENT=development|staging|production
SECRET_KEY=...

# IA
MISTRAL_API_KEY=...
AI_RATE_LIMIT_DAILY=1000
AI_RATE_LIMIT_HOURLY=100

# Auth
SUPABASE_URL=...
SUPABASE_KEY=...
JWT_SECRET=...

# Notifications
RESEND_API_KEY=...
NTFY_TOPIC=...
VAPID_PUBLIC_KEY=...
VAPID_PRIVATE_KEY=...
WHATSAPP_TOKEN=...
WHATSAPP_VERIFY_TOKEN=...

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SENTRY_DSN=...
```

---

> **Ce document est la source de vérité pour l'état du projet au 30 mars 2026.**  
> Chaque sprint d'implémentation doit mettre à jour ce document après complétion.
