 📋 PLANNING D'IMPLÉMENTATION — Assistant Matanne

> **Basé sur** : ANALYSE_COMPLETE.md (audit 360° du 30 mars 2026)  
> **Objectif** : Plan d'exécution détaillé avec toutes les tâches, priorisées et organisées en sprints  
> **Légende efforts** : S = ½ journée | M = 1-2 jours | L = 3-5 jours | XL = 1-2 semaines

---

## 📊 Tableau de bord projet — État de référence

| Catégorie | Métrique | État |
| ----------- | ---------- | ------ |
| **Tables SQL** | 143 tables, RLS, triggers, views | ✅ Solide |
| **Modèles ORM** | 31 fichiers, ~95% alignés SQL | ✅ |
| **Endpoints API** | 242+ endpoints REST (42 routers) | ✅ |
| **Services** | 60+ services (23 IA) | ✅ |
| **Pages Frontend** | 103 pages (App Router) | ⚠️ ~12 pages IA incomplètes |
| **Composants** | 105+ composants React | ✅ |
| **Tests Backend** | 70+ fichiers pytest | ⚠️ 9 routes non testées |
| **Tests Frontend** | 12 E2E + ~5 unit tests | ⚠️ Couverture unit faible |
| **Documentation** | 34 docs + 8 guides modules (Sprint H : +8 docs) | ✅ 95% à jour |
| **Jobs CRON** | 38+ jobs APScheduler | ✅ Opérationnel |
| **Notifications** | 4 canaux (push/email/WhatsApp/ntfy) | ✅ |
| **PWA** | Service Worker + manifest + offline | ✅ |

---

## Table des matières

1. Vue d'ensemble des phases
2. Sprint A — Corrections critiques
3. Sprint B — Tests manquants
4. Sprint C — Pages IA Avancée
5. Sprint D — Inter-modules & Event Bus
6. Sprint E — Notifications enrichies
7. Sprint F — Admin & DX
8. Sprint G — UX & Simplification flux
9. Sprint H — Consolidation SQL & Organisation code
10. Sprint I — Innovations long terme
11. Référentiel Bugs
12. Référentiel Gaps & Features manquantes
13. Référentiel Consolidation SQL
14. Référentiel Couverture de tests
15. Référentiel Documentation
16. Référentiel Interactions intra-modules
17. Référentiel Interactions inter-modules
18. Référentiel Opportunités IA
19. Référentiel Jobs CRON
20. Référentiel Notifications
21. Référentiel Mode Admin
22. Référentiel Simplification UX
23. Référentiel Organisation du code
24. Référentiel Axes d'innovation
25. Annexes

---

## Phase 0 — Vue d'ensemble

### Ordre d'exécution des sprints

```text
PRIORITÉ CRITIQUE (qualité & stabilité)
  Sprint A ── Corrections critiques          → ✅ TERMINÉ (30 mars 2026)
  Sprint B ── Tests manquants                → ✅ IMPLÉMENTÉ (phase 1: backend + unit + CI)

PRIORITÉ HAUTE (fonctionnalités core)
  Sprint C ── Pages IA Avancée               → ✅ TERMINE (31 mars 2026, 14 outils)
  Sprint D ── Inter-modules & Event Bus      → 7 flux majeurs

PRIORITÉ MOYENNE (enrichissement)
  Sprint E ── Notifications enrichies        → WhatsApp + centre notif
  Sprint F ── Admin & DX                     → Dashboard admin + outils
  Sprint G ── UX & Simplification flux       → 10 flux simplifiés

PRIORITÉ BASSE (consolidation & innovation)
  Sprint H ── Consolidation SQL & Code       → Organisation + docs
  Sprint I ── Innovations long terme         → Multi-users, analytics, IA proactif
```

### Matrice de dépendances

```text
Sprint A → (aucune dépendance, lancer en premier)
Sprint B → Sprint A (valider les corrections)
Sprint C → Sprint A (bugs corrigés avant nouvelles features)
Sprint D → Sprint C (pages IA existantes pour les flux inter-modules)
Sprint E → Sprint D (événements bus pour déclencher les notifications)
Sprint F → Sprint A (admin rate limiting corrigé)
Sprint G → Sprint C + Sprint E (pages + notifications prêtes)
Sprint H → indépendant (peut être parallélisé)
Sprint I → Sprint D + Sprint G (base fonctionnelle stable)
```

---

## Sprint A — Corrections critiques (bugs + qualité) ✅ TERMINÉ

**Objectif** : Stabiliser la base de code — aucun bug silencieux, sécurité durcie
**Date de complétion** : 30 mars 2026

| # | Tâche | Réf | Effort | Fichier(s) concerné(s) | Checklist |
| --- | ------- | ----- | -------- | ------------------------ | ----------- |
| A.1 | Corriger les 4 blocs `except: pass` silencieux dans webhook WhatsApp | B1 | S | `src/api/routes/webhooks_whatsapp.py` (L621, 964, 984, 1008) | ✅ Remplacé par `except Exception as e: logger.error/warning(...)` |
| A.2 | Corriger `except: pass` dans endpoint auth — échec d'audit silencieux | B2 | S | `src/api/routes/auth.py` (L94) | ✅ Ajout `logger.debug()` sur conversion int échouée |
| A.3 | Corriger `except: pass` dans export PDF | B3 | S | `src/api/routes/export.py` (L204) | ✅ Ajout `logger.warning()` sur content-type inattendu |
| A.4 | Corriger `except: pass` dans préférences | B4 | S | `src/api/routes/preferences.py` (L285) | ✅ Ajout `logger.warning()` sur format time invalide |
| A.5 | Ajouter rate limiting sur endpoints admin | B6 | S | `src/api/routes/admin.py` | ✅ Rate limit router-level 10 req/min via `_verifier_limite_admin` dependency |
| A.6 | Implémenter rate limiting IA per-user (pas global) | B7 | M | `src/core/ai/rate_limit.py` | ✅ Quota par user_id ✅ Compteur par user ✅ `peut_appeler(user_id)` + `enregistrer_appel(..., user_id)` |
| A.7 | CORS strict en production (pas de wildcard) | B8 | S | `src/api/main.py` | ✅ Conditionnel ENVIRONMENT ✅ Warning si CORS_ORIGINS absent en prod/staging ✅ Origins vides par défaut en prod |
| A.8 | Ajouter skeletons/loading sur toutes les pages hub | B11, G24 | M | `frontend/src/app/(app)/*/loading.tsx` | ✅ habitat ✅ ia-avancee (planning et maison déjà existants) |
| A.9 | Vérifier nettoyage WebSocket hooks on unmount | B12 | S | `frontend/src/crochets/` | ✅ Audit OK — cleanup correct dans `utiliser-websocket.ts` et `utiliser-websocket-courses.ts` |
| A.10 | Documenter auth WebSocket (validation JWT) | B15 | S | `docs/ARCHITECTURE.md` | ✅ Section « Authentification WebSocket » ajoutée dans ARCHITECTURE.md |

### Tâches différées (moyen terme)

| # | Tâche | Réf | Effort | Notes |
| --- | ------- | ----- | -------- | ------- |
| A.11 | Cache d'idempotence courses → Redis ou DB au lieu de mémoire | B5 | M | ✅ Idempotence courses migrée vers cache multi-niveaux (Redis si disponible) |
| A.12 | Invalidation cache auto quand modèles modifiés en DB | B9 | M | ✅ Listener PostgreSQL `planning_changed` en backend (LISTEN/NOTIFY) + invalidation cache automatique (L1/L2/Redis + purge L3) |
| A.13 | CSP strict (retirer `unsafe-inline`) dans `next.config.ts` | B10 | M | ✅ CSP stricte en production (unsafe-inline/eval retirés), policy dev conservée |
| A.14 | Toast notifications extensibles par l'utilisateur | B13 | S | ✅ Store notifications configurable (durée, conservation erreurs, prefs persistées) |
| A.15 | Retry auto sur erreurs DB transitoires | B14 | S | ✅ Retry borné implémenté dans `executer_async` pour erreurs DB transitoires |

---

## Sprint B — Tests manquants ✅ COMPLÉTÉ

**Objectif** : Couverture backend 75% → 85%, initier les tests unit frontend
**Date de complétion** : 10 janvier 2025 (Phase 1+2: backend + frontend + E2E)
**Rapport détaillé** : [SPRINT_B_COMPLETION_REPORT.md](./SPRINT_B_COMPLETION_REPORT.md)

### Backend — Routes API sans tests (9 routes)

| # | Tâche | Route | Fichier test | Priorité | Effort | Statut | Tests |
| --- | ------- | ------- | -------------- | ---------- | -------- | -------- | -------- |
| B.1 | Tests route dashboard | `dashboard` | `tests/api/test_routes_dashboard.py` | 🔴 | M | ✅ | 4/4 PASS |
| B.2 | Tests route famille_jules | `famille_jules` | `tests/api/test_routes_famille_jules.py` | 🔴 | M | ✅ | 7/7 PASS |
| B.3 | Tests route famille_budget | `famille_budget` | `tests/api/test_routes_famille_budget.py` | 🟡 | M | ✅ | 7/7 PASS |
| B.4 | Tests route famille_activites | `famille_activites` | `tests/api/test_routes_famille_activites.py` | 🟡 | M | ✅ | 7/7 PASS |
| B.5 | Tests route maison_projets | `maison_projets` | `tests/api/test_routes_maison_projets.py` | 🟡 | M | ✅ | 7/7 PASS |
| B.6 | Tests route maison_jardin | `maison_jardin` | `tests/api/test_routes_maison_jardin.py` | 🟡 | M | ✅ | 9/9 PASS |
| B.7 | Tests route maison_finances | `maison_finances` | `tests/api/test_routes_maison_finances.py` | 🟡 | M | ✅ | 8/8 PASS |
| B.8 | Tests route maison_entretien | `maison_entretien` | `tests/api/test_routes_maison_entretien.py` | 🟡 | M | ✅ | 8/8 PASS |
| B.9 | Tests route partage | `partage` | `tests/api/test_routes_partage.py` | 🟢 | S | ✅ | 2/2 PASS |
| **TOTAL BACKEND** | | | | | | **✅** | **59/59 PASS** |

### Backend — Couverture par couche (référence)

| Couche | Fichiers | Tests | Couverture actuelle | Cible |
| -------- | ---------- | ------- | --------------------- | ------- |
| **Core** (config, DB, cache, decorators) | 12 fichiers | ~100 tests | 90% | 95% |
| **Modèles ORM** | 22 fichiers | ~80 tests | 70% | 85% |
| **Routes API** | 30 fichiers | ~150 tests | 77% | 90% |
| **Services** | 20+ fichiers | ~100 tests | 90% | 95% |
| **Spécialisés** (contrats, perf, SQL) | 5 fichiers | ~30 tests | Variable | — |
| **Total Backend** | **70+ fichiers** | **~460 tests** | **~75%** | **85%** |

