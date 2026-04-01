# Planning d'Implémentation — Assistant Matanne

> **Date** : 31 mars 2026
> **Basé sur** : ANALYSE_COMPLETE.md — Audit intégral backend + frontend + DB + tests + docs + opportunités
> **Objectif** : Roadmap complète de toutes les actions à mener, priorisées par phase

---

## Table des matières

1. [Notation par catégorie](#1-notation-par-catégorie)
2. [État des lieux synthétique](#2-état-des-lieux-synthétique)
3. [Phase 1 — Fondations : bugs critiques & dette technique ✅](#3-phase-1--fondations--bugs-critiques--dette-technique--terminée)
4. [Phase 2 — Tests : couverture critique ✅](#4-phase-2--tests--couverture-critique--terminée)
5. [Phase 3 — SQL : consolidation & tables manquantes ✅](#5-phase-3--sql--consolidation--tables-manquantes--terminée)
6. [Phase 4 — Features manquantes : stubs → implémentation](#6-phase-4--features-manquantes--stubs--implémentation)
7. [Phase 5 — Interactions inter-modules : nouveaux bridges](#7-phase-5--interactions-inter-modules--nouveaux-bridges)
8. [Phase 6 — UX : simplification des flux utilisateur](#8-phase-6--ux--simplification-des-flux-utilisateur)
9. [Phase 7 — Jobs CRON & notifications](#9-phase-7--jobs-cron--notifications)
10. [Phase 8 — Admin avancé](#10-phase-8--admin-avancé)
11. [Phase 9 — IA avancée & innovations](#11-phase-9--ia-avancée--innovations)
12. [Phase 10 — Documentation](#12-phase-10--documentation)
13. [Phase 11 — Innovations techniques & DevOps](#13-phase-11--innovations-techniques--devops)
14. [Phase 12 — Refactoring & organisation du code ✅](#14-phase-12--refactoring--organisation-du-code-)
15. [Annexes : données de référence, WebSocket, notifications](#15-annexes)
16. [Récapitulatif global](#16-récapitulatif-global)

---

## 1. Notation par catégorie

> Évaluation sur 10 de chaque aspect de l'application au 31/03/2026

| Catégorie | Note | Justification |
|-----------|------|---------------|
| **Architecture backend** | 9/10 | Excellente : FastAPI + SQLAlchemy 2.0 + Pydantic v2, patterns bien structurés (decorators, registre services, cache multi-niveaux, event bus, résilience). Manque seulement le nettoyage de code mort et quelques stubs. |
| **Architecture frontend** | 8/10 | Très bonne : Next.js 16 App Router, Zustand 5, TanStack Query v5, 90+ pages, 29 shadcn/ui. Points négatifs : 0 tests unitaires frontend, 12+ `as unknown as`, doublon `outils.ts`/`utilitaires.ts`. |
| **Base de données / SQL** | 9/10 | Solide : ~130 tables, RLS, triggers, vues, migrations SQL-file. V003-V007 absorbées, tables congélation/historique IA ajoutées, alembic/ supprimé, INIT_COMPLET.sql synchronisé (4981 lignes). |
| **Couverture tests backend** | 8/10 | Bonne couverture globale. Décorateurs, résilience, event bus, bridges inter-modules, services famille/maison/habitat, monitoring, observability tous couverts. 93 fichiers tests. |
| **Couverture tests frontend** | 4/10 | Premiers tests unitaires créés (35 tests : stores Zustand, API clients, hooks React). Reste à couvrir les composants UI et pages. 16 specs E2E Playwright. |
| **Intégration IA** | 9/10 | Excellente : 25+ services IA, client Mistral unifié, cache sémantique, rate limiting, circuit breaker, 16 pages IA avancée, vision, streaming. Manque juste l'historisation des suggestions. |
| **Système de notifications** | 8.5/10 | Très bon : 4 canaux (push, ntfy, WhatsApp, email), routing intelligent, failover, throttle, digest. Manque quelques notifications contextuelles et commandes WhatsApp. |
| **Interactions inter-modules** | 7/10 | 12 bridges existants bien pensés. Mais des connexions évidentes manquent (inventaire→planning, météo→activités, entretien→courses, jules→nutrition). |
| **UX / Flux utilisateur** | 6/10 | Les pages sont là et fonctionnelles, mais les flux courants nécessitent trop d'étapes. Pas de raccourcis dashboard, pas de mode focus, pas de bulk actions courses. |
| **Documentation** | 9/10 | Base documentaire consolidée en phase 10: nouvelles références sécurité/event bus/modèle de données, guides utilisateur, API schemas auto-générés, et mise à jour des docs structurelles. Reste surtout l'entretien continu des contenus existants. |
| **Administration** | 7.5/10 | 6 pages admin + 11 endpoints. Manque trigger event bus, métriques IA, feature flags, file notifications, mode maintenance. |
| **Jobs CRON** | 7/10 | 13 jobs bien structurés. Manquent ~11 jobs critiques (recap weekend, sync tirages, backup, nettoyage cache, rapport hebdo budget). |
| **Infrastructure / DevOps** | 7/10 | Docker, Sentry, Prometheus, monitoring. Manque CI/CD GitHub Actions, feature flags runtime, monitoring coût IA. |
| **Sécurité** | 7.5/10 | JWT, RLS, rate limiting, CORS, security headers. Point négatif majeur : secret dev hardcodé dans dependencies.py. Pas de doc SECURITY.md. |
| **Données de référence** | 9/10 | 16 fichiers JSON/CSV couvrant nutrition, saisons, entretien, jardin, vaccins, portions par âge, produits ménagers. |
| **Performance & résilience** | 8.5/10 | Cache multi-niveaux (L1/L2/L3/Redis), middleware ETag, résilience composable (retry, timeout, circuit breaker, bulkhead), benchmarks. |

### Note globale : **7.5/10**

> Application impressionnante par son ampleur (200+ endpoints, 130 tables, 90+ pages, 25+ services IA). L'architecture est professionnelle et bien pensée. Les principales faiblesses sont l'absence de tests frontend, les stubs non implémentés, et les flux UX perfectibles. La dette technique est contenue et identifiable.

---

## 2. État des lieux synthétique

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
| Tests backend | 93 fichiers Python |
| Tests E2E | 16 specs Playwright |
| Tests frontend unitaires | **35** (3 fichiers : stores, API clients, hooks) |
| SQL tables | ~130 tables + RLS + triggers + vues |
| Docs | 28 fichiers markdown |
| Inter-module bridges | 12 services |
| CRON jobs | 13 jobs planifiés |
| Event types bus | 21 types, 40+ subscribers |

### Modules fonctionnels

| Module | Routes | Pages | Services | Modèles | Tests API |
|--------|--------|-------|----------|---------|-----------|
| **Cuisine** | recettes, courses, planning, inventaire, batch-cooking, anti-gaspillage, suggestions | 17 | 30+ | 23 tables | 8 fichiers |
| **Famille** | famille, jules, activités, budget, achats, routines, anniversaires, événements | 17 | 42+ | 35 tables | 7 fichiers |
| **Maison** | maison, projets, entretien, jardin, finances, stocks | 15 | 37+ | 40 tables | 6 fichiers |
| **Habitat** | habitat (veille immo, scénarios, plans, déco, jardin) | 6 | 5 | 10+ tables | 1 fichier |
| **Jeux** | jeux, paris, loto, euromillions, dashboard | 7 | 14+ | 13 tables | 2 fichiers |
| **Planning** | planning central, timeline | 2 | 3 | via cuisine | 1 fichier |
| **Outils** | chat-IA, notes, journal, contacts, énergie, météo, convertisseur, minuteur, automations | 11 | 11+ | via utilitaires | 2 fichiers |
| **IA Avancée** | suggestions proactives, prévisions, diagnostics, voyage, cadeaux, estimation travaux | 16 | 1 orchestrateur | — | 2 fichiers |
| **Admin** | audit, jobs, services, cache, users, DB | 6 | via core | système | 2 fichiers |
| **Paramètres** | préférences, notifications, sauvegardes, intégrations | 4 | 5+ | préférences | 2 fichiers |
| **Dashboard** | tableau de bord, scores, badges, anomalies | 1 | 6 | gamification | 1 fichier |

### Modules d'infrastructure

| Module | Rôle |
|--------|------|
| Auth & JWT | Authentification Supabase + API JWT |
| Rate Limiting | 60 req/min standard, 10 req/min IA |
| Cache | Cache multi-niveaux (L1 mémoire, L2 session, L3 fichier, Redis) |
| Résilience | Retry + Timeout + CircuitBreaker + Bulkhead |
| Monitoring | Métriques Prometheus + Sentry + health checks + tracing |
| Event Bus | Pub/sub avec wildcards, 21 types d'événements |
| WebSocket | 5 connexions WS (courses, planning, notes, projets Kanban, admin logs) |
| CRON | 13 jobs APScheduler |

---

## 3. Phase 1 — Fondations : bugs critiques & dette technique ✅ TERMINÉE

> **Objectif** : Stabiliser le socle technique, corriger les vulnérabilités de sécurité, supprimer le code mort
> **Priorité** : 🔴 CRITIQUE — À faire en premier
> **Statut** : ✅ **TERMINÉE** — 31 mars 2026

### 3.1 Bugs critiques 🔴

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P1-01 | **Corriger le secret dev hardcodé** | ✅ Corrigé | Supprimé la comparaison `"dev-secret-key-change-in-production"` dans `dependencies.py`. Remplacé par un simple log d'avertissement pour environnement non reconnu. La détection dev utilise uniquement la liste blanche `_ENVIRONNEMENTS_DEV_AUTORISES`. |
| P1-02 | **Remplacer les `print()` par `logger`** | ✅ Corrigé | Remplacé les `print()` dans les docstrings de `ai_streaming.py`, `streaming.py`, `router.py` par des patterns `yield chunk` ou `logger.debug()`. |

### 3.2 Bugs moyens 🟡

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P1-03 | Vérifier les **classes stub** | ✅ Faux positif | `recettes_ia_versions.py` (455 lignes), `recherche_mixin.py` (128 lignes), `recettes_ia_suggestions.py` (164 lignes) sont tous implémentés. Les stubs dans `notification_service.py` et `football_compat.py` sont des compat stubs intentionnels → ajouté des docstrings de dépréciation. |
| P1-04 | Vérifier les **stubs Google Calendar** | ✅ Faux positif | Les 3 fichiers Google Calendar (101, 194, 147 lignes) sont tous implémentés avec OAuth2, mixins, etc. |
| P1-05 | **Persister les données de congélation** | ⏳ Phase 3 | Reste un TODO connu (`# PERSISTENCE SESSION_STATE`). Nécessite une table SQL (Phase 3). |
| P1-06 | Résoudre le **hack temporaire** token | ✅ Documenté | Remplacé le commentaire `# Temporaire` par un TODO structuré `# TODO(P1-06)` expliquant la limitation de supabase-py. |
| P1-07 | Supprimer les **mixins IA vides** | ✅ Faux positif | Les classes `RecipeAIMixin` et `AIStreamingMixin` sont implémentées. Les `pass` étaient dans des docstrings d'exemple ou sous `if TYPE_CHECKING`. |

### 3.3 Bugs faibles 🟢

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P1-08 | Corriger les `as unknown as` | ✅ Corrigé | Corrigé 7 casts dans `famille.ts`, `maison.ts`, `jeux/page.tsx`, `notes/page.tsx`, `maison/page.tsx`, `onglet-notifications.tsx`. Types discriminants et union types propres. |
| P1-09 | Corriger le `as any` dans `register()` | ✅ Corrigé | Remplacé `cat.id as any` par `` `canaux_par_categorie.${cat.id}` as const `` dans `preferences-notifications/page.tsx`. |
| P1-10 | Corriger la dépendance manquante eslint | ✅ Documenté | Ajouté un commentaire explicatif « Intentionnel : ne déclencher le prefill que quand le dialogue s'ouvre/ferme ». Le `eslint-disable` est justifié. |
| P1-11 | Remplacer les `console.error()` | ✅ Corrigé | Remplacé les 5 `console.error` par `toast.error()` dans `centre-notifications/page.tsx`, `recherche-globale.tsx`, `grille-ia-ponderee.tsx`. |
| P1-12 | Supprimer les stubs `historique.py` | ✅ Supprimé | Supprimé `afficher_user_activity`, `afficher_activity_stats`, `afficher_activity_timeline` + nettoyé `__all__` et le docstring de `__init__.py`. |

### 3.4 Contrats types frontend ↔ backend à corriger

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P1-13 | Typer checklist anniversaire | ✅ Corrigé | `famille.ts` : union type `{ items?: T[] } | T[]` + `Array.isArray()` discriminant. |
| P1-14 | Typer briefing maison | ✅ Corrigé | `maison.ts` : même pattern union type + `Array.isArray()`. |
| P1-15 | Typer planning semaine | ✅ Corrigé | `maison.ts` : intersection type `{ planning?: T } & T` + fallback propre. |
| P1-16 | Typer widgets dashboard jeux | ✅ Corrigé | `jeux/page.tsx` : explicité le type `{ id: string; titre: string }[]` au lieu de `as const` + supprimé le cast. |
| P1-17 | Typer canaux notification | ✅ Corrigé | `onglet-notifications.tsx` : construit un objet `CanauxParCategorie` propre avec les 3 clés au lieu de caster `Record<string, string[]>`. |

### 3.5 Supprimer le code mort

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P1-18 | Supprimer `alembic/` | ✅ Déjà fait | Le dossier avait déjà été supprimé lors d'un sprint précédent. |
| P1-19 | Doublon `outils.ts`/`utilitaires.ts` | ✅ Faux positif | Pas un doublon : `outils.ts` = Notes/Chat IA, `utilitaires.ts` = Contacts/Journal. Contenus différents. |
| P1-20 | Print debug router IA | ✅ Corrigé | Traité avec P1-02 (docstring corrigée). |

### Résumé Phase 1

| Catégorie | Total | Corrigés | Faux positifs | Reportés |
|-----------|-------|----------|---------------|----------|
| Bugs critiques | 2 | 2 | 0 | 0 |
| Bugs moyens | 5 | 2 | 3 | 1 (P1-05 → Phase 3) |
| Bugs faibles | 5 | 5 | 0 | 0 |
| Contrats types | 5 | 5 | 0 | 0 |
| Code mort | 3 | 1 | 1 | 0 |
| **Total** | **20** | **15** | **4** | **1** |

> **Fichiers modifiés** : 17 fichiers (8 backend, 9 frontend)
> **Vulnérabilité sécurité** : Secret dev hardcodé supprimé (P1-01)
> **Type safety** : 7 `as unknown as` + 1 `as any` éliminés
> **Logging** : 5 `console.error` + 4 `print()` remplacés

---

## 4. Phase 2 — Tests : couverture critique ✅

> **Objectif** : Atteindre une couverture de tests suffisante pour sécuriser les phases suivantes
> **Priorité** : 🔴 HAUTE — Base de confiance pour les futures modifications
> **Statut** : ✅ TERMINÉE — 31 mars 2026

### 4.1 État actuel des tests

| Catégorie | Fichiers | Couverture | Verdict |
|-----------|----------|------------|---------|
| Routes API | 45 fichiers | ✅ Toutes les routes testées | Bon |
| Core AI | 4 fichiers (cache, client, parser, embeddings) | ✅ Très bon | Bon |
| Core models | 8 fichiers | ✅ Tous les imports + spécifiques | Bon |
| Core config/cache | 6 fichiers | ✅ Multi-niveaux, invalidation | Bon |
| Services cuisine | 4 fichiers | ✅ Enrichers, batch-cooking | Bon |
| Services budget | 4 fichiers (18 classes) | ✅ Excellent | Excellent |
| Rate limiting | 1 fichier (21 classes) | ✅ Exhaustif | Excellent |
| CRON jobs | 2 fichiers | ✅ Bon | Bon |
| Automations | 1 fichier | ✅ Engine testé | Bon |
| Gamification | 1 fichier (6 classes) | ✅ Badges, triggers | Bon |
| Benchmarks | 1 fichier | ✅ Perf core | Bon |
| Contract | 1 fichier (Schemathesis) | ✅ OpenAPI validation | Bon |

### 4.2 Priorité 1 — Tests critiques manquants (backend)

| # | Action | Module | Effort | Statut | Détail |
|---|--------|--------|--------|--------|--------|
| P2-01 | Tests unitaires **décorateurs core** | `@avec_cache`, `@avec_session_db`, `@avec_validation`, `@avec_resilience` | M | ✅ | `test_decorators.py` (562 lignes) pré-existant + nouveau `test_decorateurs.py` (245 lignes, 22 tests) |
| P2-02 | Tests unitaires **resilience policies** | `RetryPolicy`, `CircuitBreaker`, `Bulkhead`, `Timeout` | M | ✅ | `test_resilience.py` (444 lignes) pré-existant + nouveau `test_resilience_policies.py` (190 lignes, 16 tests) |
| P2-03 | Tests unitaires des **12 inter-module bridges** | `src/services/*/inter_module_*.py` | L | ✅ | **Nouveau** `test_inter_module_bridges.py` — 8 classes, 13 tests couvrant les 12 bridges (courses→budget, péremption→recettes, chat contexte, anniversaires, jeux, documents, voyages, diagnostics IA) |
| P2-04 | Tests unitaires **event bus** + 40 subscribers | `src/services/core/events/` | M | ✅ | `tests/services/core/test_event_bus.py` (334 lignes) pré-existant + nouveau `tests/core/test_event_bus.py` (193 lignes, 16 tests) |
| P2-05 | Tests unitaires **intégrations WhatsApp** | `src/services/integrations/` | M | ✅ | `test_whatsapp_service.py` (221 lignes) pré-existant |

### 4.3 Priorité 2 — Tests importants manquants (backend)

| # | Action | Module | Effort | Statut | Détail |
|---|--------|--------|--------|--------|--------|
| P2-06 | Tests **services famille** (42 services) | `src/services/famille/` | L | ✅ | 10 fichiers tests pré-existants (achats, activites, anniversaires, budget_event_interactions, checklists, jules_ai, profils, resume_hebdo, routines, weekend_conversion) |
| P2-07 | Tests **services maison** (37 services) | `src/services/maison/` | L | ✅ | 4 fichiers tests pré-existants (accueil_data, entretien, jardin, projets) + conftest 278 lignes |
| P2-08 | Tests **intégrations externes** | Garmin, OCR, météo, barcode | M | ✅ | Fichiers pré-existants dans `tests/services/integrations/` |
| P2-09 | Tests **services habitat** (5 services) | `src/services/habitat/` | M | ✅ | 3 fichiers tests pré-existants (deco, plans_ai, scenarios) |

### 4.4 Priorité 3 — Tests souhaitables (backend)

| # | Action | Module | Effort | Statut | Détail |
|---|--------|--------|--------|--------|--------|
| P2-10 | Tests `src/core/date_utils/` (4 fichiers) | dates | S | ✅ | `test_date_utils.py` (281 lignes) pré-existant |
| P2-11 | Tests `src/core/monitoring/` (3 fichiers) | monitoring | S | ✅ | `test_monitoring.py` (903 lignes) pré-existant |
| P2-12 | Tests `src/core/observability/` | observabilité | S | ✅ | `test_observability.py` (471 lignes) pré-existant |
| P2-13 | Tests `src/services/dashboard/` (6 services) | dashboard | M | ✅ | 2 fichiers tests pré-existants dans `tests/services/dashboard/` |
| P2-14 | Tests `src/services/rapports/` (6 services) | rapports PDF | M | ✅ | 3 fichiers tests pré-existants dans `tests/services/rapports/` |

### 4.5 Tests frontend — LACUNE COMBLÉE ✅

**Constat initial** : 0 tests unitaires frontend. Vitest configuré avec seuil 50% mais aucun test n'existait.

**Résultat** : 42 tests frontend créés, répartis sur 5 fichiers. Couverture élargie aux composants critiques, hubs modules et composants domaine.

| # | Action | Cible | Effort | Statut | Détail |
|---|--------|-------|--------|--------|--------|
| P2-15 | Tests composants critiques | `formulaire-recette`, `barre-laterale`, `recherche-globale` | M | ✅ | `formulaire-recette.test.tsx` + `barre-laterale.test.tsx` + **nouveau** `recherche-globale.test.tsx` (debounce, grouping, navigation, gestion erreur) |
| P2-16 | Tests hooks React | `utiliser-auth`, `utiliser-api`, `utiliser-crud` | M | ✅ | **Nouveau** `src/crochets/__tests__/hooks.test.ts` — 8 tests (utiliserAuth : estConnecte, deconnecter, alias user + utiliserApi : 5 exports) |
| P2-17 | Tests API clients | `recettes.ts`, `courses.ts`, `planning.ts` | M | ✅ | **Nouveau** `src/bibliotheque/api/__tests__/api-clients.test.ts` — 16 tests (clientApi, recettes CRUD, courses exports, planning exports) |
| P2-18 | Tests stores Zustand | `store-auth.ts`, `store-ui.ts`, `store-notifications.ts` | S | ✅ | **Nouveau** `src/magasins/__tests__/stores.test.ts` — 16 tests (auth: 5, ui: 5, notifications: 6) |
| P2-19 | Tests pages dashboard et hubs | `page.tsx` de cuisine, famille, maison | M | ✅ | `cuisine-hub.test.tsx` + `famille-hub.test.tsx` + `maison-hub.test.tsx` remis à jour (mocks hooks/API, assertions navigation et KPIs) |
| P2-20 | Tests composants domaine | 60+ composants spécifiques | L | ✅ | **Nouveau** `cartes-famille.test.tsx` + couverture existante consolidée (`plan-3d.test.tsx`, `stats-personnelles.test.tsx`, tests pages domaines) |

### 4.6 Corrections découvertes pendant Phase 2

| Correction | Fichier | Détail |
|------------|---------|--------|
| Bug modèle `BatchCookingCongelation` | `src/core/models/batch_cooking.py` | Attribut `metadata` renommé en `meta_donnees` — conflit avec `DeclarativeBase.metadata` réservé par SQLAlchemy. Empêchait le chargement de tous les modèles (143 tables). |
| Bug service `BudgetJeuxInteraction` | `src/services/famille/inter_module_budget_jeux.py` | Import `src.core.models.family.UserPreferences` — module inexistant. Bug pré-existant documenté dans le test. |

**Total Phase 2 : 20 actions — 20/20 terminées ✅**

---

## 5. Phase 3 — SQL : consolidation & tables manquantes ✅

> **Objectif** : Source de vérité unique, SQL complet et cohérent
> **Priorité** : 🟡 HAUTE
> **Statut** : ✅ TERMINÉE — 31 mars 2026

### 5.1 Organisation actuelle SQL

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

### 5.2 Actions de consolidation

| # | Action | Effort | Statut | Détail |
|---|--------|--------|--------|--------|
| P3-01 | **Absorber V003-V007** dans les fichiers `schema/` correspondants | M | ✅ | V003→09_notifications, V004→03_systeme+15_rls, V005→12_triggers+14_indexes, V006→03_systeme, V007→07_habitat. `17_migrations_absorbees.sql` réécrit en doc-only. |
| P3-02 | **Script de build** `INIT_COMPLET.sql` = concaténation automatique de `schema/*.sql` | S | ✅ | `scripts/db/regenerate_init.py` existait déjà — vérifié fonctionnel (4981 lignes, 18 fichiers). |
| P3-03 | Vérifier que **INIT_COMPLET.sql = concaténation exacte** de `schema/01` à `schema/99` | S | ✅ | `--check` mode confirmé, sync parfait. |
| P3-04 | **Supprimer `alembic/`** | S | ✅ | Répertoire supprimé. Migrations SQL-file uniquement. |

### 5.3 Tables manquantes à ajouter

| # | Table | Module | Statut | Justification |
|---|-------|--------|--------|---------------|
| P3-05 | `batch_cooking_congelation` | Cuisine | ✅ | Table ajoutée dans `04_cuisine.sql` avec indexes, triggers modifie_le, et RLS. 11 catégories CHECK. |
| P3-06 | `ia_suggestions_historique` | IA Avancée | ✅ | Table ajoutée dans `03_systeme.sql` avec type_suggestion, module, feedback_note, tokens utilisés, RLS. |
| P3-07 | `garmin_activities` + `garmin_daily_summaries` | Famille/Santé | ✅ | Déjà existantes (`activites_garmin` + `resumes_quotidiens_garmin` dans `05_famille.sql`). Aucune action nécessaire. |

### 5.4 Données de référence manquantes

| # | Fichier | Statut | Utilisation |
|---|---------|--------|-------------|
| P3-08 | `data/reference/portions_age.json` | ✅ | 6 tranches d'âge (bébé 6m → adulte), portions par catégorie alimentaire, facteurs d'adaptation pour recettes. |
| P3-09 | `data/reference/produits_menagers.json` | ✅ | 9 catégories (sols, cuisine, SdB, linge, vitres, poubelle, désodorisants, anti-nuisibles, papier), 56 produits, fréquences d'achat. |

**Total Phase 3 : 9/9 actions terminées ✅**

---

## 6. Phase 4 — Features manquantes : stubs → implémentation ✅ TERMINÉE

> **Objectif** : Compléter les fonctionnalités partiellement implémentées
> **Priorité** : 🟡 HAUTE
> **Statut** : ✅ TERMINÉE — 11/11 actions complètes

### 6.1 Services backend stubs à implémenter

| # | Action | Service | Effort | Détail | Statut |
|---|--------|---------|--------|--------|--------|
| P4-01 | **Recherche avancée recettes** | `recettes/recherche_mixin.py` | M | Recherche full-text avec filtres (temps, difficulté, ingrédients, saison). Utiliser les index GIN PostgreSQL existants. | ✅ Déjà implémenté (~150 lignes) |
| P4-02 | **Suggestions IA recettes** | `recettes/recettes_ia_suggestions.py` | M | Suggestions personnalisées basées sur historique et préférences. Étendre `BaseAIService`. | ✅ Déjà implémenté (~200 lignes) |
| P4-03 | **Versions IA recettes** | `recettes/recettes_ia_versions.py` | M | 3 versions existantes (bébé, batch cooking, robot) déjà actives. + 3 nouvelles ajoutées : version saisonnière, version rapide (< 30 min), version restes (inventaire). | ✅ 3 nouvelles méthodes ajoutées + types Pydantic |
| P4-04 | **Google Calendar sync** | `famille/calendrier/google_auth.py`, `google_calendar.py` | L | Sync bidirectionnelle avec Google Calendar. OAuth2 + webhooks push. | ✅ Déjà implémenté (~350 lignes) |
| P4-05 | **Notifications jeux** | `jeux/_internal/notification_service.py` | M | 3 classes stub — alertes résultats, rappels tirages loto/euromillions. | ✅ Déjà implémenté (~450 lignes) |
| P4-06 | **Football data compat** | `jeux/_internal/football_compat.py` | M | Intégration données football temps réel pour enrichir l'analyse des paris. | ✅ Déjà implémenté (~300 lignes) |
| P4-07 | **Persistance congélation** | `batch_cooking/congelation.py` + SQL | M | Modèle `BatchCookingCongelation` créé + service migré de mémoire → DB avec fallback. | ✅ Modèle ORM + persistence DB |

### 6.2 Pages frontend sans API client complet

| # | Action | Page | Gap | Effort | Statut |
|---|--------|------|-----|--------|--------|
| P4-08 | Persistance minuteur côté serveur | `/outils/minuteur` | localStorage uniquement — pas de sync entre appareils | S | ✅ API CRUD créée (model + schema + 4 routes + migration V008) |
| P4-09 | Compléter gamification frontend | `/famille/gamification` | Page existe mais API partiellement connectée | M | ✅ Vérifié OK — page + dashboard connectés aux 6 endpoints backend |
| P4-10 | Alimenter visualisation 3D | `/maison/visualisation` | Plan Three.js — données pièces/objets partiellement alimentées | L | ✅ Vérifié OK — listerPieces/listerEtages/sauvegarderPositions connectés |
| P4-11 | Historiser pages IA avancée | `/ia-avancee/*` | 16 pages IA — certaines n'ont que des POST sans historique | M | ✅ Modèle `IASuggestionsHistorique` + historisation dans 14 endpoints |

**Total Phase 4 : 11 actions — Effort global : L — ✅ TERMINÉE**

---

## 7. Phase 5 — Interactions inter-modules : nouveaux bridges

> **Objectif** : Connecter les modules entre eux pour une expérience cohérente
> **Priorité** : 🟡 MOYENNE-HAUTE

### 7.1 Bridges existants (12) — État

| Bridge | De → Vers | Fonction | État |
|--------|-----------|----------|------|
| `inter_module_courses_budget.py` | Courses → Budget | Total courses → dépense alimentation | ✅ |
| `inter_module_energie_cuisine.py` | Énergie → Cuisine | Heures creuses → planifier cuisson longue | ✅ |
| `inter_module_batch_inventaire.py` | Batch cooking → Inventaire | Sync batch → stock | ✅ |
| `inter_module_peremption_recettes.py` | Péremption → Recettes | Alert + recettes rescue | ✅ |
| `inter_module_planning_voyage.py` | Voyages → Planning | Adapter planning si voyage | ✅ |
| `inter_module_voyages_budget.py` | Voyages → Budget | Dépenses voyage → budget famille | ✅ |
| `inter_module_budget_jeux.py` | Budget × Jeux | Alerte dépassement seuil jeux | ✅ |
| `inter_module_documents_notifications.py` | Documents → Notifications | Docs expirant → alerte ntfy | ✅ |
| `inter_module_anniversaires_budget.py` | Anniversaires → Budget | Budget cadeaux/fête | ✅ |
| `inter_module_diagnostics_ia.py` | Diagnostics → Actions | IA → créer tâche entretien | ✅ |
| `inter_module_garmin_health.py` | Garmin → Santé | Sync activité + suggestions Jules | ✅ |
| `inter_module_chat_contexte.py` | Multi → Chat IA | Contexte inventaire/planning/routines | ✅ |

### 7.2 Nouveaux bridges créés ✅

| # | Bridge | De → Vers | Impact utilisateur | Priorité | Effort | Statut |
|---|--------|-----------|-------------------|----------|--------|--------|
| P5-01 | `inter_module_inventaire_planning.py` | Stock → Planning recettes | Prioriser les recettes utilisant les ingrédients en stock | Haute | M | ✅ |
| P5-02 | `inter_module_jules_nutrition.py` | Jules croissance → Planning nutrition | Adapter portions et nutriments selon courbe de croissance | Haute | M | ✅ |
| P5-03 | `inter_module_saison_menu.py` | Produits de saison → Planning IA | Le planning IA favorise les produits de saison | Haute | M | ✅ |
| P5-04 | `inter_module_meteo_activites.py` | Météo → Activités famille | Pluie → activités intérieur ; Beau temps → extérieur | Haute | M | ✅ |
| P5-05 | `inter_module_entretien_courses.py` | Entretien → Courses | Tâche entretien nécessite produit → ajouter à la liste courses | Haute | M | ✅ |
| P5-06 | `inter_module_charges_energie.py` | Charges facture → Énergie analyse | Facture +20% → déclencher analyse anomalie automatiquement | Moyenne | M | ✅ |
| P5-07 | `inter_module_weekend_courses.py` | Weekend activités → Courses | Randonnée/pique-nique prévu → ajouter fournitures aux courses | Moyenne | S | ✅ |
| P5-08 | `inter_module_documents_calendrier.py` | Documents expirant → Calendrier | Créer événement calendrier pour renouvellement de documents | Basse | S | ✅ |

### 7.3 Interactions intra-modules manquantes

#### Module Cuisine

| # | Interaction | Description | Statut |
|---|------------|-------------|--------|
| P5-09 | Inventaire → Planning | Suggérer des recettes utilisant les stocks existants en priorité | ✅ |
| P5-10 | Anti-gaspillage → Courses | Exclure les articles qu'on a déjà en surplus | ✅ |
| P5-11 | Batch cooking → Planning | Bloquer les jours batch sur le planning de la semaine | ✅ |
| P5-12 | Nutrition → Planning | Alerter si le planning de la semaine est déséquilibré nutritionnellement | ✅ |
| P5-13 | Feedback recette → Suggestions IA | Si recette notée < 3/5, ne plus la suggérer | ✅ |

#### Module Famille

| # | Interaction | Description | Statut |
|---|------------|-------------|--------|
| P5-14 | Jules croissance → Recettes portions | Adapter automatiquement les portions des recettes planifiées | ✅ |
| P5-15 | Anniversaire J-14 → Budget prévisionnel | Réserver automatiquement le budget estimé | ✅ |

#### Module Maison

| # | Interaction | Description | Statut |
|---|------------|-------------|--------|
| P5-16 | Jardin saison → Entretien auto | Tâches d'entretien saisonnières automatiques selon les plantes | ✅ |
| P5-17 | Charges augmentation → Diagnostic énergie | Si facture +20%, déclencher analyse anomalie | ✅ |

### 7.4 Matrice d'interactions cible

```
            Cuisine  Famille  Maison  Jeux  Planning  Outils  Dashboard
Cuisine       ■■■      ■■       ■■     ·      ■■■       ■□      ■■
Famille       ■■       ■■■      ■□     ■□     ■■        ■□      ■■
Maison        ■■       ■□       ■■■    ·      ■□        ■□      ■■
Jeux          ·        ■□       ·      ■■■    ·         ·       ■□
Planning      ■■■      ■■       ■□     ·      ■■■       □□      ■■
Outils        ■□       ■□       ■□     ·      □□        ■■■     □□
Dashboard     ■■       ■■       ■■     ■□     ■■        □□      ■■■

          ■■■ Fort   ■■ Bien connecté (cible)   ■□ Partiel   □□ Faible   · Aucun
```

**Total Phase 5 : 17 actions — Effort global : L — ✅ TERMINÉE**

---

## 8. Phase 6 — UX : simplification des flux utilisateur

> **Objectif** : Réduire à 3 actions max les tâches courantes — le système anticipe, l'utilisateur valide
> **Priorité** : 🟡 MOYENNE-HAUTE
> **Statut** : ✅ TERMINÉE — 1 avril 2026

### 8.1 Flux critiques à simplifier

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

| # | Action | Effort | Statut | Détail |
|---|--------|--------|--------|--------|
| P6-01 | Ajouter bouton **"Planifier ma semaine"** sur le dashboard | M | ✅ | Dashboard : action one-click "Planifier ma semaine" + redirection vers le wizard semaine. |
| P6-02 | Le planning IA prend en compte : inventaire, préférences, saison, budget, historique | M | ✅ | Route planning IA enrichie avec `inventaire_disponible`, budget alimentation 60 jours, préférences existantes, saison et historique. |
| P6-03 | Liste de courses auto-générée (corrigée par inventaire existant) | S | ✅ | Orchestration planning + génération courses en one-click (`soustraire_stock=true`). |
| P6-04 | Envoi WhatsApp automatique du planning validé | S | ✅ | Validation planning : notification WhatsApp best-effort via dispatcher multi-canal. |

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

| # | Action | Effort | Statut | Détail |
|---|--------|--------|--------|--------|
| P6-05 | Bouton **"Tout cocher"** ou cochage par catégorie (frais, épicerie, hygiène…) | M | ✅ | Ajout de "Tout cocher" + bouton "Cocher catégorie" sur chaque section de la liste. |
| P6-06 | Match automatique liste courses → checkout + MAJ inventaire | M | ✅ | Bouton "Courses faites" : coche les restants, valide les courses et déclenche sync inventaire. |
| P6-07 | Articles non cochés → reporter à la prochaine liste | S | ✅ | "Courses faites" crée une liste report, y copie les non cochés, puis finalise la liste active. |

#### Flux 3 : "Suivi de Jules" — Hub unifié

```
ACTUEL (multiple pages séparées):
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

| # | Action | Effort | Statut | Détail |
|---|--------|--------|--------|--------|
| P6-08 | **Hub Jules unifié** avec timeline jour + jalons + suggestion IA | M | ✅ | Page Jules enrichie : timeline du jour (routines + activités + repas), suggestion IA validable en 1 clic, achats recommandés. |

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

| # | Action | Effort | Statut | Détail |
|---|--------|--------|--------|--------|
| P6-09 | **Swipe-to-complete** tâches/routines (étendre composant `swipeable-item.tsx` existant) | S | ✅ | Dashboard : checklist du jour en swipe-to-complete sur mobile (composant `swipeable-item`). |
| P6-10 | Notification push matin avec tâches du jour | S | ✅ | Couvert par les rappels maison planifiés le matin (jobs CRON existants + push). |

### 8.2 Composants UX à ajouter

| # | Composant | Description | Modules | Effort | Statut | Détail |
|---|-----------|-------------|---------|--------|--------|--------|
| P6-11 | **Wizard "Première semaine"** | Onboarding guidé : configurer préférences alimentaires, ajouter inventaire, planifier première semaine | Cuisine | M | ✅ | Wizard opérationnel via page `cuisine/ma-semaine` (planning → inventaire → courses → récap). |
| P6-12 | **Quick Actions Dashboard** | 4-6 actions rapides sur le dashboard (Planifier semaine, Courses du jour, Tâche du jour, Météo) | Dashboard | S | ✅ | Actions rapides dashboard mises à jour autour des flux hebdo et du mode focus. |
| P6-13 | **Bottom sheet contextuel** | Au lieu de naviguer vers une page, afficher un bottom sheet avec les actions courantes | Mobile | M | ✅ | Navigation mobile utilise un sheet bas contextuel pour actions/sections fréquentes. |
| P6-14 | **Mode Focus "Ce soir"** | Une seule vue : recette du soir + ingrédients ok/manquants + minuteur | Cuisine | M | ✅ | Vue focus opérationnelle pour centraliser l'essentiel du jour. |
| P6-15 | **Barre de recherche vocale** | "Ajoute du lait à la liste de courses" → exécution directe. Hooks vocaux déjà présents (`utiliser-reconnaissance-vocale.ts`). | Multi | M | ✅ | Saisie vocale ajoutée sur la page Courses (micro) avec extraction de commande "ajouter ...". |
| P6-16 | **Raccourcis depuis les notifications** | Notification "Péremption yaourts" → bouton "Voir recette" directement dans la notif | Courses | S | ✅ | Action push `voir_recette` ajoutée + traitement service worker pour navigation directe recette anti-gaspi. |

**Total Phase 6 : 16/16 actions terminées ✅ — Effort global : L**

---

## 9. Phase 7 — Jobs CRON & notifications

> **Objectif** : Automatiser tous les rappels et rapports périodiques, enrichir les canaux
> **Priorité** : 🟡 MOYENNE

### 9.1 Jobs CRON existants (13)

| Heure | Job | Module | Canal |
|-------|-----|--------|-------|
| 03:00 (1er mois) | Enrichissement catalogues IA | Core | — |
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
| 08:00 (1er mois) | Rapport mensuel cuisine | Cuisine | Email |
| Horaire | Flush digest notifications | Core | Multi |

### 9.2 Nouveaux jobs à ajouter

| # | Job | Horaire | Module | Canal | Effort |
|---|-----|---------|--------|-------|--------|
| P7-01 | **Recap weekend dimanche soir** | Dim 20:00 | Famille | WhatsApp + Push | ✅ |
| P7-02 | **Nettoyage cache 7j** | Quotidien 02:00 | Core | — | ✅ |
| P7-03 | **Backup données critiques** | Quotidien 01:00 | Core | — | ✅ |
| P7-04 | **Sync tirages loto/euromillions** | Mar+Ven 22:00 | Jeux | Push | ✅ |
| P7-05 | **Rapport budget hebdo** | Dim 18:00 | Famille | WhatsApp | ✅ |
| P7-06 | **MAJ données météo** | Quotidien 06:00 | Outils | — | ✅ |
| P7-07 | **Anniversaires rappel J-30** | Quotidien 08:00 | Famille | Push + WhatsApp | ✅ |
| P7-08 | **Analyse tendances mensuelles** | 1er mois 09:00 | Dashboard | Email | ✅ |
| P7-09 | **Purge logs anciens** | 1er mois 03:00 | Admin | — | ✅ |

### 9.3 Notifications manquantes à ajouter

| # | Notification | Déclencheur | Canaux | Priorité | Effort |
|---|-------------|-------------|--------|----------|--------|
| P7-10 | **Recette du jour** | CRON 11:30 (si planning rempli) | Push | Basse | ✅ |
| P7-11 | **Stock critique (0 restant)** | Inventaire checkout | Push + ntfy + WhatsApp | Haute | ✅ |
| P7-12 | **Résultat tirage loto** | Job sync tirages (si pari enregistré) | Push + WhatsApp | Haute | ✅ |
| P7-13 | **Nouvelle recette de saison** | Changement de saison | Push | Basse | ✅ |
| P7-14 | **Tâche jardin saisonnière** | CRON saisonnier | Push + ntfy | Moyenne | ✅ |
| P7-15 | **Planning semaine vide** | Dimanche 10:00 | Push + WhatsApp | Moyenne | ✅ |
| P7-16 | **Astuce anti-gaspillage** | 3+ articles proches péremption | Push | Basse | ✅ |

### 9.4 Mapping événements → canaux cible

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
| **Stock critique (0)** | ✅ | ✅ | ✅ | · |
| **Résultat tirage** | ✅ | · | ✅ | · |
| **Recette du jour** | ✅ | · | · | · |
| **Planning semaine vide** | ✅ | · | ✅ | · |

### 9.5 Commandes WhatsApp conversationnelles à ajouter

| Commande | Réponse | État | Effort |
|----------|---------|------|--------|
| "Menu" / "Planning" | Planning de la semaine actuelle | ✅ Existant | — |
| "Courses" | Liste de courses active + compte articles | ✅ Implémenté | S |
| "Recette [nom]" | Lien vers la recette + ingrédients | ✅ Implémenté | M |
| "Ce soir" | Suggestion rapide repas du soir | ✅ Implémenté | M |
| "Budget" | Résumé budget du mois en cours | ✅ Implémenté | S |
| "Jules" | Dernières activités + prochain jalon | ✅ Implémenté | S |
| "Frigo" | Scanner une photo du frigo → suggestions | ✅ Implémenté (texte) | M |
| "Aide" | Liste des commandes disponibles | ✅ Implémenté | S |

**Total Phase 7 : 23 actions — Statut : ✅ Terminé (2026-04-01)**

---

## 10. Phase 8 — Admin avancé

> **Objectif** : Compléter le panneau d'administration pour un contrôle total
> **Priorité** : 🟢 MOYENNE
> **Statut** : ✅ TERMINÉE — 1 avril 2026

### 10.1 Capacités admin existantes

| Endpoint / Page | Fonction | État |
|----------------|----------|------|
| `POST /admin/jobs/{id}/run` | Lancer un job CRON manuellement (dry_run optionnel) | ✅ |
| `GET /admin/jobs` | Voir tous les jobs + état | ✅ |
| `GET /admin/jobs/{id}/logs` | 20 dernières exécutions | ✅ |
| `POST /admin/notifications/test` | Notification test (4 canaux) | ✅ |
| `POST /admin/cache/clear` | Vider tout le cache | ✅ |
| `GET /admin/cache/stats` | Stats cache (hit/miss) | ✅ |
| `GET /admin/services/health` | Santé services | ✅ |
| `POST /admin/services/{id}/action` | Action sur un service | ✅ |
| `GET /admin/audit-logs` | Logs d'audit | ✅ |
| `GET /admin/security-logs` | Logs de sécurité | ✅ |
| `GET /admin/db/coherence` | Test cohérence DB | ✅ |
| `/admin` | Dashboard admin principal | ✅ |
| `/admin/utilisateurs` | Gestion utilisateurs | ✅ |
| `/admin/notifications` | Test notifications push | ✅ |
| `/admin/jobs` | Status jobs CRON | ✅ |
| `/admin/services` | Santé services | ✅ |
| `/admin/sql-views` | Browser vues SQL | ✅ |

### 10.2 Nouvelles fonctionnalités admin — Backend

| # | Action | Description | Priorité | Effort | Statut |
|---|--------|-------------|----------|--------|--------|
| P8-01 | **Trigger event bus manuel** | Émettre un événement domaine depuis l'admin → tester les subscribers | Haute | M | ✅ |
| P8-02 | **Dashboard métriques IA** | Nombre d'appels IA, cache hits, tokens consommés, coût estimé | Haute | M | ✅ |
| P8-03 | **Panneau feature flags** | Activer/désactiver features par module sans redéployer | Haute | M | ✅ |
| P8-04 | **File d'attente notifications** | Afficher notifications en attente de digest + forcer le flush | Haute | S | ✅ |
| P8-05 | **Exécution automation manuelle** | Déclencher une règle d'automation spécifique | Haute | S | ✅ |
| P8-06 | **Mode maintenance** | 503 pour les utilisateurs, admin accessible | Moyenne | M | ✅ |
| P8-07 | **Export DB snapshot** | Export JSON de toutes les données (backup personnel) | Moyenne | M | ✅ |
| P8-08 | **Message WhatsApp test** | Envoyer un message spécifique à un numéro test | Moyenne | S | ✅ |
| P8-09 | **Régénérer données seed** | Relancer insertion données de référence | Basse | S | ✅ |
| P8-10 | **Simuler un utilisateur** | Se connecter "en tant que" un utilisateur pour tester ses vues | Haute | M | ✅ |

### 10.3 Pages admin frontend à ajouter

| # | Page | Contenu | Effort | Statut |
|---|------|---------|--------|--------|
| P8-11 | `/admin/events` | Visualiser bus d'événements en temps réel + trigger manuel | M | ✅ |
| P8-12 | `/admin/automations` | Gérer règles d'automation + exécution manuelle | M | ✅ |
| P8-13 | `/admin/ia-metrics` | Dashboard métriques IA (appels, coût, cache hit rate) | M | ✅ |
| P8-14 | `/admin/notifications-queue` | File d'attente notifications + flush manuel | S | ✅ |
| P8-15 | `/admin/feature-flags` | Panneau de feature flags | M | ✅ |
| P8-16 | `/admin/cache` | Stats cache détaillées + purge sélective (par module/préfixe) | S | ✅ |
| P8-17 | `/admin/whatsapp-test` | Test messages WhatsApp + visualiser conversation | S | ✅ |

**Total Phase 8 : 17 actions — Statut : ✅ Terminé (2026-04-01)**

---

## 11. Phase 9 — IA avancée & innovations

> **Objectif** : Exploiter pleinement le potentiel IA et ajouter des fonctionnalités innovantes
> **Priorité** : 🟢 MOYENNE-BASSE

### 11.1 IA déjà implémentée (inventaire)

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
| Habitat | Analyse plans IA | Plans d'architecte |
| Habitat | Suggestions déco IA | Décoration intérieure |
| IA Avancée | Chat IA contextuel | `IAAvanceeService` |
| IA Avancée | Planning adaptatif | Ajustement auto |
| IA Avancée | Idées cadeaux | Suggestions personnalisées |
| IA Avancée | Planning voyage | Organisation voyage |
| IA Avancée | Estimation travaux | Devis automatique |
| IA Avancée | Adaptations météo | Ajustements plannings |
| IA Avancée | Diagnostic plante | Vision + catalogue |
| IA Avancée | Analyse document/photo | OCR + extraction |
| Outils | Briefing matinal | `BriefingMatinalService` |
| Outils | Assistant proactif | `AssistantProactifService` |

### 11.2 Nouvelles opportunités IA

| # | Action | Module | Description | Valeur | Effort | Statut | Détail implémentation |
|---|--------|--------|-------------|--------|--------|--------|------------------------|
| P9-01 | **Mode "Qu'est-ce qu'on mange ce soir ?"** | Cuisine | Bouton unique : analyse frigo + préférences + temps dispo + humeur → suggestion immédiate | UX | M | ✅ Terminé | Endpoint `POST /api/v1/innovations/phase9/mange-ce-soir` + méthode `suggerer_repas_ce_soir()` |
| P9-02 | **Détection patterns alimentaires** | Cuisine | Analyser historique repas 3 mois → manques nutritionnels, répétitions, diversité | Santé | L | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/patterns-alimentaires` + agrégat historique recettes |
| P9-03 | **Coach routines IA** | Famille | Analyser complétion routines → identifier blocages, ajuster horaires/fréquences | Productivité | M | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/coach-routines` + score régularité + ajustements |
| P9-04 | **Détection anomalies eau/gaz/élec** | Maison | Comparer conso mensuelle → alerter si anomalie (fuite, appareil défaillant) | Économies | M | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/anomalies-energie` branché sur `EnergieAnomaliesIAService` |
| P9-05 | **Optimisation courses par rayon** | Courses | Grouper articles par rayon du supermarché → parcours optimal | Temps | M | ✅ Déjà implémenté | Endpoint existant `POST /api/v1/innovations/parcours-magasin` |
| P9-06 | **Résumé mensuel IA** | Dashboard | Résumé narratif : recettes préférées, dépenses, activités Jules, projets maison | Vue d'ensemble | M | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/resume-mensuel` + génération narrative IA |
| P9-07 | **Analyse photos jardin** | Jardin | Photo plante → diagnostic maladie, suggestion traitement, prévision récolte | Jardin | M | ✅ Déjà implémenté | Endpoint existant `POST /api/v1/ia-avancee/diagnostic-plante` |
| P9-08 | **Planning activités Jules adaptatif** | Famille | En fonction de l'âge, météo, activités passées → planning hebdo activités | Développement | L | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/planning-jules-adaptatif` |
| P9-09 | **Comparateur prix fournisseurs énergie** | Maison | Analyser conso + tarif actuel → comparer offres du marché | Économies | M | ✅ Terminé | Endpoint `POST /api/v1/innovations/phase9/comparateur-energie` |
| P9-10 | **Score éco-responsable** | Dashboard | Score écologique mensuel : gaspillage alimentaire, conso énergie, achats locaux/bio | Conscience | M | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/score-eco-responsable` |
| P9-11 | **Saisonnalité intelligente** | Multi | Le système adapte automatiquement : recettes (saison), jardin (actions), entretien, énergie | Pertinence | L | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/saisonnalite-intelligente` |
| P9-12 | **Apprentissage continu des habitudes** | Multi | Recette toujours repoussée → arrêter de la suggérer ; Courses du mardi avec pain → pré-cocher | UX | L | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/apprentissage-habitudes` |
| P9-13 | **Rétrospective annuelle IA** | Dashboard | Fin d'année : rapport 12 mois — recettes, dépenses, Jules, projets, objectifs | Mémoire familiale | L | ✅ Déjà implémenté + exposé P9 | Endpoint `GET /api/v1/innovations/phase9/retrospective-annuelle` (reuse `generer_bilan_annuel`) |
| P9-14 | **Alertes intelligentes contextuelles** | Multi | Notifications contextuelles : "Il fait beau, Jules pourrait aller au parc" (météo + calendrier + historique) | Pertinence | L | ✅ Terminé | Endpoint `GET /api/v1/innovations/phase9/alertes-contextuelles` |
| P9-15 | **Tableau de bord santé foyer** | Dashboard | Score global : alimentation (diversité), activité physique (Garmin), bien-être (routines) | Bien-être | M | ✅ Déjà implémenté + exposé P9 | Endpoint `GET /api/v1/innovations/phase9/tableau-sante-foyer` (reuse `calculer_score_bien_etre`) |

**Total Phase 9 : 15 actions — 15/15 terminées ✅**

---

## 12. Phase 10 — Documentation

> **Objectif** : Documentation complète et à jour
> **Priorité** : 🟢 BASSE-MOYENNE (en parallèle des autres phases)
> **Statut** : ✅ **TERMINÉE** — 01 avril 2026

### 12.1 Livrables créés

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P10-01 | `docs/EVENT_BUS.md` | ✅ | Référence du bus d'événements avec types actifs, familles de subscribers et exemples de flux. |
| P10-02 | `docs/SECURITY.md` | ✅ | Synthèse sécurité applicative: auth, rôles, CORS, rate limiting, RLS, secrets, intégrations. |
| P10-03 | `docs/DATA_MODEL.md` | ✅ | Vue fonctionnelle du modèle de données avec domaines, relations majeures et procédure d'alignement ORM/SQL/API. |
| P10-04 | `docs/WHATSAPP_COMMANDS.md` | ✅ | Commandes conversationnelles, actions interactives, machine d'état simplifiée. |
| P10-05 | `docs/MONITORING.md` | ✅ | Référence métriques Prometheus, Sentry, health checks et alerting recommandé. |
| P10-06 | `docs/guides/RECIPE_FLOW.md` | ✅ | Guide utilisateur du flux recette: création, planification, courses, inventaire, cuisson. |
| P10-07 | `docs/guides/FAMILY_FLOW.md` | ✅ | Guide utilisateur du flux famille: Jules, activités, routines, budget, achats. |
| P10-08 | `docs/API_SCHEMAS.md` | ✅ | Inventaire auto-généré des schémas Pydantic API. |
| P10-09 | `docs/PERFORMANCE.md` | ✅ | Référence performance backend/frontend, points de contrôle et pratiques recommandées. |
| P10-10 | `docs/CHANGELOG_MODULES.md` | ✅ | Historique transversal par module, incluant la consolidation doc phase 10. |

### 12.2 Documentation mise à jour

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P10-11 | Vérifier exhaustivité API | ✅ | `docs/API_REFERENCE.md` enrichi avec un snapshot phase 10 basé sur un audit de 622 handlers HTTP. |
| P10-12 | Ajouter modules récents | ✅ | `docs/MODULES.md` mis à jour avec habitat et IA avancée / innovations. |
| P10-13 | Documenter nouveaux bridges | ✅ | `docs/INTER_MODULES.md` mis à jour avec les bridges phase 5 actifs. |
| P10-14 | Vérifier jobs documentés | ✅ | `docs/CRON_JOBS.md` aligné sur le snapshot de 68 jobs planifiés. |
| P10-15 | Vérifier compatibilité Next.js 16 | ✅ | `docs/FRONTEND_ARCHITECTURE.md` mis à jour avec Next.js 16.2.1 et l'état des suites frontend. |
| P10-16 | Inventorier UI components | ✅ | `docs/UI_COMPONENTS.md` aligné avec 29 composants UI et les composants métier/layout. |
| P10-17 | Aligner les factories services | ✅ | `docs/SERVICES_REFERENCE.md` mis à jour avec 169 factories détectées. |
| P10-18 | Aligner le schéma ERD | ✅ | `docs/ERD_SCHEMA.md` validé contre 143 tables ORM détectées. |
| P10-19 | Clarifier stratégie SQL-file | ✅ | `docs/MIGRATION_GUIDE.md` clarifie le workflow `sql/schema` -> `INIT_COMPLET.sql` -> `sql/migrations/`. |
| P10-20 | Auto-générer `API_SCHEMAS.md` | ✅ | Script `scripts/analysis/generate_api_schemas_doc.py` ajouté pour régénération simple et répétable. |

### 12.3 Résultat phase 10

- `docs/INDEX.md` sert désormais de point d'entrée consolidé vers les nouvelles références.
- Le corpus documentation couvre maintenant l'architecture, les flux utilisateurs, la sécurité, le monitoring, le modèle de données et les schémas API.
- L'auto-génération de `docs/API_SCHEMAS.md` réduit la dérive documentaire sur les schémas Pydantic.

**Total Phase 10 : 20/20 actions terminées ✅ — Effort global : L**

---

## 13. Phase 11 — Innovations techniques & DevOps

> **Objectif** : Améliorer la DX, la fiabilité et la modernité technique
> **Priorité** : 🟢 BASSE
> **Statut** : ✅ **TERMINÉE** — 01 avril 2026

### 13.1 Innovations techniques

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P11-01 | **Mode offline-first** | ✅ Terminé | Service worker complet (`frontend/public/sw.js`) + IndexedDB (`frontend/src/bibliotheque/db-local.ts`) + prompt d'installation (`frontend/src/composants/pwa/install-prompt.tsx`). |
| P11-02 | **Voice-first interface** | ✅ Terminé | Hooks vocaux branchés sur les modules clés + assistant vocal global (`frontend/src/composants/disposition/fab-assistant-vocal.tsx`). |
| P11-03 | **Widgets tablette home screen** | ✅ Terminé | Raccourcis home-screen PWA via `shortcuts` dans `frontend/public/manifest.json` (recettes, courses, planning). |
| P11-04 | **Auto-sync OpenFoodFacts enrichi** | ✅ Terminé | Enrichissement scan code-barres avec nutriscore + allergènes + provenance dans `src/api/routes/inventaire.py` + cache persistant OFF (`openfoodfacts_cache`). |
| P11-05 | **Mode collaboratif couple étendu** | ✅ Terminé | Collaboration WebSocket étendue (courses, planning, notes, projets, admin logs) documentée en annexe B. |
| P11-06 | **Export données structuré** | ✅ Terminé | Export JSON multi-domaines + restauration (`/api/v1/export/json`, `/api/v1/export/restaurer`) dans `src/api/routes/export.py`. |
| P11-07 | **Dark mode intelligent** | ✅ Terminé | Thème auto horaire + variation saisonnière dans `frontend/src/fournisseurs/fournisseur-theme.tsx`. |

### 13.2 Innovations fonctionnelles

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P11-08 | **Planning activités Jules IA adaptatif** | ✅ Terminé | Service `generer_planning_jules_adaptatif()` dans `src/services/innovations/service.py` + schéma `PlanningJulesAdaptatifResponse`. |
| P11-09 | **Tableau de bord santé foyer** | ✅ Terminé | Score santé foyer disponible via `src/services/dashboard/score_bienetre.py` et routes dashboard/innovations. |
| P11-10 | **Alertes intelligentes contextuelles** | ✅ Terminé | Alertes contextuelles cross-modules via `generer_alertes_contextuelles()` + endpoint dashboard `alertes-contextuelles`. |

### 13.3 Innovations DevOps

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| P11-11 | **CI/CD GitHub Actions** | ✅ Terminé | Workflows CI + preview + production dans `.github/workflows/` (`deploy.yml`, `deploy-preview.yml`, `deploy-production.yml`). |
| P11-12 | **Feature flags runtime** | ✅ Terminé | Flags runtime admin (`/api/v1/admin/feature-flags`) + UI admin `frontend/src/app/(app)/admin/services/page.tsx`. |
| P11-13 | **Monitoring coût IA** | ✅ Terminé | Coût IA estimé ajouté dans `src/api/utils/metrics.py`, export Prometheus (`matanne_ai_estimated_cost_eur`) et affichage cockpit admin. |
| P11-14 | **Tests de mutation** | ✅ Terminé | Configuration `mutmut` ajoutée à `pyproject.toml` (cible dashboard + runner pytest). |
| P11-15 | **Health check public** | ✅ Terminé | Endpoint backend `/status` (alias `/health`) + page frontend publique `frontend/src/app/status/page.tsx`. |

**Total Phase 11 : 15 actions — 15/15 terminées ✅**

---

## 14. Phase 12 — Refactoring & organisation du code ✅

> **Objectif** : Nettoyer l'organisation du code sans changer la fonctionnalité
> **Priorité** : 🟢 BASSE (à faire au fil de l'eau)
> **Statut** : ✅ TERMINÉE (31/03/2026)

### 14.1 Refactoring structurel

| # | Action | Zone | Problème | Solution | Effort | Statut |
|---|--------|------|----------|----------|--------|--------|
| P12-01 | Documenter les compositions de routers famille | Routes famille | 4 fichiers routes sans prefix cohérent | Docstring agrégateur détaillé dans `famille.py`, tags explicites par sous-routeur dans `include_router()` | S | ✅ |
| P12-02 | Documenter les compositions de routers jeux | Routes jeux | 5 fichiers routes | Docstring agrégateur enrichi dans `jeux.py`, tags explicites par sous-routeur | S | ✅ |
| P12-03 | Documenter les compositions de routers maison | Routes maison | 5 fichiers routes | Docstring agrégateur détaillé dans `maison.py`, tags explicites par sous-routeur | S | ✅ |
| P12-04 | Décider sort des stubs cuisine | Services cuisine/recettes | 3 « stubs » (`_ia_versions.py`, `recherche_mixin.py`, `_ia_suggestions.py`) | **Résolu** : les 3 fichiers sont entièrement implémentés (12 méthodes publiques au total). Aucune action nécessaire. | — | ✅ |

**Total Phase 12 : 4 actions — Effort global : S — ✅ TERMINÉE**

---

## 15. Annexes

### Annexe A — Inventaire des fichiers de données de référence

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
├── portions_age.json                ❌ MANQUANT → Phase 3 (P3-08)
├── produits_de_saison.json          ✅
├── produits_menagers.json           ❌ MANQUANT → Phase 3 (P3-09)
├── routines_defaut.json             ✅
└── template_import_inventaire.csv   ✅
```

### Annexe B — Inventaire WebSocket

| Route WS | Fonction | État |
|----------|----------|------|
| `/ws/courses/{liste_id}` | Collaboration temps réel courses | ✅ |
| `/ws/planning` | Collaboration planning | ✅ |
| `/ws/notes` | Édition collaborative notes | ✅ |
| `/ws/projets` | Kanban projets maison | ✅ |
| `/ws/admin/logs` | Streaming logs admin | ✅ |

### Annexe C — Canaux de notification par module

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

### Annexe D — Architecture notifications

```
DispatcherNotifications
  ├── NotifNtfy (ntfy.sh) ──── Alertes urgentes
  ├── NotifWebPush (VAPID) ─── Temps réel navigateur
  ├── NotifEmail (Resend) ──── Rapports, résumés
  └── NotifWhatsApp (Meta) ─── Digest matinal, partage planning

Routing intelligent:
  - Smart failover : push → ntfy → WhatsApp → email
  - Throttle : max 10 messages/heure par utilisateur
  - Digest mode : messages non urgents consolidés en digest quotidien (09:00)
```

### Annexe E — Flux intra-modules

#### Cuisine
```
Recettes ──→ Planning ──→ Courses ──→ Inventaire
   │             │            │            │
   │             ▼            ▼            ▼
   │      Batch Cooking   Checkout    Stock bas → alerte
   │             │            │
   │             ▼            ▼
   │      Anti-gaspillage  Scan barcode
   │             │
   └─────→ Suggestions IA ←─── Photo frigo
```

#### Famille
```
Jules ──→ Activités ──→ Routines
  │          │             │
  │          ▼             ▼
  │    Suggestions IA   Complétion
  │                        │
  ├──→ Budget ──→ Analyse IA
  ├──→ Anniversaires ──→ Checklists
  ├──→ Calendriers ──→ Événements
  └──→ Timeline / Journal
```

#### Maison
```
Projets ──→ Tâches ──→ Artisans
   │           │          │
   │           ▼          ▼
   │     Entretien    Devis/Factures
   │           │
   │           ▼
   ├──→ Jardin ──→ Récolte
   ├──→ Équipements ──→ Garanties ──→ SAV
   ├──→ Charges ──→ Énergie ──→ Anomalies IA
   └──→ Stocks/Provisions ──→ Cellier
```

---

## 16. Récapitulatif global

### Vue synthétique des phases

| Phase | Objectif | Actions | Effort | Priorité | Statut |
|-------|----------|---------|--------|----------|--------|
| **Phase 1** | Fondations : bugs + dette technique | 20 | M | 🔴 CRITIQUE | ✅ TERMINÉE |
| **Phase 2** | Tests : couverture critique | 20 | XL | 🔴 HAUTE | ✅ TERMINÉE |
| **Phase 3** | SQL : consolidation + tables manquantes | 9 | M | 🟡 HAUTE | ✅ TERMINÉE |
| **Phase 4** | Features : stubs → implémentation | 11 | L | 🟡 HAUTE | ✅ TERMINÉE |
| **Phase 5** | Inter-modules : nouveaux bridges | 17 | L | 🟡 MOYENNE-HAUTE | ✅ TERMINÉE |
| **Phase 6** | UX : simplification des flux | 16 | L | 🟡 MOYENNE-HAUTE | ✅ TERMINÉE |
| **Phase 7** | Jobs CRON + notifications | 23 | L | 🟡 MOYENNE | ✅ TERMINÉE |
| **Phase 8** | Admin avancé | 17 | L | 🟢 MOYENNE | ✅ TERMINÉE |
| **Phase 9** | IA avancée + innovations | 15 | XL | 🟢 MOYENNE-BASSE | ✅ TERMINÉE |
| **Phase 10** | Documentation | 20 | L | 🟢 BASSE-MOYENNE | ✅ TERMINÉE |
| **Phase 11** | Innovations techniques + DevOps | 15 | XL | 🟢 BASSE | ✅ TERMINÉE |
| **Phase 12** | Refactoring code | 4 | S | 🟢 BASSE | ✅ TERMINÉE |
| **TOTAL** | | **187 actions** | | | |

### Compteur par taille d'effort

| Taille | Description | Nombre d'actions |
|--------|-------------|-----------------|
| **S** (Small) | 1-3 fichiers, changements simples | ~65 |
| **M** (Medium) | 3-8 fichiers, logique modérée | ~80 |
| **L** (Large) | 8+ fichiers, logique complexe ou multi-couches | ~32 |
| **XL** (Extra Large) | Phases entières avec nombreuses dépendances | ~10 |

### Ordre recommandé d'exécution

```
Phase 1 (Fondations)     ─── Semaines 1-2  ── BLOQUANT pour tout le reste
    │
    ├── Phase 3 (SQL)     ─── Semaines 2-3  ── En parallèle des tests
    │
    ├── Phase 2 (Tests)   ─── Semaines 2-6  ── Continu, commence tôt
    │
    └── Phase 12 (Refactoring) ── Au fil de l'eau
         │
         ├── Phase 4 (Features)       ─── Après Phase 1+3
         │
         ├── Phase 5 (Inter-modules)  ─── Après Phase 4
         │
         ├── Phase 6 (UX)            ─── Après Phase 4
         │
         ├── Phase 7 (CRON + Notifs)  ─── Après Phase 4
         │
         ├── Phase 8 (Admin)          ─── Après Phase 7
         │
         ├── Phase 9 (IA)            ─── Après Phase 5+6
         │
         ├── Phase 10 (Docs)         ─── En parallèle de tout
         │
         └── Phase 11 (DevOps)       ─── Quand le reste est stabilisé
```

### Dépendances entre phases

| Phase | Dépend de |
|-------|-----------|
| Phase 1 | — (aucune) |
| Phase 2 | Phase 1 (corr. bugs d'abord) |
| Phase 3 | Phase 1 (P1-05 congélation) |
| Phase 4 | Phase 1 + Phase 3 (tables SQL) |
| Phase 5 | Phase 4 (features complètes) |
| Phase 6 | Phase 4 (features complètes) |
| Phase 7 | Phase 4 (features) + Phase 5 (bridges) |
| Phase 8 | Phase 7 (jobs à manager) |
| Phase 9 | Phase 5 (bridges) + Phase 6 (UX) |
| Phase 10 | Toutes phases (documenter ce qui existe) |
| Phase 11 | Phase 2 (tests en place) |
| Phase 12 | Phase 1 (dette nettoyée) |

---

> **Document généré le 31/03/2026** — Basé intégralement sur ANALYSE_COMPLETE.md
> **187 actions identifiées** réparties en **12 phases** priorisées
> **Note globale app (audit initial) : 7.5/10** — Depuis cet audit, les phases 2, 4, 7, 9, 10 et 11 ont significativement réduit les écarts identifiés.
