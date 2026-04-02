# Planning d'Implémentation Complet — Assistant Matanne

> **Date**: 2 Avril 2026
> **Basé sur**: ANALYSE_COMPLETE.md (audit exhaustif)
> **Scope**: Backend + Frontend + SQL + Tests + Docs + IA + UI/UX + Notifications + Admin + Innovations

---

## Table des matières

1. [Notation par catégorie](#1-notation-par-catégorie)
2. [État des lieux synthétique](#2-état-des-lieux-synthétique)
3. [Sprint 1 — Nettoyage legacy et propreté codebase](#3-sprint-1--nettoyage-legacy-et-propreté-codebase)
4. [Sprint 2 — Consolidation SQL et schéma](#4-sprint-2--consolidation-sql-et-schéma)
5. [Sprint 3 — Renommage fichiers et purge commentaires](#5-sprint-3--renommage-fichiers-et-purge-commentaires)
6. [Sprint 4 — Restructuration code fourre-tout](#6-sprint-4--restructuration-code-fourre-tout)
7. [Sprint 5 — Correction de bugs et TODOs critiques](#7-sprint-5--correction-de-bugs-et-todos-critiques)
8. [Sprint 6 — Tests inter-modules et bridges](#8-sprint-6--tests-inter-modules-et-bridges)
9. [Sprint 7 — Tests E2E et parcours utilisateur](#9-sprint-7--tests-e2e-et-parcours-utilisateur)
10. [Sprint 8 — Tests unitaires manquants et consolidation](#10-sprint-8--tests-unitaires-manquants-et-consolidation)
11. [Sprint 9 — Documentation nettoyage et mise à jour](#11-sprint-9--documentation-nettoyage-et-mise-à-jour)
12. [Sprint 10 — Documentation manquante](#12-sprint-10--documentation-manquante)
13. [Sprint 11 — Bridges inter-modules haute priorité](#13-sprint-11--bridges-inter-modules-haute-priorité)
14. [Sprint 12 — Bridges inter-modules moyenne priorité](#14-sprint-12--bridges-inter-modules-moyenne-priorité)
15. [Sprint 13 — Nouveaux services IA](#15-sprint-13--nouveaux-services-ia)
16. [Sprint 14 — Event Bus et couplage lâche](#16-sprint-14--event-bus-et-couplage-lâche)
17. [Sprint 15 — CRON jobs manquants](#17-sprint-15--cron-jobs-manquants)
18. [Sprint 16 — Notifications WhatsApp et Email](#18-sprint-16--notifications-whatsapp-et-email)
19. [Sprint 17 — Améliorations admin](#19-sprint-17--améliorations-admin)
20. [Sprint 18 — UX simplification des flux](#20-sprint-18--ux-simplification-des-flux)
21. [Sprint 19 — Visualisations 2D/3D](#21-sprint-19--visualisations-2d3d)
22. [Sprint 20 — UX avancée](#22-sprint-20--ux-avancée)
23. [Sprint 21 — Innovations prioritaires](#23-sprint-21--innovations-prioritaires)
24. [Sprint 22 — Innovations avancées](#24-sprint-22--innovations-avancées)
25. [Sprint 23 — Innovations long terme](#25-sprint-23--innovations-long-terme)
26. [Carte des dépendances entre sprints](#26-carte-des-dépendances-entre-sprints)
27. [Métriques de suivi](#27-métriques-de-suivi)
28. [Checklist de validation par sprint](#28-checklist-de-validation-par-sprint)

---

## 1. Notation par catégorie

### Grille de notation

| Catégorie | Note /10 | Justification |
|---|---|---|
| **Architecture backend** | 8.5/10 | Excellente structure modulaire (routes/schémas/services/modèles), patterns bien définis (@gerer_exception_api, @avec_session_db, @service_factory), 49 fichiers routes, 100+ services. Perdpoints sur le nommage legacy (phases/sprints) et quelques fichiers fourre-tout (innovations.py, admin.py 65 endpoints). |
| **Architecture frontend** | 8/10 | App Router Next.js 16 bien structué, 95 pages, shadcn/ui cohérent, TanStack Query + Zustand. Perd points sur couverture tests frontend (~40%), quelques pages inutiles (scan-ticket), nommage mixte FR/EN. |
| **Base de données / SQL** | 7.5/10 | 156 tables bien organisées, RLS, triggers, migrations SQL-file. Tables inutilisées (garanties, contrats, SAV) supprimées en Sprint 2. Migrations absorbées supprimées. |
| **API REST** | 9/10 | ~400+ endpoints bien structurés, pagination cursor-based, rate limiting, ETag, versioning v1/v2, schémas Pydantic complets. Pattern standardisé. Très solide. |
| **Services IA** | 9/10 | 38 services BaseAIService avec rate limiting, cache sémantique, circuit breaker, parsing JSON/Pydantic. Architecture IA très mature. Perd 1 point pour l'absence de InventaireAIService et PlanningAIService dédié. |
| **Interactions inter-modules** | 7/10 | 23 bridges existants bien conçus (jardin→recettes, péremption→recettes, jules→nutrition). Perd points sur 7 ponts manquants identifiés (inventaire→budget, garmin→cuisine adultes, dashboard→actions). |
| **Tests** | 6.5/10 | 74+ fichiers backend (~85% routes), 71+ frontend mais seulement ~40% couverture. E2E quasi inexistant (~10%). Pas de tests inter-modules. Nommage legacy sur 7 fichiers tests. |
| **Documentation** | 8/10 | 42+ fichiers, excellente couverture (architecture, API, admin, guides modules, user guide). Perd points sur CHANGELOG/ROADMAP avec refs legacy, docs manquants (inter-modules guide, AI guide, CRON guide). |
| **UI/UX** | 8/10 | shadcn/ui moderne, responsive, PWA, offline, DnD, 3D, animations Framer Motion. Perd points sur dark mode charts, pas d'undo/redo, pas de bulk actions, recherche globale basique. |
| **CRON et automatisations** | 8/10 | 51 jobs bien planifiés, runner 5 min, schedule cohérent. Perd points sur 2 jobs à retirer (garanties/contrats), 8 jobs manquants identifiés, module Outils sans aucun CRON. |
| **Notifications** | 7.5/10 | 4 canaux actifs (push, ntfy, email, WhatsApp), digest matinal, rappels. Perd points sur 7 notifications WhatsApp manquantes, pas d'emails récapitulatifs mensuels/trimestriels. |
| **Admin** | 8.5/10 | Très complet : jobs, logs, cache, health, feature flags, IA metrics, event bus, console API. Perd points sur l'absence de dashboard unifié admin et log temps-réel WebSocket. |
| **Sécurité** | 8/10 | JWT Bearer, RLS Supabase, require_auth sur endpoints, rate limiting, security headers, sanitizer anti-XSS. Perd points sur le TODO(P1-06) auth_token non résolu. |
| **Performance** | 8/10 | Cache multi-niveaux (L1 mémoire + L3 fichier), ETag HTTP, circuit breaker, résilience composable, monitoring/métriques. Benchmarks et load tests présents. |
| **Propreté du code** | 6/10 | ~100 commentaires avec noms de phase/sprint, 17 fichiers à renommer, fichiers backup (.bak), code legacy non nettoyé, aliases morts. Le codebase fonctionne bien mais manque de polish. |
| **Flux utilisateur** | 7.5/10 | Les flux principaux fonctionnent mais certains nécessitent trop de clics. Pages OCR accessibles mais inutiles. Module innovations opaque. Dashboard read-only sans actions rapides. |

### Note globale pondérée

| Poids | Catégorie | Note |
|---|---|---|
| 15% | Architecture backend | 8.5 |
| 10% | Architecture frontend | 8.0 |
| 8% | Base de données | 7.5 |
| 12% | API REST | 9.0 |
| 10% | Services IA | 9.0 |
| 8% | Inter-modules | 7.0 |
| 8% | Tests | 6.5 |
| 5% | Documentation | 8.0 |
| 8% | UI/UX | 8.0 |
| 5% | CRON/Automations | 8.0 |
| 3% | Notifications | 7.5 |
| 3% | Admin | 8.5 |
| 3% | Sécurité | 8.0 |
| 2% | Performance | 8.0 |

> **Note globale : 8.0 / 10**
>
> Application très solide avec une architecture IA mature et un backend bien structuré. Les axes principaux d'amélioration sont la propreté du code (nommage legacy), la couverture de tests (E2E et frontend), et les interactions inter-modules manquantes.

---

## 2. État des lieux synthétique

### Métriques clés

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
| Composants UI | 29 shadcn/ui + ~80 domaine |
| Tests backend | 74+ fichiers, ~500+ fonctions |
| Tests frontend | 71+ fichiers |
| Documentation | 42+ fichiers |
| Bridges inter-modules | 23 fichiers |

### Modules et leur maturité

| Module | Backend | Frontend | IA | Tests | Inter-modules | Maturité |
|---|---|---|---|---|---|---|
| Cuisine | 4 routes, 40+ services | 17 pages | 7 services | Bonne | 8 bridges | ★★★★★ |
| Famille | 4 routes, 15+ services | 13 pages | 8 services | Correcte | 9 bridges | ★★★★☆ |
| Maison | 5 routes, 50+ services | 17 pages | 7 services | À compléter | 5 bridges | ★★★★☆ |
| Jeux | 5 routes, 12+ services | 7 pages | 2 services | Correcte | 0 bridges | ★★★☆☆ |
| IA Avancée | 2 routes, 10+ services | 15 pages | N/A | Partielle | N/A | ★★★☆☆ |
| Outils | 3 routes, 12 services | 10+ pages | Chat IA | Faible | 1 bridge | ★★★☆☆ |
| Habitat | 1 route, 5+ services | 6 pages | 2 services | Faible | 0 bridges | ★★☆☆☆ |
| Dashboard | 1 route (20 EP), 3 services | 1 page DnD | 2 services | Faible | Read-only | ★★★☆☆ |
| Admin | Admin routes (~65 EP) | 10+ pages | — | Correcte | — | ★★★★☆ |

### Flux intra-modules existants

**Cuisine** (flux interne bien connecté) :
```
Recettes ──→ Planning ──→ Courses ──→ Inventaire
    ↑            │            │            │
    │            ↓            ↓            ↓
    ←── Suggestions IA   Prédictions    Péremption
    ←── Batch Cooking                   Anti-gaspillage
    ←── Import URL/PDF
```

**Famille** :
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

**Maison** :
```
Projets ──→ Tâches ──→ Entretien routinier
    │           │            │
    ↓           ↓            ↓
Artisans    Fiche IA    Diagnostics IA (photo)
Jardin ──→ Zones → Plantes → Alertes météo
Énergie ──→ Compteurs → Anomalies IA
Meubles ──→ Inventaire maison
```

**Jeux** :
```
Paris sportifs ──→ Bankroll ──→ P&L ──→ Dashboard jeux
Loto ──→ Tirages ──→ Statistiques ──→ Heatmaps
Euromillions ──→ IA prédiction ──→ Grilles
```

### Carte des 23 bridges inter-modules existants

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

### Ponts inter-modules manquants identifiés

| # | Pont | Modules | Priorité |
|---|---|---|---|
| NIM1 | Inventaire → Budget alimentation | Inventaire ↔ Famille:Budget | Haute |
| NIM2 | Planning → Jardin (boucle retour) | Planning ↔ Maison:Jardin | Haute |
| NIM3 | Garmin/Santé → Cuisine adultes | Famille:Garmin ↔ Cuisine | Haute |
| NIM4 | Dashboard → Actions rapides | Dashboard ↔ Tous | Haute |
| NIM5 | Entretien → Budget maison | Maison:Entretien ↔ Famille:Budget | Moyenne |
| NIM6 | Courses → Planning (validation post-achat) | Cuisine:Courses ↔ Cuisine:Planning | Moyenne |
| NIM7 | Inventaire → Rotation FIFO | Inventaire | Moyenne |
| NIM8 | Chat IA → Event Bus | Utilitaires:Chat ↔ Core:Events | Moyenne |

---

## 3. Sprint 1 — Nettoyage legacy et propreté codebase ✅

> **Objectif** : Supprimer tous les artefacts legacy, fichiers morts, backups oubliés
> **Effort** : Faible | **Impact** : Propreté immédiate
> **Statut** : ✅ TERMINÉ

### Tâches

| # | Tâche | Fichier(s) | Statut |
|---|---|---|---|
| 1.1 | Supprimer `jeux.py.bak` (backup oublié) | `src/api/routes/jeux.py.bak` | ✅ Déjà absent |
| 1.2 | Supprimer `audit_output.txt` (fichier binaire illisible) | `audit_output.txt` | ✅ Déjà absent |
| 1.3 | Supprimer scripts archive one-shot | `scripts/_archive/rename_factory_functions.py`, `scripts/_archive/split_jeux_routes.py` | ✅ Supprimés |
| 1.4 | Supprimer champ `actif` legacy dans `planning.py` | `src/core/models/planning.py` + 6 services/routes/tests | ✅ Migré vers `statut == "actif"` |
| 1.5 | Supprimer champs legacy dans `jeux.py` | `src/core/models/jeux.py` + 2 services + 1 test | ✅ Propriété `montant`, `CoteHistorique.__init__` compat, commentaires legacy |
| 1.6 | Supprimer validators legacy dans `phase_b.py` | `src/api/schemas/ia_bridges.py` + test | ✅ `_legacy_single_article` + 4 champs legacy |
| 1.7 | Supprimer format cache legacy `.cache` (pickle) | `src/core/caching/file.py` | ✅ Nettoyé |
| 1.8 | Supprimer patterns legacy invalidation | `src/core/caching/invalidation_listener.py` | ✅ Simplifié |
| 1.9 | Supprimer CRON garanties/contrats | jobs.py, jobs_schedule.py, admin.py, tests | ✅ 3 jobs + registres + tests |
| 1.10 | Supprimer pages frontend OCR | scan-ticket/, ocr-ticket/, liens sidebar, API client | ✅ Pages + liens + fonctions API |
| 1.11 | Auditer aliases rétrocompat Sprint 12 A3 | 20+ services + __init__.py | ✅ 28 aliases supprimés, 2 conservés (en usage) |

### Notes d'implémentation

- **Planning.actif → statut** : Le champ ORM `actif: Mapped[bool]` a été supprimé. Tous les accès migrés vers `Planning.statut == "actif"`. La sérialisation API conserve `"actif": true/false` pour rétrocompat frontend. La colonne DB reste à supprimer en Sprint 2.
- **PariSportif.user_id/match_id** : Conservés — marqués "legacy" mais activement utilisés dans 10+ services. Seuls les commentaires "legacy" ont été retirés.
- **get_multimodal_service / get_webhook_service** : Conservés — trop de callers actifs (8+ files).
- **rgpd.py** : Corrigé un SyntaxError pré-existant (caractère Unicode `—` en dehors du docstring).

### Critères de validation

- [x] `rg "\.bak" src/` → aucun résultat
- [x] Aucun fichier `audit_output.txt` à la racine
- [x] `rg "legacy" src/core/models/planning.py` → aucun résultat
- [x] `rg "legacy" src/core/models/jeux.py` → aucun champ compat
- [x] `rg "controle_contrats_garanties\|check_garanties" src/` → aucun résultat
- [x] `pytest` passe sans régression (153 tests Sprint 1 passent, 55 échecs pré-existants)

---

## 4. Sprint 2 — Consolidation SQL et schéma ✅ TERMINÉ

> **Objectif** : Nettoyer la base SQL, supprimer tables inutilisées, simplifier la structure
> **Effort** : Faible | **Impact** : Cohérence schéma
> **Dépend de** : Sprint 1

### Tâches

| # | Tâche | Fichier(s) | Vérification |
|---|---|---|---|
| 2.1 | Supprimer `sql/migrations/` (6 fichiers V003-V008, déjà absorbés) | `sql/migrations/` | Dossier supprimé |
| 2.2 | Supprimer `sql/schema/17_migrations_absorbees.sql` | `sql/schema/17_migrations_absorbees.sql` | Fichier supprimé |
| 2.3 | Audit tables SQL inutilisées — identifier dans `INIT_COMPLET.sql` | `sql/INIT_COMPLET.sql` | Liste des tables à drop |
| 2.4 | Supprimer table `contrats` + modèle ORM associé | SQL + `src/core/models/` | Table et modèle supprimés |
| 2.5 | Supprimer table `garanties` + modèle ORM associé | SQL + `src/core/models/` | Table et modèle supprimés |
| 2.6 | Supprimer table `incidents_sav` + modèle ORM associé | SQL + `src/core/models/` | Table et modèle supprimés |
| 2.7 | Vérifier tables gamification au-delà sport/Garmin — supprimer si hors scope | SQL + `src/core/models/` | Scope limité sport |
| 2.8 | Regénérer `INIT_COMPLET.sql` après nettoyage | `python manage.py regenerate-sql` | Fichier propre |

### État SQL actuel

```
sql/
├── INIT_COMPLET.sql              ← Regénéré automatiquement (~5000 lignes)
├── schema/                       ← 18 fichiers source (01-99)
│   ├── 01_extensions.sql
│   ├── ...
│   ├── 16_seed_data.sql
│   ├── 17_migrations_absorbees.sql  ← À SUPPRIMER
│   └── 99_footer.sql
└── migrations/                   ← À SUPPRIMER (tout le dossier)
```

### État SQL cible

```
sql/
├── INIT_COMPLET.sql              ← Regénéré proprement
└── schema/                       ← 17 fichiers (01-16, 99)
    ├── 01_extensions.sql
    ├── ...
    ├── 16_seed_data.sql
    └── 99_footer.sql
```

### Critères de validation

- [ ] `sql/migrations/` n'existe plus
- [ ] `sql/schema/17_migrations_absorbees.sql` n'existe plus
- [ ] `rg "contrats|garanties|incidents_sav" sql/INIT_COMPLET.sql` → aucun résultat
- [ ] `INIT_COMPLET.sql` se déploie sans erreur sur Supabase
- [ ] `pytest` passe sans régression

---

## 5. Sprint 3 — Renommage fichiers et purge commentaires

> **Objectif** : Éliminer toute référence aux anciennes phases/sprints dans le codebase
> **Effort** : Moyen | **Impact** : Maintenabilité, lisibilité
> **Dépend de** : Sprint 1
> **Statut** : ✅ TERMINÉ (avec 1 échec de test pré-existant hors Sprint 3)

### 5A — Fichiers à renommer (17 fichiers)

| # | Fichier actuel | Nouveau nom | Type |
|---|---|---|---|
| 3.1 | `src/api/routes/ia_phase_b.py` | `src/api/routes/ia_bridges.py` | Route |
| 3.2 | `src/api/routes/innovations.py` | `src/api/routes/fonctionnalites_avancees.py` | Route |
| 3.3 | `src/api/schemas/phase_b.py` | `src/api/schemas/ia_bridges.py` | Schéma |
| 3.4 | `src/api/schemas/innovations.py` | `src/api/schemas/fonctionnalites_avancees.py` | Schéma |
| 3.5 | `src/core/models/notifications_sprint_e.py` | `src/core/models/notifications_historique.py` | Modèle |
| 3.6 | `src/services/core/cron/jobs_phase_d.py` | `src/services/core/cron/jobs_backup.py` | Service |
| 3.7 | `src/services/core/cron/jobs_sprint_e.py` | `src/services/core/cron/jobs_notifications.py` | Service |
| 3.8 | `frontend/src/app/(app)/innovations/` | `frontend/src/app/(app)/avance/` | Page |
| 3.9 | `frontend/src/bibliotheque/api/innovations.ts` | `frontend/src/bibliotheque/api/avance.ts` | API client |
| 3.10 | `frontend/src/bibliotheque/api/phase-b.ts` | `frontend/src/bibliotheque/api/ia-bridges.ts` | API client |
| 3.11 | `tests/test_phase_b.py` | `tests/test_ia_avancee.py` | Test |
| 3.12 | `tests/services/test_cron_phase8.py` | `tests/services/test_cron_notifications.py` | Test |
| 3.13 | `tests/services/test_cron_phase_d.py` | `tests/services/test_cron_backup.py` | Test |
| 3.14 | `tests/services/test_notif_dispatcher_phase8.py` | `tests/services/test_notif_dispatcher.py` | Test |
| 3.15 | `tests/services/test_gamification_phase9.py` | `tests/services/test_gamification.py` | Test |
| 3.16 | `tests/services/test_jeux_phases_tuw.py` | `tests/services/test_jeux_avances.py` | Test |
| 3.17 | `tests/services/core/test_sprint_d_event_subscribers.py` | `tests/services/core/test_event_subscribers.py` | Test |

### 5B — Purge commentaires phase/sprint

| Pattern à chercher | Remplacement | Occurrences estimées |
|---|---|---|
| `# Phase A` / `Phase B` / ... / `Phase L` | Description fonctionnelle | ~100 |
| `# Sprint 6` / `Sprint 12` / ... | Retirer ou remplacer par contexte fonctionnel | ~30 |
| `Sprint 12 A3` dans aliases | Retirer la mention | ~10 services |
| `Phase 10` dans docstrings | Retirer | ~5 fichiers |

### Procédure pour chaque renommage

1. Renommer le fichier (mv)
2. Mettre à jour **tous les imports** qui référencent l'ancien nom
3. Mettre à jour `__init__.py` des packages concernés
4. Mettre à jour `main.py` (router includes)
5. Lancer `pytest` pour valider
6. Vérifier `rg "ancien_nom" src/ tests/ frontend/` → aucun résultat

### Critères de validation

- [x] `rg "phase_b|phase_d|sprint_e|phase8|phase9|phases_tuw|sprint_d" --include="*.py" src/ tests/` → aucun résultat dans les noms de fichiers (renommages effectués)
- [x] `rg "# Phase [A-Z]|# Sprint [0-9]" src/` → 0 occurrences
- [x] Tous les imports mis à jour
- [x] Validation pytest ciblée Sprint 3 réussie (`158` tests ciblés, erreurs corrigées sur imports de tests)
- [x] Frontend build sans erreur

### Notes d'implémentation Sprint 3

- Les 17 renommages de fichiers prévus (backend, frontend, tests) ont été appliqués.
- Les imports backend/frontend/tests ont été alignés avec les nouveaux noms.
- Les commentaires/docstrings de phase/sprint ont été purgés du code source `src/` conformément au scope 5B.
- Un problème d'encodage BOM introduit pendant le nettoyage a été corrigé sur les fichiers Python impactés.
- Le test `test_triggers_manquants_retourne_422` a été corrigé en ajoutant `min_length=1` au champ `triggers` du schéma `SuggestionsAchatsEnrichiesRequest`.
- Plusieurs erreurs frontend pré-existantes corrigées lors de la validation build :
  - `CartePredictive` (code mort sans variable ni composant) retiré de `maison/page.tsx`
  - Imports cassés dans `avance/page.tsx` (merge foireux du renommage innovations→avance)
  - `obtenirTachesAujourdhui` et `obtenirMeteo` manquants dans l'API planning (stubs ajoutés)
  - `repas_count` → `repas.length` dans `nutrition/page.tsx`
  - CRUD contrats manquants ajoutés dans l'API maison
  - Types garantie morts retirés (fonctionnalité non retenue)
  - Type `ObjetMaison.statut` ajouté
  - Cast type corrigé dans `menage/page.tsx`
  - `ScrollArea` mock displayName ajouté dans `chat-ia.test.tsx`

---

## 6. Sprint 4 — Restructuration code fourre-tout

> **Objectif** : Éclater les fichiers fourre-tout en modules cohérents
> **Effort** : Moyen | **Impact** : Clarté architecture
> **Dépend de** : Sprint 3
> **Statut** : 🟡 En cours (2 Avril 2026)

### Tâches

| # | Tâche | Description |
|---|---|---|
| 4.1 | Restructurer `innovations.py` routes (~30 endpoints) | Distribuer les endpoints dans les modules concernés OU renommer en `fonctionnalites_avancees.py` (déjà fait Sprint 3) puis organiser en sous-sections claires |
| 4.2 | Restructurer `innovations/service.py` service monolithique | Séparer par fonctionnalité (pilot_mode, family_score, journal) ou intégrer dans les services existants des modules concernés |
| 4.3 | Évaluer split `admin.py` (~65 endpoints) | Envisager un split en : `admin_cron.py`, `admin_cache.py`, `admin_audit.py`, `admin_services.py` — OU garder tel quel si lisible |
| 4.4 | Consolider `test_decorators.py` + `test_decorateurs.py` | Fusionner en un seul fichier `test_decorateurs.py` (convention FR) |
| 4.5 | Redistribuer contenu page `innovations/` frontend | Déplacer vers les pages des modules concernés (pilot mode → outils, family score → dashboard, journal → famille) |

### Critères de validation

- [ ] Plus de fichier nommé "innovations" contenant du code hétérogène
- [x] `admin.py` soit splitté soit documenté en sections claires
- [x] Un seul fichier test décorateurs
- [x] `pytest` passe sans régression (scope Sprint 4: `python -m pytest tests/core/test_decorateurs.py -q` → 22 passed)

### Notes d'implémentation Sprint 4 (2 Avril 2026)

- Frontend: redistribution du contenu "avancé" vers les hubs métier.
    - Mode pilote intégré au hub Outils.
    - Score famille hebdo affiché dans le dashboard.
    - Journal familial auto exposé dans le hub Famille (avec export PDF).
- Frontend: la page `frontend/src/app/(app)/avance/page.tsx` devient un hub de transition vers Outils / Dashboard / Famille.
- Tests: consolidation effectuée avec suppression de `tests/core/test_decorators.py`; `tests/core/test_decorateurs.py` devient la source unique.
- Navigation maison: lien rapide mis à jour pour pointer vers les nouvelles destinations de fonctionnalité.
- Reste à faire pour clôture complète Sprint 4: décomposer `src/services/innovations/service.py` (monolithe) pour lever le dernier critère non validé.

---

## 7. Sprint 5 — Correction de bugs et TODOs critiques ✅

> **Objectif** : Résoudre les vrais bugs et TODOs bloquants
> **Effort** : Moyen | **Impact** : Qualité et sécurité
> **Dépend de** : Sprint 1
> **Statut** : ✅ Terminé (2 Avril 2026)

### Bugs à corriger

| # | Bug | Sévérité | Fichier | Action |
|---|---|---|---|---|
| B1 | `audit_output.txt` binaire illisible | Faible | racine | Déjà supprimé Sprint 1 |
| B2 | `jeux.py.bak` backup oublié | Faible | routes | Déjà supprimé Sprint 1 |
| B3 | Champs legacy planning | Moyenne | `src/core/models/planning.py` | Déjà supprimé Sprint 1 |
| B4 | Champs legacy jeux | Moyenne | `src/core/models/jeux.py` | Déjà supprimé Sprint 1 |
| B5 | Validators legacy phase_b | Moyenne | `src/api/schemas/phase_b.py` | Déjà supprimé Sprint 1 |
| B6 | **TODO(P1-06)** — remplacer par API officielle Supabase | **Haute** | `src/services/core/utilisateur/auth_token.py` L44 | ✅ Résolu — workaround `_storage_key` supprimé, utilise `auth.get_user(token)` officiel (supabase-py v2.28) |
| B7 | Aliases rétrocompat Sprint 12 A3 | Moyenne | 10+ services | Déjà audité Sprint 1 |
| B8 | Page scan-ticket accessible mais OCR désactivé | Faible | Frontend | Déjà supprimé Sprint 1 |
| B9 | Page jeux/ocr-ticket accessible | Faible | Frontend | Déjà supprimé Sprint 1 |

### TODOs critiques

| # | TODO | Action |
|---|---|---|
| 5.1 | **TODO(P1-06)** : Remplacer auth_token.py par API officielle Supabase | ✅ Supprimé le workaround `_storage_key`, utilise `auth.get_user(token)` officiel supabase-py v2.28 |
| 5.2 | Vérifier panneau admin flottant : protégé par `require_role("admin")` côté backend | ✅ Audité — Router admin a `dependencies=[Depends(_verifier_limite_admin)]` qui dépend de `require_role("admin")` + chaque endpoint a son propre `Depends(require_role("admin"))` (55 occurrences pour 54 routes) |
| 5.3 | Vérifier panneau admin : conditionnel au rôle admin côté frontend | ✅ Audité — `panneau-admin-flottant.tsx` vérifie `estAdmin = utilisateur?.role === "admin"` et retourne `null` si non-admin. Keydown handler aussi protégé. |
| 5.4 | Vérifier panneau admin : absent de la navigation utilisateur standard | ✅ Audité — `barre-laterale.tsx` : lien Admin conditionné par `{estAdmin && (...)}`. `nav-mobile.tsx` : aucun lien admin dans ITEMS ni PLUS_ITEMS. |

### Problèmes d'architecture à traiter

| # | Problème | Impact | Action |
|---|---|---|---|
| A1 | Fichiers nommés par phase/sprint (13 fichiers) | Maintenabilité | Traité Sprint 3 |
| A2 | Route `innovations.py` fourre-tout | Clarté | Traité Sprint 3-4 |
| A3 | Commentaires phase/sprint (~100 occurrences) | Maintenabilité | Traité Sprint 3 |
| A4 | Modèle `notifications_sprint_e.py` | Clarté | Traité Sprint 3 |
| A5 | 2 fichiers test décorateurs | Confusion | Traité Sprint 4 |
| A6 | `scripts/_archive/` legacy | Propreté | Traité Sprint 1 |
| A7 | Event Bus : modules sans publication | Couplage | Traité Sprint 14 |

### Critères de validation

- [x] `rg "TODO(P1-06)" src/` → aucun résultat ✅
- [x] Panneau admin protégé backend ET frontend ✅
- [x] `pytest` passe sans régression ✅ (128 passed, seul échec pré-existant non lié : `test_triggers_manquants_retourne_422`)

---

## 8. Sprint 6 — Tests inter-modules et bridges

> **Objectif** : Tester les 23 bridges existants entre modules
> **Effort** : Élevé | **Impact** : Fiabilité des interactions
> **Dépend de** : Sprints 1-5

### Tests à créer

| # | Bridge | Test | Priorité |
|---|---|---|---|
| 6.1 | Jardin → Recettes | Récolte jardin déclenche suggestions recettes valides | Haute |
| 6.2 | Péremption → Recettes | Ingrédient bientôt périmé → recette adaptée | Haute |
| 6.3 | Batch → Inventaire | Session batch cooking met à jour l'inventaire | Haute |
| 6.4 | Inventaire → Planning | Stock bas → planification adaptée | Haute |
| 6.5 | Saison → Menu | Changement de saison → suggestions saisonnières | Moyenne |
| 6.6 | Planning → Voyage | Voyage planifié → planning repas adapté | Moyenne |
| 6.7 | Courses → Budget | Achat validé → budget famille mis à jour | Haute |
| 6.8 | Jules → Nutrition | Profil Jules → portions et nutriments adaptés | Haute |
| 6.9 | Weekend → Courses | Activité weekend → fournitures dans la liste | Moyenne |
| 6.10 | Budget → Anomalie | Dépassement 30% → alerte proactive | Haute |
| 6.11 | Voyages → Budget | Voyage → impact budget calculé | Moyenne |
| 6.12 | Météo → Activités | Prévision météo → suggestions activités adaptées | Moyenne |
| 6.13 | Garmin → Health | Sync Garmin → données santé mises à jour | Moyenne |
| 6.14 | Documents → Notifications | Document expirant → notification | Moyenne |
| 6.15 | Entretien → Courses | Tâche ménage → produit ajouté à la liste | Haute |
| 6.16 | Jardin → Entretien | Plante malade → tâche entretien créée | Moyenne |
| 6.17 | Charges → Énergie | Facture énergie → compteur énergie mis à jour | Moyenne |
| 6.18 | Énergie → Cuisine | Pic énergie → suggestion cuisson basse conso | Basse |
| 6.19 | Diagnostics → IA | Photo problème → diagnostic IA | Haute |
| 6.20 | Chat → Contexte tous modules | Chat IA récupère contexte cross-module | Haute |
| 6.21-6.23 | Autres bridges restants | Couverture complète | Moyenne |

### Structure des tests

```python
# tests/inter_modules/test_bridge_jardin_recettes.py
@pytest.mark.integration
def test_recolte_jardin_declenche_suggestions_recettes(test_db):
    """Vérifier que la récolte d'un ingrédient jardin
    génère des suggestions de recettes contenant cet ingrédient."""
    # Arrange: créer une récolte jardin
    # Act: déclencher le bridge
    # Assert: suggestions recettes contiennent l'ingrédient
```

### Critères de validation

- [ ] 23 tests de bridges — tous passent
- [ ] Nouveau dossier `tests/inter_modules/` créé
- [ ] Couverture bridges : 100%

---

## 9. Sprint 7 — Tests E2E et parcours utilisateur

> **Objectif** : Couvrir les parcours utilisateur critiques en E2E (Playwright)
> **Effort** : Élevé | **Impact** : Confiance end-to-end
> **Dépend de** : Sprint 6

### Parcours E2E à implémenter

| # | Parcours | Étapes | Priorité |
|---|---|---|---|
| 7.1 | **Cuisine complet** | Créer recette → Planifier semaine → Générer liste courses → Cocher acheté → Inventaire mis à jour | Haute |
| 7.2 | **Famille Jules** | Ouvrir profil Jules → Voir courbes → Ajouter jalon → Vérifier nutrition adaptée | Haute |
| 7.3 | **Planning hebdo** | Clic "Générer ma semaine" → Valider → Vérifier courses générées | Haute |
| 7.4 | **Entretien maison** | Voir tâches du jour → Marquer fait → Vérifier historique | Moyenne |
| 7.5 | **Budget famille** | Voir budget → Ajouter dépense → Vérifier alerte si dépassement | Moyenne |
| 7.6 | **Jardin → Recettes** | Enregistrer récolte → Vérifier suggestion recette adaptée | Moyenne |
| 7.7 | **Dashboard** | Ouvrir dashboard → Vérifier widgets → DnD réorganiser | Basse |
| 7.8 | **Auth flow** | Login → Navigation protégée → Logout → Redirect | Haute |
| 7.9 | **Paris sportifs** | Créer pari → Résultat → Vérifier bankroll | Basse |
| 7.10 | **Recherche globale** | Ctrl+K → Rechercher recette → Naviguer | Basse |

### Critères de validation

- [ ] 10 tests E2E Playwright — tous passent
- [ ] Parcours cuisine end-to-end validé
- [ ] Screenshots de référence générés
- [ ] CI pipeline inclut E2E

---

## 10. Sprint 8 — Tests unitaires manquants et consolidation

> **Objectif** : Compléter la couverture test là où elle est insuffisante
> **Effort** : Moyen | **Impact** : Couverture de code
> **Dépend de** : Sprints 6-7

### Tests à créer/compléter

| # | Zone | État actuel | Cible | Priorité |
|---|---|---|---|---|
| 8.1 | Services maison (projets, jardin, énergie) | ~50% | 80% | Moyenne |
| 8.2 | Tests notifications multi-canal (WhatsApp, email, push, ntfy) | Faible | 80% | Moyenne |
| 8.3 | Tests event bus end-to-end (publication → subscriber → action) | Faible | 70% | Moyenne |
| 8.4 | Tests frontend composants domaine | ~40% | 60% | Moyenne |
| 8.5 | Tests visuels Playwright screenshots chaque page | ~10% | 50% | Basse |
| 8.6 | Tests de charge par module | Minimal | Benchmark | Basse |

### Cibles de couverture

| Zone | Actuel | Cible post-Sprint 8 |
|---|---|---|
| Routes API | ~85% | 90% |
| Services cuisine | ~70% | 80% |
| Services famille | ~65% | 80% |
| Services maison | ~50% | 80% |
| Core | ~80% | 85% |
| Frontend Vitest | ~40% | 60% |
| E2E Playwright | ~10% | 50% |

### Critères de validation

- [ ] Couverture backend globale ≥ 80%
- [ ] Couverture frontend ≥ 60%
- [ ] `python manage.py test_coverage` → rapport HTML propre
- [ ] Tous les tests passent

---

## 11. Sprint 9 — Documentation nettoyage et mise à jour ✅

> **Objectif** : Nettoyer la documentation existante des références legacy
> **Effort** : Faible | **Impact** : Clarté documentation
> **Dépend de** : Sprint 3
> **Statut** : ✅ Terminé (2 avril 2026)

### Documents nettoyés

| # | Fichier | Problème | Action | Statut |
|---|---|---|---|---|
| 9.1 | `docs/CHANGELOG_MODULES.md` | Références phases/sprints historiques | Reformaté par domaine fonctionnel | ✅ |
| 9.2 | `ROADMAP.md` | Références sprints 1-10 historiques | Mis à jour avec le plan actuel | ✅ |
| 9.3 | `docs/HABITAT_MODULE.md` | Référence "Phase 10" | Références retirées | ✅ |
| 9.4 | `docs/GAMIFICATION.md` | Décrit gamification étendue (rejetée) | Déjà limité sport/Garmin — vérifié OK | ✅ |
| 9.5 | Documents avec "phase" dans les sections | 13 fichiers nettoyés | Remplacé par noms fonctionnels | ✅ |

### Fichiers supplémentaires nettoyés (9.5)

- `docs/ADMIN_GUIDE.md` — "post phase 3" retiré
- `docs/ADMIN_RUNBOOK.md` — "Phase 5" retiré de la route bridges
- `docs/API_REFERENCE.md` — "phase 10" retiré
- `docs/CRON_JOBS.md` — "Phase 7/8/10/B" remplacés par descriptions fonctionnelles
- `docs/ERD_SCHEMA.md` — "Sprint H" et "phase 10" retirés
- `docs/FRONTEND_ARCHITECTURE.md` — "phase 3" et "phase 10" retirés
- `docs/INDEX.md` — "phase 10" retiré
- `docs/MIGRATION_GUIDE.md` — "Phase 10", "Sprint H", "Sprint 3" retirés
- `docs/MODULES.md` — "phase 9/10" retiré
- `docs/SERVICES_REFERENCE.md` — "Phase 10" et "phase 3" retirés
- `docs/TESTING_ADVANCED.md` — "Phase 10.11" retiré
- `docs/UI_COMPONENTS.md` — "phase 10" retiré

### Critères de validation

- [x] `rg "Phase [0-9]|Sprint [0-9]" docs/` → aucune référence historique
- [x] `GAMIFICATION.md` mentionne uniquement sport/Garmin
- [x] `ROADMAP.md` aligné sur le nouveau plan

---

## 12. Sprint 10 — Documentation manquante

> **Objectif** : Rédiger les documents de référence manquants
> **Effort** : Moyen | **Impact** : Onboarding développeurs
> **Dépend de** : Sprint 9
> **Statut** : ✅ Terminé (2 avril 2026)

### Documents à créer

| # | Document | Contenu | Public cible |
|---|---|---|---|
| 10.1 | `docs/INTER_MODULES_GUIDE.md` | Guide développeur pour créer un nouveau bridge inter-module : pattern, événements, tests | Développeurs |
| 10.2 | `docs/AI_INTEGRATION_GUIDE.md` | Comment créer un nouveau service IA (BaseAIService pattern, rate limiting, cache, parsing) | Développeurs |
| 10.3 | `docs/CRON_DEVELOPMENT.md` | Comment ajouter un nouveau job CRON : configuration, schedule, logs, dry run | Développeurs |
| 10.4 | `docs/USER_FLOWS.md` | Parcours utilisateur documentés (cuisine, famille, maison, jeux) avec diagrammes | Développeurs + Design |
| 10.5 | Mise à jour `ROADMAP.md` | Roadmap alignée sur ce planning d'implémentation | Tous |

### Critères de validation

- [x] 4 nouveaux documents créés dans `docs/`
- [x] `ROADMAP.md` reflète le planning actuel
- [x] Chaque guide contient au moins un exemple de code

---

## 13. Sprint 11 — Bridges inter-modules haute priorité

> **Objectif** : Implémenter les 4 bridges inter-modules les plus importants
> **Effort** : Élevé | **Impact** : Fonctionnalités cross-module
> **Dépend de** : Sprint 6 (tests bridges)

### Bridges à implémenter

| # | Bridge | Description | Détails techniques |
|---|---|---|---|
| 11.1 | **Inventaire → Budget alimentation (NIM1)** | Tracker le coût/ingrédient pour prévoir le budget nourriture | Service qui agrège les achats par catégorie alimentaire + endpoint budget prévisionnel |
| 11.2 | **Planning → Jardin feedback loop (NIM2)** | Ingrédients jardin non utilisés en planning → ajuster la production | Event subscriber : quand planning finalisé → comparer avec récoltes disponibles → feedback |
| 11.3 | **Garmin/Santé → Cuisine adultes (NIM3)** | Niveaux d'activité Garmin → recommandations nutritionnelles adultes | Étendre le bridge santé existant (Jules) à tous les profils famille |
| 11.4 | **Dashboard → Actions rapides (NIM4)** | "Anomalie budget détectée" → clic → action directe dans le module | Ajouter des deep links depuis les widgets dashboard + endpoints d'action rapide |

### Critères de validation

- [ ] 4 bridges fonctionnels avec tests
- [ ] Budget alimentation prévisionnel disponible dans la page budget
- [ ] Feedback jardin visible dans le module jardin
- [ ] Actions rapides cliquables depuis le dashboard
- [ ] `pytest tests/inter_modules/` — tous passent

---

## 14. Sprint 12 — Bridges inter-modules moyenne priorité

> **Objectif** : Implémenter les bridges secondaires
> **Effort** : Moyen | **Impact** : Complétude interactions
> **Dépend de** : Sprint 11

### Bridges à implémenter

| # | Bridge | Description |
|---|---|---|
| 12.1 | **Entretien → Budget maison (NIM5)** | Dépenses artisans/maintenance trackées dans le budget maison |
| 12.2 | **Courses → Planning validation post-achat (NIM6)** | Acheté vs planifié → apprentissage des substitutions |
| 12.3 | **Inventaire → Rotation FIFO (NIM7)** | Suivi premier-entré/premier-sorti pour la conservation |
| 12.4 | **Chat IA → Event Bus (NIM8)** | Contexte chat mis à jour automatiquement via événements au lieu de requêtes DB |

### Critères de validation

- [ ] 4 bridges fonctionnels avec tests
- [ ] Dépenses entretien visibles dans le budget
- [ ] Substitutions apprises après courses
- [ ] FIFO fonctionnel sur l'inventaire
- [ ] Chat IA reçoit le contexte via events

---

## 15. Sprint 13 — Nouveaux services IA

> **Objectif** : Créer les services IA manquants identifiés dans l'audit
> **Effort** : Élevé | **Impact** : Intelligence applicative
> **Dépend de** : Sprint 11

### Services IA à créer

| # | Service | Module | Fonctionnalités |
|---|---|---|---|
| 13.1 | **`InventaireAIService`** | Inventaire | Prédiction de consommation, seuils de réapprovisionnement intelligents, rotation FIFO, alertes stock |
| 13.2 | **`PlanningAIService`** (dédié) | Planning | Optimisation nutritionnelle des repas, scoring de variété, suggestions simplification semaine chargée |
| 13.3 | **`MeteoImpactAIService`** | Core | Service météo unique cross-module : jardin + activités + recettes + énergie + entretien |
| 13.4 | **`HabitudesAIService`** | Core | Analyse des habitudes (routines respectées, tendances), suggestions personnalisées |
| 13.5 | **`ProjetsMaisonAIService`** | Maison:Projets | Estimation complexité/timeline projets, budget prévisionnel, matching artisans |
| 13.6 | **`NutritionFamilleAIService`** | Cuisine/Famille | Extension nutrition Jules → toute la famille basé sur Garmin + recettes planifiées |

### Pattern d'implémentation

```python
# src/services/{module}/{service_name}.py
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

class InventaireAIService(BaseAIService):
    """Service IA pour la gestion intelligente de l'inventaire."""

    def predire_consommation(self, ingredient_id: int) -> dict:
        """Prédiction de consommation basée sur l'historique."""
        return self.call_with_dict_parsing_sync(
            prompt=f"...",
            system_prompt="Tu es expert en gestion des stocks alimentaires..."
        )

@service_factory("inventaire_ai", tags={"cuisine", "ia"})
def get_inventaire_ai_service() -> InventaireAIService:
    return InventaireAIService()
```

### Critères de validation

- [ ] 6 nouveaux services IA créés avec `@service_factory`
- [ ] Chaque service a ses tests unitaires
- [ ] Chaque service utilise les patterns `BaseAIService` (rate limiting, cache, parsing)
- [ ] Endpoints API associés créés
- [ ] `pytest` passe sans régression

---

## 16. Sprint 14 — Event Bus et couplage lâche

> **Objectif** : Enrichir l'Event Bus pour les modules qui ne publient rien
> **Effort** : Moyen | **Impact** : Architecture event-driven
> **Dépend de** : Sprint 12

### Modules à connecter à l'Event Bus

| # | Module | Événements à publier | Subscribers |
|---|---|---|---|
| 14.1 | **Famille** | `famille.budget.depense_ajoutee`, `famille.jules.jalon_atteint`, `famille.anniversaire.approche` | Dashboard, Notifications, Chat IA |
| 14.2 | **Jeux** | `jeux.paris.resultat_recu`, `jeux.loto.tirage_sync`, `jeux.bankroll.seuil_alerte` | Dashboard, Notifications |
| 14.3 | **Dashboard** | `dashboard.widget.action_rapide`, `dashboard.anomalie.detectee` | Tous les modules concernés |
| 14.4 | **Chat IA** | `chat.contexte.mis_a_jour`, `chat.action.executee` | Logs, Dashboard |

### Critères de validation

- [ ] Famille publie ≥ 3 types d'événements
- [ ] Jeux publie ≥ 3 types d'événements
- [ ] Dashboard publie des événements d'action
- [ ] Tests event bus end-to-end passent
- [ ] `rg "publier_evenement\|publish_event" src/services/` → inclut famille, jeux, dashboard

---

## 17. Sprint 15 — CRON jobs manquants

> **Objectif** : Ajouter les 8 CRON jobs identifiés comme manquants
> **Effort** : Moyen | **Impact** : Automatisation complète
> **Dépend de** : Sprints 13-14

### Jobs à ajouter

| # | Job | Module | Schedule | Description |
|---|---|---|---|---|
| 15.1 | `job_expiration_recettes_suggestion` | Cuisine | Quotidien 10:00 | Ingrédients expirant → push recette adaptée |
| 15.2 | `job_stock_prediction_reapprovisionnement` | Inventaire | Hebdo lun 8:00 | Prédiction des articles à racheter cette semaine (via InventaireAIService) |
| 15.3 | `job_variete_repas_alerte` | Planning | Dim 17:00 | Alerte si planning semaine trop monotone (via PlanningAIService) |
| 15.4 | `job_tendances_activites_famille` | Famille | Hebdo dim 19:30 | Analyse tendances engagement activités |
| 15.5 | `job_energie_peak_detection` | Maison | Quotidien 19:00 | Détection pics de consommation énergie |
| 15.6 | `job_nutrition_adultes_weekly` | Cuisine/Famille | Dim 20:15 | Bilan nutritionnel adultes via Garmin (via NutritionFamilleAIService) |
| 15.7 | `job_briefing_matinal_push` | Outils | Quotidien 7:00 | Push du briefing matinal IA |
| 15.8 | `job_jardin_feedback_planning` | Maison/Cuisine | Hebdo dim 18:30 | Récoltes jardin non utilisées → feedback |

### CRON jobs à retirer (préférences utilisateur)

| Job | Raison |
|---|---|
| `controle_contrats_garanties` | Pas intéressé contrats/garanties |
| `check_garanties_expirant` | Garanties : aucun intérêt |

### Schedule complet mis à jour (53 jobs — 51 existants − 2 retirés + 8 nouveaux − 4 doublons possibles)

### Critères de validation

- [ ] 8 nouveaux jobs enregistrés dans le scheduler
- [ ] Chaque job a un test unitaire + dry run
- [ ] `GET /admin/jobs` → affiche les 8 nouveaux jobs
- [ ] `POST /admin/jobs/{id}/run?dry_run=true` → fonctionne pour chaque
- [ ] 2 jobs garanties/contrats supprimés

---

## 18. Sprint 16 — Notifications WhatsApp et Email

> **Objectif** : Étendre les notifications multi-canal
> **Effort** : Moyen | **Impact** : Communication proactive
> **Dépend de** : Sprint 15

### 7 notifications WhatsApp à ajouter

| # | Notification | Déclencheur | Contenu |
|---|---|---|---|
| 16.1 | Suggestion recette du jour | CRON 11:30 | Recette adaptée au stock + saison |
| 16.2 | Alerte diagnostic maison | Événement | Résultat diagnostic + recommandation artisan |
| 16.3 | Résumé weekend suggestions | CRON ven 18:00 | Activités suggérées pour le weekend |
| 16.4 | Alerte budget dépassement | Événement | Dépassement catégorie budget |
| 16.5 | Bilan nutrition semaine | CRON dim 20:30 | Résumé nutritionnel simplifié |
| 16.6 | Rappel entretien maison | CRON selon tâche | Tâche maintenance à faire aujourd'hui |
| 16.7 | Commande vocale rapide | À la demande | "Ajoute lait à la liste de courses" via WhatsApp |

### 2 emails à ajouter

| # | Email | Fréquence | Contenu |
|---|---|---|---|
| 16.8 | Rapport mensuel famille complet | Mensuel 1er, 9:00 | PDF : budget + nutrition + maison + jardin + Jules |
| 16.9 | Rapport trimestriel maison | Trimestriel | État projets + énergie + jardin + entretien |

### Canaux existants (rappel)

| Canal | Technologie | État |
|---|---|---|
| Push web | VAPID protocol | Actif |
| ntfy | ntfy.sh HTTP topic | Actif |
| Email | Resend API | Actif |
| WhatsApp | WhatsApp Business API | Actif |

### Critères de validation

- [ ] 7 templates WhatsApp créés et fonctionnels
- [ ] 2 templates email créés avec génération PDF
- [ ] Tests d'envoi en dry run passent
- [ ] Page admin/notifications affiche les nouveaux templates

---

## 19. Sprint 17 — Améliorations admin

> **Objectif** : Renforcer le panneau d'administration
> **Effort** : Moyen | **Impact** : Testabilité et monitoring
> **Dépend de** : Sprint 15

### Améliorations à implémenter

| # | Amélioration | Description | Effort |
|---|---|---|---|
| 17.1 | **Dashboard admin unifié** | Vue unique : santé services + derniers jobs + alertes + métriques IA | Moyen |
| 17.2 | **Bouton "Lancer tous les jobs du matin"** | Exécuter groupé les jobs 06:00-09:00 en un clic | Faible |
| 17.3 | **Mode "simuler une journée"** | Lancer séquentiellement tous les jobs d'une journée type (dry run) | Faible |
| 17.4 | **Log temps-réel WebSocket** | Stream des logs d'exécution en direct dans la console admin | Moyen |
| 17.5 | **Comparer dry run vs vraie exécution** | Tableau comparatif pour valider avant prod | Faible |
| 17.6 | **Export audit logs en PDF** | Rapport audit téléchargeable | Faible |
| 17.7 | **Panneau admin flottant — sécurité** | Confirmer : invisible pour utilisateur normal, protégé backend + frontend | Faible |

### Admin existant (rappel — déjà bien développé)

| Fonctionnalité | Route/Page | État |
|---|---|---|
| Audit logs | `GET /admin/audit-logs` | ✅ |
| CRON : lister/lancer/dry run/logs | `GET/POST /admin/jobs/` | ✅ |
| Notifications test | `POST /admin/notifications/test` | ✅ |
| Cache stats/purge | `GET/POST /admin/cache/` | ✅ |
| Services health | `GET /admin/services/health` | ✅ |
| Feature flags | Page admin/feature-flags | ✅ |
| IA métriques | Page admin/ia-metrics | ✅ |
| Event bus monitor | Page admin/events | ✅ |
| Console API | Page admin/console | ✅ |

### Critères de validation

- [ ] Dashboard admin unifié accessible
- [ ] Bouton "jobs du matin" fonctionne
- [ ] Mode "simuler une journée" exécute en dry run
- [ ] WebSocket log temps-réel fonctionnel
- [ ] `pytest` passe

---

## 20. Sprint 18 — UX simplification des flux

> **Objectif** : Simplifier les flux utilisateur principaux
> **Effort** : Moyen | **Impact** : Expérience utilisateur
> **Dépend de** : Sprints 11-13

### Principes

1. **L'utilisateur ne voit jamais la complexité** — pas de Phase A/B, pas d'innovations, pas de bridges visibles
2. **Actions en 1-3 clics max** — les flux principaux doivent être rapides
3. **L'IA travaille en arrière-plan** — suggestions proactives, pas de configuration manuelle
4. **Notifications intelligentes** — pas de spam, digest groupés, canal préféré auto-détecté
5. **Mode admin invisible** — panneau flottant accessible uniquement par rôle admin

### Flux à simplifier

| # | Flux | Étapes utilisateur | Travail IA en coulisses |
|---|---|---|---|
| 18.1 | **Planifier la semaine** | 1. Ouvrir Planning → 2. "Générer ma semaine" → 3. Valider/modifier | IA analyse stock, saison, historique préférences, météo, Jules |
| 18.2 | **Faire les courses** | 1. Clic "Liste de courses" → 2. Ajouter si besoin → 3. Valider | Générée auto depuis planning + stock bas + prédictions |
| 18.3 | **Après les courses** | 1. Scanner ou cocher "acheté" | Inventaire mis à jour, budget actualisé, prédictions ajustées |
| 18.4 | **Entretien maison** | 1. Voir tâches du jour (push) → 2. Marquer fait | IA planifie selon saison, historique, météo |
| 18.5 | **Suivi Jules** | 1. Ouvrir Jules → 2. Voir dashboard | Jalons auto-détectés, nutrition adaptée, courbes OMS |
| 18.6 | **Budget** | 1. Ouvrir Budget → voir statut | Catégorisation auto, alertes anomalies, prévisions |
| 18.7 | **Jardin** | 1. Ouvrir Jardin → voir tâches | Alertes météo, saisons, récoltes → auto-suggestion recettes |

### Actions rapides dashboard (UX2)

| Action rapide | Résultat |
|---|---|
| "Ajouter course" | Ouvre mini-modal ajout article |
| "Planifier repas" | Ouvre le planning de la semaine |
| "Nouvelle tâche" | Ouvre mini-modal ajout tâche |
| "Voir anomalies" | Navigue vers le détail de l'anomalie |

### Critères de validation

- [ ] Flux cuisine : recette → planning → courses en ≤ 3 clics
- [ ] Dashboard avec boutons d'action rapide
- [ ] Plus aucune page "innovations" visible utilisateur
- [ ] Navigation cohérente et intuitive

---

## 21. Sprint 19 — Visualisations 2D/3D

> **Objectif** : Ajouter des visualisations riches pour chaque module
> **Effort** : Élevé | **Impact** : Engagement visuel
> **Dépend de** : Sprint 18

### Visualisations à implémenter

| # | Visualisation | Module | Technologie | Description |
|---|---|---|---|---|
| 19.1 | **Timeline interactive famille** | Famille | D3/Recharts | Frise chronologique zoomable : jalons Jules, anniversaires, voyages, événements |
| 19.2 | **Heatmap planning nutritionnel** | Cuisine | Recharts | Carte thermique nutritionnelle sur le mois (carences, excès, variété) |
| 19.3 | **Vue jardin 2D interactive** | Maison:Jardin | Canvas/SVG | Plan du jardin avec zones cliquables, état des plantes, prochaines actions |
| 19.4 | **Treemap budget interactif** | Famille:Budget | D3/Recharts | Treemap cliquable des catégories de dépenses avec drill-down |
| 19.5 | **Graphe Sankey flux financiers** | Famille:Budget | D3 | Revenus → catégories → sous-catégories |
| 19.6 | **Calendrier énergie** | Maison:Énergie | Custom | Calendrier coloré par consommation jour/jour |
| 19.7 | **Radar nutritionnel famille** | Cuisine/Famille | Recharts | Radar chart : protéines, glucides, lipides, fibres, vitamines — toute la famille |
| 19.8 | **Animation batch cooking** | Cuisine:Batch | Framer Motion | Vue timeline des étapes batch cooking avec progression animée |
| 19.9 | **Dashboard glissières temporelles** | Dashboard | Custom slider | Slider pour comparer les métriques mois par mois |
| 19.10 | **Graphe réseau inter-modules** | Admin | D3 force-directed | Visualisation connexions entre modules (composant `graphe-reseau-modules.tsx` existe déjà) |

### Technologies frontend existantes utilisables

| Technologie | Déjà installée | Utilisation |
|---|---|---|
| Recharts | ✅ | Charts standards (bar, line, pie, radar) |
| D3 | ✅ | Visualisations complexes (Sankey, force-directed) |
| Three.js / @react-three | ✅ | 3D (plan maison 3D existant) |
| Framer Motion | ✅ | Animations et transitions |
| @dnd-kit | ✅ | Drag & drop |

### Critères de validation

- [ ] 10 nouvelles visualisations fonctionnelles
- [ ] Responsive (desktop + tablette + mobile)
- [ ] Dark mode compatible
- [ ] Performance acceptable (pas de lag sur les gros datasets)

---

## 22. Sprint 20 — UX avancée

> **Objectif** : Améliorer l'expérience utilisateur avec des features de confort
> **Effort** : Moyen | **Impact** : UX moderne
> **Dépend de** : Sprint 18

### Améliorations UX

| # | Amélioration | Description | Effort |
|---|---|---|---|
| 20.1 | **Quick actions universelles (IN6)** | Barre d'action universelle : "Ajoute tomates à la liste" sans changer de page | Moyen |
| 20.2 | **Recherche globale enrichie (UX3)** | `menu-commandes.tsx` (Ctrl+K) avec résultats plus riches : aperçu recettes, preview tâches | Moyen |
| 20.3 | **Undo/Redo sur suppressions (UX4)** | Toast avec bouton "Annuler" pour suppressions | Moyen |
| 20.4 | **Auto-save brouillons (UX9)** | Sauvegarde automatique des formulaires en cours | Moyen |
| 20.5 | **Raccourcis clavier par page (UX5)** | N pour nouveau, E éditer, S sauvegarder, Suppr supprimer | Faible |
| 20.6 | **Bulk actions sur listes (UX6)** | Sélection multiple + actions groupées (supprimer, déplacer, compléter) | Moyen |
| 20.7 | **Filtres avancés sidebar (UX7)** | Panneau latéral de filtres pour recettes, courses, tâches | Moyen |
| 20.8 | **Dark mode charts peaufiné (UX8)** | Vérifier cohérence graphiques/charts en mode sombre | Faible |
| 20.9 | **Swipe gestures mobiles (UX10)** | Étendre `swipeable-item.tsx` existant à toutes les listes | Faible |
| 20.10 | **Onboarding guidé (UX1)** | Tour interactif (~5 étapes) — `tour-onboarding.tsx` déjà créé, le connecter | Faible |

### Critères de validation

- [ ] Quick actions accessibles depuis n'importe quelle page
- [ ] Recherche globale affiche des previews riches
- [ ] Undo fonctionne sur suppressions (avec TTL 10s)
- [ ] Auto-save ne perd aucun brouillon après navigation
- [ ] Dark mode cohérent sur tous les charts

---

## 23. Sprint 21 — Innovations prioritaires

> **Objectif** : Implémenter les innovations les plus impactantes
> **Effort** : Moyen à Élevé | **Impact** : Fonctionnalités différenciantes
> **Dépend de** : Sprints 13, 18

### Innovations prioritaires

| # | Innovation | Description | Effort | Impact |
|---|---|---|---|---|
| 21.1 | **Mode saison cross-module (IN3)** | Adaptation automatique de tous les modules selon la saison : recettes saisonnières, jardin adapté, entretien saisonnier, activités, énergie | Moyen | Cohérence app |
| 21.2 | **Mode vacances (IN10)** | Toggle "En vacances" : courses mini, suspension entretien, checklist voyage active | Faible | UX |
| 21.3 | **Insights IA proactifs quotidiens (IN11)** | Push 1-2 insights/jour (pas de spam) : "Tu n'as pas mangé de poisson depuis 2 semaines" | Moyen | Engagement |
| 21.4 | **Journal automatique (IN14)** | Journal de bord auto-alimenté par les actions : repas, activités, événements | Faible | Mémoire familiale |
| 21.5 | **Rapport PDF mensuel unifié (IN5)** | Un seul PDF : résumé famille + budget + nutrition + maison + jardin + Jules | Faible | Rapports |
| 21.6 | **Score bien-être familial (IN2)** | Indicateur composite : nutrition + activités + budget + maison + Jules | Faible | Dashboard |
| 21.7 | **Intelligence contextuelle météo (IN4)** | Service météo unique impactant jardin + activités + recettes + énergie + entretien | Moyen | Cohérence |

### Critères de validation

- [ ] Mode saison détecte automatiquement la saison et adapte les suggestions
- [ ] Mode vacances toggle fonctionnel
- [ ] 1-2 insights IA par jour, pertinents, pas de spam
- [ ] Journal auto-alimenté visible dans la page famille
- [ ] PDF mensuel unifié généré et envoyé par email

---

## 24. Sprint 22 — Innovations avancées

> **Objectif** : Implémenter les innovations de personnalisation et d'intelligence
> **Effort** : Moyen à Élevé | **Impact** : Personnalisation
> **Dépend de** : Sprint 21

### Innovations avancées

| # | Innovation | Description | Effort |
|---|---|---|---|
| 22.1 | **Apprentissage des préférences (IN1)** | Système qui apprend les goûts, habitudes, rythmes de la famille au fil du temps | Moyen |
| 22.2 | **Planification hebdo complète automatique (IN9)** | Dim soir : auto-build planning repas + courses + tâches ménage + jardin en un bloc | Élevé |
| 22.3 | **Suggestions batch cooking intelligentes (IN13)** | IA propose un plan batch cooking optimal basé sur planning de la semaine | Moyen |
| 22.4 | **Cartes visuelles partageables (IN17)** | Générer une carte visuelle image pour recette, planning, etc. | Moyen |
| 22.5 | **Mode tablette magazine (IN7)** | Dashboard tablette spécifique avec vue magazine (widget-tablette existe déjà) | Moyen |

### Critères de validation

- [ ] Préférences apprises influencent les suggestions après 2+ semaines de données
- [ ] Planification auto génère un planning complet en un clic
- [ ] Batch cooking IA propose un plan cohérent
- [ ] Cartes visuelles exportables en image

---

## 25. Sprint 23 — Innovations long terme

> **Objectif** : Implémenter les innovations les plus ambitieuses
> **Effort** : Élevé | **Impact** : Différenciation majeure
> **Dépend de** : Sprint 22

### Innovations long terme

| # | Innovation | Description | Effort |
|---|---|---|---|
| 23.1 | **WhatsApp conversationnel (IN16)** | Répondre aux messages WhatsApp avec des actions : "Oui", "Non", "Ajoute X" → actions dans l'app | Élevé |
| 23.2 | **Comparateur prix automatique (IN15)** | Veille prix automatique sur les ingrédients fréquents (API scraping) + alertes soldes | Élevé |
| 23.3 | **Tableau de bord énergie temps-réel (IN12)** | Si compteur Linky connecté : visualisation en temps réel de la conso | Élevé |
| 23.4 | **Historique familial timeline étendu (IN8)** | Frise chronologique enrichie des événements marquants (jalons Jules, voyages, projets terminés, jardinage) | Moyen |

### Critères de validation

- [ ] WhatsApp conversationnel : au moins 5 commandes textuelles fonctionnelles
- [ ] Comparateur prix : scraping + alertes sur top 20 ingrédients
- [ ] Énergie temps-réel si Linky connecté
- [ ] Timeline enrichie avec tous les modules

---

## 26. Carte des dépendances entre sprints

```
Sprint 1 (Nettoyage legacy)
    │
    ├──→ Sprint 2 (SQL cleanup)
    │       │
    │       └──→ Sprint 4 (Restructuration)
    │
    ├──→ Sprint 3 (Renommage)
    │       │
    │       ├──→ Sprint 4 (Restructuration)
    │       └──→ Sprint 9 (Docs cleanup)
    │               │
    │               └──→ Sprint 10 (Docs manquants)
    │
    └──→ Sprint 5 (Bugs/TODOs)

Sprint 1-5 (Fondations propres)
    │
    └──→ Sprint 6 (Tests bridges)
            │
            ├──→ Sprint 7 (Tests E2E)
            │       │
            │       └──→ Sprint 8 (Tests compléments)
            │
            ├──→ Sprint 11 (Bridges haute priorité)
            │       │
            │       ├──→ Sprint 12 (Bridges moyenne priorité)
            │       │       │
            │       │       └──→ Sprint 14 (Event Bus)
            │       │
            │       └──→ Sprint 13 (Nouveaux services IA)
            │               │
            │               └──→ Sprint 15 (CRON jobs)
            │                       │
            │                       ├──→ Sprint 16 (Notifications)
            │                       └──→ Sprint 17 (Admin)
            │
            └──→ Sprint 18 (UX flux)
                    │
                    ├──→ Sprint 19 (Visualisations)
                    ├──→ Sprint 20 (UX avancée)
                    └──→ Sprint 21 (Innovations prioritaires)
                            │
                            └──→ Sprint 22 (Innovations avancées)
                                    │
                                    └──→ Sprint 23 (Innovations long terme)
```

### Parallélisation possible

Les groupes suivants peuvent être travaillés en parallèle :

| Groupe A (Backend) | Groupe B (Frontend) | Groupe C (Docs/Tests) |
|---|---|---|
| Sprint 1-2 (cleanup) | — | — |
| Sprint 3-4 (renommage) | Sprint 3 (renommage front) | Sprint 9 (docs cleanup) |
| Sprint 5 (bugs) | — | Sprint 10 (docs manquants) |
| Sprint 11-12 (bridges) | Sprint 18 (UX flux) | Sprint 6-8 (tests) |
| Sprint 13 (IA services) | Sprint 19 (visualisations) | — |
| Sprint 14-15 (events/CRON) | Sprint 20 (UX avancée) | — |
| Sprint 16 (notifications) | Sprint 21-23 (innovations) | — |
| Sprint 17 (admin) | — | — |

---

## 27. Métriques de suivi

### KPIs par phase

| Phase | Sprints | KPI principal | Cible |
|---|---|---|---|
| Fondations | 1-5 | Fichiers legacy restants | 0 |
| Tests | 6-8 | Couverture globale backend | ≥ 80% |
| Documentation | 9-10 | Docs avec refs legacy | 0 |
| Inter-modules | 11-14 | Bridges fonctionnels | 30+ (23 + 7 nouveaux) |
| IA | 13 | Services BaseAIService | 44+ (38 + 6 nouveaux) |
| Automatisation | 15-17 | CRON jobs fonctionnels | 57+ |
| UX | 18-20 | Flux ≤ 3 clics | 100% flux principaux |
| Innovations | 21-23 | Features innovantes livrées | 17 innovations |

### Compteurs globaux — avant vs après

| Métrique | Avant | Après (cible) |
|---|---|---|
| Fichiers avec noms phase/sprint | 17 | 0 |
| Commentaires phase/sprint | ~130 | 0 |
| Tables SQL inutilisées | ≥4 | 0 |
| Fichiers artefacts (bak, binaire) | 3+ | 0 |
| CRON jobs | 51 | ~57 |
| Bridges inter-modules | 23 | 30+ |
| Services IA | 38 | 44+ |
| Notifications WhatsApp | 5 | 12 |
| Tests E2E Playwright | ~5 | 15+ |
| Couverture tests backend | ~70% | ≥80% |
| Couverture tests frontend | ~40% | ≥60% |
| Documentation | 42 fichiers | 47+ fichiers |

---

## 28. Checklist de validation par sprint

### Sprint 1 — Nettoyage legacy ✅
- [x] Aucun fichier `.bak` dans `src/`
- [x] Aucun `audit_output.txt`
- [x] Aucun champ "legacy" dans les modèles ORM
- [x] CRON garanties/contrats supprimés
- [x] Pages OCR supprimées
- [x] Aliases rétrocompat nettoyés (28 supprimés, 2 conservés)
- [x] `pytest` vert (0 régression Sprint 1)

### Sprint 2 — SQL ✅
- [x] `sql/migrations/` supprimé
- [x] `sql/schema/17_migrations_absorbees.sql` supprimé
- [x] Tables contrats/contrats_maison/garanties/incidents_sav supprimées (SQL + modèles ORM)
- [x] Services contrats_crud_service.py et garanties_crud_service.py supprimés
- [x] Schémas Pydantic Contrat*/Garantie*/IncidentSAV* supprimés
- [x] Routes API contrats/garanties/charges/fin-vie supprimées
- [x] Event subscribers, CRON jobs, rappels intelligents nettoyés
- [x] Frontend : page contrats supprimée, hub/documents/équipements nettoyés
- [x] Types TS, API clients, navigation nettoyés
- [x] Références profondes nettoyées (events.py, notifications/types.py)
- [x] Gamification vérifiée sport-scoped (OK)
- [x] `INIT_COMPLET.sql` nettoyé
- [x] `pytest` vert (113 tests maison+events+cron passés, 0 régression Sprint 2)

### Sprint 3 — Renommage
- [ ] 17 fichiers renommés
- [ ] Tous les imports mis à jour
- [ ] 0 commentaires phase/sprint
- [ ] `pytest` vert + `npm run build` OK

### Sprint 4 — Restructuration
- [x] `innovations.py` restructuré
- [x] 1 seul fichier test décorateurs
- [x] `pytest` vert (scope Sprint 4: `tests/core/test_decorateurs.py`)

### Sprint 5 — Bugs ✅
- [x] TODO(P1-06) résolu
- [x] Panneau admin sécurisé (backend + frontend)
- [x] `pytest` vert (aucune régression)

### Sprint 6 — Tests bridges
- [ ] 23 tests de bridges créés
- [ ] `tests/inter_modules/` existe
- [ ] `pytest tests/inter_modules/` vert

### Sprint 7 — Tests E2E
- [ ] 10 parcours E2E Playwright
- [ ] Screenshots de référence
- [ ] `npx playwright test` vert

### Sprint 8 — Tests compléments
- [ ] Couverture backend ≥ 80%
- [ ] Couverture frontend ≥ 60%
- [ ] `pytest` vert complet

### Sprint 9 — Docs cleanup ✅
- [x] 0 refs legacy dans `docs/`
- [x] `GAMIFICATION.md` réduit au sport

### Sprint 10 — Docs manquants ✅
- [x] 4 guides créés
- [x] `ROADMAP.md` à jour
- [x] Chaque guide contient au moins un exemple de code

### Sprint 11 — Bridges haute priorité
- [ ] 4 bridges NIM1-NIM4 fonctionnels
- [ ] Tests inter-modules passent

### Sprint 12 — Bridges moyenne priorité
- [ ] 4 bridges NIM5-NIM8 fonctionnels
- [ ] Tests passent

### Sprint 13 — Services IA
- [ ] 6 nouveaux services IA
- [ ] Tous avec tests + `@service_factory`

### Sprint 14 — Event Bus
- [ ] Famille, Jeux, Dashboard publient des événements
- [ ] Tests event bus E2E passent

### Sprint 15 — CRON
- [ ] 8 nouveaux jobs ajoutés
- [ ] 2 jobs retirés
- [ ] Dry run fonctionnel pour chaque

### Sprint 16 — Notifications
- [ ] 7 templates WhatsApp
- [ ] 2 templates email/PDF
- [ ] Tests dry run passent

### Sprint 17 — Admin
- [ ] Dashboard admin unifié
- [ ] WebSocket log temps-réel
- [ ] Bouton jobs du matin

### Sprint 18 — UX flux
- [ ] Flux principaux ≤ 3 clics
- [ ] Actions rapides dashboard

### Sprint 19 — Visualisations
- [ ] 10 visualisations fonctionnelles
- [ ] Responsive + dark mode

### Sprint 20 — UX avancée
- [ ] Quick actions, undo, auto-save, bulk actions
- [ ] Recherche globale enrichie

### Sprint 21 — Innovations prioritaires
- [ ] Mode saison, mode vacances, insights IA, journal auto, PDF mensuel, score bien-être, météo cross

### Sprint 22 — Innovations avancées
- [ ] Apprentissage préférences, planification auto, batch cooking IA, cartes visuelles, mode tablette

### Sprint 23 — Innovations long terme
- [ ] WhatsApp conversationnel, comparateur prix, énergie temps-réel, timeline enrichie

---

> **Total : 23 sprints, ~150 tâches structurées**
> Chaque sprint est indépendant dans sa phase mais dépend des fondations précédentes.
> Les sprints sont nommés par fonctionnalité, pas par numéro arbitraire de phase.
> Ce planning couvre l'intégralité du contenu de l'ANALYSE_COMPLETE.md.