### Frontend — Plan de tests

| # | Tâche | Type | Fichier(s) | Effort | Statut | Tests |
| --- | ------- | ------ | ----------- | -------- | -------- | -------- |
| B.10 | Tests custom hooks (utiliser-api, utiliser-auth) | Unit (Vitest) | `frontend/src/__tests__/hooks/utiliser-api.test.ts`, `frontend/src/__tests__/hooks/utiliser-auth.test.ts` | M | ✅ | 5/5 PASS |
| B.11 | Tests composants critiques (sidebar, pages hub) | Unit (Vitest) | `frontend/src/__tests__/components/barre-laterale.test.tsx`, `frontend/src/__tests__/pages/hubs.test.tsx` | M | ✅ | 4/4 PASS |
| B.12 | E2E complets par module (cuisine, famille, maison) | E2E (Playwright) | `frontend/e2e/cuisine-complet.spec.ts`, `frontend/e2e/modules-complet.spec.ts` | L | ✅ | Ready |
| B.13 | Tests d'accessibilité WCAG2A/2AA (axe-core) | E2E | `frontend/e2e/accessibility.spec.ts` | M | ✅ | Ready |
| **TOTAL FRONTEND** | | | | | **✅** | **9/9 PASS + 2 E2E suites ready** |

### CI — Validation schéma

| # | Tâche | Réf | Effort | Statut | Détail |
| --- | ------- | ----- | -------- | -------- | -------- |
| B.15 | Ajouter `test_schema_coherence.py` au pipeline CI | S3 | S | ✅ | `.github/workflows/tests.yml` + `.github/workflows/backend-tests.yml` wired |
| B.16 | Mock fix: `useMutation` callback execution (Vitest) | — | S | ✅ | Fixed frontend test mock to properly invoke `onSuccess` callback |

---

## Sprint C — Pages IA Avancée ✅ TERMINE

**Objectif** : Finaliser les pages IA avancées, les clients API et la documentation

### Pages à finaliser/créer

| # | Page | État actuel | Action requise | Effort |
| --- | ------ | ------------- | ---------------- | -------- |
| C.1 | `/ia-avancee/suggestions-achats` | ✅ Page complete et connectee API | Cloture | M |
| C.2 | `/ia-avancee/diagnostic-plante` | ✅ Page complete (upload image + rendu resultat) | Cloture | M |
| C.3 | `/ia-avancee/planning-adaptatif` | ✅ Page complete et connectee API | Cloture | M |
| C.4 | `/ia-avancee/analyse-photo` | ✅ Page complete et connectee API | Cloture | M |
| C.5 | `/ia-avancee/optimisation-routines` | ✅ Page complete et connectee API | Cloture | M |
| C.6 | `/ia-avancee/recommandations-energie` | ✅ Finalisee | Cloture | S |
| C.7 | `/ia-avancee/prevision-depenses` | ✅ Finalisee | Cloture | S |
| C.8 | `/ia-avancee/idees-cadeaux` | ✅ Finalisee | Cloture | S |
| C.9 | `/ia-avancee/analyse-document` | ✅ Finalisee | Cloture | S |
| C.10 | `/ia-avancee/estimation-travaux` | ✅ Finalisee | Cloture | S |
| C.11 | `/ia-avancee/planning-voyage` | ✅ Finalisee | Cloture | S |
| C.12 | `/ia-avancee/adaptations-meteo` | ✅ Finalisee | Cloture | S |

### Correspondance legacy (analyse initiale → routes finales)

| Entrée legacy | Route finale retenue |
| --- | --- |
| `/ia-avancee/optimisation-stock` | `/ia-avancee/optimisation-routines` |
| `/ia-avancee/analyse-habitudes` | `/ia-avancee/analyse-photo` |
| `/ia-avancee/conseiller-energie` | `/ia-avancee/recommandations-energie` |
| `/ia-avancee/prevision-courses` | `/ia-avancee/suggestions-achats` |
| `/ia-avancee/menu-equilibre` | `/ia-avancee/planning-adaptatif` + `/ia-avancee/adaptations-meteo` |
| `/ia-avancee/routine-optimale` | `/ia-avancee/optimisation-routines` |
| `/ia-avancee/bilan-financier` | `/ia-avancee/prevision-depenses` |
| `/ia-avancee/assistant-jardin` | `/ia-avancee/diagnostic-plante` |
| `/ia-avancee/coach-bien-etre` | `/ia-avancee/suggestions-proactives` |

### Clients API & Infrastructure

| # | Tâche | Réf | Effort | Statut |
| --- | ------- | ----- | -------- | -------- |
| C.13 | Fonctions client IA ajoutees et alignees backend dans `ia_avancee.ts` | G25 | M | ✅ |
| C.14 | Guide module IA Avancee cree (`docs/guides/ia-avancee/README.md`) | D1 | M | ✅ |
| C.15 | Error boundaries presentes sur `planning`, `habitat`, `ia-avancee` | G23 | M | ✅ |
| C.16 | Pages admin frontend enrichies (jobs, services, utilisateurs, notifications, SQL views) | G26 | M | ✅ |
| C.17 | Section RGPD presente dans `/parametres` (export/suppression) | G27 | S | ✅ |

---

## Sprint D — Inter-modules & Event Bus

**Objectif** : Implémenter les 7 flux inter-modules prioritaires + enrichir le bus d'événements

### Flux inter-modules existants (8 — référence)

| # | Flux | Source → Cible | Fichier | Trigger |
| --- | ------ | ---------------- | --------- | --------- |
| 1 | Péremption → Recettes | Inventaire → Cuisine | `inter_module_peremption_recettes.py` | Job/API |
| 2 | Total courses → Budget | Courses → Famille | `inter_module_courses_budget.py` | Save courses |
| 3 | Document expire → Alerte | Famille → Notifications | `inter_module_documents_notifications.py` | Job J-30/15/7/1 |
| 4 | Chat IA → Multi-contexte | Tous → Utilitaires | `inter_module_chat_contexte.py` | Chat appel |
| 5 | Batch cooking → Stock | Cuisine → Inventaire | `inter_module_batch_inventaire.py` | Fin session |
| 6 | Anniversaires → Budget | Famille → Famille | `inter_module_anniversaires_budget.py` | Auto |
| 7 | Voyages → Budget | Voyages → Famille | `inter_module_voyages_budget.py` | Save voyage |
| 8 | Mises jeux → Budget | Jeux → Famille | `inter_module_budget_jeux.py` | Mise placée |

### Flux à implémenter (prioritaires)

| # | Tâche | Réf | Source → Cible | Effort | Checklist |
| --- | ------- | ----- | ---------------- | -------- | ----------- |
| D.1 | Récolte jardin → Recettes saison (proposées au prochain planning semaine) | I1 | Maison/Jardin → Cuisine | M | ✅ Event `jardin.recolte` ✅ Abonné suggestions/cache ✅ Tests |
| D.2 | Anomalie énergie → Tâche entretien auto | I3 | Maison/Énergie → Maison/Entretien | S | ✅ Event `energie.anomalie` ✅ Création tâche ✅ Tests |
| D.3 | Budget dépassement → Alerte dashboard | I4 | Famille/Budget → Dashboard | S | ✅ Event `budget.depassement` ✅ Alerte/backend cache ✅ Tests |
| D.4 | Inventaire → Courses prédictives | I9 | Inventaire → Courses | L | ✅ Event + service prédictif + recalcul + tests (version v1) |
| D.5 | Retour recette → Ajuster planning futur (feedback loop IA) | I13 | Cuisine → Planning | M | ✅ Event `recette.feedback` ✅ Invalidation contexte planning ✅ Tests |
| D.6 | Contrats maison → Alertes renouvellement | I14 | Maison/Contrats → Notifications | S | ✅ Event/notifications multi-canal ✅ Tests |
| D.7 | Enrichir abonnés EventBus (pas juste cache) | — | Global | M | ✅ Subscribers business ajoutés (D.1→D.6) + tests |

### Flux futurs (backlog)

| # | Flux proposé | Réf | Source → Cible | Valeur | Effort |
| --- | ------------- | ----- | ---------------- | -------- | -------- |
| D.8 | Garmin santé → Activités Jules | I2 | Famille/Garmin → Famille/Jules | 🟡 | M |
| D.9 | Météo → Planning repas adapté | I5 | Outils/Météo → Cuisine/Planning | 🟡 | M |
| D.10 | Météo → Tâches jardin urgentes | I6 | Outils/Météo → Maison/Jardin | 🟡 | S |
| D.11 | Projets terminés → Valeur bien habitat | I7 | Maison/Projets → Habitat | 🟡 | M |
| D.12 | Entretien artisan → Devis comparatif auto | I8 | Maison/Entretien → Maison/Artisans | 🟡 | M |
| D.13 | Routines santé → Briefing matinal | I11 | Famille/Santé → Dashboard | 🟡 | S |
| D.14 | Anniversaire → Suggestion cadeau IA | I12 | Famille → IA Avancée | 🟢 | M |
| D.15 | Score gamification → Récompenses famille | I15 | Gamification → Famille | 🟢 | M |
| — | ~~Résultats paris → P&L famille~~ | ~~I10~~ | ❌ **Rejeté** — Budget jeux volontairement séparé | — | — |

### Architecture Event Bus — Pattern d'implémentation

Le bus d'événements `EventBus` émet des événements `recette.*`, `stock.*`, `courses.*`, `entretien.*`, `planning.*`, `jeux.*` — mais les **seuls abonnés sont pour l'invalidation de cache**.

**Opportunité** : Ajouter des abonnés pour déclencher les flux D.1-D.7 via le bus existant, sans coupler les services.

```python
# Exemple : Récolte jardin → Suggestions recettes
bus.souscrire("jardin.recolte", lambda evt: 
    get_suggestions_service().suggerer_recettes_saison(evt["plantes_recoltees"])
)
```

---

## Sprint E — Notifications enrichies

**Objectif** : Enrichir WhatsApp, ajouter centre de notifications, nouveaux jobs CRON

### Architecture notifications (référence)

```text
DispatcherNotifications (central)
├── ntfy.sh        → REST API → push notifications
├── Web Push       → VAPID protocol → navigateur
├── Email          → Resend API → Jinja2 templates
└── WhatsApp       → Meta Cloud API → webhook bidirectionnel
```

### Tâches notifications

