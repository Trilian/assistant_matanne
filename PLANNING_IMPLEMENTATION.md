# ðŸ“‹ PLANNING D'IMPLÃ‰MENTATION â€” Assistant Matanne

> **BasÃ© sur** : ANALYSE_COMPLETE.md (audit 360Â° du 30 mars 2026)  
> **Objectif** : Plan d'exÃ©cution dÃ©taillÃ© avec toutes les tÃ¢ches, priorisÃ©es et organisÃ©es en sprints  
> **LÃ©gende efforts** : S = Â½ journÃ©e | M = 1-2 jours | L = 3-5 jours | XL = 1-2 semaines

---

## ðŸ“Š Tableau de bord projet â€” Ã‰tat de rÃ©fÃ©rence

| CatÃ©gorie | MÃ©trique | Ã‰tat |
| ----------- | ---------- | ------ |
| **Tables SQL** | 143 tables, RLS, triggers, views | âœ… Solide |
| **ModÃ¨les ORM** | 31 fichiers, ~95% alignÃ©s SQL | âœ… |
| **Endpoints API** | 242+ endpoints REST (42 routers) | âœ… |
| **Services** | 60+ services (23 IA) | âœ… |
| **Pages Frontend** | 103 pages (App Router) | âš ï¸ ~12 pages IA incomplÃ¨tes |
| **Composants** | 105+ composants React | âœ… |
| **Tests Backend** | 70+ fichiers pytest | âš ï¸ 9 routes non testÃ©es |
| **Tests Frontend** | 12 E2E + ~5 unit tests | âš ï¸ Couverture unit faible |
| **Documentation** | 34 docs + 8 guides modules (Sprint H : +8 docs) | âœ… 95% Ã  jour |
| **Jobs CRON** | 38+ jobs APScheduler | âœ… OpÃ©rationnel |
| **Notifications** | 4 canaux (push/email/WhatsApp/ntfy) | âœ… |
| **PWA** | Service Worker + manifest + offline | âœ… |

---

## Table des matiÃ¨res

