# Planning d'Implémentation — Assistant Matanne

> **Date** : 1er Avril 2026
> **Source** : ANALYSE_COMPLETE.md — Audit exhaustif intégral (19 sections)
> **Objectif** : Roadmap complète couvrant **tous** les constats de l'analyse : bugs, gaps, SQL, interactions intra/inter-modules, IA, CRON, notifications, admin, tests, docs, UX, visualisations 2D/3D, flux utilisateur, et innovations

---

## Table des matières

- [Planning d'Implémentation — Assistant Matanne](#planning-dimplémentation--assistant-matanne)
  - [Table des matières](#table-des-matières)
  - [1. Notation par catégorie](#1-notation-par-catégorie)
    - [Note globale : **7.5/10**](#note-globale--7510)
  - [2. État des lieux synthétique](#2-état-des-lieux-synthétique)
    - [Chiffres clés](#chiffres-clés)
    - [Stack technique](#stack-technique)
    - [Modules par domaine](#modules-par-domaine)
    - [Frontend — Pages par module](#frontend--pages-par-module)
  - [3. Phase A — Stabilisation](#3-phase-a--stabilisation)
  - [4. Phase B — Fonctionnalités \& IA](#4-phase-b--fonctionnalités--ia)
  - [5. Phase C — UI/UX \& Visualisations](#5-phase-c--uiux--visualisations)
  - [6. Phase D — Admin \& Automatisations](#6-phase-d--admin--automatisations)
  - [7. Phase E — Innovations](#7-phase-e--innovations)
  - [8. Référentiel complet par section d'analyse](#8-référentiel-complet-par-section-danalyse)
    - [8.1 Bugs et problèmes détectés (analyse §3)](#81-bugs-et-problèmes-détectés-analyse-3)
      - [🔴 Critiques (4)](#-critiques-4)
      - [🟡 Importants (6)](#-importants-6)
      - [🟢 Mineurs (4)](#-mineurs-4)
    - [8.2 Gaps et fonctionnalités manquantes (analyse §4)](#82-gaps-et-fonctionnalités-manquantes-analyse-4)
      - [🍽️ Cuisine (5 gaps)](#️-cuisine-5-gaps)
      - [👶 Famille (4 gaps)](#-famille-4-gaps)
      - [🏡 Maison (4 gaps)](#-maison-4-gaps)
      - [🎮 Jeux (3 gaps)](#-jeux-3-gaps)
      - [📅 Planning (3 gaps)](#-planning-3-gaps)
      - [🧰 Général (4 gaps)](#-général-4-gaps)
    - [8.3 Consolidation SQL (analyse §5)](#83-consolidation-sql-analyse-5)
      - [Structure actuelle](#structure-actuelle)
      - [Actions](#actions)
      - [Workflow simplifié cible](#workflow-simplifié-cible)
    - [8.4 Interactions intra-modules (analyse §6)](#84-interactions-intra-modules-analyse-6)
      - [Cuisine (interne) — ✅ Bien connecté](#cuisine-interne---bien-connecté)
      - [Famille (interne) — 🔧 Améliorable](#famille-interne---améliorable)
      - [Maison (interne) — 🔧 Améliorable](#maison-interne---améliorable)
    - [8.5 Interactions inter-modules (analyse §7)](#85-interactions-inter-modules-analyse-7)
      - [21 bridges existants ✅](#21-bridges-existants-)
      - [10 nouvelles interactions à implémenter](#10-nouvelles-interactions-à-implémenter)
    - [8.6 Opportunités IA (analyse §8)](#86-opportunités-ia-analyse-8)
      - [IA déjà en place (9 fonctionnels)](#ia-déjà-en-place-9-fonctionnels)
      - [12 nouvelles opportunités](#12-nouvelles-opportunités)
    - [8.7 Jobs automatiques CRON (analyse §9)](#87-jobs-automatiques-cron-analyse-9)
      - [68+ jobs existants — Résumé](#68-jobs-existants--résumé)
      - [10 nouveaux jobs proposés](#10-nouveaux-jobs-proposés)
    - [8.8 Notifications (analyse §10)](#88-notifications-analyse-10)
      - [Architecture](#architecture)
      - [Améliorations WhatsApp](#améliorations-whatsapp)
      - [Améliorations Email](#améliorations-email)
      - [Améliorations Push](#améliorations-push)
    - [8.9 Mode Admin (analyse §11)](#89-mode-admin-analyse-11)
      - [Existant — ✅ Très complet](#existant---très-complet)
      - [Améliorations](#améliorations)
    - [8.10 Couverture de tests (analyse §12)](#810-couverture-de-tests-analyse-12)
      - [Backend — ~55% couverture](#backend--55-couverture)
      - [Frontend — ~40% couverture](#frontend--40-couverture)
      - [Tests manquants prioritaires](#tests-manquants-prioritaires)
    - [8.11 Documentation (analyse §13)](#811-documentation-analyse-13)
      - [État](#état)
      - [Documentation à créer](#documentation-à-créer)
    - [8.12 Organisation \& architecture (analyse §14)](#812-organisation--architecture-analyse-14)
      - [Points forts ✅](#points-forts-)
      - [Points à améliorer](#points-à-améliorer)
    - [8.13 Améliorations UI/UX (analyse §15)](#813-améliorations-uiux-analyse-15)
      - [Dashboard](#dashboard)
      - [Navigation](#navigation)
      - [Formulaires](#formulaires)
      - [Mobile](#mobile)
      - [Micro-interactions](#micro-interactions)
    - [8.14 Visualisations 2D/3D (analyse §16)](#814-visualisations-2d3d-analyse-16)
      - [Existant](#existant)
      - [Nouvelles visualisations](#nouvelles-visualisations)
    - [8.15 Simplification flux utilisateur (analyse §17)](#815-simplification-flux-utilisateur-analyse-17)
      - [🍽️ Flux cuisine (central)](#️-flux-cuisine-central)
      - [👶 Flux famille quotidien](#-flux-famille-quotidien)
      - [🏡 Flux maison](#-flux-maison)
      - [Actions rapides FAB mobile](#actions-rapides-fab-mobile)
    - [8.16 Axes d'innovation (analyse §18)](#816-axes-dinnovation-analyse-18)
  - [9. Annexes](#9-annexes)
    - [Annexe A — Arborescence fichiers clés](#annexe-a--arborescence-fichiers-clés)
      - [Backend Python](#backend-python)
      - [Frontend Next.js](#frontend-nextjs)
      - [SQL](#sql)
    - [Annexe B — WebSockets](#annexe-b--websockets)
    - [Annexe C — Données de référence](#annexe-c--données-de-référence)
    - [Annexe D — Canaux de notification par événement](#annexe-d--canaux-de-notification-par-événement)
  - [10. Récapitulatif global \& métriques de santé](#10-récapitulatif-global--métriques-de-santé)
    - [Vue synthétique des phases](#vue-synthétique-des-phases)
    - [Dépendances](#dépendances)
    - [Métriques de santé projet](#métriques-de-santé-projet)
    - [Comptage total par catégorie](#comptage-total-par-catégorie)

---

## 1. Notation par catégorie

> Évaluation au 1er avril 2026 — basée sur l'audit exhaustif

| Catégorie | Note | Justification |
|-----------|------|---------------|
| **Architecture backend** | **9/10** | FastAPI + SQLAlchemy 2.0 + Pydantic v2. Patterns exemplaires : service registry `@service_factory`, event bus pub/sub (21 types, 40+ subscribers), cache multi-niveaux (L1/L2/L3/Redis), résilience composable (retry, timeout, circuit breaker, bulkhead). 38 routeurs, ~250 endpoints, 7 middlewares. |
| **Architecture frontend** | **8/10** | Next.js 16 App Router, React 19, Zustand 5, TanStack Query v5, ~60+ pages, 208+ composants (29 shadcn/ui), 34 clients API, 15 hooks custom. Points négatifs : couverture tests ~40%, doubles bibliothèques charts (Recharts + Chart.js). |
| **Base de données / SQL** | **8/10** | 80+ tables PostgreSQL, RLS, triggers, vues, 18 fichiers schema ordonnés. Points négatifs : 7 migrations non consolidées dans les fichiers schema, audit ORM↔SQL non exécuté, index potentiellement manquants. |
| **Couverture tests backend** | **6.5/10** | 74+ fichiers, ~1000 fonctions test, ~55% couverture estimée. Bien couvert : routes cuisine, services budget, rate limiting. Faible : export PDF (~30%), webhooks (~25%), event bus (~20%), WebSocket (~25%), intégrations (~20%). |
| **Couverture tests frontend** | **4.5/10** | 71 fichiers tests, ~40% couverture. Bien couvert : pages cuisine, stores Zustand. Faible : pages famille/maison/admin (~30%), API clients (~15%), E2E Playwright (~10%). Seuil Vitest 50% → non atteint. |
| **Intégration IA** | **8.5/10** | Client Mistral unifié + cache sémantique + circuit breaker. 9 services IA fonctionnels (suggestions, planning, rescue, batch, weekend, bien-être, chat, jules, IA avancée partielle). 12 nouvelles opportunités IA identifiées. |
| **Système de notifications** | **8/10** | 4 canaux (push VAPID, ntfy.sh, WhatsApp Meta, email Resend), failover intelligent, throttle 2h/type/canal. Points négatifs : WhatsApp state non persisté (B9), commandes texte limitées, pas d'actions dans les push. |
| **Interactions inter-modules** | **8/10** | 21 bridges actifs bien pensés. 10 nouvelles interactions identifiées dont 3 haute priorité (récolte→recettes, budget→notifications, documents→dashboard). |
| **UX / Flux utilisateur** | **5.5/10** | Pages fonctionnelles mais flux courants en 4-6 clics au lieu de 3 max. Pas de drag-drop planning, pas de mode offline courses, pas d'auto-complétion historique, transitions de page absentes. FAB actions rapides et swipe-to-complete existants mais sous-exploités. |
| **Visualisations** | **5/10** | Base présente (Recharts heatmaps, camemberts, graphiques ROI, Leaflet cartes). Plan 3D maison (Three.js) non connecté aux données. Manquent : heatmap nutrition, treemap budget, radar Jules, sparklines dashboard, Gantt entretien. |
| **Documentation** | **6/10** | ~60% à jour (35/58 fichiers estimés). CRON_JOBS.md, NOTIFICATIONS.md, AUTOMATIONS.md obsolètes post-phases 8-10. PLANNING_IMPLEMENTATION.md et ROADMAP.md périmés. Docs manquantes : guide CRON complet, guide notifications refonte, guide bridges. |
| **Administration** | **9/10** | Panneau admin très complet : 10 pages frontend, 20+ endpoints, raccourci Ctrl+Shift+A, event bus manuel, feature flags, impersonation, dry-run workflows, IA console, WhatsApp test, export/import config. Améliorations possibles : console commande rapide, scheduler visuel, replay événements. |
| **Jobs CRON** | **7.5/10** | 68+ jobs bien structurés (quotidiens, hebdo, mensuels). Points négatifs : fichier `jobs.py` monolithique (3500+ lignes), ~30% testés, 10 nouveaux jobs proposés (prédiction courses, planning auto, alertes budget). |
| **Infrastructure / DevOps** | **7/10** | Docker, Sentry (50%), Prometheus metrics. Points négatifs : pas de CI/CD GitHub Actions, pas de monitoring coût IA, Sentry pas complet. |
| **Sécurité** | **7/10** | JWT + 2FA TOTP, RLS, rate limiting multi-strategy, security headers, sanitization. Points négatifs : B1 (API_SECRET_KEY random par process en multi-worker), B7 (X-Forwarded-For spoofable), B10 (CORS vide en prod sans erreur). |
| **Performance & résilience** | **8.5/10** | Cache multi-niveaux (L1→L2→L3→Redis), middleware ETag, résilience composable, rate limiting (60 req/min standard, 10 req/min IA). Metrics capped à 500 endpoints (B8). |
| **Données de référence** | **9/10** | 14+ fichiers JSON/CSV couvrant nutrition, saisons, entretien, jardin, vaccins, soldes, pannes, lessive, nettoyage, domotique, travaux, plantes, routines. |

### Note globale : **7.5/10**

> Application ambitieuse et impressionnante : ~250 endpoints, 80+ tables SQL, ~60+ pages, 208+ composants, 68+ CRON jobs, 21 bridges inter-modules, 4 canaux de notification, 9+ services IA. Architecture professionnelle avec des patterns bien maîtrisés. Principales faiblesses : tests (~50% global), UX multi-clics, bugs critiques de production (auth multi-worker, WebSocket sans fallback), et docs partiellement obsolètes.

---

## 2. État des lieux synthétique

### Chiffres clés

| Métrique | Valeur |
|----------|--------|
| Routes API (endpoints) | ~250+ |
| Routeurs FastAPI | 38 |
| Modèles SQLAlchemy (ORM) | 100+ (32 fichiers) |
| Schémas Pydantic | ~150+ (25 fichiers) |
| Tables SQL | 80+ |
| Pages frontend | ~60+ |
| Composants React | 208+ |
| Clients API frontend | 34 |
| Hooks React custom | 15 |
| Stores Zustand | 4 |
| Schémas Zod | 22 |
| Fichiers de tests (backend) | 74+ |
| Fichiers de tests (frontend) | 71 |
| CRON jobs | 68+ |
| Bridges inter-modules | 21 |
| Middlewares | 7 couches |
| WebSockets | 5 implémentations |
| Canaux de notification | 4 (push, ntfy, WhatsApp, email) |

### Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.13+, FastAPI 0.109, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 16.2.1, React 19, TypeScript 5, Tailwind CSS v4 |
| Base de données | Supabase PostgreSQL, migrations SQL-file |
| IA | Mistral AI (client custom + cache sémantique + circuit breaker) |
| État frontend | TanStack Query v5, Zustand 5 |
| Charts | Recharts 3.8, Chart.js 4.5 |
| 3D | Three.js 0.183, @react-three/fiber 9.5 |
| Cartes | Leaflet 1.9, react-leaflet 5.0 |
| Tests | pytest + Vitest 4.1 + Testing Library + Playwright |
| Monitoring | Prometheus, Sentry |
| Notifications | ntfy.sh, Web Push VAPID, Meta WhatsApp Cloud, Resend |

### Modules par domaine

| Module | Routes | Services | Bridges | CRON | Tests | Statut |
|--------|--------|----------|---------|------|-------|--------|
| 🍽️ Cuisine/Recettes | 20 | RecetteService, ImportService | 7 | 5 | ✅ Complet | ✅ Mature |
| 🛒 Courses | 20 | CoursesService | 3 | 3 | ✅ Complet | ✅ Mature |
| 📦 Inventaire | 14 | InventaireService | 4 | 3 | ✅ Complet | ✅ Mature |
| 📅 Planning | 15 | PlanningService (5 sous-modules) | 5 | 4 | ✅ Complet | ✅ Mature |
| 🧑‍🍳 Batch Cooking | 8 | BatchCookingService | 1 | 1 | ✅ OK | ✅ Stable |
| ♻️ Anti-Gaspillage | 6 | AntiGaspillageService | 2 | 2 | ✅ OK | ✅ Stable |
| 💡 Suggestions IA | 4 | BaseAIService | 0 | 0 | ✅ OK | ✅ Stable |
| 👶 Famille/Jules | 20 | JulesAIService | 7 | 5 | ✅ Complet | ✅ Mature |
| 🏡 Maison | 15+ | MaisonService | 4 | 6 | ✅ OK | ✅ Stable |
| 🏠 Habitat | 10 | HabitatService | 0 | 2 | ⚠️ Partiel | 🟡 En cours |
| 🎮 Jeux | 12 | JeuxService | 1 | 3 | ✅ OK | ✅ Stable |
| 🗓️ Calendriers | 6 | CalendrierService | 2 | 2 | ⚠️ Partiel | 🟡 En cours |
| 📊 Dashboard | 3 | DashboardService | 0 | 0 | ✅ OK | ✅ Stable |
| 📄 Documents | 6 | DocumentService | 1 | 1 | ⚠️ Partiel | 🟡 En cours |
| 🧰 Utilitaires | 10+ | Notes, Journal, Contacts | 1 | 0 | ⚠️ Partiel | 🟡 En cours |
| 🤖 IA Avancée | 14 | Multi-service | 0 | 0 | ⚠️ Partiel | 🟡 En cours |
| ✈️ Voyages | 8 | VoyageService | 2 | 1 | ⚠️ Partiel | 🟡 En cours |
| ⌚ Garmin | 5 | GarminService | 1 | 1 | ⚠️ Minimal | 🟡 En cours |
| 🔐 Auth / Admin | 15+ | AuthService | 0 | 0 | ✅ OK | ✅ Stable |
| 📤 Export PDF | 3 | RapportService | 0 | 0 | ⚠️ Partiel | 🟡 En cours |
| 🔔 Push / Webhooks | 8 | NotificationService | 0 | 5 | ⚠️ Partiel | 🟡 En cours |
| 🤖 Automations | 6 | AutomationsEngine | 0 | 1 | ⚠️ Partiel | 🟡 En cours |

### Frontend — Pages par module

| Module | Pages | Composants | Tests | Statut |
|--------|-------|------------|-------|--------|
| 🍽️ Cuisine | 12 | ~20 | ✅ 8 fichiers | ✅ Mature |
| 👶 Famille | 10 | ~8 | ⚠️ 3 fichiers | 🟡 Gaps |
| 🏡 Maison | 8 | ~15 | ⚠️ 2 fichiers | 🟡 Gaps |
| 🏠 Habitat | 3 | ~6 | ⚠️ 1 fichier | 🟡 Gaps |
| 🎮 Jeux | 7 | ~12 | ✅ 5 fichiers | ✅ OK |
| 📅 Planning | 2 | ~3 | ✅ 2 fichiers | ✅ OK |
| 🧰 Outils | 6 | ~5 | ✅ 6 fichiers | ✅ OK |
| ⚙️ Paramètres | 3 + 7 onglets | ~7 | ⚠️ 1 fichier | 🟡 Gaps |
| 🔧 Admin | 10 | ~5 | ⚠️ 2 fichiers | 🟡 Gaps |

---

## 3. Phase A — Stabilisation ✅ TERMINÉE

> **Objectif** : Corriger les bugs critiques/importants, consolider SQL, couvrir les tests critiques, mettre à jour la doc obsolète
> **Semaines** : 1-2
> **Priorité** : 🔴 BLOQUANT
> **Statut** : ✅ **Terminée** — 16/16 tâches complétées

| # | Tâche | Source | Effort | Catégorie | Statut |
|---|-------|--------|--------|-----------|--------|
| A1 | Fixer B1 — API_SECRET_KEY random par process (tokens invalides en multi-worker) | §3 Bug critique | 1h | Sécurité | ✅ |
| A2 | Fixer B2 — WebSocket courses sans fallback HTTP polling | §3 Bug critique | 1j | Résilience | ✅ |
| A3 | Fixer B3 — Intercepteur auth promise non gérée (token expiré → utilisateur bloqué) | §3 Bug critique | 2h | Frontend | ✅ |
| A4 | Fixer B4 — Event bus en mémoire uniquement (historique perdu au restart) | §3 Bug critique | 1j | Core | ✅ |
| A5 | Fixer B5 — Rate limiting mémoire non borné (fuite mémoire lente) → LRU | §3 Bug important | 2h | Perf | ✅ |
| A6 | Fixer B7 — X-Forwarded-For spoofable (bypass rate limiting) | §3 Bug important | 2h | Sécurité | ✅ |
| A7 | Fixer B9 — WhatsApp state non persisté (conversation cassée) → DB | §3 Bug important | 1j | WhatsApp | ✅ |
| A8 | Fixer B10 — CORS vide en production sans erreur explicite | §3 Bug important | 1h | Config | ✅ |
| A9 | Exécuter audit_orm_sql.py et corriger divergences ORM↔SQL (S2) | §5 SQL | 1j | SQL | ✅ |
| A10 | Consolider migrations V003-V008 dans les fichiers schema (S3) | §5 SQL | 1j | SQL | ✅ |
| A11 | Régénérer INIT_COMPLET.sql propre (S1) | §5 SQL | 30min | SQL | ✅ |
| A12 | Tests export PDF (T1) | §12 Tests | 1j | Tests | ✅ |
| A13 | Tests webhooks WhatsApp (T2) | §12 Tests | 1j | Tests | ✅ |
| A14 | Tests event bus scénarios (T3) | §12 Tests | 1j | Tests | ✅ |
| A15 | Mettre à jour CRON_JOBS.md — 68+ jobs à documenter (D1) | §13 Doc | 2h | Doc | ✅ |
| A16 | Mettre à jour NOTIFICATIONS.md — système refait en phase 8 (D2) | §13 Doc | 2h | Doc | ✅ |

**Total Phase A : 16/16 tâches ✅**

---

## 4. Phase B — Fonctionnalités & IA

> **Objectif** : Combler les gaps fonctionnels, enrichir l'IA, ajouter les CRON et inter-modules critiques
> **Semaines** : 3-4
> **Priorité** : 🟡 HAUTE

| # | Tâche | Source | Effort | Catégorie |
|---|-------|--------|--------|-----------|
| B1 | G5 — Mode hors-ligne courses (PWA cache offline en magasin) | §4 Gap | 3j | PWA |
| B2 | IA1 — Prédiction courses intelligente (historique → pré-remplir liste) | §8 IA | 3j | IA |
| B3 | J2 — CRON planning auto semaine (dimanche 19h si planning vide) | §9 CRON | 2j | CRON |
| B4 | J9 — CRON alertes budget seuil (quotidien 20h, catégorie > 80%) | §9 CRON | 1j | CRON |
| B5 | W2 — Commandes WhatsApp enrichies ("ajoute du lait", "budget ce mois") via Mistral NLP | §10 WhatsApp | 3j | WhatsApp |
| B6 | I1 — Bridge récolte jardin → recettes semaine suivante | §7 Inter-module | 2j | Bridge |
| B7 | I3 — Bridge budget anomalie → notification proactive (+30% restaurants) | §7 Inter-module | 2j | Bridge |
| B8 | I5 — Bridge documents expirés → dashboard alerte widget | §7 Inter-module | 1j | Bridge |
| B9 | IA5 — Résumé hebdomadaire IA intelligent (narratif : repas, tâches, budget, scores) | §8 IA | 2j | IA |
| B10 | IA8 — Suggestion batch cooking intelligent (planning + appareils → timeline optimale) | §8 IA | 3j | IA |
| B11 | G20 — Recherche globale complète (Ctrl+K → couvrir notes, jardin, contrats) | §4 Gap | 3j | Frontend |
| B12 | Tests pages famille frontend (T8 étendu) | §12 Tests | 2j | Tests |
| B13 | Tests E2E parcours utilisateur complet (T6) | §12 Tests | 3j | Tests |

**Total Phase B : 13 tâches**

---

## 5. Phase C — UI/UX & Visualisations

> **Objectif** : Rendre l'interface belle, moderne, fluide. Enrichir les visualisations de données
> **Semaines** : 5-6
> **Priorité** : 🟢 MOYENNE-HAUTE

| # | Tâche | Source | Effort | Catégorie |
|---|-------|--------|--------|-----------|
| C1 | U1 — Dashboard widgets drag-drop (`@dnd-kit/core`) | §15 UI | 2j | UI |
| C2 | IN3 — Page "Ma journée" unifiée (repas + tâches + routines + météo + anniversaires) | §18 Innovation | 3j | Innovation |
| C3 | V1 — Plan 3D maison interactif (connecter aux données réelles : tâches par pièce, énergie) | §16 3D | 5j | 3D |
| C4 | V4 — Calendrier nutritionnel heatmap (type GitHub contributions, rouge → vert) | §16 2D | 2j | 2D |
| C5 | V5 — Treemap budget (proportionnel, cliquable drill-down) | §16 2D | 2j | 2D |
| C6 | V7 — Radar skill Jules (motricité, langage, social, cognitif vs normes OMS) | §16 2D | 1j | 2D |
| C7 | V8 — Sparklines dans cartes dashboard (tendance 7 jours) | §16 2D | 1j | 2D |
| C8 | U7 — Transitions de page fluides (framer-motion ou View Transitions API) | §15 UI | 2j | UI |
| C9 | U12 — Swipe actions sur toutes les listes (courses, tâches, recettes) | §15 Mobile | 1j | Mobile |
| C10 | U16 — Compteurs animés dashboard (incrémentation visuelle) | §15 UI | 1j | UI |
| C11 | U9 — Auto-complétion intelligente formulaires (basée sur historique) | §15 UX | 2j | UX |
| C12 | IN4 — Suggestions proactives contextuelles (bannière IA en haut de chaque module) | §18 Innovation | 3j | Innovation |

**Total Phase C : 12 tâches**

---

## 6. Phase D — Admin & Automatisations

> **Objectif** : Enrichir le mode admin, ajouter les CRON manquants, améliorer les notifications
> **Semaines** : 7-8
> **Priorité** : 🟢 MOYENNE

| # | Tâche | Source | Effort | Catégorie |
|---|-------|--------|--------|-----------|
| D1 | A1 — Console commande rapide admin (champ texte : "run job X", "clear cache Y") | §11 Admin | 2j | Admin |
| D2 | A3 — Scheduler visuel CRON (timeline 68 jobs, prochain run, dépendances) | §11 Admin | 3j | Admin |
| D3 | A6 — Logs temps réel via WebSocket admin_logs (endpoint existant → connecter UI) | §11 Admin | 2j | Admin |
| D4 | J1 — CRON prédiction courses hebdo (vendredi 16h) | §9 CRON | 1j | CRON |
| D5 | J4 — CRON rappels jardin saisonniers (hebdo lundi) | §9 CRON | 1j | CRON |
| D6 | J6 — CRON vérification santé système (horaire → alerte ntfy si service down) | §9 CRON | 1j | CRON |
| D7 | J7 — CRON backup auto hebdo JSON (dimanche 04h) | §9 CRON | 1j | CRON |
| D8 | W1 — WhatsApp state persistence (Redis/DB pour multi-turn) | §10 WhatsApp | 2j | Notifications |
| D9 | E1 — Templates email HTML/MJML pour rapports mensuels | §10 Email | 2j | Notifications |
| D10 | O1 — Découper jobs.py monolithique (3500+ lignes) en modules par domaine | §14 Refactoring | 1j | Nettoyage |
| D11 | O3 — Archiver scripts legacy dans `scripts/_archive/` | §14 Refactoring | 30min | Nettoyage |
| D12 | O4 — Standardiser sur Recharts, retirer Chart.js | §14 Refactoring | 1j | Nettoyage |

**Total Phase D : 12 tâches**

---

## 7. Phase E — Innovations

> **Objectif** : Features différenciantes et visionnaires
> **Semaines** : 9+
> **Priorité** : 🟢 BASSE

| # | Tâche | Source | Effort | Catégorie |
|---|-------|--------|--------|-----------|
| E1 | IN1 — Mode "Pilote automatique" (IA gère planning/courses/rappels, utilisateur valide) | §18 Innovation | 5j | Innovation |
| E2 | IN2 — Widget tablette Google (repas du jour, tâche, météo, timer) | §18 Innovation | 4j | Innovation |
| E3 | IN10 — Score famille hebdomadaire composite (nutrition + dépenses + activités + entretien) | §18 Innovation | 2j | Innovation |
| E4 | IN14 — Mode "invité" conjoint (vue simplifiée : courses, planning, routines) | §18 Innovation | 2j | Innovation |
| E5 | V9 — Graphe réseau modules admin (D3.js force graph, 21 bridges visuels) | §16 3D | 2j | Visualisation |
| E6 | V10 — Timeline Gantt entretien maison (Recharts, planification annuelle) | §16 2D | 2j | Visualisation |
| E7 | V2 — Vue jardin 2D/3D (zones plantation, état plantes, calendrier arrosage) | §16 3D | 3j | Visualisation |
| E8 | IN5 — Journal familial automatique (IA génère résumé semaine exportable PDF) | §18 Innovation | 3j | Innovation |
| E9 | IN11 — Rapport mensuel PDF export (graphiques + résumé narratif IA) | §18 Innovation | 3j | Innovation |
| E10 | IN8 — Google Home routines étendues ("Bonsoir" → repas demain + tâches) | §18 Innovation | 4j | Innovation |
| E11 | G17 — Sync Google Calendar bidirectionnelle complète | §4 Gap | 4j | Gap |
| E12 | IA4 — Assistant vocal étendu (intents Google Assistant enrichis) | §8 IA | 4j | IA |

**Total Phase E : 12 tâches**

---

## 8. Référentiel complet par section d'analyse

### 8.1 Bugs et problèmes détectés (analyse §3)

#### 🔴 Critiques (4)

| # | Bug | Module | Impact | Phase |
|---|-----|--------|--------|-------|
| B1 | **API_SECRET_KEY random par process** — chaque worker génère un secret différent → tokens invalides en multi-worker | Auth | Tokens invalides en prod | A1 |
| B2 | **WebSocket courses sans fallback HTTP** — proxy restrictif/3G → collaboration casse silencieusement | Courses | Perte de sync temps réel | A2 |
| B3 | **Promesse non gérée intercepteur auth** — refresh token timeout → utilisateur ni connecté ni déconnecté | Frontend Auth | UX dégradée | A3 |
| B4 | **Event bus en mémoire uniquement** — historique perdu au redémarrage, impossible de rejouer | Core Events | Perte audit trail | A4 |

#### 🟡 Importants (6)

| # | Bug | Module | Impact | Phase |
|---|-----|--------|--------|-------|
| B5 | **Rate limiting mémoire non borné** — chaque IP/user unique sans éviction → fuite mémoire | Rate Limiting | Memory leak prod | A5 |
| B6 | **Maintenance mode cache 5s** — requêtes acceptées pendant la transition | Admin | Requêtes pendant maintenance | D (si temps) |
| B7 | **X-Forwarded-For spoofable** — bypass rate limiting | Sécurité | Rate limiting contournable | A6 |
| B8 | **Metrics capped 500 endpoints / 1000 samples** — percentiles imprécis | Monitoring | Métriques dégradées | D (si temps) |
| B9 | **WhatsApp multi-turn sans persistence** — state machine perd état entre messages | WhatsApp | Conversation cassée | A7 |
| B10 | **CORS vide en production** — frontend bloqué sans config explicite | Config | Frontend bloqué | A8 |

#### 🟢 Mineurs (4)

| # | Bug | Module | Phase |
|---|-----|--------|-------|
| B11 | ResponseValidationError loggé en 500 sans contexte debug | API | Backlog |
| B12 | Pagination cursor — suppressions concurrentes sautent des enregistrements | Pagination | Backlog |
| B13 | ServiceMeta auto-sync wrappers non testée exhaustivement | Core | Backlog |
| B14 | Sentry intégration à 50% — erreurs frontend non tracées | Frontend | B (si temps) |

---

### 8.2 Gaps et fonctionnalités manquantes (analyse §4)

#### 🍽️ Cuisine (5 gaps)

| # | Gap | Priorité | Effort | Phase |
|---|-----|----------|--------|-------|
| G1 | **Drag-drop recettes dans planning** — UX fastidieuse sans | Moyenne | 2j | C |
| G2 | **Import recettes par photo** — Pixtral disponible côté IA | Moyenne | 3j | B/C |
| G3 | **Partage recette via WhatsApp** avec preview | Basse | 1j | D |
| G4 | **Veille prix articles désirés** — scraper API Dealabs/Idealo + alertes soldes via `calendrier_soldes.json` | Moyenne | 3j | E |
| G5 | **Mode hors-ligne courses** — PWA sans cache offline en magasin | Haute | 3j | B1 |

#### 👶 Famille (4 gaps)

| # | Gap | Priorité | Effort | Phase |
|---|-----|----------|--------|-------|
| G6 | **Prévision budget IA** — pas de prédiction "fin de mois" | Haute | 3j | B |
| G7 | **Timeline Jules visuelle** — frise chronologique interactive des jalons | Moyenne | 2j | C |
| G8 | **Export calendrier anniversaires** vers Google Calendar | Basse | 1j | E |
| G9 | **Photos souvenirs liées aux activités** — upload photo pour le journal | Moyenne | 2j | D |

#### 🏡 Maison (4 gaps)

| # | Gap | Priorité | Effort | Phase |
|---|-----|----------|--------|-------|
| G10 | **Plan 3D interactif limité** — Three.js non connecté aux données réelles | Haute | 5j | C3 |
| G11 | **Historique énergie avec graphes** — pas de courbes mois/année | Moyenne | 2j | C |
| G12 | **Catalogue artisans enrichi** — pas d'avis/notes, pas de recherche par métier | Basse | 2j | E |
| G13 | **Devis comparatif** — pas de visualisation comparative devis pour un projet | Moyenne | 3j | E |

#### 🎮 Jeux (3 gaps)

| # | Gap | Priorité | Effort | Phase |
|---|-----|----------|--------|-------|
| G14 | **Graphique ROI temporel** — pas de courbe évolution mensuelle ROI | Haute | 2j | C |
| G15 | **Alertes cotes temps réel** — alerte quand cote atteint seuil défini | Moyenne | 3j | D |
| G16 | **Comparaison stratégies loto** — backtest côte à côte 2+ stratégies | Basse | 2j | E |

#### 📅 Planning (3 gaps)

| # | Gap | Priorité | Effort | Phase |
|---|-----|----------|--------|-------|
| G17 | **Sync Google Calendar bidirectionnelle** — export iCal existe, sync ~60% | Haute | 4j | E11 |
| G18 | **Planning familial consolidé visuel** — pas de Gantt repas + activités + entretien | Moyenne | 3j | C |
| G19 | **Récurrence d'événements** — pas de "tous les mardis" natif | Moyenne | 2j | D |

#### 🧰 Général (4 gaps)

| # | Gap | Priorité | Effort | Phase |
|---|-----|----------|--------|-------|
| G20 | **Recherche globale incomplète** — Ctrl+K manque notes, jardin, contrats | Haute | 3j | B11 |
| G21 | **Mode hors-ligne PWA** — Service Worker enregistré mais pas de stratégie structurée | Haute | 5j | B/E |
| G22 | **Onboarding interactif** — composant tour-onboarding existe mais pas activé | Moyenne | 3j | D |
| G23 | **Export données backup incomplet** — export JSON OK, import/restauration UI incomplet | Moyenne | 2j | D |

---

### 8.3 Consolidation SQL (analyse §5)

#### Structure actuelle

```
sql/
├── INIT_COMPLET.sql          # Auto-généré (4922 lignes, 18 fichiers)
├── schema/                   # 18 fichiers ordonnés (01_extensions → 99_footer)
└── migrations/               # 7 fichiers (V003-V008) + README
```

#### Actions

| # | Action | Priorité | Phase |
|---|--------|----------|-------|
| S1 | Régénérer INIT_COMPLET.sql (`python scripts/db/regenerate_init.py`) | Haute | A11 |
| S2 | Audit ORM↔SQL (`python scripts/audit_orm_sql.py`) et corriger divergences | Haute | A9 |
| S3 | Consolider 7 migrations dans les fichiers schema — source unique | Haute | A10 |
| S4 | Vérifier index manquants (user_id, date, statut) dans `14_indexes.sql` | Moyenne | B |
| S5 | Nettoyer tables inutilisées (80+ tables toutes ont ORM + route ?) | Basse | E |
| S6 | Vérifier vues SQL (`17_views.sql`) réellement utilisées par le backend | Basse | E |

#### Workflow simplifié cible

```
1. Modifier le fichier schema approprié (ex: sql/schema/04_cuisine.sql)
2. Exécuter: python scripts/db/regenerate_init.py
3. Appliquer: INIT_COMPLET.sql sur Supabase (SQL Editor)
4. Vérifier: python scripts/audit_orm_sql.py
```

---

### 8.4 Interactions intra-modules (analyse §6)

#### Cuisine (interne) — ✅ Bien connecté

```
Recettes ──── planifiées ───→ Planning
    │                            │
    │                            ├── génère ──→ Courses
    │                            │
    └── version Jules ──→ portions adaptées
                                 │
Inventaire ◄────── checkout ────┘
    │
    ├── péremption ──→ Anti-Gaspillage ──→ Recettes rescue
    │
    └── stock bas ──→ Automation ──→ Courses auto

Batch Cooking ◄── planning semaine ── prépare ──→ bloque planning
```

**À améliorer :**
| # | Amélioration | Phase |
|---|-------------|-------|
| IM-C1 | Checkout courses → MAJ prix moyens inventaire automatiquement | D |
| IM-C2 | Batch cooking "mode robot" — optimiser ordre étapes par appareil | E |

#### Famille (interne) — 🔧 Améliorable

```
Jules profil ──→ jalons developpement ──→ notifications jalon
Budget ◄──── dépenses catégorisées
Routines ──→ check quotidien ──→ gamification
Anniversaires ──→ checklist ──→ budget cadeau
Documents ──→ expiration ──→ rappels calendrier
```

**À améliorer :**
| # | Amélioration | Phase |
|---|-------------|-------|
| IM-F1 | Jules jalons → suggestions activités adaptées âge (IA contextuelle) | B |
| IM-F2 | Budget anomalies → notification proactive ("tu dépenses +30% en X") | B7 |
| IM-F3 | Routines → tracking complétion visuel (streak) | C |

#### Maison (interne) — 🔧 Améliorable

```
Projets ──→ tâches ──→ devis ──→ dépenses
Entretien ──→ calendrier ──→ produits nécessaires
Jardin ──→ arrosage/récolte ──→ saison
Énergie ──→ relevés compteurs ──→ historique
Stocks (cellier) ──→ consolidé avec inventaire cuisine
```

**À améliorer :**
| # | Amélioration | Phase |
|---|-------------|-------|
| IM-M1 | Projets → timeline Gantt visuelle des travaux | C/E6 |
| IM-M2 | Énergie → graphe évolution + comparaison N vs N-1 | C (V11) |
| IM-M3 | Entretien → suggestions IA proactives ("chaudière 8 ans → révision") | D |

---

### 8.5 Interactions inter-modules (analyse §7)

#### 21 bridges existants ✅

```
┌──────────┐     ┌───────────┐     ┌──────────┐
│ CUISINE  │◄───►│ PLANNING  │◄───►│ COURSES  │
│ recettes │     │ repas     │     │ listes   │
│ inventaire│    │ semaine   │     │ articles │
│ nutrition │    │ conflits  │     │          │
│ batch     │    │           │     │          │
└────┬─────┘     └─────┬─────┘     └────┬─────┘
     │                 │                 │
     │    ┌────────────┤                 │
     │    │            │                 │
┌────▼────▼──┐   ┌────▼─────┐     ┌────▼─────┐
│  FAMILLE   │   │  MAISON  │     │  BUDGET  │
│ jules      │   │ entretien│     │ famille  │
│ routines   │   │ jardin   │     │ jeux (séparé)
│ annivers.  │   │ énergie  │     │ maison   │
└────┬───────┘   └────┬─────┘     └──────────┘
     │                │
     │    ┌───────────┤
┌────▼────▼──┐   ┌───▼──────┐
│ CALENDRIER │   │  JEUX    │
│ google cal │   │ paris    │
│ événements │   │ loto     │
└────────────┘   └──────────┘
```

| # | Bridge | De → Vers | État |
|---|--------|-----------|------|
| 1 | `inter_module_inventaire_planning` | Stock → Planning | ✅ |
| 2 | `inter_module_jules_nutrition` | Jules → Recettes | ✅ |
| 3 | `inter_module_saison_menu` | Saison → Planning | ✅ |
| 4 | `inter_module_courses_budget` | Courses → Budget | ✅ |
| 5 | `inter_module_batch_inventaire` | Batch → Inventaire | ✅ |
| 6 | `inter_module_planning_voyage` | Voyage → Planning | ✅ |
| 7 | `inter_module_peremption_recettes` | Péremption → Recettes | ✅ |
| 8 | `inter_module_documents_calendrier` | Documents → Calendrier | ✅ |
| 9 | `inter_module_meteo_activites` | Météo → Activités | ✅ |
| 10 | `inter_module_weekend_courses` | Weekend → Courses | ✅ |
| 11 | `inter_module_voyages_budget` | Voyages → Budget | ✅ |
| 12 | `inter_module_anniversaires_budget` | Anniversaires → Budget | ✅ |
| 13 | `inter_module_budget_jeux` | Jeux ↔ Budget | ✅ (info seulement, budgets séparés) |
| 14 | `inter_module_garmin_health` | Garmin → Dashboard | ✅ |
| 15 | `inter_module_entretien_courses` | Entretien → Courses | ✅ |
| 16 | `inter_module_jardin_entretien` | Jardin → Entretien | ✅ |
| 17 | `inter_module_charges_energie` | Charges → Énergie | ✅ |
| 18 | `inter_module_energie_cuisine` | Énergie → Cuisine | ✅ |
| 19 | `inter_module_chat_contexte` | Tous → Chat IA | ✅ |
| 20 | `inter_module_voyages_calendrier` | Voyages → Calendrier | ✅ |
| 21 | `inter_module_garmin_planning` | Garmin → Planning | ⚠️ Partiel |

#### 10 nouvelles interactions à implémenter

| # | Interaction | De → Vers | Valeur | Effort | Phase |
|---|------------|-----------|--------|--------|-------|
| I1 | **Récolte jardin → Recettes semaine suivante** | Jardin → Planning | ✅ Acceptée | 2j | B6 |
| I2 | **Entretien récurrent → Planning unifié** | Entretien → Planning | Haute | 2j | D |
| I3 | **Budget anomalie → Notification proactive** | Budget → Notifs | Haute | 2j | B7 |
| I4 | **Voyages → Inventaire** (déstockage avant départ) | Voyages → Inventaire | Moyenne | 1j | D |
| I5 | **Documents expirés → Dashboard alerte** | Documents → Dashboard | Haute | 1j | B8 |
| I6 | **Anniversaire proche → Suggestions cadeaux IA** | Anniversaires → IA | Moyenne | 2j | E |
| I7 | **Contrats/Garanties → Dashboard widgets** | Maison → Dashboard | Moyenne | 1j | D |
| I8 | **Météo → Entretien maison** (gel → penser au jardin) | Météo → Maison | Moyenne | 2j | D |
| I9 | **Planning sport Garmin → Planning repas** (adapter alimentation) | Garmin → Cuisine | Moyenne | 3j | E |
| I10 | **Courses historique → Prédiction prochaine liste** | Courses → IA | Haute | 3j | B2 |

---

### 8.6 Opportunités IA (analyse §8)

#### IA déjà en place (9 fonctionnels)

| Fonctionnalité | Service | Module | Statut |
|----------------|---------|--------|--------|
| Suggestions recettes | BaseAIService | Cuisine | ✅ |
| Génération planning IA | PlanningService | Planning | ✅ |
| Recettes rescue anti-gaspi | AntiGaspillageService | Cuisine | ✅ |
| Batch cooking optimisé | BatchCookingService | Cuisine | ✅ |
| Suggestions weekend | WeekendAIService | Famille | ✅ |
| Score bien-être | DashboardService | Dashboard | ✅ |
| Chat IA contextualisé | AssistantService | Outils | ✅ |
| Version Jules recettes | JulesAIService | Famille | ✅ |
| 14 endpoints IA avancée | Multi-services | IA Avancée | ⚠️ Partiel |

#### 12 nouvelles opportunités

| # | Opportunité | Module(s) | Priorité | Effort | Phase |
|---|-------------|-----------|----------|--------|-------|
| IA1 | **Prédiction courses intelligente** — historique → pré-remplir liste | Courses + IA | 🔴 | 3j | B2 |
| IA2 | **Planificateur adaptatif** météo+stock+budget — endpoint sous-utilisé | Planning + Multi | 🔴 | 2j | B |
| IA3 | **Diagnostic pannes maison** — photo Pixtral → diagnostic + action | Maison | 🟡 | 3j | D |
| IA4 | **Assistant vocal contextuel étendu** — Google Assistant intents enrichis | Tous | 🟡 | 4j | E12 |
| IA5 | **Résumé hebdomadaire intelligent** — narratif agréable à lire | Dashboard | 🔴 | 2j | B9 |
| IA6 | **Optimisation énergie prédictive** — relevés + météo → prédiction facture | Maison/Énergie | 🟡 | 3j | E |
| IA7 | **Analyse nutritionnelle photo** — Pixtral → calories/macros estimés | Cuisine | 🟡 | 3j | E |
| IA8 | **Suggestion batch cooking intelligent** — planning + appareils → timeline | Batch Cooking | 🔴 | 3j | B10 |
| IA9 | **Jules conseil développement proactif** — suggestions âge + jalons | Famille/Jules | 🟡 | 2j | D |
| IA10 | **Auto-catégorisation budget** — commerçant/article → catégorie (pas OCR) | Budget | 🟡 | 2j | D |
| IA11 | **Génération checklist voyage** — destination + dates → checklist IA | Voyages | 🟡 | 2j | D |
| IA12 | **Score écologique repas** — saisonnalité, distance, végétal vs animal | Cuisine | 🟢 | 2j | E |

---

### 8.7 Jobs automatiques CRON (analyse §9)

#### 68+ jobs existants — Résumé

**Quotidiens :**
- 06h00 : sync Garmin
- 07h00 : péremptions, rappels famille, alerte stock bas
- 07h30 : digest WhatsApp matinal
- 08h00 : rappels maison
- 09h00 : digest ntfy
- 18h00 : rappel courses, push contextuel soir
- 23h00 : sync Google Calendar
- 5 min : runner automations

**Hebdomadaires :**
- Lundi 07h30 : résumé hebdo
- Vendredi 17h00 : score weekend
- Dimanche 03h00 : sync OpenFoodFacts
- Dimanche 20h00 : score bien-être, points gamification

**Mensuels :**
- 1er 08h15 : rapport budget
- 1er 09h00 : contrôle contrats/garanties
- 1er 09h30 : rapport maison

#### 10 nouveaux jobs proposés

| # | Job | Fréquence | Modules | Priorité | Phase |
|---|-----|-----------|---------|----------|-------|
| J1 | **Prédiction courses hebdo** | Vendredi 16h | Courses + IA | 🔴 | D4 |
| J2 | **Planning auto semaine** (si vide → propose via WhatsApp) | Dimanche 19h | Planning + IA | 🔴 | B3 |
| J3 | **Nettoyage cache/exports** (> 7 jours) | Quotidien 02h | Export | 🟡 | D |
| J4 | **Rappel jardin saison** | Hebdo (Lundi) | Jardin | 🟡 | D5 |
| J5 | **Sync budget consolidation** (tous modules) | Quotidien 22h | Budget | 🟡 | D |
| J6 | **Vérification santé système** | Horaire | Admin | 🟡 | D6 |
| J7 | **Backup auto JSON** | Hebdo (Dimanche 04h) | Admin | 🟢 | D7 |
| J8 | **Tendances nutrition hebdo** | Dimanche 18h | Cuisine/Nutrition | 🟡 | E |
| J9 | **Alertes budget seuil** (catégorie > 80%) | Quotidien 20h | Budget | 🔴 | B4 |
| J10 | **Rappel activité Jules** ("Jules a X mois → activités recommandées") | Quotidien 09h | Famille | 🟡 | D |

---

### 8.8 Notifications (analyse §10)

#### Architecture

```
                    ┌─────────────────┐
                    │  Événement      │
                    │  (CRON / User)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Router de      │
                    │  notifications  │
                    └────────┬────────┘
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼──────┐ ┌──────▼───────┐ ┌─────▼──────┐
    │  Web Push    │ │   ntfy.sh    │ │ WhatsApp   │
    │  (VAPID)     │ │  (open src)  │ │ (Meta API) │
    └──────────────┘ └──────────────┘ └────────────┘
                             │
                    ┌────────▼────────┐
                    │    Email        │
                    │   (Resend)      │
                    └─────────────────┘
    Failover: Push → ntfy → WhatsApp → Email
    Throttle: 2h par type d'événement par canal
```

#### Améliorations WhatsApp

| # | Amélioration | Priorité | Effort | Phase |
|---|-------------|----------|--------|-------|
| W1 | Persistence état conversation multi-turn (Redis/DB) | 🔴 | 2j | D8 |
| W2 | Commandes texte enrichies ("ajoute du lait", "budget ce mois") via NLP Mistral | 🔴 | 3j | B5 |
| W3 | Boutons interactifs étendus (valider courses, noter dépense, signaler panne) | 🟡 | 2j | D |
| W4 | Photo → action (plante malade → diagnostic, plat → identification recette) | 🟡 | 3j | E |
| W5 | Résumé quotidien personnalisable (choix infos via paramètres) | 🟡 | 2j | D |

#### Améliorations Email

| # | Amélioration | Priorité | Effort | Phase |
|---|-------------|----------|--------|-------|
| E1 | Templates HTML/MJML jolis pour rapports mensuels | 🟡 | 2j | D9 |
| E2 | Résumé hebdo email optionnel | 🟡 | 1j | D |
| E3 | Alertes critiques par email (document expiré, stock critique, budget dépassé) | 🔴 | 1j | B |

#### Améliorations Push

| # | Amélioration | Priorité | Effort | Phase |
|---|-------------|----------|--------|-------|
| P1 | Actions dans la notification push ("Ajouter aux courses") | 🟡 | 2j | C |
| P2 | Push conditionnel (heures calmes configurables) | 🟡 | 1j | D |
| P3 | Badge app PWA (nombre notifications non lues) | 🟢 | 1j | E |

---

### 8.9 Mode Admin (analyse §11)

#### Existant — ✅ Très complet

| Catégorie | Fonctionnalité | Statut |
|-----------|---------------|--------|
| Jobs CRON | Lister, déclencher, historique | ✅ |
| Notifications | Tester un canal, broadcast test | ✅ |
| Event Bus | Historique, émission manuelle | ✅ |
| Cache | Stats, purge par pattern | ✅ |
| Services | État registre complet | ✅ |
| Feature Flags | Activer/désactiver features | ✅ |
| Maintenance | Mode maintenance ON/OFF | ✅ |
| Simulation | Dry-run workflows (péremption, digest, rappels) | ✅ |
| IA Console | Tester prompts (température, tokens) | ✅ |
| Impersonation | Switcher d'utilisateur | ✅ |
| Audit/Security Logs | Traçabilité complète | ✅ |
| SQL Views | Browser de vues SQL | ✅ |
| WhatsApp Test | Message test | ✅ |
| Config | Export/import runtime | ✅ |

#### Améliorations

| # | Amélioration | Priorité | Effort | Phase |
|---|-------------|----------|--------|-------|
| A1 | Console commande rapide ("run job X", "clear cache Y") | 🟡 | 2j | D1 |
| A2 | Dashboard admin temps réel (WebSocket admin_logs → UI filtres + auto-scroll) | 🟡 | 3j | D |
| A3 | Scheduler visuel (timeline 68 jobs, prochain run, dépendances) | 🟡 | 3j | D2 |
| A4 | Replay d'événements passés du bus avec handlers | 🟡 | 2j | D |
| A6 | Logs en temps réel (endpoint WS existe → connecter UI) | 🟡 | 2j | D3 |
| A7 | Test E2E one-click (scénario complet recette→planning→courses→checkout→inventaire) | 🟢 | 3j | E |

---

### 8.10 Couverture de tests (analyse §12)

#### Backend — ~55% couverture

| Zone | Fichiers | Couverture | Note |
|------|----------|------------|------|
| Routes API cuisine | 8 | ✅ ~85% | Bien |
| Routes API famille | 6 | ✅ ~75% | OK |
| Routes API maison | 5 | ⚠️ ~60% | Gaps jardin/énergie |
| Routes API jeux | 2 | ⚠️ ~55% | Gaps loto/euro |
| Routes API admin | 2 | ✅ ~70% | OK |
| Routes export/upload | 2 | ❌ ~30% | Très faible |
| Routes webhooks | 2 | ❌ ~25% | Très faible |
| Services | 20+ | ⚠️ ~60% | Variable |
| Core (config, db, cache) | 6 | ⚠️ ~55% | Cache orchestrateur faible |
| Event Bus | 1 | ❌ ~20% | Très faible |
| Résilience | 1 | ⚠️ ~40% | Manque scénarios réels |
| WebSocket | 1 | ❌ ~25% | Edge cases manquants |
| Intégrations | 3 | ❌ ~20% | Stubs sans E2E |

#### Frontend — ~40% couverture

| Zone | Fichiers | Couverture | Note |
|------|----------|------------|------|
| Pages cuisine | 8 | ✅ ~70% | Bien |
| Pages jeux | 5 | ✅ ~65% | OK |
| Pages outils | 6 | ✅ ~60% | OK |
| Pages famille | 3 | ⚠️ ~35% | Gaps importants |
| Pages maison | 2 | ⚠️ ~30% | Gaps importants |
| Pages admin | 2 | ⚠️ ~30% | Gaps importants |
| Pages paramètres | 1 | ❌ ~15% | Très faible |
| Hooks | 2 | ⚠️ ~45% | WebSocket sous-testé |
| Stores | 4 | ✅ ~80% | Bien |
| Composants | 12 | ⚠️ ~40% | Variable |
| API clients | 1 | ❌ ~15% | Très faible |
| E2E Playwright | Quelques | ❌ ~10% | Quasi inexistant |

#### Tests manquants prioritaires

| # | Test | Module | Priorité | Phase |
|---|------|--------|----------|-------|
| T1 | Tests export PDF (courses, planning, recettes, budget) | Export | 🔴 | A12 |
| T2 | Tests webhooks WhatsApp (state machine, parsing) | Notifications | 🔴 | A13 |
| T3 | Tests event bus scenarios (pub/sub, wildcards, erreurs) | Core | 🔴 | A14 |
| T4 | Tests cache L1/L2/L3 (promotion, éviction) | Core | 🟡 | B |
| T5 | Tests WebSocket edge cases (reconnexion, timeout, malformé) | Courses | 🟡 | D |
| T6 | Tests E2E parcours utilisateur complet | Frontend | 🔴 | B13 |
| T7 | Tests API clients frontend (erreurs réseau, refresh, pagination) | Frontend | 🟡 | D |
| T8 | Tests pages paramètres (chaque onglet) | Frontend | 🟡 | B12 |
| T9 | Tests pages admin (jobs, services, cache, flags) | Frontend | 🟡 | D |
| T10 | Tests Playwright accessibilité (axe-core pages principales) | Frontend | 🟢 | E |

---

### 8.11 Documentation (analyse §13)

#### État

| Document | Statut | Action | Phase |
|----------|--------|--------|-------|
| `docs/INDEX.md` | ✅ Courant | — | — |
| `docs/MODULES.md` | ✅ Courant | — | — |
| `docs/API_REFERENCE.md` | ✅ Courant | — | — |
| `docs/API_SCHEMAS.md` | ✅ Courant | — | — |
| `docs/SERVICES_REFERENCE.md` | ✅ Courant | — | — |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | ✅ Courant | — | — |
| `docs/ERD_SCHEMA.md` | ✅ Courant | — | — |
| `docs/ARCHITECTURE.md` | ⚠️ 1 mois | Rafraîchir | D |
| `docs/DATA_MODEL.md` | ⚠️ Vérifier | Peut être obsolète post-phases | D |
| `docs/DEPLOYMENT.md` | ⚠️ Vérifier | Config Railway/Vercel actuelle | D |
| `docs/ADMIN_RUNBOOK.md` | ⚠️ Vérifier | 20+ endpoints admin tous docum. ? | D |
| `docs/CRON_JOBS.md` | 🔴 Obsolète | 68+ jobs à documenter | A15 |
| `docs/NOTIFICATIONS.md` | 🔴 Obsolète | Système refait en phase 8 | A16 |
| `docs/AUTOMATIONS.md` | 🔴 Obsolète | Expansion phases 8-10 | D |
| `docs/INTER_MODULES.md` | ⚠️ Vérifier | 21 bridges documentés ? | D |
| `docs/EVENT_BUS.md` | ⚠️ Vérifier | Subscribers à jour ? | D |
| `docs/MONITORING.md` | ⚠️ Vérifier | Prometheus metrics actuelles ? | D |
| `docs/SECURITY.md` | ⚠️ Vérifier | Rate limiting, 2FA, CORS | D |
| `PLANNING_IMPLEMENTATION.md` | 🔴 Obsolète | Ce document le remplace | — |
| `ROADMAP.md` | 🔴 Obsolète | Priorités périmées | D |

#### Documentation à créer

| # | Document | Priorité | Phase |
|---|---------|----------|-------|
| D1 | Guide complet CRON jobs (68+ jobs, horaires, dépendances) | 🔴 | A15 |
| D2 | Guide notifications refonte (4 canaux, failover, templates, config) | 🔴 | A16 |
| D3 | Guide admin MàJ (20+ endpoints, panneau, simulations, flags) | 🟡 | D |
| D4 | Guide bridges inter-modules (21 bridges, naming, comment en créer) | 🟡 | D |
| D5 | Guide de test unifié (pytest + Vitest + Playwright, fixtures, mocks) | 🟡 | D |
| D6 | Changelog module par module | 🟢 | E |

---

### 8.12 Organisation & architecture (analyse §14)

#### Points forts ✅

- Architecture modulaire : séparation routes/schemas/services/models
- Service Registry : `@service_factory` singleton thread-safe
- Event Bus : pub/sub découplé, wildcards, priorités
- Cache multi-niveaux : L1→L2→L3+Redis
- Résilience : retry+timeout+circuit breaker composables
- Sécurité : JWT+2FA TOTP+rate limiting+security headers+sanitization
- Frontend : App Router Next.js 16, composants shadcn/ui consistants

#### Points à améliorer

| # | Problème | Action | Effort | Phase |
|---|----------|--------|--------|-------|
| O1 | `jobs.py` monolithique (3500+ lignes) | Découper en `jobs_cuisine.py`, `jobs_famille.py`, etc. | 1j | D10 |
| O2 | Routes famille éclatées (multiples fichiers) | Documenter naming pattern | 30min | D |
| O3 | Scripts legacy non archivés | Déplacer dans `scripts/_archive/` | 30min | D11 |
| O4 | Doubles bibliothèques charts (Chart.js + Recharts) | Standardiser sur Recharts | 1j | D12 |
| O5 | RGPD route non pertinente (app privée) | Simplifier en "Export backup" | 30min | E |
| O6 | Types frontend dupliqués entre fichiers | Centraliser via barrel exports | 1j | D |
| O7 | Données référence non versionnées | Ajouter version dans chaque JSON | 30min | E |
| O8 | Dossier exports non nettoyé (`data/exports/`) | Politique rétention automatique (CRON J3) | 30min | D |

---

### 8.13 Améliorations UI/UX (analyse §15)

#### Dashboard

| # | Amélioration | Priorité | Phase |
|---|-------------|----------|-------|
| U1 | **Widgets drag-drop** (`@dnd-kit/core`) | 🔴 | C1 |
| U2 | Cartes avec micro-animations (Framer Motion) | 🟡 | C |
| U3 | Mode sombre raffiné (charts, calendrier) | 🟡 | E |
| U4 | Squelettes de chargement fidèles | 🟡 | D |

#### Navigation

| # | Amélioration | Priorité | Phase |
|---|-------------|----------|-------|
| U5 | Sidebar avec favoris dynamiques (composant existant → store) | 🟡 | D |
| U6 | Breadcrumbs interactifs (tous niveaux cliquables) | 🟢 | E |
| U7 | **Transitions de page fluides** (framer-motion ou View Transitions) | 🟡 | C8 |
| U8 | Bottom bar mobile enrichie (indicateur page active + animation) | 🟡 | C |

#### Formulaires

| # | Amélioration | Priorité | Phase |
|---|-------------|----------|-------|
| U9 | **Auto-complétion intelligente** (historique) | 🔴 | C11 |
| U10 | Validation inline temps réel (onBlur au lieu de submit) | 🟡 | D |
| U11 | Assistant formulaire IA ("Aide-moi à remplir") | 🟡 | E |

#### Mobile

| # | Amélioration | Priorité | Phase |
|---|-------------|----------|-------|
| U12 | **Swipe actions** sur toutes les listes | 🟡 | C9 |
| U13 | Pull-to-refresh (TanStack Query le supporte) | 🟡 | D |
| U14 | Haptic feedback (Vibration API) | 🟢 | E |

#### Micro-interactions

| # | Amélioration | Priorité | Phase |
|---|-------------|----------|-------|
| U15 | Confetti sur accomplissement (planning validé, courses complètes) | 🟢 | E |
| U16 | **Compteurs animés dashboard** (0 → valeur réelle) | 🟡 | C10 |
| U17 | Toast notifications Sonner améliorées (succès check animé, erreur shake) | 🟡 | D |

---

### 8.14 Visualisations 2D/3D (analyse §16)

#### Existant

| Composant | Technologie | Module | Statut |
|-----------|-------------|--------|--------|
| Plan 3D maison | Three.js/@react-three/fiber | Maison | ⚠️ Non connecté aux données |
| Heatmap numéros loto | Recharts | Jeux | ✅ |
| Heatmap cotes paris | Recharts | Jeux | ✅ |
| Camembert budget | Recharts | Famille | ✅ |
| Graphique ROI | Recharts | Jeux | ✅ |
| Graphique jalons Jules | Recharts | Famille | ✅ |
| Timeline planning | Custom CSS | Planning | ⚠️ Basique |
| Carte Leaflet habitat | react-leaflet | Habitat | ⚠️ Partiel |

#### Nouvelles visualisations

**3D :**

| # | Visualisation | Module | Description | Effort | Phase |
|---|---------------|--------|-------------|--------|-------|
| V1 | **Plan 3D maison interactif** | Maison | Connecter aux données : couleur pièces par tâches, énergie par pièce, clic → détail | 5j | C3 |
| V2 | **Vue jardin 2D/3D** | Jardin | Zones plantation, état plantes, calendrier arrosage | 3j | E7 |
| V3 | **Globe 3D voyages** | Voyages | Destinations + itinéraires (globe.gl) | 2j | E |

**2D :**

| # | Visualisation | Module | Description | Effort | Phase |
|---|---------------|--------|-------------|--------|-------|
| V4 | **Calendrier nutritionnel heatmap** | Cuisine | Grille GitHub contributions jour par jour (rouge → vert) | 2j | C4 |
| V5 | **Treemap budget** | Budget | Proportionnel catégories, drill-down cliquable | 2j | C5 |
| V6 | **Sunburst recettes** | Cuisine | Catégories → sous-catégories → recettes (D3.js) | 2j | E |
| V7 | **Radar skill Jules** | Famille | Diagramme araignée compétences vs normes OMS | 1j | C6 |
| V8 | **Sparklines dans cartes** | Dashboard | Mini graphiques tendance 7 jours | 1j | C7 |
| V9 | **Graphe réseau modules** | Admin | 21 bridges visuels (D3.js force graph) | 2j | E5 |
| V10 | **Timeline Gantt entretien** | Maison | Planification annuelle | 2j | E6 |
| V11 | **Courbe énergie N vs N-1** | Énergie | Comparaison consommation | 2j | C |
| V12 | **Flux Sankey courses → catégories** | Courses/Budget | Fournisseurs → catégories → sous-catégories | 2j | E |
| V13 | **Wheel fortune loto** | Jeux | Animation roue révélation numéros IA | 1j | E |

---

### 8.15 Simplification flux utilisateur (analyse §17)

> L'utilisateur doit accomplir ses tâches quotidiennes en **3 clics maximum**.
> L'IA fait le travail lourd en arrière-plan, l'utilisateur **valide**.

#### 🍽️ Flux cuisine (central)

```
Semaine vide → IA propose planning → Valider/Modifier/Régénérer
                                         │
                                    Planning validé
                                   ┌─────┴─────┐
                            Auto-génère      Notif WhatsApp
                            courses           recap
                                │
                          Liste courses (triée par rayon)
                                │
                     En magasin: cocher au fur et à mesure
                                │
                     Checkout → transfert automatique inventaire
                                │
                     Score anti-gaspi mis à jour

Fin de semaine: "Qu'avez-vous vraiment mangé ?" → feedback IA
```

**Actions utilisateur** : 3 (valider planning → cocher courses → checkout)
**Actions IA** : Planning, courses, rayons, transfert inventaire

#### 👶 Flux famille quotidien

```
Matin (auto WhatsApp 07h30):
  "Bonjour ! Repas X, tâche Y, Jules a Z mois" → OK / Modifier

Journée:
  Routines Jules (checklist → cocher)

Soir:
  Récap auto: "3/5 tâches, 2 repas ok, Jules: poids noté"
```

#### 🏡 Flux maison

```
Notification push auto:
  "Tâche entretien: [tâche]" → Voir → Marquer fait → auto-prochaine date
  "Stock [X] bas" → Ajouter aux courses (1 clic)
  1er du mois: Rapport email résumé tâches + budget maison
```

#### Actions rapides FAB mobile

| Action rapide | Cible | Icône |
|--------------|-------|-------|
| + Recette rapide | Formulaire simplifié (nom + photo) | 📸 |
| + Article courses | Ajout vocal ou texte | 🛒 |
| + Dépense | Montant + catégorie | 💰 |
| + Note | Texte libre | 📝 |
| Scan barcode | Scanner → inventaire ou courses | 📷 |
| Timer cuisine | Minuteur rapide | ⏱️ |

**Phase : C (actions rapides), B (flux simplifiés cuisine/famille), D (flux maison)**

---

### 8.16 Axes d'innovation (analyse §18)

| # | Innovation | Modules | Description | Effort | Impact | Phase |
|---|-----------|---------|-------------|--------|--------|-------|
| IN1 | **Mode "Pilote automatique"** | Tous | IA gère planning/courses/rappels sans intervention. Résumé quotidien, corrections uniquement. ON/OFF paramètres | 5j | 🔴 Très élevé | E1 |
| IN2 | **Widget tablette Google** | Dashboard | Widget Android/web : repas du jour, tâche, météo, timer. Compatible tablette Google | 4j | 🔴 Élevé | E2 |
| IN3 | **Page "Ma journée" unifiée** | Planning+Cuisine+Famille+Maison | Tout en une page : repas, tâches, routines Jules, météo, anniversaires, timer | 3j | 🔴 Très élevé | C2 |
| IN4 | **Suggestions proactives contextuelles** | IA+Tous | Bannière IA en haut de chaque module : "tomates expirent → recettes", "budget restaurants 80% → détail" | 3j | 🔴 Élevé | C12 |
| IN5 | **Journal familial automatique** | Famille | IA génère journal de la semaine : repas, activités, Jules, photos, météo, dépenses. Exportable PDF | 3j | 🟡 Moyen | E8 |
| IN6 | **Mode focus/zen** | UI | Masque tout sauf la tâche en cours (recette en cuisine, liste en magasin). Composant `focus/` existant | 2j | 🟡 Moyen | D |
| IN7 | **Comparateur prix courses** | Courses+IA | Liste → IA compare prix référence (sans OCR) → budget estimé | 3j | 🟡 Moyen | E |
| IN8 | **Google Home routines étendues** | Assistant | "Bonsoir" → lecture repas demain + tâches | 4j | 🟡 Moyen | E10 |
| IN9 | **Seasonal meal prep planner** | Cuisine+IA | Chaque saison → plan batch cooking saisonnier + congélations recommandées | 2j | 🟡 Moyen | E |
| IN10 | **Score famille hebdomadaire** | Dashboard | Composite : nutrition + dépenses + activités + entretien + bien-être. Graphe semaine par semaine | 2j | 🔴 Élevé | E3 |
| IN11 | **Export rapport mensuel PDF** | Export+IA | PDF avec graphiques : budget, nutrition, entretien, Jules, jeux. Résumé narratif IA | 3j | 🟡 Moyen | E9 |
| IN12 | **Planning vocal** | Assistant+Planning | "Planifie du poulet mardi soir" → crée repas + vérifie stock + ajoute manquants | 3j | 🟡 Moyen | E |
| IN13 | **Tableau de bord énergie** | Maison | Dashboard dédié : conso temps réel (Linky), historique, N-1, prévision facture, tips IA | 4j | 🟡 Moyen | E |
| IN14 | **Mode "invité" conjoint** | Auth | Vue simplifiée 2ème utilisateur : courses, planning, routines. Sans admin ni config | 2j | 🔴 Élevé | E4 |

---

## 9. Annexes

### Annexe A — Arborescence fichiers clés

#### Backend Python

```
src/
├── api/
│   ├── main.py                    # FastAPI app + 7 middlewares + health
│   ├── auth.py                    # JWT + 2FA TOTP
│   ├── dependencies.py            # require_auth, require_role
│   ├── routes/                    # 41 fichiers routeurs (~250 endpoints)
│   ├── schemas/                   # 25 fichiers Pydantic (~150 modèles)
│   ├── utils/                     # Exception handler, pagination, metrics, ETag, security
│   ├── rate_limiting/             # Multi-strategy (memory/Redis/file)
│   ├── websocket_courses.py       # WS collaboration courses
│   └── websocket/                 # 4 autres WebSockets
├── core/
│   ├── ai/                        # Mistral client, cache sémantique, circuit breaker
│   ├── caching/                   # L1/L2/L3 + Redis
│   ├── config/                    # Pydantic BaseSettings
│   ├── db/                        # Engine, sessions, migrations
│   ├── decorators/                # @avec_session_db, @avec_cache, @avec_resilience
│   ├── models/                    # 32 fichiers ORM (100+ classes)
│   ├── resilience/                # Retry + Timeout + CircuitBreaker
│   └── validation/                # Pydantic schemas + sanitizer
└── services/
    ├── core/
    │   ├── base/                  # BaseAIService (4 mixins)
    │   ├── cron/                  # 68+ jobs (3500+ lignes)
    │   ├── events/                # Pub/Sub event bus
    │   └── registry.py            # @service_factory singleton
    ├── cuisine/                   # RecetteService, ImportService
    ├── famille/                   # JulesAI, WeekendAI
    ├── maison/                    # MaisonService
    ├── jeux/                      # JeuxService
    ├── planning/                  # 5 sous-modules
    ├── inventaire/                # InventaireService
    ├── dashboard/                 # Agrégation multi-module
    ├── integrations/              # Multimodal, webhooks
    └── utilitaires/               # Automations, divers
```

#### Frontend Next.js

```
frontend/src/
├── app/
│   ├── (auth)/                    # Login / Inscription
│   ├── (app)/                     # App protégée (~60 pages)
│   │   ├── cuisine/               # 12 pages
│   │   ├── famille/               # 10 pages
│   │   ├── maison/                # 8 pages
│   │   ├── jeux/                  # 7 pages
│   │   ├── planning/              # 2 pages
│   │   ├── outils/                # 6 pages
│   │   ├── parametres/            # 3 pages + 7 onglets
│   │   ├── admin/                 # 10 pages
│   │   ├── habitat/               # 3 pages
│   │   └── ia-avancee/            # IA avancée
│   └── share/                     # Partage public
├── composants/
│   ├── ui/                        # 29 shadcn/ui
│   ├── disposition/               # 19 layout components
│   ├── cuisine/, famille/, jeux/, maison/, habitat/
│   ├── graphiques/                # Charts réutilisables
│   └── planning/                  # Timeline, calendrier
├── bibliotheque/
│   ├── api/                       # 34 clients API
│   └── validateurs.ts             # 22 schémas Zod
├── crochets/                      # 15 hooks custom
├── magasins/                      # 4 stores Zustand
├── types/                         # 15 fichiers TypeScript
└── fournisseurs/                  # 3 providers React
```

#### SQL

```
sql/
├── INIT_COMPLET.sql               # 4922 lignes, source unique (prod)
├── schema/ (18 fichiers)          # Source de vérité par domaine
└── migrations/ (7 fichiers)       # À consolider dans schema/
```

### Annexe B — WebSockets

| Route WS | Fonction | État |
|----------|----------|------|
| `/ws/courses/{liste_id}` | Collaboration temps réel courses | ✅ (manque fallback HTTP → B2) |
| `/ws/planning` | Collaboration planning | ✅ |
| `/ws/notes` | Édition collaborative notes | ✅ |
| `/ws/projets` | Kanban projets maison | ✅ |
| `/ws/admin/logs` | Streaming logs admin | ✅ (UI non connectée → A6/D3) |

### Annexe C — Données de référence

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
├── produits_de_saison.json          ✅
├── routines_defaut.json             ✅
└── template_import_inventaire.csv   ✅
```

### Annexe D — Canaux de notification par événement

```
Failover: Push → ntfy → WhatsApp → Email
Throttle: 2h par type / canal
```

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
| Stock critique | ✅ | ✅ | ✅ | · |
| Planning vide dimanche | ✅ | · | ✅ | · |
| Digest matinal | · | · | ✅ | · |
| Rapport mensuel | · | · | · | ✅ |

---

## 10. Récapitulatif global & métriques de santé

### Vue synthétique des phases

| Phase | Objectif | Tâches | Semaines | Priorité |
|-------|----------|--------|----------|----------|
| **Phase A** | Stabilisation : bugs critiques, SQL, tests critiques, doc obsolète | 16 | 1-2 | 🔴 BLOQUANT |
| **Phase B** | Fonctionnalités : gaps, IA, CRON, bridges, recherche, tests | 13 | 3-4 | 🟡 HAUTE |
| **Phase C** | UI/UX : visualisations, drag-drop, animations, flux simplifiés | 12 | 5-6 | 🟢 MOYENNE-HAUTE |
| **Phase D** | Admin : console, scheduler, CRON, notifications, refactoring | 12 | 7-8 | 🟢 MOYENNE |
| **Phase E** | Innovations : pilote automatique, widget, Google Home, exports | 12 | 9+ | 🟢 BASSE |
| **TOTAL** | | **65 tâches** | | |

### Dépendances

```
Phase A (Stabilisation) ──── BLOQUANT pour tout
    │
    ├── Phase B (Features)      ──── Après A
    │       │
    │       ├── Phase C (UI/UX)  ──── Après B
    │       │
    │       └── Phase D (Admin)  ──── Après B
    │               │
    │               └── Phase E (Innovations) ──── Après C+D
    │
    └── Docs en parallèle de tout
```

### Métriques de santé projet

| Indicateur | Valeur actuelle | Cible | Statut |
|-----------|----------------|-------|--------|
| Tests backend couverture | ~55% | ≥70% | 🟡 |
| Tests frontend couverture | ~40% | ≥50% | 🔴 |
| Tests E2E | ~10% | ≥30% | 🔴 |
| Docs à jour | ~60% | ≥90% | 🟡 |
| SQL ORM sync | Non vérifié | 100% | ⚠️ |
| Endpoints documentés | ~80% | 100% | 🟡 |
| Bridges inter-modules | 21 actifs | 31 possibles | 🟡 |
| CRON jobs testés | ~30% | ≥70% | 🔴 |
| Bugs critiques ouverts | 4 | 0 | 🔴 |
| Sécurité (OWASP) | Bon (partiel) | Complet | 🟡 |

### Comptage total par catégorie

| Catégorie | Items dans l'analyse | Planifié |
|-----------|---------------------|----------|
| Bugs critiques | 4 | Phase A |
| Bugs importants | 6 | Phase A + D |
| Bugs mineurs | 4 | Backlog |
| Gaps fonctionnels | 23 | Phases B-E |
| Actions SQL | 6 | Phase A |
| Interactions intra-modules à améliorer | 8 | Phases B-E |
| Nouvelles interactions inter-modules | 10 | Phases B-E |
| Opportunités IA | 12 | Phases B-E |
| Nouveaux CRON jobs | 10 | Phases B-D |
| Améliorations notifications | 11 | Phases B-E |
| Améliorations admin | 7 | Phase D |
| Tests manquants prioritaires | 10 | Phases A-D |
| Documentation à créer/MàJ | 17 | Phases A-D |
| Refactoring organisation | 8 | Phase D |
| Améliorations UI/UX | 17 | Phases C-E |
| Visualisations 2D/3D | 13 | Phases C-E |
| Innovations | 14 | Phase E |
| **TOTAL items identifiés** | **~170** | **65 tâches groupées en 5 phases** |

---

> **Document généré le 1er avril 2026**
> Basé intégralement sur les 19 sections de ANALYSE_COMPLETE.md
> **65 tâches planifiées** couvrant **~170 items identifiés** en **5 phases**
> **Note globale app : 7.5/10** — Architecture excellente, pénalisée par la couverture de tests, la dette UX, et 4 bugs critiques de production