| # | Tâche | Réf | Canal | Effort | Checklist |
| --- | ------- | ----- | ------- | -------- | ----------- |
| E.1 | WhatsApp : Flux liste courses semaine | N1 | WhatsApp | M | ✅ Handler/service implémentés (version v1) |
| E.2 | WhatsApp : Rappel activité Jules | N2 | WhatsApp | S | ✅ Handler/service implémentés (version v1) |
| E.3 | WhatsApp : Résultats paris sportifs | N3 | WhatsApp | S | ✅ Handler/service implémentés (version v1) |
| E.4 | Préférences notifications granulaires — UI par module | N9 | Tous | M | ✅ Schéma + API + service + UI centre notifs (version v1) |
| E.5 | Centre de notifications dans l'app (historique) | N10 | Tous | M | ✅ Page + listing + marquer lu/tous lus + filtres/stats |
| E.6 | Email : Newsletter hebdo template riche | N5 | Email | M | ✅ Job/service implémentés (version v1) |
| E.7 | Email : Rapport budget PDF en pièce jointe | N6 | Email | S | ✅ Flux email rapport implémenté (version v1) |
| E.8 | Push : Actions rapides dans les notifications | N7 | Push | M | ✅ Flux push enrichi (version v1) |

### Nouveaux jobs CRON

| # | Job | Réf | Schedule | Description | Effort | Statut |
| --- | ----- | ----- | ---------- | ------------- | -------- | -------- |
| E.9 | `prediction_courses_hebdo` | C1 | Dim 18h | Générer liste courses prédictive pour la semaine | M | ✅ |
| E.10 | `rapport_energie_mensuel` | C2 | 1er 10h | Rapport conso énergie + comparaison mois précédent | S | ✅ |
| E.11 | `suggestions_recettes_saison` | C3 | 1er et 15 6h | Nouvelles recettes de saison à découvrir | S | ✅ |
| E.12 | `audit_securite_hebdo` | C4 | Dim 2h | Vérification intégrité données + logs suspects | M | ✅ |
| E.13 | `nettoyage_notifications_anciennes` | C5 | Dim 4h | Purger notifications > 90 jours | S | ✅ |
| E.14 | `mise_a_jour_scores_gamification` | C6 | Minuit | Recalculer scores/badges quotidiens | S | ✅ |
| E.15 | `alerte_meteo_jardin` | C7 | 7h | Alerte gel/canicule → protéger plantes | S | ✅ |
| E.16 | `resume_financier_semaine` | C8 | Ven 18h | Résumé dépenses de la semaine | S | ✅ |

### Mapping événements → canaux (existant + proposé)

| Événement | ntfy | Push | Email | WhatsApp | État |
| ----------- | ------ | ------ | ------- | ---------- | ------ |
| Péremption J-2 | ✅ | ✅ | — | — | ✅ Implémenté |
| Rappel courses | ✅ | ✅ | — | ✅ | ✅ Implémenté |
| Résumé hebdo | — | — | ✅ | ✅ | ✅ Implémenté |
| Échec cron job | ✅ | ✅ | ✅ | ✅ | ✅ Implémenté |
| Document expirant | ✅ | ✅ | ✅ | — | ✅ Implémenté |
| Rappel vaccin | — | ✅ | ✅ | — | ✅ Implémenté |
| **Liste courses semaine** | — | ✅ | — | ✅ | ☐ À ajouter |
| **Résultats paris** | ✅ | ✅ | — | ✅ | ☐ À ajouter |
| **Budget dépassé** | ✅ | ✅ | ✅ | ✅ | ☐ À ajouter |
| **Activité Jules** | — | ✅ | — | ✅ | ☐ À ajouter |
| **Alerte météo jardin** | ✅ | ✅ | — | — | ☐ À ajouter |
| **Contrat à renouveler** | — | ✅ | ✅ | — | ☐ À ajouter |

---

## Sprint F — Admin & DX

**Objectif** : Dashboard admin riche, outils développeur, mode maintenance

### Fonctionnalités admin existantes (référence)

| Feature | Endpoint | État |
| --------- | ---------- | ------ |
| Liste jobs | `GET /api/v1/admin/jobs` | ✅ |
| Trigger manuel | `POST /api/v1/admin/jobs/{id}/run` | ✅ (rate limit 5/min) |
| Dry run | `POST /api/v1/admin/jobs/{id}/run?dry_run=true` | ✅ |
| Logs jobs | `GET /api/v1/admin/jobs/{id}/logs` | ✅ |
| Audit logs | `GET /api/v1/admin/audit-logs` | ✅ |
| Stats audit | `GET /api/v1/admin/audit-stats` | ✅ |
| Export audit CSV | `GET /api/v1/admin/audit-export` | ✅ |
| Health check services | `GET /api/v1/admin/services/health` | ✅ |
| Test notifications | `POST /api/v1/admin/notifications/test` | ✅ |
| Stats cache | `GET /api/v1/admin/cache/stats` | ✅ |
| Purge cache | `POST /api/v1/admin/cache/clear` | ✅ |
| Liste users | `GET /api/v1/admin/users` | ✅ |
| Désactiver user | `POST /api/v1/admin/users/{id}/disable` | ✅ |
| Cohérence DB | `GET /api/v1/admin/db/coherence` | ✅ |
| Feature flags | `GET/PUT /api/v1/admin/feature-flags` | ✅ |
| Runtime config | `GET/PUT /api/v1/admin/config` | ✅ |
| Flow simulator | `POST /api/v1/admin/simulate-flow` | ✅ |

### Tâches admin

| # | Tâche | Réf | Effort | Checklist |
| --- | ------- | ----- | -------- | ----------- |
| F.1 | Dashboard admin dédié — graphiques jobs, erreurs, usage IA, notifications | A1 | M | ✅ Page frontend ✅ API agrégation ✅ Charts |
| F.2 | Console IA admin — tester un prompt depuis l'admin, voir réponse brute | A2 | S | ✅ Input prompt ✅ Affichage réponse ✅ Rate limit |
| F.3 | Seed data one-click (dev only) | A3 | S | ✅ POST /seed/dev ✅ Parse recettes_standard.json ✅ Guard env=dev + pytest |
| F.4 | Panneau admin flottant (Ctrl+Shift+A) | 🟡 | M | ✅ Overlay React + raccourci clavier + métriques/flags/jobs |
| F.5 | Toggle mode maintenance (bandeau utilisateur) | A10 | S | ✅ API toggle + lecture publique + bandeau UI |
| F.6 | Queue de notifications à voir et gérer la file d'attente | A8 | S | ✅ API listing + UI admin + retry/purge |
| F.7 | Historique jobs paginé avec filtres | A9 | M | ✅ GET /jobs/history paginesé ✅ Filtres status/date/job_id ✅ Page admin + UI |
| F.8 | Reset module (dev only) à vider données d'un module | A4 | S | ✅ Endpoint `/api/v1/admin/reset-module` + guard env=dev/test |
| F.9 | Export DB complet JSON/SQL | A5 | M | ✅ Export sérialisé ✅ Download |
| F.10 | Import DB — restaurer un backup | A6 | M | ✅ Upload ✅ Validation ✅ Restore |
| F.11 | Monitoring temps réel — WebSocket admin métriques live | A7 | L | ✅ WS endpoint ✅ Dashboard real-time |

### Principe admin

L'admin est accessible via :
- `Depends(require_role("admin"))` côté API (protégé)
- Conditionnel dans la sidebar frontend (si `user.role === 'admin'`)
- Feature flag `admin.mode_test` pour activer des fonctions debug
- **Panneau admin flottant** (overlay) activable par `Ctrl+Shift+A` — invisible pour les utilisateurs normaux

---

## Sprint G — UX & Simplification flux

**Objectif** : Maximum 3 clics pour toute action courante, zéro config au premier lancement

### Principes UX

```text
1. Maximum 3 clics pour toute action courante
2. Zéro configuration requise au premier lancement
3. L'IA fait le travail, l'utilisateur valide
4. Notifications proactives plutôt que consultation
5. Interface adaptative (mobile-first, contexte-sensitive)
```

### Flux à simplifier

| # | Tâche | Réf | Flux actuel | Flux cible | Effort | Statut |
| --- | ------- | ----- | ------------- | ------------ | -------- | -------- |
| G.1 | Bouton "Planifier ma semaine" one-click | U1 | Planning → Choisir jour → Chercher recette → Sélectionner (4 clics) | **1 clic** : IA génère → Valider/ajuster | S | ✅ |
| G.2 | Génération courses auto depuis planning validé | U2 | Naviguer Courses → Créer liste → Ajouter un par un | **Auto** : Depuis planning → "Générer courses" → Liste pré-remplie | S | ✅ |
| G.3 | Widget budget sur le dashboard avec tendance | U3 | Famille → Budget → Filtrer mois → Lire | **Dashboard** : Widget tendance budget en page d'accueil | S | ✅ |
| G.4 | Recherche globale instantanée de recettes | U4 | Cuisine → Recettes → Filtres → Parcourir | **Barre de recherche** : Résultats instantanés | M | ✅ |
| G.5 | Wizard création projet maison (3 étapes) | U5 | Formulaire complet à remplir | **Wizard** : Nom → Type/Budget → Tâches suggérées IA | M | ✅ (31/03/2026) |
| G.6 | Alertes proactives inventaire bas → action directe depuis notif | U6 | Cuisine → Inventaire → Parcourir | **Notifications** push quand stock bas | S | ✅ (31/03/2026) |
| G.7 | Timeline Jules chronologique unique (jalons + activités + santé) | U7 | Navigation onglets multiples | **Timeline** : Vue unique chronologique | M | ✅ |
| G.8 | Checklist du jour (widget dashboard) avec swipe pour valider | U8 | Maison → Entretien → Voir tâches → Marquer fait | **Widget** : Swipe pour valider dans le dashboard | S | ✅ (31/03/2026) |
| G.9 | Widget météo intégré (header ou dashboard) → adapte suggestions | U9 | Outils → Météo → Page dédiée | **Intégré** : Météo directement dans le header/dashboard | S | ✅ |
| G.10 | Préférences notifications par module (dans chaque module) | U10 | Paramètres → Section notifications → Toggle par type | **Par module** : "Me notifier pour..." dans chaque module | M | ✅ (31/03/2026) |
| G.11 | Mode focus "essentiel du jour" (1 écran) | IN11 | Plusieurs pages à consulter | **1 écran** : météo + repas + tâches + rappels | M | ✅ (31/03/2026) |
| G.12 | Mode vacances (pause notifications non essentielles) | IN14 | Pas de fonctionnalité | **Toggle** : Pause + checklist voyage auto | S | ✅ (31/03/2026) |

### Bilan Sprint G (mise à jour du 31/03/2026)

- ✅ Implémenté dans cette passe : G.5, G.10, G.11, G.12
- ✅ Déjà présent dans le code et confirmé : G.1, G.2, G.3, G.4, G.7, G.9
- ✅ Sprint G désormais couvert sur les 12 items (G.1 → G.12)

### Composants UX à ajouter/enrichir

