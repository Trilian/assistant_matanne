# Planning d'Implémentation — Assistant Matanne

> **Date** : 3 avril 2026
> **Source** : Basé intégralement sur l'analyse complète de `PLAN_PROJET.md` (2 avril 2026)
> **Objectif** : Plan d'exécution détaillé avec notation par catégorie, priorisation, et suivi

---

## Table des matières

1. [Notation de l'app par catégorie](#1-notation-de-lapp-par-catégorie)
2. [État des lieux — Inventaire complet](#2-état-des-lieux--inventaire-complet)
3. [Phase 1 — Nettoyage et dette technique](#3-phase-1--nettoyage-et-dette-technique) *(en cours)*
4. [Phase 2 — Consolidation inter-modules](#4-phase-2--consolidation-inter-modules) *(en cours)*
5. [Phase 3 — IA et automatisations](#5-phase-3--ia-et-automatisations)
6. [Phase 4 — UI/UX moderne](#6-phase-4--uiux-moderne)
7. [Phase 5 — Simplification des flux + Validation v2](#7-phase-5--simplification-des-flux--validation-v2)
8. [Phase 6 — Optimisation technique + Railway](#8-phase-6--optimisation-technique--railway)
9. [Migration WhatsApp → Telegram](#9-migration-whatsapp--telegram)
10. [Flux utilisateur avec validation v2](#10-flux-utilisateur-avec-validation-v2)
11. [Contraintes Railway Free ($0/mois)](#11-contraintes-railway-free-0mois)
12. [Annexes — Détails techniques de référence](#12-annexes--détails-techniques-de-référence)
9. [Annexes — Détails techniques de référence](#9-annexes--détails-techniques-de-référence)

---

## 1. Notation de l'app par catégorie

### Vue synthétique

| Catégorie | Note /10 | Justification |
|-----------|----------|---------------|
| **Architecture backend** | 8.5/10 | Très solide : FastAPI + SQLAlchemy 2.0 + Pydantic v2, 14 sous-packages core bien découpés, 138+ factories, registre de services singleton, résilience, cache multi-niveaux, event bus. Défauts : 3 fichiers fourre-tout (innovations 999L, admin 800L, dashboard 1000L), code legacy persistant. |
| **Architecture frontend** | 8/10 | Stack moderne : Next.js 16, App Router, TanStack Query v5, Zustand, shadcn/ui 29 composants, 121 pages. Défauts : doublons (utils, bandeau-meteo), stubs morts, fichiers nommés avec sprint. |
| **Couverture fonctionnelle** | 9/10 | Impressionnante : 9 modules complets (Cuisine, Famille, Maison, Jeux, Outils, Planning, Habitat, Admin, Dashboard), 42 routes API, ~150 tables. Tout "fonctionne". Seul défaut : quelques features backend non exposées en frontend. |
| **Intégration IA** | 8.5/10 | 12 services IA en production, BaseAIService avec rate limiting, cache sémantique, circuit breaker, streaming supporté backend. Défauts : streaming non branché frontend, certains services IA backend sans UI. |
| **Qualité du code** | 6/10 | 4932 tests, 82% coverage cible, décorateurs standardisés (@gerer_exception_api, @avec_session_db, @avec_cache). Mais : 150+ commentaires de sprint, 20+ shims legacy, fichiers de phase, code mort, stubs inertes, 3 fichiers fourre-tout. Dette technique significative. |
| **Base de données / SQL** | 7.5/10 | Schéma bien organisé (20 fichiers numérotés), RLS policies, triggers, vues, seed data. Défauts : tables inutilisées (garanties, incidents_sav, contrats), `06_maison.sql` a 43 tables (trop gros), pas de versioning migrations. |
| **Tests** | 7/10 | 4932 tests collectés, tous passent, fixtures SQLite in-memory. Défauts : tests WebSocket skippés, pas de tests offline/PWA, tests E2E minimaux (backend 1 fichier, frontend basique), pas de tests visuels. |
| **Documentation** | 7/10 | 44 fichiers, architecture documentée, guides utilisateur, API Reference. Défauts : 3 docs de sprint inutiles, références à des modules supprimés (RGPD, garanties, contrats), CHANGELOG par sprint. |
| **UI/UX** | 7.5/10 | Stack visuel riche (Recharts, D3, Three.js, Leaflet, Framer Motion, DnD Kit), mode sombre, responsive, 16 graphiques custom. Défauts : pas d'empty states, spinners au lieu de skeletons, transitions brutales, mode tablette cuisine manquant. |
| **Automatisations (CRON/Jobs)** | 8/10 | 55+ jobs planifiés sur toute la journée, admin trigger manuel, APScheduler. Défauts : pas de mode --force, pas de log viewer temps réel, quelques jobs liés à des features supprimées. |
| **Notifications** | 8.5/10 | 4 canaux complets (Web Push, WhatsApp, Email, In-app), state machine WhatsApp, digest pipeline. Défauts : notifications pas assez actionnables (manquent les CTA), commandes WhatsApp à enrichir. |
| **DevOps / Infrastructure** | 7/10 | Docker, Prometheus metrics, health checks, VAPID keys, service worker. Pas de CI/CD visible, pas de staging automatisé, pas de monitoring alerting production. |
| **Sécurité** | 7.5/10 | JWT Bearer auth, rate limiting (60/min standard, 10/min IA), CORS, security headers middleware, sanitizer anti-XSS. Défauts : RLS à vérifier exhaustivement, pas d'audit de sécurité formel. |
| **Performance** | 6.5/10 | Cache multi-niveaux, ETag middleware, QueuePool SQLAlchemy. Défauts : pas de bundle analysis, Three.js chargé en bloc, pas d'optimistic updates, pas de SSR pages publiques, pas de prefetch routes. |
| **Inter-modules** | 7/10 | 6 bridges existants + EventBus pub/sub. Défauts : planning → courses pas automatique, inventaire → anti-gaspi non connecté, plusieurs bridges évidents manquants. |

### Note globale : **7.5/10**

> **Verdict** : App remarquablement complète et fonctionnelle pour un projet personnel. L'architecture est solide, la couverture fonctionnelle est impressionnante. Les principaux axes d'amélioration sont le nettoyage de la dette technique (code legacy/sprints), l'amélioration de l'UX (simplification des flux, empty states, skeletons), et la finalisation des connexions inter-modules.

---

## 2. État des lieux — Inventaire complet

### 2.1 Backend Python (FastAPI)

| Catégorie | Nombre | Détail |
|-----------|--------|--------|
| Routes API | 42 fichiers | 20 domaines métier + admin + bridges + IA |
| Schémas Pydantic | 24 fichiers | Validation/sérialisation par domaine |
| Modèles ORM | 30 fichiers | ~150 tables SQLAlchemy 2.0 |
| Services | 138+ factories | 16 packages de services |
| Core packages | 14 sous-packages | ai, caching, config, db, decorators, etc. |
| Jobs CRON | 55+ jobs | APScheduler, planification 24h |
| Tests Python | 4932 collectés | Tous passent |

### 2.2 Frontend Next.js

| Catégorie | Nombre | Détail |
|-----------|--------|--------|
| Pages (routes) | ~121 | 15 modules principaux |
| Composants | 130+ | UI (29 shadcn) + layout (22) + métier |
| Clients API | 31 modules | Un par domaine |
| Hooks custom | 19 | Auth, API, WebSocket, CRUD, etc. |
| Stores Zustand | 4 | auth, ui, notifications, maison |
| Types TS | 15 fichiers | Interfaces par domaine |
| Tests frontend | 31 fichiers | Vitest + Playwright |

### 2.3 Modules fonctionnels — État complet

| Module | Backend | Frontend | IA | CRON | Status |
|--------|---------|----------|----|------|--------|
| **Cuisine** | Routes + services | 15 pages | Suggestions, planning IA | 4 jobs | ✅ Complet |
| **Famille** | Routes + 25 services | 16 pages | Résumé, prévision budget | 8 jobs | ✅ Complet |
| **Maison** | Routes + 15 services | 15 pages | Diagnostics, fiches tâche | 6 jobs | ✅ Complet |
| **Jeux** | Routes + 15 services | 5 pages | Prédictions, backtest | 3 jobs | ✅ Complet |
| **Outils** | Routes + 12 services | 14 pages | Chat IA, briefing | 2 jobs | ✅ Complet |
| **Planning** | Routes + 5 services | 2 pages | Planification semaine | 2 jobs | ✅ Complet |
| **Habitat** | Routes + 5 services | 1 page | Déco IA, plans IA | 1 job | ✅ Complet |
| **Admin** | Routes admin | 13 pages | — | — | ✅ Complet |
| **Dashboard** | Routes + 8 services | 1 page | Score bien-être | 3 jobs | ✅ Complet |

### 2.4 SQL — Structure existante

```
sql/
├── INIT_COMPLET.sql          # Auto-régénéré depuis schema/
└── schema/                   # 20 fichiers numérotés
    ├── 01_extensions.sql
    ├── 02_functions.sql
    ├── 03_systeme.sql
    ├── 04_cuisine.sql
    ├── 05_famille.sql
    ├── 06_maison.sql          # 43 tables — le plus gros
    ├── 07_habitat.sql
    ├── 08_jeux.sql
    ├── 09_notifications.sql
    ├── 10_finances.sql
    ├── 11_utilitaires.sql
    ├── 12_triggers.sql
    ├── 13_views.sql
    ├── 14_indexes.sql
    ├── 15_rls_policies.sql
    ├── 16_seed_data.sql
    └── 99_footer.sql
```

### 2.5 IA déjà en place — 12 services

| Module | Service IA | Usage |
|--------|-----------|-------|
| Cuisine | `SuggestionsIAService` | Suggestions repas, batch cooking |
| Cuisine | `PlanningAIService` | Génération planning semaine |
| Famille | `ResumeHebdoService` | Résumé famille hebdomadaire |
| Famille | `PrevisionBudgetService` | Prévision budget + anomalies |
| Maison | `DiagnosticMaisonService` | Diagnostics (vision IA) |
| Maison | `PlansHabitatAIService` | Plans rénovation |
| Maison | `FicheTacheService` | Instructions tâches |
| Habitat | `DecoHabitatService` | Suggestions déco |
| Outils | `ChatAIService` | Chat IA général |
| Outils | `BriefingMatinalService` | Briefing matin |
| Rapports | `BilanMensuelService` | Synthèse mensuelle |
| Bridges | Récolte → Recettes, Météo → Entretien | Bridges IA |

### 2.6 Bridges inter-modules existants

| Bridge | Source → Destination | Mécanisme |
|--------|---------------------|-----------|
| B5.1 | Récolte jardin → Recettes | API bridge + IA |
| B5.3 | Documents expiration → Alertes | CRON + notifications |
| B5.5 | Planning unifié (entretien + activités) | Vue combinée |
| B5.8 | Météo → Entretien maison | API bridge + IA |
| B6 | Routine streaks + énergie | Intra-module |
| B7 | Flux simplifiés (3-click cuisine, digest) | Intra-module |
| EventBus | Cache invalidation multi-domaines | Pub/Sub |

### 2.7 Notifications — 4 canaux complets

| Canal | Implémenté | Configuration |
|-------|-----------|---------------|
| Web Push | ✅ Complet | VAPID keys, service worker |
| WhatsApp | ✅ Complet | Meta Cloud API, webhook, state machine |
| Email | ✅ Complet | Digest pipeline, templates |
| Notification in-app | ✅ Complet | Store Zustand + sonner toasts |

### 2.8 Admin — 13 pages

| Page | Fonctionnalité |
|------|---------------|
| Dashboard admin | Vue d'ensemble, audit logs |
| Cache | Stats, purge, invalidation par pattern |
| Jobs/Scheduler | Liste jobs, trigger manuel, logs d'exécution |
| Notifications | Test tous canaux (ntfy, push, email, WhatsApp) |
| Services | Health checks, statut services |
| Events | Bus d'événements, historique |
| Utilisateurs | Gestion comptes |
| Feature flags | Activation/désactivation features |
| SQL Views | Vues SQL directes |
| Console | Console admin (requêtes manuelles) |
| IA Metrics | Métriques d'utilisation IA |
| Automations | Gestionnaire automations |
| WhatsApp Test | Test webhook WhatsApp |

### 2.9 Stack visuel frontend

| Technologie | Usage |
|------------|-------|
| Tailwind CSS v4 | Styling principal |
| shadcn/ui (29 composants) | Composants de base |
| Recharts | Graphiques classiques |
| D3.js | Visualisations avancées (Sankey, treemap) |
| Three.js (react-three-fiber) | Plan 3D maison |
| Leaflet | Cartes |
| Framer Motion | Animations |
| DnD Kit | Drag & drop dashboard |

### 2.10 Composants graphiques existants — 16 visualisations

| Composant | Type | Module |
|-----------|------|--------|
| `treemap-budget.tsx` | Treemap D3 | Budget |
| `heatmap-nutritionnel.tsx` | Heatmap | Nutrition |
| `sankey-flux-financiers.tsx` | Sankey D3 | Finances |
| `radar-skill-jules.tsx` | Radar | Jules |
| `radar-nutrition-famille.tsx` | Radar | Nutrition |
| `graphique-roi.tsx` | Ligne/Barre | ROI |
| `graphique-jalons.tsx` | Timeline | Jules jalons |
| `camembert-budget.tsx` | Pie chart | Budget |
| `calendrier-energie.tsx` | Calendrier heatmap | Énergie |
| `sparkline.tsx` | Mini graphe inline | Dashboard |
| `heatmap-numeros.tsx` | Heatmap | Loto numéros |
| `heatmap-cotes.tsx` | Heatmap | Paris cotes |
| `plan-3d.tsx` | Three.js 3D | Maison plan |
| `vue-jardin-interactive.tsx` | Canvas interactif | Jardin |
| `graphe-reseau-modules.tsx` | Network graph | Admin |

### 2.11 Jobs CRON existants — 55+ jobs

| Plage horaire | Jobs |
|---------------|------|
| **Matin (6h-9h)** | Rappels famille, alertes péremption, vérif stocks, météo, briefing matinal |
| **Soir (17h-23h)** | Digest quotidien, planning auto, résultats sportifs, sync jeux |
| **Hebdo** | Résumé famille (lun 7h30), planning semaine (dim 18h), jardin |
| **Mensuel** | Bilan budget, énergie, rapport mensuel |
| **Maintenance** | Cache cleanup (2h), backup DB (1h), purge logs |

### 2.12 Tests — État actuel

| Métrique | Valeur |
|----------|--------|
| Tests collectés | 4907 |
| Tests fonctionnels | ✅ Tous passent |
| Coverage backend cible | 82% |
| Coverage frontend cible | 50% lignes, 40% branches |
| Tests E2E backend | 1 fichier (minimal) |
| Tests E2E frontend | Playwright configuré |
| Tests de charge | 1 fichier (minimal) |

### 2.13 Documentation — 44 fichiers

**Points positifs** : Architecture documentée, guides utilisateur, API Reference complète, docs inter-modules.

**Problèmes identifiés** :

| Problème | Fichiers concernés |
|----------|-------------------|
| Docs sprint-spécifiques | `SPRINT13_COMPLETION_SUMMARY.md`, `SPRINT13_INTEGRATION_GUIDE.md`, `SPRINT13_QUICKSTART.md` |
| Références garanties/contrats | `API_REFERENCE.md`, `API_SCHEMAS.md`, `MODULES.md`, `guides/maison/` |
| Références RGPD | `user-guide/FAQ.md` |
| `CHANGELOG_MODULES.md` | Historique de sprints |
| Docs CRON avec jobs supprimés | `CRON_JOBS.md` |

---

## 3. Phase 1 — Nettoyage et dette technique

> **Objectif** : Codebase propre, sans dette technique, sans code mort.
> **Prérequis** : Aucun
> **Validation** : `pytest` complet + `npm run build` frontend sans erreur
> **Statut** : 🟡 En cours — Sprints 1.1 (partiel), 1.3, 1.4 (partiel), 1.5 (partiel), 1.6 (partiel), 1.7 (partiel) complétés. Sprint 1.2 reporté. ✅ 4907 tests passent, build frontend OK.

### 3.1 Bugs et problèmes identifiés

#### Fichiers fourre-tout

| Fichier | Lignes | Problème |
|---------|--------|----------|
| `src/services/innovations/service.py` | ~999 | 60+ méthodes mélangées : suggestions repas, énergie, analytics, WhatsApp, batch cooking, comparateur prix, mode vacances |
| `src/api/routes/admin.py` | ~800 | 65+ endpoints : santé, config, logs, backups, métriques, users |
| `src/api/routes/dashboard.py` | ~1000 | Dashboard + gamification + stats famille |

#### Code legacy / rétrocompatibilité — 50+ occurrences

| Pattern | Occurrences | Fichiers concernés |
|---------|-------------|-------------------|
| Champs legacy dans modèles | 8-10 | `models/planning.py`, `models/jeux.py` |
| Validateurs legacy | 5-7 | `schemas/phase_b.py` — `_legacy_single_article` |
| `TypeNotificationLegacy` | 3 | `store-notifications.ts` |
| Shims compatibilité | 20+ | `jeux/euromillions_ia.py`, `jeux/bankroll_manager.py` — `_to_legacy_grille()` |
| `cleanup_legacy_cache()` | 2 | `core/caching/file.py` |
| Ancien format planning | 3 | `cuisine/planning/service.py` — support "jour_0" vs "jour_0_midi/soir" |
| Fonctions deprecated | 5 | `core/exceptions.py` |
| Pagination backward | 3 | `api/pagination.py` |
| Ré-exports rétrocompat | 4 | `integrations/images/generator.py` |

#### Références phase/sprint dans le code — 150+ commentaires

- Docstrings : `"Phase 9 et 10 du planning"`, `"S21 IN1"`, `"P9-01"`
- Cache keys : `"phase_e_score_famille_hebdo"`
- Section headers : `# PHASE 8 — Connexions inter-modules`
- Décorateurs : `@chronometre("innovations.p9.mange_ce_soir")`
- Classes de test : `TestEventsPhaseB`, `TestSprintE2E`

#### Stubs et code mort

| Fichier | Problème |
|---------|----------|
| `frontend/src/composants/maison/drawer-garantie.tsx` | Stub 2 lignes : `"fonctionnalité non retenue"` |
| `src/services/innovations/service.py` | Méthodes appelant des helpers privés inexistants |
| `data/exports/` | 152 fichiers ZIP d'exports RGPD de test |

---

### 3.2 Tâches Phase 1 — Détail complet

#### Sprint 1.1 — Suppression des modules obsolètes

##### 1.1.1 RGPD → Backup personnel

| # | Tâche | Fichiers | Statut |
|---|-------|----------|--------|
| 1 | Supprimer `src/api/routes/rgpd.py` | Route API | ✅ |
| 2 | Ajouter endpoint `POST /api/v1/export/backup` dans `export.py` | Route API | ✅ |
| 3 | Supprimer `src/api/schemas/rgpd.py`, ajouter `BackupResponse(url, date)` dans `export.py` | Schéma | ✅ |
| 4 | Refactorer `src/services/core/utilisateur/rgpd.py` → extraire export ZIP dans `backup_personnel.py`, supprimer le reste (droit à l'oubli, data summary, conformité) | Service | ✅ |
| 5 | Supprimer `frontend/src/bibliotheque/api/rgpd.ts`, ajouter `exporterBackup()` dans `export.ts` | Client API | ✅ |
| 6 | Modifier `parametres/onglet-donnees.tsx` : remplacer section RGPD par bouton "Télécharger mon backup" | Frontend | ✅ |
| 7 | Supprimer `tests/api/test_rgpd.py`, ajouter tests backup dans `test_routes_export.py` | Tests | ✅ |
| 8 | Supprimer les 152 fichiers `data/exports/export_rgpd_*.zip` | Données | ⬜ |
| 9 | Retirer mentions RGPD dans `docs/user-guide/FAQ.md`, garder backup | Docs | ⬜ |
| 10 | Retirer `rgpd_router` de `src/api/main.py` et `routes/__init__.py` | Enregistrement | ✅ |

##### 1.1.2 Garanties → Badge sur fiche équipement

| # | Tâche | Fichiers | Statut |
|---|-------|----------|--------|
| 1 | Simplifier SQL : supprimer tables `garanties`, `incidents_sav` | SQL | ⬜ |
| 2 | Garder colonnes `date_achat` et `duree_garantie_mois` sur table `equipements` | SQL | ⬜ |
| 3 | Ajouter champs sur modèle ORM `Equipement`, supprimer modèle `Garantie` séparé | Modèle | ⬜ |
| 4 | Supprimer endpoints CRUD `/maison/garanties` | Route API | ⬜ |
| 5 | Supprimer `AlerteGarantieResponse`, `GarantieCreate`, etc., enrichir `EquipementResponse` avec `sous_garantie: bool` (calculé) | Schéma | ⬜ |
| 6 | Remplacer `drawer-garantie.tsx` (stub) par badge "Sous garantie ✅ / Hors garantie ❌" sur fiche équipement | Frontend | ⬜ |
| 7 | Supprimer jobs CRON `controle_contrats_garanties`, `check_garanties_expirant` | CRON | ⬜ |
| 8 | Mettre à jour docs maison | Docs | ⬜ |

##### 1.1.3 Contrats → Comparateur d'abonnements

| # | Tâche | Fichiers | Statut |
|---|-------|----------|--------|
| 1 | Renommer modèle `contrats_artisans.py` → `abonnements.py`. Simplifier : `Abonnement(type, fournisseur, prix_mensuel, date_debut, date_fin_engagement, notes)` | Modèle | ⬜ |
| 2 | Types : `eau`, `electricite`, `gaz`, `assurance_habitation`, `assurance_auto`, `chaudiere`, `telephone`, `internet` | Modèle | ⬜ |
| 3 | Ajouter champs `meilleur_prix_trouve`, `fournisseur_alternatif` | Modèle | ⬜ |
| 4 | Remplacer routes `/maison/contrats` → `/maison/abonnements` : CRUD + `GET /maison/abonnements/resume` | Route API | ⬜ |
| 5 | Simplifier SQL : une table `abonnements` remplaçant `contrats`, `contrats_maison`, `factures`. Renommer `comparatifs` → `alternatives_abonnement` | SQL | ⬜ |
| 6 | Créer page `maison/abonnements/page.tsx` : tableau récap, coût total, date fin engagement | Frontend | ⬜ |
| 7 | Remplacer job `sync_contrats_alertes` par rappel simple "Engagement se termine dans 30 jours" | CRON | ⬜ |
| 8 | Mettre à jour docs maison | Docs | ⬜ |

---

#### Sprint 1.2 — Éclater les fichiers fourre-tout

> **⏳ Reporté** — Analyse complète réalisée : admin.py (57 endpoints, 8 domaines mappés), innovations/service.py (77 méthodes, 5 services cibles), dashboard.py (20 endpoints, 3 modules). Refactoring dédié prévu en session séparée pour minimiser les risques de régression.

##### 1.2.1 Éclater `innovations/service.py` (999 lignes → 5 services)

| Nouveau service | Méthodes à déplacer |
|----------------|---------------------|
| `src/services/cuisine/suggestions_repas.py` | `mange_ce_soir()`, `recettes_rapides()`, `patterns_recettes()` |
| `src/services/maison/energie_ia.py` | `anomalies_energie()`, `eco_scoring()`, `puissance_linky()` |
| `src/services/famille/analytics_famille.py` | `score_famille_hebdo()`, `journal_familial()`, `rapport_mensuel()` |
| `src/services/integrations/comparateur_prix.py` | `comparateur_prix()`, `veille_prix()` |
| `src/services/ia/assistant_mode.py` | `mode_pilote()`, `mode_vacances()`, `coach_routines()` |

→ Puis **supprimer** `src/services/innovations/` entièrement.

##### 1.2.2 Éclater `admin.py` (800 lignes → 5 fichiers)

| Nouveau fichier | Contenu |
|----------------|---------|
| `admin_sante.py` | Health checks, statut services |
| `admin_cache.py` | Stats cache, purge, invalidation |
| `admin_jobs.py` | Jobs CRON, trigger, logs |
| `admin_users.py` | Gestion utilisateurs |
| `admin_logs.py` | Logs, audit, métriques |

##### 1.2.3 Éclater `dashboard.py` (1000 lignes → 3 fichiers)

| Nouveau fichier | Contenu |
|----------------|---------|
| `dashboard_accueil.py` | Données page d'accueil |
| `dashboard_gamification.py` | Badges, streaks, points |
| `dashboard_stats.py` | Stats famille, métriques agrégées |

---

#### Sprint 1.3 — Renommage fichiers sprint/phase → fonctionnel

| # | Fichier actuel | Nouveau nom | Statut |
|---|----------------|-------------|--------|
| 1 | `src/api/routes/ia_sprint13.py` | `ia_modules.py` | ✅ |
| 2 | `src/api/schemas/sprint13_ai.py` | `ia_modules.py` | ✅ |
| 3 | `src/services/core/cron_phase_b.py` | `cron_bridges.py` | ✅ |
| 4 | `src/api/routes/notifications_sprint_e.py` | `notifications_enrichies.py` | ✅ |
| 5 | `src/services/core/notifications/notifications_enrichis_sprint_e.py` | `notifications_enrichies.py` | ✅ |
| 6 | `frontend/src/crochets/utiliser-sprint13-ia.ts` | `utiliser-ia-modules.ts` | ✅ |
| 7 | `frontend/src/bibliotheque/api/ia-sprint13.ts` | `ia-modules.ts` | ✅ |
| 8 | `tests/test_sprint_12_bridges.py` | `test_bridges_inter_modules.py` | ✅ |
| 9 | `tests/services/test_sprint13_simple.py` | `test_ia_modules.py` | ✅ |
| 10 | `tests/services/test_sprint13_new_ai_services.py` | `test_ia_services.py` | ✅ |
| 11 | `tests/inter_modules/test_bridges_sprint6.py` | `test_bridges_base.py` | ✅ |
| 12 | `tests/inter_modules/test_bridges_sprint11.py` | `test_bridges_avances.py` | ✅ |
| 13 | `tests/services/famille/test_sprint14_events.py` | `test_famille_events.py` | ✅ |
| 14 | `tests/e2e/test_sprint13_integration.py` | `test_ia_integration.py` | ✅ |
| 15 | `tests/api/test_routes_ia_sprint13.py` | `test_routes_ia_modules.py` | ✅ |

→ Après renommage : mettre à jour **tous les imports** dans le codebase.

---

#### Sprint 1.4 — Nettoyage code legacy

| # | Tâche | Statut |
|---|-------|--------|
| 1 | Supprimer champs "legacy" dans les modèles ORM, migrer colonnes | ⬜ |
| 2 | Supprimer validateur `_legacy_single_article` et ancien format | ⬜ |
| 3 | Supprimer `TypeNotificationLegacy` mapping, utiliser types modernes | ✅ |
| 4 | Supprimer `_to_legacy_grille()` et shims jeux, adapter callers | ✅ |
| 5 | Supprimer `cleanup_legacy_cache()`, support pickle → JSON only | ⬜ |
| 6 | Supprimer support ancien format "jour_0" planning, garder "jour_0_midi/soir" | ⬜ |
| 7 | Supprimer fonctions deprecated dans `core/exceptions.py` | ⬜ |
| 8 | Supprimer ré-exports rétrocompat images, mettre à jour imports | ⬜ |

---

#### Sprint 1.5 — Nettoyage commentaires, doublons, docs

| # | Tâche | Statut |
|---|-------|--------|
| 1 | Nettoyer les 150+ commentaires de phases/sprints → noms fonctionnels | ⬜ |
| 2 | Renommer cache keys : `"phase_e_score_famille_hebdo"` → `"score_famille_hebdo"` | ⬜ |
| 3 | Renommer décorateurs métriques : `"innovations.p9.mange_ce_soir"` → `"cuisine.mange_ce_soir"` | ⬜ |
| 4 | Renommer classes de test : `TestEventsPhaseB` → `TestEventsBridges` | ⬜ |
| 5 | Fusionner `utilitaires.ts` + `utils.ts` dans frontend → un seul `utils.ts` | ✅ |
| 6 | Factoriser `bandeau-meteo.tsx` (doublon famille/maison) → `composants/partages/` | ✅ N/A — Pas de doublon (composants famille/maison utilisent des types différents) |
| 7 | Supprimer `docs/SPRINT13_COMPLETION_SUMMARY.md` | ✅ |
| 8 | Supprimer `docs/SPRINT13_INTEGRATION_GUIDE.md` | ✅ |
| 9 | Supprimer `docs/SPRINT13_QUICKSTART.md` | ✅ |
| 10 | Supprimer ou convertir `docs/CHANGELOG_MODULES.md` → CHANGELOG fonctionnel | ✅ |
| 11 | Supprimer `scripts/_archive/` | ✅ |
| 12 | Supprimer stub `drawer-garantie.tsx` | ✅ |

---

#### Sprint 1.6 — SQL et régénération

| # | Tâche | Statut |
|---|-------|--------|
| 1 | Supprimer tables `garanties`, `incidents_sav` dans `06_maison.sql` | ⬜ |
| 2 | Remplacer tables `contrats`, `contrats_maison`, `factures` → `abonnements` | ⬜ |
| 3 | Renommer `comparatifs` → `alternatives_abonnement` | ⬜ |
| 4 | Vérifier et nettoyer `10_finances.sql` (refs contrats) | ⬜ |
| 5 | Nettoyer `12_triggers.sql` (triggers garanties/contrats) | ✅ |
| 6 | Nettoyer `15_rls_policies.sql` (policies tables supprimées) | ✅ |
| 7 | Lancer `python scripts/audit_orm_sql.py` pour détecter désalignements | ⬜ |
| 8 | Régénérer `INIT_COMPLET.sql` | ⬜ |

---

#### Sprint 1.7 — Tests et documentation

| # | Tâche | Statut |
|---|-------|--------|
| 1 | Supprimer/adapter tests modules supprimés (RGPD, garanties, contrats) | ✅ |
| 2 | Renommer tests avec noms de sprint → noms fonctionnels | ✅ |
| 3 | Mettre à jour classes de test (noms de phase → fonctionnels) | ⬜ |
| 4 | Nettoyer `docs/API_REFERENCE.md` (retirer garanties, contrats, RGPD) | ⬜ |
| 5 | Nettoyer `docs/API_SCHEMAS.md` (idem) | ⬜ |
| 6 | Mettre à jour `docs/MODULES.md` (retirer modules supprimés) | ⬜ |
| 7 | Mettre à jour `docs/CRON_JOBS.md` (retirer jobs supprimés) | ⬜ |
| 8 | Mettre à jour `docs/guides/maison/` (retirer garanties/contrats) | ⬜ |
| 9 | Mettre à jour `docs/INDEX.md` (refléter nouvelle structure) | ⬜ |
| 10 | Lancer `pytest` complet — fixer toute régression | ✅ |
| 11 | Lancer `npm run build` frontend — fixer toute erreur | ✅ |

---

## 4. Phase 2 — Consolidation inter-modules

> **Objectif** : Les modules communiquent entre eux automatiquement via l'EventBus.
> **Prérequis** : Phase 1 terminée
> **Mécanisme** : EventBus `src/services/core/events/` avec subscribers dédiés

### 4.1 Pattern de référence pour les bridges

```python
# Dans subscribers.py — bridge planification → courses
@event_handler("planning.semaine_validee")
async def generer_courses_depuis_planning(event):
    """Génère automatiquement la liste de courses à partir du planning validé."""
    planning = event.data
    courses_service = get_courses_service()
    courses_service.generer_depuis_planning(planning)
```

### 4.2 Nouveaux bridges à implémenter

| # | Bridge | Source → Destination | Priorité | Statut |
|---|--------|---------------------|----------|--------|
| 1 | **Planning → Courses auto** | Planning semaine validé → Liste courses générée | 🔴 Haute | ⬜ |
| 2 | **Inventaire → Anti-gaspi IA** | Stock bientôt périmé → Recettes de récupération IA | 🔴 Haute | ⬜ |
| 3 | **Budget → Dashboard alertes** | Seuil budget dépassé → Notification + widget dashboard | 🔴 Haute | ⬜ |
| 4 | **Activités → Timeline Jules** | Activité terminée → Jalon enregistré automatiquement | 🟡 Moyenne | ⬜ |
| 5 | **Projets → Calendrier unifié** | Tâche projet avec deadline → Événement calendrier | 🟡 Moyenne | ⬜ |
| 6 | **Jardin saison → Recettes** | Légumes de saison du jardin → Suggestions recettes | 🟡 Moyenne | ⬜ |
| 7 | **Résultats jeux → Dashboard** | Résultat automatisé → Stats P&L auto | 🟡 Moyenne | ⬜ |
| 8 | **Météo → Activités weekend** | Prévisions → Suggestions activités adaptées | 🟢 Basse | ⬜ |
| 9 | **Entretien → Rappels push** | Tâche entretien due → Notification matin | 🟢 Basse | ⬜ |

### 4.3 Connexions IA à finaliser

| # | Tâche | Détail | Priorité | Statut |
|---|-------|--------|----------|--------|
| 1 | **Photo frigo → recettes** | Connecter le composant `photo-frigo` existant frontend à l'IA vision backend. L'utilisateur photographie son frigo, l'IA identifie les ingrédients et propose des recettes. | 🔴 Haute | ⬜ |
| 2 | **Adaptation recettes Jules** | Adapter automatiquement chaque recette pour Jules (sans sel, mixé, portions adaptées). Utiliser `data/reference/portions_age.json`. | 🔴 Haute | ⬜ |

### 4.4 Tests inter-modules

| # | Tâche | Statut |
|---|-------|--------|
| 1 | Tests pour chaque nouveau bridge (événement émis → action exécutée) | ⬜ |
| 2 | Tests d'intégration : planning validé → courses générées → notification envoyée | ⬜ |
| 3 | Tests bridge photo-frigo → recettes | ⬜ |
| 4 | Tests adaptation recettes Jules (portions, restrictions) | ⬜ |

---

## 5. Phase 3 — IA et automatisations

> **Objectif** : L'IA anticipe et réduit le travail manuel.
> **Prérequis** : Phase 2 terminée

### 5.1 Nouvelles intégrations IA

| # | Module | Intégration | Description | Priorité | Statut |
|---|--------|-------------|-------------|----------|--------|
| 1 | Inventaire | Prédiction besoins stocks | Analyser l'historique de consommation pour prédire quand un produit sera épuisé | 🟡 Moyenne | ⬜ |
| 2 | Maison | Optimisation planning entretien | L'IA analyse tâches, météo et propose un planning optimal | 🟡 Moyenne | ⬜ |
| 3 | Jeux | Analyse tendances paris | Analyse cotes, value bets, couche narrative sur backtest existant | 🟡 Moyenne | ⬜ |
| 4 | Famille | Journal automatique enrichi | Résumé journal quotidien à partir des événements (repas, activités, météo) | 🟢 Basse | ⬜ |
| 5 | Dashboard | Insights proactifs | L'IA scanne les données et propose des insights non demandés | 🟢 Basse | ⬜ |
| 6 | Jardin | Calendrier plantation IA | Proposer calendrier plantation par zone géo, saison, plantes existantes | 🟢 Basse | ⬜ |

### 5.2 Points IA backend non exposés en frontend

| Service implémenté backend | Frontend manquant | Statut |
|----------------------------|-------------------|--------|
| Prédiction courses | Pas de page/widget dédié | ⬜ |
| Scoring nutrition avancé | Pas de visualisation détaillée | ⬜ |
| Suggestions jardinage | Pas de widget jardin IA | ⬜ |
| Recommandations proactives | Bannière existe mais contenu limité | ⬜ |

### 5.3 Streaming IA frontend

| # | Tâche | Statut |
|---|-------|--------|
| 1 | Implémenter le rendu progressif côté frontend pour les réponses IA | ⬜ |
| 2 | Connecter au streaming Mistral backend (déjà supporté) | ⬜ |
| 3 | Composant réutilisable `stream-ia.tsx` avec animation typing | ⬜ |

### 5.4 Nouveaux jobs CRON

| # | Job | Schedule | Description | Priorité | Statut |
|---|-----|----------|-------------|----------|--------|
| 1 | Cohérence planning ↔ courses | Dim 19h | Vérifier que tous les ingrédients du planning sont dans la liste de courses | 🔴 Haute | ⬜ |
| 2 | Alerte budget instantanée | Quotidien 20h | Si dépenses > X% du budget prévu, notifier | 🔴 Haute | ⬜ |
| 3 | Sync résultats paris auto | Après matchs | Récupérer résultats et mettre à jour les paris | 🟡 Moyenne | ⬜ |
| 4 | Rapport jardin saisonnier | 1er/mois | Résumé : ce qu'il faut planter, récolter, entretenir | 🟡 Moyenne | ⬜ |
| 5 | Nettoyage exports anciens | Hebdo dim 3h | Supprimer exports > 30 jours | 🟢 Basse | ⬜ |
| 6 | Health check services IA | Toutes les 6h | Vérifier Mistral, alerter si circuit breaker ouvert | 🟢 Basse | ⬜ |

### 5.5 Notifications enrichies

> **Note** : Les canaux WhatsApp ci-dessous seront remplacés par Telegram après la migration (voir [section 9](#9-migration-whatsapp--telegram)).

| # | Notification | Canal | Trigger | Priorité | Statut |
|---|-------------|-------|---------|----------|--------|
| 1 | "Recette du soir" rappel | Telegram + Push | 16h si repas planifié, avec lien recette | 🔴 Haute | ⬜ |
| 2 | "Courses prêtes" | Telegram | Après génération auto courses | 🔴 Haute | ⬜ |
| 3 | "Budget alerte" | Push + Email | Seuil dépassé (job CRON) | 🔴 Haute | ⬜ |
| 4 | "Tâches entretien semaine" | Telegram lundi matin | Résumé tâches planifiées | 🟡 Moyenne | ⬜ |
| 5 | "Résultats paris" | Push | Après sync résultats | 🟡 Moyenne | ⬜ |
| 6 | "Jardin — actions du mois" | Email mensuel | Rapport jardin saisonnier | 🟢 Basse | ⬜ |
| 7 | "Jules — jalon développement" | Push | Quand un jalon est atteint selon l'âge | 🟢 Basse | ⬜ |

### 5.6 Commandes Telegram enrichies

Ajouter des commandes en langage naturel (via Telegram Bot) :
- "Qu'est-ce qu'on mange ce soir ?"
- "Ajoute lait à la liste"
- "Activité samedi ?"
- Réponses interactives via InlineKeyboardMarkup (boutons illimités)

### 5.7 Améliorations admin

| # | Amélioration | Priorité | Statut |
|---|-------------|----------|--------|
| 1 | Bouton "Tout exécuter" — séquence de jobs (planning → courses → notifications) | 🔴 Haute | ⬜ |
| 2 | Log viewer temps réel — WebSocket logs serveur | 🔴 Haute | ⬜ |
| 3 | Mode `--force` bypass conditions sur trigger jobs | 🟡 Moyenne | ⬜ |
| 4 | Log détaillé visible admin UI avec résultats du job | 🟡 Moyenne | ⬜ |
| 5 | Bouton "Relancer" sur chaque job dans admin/scheduler | 🟡 Moyenne | ⬜ |
| 6 | Simulateur de scénarios — "Simuler lundi 7h" pour tester CRON | 🟡 Moyenne | ⬜ |
| 7 | DB explorer — interface lecture seule tables | 🟡 Moyenne | ⬜ |
| 8 | Template preview notifications avant envoi | 🟡 Moyenne | ⬜ |
| 9 | Historique notifications envoyées avec statut livraison | 🟡 Moyenne | ⬜ |
| 10 | Bouton "Simuler notification" (dry-run) | 🟡 Moyenne | ⬜ |
| 11 | Mode maintenance toggle | 🟢 Basse | ⬜ |
| 12 | Métriques IA détaillées — graphiques tokens, coût, cache hits | 🟢 Basse | ⬜ |
| 13 | Modifier schedule jobs depuis admin UI | 🟢 Basse | ⬜ |

---

## 6. Phase 4 — UI/UX moderne

> **Objectif** : Interface belle, fluide, avec des visualisations riches.
> **Prérequis** : Phase 3 terminée

### 6.1 Nouvelles visualisations

| # | Visualisation | Module | Technologie | Priorité | Statut |
|---|--------------|--------|-------------|----------|--------|
| 1 | Timeline interactive famille | Dashboard | D3 / Framer Motion | 🔴 Haute | ⬜ |
| 2 | Kanban drag & drop projets | Maison/Travaux | DnD Kit | 🔴 Haute | ⬜ |
| 3 | Graphique croissance Jules OMS | Famille/Jules | Recharts | 🔴 Haute | ⬜ |
| 4 | Calendrier mosaïque repas | Cuisine/Planning | Grid CSS + images | 🔴 Haute | ⬜ |
| 5 | Gauge score bien-être | Dashboard | SVG animé | 🟡 Moyenne | ⬜ |
| 6 | Graphique budget vs réel | Famille/Budget | Recharts barres groupées | 🟡 Moyenne | ⬜ |
| 7 | Treemap inventaire | Cuisine/Inventaire | D3 | 🟡 Moyenne | ⬜ |
| 8 | Carte zones jardin 2D | Maison/Jardin | Canvas/SVG | 🟡 Moyenne | ⬜ |
| 9 | Dashboard widgets configurables | Dashboard | DnD Kit | 🟡 Moyenne | ⬜ |
| 10 | Animations transitions pages | Global | Framer Motion | 🟢 Basse | ⬜ |
| 11 | Vue "focus du jour" | Ma Journée | Layout cards | 🟢 Basse | ⬜ |

### 6.2 Améliorations design existant

| # | Amélioration | Détail | Priorité | Statut |
|---|-------------|--------|----------|--------|
| 1 | Mode sombre cohérent | Audit toutes les pages, composants custom | 🔴 Haute | ⬜ |
| 2 | Responsive mobile | Audit toutes les pages, vérifier débordements | 🔴 Haute | ⬜ |
| 3 | Empty states | Illustrations/messages pour les pages vides au premier lancement | 🔴 Haute | ⬜ |
| 4 | Loading skeletons | Remplacer spinners par skeletons shadcn partout | 🟡 Moyenne | ⬜ |
| 5 | Animations micro-interactions | Hover effects, click feedback, transitions douces | 🟡 Moyenne | ⬜ |
| 6 | Confettis célébration | Utiliser `confettis.ts` existant pour jalons Jules, badges | 🟢 Basse | ⬜ |

---

## 7. Phase 5 — Simplification des flux + Validation v2

> **Objectif** : L'utilisateur fait le minimum, l'app fait le reste. IA propose, utilisateur valide, app exécute.
> **Prérequis** : Phase 4 terminée
> **Principe** : Les "3 clics" ne suppriment pas la validation — ils suppriment la **saisie**. L'utilisateur garde le contrôle mais ne tape rien.

### 7.1 Flux actuels vs flux simplifiés

| Flux actuel | Étapes actuelles | Flux simplifié | Étapes simplifiées |
|------------|------------------|----------------|-------------------|
| Planifier la semaine | 1. Aller dans planning 2. Choisir chaque repas 3. Valider 4. Aller dans courses 5. Ajouter ingrédients | 1. L'IA propose un planning 2. Valider/ajuster 3. Courses auto | 2-3 clics |
| Ajouter une recette | 1. Aller dans recettes 2. Remplir formulaire complet | 1. Coller un lien ou décrire en texte 2. IA pré-remplit tout 3. Valider | 2-3 clics |
| Gérer les courses | 1. Ouvrir liste 2. Cocher un par un 3. Retirer les cochés | 1. Articles viennent du planning auto 2. Vue par rayon 3. Swipe pour cocher | 1-2 gestes |
| Saisir activité weekend | 1. Famille 2. Activités 3. Formulaire 4. Date/heure | 1. Via Telegram : "Ajoute parc samedi 14h" | 1 message |
| Vérifier budget | 1. Famille 2. Budget 3. Graphiques | 1. Widget dashboard + alerte push si anomalie | 0 action |

### 7.2 Tâches de simplification

| # | Tâche | Description | Priorité | Statut |
|---|-------|-------------|----------|--------|
| 1 | **Flux 3-clics cuisine** | Planning IA → Validation → Courses auto. Le flux B7 existe partiellement — le finaliser. | 🔴 Haute | ⬜ |
| 2 | **Import recette par lien** | `dialogue-import-recette.tsx` et `importer.py` existent. Vérifier pré-remplissage IA complet. | 🔴 Haute | ⬜ |
| 3 | **Scan codes-barres → inventaire** | Composant `scanneur-multi-codes.tsx` + `@zxing/browser` existent. Connecter au service inventaire. | 🟡 Moyenne | ⬜ |
| 4 | **Briefing vocal matin** | `bouton-vocal.tsx`, hooks `synthese-vocale`/`reconnaissance-vocale` existent. Briefing backend existe. Connecter. | 🟡 Moyenne | ⬜ |
| 5 | **Widgets dashboard actionnables** | Chaque widget doit avoir un CTA direct (pas juste de l'info) | 🟡 Moyenne | ⬜ |
| 6 | **Notifications actionnables** | Chaque notification push/Telegram doit avoir un lien direct | 🟡 Moyenne | ⬜ |
| 7 | **Onboarding premier lancement** | `tour-onboarding.tsx` existe — vérifier le guidage | 🟢 Basse | ⬜ |
| 8 | **Google Assistant deep linking** | Page `google-assistant/page.tsx` existe, doc setup aussi. Vérifier Actions on Google. | 🟢 Basse | ⬜ |
| 9 | **PWA + offline** | `install-prompt.tsx`, `utiliser-hors-ligne.ts`, `enregistrement-sw.tsx` existent. Vérifier fonctionnel. | 🟢 Basse | ⬜ |

### 7.3 Innovations pertinentes

| Innovation | Module | Complexité | Statut |
|-----------|--------|-----------|--------|
| **Mode tablette cuisine** | Cuisine | Moyenne | ⬜ |
| **Dashboard personnalisable** | Dashboard | Moyenne | ⬜ |
| **Leaflet carte activités** | Famille | Moyenne | ⬜ |
| **Comparateur prix ingrédients** (frontend) | Cuisine | Moyenne | ⬜ |

### 7.4 Automatisations intelligentes

| Automatisation | Trigger | Action | Module | Statut |
|---------------|---------|--------|--------|--------|
| Inventaire auto-replenish | Stock < seuil minimum | Ajouter à la liste de courses | Inventaire → Courses | ⬜ |
| Suggestion weekend auto | Vendredi soir si rien planifié | IA propose activités selon météo + historique | Famille | ⬜ |
| Archivage projets terminés | Projet "terminé" depuis 30j | Archiver automatiquement | Maison | ⬜ |
| Rappel anniversaire J-7 | 7j avant anniversaire | Notification + suggestions cadeaux IA | Famille | ⬜ |
| Bilan mensuel auto | 1er du mois | Générer et envoyer bilan complet par email | Rapports | ⬜ |

### 7.5 Flux validation brouillon (v2)

Le flux actuel (`src/services/ia/flux_utilisateur.py`, `src/api/routes/intra_flux.py`) détecte automatiquement l'étape mais ne propose pas de brouillon éditable et passe directement à la génération de courses.

**Nouveau flux cuisine : IA → Brouillon → Validation → Courses** :

```
Étape 1 — Proposition IA (automatique, dimanche soir ou à la demande)
  └─ L'IA génère un planning semaine → statut "brouillon"
  └─ Telegram : message avec boutons [✅ Valider] [✏️ Modifier] [🔄 Régénérer]
  └─ Web : bandeau jaune "Brouillon — En attente de validation"

Étape 2 — Validation utilisateur (OBLIGATOIRE, via web OU Telegram)
  └─ Telegram : tap sur ✅ Valider ou écrire "Remplace mardi par du poisson"
  └─ Web : clic sur bouton Valider / Modifier / Régénérer
  └─ Statut passe à "validé" → déclenche étape 3

Étape 3 — Courses générées (brouillon)
  └─ Liste générée automatiquement depuis planning validé → statut "brouillon"
  └─ Telegram : message avec [✅ Confirmer] [✏️ Ajouter] [❌ Refaire]
  └─ Web : même pattern bandeau + boutons

Étape 4 — Confirmation courses (OBLIGATOIRE)
  └─ Telegram : tap ✅ Confirmer
  └─ Web : clic Confirmer la liste
  └─ Statut passe à "active" → mode courses (swipe pour cocher)
```

**Résultat** : 2 validations explicites (planning + courses), 0 saisie manuelle, 4 clics max.

#### Modèle brouillon/validation par entité

| Entité | Statuts | Qui crée | Qui valide |
|--------|---------|----------|------------|
| **Planning semaine** | `brouillon` → `valide` → `archive` | IA ou CRON | Utilisateur (web ou Telegram) |
| **Liste de courses** | `brouillon` → `active` → `terminee` | Bridge depuis planning | Utilisateur (web ou Telegram) |
| **Suggestions weekend** | `suggeree` → `planifiee` → `terminee` | IA | Utilisateur |
| **Sessions batch cooking** | `brouillon` → `en_cours` → `termine` | IA | Utilisateur |

**NE nécessitent PAS de validation** (informatifs) : alertes péremption, briefing matin, rappels entretien, insights budget, suggestions recettes ponctuelles.

#### Règles validation par module

| Module | IA propose | Validation obligatoire ? | Sans validation |
|--------|-----------|--------------------------|------------------|
| **Planning repas** | Planning semaine | ✅ Oui (web ou Telegram) | Non |
| **Liste courses** | Articles depuis planning | ✅ Oui (web ou Telegram) | Non |
| **Activités weekend** | Suggestions d'activités | ✅ Si ajouté au calendrier | Consulter = OK |
| **Batch cooking** | Sessions proposées | ✅ Avant de lancer | Non |
| **Suggestions recettes** | "Ce soir..." | ❌ Informatif | — |
| **Alertes péremption** | Recettes anti-gaspi | ❌ Informatif | — |
| **Briefing matin** | Résumé journée | ❌ Informatif | — |
| **Entretien maison** | Tâches semaine | Optionnel (marquer planifié) | Rappels auto OK |
| **Budget alerte** | Seuil dépassé | ❌ Informatif | — |

#### Tâches techniques validation v2

| # | Tâche | Fichiers | Statut |
|---|-------|----------|--------|
| 1 | Ajouter `etat: Mapped[str]` sur modèle Planning (brouillon/valide/archive) | `src/core/models/planning.py` | ⬜ |
| 2 | Ajouter `etat: Mapped[str]` sur modèle ListeCourses (brouillon/active/terminee) | `src/core/models/courses.py` | ⬜ |
| 3 | Modifier flux utilisateur : bloquer auto-progression, étape 2 = valider le brouillon | `src/services/ia/flux_utilisateur.py` | ⬜ |
| 4 | Ajouter `POST /api/v1/planning/{id}/valider` et `POST /api/v1/planning/{id}/regenerer` | `src/api/routes/planning.py` | ⬜ |
| 5 | Ajouter `POST /api/v1/courses/{id}/confirmer` | `src/api/routes/courses.py` | ⬜ |
| 6 | Adapter flux B7 : ne pas auto-générer courses sans validation du planning | `src/api/routes/intra_flux.py` | ⬜ |
| 7 | Bandeau brouillon/validé + boutons valider/modifier/régénérer (frontend planning) | Frontend planning page | ⬜ |
| 8 | Mode brouillon courses avec confirmation obligatoire | Frontend courses page | ⬜ |
| 9 | Migration SQL : `ALTER TABLE planning ADD COLUMN etat VARCHAR(20) DEFAULT 'brouillon'` | `sql/` | ⬜ |
| 10 | Migration SQL : `ALTER TABLE listes_courses ADD COLUMN etat VARCHAR(20) DEFAULT 'brouillon'` | `sql/` | ⬜ |
| 11 | InlineKeyboardMarkup Telegram avec boutons ✅/✏️/🔄 | `src/services/integrations/telegram.py` | ⬜ |
| 12 | Handler `callback_query` Telegram → endpoints validation | `src/api/routes/webhooks_telegram.py` | ⬜ |
| Bilan mensuel auto | 1er du mois | Générer et envoyer bilan complet par email | Rapports | ⬜ |

---

## 8. Phase 6 — Optimisation technique + Railway

> **Objectif** : Performance, bundle size, robustesse, rester en Free Railway ($0/mois).
> **Prérequis** : Phase 5 terminée

### 8.1 Améliorations techniques

| # | Amélioration | Description | Impact | Statut |
|---|-------------|-------------|--------|--------|
| 1 | **Bundle analysis** | `@next/bundle-analyzer` installé. Analyser et optimiser. Lazy load Three.js (lourd). | Performance | ⬜ |
| 2 | **SSR pages publiques** | Pages login/inscription en SSR pour performance | Performance | ⬜ |
| 3 | **Optimistic updates** | TanStack Query supporte. Ajouter pour CRUD courant (cocher course, ajouter note). | UX | ⬜ |
| 4 | **Prefetch routes** | Next.js 16 supporte. Ajouter sur les liens navigation fréquents. | Performance | ⬜ |

### 8.2 Optimisations mémoire Railway — OBLIGATOIRES

Ces optimisations sont nécessaires pour tenir sous 0.5 GB RAM (limite Railway Free).

| # | Optimisation | Description | Gain estimé | Fichiers | Statut |
|---|-------------|-------------|-------------|----------|--------|
| 1 | **Cache L1 mémoire borné** | Limiter `CacheMemoire` à 500 entrées max avec eviction LRU | -50-100 MB | `src/core/caching/memory.py` | ⬜ |
| 2 | **Lazy-load modèles IA** | `ClientIA`, `AnalyseurIA` instanciés au premier appel, pas au démarrage | -30 MB | `src/core/ai/client.py` | ⬜ |
| 3 | **Import lazy services** | 138 factories importés au démarrage → passer en importlib lazy | -20 MB | `src/services/core/registry.py` | ⬜ |
| 4 | **1 worker uvicorn** | `uvicorn --workers 1` (déjà le cas) | Déjà OK | — | ✅ |
| 5 | **Désactiver Prometheus** | Métriques Prometheus consomment mémoire → flag pour désactiver | -10 MB | `src/api/prometheus.py` | ⬜ |

### 8.3 Optimisations Mistral AI

| Métrique | Valeur |
|----------|--------|
| Limite quotidienne | 100 appels/jour |
| Limite horaire | 30 appels/heure |
| Usage CRON actuel | ~0.29 appel/jour (<1%) |

| # | Optimisation | Description | Statut |
|---|-------------|-------------|--------|
| 1 | Cache sémantique TTL 48h | Augmenter TTL du `CacheIA` à 48h pour suggestions récurrentes | ⬜ |
| 2 | Batch prompts | Combiner résumé hebdo + planning IA dimanche en un seul prompt | ⬜ |
| 3 | Fallback règles locales | Catégorisation ingrédients, calcul portions → règles Python | ⬜ |
| 4 | Rate limit utilisateur | Limiter chat IA à 20 messages/jour/utilisateur | ⬜ |

### 8.4 Tests avancés

| # | Tâche | Statut |
|---|-------|--------|
| 1 | Tests E2E flux critiques (inscription → connexion → recette → planifier → courses) | ⬜ |
| 2 | Tests de charge production (simuler usage réel) | ⬜ |
| 3 | Tests visuels screenshots pages principales | ⬜ |
| 4 | Fixer test WebSocket courses (skip deadlock → revoir async) | ⬜ |
| 5 | Tests mode hors-ligne frontend | ⬜ |
| 6 | Tests service worker PWA | ⬜ |

### 8.5 Tests manquants identifiés

| Module | Manque | Statut |
|--------|--------|--------|
| Bridges inter-modules | Tests pour les nouveaux bridges | ⬜ |
| Admin panel | Tests endpoints trigger manuel | ⬜ |
| WebSocket courses | Test annoté `@skip` — deadlock TestClient | ⬜ |
| Mode hors-ligne | Aucun test sync offline | ⬜ |
| Service Worker | Pas de tests enregistrement SW | ⬜ |

---

## 9. Migration WhatsApp → Telegram

> **Objectif** : Remplacer WhatsApp Business API (payant) par Telegram Bot API (100% gratuit, illimité).
> **Prérequis** : Phase 3 terminée (notifications enrichies)
> **Impact** : Réduit le coût mensuel de ~2.40€ à 0€, simplifie l'API, boutons illimités.

### 9.1 Pourquoi Telegram remplace WhatsApp

| Critère | WhatsApp Business API (Meta) | Telegram Bot API |
|---------|------------------------------|------------------|
| **Coût messages proactifs** | ~0.02€/msg (Utility) | **Gratuit, illimité** |
| **Coût actuel** | ~2.40€/mois (4 msgs/jour) | **0€** |
| **Fenêtre de réponse** | 24h max pour réponses gratuites | **Aucune limite** |
| **Templates à approuver** | Oui (validation Meta, 24-48h) | **Non requis** |
| **Boutons interactifs** | 3 max par message (reply buttons) | **Illimité** (inline keyboards) |
| **Catégories de messages** | Service / Utility / Marketing / Auth | **Aucune catégorie** |
| **API complexity** | Élevée (webhooks Meta, tokens multiples) | **Simple** (1 token, BotFather) |
| **Disponibilité tablette** | WhatsApp Web (navigateur) | **App native Android + Web** |

### 9.2 Mapping fonctions WhatsApp → Telegram

| Fonction WhatsApp actuelle | Équivalent Telegram | Notes |
|---------------------------|---------------------|-------|
| `envoyer_message_whatsapp()` | `envoyer_message_telegram()` | `sendMessage` avec `parse_mode=HTML` |
| `envoyer_message_interactif()` | `envoyer_message_interactif_telegram()` | `InlineKeyboardMarkup` (illimité vs 3 max) |
| `envoyer_digest_matinal()` | `envoyer_digest_matinal()` | Même contenu, format Telegram |
| `envoyer_planning_semaine()` | `envoyer_planning_semaine()` | + boutons ✅ Valider / ✏️ Modifier / 🔄 Régénérer |
| `envoyer_alerte_peremption()` | `envoyer_alerte_peremption()` | + boutons "Recette anti-gaspi" |
| `envoyer_liste_courses_partagee()` | `envoyer_liste_courses()` | + boutons ✅ Confirmer / ✏️ Ajouter |
| `envoyer_message_liste()` | N/A | Telegram n'a pas de list menus → inline keyboards |
| 6 fonctions Sprint 16 | Mêmes noms, transport Telegram | Recettes, diagnostic, weekend, budget, nutrition, entretien |

**Principe** : mêmes signatures publiques → les CRON jobs et le dispatcher ne changent quasi pas.

### 9.3 Architecture cible

```
src/services/integrations/
├── telegram.py              # NOUVEAU — 14 fonctions publiques (remplace whatsapp.py)
└── whatsapp.py              # SUPPRIMER après migration

src/api/routes/
├── webhooks_telegram.py     # NOUVEAU — webhook Telegram (updates + callback_query)
└── webhooks_whatsapp.py     # SUPPRIMER après migration

src/core/config/settings.py  # Remplacer META_WHATSAPP_* par TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
```

### 9.4 Stratégie notifications par canal

| Canal | Usage | Coût |
|-------|-------|------|
| **Telegram** | Digest matin, planning semaine, courses, weekend, entretien, nutrition, validation interactive, commandes conversationnelles | **$0** |
| **Push Web** (VAPID) | Rappels rapides, alertes péremption, toutes notifications non interactives | **$0** |
| **Email** (SMTP Supabase) | Bilan mensuel PDF, rapports | **$0** |
| **In-app** (sonner) | Toasts, confirmations, micro-interactions | **$0** |

### 9.5 Plan de migration étape par étape

| # | Étape | Fichiers | Statut |
|---|-------|----------|--------|
| 1 | Créer bot Telegram via @BotFather, obtenir token | `.env.local` | ⬜ |
| 2 | Créer `telegram.py` avec les 14 fonctions (mêmes signatures) | `src/services/integrations/telegram.py` | ⬜ |
| 3 | Créer `webhooks_telegram.py` (réception messages + callback_query) | `src/api/routes/webhooks_telegram.py` | ⬜ |
| 4 | Adapter le dispatcher de notifications : canal "telegram" | `src/services/core/notifications/notif_dispatcher.py` | ⬜ |
| 5 | Adapter les notifications enrichies | `src/services/core/notifications/notifications_enrichies.py` | ⬜ |
| 6 | Adapter l'engine d'automations | `src/services/utilitaires/automations_engine.py` | ⬜ |
| 7 | Adapter la config | `src/core/config/settings.py` | ⬜ |
| 8 | Adapter les 4 CRON jobs (imports) | `src/services/core/cron/jobs.py` | ⬜ |
| 9 | Adapter le frontend admin (3 pages) | `frontend/src/app/(app)/admin/` | ⬜ |
| 10 | Adapter les préférences notifications | `frontend/src/app/(app)/parametres/preferences-notifications/` | ⬜ |
| 11 | Adapter les clients API frontend | `frontend/src/bibliotheque/api/admin.ts`, `avance.ts` | ⬜ |
| 12 | Réécrire les tests | `tests/services/integrations/test_telegram_service.py` | ⬜ |
| 13 | Écrire la documentation | `docs/TELEGRAM_SETUP.md`, `docs/TELEGRAM_COMMANDS.md` | ⬜ |
| 14 | Supprimer les fichiers WhatsApp | `whatsapp.py`, `webhooks_whatsapp.py`, `WHATSAPP_*.md` | ⬜ |
| 15 | Tester le flux complet (digest + validation + commandes) | Tests manuels + E2E | ⬜ |

### 9.6 Concepts API Telegram — Référence

```
1. Créer le bot via @BotFather → obtenir TELEGRAM_BOT_TOKEN
2. Récupérer le TELEGRAM_CHAT_ID (ton ID utilisateur)
3. Envoyer des messages : POST https://api.telegram.org/bot{TOKEN}/sendMessage
4. Boutons interactifs : InlineKeyboardMarkup dans le payload
5. Recevoir les réponses : Webhook POST vers /api/v1/telegram/webhook
6. Recevoir les clics boutons : callback_query dans le webhook
```

**Bibliothèque recommandée** : `python-telegram-bot` (async) ou appels HTTP directs via `httpx` (plus léger, cohérent avec le reste du code).

---

## 10. Flux utilisateur avec validation v2

> Détail complet du modèle brouillon/validation. Les tâches d'implémentation sont dans la [Phase 5 section 7.5](#75-flux-validation-brouillon-v2).

### 10.1 Pattern UI web de validation

```
┌─────────────────────────────────────────────┐
│  ⚡ Brouillon — En attente de validation    │
│                                             │
│  [Contenu du planning / liste]              │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
│  │✅ Valider│  │✏️ Modifier│  │🔄 Régénérer│ │
│  └─────────┘  └──────────┘  └───────────┘  │
└─────────────────────────────────────────────┘
```

- **Bandeau jaune** : brouillon en attente
- **Bandeau vert** : validé
- **Valider** : bouton principal, action en 1 clic
- **Modifier** : édition inline (pas de navigation)
- **Régénérer** : re-demander à l'IA une nouvelle proposition

### 10.2 Pattern Telegram de validation

```
Bot envoie :
  "🍽️ Planning semaine prêt !

   🟡 Lundi midi : Poulet rôti, légumes grillés
   🟡 Lundi soir : Salade César
   🟡 Mardi midi : Pâtes carbonara
   🟡 Mardi soir : Soupe de légumes
   ...

   [✅ Valider]  [✏️ Modifier]  [🔄 Régénérer]"

→ Tap "✏️ Modifier"
→ Bot : "Quel repas veux-tu changer ?"
→ User : "Mardi soir → poisson grillé"
→ Bot met à jour, renvoie le planning modifié avec les mêmes boutons
→ Tap "✅ Valider"

Bot envoie :
  "🛒 Liste de courses (12 articles)
   • Poulet 1.5kg
   • Salade, parmesan, croûtons
   • Spaghetti, œufs, guanciale
   • Poisson blanc 400g
   ...

   [✅ Confirmer]  [✏️ Ajouter]  [❌ Refaire]"
```

Les `callback_query` Telegram sont routés vers les mêmes endpoints API que les boutons web.

---

## 11. Contraintes Railway Free ($0/mois)

### 11.1 Limites Railway Free

| Critère | Railway Free | Usage actuel |
|---------|-------------|---------------|
| Projets | 1 | 1 |
| Services par projet | 3 | 1 (FastAPI) |
| CPU par service | 1 vCPU | ~0.2 vCPU |
| RAM par service | **0.5 GB** | ~300 MB |
| Volume storage | 0.5 GB | Non utilisé (DB sur Supabase) |
| **CRON jobs natifs** | **NON** | **85 jobs via APScheduler interne** (pas impacté) |
| Custom domains | **0** | URL `*.railway.app` (OK pour usage perso) |
| Build timeout | 10 min | OK |
| Replicas | 1 | 1 |

> **Point clé** : Les CRON jobs Railway natifs ne sont pas disponibles en Free. Mais les 85 jobs de l'app utilisent **APScheduler en interne** dans le process Python — ils tournent tant que le process FastAPI est actif.

### 11.2 Risques et mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Service mis en sommeil si inactif | APScheduler s'arrête, plus de CRON | Healthcheck ping `/health` toutes les 5 min (déjà en place) |
| 0.5 GB RAM max | FastAPI + APScheduler + cache L1 + 138 services | Optimisations mémoire Phase 6 (section 8.2) |
| Pas de custom domain | URL = `*.railway.app` | Acceptable pour app familiale privée |
| Build timeout 10 min | Builds longs échouent | Image Docker optimisée, multi-stage build |

### 11.3 Budget mensuel total

| Service | Coût |
|---------|------|
| Railway | **$0** (Free) |
| Telegram Bot API | **$0** (gratuit illimité) |
| Mistral AI | **$0** (free tier, <1% utilisé) |
| Supabase | **$0** (free tier) |
| Vercel | **$0** (free tier) |
| **Total** | **$0/mois** |

---

## 12. Annexes — Détails techniques de référence

### A. Panneau admin flottant

`panneau-admin-flottant.tsx` — panneau visible uniquement en dev/admin pour accès rapide. Non visible utilisateur final.

### B. Fichiers documentation à nettoyer

| Action | Fichiers |
|--------|----------|
| Supprimer | `SPRINT13_COMPLETION_SUMMARY.md`, `SPRINT13_INTEGRATION_GUIDE.md`, `SPRINT13_QUICKSTART.md` |
| Nettoyer | `API_REFERENCE.md`, `API_SCHEMAS.md` (retirer garanties, contrats, RGPD) |
| Mettre à jour | `MODULES.md`, `CRON_JOBS.md`, `guides/maison/`, `INDEX.md` |
| Convertir | `CHANGELOG_MODULES.md` → CHANGELOG fonctionnel |
| Retirer | Mentions RGPD dans `user-guide/FAQ.md` |

### C. Documentation plan — 44 fichiers actuels

| Catégorie | Nombre | État |
|-----------|--------|------|
| Architecture & technique | 12 | ✅ À jour (sauf refs modules supprimés) |
| Guides développeur | 8 | ✅ À jour |
| Guides utilisateur | 6 | ⚠️ Refs RGPD à nettoyer |
| Références API | 4 | ⚠️ Refs modules supprimés |
| Historique sprints | 4 | ❌ À supprimer |
| Docs modules | 10 | ⚠️ Certains à nettoyer |

### D. Sources de configuration

| Priorité | Source |
|----------|--------|
| 1 (haute) | Variables d'environnement système |
| 2 | Fichier `.env.local` (racine projet) |
| 3 | Fichier `.env` (fallback) |
| 4 (basse) | Valeurs par défaut dans `src/core/constants.py` |

### E. Récapitulatif des compteurs

| Élément | Total existant | À supprimer/modifier | Restant après Phase 1 |
|---------|---------------|---------------------|----------------------|
| Routes API | 42 fichiers | ~5 (RGPD, garanties, sprint-nommés) | ~42 (remplacement 1:1 + splits) |
| Schémas Pydantic | 24 | ~3 | ~24 |
| Tests Python | 4932 | ~200 (sprint/modules supprimés) | ~4800+ |
| Commentaires legacy | 150+ | 150+ | 0 |
| Code legacy (shims) | 50+ | 50+ | 0 |
| Fichiers sprint-nommés | 15 | 15 | 0 |
| Fichiers fourre-tout | 3 | 3 (éclatés) | 0 |
| Docs sprint | 4 | 4 | 0 |
| Exports RGPD test | 152 | 152 | 0 |
| Tables SQL à supprimer | ~6 | ~6 | 0 |

---

> **Ce planning est le document de référence pour l'implémentation. Chaque phase doit être validée avant exécution. Rien ne doit être implémenté sans accord explicite.**