1. [Vue d'ensemble des phases](#vue-densemble-des-phases)
2. [Sprint A â€” Corrections critiques](#sprint-a-a-corrections-critiques)
3. [Sprint B â€” Tests manquants](#sprint-b-a-tests-manquants)
4. [Sprint C â€” Pages IA AvancÃ©e](#sprint-c-a-pages-ia-avancae)
5. [Sprint D â€” Inter-modules & Event Bus](#sprint-d-a-inter-modules-and-event-bus)
6. [Sprint E â€” Notifications enrichies](#sprint-e-a-notifications-enrichies)
7. [Sprint F â€” Admin & DX](#sprint-f-a-admin-and-dx)
8. [Sprint G â€” UX & Simplification flux](#sprint-g-a-ux-and-simplification-flux)
9. [Sprint H â€” Consolidation SQL & Organisation code](#sprint-h-a-consolidation-sql-and-organisation-code)
10. [Sprint I â€” Innovations long terme](#sprint-i-a-innovations-long-terme)
11. [RÃ©fÃ©rentiel Bugs](#rafarentiel-bugs)
12. [RÃ©fÃ©rentiel Gaps & Features manquantes](#rafarentiel-gaps-and-features-manquantes)
13. [RÃ©fÃ©rentiel Consolidation SQL](#rafarentiel-consolidation-sql)
14. [RÃ©fÃ©rentiel Couverture de tests](#rafarentiel-couverture-de-tests)
15. [RÃ©fÃ©rentiel Documentation](#rafarentiel-documentation)
16. [RÃ©fÃ©rentiel Interactions intra-modules](#rafarentiel-interactions-intra-modules)
17. [RÃ©fÃ©rentiel Interactions inter-modules](#rafarentiel-interactions-inter-modules)
18. [RÃ©fÃ©rentiel OpportunitÃ©s IA](#rafarentiel-opportunitas-ia)
19. [RÃ©fÃ©rentiel Jobs CRON](#rafarentiel-jobs-cron)
20. [RÃ©fÃ©rentiel Notifications](#rafarentiel-notifications)
21. [RÃ©fÃ©rentiel Mode Admin](#rafarentiel-mode-admin)
22. [RÃ©fÃ©rentiel Simplification UX](#rafarentiel-simplification-ux)
23. [RÃ©fÃ©rentiel Organisation du code](#rafarentiel-organisation-du-code)
24. [RÃ©fÃ©rentiel Axes d'innovation](#rafarentiel-axes-dinnovation)
25. [Annexes](#annexes)

---

## Phase 0 â€” Vue d'ensemble

### Ordre d'exÃ©cution des sprints

```
PRIORITÃ‰ CRITIQUE (qualitÃ© & stabilitÃ©)
  Sprint A â”€â”€ Corrections critiques          â†’ âœ… TERMINÃ‰ (30 mars 2026)
  Sprint B â”€â”€ Tests manquants                â†’ âœ… IMPLÃ‰MENTÃ‰ (phase 1: backend + unit + CI)

PRIORITÃ‰ HAUTE (fonctionnalitÃ©s core)
  Sprint C â”€â”€ Pages IA AvancÃ©e               â†’ âœ… TERMINE (31 mars 2026, 14 outils)
  Sprint D â”€â”€ Inter-modules & Event Bus      â†’ 7 flux majeurs

PRIORITÃ‰ MOYENNE (enrichissement)
  Sprint E â”€â”€ Notifications enrichies        â†’ WhatsApp + centre notif
  Sprint F â”€â”€ Admin & DX                     â†’ Dashboard admin + outils
  Sprint G â”€â”€ UX & Simplification flux       â†’ 10 flux simplifiÃ©s

PRIORITÃ‰ BASSE (consolidation & innovation)
  Sprint H â”€â”€ Consolidation SQL & Code       â†’ Organisation + docs
  Sprint I â”€â”€ Innovations long terme         â†’ Multi-users, analytics, IA proactif
```

### Matrice de dÃ©pendances

```
Sprint A â†’ (aucune dÃ©pendance, lancer en premier)
Sprint B â†’ Sprint A (valider les corrections)
Sprint C â†’ Sprint A (bugs corrigÃ©s avant nouvelles features)
Sprint D â†’ Sprint C (pages IA existantes pour les flux inter-modules)
Sprint E â†’ Sprint D (Ã©vÃ©nements bus pour dÃ©clencher les notifications)
Sprint F â†’ Sprint A (admin rate limiting corrigÃ©)
Sprint G â†’ Sprint C + Sprint E (pages + notifications prÃªtes)
Sprint H â†’ indÃ©pendant (peut Ãªtre parallÃ©lisÃ©)
Sprint I â†’ Sprint D + Sprint G (base fonctionnelle stable)
```

---

## Sprint A â€” Corrections critiques (bugs + qualitÃ©) âœ… TERMINÃ‰

**Objectif** : Stabiliser la base de code â€” aucun bug silencieux, sÃ©curitÃ© durcie
**Date de complÃ©tion** : 30 mars 2026

| # | TÃ¢che | RÃ©f | Effort | Fichier(s) concernÃ©(s) | Checklist |
| --- | ------- | ----- | -------- | ------------------------ | ----------- |
| A.1 | Corriger les 4 blocs `except: pass` silencieux dans webhook WhatsApp | B1 | S | `src/api/routes/webhooks_whatsapp.py` (L621, 964, 984, 1008) | âœ… RemplacÃ© par `except Exception as e: logger.error/warning(...)` |
| A.2 | Corriger `except: pass` dans endpoint auth â€” Ã©chec d'audit silencieux | B2 | S | `src/api/routes/auth.py` (L94) | âœ… Ajout `logger.debug()` sur conversion int Ã©chouÃ©e |
| A.3 | Corriger `except: pass` dans export PDF | B3 | S | `src/api/routes/export.py` (L204) | âœ… Ajout `logger.warning()` sur content-type inattendu |
| A.4 | Corriger `except: pass` dans prÃ©fÃ©rences | B4 | S | `src/api/routes/preferences.py` (L285) | âœ… Ajout `logger.warning()` sur format time invalide |
| A.5 | Ajouter rate limiting sur endpoints admin | B6 | S | `src/api/routes/admin.py` | âœ… Rate limit router-level 10 req/min via `_verifier_limite_admin` dependency |
| A.6 | ImplÃ©menter rate limiting IA per-user (pas global) | B7 | M | `src/core/ai/rate_limit.py` | âœ… Quota par user_id âœ… Compteur par user âœ… `peut_appeler(user_id)` + `enregistrer_appel(..., user_id)` |
| A.7 | CORS strict en production (pas de wildcard) | B8 | S | `src/api/main.py` | âœ… Conditionnel ENVIRONMENT âœ… Warning si CORS_ORIGINS absent en prod/staging âœ… Origins vides par dÃ©faut en prod |
| A.8 | Ajouter skeletons/loading sur toutes les pages hub | B11, G24 | M | `frontend/src/app/(app)/*/loading.tsx` | âœ… habitat âœ… ia-avancee (planning et maison dÃ©jÃ  existants) |
| A.9 | VÃ©rifier nettoyage WebSocket hooks on unmount | B12 | S | `frontend/src/crochets/` | âœ… Audit OK â€” cleanup correct dans `utiliser-websocket.ts` et `utiliser-websocket-courses.ts` |
| A.10 | Documenter auth WebSocket (validation JWT) | B15 | S | `docs/ARCHITECTURE.md` | âœ… Section Â« Authentification WebSocket Â» ajoutÃ©e dans ARCHITECTURE.md |

### TÃ¢ches diffÃ©rÃ©es (moyen terme)

| # | TÃ¢che | RÃ©f | Effort | Notes |
| --- | ------- | ----- | -------- | ------- |
| A.11 | Cache d'idempotence courses â†’ Redis ou DB au lieu de mÃ©moire | B5 | M | Multi-worker safe |
| A.12 | Invalidation cache auto quand modÃ¨les modifiÃ©s en DB | B9 | M | Trigger PostgreSQL â†’ invalidation |
| A.13 | CSP strict (retirer `unsafe-inline`) dans `next.config.ts` | B10 | M | Nonce-based CSP |
| A.14 | Toast notifications extensibles par l'utilisateur | B13 | S | Bouton "Voir plus" |
| A.15 | Retry auto sur erreurs DB transitoires | B14 | S | `tenacity` ou retry dans `avec_session_db` |

---

## Sprint B â€” Tests manquants âœ… IMPLÃ‰MENTÃ‰ (phase 1)

**Objectif** : Couverture backend 75% â†’ 85%, initier les tests unit frontend
**Date de complÃ©tion (phase 1)** : 31 mars 2026

### Backend â€” Routes API sans tests (9 routes)

| # | TÃ¢che | Route | Fichier test | PrioritÃ© | Effort | Statut |
| --- | ------- | ------- | -------------- | ---------- | -------- | -------- |
| B.1 | Tests route dashboard | `dashboard` | `tests/api/test_routes_dashboard.py` | ðŸ”´ | M | âœ… |
| B.2 | Tests route famille_jules | `famille_jules` | `tests/api/test_routes_famille_jules.py` | ðŸ”´ | M | âœ… |
| B.3 | Tests route famille_budget | `famille_budget` | `tests/api/test_routes_famille_budget.py` | ðŸŸ¡ | M | âœ… |
| B.4 | Tests route famille_activites | `famille_activites` | `tests/api/test_routes_famille_activites.py` | ðŸŸ¡ | M | âœ… |
| B.5 | Tests route maison_projets | `maison_projets` | `tests/api/test_routes_maison_projets.py` | ðŸŸ¡ | M | âœ… |
| B.6 | Tests route maison_jardin | `maison_jardin` | `tests/api/test_routes_maison_jardin.py` | ðŸŸ¡ | M | âœ… |
| B.7 | Tests route maison_finances | `maison_finances` | `tests/api/test_routes_maison_finances.py` | ðŸŸ¡ | M | âœ… |
| B.8 | Tests route maison_entretien | `maison_entretien` | `tests/api/test_routes_maison_entretien.py` | ðŸŸ¡ | M | âœ… |
| B.9 | Tests route partage | `partage` | `tests/api/test_routes_partage.py` | ðŸŸ¢ | S | âœ… |

### Backend â€” Couverture par couche (rÃ©fÃ©rence)

| Couche | Fichiers | Tests | Couverture actuelle | Cible |
| -------- | ---------- | ------- | --------------------- | ------- |
| **Core** (config, DB, cache, decorators) | 12 fichiers | ~100 tests | 90% | 95% |
| **ModÃ¨les ORM** | 22 fichiers | ~80 tests | 70% | 85% |
| **Routes API** | 30 fichiers | ~150 tests | 77% | 90% |
| **Services** | 20+ fichiers | ~100 tests | 90% | 95% |
| **SpÃ©cialisÃ©s** (contrats, perf, SQL) | 5 fichiers | ~30 tests | Variable | â€” |
| **Total Backend** | **70+ fichiers** | **~460 tests** | **~75%** | **85%** |

### Frontend â€” Plan de tests

| # | TÃ¢che | Type | Fichier(s) | Effort | Statut |
| --- | ------- | ------ | ----------- | -------- | -------- |
| B.10 | Tests custom hooks (utiliser-api, utiliser-auth) | Unit (Vitest) | `frontend/src/__tests__/hooks/utiliser-api.test.ts`, `frontend/src/__tests__/hooks/utiliser-auth.test.ts` | M | âœ… |
| B.11 | Tests composants critiques (formulaire-recette, sidebar) | Unit (Vitest) | `frontend/src/__tests__/cuisine/formulaire-recette.test.tsx`, `frontend/src/__tests__/components/barre-laterale.test.tsx` | M | âœ… |
| B.12 | Tests rendering pages hub | Unit (Vitest) | `frontend/src/__tests__/pages/hubs.test.tsx` | M | âœ… |
| B.13 | E2E complets par module (pas juste smoke) | E2E (Playwright) | `frontend/e2e/cuisine-complet.spec.ts` | L | â— Partiel (module Cuisine) |
| B.14 | Tests d'accessibilitÃ© (axe-core) | E2E | `frontend/e2e/accessibility.spec.ts` | M | âœ… |

### CI â€” Validation schÃ©ma

| # | TÃ¢che | RÃ©f | Effort | Statut |
| --- | ------- | ----- | -------- | -------- |
| B.15 | Ajouter `test_schema_coherence.py` au pipeline CI | S3 | S | âœ… (`.github/workflows/tests.yml`, `.github/workflows/backend-tests.yml`) |

---

## Sprint C â€” Pages IA AvancÃ©e âœ… TERMINE

**Objectif** : Finaliser les pages IA avancÃ©es, les clients API et la documentation

### Pages Ã  finaliser/crÃ©er

| # | Page | Ã‰tat actuel | Action requise | Effort |
| --- | ------ | ------------- | ---------------- | -------- |
| C.1 | `/ia-avancee/suggestions-achats` | âœ… Page complete et connectee API | Cloture | M |
| C.2 | `/ia-avancee/diagnostic-plante` | âœ… Page complete (upload image + rendu resultat) | Cloture | M |
| C.3 | `/ia-avancee/planning-adaptatif` | âœ… Page complete et connectee API | Cloture | M |
| C.4 | `/ia-avancee/analyse-photo` | âœ… Page complete et connectee API | Cloture | M |
| C.5 | `/ia-avancee/optimisation-routines` | âœ… Page complete et connectee API | Cloture | M |
| C.6 | `/ia-avancee/recommandations-energie` | âœ… Finalisee | Cloture | S |
| C.7 | `/ia-avancee/prevision-depenses` | âœ… Finalisee | Cloture | S |
| C.8 | `/ia-avancee/idees-cadeaux` | âœ… Finalisee | Cloture | S |
| C.9 | `/ia-avancee/analyse-document` | âœ… Finalisee | Cloture | S |
| C.10 | `/ia-avancee/estimation-travaux` | âœ… Finalisee | Cloture | S |
| C.11 | `/ia-avancee/planning-voyage` | âœ… Finalisee | Cloture | S |
| C.12 | `/ia-avancee/adaptations-meteo` | âœ… Finalisee | Cloture | S |

### Correspondance legacy (analyse initiale â†’ routes finales)

| EntrÃ©e legacy | Route finale retenue |
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

| # | TÃ¢che | RÃ©f | Effort |
| --- | ------- | ----- | -------- |
| C.13 | âœ… Fonctions client IA ajoutees et alignees backend dans `ia_avancee.ts` | G25 | M |
| C.14 | âœ… Guide module IA Avancee cree (`docs/guides/ia-avancee/README.md`) | D1 | M |
| C.15 | âœ… Error boundaries presentes sur `planning`, `habitat`, `ia-avancee` | G23 | M |
| C.16 | âœ… Pages admin frontend enrichies (jobs, services, utilisateurs, notifications, SQL views) | G26 | M |
| C.17 | âœ… Section RGPD presente dans `/parametres` (export/suppression) | G27 | S |

---

## Sprint D â€” Inter-modules & Event Bus

**Objectif** : ImplÃ©menter les 7 flux inter-modules prioritaires + enrichir le bus d'Ã©vÃ©nements

### Flux inter-modules existants (8 â€” rÃ©fÃ©rence)

| # | Flux | Source â†’ Cible | Fichier | Trigger |
| --- | ------ | ---------------- | --------- | --------- |
| 1 | PÃ©remption â†’ Recettes | Inventaire â†’ Cuisine | `inter_module_peremption_recettes.py` | Job/API |
| 2 | Total courses â†’ Budget | Courses â†’ Famille | `inter_module_courses_budget.py` | Save courses |
| 3 | Document expire â†’ Alerte | Famille â†’ Notifications | `inter_module_documents_notifications.py` | Job J-30/15/7/1 |
| 4 | Chat IA â†’ Multi-contexte | Tous â†’ Utilitaires | `inter_module_chat_contexte.py` | Chat appel |
| 5 | Batch cooking â†’ Stock | Cuisine â†’ Inventaire | `inter_module_batch_inventaire.py` | Fin session |
| 6 | Anniversaires â†’ Budget | Famille â†’ Famille | `inter_module_anniversaires_budget.py` | Auto |
| 7 | Voyages â†’ Budget | Voyages â†’ Famille | `inter_module_voyages_budget.py` | Save voyage |
| 8 | Mises jeux â†’ Budget | Jeux â†’ Famille | `inter_module_budget_jeux.py` | Mise placÃ©e |

### Flux Ã  implÃ©menter (prioritaires)

| # | TÃ¢che | RÃ©f | Source â†’ Cible | Effort | Checklist |
| --- | ------- | ----- | ---------------- | -------- | ----------- |
| D.1 | RÃ©colte jardin â†’ Recettes saison (proposÃ©es au prochain planning semaine) | I1 | Maison/Jardin â†’ Cuisine | M | â˜ Event `jardin.recolte` â˜ AbonnÃ© suggestions â˜ Tests |
| D.2 | Anomalie Ã©nergie â†’ TÃ¢che entretien auto | I3 | Maison/Ã‰nergie â†’ Maison/Entretien | S | â˜ Event `energie.anomalie` â˜ CrÃ©ation tÃ¢che â˜ Tests |
| D.3 | Budget dÃ©passement â†’ Alerte dashboard | I4 | Famille/Budget â†’ Dashboard | S | â˜ Event `budget.depassement` â˜ Widget alerte â˜ Tests |
| D.4 | Inventaire â†’ Courses prÃ©dictives | I9 | Inventaire â†’ Courses | L | â˜ ML sur historique â˜ Liste prÃ©-remplie â˜ Tests |
| D.5 | Retour recette â†’ Ajuster planning futur (feedback loop IA) | I13 | Cuisine â†’ Planning | M | â˜ Score recette â˜ Contexte IA â˜ Tests |
| D.6 | Contrats maison â†’ Alertes renouvellement | I14 | Maison/Contrats â†’ Notifications | S | â˜ Job CRON â˜ Multi-canal â˜ Tests |
| D.7 | Enrichir abonnÃ©s EventBus (pas juste cache) | â€” | Global | M | â˜ Refactor bus â˜ AbonnÃ©s business â˜ Tests |

### Flux futurs (backlog)

| # | Flux proposÃ© | RÃ©f | Source â†’ Cible | Valeur | Effort |
| --- | ------------- | ----- | ---------------- | -------- | -------- |
| D.8 | Garmin santÃ© â†’ ActivitÃ©s Jules | I2 | Famille/Garmin â†’ Famille/Jules | ðŸŸ¡ | M |
| D.9 | MÃ©tÃ©o â†’ Planning repas adaptÃ© | I5 | Outils/MÃ©tÃ©o â†’ Cuisine/Planning | ðŸŸ¡ | M |
| D.10 | MÃ©tÃ©o â†’ TÃ¢ches jardin urgentes | I6 | Outils/MÃ©tÃ©o â†’ Maison/Jardin | ðŸŸ¡ | S |
| D.11 | Projets terminÃ©s â†’ Valeur bien habitat | I7 | Maison/Projets â†’ Habitat | ðŸŸ¡ | M |
| D.12 | Entretien artisan â†’ Devis comparatif auto | I8 | Maison/Entretien â†’ Maison/Artisans | ðŸŸ¡ | M |
| D.13 | Routines santÃ© â†’ Briefing matinal | I11 | Famille/SantÃ© â†’ Dashboard | ðŸŸ¡ | S |
| D.14 | Anniversaire â†’ Suggestion cadeau IA | I12 | Famille â†’ IA AvancÃ©e | ðŸŸ¢ | M |
| D.15 | Score gamification â†’ RÃ©compenses famille | I15 | Gamification â†’ Famille | ðŸŸ¢ | M |
| â€” | ~~RÃ©sultats paris â†’ P&L famille~~ | ~~I10~~ | âŒ **RejetÃ©** â€” Budget jeux volontairement sÃ©parÃ© | â€” | â€” |

### Architecture Event Bus â€” Pattern d'implÃ©mentation

Le bus d'Ã©vÃ©nements `EventBus` Ã©met des Ã©vÃ©nements `recette.*`, `stock.*`, `courses.*`, `entretien.*`, `planning.*`, `jeux.*` â€” mais les **seuls abonnÃ©s sont pour l'invalidation de cache**.

**OpportunitÃ©** : Ajouter des abonnÃ©s pour dÃ©clencher les flux D.1-D.7 via le bus existant, sans coupler les services.

```python
# Exemple : RÃ©colte jardin â†’ Suggestions recettes
bus.souscrire("jardin.recolte", lambda evt: 
    get_suggestions_service().suggerer_recettes_saison(evt["plantes_recoltees"])
)
```

---

## Sprint E â€” Notifications enrichies

**Objectif** : Enrichir WhatsApp, ajouter centre de notifications, nouveaux jobs CRON

### Architecture notifications (rÃ©fÃ©rence)

```
DispatcherNotifications (central)
â”œâ”€â”€ ntfy.sh        â†’ REST API â†’ push notifications
â”œâ”€â”€ Web Push       â†’ VAPID protocol â†’ navigateur
â”œâ”€â”€ Email          â†’ Resend API â†’ Jinja2 templates
â””â”€â”€ WhatsApp       â†’ Meta Cloud API â†’ webhook bidirectionnel
```

### TÃ¢ches notifications

| # | TÃ¢che | RÃ©f | Canal | Effort | Checklist |
| --- | ------- | ----- | ------- | -------- | ----------- |
| E.1 | WhatsApp : Flux liste courses semaine | N1 | WhatsApp | M | â˜ Template â˜ Bouton interactif â˜ Tests |
| E.2 | WhatsApp : Rappel activitÃ© Jules | N2 | WhatsApp | S | â˜ Template â˜ Suggestion activitÃ© â˜ Tests |
| E.3 | WhatsApp : RÃ©sultats paris sportifs | N3 | WhatsApp | S | â˜ Template â˜ P&L inline â˜ Tests |
| E.4 | PrÃ©fÃ©rences notifications granulaires â€” UI par module | N9 | Tous | M | â˜ Schema DB â˜ API â˜ UI settings â˜ Tests |
| E.5 | Centre de notifications dans l'app (historique) | N10 | Tous | M | â˜ Page â˜ Listing â˜ Mark as read â˜ Filtres |
| E.6 | Email : Newsletter hebdo template riche | N5 | Email | M | â˜ Template Jinja2 â˜ Images â˜ Call-to-action |
| E.7 | Email : Rapport budget PDF en piÃ¨ce jointe | N6 | Email | S | â˜ Attach PDF (dÃ©jÃ  gÃ©nÃ©rÃ©) |
| E.8 | Push : Actions rapides dans les notifications | N7 | Push | M | â˜ Boutons action â˜ Callback API |

### Nouveaux jobs CRON

| # | Job | RÃ©f | Schedule | Description | Effort |
| --- | ----- | ----- | ---------- | ------------- | -------- |
| E.9 | `prediction_courses_hebdo` | C1 | Dim 18h | GÃ©nÃ©rer liste courses prÃ©dictive pour la semaine | M |
| E.10 | `rapport_energie_mensuel` | C2 | 1er 10h | Rapport conso Ã©nergie + comparaison mois prÃ©cÃ©dent | S |
| E.11 | `suggestions_recettes_saison` | C3 | 1er et 15 6h | Nouvelles recettes de saison Ã  dÃ©couvrir | S |
| E.12 | `audit_securite_hebdo` | C4 | Dim 2h | VÃ©rification intÃ©gritÃ© donnÃ©es + logs suspects | M |
| E.13 | `nettoyage_notifications_anciennes` | C5 | Dim 4h | Purger notifications > 90 jours | S |
| E.14 | `mise_a_jour_scores_gamification` | C6 | Minuit | Recalculer scores/badges quotidiens | S |
| E.15 | `alerte_meteo_jardin` | C7 | 7h | Alerte gel/canicule â†’ protÃ©ger plantes | S |
| E.16 | `resume_financier_semaine` | C8 | Ven 18h | RÃ©sumÃ© dÃ©penses de la semaine | S |

### Mapping Ã©vÃ©nements â†’ canaux (existant + proposÃ©)

| Ã‰vÃ©nement | ntfy | Push | Email | WhatsApp | Ã‰tat |
| ----------- | ------ | ------ | ------- | ---------- | ------ |
| PÃ©remption J-2 | âœ… | âœ… | â€” | â€” | âœ… ImplÃ©mentÃ© |
| Rappel courses | âœ… | âœ… | â€” | âœ… | âœ… ImplÃ©mentÃ© |
| RÃ©sumÃ© hebdo | â€” | â€” | âœ… | âœ… | âœ… ImplÃ©mentÃ© |
| Ã‰chec cron job | âœ… | âœ… | âœ… | âœ… | âœ… ImplÃ©mentÃ© |
| Document expirant | âœ… | âœ… | âœ… | â€” | âœ… ImplÃ©mentÃ© |
| Rappel vaccin | â€” | âœ… | âœ… | â€” | âœ… ImplÃ©mentÃ© |
| **Liste courses semaine** | â€” | âœ… | â€” | âœ… | â˜ Ã€ ajouter |
| **RÃ©sultats paris** | âœ… | âœ… | â€” | âœ… | â˜ Ã€ ajouter |
| **Budget dÃ©passÃ©** | âœ… | âœ… | âœ… | âœ… | â˜ Ã€ ajouter |
| **ActivitÃ© Jules** | â€” | âœ… | â€” | âœ… | â˜ Ã€ ajouter |
| **Alerte mÃ©tÃ©o jardin** | âœ… | âœ… | â€” | â€” | â˜ Ã€ ajouter |
| **Contrat Ã  renouveler** | â€” | âœ… | âœ… | â€” | â˜ Ã€ ajouter |

---

## Sprint F â€” Admin & DX

**Objectif** : Dashboard admin riche, outils dÃ©veloppeur, mode maintenance

### FonctionnalitÃ©s admin existantes (rÃ©fÃ©rence)

| Feature | Endpoint | Ã‰tat |
| --------- | ---------- | ------ |
| Liste jobs | `GET /api/v1/admin/jobs` | âœ… |
| Trigger manuel | `POST /api/v1/admin/jobs/{id}/run` | âœ… (rate limit 5/min) |
| Dry run | `POST /api/v1/admin/jobs/{id}/run?dry_run=true` | âœ… |
| Logs jobs | `GET /api/v1/admin/jobs/{id}/logs` | âœ… |
| Audit logs | `GET /api/v1/admin/audit-logs` | âœ… |
| Stats audit | `GET /api/v1/admin/audit-stats` | âœ… |
| Export audit CSV | `GET /api/v1/admin/audit-export` | âœ… |
| Health check services | `GET /api/v1/admin/services/health` | âœ… |
| Test notifications | `POST /api/v1/admin/notifications/test` | âœ… |
| Stats cache | `GET /api/v1/admin/cache/stats` | âœ… |
| Purge cache | `POST /api/v1/admin/cache/clear` | âœ… |
| Liste users | `GET /api/v1/admin/users` | âœ… |
| DÃ©sactiver user | `POST /api/v1/admin/users/{id}/disable` | âœ… |
| CohÃ©rence DB | `GET /api/v1/admin/db/coherence` | âœ… |
| Feature flags | `GET/PUT /api/v1/admin/feature-flags` | âœ… |
| Runtime config | `GET/PUT /api/v1/admin/config` | âœ… |
| Flow simulator | `POST /api/v1/admin/simulate-flow` | âœ… |

### TÃ¢ches admin

| # | TÃ¢che | RÃ©f | Effort | Checklist |
| --- | ------- | ----- | -------- | ----------- |
| F.1 | Dashboard admin dÃ©diÃ© â€” graphiques jobs, erreurs, usage IA, notifications | A1 | M | âœ… Page frontend âœ… API agrÃ©gation âœ… Charts |
| F.2 | Console IA admin â€” tester un prompt depuis l'admin, voir rÃ©ponse brute | A2 | S | âœ… Input prompt âœ… Affichage rÃ©ponse âœ… Rate limit |
| F.3 | Seed data one-click (dev only) | A3 | S | â˜ Endpoint â˜ DonnÃ©es seed â˜ Guard env=dev |
| F.4 | Panneau admin flottant (Ctrl+Shift+A) | â€” | M | âœ… Overlay React âœ… Trigger jobs âœ… Feature flags âœ… SantÃ© âœ… Quotas IA |
| F.5 | Toggle mode maintenance (bandeau utilisateur) | A10 | S | âœ… Feature flag âœ… Bandeau UI âœ… API toggle |
| F.6 | Queue de notifications â€” voir et gÃ©rer la file d'attente | A8 | S | âœ… API listing âœ… Page admin âœ… Delete/retry |
| F.7 | Historique jobs paginÃ© avec filtres | A9 | M | â˜ API paginÃ©e â˜ Filtres status/date â˜ UI |
| F.8 | Reset module (dev only) â€” vider donnÃ©es d'un module | A4 | S | âœ… Endpoint âœ… Guard env=dev |
| F.9 | Export DB complet JSON/SQL | A5 | M | âœ… Export sÃ©rialisÃ© âœ… Download |
| F.10 | Import DB â€” restaurer un backup | A6 | M | âœ… Upload âœ… Validation âœ… Restore |
| F.11 | Monitoring temps rÃ©el â€” WebSocket admin mÃ©triques live | A7 | L | âœ… WS endpoint âœ… Dashboard real-time |

### Principe admin

L'admin est accessible via :
- `Depends(require_role("admin"))` cÃ´tÃ© API (protÃ©gÃ©)
- Conditionnel dans la sidebar frontend (si `user.role === 'admin'`)
- Feature flag `admin.mode_test` pour activer des fonctions debug
- **Panneau admin flottant** (overlay) activable par `Ctrl+Shift+A` â€” invisible pour les utilisateurs normaux

---

## Sprint G â€” UX & Simplification flux

**Objectif** : Maximum 3 clics pour toute action courante, zÃ©ro config au premier lancement

### Principes UX

```
1. Maximum 3 clics pour toute action courante
2. ZÃ©ro configuration requise au premier lancement
3. L'IA fait le travail, l'utilisateur valide
4. Notifications proactives plutÃ´t que consultation
5. Interface adaptative (mobile-first, contexte-sensitive)
```

### Flux Ã  simplifier

| # | TÃ¢che | RÃ©f | Flux actuel | Flux cible | Effort |
| --- | ------- | ----- | ------------- | ------------ | -------- |
| G.1 | Bouton "Planifier ma semaine" one-click | U1 | Planning â†’ Choisir jour â†’ Chercher recette â†’ SÃ©lectionner (4 clics) | **1 clic** : IA gÃ©nÃ¨re â†’ Valider/ajuster | S |
| G.2 | GÃ©nÃ©ration courses auto depuis planning validÃ© | U2 | Naviguer Courses â†’ CrÃ©er liste â†’ Ajouter un par un | **Auto** : Depuis planning â†’ "GÃ©nÃ©rer courses" â†’ Liste prÃ©-remplie | S |
| G.3 | Widget budget sur le dashboard avec tendance | U3 | Famille â†’ Budget â†’ Filtrer mois â†’ Lire | **Dashboard** : Widget tendance budget en page d'accueil | S |
| G.4 | Recherche globale instantanÃ©e de recettes | U4 | Cuisine â†’ Recettes â†’ Filtres â†’ Parcourir | **Barre de recherche** : RÃ©sultats instantanÃ©s | M |
| G.5 | Wizard crÃ©ation projet maison (3 Ã©tapes) | U5 | Formulaire complet Ã  remplir | **Wizard** : Nom â†’ Type/Budget â†’ TÃ¢ches suggÃ©rÃ©es IA | M |
| G.6 | Alertes proactives inventaire bas â†’ action directe depuis notif | U6 | Cuisine â†’ Inventaire â†’ Parcourir | **Notifications** push quand stock bas | S |
| G.7 | Timeline Jules chronologique unique (jalons + activitÃ©s + santÃ©) | U7 | Navigation onglets multiples | **Timeline** : Vue unique chronologique | M |
| G.8 | Checklist du jour (widget dashboard) avec swipe pour valider | U8 | Maison â†’ Entretien â†’ Voir tÃ¢ches â†’ Marquer fait | **Widget** : Swipe pour valider dans le dashboard | S |
| G.9 | Widget mÃ©tÃ©o intÃ©grÃ© (header ou dashboard) â†’ adapte suggestions | U9 | Outils â†’ MÃ©tÃ©o â†’ Page dÃ©diÃ©e | **IntÃ©grÃ©** : MÃ©tÃ©o directement dans le header/dashboard | S |
| G.10 | PrÃ©fÃ©rences notifications par module (dans chaque module) | U10 | ParamÃ¨tres â†’ Section notifications â†’ Toggle par type | **Par module** : "Me notifier pour..." dans chaque module | M |
| G.11 | Mode focus "essentiel du jour" (1 Ã©cran) | IN11 | Plusieurs pages Ã  consulter | **1 Ã©cran** : mÃ©tÃ©o + repas + tÃ¢ches + rappels | M |
| G.12 | Mode vacances (pause notifications non essentielles) | IN14 | Pas de fonctionnalitÃ© | **Toggle** : Pause + checklist voyage auto | S |

### Composants UX Ã  ajouter/enrichir

| # | Composant | RÃ©f | Description | Impact |
| --- | ----------- | ----- | ------------- | -------- |
| G.13 | Quick Actions FAB enrichi | UX1 | Actions rapides contextuelles (existant, Ã  enrichir) | Navigation rapide |
| G.14 | Command Palette enrichie | UX2 | `Cmd+K` pour naviguer/agir (existant `menu-commandes.tsx`) | Power users |
| G.15 | Onboarding tour amÃ©liorÃ© | UX3 | Tour guidÃ© au premier lancement (existant `tour-onboarding.tsx`) | DÃ©couvrabilitÃ© |
| G.16 | Empty states riches | UX4 | Module vide â†’ message encourageant + CTA pour commencer | Engagement |
| G.17 | Skeleton screens complets | UX5 | Loading skeletons sur toutes les pages restantes | UX perÃ§ue |
| G.18 | Swipe gestures mobile gÃ©nÃ©ralisÃ©es | UX6 | Swipe gauche/droite sur items de liste (existant, gÃ©nÃ©raliser) | Mobile fluide |
| G.19 | Cards drag & drop dashboard | UX7 | RÃ©organisation widgets dashboard (existant `grille-widgets.tsx`) | Personnalisation |
| G.20 | Confirmations inline (toasts au lieu de modals) | UX8 | Toasts pour actions simples, modals pour actions destructives | Moins intrusif |

---

## Sprint H â€” Consolidation SQL & Organisation code

**Ã‰tat** : âœ… COMPLÃ‰TÃ‰ Ã€ 100% â€” Avril 2026

**Objectif** : SQL structurÃ©, code organisÃ©, documentation complÃ¨te

### Consolidation SQL

#### Ã‰tat actuel SQL

- **Fichier source** : `sql/INIT_COMPLET.sql` (~3000+ lignes)
- **Migrations** : `sql/migrations/` (V003 Ã  V007)
- **Alembic** : ArchivÃ© intentionnellement (stratÃ©gie SQL-first)
- **Alignement ORM** : ~95% (31 fichiers modÃ¨les â†” 143 tables)

#### TÃ¢ches SQL

| # | TÃ¢che | RÃ©f | Effort | Checklist |
| --- | ------- | ----- | -------- | ----------- |
| H.1 | DÃ©couper `INIT_COMPLET.sql` en fichiers thÃ©matiques | S1 | M | âœ… Structure ci-dessous âœ… Fichiers crÃ©Ã©s âœ… TestÃ© |
| H.2 | Script `scripts/db/regenerate_init.py` â€” concatÃ¨ne schema/* â†’ INIT_COMPLET.sql | S1 | S | âœ… Script âœ… Idempotent âœ… Tests |
| H.3 | ComplÃ©ter ORM pour tables orphelines (`notes_memos`, `presse_papier_entrees`, `releves_energie`) | S2 | S | âœ… ModÃ¨les ORM âœ… Tests |
| H.4 | Audit indexes sur colonnes frÃ©quemment filtrÃ©es | S4 | M | âœ… docs/guides/DATABASE_INDEXES.md crÃ©Ã© âœ… Index listÃ©s |
| H.5 | Documenter le workflow SQL-first (migrations) | S5 | S | âœ… Section ajoutÃ©e dans MIGRATION_GUIDE.md |

#### Structure SQL cible

```
sql/
â”œâ”€â”€ INIT_COMPLET.sql          â†’ Script unique d'init (rÃ©gÃ©nÃ©rÃ© automatiquement)
â”œâ”€â”€ schema/
â”‚   â”œâ”€â”€ 01_extensions.sql     â†’ Extensions PostgreSQL
â”‚   â”œâ”€â”€ 02_functions.sql      â†’ Fonctions et triggers
â”‚   â”œâ”€â”€ 03_cuisine.sql        â†’ Tables cuisine (recettes, ingredients, planning, courses)
â”‚   â”œâ”€â”€ 04_famille.sql        â†’ Tables famille (profils, activitÃ©s, budget, santÃ©)
â”‚   â”œâ”€â”€ 05_maison.sql         â†’ Tables maison (projets, entretien, jardin, stocks)
â”‚   â”œâ”€â”€ 06_habitat.sql        â†’ Tables habitat (scÃ©narios, plans, veille)
â”‚   â”œâ”€â”€ 07_jeux.sql           â†’ Tables jeux (paris, loto, euromillions)
â”‚   â”œâ”€â”€ 08_systeme.sql        â†’ Tables systÃ¨me (logs, config, migrations)
â”‚   â”œâ”€â”€ 09_notifications.sql  â†’ Tables notifications (push, webhooks)
â”‚   â”œâ”€â”€ 10_finances.sql       â†’ Tables finances (dÃ©penses, budgets)
â”‚   â”œâ”€â”€ 11_views.sql          â†’ Toutes les vues
â”‚   â”œâ”€â”€ 12_indexes.sql        â†’ Tous les index
â”‚   â””â”€â”€ 13_rls_policies.sql   â†’ Toutes les politiques RLS
â”œâ”€â”€ seed/                     â†’ DonnÃ©es de seed (rÃ©fÃ©rence)
â””â”€â”€ migrations/               â†’ Garde tel quel
```

### Organisation du code â€” Backend

#### Ã‰tat actuel backend

```
src/
â”œâ”€â”€ api/                        âœ… Bien structurÃ©
â”‚   â”œâ”€â”€ routes/ (38 fichiers)   âš ï¸ Certains trÃ¨s gros (>500 lignes)
â”‚   â”œâ”€â”€ schemas/ (24 fichiers)  âœ… Bien organisÃ©
â”‚   â”œâ”€â”€ utils/                  âœ… 
â”‚   â”œâ”€â”€ rate_limiting/          âœ…
â”‚   â”œâ”€â”€ dependencies.py         âœ…
â”‚   â”œâ”€â”€ auth.py                 âœ…
â”‚   â””â”€â”€ main.py                 âœ…
â”œâ”€â”€ core/                       âœ… Excellent
â”‚   â”œâ”€â”€ ai/ (5 fichiers)        âœ…
â”‚   â”œâ”€â”€ caching/ (4 fichiers)   âœ…
â”‚   â”œâ”€â”€ config/ (3 fichiers)    âœ…
â”‚   â”œâ”€â”€ db/ (4 fichiers)        âœ…
â”‚   â”œâ”€â”€ decorators/ (5 fichiers)âœ…
â”‚   â”œâ”€â”€ models/ (31 fichiers)   âœ…
â”‚   â”œâ”€â”€ monitoring/             âœ…
â”‚   â”œâ”€â”€ resilience/             âœ…
â”‚   â””â”€â”€ validation/             âœ…
â”œâ”€â”€ services/                   âœ… Bien modulaire
â”‚   â”œâ”€â”€ core/ (base, events, cron, notifications) âœ…
â”‚   â”œâ”€â”€ cuisine/ (5+ fichiers)  âœ…
â”‚   â”œâ”€â”€ famille/ (6+ fichiers)  âœ…
â”‚   â”œâ”€â”€ maison/ (10+ fichiers)  âœ…
â”‚   â”œâ”€â”€ habitat/ (4 fichiers)   âœ…
â”‚   â”œâ”€â”€ jeux/ (5+ fichiers)     âœ…
â”‚   â”œâ”€â”€ inventaire/             âœ…
â”‚   â”œâ”€â”€ rapports/               âœ…
â”‚   â”œâ”€â”€ dashboard/              âœ…
â”‚   â”œâ”€â”€ utilitaires/            âœ…
â”‚   â””â”€â”€ integrations/           âœ…
```

#### TÃ¢ches organisation backend

| # | TÃ¢che | RÃ©f | Effort |
| --- | ------- | ----- | -------- |
| H.6 | DÃ©couper routes volumineuses (>500 lignes) en sous-modules | O1 | M | âœ… jeux.py (2545L) â†’ 4 fichiers (paris, loto, euromillions, dashboard) |
| H.7 | Auditer imports circulaires entre services | O2 | S | âœ… 21 modules testÃ©s â€” aucun import circulaire |
| H.8 | Unifier schÃ©mas Pydantic (`api/schemas/` pour API, `core/validation/` pour business) | O3 | M | âœ… Section ajoutÃ©e dans docs/PATTERNS.md |
| H.9 | Nommer tests de faÃ§on cohÃ©rente | O4 | S | âœ… Section ajoutÃ©e dans docs/TESTING_ADVANCED.md |
| H.10 | DÃ©placer scripts archivÃ©s (`split_famille.py`, `split_maison.py`) vers `scripts/archive/` | O5 | S | âœ… scripts/archive/ crÃ©Ã© + 2 scripts dÃ©placÃ©s |

### Organisation du code â€” Frontend

#### Ã‰tat actuel frontend

```
frontend/src/
â”œâ”€â”€ app/(app)/               âœ… App Router bien structurÃ© (103 pages)
â”œâ”€â”€ app/(auth)/              âœ… Auth sÃ©parÃ©
â”œâ”€â”€ composants/
â”‚   â”œâ”€â”€ ui/ (30 fichiers)    âœ… shadcn/ui complet
â”‚   â”œâ”€â”€ disposition/ (18)    âœ… Layout riche
â”‚   â”œâ”€â”€ cuisine/ (8)         âœ…
â”‚   â”œâ”€â”€ famille/ (9)         âœ…
â”‚   â”œâ”€â”€ jeux/ (13)           âœ…
â”‚   â”œâ”€â”€ maison/ (13)         âœ…
â”‚   â”œâ”€â”€ habitat/ (6)         âœ… Extraction Sprint H rÃ©alisÃ©e
â”‚   â”œâ”€â”€ planning/ (3)        âœ… Extraction Sprint H rÃ©alisÃ©e
â”‚   â””â”€â”€ graphiques/ (3)      âœ…
â”œâ”€â”€ bibliotheque/api/ (25)   âœ… Clients API complets
â”œâ”€â”€ crochets/ (13)           âœ… Hooks riches
â”œâ”€â”€ magasins/ (4)            âœ… Stores Zustand
â”œâ”€â”€ types/ (15)              âœ… TypeScript complet
â””â”€â”€ fournisseurs/ (3)        âœ… Providers
```

#### TÃ¢ches organisation frontend

| # | TÃ¢che | RÃ©f | Effort |
| --- | ------- | ----- | -------- |
| H.11 | Extraire composants rÃ©utilisables habitat (3 â†’ plus) | O6 | M | âœ… 3 nouveaux composants habitat extraits |
| H.12 | Extraire composants planning (timeline, week view, etc.) | O7 | M | âœ… 2 composants planning extraits |
| H.13 | DÃ©couper pages monolithiques (paramÃ¨tres > 1200 lignes) | O8 | M | âœ… page paramÃ¨tres dÃ©coupÃ©e en sous-composants |
| H.14 | Tests unit frontend â€” plan complet hooks, stores, composants | O9 | L | âœ… Plan ajoutÃ©: docs/guides/FRONTEND_TEST_PLAN.md |

### Documentation manquante

| # | Document | RÃ©f | PrioritÃ© | Contenu attendu | Effort |
| --- | ---------- | ----- | ---------- | ----------------- | -------- |
| H.15 | Guide module IA AvancÃ©e | D1 | ðŸ”´ | Les 14 outils IA, endpoints, prompts, cache, limites | M | âœ… docs/guides/IA_AVANCEE.md |
| H.16 | Guide intÃ©gration Sentry | D2 | ðŸŸ¡ | Setup DSN, sampling, error boundaries, replay | S | âœ… docs/guides/SENTRY.md |
| H.17 | Guide Docker production | D3 | ðŸŸ¡ | Railway-specific, performance tuning, scaling | M | âœ… docs/guides/DOCKER_PRODUCTION.md |
| H.18 | Design System visuel | D4 | ðŸŸ¢ | Specs visuels composants (couleurs, spacing, typo) | M | âœ… docs/DESIGN_SYSTEM.md |
| H.19 | Guide contribution (CONTRIBUTING.md) | D5 | ðŸŸ¡ | Conventions, PR process, code review | S | âœ… CONTRIBUTING.md |
| H.20 | Changelog technique Phase 10 | D6 | ðŸŸ¡ | DÃ©tails techniques des innovations | S | âœ… CHANGELOG_PHASE10.md |
| H.21 | Guide PWA/Offline | D7 | ðŸŸ¢ | Service Worker, cache strategies, sync | S | âœ… docs/guides/PWA_OFFLINE.md |
| H.22 | SchÃ©ma d'architecture Mermaid complet | D8 | ðŸŸ¡ | Diagramme architectural Ã  jour | M | âœ… AjoutÃ© dans docs/ARCHITECTURE.md |
| H.23 | RafraÃ®chir ERD_SCHEMA.md (diagramme Mermaid 143 tables) | â€” | ðŸŸ¡ | RÃ©gÃ©nÃ©rer le diagramme entitÃ©-relation | M | âœ… Sprint H metadata + procÃ©dure de refresh |
| H.24 | Enrichir SQLALCHEMY_SESSION_GUIDE.md (exemples 2.0+) | â€” | ðŸŸ¢ | Exemples avancÃ©s SQLAlchemy 2.0 | S | âœ… Section FastAPI patterns ajoutÃ©e |

---

## Sprint I â€” Innovations long terme

**Objectif** : Transformations majeures de l'application â€” multi-utilisateurs, analytics, IA proactive

### Innovations technologiques

| # | TÃ¢che | RÃ©f | Description | Impact | Effort |
| --- | ------- | ----- | ------------- | -------- | -------- |
| I.1 | Mode famille multi-utilisateurs | IN1 | Chaque membre a son profil avec rÃ´les (parent, enfant, invitÃ©) | ðŸ”´ Transformant | XL |
| I.2 | Synchronisation temps rÃ©el (WebSocket tous modules) | IN2 | Ã‰dition collaborative au-delÃ  des courses | ðŸŸ¡ Fort | L |
| I.3 | Widget smartphone (PWA natif) | IN3 | Widgets iOS/Android (courses du jour, prochaine tÃ¢che, mÃ©tÃ©o) | ðŸŸ¡ Fort | L |
| I.4 | Mode vocal complet | IN4 | "Hey Matanne, qu'est-ce qu'on mange ce soir ?" â†’ TTS | ðŸŸ¢ Innovation | L |
| I.5 | Scan & Go code-barres | IN5 | Scanner code-barres â†’ inventaire + infos nutrition auto | ðŸŸ¡ Fort | M |
| I.6 | IntÃ©gration IoT (capteurs maison) | IN6 | TempÃ©rature, humiditÃ©, consommation â†’ dashboards | ðŸŸ¢ Innovation | XL |
| I.7 | Mode dÃ©connectÃ© enrichi | IN8 | IndexedDB + background sync â†’ fonctions de base hors-ligne | ðŸŸ¡ Fort | XL |
| â€” | ~~Marketplace recettes~~ | ~~IN7~~ | âŒ **RejetÃ©** â€” Pas de volet social | â€” | â€” |

### Innovations UX

| # | TÃ¢che | RÃ©f | Description | Impact | Effort |
| --- | ------- | ----- | ------------- | -------- | -------- |
| I.8 | ThÃ¨mes saisonniers | IN9 | Interface s'adapte visuellement aux saisons | ðŸŸ¢ Fun | S |
| I.9 | Gamification sportive uniquement | IN10 | Points/badges sur donnÃ©es Garmin/activitÃ© physique | ðŸŸ¡ Fort | S |
| I.10 | Raccourcis Google Assistant | IN12 | Actions rapides via assistant vocal Google (tablette) | ðŸŸ¢ Innovation | M |
| â€” | ~~QR code partage~~ | ~~IN13~~ | âŒ **RejetÃ©** â€” Aucun intÃ©rÃªt | â€” | â€” |

### Innovations Data & IA

| # | TÃ¢che | RÃ©f | Description | Impact | Effort |
| --- | ------- | ----- | ------------- | -------- | -------- |
| I.11 | Analytics familiales long terme | IN15 | Tendances nutrition, dÃ©penses, activitÃ©s, Ã©nergie â†’ graphiques | ðŸ”´ Transformant | L |
| I.12 | PrÃ©dictions ML | IN16 | ModÃ¨les prÃ©dictifs : courses, dÃ©penses, pannes | ðŸŸ¡ Fort | XL |
| I.13 | Benchmark famille anonyme | IN17 | Comparer habitudes avec moyennes nationales | ðŸŸ¢ Innovation | L |
| I.14 | IntÃ©gration bancaire (Plaid/Bridge) | IN19 | Sync banque â†’ dÃ©penses auto-catÃ©gorisÃ©es | ðŸ”´ Transformant | XL |
| I.15 | Agent IA proactif | IN20 | L'IA suggÃ¨re des actions avant la demande ("Il fait beau, promenez-vous !") | ðŸŸ¡ Fort | M |
| â€” | ~~Export Notion/Obsidian~~ | ~~IN18~~ | âŒ **RejetÃ©** â€” Pas d'intÃ©rÃªt | â€” | â€” |

### Nouvelles opportunitÃ©s IA (services Ã  dÃ©velopper)

| # | OpportunitÃ© | RÃ©f | Module | Description | Effort |
| --- | ------------- | ----- | -------- | ------------- | -------- |
| I.16 | Nutritionniste IA | IA1 | Cuisine | Analyse nutrition hebdo â†’ recommandations (protÃ©ines, fibres, vitamines) | M |
| I.17 | Coach budget IA | IA2 | Famille | Analyse tendances dÃ©penses â†’ suggestions Ã©conomies + benchmarks | M |
| I.18 | Planificateur voyages IA | IA3 | Famille | GÃ©nÃ©ration itinÃ©raire + checklist + budget prÃ©visionnel | L |
| I.19 | Diagnostic plante photo (vision IA) | IA4 | Maison | Upload photo plante â†’ diagnostic maladie + traitement | M |
| I.20 | Optimiseur courses prÃ©dictif (ML) | IA5 | Courses | ML sur historique achats â†’ liste courses prÃ©-remplie | L |
| I.21 | Assistant vocal enrichi | IA6 | Outils | Commandes vocales â†’ actions multi-modules | L |
| I.22 | RÃ©sumÃ© vocal quotidien (TTS) | IA7 | Dashboard | TTS du briefing matinal â†’ Ã©coutable en voiture | M |
| I.23 | Styliste dÃ©co personnalisÃ© | IA8 | Habitat | Analyse photos piÃ¨ces â†’ suggestions dÃ©co | L |
| I.24 | PrÃ©dicteur pannes (ML) | IA9 | Maison | ML sur Ã¢ge/usage appareils â†’ maintenance prÃ©ventive | M |
| I.25 | GÃ©nÃ©rateur menus Ã©vÃ©nements | IA10 | Cuisine | Menu complet anniversaire/fÃªte selon nb personnes + rÃ©gimes | M |
| I.26 | Analyseur ticket de caisse (OCR) | IA11 | Famille | OCR ticket â†’ catÃ©gorisation auto dÃ©penses + promos | L |
| I.27 | Comparateur recettes nutritionnel | IA12 | Cuisine | Comparer 2 recettes â†’ diffÃ©rences nutritionnelles visuelles | S |
| I.28 | Assistant devis travaux | IA13 | Maison | Description travaux â†’ estimation prix + matÃ©riaux | M |
| I.29 | Coach routine bien-Ãªtre | IA14 | Famille | Analyse habitudes â†’ routines personnalisÃ©es selon Garmin | M |

### Architecture IA â€” AmÃ©liorations

| # | AmÃ©lioration | Description | Effort |
| --- | ------------- | ------------- | -------- |
| I.30 | Rate limit per-user (pas global) | Chaque utilisateur a son propre quota IA | M |
| I.31 | Cache sÃ©mantique enrichi (embeddings) | Matcher prompts similaires (pas juste hash exact) â†’ -30-40% appels | L |
| I.32 | Fallback model | Si Mistral down â†’ fallback Ollama ou autre provider (circuit breaker dÃ©jÃ  en place) | M |
| I.33 | Feedback loop | Stocker retours thumbs up/down â†’ amÃ©liorer prompts comme contexte | M |

---

## RÃ©fÃ©rentiel Bugs

### ðŸ”´ Critiques

| # | ProblÃ¨me | Fichier | Impact | Sprint |
| --- | ---------- | --------- | -------- | -------- |
| B1 | **5 blocs `except: pass` silencieux** dans webhook WhatsApp â€” erreurs avalÃ©es sans log | `src/api/routes/webhooks_whatsapp.py` (L621, 964, 984, 1008) | Messages WhatsApp perdus silencieusement | A.1 |
| B2 | **`except: pass`** dans endpoint auth â€” Ã©chec d'audit silencieux | `src/api/routes/auth.py` (L94) | Impossible de tracer les tentatives de login | A.2 |
| B3 | **`except: pass`** dans export PDF â€” erreur masquÃ©e | `src/api/routes/export.py` (L204) | Exports PDF Ã©chouent sans feedback | A.3 |
| B4 | **`except: pass`** dans prÃ©fÃ©rences â€” sauvegarde silencieuse | `src/api/routes/preferences.py` (L285) | PrÃ©fÃ©rences non sauvegardÃ©es sans erreur | A.4 |
| B5 | **Cache d'idempotence en mÃ©moire** pour courses â€” incompatible multi-instance | `src/api/routes/courses.py` | Doublons possibles si plusieurs workers | A.11 |

### ðŸŸ¡ ModÃ©rÃ©s

| # | ProblÃ¨me | Fichier | Impact | Sprint |
| --- | ---------- | --------- | -------- | -------- |
| B6 | **Pas de rate limiting sur endpoints admin** | `src/api/routes/admin.py` | Potentiel DoS sur actions admin sensibles | A.5 |
| B7 | **Rate limiting IA global** vs per-user â€” ambiguÃ¯tÃ© | `src/core/ai/rate_limit.py` | Un utilisateur peut consommer le quota de tous | A.6 |
| B8 | **CORS avec origines par dÃ©faut** â€” devrait Ãªtre strict en prod | `src/api/main.py` | Risque CORS en production | A.7 |
| B9 | **Pas d'invalidation cache auto** quand modÃ¨les modifiÃ©s directement en DB | `src/core/caching/` | DonnÃ©es stales possibles aprÃ¨s update direct | A.12 |
| B10 | **CSP avec `unsafe-inline`** pour scripts/styles dans `next.config.ts` | `frontend/next.config.ts` | VulnÃ©rabilitÃ© XSS potentielle | A.13 |

### ðŸŸ¢ Mineurs

| # | ProblÃ¨me | Impact | Sprint |
| --- | ---------- | -------- | -------- |
| B11 | Certaines pages frontend sans skeleton/loading pendant le fetch initial | UX dÃ©gradÃ©e (flash of empty content) | A.8 |
| B12 | WebSocket hooks â€” nettoyage on unmount Ã  vÃ©rifier | Fuite mÃ©moire potentielle | A.9 |
| B13 | Toast notifications auto-dismiss â€” pas extensible par l'utilisateur | Messages importants potentiellement ratÃ©s | A.14 |
| B14 | Pas de retry auto sur erreurs DB transitoires | Erreurs intermittentes non rÃ©cupÃ©rÃ©es | A.15 |
| B15 | Auth WebSocket â€” documentation manquante sur la validation JWT | Confusion sur la sÃ©curisation des WS | A.10 |

---

## RÃ©fÃ©rentiel Gaps & Features manquantes

### Backend â€” Endpoints/Services manquants

| # | Gap | Module | Effort | PrioritÃ© |
| --- | ----- | -------- | -------- | ---------- |
| G1 | **Dashboard personnalisable** â€” pas de CRUD widgets par utilisateur | Dashboard | M | ðŸ”´ Haute |
| G2 | **Historique des modifications** (audit trail) pour recettes/planning | Cuisine | M | ðŸŸ¡ Moyenne |
| G3 | **Mode collaboratif** courses temps rÃ©el â€” WebSocket implÃ©mentÃ© mais UX basique | Courses | L | ðŸŸ¡ Moyenne |
| G4 | **Import bulk recettes** â€” import CSV/JSON en masse | Cuisine | S | ðŸŸ¢ Basse |
| G5 | **Scan ticket de caisse** â†’ dÃ©penses auto (OCR) | Famille | L | ðŸŸ¡ Moyenne |
| G6 | **Comparateur de prix** â€” historique prix par article | Courses | L | ðŸŸ¡ Moyenne |
| G7 | **Planning adaptatif** â€” ajuste automatiquement selon mÃ©tÃ©o/saison | Planning | L | ðŸŸ¢ Innovation |
| G8 | **Suivi Ã©nergie dÃ©taillÃ©** â€” graphiques conso par appareil | Maison | M | ðŸŸ¡ Moyenne |
| G9 | **Calendrier partagÃ© famille** â€” sync Google/Apple Calendar bidirectionnelle | Planning | L | ðŸ”´ Haute |
| G10 | **Mode hors-ligne enrichi** â€” sync diffÃ©rÃ©e des modifications | Global | XL | ðŸŸ¡ Moyenne |

### Frontend â€” Pages incomplÃ¨tes

| # | Page | Ã‰tat | Action requise | Sprint |
| --- | ------ | ------ | ---------------- | -------- |
| G11 | `/ia-avancee/suggestions-achats` | âœ… Fait | Cloture | C.1 |
| G12 | `/ia-avancee/diagnostic-plante` | âœ… Fait | Cloture | C.2 |
| G13 | `/ia-avancee/planning-adaptatif` | âœ… Fait | Cloture | C.3 |
| G14 | `/ia-avancee/analyse-photo` | âœ… Fait | Cloture | C.4 |
| G15 | `/ia-avancee/optimisation-routines` | âœ… Fait | Cloture | C.5 |
| G16 | `/ia-avancee/recommandations-energie` | âœ… Fait | Cloture | C.6 |
| G17 | `/ia-avancee/prevision-depenses` | âœ… Fait | Cloture | C.7 |
| G18 | `/ia-avancee/idees-cadeaux` | âœ… Fait | Cloture | C.8 |
| G19 | `/ia-avancee/analyse-document` | âœ… Fait | Cloture | C.9 |
| G20 | `/ia-avancee/estimation-travaux` | âœ… Fait | Cloture | C.10 |
| G21 | `/ia-avancee/planning-voyage` | âœ… Fait | Cloture | C.11 |
| G22 | `/ia-avancee/adaptations-meteo` | âœ… Fait | Cloture | C.12 |
| G23 | Error boundaries sur `planning`, `habitat`, `ia-avancee` | âœ… Fait | Cloture | C.15 |
| G24 | Loading states (skeletons) manquants sur pages hub | `planning`, `habitat`, `maison` sous-pages | Ajouter `loading.tsx` | A.8 |

### API Client â†” Backend â€” DÃ©salignements

| # | ProblÃ¨me | Action | Sprint |
| --- | ---------- | -------- | -------- |
| G25 | `ia_avancee.ts` est aligne sur les 14 outils du hub | âœ… Resolu | C.13 |
| G26 | Endpoints admin riches cÃ´tÃ© backend, frontend admin basique | âœ… Resolu (pages admin enrichies) | C.16 |
| G27 | RGPD (export/suppression donnÃ©es) â€” client existe mais pas de page dÃ©diÃ©e | âœ… Resolu (section RGPD dans `/parametres`) | C.17 |

---

## RÃ©fÃ©rentiel Consolidation SQL

### ProblÃ¨mes identifiÃ©s

| # | ProblÃ¨me | Impact | Action | Sprint |
| --- | ---------- | -------- | -------- | -------- |
| S1 | **INIT_COMPLET.sql monolithique** (3000+ lignes) â€” difficile Ã  naviguer | Maintenance | DÃ©couper en fichiers thÃ©matiques | H.1, H.2 |
| S2 | **Tables utilitaires orphelines** â€” `notes_memos`, `presse_papier_entrees`, `releves_energie` sans ORM complet | DonnÃ©es inaccessibles | CrÃ©er/complÃ©ter les modÃ¨les ORM | H.3 |
| S3 | **Pas de vÃ©rification auto** SQL â†” ORM en CI | DÃ©rives silencieuses possibles | Ajouter `test_schema_coherence.py` au CI | B.15 |
| S4 | **Indexes manquants** potentiels sur colonnes frÃ©quemment filtrÃ©es | Performance | Audit des queries lentes | H.4 |
| S5 | **Migrations non versionnÃ©es** en dev â€” OK mais risque de conflits | Team dev | Documenter le workflow SQL-first | H.5 |

---

## RÃ©fÃ©rentiel Couverture de tests

### Backend â€” Tests par couche

| Couche | Fichiers | Tests | Couverture | Cible | Ã‰tat |
| -------- | ---------- | ------- | ------------ | ------- | ------ |
| **Core** (config, DB, cache, decorators) | 12 fichiers | ~100 tests | 90% | 95% | âœ… Solide |
| **ModÃ¨les ORM** | 22 fichiers | ~80 tests | 70% | 85% | âš ï¸ Partiel |
| **Routes API** | 30 fichiers | ~150 tests | 77% | 90% | âš ï¸ 9 routes non testÃ©es |
| **Services** | 20+ fichiers | ~100 tests | 90% | 95% | âœ… Solide |
| **SpÃ©cialisÃ©s** (contrats, perf, SQL) | 5 fichiers | ~30 tests | Variable | â€” | âœ… |
| **Total Backend** | **70+ fichiers** | **~460 tests** | **~75%** | **85%** | âš ï¸ |

### Routes API sans tests (9 routes)

| Route | Fichier | PrioritÃ© test | Sprint |
| ------- | --------- | --------------- | -------- |
| `dashboard` | `src/api/routes/dashboard.py` | ðŸ”´ Haute | B.1 |
| `famille_jules` | `src/api/routes/famille_jules.py` | ðŸ”´ Haute | B.2 |
| `famille_budget` | `src/api/routes/famille_budget.py` | ðŸŸ¡ Moyenne | B.3 |
| `famille_activites` | `src/api/routes/famille_activites.py` | ðŸŸ¡ Moyenne | B.4 |
| `maison_projets` | `src/api/routes/maison_projets.py` | ðŸŸ¡ Moyenne | B.5 |
| `maison_jardin` | `src/api/routes/maison_jardin.py` | ðŸŸ¡ Moyenne | B.6 |
| `maison_finances` | `src/api/routes/maison_finances.py` | ðŸŸ¡ Moyenne | B.7 |
| `maison_entretien` | `src/api/routes/maison_entretien.py` | ðŸŸ¡ Moyenne | B.8 |
| `partage` | `src/api/routes/partage.py` | ðŸŸ¢ Basse | B.9 |

### Frontend â€” Couverture tests

| Type | Fichiers | Couverture | Ã‰tat |
| ------ | ---------- | ------------ | ------ |
| **Unit (Vitest)** | ~5 fichiers (stores + API clients) | Faible (~20%) | ðŸ”´ Ã€ renforcer |
| **E2E (Playwright)** | 12 fichiers | Bonne (smoke tests) | âœ… |
| **Visual Regression** | 1 fichier | Basique | âš ï¸ |

### Plan d'amÃ©lioration tests

```
Objectif : 85% couverture backend, 50% frontend unit

Backend â€” PrioritÃ© 1 :
  â”œâ”€â”€ tests/api/test_routes_dashboard.py (CRUD dashboard + widgets)
  â”œâ”€â”€ tests/api/test_routes_famille_jules.py (profil, jalons, suggestions IA)
  â”œâ”€â”€ tests/api/test_routes_famille_budget.py (dÃ©penses, budgets, historique)
  â”œâ”€â”€ tests/api/test_routes_maison_projets.py (projets, tÃ¢ches, budget)
  â””â”€â”€ tests/api/test_routes_partage.py (partage recettes, listes)

Backend â€” PrioritÃ© 2 :
  â”œâ”€â”€ tests/api/test_routes_famille_activites.py
  â”œâ”€â”€ tests/api/test_routes_maison_jardin.py
  â”œâ”€â”€ tests/api/test_routes_maison_finances.py
  â””â”€â”€ tests/api/test_routes_maison_entretien.py

Frontend â€” PrioritÃ© 1 :
  â”œâ”€â”€ src/__tests__/hooks/ (tests des custom hooks : utiliser-api, utiliser-auth)
  â”œâ”€â”€ src/__tests__/components/ (composants critiques : formulaire-recette, sidebar)
  â””â”€â”€ src/__tests__/pages/ (tests de rendering des pages hub)

Frontend â€” PrioritÃ© 2 :
  â”œâ”€â”€ E2E complets pour chaque module (pas juste smoke)
  â””â”€â”€ Tests d'accessibilitÃ© (axe-core)
```

---

## RÃ©fÃ©rentiel Documentation

### Documents existants â€” Ã‰tat

| Document | Statut | Notes |
| ---------- | -------- | ------- |
| `docs/ARCHITECTURE.md` | âœ… Ã€ jour | Architecture complÃ¨te FastAPI + Next.js |
| `docs/API_REFERENCE.md` | âœ… Ã€ jour | 242+ endpoints documentÃ©s |
| `docs/MODULES.md` | âœ… Ã€ jour | Carte fonctionnelle des modules |
| `docs/SERVICES_REFERENCE.md` | âœ… Ã€ jour | Tous les services documentÃ©s |
| `docs/ERD_SCHEMA.md` | âš ï¸ Ã€ rafraÃ®chir | Diagramme Mermaid Ã  regenerer (143 tables) |
| `docs/PATTERNS.md` | âœ… Ã€ jour | Patterns rÃ©silience, cache, events |
| `docs/CRON_JOBS.md` | âœ… Ã€ jour | 38+ jobs documentÃ©s |
| `docs/NOTIFICATIONS.md` | âœ… Ã€ jour | 4 canaux, throttling, digest |
| `docs/INTER_MODULES.md` | âœ… Ã€ jour | 8+ flux inter-modules |
| `docs/AI_SERVICES.md` | âœ… Ã€ jour | 23 services IA documentÃ©s |
| `docs/AUTOMATIONS.md` | âœ… Ã€ jour | Engine Ifâ†’Then |
| `docs/ADMIN_GUIDE.md` | âœ… Ã€ jour | Guide admin complet |
| `docs/ADMIN_RUNBOOK.md` | âœ… Ã€ jour | ProcÃ©dures opÃ©rationnelles |
| `docs/DEPLOYMENT.md` | âœ… Ã€ jour | Railway + Vercel + Supabase |
| `docs/TROUBLESHOOTING.md` | âœ… Ã€ jour | FAQ technique |
| `docs/DEVELOPER_SETUP.md` | âœ… Ã€ jour | Setup local |
| `docs/TESTING_ADVANCED.md` | âœ… Ã€ jour | Mutation + contract testing |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | âš ï¸ Peut Ãªtre enrichi | Exemples SQLAlchemy 2.0+ |
| `docs/REDIS_SETUP.md` | âš ï¸ Optionnel | Feature rarement utilisÃ©e |
| `docs/HABITAT_MODULE.md` | âœ… Nouveau | Module habitat complet |
| `docs/GAMIFICATION.md` | âœ… Nouveau | Badges sport + nutrition |
| `docs/WHATSAPP_SETUP.md` | âœ… Ã€ jour | Configuration Meta Cloud API |
| `docs/FRONTEND_ARCHITECTURE.md` | âœ… Ã€ jour | Architecture Next.js |
| `docs/UI_COMPONENTS.md` | âœ… Ã€ jour | Composants shadcn/ui |
| `docs/MIGRATION_GUIDE.md` | âœ… Ã€ jour | Workflow SQL-first |
| `docs/INDEX.md` | âœ… Ã€ jour | Index navigation |

### Documentation manquante

| # | Document manquant | RÃ©f | PrioritÃ© | Contenu attendu | Sprint |
| --- | ------------------- | ----- | ---------- | ----------------- | -------- |
| D2 | **Guide intÃ©gration Sentry** | â€” | ðŸŸ¡ Moyenne | Setup DSN, sampling, error boundaries, replay | H.16 |
| D3 | **Guide Docker production** | â€” | ðŸŸ¡ Moyenne | Railway-specific, performance tuning, scaling | H.17 |
| D4 | **Design System visuel** | â€” | ðŸŸ¢ Basse | Specs visuels composants (couleurs, spacing, typo) | H.18 |
| D5 | **Guide contribution** (CONTRIBUTING.md) | â€” | ðŸŸ¡ Moyenne | Conventions, PR process, code review | H.19 |
| D6 | **Changelog technique Phase 10** | â€” | ðŸŸ¡ Moyenne | DÃ©tails techniques des innovations | H.20 |
| D7 | **Guide PWA/Offline** | â€” | ðŸŸ¢ Basse | Service Worker, cache strategies, sync | H.21 |
| D8 | **SchÃ©ma d'architecture Mermaid** complet | â€” | ðŸŸ¡ Moyenne | Diagramme architectural Ã  jour | H.22 |

### Guides modules â€” Couverture

| Module | Guide | Ã‰tat |
| -------- | ------- | ------ |
| ðŸ½ï¸ Cuisine | `docs/guides/cuisine/README.md` + `batch_cooking.md` | âœ… Complet |
| ðŸ‘¶ Famille | `docs/guides/famille/README.md` | âœ… Complet |
| ðŸ¡ Maison | `docs/guides/maison/README.md` | âœ… Complet |
| ðŸ“Š Dashboard | `docs/guides/dashboard/README.md` | âœ… Complet |
| ðŸŽ® Jeux | `docs/guides/jeux/README.md` | âœ… Complet |
| ðŸ› ï¸ Outils | `docs/guides/outils/README.md` | âœ… Complet |
| ðŸ“… Planning | `docs/guides/planning/README.md` | âœ… Complet |
| ðŸ˜ï¸ Habitat | `docs/HABITAT_MODULE.md` | âœ… Complet |
| ðŸ¤– IA AvancÃ©e | `docs/guides/ia-avancee/README.md` + `docs/guides/IA_AVANCEE.md` | âœ… Complet |
| âš™ï¸ Admin | `docs/ADMIN_GUIDE.md` | âœ… Complet |

---

## RÃ©fÃ©rentiel Interactions intra-modules

### ðŸ½ï¸ Cuisine (Recettes â†’ Planning â†’ Courses â†’ Inventaire â†’ Batch Cooking)

```
Recettes â”€â”€planifierâ”€â”€â†’ Planning â”€â”€gÃ©nÃ©rerâ”€â”€â†’ Liste Courses
    â”‚                      â”‚                      â”‚
    â”‚                      â–¼                      â–¼
    â”‚               Batch Cooking           Inventaire
    â”‚                      â”‚                      â”‚
    â””â”€â”€versions julesâ”€â”€â”€â”€â”€â”€â”˜â”€â”€dÃ©crÃ©menter stockâ”€â”€â†’â”˜
```

| Flux | Ã‰tat | Action |
| ------ | ------ | -------- |
| Recette â†’ ajouter au planning | âœ… ImplÃ©mentÃ© | â€” |
| Planning â†’ gÃ©nÃ©rer liste courses | âœ… ImplÃ©mentÃ© | â€” |
| Courses achetÃ©es â†’ mettre Ã  jour inventaire | âœ… ImplÃ©mentÃ© | â€” |
| Inventaire bas â†’ suggestion recettes avec dispo | âš ï¸ Partiel | Enrichir avec IA |
| Batch cooking â†’ dÃ©crÃ©menter stocks | âœ… ImplÃ©mentÃ© | â€” |
| Recette â†’ version Jules (bÃ©bÃ©) | âœ… ImplÃ©mentÃ© | â€” |
| Anti-gaspillage â†’ suggestion recettes pÃ©remption | âœ… ImplÃ©mentÃ© | â€” |
| **MANQUANT** : Retour recette â†’ ajuster suggestions futures | âŒ | ImplÃ©menter feedback loop IA (Sprint D.5) |
| **MANQUANT** : Historique repas â†’ Ã©viter rÃ©pÃ©titions | âš ï¸ Partiel | Algorithme de diversitÃ© |

### ðŸ‘¶ Famille (Jules â†’ ActivitÃ©s â†’ Budget â†’ SantÃ© â†’ Documents)

| Flux | Ã‰tat | Action |
| ------ | ------ | -------- |
| Profil Jules â†’ suggestions activitÃ©s par Ã¢ge | âœ… ImplÃ©mentÃ© | â€” |
| ActivitÃ©s â†’ suivi jalons dÃ©veloppement | âœ… ImplÃ©mentÃ© | â€” |
| Budget famille â†’ suivi dÃ©penses | âœ… ImplÃ©mentÃ© | â€” |
| Anniversaires â†’ rappels + budget cadeaux | âœ… ImplÃ©mentÃ© | â€” |
| Documents â†’ alertes expiration | âœ… ImplÃ©mentÃ© | â€” |
| Voyages â†’ checklists + budget | âœ… ImplÃ©mentÃ© | â€” |
| **MANQUANT** : Jalons Jules â†’ cours/activitÃ©s recommandÃ©s | âŒ | IA recommandation |
| **MANQUANT** : Budget â†’ alertes seuil dÃ©passement | âš ï¸ Partiel | Notification push (Sprint D.3) |

### ðŸ¡ Maison (Projets â†’ Entretien â†’ Jardin â†’ Ã‰nergie â†’ Stocks)

| Flux | Ã‰tat | Action |
| ------ | ------ | -------- |
| Projets â†’ tÃ¢ches â†’ suivi avancement | âœ… ImplÃ©mentÃ© | â€” |
| Entretien prÃ©ventif â†’ calendrier tÃ¢ches | âœ… ImplÃ©mentÃ© | â€” |
| Jardin â†’ calendrier saisons â†’ tÃ¢ches | âœ… ImplÃ©mentÃ© | â€” |
| Stocks maison â†’ alertes rÃ©approvisionnement | âœ… ImplÃ©mentÃ© | â€” |
| Ã‰nergie â†’ relevÃ©s compteurs â†’ graphiques | âœ… ImplÃ©mentÃ© | â€” |
| **MANQUANT** : Entretien â†’ devis artisans auto | âŒ | Lier artisans + estimations (Sprint D.12) |
| **MANQUANT** : Projets terminÃ©s â†’ mise Ã  jour valeur bien | âŒ | Impact habitat (Sprint D.11) |

### ðŸŽ® Jeux (Paris â†’ Loto â†’ EuroMillions â†’ Bankroll â†’ Performance)

| Flux | Ã‰tat | Action |
| ------ | ------ | -------- |
| Analyse matchs â†’ paris proposÃ©s | âœ… ImplÃ©mentÃ© | â€” |
| Backtest stratÃ©gies â†’ scoring | âœ… ImplÃ©mentÃ© | â€” |
| Bankroll â†’ suivi P&L | âœ… ImplÃ©mentÃ© | â€” |
| Stats historiques â†’ heatmaps numÃ©ros | âœ… ImplÃ©mentÃ© | â€” |
| **MANQUANT** : RÃ©sultats auto â†’ P&L instantanÃ© | âš ï¸ Cron existe | Affichage temps rÃ©el |

---

## RÃ©fÃ©rentiel Interactions inter-modules

### Flux existants (8 implÃ©mentÃ©s)

| # | Flux | Source â†’ Cible | Fichier | Trigger |
| --- | ------ | ---------------- | --------- | --------- |
| 1 | PÃ©remption â†’ Recettes | Inventaire â†’ Cuisine | `inter_module_peremption_recettes.py` | Job/API |
| 2 | Total courses â†’ Budget | Courses â†’ Famille | `inter_module_courses_budget.py` | Save courses |
| 3 | Document expire â†’ Alerte | Famille â†’ Notifications | `inter_module_documents_notifications.py` | Job J-30/15/7/1 |
| 4 | Chat IA â†’ Multi-contexte | Tous â†’ Utilitaires | `inter_module_chat_contexte.py` | Chat appel |
| 5 | Batch cooking â†’ Stock | Cuisine â†’ Inventaire | `inter_module_batch_inventaire.py` | Fin session |
| 6 | Anniversaires â†’ Budget | Famille â†’ Famille | `inter_module_anniversaires_budget.py` | Auto |
| 7 | Voyages â†’ Budget | Voyages â†’ Famille | `inter_module_voyages_budget.py` | Save voyage |
| 8 | Mises jeux â†’ Budget | Jeux â†’ Famille | `inter_module_budget_jeux.py` | Mise placÃ©e |

### Flux Ã  implÃ©menter (15 opportunitÃ©s)

| # | Flux proposÃ© | Source â†’ Cible | Valeur | Effort | Sprint |
| --- | ------------- | ---------------- | -------- | -------- | -------- |
| I1 | **RÃ©colte jardin â†’ Recettes saison** (proposÃ©es au prochain planning semaine) | Maison/Jardin â†’ Cuisine | ðŸ”´ Haute | M | D.1 |
| I2 | **Garmin santÃ© â†’ ActivitÃ©s Jules** | Famille/Garmin â†’ Famille/Jules | ðŸŸ¡ Moyenne | M | D.8 |
| I3 | **Anomalie Ã©nergie â†’ TÃ¢che entretien** | Maison/Ã‰nergie â†’ Maison/Entretien | ðŸ”´ Haute | S | D.2 |
| I4 | **Budget dÃ©passement â†’ Alerte dashboard** | Famille/Budget â†’ Dashboard | ðŸ”´ Haute | S | D.3 |
| I5 | **MÃ©tÃ©o â†’ Planning repas adaptÃ©** | Outils/MÃ©tÃ©o â†’ Cuisine/Planning | ðŸŸ¡ Moyenne | M | D.9 |
| I6 | **MÃ©tÃ©o â†’ TÃ¢ches jardin urgentes** | Outils/MÃ©tÃ©o â†’ Maison/Jardin | ðŸŸ¡ Moyenne | S | D.10 |
| I7 | **Projets terminÃ©s â†’ Valeur bien habitat** | Maison/Projets â†’ Habitat | ðŸŸ¡ Moyenne | M | D.11 |
| I8 | **Entretien artisan â†’ Devis comparatif auto** | Maison/Entretien â†’ Maison/Artisans | ðŸŸ¡ Moyenne | M | D.12 |
| I9 | **Inventaire â†’ Courses prÃ©dictives** | Inventaire â†’ Courses | ðŸ”´ Haute | L | D.4 |
| ~~I10~~ | ~~RÃ©sultats paris â†’ P&L famille~~ | ~~Jeux â†’ Famille/Budget~~ | âŒ **RejetÃ©** | â€” | â€” |
| I11 | **Routines santÃ© â†’ Briefing matinal** | Famille/SantÃ© â†’ Dashboard | ðŸŸ¡ Moyenne | S | D.13 |
| I12 | **Anniversaire â†’ Suggestion cadeau IA** | Famille â†’ IA AvancÃ©e | ðŸŸ¢ Innovation | M | D.14 |
| I13 | **Retour recette â†’ Ajuster planning futur** | Cuisine â†’ Planning | ðŸ”´ Haute | M | D.5 |
| I14 | **Contrats maison â†’ Alertes renouvellement** | Maison/Contrats â†’ Notifications | ðŸŸ¡ Moyenne | S | D.6 |
| I15 | **Score gamification â†’ RÃ©compenses famille** | Gamification â†’ Famille | ðŸŸ¢ Innovation | M | D.15 |

---

## RÃ©fÃ©rentiel OpportunitÃ©s IA

### Services IA existants (23 services)

| Service | Module | FonctionnalitÃ© |
| --------- | -------- | ---------------- |
| `ChatAIService` | Outils | Chat multi-contexte |
| `BriefingMatinalService` | Dashboard | Briefing quotidien personnalisÃ© |
| `ServiceSuggestions` | Cuisine | Suggestions recettes |
| `ServiceVersionRecetteJules` | Famille | Adaptation recettes bÃ©bÃ© |
| `WeekendAIService` | Famille | IdÃ©es weekend |
| `SoireeAIService` | Famille | IdÃ©es soirÃ©e couple |
| `JulesAIService` | Famille | ActivitÃ©s par Ã¢ge |
| `ServiceResumeHebdo` | Famille | RÃ©sumÃ© hebdo narratif |
| `AchatsIAService` | Famille | Suggestions cadeaux |
| `BilanMensuelService` | Rapports | Bilan financier |
| `ProjetsService` | Maison | Estimation projets |
| `JardinService` | Maison | Conseils saisonniers |
| `EntretienService` | Maison | Optimisation nettoyage |
| `FicheTacheService` | Maison | Fiches tÃ¢ches mÃ©nage |
| `EnergieAnomaliesIAService` | Maison | DÃ©tection anomalies Ã©nergie |
| `ConseillierMaisonService` | Maison | Conseils contextuels |
| `DiagnosticsIAArtisansService` | Maison | Diagnostic pannes |
| `PlansHabitatAIService` | Habitat | Analyse plans |
| `DecoHabitatService` | Habitat | Concepts dÃ©co IA |
| `JeuxAIService` | Jeux | Analyse paris sportifs |
| `EuromillionsIAService` | Jeux | StratÃ©gies numÃ©riques |
| `ServiceAnomaliesFinancieres` | Dashboard | DÃ©tection anomalies dÃ©penses |
| `ResumeFamilleIAService` | Dashboard | RÃ©sumÃ© multi-module |

### Nouvelles opportunitÃ©s IA (14 propositions)

| # | OpportunitÃ© | Module | Description | Effort | Sprint |
| --- | ------------- | -------- | ------------- | -------- | -------- |
| IA1 | **Nutritionniste IA** | Cuisine | Analyse nutrition hebdo â†’ recommandations (protÃ©ines, fibres, vitamines) | M | I.16 |
| IA2 | **Coach budget IA** | Famille | Analyse tendances dÃ©penses â†’ suggestions Ã©conomies + benchmarks | M | I.17 |
| IA3 | **Planificateur voyages IA** | Famille | GÃ©nÃ©ration itinÃ©raire + checklist + budget prÃ©visionnel | L | I.18 |
| IA4 | **Diagnostic plante photo** | Maison | Upload photo plante â†’ diagnostic maladie + traitement (vision IA) | M | I.19 |
| IA5 | **Optimiseur courses prÃ©dictif** | Courses | ML sur historique achats â†’ liste courses prÃ©-remplie | L | I.20 |
| IA6 | **Assistant vocal enrichi** | Outils | Commandes vocales â†’ actions multi-modules | L | I.21 |
| IA7 | **RÃ©sumÃ© vocal quotidien** | Dashboard | TTS du briefing matinal â†’ Ã©coutable en voiture | M | I.22 |
| IA8 | **Styliste dÃ©co personnalisÃ©** | Habitat | Analyse photos piÃ¨ces â†’ suggestions dÃ©co personnalisÃ©es | L | I.23 |
| IA9 | **PrÃ©dicteur pannes** | Maison | ML sur Ã¢ge/usage appareils â†’ maintenance prÃ©ventive | M | I.24 |
| IA10 | **GÃ©nÃ©rateur menus Ã©vÃ©nements** | Cuisine | Menu complet anniversaire/fÃªte selon nb personnes + rÃ©gimes | M | I.25 |
| IA11 | **Analyseur ticket de caisse** | Famille | OCR ticket â†’ catÃ©gorisation auto dÃ©penses + promos | L | I.26 |
| IA12 | **Comparateur recettes nutritionnel** | Cuisine | Comparer 2 recettes â†’ diffÃ©rences nutritionnelles visuelles | S | I.27 |
| IA13 | **Assistant devis travaux** | Maison | Description travaux â†’ estimation prix + matÃ©riaux | M | I.28 |
| IA14 | **Coach routine bien-Ãªtre** | Famille | Analyse habitudes â†’ routines personnalisÃ©es selon Garmin | M | I.29 |

### Architecture IA â€” AmÃ©liorations suggÃ©rÃ©es

```
AmÃ©lioration 1 : Rate limit per-user (pas global)
  â†’ Chaque utilisateur a son propre quota IA
  â†’ EmpÃªche un user de bloquer tous les autres

AmÃ©lioration 2 : Cache sÃ©mantique enrichi
  â†’ Utiliser embeddings pour matcher des prompts similaires (pas juste hash exact)
  â†’ RÃ©duire les appels IA de 30-40%

AmÃ©lioration 3 : Fallback model
  â†’ Si Mistral down â†’ fallback vers un modÃ¨le local (Ollama) ou autre provider
  â†’ Circuit breaker dÃ©jÃ  en place, ajouter le fallback

AmÃ©lioration 4 : Feedback loop
  â†’ Stocker les retours utilisateurs (thumbs up/down) sur les suggestions IA
  â†’ Utiliser comme contexte pour amÃ©liorer les prompts
```

---

## RÃ©fÃ©rentiel Jobs CRON

### Jobs existants (38+ planifiÃ©s)

#### Rappels & Alertes

| Job | Schedule | Description | Canal |
| ----- | ---------- | ------------- | ------- |
| `rappels_famille` | 7h00 | Rappels activitÃ©s/RDV du jour | push, ntfy |
| `rappels_maison` | 8h00 | TÃ¢ches entretien du jour | push, ntfy |
| `alertes_peremption_48h` | 6h00 | Produits expirant dans 48h | push, ntfy |
| `alertes_stocks_bas` | Lun 9h | Stocks sous seuil | push |
| `rappels_documents_expirants` | 8h30 | Documents J-30/15/7/1 | push, email |
| `rappels_vaccins` | 8h15 | Vaccins Ã  planifier | push, email |
| `alertes_contrats` | 8h45 | Contrats Ã  renouveler | push, email |

#### Notifications & Digests

| Job | Schedule | Description | Canal |
| ----- | ---------- | ------------- | ------- |
| `push_quotidien` | 9h00 | Push quotidien rÃ©sumÃ© | push |
| `digest_ntfy` | 9h00 | Digest via ntfy | ntfy |
| `digest_whatsapp_matinal` | 7h30 | Briefing matinal WhatsApp | whatsapp |
| `digest_email_hebdo` | Lun 8h | Digest email hebdomadaire | email |
| `digest_notifications_queue` | /2h | Flush file de notifications | multi |

#### Rapports & RÃ©sumÃ©s

| Job | Schedule | Description |
| ----- | ---------- | ------------- |
| `resume_hebdo` | Lun 7h30 | RÃ©sumÃ© hebdo IA narratif |
| `rapport_mensuel_budget` | 1er 8h15 | Bilan budget mensuel |
| `rapport_jardin` | Mer 20h | Rapport jardin hebdo |
| `bilan_mensuel_complet` | 1er 9h | Bilan multi-module |
| `score_weekend` | Ven 17h | Score prÃ©paration weekend |

#### Syncs & Scraping

| Job | Schedule | Description |
| ----- | ---------- | ------------- |
| `sync_calendrier_scolaire` | 5h30 | Sync vacances scolaires |
| `sync_google_calendar` | 23h | Sync calendrier Google |
| `sync_openfoodfacts` | Dim 3h | Sync donnÃ©es nutritionnelles |
| `sync_garmin` | 6h | Sync donnÃ©es Garmin |
| `scraping_paris_cotes` | /2h | Scraping cotes sportives |
| `scraping_paris_resultats` | 23h | RÃ©sultats matchs |
| `scraping_fdj_resultats` | 21h30 | RÃ©sultats Loto/EuroMillions |
| `backtest_grilles` | 22h | Backtest stratÃ©gies loto |
| `detection_value_bets` | /30min | DÃ©tection paris value |
| `analyse_series` | 9h | Analyse sÃ©ries jeux |

#### Maintenance

| Job | Schedule | Description |
| ----- | ---------- | ------------- |
| `nettoyage_cache` | 3h | Purge cache pÃ©rimÃ© |
| `nettoyage_logs` | 4h | Rotation logs anciens |
| `automations_runner` | /5min | ExÃ©cution automations Ifâ†’Then |
| `health_check_services` | /15min | VÃ©rification santÃ© services |
| `backup_etats_persistants` | 2h | Sauvegarde Ã©tats |

### Jobs CRON Ã  ajouter (8 propositions)

| # | Job proposÃ© | Schedule | Description | PrioritÃ© | Sprint |
| --- | ------------- | ---------- | ------------- | ---------- | -------- |
| C1 | `prediction_courses_hebdo` | Dim 18h | GÃ©nÃ©rer liste courses prÃ©dictive pour la semaine | ðŸ”´ | E.9 |
| C2 | `rapport_energie_mensuel` | 1er 10h | Rapport conso Ã©nergie + comparaison mois prÃ©cÃ©dent | ðŸŸ¡ | E.10 |
| C3 | `suggestions_recettes_saison` | 1er et 15 6h | Nouvelles recettes de saison Ã  dÃ©couvrir | ðŸŸ¡ | E.11 |
| C4 | `audit_securite_hebdo` | Dim 2h | VÃ©rification intÃ©gritÃ© donnÃ©es + logs suspects | ðŸŸ¡ | E.12 |
| C5 | `nettoyage_notifications_anciennes` | Dim 4h | Purger notifications > 90 jours | ðŸŸ¢ | E.13 |
| C6 | `mise_a_jour_scores_gamification` | Minuit | Recalculer scores/badges quotidiens | ðŸŸ¡ | E.14 |
| C7 | `alerte_meteo_jardin` | 7h | Alerte gel/canicule â†’ protÃ©ger plantes | ðŸŸ¡ | E.15 |
| C8 | `resume_financier_semaine` | Ven 18h | RÃ©sumÃ© dÃ©penses de la semaine | ðŸŸ¡ | E.16 |

---

## RÃ©fÃ©rentiel Notifications

### Architecture

```
DispatcherNotifications (central)
â”œâ”€â”€ ntfy.sh        â†’ REST API â†’ push notifications
â”œâ”€â”€ Web Push       â†’ VAPID protocol â†’ navigateur
â”œâ”€â”€ Email          â†’ Resend API â†’ Jinja2 templates
â””â”€â”€ WhatsApp       â†’ Meta Cloud API â†’ webhook bidirectionnel
```

### Ã‰tat par canal

| Canal | Ã‰tat | FonctionnalitÃ©s | Manques |
| ------- | ------ | ----------------- | --------- |
| **ntfy** | âœ… OpÃ©rationnel | Push simple, digest | â€” |
| **Web Push** | âœ… OpÃ©rationnel | Abonnement VAPID, notifications navigateur | Tests E2E push |
| **Email** | âœ… OpÃ©rationnel | 7 templates Jinja2 (reset pwd, vÃ©rif, digest, rapport, alerte, invitation, digest) | Template personnalisation |
| **WhatsApp** | âœ… OpÃ©rationnel | Webhook Meta, boutons interactifs (planning valider/modifier/rÃ©gÃ©nÃ©rer) | Conversations enrichies |

### AmÃ©liorations proposÃ©es

| # | AmÃ©lioration | Canal | Description | Effort | Sprint |
| --- | ------------- | ------- | ------------- | -------- | -------- |
| N1 | **WhatsApp : Flux courses** | WhatsApp | "Voici ta liste courses de la semaine" + bouton "Ajouter au panier" | M | E.1 |
| N2 | **WhatsApp : Rappel activitÃ© Jules** | WhatsApp | "C'est l'heure de l'activitÃ© de Jules!" + suggestion | S | E.2 |
| N3 | **WhatsApp : RÃ©sultats paris** | WhatsApp | "Match terminÃ© : Paris SG 2-1 â†’ Tu as gagnÃ© !" | S | E.3 |
| N4 | **WhatsApp : Mode conversationnel** | WhatsApp | Ã‰tat machine plus riche â€” gestion multi-Ã©tapes | L | Backlog |
| N5 | **Email : Newsletter hebdo** | Email | Template riche avec images, graphiques inline, call-to-action | M | E.6 |
| N6 | **Email : Rapport budget PDF** | Email | PDF en piÃ¨ce jointe (dÃ©jÃ  gÃ©nÃ©rÃ©, ajouter l'envoi) | S | E.7 |
| N7 | **Push : Actions rapides** | Push | Notifications avec boutons d'action (ex: "Valider" / "Reporter") | M | E.8 |
| ~~N8~~ | ~~Push : GÃ©olocalisation~~ | ~~Push~~ | âŒ **RejetÃ©** (habite Ã  cÃ´tÃ© du supermarchÃ©) | â€” | â€” |
| N9 | **PrÃ©fÃ©rences granulaires** | Tous | UI pour choisir par type d'Ã©vÃ©nement quel canal utiliser | M | E.4 |
| N10 | **Historique notifications** | Tous | Page "Centre de notifications" dans l'app | M | E.5 |

---

## RÃ©fÃ©rentiel Mode Admin

### FonctionnalitÃ©s existantes

| Feature | Endpoint | Ã‰tat |
| --------- | ---------- | ------ |
| Liste jobs | `GET /api/v1/admin/jobs` | âœ… |
| Trigger manuel | `POST /api/v1/admin/jobs/{id}/run` | âœ… (rate limit 5/min) |
| Dry run | `POST /api/v1/admin/jobs/{id}/run?dry_run=true` | âœ… |
| Logs jobs | `GET /api/v1/admin/jobs/{id}/logs` | âœ… |
| Audit logs | `GET /api/v1/admin/audit-logs` | âœ… |
| Stats audit | `GET /api/v1/admin/audit-stats` | âœ… |
| Export audit CSV | `GET /api/v1/admin/audit-export` | âœ… |
| Health check services | `GET /api/v1/admin/services/health` | âœ… |
| Test notifications | `POST /api/v1/admin/notifications/test` | âœ… |
| Stats cache | `GET /api/v1/admin/cache/stats` | âœ… |
| Purge cache | `POST /api/v1/admin/cache/clear` | âœ… |
| Liste users | `GET /api/v1/admin/users` | âœ… |
| DÃ©sactiver user | `POST /api/v1/admin/users/{id}/disable` | âœ… |
| CohÃ©rence DB | `GET /api/v1/admin/db/coherence` | âœ… |
| Feature flags | `GET/PUT /api/v1/admin/feature-flags` | âœ… |
| Runtime config | `GET/PUT /api/v1/admin/config` | âœ… |
| Flow simulator | `POST /api/v1/admin/simulate-flow` | âœ… |

### AmÃ©liorations proposÃ©es

| # | AmÃ©lioration | Description | Effort | PrioritÃ© | Sprint |
| --- | ------------- | ------------- | -------- | ---------- | -------- |
| A1 | **Dashboard admin dÃ©diÃ©** | Graphiques : jobs exÃ©cutÃ©s, erreurs, usage IA, notifications | M | ðŸŸ¢ | F.1 |
| A2 | **Console IA admin** | Tester un prompt IA directement depuis l'admin â†’ voir rÃ©ponse brute | S | ðŸŸ¢ | F.2 |
| A3 | **Seed data one-click** | Bouton pour peupler la DB avec donnÃ©es de test (dev only) | S | ðŸŸ¡ | F.3 |
| A4 | **Reset module** | Bouton pour vider les donnÃ©es d'un module spÃ©cifique (dev only) | S | ðŸŸ¢ | F.8 |
| A5 | **Export DB complet** | Export JSON/SQL complet de toutes les donnÃ©es utilisateur | M | ðŸŸ¢ | F.9 |
| A6 | **Import DB** | Import JSON/SQL pour restaurer un backup | M | ðŸŸ¢ | F.10 |
| A7 | **Monitoring temps rÃ©el** | WebSocket admin â†’ mÃ©triques live (requÃªtes/s, erreurs, cache hits) | L | ðŸŸ¢ | F.11 |
| A8 | **Queue de notifications** | Voir et gÃ©rer la file d'attente des notifications pendantes | S | ðŸŸ¢ | F.6 |
| A9 | **Historique jobs paginated** | Vue paginÃ©e de tous les runs de jobs avec filtres | M | ðŸŸ¡ | F.7 |
| A10 | **Toggle maintenance mode** | Activer un mode maintenance avec bandeau utilisateur | S | ðŸŸ¡ | F.5 |

---

## RÃ©fÃ©rentiel Simplification UX

### Flux Ã  simplifier (10 amÃ©liorations)

| # | Flux actuel | ProblÃ¨me | Flux proposÃ© | Effort | Sprint |
| --- | ------------- | ---------- | -------------- | -------- | -------- |
| U1 | **Planifier repas** : Planning â†’ Jour â†’ Recette â†’ SÃ©lectionner | 4 clics minimum | **1 clic** : "Planifier ma semaine" â†’ IA gÃ©nÃ¨re â†’ Valider/ajuster | S | G.1 |
| U2 | **Ajouter aux courses** : Courses â†’ CrÃ©er liste â†’ Ajouter un par un | Fastidieux | **Auto** : Depuis planning â†’ "GÃ©nÃ©rer courses" â†’ Liste prÃ©-remplie | S | G.2 |
| U3 | **Consulter dÃ©penses** : Famille â†’ Budget â†’ Filtrer â†’ Lire | DispersÃ© | **Dashboard** : Widget budget avec tendance en page d'accueil | S | G.3 |
| U4 | **Trouver recette** : Cuisine â†’ Recettes â†’ Filtres â†’ Parcourir | Long | **Recherche globale** : Barre de recherche â†’ rÃ©sultats instantanÃ©s | M | G.4 |
| U5 | **CrÃ©er projet maison** : Maison â†’ Projets â†’ Formulaire complet | Formulaire lourd | **Wizard 3 Ã©tapes** : Nom â†’ Type/Budget â†’ TÃ¢ches IA | M | G.5 |
| U6 | **VÃ©rifier inventaire** : Cuisine â†’ Inventaire â†’ Parcourir | Pas intuitif | **Alertes proactives** : Notif quand stock bas â†’ action directe | S | G.6 |
| U7 | **Suivre Jules** : Famille â†’ Jules â†’ Onglets multiples | Complexe | **Timeline Jules** : Vue chronologique unique jalons + activitÃ©s + santÃ© | M | G.7 |
| U8 | **GÃ©rer entretien** : Maison â†’ Entretien â†’ Voir â†’ Marquer | Pas engageant | **Checklist du jour** : Widget dashboard + swipe pour valider | S | G.8 |
| U9 | **Consulter mÃ©tÃ©o** : Outils â†’ MÃ©tÃ©o â†’ Page dÃ©diÃ©e | DÃ©tour | **Widget intÃ©grÃ©** : MÃ©tÃ©o dans header/dashboard + suggestions adaptÃ©es | S | G.9 |
| U10 | **ParamÃ©trer notifs** : ParamÃ¨tres â†’ Notifications â†’ Toggle | GranularitÃ© floue | **Par module** : "Me notifier pour..." dans chaque module | M | G.10 |

### Composants UX Ã  ajouter

| # | Composant | Description | Impact | Sprint |
| --- | ----------- | ------------- | -------- | -------- |
| UX1 | **Quick Actions FAB** (enrichir) | Bouton flottant avec actions rapides contextuelles | Navigation rapide | G.13 |
| UX2 | **Command Palette** (enrichir) | `Cmd+K` naviguer/agir partout (`menu-commandes.tsx`) | Power users | G.14 |
| UX3 | **Onboarding tour** (amÃ©liorer) | Tour guidÃ© au premier lancement (`tour-onboarding.tsx`) | DÃ©couvrabilitÃ© | G.15 |
| UX4 | **Empty states riches** | Module vide â†’ message + CTA pour commencer | Engagement | G.16 |
| UX5 | **Skeleton screens** (complÃ©ter) | Loading skeletons sur toutes les pages | UX perÃ§ue | G.17 |
| UX6 | **Swipe gestures mobile** (gÃ©nÃ©raliser) | Swipe gauche/droite sur items de liste | Mobile fluide | G.18 |
| UX7 | **Cards drag & drop** | RÃ©organisation widgets dashboard (`grille-widgets.tsx`) | Personnalisation | G.19 |
| UX8 | **Confirmations inline** | Toasts au lieu de modals pour actions simples | Moins intrusif | G.20 |

---

## RÃ©fÃ©rentiel Organisation du code

### Backend â€” Points d'amÃ©lioration

| # | ProblÃ¨me | Action | Effort | Sprint |
| --- | ---------- | -------- | -------- | -------- |
| O1 | **Routes volumineuses** â€” certains fichiers > 500 lignes | DÃ©couper en sous-modules | M | H.6 |
| O2 | **Imports circulaires potentiels** entre services | Auditer avec `importlib` ou `pylint` | S | H.7 |
| O3 | **SchÃ©mas Pydantic dupliquÃ©s** entre `api/schemas/` et `core/validation/schemas/` | Unifier les responsabilitÃ©s | M | H.8 |
| O4 | **Tests dispersÃ©s** â€” nommage incohÃ©rent | Nommer de faÃ§on cohÃ©rente | S | H.9 |
| O5 | **Scripts archivÃ©s** toujours prÃ©sents | DÃ©placer vers `scripts/archive/` | S | H.10 |

### Frontend â€” Points d'amÃ©lioration

| # | ProblÃ¨me | Action | Effort | Sprint |
| --- | ---------- | -------- | -------- | -------- |
| O6 | **Composants habitat insuffisants** â€” 3 composants pour un module riche | Extraire composants rÃ©utilisables | M | H.11 |
| O7 | **Composants planning insuffisants** â€” 1 seul composant calendrier | Extraire timeline, week view, etc. | M | H.12 |
| O8 | **Pages monolithiques** â€” paramÃ¨tres > 1200 lignes | DÃ©couper en composants nommÃ©s | M | H.13 |
| O9 | **Tests unit frontend** â€” seulement ~5 fichiers | Plan de test complet | L | H.14 |
| O10 | **Pas de storybook** â€” composants UI non documentÃ©s visuellement | Optionnel mais recommandÃ© | L | Backlog |

---

## RÃ©fÃ©rentiel Axes d'innovation

### Innovations technologiques

| # | Innovation | Description | Impact | Effort | Sprint |
| --- | ----------- | ------------- | -------- | -------- | -------- |
| IN1 | **Mode famille multi-utilisateurs** | Chaque membre a son profil avec rÃ´les (parent, enfant, invitÃ©) | ðŸ”´ Transformant | XL | I.1 |
| IN2 | **Synchronisation temps rÃ©el** | WebSocket tous modules (pas juste courses) â†’ Ã©dition collaborative | ðŸŸ¡ Fort | L | I.2 |
| IN3 | **Widget smartphone** | Widgets iOS/Android natifs via PWA | ðŸŸ¡ Fort | L | I.3 |
| IN4 | **Mode vocal complet** | "Hey Matanne, qu'est-ce qu'on mange ce soir ?" â†’ TTS | ðŸŸ¢ Innovation | L | I.4 |
| IN5 | **Scan & Go** | Scanner code-barres â†’ inventaire + infos nutrition auto | ðŸŸ¡ Fort | M | I.5 |
| IN6 | **IntÃ©gration IoT** | Capteurs maison (tempÃ©rature, humiditÃ©, consommation) â†’ dashboards | ðŸŸ¢ Innovation | XL | I.6 |
| ~~IN7~~ | ~~Marketplace recettes~~ | âŒ **RejetÃ©** (pas de volet social) | â€” | â€” | â€” |
| IN8 | **Mode dÃ©connectÃ© enrichi** | IndexedDB + background sync â†’ fonctions de base hors-ligne | ðŸŸ¡ Fort | XL | I.7 |

### Innovations UX

| # | Innovation | Description | Impact | Effort | Sprint |
| --- | ----------- | ------------- | -------- | -------- | -------- |
| IN9 | **ThÃ¨mes saisonniers** | Interface s'adapte visuellement aux saisons | ðŸŸ¢ Fun | S | I.8 |
| IN10 | **Gamification sportive uniquement** | Points/badges sur donnÃ©es Garmin/activitÃ© physique | ðŸŸ¡ Fort | S | I.9 |
| IN11 | **Mode focus** | Vue Ã©purÃ©e "essentiel du jour" : 1 Ã©cran = mÃ©tÃ©o + repas + tÃ¢ches + rappels | ðŸ”´ Transformant | M | G.11 |
| IN12 | **Raccourcis Google Assistant** | Actions rapides via assistant vocal Google (tablette) | ðŸŸ¢ Innovation | M | I.10 |
| ~~IN13~~ | ~~QR code partage~~ | âŒ **RejetÃ©** (aucun intÃ©rÃªt) | â€” | â€” | â€” |
| IN14 | **Mode vacances** | Pause notifications non essentielles + checklist voyage auto | ðŸŸ¡ Fort | S | G.12 |

### Innovations Data & IA

| # | Innovation | Description | Impact | Effort | Sprint |
| --- | ----------- | ------------- | -------- | -------- | -------- |
| IN15 | **Analytics familiales** | Tendances long terme : nutrition, dÃ©penses, activitÃ©s, Ã©nergie â†’ graphiques | ðŸ”´ Transformant | L | I.11 |
| IN16 | **PrÃ©dictions ML** | ModÃ¨les prÃ©dictifs : courses, dÃ©penses, pannes | ðŸŸ¡ Fort | XL | I.12 |
| IN17 | **Benchmark famille** | Comparer (anonymement) ses habitudes avec moyennes nationales | ðŸŸ¢ Innovation | L | I.13 |
| ~~IN18~~ | ~~Export Notion/Obsidian~~ | âŒ **RejetÃ©** (pas d'intÃ©rÃªt) | â€” | â€” | â€” |
| IN19 | **IntÃ©gration bancaire** | Sync banque via API (Plaid/Bridge) â†’ dÃ©penses auto-catÃ©gorisÃ©es | ðŸ”´ Transformant | XL | I.14 |
| IN20 | **Agent IA proactif** | L'IA suggÃ¨re des actions avant la demande | ðŸŸ¡ Fort | M | I.15 |

---

## Annexes

### A. Inventaire complet des fichiers

| Dossier | Fichiers Python | Fichiers TS/TSX | Total |
| --------- | ---------------- | ----------------- | ------- |
| `src/api/` | ~45 | â€” | 45 |
| `src/core/` | ~55 | â€” | 55 |
| `src/services/` | ~80 | â€” | 80 |
| `tests/` | ~70 | â€” | 70 |
| `frontend/src/` | â€” | ~180 | 180 |
| **Total** | **~250** | **~180** | **~430** |

### B. DÃ©pendances clÃ©s

**Backend** : FastAPI, SQLAlchemy 2.0, Pydantic v2, Mistral AI, APScheduler, httpx, WeasyPrint, Pillow

**Frontend** : Next.js 16, React 19, TanStack Query 5, Zustand 5, Zod 4, Tailwind CSS 4, Chart.js, Three.js, Recharts, Axios, Playwright

### C. Infrastructure

| Service | RÃ´le | Provider |
| --------- | ------ | ---------- |
| Backend API | FastAPI (Python) | Railway |
| Frontend | Next.js (SSR) | Vercel |
| Database | PostgreSQL 16 | Supabase |
| Auth | JWT + Supabase Auth | Supabase |
| IA | Mistral AI API | Mistral |
| Notifications | ntfy, Resend, Meta | Multi |
| Monitoring | Sentry, Prometheus | Multi |
| CI/CD | GitHub Actions | GitHub |

### D. Variables d'environnement clÃ©s

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

### E. DÃ©cisions rejetÃ©es (historique)

| Proposition | Raison du rejet |
| ------------- | ----------------- |
| N8 : Push gÃ©olocalisation | Habite Ã  cÃ´tÃ© du supermarchÃ© |
| IN7 : Marketplace recettes | Pas de volet social/communautaire |
| IN10 : Gamification familiale gÃ©nÃ©rale | LimitÃ© au sport/Garmin uniquement |
| IN13 : QR code partage | Aucun intÃ©rÃªt |
| IN18 : Export Notion/Obsidian | Pas d'intÃ©rÃªt |
| I10 : RÃ©sultats paris â†’ P&L famille | Budget jeux volontairement sÃ©parÃ© |
| Jeu responsable | Feature entiÃ¨rement supprimÃ©e du codebase |

### F. PrÃ©cisions acceptÃ©es

| Proposition | PrÃ©cision |
| ------------- | ----------- |
| I1 : RÃ©colte jardin â†’ Recettes | Uniquement Ã  la prochaine semaine planifiÃ©e |
| IN12 : Assistant vocal | Google Assistant uniquement (pas Siri â€” tablette Google) |

---

> **Ce document est le plan d'exÃ©cution officiel basÃ© sur l'ANALYSE_COMPLETE.md du 30 mars 2026.**  
> Chaque sprint doit mettre Ã  jour ce document aprÃ¨s complÃ©tion (cocher les tÃ¢ches, ajouter les dates).  
> Les rÃ©fÃ©rentiels servent de source de vÃ©ritÃ© pour le contexte de chaque tÃ¢che.