| # | Composant | Réf | Description | Impact |
| --- | ----------- | ----- | ------------- | -------- |
| G.13 | Quick Actions FAB enrichi | UX1 | Actions rapides contextuelles (existant, à enrichir) | Navigation rapide |
| G.14 | Command Palette enrichie | UX2 | `Cmd+K` pour naviguer/agir (existant `menu-commandes.tsx`) | Power users |
| G.15 | Onboarding tour amélioré | UX3 | Tour guidé au premier lancement (existant `tour-onboarding.tsx`) | Découvrabilité |
| G.16 | Empty states riches | UX4 | Module vide → message encourageant + CTA pour commencer | Engagement |
| G.17 | Skeleton screens complets | UX5 | Loading skeletons sur toutes les pages restantes | UX perçue |
| G.18 | Swipe gestures mobile généralisées | UX6 | Swipe gauche/droite sur items de liste (existant, généraliser) | Mobile fluide |
| G.19 | Cards drag & drop dashboard | UX7 | Réorganisation widgets dashboard (existant `grille-widgets.tsx`) | Personnalisation |
| G.20 | Confirmations inline (toasts au lieu de modals) | UX8 | Toasts pour actions simples, modals pour actions destructives | Moins intrusif |

---

## Sprint H — Consolidation SQL & Organisation code

**État** : ✅ COMPLÉTÉ À 100% — Avril 2026

**Objectif** : SQL structuré, code organisé, documentation complète

### Consolidation SQL

#### État actuel SQL

- **Fichier source** : `sql/INIT_COMPLET.sql` (~3000+ lignes)
- **Migrations** : `sql/migrations/` (V003 à V007)
- **Alembic** : Archivé intentionnellement (stratégie SQL-first)
- **Alignement ORM** : ~95% (31 fichiers modèles ↔ 143 tables)

#### Tâches SQL

