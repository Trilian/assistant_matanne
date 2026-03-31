# Analyse Complète — Assistant Matanne

> **Date**: 31 mars 2026
> **Scope**: Audit intégral backend + frontend + DB + tests + docs + opportunités
> **Objectif**: Détecter bugs, gaps, manques, proposer interactions inter-modules, IA, jobs automatiques, notifications, mode admin manuel, et axes d'amélioration

---

## Table des matières

1. [Vue d'ensemble de l'application](#1-vue-densemble-de-lapplication)
2. [Inventaire complet des modules](#2-inventaire-complet-des-modules)
3. [Bugs & problèmes détectés](#3-bugs--problèmes-détectés)
4. [Features manquantes & gaps](#4-features-manquantes--gaps)
5. [SQL — Consolidation & cohérence](#5-sql--consolidation--cohérence)
6. [Tests — Couverture & lacunes](#6-tests--couverture--lacunes)
7. [Documentation — Audit & manques](#7-documentation--audit--manques)
8. [Interactions intra-modules](#8-interactions-intra-modules)
9. [Interactions inter-modules — Existantes & nouvelles](#9-interactions-inter-modules--existantes--nouvelles)
10. [Opportunités IA supplémentaires](#10-opportunités-ia-supplémentaires)
11. [Jobs automatiques & CRON](#11-jobs-automatiques--cron)
12. [Notifications — WhatsApp, email, push](#12-notifications--whatsapp-email-push)
13. [Mode admin manuel (test)](#13-mode-admin-manuel-test)
14. [UX — Simplification du flux utilisateur](#14-ux--simplification-du-flux-utilisateur)
15. [Organisation du code — Refactoring nécessaire](#15-organisation-du-code--refactoring-nécessaire)
16. [Axes d'innovation & amélioration](#16-axes-dinnovation--amélioration)
17. [Plan d'action priorisé](#17-plan-daction-priorisé)

---

## 1. Vue d'ensemble de l'application

### Stack technique

| Couche | Technologie | Version |
|--------|------------|---------|
| Backend | FastAPI + SQLAlchemy 2.0 + Pydantic v2 | Python 3.13+ |
| Frontend | Next.js (App Router) + TypeScript + Tailwind v4 | Next.js 16.2.1 |
| Base de données | Supabase PostgreSQL | ~130 tables |
| IA | Mistral AI (client unifié) | SDK intégré |
| State management | Zustand 5 + TanStack Query v5 | — |
| Notifications | ntfy.sh + Web Push + Email (Resend) + WhatsApp (Meta API) | 4 canaux |
| Tests | pytest (89 fichiers) + Vitest + Playwright (16 specs E2E) | — |

### Métriques du codebase

| Métrique | Valeur |
|----------|--------|
| Routes API | 200+ endpoints sur 42 fichiers routes |
| Modèles SQLAlchemy | 130+ classes sur 31 fichiers |
| Services | 161+ factory functions sur ~150 fichiers |
| Pages frontend | 90+ pages (app router) |
| Composants UI | 29 shadcn/ui + 60+ composants domaine |
| API clients frontend | 28 fichiers client |
| Hooks React | 14 hooks custom |
| Tests backend | 89 fichiers Python |
| Tests E2E | 16 specs Playwright |
| Tests frontend unitaires | **0** (lacune majeure) |
| SQL tables | ~130 tables + RLS + triggers + vues |
| Docs | 28 fichiers markdown |
| Inter-module bridges | 12 services |
| CRON jobs | 13 jobs planifiés |
| Event types bus | 21 types, 40+ subscribers |

---

## 2. Inventaire complet des modules

### 2.1 Modules fonctionnels

| Module | Backend routes | Pages frontend | Services | Modèles | Tests API |
|--------|---------------|----------------|----------|---------|-----------|
| **Cuisine** | recettes, courses, planning, inventaire, batch-cooking, anti-gaspillage, suggestions | 17 pages | 30+ | 23 tables | 8 fichiers |
| **Famille** | famille, jules, activités, budget, achats, routines, anniversaires, événements | 17 pages | 42+ | 35 tables | 7 fichiers |
| **Maison** | maison, projets, entretien, jardin, finances, stocks | 15 pages | 37+ | 40 tables | 6 fichiers |
| **Habitat** | habitat (veille immo, scénarios, plans, déco, jardin) | 6 pages | 5 | 10+ tables | 1 fichier |
| **Jeux** | jeux, paris, loto, euromillions, dashboard | 7 pages | 14+ | 13 tables | 2 fichiers |
| **Planning** | planning central, timeline | 2 pages | 3 | via cuisine | 1 fichier |
| **Outils** | chat-IA, notes, journal, contacts, énergie, météo, convertisseur, minuteur, automations | 11 pages | 11+ | via utilitaires | 2 fichiers |
| **IA Avancée** | suggestions proactives, prévisions, diagnostics, voyage, cadeaux, estimation travaux | 16 pages | 1 orchestrateur | — | 2 fichiers |
| **Admin** | audit, jobs, services, cache, users, DB | 6 pages | via core | système | 2 fichiers |
| **Paramètres** | préférences, notifications, sauvegardes, intégrations | 4 pages | 5+ | préférences | 2 fichiers |
| **Dashboard** | tableau de bord, scores, badges, anomalies | 1 page principale | 6 | gamification | 1 fichier |

### 2.2 Modules d'infrastructure

| Module | Fichiers | Rôle |
|--------|----------|------|
| Auth & JWT | auth.py, dependencies.py | Authentification Supabase + API JWT |
| Rate Limiting | rate_limiting/ | 60 req/min standard, 10 req/min IA |
| Cache | caching/ (L1 mémoire, L2 session, L3 fichier, Redis) | Cache multi-niveaux unifié |
| Résilience | resilience/ | Retry + Timeout + CircuitBreaker + Bulkhead |
| Monitoring | monitoring/ + Sentry + Prometheus | Métriques, health checks, tracing |
| Event Bus | events/ | Pub/sub avec wildcards, 21 types d'événements |
| WebSocket | 5 connexions WS | Courses, planning, notes, projets Kanban, admin logs |
| CRON | cron/ | 13 jobs APScheduler |

---

## 3. Bugs & problèmes détectés

### 3.1 Critiques 🔴

| # | Fichier | Problème | Impact |
|---|---------|----------|--------|
| B1 | `src/api/dependencies.py:65` | **Secret dev hardcodé** : `"dev-secret-key-change-in-production"` utilisé pour la détection d'environnement dev. Si `API_SECRET_KEY` n'est pas défini et que l'env n'est pas dans la whitelist, ce secret est comparé. Risque de contournement d'auth en prod si `API_SECRET_KEY` = cette valeur. | Sécurité |
| B2 | `src/services/core/base/ai_streaming.py` | **6 `print()` dans du code de streaming** au lieu de `logger`. En production les prints stdout polluent les logs structurés et ne sont pas captés par Sentry/monitoring. | Observabilité |
| B3 | `src/core/ai/streaming.py:62` et `src/core/ai/router.py:26` | Même problème — `print(chunk)` au lieu de logger dans le pipeline IA. | Observabilité |

### 3.2 Moyens 🟡

| # | Fichier | Problème | Impact |
|---|---------|----------|--------|
| B4 | `src/services/cuisine/recettes/recettes_ia_versions.py:38` | **Classe stub** avec `pass` — service de versions IA de recettes non implémenté. | Feature incomplète |
| B5 | `src/services/cuisine/recettes/recherche_mixin.py:20` | **Mixin stub** avec `pass` — recherche avancée recettes non implémentée. | Feature incomplète |
| B6 | `src/services/cuisine/recettes/recettes_ia_suggestions.py:24` | **Classe stub** avec `pass` — suggestions IA recettes non implémentée. | Feature incomplète |
| B7 | `src/services/famille/calendrier/google_auth.py:21` | **Stub Google Auth** — intégration Google Calendar non implémentée. | Feature incomplète |
| B8 | `src/services/famille/calendrier/google_calendar.py:34` | **Stub Google Calendar** — sync non implémentée. | Feature incomplète |
| B9 | `src/services/jeux/_internal/notification_service.py:407-421` | **3 classes stub** avec `pass` — notifications jeux partiellement implémentées. | Feature incomplète |
| B10 | `src/services/jeux/_internal/football_compat.py:295` | **Classe stub** compat football — données non connectées. | Feature incomplète |
| B11 | `src/services/core/base/ai_mixins.py:10` | **Mixin IA vide** avec `...` — base mixin pas implémentée. | Code mort |
| B12 | `src/services/core/base/ai_streaming.py:9` | **Streaming mixin vide** avec `...` — base non implémentée. | Code mort |
| B13 | `src/services/cuisine/batch_cooking/congelation.py:259` | Commentaire `# PERSISTENCE SESSION_STATE (en attendant table SQL)` — données de congélation pas persistées en DB. | Perte de données |
| B14 | `src/services/core/utilisateur/auth_token.py:45` | Commentaire `# Temporaire` sur un hack de stockage de token. | Dette technique |

### 3.3 Faibles 🟢

| # | Fichier | Problème |
|---|---------|----------|
| B15 | Frontend — 12+ occurrences de `as unknown as` | Contrats API/types mal alignés entre backend et frontend |
| B16 | `frontend/src/app/(app)/parametres/preferences-notifications/page.tsx:167` | `as any` dans un `register()` react-hook-form |
| B17 | `frontend/src/app/(app)/famille/activites/page.tsx:194` | `eslint-disable-next-line react-hooks/exhaustive-deps` — dépendance manquante |
| B18 | 5 occurrences de `console.error()` dans le frontend | Acceptable pour le debugging mais devrait utiliser un logger structuré |
| B19 | `src/services/core/utilisateur/historique.py` | Stubs rétrocompatibles marqués "UI supprimée" — code mort à nettoyer |

---

## 4. Features manquantes & gaps

### 4.1 Backend — Services stubs à implémenter

| # | Service | Fichier | Description |
|---|---------|---------|-------------|
| G1 | Recherche avancée recettes | `recettes/recherche_mixin.py` | Recherche full-text avec filtres (temps, difficulté, ingrédients, saison) |
| G2 | Suggestions IA recettes | `recettes/recettes_ia_suggestions.py` | Suggestions personnalisées basées sur historique et préférences |
| G3 | Versions IA recettes | `recettes/recettes_ia_versions.py` | 3 versions existantes (bébé, batch cooking, robot) **commentées dans service.py:305-306** — à activer. + 3 nouvelles : version saisonnière (produits de saison), version rapide (< 30 min), version restes (inventaire) |
| G4 | Google Calendar sync | `famille/calendrier/google_*.py` | Sync bidirectionnelle avec Google Calendar |
| G5 | Notifications jeux complètes | `jeux/_internal/notification_service.py` | 3 classes stub — alertes résultats, rappels tirages |
| G6 | Football data compat | `jeux/_internal/football_compat.py` | Intégration données football temps réel |
| G7 | Congélation persistée | `batch_cooking/congelation.py` | Table SQL pour suivi stocks congelés |

### 4.2 Frontend — Pages sans API client complet

| # | Page | Gap |
|---|------|-----|
| G8 | `/outils/minuteur` | Pas de persistance côté serveur (localStorage uniquement) |
| G9 | `/outils/convertisseur` | Fonctionnalité purement client-side, pas d'historique |
| G10 | `/famille/gamification` | Page existe mais API gamification partiellement connectée |
| G11 | `/maison/visualisation` | Plan 3D (Three.js) — données de pièces/objets partiellement alimentées |
| G12 | `/ia-avancee/*` | 16 pages IA avancée — certaines n'ont que des appels POST sans historique |

### 4.3 Contrats types frontend ↔ backend

| # | Problème | Fichiers concernés |
|---|----------|--------------------|
| G13 | `famille.ts:481` — réponse checklist anniversaire mal typée | `api/famille.ts` + `schemas/famille.py` |
| G14 | `maison.ts:1036` — briefing maison mal typé | `api/maison.ts` + routes maison |
| G15 | `maison.ts:1345` — planning semaine mal typé | `api/maison.ts` |
| G16 | `jeux/page.tsx:182` — widgets dashboard non typés | `jeux/page.tsx` + `types/jeux.ts` |
| G17 | `parametres/onglet-notifications.tsx:104` — canaux notification mal typés | types notifications |

### 4.4 Données de référence manquantes

| # | Donnée | Fichier attendu | Utilisation |
|---|--------|-----------------|-------------|
| G19 | Table calories/portions par âge | `data/reference/portions_age.json` | Adapter portions recettes Jules |
| G20 | Catalogue produits ménagers | `data/reference/produits_menagers.json` | Auto-complétion inventaire maison |

---

## 5. SQL — Consolidation & cohérence

### 5.1 Organisation actuelle

```
sql/
├── INIT_COMPLET.sql          # Source de vérité (~10 000 lignes)
├── schema/                   # 17 fichiers ordonnés (01-99)
│   ├── 01_extensions.sql     # uuid-ossp, pgcrypto, json, hstore
│   ├── 02_functions.sql      # Helpers (audit_log, dates, JSON)
│   ├── 03_systeme.sql        # Users, prefs, logs, automations
│   ├── 04_cuisine.sql        # 23 tables cuisine
│   ├── 05_famille.sql        # 35 tables famille
│   ├── 06_maison.sql         # 40 tables maison
│   ├── 07_habitat.sql        # Habitat extension
│   ├── 08_jeux.sql           # 13 tables jeux
│   ├── 09_notifications.sql  # 12 tables notifications
│   ├── 10_finances.sql       # 6 tables finances
│   ├── 11_utilitaires.sql    # Calendriers, docs
│   ├── 12_triggers.sql       # Audit + updated_at
│   ├── 13_views.sql          # 8+ vues agrégées
│   ├── 14_indexes.sql        # Index de performance
│   ├── 15_rls_policies.sql   # Row-level security
│   ├── 16_seed_data.sql      # Données de référence
│   ├── 17_migrations_absorbees.sql  # V001-V002 absorbées
│   └── 99_footer.sql         # COMMIT + vérification
└── migrations/               # 5 migrations (V003-V007)
    ├── V003__sprint13_canaux_notifications.sql
    ├── V004__logs_securite_admin_only.sql
    ├── V005__phase2_sql_consolidation.sql
    ├── V006__phase7_jobs_automations.sql
    ├── V007__module_habitat.sql
    └── README.md
```

### 5.2 Constats

| # | Constat | Action recommandée |
|---|---------|-------------------|
| S1 | `INIT_COMPLET.sql` est le source de vérité et contient déjà les migrations V001-V007 absorbées | **OK** — stratégie correcte en dev |
| S2 | Les fichiers `sql/schema/` sont un découpage logique de `INIT_COMPLET.sql` | Vérifier que `INIT_COMPLET.sql` = concaténation exacte de `schema/01` à `schema/99` |
| S3 | `17_migrations_absorbees.sql` référence V001-V002 seulement | Absorber V003-V007 dans `INIT_COMPLET.sql` et les fichiers `schema/` correspondants |
| S4 | Table `batch_cooking_congelation` manquante | Le service `congelation.py` utilise du state mémoire au lieu de SQL |
| S5 | Pas de table `garmin_activities` / `garmin_daily_summaries` | Données Garmin pas persistées en DB (API directe) |
| S6 | Pas de table `ia_suggestions_historique` pour les 16 pages IA avancée | Les suggestions IA ne sont pas historisées en DB |
| S7 | Alembic présent (`alembic/`) mais inutilisé — migrations SQL-file uniquement | Supprimer `alembic/` ou documenter qu'il n'est pas utilisé |

### 5.3 Plan de consolidation SQL

```
Action : Regrouper TOUT dans sql/schema/ (fichiers modulaires ordonnés)
         Régénérer INIT_COMPLET.sql = concaténation automatique de schema/*.sql
         Absorber V003-V007 dans les fichiers schema/ correspondants
         Ajouter les tables manquantes (congelation, garmin, ia_historique)
         Supprimer sql/migrations/ (tout est dans schema/ + INIT_COMPLET.sql)
         Script de concaténation : scripts/db/build_init_complet.py
```

---

## 6. Tests — Couverture & lacunes

### 6.1 Backend — Bonne couverture

| Catégorie | Fichiers | Couverture |
|-----------|----------|------------|
| Routes API | 45 fichiers | ✅ Toutes les routes testées |
| Core AI | 4 fichiers (cache, client, parser, embeddings) | ✅ Très bon |
| Core models | 8 fichiers | ✅ Tous les imports + spécifiques |
| Core config/cache | 6 fichiers | ✅ Multi-niveaux, invalidation |
| Services cuisine | 4 fichiers | ✅ Enrichers, batch-cooking |
| Services budget | 4 fichiers (18 classes) | ✅ Excellent |
| Rate limiting | 1 fichier (21 classes) | ✅ Exhaustif |
| CRON jobs | 2 fichiers | ✅ Bon |
| Automations | 1 fichier | ✅ Engine testé |
| Gamification | 1 fichier (6 classes) | ✅ Badges, triggers |
| Benchmarks | 1 fichier | ✅ Perf core |
| Contract | 1 fichier (Schemathesis) | ✅ OpenAPI validation |

### 6.2 Backend — Lacunes identifiées

| # | Module non testé | Priorité | Justification |
|---|-----------------|----------|---------------|
| T1 | `src/core/date_utils/` (4 fichiers) | Moyenne | Logique de dates utilisée partout |
| T2 | `src/core/decorators/` (4 fichiers) | Haute | `@avec_cache`, `@avec_session_db`, `@avec_validation` — critiques |
| T3 | `src/core/observability/` | Basse | Contexte d'opération |
| T4 | `src/core/monitoring/` (3 fichiers) | Moyenne | Collecteur métriques, health |
| T5 | `src/core/resilience/policies.py` | Haute | Retry, timeout, circuit breaker — critique pour la prod |
| T6 | `src/services/famille/` (42 services) | Haute | Seulement testé via routes API, pas de tests unitaires services |
| T7 | `src/services/maison/` (37 services) | Haute | Idem |
| T8 | `src/services/habitat/` (5 services) | Moyenne | Module récent |
| T9 | `src/services/integrations/` (19 services) | Haute | Intégrations externes (Garmin, OCR, météo, barcode) — critique |
| T10 | `src/services/dashboard/` (6 services) | Moyenne | Agrégation données |
| T11 | `src/services/rapports/` (6 services) | Moyenne | Génération PDF |
| T12 | Inter-modules bridges (12 fichiers) | Haute | Logique métier critique entre modules |
| T13 | WhatsApp integration | Haute | Canal de notification primaire |
| T14 | Event bus subscribers | Haute | 40+ subscribers non testés unitairement |

### 6.3 Frontend — Lacune majeure 🔴

| # | Problème | Impact |
|---|---------|--------|
| T15 | **0 tests unitaires frontend** (`frontend/src/**/*.test.{ts,tsx}` → 0 fichiers trouvés) | Les 90+ pages et 60+ composants ne sont pas testés unitairement |
| T16 | Vitest configuré avec seuil 50% mais aucun test n'existe | Le seuil est fictif |
| T17 | **Seuls les tests E2E Playwright** (16 specs) couvrent le frontend | Les tests E2E ne remplacent pas les tests unitaires pour la logique des composants |

### 6.4 Plan de couverture tests

```
Priorité 1 (critique):
  - Tests unitaires des décorateurs core (@avec_cache, @avec_session_db, @avec_validation)
  - Tests unitaires resilience (RetryPolicy, CircuitBreaker, Bulkhead)
  - Tests unitaires des 12 inter-module bridges
  - Tests unitaires event bus subscribers
  - Tests frontend composants critiques (formulaire-recette, barre-laterale, recherche-globale)

Priorité 2 (importante):
  - Tests services famille (42 services)
  - Tests services maison (37 services)
  - Tests intégrations (WhatsApp, Garmin, OCR, météo)
  - Tests frontend hooks (utiliser-auth, utiliser-api, utiliser-crud)
  - Tests frontend API clients (recettes.ts, courses.ts, planning.ts)

Priorité 3 (souhaitable):
  - Tests date_utils
  - Tests monitoring/observability
  - Tests dashboard/rapports services
  - Tests frontend pages (dashboard, cuisine hub, famille hub)
```

---

## 7. Documentation — Audit & manques

### 7.1 Docs existantes (28 fichiers)

| Fichier | Contenu | État |
|---------|---------|------|
| `docs/INDEX.md` | Index central de navigation | ✅ À jour |
| `docs/ARCHITECTURE.md` | Architecture technique générale | ✅ |
| `docs/API_REFERENCE.md` | Référence endpoints API | ⚠️ Vérifier exhaustivité (200+ endpoints) |
| `docs/MODULES.md` | Description des modules métier | ⚠️ Modules récents (habitat, innovations) manquants ? |
| `docs/INTER_MODULES.md` | Interactions inter-modules | ⚠️ Nouveaux bridges à documenter |
| `docs/NOTIFICATIONS.md` | Système de notifications 4 canaux | ✅ |
| `docs/CRON_JOBS.md` | Jobs planifiés | ⚠️ Vérifier les 13 jobs vs docs |
| `docs/AUTOMATIONS.md` | Moteur d'automations | ✅ |
| `docs/AI_SERVICES.md` | Services IA (Mistral, cache, rate limit) | ✅ |
| `docs/ADMIN_GUIDE.md` | Guide administrateur | ✅ |
| `docs/ADMIN_RUNBOOK.md` | Procédures opérationnelles | ✅ |
| `docs/DEPLOYMENT.md` | Déploiement (Docker, Vercel, Railway) | ✅ |
| `docs/DEVELOPER_SETUP.md` | Setup environnement dev | ✅ |
| `docs/FRONTEND_ARCHITECTURE.md` | Architecture frontend | ⚠️ Vérifier avec Next.js 16 |
| `docs/DESIGN_SYSTEM.md` | Design system (composants, couleurs) | ✅ |
| `docs/UI_COMPONENTS.md` | Inventaire composants UI | ⚠️ 29+ shadcn + 60+ custom |
| `docs/PATTERNS.md` | Patterns de code | ✅ |
| `docs/SERVICES_REFERENCE.md` | Référence services | ⚠️ 161 factories vs docs |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | Guide sessions DB | ✅ |
| `docs/ERD_SCHEMA.md` | Schéma entité-relation | ⚠️ 130 tables vs schéma |
| `docs/TESTING_ADVANCED.md` | Stratégie de tests avancée | ✅ |
| `docs/HABITAT_MODULE.md` | Module habitat | ✅ |
| `docs/GAMIFICATION.md` | Système gamification | ✅ |
| `docs/GOOGLE_ASSISTANT_SETUP.md` | Setup Google Assistant | ✅ |
| `docs/WHATSAPP_SETUP.md` | Setup WhatsApp | ✅ |
| `docs/REDIS_SETUP.md` | Setup Redis | ✅ |
| `docs/MIGRATION_GUIDE.md` | Guide migrations | ⚠️ Stratégie SQL-file |
| `docs/TROUBLESHOOTING.md` | Dépannage | ✅ |

### 7.2 Documentation manquante

| # | Doc manquante | Contenu attendu |
|---|--------------|-----------------|
| D1 | `docs/CHANGELOG_MODULES.md` | Historique des changements par module (pas juste par sprint) |
| D2 | `docs/EVENT_BUS.md` | Catalogue complet des 21 types d'événements + 40 subscribers + exemples |
| D3 | `docs/SECURITY.md` | Politique de sécurité (auth, CORS, rate limiting, RLS, secrets management, OWASP) |
| D4 | `docs/DATA_MODEL.md` | Modèle de données détaillé avec relations (les 130 tables + FK + contraintes) |
| D5 | `docs/WHATSAPP_COMMANDS.md` | Commandes WhatsApp conversationnelles + machine d'états |
| D6 | `docs/MONITORING.md` | Métriques Prometheus, Sentry, health checks, alerting |
| D7 | `docs/guides/RECIPE_FLOW.md` | Guide utilisateur : flux complet d'une recette (création → planification → courses → cuisson) |
| D8 | `docs/guides/FAMILY_FLOW.md` | Guide utilisateur : flux famille (Jules, activités, routines, budget) |
| D9 | `docs/API_SCHEMAS.md` | Documentation Pydantic schemas (auto-générée depuis le code) |
| D10 | `docs/PERFORMANCE.md` | Benchmarks, bonnes pratiques perf, résultats load tests |

---

## 8. Interactions intra-modules

### 8.1 Module Cuisine — Flux interne

```
Recettes ──→ Planning ──→ Courses ──→ Inventaire
   │             │            │            │
   │             ▼            ▼            ▼
   │      Batch Cooking   Checkout    Stock bas
   │             │            │         → alerte
   │             ▼            ▼
   │      Anti-gaspillage  Scan barcode
   │             │
   └─────→ Suggestions IA ←─── Photo frigo
```

**Interactions existantes** ✅ :
- Recettes → Planning (planifier une recette sur la semaine)
- Planning → Courses (générer liste de courses depuis planning)
- Courses → Inventaire (checkout = décrémenter stock)
- Inventaire → Anti-gaspillage (articles périmant → recettes rescue)
- Batch cooking → Inventaire (sync stocks congelés)
- Photo frigo → Suggestions recettes (IA vision)

**Interactions manquantes à ajouter** 🟡 :
- Inventaire → Planning : suggérer des recettes utilisant les stocks existants en priorité
- Anti-gaspillage → Courses : exclure les articles qu'on a déjà en surplus
- Batch cooking → Planning : bloquer les jours batch sur le planning de la semaine
- Nutrition → Planning : alerter si le planning de la semaine est déséquilibré nutritionnellement
- Feedback recette → Suggestions IA : si une recette a été notée < 3/5, ne plus la suggérer

### 8.2 Module Famille — Flux interne

```
Jules ──→ Activités ──→ Routines
  │          │             │
  │          ▼             ▼
  │    Suggestions IA   Complétion
  │                        │
  ├──→ Budget ──→ Analyse IA
  │
  ├──→ Anniversaires ──→ Checklists
  │
  ├──→ Calendriers ──→ Événements
  │
  └──→ Timeline / Journal
```

**Interactions manquantes** 🟡 :
- Jules croissance → Recettes portions : adapter automatiquement les portions des recettes planifiées
- Anniversaire J-14 → Budget prévisionnel : réserver automatiquement le budget estimé

### 8.3 Module Maison — Flux interne

```
Projets ──→ Tâches ──→ Artisans
   │           │          │
   │           ▼          ▼
   │     Entretien    Devis/Factures
   │           │
   │           ▼
   ├──→ Jardin ──→ Récolte
   │
   ├──→ Équipements ──→ Garanties ──→ SAV
   │
   ├──→ Charges ──→ Énergie ──→ Anomalies IA
   │
   └──→ Stocks/Provisions ──→ Cellier
```

**Interactions manquantes** 🟡 :
- Jardin saison → Entretien auto : tâches d'entretien saisonnières automatiques selon les plantes
- Charges augmentation → Diagnostic énergie : si facture +20%, déclencher analyse anomalie

---

## 9. Interactions inter-modules — Existantes & nouvelles

### 9.1 Bridges existants (12)

| Bridge | De → Vers | Fonction |
|--------|-----------|----------|
| `inter_module_courses_budget.py` | Courses → Budget | Total courses → dépense alimentation |
| `inter_module_energie_cuisine.py` | Énergie → Cuisine | Heures creuses → planifier cuisson longue |
| `inter_module_batch_inventaire.py` | Batch cooking → Inventaire | Sync batch → stock |
| `inter_module_peremption_recettes.py` | Péremption → Recettes | Alert + recettes rescue |
| `inter_module_planning_voyage.py` | Voyages → Planning | Adapter planning si voyage |
| `inter_module_voyages_budget.py` | Voyages → Budget | Dépenses voyage → budget famille |
| `inter_module_budget_jeux.py` | Budget × Jeux | Alerte dépassement seuil jeux |
| `inter_module_documents_notifications.py` | Documents → Notifications | Docs expirant → alerte ntfy |
| `inter_module_anniversaires_budget.py` | Anniversaires → Budget | Budget cadeaux/fête |
| `inter_module_diagnostics_ia.py` | Diagnostics → Actions | IA → créer tâche entretien |
| `inter_module_garmin_health.py` | Garmin → Santé | Sync activité + suggestions Jules |
| `inter_module_chat_contexte.py` | Multi → Chat IA | Contexte inventaire/planning/routines |

### 9.2 Nouvelles interactions inter-modules proposées

| # | Bridge proposé | De → Vers | Impact utilisateur |
|---|---------------|-----------|-------------------|
| I1 | `inter_module_jardin_recettes.py` | Jardin récolte → Recettes planning prochain | Quand une récolte est prête, la semaine suivante suggère des recettes utilisant ces légumes |
| I2 | `inter_module_meteo_activites.py` | Météo → Activités famille | Pluie prévue samedi → suggérer activités intérieur pour Jules ; Beau temps → activités extérieur |
| I3 | `inter_module_entretien_courses.py` | Entretien → Courses | Tâche entretien nécessite produit → ajouter automatiquement à la liste de courses |
| I4 | `inter_module_charges_energie.py` | Charges (facture) → Énergie (analyse) | Facture reçue avec hausse → déclencher analyse anomalie énergie automatiquement |
| I5 | `inter_module_weekend_courses.py` | Weekend activités → Courses | Activité prévue (randonnée, pique-nique) → ajouter fournitures à la liste de courses |
| I7 | `inter_module_jules_nutrition.py` | Jules croissance → Planning nutrition | Adapter les portions et nutriments selon la courbe de croissance |
| I10 | `inter_module_documents_calendrier.py` | Documents expirant → Calendrier | Créer événement calendrier pour renouvellement de documents |
| I11 | `inter_module_inventaire_planning.py` | Inventaire stock → Planning recettes | Prioriser les recettes utilisant les ingrédients en stock |
| I12 | `inter_module_saison_menu.py` | Produits de saison → Planning IA | Le planning IA favorise les produits de saison (meilleur prix + qualité) |

### 9.3 Matrice d'interactions (vue d'ensemble)

```
            Cuisine  Famille  Maison  Jeux  Planning  Outils  Dashboard
Cuisine       ■■■      ■□       ■□     ·      ■■■       ■□      ■■
Famille       ■□       ■■■      □□     ■□     ■□        ■□      ■■
Maison        ■□       □□       ■■■    ·      □□        □□      ■□
Jeux          ·        ■□       ·      ■■■    ·         ·       ■□
Planning      ■■■      ■□       □□     ·      ■■■       □□      ■■
Outils        ■□       ■□       □□     ·      □□        ■■■     □□
Dashboard     ■■       ■■       ■□     ■□     ■■        □□      ■■■

Légende: ■■■ Fort (bien connecté)  ■□ Partiel  □□ Faible  · Aucun
```

---

## 10. Opportunités IA supplémentaires

### 10.1 IA déjà implémentée

| Module | Fonctionnalité IA | Service |
|--------|-------------------|---------|
| Cuisine | Suggestions recettes (inventaire + préférences) | `BaseAIService` |
| Cuisine | Génération planning IA | `PlanningAIMixin` |
| Cuisine | Photo frigo → recettes | `VisionMixin` |
| Cuisine | Import recette depuis URL/PDF | `importer.py` |
| Cuisine | Enrichissement nutrition | `nutrition_enrichment.py` |
| Cuisine | Version recette pour Jules | `version_recette_jules.py` |
| Famille | Suggestions activités Jules | `JulesAIService` |
| Famille | Suggestions weekend | `WeekendAIService` |
| Famille | Suggestions soirée | `SoireeAIService` |
| Famille | Résumé hebdomadaire | `ResumeHebdoService` |
| Famille | Analyse budget IA | `BudgetAIService` |
| Famille | Suggestions achats enrichies | `AchatsIAService` |
| Famille | Annonce LBC/Vinted IA | Pré-remplissage annonce vente |
| Maison | Diagnostics IA artisans | `DiagnosticsIAArtisans` |
| Maison | Anomalies énergie IA | `EnergieAnomaliesIA` |
| Maison | Entretien IA | `EntretienIAService` |
| Habitat | Analyse plans IA | Plans d'architecte analyse |
| Habitat | Suggestions déco IA | Décoration intérieure |
| IA Avancée | Chat IA contextuel | `IAAvanceeService` |
| IA Avancée | Planning adaptatif | Ajustement auto planning |
| IA Avancée | Idées cadeaux | Suggestions personnalisées |
| IA Avancée | Planning voyage | Organisation voyage |
| IA Avancée | Estimation travaux | Devis automatique |
| IA Avancée | Adaptations météo | Ajustements plannings |
| IA Avancée | Diagnostic plante | Vision + catalogue |
| IA Avancée | Analyse document/photo | OCR + extraction |
| Outils | Briefing matinal | `BriefingMatinalService` |
| Outils | Assistant proactif | `AssistantProactifService` |

### 10.2 Nouvelles opportunités IA

| # | Opportunité | Module | Description | Valeur utilisateur |
|---|-------------|--------|-------------|-------------------|
| IA1 | **Détection patterns alimentaires** | Cuisine | Analyser l'historique des repas sur 3 mois → détecter manques nutritionnels, répétitions excessives, proposer de la diversité | Santé famille |
| IA3 | **Coach routines IA** | Famille | Analyser la complétion des routines → identifier les blocages, suggérer des ajustements d'horaires/fréquences | Productivité |
| IA4 | **Détection anomalies consommation eau/gaz/élec** | Maison | Comparer consommation mensuelle → alerter si anomalie détectée (fuite, appareil défaillant) | Économies |
| IA5 | **Optimisation courses par rayon** | Courses | Grouper les articles de la liste par rayon du supermarché → parcours optimal | Temps |
| IA6 | **Résumé mensuel IA** | Dashboard | Résumé narratif mensuel : recettes préférées, dépenses, activités Jules, projets maison | Vue d'ensemble |
| IA7 | **Analyse photos jardin** | Maison/Jardin | Photo de plante → diagnostic maladie, suggestion traitement, prévision récolte | Jardin |
| IA8 | **Planning activités Jules adaptatif** | Famille | En fonction de l'âge, de la météo, des activités passées → planning hebdo activités | Développement |
| IA11 | **Mode "Qu'est-ce qu'on mange ce soir ?"** | Cuisine | Bouton unique : analyse frigo + préférences + temps dispo + humeur → suggestion immédiate | UX |
| IA12 | **Comparateur prix fournisseurs énergie** | Maison | Analyser la consommation + tarif actuel → comparer avec les offres du marché | Économies |

---

## 11. Jobs automatiques & CRON

### 11.1 Jobs existants (13)

| Heure | Job | Module | Canal notification |
|-------|-----|--------|-------------------|
| 03:00 (1er du mois) | Enrichissement catalogues IA | Core | — |
| 06:00 (lundi) | Entretien saisonnier | Maison | Push + ntfy |
| 07:00 | Analyser péremptions matin | Cuisine | Push + ntfy |
| 07:00 | Rappels famille | Famille | Push + ntfy + WhatsApp |
| 07:30 | Digest WhatsApp matinal | Multi | WhatsApp |
| 08:00 | Rappels maison | Maison | Push + ntfy |
| 08:30 | Rappels généraux | Multi | Push + ntfy |
| 09:00 | Digest ntfy | Multi | ntfy.sh |
| 09:00 (lundi) | Vérifier stocks bas | Cuisine | Push + ntfy |
| 18:00 | Rappel courses | Courses | Push + ntfy + WhatsApp |
| 18:00 (dimanche) | Suggérer planning semaine | Planning | WhatsApp |
| 08:00 (1er du mois) | Rapport mensuel cuisine | Cuisine | Email |
| Horaire | Flush digest notifications | Core | Multi |

### 11.2 Jobs manquants proposés

| # | Job proposé | Horaire | Module | Canal | Description |
|---|------------|---------|--------|-------|-------------|
| J1 | **Recap weekend dimanche soir** | Dim 20:00 | Famille | WhatsApp + Push | Résumé des activités du weekend + preview semaine |
| J4 | **Nettoyage cache vieux de 7j** | Quotidien 02:00 | Core | — | Nettoyer les fichiers cache L3 expirés |
| J5 | **Backup données critiques** | Quotidien 01:00 | Core | — | Export JSON des données essentielles (recettes, planning, inventaire) |
| J6 | **Sync tirages loto/euromillions** | Mar+Ven 22:00 | Jeux | Push | Vérifier les résultats des tirages + notifier gains |
| J7 | **Rapport budget hebdo** | Dim 18:00 | Famille | WhatsApp | Résumé dépenses de la semaine + prévision fin de mois |
| J8 | **Mise à jour données météo** | Quotidien 06:00 | Outils | — | Rafraîchir prévisions météo pour la semaine (cache) |
| J9 | **Anniversaires rappel J-30** | Quotidien 08:00 | Famille | Push + WhatsApp | Rappel anniversaires dans 30 jours → préparation |
| J10 | **Analyse tendances mensuelles** | 1er du mois 09:00 | Dashboard | Email | Rapport IA tendances : alimentation, budget, activités Jules, énergie |
| J11 | **Purge logs anciens** | 1er du mois 03:00 | Admin | — | Supprimer logs et audit > 6 mois |

---

## 12. Notifications — WhatsApp, email, push

### 12.1 Architecture actuelle

```
DispatcherNotifications
  ├── NotifNtfy (ntfy.sh) ──── Alertes urgentes
  ├── NotifWebPush (VAPID) ─── Temps réel navigateur
  ├── NotifEmail (Resend) ──── Rapports, résumés
  └── NotifWhatsApp (Meta) ─── Digest matinal, partage planning
```

**Routing intelligent** :
- Smart failover : push → ntfy → WhatsApp → email
- Throttle : max 10 messages/heure par utilisateur
- Digest mode : messages non urgents consolidés en digest quotidien (09:00)

### 12.2 Mapping événements → canaux

| Événement | Push | ntfy | WhatsApp | Email |
|-----------|------|------|----------|-------|
| Péremption J-2 | ✅ | ✅ | · | · |
| Rappel courses | ✅ | ✅ | ✅ | · |
| Résumé hebdomadaire | · | · | ✅ | ✅ |
| Rapport budget mensuel | · | · | · | ✅ |
| Anniversaire J-7 | ✅ | ✅ | ✅ | · |
| Tâche entretien urgente | ✅ | ✅ | ✅ | · |
| Échec CRON job | ✅ | ✅ | ✅ | ✅ |
| Document expirant | ✅ | ✅ | · | ✅ |
| Badge débloqué | ✅ | ✅ | · | · |

### 12.3 Notifications manquantes proposées

| # | Notification | Déclencheur | Canaux | Priorité |
|---|-------------|-------------|--------|----------|
| N1 | **Recette du jour** | CRON 11:30 (si planning rempli) | Push | Basse |
| N2 | **Stock critique (0 restant)** | Inventaire checkout | Push + ntfy + WhatsApp | Haute |
| N4 | **Résultat tirage loto** | Job sync tirages (seulement si un pari/tirage est enregistré) | Push + WhatsApp | Haute |
| N6 | **Nouvelle recette de saison** | Changement de saison | Push | Basse |
| N7 | **Tâche jardin saisonnière** | CRON saisonnier | Push + ntfy | Moyenne |
| N9 | **Planning semaine vide** | Dimanche 10:00 | Push + WhatsApp | Moyenne |
| N10 | **Astuce anti-gaspillage** | 3+ articles proches péremption | Push | Basse |

### 12.4 Commandes WhatsApp conversationnelles proposées

| Commande | Réponse | État |
|----------|---------|------|
| "Menu" / "Planning" | Planning de la semaine actuelle | ✅ Existant |
| "Courses" | Liste de courses active + compte articles | À ajouter |
| "Recette [nom]" | Lien vers la recette + ingrédients | À ajouter |
| "Ce soir" | Suggestion rapide repas du soir | À ajouter |
| "Budget" | Résumé budget du mois en cours | À ajouter |
| "Jules" | Dernières activités + prochain jalon | À ajouter |
| "Frigo" | Scanner une photo du frigo → suggestions | À ajouter |
| "Aide" | Liste des commandes disponibles | À ajouter |

---

## 13. Mode admin manuel (test)

### 13.1 Capacités admin existantes

| Endpoint | Fonction | Mode dry_run |
|----------|----------|-------------|
| `POST /admin/jobs/{id}/run` | Lancer un job CRON manuellement | ✅ dry_run optionnel |
| `GET /admin/jobs` | Voir tous les jobs + état | — |
| `GET /admin/jobs/{id}/logs` | Voir les 20 dernières exécutions | — |
| `POST /admin/notifications/test` | Envoyer notification test (4 canaux) | — |
| `POST /admin/cache/clear` | Vider tout le cache | — |
| `GET /admin/cache/stats` | Stats cache (hit/miss) | — |
| `GET /admin/services/health` | Santé de tous les services | — |
| `POST /admin/services/{id}/action` | Action sur un service | — |
| `GET /admin/audit-logs` | Logs d'audit | — |
| `GET /admin/security-logs` | Logs de sécurité | — |
| `GET /admin/db/coherence` | Test cohérence DB | — |

### 13.2 Capacités admin manquantes

| # | Fonctionnalité admin | Description | Priorité |
|---|---------------------|-------------|----------|
| A1 | **Trigger event bus manuellement** | Émettre un événement domaine depuis l'admin panel → tester les subscribers | Haute |
| A2 | **Voir la file de notifications** | Afficher les notifications en attente de digest + forcer le flush | Haute |
| A3 | **Simuler un utilisateur** | Se connecter "en tant que" un utilisateur spécifique pour tester ses vues | Haute |
| A4 | **Exécuter une automation** | Déclencher une règle d'automation spécifique manuellement | Haute |
| A5 | **Envoyer un message WhatsApp test** | Envoyer un message WhatsApp spécifique à un numéro test | Moyenne |
| A6 | **Voir les métriques IA** | Dashboard : nombre d'appels IA, cache hits, tokens consommés, coût estimé | Haute |
| A7 | **Régénérer les données de seed** | Relancer l'insertion des données de référence | Basse |
| A8 | **Mode maintenance** | Activer un mode maintenance (503 pour les utilisateurs, admin accessible) | Moyenne |
| A9 | **Export DB snapshot** | Exporter un snapshot JSON de toutes les données (backup personnel) | Moyenne |
| A10 | **Dashboard temps réel** | WebSocket admin : voir les requêtes en cours, les jobs actifs, les events | Moyenne |
| A11 | **Panneau de feature flags** | Activer/désactiver des features par module sans redéployer | Haute |
| A12 | **Logs en temps réel** | Streaming des logs applicatifs via WebSocket (déjà `ws_admin_logs_router`) | ✅ Existe (vérifier fonctionnel) |

### 13.3 Frontend admin — Pages existantes

| Page | Fonction | État |
|------|----------|------|
| `/admin` | Dashboard admin principal | ✅ |
| `/admin/utilisateurs` | Gestion utilisateurs | ✅ |
| `/admin/notifications` | Test notifications push | ✅ |
| `/admin/jobs` | Status des jobs CRON | ✅ |
| `/admin/services` | Santé des services | ✅ |
| `/admin/sql-views` | Browser de vues SQL | ✅ |

### 13.4 Pages admin à ajouter

| # | Page | Contenu |
|---|------|---------|
| AP1 | `/admin/events` | Visualiser le bus d'événements en temps réel + trigger manuel |
| AP2 | `/admin/automations` | Gérer les règles d'automation + exécution manuelle |
| AP3 | `/admin/ia-metrics` | Dashboard métriques IA (appels, coût, cache hit rate) |
| AP4 | `/admin/notifications-queue` | File d'attente notifications + flush manuel |
| AP5 | `/admin/feature-flags` | Panneau de feature flags |
| AP6 | `/admin/cache` | Stats cache détaillées + purge sélective (par module/préfixe) |
| AP7 | `/admin/whatsapp-test` | Test de messages WhatsApp + visualiser conversation |

---

## 14. UX — Simplification du flux utilisateur

### 14.1 Principe directeur

> **Règle UX** : L'utilisateur ne doit pas avoir plus de 3 actions pour accomplir une tâche courante. Le système anticipe et propose, l'utilisateur valide.

### 14.2 Flux critiques à simplifier

#### Flux 1 : "Qu'est-ce qu'on mange cette semaine ?"

```
ACTUEL (6 étapes):
1. Aller dans Cuisine → Planning
2. Cliquer "Générer planning"
3. Configurer les préférences
4. Valider le planning
5. Aller dans Courses
6. Générer la liste de courses

PROPOSÉ (2 étapes):
1. Dashboard → Bouton "Planifier ma semaine" (ou WhatsApp "Menu")
2. IA génère planning + courses en 1 clic → Validation
   └── Option "Modifier" si besoin
```

**Actions** :
- Ajouter un bouton "Planifier ma semaine" sur le dashboard
- Le planning IA prend en compte : inventaire actuel, préférences, saison, budget, historique
- La liste de courses est auto-générée (corrigée par l'inventaire existant)
- Envoi WhatsApp automatique du planning validé

#### Flux 2 : "J'ai fait les courses"

```
ACTUEL (4 étapes):
1. Aller dans Courses → Liste active
2. Cocher les articles un par un
3. Aller dans Inventaire
4. Mettre à jour les stocks

PROPOSÉ (1 étape):
1. Bouton "Courses faites" → Cocher tout d'un coup ou par catégorie
   └── Auto-checkout + auto-update inventaire
```

**Actions** :
- Bouton "Tout cocher" ou cochage par catégorie (frais, épicerie, hygiène…)
- Match automatique avec la liste de courses → checkout
- Articles restants non cochés → reporter à la prochaine liste
- Inventaire mis à jour automatiquement

#### Flux 3 : "Suivi de Jules"

```
ACTUEL (multiple pages):
- Page Jules pour les jalons
- Page Activités pour les activités
- Page Routines pour les routines
- Page Budget pour les achats bébé

PROPOSÉ (1 hub intelligent):
1. Hub Jules unifié avec :
   ├── Timeline du jour (routines + activités + repas)
   ├── Prochains jalons à venir
   ├── Suggestion d'activité IA (1 click "Valider")
   └── Achats recommandés (taille vêtements, jouets d'éveil)
```

#### Flux 4 : "Entretien de la maison"

```
ACTUEL:
- Aller dans Maison → Entretien → Voir les tâches à faire
- Manuellement les compléter

PROPOSÉ:
1. Dashboard maison → "Tâches du jour" avec swipe pour compléter
   └── Notification push matin avec les tâches du jour
   └── Swipe gauche = fait, swipe droit = reporter
```

### 14.3 Composants UX à ajouter

| # | Composant | Description | Modules |
|---|-----------|-------------|---------|
| UX1 | **Wizard "Première semaine"** | Onboarding guidé : configurer préférences alimentaires, ajouter inventaire, planifier première semaine | Cuisine |
| UX2 | **Quick Actions Dashboard** | 4-6 actions rapides sur le dashboard (Planifier semaine, Courses du jour, Tâche du jour, Météo) | Dashboard |
| UX3 | **Swipe-to-complete** | Composant swipeable pour compléter tâches/routines/courses (déjà `swipeable-item.tsx` présent) | Multi |
| UX4 | **Bottom sheet contextuel** | Au lieu de naviguer vers une page, afficher un bottom sheet avec les actions courantes | Mobile |
| UX5 | **Mode Focus "Ce soir"** | Une seule vue : recette du soir + ingrédients ok/manquants + minuteur + musique | Cuisine |
| UX6 | **Barre de recherche vocale** | "Ajoute du lait à la liste de courses" → exécution directe | Multi |
| UX7 | **Raccourcis depuis la notification** | Notification "Péremption yaourts" → bouton "Voir recette" directement dans la notif | Courses |

---

## 15. Organisation du code — Refactoring nécessaire

### 15.1 Code mort à supprimer

| # | Fichier | Raison |
|---|---------|--------|
| R1 | `src/services/core/utilisateur/historique.py` (stubs "UI supprimée") | Stubs rétrocompatibles pour une UI qui n'existe plus |
| R2 | `src/services/core/base/ai_mixins.py:10` (classe vide `...`) | Base mixin jamais implémentée |
| R3 | `src/services/core/base/ai_streaming.py:9` (classe vide `...`) + `print()` | Streaming mixin vide + debug prints |
| R4 | `alembic/` (dossier entier) | Alembic non utilisé — migrations SQL-file uniquement |
| R5 | `src/core/ai/router.py:26` | `print()` debug dans le router IA |

### 15.2 Refactoring structurel

| # | Zone | Problème | Solution |
|---|------|----------|----------|
| R6 | Routes famille | 4 fichiers routes (`famille.py`, `famille_jules.py`, `famille_activites.py`, `famille_budget.py`) sans prefix cohérent — certains n'ont pas de prefix propre | Documenter la composition des routers et s'assurer que chaque sous-router a un prefix explicite |
| R7 | Routes jeux | 5 fichiers routes (`jeux.py`, `jeux_paris.py`, `jeux_loto.py`, `jeux_euromillions.py`, `jeux_dashboard.py`) | Même problème — documenter |
| R8 | Routes maison | 5 fichiers routes (`maison.py`, `maison_entretien.py`, `maison_finances.py`, `maison_jardin.py`, `maison_projets.py`) | Même problème |
| R9 | `frontend/src/bibliotheque/api/outils.ts` vs `utilitaires.ts` | Deux fichiers qui exportent les mêmes fonctions (contacts, journal, énergie) | Supprimer le doublon et garder un seul |
| R10 | Services cuisine/recettes | 3 stubs (`_ia_versions.py`, `recherche_mixin.py`, `_ia_suggestions.py`) | Soit implémenter soit supprimer |

### 15.3 Typage à corriger

| # | Fichier | Correction |
|---|---------|-----------|
| R11 | `frontend/src/bibliotheque/api/famille.ts:481` | Typer correctement la réponse checklist |
| R12 | `frontend/src/bibliotheque/api/maison.ts:1036,1345` | Typer correctement briefing et planning |
| R13 | `frontend/src/app/(app)/jeux/page.tsx:182` | Typer les widgets dashboard jeux |
| R14 | `frontend/src/app/(app)/parametres/onglet-notifications.tsx:104` | Typer les canaux par catégorie |

---

## 16. Axes d'innovation & amélioration

### 16.1 Innovations techniques

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| IN1 | **Mode offline-first** | Service Worker + IndexedDB pour fonctionner sans réseau (recettes, liste courses, minuteur) | PWA déjà initiée (`enregistrement-sw.tsx`, `install-prompt.tsx`) mais pas complète |
| IN2 | **Voice-first interface** | Hooks vocaux déjà présents (`utiliser-reconnaissance-vocale.ts`, `utiliser-synthese-vocale.ts`) → les connecter à tous les modules | UX mains libres en cuisine |
| IN3 | **Widgets tablette home screen** | Widgets natifs Android via PWA : planning du jour, minuteur, liste courses | Accès rapide |
| IN4 | **Auto-sync OpenFoodFacts enrichi** | Scan code-barres → enrichir automatiquement avec nutriscore, allergènes, provenance | Nutrition |
| IN5 | **Mode collaboratif couple** | Partage planning/courses en temps réel via WebSocket (déjà `websocket_courses.py`) → étendre à planning/tâches | Famille |
| IN6 | **Export données structuré** | Export CSV/JSON de chaque module (backup personnel) | Sécurité |
| IN7 | **Dark mode intelligent** | Déjà next-themes → ajouter mode auto (sombre le soir, clair le jour) basé sur les habitudes | UX |

### 16.2 Innovations fonctionnelles

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| IN8 | **Score éco-responsable** | Calculer un score écologique mensuel : gaspillage alimentaire, consommation énergie, achats locaux/bio | Conscience écologique |
| IN9 | **Planning activités Jules IA adaptatif** | IA génère un planning hebdo d'activités pour Jules en fonction de son âge, de la météo, des activités passées, et des recommandations de développement | Développement enfant |
| IN11 | **Tableau de bord santé foyer** | Score global santé du foyer : alimentation (diversité, équilibre), activité physique (Garmin), bien-être (routines), sommeil | Bien-être |
| IN12 | **Saisonnalité intelligente** | Le système adapte automatiquement : recettes (produits de saison), jardin (actions saisonnières), entretien (tâches saisonnières), énergie (chauffage/clim) | Pertinence |
| IN13 | **Rétrospective annuelle** | Fin d'année : rapport IA sur les 12 mois — recettes préférées, dépenses, évolution Jules, projets maison terminés, objectifs atteints | Mémoire familiale |
| IN14 | **Apprentissage continu** | Le système apprend des habitudes : si une recette est toujours repoussée → arrêter de la suggérer ; si les courses du mardi contiennent toujours du pain → le pré-cocher | UX |
| IN15 | **Alertes intelligentes contextuelles** | Au lieu de notifications fixes → notifications contextuelles : "Il fait beau, Jules pourrait aller au parc" (météo + calendrier + historique activités) | Pertinence |

### 16.3 Innovations DevOps

| # | Innovation | Description |
|---|-----------|-------------|
| IN16 | **CI/CD GitHub Actions** | Pipeline : lint + tests + build + deploy staging → Vercel preview |
| IN17 | **Feature flags runtime** | Activer/désactiver des fonctionnalités sans redéploiement (LaunchDarkly ou maison) |
| IN18 | **Monitoring coût IA** | Dashboard suivi tokens Mistral consommés + budget mensuel IA |
| IN19 | **Tests de mutation** | `mutmut` déjà en dépendance → configurer et exécuter pour valider la robustesse des tests |
| IN20 | **Health check dashboard** | Page publique `/status` avec uptime de chaque service |

---

## 17. Plan d'action priorisé

### Phase 1 — Fondations (bugs critiques + dette technique)

| # | Action | Fichiers | Effort |
|---|--------|----------|--------|
| 1.1 | Corriger le secret hardcodé `dependencies.py:65` | `src/api/dependencies.py` | S |
| 1.2 | Remplacer les 6 `print()` par `logger` dans le pipeline IA | `ai_streaming.py`, `streaming.py`, `router.py`, `health.py`, `file_attente.py` | S |
| 1.3 | Supprimer le code mort (stubs vides, historique UI, alembic/) | 5+ fichiers | S |
| 1.4 | Corriger les 12 `as unknown as` dans le frontend (aligner types) | `famille.ts`, `maison.ts`, `jeux/page.tsx`, etc. | M |
| 1.5 | Supprimer le doublon `outils.ts` / `utilitaires.ts` frontend | `frontend/src/bibliotheque/api/` | S |
| 1.6 | Consolider SQL : absorber V003-V007 dans `schema/`, script de build INIT_COMPLET | `sql/` | M |
| 1.7 | Ajouter tables manquantes : `batch_cooking_congelation`, `ia_suggestions_historique` | `sql/schema/` + modèles | M |

### Phase 2 — Tests (couverture critique)

| # | Action | Effort |
|---|--------|--------|
| 2.1 | Tests unitaires décorateurs core (`@avec_cache`, `@avec_session_db`, `@avec_validation`, `@avec_resilience`) | M |
| 2.2 | Tests unitaires resilience policies (Retry, CircuitBreaker, Bulkhead, Timeout) | M |
| 2.3 | Tests unitaires des 12 inter-module bridges | L |
| 2.4 | Tests unitaires event bus + subscribers | M |
| 2.5 | Tests frontend : composants critiques (formulaire-recette, barre-laterale, recherche-globale) | M |
| 2.6 | Tests frontend : hooks (utiliser-auth, utiliser-api, utiliser-crud) | M |
| 2.7 | Tests frontend : API clients (recettes.ts, courses.ts, planning.ts) | M |

### Phase 3 — Features manquantes (stubs → implémentation)

| # | Action | Service | Effort |
|---|--------|---------|--------|
| 3.1 | Implémenter recherche avancée recettes | `recherche_mixin.py` | M |
| 3.2 | Implémenter suggestions IA recettes | `recettes_ia_suggestions.py` | M |
| 3.3 | Implémenter versions IA recettes | `recettes_ia_versions.py` | M |
| 3.4 | Implémenter intégration Google Calendar | `google_auth.py`, `google_calendar.py` | L |
| 3.5 | Compléter notifications jeux | `notification_service.py` | M |
| 3.6 | Table + persistance congélation | `congelation.py` + SQL | M |
| 3.7 | Compléter typage gamification frontend | `gamification/page.tsx` | S |

### Phase 4 — Interactions inter-modules (nouveaux bridges)

| # | Action | Priorité |
|---|--------|----------|
| 4.1 | `inter_module_inventaire_planning.py` — Stock → Planning recettes | Haute |
| 4.2 | `inter_module_meteo_activites.py` — Météo → Activités famille | Haute |
| 4.3 | `inter_module_entretien_courses.py` — Entretien → Courses | Haute |
| 4.4 | `inter_module_charges_energie.py` — Charges → Énergie anomalies | Moyenne |
| 4.5 | `inter_module_routine_gamification.py` — Routines → Points | Moyenne |
| 4.6 | `inter_module_weekend_courses.py` — Weekend → Courses | Moyenne |
| 4.7 | `inter_module_jules_nutrition.py` — Jules → Planning nutrition | Haute |
| 4.10 | `inter_module_saison_menu.py` — Saison → Planning IA | Haute |
| 4.11 | `inter_module_documents_calendrier.py` — Documents → Calendrier | Basse |

### Phase 5 — UX & simplification

| # | Action | Effort |
|---|--------|--------|
| 5.1 | Bouton "Planifier ma semaine" sur le dashboard (planning + courses en 1 clic) | M |
| 5.2 | Bouton "Courses faites" (cochage bulk par catégorie) → auto-checkout + MAJ inventaire | M |
| 5.3 | Hub Jules unifié (timeline jour + jalons + suggestion IA) | M |
| 5.4 | Swipe-to-complete pour tâches/routines (étendre le composant existant) | S |
| 5.5 | Quick Actions sur le dashboard (4-6 boutons d'actions rapides) | S |
| 5.6 | Mode "Ce soir" — vue focalisée sur le repas du soir | M |
| 5.7 | Commandes WhatsApp conversationnelles (Courses, Ce soir, Budget, Jules, Aide) | L |

### Phase 6 — Jobs CRON & notifications

| # | Action | Effort |
|---|--------|--------|
| 6.1 | Ajouter les 12 jobs manquants (J1-J12) | L |
| 6.2 | Ajouter les 10 notifications manquantes (N1-N10) | M |
| 6.3 | Commandes WhatsApp conversationnelles (machine d'états étendue) | L |

### Phase 7 — Admin avancé

| # | Action | Effort |
|---|--------|--------|
| 7.1 | Trigger event bus manuel depuis admin | M |
| 7.2 | Dashboard métriques IA (tokens, coût, cache) | M |
| 7.3 | Panneau feature flags | M |
| 7.4 | File d'attente notifications visuelle + flush | S |
| 7.5 | Exécution automation manuelle | S |
| 7.6 | Pages admin frontend (AP1-AP7) | L |

### Phase 8 — IA avancée & innovations

| # | Action | Effort |
|---|--------|--------|
| 8.1 | Mode "Qu'est-ce qu'on mange ce soir ?" (IA11) | M |
| 8.2 | Détection patterns alimentaires (IA1) | L |
| 8.3 | Coach routines IA (IA3) | M |
| 8.4 | Score éco-responsable (IN8) | M |
| 8.6 | Saisonnalité intelligente (IN12) | L |
| 8.7 | Apprentissage continu des habitudes (IN14) | L |
| 8.8 | Rétrospective annuelle IA (IN13) | L |

### Phase 9 — Documentation

| # | Action | Effort |
|---|--------|--------|
| 9.1 | `docs/EVENT_BUS.md` — Catalogue événements + subscribers | M |
| 9.2 | `docs/SECURITY.md` — Politique de sécurité complète | M |
| 9.3 | `docs/DATA_MODEL.md` — Modèle de données détaillé 130 tables | L |
| 9.4 | `docs/WHATSAPP_COMMANDS.md` — Commandes conversationnelles | S |
| 9.5 | `docs/MONITORING.md` — Métriques et alerting | S |
| 9.6 | `docs/guides/RECIPE_FLOW.md` — Guide utilisateur recettes | S |
| 9.7 | `docs/guides/FAMILY_FLOW.md` — Guide utilisateur famille | S |
| 9.8 | Mettre à jour `API_REFERENCE.md`, `MODULES.md`, `INTER_MODULES.md` | M |
| 9.9 | Auto-générer `API_SCHEMAS.md` depuis Pydantic | S |

---

### Légende effort

| Taille | Estimation |
|--------|-----------|
| **S** (Small) | 1-3 fichiers, changements simples |
| **M** (Medium) | 3-8 fichiers, logique modérée |
| **L** (Large) | 8+ fichiers, logique complexe ou multi-couches |

---

## Annexe A — Inventaire des fichiers de données de référence

```
data/reference/
├── astuces_domotique.json           ✅
├── calendrier_soldes.json           ✅
├── calendrier_vaccinal_fr.json      ✅
├── catalogue_pannes_courantes.json  ✅
├── entretien_catalogue.json         ✅
├── guide_lessive.json               ✅
├── guide_nettoyage_surfaces.json    ✅
├── guide_travaux_courants.json      ✅
├── normes_oms.json                  ✅
├── nutrition_table.json             ✅
├── plantes_catalogue.json           ✅
├── portions_age.json                ❌ MANQUANT
├── produits_de_saison.json          ✅
├── produits_menagers.json           ❌ MANQUANT
├── routines_defaut.json             ✅
└── template_import_inventaire.csv   ✅
```

## Annexe B — Inventaire WebSocket

| Route WS | Fonction | État |
|----------|----------|------|
| `/ws/courses/{liste_id}` | Collaboration temps réel courses | ✅ |
| `/ws/planning` | Collaboration planning | ✅ |
| `/ws/notes` | Édition collaborative notes | ✅ |
| `/ws/projets` | Kanban projets maison | ✅ |
| `/ws/admin/logs` | Streaming logs admin | ✅ |

## Annexe C — Canaux de notification par module

| Module | Push | ntfy | WhatsApp | Email |
|--------|------|------|----------|-------|
| Cuisine (péremption) | ✅ | ✅ | · | · |
| Cuisine (planning) | · | · | ✅ | · |
| Courses (rappel) | ✅ | ✅ | ✅ | · |
| Famille (anniversaire) | ✅ | ✅ | ✅ | · |
| Famille (documents) | ✅ | ✅ | · | ✅ |
| Famille (budget) | · | · | · | ✅ |
| Maison (entretien urgent) | ✅ | ✅ | ✅ | · |
| Maison (garantie) | ✅ | · | · | ✅ |
| Jeux (résultats) | ✅ | ✅ | · | · |
| Dashboard (badges) | ✅ | ✅ | · | · |
| Admin (échec CRON) | ✅ | ✅ | ✅ | ✅ |
| Multi (digest matin) | · | · | ✅ | · |
| Multi (résumé hebdo) | · | · | ✅ | ✅ |
| Multi (rapport mensuel) | · | · | · | ✅ |
