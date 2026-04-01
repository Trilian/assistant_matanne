# Planning d'ImplÃ©mentation â€” Assistant Matanne

> **Date** : 1er Avril 2026
> **Source** : ANALYSE_COMPLETE.md â€” Audit exhaustif intÃ©gral (19 sections)
> **Objectif** : Roadmap complÃ¨te couvrant **tous** les constats de l'analyse : bugs, gaps, SQL, interactions intra/inter-modules, IA, CRON, notifications, admin, tests, docs, UX, visualisations 2D/3D, flux utilisateur, et innovations

---

## Table des matiÃ¨res

- [Planning d'ImplÃ©mentation â€” Assistant Matanne](#planning-dimplÃ©mentation--assistant-matanne)
  - [Table des matiÃ¨res](#table-des-matiÃ¨res)
  - [1. Notation par catÃ©gorie](#1-notation-par-catÃ©gorie)
    - [Note globale : **7.5/10**](#note-globale--7510)
  - [2. Ã‰tat des lieux synthÃ©tique](#2-Ã©tat-des-lieux-synthÃ©tique)
    - [Chiffres clÃ©s](#chiffres-clÃ©s)
    - [Stack technique](#stack-technique)
    - [Modules par domaine](#modules-par-domaine)
    - [Frontend â€” Pages par module](#frontend--pages-par-module)
  - [3. Phase A â€” Stabilisation](#3-phase-a--stabilisation)
  - [4. Phase B â€” FonctionnalitÃ©s \& IA](#4-phase-b--fonctionnalitÃ©s--ia)
  - [5. Phase C â€” UI/UX \& Visualisations](#5-phase-c--uiux--visualisations)
  - [6. Phase D â€” Admin \& Automatisations](#6-phase-d--admin--automatisations)
  - [7. Phase E â€” Innovations](#7-phase-e--innovations)
  - [8. RÃ©fÃ©rentiel complet par section d'analyse](#8-rÃ©fÃ©rentiel-complet-par-section-danalyse)
    - [8.1 Bugs et problÃ¨mes dÃ©tectÃ©s (analyse Â§3)](#81-bugs-et-problÃ¨mes-dÃ©tectÃ©s-analyse-3)
      - [ðŸ”´ Critiques (4)](#-critiques-4)
      - [ðŸŸ¡ Importants (6)](#-importants-6)
      - [ðŸŸ¢ Mineurs (4)](#-mineurs-4)
    - [8.2 Gaps et fonctionnalitÃ©s manquantes (analyse Â§4)](#82-gaps-et-fonctionnalitÃ©s-manquantes-analyse-4)
      - [ðŸ½ï¸ Cuisine (5 gaps)](#ï¸-cuisine-5-gaps)
      - [ðŸ‘¶ Famille (4 gaps)](#-famille-4-gaps)
      - [ðŸ¡ Maison (4 gaps)](#-maison-4-gaps)
      - [ðŸŽ® Jeux (3 gaps)](#-jeux-3-gaps)
      - [ðŸ“… Planning (3 gaps)](#-planning-3-gaps)
      - [ðŸ§° GÃ©nÃ©ral (4 gaps)](#-gÃ©nÃ©ral-4-gaps)
    - [8.3 Consolidation SQL (analyse Â§5)](#83-consolidation-sql-analyse-5)
      - [Structure actuelle](#structure-actuelle)
      - [Actions](#actions)
      - [Workflow simplifiÃ© cible](#workflow-simplifiÃ©-cible)
    - [8.4 Interactions intra-modules (analyse Â§6)](#84-interactions-intra-modules-analyse-6)
      - [Cuisine (interne) â€” âœ… Bien connectÃ©](#cuisine-interne---bien-connectÃ©)
      - [Famille (interne) â€” ðŸ”§ AmÃ©liorable](#famille-interne---amÃ©liorable)
      - [Maison (interne) â€” ðŸ”§ AmÃ©liorable](#maison-interne---amÃ©liorable)
    - [8.5 Interactions inter-modules (analyse Â§7)](#85-interactions-inter-modules-analyse-7)
      - [21 bridges existants âœ…](#21-bridges-existants-)
      - [10 nouvelles interactions Ã  implÃ©menter](#10-nouvelles-interactions-Ã -implÃ©menter)
    - [8.6 OpportunitÃ©s IA (analyse Â§8)](#86-opportunitÃ©s-ia-analyse-8)
      - [IA dÃ©jÃ  en place (9 fonctionnels)](#ia-dÃ©jÃ -en-place-9-fonctionnels)
      - [12 nouvelles opportunitÃ©s](#12-nouvelles-opportunitÃ©s)
    - [8.7 Jobs automatiques CRON (analyse Â§9)](#87-jobs-automatiques-cron-analyse-9)
      - [68+ jobs existants â€” RÃ©sumÃ©](#68-jobs-existants--rÃ©sumÃ©)
      - [10 nouveaux jobs proposÃ©s](#10-nouveaux-jobs-proposÃ©s)
    - [8.8 Notifications (analyse Â§10)](#88-notifications-analyse-10)
      - [Architecture](#architecture)
      - [AmÃ©liorations WhatsApp](#amÃ©liorations-whatsapp)
      - [AmÃ©liorations Email](#amÃ©liorations-email)
      - [AmÃ©liorations Push](#amÃ©liorations-push)
    - [8.9 Mode Admin (analyse Â§11)](#89-mode-admin-analyse-11)
      - [Existant â€” âœ… TrÃ¨s complet](#existant---trÃ¨s-complet)
      - [AmÃ©liorations](#amÃ©liorations)
    - [8.10 Couverture de tests (analyse Â§12)](#810-couverture-de-tests-analyse-12)
      - [Backend â€” ~55% couverture](#backend--55-couverture)
      - [Frontend â€” ~40% couverture](#frontend--40-couverture)
      - [Tests manquants prioritaires](#tests-manquants-prioritaires)
    - [8.11 Documentation (analyse Â§13)](#811-documentation-analyse-13)
      - [Ã‰tat](#Ã©tat)
      - [Documentation Ã  crÃ©er](#documentation-Ã -crÃ©er)
    - [8.12 Organisation \& architecture (analyse Â§14)](#812-organisation--architecture-analyse-14)
      - [Points forts âœ…](#points-forts-)
      - [Points Ã  amÃ©liorer](#points-Ã -amÃ©liorer)
    - [8.13 AmÃ©liorations UI/UX (analyse Â§15)](#813-amÃ©liorations-uiux-analyse-15)
      - [Dashboard](#dashboard)
      - [Navigation](#navigation)
      - [Formulaires](#formulaires)
      - [Mobile](#mobile)
      - [Micro-interactions](#micro-interactions)
    - [8.14 Visualisations 2D/3D (analyse Â§16)](#814-visualisations-2d3d-analyse-16)
      - [Existant](#existant)
      - [Nouvelles visualisations](#nouvelles-visualisations)
    - [8.15 Simplification flux utilisateur (analyse Â§17)](#815-simplification-flux-utilisateur-analyse-17)
      - [ðŸ½ï¸ Flux cuisine (central)](#ï¸-flux-cuisine-central)
      - [ðŸ‘¶ Flux famille quotidien](#-flux-famille-quotidien)
      - [ðŸ¡ Flux maison](#-flux-maison)
      - [Actions rapides FAB mobile](#actions-rapides-fab-mobile)
    - [8.16 Axes d'innovation (analyse Â§18)](#816-axes-dinnovation-analyse-18)
  - [9. Annexes](#9-annexes)
    - [Annexe A â€” Arborescence fichiers clÃ©s](#annexe-a--arborescence-fichiers-clÃ©s)
      - [Backend Python](#backend-python)
      - [Frontend Next.js](#frontend-nextjs)
      - [SQL](#sql)
    - [Annexe B â€” WebSockets](#annexe-b--websockets)
    - [Annexe C â€” DonnÃ©es de rÃ©fÃ©rence](#annexe-c--donnÃ©es-de-rÃ©fÃ©rence)
    - [Annexe D â€” Canaux de notification par Ã©vÃ©nement](#annexe-d--canaux-de-notification-par-Ã©vÃ©nement)
  - [10. RÃ©capitulatif global \& mÃ©triques de santÃ©](#10-rÃ©capitulatif-global--mÃ©triques-de-santÃ©)
    - [Vue synthÃ©tique des phases](#vue-synthÃ©tique-des-phases)
    - [DÃ©pendances](#dÃ©pendances)
    - [MÃ©triques de santÃ© projet](#mÃ©triques-de-santÃ©-projet)
    - [Comptage total par catÃ©gorie](#comptage-total-par-catÃ©gorie)

---

## 1. Notation par catÃ©gorie

> Ã‰valuation au 1er avril 2026 â€” basÃ©e sur l'audit exhaustif

| CatÃ©gorie | Note | Justification |
| ----------- | ------ | --------------- |
| **Architecture backend** | **9/10** | FastAPI + SQLAlchemy 2.0 + Pydantic v2. Patterns exemplaires : service registry `@service_factory`, event bus pub/sub (21 types, 40+ subscribers), cache multi-niveaux (L1/L2/L3/Redis), rÃ©silience composable (retry, timeout, circuit breaker, bulkhead). 38 routeurs, ~250 endpoints, 7 middlewares. |
| **Architecture frontend** | **8/10** | Next.js 16 App Router, React 19, Zustand 5, TanStack Query v5, ~60+ pages, 208+ composants (29 shadcn/ui), 34 clients API, 15 hooks custom. Points nÃ©gatifs : couverture tests ~40%, doubles bibliothÃ¨ques charts (Recharts + Chart.js). |
| **Base de donnÃ©es / SQL** | **8/10** | 80+ tables PostgreSQL, RLS, triggers, vues, 18 fichiers schema ordonnÃ©s. Points nÃ©gatifs : 7 migrations non consolidÃ©es dans les fichiers schema, audit ORMâ†”SQL non exÃ©cutÃ©, index potentiellement manquants. |
| **Couverture tests backend** | **6.5/10** | 74+ fichiers, ~1000 fonctions test, ~55% couverture estimÃ©e. Bien couvert : routes cuisine, services budget, rate limiting. Faible : export PDF (~30%), webhooks (~25%), event bus (~20%), WebSocket (~25%), intÃ©grations (~20%). |
| **Couverture tests frontend** | **4.5/10** | 71 fichiers tests, ~40% couverture. Bien couvert : pages cuisine, stores Zustand. Faible : pages famille/maison/admin (~30%), API clients (~15%), E2E Playwright (~10%). Seuil Vitest 50% â†’ non atteint. |
| **IntÃ©gration IA** | **8.5/10** | Client Mistral unifiÃ© + cache sÃ©mantique + circuit breaker. 9 services IA fonctionnels (suggestions, planning, rescue, batch, weekend, bien-Ãªtre, chat, jules, IA avancÃ©e partielle). 12 nouvelles opportunitÃ©s IA identifiÃ©es. |
| **SystÃ¨me de notifications** | **8/10** | 4 canaux (push VAPID, ntfy.sh, WhatsApp Meta, email Resend), failover intelligent, throttle 2h/type/canal. Points nÃ©gatifs : WhatsApp state non persistÃ© (B9), commandes texte limitÃ©es, pas d'actions dans les push. |
| **Interactions inter-modules** | **8/10** | 21 bridges actifs bien pensÃ©s. 10 nouvelles interactions identifiÃ©es dont 3 haute prioritÃ© (rÃ©colteâ†’recettes, budgetâ†’notifications, documentsâ†’dashboard). |
| **UX / Flux utilisateur** | **5.5/10** | Pages fonctionnelles mais flux courants en 4-6 clics au lieu de 3 max. Pas de drag-drop planning, pas de mode offline courses, pas d'auto-complÃ©tion historique, transitions de page absentes. FAB actions rapides et swipe-to-complete existants mais sous-exploitÃ©s. |
| **Visualisations** | **5/10** | Base prÃ©sente (Recharts heatmaps, camemberts, graphiques ROI, Leaflet cartes). Plan 3D maison (Three.js) non connectÃ© aux donnÃ©es. Manquent : heatmap nutrition, treemap budget, radar Jules, sparklines dashboard, Gantt entretien. |
| **Documentation** | **6/10** | ~60% Ã  jour (35/58 fichiers estimÃ©s). CRON_JOBS.md, NOTIFICATIONS.md, AUTOMATIONS.md obsolÃ¨tes post-phases 8-10. PLANNING_IMPLEMENTATION.md et ROADMAP.md pÃ©rimÃ©s. Docs manquantes : guide CRON complet, guide notifications refonte, guide bridges. |
| **Administration** | **9/10** | Panneau admin trÃ¨s complet : 10 pages frontend, 20+ endpoints, raccourci Ctrl+Shift+A, event bus manuel, feature flags, impersonation, dry-run workflows, IA console, WhatsApp test, export/import config. AmÃ©liorations possibles : console commande rapide, scheduler visuel, replay Ã©vÃ©nements. |
| **Jobs CRON** | **7.5/10** | 68+ jobs bien structurÃ©s (quotidiens, hebdo, mensuels). Points nÃ©gatifs : fichier `jobs.py` monolithique (3500+ lignes), ~30% testÃ©s, 10 nouveaux jobs proposÃ©s (prÃ©diction courses, planning auto, alertes budget). |
| **Infrastructure / DevOps** | **7/10** | Docker, Sentry (50%), Prometheus metrics. Points nÃ©gatifs : pas de CI/CD GitHub Actions, pas de monitoring coÃ»t IA, Sentry pas complet. |
| **SÃ©curitÃ©** | **7/10** | JWT + 2FA TOTP, RLS, rate limiting multi-strategy, security headers, sanitization. Points nÃ©gatifs : B1 (API_SECRET_KEY random par process en multi-worker), B7 (X-Forwarded-For spoofable), B10 (CORS vide en prod sans erreur). |
| **Performance & rÃ©silience** | **8.5/10** | Cache multi-niveaux (L1â†’L2â†’L3â†’Redis), middleware ETag, rÃ©silience composable, rate limiting (60 req/min standard, 10 req/min IA). Metrics capped Ã  500 endpoints (B8). |
| **DonnÃ©es de rÃ©fÃ©rence** | **9/10** | 14+ fichiers JSON/CSV couvrant nutrition, saisons, entretien, jardin, vaccins, soldes, pannes, lessive, nettoyage, domotique, travaux, plantes, routines. |

### Note globale : **7.5/10**

> Application ambitieuse et impressionnante : ~250 endpoints, 80+ tables SQL, ~60+ pages, 208+ composants, 68+ CRON jobs, 21 bridges inter-modules, 4 canaux de notification, 9+ services IA. Architecture professionnelle avec des patterns bien maÃ®trisÃ©s. Principales faiblesses : tests (~50% global), UX multi-clics, bugs critiques de production (auth multi-worker, WebSocket sans fallback), et docs partiellement obsolÃ¨tes.

---

## 2. Ã‰tat des lieux synthÃ©tique

### Chiffres clÃ©s

| MÃ©trique | Valeur |
| ---------- | -------- |
| Routes API (endpoints) | ~250+ |
| Routeurs FastAPI | 38 |
| ModÃ¨les SQLAlchemy (ORM) | 100+ (32 fichiers) |
| SchÃ©mas Pydantic | ~150+ (25 fichiers) |
| Tables SQL | 80+ |
| Pages frontend | ~60+ |
| Composants React | 208+ |
| Clients API frontend | 34 |
| Hooks React custom | 15 |
| Stores Zustand | 4 |
| SchÃ©mas Zod | 22 |
| Fichiers de tests (backend) | 74+ |
| Fichiers de tests (frontend) | 71 |
| CRON jobs | 68+ |
| Bridges inter-modules | 21 |
| Middlewares | 7 couches |
| WebSockets | 5 implÃ©mentations |
| Canaux de notification | 4 (push, ntfy, WhatsApp, email) |

### Stack technique

| Couche | Technologie |
| -------- | ------------- |
| Backend | Python 3.13+, FastAPI 0.109, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 16.2.1, React 19, TypeScript 5, Tailwind CSS v4 |
| Base de donnÃ©es | Supabase PostgreSQL, migrations SQL-file |
| IA | Mistral AI (client custom + cache sÃ©mantique + circuit breaker) |
| Ã‰tat frontend | TanStack Query v5, Zustand 5 |
| Charts | Recharts 3.8, Chart.js 4.5 |
| 3D | Three.js 0.183, @react-three/fiber 9.5 |
| Cartes | Leaflet 1.9, react-leaflet 5.0 |
| Tests | pytest + Vitest 4.1 + Testing Library + Playwright |
| Monitoring | Prometheus, Sentry |
| Notifications | ntfy.sh, Web Push VAPID, Meta WhatsApp Cloud, Resend |

### Modules par domaine

| Module | Routes | Services | Bridges | CRON | Tests | Statut |
| -------- | -------- | ---------- | --------- | ------ | ------- | -------- |
| ðŸ½ï¸ Cuisine/Recettes | 20 | RecetteService, ImportService | 7 | 5 | âœ… Complet | âœ… Mature |
| ðŸ›’ Courses | 20 | CoursesService | 3 | 3 | âœ… Complet | âœ… Mature |
| ðŸ“¦ Inventaire | 14 | InventaireService | 4 | 3 | âœ… Complet | âœ… Mature |
| ðŸ“… Planning | 15 | PlanningService (5 sous-modules) | 5 | 4 | âœ… Complet | âœ… Mature |
| ðŸ§‘â€ðŸ³ Batch Cooking | 8 | BatchCookingService | 1 | 1 | âœ… OK | âœ… Stable |
| â™»ï¸ Anti-Gaspillage | 6 | AntiGaspillageService | 2 | 2 | âœ… OK | âœ… Stable |
| ðŸ’¡ Suggestions IA | 4 | BaseAIService | 0 | 0 | âœ… OK | âœ… Stable |
| ðŸ‘¶ Famille/Jules | 20 | JulesAIService | 7 | 5 | âœ… Complet | âœ… Mature |
| ðŸ¡ Maison | 15+ | MaisonService | 4 | 6 | âœ… OK | âœ… Stable |
| ðŸ  Habitat | 10 | HabitatService | 0 | 2 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸŽ® Jeux | 12 | JeuxService | 1 | 3 | âœ… OK | âœ… Stable |
| ðŸ—“ï¸ Calendriers | 6 | CalendrierService | 2 | 2 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ“Š Dashboard | 3 | DashboardService | 0 | 0 | âœ… OK | âœ… Stable |
| ðŸ“„ Documents | 6 | DocumentService | 1 | 1 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ§° Utilitaires | 10+ | Notes, Journal, Contacts | 1 | 0 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ¤– IA AvancÃ©e | 14 | Multi-service | 0 | 0 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| âœˆï¸ Voyages | 8 | VoyageService | 2 | 1 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| âŒš Garmin | 5 | GarminService | 1 | 1 | âš ï¸ Minimal | ðŸŸ¡ En cours |
| ðŸ” Auth / Admin | 15+ | AuthService | 0 | 0 | âœ… OK | âœ… Stable |
| ðŸ“¤ Export PDF | 3 | RapportService | 0 | 0 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ”” Push / Webhooks | 8 | NotificationService | 0 | 5 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ¤– Automations | 6 | AutomationsEngine | 0 | 1 | âš ï¸ Partiel | ðŸŸ¡ En cours |

### Frontend â€” Pages par module

| Module | Pages | Composants | Tests | Statut |
| -------- | ------- | ------------ | ------- | -------- |
| ðŸ½ï¸ Cuisine | 12 | ~20 | âœ… 8 fichiers | âœ… Mature |
| ðŸ‘¶ Famille | 10 | ~8 | âš ï¸ 3 fichiers | ðŸŸ¡ Gaps |
| ðŸ¡ Maison | 8 | ~15 | âš ï¸ 2 fichiers | ðŸŸ¡ Gaps |
| ðŸ  Habitat | 3 | ~6 | âš ï¸ 1 fichier | ðŸŸ¡ Gaps |
| ðŸŽ® Jeux | 7 | ~12 | âœ… 5 fichiers | âœ… OK |
| ðŸ“… Planning | 2 | ~3 | âœ… 2 fichiers | âœ… OK |
| ðŸ§° Outils | 6 | ~5 | âœ… 6 fichiers | âœ… OK |
| âš™ï¸ ParamÃ¨tres | 3 + 7 onglets | ~7 | âš ï¸ 1 fichier | ðŸŸ¡ Gaps |
| ðŸ”§ Admin | 10 | ~5 | âš ï¸ 2 fichiers | ðŸŸ¡ Gaps |

---

## 3. Phase A â€” Stabilisation âœ… TERMINÃ‰E

> **Objectif** : Corriger les bugs critiques/importants, consolider SQL, couvrir les tests critiques, mettre Ã  jour la doc obsolÃ¨te
> **Semaines** : 1-2
> **PrioritÃ©** : ðŸ”´ BLOQUANT
> **Statut** : âœ… **TerminÃ©e** â€” 16/16 tÃ¢ches complÃ©tÃ©es

| # | TÃ¢che | Source | Effort | CatÃ©gorie | Statut |
| --- | ------- | -------- | -------- | ----------- | -------- |
| A1 | Fixer B1 â€” API_SECRET_KEY random par process (tokens invalides en multi-worker) | Â§3 Bug critique | 1h | SÃ©curitÃ© | âœ… |
| A2 | Fixer B2 â€” WebSocket courses sans fallback HTTP polling | Â§3 Bug critique | 1j | RÃ©silience | âœ… |
| A3 | Fixer B3 â€” Intercepteur auth promise non gÃ©rÃ©e (token expirÃ© â†’ utilisateur bloquÃ©) | Â§3 Bug critique | 2h | Frontend | âœ… |
| A4 | Fixer B4 â€” Event bus en mÃ©moire uniquement (historique perdu au restart) | Â§3 Bug critique | 1j | Core | âœ… |
| A5 | Fixer B5 â€” Rate limiting mÃ©moire non bornÃ© (fuite mÃ©moire lente) â†’ LRU | Â§3 Bug important | 2h | Perf | âœ… |
| A6 | Fixer B7 â€” X-Forwarded-For spoofable (bypass rate limiting) | Â§3 Bug important | 2h | SÃ©curitÃ© | âœ… |
| A7 | Fixer B9 â€” WhatsApp state non persistÃ© (conversation cassÃ©e) â†’ DB | Â§3 Bug important | 1j | WhatsApp | âœ… |
| A8 | Fixer B10 â€” CORS vide en production sans erreur explicite | Â§3 Bug important | 1h | Config | âœ… |
| A9 | ExÃ©cuter audit_orm_sql.py et corriger divergences ORMâ†”SQL (S2) | Â§5 SQL | 1j | SQL | âœ… |
| A10 | Consolider migrations V003-V008 dans les fichiers schema (S3) | Â§5 SQL | 1j | SQL | âœ… |
| A11 | RÃ©gÃ©nÃ©rer INIT_COMPLET.sql propre (S1) | Â§5 SQL | 30min | SQL | âœ… |
| A12 | Tests export PDF (T1) | Â§12 Tests | 1j | Tests | âœ… |
| A13 | Tests webhooks WhatsApp (T2) | Â§12 Tests | 1j | Tests | âœ… |
| A14 | Tests event bus scÃ©narios (T3) | Â§12 Tests | 1j | Tests | âœ… |
| A15 | Mettre Ã  jour CRON_JOBS.md â€” 68+ jobs Ã  documenter (D1) | Â§13 Doc | 2h | Doc | âœ… |
| A16 | Mettre Ã  jour NOTIFICATIONS.md â€” systÃ¨me refait en phase 8 (D2) | Â§13 Doc | 2h | Doc | âœ… |

**Total Phase A : 16/16 tÃ¢ches âœ…**

---

## 4. Phase B â€” FonctionnalitÃ©s & IA âœ… TERMINÃ‰E

> **Objectif** : Combler les gaps fonctionnels, enrichir l'IA, ajouter les CRON et inter-modules critiques
> **Semaines** : 3-4
> **PrioritÃ©** : ðŸŸ¡ HAUTE
> **Statut** : âœ… **TerminÃ©e** â€” 13/13 tÃ¢ches complÃ©tÃ©es

| # | TÃ¢che | Source | Effort | CatÃ©gorie | Statut |
| --- | ------- | -------- | -------- | ----------- | -------- |
| B1 | G5 â€” Mode hors-ligne courses (PWA cache offline en magasin) | Â§4 Gap | 3j | PWA | âœ… |
| B2 | IA1 â€” PrÃ©diction courses intelligente (historique â†’ prÃ©-remplir liste) | Â§8 IA | 3j | IA | âœ… |
| B3 | J2 â€” CRON planning auto semaine (dimanche 19h si planning vide) | Â§9 CRON | 2j | CRON | âœ… |
| B4 | J9 â€” CRON alertes budget seuil (quotidien 20h, catÃ©gorie > 80%) | Â§9 CRON | 1j | CRON | âœ… |
| B5 | W2 â€” Commandes WhatsApp enrichies ("ajoute du lait", "budget ce mois") via Mistral NLP | Â§10 WhatsApp | 3j | WhatsApp | âœ… |
| B6 | I1 â€” Bridge rÃ©colte jardin â†’ recettes semaine suivante | Â§7 Inter-module | 2j | Bridge | âœ… |
| B7 | I3 â€” Bridge budget anomalie â†’ notification proactive (+30% restaurants) | Â§7 Inter-module | 2j | Bridge | âœ… |
| B8 | I5 â€” Bridge documents expirÃ©s â†’ dashboard alerte widget | Â§7 Inter-module | 1j | Bridge | âœ… |
| B9 | IA5 â€” RÃ©sumÃ© hebdomadaire IA intelligent (narratif : repas, tÃ¢ches, budget, scores) | Â§8 IA | 2j | IA | âœ… |
| B10 | IA8 â€” Suggestion batch cooking intelligent (planning + appareils â†’ timeline optimale) | Â§8 IA | 3j | IA | âœ… |
| B11 | G20 â€” Recherche globale complÃ¨te (Ctrl+K â†’ couvrir notes, jardin, contrats) | Â§4 Gap | 3j | Frontend | âœ… |
| B12 | Tests pages famille frontend (T8 Ã©tendu) | Â§12 Tests | 2j | Tests | âœ… |
| B13 | Tests E2E parcours utilisateur complet (T6) | Â§12 Tests | 3j | Tests | âœ… |

**Total Phase B : 13/13 tÃ¢ches âœ…**

---

## 5. Phase C â€” UI/UX & Visualisations

> **Objectif** : Rendre l'interface belle, moderne, fluide. Enrichir les visualisations de donnÃ©es
> **Semaines** : 5-6
> **PrioritÃ©** : ðŸŸ¢ MOYENNE-HAUTE

| # | TÃ¢che | Source | Effort | CatÃ©gorie |
| --- | ------- | -------- | -------- | ----------- |
| C1 | U1 â€” Dashboard widgets drag-drop (`@dnd-kit/core`) | Â§15 UI | 2j | UI |
| C2 | IN3 â€” Page "Ma journÃ©e" unifiÃ©e (repas + tÃ¢ches + routines + mÃ©tÃ©o + anniversaires) | Â§18 Innovation | 3j | Innovation |
| C3 | V1 â€” Plan 3D maison interactif (connecter aux donnÃ©es rÃ©elles : tÃ¢ches par piÃ¨ce, Ã©nergie) | Â§16 3D | 5j | 3D |
| C4 | V4 â€” Calendrier nutritionnel heatmap (type GitHub contributions, rouge â†’ vert) | Â§16 2D | 2j | 2D |
| C5 | V5 â€” Treemap budget (proportionnel, cliquable drill-down) | Â§16 2D | 2j | 2D |
| C6 | V7 â€” Radar skill Jules (motricitÃ©, langage, social, cognitif vs normes OMS) | Â§16 2D | 1j | 2D |
| C7 | V8 â€” Sparklines dans cartes dashboard (tendance 7 jours) | Â§16 2D | 1j | 2D |
| C8 | U7 â€” Transitions de page fluides (framer-motion ou View Transitions API) | Â§15 UI | 2j | UI |
| C9 | U12 â€” Swipe actions sur toutes les listes (courses, tÃ¢ches, recettes) | Â§15 Mobile | 1j | Mobile |
| C10 | U16 â€” Compteurs animÃ©s dashboard (incrÃ©mentation visuelle) | Â§15 UI | 1j | UI |
| C11 | U9 â€” Auto-complÃ©tion intelligente formulaires (basÃ©e sur historique) | Â§15 UX | 2j | UX |
| C12 | IN4 â€” Suggestions proactives contextuelles (banniÃ¨re IA en haut de chaque module) | Â§18 Innovation | 3j | Innovation |

**Total Phase C : 12 tÃ¢ches**

---

## 6. Phase D â€” Admin & Automatisations

> **Objectif** : Enrichir le mode admin, ajouter les CRON manquants, amÃ©liorer les notifications
> **Semaines** : 7-8
> **PrioritÃ©** : ðŸŸ¢ MOYENNE

| # | TÃ¢che | Source | Effort | CatÃ©gorie |
| --- | ------- | -------- | -------- | ----------- |
| D1 | A1 â€” Console commande rapide admin (champ texte : "run job X", "clear cache Y") | Â§11 Admin | 2j | Admin |
| D2 | A3 â€” Scheduler visuel CRON (timeline 68 jobs, prochain run, dÃ©pendances) | Â§11 Admin | 3j | Admin |
| D3 | A6 â€” Logs temps rÃ©el via WebSocket admin_logs (endpoint existant â†’ connecter UI) | Â§11 Admin | 2j | Admin |
| D4 | J1 â€” CRON prÃ©diction courses hebdo (vendredi 16h) | Â§9 CRON | 1j | CRON |
| D5 | J4 â€” CRON rappels jardin saisonniers (hebdo lundi) | Â§9 CRON | 1j | CRON |
| D6 | J6 â€” CRON vÃ©rification santÃ© systÃ¨me (horaire â†’ alerte ntfy si service down) | Â§9 CRON | 1j | CRON |
| D7 | J7 â€” CRON backup auto hebdo JSON (dimanche 04h) | Â§9 CRON | 1j | CRON |
| D8 | W1 â€” WhatsApp state persistence (Redis/DB pour multi-turn) | Â§10 WhatsApp | 2j | Notifications |
| D9 | E1 â€” Templates email HTML/MJML pour rapports mensuels | Â§10 Email | 2j | Notifications |
| D10 | O1 â€” DÃ©couper jobs.py monolithique (3500+ lignes) en modules par domaine | Â§14 Refactoring | 1j | Nettoyage |
| D11 | O3 â€” Archiver scripts legacy dans `scripts/_archive/` | Â§14 Refactoring | 30min | Nettoyage |
| D12 | O4 â€” Standardiser sur Recharts, retirer Chart.js | Â§14 Refactoring | 1j | Nettoyage |

**Total Phase D : 12 tÃ¢ches**

---

## 7. Phase E â€” Innovations

> **Objectif** : Features diffÃ©renciantes et visionnaires
> **Semaines** : 9+
> **PrioritÃ©** : ðŸŸ¢ BASSE

| # | TÃ¢che | Source | Effort | CatÃ©gorie |
| --- | ------- | -------- | -------- | ----------- |
| E1 | IN1 â€” Mode "Pilote automatique" (IA gÃ¨re planning/courses/rappels, utilisateur valide) | Â§18 Innovation | 5j | Innovation |
| E2 | IN2 â€” Widget tablette Google (repas du jour, tÃ¢che, mÃ©tÃ©o, timer) | Â§18 Innovation | 4j | Innovation |
| E3 | IN10 â€” Score famille hebdomadaire composite (nutrition + dÃ©penses + activitÃ©s + entretien) | Â§18 Innovation | 2j | Innovation |
| E4 | IN14 â€” Mode "invitÃ©" conjoint (vue simplifiÃ©e : courses, planning, routines) | Â§18 Innovation | 2j | Innovation |
| E5 | V9 â€” Graphe rÃ©seau modules admin (D3.js force graph, 21 bridges visuels) | Â§16 3D | 2j | Visualisation |
| E6 | V10 â€” Timeline Gantt entretien maison (Recharts, planification annuelle) | Â§16 2D | 2j | Visualisation |
| E7 | V2 â€” Vue jardin 2D/3D (zones plantation, Ã©tat plantes, calendrier arrosage) | Â§16 3D | 3j | Visualisation |
| E8 | IN5 â€” Journal familial automatique (IA gÃ©nÃ¨re rÃ©sumÃ© semaine exportable PDF) | Â§18 Innovation | 3j | Innovation |
| E9 | IN11 â€” Rapport mensuel PDF export (graphiques + rÃ©sumÃ© narratif IA) | Â§18 Innovation | 3j | Innovation |
| E10 | IN8 â€” Google Home routines Ã©tendues ("Bonsoir" â†’ repas demain + tÃ¢ches) | Â§18 Innovation | 4j | Innovation |
| E11 | G17 â€” Sync Google Calendar bidirectionnelle complÃ¨te | Â§4 Gap | 4j | Gap |
| E12 | IA4 â€” Assistant vocal Ã©tendu (intents Google Assistant enrichis) | Â§8 IA | 4j | IA |

**Total Phase E : 12 tÃ¢ches**

---

## 8. RÃ©fÃ©rentiel complet par section d'analyse

### 8.1 Bugs et problÃ¨mes dÃ©tectÃ©s (analyse Â§3)

#### ðŸ”´ Critiques (4)

| # | Bug | Module | Impact | Phase |
| --- | ----- | -------- | -------- | ------- |
| B1 | **API_SECRET_KEY random par process** â€” chaque worker gÃ©nÃ¨re un secret diffÃ©rent â†’ tokens invalides en multi-worker | Auth | Tokens invalides en prod | A1 |
| B2 | **WebSocket courses sans fallback HTTP** â€” proxy restrictif/3G â†’ collaboration casse silencieusement | Courses | Perte de sync temps rÃ©el | A2 |
| B3 | **Promesse non gÃ©rÃ©e intercepteur auth** â€” refresh token timeout â†’ utilisateur ni connectÃ© ni dÃ©connectÃ© | Frontend Auth | UX dÃ©gradÃ©e | A3 |
| B4 | **Event bus en mÃ©moire uniquement** â€” historique perdu au redÃ©marrage, impossible de rejouer | Core Events | Perte audit trail | A4 |

#### ðŸŸ¡ Importants (6)

| # | Bug | Module | Impact | Phase |
| --- | ----- | -------- | -------- | ------- |
| B5 | **Rate limiting mÃ©moire non bornÃ©** â€” chaque IP/user unique sans Ã©viction â†’ fuite mÃ©moire | Rate Limiting | Memory leak prod | A5 |
| B6 | **Maintenance mode cache 5s** â€” requÃªtes acceptÃ©es pendant la transition | Admin | RequÃªtes pendant maintenance | D (si temps) |
| B7 | **X-Forwarded-For spoofable** â€” bypass rate limiting | SÃ©curitÃ© | Rate limiting contournable | A6 |
| B8 | **Metrics capped 500 endpoints / 1000 samples** â€” percentiles imprÃ©cis | Monitoring | MÃ©triques dÃ©gradÃ©es | D (si temps) |
| B9 | **WhatsApp multi-turn sans persistence** â€” state machine perd Ã©tat entre messages | WhatsApp | Conversation cassÃ©e | A7 |
| B10 | **CORS vide en production** â€” frontend bloquÃ© sans config explicite | Config | Frontend bloquÃ© | A8 |

#### ðŸŸ¢ Mineurs (4)

| # | Bug | Module | Phase |
| --- | ----- | -------- | ------- |
| B11 | ResponseValidationError loggÃ© en 500 sans contexte debug | API | Backlog |
| B12 | Pagination cursor â€” suppressions concurrentes sautent des enregistrements | Pagination | Backlog |
| B13 | ServiceMeta auto-sync wrappers non testÃ©e exhaustivement | Core | Backlog |
| B14 | Sentry intÃ©gration Ã  50% â€” erreurs frontend non tracÃ©es | Frontend | B (si temps) |

---

### 8.2 Gaps et fonctionnalitÃ©s manquantes (analyse Â§4)

#### ðŸ½ï¸ Cuisine (5 gaps)

| # | Gap | PrioritÃ© | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G1 | **Drag-drop recettes dans planning** â€” UX fastidieuse sans | Moyenne | 2j | C |
| G2 | **Import recettes par photo** â€” Pixtral disponible cÃ´tÃ© IA | Moyenne | 3j | B/C |
| G3 | **Partage recette via WhatsApp** avec preview | Basse | 1j | D |
| G4 | **Veille prix articles dÃ©sirÃ©s** â€” scraper API Dealabs/Idealo + alertes soldes via `calendrier_soldes.json` | Moyenne | 3j | E |
| G5 | **Mode hors-ligne courses** â€” PWA sans cache offline en magasin | Haute | 3j | B1 |

#### ðŸ‘¶ Famille (4 gaps)

| # | Gap | PrioritÃ© | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G6 | **PrÃ©vision budget IA** â€” pas de prÃ©diction "fin de mois" | Haute | 3j | B |
| G7 | **Timeline Jules visuelle** â€” frise chronologique interactive des jalons | Moyenne | 2j | C |
| G8 | **Export calendrier anniversaires** vers Google Calendar | Basse | 1j | E |
| G9 | **Photos souvenirs liÃ©es aux activitÃ©s** â€” upload photo pour le journal | Moyenne | 2j | D |

#### ðŸ¡ Maison (4 gaps)

| # | Gap | PrioritÃ© | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G10 | **Plan 3D interactif limitÃ©** â€” Three.js non connectÃ© aux donnÃ©es rÃ©elles | Haute | 5j | C3 |
| G11 | **Historique Ã©nergie avec graphes** â€” pas de courbes mois/annÃ©e | Moyenne | 2j | C |
| G12 | **Catalogue artisans enrichi** â€” pas d'avis/notes, pas de recherche par mÃ©tier | Basse | 2j | E |
| G13 | **Devis comparatif** â€” pas de visualisation comparative devis pour un projet | Moyenne | 3j | E |

#### ðŸŽ® Jeux (3 gaps)

| # | Gap | PrioritÃ© | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G14 | **Graphique ROI temporel** â€” pas de courbe Ã©volution mensuelle ROI | Haute | 2j | C |
| G15 | **Alertes cotes temps rÃ©el** â€” alerte quand cote atteint seuil dÃ©fini | Moyenne | 3j | D |
| G16 | **Comparaison stratÃ©gies loto** â€” backtest cÃ´te Ã  cÃ´te 2+ stratÃ©gies | Basse | 2j | E |

#### ðŸ“… Planning (3 gaps)

| # | Gap | PrioritÃ© | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G17 | **Sync Google Calendar bidirectionnelle** â€” export iCal existe, sync ~60% | Haute | 4j | E11 |
| G18 | **Planning familial consolidÃ© visuel** â€” pas de Gantt repas + activitÃ©s + entretien | Moyenne | 3j | C |
| G19 | **RÃ©currence d'Ã©vÃ©nements** â€” pas de "tous les mardis" natif | Moyenne | 2j | D |

#### ðŸ§° GÃ©nÃ©ral (4 gaps)

| # | Gap | PrioritÃ© | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G20 | **Recherche globale incomplÃ¨te** â€” Ctrl+K manque notes, jardin, contrats | Haute | 3j | B11 |
| G21 | **Mode hors-ligne PWA** â€” Service Worker enregistrÃ© mais pas de stratÃ©gie structurÃ©e | Haute | 5j | B/E |
| G22 | **Onboarding interactif** â€” composant tour-onboarding existe mais pas activÃ© | Moyenne | 3j | D |
| G23 | **Export donnÃ©es backup incomplet** â€” export JSON OK, import/restauration UI incomplet | Moyenne | 2j | D |

---

### 8.3 Consolidation SQL (analyse Â§5)

#### Structure actuelle

```
sql/
â”œâ”€â”€ INIT_COMPLET.sql          # Auto-gÃ©nÃ©rÃ© (4922 lignes, 18 fichiers)
â”œâ”€â”€ schema/                   # 18 fichiers ordonnÃ©s (01_extensions â†’ 99_footer)
â””â”€â”€ migrations/               # 7 fichiers (V003-V008) + README
```

#### Actions

| # | Action | PrioritÃ© | Phase |
| --- | -------- | ---------- | ------- |
| S1 | RÃ©gÃ©nÃ©rer INIT_COMPLET.sql (`python scripts/db/regenerate_init.py`) | Haute | A11 |
| S2 | Audit ORMâ†”SQL (`python scripts/audit_orm_sql.py`) et corriger divergences | Haute | A9 |
| S3 | Consolider 7 migrations dans les fichiers schema â€” source unique | Haute | A10 |
| S4 | VÃ©rifier index manquants (user_id, date, statut) dans `14_indexes.sql` | Moyenne | B |
| S5 | Nettoyer tables inutilisÃ©es (80+ tables toutes ont ORM + route ?) | Basse | E |
| S6 | VÃ©rifier vues SQL (`17_views.sql`) rÃ©ellement utilisÃ©es par le backend | Basse | E |

#### Workflow simplifiÃ© cible

```
1. Modifier le fichier schema appropriÃ© (ex: sql/schema/04_cuisine.sql)
2. ExÃ©cuter: python scripts/db/regenerate_init.py
3. Appliquer: INIT_COMPLET.sql sur Supabase (SQL Editor)
4. VÃ©rifier: python scripts/audit_orm_sql.py
```

---

### 8.4 Interactions intra-modules (analyse Â§6)

#### Cuisine (interne) â€” âœ… Bien connectÃ©

```
Recettes â”€â”€â”€â”€ planifiÃ©es â”€â”€â”€â†’ Planning
    â”‚                            â”‚
    â”‚                            â”œâ”€â”€ gÃ©nÃ¨re â”€â”€â†’ Courses
    â”‚                            â”‚
    â””â”€â”€ version Jules â”€â”€â†’ portions adaptÃ©es
                                 â”‚
Inventaire â—„â”€â”€â”€â”€â”€â”€ checkout â”€â”€â”€â”€â”˜
    â”‚
    â”œâ”€â”€ pÃ©remption â”€â”€â†’ Anti-Gaspillage â”€â”€â†’ Recettes rescue
    â”‚
    â””â”€â”€ stock bas â”€â”€â†’ Automation â”€â”€â†’ Courses auto

Batch Cooking â—„â”€â”€ planning semaine â”€â”€ prÃ©pare â”€â”€â†’ bloque planning
```

**Ã€ amÃ©liorer :**
| # | AmÃ©lioration | Phase |
| --- | ------------- | ------- |
| IM-C1 | Checkout courses â†’ MAJ prix moyens inventaire automatiquement | D |
| IM-C2 | Batch cooking "mode robot" â€” optimiser ordre Ã©tapes par appareil | E |

#### Famille (interne) â€” ðŸ”§ AmÃ©liorable

```
Jules profil â”€â”€â†’ jalons developpement â”€â”€â†’ notifications jalon
Budget â—„â”€â”€â”€â”€ dÃ©penses catÃ©gorisÃ©es
Routines â”€â”€â†’ check quotidien â”€â”€â†’ gamification
Anniversaires â”€â”€â†’ checklist â”€â”€â†’ budget cadeau
Documents â”€â”€â†’ expiration â”€â”€â†’ rappels calendrier
```

**Ã€ amÃ©liorer :**
| # | AmÃ©lioration | Phase |
| --- | ------------- | ------- |
| IM-F1 | Jules jalons â†’ suggestions activitÃ©s adaptÃ©es Ã¢ge (IA contextuelle) | B |
| IM-F2 | Budget anomalies â†’ notification proactive ("tu dÃ©penses +30% en X") | B7 |
| IM-F3 | Routines â†’ tracking complÃ©tion visuel (streak) | C |

#### Maison (interne) â€” ðŸ”§ AmÃ©liorable

```
Projets â”€â”€â†’ tÃ¢ches â”€â”€â†’ devis â”€â”€â†’ dÃ©penses
Entretien â”€â”€â†’ calendrier â”€â”€â†’ produits nÃ©cessaires
Jardin â”€â”€â†’ arrosage/rÃ©colte â”€â”€â†’ saison
Ã‰nergie â”€â”€â†’ relevÃ©s compteurs â”€â”€â†’ historique
Stocks (cellier) â”€â”€â†’ consolidÃ© avec inventaire cuisine
```

**Ã€ amÃ©liorer :**
| # | AmÃ©lioration | Phase |
| --- | ------------- | ------- |
| IM-M1 | Projets â†’ timeline Gantt visuelle des travaux | C/E6 |
| IM-M2 | Ã‰nergie â†’ graphe Ã©volution + comparaison N vs N-1 | C (V11) |
| IM-M3 | Entretien â†’ suggestions IA proactives ("chaudiÃ¨re 8 ans â†’ rÃ©vision") | D |

---

### 8.5 Interactions inter-modules (analyse Â§7)

#### 21 bridges existants âœ…

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ CUISINE  â”‚â—„â”€â”€â”€â–ºâ”‚ PLANNING  â”‚â—„â”€â”€â”€â–ºâ”‚ COURSES  â”‚
â”‚ recettes â”‚     â”‚ repas     â”‚     â”‚ listes   â”‚
â”‚ inventaireâ”‚    â”‚ semaine   â”‚     â”‚ articles â”‚
â”‚ nutrition â”‚    â”‚ conflits  â”‚     â”‚          â”‚
â”‚ batch     â”‚    â”‚           â”‚     â”‚          â”‚
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
     â”‚                 â”‚                 â”‚
     â”‚    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤                 â”‚
     â”‚    â”‚            â”‚                 â”‚
â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â–¼â”€â”€â”   â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”
â”‚  FAMILLE   â”‚   â”‚  MAISON  â”‚     â”‚  BUDGET  â”‚
â”‚ jules      â”‚   â”‚ entretienâ”‚     â”‚ famille  â”‚
â”‚ routines   â”‚   â”‚ jardin   â”‚     â”‚ jeux (sÃ©parÃ©)
â”‚ annivers.  â”‚   â”‚ Ã©nergie  â”‚     â”‚ maison   â”‚
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â”‚                â”‚
     â”‚    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â–¼â”€â”€â”   â”Œâ”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”
â”‚ CALENDRIER â”‚   â”‚  JEUX    â”‚
â”‚ google cal â”‚   â”‚ paris    â”‚
â”‚ Ã©vÃ©nements â”‚   â”‚ loto     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

| # | Bridge | De â†’ Vers | Ã‰tat |
| --- | -------- | ----------- | ------ |
| 1 | `inter_module_inventaire_planning` | Stock â†’ Planning | âœ… |
| 2 | `inter_module_jules_nutrition` | Jules â†’ Recettes | âœ… |
| 3 | `inter_module_saison_menu` | Saison â†’ Planning | âœ… |
| 4 | `inter_module_courses_budget` | Courses â†’ Budget | âœ… |
| 5 | `inter_module_batch_inventaire` | Batch â†’ Inventaire | âœ… |
| 6 | `inter_module_planning_voyage` | Voyage â†’ Planning | âœ… |
| 7 | `inter_module_peremption_recettes` | PÃ©remption â†’ Recettes | âœ… |
| 8 | `inter_module_documents_calendrier` | Documents â†’ Calendrier | âœ… |
| 9 | `inter_module_meteo_activites` | MÃ©tÃ©o â†’ ActivitÃ©s | âœ… |
| 10 | `inter_module_weekend_courses` | Weekend â†’ Courses | âœ… |
| 11 | `inter_module_voyages_budget` | Voyages â†’ Budget | âœ… |
| 12 | `inter_module_anniversaires_budget` | Anniversaires â†’ Budget | âœ… |
| 13 | `inter_module_budget_jeux` | Jeux â†” Budget | âœ… (info seulement, budgets sÃ©parÃ©s) |
| 14 | `inter_module_garmin_health` | Garmin â†’ Dashboard | âœ… |
| 15 | `inter_module_entretien_courses` | Entretien â†’ Courses | âœ… |
| 16 | `inter_module_jardin_entretien` | Jardin â†’ Entretien | âœ… |
| 17 | `inter_module_charges_energie` | Charges â†’ Ã‰nergie | âœ… |
| 18 | `inter_module_energie_cuisine` | Ã‰nergie â†’ Cuisine | âœ… |
| 19 | `inter_module_chat_contexte` | Tous â†’ Chat IA | âœ… |
| 20 | `inter_module_voyages_calendrier` | Voyages â†’ Calendrier | âœ… |
| 21 | `inter_module_garmin_planning` | Garmin â†’ Planning | âš ï¸ Partiel |

#### 10 nouvelles interactions Ã  implÃ©menter

| # | Interaction | De â†’ Vers | Valeur | Effort | Phase |
| --- | ------------ | ----------- | -------- | -------- | ------- |
| I1 | **RÃ©colte jardin â†’ Recettes semaine suivante** | Jardin â†’ Planning | âœ… AcceptÃ©e | 2j | B6 |
| I2 | **Entretien rÃ©current â†’ Planning unifiÃ©** | Entretien â†’ Planning | Haute | 2j | D |
| I3 | **Budget anomalie â†’ Notification proactive** | Budget â†’ Notifs | Haute | 2j | B7 |
| I4 | **Voyages â†’ Inventaire** (dÃ©stockage avant dÃ©part) | Voyages â†’ Inventaire | Moyenne | 1j | D |
| I5 | **Documents expirÃ©s â†’ Dashboard alerte** | Documents â†’ Dashboard | Haute | 1j | B8 |
| I6 | **Anniversaire proche â†’ Suggestions cadeaux IA** | Anniversaires â†’ IA | Moyenne | 2j | E |
| I7 | **Contrats/Garanties â†’ Dashboard widgets** | Maison â†’ Dashboard | Moyenne | 1j | D |
| I8 | **MÃ©tÃ©o â†’ Entretien maison** (gel â†’ penser au jardin) | MÃ©tÃ©o â†’ Maison | Moyenne | 2j | D |
| I9 | **Planning sport Garmin â†’ Planning repas** (adapter alimentation) | Garmin â†’ Cuisine | Moyenne | 3j | E |
| I10 | **Courses historique â†’ PrÃ©diction prochaine liste** | Courses â†’ IA | Haute | 3j | B2 |

---

### 8.6 OpportunitÃ©s IA (analyse Â§8)

#### IA dÃ©jÃ  en place (9 fonctionnels)

| FonctionnalitÃ© | Service | Module | Statut |
| ---------------- | --------- | -------- | -------- |
| Suggestions recettes | BaseAIService | Cuisine | âœ… |
| GÃ©nÃ©ration planning IA | PlanningService | Planning | âœ… |
| Recettes rescue anti-gaspi | AntiGaspillageService | Cuisine | âœ… |
| Batch cooking optimisÃ© | BatchCookingService | Cuisine | âœ… |
| Suggestions weekend | WeekendAIService | Famille | âœ… |
| Score bien-Ãªtre | DashboardService | Dashboard | âœ… |
| Chat IA contextualisÃ© | AssistantService | Outils | âœ… |
| Version Jules recettes | JulesAIService | Famille | âœ… |
| 14 endpoints IA avancÃ©e | Multi-services | IA AvancÃ©e | âš ï¸ Partiel |

#### 12 nouvelles opportunitÃ©s

| # | OpportunitÃ© | Module(s) | PrioritÃ© | Effort | Phase |
| --- | ------------- | ----------- | ---------- | -------- | ------- |
| IA1 | **PrÃ©diction courses intelligente** â€” historique â†’ prÃ©-remplir liste | Courses + IA | ðŸ”´ | 3j | B2 |
| IA2 | **Planificateur adaptatif** mÃ©tÃ©o+stock+budget â€” endpoint sous-utilisÃ© | Planning + Multi | ðŸ”´ | 2j | B |
| IA3 | **Diagnostic pannes maison** â€” photo Pixtral â†’ diagnostic + action | Maison | ðŸŸ¡ | 3j | D |
| IA4 | **Assistant vocal contextuel Ã©tendu** â€” Google Assistant intents enrichis | Tous | ðŸŸ¡ | 4j | E12 |
| IA5 | **RÃ©sumÃ© hebdomadaire intelligent** â€” narratif agrÃ©able Ã  lire | Dashboard | ðŸ”´ | 2j | B9 |
| IA6 | **Optimisation Ã©nergie prÃ©dictive** â€” relevÃ©s + mÃ©tÃ©o â†’ prÃ©diction facture | Maison/Ã‰nergie | ðŸŸ¡ | 3j | E |
| IA7 | **Analyse nutritionnelle photo** â€” Pixtral â†’ calories/macros estimÃ©s | Cuisine | ðŸŸ¡ | 3j | E |
| IA8 | **Suggestion batch cooking intelligent** â€” planning + appareils â†’ timeline | Batch Cooking | ðŸ”´ | 3j | B10 |
| IA9 | **Jules conseil dÃ©veloppement proactif** â€” suggestions Ã¢ge + jalons | Famille/Jules | ðŸŸ¡ | 2j | D |
| IA10 | **Auto-catÃ©gorisation budget** â€” commerÃ§ant/article â†’ catÃ©gorie (pas OCR) | Budget | ðŸŸ¡ | 2j | D |
| IA11 | **GÃ©nÃ©ration checklist voyage** â€” destination + dates â†’ checklist IA | Voyages | ðŸŸ¡ | 2j | D |
| IA12 | **Score Ã©cologique repas** â€” saisonnalitÃ©, distance, vÃ©gÃ©tal vs animal | Cuisine | ðŸŸ¢ | 2j | E |

---

### 8.7 Jobs automatiques CRON (analyse Â§9)

#### 68+ jobs existants â€” RÃ©sumÃ©

**Quotidiens :**
- 06h00 : sync Garmin
- 07h00 : pÃ©remptions, rappels famille, alerte stock bas
- 07h30 : digest WhatsApp matinal
- 08h00 : rappels maison
- 09h00 : digest ntfy
- 18h00 : rappel courses, push contextuel soir
- 23h00 : sync Google Calendar
- 5 min : runner automations

**Hebdomadaires :**
- Lundi 07h30 : rÃ©sumÃ© hebdo
- Vendredi 17h00 : score weekend
- Dimanche 03h00 : sync OpenFoodFacts
- Dimanche 20h00 : score bien-Ãªtre, points gamification

**Mensuels :**
- 1er 08h15 : rapport budget
- 1er 09h00 : contrÃ´le contrats/garanties
- 1er 09h30 : rapport maison

#### 10 nouveaux jobs proposÃ©s

| # | Job | FrÃ©quence | Modules | PrioritÃ© | Phase |
| --- | ----- | ----------- | --------- | ---------- | ------- |
| J1 | **PrÃ©diction courses hebdo** | Vendredi 16h | Courses + IA | ðŸ”´ | D4 |
| J2 | **Planning auto semaine** (si vide â†’ propose via WhatsApp) | Dimanche 19h | Planning + IA | ðŸ”´ | B3 |
| J3 | **Nettoyage cache/exports** (> 7 jours) | Quotidien 02h | Export | ðŸŸ¡ | D |
| J4 | **Rappel jardin saison** | Hebdo (Lundi) | Jardin | ðŸŸ¡ | D5 |
| J5 | **Sync budget consolidation** (tous modules) | Quotidien 22h | Budget | ðŸŸ¡ | D |
| J6 | **VÃ©rification santÃ© systÃ¨me** | Horaire | Admin | ðŸŸ¡ | D6 |
| J7 | **Backup auto JSON** | Hebdo (Dimanche 04h) | Admin | ðŸŸ¢ | D7 |
| J8 | **Tendances nutrition hebdo** | Dimanche 18h | Cuisine/Nutrition | ðŸŸ¡ | E |
| J9 | **Alertes budget seuil** (catÃ©gorie > 80%) | Quotidien 20h | Budget | ðŸ”´ | B4 |
| J10 | **Rappel activitÃ© Jules** ("Jules a X mois â†’ activitÃ©s recommandÃ©es") | Quotidien 09h | Famille | ðŸŸ¡ | D |

---

### 8.8 Notifications (analyse Â§10)

#### Architecture

```
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚  Ã‰vÃ©nement      â”‚
                    â”‚  (CRON / User)  â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚  Router de      â”‚
                    â”‚  notifications  â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚                â”‚                â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”
    â”‚  Web Push    â”‚ â”‚   ntfy.sh    â”‚ â”‚ WhatsApp   â”‚
    â”‚  (VAPID)     â”‚ â”‚  (open src)  â”‚ â”‚ (Meta API) â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚    Email        â”‚
                    â”‚   (Resend)      â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
    Failover: Push â†’ ntfy â†’ WhatsApp â†’ Email
    Throttle: 2h par type d'Ã©vÃ©nement par canal
```

#### AmÃ©liorations WhatsApp

| # | AmÃ©lioration | PrioritÃ© | Effort | Phase |
| --- | ------------- | ---------- | -------- | ------- |
| W1 | Persistence Ã©tat conversation multi-turn (Redis/DB) | ðŸ”´ | 2j | D8 |
| W2 | Commandes texte enrichies ("ajoute du lait", "budget ce mois") via NLP Mistral | ðŸ”´ | 3j | B5 |
| W3 | Boutons interactifs Ã©tendus (valider courses, noter dÃ©pense, signaler panne) | ðŸŸ¡ | 2j | D |
| W4 | Photo â†’ action (plante malade â†’ diagnostic, plat â†’ identification recette) | ðŸŸ¡ | 3j | E |
| W5 | RÃ©sumÃ© quotidien personnalisable (choix infos via paramÃ¨tres) | ðŸŸ¡ | 2j | D |

#### AmÃ©liorations Email

| # | AmÃ©lioration | PrioritÃ© | Effort | Phase |
| --- | ------------- | ---------- | -------- | ------- |
| E1 | Templates HTML/MJML jolis pour rapports mensuels | ðŸŸ¡ | 2j | D9 |
| E2 | RÃ©sumÃ© hebdo email optionnel | ðŸŸ¡ | 1j | D |
| E3 | Alertes critiques par email (document expirÃ©, stock critique, budget dÃ©passÃ©) | ðŸ”´ | 1j | B |

#### AmÃ©liorations Push

| # | AmÃ©lioration | PrioritÃ© | Effort | Phase |
| --- | ------------- | ---------- | -------- | ------- |
| P1 | Actions dans la notification push ("Ajouter aux courses") | ðŸŸ¡ | 2j | C |
| P2 | Push conditionnel (heures calmes configurables) | ðŸŸ¡ | 1j | D |
| P3 | Badge app PWA (nombre notifications non lues) | ðŸŸ¢ | 1j | E |

---

### 8.9 Mode Admin (analyse Â§11)

#### Existant â€” âœ… TrÃ¨s complet

| CatÃ©gorie | FonctionnalitÃ© | Statut |
| ----------- | --------------- | -------- |
| Jobs CRON | Lister, dÃ©clencher, historique | âœ… |
| Notifications | Tester un canal, broadcast test | âœ… |
| Event Bus | Historique, Ã©mission manuelle | âœ… |
| Cache | Stats, purge par pattern | âœ… |
| Services | Ã‰tat registre complet | âœ… |
| Feature Flags | Activer/dÃ©sactiver features | âœ… |
| Maintenance | Mode maintenance ON/OFF | âœ… |
| Simulation | Dry-run workflows (pÃ©remption, digest, rappels) | âœ… |
| IA Console | Tester prompts (tempÃ©rature, tokens) | âœ… |
| Impersonation | Switcher d'utilisateur | âœ… |
| Audit/Security Logs | TraÃ§abilitÃ© complÃ¨te | âœ… |
| SQL Views | Browser de vues SQL | âœ… |
| WhatsApp Test | Message test | âœ… |
| Config | Export/import runtime | âœ… |

#### AmÃ©liorations

| # | AmÃ©lioration | PrioritÃ© | Effort | Phase |
| --- | ------------- | ---------- | -------- | ------- |
| A1 | Console commande rapide ("run job X", "clear cache Y") | ðŸŸ¡ | 2j | D1 |
| A2 | Dashboard admin temps rÃ©el (WebSocket admin_logs â†’ UI filtres + auto-scroll) | ðŸŸ¡ | 3j | D |
| A3 | Scheduler visuel (timeline 68 jobs, prochain run, dÃ©pendances) | ðŸŸ¡ | 3j | D2 |
| A4 | Replay d'Ã©vÃ©nements passÃ©s du bus avec handlers | ðŸŸ¡ | 2j | D |
| A6 | Logs en temps rÃ©el (endpoint WS existe â†’ connecter UI) | ðŸŸ¡ | 2j | D3 |
| A7 | Test E2E one-click (scÃ©nario complet recetteâ†’planningâ†’coursesâ†’checkoutâ†’inventaire) | ðŸŸ¢ | 3j | E |

---

### 8.10 Couverture de tests (analyse Â§12)

#### Backend â€” ~55% couverture

| Zone | Fichiers | Couverture | Note |
| ------ | ---------- | ------------ | ------ |
| Routes API cuisine | 8 | âœ… ~85% | Bien |
| Routes API famille | 6 | âœ… ~75% | OK |
| Routes API maison | 5 | âš ï¸ ~60% | Gaps jardin/Ã©nergie |
| Routes API jeux | 2 | âš ï¸ ~55% | Gaps loto/euro |
| Routes API admin | 2 | âœ… ~70% | OK |
| Routes export/upload | 2 | âŒ ~30% | TrÃ¨s faible |
| Routes webhooks | 2 | âŒ ~25% | TrÃ¨s faible |
| Services | 20+ | âš ï¸ ~60% | Variable |
| Core (config, db, cache) | 6 | âš ï¸ ~55% | Cache orchestrateur faible |
| Event Bus | 1 | âŒ ~20% | TrÃ¨s faible |
| RÃ©silience | 1 | âš ï¸ ~40% | Manque scÃ©narios rÃ©els |
| WebSocket | 1 | âŒ ~25% | Edge cases manquants |
| IntÃ©grations | 3 | âŒ ~20% | Stubs sans E2E |

#### Frontend â€” ~40% couverture

| Zone | Fichiers | Couverture | Note |
| ------ | ---------- | ------------ | ------ |
| Pages cuisine | 8 | âœ… ~70% | Bien |
| Pages jeux | 5 | âœ… ~65% | OK |
| Pages outils | 6 | âœ… ~60% | OK |
| Pages famille | 3 | âš ï¸ ~35% | Gaps importants |
| Pages maison | 2 | âš ï¸ ~30% | Gaps importants |
| Pages admin | 2 | âš ï¸ ~30% | Gaps importants |
| Pages paramÃ¨tres | 1 | âŒ ~15% | TrÃ¨s faible |
| Hooks | 2 | âš ï¸ ~45% | WebSocket sous-testÃ© |
| Stores | 4 | âœ… ~80% | Bien |
| Composants | 12 | âš ï¸ ~40% | Variable |
| API clients | 1 | âŒ ~15% | TrÃ¨s faible |
| E2E Playwright | Quelques | âŒ ~10% | Quasi inexistant |

#### Tests manquants prioritaires

| # | Test | Module | PrioritÃ© | Phase |
| --- | ------ | -------- | ---------- | ------- |
| T1 | Tests export PDF (courses, planning, recettes, budget) | Export | ðŸ”´ | A12 |
| T2 | Tests webhooks WhatsApp (state machine, parsing) | Notifications | ðŸ”´ | A13 |
| T3 | Tests event bus scenarios (pub/sub, wildcards, erreurs) | Core | ðŸ”´ | A14 |
| T4 | Tests cache L1/L2/L3 (promotion, Ã©viction) | Core | ðŸŸ¡ | B |
| T5 | Tests WebSocket edge cases (reconnexion, timeout, malformÃ©) | Courses | ðŸŸ¡ | D |
| T6 | Tests E2E parcours utilisateur complet | Frontend | ðŸ”´ | B13 |
| T7 | Tests API clients frontend (erreurs rÃ©seau, refresh, pagination) | Frontend | ðŸŸ¡ | D |
| T8 | Tests pages paramÃ¨tres (chaque onglet) | Frontend | ðŸŸ¡ | B12 |
| T9 | Tests pages admin (jobs, services, cache, flags) | Frontend | ðŸŸ¡ | D |
| T10 | Tests Playwright accessibilitÃ© (axe-core pages principales) | Frontend | ðŸŸ¢ | E |

---

### 8.11 Documentation (analyse Â§13)

#### Ã‰tat

| Document | Statut | Action | Phase |
| ---------- | -------- | -------- | ------- |
| `docs/INDEX.md` | âœ… Courant | â€” | â€” |
| `docs/MODULES.md` | âœ… Courant | â€” | â€” |
| `docs/API_REFERENCE.md` | âœ… Courant | â€” | â€” |
| `docs/API_SCHEMAS.md` | âœ… Courant | â€” | â€” |
| `docs/SERVICES_REFERENCE.md` | âœ… Courant | â€” | â€” |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | âœ… Courant | â€” | â€” |
| `docs/ERD_SCHEMA.md` | âœ… Courant | â€” | â€” |
| `docs/ARCHITECTURE.md` | âš ï¸ 1 mois | RafraÃ®chir | D |
| `docs/DATA_MODEL.md` | âš ï¸ VÃ©rifier | Peut Ãªtre obsolÃ¨te post-phases | D |
| `docs/DEPLOYMENT.md` | âš ï¸ VÃ©rifier | Config Railway/Vercel actuelle | D |
| `docs/ADMIN_RUNBOOK.md` | âš ï¸ VÃ©rifier | 20+ endpoints admin tous docum. ? | D |
| `docs/CRON_JOBS.md` | âœ… MÃ J 01/04/2026 | 68 jobs documentÃ©s | TerminÃ© |
| `docs/NOTIFICATIONS.md` | âœ… MÃ J 01/04/2026 | 4 canaux, failover, digest, templates | TerminÃ© |
| `docs/AUTOMATIONS.md` | âœ… MÃ J 01/04/2026 | DÃ©clencheurs/actions rÃ©els documentÃ©s | TerminÃ© |
| `docs/INTER_MODULES.md` | âœ… MÃ J 01/04/2026 | 21+ bridges et patterns documentÃ©s | TerminÃ© |
| `docs/EVENT_BUS.md` | âœ… MÃ J 01/04/2026 | 32 Ã©vÃ©nements, 51 subscribers | TerminÃ© |
| `docs/MONITORING.md` | âš ï¸ VÃ©rifier | Prometheus metrics actuelles ? | D |
| `docs/SECURITY.md` | âš ï¸ VÃ©rifier | Rate limiting, 2FA, CORS | D |
| `PLANNING_IMPLEMENTATION.md` | ðŸ”´ ObsolÃ¨te | Ce document le remplace | â€” |
| `ROADMAP.md` | ðŸ”´ ObsolÃ¨te | PrioritÃ©s pÃ©rimÃ©es | D |

#### Documentation Ã  crÃ©er

| # | Document | PrioritÃ© | Phase |
| --- | --------- | ---------- | ------- |
| D1 | Guide complet CRON jobs (68+ jobs, horaires, dÃ©pendances) | âœ… Fait | TerminÃ© |
| D2 | Guide notifications refonte (4 canaux, failover, templates, config) | âœ… Fait | TerminÃ© |
| D3 | Guide admin MÃ J (20+ endpoints, panneau, simulations, flags) | âœ… Fait | TerminÃ© |
| D4 | Guide bridges inter-modules (21 bridges, naming, comment en crÃ©er) | âœ… Fait | TerminÃ© |
| D5 | Guide de test unifiÃ© (pytest + Vitest + Playwright, fixtures, mocks) | âœ… Fait | TerminÃ© |
| D6 | Changelog module par module | âš ï¸ Partiel | Ã€ complÃ©ter |

---

### 8.12 Organisation & architecture (analyse Â§14)

#### Points forts âœ…

- Architecture modulaire : sÃ©paration routes/schemas/services/models
- Service Registry : `@service_factory` singleton thread-safe
- Event Bus : pub/sub dÃ©couplÃ©, wildcards, prioritÃ©s
- Cache multi-niveaux : L1â†’L2â†’L3+Redis
- RÃ©silience : retry+timeout+circuit breaker composables
- SÃ©curitÃ© : JWT+2FA TOTP+rate limiting+security headers+sanitization
- Frontend : App Router Next.js 16, composants shadcn/ui consistants

#### Points Ã  amÃ©liorer

| # | ProblÃ¨me | Action | Effort | Phase |
| --- | ---------- | -------- | -------- | ------- |
| O1 | `jobs.py` monolithique (3500+ lignes) | DÃ©couper en `jobs_cuisine.py`, `jobs_famille.py`, etc. | 1j | D10 |
| O2 | Routes famille Ã©clatÃ©es (multiples fichiers) | Documenter naming pattern | 30min | D |
| O3 | Scripts legacy non archivÃ©s | DÃ©placer dans `scripts/_archive/` | 30min | D11 |
| O4 | Doubles bibliothÃ¨ques charts (Chart.js + Recharts) | Standardiser sur Recharts | 1j | D12 |
| O5 | RGPD route non pertinente (app privÃ©e) | Simplifier en "Export backup" | 30min | E |
| O6 | Types frontend dupliquÃ©s entre fichiers | Centraliser via barrel exports | 1j | D |
| O7 | DonnÃ©es rÃ©fÃ©rence non versionnÃ©es | Ajouter version dans chaque JSON | 30min | E |
| O8 | Dossier exports non nettoyÃ© (`data/exports/`) | Politique rÃ©tention automatique (CRON J3) | 30min | D |

---

### 8.13 AmÃ©liorations UI/UX (analyse Â§15)

#### Dashboard

| # | AmÃ©lioration | PrioritÃ© | Phase |
| --- | ------------- | ---------- | ------- |
| U1 | **Widgets drag-drop** (`@dnd-kit/core`) | ðŸ”´ | C1 |
| U2 | Cartes avec micro-animations (Framer Motion) | ðŸŸ¡ | C |
| U3 | Mode sombre raffinÃ© (charts, calendrier) | ðŸŸ¡ | E |
| U4 | Squelettes de chargement fidÃ¨les | ðŸŸ¡ | D |

#### Navigation

| # | AmÃ©lioration | PrioritÃ© | Phase |
| --- | ------------- | ---------- | ------- |
| U5 | Sidebar avec favoris dynamiques (composant existant â†’ store) | ðŸŸ¡ | D |
| U6 | Breadcrumbs interactifs (tous niveaux cliquables) | ðŸŸ¢ | E |
| U7 | **Transitions de page fluides** (framer-motion ou View Transitions) | ðŸŸ¡ | C8 |
| U8 | Bottom bar mobile enrichie (indicateur page active + animation) | ðŸŸ¡ | C |

#### Formulaires

| # | AmÃ©lioration | PrioritÃ© | Phase |
| --- | ------------- | ---------- | ------- |
| U9 | **Auto-complÃ©tion intelligente** (historique) | ðŸ”´ | C11 |
| U10 | Validation inline temps rÃ©el (onBlur au lieu de submit) | ðŸŸ¡ | D |
| U11 | Assistant formulaire IA ("Aide-moi Ã  remplir") | ðŸŸ¡ | E |

#### Mobile

| # | AmÃ©lioration | PrioritÃ© | Phase |
| --- | ------------- | ---------- | ------- |
| U12 | **Swipe actions** sur toutes les listes | ðŸŸ¡ | C9 |
| U13 | Pull-to-refresh (TanStack Query le supporte) | ðŸŸ¡ | D |
| U14 | Haptic feedback (Vibration API) | ðŸŸ¢ | E |

#### Micro-interactions

| # | AmÃ©lioration | PrioritÃ© | Phase |
| --- | ------------- | ---------- | ------- |
| U15 | Confetti sur accomplissement (planning validÃ©, courses complÃ¨tes) | ðŸŸ¢ | E |
| U16 | **Compteurs animÃ©s dashboard** (0 â†’ valeur rÃ©elle) | ðŸŸ¡ | C10 |
| U17 | Toast notifications Sonner amÃ©liorÃ©es (succÃ¨s check animÃ©, erreur shake) | ðŸŸ¡ | D |

---

### 8.14 Visualisations 2D/3D (analyse Â§16)

#### Existant

| Composant | Technologie | Module | Statut |
| ----------- | ------------- | -------- | -------- |
| Plan 3D maison | Three.js/@react-three/fiber | Maison | âš ï¸ Non connectÃ© aux donnÃ©es |
| Heatmap numÃ©ros loto | Recharts | Jeux | âœ… |
| Heatmap cotes paris | Recharts | Jeux | âœ… |
| Camembert budget | Recharts | Famille | âœ… |
| Graphique ROI | Recharts | Jeux | âœ… |
| Graphique jalons Jules | Recharts | Famille | âœ… |
| Timeline planning | Custom CSS | Planning | âš ï¸ Basique |
| Carte Leaflet habitat | react-leaflet | Habitat | âš ï¸ Partiel |

#### Nouvelles visualisations

**3D :**

| # | Visualisation | Module | Description | Effort | Phase |
| --- | --------------- | -------- | ------------- | -------- | ------- |
| V1 | **Plan 3D maison interactif** | Maison | Connecter aux donnÃ©es : couleur piÃ¨ces par tÃ¢ches, Ã©nergie par piÃ¨ce, clic â†’ dÃ©tail | 5j | C3 |
| V2 | **Vue jardin 2D/3D** | Jardin | Zones plantation, Ã©tat plantes, calendrier arrosage | 3j | E7 |
| V3 | **Globe 3D voyages** | Voyages | Destinations + itinÃ©raires (globe.gl) | 2j | E |

**2D :**

| # | Visualisation | Module | Description | Effort | Phase |
| --- | --------------- | -------- | ------------- | -------- | ------- |
| V4 | **Calendrier nutritionnel heatmap** | Cuisine | Grille GitHub contributions jour par jour (rouge â†’ vert) | 2j | C4 |
| V5 | **Treemap budget** | Budget | Proportionnel catÃ©gories, drill-down cliquable | 2j | C5 |
| V6 | **Sunburst recettes** | Cuisine | CatÃ©gories â†’ sous-catÃ©gories â†’ recettes (D3.js) | 2j | E |
| V7 | **Radar skill Jules** | Famille | Diagramme araignÃ©e compÃ©tences vs normes OMS | 1j | C6 |
| V8 | **Sparklines dans cartes** | Dashboard | Mini graphiques tendance 7 jours | 1j | C7 |
| V9 | **Graphe rÃ©seau modules** | Admin | 21 bridges visuels (D3.js force graph) | 2j | E5 |
| V10 | **Timeline Gantt entretien** | Maison | Planification annuelle | 2j | E6 |
| V11 | **Courbe Ã©nergie N vs N-1** | Ã‰nergie | Comparaison consommation | 2j | C |
| V12 | **Flux Sankey courses â†’ catÃ©gories** | Courses/Budget | Fournisseurs â†’ catÃ©gories â†’ sous-catÃ©gories | 2j | E |
| V13 | **Wheel fortune loto** | Jeux | Animation roue rÃ©vÃ©lation numÃ©ros IA | 1j | E |

---

### 8.15 Simplification flux utilisateur (analyse Â§17)

> L'utilisateur doit accomplir ses tÃ¢ches quotidiennes en **3 clics maximum**.
> L'IA fait le travail lourd en arriÃ¨re-plan, l'utilisateur **valide**.

#### ðŸ½ï¸ Flux cuisine (central)

```
Semaine vide â†’ IA propose planning â†’ Valider/Modifier/RÃ©gÃ©nÃ©rer
                                         â”‚
                                    Planning validÃ©
                                   â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”
                            Auto-gÃ©nÃ¨re      Notif WhatsApp
                            courses           recap
                                â”‚
                          Liste courses (triÃ©e par rayon)
                                â”‚
                     En magasin: cocher au fur et Ã  mesure
                                â”‚
                     Checkout â†’ transfert automatique inventaire
                                â”‚
                     Score anti-gaspi mis Ã  jour

Fin de semaine: "Qu'avez-vous vraiment mangÃ© ?" â†’ feedback IA
```

**Actions utilisateur** : 3 (valider planning â†’ cocher courses â†’ checkout)
**Actions IA** : Planning, courses, rayons, transfert inventaire

#### ðŸ‘¶ Flux famille quotidien

```
Matin (auto WhatsApp 07h30):
  "Bonjour ! Repas X, tÃ¢che Y, Jules a Z mois" â†’ OK / Modifier

JournÃ©e:
  Routines Jules (checklist â†’ cocher)

Soir:
  RÃ©cap auto: "3/5 tÃ¢ches, 2 repas ok, Jules: poids notÃ©"
```

#### ðŸ¡ Flux maison

```
Notification push auto:
  "TÃ¢che entretien: [tÃ¢che]" â†’ Voir â†’ Marquer fait â†’ auto-prochaine date
  "Stock [X] bas" â†’ Ajouter aux courses (1 clic)
  1er du mois: Rapport email rÃ©sumÃ© tÃ¢ches + budget maison
```

#### Actions rapides FAB mobile

| Action rapide | Cible | IcÃ´ne |
| -------------- | ------- | ------- |
| + Recette rapide | Formulaire simplifiÃ© (nom + photo) | ðŸ“¸ |
| + Article courses | Ajout vocal ou texte | ðŸ›’ |
| + DÃ©pense | Montant + catÃ©gorie | ðŸ’° |
| + Note | Texte libre | ðŸ“ |
| Scan barcode | Scanner â†’ inventaire ou courses | ðŸ“· |
| Timer cuisine | Minuteur rapide | â±ï¸ |

**Phase : C (actions rapides), B (flux simplifiÃ©s cuisine/famille), D (flux maison)**

---

### 8.16 Axes d'innovation (analyse Â§18)

| # | Innovation | Modules | Description | Effort | Impact | Phase |
| --- | ----------- | --------- | ------------- | -------- | -------- | ------- |
| IN1 | **Mode "Pilote automatique"** | Tous | IA gÃ¨re planning/courses/rappels sans intervention. RÃ©sumÃ© quotidien, corrections uniquement. ON/OFF paramÃ¨tres | 5j | ðŸ”´ TrÃ¨s Ã©levÃ© | E1 |
| IN2 | **Widget tablette Google** | Dashboard | Widget Android/web : repas du jour, tÃ¢che, mÃ©tÃ©o, timer. Compatible tablette Google | 4j | ðŸ”´ Ã‰levÃ© | E2 |
| IN3 | **Page "Ma journÃ©e" unifiÃ©e** | Planning+Cuisine+Famille+Maison | Tout en une page : repas, tÃ¢ches, routines Jules, mÃ©tÃ©o, anniversaires, timer | 3j | ðŸ”´ TrÃ¨s Ã©levÃ© | C2 |
| IN4 | **Suggestions proactives contextuelles** | IA+Tous | BanniÃ¨re IA en haut de chaque module : "tomates expirent â†’ recettes", "budget restaurants 80% â†’ dÃ©tail" | 3j | ðŸ”´ Ã‰levÃ© | C12 |
| IN5 | **Journal familial automatique** | Famille | IA gÃ©nÃ¨re journal de la semaine : repas, activitÃ©s, Jules, photos, mÃ©tÃ©o, dÃ©penses. Exportable PDF | 3j | ðŸŸ¡ Moyen | E8 |
| IN6 | **Mode focus/zen** | UI | Masque tout sauf la tÃ¢che en cours (recette en cuisine, liste en magasin). Composant `focus/` existant | 2j | ðŸŸ¡ Moyen | D |
| IN7 | **Comparateur prix courses** | Courses+IA | Liste â†’ IA compare prix rÃ©fÃ©rence (sans OCR) â†’ budget estimÃ© | 3j | ðŸŸ¡ Moyen | E |
| IN8 | **Google Home routines Ã©tendues** | Assistant | "Bonsoir" â†’ lecture repas demain + tÃ¢ches | 4j | ðŸŸ¡ Moyen | E10 |
| IN9 | **Seasonal meal prep planner** | Cuisine+IA | Chaque saison â†’ plan batch cooking saisonnier + congÃ©lations recommandÃ©es | 2j | ðŸŸ¡ Moyen | E |
| IN10 | **Score famille hebdomadaire** | Dashboard | Composite : nutrition + dÃ©penses + activitÃ©s + entretien + bien-Ãªtre. Graphe semaine par semaine | 2j | ðŸ”´ Ã‰levÃ© | E3 |
| IN11 | **Export rapport mensuel PDF** | Export+IA | PDF avec graphiques : budget, nutrition, entretien, Jules, jeux. RÃ©sumÃ© narratif IA | 3j | ðŸŸ¡ Moyen | E9 |
| IN12 | **Planning vocal** | Assistant+Planning | "Planifie du poulet mardi soir" â†’ crÃ©e repas + vÃ©rifie stock + ajoute manquants | 3j | ðŸŸ¡ Moyen | E |
| IN13 | **Tableau de bord Ã©nergie** | Maison | Dashboard dÃ©diÃ© : conso temps rÃ©el (Linky), historique, N-1, prÃ©vision facture, tips IA | 4j | ðŸŸ¡ Moyen | E |
| IN14 | **Mode "invitÃ©" conjoint** | Auth | Vue simplifiÃ©e 2Ã¨me utilisateur : courses, planning, routines. Sans admin ni config | 2j | ðŸ”´ Ã‰levÃ© | E4 |

---

## 9. Annexes

### Annexe A â€” Arborescence fichiers clÃ©s

#### Backend Python

```
src/
â”œâ”€â”€ api/
â”‚   â”œâ”€â”€ main.py                    # FastAPI app + 7 middlewares + health
â”‚   â”œâ”€â”€ auth.py                    # JWT + 2FA TOTP
â”‚   â”œâ”€â”€ dependencies.py            # require_auth, require_role
â”‚   â”œâ”€â”€ routes/                    # 41 fichiers routeurs (~250 endpoints)
â”‚   â”œâ”€â”€ schemas/                   # 25 fichiers Pydantic (~150 modÃ¨les)
â”‚   â”œâ”€â”€ utils/                     # Exception handler, pagination, metrics, ETag, security
â”‚   â”œâ”€â”€ rate_limiting/             # Multi-strategy (memory/Redis/file)
â”‚   â”œâ”€â”€ websocket_courses.py       # WS collaboration courses
â”‚   â””â”€â”€ websocket/                 # 4 autres WebSockets
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ ai/                        # Mistral client, cache sÃ©mantique, circuit breaker
â”‚   â”œâ”€â”€ caching/                   # L1/L2/L3 + Redis
â”‚   â”œâ”€â”€ config/                    # Pydantic BaseSettings
â”‚   â”œâ”€â”€ db/                        # Engine, sessions, migrations
â”‚   â”œâ”€â”€ decorators/                # @avec_session_db, @avec_cache, @avec_resilience
â”‚   â”œâ”€â”€ models/                    # 32 fichiers ORM (100+ classes)
â”‚   â”œâ”€â”€ resilience/                # Retry + Timeout + CircuitBreaker
â”‚   â””â”€â”€ validation/                # Pydantic schemas + sanitizer
â””â”€â”€ services/
    â”œâ”€â”€ core/
    â”‚   â”œâ”€â”€ base/                  # BaseAIService (4 mixins)
    â”‚   â”œâ”€â”€ cron/                  # 68+ jobs (3500+ lignes)
    â”‚   â”œâ”€â”€ events/                # Pub/Sub event bus
    â”‚   â””â”€â”€ registry.py            # @service_factory singleton
    â”œâ”€â”€ cuisine/                   # RecetteService, ImportService
    â”œâ”€â”€ famille/                   # JulesAI, WeekendAI
    â”œâ”€â”€ maison/                    # MaisonService
    â”œâ”€â”€ jeux/                      # JeuxService
    â”œâ”€â”€ planning/                  # 5 sous-modules
    â”œâ”€â”€ inventaire/                # InventaireService
    â”œâ”€â”€ dashboard/                 # AgrÃ©gation multi-module
    â”œâ”€â”€ integrations/              # Multimodal, webhooks
    â””â”€â”€ utilitaires/               # Automations, divers
```

#### Frontend Next.js

```
frontend/src/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ (auth)/                    # Login / Inscription
â”‚   â”œâ”€â”€ (app)/                     # App protÃ©gÃ©e (~60 pages)
â”‚   â”‚   â”œâ”€â”€ cuisine/               # 12 pages
â”‚   â”‚   â”œâ”€â”€ famille/               # 10 pages
â”‚   â”‚   â”œâ”€â”€ maison/                # 8 pages
â”‚   â”‚   â”œâ”€â”€ jeux/                  # 7 pages
â”‚   â”‚   â”œâ”€â”€ planning/              # 2 pages
â”‚   â”‚   â”œâ”€â”€ outils/                # 6 pages
â”‚   â”‚   â”œâ”€â”€ parametres/            # 3 pages + 7 onglets
â”‚   â”‚   â”œâ”€â”€ admin/                 # 10 pages
â”‚   â”‚   â”œâ”€â”€ habitat/               # 3 pages
â”‚   â”‚   â””â”€â”€ ia-avancee/            # IA avancÃ©e
â”‚   â””â”€â”€ share/                     # Partage public
â”œâ”€â”€ composants/
â”‚   â”œâ”€â”€ ui/                        # 29 shadcn/ui
â”‚   â”œâ”€â”€ disposition/               # 19 layout components
â”‚   â”œâ”€â”€ cuisine/, famille/, jeux/, maison/, habitat/
â”‚   â”œâ”€â”€ graphiques/                # Charts rÃ©utilisables
â”‚   â””â”€â”€ planning/                  # Timeline, calendrier
â”œâ”€â”€ bibliotheque/
â”‚   â”œâ”€â”€ api/                       # 34 clients API
â”‚   â””â”€â”€ validateurs.ts             # 22 schÃ©mas Zod
â”œâ”€â”€ crochets/                      # 15 hooks custom
â”œâ”€â”€ magasins/                      # 4 stores Zustand
â”œâ”€â”€ types/                         # 15 fichiers TypeScript
â””â”€â”€ fournisseurs/                  # 3 providers React
```

#### SQL

```
sql/
â”œâ”€â”€ INIT_COMPLET.sql               # 4922 lignes, source unique (prod)
â”œâ”€â”€ schema/ (18 fichiers)          # Source de vÃ©ritÃ© par domaine
â””â”€â”€ migrations/ (7 fichiers)       # Ã€ consolider dans schema/
```

### Annexe B â€” WebSockets

| Route WS | Fonction | Ã‰tat |
| ---------- | ---------- | ------ |
| `/ws/courses/{liste_id}` | Collaboration temps rÃ©el courses | âœ… (manque fallback HTTP â†’ B2) |
| `/ws/planning` | Collaboration planning | âœ… |
| `/ws/notes` | Ã‰dition collaborative notes | âœ… |
| `/ws/projets` | Kanban projets maison | âœ… |
| `/ws/admin/logs` | Streaming logs admin | âœ… (UI non connectÃ©e â†’ A6/D3) |

### Annexe C â€” DonnÃ©es de rÃ©fÃ©rence

```
data/reference/
â”œâ”€â”€ astuces_domotique.json           âœ…
â”œâ”€â”€ calendrier_soldes.json           âœ…
â”œâ”€â”€ calendrier_vaccinal_fr.json      âœ…
â”œâ”€â”€ catalogue_pannes_courantes.json  âœ…
â”œâ”€â”€ entretien_catalogue.json         âœ…
â”œâ”€â”€ guide_lessive.json               âœ…
â”œâ”€â”€ guide_nettoyage_surfaces.json    âœ…
â”œâ”€â”€ guide_travaux_courants.json      âœ…
â”œâ”€â”€ normes_oms.json                  âœ…
â”œâ”€â”€ nutrition_table.json             âœ…
â”œâ”€â”€ plantes_catalogue.json           âœ…
â”œâ”€â”€ produits_de_saison.json          âœ…
â”œâ”€â”€ routines_defaut.json             âœ…
â””â”€â”€ template_import_inventaire.csv   âœ…
```

### Annexe D â€” Canaux de notification par Ã©vÃ©nement

```
Failover: Push â†’ ntfy â†’ WhatsApp â†’ Email
Throttle: 2h par type / canal
```

| Ã‰vÃ©nement | Push | ntfy | WhatsApp | Email |
| ----------- | ------ | ------ | ---------- | ------- |
| PÃ©remption J-2 | âœ… | âœ… | Â· | Â· |
| Rappel courses | âœ… | âœ… | âœ… | Â· |
| RÃ©sumÃ© hebdomadaire | Â· | Â· | âœ… | âœ… |
| Rapport budget mensuel | Â· | Â· | Â· | âœ… |
| Anniversaire J-7 | âœ… | âœ… | âœ… | Â· |
| TÃ¢che entretien urgente | âœ… | âœ… | âœ… | Â· |
| Ã‰chec CRON job | âœ… | âœ… | âœ… | âœ… |
| Document expirant | âœ… | âœ… | Â· | âœ… |
| Badge dÃ©bloquÃ© | âœ… | âœ… | Â· | Â· |
| Stock critique | âœ… | âœ… | âœ… | Â· |
| Planning vide dimanche | âœ… | Â· | âœ… | Â· |
| Digest matinal | Â· | Â· | âœ… | Â· |
| Rapport mensuel | Â· | Â· | Â· | âœ… |

---

## 10. RÃ©capitulatif global & mÃ©triques de santÃ©

### Vue synthÃ©tique des phases

| Phase | Objectif | TÃ¢ches | Semaines | PrioritÃ© |
| ------- | ---------- | -------- | ---------- | ---------- |
| **Phase A** | Stabilisation : bugs critiques, SQL, tests critiques, doc obsolÃ¨te | 16 | 1-2 | âœ… TERMINÃ‰E |
| **Phase B** | FonctionnalitÃ©s : gaps, IA, CRON, bridges, recherche, tests | 13 | 3-4 | âœ… TERMINÃ‰E |
| **Phase C** | UI/UX : visualisations, drag-drop, animations, flux simplifiÃ©s | 12 | 5-6 | ðŸŸ¢ MOYENNE-HAUTE |
| **Phase D** | Admin : console, scheduler, CRON, notifications, refactoring | 12 | 7-8 | ðŸŸ¢ MOYENNE |
| **Phase E** | Innovations : pilote automatique, widget, Google Home, exports | 12 | 9+ | ðŸŸ¢ BASSE |
| **TOTAL** | | **65 tÃ¢ches** | | |

### DÃ©pendances

```
Phase A (Stabilisation) â”€â”€â”€â”€ BLOQUANT pour tout
    â”‚
    â”œâ”€â”€ Phase B (Features)      â”€â”€â”€â”€ AprÃ¨s A
    â”‚       â”‚
    â”‚       â”œâ”€â”€ Phase C (UI/UX)  â”€â”€â”€â”€ AprÃ¨s B
    â”‚       â”‚
    â”‚       â””â”€â”€ Phase D (Admin)  â”€â”€â”€â”€ AprÃ¨s B
    â”‚               â”‚
    â”‚               â””â”€â”€ Phase E (Innovations) â”€â”€â”€â”€ AprÃ¨s C+D
    â”‚
    â””â”€â”€ Docs en parallÃ¨le de tout
```

### MÃ©triques de santÃ© projet

| Indicateur | Valeur actuelle | Cible | Statut |
| ----------- | ---------------- | ------- | -------- |
| Tests backend couverture | ~55% | â‰¥70% | ðŸŸ¡ |
| Tests frontend couverture | ~40% | â‰¥50% | ðŸ”´ |
| Tests E2E | ~10% | â‰¥30% | ðŸ”´ |
| Docs Ã  jour | ~60% | â‰¥90% | ðŸŸ¡ |
| SQL ORM sync | Non vÃ©rifiÃ© | 100% | âš ï¸ |
| Endpoints documentÃ©s | ~80% | 100% | ðŸŸ¡ |
| Bridges inter-modules | 21 actifs | 31 possibles | ðŸŸ¡ |
| CRON jobs testÃ©s | ~30% | â‰¥70% | ðŸ”´ |
| Bugs critiques ouverts | 4 | 0 | ðŸ”´ |
| SÃ©curitÃ© (OWASP) | Bon (partiel) | Complet | ðŸŸ¡ |

### Comptage total par catÃ©gorie

| CatÃ©gorie | Items dans l'analyse | PlanifiÃ© |
| ----------- | --------------------- | ---------- |
| Bugs critiques | 4 | Phase A |
| Bugs importants | 6 | Phase A + D |
| Bugs mineurs | 4 | Backlog |
| Gaps fonctionnels | 23 | Phases B-E |
| Actions SQL | 6 | Phase A |
| Interactions intra-modules Ã  amÃ©liorer | 8 | Phases B-E |
| Nouvelles interactions inter-modules | 10 | Phases B-E |
| OpportunitÃ©s IA | 12 | Phases B-E |
| Nouveaux CRON jobs | 10 | Phases B-D |
| AmÃ©liorations notifications | 11 | Phases B-E |
| AmÃ©liorations admin | 7 | Phase D |
| Tests manquants prioritaires | 10 | Phases A-D |
| Documentation Ã  crÃ©er/MÃ J | 17 | Phases A-D |
| Refactoring organisation | 8 | Phase D |
| AmÃ©liorations UI/UX | 17 | Phases C-E |
| Visualisations 2D/3D | 13 | Phases C-E |
| Innovations | 14 | Phase E |
| **TOTAL items identifiÃ©s** | **~170** | **65 tÃ¢ches groupÃ©es en 5 phases** |

---

> **Document gÃ©nÃ©rÃ© le 1er avril 2026**
> BasÃ© intÃ©gralement sur les 19 sections de ANALYSE_COMPLETE.md
> **65 tÃ¢ches planifiÃ©es** couvrant **~170 items identifiÃ©s** en **5 phases**
> **Note globale app : 7.5/10** â€” Architecture excellente, pÃ©nalisÃ©e par la couverture de tests, la dette UX, et 4 bugs critiques de production