| # | Tâche | Réf | Effort | Checklist |
| --- | ------- | ----- | -------- | ----------- |
| H.1 | Découper `INIT_COMPLET.sql` en fichiers thématiques | S1 | M | ✅ Structure ci-dessous ✅ Fichiers créés ✅ Testé |
| H.2 | Script `scripts/db/regenerate_init.py` — concatène schema/* → INIT_COMPLET.sql | S1 | S | ✅ Script ✅ Idempotent ✅ Tests |
| H.3 | Compléter ORM pour tables orphelines (`notes_memos`, `presse_papier_entrees`, `releves_energie`) | S2 | S | ✅ Modèles ORM ✅ Tests |
| H.4 | Audit indexes sur colonnes fréquemment filtrées | S4 | M | ✅ docs/guides/DATABASE_INDEXES.md créé ✅ Index listés |
| H.5 | Documenter le workflow SQL-first (migrations) | S5 | S | ✅ Section ajoutée dans MIGRATION_GUIDE.md |

#### Structure SQL cible

```text
sql/
├── INIT_COMPLET.sql          → Script unique d'init (régénéré automatiquement)
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
```

### Organisation du code — Backend

#### État actuel backend

```text
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

#### Tâches organisation backend

| # | Tâche | Réf | Effort | Statut |
| --- | ------- | ----- | -------- | -------- |
| H.6 | Découper routes volumineuses (>500 lignes) en sous-modules | O1 | M | ✅ jeux.py (2545L) → 4 fichiers (paris, loto, euromillions, dashboard) |
| H.7 | Auditer imports circulaires entre services | O2 | S | ✅ 21 modules testés — aucun import circulaire |
| H.8 | Unifier schémas Pydantic (`api/schemas/` pour API, `core/validation/` pour business) | O3 | M | ✅ Section ajoutée dans docs/PATTERNS.md |
| H.9 | Nommer tests de façon cohérente | O4 | S | ✅ Section ajoutée dans docs/TESTING_ADVANCED.md |
| H.10 | Déplacer scripts archivés (`split_famille.py`, `split_maison.py`) vers `scripts/archive/` | O5 | S | ✅ scripts/archive/ créé + 2 scripts déplacés |

### Organisation du code — Frontend

#### État actuel frontend

```text
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
│   ├── habitat/ (6)         ✅ Extraction Sprint H réalisée
│   ├── planning/ (3)        ✅ Extraction Sprint H réalisée
│   └── graphiques/ (3)      ✅
├── bibliotheque/api/ (25)   ✅ Clients API complets
├── crochets/ (13)           ✅ Hooks riches
├── magasins/ (4)            ✅ Stores Zustand
├── types/ (15)              ✅ TypeScript complet
└── fournisseurs/ (3)        ✅ Providers
```

#### Tâches organisation frontend

| # | Tâche | Réf | Effort | Statut |
| --- | ------- | ----- | -------- | -------- |
| H.11 | Extraire composants réutilisables habitat (3 → plus) | O6 | M | ✅ 3 nouveaux composants habitat extraits |
| H.12 | Extraire composants planning (timeline, week view, etc.) | O7 | M | ✅ 2 composants planning extraits |
| H.13 | Découper pages monolithiques (paramètres > 1200 lignes) | O8 | M | ✅ page paramètres découpée en sous-composants |
| H.14 | Tests unit frontend — plan complet hooks, stores, composants | O9 | L | ✅ Plan ajouté: docs/guides/FRONTEND_TEST_PLAN.md |

### Tâches documentation (Sprint H)

| # | Document | Réf | Priorité | Contenu attendu | Effort | Statut |
| --- | ---------- | ----- | ---------- | ----------------- | -------- | -------- |
| H.15 | Guide module IA Avancée | D1 | 🔴 | Les 14 outils IA, endpoints, prompts, cache, limites | M | ✅ docs/guides/IA_AVANCEE.md |
| H.16 | Guide intégration Sentry | D2 | 🟡 | Setup DSN, sampling, error boundaries, replay | S | ✅ docs/guides/SENTRY.md |
| H.17 | Guide Docker production | D3 | 🟡 | Railway-specific, performance tuning, scaling | M | ✅ docs/guides/DOCKER_PRODUCTION.md |
| H.18 | Design System visuel | D4 | 🟢 | Specs visuels composants (couleurs, spacing, typo) | M | ✅ docs/DESIGN_SYSTEM.md |
| H.19 | Guide contribution (CONTRIBUTING.md) | D5 | 🟡 | Conventions, PR process, code review | S | ✅ CONTRIBUTING.md |
| H.20 | Changelog technique Phase 10 | D6 | 🟡 | Détails techniques des innovations | S | ✅ CHANGELOG_PHASE10.md |
| H.21 | Guide PWA/Offline | D7 | 🟢 | Service Worker, cache strategies, sync | S | ✅ docs/guides/PWA_OFFLINE.md |
| H.22 | Schéma d'architecture Mermaid complet | D8 | 🟡 | Diagramme architectural à jour | M | ✅ Ajouté dans docs/ARCHITECTURE.md |
| H.23 | Rafraîchir ERD_SCHEMA.md (diagramme Mermaid 143 tables) | — | 🟡 | Régénérer le diagramme entité-relation | M | ✅ Sprint H metadata + procédure de refresh |
| H.24 | Enrichir SQLALCHEMY_SESSION_GUIDE.md (exemples 2.0+) | — | 🟢 | Exemples avancés SQLAlchemy 2.0 | S | ✅ Section FastAPI patterns ajoutée |

---

## Sprint I — Innovations long terme

**Objectif** : Transformations majeures de l'application — multi-utilisateurs, analytics, IA proactive

### Avancement Sprint I (lot du 31 mars 2026)

| # | Item | Statut | Livraison réalisée |
| --- | --- | --- | --- |
| I.8 | Thèmes saisonniers | ✅ Terminé | Ajout d'un thème saisonnier automatique via `data-saison` + tokens CSS saisonniers globaux |
| I.4 | Mode vocal complet | ⚠️ Partiel | Synthèse vocale intégrée sur les suggestions proactives (lecture/arrêt) |
| I.22 | Résumé vocal quotidien (TTS) | ⚠️ Partiel | Lecture vocale du briefing quotidien sur le hub Maison |
| I.27 | Comparateur recettes nutritionnel | ✅ Terminé | Nouvelle page `/ia-avancee/comparateur-recettes` (sélection 2 recettes + comparaison calories/macros) |
| I.10 | Raccourcis Google Assistant | ✅ Terminé (v2) | Mapping intents/actions + endpoint fulfillment `/assistant/google-assistant/webhook` + UI de test `/outils/google-assistant` |
| I.15 | Agent IA proactif | ✅ Terminé (v1) | Service `assistant_proactif` branché EventBus (météo/planning/budget/assistant) + endpoint lecture `/assistant/proactif/dernieres-suggestions` |
| I.31 | Cache sémantique embeddings | ✅ Terminé (v3 full + fallback) | Index vectoriel persistant avec embeddings externes Mistral (si dispo) + fallback local déterministe + filtrage ANN (signature+hamming) |

### Prochaine tranche Sprint I proposée

| # | Item | Action suivante | Effort |
| --- | --- | --- | --- |
| I.31 | Cache sémantique embeddings | Passer de l'approximation lexicale à de vrais embeddings vectoriels (store + ANN) | L |
| I.1 | Multi-utilisateurs & rôles famille | Étendre RBAC/permissions par profil (parent/enfant/invité) | XL |
| I.11 | Analytics familiales long terme | Construire tableaux de tendances multi-modules (nutrition, dépenses, énergie) | L |

### Innovations technologiques

| # | Tâche | Réf | Description | Impact | Effort |
| --- | ------- | ----- | ------------- | -------- | -------- |
| I.1 | Mode famille multi-utilisateurs | IN1 | Chaque membre a son profil avec rôles (parent, enfant, invité) | 🔴 Transformant | XL |
| I.2 | Synchronisation temps réel (WebSocket tous modules) | IN2 | Édition collaborative au-delà des courses | 🟡 Fort | L |
| I.3 | Widget smartphone (PWA natif) | IN3 | Widgets iOS/Android (courses du jour, prochaine tâche, météo) | 🟡 Fort | L |
| I.4 | Mode vocal complet | IN4 | "Hey Matanne, qu'est-ce qu'on mange ce soir ?" → TTS | 🟢 Innovation | L |
| I.5 | Scan & Go code-barres | IN5 | Scanner code-barres → inventaire + infos nutrition auto | 🟡 Fort | M |
| I.6 | Intégration IoT (capteurs maison) | IN6 | Température, humidité, consommation → dashboards | 🟢 Innovation | XL |
| I.7 | Mode déconnecté enrichi | IN8 | IndexedDB + background sync → fonctions de base hors-ligne | 🟡 Fort | XL |
| — | ~~Marketplace recettes~~ | ~~IN7~~ | ❌ **Rejeté** — Pas de volet social | — | — |

### Innovations UX

| # | Tâche | Réf | Description | Impact | Effort |
| --- | ------- | ----- | ------------- | -------- | -------- |
| I.8 | Thèmes saisonniers | IN9 | Interface s'adapte visuellement aux saisons | 🟢 Fun | S |
| I.9 | Gamification sportive uniquement | IN10 | Points/badges sur données Garmin/activité physique | 🟡 Fort | S |
| I.10 | Raccourcis Google Assistant | IN12 | Actions rapides via assistant vocal Google (tablette) | 🟢 Innovation | M |
| — | ~~QR code partage~~ | ~~IN13~~ | ❌ **Rejeté** — Aucun intérêt | — | — |

### Innovations Data & IA

| # | Tâche | Réf | Description | Impact | Effort |
| --- | ------- | ----- | ------------- | -------- | -------- |
| I.11 | Analytics familiales long terme | IN15 | Tendances nutrition, dépenses, activités, énergie → graphiques | 🔴 Transformant | L |
| I.12 | Prédictions ML | IN16 | Modèles prédictifs : courses, dépenses, pannes | 🟡 Fort | XL |
| I.13 | Benchmark famille anonyme | IN17 | Comparer habitudes avec moyennes nationales | 🟢 Innovation | L |
| I.14 | Intégration bancaire (Plaid/Bridge) | IN19 | Sync banque → dépenses auto-catégorisées | 🔴 Transformant | XL |
| I.15 | Agent IA proactif | IN20 | L'IA suggère des actions avant la demande ("Il fait beau, promenez-vous !") | 🟡 Fort | M |
| — | ~~Export Notion/Obsidian~~ | ~~IN18~~ | ❌ **Rejeté** — Pas d'intérêt | — | — |

### Nouvelles opportunités IA (services à développer)

| # | Opportunité | Réf | Module | Description | Effort |
| --- | ------------- | ----- | -------- | ------------- | -------- |
| I.16 | Nutritionniste IA | IA1 | Cuisine | Analyse nutrition hebdo → recommandations (protéines, fibres, vitamines) | M |
| I.17 | Coach budget IA | IA2 | Famille | Analyse tendances dépenses → suggestions économies + benchmarks | M |
| I.18 | Planificateur voyages IA | IA3 | Famille | Génération itinéraire + checklist + budget prévisionnel | L |
| I.19 | Diagnostic plante photo (vision IA) | IA4 | Maison | Upload photo plante → diagnostic maladie + traitement | M |
| I.20 | Optimiseur courses prédictif (ML) | IA5 | Courses | ML sur historique achats → liste courses pré-remplie | L |
| I.21 | Assistant vocal enrichi | IA6 | Outils | Commandes vocales → actions multi-modules | L |
| I.22 | Résumé vocal quotidien (TTS) | IA7 | Dashboard | TTS du briefing matinal → écoutable en voiture | M |
| I.23 | Styliste déco personnalisé | IA8 | Habitat | Analyse photos pièces → suggestions déco | L |
| I.24 | Prédicteur pannes (ML) | IA9 | Maison | ML sur âge/usage appareils → maintenance préventive | M |
| I.25 | Générateur menus événements | IA10 | Cuisine | Menu complet anniversaire/fête selon nb personnes + régimes | M |
| I.26 | Analyseur ticket de caisse (OCR) | IA11 | Famille | OCR ticket → catégorisation auto dépenses + promos | L |
| I.27 | Comparateur recettes nutritionnel | IA12 | Cuisine | Comparer 2 recettes → différences nutritionnelles visuelles | S |
| I.28 | Assistant devis travaux | IA13 | Maison | Description travaux → estimation prix + matériaux | M |
| I.29 | Coach routine bien-être | IA14 | Famille | Analyse habitudes → routines personnalisées selon Garmin | M |

### Architecture IA — Améliorations

| # | Amélioration | Description | Effort |
| --- | ------------- | ------------- | -------- |
| I.30 | Rate limit per-user (pas global) | Chaque utilisateur a son propre quota IA | M |
| I.31 | Cache sémantique enrichi (embeddings) | Matcher prompts similaires (pas juste hash exact) → -30-40% appels | L |
| I.32 | Fallback model | Si Mistral down → fallback Ollama ou autre provider (circuit breaker déjà en place) | M |
| I.33 | Feedback loop | Stocker retours thumbs up/down → améliorer prompts comme contexte | M |

---

## Référentiel Bugs

### 🔴 Critiques

| # | Problème | Fichier | Impact | Sprint |
| --- | ---------- | --------- | -------- | -------- |
| B1 | **5 blocs `except: pass` silencieux** dans webhook WhatsApp — erreurs avalées sans log | `src/api/routes/webhooks_whatsapp.py` (L621, 964, 984, 1008) | Messages WhatsApp perdus silencieusement | A.1 |
| B2 | **`except: pass`** dans endpoint auth — échec d'audit silencieux | `src/api/routes/auth.py` (L94) | Impossible de tracer les tentatives de login | A.2 |
| B3 | **`except: pass`** dans export PDF — erreur masquée | `src/api/routes/export.py` (L204) | Exports PDF échouent sans feedback | A.3 |
| B4 | **`except: pass`** dans préférences — sauvegarde silencieuse | `src/api/routes/preferences.py` (L285) | Préférences non sauvegardées sans erreur | A.4 |
| B5 | **Cache d'idempotence en mémoire** pour courses — incompatible multi-instance | `src/api/routes/courses.py` | Doublons possibles si plusieurs workers | A.11 |

### 🟡 Modérés

| # | Problème | Fichier | Impact | Sprint |
| --- | ---------- | --------- | -------- | -------- |
| B6 | **Pas de rate limiting sur endpoints admin** | `src/api/routes/admin.py` | Potentiel DoS sur actions admin sensibles | A.5 |
| B7 | **Rate limiting IA global** vs per-user — ambiguïté | `src/core/ai/rate_limit.py` | Un utilisateur peut consommer le quota de tous | A.6 |
| B8 | **CORS avec origines par défaut** — devrait être strict en prod | `src/api/main.py` | Risque CORS en production | A.7 |
| B9 | **Pas d'invalidation cache auto** quand modèles modifiés directement en DB | `src/core/caching/` | Données stales possibles après update direct | A.12 |
| B10 | **CSP avec `unsafe-inline`** pour scripts/styles dans `next.config.ts` | `frontend/next.config.ts` | Vulnérabilité XSS potentielle | A.13 |

### 🟢 Mineurs

| # | Problème | Impact | Sprint |
| --- | ---------- | -------- | -------- |
| B11 | Certaines pages frontend sans skeleton/loading pendant le fetch initial | UX dégradée (flash of empty content) | A.8 |
| B12 | WebSocket hooks — nettoyage on unmount à vérifier | Fuite mémoire potentielle | A.9 |
| B13 | Toast notifications auto-dismiss — pas extensible par l'utilisateur | Messages importants potentiellement ratés | A.14 |
| B14 | Pas de retry auto sur erreurs DB transitoires | Erreurs intermittentes non récupérées | A.15 |
| B15 | Auth WebSocket — documentation manquante sur la validation JWT | Confusion sur la sécurisation des WS | A.10 |

---

## Référentiel Gaps & Features manquantes

### Backend — Endpoints/Services manquants

| # | Gap | Module | Effort | Priorité |
| --- | ----- | -------- | -------- | ---------- |
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

| # | Page | État | Action requise | Sprint |
| --- | ------ | ------ | ---------------- | -------- |
| G11 | `/ia-avancee/suggestions-achats` | ✅ Fait | Cloture | C.1 |
| G12 | `/ia-avancee/diagnostic-plante` | ✅ Fait | Cloture | C.2 |
| G13 | `/ia-avancee/planning-adaptatif` | ✅ Fait | Cloture | C.3 |
| G14 | `/ia-avancee/analyse-photo` | ✅ Fait | Cloture | C.4 |
| G15 | `/ia-avancee/optimisation-routines` | ✅ Fait | Cloture | C.5 |
| G16 | `/ia-avancee/recommandations-energie` | ✅ Fait | Cloture | C.6 |
| G17 | `/ia-avancee/prevision-depenses` | ✅ Fait | Cloture | C.7 |
| G18 | `/ia-avancee/idees-cadeaux` | ✅ Fait | Cloture | C.8 |
| G19 | `/ia-avancee/analyse-document` | ✅ Fait | Cloture | C.9 |
| G20 | `/ia-avancee/estimation-travaux` | ✅ Fait | Cloture | C.10 |
| G21 | `/ia-avancee/planning-voyage` | ✅ Fait | Cloture | C.11 |
| G22 | `/ia-avancee/adaptations-meteo` | ✅ Fait | Cloture | C.12 |
| G23 | Error boundaries sur `planning`, `habitat`, `ia-avancee` | ✅ Fait | Cloture | C.15 |
| G24 | Loading states (skeletons) manquants sur pages hub | `planning`, `habitat`, `maison` sous-pages | Ajouter `loading.tsx` | A.8 |

### API Client ↔ Backend — Désalignements

| # | Problème | Action | Sprint |
| --- | ---------- | -------- | -------- |
| G25 | `ia_avancee.ts` est aligne sur les 14 outils du hub | ✅ Resolu | C.13 |
| G26 | Endpoints admin riches côté backend, frontend admin basique | ✅ Resolu (pages admin enrichies) | C.16 |
| G27 | RGPD (export/suppression données) — client existe mais pas de page dédiée | ✅ Resolu (section RGPD dans `/parametres`) | C.17 |

---

## Référentiel Consolidation SQL

### Problèmes identifiés

| # | Problème | Impact | Action | Sprint |
| --- | ---------- | -------- | -------- | -------- |
| S1 | **INIT_COMPLET.sql monolithique** (3000+ lignes) — difficile à naviguer | Maintenance | Découper en fichiers thématiques | H.1, H.2 |
| S2 | **Tables utilitaires orphelines** — `notes_memos`, `presse_papier_entrees`, `releves_energie` sans ORM complet | Données inaccessibles | Créer/compléter les modèles ORM | H.3 |
| S3 | **Pas de vérification auto** SQL ↔ ORM en CI | Dérives silencieuses possibles | Ajouter `test_schema_coherence.py` au CI | B.15 |
| S4 | **Indexes manquants** potentiels sur colonnes fréquemment filtrées | Performance | Audit des queries lentes | H.4 |
| S5 | **Migrations non versionnées** en dev — OK mais risque de conflits | Team dev | Documenter le workflow SQL-first | H.5 |

---

## Référentiel Couverture de tests

### Backend — Tests par couche

| Couche | Fichiers | Tests | Couverture | Cible | État |
| -------- | ---------- | ------- | ------------ | ------- | ------ |
| **Core** (config, DB, cache, decorators) | 12 fichiers | ~100 tests | 90% | 95% | ✅ Solide |
| **Modèles ORM** | 22 fichiers | ~80 tests | 70% | 85% | ⚠️ Partiel |
| **Routes API** | 30 fichiers | ~150 tests | 77% | 90% | ⚠️ 9 routes non testées |
| **Services** | 20+ fichiers | ~100 tests | 90% | 95% | ✅ Solide |
| **Spécialisés** (contrats, perf, SQL) | 5 fichiers | ~30 tests | Variable | — | ✅ |
| **Total Backend** | **70+ fichiers** | **~460 tests** | **~75%** | **85%** | ⚠️ |

### Routes API sans tests (9 routes)

| Route | Fichier | Priorité test | Sprint |
| ------- | --------- | --------------- | -------- |
| `dashboard` | `src/api/routes/dashboard.py` | 🔴 Haute | B.1 |
| `famille_jules` | `src/api/routes/famille_jules.py` | 🔴 Haute | B.2 |
| `famille_budget` | `src/api/routes/famille_budget.py` | 🟡 Moyenne | B.3 |
| `famille_activites` | `src/api/routes/famille_activites.py` | 🟡 Moyenne | B.4 |
| `maison_projets` | `src/api/routes/maison_projets.py` | 🟡 Moyenne | B.5 |
| `maison_jardin` | `src/api/routes/maison_jardin.py` | 🟡 Moyenne | B.6 |
| `maison_finances` | `src/api/routes/maison_finances.py` | 🟡 Moyenne | B.7 |
| `maison_entretien` | `src/api/routes/maison_entretien.py` | 🟡 Moyenne | B.8 |
| `partage` | `src/api/routes/partage.py` | 🟢 Basse | B.9 |

### Frontend — Couverture tests

| Type | Fichiers | Couverture | État |
| ------ | ---------- | ------------ | ------ |
| **Unit (Vitest)** | ~5 fichiers (stores + API clients) | Faible (~20%) | 🔴 À renforcer |
| **E2E (Playwright)** | 12 fichiers | Bonne (smoke tests) | ✅ |
| **Visual Regression** | 1 fichier | Basique | ⚠️ |

### Plan d'amélioration tests

```text
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

## Référentiel Documentation

### Documents existants — État

| Document | Statut | Notes |
| ---------- | -------- | ------- |
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

| # | Document manquant | Réf | Priorité | Contenu attendu | Sprint |
| --- | ------------------- | ----- | ---------- | ----------------- | -------- |
| D2 | **Guide intégration Sentry** | — | 🟡 Moyenne | Setup DSN, sampling, error boundaries, replay | H.16 |
| D3 | **Guide Docker production** | — | 🟡 Moyenne | Railway-specific, performance tuning, scaling | H.17 |
| D4 | **Design System visuel** | — | 🟢 Basse | Specs visuels composants (couleurs, spacing, typo) | H.18 |
| D5 | **Guide contribution** (CONTRIBUTING.md) | — | 🟡 Moyenne | Conventions, PR process, code review | H.19 |
| D6 | **Changelog technique Phase 10** | — | 🟡 Moyenne | Détails techniques des innovations | H.20 |
| D7 | **Guide PWA/Offline** | — | 🟢 Basse | Service Worker, cache strategies, sync | H.21 |
| D8 | **Schéma d'architecture Mermaid** complet | — | 🟡 Moyenne | Diagramme architectural à jour | H.22 |

### Guides modules — Couverture

| Module | Guide | État |
| -------- | ------- | ------ |
| 🍽️ Cuisine | `docs/guides/cuisine/README.md` + `batch_cooking.md` | ✅ Complet |
| 👶 Famille | `docs/guides/famille/README.md` | ✅ Complet |
| 🏡 Maison | `docs/guides/maison/README.md` | ✅ Complet |
| 📊 Dashboard | `docs/guides/dashboard/README.md` | ✅ Complet |
| 🎮 Jeux | `docs/guides/jeux/README.md` | ✅ Complet |
| 🛠️ Outils | `docs/guides/outils/README.md` | ✅ Complet |
| 📅 Planning | `docs/guides/planning/README.md` | ✅ Complet |
| 🏘️ Habitat | `docs/HABITAT_MODULE.md` | ✅ Complet |
| 🤖 IA Avancée | `docs/guides/ia-avancee/README.md` + `docs/guides/IA_AVANCEE.md` | ✅ Complet |
| ⚙️ Admin | `docs/ADMIN_GUIDE.md` | ✅ Complet |

---

## Référentiel Interactions intra-modules

### 🍽️ Cuisine (Recettes → Planning → Courses → Inventaire → Batch Cooking)

```text
Recettes ──planifier──→ Planning ──générer──→ Liste Courses
    │                      │                      │
    │                      ▼                      ▼
    │               Batch Cooking           Inventaire
    │                      │                      │
    └──versions jules──────┘──décrémenter stock──→┘
```

| Flux | État | Action |
| ------ | ------ | -------- |
| Recette → ajouter au planning | ✅ Implémenté | — |
| Planning → générer liste courses | ✅ Implémenté | — |
| Courses achetées → mettre à jour inventaire | ✅ Implémenté | — |
| Inventaire bas → suggestion recettes avec dispo | ⚠️ Partiel | Enrichir avec IA |
| Batch cooking → décrémenter stocks | ✅ Implémenté | — |
| Recette → version Jules (bébé) | ✅ Implémenté | — |
| Anti-gaspillage → suggestion recettes péremption | ✅ Implémenté | — |
| **MANQUANT** : Retour recette → ajuster suggestions futures | ❌ | Implémenter feedback loop IA (Sprint D.5) |
| **MANQUANT** : Historique repas → éviter répétitions | ⚠️ Partiel | Algorithme de diversité |

### 👶 Famille (Jules → Activités → Budget → Santé → Documents)

| Flux | État | Action |
| ------ | ------ | -------- |
| Profil Jules → suggestions activités par âge | ✅ Implémenté | — |
| Activités → suivi jalons développement | ✅ Implémenté | — |
| Budget famille → suivi dépenses | ✅ Implémenté | — |
| Anniversaires → rappels + budget cadeaux | ✅ Implémenté | — |
| Documents → alertes expiration | ✅ Implémenté | — |
| Voyages → checklists + budget | ✅ Implémenté | — |
| **MANQUANT** : Jalons Jules → cours/activités recommandés | ❌ | IA recommandation |
| **MANQUANT** : Budget → alertes seuil dépassement | ⚠️ Partiel | Notification push (Sprint D.3) |

### 🏡 Maison (Projets → Entretien → Jardin → Énergie → Stocks)

| Flux | État | Action |
| ------ | ------ | -------- |
| Projets → tâches → suivi avancement | ✅ Implémenté | — |
| Entretien préventif → calendrier tâches | ✅ Implémenté | — |
| Jardin → calendrier saisons → tâches | ✅ Implémenté | — |
| Stocks maison → alertes réapprovisionnement | ✅ Implémenté | — |
| Énergie → relevés compteurs → graphiques | ✅ Implémenté | — |
| **MANQUANT** : Entretien → devis artisans auto | ❌ | Lier artisans + estimations (Sprint D.12) |
| **MANQUANT** : Projets terminés → mise à jour valeur bien | ❌ | Impact habitat (Sprint D.11) |

### 🎮 Jeux (Paris → Loto → EuroMillions → Bankroll → Performance)

| Flux | État | Action |
| ------ | ------ | -------- |
| Analyse matchs → paris proposés | ✅ Implémenté | — |
| Backtest stratégies → scoring | ✅ Implémenté | — |
| Bankroll → suivi P&L | ✅ Implémenté | — |
| Stats historiques → heatmaps numéros | ✅ Implémenté | — |
| **MANQUANT** : Résultats auto → P&L instantané | ⚠️ Cron existe | Affichage temps réel |

---

## Référentiel Interactions inter-modules

### Flux existants (8 implémentés)

| # | Flux | Source → Cible | Fichier | Trigger |
| --- | ------ | ---------------- | --------- | --------- |
| 1 | Péremption → Recettes | Inventaire → Cuisine | `inter_module_peremption_recettes.py` | Job/API |
| 2 | Total courses → Budget | Courses → Famille | `inter_module_courses_budget.py` | Save courses |
| 3 | Document expire → Alerte | Famille → Notifications | `inter_module_documents_notifications.py` | Job J-30/15/7/1 |
| 4 | Chat IA → Multi-contexte | Tous → Utilitaires | `inter_module_chat_contexte.py` | Chat appel |
| 5 | Batch cooking → Stock | Cuisine → Inventaire | `inter_module_batch_inventaire.py` | Fin session |
| 6 | Anniversaires → Budget | Famille → Famille | `inter_module_anniversaires_budget.py` | Auto |
| 7 | Voyages → Budget | Voyages → Famille | `inter_module_voyages_budget.py` | Save voyage |
| 8 | Mises jeux → Budget | Jeux → Famille | `inter_module_budget_jeux.py` | Mise placée |

### Flux à implémenter (15 opportunités)

| # | Flux proposé | Source → Cible | Valeur | Effort | Sprint |
| --- | ------------- | ---------------- | -------- | -------- | -------- |
| I1 | **Récolte jardin → Recettes saison** (proposées au prochain planning semaine) | Maison/Jardin → Cuisine | 🔴 Haute | M | D.1 |
| I2 | **Garmin santé → Activités Jules** | Famille/Garmin → Famille/Jules | 🟡 Moyenne | M | D.8 |
| I3 | **Anomalie énergie → Tâche entretien** | Maison/Énergie → Maison/Entretien | 🔴 Haute | S | D.2 |
| I4 | **Budget dépassement → Alerte dashboard** | Famille/Budget → Dashboard | 🔴 Haute | S | D.3 |
| I5 | **Météo → Planning repas adapté** | Outils/Météo → Cuisine/Planning | 🟡 Moyenne | M | D.9 |
| I6 | **Météo → Tâches jardin urgentes** | Outils/Météo → Maison/Jardin | 🟡 Moyenne | S | D.10 |
| I7 | **Projets terminés → Valeur bien habitat** | Maison/Projets → Habitat | 🟡 Moyenne | M | D.11 |
| I8 | **Entretien artisan → Devis comparatif auto** | Maison/Entretien → Maison/Artisans | 🟡 Moyenne | M | D.12 |
| I9 | **Inventaire → Courses prédictives** | Inventaire → Courses | 🔴 Haute | L | D.4 |
| ~~I10~~ | ~~Résultats paris → P&L famille~~ | ~~Jeux → Famille/Budget~~ | ❌ **Rejeté** | — | — |
| I11 | **Routines santé → Briefing matinal** | Famille/Santé → Dashboard | 🟡 Moyenne | S | D.13 |
| I12 | **Anniversaire → Suggestion cadeau IA** | Famille → IA Avancée | 🟢 Innovation | M | D.14 |
| I13 | **Retour recette → Ajuster planning futur** | Cuisine → Planning | 🔴 Haute | M | D.5 |
| I14 | **Contrats maison → Alertes renouvellement** | Maison/Contrats → Notifications | 🟡 Moyenne | S | D.6 |
| I15 | **Score gamification → Récompenses famille** | Gamification → Famille | 🟢 Innovation | M | D.15 |

---

## Référentiel Opportunités IA

### Services IA existants (23 services)

| Service | Module | Fonctionnalité |
| --------- | -------- | ---------------- |
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

| # | Opportunité | Module | Description | Effort | Sprint |
| --- | ------------- | -------- | ------------- | -------- | -------- |
| IA1 | **Nutritionniste IA** | Cuisine | Analyse nutrition hebdo → recommandations (protéines, fibres, vitamines) | M | I.16 |
| IA2 | **Coach budget IA** | Famille | Analyse tendances dépenses → suggestions économies + benchmarks | M | I.17 |
| IA3 | **Planificateur voyages IA** | Famille | Génération itinéraire + checklist + budget prévisionnel | L | I.18 |
| IA4 | **Diagnostic plante photo** | Maison | Upload photo plante → diagnostic maladie + traitement (vision IA) | M | I.19 |
| IA5 | **Optimiseur courses prédictif** | Courses | ML sur historique achats → liste courses pré-remplie | L | I.20 |
| IA6 | **Assistant vocal enrichi** | Outils | Commandes vocales → actions multi-modules | L | I.21 |
| IA7 | **Résumé vocal quotidien** | Dashboard | TTS du briefing matinal → écoutable en voiture | M | I.22 |
| IA8 | **Styliste déco personnalisé** | Habitat | Analyse photos pièces → suggestions déco personnalisées | L | I.23 |
| IA9 | **Prédicteur pannes** | Maison | ML sur âge/usage appareils → maintenance préventive | M | I.24 |
| IA10 | **Générateur menus événements** | Cuisine | Menu complet anniversaire/fête selon nb personnes + régimes | M | I.25 |
| IA11 | **Analyseur ticket de caisse** | Famille | OCR ticket → catégorisation auto dépenses + promos | L | I.26 |
| IA12 | **Comparateur recettes nutritionnel** | Cuisine | Comparer 2 recettes → différences nutritionnelles visuelles | S | I.27 |
| IA13 | **Assistant devis travaux** | Maison | Description travaux → estimation prix + matériaux | M | I.28 |
| IA14 | **Coach routine bien-être** | Famille | Analyse habitudes → routines personnalisées selon Garmin | M | I.29 |

### Architecture IA — Améliorations suggérées

```text
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

## Référentiel Jobs CRON

### Jobs existants (38+ planifiés)

#### Rappels & Alertes

| Job | Schedule | Description | Canal |
| ----- | ---------- | ------------- | ------- |
| `rappels_famille` | 7h00 | Rappels activités/RDV du jour | push, ntfy |
| `rappels_maison` | 8h00 | Tâches entretien du jour | push, ntfy |
| `alertes_peremption_48h` | 6h00 | Produits expirant dans 48h | push, ntfy |
| `alertes_stocks_bas` | Lun 9h | Stocks sous seuil | push |
| `rappels_documents_expirants` | 8h30 | Documents J-30/15/7/1 | push, email |
| `rappels_vaccins` | 8h15 | Vaccins à planifier | push, email |
| `alertes_contrats` | 8h45 | Contrats à renouveler | push, email |

#### Notifications & Digests

| Job | Schedule | Description | Canal |
| ----- | ---------- | ------------- | ------- |
| `push_quotidien` | 9h00 | Push quotidien résumé | push |
| `digest_ntfy` | 9h00 | Digest via ntfy | ntfy |
| `digest_whatsapp_matinal` | 7h30 | Briefing matinal WhatsApp | whatsapp |
| `digest_email_hebdo` | Lun 8h | Digest email hebdomadaire | email |
| `digest_notifications_queue` | /2h | Flush file de notifications | multi |

#### Rapports & Résumés

| Job | Schedule | Description |
| ----- | ---------- | ------------- |
| `resume_hebdo` | Lun 7h30 | Résumé hebdo IA narratif |
| `rapport_mensuel_budget` | 1er 8h15 | Bilan budget mensuel |
| `rapport_jardin` | Mer 20h | Rapport jardin hebdo |
| `bilan_mensuel_complet` | 1er 9h | Bilan multi-module |
| `score_weekend` | Ven 17h | Score préparation weekend |

#### Syncs & Scraping

| Job | Schedule | Description |
| ----- | ---------- | ------------- |
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
| ----- | ---------- | ------------- |
| `nettoyage_cache` | 3h | Purge cache périmé |
| `nettoyage_logs` | 4h | Rotation logs anciens |
| `automations_runner` | /5min | Exécution automations If→Then |
| `health_check_services` | /15min | Vérification santé services |
| `backup_etats_persistants` | 2h | Sauvegarde états |

### Jobs CRON à ajouter (8 propositions)

| # | Job proposé | Schedule | Description | Priorité | Sprint |
| --- | ------------- | ---------- | ------------- | ---------- | -------- |
| C1 | `prediction_courses_hebdo` | Dim 18h | Générer liste courses prédictive pour la semaine | 🔴 | E.9 |
| C2 | `rapport_energie_mensuel` | 1er 10h | Rapport conso énergie + comparaison mois précédent | 🟡 | E.10 |
| C3 | `suggestions_recettes_saison` | 1er et 15 6h | Nouvelles recettes de saison à découvrir | 🟡 | E.11 |
| C4 | `audit_securite_hebdo` | Dim 2h | Vérification intégrité données + logs suspects | 🟡 | E.12 |
| C5 | `nettoyage_notifications_anciennes` | Dim 4h | Purger notifications > 90 jours | 🟢 | E.13 |
| C6 | `mise_a_jour_scores_gamification` | Minuit | Recalculer scores/badges quotidiens | 🟡 | E.14 |
| C7 | `alerte_meteo_jardin` | 7h | Alerte gel/canicule → protéger plantes | 🟡 | E.15 |
| C8 | `resume_financier_semaine` | Ven 18h | Résumé dépenses de la semaine | 🟡 | E.16 |

---

## Référentiel Notifications

### Architecture

```text
DispatcherNotifications (central)
├── ntfy.sh        → REST API → push notifications
├── Web Push       → VAPID protocol → navigateur
├── Email          → Resend API → Jinja2 templates
└── WhatsApp       → Meta Cloud API → webhook bidirectionnel
```

### État par canal

| Canal | État | Fonctionnalités | Manques |
| ------- | ------ | ----------------- | --------- |
| **ntfy** | ✅ Opérationnel | Push simple, digest | — |
| **Web Push** | ✅ Opérationnel | Abonnement VAPID, notifications navigateur | Tests E2E push |
| **Email** | ✅ Opérationnel | 7 templates Jinja2 (reset pwd, vérif, digest, rapport, alerte, invitation, digest) | Template personnalisation |
| **WhatsApp** | ✅ Opérationnel | Webhook Meta, boutons interactifs (planning valider/modifier/régénérer) | Conversations enrichies |

### Améliorations proposées

| # | Amélioration | Canal | Description | Effort | Sprint |
| --- | ------------- | ------- | ------------- | -------- | -------- |
| N1 | **WhatsApp : Flux courses** | WhatsApp | "Voici ta liste courses de la semaine" + bouton "Ajouter au panier" | M | E.1 |
| N2 | **WhatsApp : Rappel activité Jules** | WhatsApp | "C'est l'heure de l'activité de Jules!" + suggestion | S | E.2 |
| N3 | **WhatsApp : Résultats paris** | WhatsApp | "Match terminé : Paris SG 2-1 → Tu as gagné !" | S | E.3 |
| N4 | **WhatsApp : Mode conversationnel** | WhatsApp | État machine plus riche — gestion multi-étapes | L | Backlog |
| N5 | **Email : Newsletter hebdo** | Email | Template riche avec images, graphiques inline, call-to-action | M | E.6 |
| N6 | **Email : Rapport budget PDF** | Email | PDF en pièce jointe (déjà généré, ajouter l'envoi) | S | E.7 |
| N7 | **Push : Actions rapides** | Push | Notifications avec boutons d'action (ex: "Valider" / "Reporter") | M | E.8 |
| ~~N8~~ | ~~Push : Géolocalisation~~ | ~~Push~~ | ❌ **Rejeté** (habite à côté du supermarché) | — | — |
| N9 | **Préférences granulaires** | Tous | UI pour choisir par type d'événement quel canal utiliser | M | E.4 |
| N10 | **Historique notifications** | Tous | Page "Centre de notifications" dans l'app | M | E.5 |

---

## Référentiel Mode Admin

### Fonctionnalités existantes

| Feature | Endpoint | État |
| --------- | ---------- | ------ |
| Liste jobs | `GET /api/v1/admin/jobs` | ✅ |
| Trigger manuel | `POST /api/v1/admin/jobs/{id}/run` | ✅ (rate limit 5/min) |
| Dry run | `POST /api/v1/admin/jobs/{id}/run?dry_run=true` | ✅ |
| Logs jobs | `GET /api/v1/admin/jobs/{id}/logs` | ✅ |
| Audit logs | `GET /api/v1/admin/audit-logs` | ✅ |
| Stats audit | `GET /api/v1/admin/audit-stats` | ✅ |
| Export audit CSV | `GET /api/v1/admin/audit-export` | ✅ |
| Health check services | `GET /api/v1/admin/services/health` | ✅ |
| Test notifications | `POST /api/v1/admin/notifications/test` | ✅ |
| Stats cache | `GET /api/v1/admin/cache/stats` | ✅ |
| Purge cache | `POST /api/v1/admin/cache/clear` | ✅ |
| Liste users | `GET /api/v1/admin/users` | ✅ |
| Désactiver user | `POST /api/v1/admin/users/{id}/disable` | ✅ |
| Cohérence DB | `GET /api/v1/admin/db/coherence` | ✅ |
| Feature flags | `GET/PUT /api/v1/admin/feature-flags` | ✅ |
| Runtime config | `GET/PUT /api/v1/admin/config` | ✅ |
| Flow simulator | `POST /api/v1/admin/simulate-flow` | ✅ |

### Améliorations admin proposées

| # | Amélioration | Description | Effort | Priorité | Sprint |
| --- | ------------- | ------------- | -------- | ---------- | -------- |
| A1 | **Dashboard admin d�di�** | Graphiques : jobs ex�cut�s, erreurs, usage IA, notifications | M | ?? | F.1 |
| A2 | **Console IA admin** | Tester un prompt IA directement depuis l'admin ? voir r�ponse brute | S | ?? | F.2 |
| A3 | **Seed data one-click** | Bouton pour peupler la DB avec donn�es de test (dev only) | S | ?? | F.3 |
| A4 | **Reset module** | Bouton pour vider les donn�es d'un module sp�cifique (dev only) | S | ?? | F.8 |
| A5 | **Export DB complet** | Export JSON/SQL complet de toutes les donn�es utilisateur | M | ?? | F.9 |
| A6 | **Import DB** | Import JSON/SQL pour restaurer un backup | M | ?? | F.10 |
| A7 | **Monitoring temps r�el** | WebSocket admin ? m�triques live (requ�tes/s, erreurs, cache hits) | L | ?? | F.11 |
| A8 | **Queue de notifications** | Voir et g�rer la file d'attente des notifications pendantes | S | ?? | F.6 |
| A9 | **Historique jobs paginated** | Vue pagin�e de tous les runs de jobs avec filtres | M | ?? | F.7 |
| A10 | **Toggle maintenance mode** | Activer un mode maintenance avec bandeau utilisateur | S | ?? | F.5 |

---

## Référentiel Simplification UX

### Flux à simplifier (10 améliorations)

| # | Flux actuel | Problème | Flux proposé | Effort | Sprint |
| --- | ------------- | ---------- | -------------- | -------- | -------- |
| U1 | **Planifier repas** : Planning → Jour → Recette → Sélectionner | 4 clics minimum | **1 clic** : "Planifier ma semaine" → IA génère → Valider/ajuster | S | G.1 |
| U2 | **Ajouter aux courses** : Courses → Créer liste → Ajouter un par un | Fastidieux | **Auto** : Depuis planning → "Générer courses" → Liste pré-remplie | S | G.2 |
| U3 | **Consulter dépenses** : Famille → Budget → Filtrer → Lire | Dispersé | **Dashboard** : Widget budget avec tendance en page d'accueil | S | G.3 |
| U4 | **Trouver recette** : Cuisine → Recettes → Filtres → Parcourir | Long | **Recherche globale** : Barre de recherche → résultats instantanés | M | G.4 |
| U5 | **Créer projet maison** : Maison → Projets → Formulaire complet | Formulaire lourd | **Wizard 3 étapes** : Nom → Type/Budget → Tâches IA | M | G.5 |
| U6 | **Vérifier inventaire** : Cuisine → Inventaire → Parcourir | Pas intuitif | **Alertes proactives** : Notif quand stock bas → action directe | S | G.6 |
| U7 | **Suivre Jules** : Famille → Jules → Onglets multiples | Complexe | **Timeline Jules** : Vue chronologique unique jalons + activités + santé | M | G.7 |
| U8 | **Gérer entretien** : Maison → Entretien → Voir → Marquer | Pas engageant | **Checklist du jour** : Widget dashboard + swipe pour valider | S | G.8 |
| U9 | **Consulter météo** : Outils → Météo → Page dédiée | Détour | **Widget intégré** : Météo dans header/dashboard + suggestions adaptées | S | G.9 |
| U10 | **Paramétrer notifs** : Paramètres → Notifications → Toggle | Granularité floue | **Par module** : "Me notifier pour..." dans chaque module | M | G.10 |

### Composants UX à ajouter

| # | Composant | Description | Impact | Sprint |
| --- | ----------- | ------------- | -------- | -------- |
| UX1 | **Quick Actions FAB** (enrichir) | Bouton flottant avec actions rapides contextuelles | Navigation rapide | G.13 |
| UX2 | **Command Palette** (enrichir) | `Cmd+K` naviguer/agir partout (`menu-commandes.tsx`) | Power users | G.14 |
| UX3 | **Onboarding tour** (améliorer) | Tour guidé au premier lancement (`tour-onboarding.tsx`) | Découvrabilité | G.15 |
| UX4 | **Empty states riches** | Module vide → message + CTA pour commencer | Engagement | G.16 |
| UX5 | **Skeleton screens** (compléter) | Loading skeletons sur toutes les pages | UX perçue | G.17 |
| UX6 | **Swipe gestures mobile** (généraliser) | Swipe gauche/droite sur items de liste | Mobile fluide | G.18 |
| UX7 | **Cards drag & drop** | Réorganisation widgets dashboard (`grille-widgets.tsx`) | Personnalisation | G.19 |
| UX8 | **Confirmations inline** | Toasts au lieu de modals pour actions simples | Moins intrusif | G.20 |

---

## Référentiel Organisation du code

### Backend — Points d'amélioration

| # | Problème | Action | Effort | Sprint |
| --- | ---------- | -------- | -------- | -------- |
| O1 | **Routes volumineuses** — certains fichiers > 500 lignes | Découper en sous-modules | M | H.6 |
| O2 | **Imports circulaires potentiels** entre services | Auditer avec `importlib` ou `pylint` | S | H.7 |
| O3 | **Schémas Pydantic dupliqués** entre `api/schemas/` et `core/validation/schemas/` | Unifier les responsabilités | M | H.8 |
| O4 | **Tests dispersés** — nommage incohérent | Nommer de façon cohérente | S | H.9 |
| O5 | **Scripts archivés** toujours présents | Déplacer vers `scripts/archive/` | S | H.10 |

### Frontend — Points d'amélioration

| # | Problème | Action | Effort | Sprint |
| --- | ---------- | -------- | -------- | -------- |
| O6 | **Composants habitat insuffisants** — 3 composants pour un module riche | Extraire composants réutilisables | M | H.11 |
| O7 | **Composants planning insuffisants** — 1 seul composant calendrier | Extraire timeline, week view, etc. | M | H.12 |
| O8 | **Pages monolithiques** — paramètres > 1200 lignes | Découper en composants nommés | M | H.13 |
| O9 | **Tests unit frontend** — seulement ~5 fichiers | Plan de test complet | L | H.14 |
| O10 | **Pas de storybook** — composants UI non documentés visuellement | Optionnel mais recommandé | L | Backlog |

---

## Référentiel Axes d'innovation

### Catalogue innovations technologiques

| # | Innovation | Description | Impact | Effort | Sprint |
| --- | ----------- | ------------- | -------- | -------- | -------- |
| IN1 | **Mode famille multi-utilisateurs** | Chaque membre a son profil avec rôles (parent, enfant, invité) | 🔴 Transformant | XL | I.1 |
| IN2 | **Synchronisation temps réel** | WebSocket tous modules (pas juste courses) → édition collaborative | 🟡 Fort | L | I.2 |
| IN3 | **Widget smartphone** | Widgets iOS/Android natifs via PWA | 🟡 Fort | L | I.3 |
| IN4 | **Mode vocal complet** | "Hey Matanne, qu'est-ce qu'on mange ce soir ?" → TTS | 🟢 Innovation | L | I.4 |
| IN5 | **Scan & Go** | Scanner code-barres → inventaire + infos nutrition auto | 🟡 Fort | M | I.5 |
| IN6 | **Intégration IoT** | Capteurs maison (température, humidité, consommation) → dashboards | 🟢 Innovation | XL | I.6 |
| ~~IN7~~ | ~~Marketplace recettes~~ | ❌ **Rejeté** (pas de volet social) | — | — | — |
| IN8 | **Mode déconnecté enrichi** | IndexedDB + background sync → fonctions de base hors-ligne | 🟡 Fort | XL | I.7 |

### Catalogue innovations UX

| # | Innovation | Description | Impact | Effort | Sprint |
| --- | ----------- | ------------- | -------- | -------- | -------- |
| IN9 | **Thèmes saisonniers** | Interface s'adapte visuellement aux saisons | 🟢 Fun | S | I.8 |
| IN10 | **Gamification sportive uniquement** | Points/badges sur données Garmin/activité physique | 🟡 Fort | S | I.9 |
| IN11 | **Mode focus** | Vue épurée "essentiel du jour" : 1 écran = météo + repas + tâches + rappels | 🔴 Transformant | M | G.11 |
| IN12 | **Raccourcis Google Assistant** | Actions rapides via assistant vocal Google (tablette) | 🟢 Innovation | M | I.10 |
| ~~IN13~~ | ~~QR code partage~~ | ❌ **Rejeté** (aucun intérêt) | — | — | — |
| IN14 | **Mode vacances** | Pause notifications non essentielles + checklist voyage auto | 🟡 Fort | S | G.12 |

### Catalogue innovations Data & IA

| # | Innovation | Description | Impact | Effort | Sprint |
| --- | ----------- | ------------- | -------- | -------- | -------- |
| IN15 | **Analytics familiales** | Tendances long terme : nutrition, dépenses, activités, énergie → graphiques | 🔴 Transformant | L | I.11 |
| IN16 | **Prédictions ML** | Modèles prédictifs : courses, dépenses, pannes | 🟡 Fort | XL | I.12 |
| IN17 | **Benchmark famille** | Comparer (anonymement) ses habitudes avec moyennes nationales | 🟢 Innovation | L | I.13 |
| ~~IN18~~ | ~~Export Notion/Obsidian~~ | ❌ **Rejeté** (pas d'intérêt) | — | — | — |
| IN19 | **Intégration bancaire** | Sync banque via API (Plaid/Bridge) → dépenses auto-catégorisées | 🔴 Transformant | XL | I.14 |
| IN20 | **Agent IA proactif** | L'IA suggère des actions avant la demande | 🟡 Fort | M | I.15 |

---

## Annexes

### A. Inventaire complet des fichiers

| Dossier | Fichiers Python | Fichiers TS/TSX | Total |
| --------- | ---------------- | ----------------- | ------- |
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
| --------- | ------ | ---------- |
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

### E. Décisions rejetées (historique)

| Proposition | Raison du rejet |
| ------------- | ----------------- |
| N8 : Push géolocalisation | Habite à côté du supermarché |
| IN7 : Marketplace recettes | Pas de volet social/communautaire |
| IN10 : Gamification familiale générale | Limité au sport/Garmin uniquement |
| IN13 : QR code partage | Aucun intérêt |
| IN18 : Export Notion/Obsidian | Pas d'intérêt |
| I10 : Résultats paris → P&L famille | Budget jeux volontairement séparé |
| Jeu responsable | Feature entièrement supprimée du codebase |

### F. Précisions acceptées

| Proposition | Précision |
| ------------- | ----------- |
| I1 : Récolte jardin → Recettes | Uniquement à la prochaine semaine planifiée |
| IN12 : Assistant vocal | Google Assistant uniquement (pas Siri — tablette Google) |

---

> **Ce document est le plan d'exécution officiel basé sur l'ANALYSE_COMPLETE.md du 30 mars 2026.**  
> Chaque sprint doit mettre à jour ce document après complétion (cocher les tâches, ajouter les dates).  
> Les référentiels servent de source de vérité pour le contexte de chaque tâche.
