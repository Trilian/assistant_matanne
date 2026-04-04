# Planning d'Implémentation — Assistant Matanne

> **Basé sur** : Audit Complet & Plan d'Amélioration du 3 avril 2026
> **Dernière mise à jour** : 4 avril 2026
> **Objectif** : Roadmap exhaustive intégrant tous les axes de l'audit — bugs, nettoyage, SQL, tests, inter-modules, IA, automations, Telegram, email, admin, UI/UX, documentation, innovation

---

## Table des matières

1. [Notation par catégorie](#1-notation-par-catégorie)
2. [Chiffres clés du projet](#2-chiffres-clés-du-projet)
3. [Cartographie des modules](#3-cartographie-des-modules)
4. [Phase 1 — Corrections critiques & suppression code mort](#phase-1--corrections-critiques--suppression-code-mort)
5. [Phase 2 — Nettoyage commentaires, nommage, fichiers fourre-tout](#phase-2--nettoyage-commentaires-nommage-fichiers-fourre-tout)
6. [Phase 3 — Consolidation SQL & données](#phase-3--consolidation-sql--données)
7. [Phase 4 — Tests & couverture qualité](#phase-4--tests--couverture-qualité)
8. [Phase 5 — Documentation](#phase-5--documentation)
9. [Phase 6 — Interactions inter-modules](#phase-6--interactions-inter-modules)
10. [Phase 7 — IA & automations](#phase-7--ia--automations)
11. [Phase 8 — Telegram & notifications email](#phase-8--telegram--notifications-email)
12. [Phase 9 — UI/UX & visualisations](#phase-9--uiux--visualisations)
13. [Phase 10 — Mode admin avancé](#phase-10--mode-admin-avancé)
14. [Phase 11 — Innovations](#phase-11--innovations)
15. [Annexe A — Bugs détectés (inventaire complet)](#annexe-a--bugs-détectés-inventaire-complet)
16. [Annexe B — Code mort et legacy (inventaire complet)](#annexe-b--code-mort-et-legacy-inventaire-complet)
17. [Annexe C — Commentaires Phase/Sprint à nettoyer](#annexe-c--commentaires-phasesprint-à-nettoyer)
18. [Annexe D — Fichiers fourre-tout à éclater](#annexe-d--fichiers-fourre-tout-à-éclater)
19. [Annexe E — Interactions inter-modules existantes](#annexe-e--interactions-inter-modules-existantes)
20. [Annexe F — IA existante & opportunités](#annexe-f--ia-existante--opportunités)
21. [Annexe G — Jobs CRON existants (68)](#annexe-g--jobs-cron-existants-68)
22. [Annexe H — Telegram existant & extensions](#annexe-h--telegram-existant--extensions)
23. [Annexe I — Email existant & propositions](#annexe-i--email-existant--propositions)
24. [Annexe J — Admin existant & améliorations](#annexe-j--admin-existant--améliorations)
25. [Annexe K — Visualisations existantes & améliorations UI](#annexe-k--visualisations-existantes--améliorations-ui)
26. [Annexe L — Simplification des flux utilisateur](#annexe-l--simplification-des-flux-utilisateur)
27. [Annexe M — Axes d'innovation](#annexe-m--axes-dinnovation)
28. [Annexe N — Consolidation SQL détaillée](#annexe-n--consolidation-sql-détaillée)
29. [Récapitulatif effort & dépendances](#récapitulatif-effort--dépendances)

---

## 1. Notation par catégorie

| Catégorie | Note /10 | Forces | Faiblesses |
|-----------|----------|--------|------------|
| **Architecture frontend** | **9.0** | 40+ pages, 138+ composants, React 19, Next.js 16, TanStack Query v5 | — |
| **Admin / DevTools** | **9.0** | 51 endpoints admin, dry-run, simulation flux, console IA, feature flags | Simulateur de date manquant |
| **Architecture backend** | **8.5** | Modulaire, service factory, event bus, décorateurs, résilience | Quelques stub `pass`, imports circulaires |
| **Interactions inter-modules** | **8.5** | 21+ bridges, event bus 32 événements / 51 subscribers | Quelques bridges manquants clés |
| **Base de données SQL** | **8.5** | 22 fichiers modulaires, script régénération, test cohérence ORM↔SQL | Index dupliqués, fichier 17 vide |
| **Modèles de données** | **8.0** | 32 fichiers ORM cohérents | Tables orphelines, nommage suspect (`SauvegardeMoelleOsseuse`) |
| **Schémas Pydantic/Zod** | **8.0** | Bonne couverture backend↔frontend miroir | Quelques schémas inutilisés |
| **Automatisations / Cron** | **8.0** | 68 jobs, moteur si/alors, exécution 5 min | Jobs manquants (briefing matinal, comparateur abonnements) |
| **Notifications** | **8.0** | 4 canaux (ntfy, push, email, Telegram), fallback chain, throttling | Emails incomplets |
| **UI/UX** | **8.0** | 3D, heatmaps, Sankey, DnD, dark mode, mobile-first | Accessibilité à renforcer, micro-interactions manquantes |
| **Sécurité** | **7.5** | JWT, sanitizer XSS, rate limiting, CORS | Endpoints admin sans validation SQL stricte |
| **IA / Mistral** | **7.5** | BaseAIService solide, rate limiting, cache sémantique | Services IA expérimentaux non testés, chat stub |
| **API REST** | **7.5** | 57 routes, ~200+ endpoints | 5+ endpoints avec `pass`, OCR/Vinted actifs à supprimer |
| **Performance** | **7.5** | Cache 3 niveaux, lazy loading, Suspense | Redis optionnel pas intégré partout |
| **DevOps / Déploiement** | **7.5** | Dockerfile multi-stage, Docker Compose staging, Sentry, Prometheus | Railway Free limité |
| **Documentation** | **7.0** | 45+ fichiers | Chevauchements, noms fichiers avec sprint/phase |
| **Qualité du code** | **7.0** | Zéro TODO/FIXME dans le code actif | Commentaires Phase/Sprint, fichiers fourre-tout, dead code |
| **Tests** | **5.5** | 234 fichiers backend, 50+ frontend | Gaps routes/services, batch cooking 0%, E2E minimal |
| | | | |
| **NOTE GLOBALE** | **7.8 / 10** | **App très fonctionnelle, architecture solide** | **Tests faibles, code legacy, polish UI à renforcer** |

---

## 2. Chiffres clés du projet

| Métrique | Valeur |
|----------|--------|
| Routes API | 57 fichiers, ~200+ endpoints |
| Modèles ORM | 32 fichiers |
| Schémas Pydantic | 30 fichiers |
| Tables SQL | ~130 |
| Pages frontend | 42+ |
| Composants frontend | 138+ |
| Clients API frontend | 33 |
| Hooks React | 19 |
| Tests backend | 234 fichiers |
| Tests frontend | 50+ fichiers |
| Jobs cron | 68 enregistrés |
| Événements bus | 32 types, 51 subscribers |
| Bridges inter-modules | 21+ |
| Canaux de notification | 4 (ntfy, push, email, Telegram) |
| Endpoints admin | 51 |
| Feature flags | 18 |
| Documentation | 45+ fichiers |
| Bugs détectés | 14 (5 critiques, 5 moyens, 4 cohérence) |
| Code mort identifié | 9 éléments |
| Tests manquants | 14 domaines prioritaires |
| Nouvelles interactions proposées | 9 bridges |
| Nouvelles opportunités IA | 10 |
| Nouveaux jobs proposés | 8 |
| Nouvelles commandes Telegram | 8 + 4 enrichies |
| Améliorations UI | 14 propositions |
| Innovations | 15 axes |

---

## 3. Cartographie des modules

### 🍽️ Cuisine (Recettes, Planning, Courses, Inventaire, Batch Cooking)

| Sous-module | Backend | Frontend | Tests | IA | Problèmes détectés |
|-------------|---------|----------|-------|----|---------------------|
| Recettes CRUD | ✅ | ✅ | ✅ | Suggestions | — |
| Planning repas | ✅ | ✅ | ✅ | Génération IA | G4: stub `harnessTablierMeteo()` |
| Courses | ✅ + WebSocket | ✅ (1200L!) | ⚠️ WS deadlock | Agrégation IA | G8: fichier à refactorer, G7: WS test cassé |
| Inventaire/Stock | ✅ | ✅ | ✅ | Basique | — |
| Batch Cooking | ✅ | ✅ | ❌ 15 tests skip | Planning IA | B10: 0% couverture |
| Anti-gaspillage | ✅ | ✅ | ✅ | Suggestions | — |
| Import recettes URL/PDF | ✅ | ✅ | ✅ | Parsing IA | — |
| Nutrition (Jules) | ✅ | ✅ | ⚠️ | Adaptation IA | ~~B2~~ ✅ Fixé |

### 👶 Famille (Jules, Budget, Activités, Routines, Documents)

| Sous-module | Backend | Frontend | Tests | IA | Problèmes détectés |
|-------------|---------|----------|-------|----|---------------------|
| Profil Jules | ✅ | ✅ | ✅ | Développement IA | ~~B6~~ ✅ TYPE_CHECKING ajouté |
| Budget famille | ✅ | ✅ | ✅ | Prévisions IA | — |
| Activités | ✅ | ✅ | ✅ | Suggestions météo | — |
| Routines | ✅ | ✅ | ✅ | — | — |
| Documents | ✅ | ✅ | ✅ | Alertes | — |
| Anniversaires | ✅ | ✅ | ✅ | — | — |
| Weekend | ✅ | ✅ | ✅ | Suggestions IA | — |
| Voyages | ✅ | ✅ | ⚠️ Faible | Destockage IA | T7: tests manquants |
| Journal | ✅ | ✅ | ⚠️ | — | — |
| Contacts | ✅ | ✅ | ⚠️ | — | — |

### 🏡 Maison (Projets, Entretien, Énergie, Jardin, Équipements)

| Sous-module | Backend | Frontend | Tests | IA | Problèmes détectés |
|-------------|---------|----------|-------|----|---------------------|
| Projets (Kanban) | ✅ | ✅ DnD | ✅ | Conseils IA | — |
| Entretien saisonnier | ✅ | ✅ | ✅ | Fiches IA | — |
| Énergie | ✅ | ✅ | ✅ | — | — |
| Jardin/Plantes | ✅ | ✅ SVG | ✅ | Basique | — |
| Équipements/Meubles | ✅ | ✅ | ⚠️ | — | — |
| Travaux | ✅ | ✅ (730L!) | ⚠️ | — | G9: fichier à refactorer |
| Charges/Abonnements | ✅ | ✅ | ⚠️ | Comparateur | — |
| Visualisation 3D | ✅ | ✅ Three.js | — | — | — |
| Diagnostics photo | ✅ | ✅ | ⚠️ | Vision IA | — |
| Habitat/DVF | ✅ | ✅ | ⚠️ | — | T6: tests manquants |

### 🎮 Jeux (Paris sportifs, Loto, Euromillions, Bankroll)

| Sous-module | Backend | Frontend | Tests | IA | Problèmes détectés |
|-------------|---------|----------|-------|----|---------------------|
| Paris sportifs | ✅ | ✅ | ✅ | Analyse cotes | ~~B5~~ ✅ Gardé test-only |
| Loto | ✅ | ✅ heatmap D3 | ✅ | Patterns IA | — |
| Euromillions | ✅ | ✅ heatmap + backtest | ✅ | Backtest IA | — |
| Bankroll | ✅ | ✅ widget | ✅ | — | — |
| Dashboard jeux | ✅ | ✅ | ⚠️ Faible | — | ~~L4~~ ✅ Supprimé |

### 🔧 Outils (Chat IA, Convertisseur, Météo, Notes, Minuteur)

| Sous-module | Backend | Frontend | Tests | IA | Problèmes détectés |
|-------------|---------|----------|-------|----|---------------------|
| Chat IA | ✅ streaming | ✅ | ⚠️ | Conversationnel | ~~B1~~ ✅ Fixé |
| Convertisseur | ✅ | ✅ | ✅ | — | — |
| Météo | ✅ | ✅ | ✅ | Impact IA | — |
| Notes | ✅ | ✅ | ⚠️ | — | — |
| Minuteur | — (frontend) | ✅ | ⚠️ | — | — |
| Préférences | ✅ | ✅ | ⚠️ | — | ~~B3~~ ✅ Fixé |

### 📊 Admin & Dashboard

| Sous-module | Backend | Frontend | Tests | Problèmes détectés |
|-------------|---------|----------|-------|---------------------|
| Dashboard accueil | ✅ | ✅ DnD | ✅ | ~~B4~~ ✅ Fixé |
| Panel admin | ✅ 51 endpoints | ✅ | ⚠️ Faible | AD8: visibilité sidebar à vérifier |
| Jobs management | ✅ 68 jobs | ✅ | ⚠️ | — |
| Feature flags | ✅ 18 flags | ✅ | ⚠️ | — |
| Config export/import | ✅ | ⚠️ Partiel | — | G14: UI import incomplète |

---

## Phase 1 — Corrections critiques & suppression code mort ✅ TERMINÉE

> **Objectif** : Éliminer les bugs silencieux, supprimer tout le code de features rejetées
> **Durée estimée** : 2-3 jours → **Réalisé** : 4 avril 2026
> **Prérequis** : Aucun
> **Impact** : Cohérence avec préférences utilisateur + fix des bugs critiques

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 1.1 | **Implémenter les 5 stubs `pass`** | B1: `/chat` (assistant.py L88), B2: suivi alimentaire Jules (famille_jules.py L198), B3: préférences (preferences.py L389+L394), B4: error handlers dashboard (dashboard.py L765+L1264) | 4h | 🔴 Critique |
| 1.2 | **Supprimer tous les endpoints OCR** | `courses.py` (`/ocr-ticket-caisse`), `upload.py` (`/ocr-document`), `jeux_dashboard.py` (`/ocr-ticket`), `maison_finances.py` (`/ocr-ticket`), `ocr_service.py` | 2h | 🔴 Critique |
| 1.3 | **Supprimer code Vinted** | `src/api/schemas/famille.py` (schemas `AnnonceVinted*`), `src/services/famille/achats_ia.py` (Vinted service) | 1h | 🔴 Critique |
| 1.4 | **Limiter gamification au Garmin/sport** | `src/core/models/gamification.py` — supprimer tables Badge/Point/Historique si non liées au sport, `dashboard.py` endpoint `/points-famille`, job `points_famille_hebdo` | 2h | 🔴 Critique |
| 1.5 | **Supprimer "jeu responsable"** | Résidus dans `jeux_dashboard.py` L555 | 30min | 🔴 Critique |
| 1.6 | **Supprimer fichiers dead code** | `ocr_service.py` (L6), `rerun_profiler.py` (L7) | 30min | 🔴 Critique |
| 1.7 | **Renommer `SauvegardeMoelleOsseuseDB`** | `src/core/models/systeme.py` — nom incohérent B8 | 15min | 🟡 Important |
| 1.8 | **Renommer `whatsapp-test/`** | `frontend/src/app/(app)/admin/whatsapp-test/` → `telegram-test/` (B11) | 15min | 🟡 Important |
| 1.9 | **Fixer générateur placeholder paris** | `src/core/models/jeux.py` L361 — ne plus créer de données fictives silencieusement (B5) | 1h | 🟡 Important |
| 1.10 | **Résoudre forward refs** | `src/core/models/famille.py` L74-83 — `# noqa: F821` (B6) | 1h | 🟡 Important |
| 1.11 | **Fixer imports circulaires** | `famille.py` et `maison.py` routes — late import pattern (B7) | 1h | 🟡 Important |
| 1.12 | **Déplacer `generate_screenshots.ts`** | `scripts/` → `frontend/scripts/` (L9) | 15min | 🟢 Souhaitable |

### Critères de validation

- [x] `grep -r "pass$" src/api/routes/` ne remonte plus aucun stub fonctionnel
- [x] `grep -ri "ocr" src/` ne remonte plus rien (sauf DEPRECATED.md)
- [x] `grep -ri "vinted" src/` ne remonte plus rien
- [x] `grep -ri "jeu responsable" src/` ne remonte plus rien
- [x] `grep -r "whatsapp" frontend/src/` ne remonte plus rien
- [x] Imports OK après suppressions (OCR, Vinted, gamification famille)

---

## Phase 2 — Nettoyage commentaires, nommage, fichiers fourre-tout

> **Objectif** : Code lisible sans références temporelles, fichiers bien découpés et nommés
> **Durée estimée** : 3-4 jours
> **Prérequis** : Phase 1 terminée
> **Impact** : Maintenabilité long terme, onboarding facilité

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 2.1 | **Supprimer 150+ commentaires Phase/Sprint** | Remplacer `# Phase X.Y`, `# Sprint N`, `// Phase X` par descriptions fonctionnelles (voir [Annexe C](#annexe-c--commentaires-phasesprint-à-nettoyer)) | 3h | 🔴 Critique |
| 2.2 | **Renommer fichiers docs** | `TELEGRAM_RECETTE_SPRINT5.md` → `TELEGRAM_RECETTES.md`, `EXPLAIN_ANALYZE_SPRINT2.md` → `PERFORMANCE_QUERIES.md` | 30min | 🔴 Critique |
| 2.3 | **Renommer fichiers tests** | Tous les `test_phase_*.py`, `test_sprint_*.py` → noms descriptifs, `test_bridges_nim.py` → `test_bridges_cross_module.py` | 1h | 🔴 Critique |
| 2.4 | **Renommer `ia_avancee.ts`** | `frontend/src/bibliotheque/api/ia_avancee.ts` → `ia-avancee.ts` (cohérence kebab-case) (B12) | 15min | 🟡 Important |
| 2.5 | **Éclater `fonctionnalites_avancees.py`** | 16+ endpoints → fichiers par domaine (`batch_cooking_avance.py`, `tendances.py`, `journaux.py`) (L10) | 2h | 🔴 Critique |
| 2.6 | **Éclater `validateurs.ts`** | `frontend/src/bibliotheque/validateurs.ts` → `validateurs-recettes.ts`, `validateurs-famille.ts`, etc. | 1h | 🟡 Important |
| 2.7 | **Refactorer page courses** | `frontend/src/app/(app)/cuisine/courses/page.tsx` 1200+ lignes → extraire composants dans `composants/courses/` (G8) | 2h | 🟡 Important |
| 2.8 | **Refactorer page travaux** | `frontend/src/app/(app)/maison/travaux/page.tsx` 730+ lignes → extraire composants (G9) | 1h | 🟡 Important |
| 2.9 | **Archiver fichiers racine obsolètes** | `AUDIT_COMPLET_AVRIL_2026.md` → `docs/archive/` (L11) | 15min | 🟢 Souhaitable |

### Critères de validation

- [ ] `grep -rn "Phase [A-Z0-9]" src/ frontend/src/ --include="*.py" --include="*.ts" --include="*.tsx"` ne remonte plus de commentaires Phase/Sprint
- [ ] Aucun fichier de test ne contient "phase" ou "sprint" dans son nom
- [ ] `fonctionnalites_avancees.py` n'existe plus
- [ ] Pages courses et travaux < 500 lignes chacune
- [ ] Tous les fichiers API frontend sont en kebab-case

---

## Phase 3 — Consolidation SQL & données

> **Objectif** : Base propre, indexes validés, tables orphelines supprimées
> **Durée estimée** : 1-2 jours → **Réalisé** : 4 avril 2026
> **Prérequis** : Phase 1 terminée (tables gamification traitées)
> **Impact** : Performance DB, propreté schéma
> **Statut** : ✅ **Terminée et vérifiée**

### Sprint SQL — 4 avril 2026

- ✅ `13_views.sql` nettoyé : plus aucun `CREATE INDEX`, vues conservées uniquement
- ✅ vues maison basculées sur `taches_entretien` au lieu des tables legacy `taches_home` / `stats_home`
- ✅ `17_migrations_absorbees.sql` rempli avec le nettoyage idempotent des reliquats SQL (`archive_articles`, `journal_sante`, `stats_home`, `taches_home`)
- ✅ ajout du script `scripts/analysis/audit_orm_sql.py` pour rejouer l’audit ORM↔SQL hors pytest
- ✅ `INIT_COMPLET.sql` régénéré et validé — SHA256 : `3537E08CBFEAFBAE917D978E55E228CBEDCC579E1D321F372E0329B7E4C73F1C`
- ✅ vérification finale rejouée le 4 avril 2026 : audit ORM↔SQL OK, aucune orpheline non documentée, `146 passed` sur `tests/sql/test_schema_coherence.py`

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 3.1 | ✅ **Dédupliquer indexes SQL** | `13_views.sql` nettoyé ; tous les indexes restent centralisés dans `14_indexes.sql` (S1, B13) | 30min | 🔴 Critique |
| 3.2 | ✅ **Résoudre fichier 17 vide** | `17_migrations_absorbees.sql` contient désormais les nettoyages V005-V007 et les `DROP IF EXISTS` legacy (S2, B14) | 15min | 🟡 Important |
| 3.3 | ✅ **Drop tables orphelines** | retrait du schéma actif de `stats_home` / `taches_home` + nettoyage idempotent de `archive_articles` et `journal_sante` (S3, L8) | 1h | 🔴 Critique |
| 3.4 | ✅ **Valider la gamification SQL** | Conformité confirmée : seules `points_utilisateurs` et `badges_utilisateurs` (sport/nutrition/Garmin) sont conservées ; aucune table générique legacy `badges` / `points` / `historique_gamification` active (S4) | 30min | 🔴 Critique |
| 3.5 | ✅ **Régénérer `INIT_COMPLET.sql`** | `python scripts/db/regenerate_init.py` exécuté après nettoyage ; fichier recompilé avec succès (S5) | 15min | 🟡 Important |
| 3.6 | ✅ **Audit ORM↔SQL final** | `python scripts/analysis/audit_orm_sql.py` + `pytest tests/sql/test_schema_coherence.py -q` validés (S6) | 15min | 🟡 Important |

### Critères de validation

- [x] `grep -n "CREATE INDEX" sql/schema/13_views.sql` ne remonte plus d'index
- [x] `17_migrations_absorbees.sql` résolu (contenu idempotent ajouté)
- [x] Tables orphelines ciblées supprimées du schéma actif / nettoyées pour migration
- [x] `test_schema_coherence.py` passe à 100% (`146 passed`)
- [x] `INIT_COMPLET.sql` régénéré et hash SHA256 mis à jour (`3537E08CBFEAFBAE917D978E55E228CBEDCC579E1D321F372E0329B7E4C73F1C`)

### Checklist de clôture — preuve de vérification

- [x] `python scripts/analysis/audit_orm_sql.py` → **OK** (`149` tables SQL, `141` tables ORM, `0` nouvelle orpheline, `11` instructions SQL dans `17_migrations_absorbees.sql`)
- [x] `pytest tests/sql/test_schema_coherence.py -q` → **OK** (`146 passed in 4.19s`)
- [x] `Get-FileHash sql/INIT_COMPLET.sql -Algorithm SHA256` → **OK** (`3537E08CBFEAFBAE917D978E55E228CBEDCC579E1D321F372E0329B7E4C73F1C`)

---

## Phase 4 — Tests & couverture qualité

> **Objectif** : Combler les gaps critiques (batch cooking, routes, bridges, E2E)
> **Durée estimée** : 5-7 jours
> **Prérequis** : Phase 1 terminée (stubs implémentés)
> **Impact** : Confiance déploiement, détection régressions

### État actuel des tests

| Domaine | Fichiers | Couverture | Note /10 |
|---------|----------|------------|----------|
| API Auth | 3 | 90% | 9 |
| Core DB / Sessions | 8 | 85% | 8.5 |
| Core Cache | 5 | 80% | 8 |
| Schémas Pydantic | 6 | 80% | 8 |
| Core Config | 3 | 75% | 7.5 |
| Core Models | 4 | 70% | 7 |
| Services cuisine | 5 | 60% | 6 |
| Frontend unit tests | 50+ | 60% | 6 |
| Services famille | 4 | 50% | 5 |
| Routes API | 35 | 45% | 4.5 |
| Services maison | 3 | 40% | 4 |
| Bridges inter-modules | 3 | 35% | 3.5 |
| Services jeux | 2 | 30% | 3 |
| Admin routes | 1+ | 20% | 2 |
| Frontend E2E | 1 | 5% | 0.5 |
| **Batch cooking** | **1** | **0%** | **0** |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 4.1 | **Fixer 15 tests batch cooking** | Résoudre problème session DB (B10) | 3h | 🔴 Critique |
| 4.2 | **Tests `/chat` (après fix stub B1)** | Endpoint assistant IA — conversation, streaming, contexte | 2h | 🔴 Critique |
| 4.3 | **Tests préférences (après fix B3)** | CRUD préférences complet | 1h | 🔴 Critique |
| 4.4 | **Tests Jules nutrition (après fix B2)** | Suivi alimentaire Jules | 1h | 🔴 Critique |
| 4.5 | **Tests `fonctionnalites_avancees.py`** | 16 endpoints sans aucun test (T5) | 4h | 🔴 Critique |
| 4.6 | **Tests bridges inter-modules** | Tests unitaires pour chaque bridge (21+) (T10) | 4h | 🟡 Important |
| 4.7 | **Tests `habitat.py`, `voyages.py`, `garmin.py`** | CRUD + mock API Garmin (T6-T8) | 3h | 🟡 Important |
| 4.8 | **Tests admin routes** | Chaque catégorie admin : audit, jobs, cache, flags, etc. (T12) | 3h | 🟡 Important |
| 4.9 | **Tests upload** | Upload fichier sans OCR (T9) | 1h | 🟡 Important |
| 4.10 | **Résoudre deadlock WebSocket** | Test WebSocket courses — deadlock sync TestClient (T11, G7) | 2h | 🟡 Important |
| 4.11 | **Frontend E2E : parcours complet** | Login → créer recette → planifier → générer courses → cocher articles (T13) | 3h | 🟢 Souhaitable |
| 4.12 | **Contract tests OpenAPI** | Étendre schemathesis sur les nouveaux endpoints (T14) | 2h | 🟢 Souhaitable |
| 4.13 | **Renommer fichiers test** | `test_phase_*.py` → noms descriptifs, `test_bridges_nim.py` → `test_bridges_cross_module.py` | 30min | 🟡 Important |

### Critères de validation

- [ ] 0 tests skippés pour batch cooking
- [ ] Couverture routes API ≥ 70%
- [ ] Couverture bridges ≥ 60%
- [ ] Au moins 1 parcours E2E frontend complet
- [ ] `pytest --tb=short` : 0 failures, 0 errors
- [ ] Aucun fichier de test avec "phase"/"sprint" dans le nom

---

## Phase 5 — Documentation

> **Objectif** : Documentation à jour, sans doublons, références legacy éliminées
> **Durée estimée** : 2-3 jours
> **Prérequis** : Phases 1-2 terminées (suppressions et renommages effectués)
> **Impact** : Onboarding, maintenabilité

### Documentation existante à fusionner/nettoyer

| Action | Fichiers | Raison |
|--------|----------|--------|
| **Fusionner** | `AUTOMATIONS.md` + `AUTOMATION_GUIDE.md` | Chevauchement — un seul guide automations |
| **Fusionner** | `CRON_JOBS.md` + `CRON_DEVELOPMENT.md` | Chevauchement — un seul guide cron |
| **Renommer** | `TELEGRAM_RECETTE_SPRINT5.md` → `TELEGRAM_RECETTES.md` | Référence sprint |
| **Renommer** | `EXPLAIN_ANALYZE_SPRINT2.md` → `PERFORMANCE_QUERIES.md` | Référence sprint |
| **Archiver** | `AUDIT_COMPLET_AVRIL_2026.md` | Remplacé par `AUDIT_ET_PLAN_AMELIORATION.md` |

### Documentation manquante à créer

| # | Doc à créer | Contenu |
|---|-------------|---------|
| D1 | `docs/INTER_MODULES_MAP.md` | Carte visuelle des 21+ bridges avec déclencheurs et flux |
| D2 | `docs/ADMIN_QUICK_REFERENCE.md` | Cheatsheet admin : commandes, triggers, flags les plus utilisés |
| D3 | `scripts/README.md` | Documentation des 18 scripts (4 non documentés) |
| D4 | Mise à jour `DEPRECATED.md` | Ajouter OCR, Vinted, gamification générale, WhatsApp, jeu responsable |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 5.1 | **Fusionner `AUTOMATIONS.md` + `AUTOMATION_GUIDE.md`** | Un seul guide automations | 1h | 🔴 Critique |
| 5.2 | **Fusionner `CRON_JOBS.md` + `CRON_DEVELOPMENT.md`** | Un seul guide cron | 1h | 🔴 Critique |
| 5.3 | **Créer `docs/INTER_MODULES_MAP.md`** | Carte visuelle et descriptive des 21+ bridges (D1) | 2h | 🟡 Important |
| 5.4 | **Documenter scripts non documentés** | 4 scripts sur 18 (D3) | 1h | 🟡 Important |
| 5.5 | **Mettre à jour `DEPRECATED.md`** | OCR, Vinted, gamification, WhatsApp, jeu responsable (D4) | 30min | 🟡 Important |
| 5.6 | **Créer `docs/ADMIN_QUICK_REFERENCE.md`** | Cheatsheet admin (D2) | 1h | 🟢 Souhaitable |
| 5.7 | **Archiver fichiers racine** | `AUDIT_COMPLET_AVRIL_2026.md` → `docs/archive/` | 15min | 🟢 Souhaitable |
| 5.8 | **Ajouter index guides** | `docs/guides/` et `docs/user-guide/` non référencés → ajouter README | 30min | 🟢 Souhaitable |

### Critères de validation

- [ ] Plus de fichier doc avec "Sprint" ou "Phase" dans le nom
- [ ] `AUTOMATIONS.md` unique, `CRON_JOBS.md` unique
- [ ] `DEPRECATED.md` contient OCR, Vinted, gamification, WhatsApp, jeu responsable
- [ ] `INTER_MODULES_MAP.md` créé avec tous les bridges
- [ ] Tous les scripts ont une doc

---

## Phase 6 — Interactions inter-modules

> **Objectif** : Connecter les 9 bridges manquants pour une expérience intégrée
> **Durée estimée** : 3-4 jours
> **Prérequis** : Phase 1 terminée
> **Impact** : Automatisation des flux, moins de clics utilisateur

### Bridges existants (21+) — voir [Annexe E](#annexe-e--interactions-inter-modules-existantes)

### Nouveaux bridges à implémenter

| # | Source → Cible | Description | Valeur |
|---|----------------|-------------|--------|
| I1 | Planning validé → Courses auto | Planning semaine validé → liste courses auto-générée | ⭐⭐⭐ |
| I2 | Météo → Jardin | Prévisions météo → alertes arrosage/gel | ⭐⭐ |
| I4 | Budget mensuel → Rapport famille | Clôture mois → intégrer budget dans résumé | ⭐⭐ |
| I5 | Entretien terminé → MAJ équipement | Tâche validée → date dernier entretien sur fiche | ⭐⭐⭐ |
| I6 | Batch cooking → Planning semaine | Session terminée → pré-remplir planning | ⭐⭐⭐ |
| I7 | Anniversaire → Recettes festives | Anniversaire J-3 → suggestions gâteau/menu festif | ⭐⭐ |
| I8 | Garmin sport → Nutrition | Grosse séance → repas plus copieux/protéiné | ⭐⭐ |
| I9 | Fin voyage → Résumé dépenses | Retour → résumé budget voyage + réintégration planning | ⭐ |
| I10 | Feedback recette → Poids suggestion | 5★ → plus suggérée, 1★ → exclue | ⭐⭐⭐ |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 6.1 | **I1 : Planning → Courses auto** | Bridge event_bus : `planning.valide` → générer courses | 3h | 🔴 Critique |
| 6.2 | **I5 : Entretien → MAJ équipement** | Bridge : tâche validée → update fiche équipement | 2h | 🔴 Critique |
| 6.3 | **I6 : Batch → Planning** | Bridge : batch terminé → pré-remplir planning | 2h | 🔴 Critique |
| 6.4 | **I10 : Feedback → Suggestion** | Bridge : note recette → ajuster poids de suggestion | 2h | 🔴 Critique |
| 6.5 | **I2 : Météo → Jardin** | Bridge : prévisions → alertes arrosage/gel | 2h | 🟡 Important |
| 6.6 | **I7 : Anniversaire → Menu festif** | Bridge : J-3 → suggestions recettes festives | 2h | 🟡 Important |
| 6.7 | **I8 : Garmin → Nutrition** | Bridge : activité sportive → ajuster portions | 2h | 🟡 Important |
| 6.8 | **I4 : Budget → Rapport** | Bridge : clôture mois → données dans résumé | 1h | 🟢 Souhaitable |
| 6.9 | **I9 : Voyage → Résumé** | Bridge : retour → résumé dépenses | 1h | 🟢 Souhaitable |

### Critères de validation

- [ ] Valider un planning → la liste de courses est auto-générée
- [ ] Terminer un batch cooking → repas pré-remplis dans le planning
- [ ] Valider une tâche entretien → fiche équipement mise à jour
- [ ] Noter une recette 1★ → elle n'est plus suggérée
- [ ] Tests unitaires pour chaque nouveau bridge

---

## Phase 7 — IA & automations

> **Objectif** : Exploiter les nouvelles opportunités IA + ajouter les jobs manquants
> **Durée estimée** : 4-5 jours
> **Prérequis** : Phase 1 terminée (stub `/chat` implémenté), Phase 6 terminée (bridges en place)
> **Impact** : Valeur quotidienne pour l'utilisateur, proactivité

### IA existante (voir [Annexe F](#annexe-f--ia-existante--opportunités))

10 services IA en place (planning, anti-gaspi, batch cook, Jules coaching, weekend, dashboard résumé, diagnostics, estimation travaux, chat, nutrition).

### Nouvelles opportunités IA

| # | Opportunité | Complexité | Impact |
|---|-------------|------------|--------|
| IA1 | Coach jardin via photo plante (Vision Mistral) | Moyenne | ⭐⭐⭐ |
| IA2 | Optimisateur énergie IA | Faible | ⭐⭐ |
| IA3 | Résumé matinal personnalisé (Telegram 7h) | Faible | ⭐⭐⭐ |
| IA4 | Adaptation recettes "J'ai pas de X" | Moyenne | ⭐⭐⭐ |
| IA5 | Prédiction restock intelligent | Moyenne | ⭐⭐⭐ |
| IA6 | Assistant vocal mains-libres cuisine | Moyenne | ⭐⭐ |
| IA7 | Analyse tendances familiales mensuelles | Faible | ⭐⭐ |
| IA8 | Planificateur sorties (budget+météo+Jules) | Moyenne | ⭐⭐ |
| IA9 | Générateur courses intelligent "vous avez oublié le lait" | Faible | ⭐⭐⭐ |
| IA10 | Coach entretien prédictif (historique → prochaine révision) | Faible | ⭐⭐ |

### Nouveaux jobs CRON (voir [Annexe G](#annexe-g--jobs-cron-existants-68))

| Job | Schedule | Module | Description |
|-----|----------|--------|-------------|
| J1 `briefing_matinal_ia` | Quotidien 7h | Transversal | Résumé narratif IA (météo+repas+tâches+Jules) |
| J2 `comparateur_abonnements` | 1er du mois | Abonnements | Comparer prix actuels vs offres marché |
| J4 `rapport_nutritionnel_jules` | Hebdo dim 19h | Jules | Résumé nutritionnel hebdo |
| J5 `nettoyage_notifications_30j` | Mensuel | Système | Purger historique > 30 jours |
| J6 `prediction_depenses` | 15 du mois | Budget | Prédiction fin de mois |
| J7 `alerte_plantes_arrosage` | Quotidien 8h (été) | Jardin | Météo chaude + pas d'arrosage |
| J8 `sync_tirages_euromillions` | Mar/Ven 22:30 | Jeux | Sync résultats Euromillions |

### Nouvelles règles automations (moteur si/alors)

| # | Déclencheur | Condition | Action |
|---|------------|-----------|--------|
| A1 | Recette notée 1★ | `feedback.note <= 2` | Exclure de la suggestion auto |
| A2 | Planning validé | `planning.statut = 'valide'` | Générer courses auto (bridge I1) |
| A3 | Session batch terminée | `batch.statut = 'termine'` | Pré-remplir planning (bridge I6) |
| A4 | Température < 0°C | `meteo.temp_min < 0` | Alerte protection plantes jardin |
| A5 | Dernier entretien > fréquence | `entretien.derniere + freq < today` | Créer tâche + notification |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 7.1 | **IA3 : Résumé matinal Telegram** | Briefing narratif IA à 7h : météo + repas + tâches + Jules | 3h | 🔴 Critique |
| 7.2 | **IA4 : Adaptation recettes** | "J'ai pas de crème fraîche" → IA adapte en temps réel | 4h | 🔴 Critique |
| 7.3 | **IA10 : Coach entretien prédictif** | Historique + âge équipement → prochaine révision | 3h | 🟡 Important |
| 7.4 | **IA9 : Courses intelligentes** | Analyse 4 dernières semaines → "vous avez oublié le lait" | 3h | 🟡 Important |
| 7.5 | **Jobs J1-J8** | 7 nouveaux jobs cron | 4h | 🟡 Important |
| 7.6 | **Automations A1-A5** | 5 nouvelles règles moteur si/alors | 3h | 🟡 Important |
| 7.7 | **IA1 : Coach jardin photo** | Photo plante → diagnostic maladie (Vision Mistral) | 4h | 🟢 Souhaitable |
| 7.8 | **IA5 : Prédiction restock** | Fréquence achat + quantité → quand racheter | 4h | 🟢 Souhaitable |

### Critères de validation

- [ ] Briefing matinal Telegram reçu à 7h avec tous les éléments
- [ ] "J'ai pas de crème" sur une recette → proposition alternative IA
- [ ] Coach entretien affiche les prochaines révisions sur chaque fiche
- [ ] 7 nouveaux jobs enregistrés et déclenchables via admin
- [ ] 5 nouvelles règles automations visibles dans la page automations

---

## Phase 8 — Telegram & notifications email

> **Objectif** : Telegram = hub mobile complet, emails = rapports périodiques
> **Durée estimée** : 3-4 jours
> **Prérequis** : Phase 7 terminée (IA3 briefing matinal en place)
> **Impact** : Accès rapide mobile, communications enrichies

### Commandes Telegram existantes (11)

`/planning`, `/courses`, `/ajout [article]`, `/repas [midi|soir]`, `/jules`, `/maison`, `/budget`, `/meteo`, `/menu`, `/aide`

### Nouvelles commandes

| # | Commande | Description | Priorité |
|---|----------|-------------|----------|
| T1 | `/inventaire` | Liste frigo avec icônes péremption 🟢🟡🔴 | 🔴 Haute |
| T2 | `/recette [nom]` | Recette rapide avec ingrédients | 🔴 Haute |
| T3 | `/batch` | Résumé batch cooking en cours/dernière | 🟡 Moyenne |
| T4 | `/jardin` | Prochaines tâches + prochaines récoltes | 🟡 Moyenne |
| T5 | `/energie` | KPIs énergie du mois | 🟢 Basse |
| T6 | `/rappels` | Tous les rappels en attente groupés | 🔴 Haute |
| T7 | `/timer [Xmin]` | Minuteur depuis Telegram → notification quand fini | 🟡 Moyenne |
| T8 | `/note [texte]` | Créer une note rapide | 🟡 Moyenne |

### Interactions enrichies

| # | Feature | Description |
|---|---------|-------------|
| T9 | Boutons validation courses | ✅ Acheté / ❌ Pas trouvé / 🔄 Reporter |
| T10 | Mini-sondage repas | "Qu'est-ce qui vous ferait plaisir ?" → boutons choix |
| T11 | Photo → IA | Photo frigo → IA analyse → suggestions recettes |

### Emails manquants

| # | Email | Déclencheur | Contenu |
|---|-------|-------------|---------|
| E1 | Résumé nutritionnel mensuel | 1er du mois | Diversité repas, scores nutri, tendances |
| E2 | Bilan trimestriel jardin | Trimestriel | Récoltes vs prévisions, planning saison suivante |
| E4 | Backup confirmation | Après backup | Confirmation avec taille et hash |
| E5 | Rapport Jules mensuel | 1er du mois | Jalons, prochaines étapes, photos |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 8.1 | **T1, T2, T6 : Commandes Telegram haute priorité** | `/inventaire`, `/recette`, `/rappels` | 3h | 🔴 Critique |
| 8.2 | **T3, T4, T7, T8 : Commandes Telegram moyennes** | `/batch`, `/jardin`, `/timer`, `/note` | 3h | 🟡 Important |
| 8.3 | **T9 : Boutons validation courses** | Inline keyboard ✅/❌/🔄 sur chaque article | 2h | 🔴 Critique |
| 8.4 | **T10 : Mini-sondage repas** | Inline keyboard choix de repas | 1h | 🟡 Important |
| 8.5 | **T11 : Photo frigo → IA** | Photo Telegram → Vision Mistral → suggestions | 3h | 🟢 Souhaitable |
| 8.6 | **E1-E5 : Emails manquants** | Nutritionnel mensuel, jardin trimestriel, backup confirm, Jules mensuel | 3h | 🟡 Important |

### Critères de validation

- [ ] 8 nouvelles commandes Telegram fonctionnelles
- [ ] Boutons inline ✅/❌/🔄 sur la liste courses Telegram
- [ ] Emails mensuels configurés et envoyés
- [ ] Tests sur chaque commande Telegram

---

## Phase 9 — UI/UX & visualisations

> **Objectif** : Interface fluide, simple, riche visuellement
> **Durée estimée** : 7-10 jours
> **Prérequis** : Phase 2 terminée (code propre)
> **Impact** : Expérience utilisateur, plaisir d'utilisation

### Visualisations existantes (voir [Annexe K](#annexe-k--visualisations-existantes--améliorations-ui))

14 composants de visualisation déjà en place (3D maison, jardin SVG, heatmaps D3, Sankey, treemaps, radars, sparklines, Kanban DnD, dashboard DnD, timeline batch cooking).

### Améliorations UI proposées

| # | Amélioration | Composant cible | Impact | Priorité |
|---|-------------|-----------------|--------|----------|
| UI1 | Calendrier repas avec photos miniatures | Planning | ⭐⭐⭐ | 🔴 Haute |
| UI4 | Dashboard widgets personnalisables | Dashboard | ⭐⭐⭐ | 🔴 Haute |
| UI5 | Timeline Jules style story scroll | Jules | ⭐⭐⭐ | 🔴 Haute |
| UI6 | Mode cuisine tablette (gros texte, gros boutons) | Recettes | ⭐⭐⭐ | 🔴 Haute |
| UI2 | Carte jardin 2D améliorée (zones colorées) | Jardin | ⭐⭐ | 🟡 Moyenne |
| UI3 | Graphe temporel dépenses avec annotations | Finances | ⭐⭐ | 🟡 Moyenne |
| UI8 | Barre de progression batch cooking animée | Batch | ⭐⭐ | 🟡 Moyenne |
| UI10 | Dark mode amélioré (contraste, couleurs) | Global | ⭐⭐ | 🟡 Moyenne |
| UI13 | Planning colonnes Google Calendar | Planning | ⭐⭐ | 🟡 Moyenne |
| UI14 | Gantt projets maison | Travaux | ⭐⭐ | 🟡 Moyenne |
| UI7 | Sankey amélioré (animation survol) | Finances | ⭐ | 🟢 Basse |
| UI9 | Micro-interactions Framer Motion | Global | ⭐⭐ | 🟢 Basse |
| UI11 | Mini widget météo header | Layout | ⭐ | 🟢 Basse |
| UI12 | Skeletons contextuels (ressemblent au contenu) | Global | ⭐ | 🟢 Basse |

### Accessibilité

| # | Problème | Action | Priorité |
|---|----------|--------|----------|
| G10 | Pas de `aria-live` pour mises à jour temps réel (courses WebSocket) | Ajouter `aria-live="polite"` | 🟡 Moyenne |
| G11 | `aria-describedby` manquant sur composants complexes | Ajouter descriptions | 🟢 Basse |
| G12 | `htmlFor` pas toujours associé aux labels | Corriger formulaires | 🟢 Basse |

### Simplification des flux (voir [Annexe L](#annexe-l--simplification-des-flux-utilisateur))

| # | Flux simplifié | Impact |
|---|----------------|--------|
| F1 | Dashboard → 1 bouton "Planifier ma semaine" → Courses auto | ⭐⭐⭐ |
| F2 | Bouton "Ajouter au planning" depuis une recette | ⭐⭐⭐ |
| F3 | Push anti-gaspillage directe (pas besoin d'ouvrir l'app) | ⭐⭐⭐ |
| F4 | Page Focus comme page d'accueil par défaut | ⭐⭐ |
| F5 | Bouton ✅ Telegram directement sur les tâches | ⭐⭐⭐ |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 9.1 | **UI1 : Calendrier repas mosaïque** | Vue semaine avec photos miniatures des recettes | 4h | 🔴 Critique |
| 9.2 | **UI4 : Dashboard personnalisable** | Choix et réorganisation des widgets par l'utilisateur | 6h | 🔴 Critique |
| 9.3 | **UI5 : Timeline Jules** | Timeline verticale avec photos et jalons, style story | 4h | 🔴 Critique |
| 9.4 | **UI6 : Mode cuisine tablette** | Vue épurée: gros texte, gros boutons, minuteurs intégrés | 4h | 🔴 Critique |
| 9.5 | **F1-F5 : Simplification flux** | 5 flux simplifiés (voir ci-dessus) | 6h | 🔴 Critique |
| 9.6 | **UI13 : Planning colonnes** | Style Google Calendar (colonnes jours, blocs horaires) | 4h | 🟡 Important |
| 9.7 | **UI14 : Gantt projets maison** | Diagramme de Gantt avec dépendances | 4h | 🟡 Important |
| 9.8 | **UI8 : Progress bar batch** | Barre animée avec étapes en cours/passées/à venir | 2h | 🟡 Important |
| 9.9 | **UI10 : Dark mode amélioré** | Revue contraste, couleurs accent, readability | 2h | 🟡 Important |
| 9.10 | **Accessibilité G10-G12** | `aria-live`, `aria-describedby`, `htmlFor` | 2h | 🟡 Important |
| 9.11 | **UI9 : Micro-interactions** | Framer Motion transitions pages, ajouts panier, validations | 4h | 🟢 Souhaitable |
| 9.12 | **UI2 : Carte jardin améliorée** | Zones colorées par état (planté, récolté, vide) | 3h | 🟢 Souhaitable |

### Critères de validation

- [ ] Calendrier repas affiche les photos miniatures
- [ ] Widgets dashboard réorganisables par drag-n-drop
- [ ] Timeline Jules fonctionnelle avec jalons et photos
- [ ] Mode cuisine utilisable sur tablette (Google Tablet)
- [ ] "Planifier ma semaine" en 1 clic depuis le dashboard
- [ ] `aria-live` sur le composant courses WebSocket
- [ ] Dark mode sans problème de contraste

---

## Phase 10 — Mode admin avancé

> **Objectif** : Outils de test puissants, invisibles pour l'utilisateur final
> **Durée estimée** : 2-3 jours
> **Prérequis** : Phase 7 terminée (jobs en place)
> **Impact** : Productivité dev/test, qualité QA

### Admin existant (voir [Annexe J](#annexe-j--admin-existant--améliorations))

51 endpoints, dry-run, simulation flux, console IA, test multi-canal, purge cache, feature flags, mode maintenance, impersonation (1h, audité), export/import config, santé bridges.

### Améliorations proposées

| # | Feature | Description | Priorité |
|---|---------|-------------|----------|
| AD1 | Smoke test tous bridges (1 clic) | Tester 21+ bridges avec rapport visuel | 🔴 Haute |
| AD2 | Replay événement depuis historique | Sélectionner + re-jouer un événement passé | 🟡 Moyenne |
| AD3 | Tableau de bord jobs temps réel | Jobs en cours, dernière exécution, prochaine, taux succès | 🟡 Moyenne |
| AD4 | Simulateur de date | Tester comme si on était le 1er du mois, un lundi, etc. | 🔴 Haute |
| AD5 | Log en direct (tail) | Stream SSE des logs serveur dans la page admin | 🟡 Moyenne |
| AD6 | Générateur données de test | Bouton peupler DB avec données réalistes | 🔴 Haute |
| AD7 | Diff de config | Comparer config actuelle vs défaut | 🟢 Basse |
| AD8 | Admin invisible sidebar | Lien admin seulement par URL ou raccourci clavier secret | 🔴 Haute |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 10.1 | **AD4 : Simulateur de date** | Tester cron comme si on était une date donnée | 3h | 🔴 Critique |
| 10.2 | **AD6 : Générateur données test** | Seed DB avec données réalistes 1 clic | 3h | 🔴 Critique |
| 10.3 | **AD8 : Admin invisible** | Supprimer lien sidebar, accès par URL directe ou raccourci secret | 1h | 🔴 Critique |
| 10.4 | **AD1 : Smoke test bridges** | 1 clic → teste tous les 21+ bridges avec rapport | 2h | 🔴 Critique |
| 10.5 | **AD3 : Dashboard jobs** | Vue temps réel des jobs (en cours, dernière exec, prochaine) | 3h | 🟡 Important |
| 10.6 | **AD5 : Log tail** | Stream SSE logs serveur dans la page admin | 3h | 🟡 Important |
| 10.7 | **AD2 : Replay événement** | Sélection + re-play d'un événement passé | 2h | 🟢 Souhaitable |
| 10.8 | **AD7 : Diff config** | Comparer config actuelle vs par défaut | 1h | 🟢 Souhaitable |

### Critères de validation

- [ ] Simulateur de date permet de tester les jobs mensuels/hebdo
- [ ] Générateur de données crée un jeu réaliste en < 10s
- [ ] Lien admin absent de la sidebar utilisateur classique
- [ ] Smoke test bridges affiche rapport succès/échec pour chaque bridge
- [ ] Dashboard jobs montre le statut temps réel

---

## Phase 11 — Innovations

> **Objectif** : Différenciateurs UX, intelligence proactive
> **Durée estimée** : 3-5 jours
> **Prérequis** : Phases 6-9 terminées
> **Impact** : Wow factor, valeur quotidienne

### UX — Quick wins

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| X1 | **Mode Quick Add global (`Cmd+K`)** | Ajouter rapidement recette, article, note, tâche sans naviguer | ⭐⭐⭐ |
| X2 | **Widget tablette écran d'accueil** | Widget Android avec repas du jour + tâches urgentes | ⭐⭐⭐ |
| X3 | **PWA offline complète** | IndexedDB pour données critiques, sync au retour online | ⭐⭐ |

### Data & Intelligence

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| X6 | **Score foyer** | Indicateur composite : nutrition + budget + entretien + routines | ⭐⭐ |
| X7 | **Prédictions intelligentes** | ML sur 6 mois → prédire budget, courses, tâches | ⭐⭐⭐ |
| X8 | **Saisonnalité automatique** | Adapter recettes/jardin à la saison sans action | ⭐⭐ |
| X9 | **"Pourquoi cette suggestion ?"** | Transparence IA — expliquer d'où vient chaque suggestion | ⭐ |

### Intégrations

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| X11 | **Google Calendar sync bidirectionnelle** | Événements planning/tâches → Google Calendar auto | ⭐⭐⭐ |
| X12 | **Import recettes URL amélioré** | URL → parsing automatique de n'importe quel site | ⭐⭐ |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 11.1 | **X1 : Quick Add global** | `Cmd+K` → palette de commandes pour ajout rapide | 4h | 🔴 Critique |
| 11.2 | **X6 : Score foyer** | Indicateur composite affiché sur le dashboard | 3h | 🟡 Important |
| 11.3 | **X11 : Google Calendar sync** | Sync bidirectionnelle planning ↔ Google Calendar | 4h | 🟡 Important |
| 11.4 | **X9 : Transparence IA** | Tooltip "Pourquoi ?" sur chaque suggestion | 2h | 🟢 Souhaitable |
| 11.5 | **X8 : Saisonnalité auto** | Recettes/jardin s'adaptent à la saison sans action | 3h | 🟢 Souhaitable |

### Critères de validation

- [ ] `Cmd+K` ouvre une palette de commandes fonctionnelle
- [ ] Score foyer visible sur le dashboard avec évolution
- [ ] Événements planning apparaissent dans Google Calendar

---

## Annexe A — Bugs détectés (inventaire complet)

### Bugs critiques (impact utilisateur)

| # | Fichier | Problème | Impact | Phase |
|---|---------|----------|--------|-------|
| B1 | `src/api/routes/assistant.py` L88 | `/chat` contient un `pass` — ne fait rien | Réponse vide pour l'utilisateur | Phase 1 |
| B2 | `src/api/routes/famille_jules.py` L198 | Suivi alimentaire Jules = `pass` | Nutrition Jules cassée | Phase 1 |
| B3 | `src/api/routes/preferences.py` L389, L394 | Handlers préférences = `pass` | Préférences ne persistent pas | Phase 1 |
| B4 | `src/api/routes/dashboard.py` L765, L1264 | `except: pass` | Erreurs silencieusement avalées | Phase 1 |
| B5 | `src/core/models/jeux.py` L361 | Générateur données fictives si ID inexistant | Masque des bugs | Phase 1 |

### Bugs moyens (qualité/maintenabilité)

| # | Fichier | Problème | Impact | Phase |
|---|---------|----------|--------|-------|
| B6 | `src/core/models/famille.py` L74-83 | Forward references `# noqa: F821` | Analyse type cassée | Phase 1 |
| B7 | `src/api/routes/famille.py` et `maison.py` | Imports circulaires (late import) | Risque boucle infinie | Phase 1 |
| B8 | `src/core/models/systeme.py` | `SauvegardeMoelleOsseuseDB` — nommage incohérent | Confusion | Phase 1 |
| B9 | `frontend/src/bibliotheque/api/planning.ts` L196 | `harnessTablierMeteo()` non implémenté | Pas de météo planning | Phase 1 |
| B10 | `tests/services/batch_cooking/test_service.py` | ~15 tests `pytest.skip()` | 0% couverture batch | Phase 4 |

### Problèmes de cohérence

| # | Problème | Détail | Phase |
|---|----------|--------|-------|
| B11 | `admin/whatsapp-test/page.tsx` | Nom dit WhatsApp, contenu = Telegram | Phase 1 |
| B12 | `ia_avancee.ts` (underscore) | Tous les autres en kebab-case | Phase 2 |
| B13 | `sql/schema/13_views.sql` L107-129 | Index dupliqués (aussi dans `14_indexes.sql`) | Phase 3 |
| B14 | `sql/schema/17_migrations_absorbees.sql` | Fichier vide, migrations non absorbées | Phase 3 |

---

## Annexe B — Code mort et legacy (inventaire complet)

### Features actives mais rejetées

| # | Feature | Fichiers | Action | Phase |
|---|---------|----------|--------|-------|
| L1 | OCR/Scan tickets | `courses.py`, `upload.py`, `jeux_dashboard.py`, `maison_finances.py`, `ocr_service.py` | Supprimer tous les endpoints + service | Phase 1 |
| L2 | Intégration Vinted | `famille.py` schemas, `achats_ia.py` | Supprimer schemas + service | Phase 1 |
| L3 | Gamification familiale | `gamification.py` modèles, `dashboard.py` `/points-famille`, job `points_famille_hebdo` | Limiter au Garmin ou supprimer | Phase 1 |
| L4 | Jeu responsable | `jeux_dashboard.py` L555 | Supprimer toute référence | Phase 1 |

### Code legacy/historique

| # | Élément | Détail | Action | Phase |
|---|---------|--------|--------|-------|
| L5 | Commentaires Phase/Sprint | 150+ occurrences dans tout le code | Remplacer par descriptions fonctionnelles | Phase 2 |
| L6 | `ocr_service.py` | Marqué "Adaptateur legacy", toujours importé | Supprimer | Phase 1 |
| L7 | `rerun_profiler.py` | "Removed — only stubs no-op" | Supprimer | Phase 1 |
| L8 | Tables SQL orphelines | `stats_home`, `taches_home`, `archive_articles`, `journal_sante` | Drop si inutilisées | Phase 3 |
| L9 | `scripts/generate_screenshots.ts` | TypeScript dans dossier Python | Déplacer ou supprimer | Phase 1 |

### Fichiers mal nommés

| # | Fichier | Problème | Action | Phase |
|---|---------|----------|--------|-------|
| L10 | `fonctionnalites_avancees.py` | 16+ endpoints trop vague | Éclater par domaine | Phase 2 |
| L11 | `AUDIT_COMPLET_AVRIL_2026.md` | Audit historique | Archiver `docs/archive/` | Phase 2 |
| L12 | `PLANNING_IMPLEMENTATION.md` (ancien) | Plan historique | Remplacé par ce document | — |
| L13 | `admin/whatsapp-test/page.tsx` | Legacy WhatsApp | Renommer `telegram-test/` | Phase 1 |

---

## Annexe C — Commentaires Phase/Sprint à nettoyer

150+ occurrences. Règle : tout commentaire "Phase X" / "Sprint Y" → description fonctionnelle.

| Type | Pattern à chercher | Remplacement |
|------|-------------------|--------------|
| Backend Python | `# Phase X.Y`, `# Sprint N`, `# phase N`, `# Phase A2`, `# Phase B`, `# Phase M` | Description de ce que fait le code |
| Frontend TypeScript | `// Phase X`, `// Sprint N` | Idem |
| Fichiers de test | `test_phase_*.py`, `test_sprint_*.py` | Noms descriptifs |
| Documentation | `*SPRINT*.md`, `*PHASE*.md` | Sans référence temporelle |

---

## Annexe D — Fichiers fourre-tout à éclater

| Fichier | Lignes | Problème | Action | Phase |
|---------|--------|----------|--------|-------|
| `src/api/routes/fonctionnalites_avancees.py` | 16+ endpoints | Trop vague | Éclater (`batch_cooking_avance.py`, `tendances.py`, `journaux.py`) | Phase 2 |
| `frontend/.../courses/page.tsx` | 1200+ | Composants non extraits | Extraire dans `composants/courses/` | Phase 2 |
| `frontend/.../travaux/page.tsx` | 730+ | Composants non extraits | Extraire dans `composants/maison/` | Phase 2 |
| `frontend/.../validateurs.ts` | Long | Tous domaines mélangés | Éclater (`validateurs-recettes.ts`, etc.) | Phase 2 |

---

## Annexe E — Interactions inter-modules existantes

### Carte des 21+ bridges

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   CUISINE    │     │   FAMILLE    │     │    MAISON    │
│              │     │              │     │              │
│ Recettes     │◄────│ Jules growth │     │ Projets      │
│ Planning     │◄────│ (portions)   │     │ Entretien    │
│ Courses      │◄────│              │     │ Jardin ──────┼──► Planning
│ Inventaire   │◄────│ Budget ──────┼──►  │ Énergie      │
│ Batch cook.  │     │ Annivers. ───┼──►  │ Finances     │
│ Anti-gaspi   │◄────│ Garmin ──────┼──►  │ Diagnostics  │
│              │     │ Documents ───┼──►  │              │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  TRANSVERSAL  │
                    │ Chat IA ctx   │
                    │ Event bus     │
                    │ Notifications │
                    │ Dashboard     │
                    │ Automations   │
                    └───────────────┘
```

### Bridges détaillés

| Source → Cible | Bridge | Déclencheur |
|----------------|--------|-------------|
| Inventaire → Planning | `inter_module_inventaire_planning.py` | Stock bas → suggestions recettes |
| Profil Jules → Planning | `inter_module_jules_nutrition.py` | Repères Jules → adapter portions |
| Saisonnalité → Planning IA | `inter_module_saison_menu.py` | Changement mois → suggestions saisonnières |
| Courses total → Budget | `inter_module_courses_budget.py` | Achat validé → sync budget alimentation |
| Batch cooking → Stock | `inter_module_batch_inventaire.py` | Session terminée → déduire ingrédients |
| Péremption → Recettes | `inter_module_peremption_recettes.py` | J-3 → recettes anti-gaspillage |
| Jardin récolte → Planning | `inter_module_jardin_recettes.py` | Récolte → planning semaine suivante |
| Garmin → Santé | `inter_module_garmin_health.py` | Sync 6h → données activité |
| Documents → Calendrier | `inter_module_documents_notifications.py` | Expiration J-14 → événement + notif |
| Jeux P&L → Budget jeux | `inter_module_budget_jeux.py` | Résultats → catégorie budget jeux (séparé) |
| Anomalie budget → Alerte | `inter_module_budget_anomalie.py` | Dépassement +30% → notification |
| Anniversaire → Budget | `inter_module_anniversaires_budget.py` | J-14 → réserve budgétaire |
| Entretien → Courses | `inter_module_entretien_courses.py` | Tâche due → produits dans courses |
| Énergie → Analyse | `inter_module_energie_cuisine.py` | Hausse +20% → alerte + diagnostic |
| Photo diagnostic → Projet | `inter_module_diagnostics_ia.py` | Photo panne → IA → projet réparation |
| Multi-module → Chat IA | `inter_module_chat_contexte.py` | Message → contexte enrichi |
| Voyage → Planning | `inter_module_planning_voyage.py` | Départ → ajuster planning/quantités |

---

## Annexe F — IA existante & opportunités

### IA en place (10 services)

| Module | Utilisation | Service |
|--------|-------------|---------|
| Planning repas | Génération planning semaine | `BaseAIService.call_with_list_parsing_sync()` |
| Anti-gaspillage | Suggestions avec produits proches péremption | `AntiGaspillageService` |
| Batch cooking | Plan batch + étapes | `BatchCookingService` |
| Jules coaching | Conseils développement enfant | `JulesAIService` |
| Weekend | Suggestions activités (météo + Jules) | `WeekendAIService` |
| Dashboard | Résumé narratif hebdo | `DashboardService` |
| Diagnostics | Photo → diagnostic panne | `MultimodalService` |
| Estimation travaux | Photo → estimation coût | `MultimodalService` |
| Chat assistant | Conversation libre avec contexte | `AssistantService` (⚠️ stub B1) |
| Nutritionniste | Analyse nutritionnelle planning | `NutritionService` |

### Opportunités IA

| # | Opportunité | Complexité | Impact | Phase |
|---|-------------|------------|--------|-------|
| IA1 | Coach jardin photo plante (Vision) | Moyenne | ⭐⭐⭐ | Phase 7 |
| IA2 | Optimisateur énergie | Faible | ⭐⭐ | Phase 7 |
| IA3 | Résumé matinal Telegram personnalisé | Faible | ⭐⭐⭐ | Phase 7 |
| IA4 | Adaptation recettes "J'ai pas de X" | Moyenne | ⭐⭐⭐ | Phase 7 |
| IA5 | Prédiction restock intelligent | Moyenne | ⭐⭐⭐ | Phase 7 |
| IA6 | Assistant vocal mains-libres | Moyenne | ⭐⭐ | Phase 11 |
| IA7 | Tendances familiales mensuelles | Faible | ⭐⭐ | Phase 7 |
| IA8 | Planificateur sorties complet | Moyenne | ⭐⭐ | Phase 11 |
| IA9 | Courses intelligentes "oublié le lait" | Faible | ⭐⭐⭐ | Phase 7 |
| IA10 | Coach entretien prédictif | Faible | ⭐⭐ | Phase 7 |

---

## Annexe G — Jobs CRON existants (68)

| Heure | Job | Module | Canal |
|-------|-----|--------|-------|
| 06:00 | `alertes_peremption_48h` | Inventaire | push, ntfy |
| 06:00 | `garmin_sync_matinal` | Garmin | silencieux |
| 06:15 | `sync_recoltes_inventaire` | Jardin→Inventaire | silencieux |
| 07:00 | `rappels_famille` | Famille | push, ntfy, Telegram |
| 07:00 | `alerte_stock_bas` | Inventaire | push, ntfy |
| 07:00 | `alertes_energie` | Énergie | push, email |
| 07:30 | `digest_telegram_matinal` | Transversal | Telegram |
| 08:00 | `rappels_maison` | Maison | push, ntfy |
| 08:00 | `check_garmin_anomalies` | Garmin | push |
| 08:30 | `rappels_generaux` | Transversal | push, ntfy |
| 09:00 (lun) | `rappel_vaccins` | Santé | push, ntfy |
| 17:00 (ven) | `score_weekend` | Weekend | Telegram |
| 19:00 (dim) | `planning_semaine_si_vide` | Planning | push |
| 20:00 | `verification_budget_quotidien` | Budget | push si dépass. |
| 20:30 (dim) | `resume_hebdo_ia` | Transversal | Telegram, email |
| 22:00 | `sync_jeux_budget` | Jeux→Budget | silencieux |
| 22:15 (mar/ven) | `resultat_tirage_loto` | Jeux | Telegram |
| 23:00 | `sync_google_calendar` | Calendar | silencieux |
| 01:00 | `nettoyage_cache_7j` | Système | silencieux |
| 02:00 | `backup_donnees_critiques` | Système | email si erreur |
| 1er mois 08:15 | `rapport_mensuel_budget` | Budget | email |
| 1er mois 09:30 | `rapport_maison_mensuel` | Maison | email |
| Trimestriel | `tache_jardin_saisonniere` | Jardin | push |
| /5min | `automations_runner` | Moteur automations | variable |

---

## Annexe H — Telegram existant & extensions

### Commandes existantes (11)

`/planning`, `/courses`, `/ajout [article]`, `/repas [midi|soir]`, `/jules`, `/maison`, `/budget`, `/meteo`, `/menu`, `/aide`

### Nouvelles commandes proposées

| # | Commande | Description | Priorité | Phase |
|---|----------|-------------|----------|-------|
| T1 | `/inventaire` | Frigo avec icônes péremption | 🔴 | Phase 8 |
| T2 | `/recette [nom]` | Recette rapide avec ingrédients | 🔴 | Phase 8 |
| T3 | `/batch` | Résumé batch cooking | 🟡 | Phase 8 |
| T4 | `/jardin` | Tâches + récoltes | 🟡 | Phase 8 |
| T5 | `/energie` | KPIs énergie | 🟢 | Phase 8 |
| T6 | `/rappels` | Rappels en attente groupés | 🔴 | Phase 8 |
| T7 | `/timer [Xmin]` | Minuteur Telegram | 🟡 | Phase 8 |
| T8 | `/note [texte]` | Note rapide | 🟡 | Phase 8 |

### Interactions enrichies

| # | Feature | Description | Phase |
|---|---------|-------------|-------|
| T9 | Boutons validation courses | ✅ Acheté / ❌ Pas trouvé / 🔄 Reporter | Phase 8 |
| T10 | Mini-sondage repas | Boutons choix de repas | Phase 8 |
| T11 | Photo → IA | Photo frigo → suggestions recettes | Phase 8 |

---

## Annexe I — Email existant & propositions

### Emails existants

- Résumé hebdomadaire (dim 20h30)
- Rapport budget mensuel (1er)
- Rapport maison mensuel (1er)
- Alertes anomalies énergie/budget

### Emails proposés

| # | Email | Déclencheur | Phase |
|---|-------|-------------|-------|
| E1 | Résumé nutritionnel mensuel | 1er du mois | Phase 8 |
| E2 | Bilan trimestriel jardin | Trimestriel | Phase 8 |
| E4 | Backup confirmation | Après backup | Phase 8 |
| E5 | Rapport Jules mensuel | 1er du mois | Phase 8 |

---

## Annexe J — Admin existant & améliorations

### Capacités existantes (51 endpoints)

- ✅ Déclenchement manuel de n'importe quel job (`POST /admin/jobs/{id}/run`)
- ✅ Mode dry-run
- ✅ Simulation de flux sans effets de bord (`POST /admin/simulate/flow`)
- ✅ Console IA directe (`POST /admin/ai/console`)
- ✅ Test multi-canal notifications (`POST /admin/notifications/test-all`)
- ✅ Purge cache sélective (`POST /admin/cache/purge`)
- ✅ Feature flags runtime (18 flags)
- ✅ Mode maintenance / mode test
- ✅ Impersonation utilisateur (1h, audité)
- ✅ Export/import config complète
- ✅ Visualisation santé bridges (`GET /admin/bridges/status`)

### Améliorations proposées

| # | Feature | Description | Priorité | Phase |
|---|---------|-------------|----------|-------|
| AD1 | Smoke test bridges (1 clic) | Rapport visuel sur 21+ bridges | 🔴 | Phase 10 |
| AD2 | Replay événement | Depuis l'historique | 🟡 | Phase 10 |
| AD3 | Dashboard jobs temps réel | En cours, dernière, prochaine, taux succès | 🟡 | Phase 10 |
| AD4 | Simulateur de date | Tester jobs comme si une date | 🔴 | Phase 10 |
| AD5 | Log tail | SSE logs serveur dans admin | 🟡 | Phase 10 |
| AD6 | Générateur données test | Peupler DB réaliste | 🔴 | Phase 10 |
| AD7 | Diff config | Actuelle vs défaut | 🟢 | Phase 10 |
| AD8 | Admin invisible sidebar | Accès URL/raccourci seulement | 🔴 | Phase 10 |

---

## Annexe K — Visualisations existantes & améliorations UI

### Composants de visualisation existants (14)

| Type | Composant | Librairie | Module |
|------|-----------|-----------|--------|
| 3D Plan maison | `plan-3d.tsx` | Three.js / R3F | Maison |
| Jardin interactif | `vue-jardin-interactive.tsx` | SVG/Canvas | Maison |
| Heatmap numéros loto | `heatmap-numeros.tsx` | D3.js | Jeux |
| Heatmap cotes paris | `heatmap-cotes.tsx` | D3.js | Jeux |
| Heatmap nutritionnel | `heatmap-nutritionnel.tsx` | D3.js | Cuisine |
| Sankey flux financiers | `sankey-flux-financiers.tsx` | D3.js | Finances |
| Treemap budget | `treemap-budget.tsx` | D3.js | Budget |
| Treemap inventaire | `treemap-inventaire.tsx` | D3.js | Inventaire |
| Radar nutrition famille | `radar-nutrition-famille.tsx` | Recharts | Cuisine |
| Radar skills Jules | `radar-skill-jules.tsx` | Recharts | Famille |
| Calendrier énergie | `calendrier-energie.tsx` | D3.js | Maison |
| Graphe réseau modules | `graphe-reseau-modules.tsx` | D3.js | Admin |
| Sparklines | `sparkline.tsx` | SVG custom | Dashboard |
| Kanban projets | `kanban-projets.tsx` | @dnd-kit | Maison |
| Dashboard DnD | `grille-dashboard-dnd.tsx` | @dnd-kit | Dashboard |
| Timeline batch cooking | `timeline-batch-cooking.tsx` | Custom | Cuisine |

### Améliorations UI proposées

| # | Amélioration | Composant | Impact | Phase |
|---|-------------|-----------|--------|-------|
| UI1 | Calendrier repas mosaïque photos | Planning | ⭐⭐⭐ | Phase 9 |
| UI2 | Carte jardin 2D zones colorées | Jardin | ⭐⭐ | Phase 9 |
| UI3 | Graphe temporel dépenses annoté | Finances | ⭐⭐ | Phase 9 |
| UI4 | Dashboard widgets personnalisables | Dashboard | ⭐⭐⭐ | Phase 9 |
| UI5 | Timeline Jules style story | Jules | ⭐⭐⭐ | Phase 9 |
| UI6 | Mode cuisine tablette | Recettes | ⭐⭐⭐ | Phase 9 |
| UI7 | Sankey animé au survol | Finances | ⭐ | Phase 9 |
| UI8 | Progress bar batch animée | Batch | ⭐⭐ | Phase 9 |
| UI9 | Micro-interactions Framer Motion | Global | ⭐⭐ | Phase 9 |
| UI10 | Dark mode amélioré | Global | ⭐⭐ | Phase 9 |
| UI11 | Mini météo header | Layout | ⭐ | Phase 9 |
| UI12 | Skeleton contextuels | Global | ⭐ | Phase 9 |
| UI13 | Planning colonnes Google Calendar | Planning | ⭐⭐ | Phase 9 |
| UI14 | Gantt projets maison | Travaux | ⭐⭐ | Phase 9 |

---

## Annexe L — Simplification des flux utilisateur

| # | Flux actuel | Flux simplifié | Impact |
|---|------------|----------------|--------|
| F1 | Dashboard → Cuisine → Planning → Générer → Valider → Courses → Générer | Dashboard → **1 bouton "Planifier ma semaine"** → Validation → Courses auto | ⭐⭐⭐ |
| F2 | Créer recette → Revenir au planning → Ajouter | Bouton **"Ajouter au planning"** directement sur la recette | ⭐⭐⭐ |
| F3 | Inventaire → Péremptions → Anti-gaspi → Suggestions | **Push directe** avec suggestions anti-gaspillage | ⭐⭐⭐ |
| F4 | Ouvrir app → Chercher quoi faire → Naviguer | **Page Focus** comme page d'accueil par défaut | ⭐⭐ |
| F5 | Aller maison → Entretien → Tâches → Cocher | **Bouton ✅ Telegram** directement sur les tâches | ⭐⭐⭐ |

---

## Annexe M — Axes d'innovation

### UX — Quick wins

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| X1 | Quick Add global (`Cmd+K`) | Ajout rapide recette/article/note/tâche sans naviguer | ⭐⭐⭐ |
| X2 | Widget tablette Android | Repas du jour + tâches urgentes | ⭐⭐⭐ |
| X3 | PWA offline complète | IndexedDB, sync au retour online | ⭐⭐ |

### Data & Intelligence

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| X6 | Score foyer composite | nutrition + budget + entretien + routines | ⭐⭐ |
| X7 | Prédictions ML (6 mois données) | Budget, courses, tâches | ⭐⭐⭐ |
| X8 | Saisonnalité automatique | Recettes/jardin adaptés sans action | ⭐⭐ |
| X9 | "Pourquoi cette suggestion ?" | Transparence IA | ⭐ |

### Intégrations

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| X11 | Google Calendar sync bidi | Planning/tâches → Google Calendar auto | ⭐⭐⭐ |
| X12 | Import recettes URL amélioré | N'importe quel site → parsing auto | ⭐⭐ |

---

## Annexe N — Consolidation SQL détaillée

### Structure actuelle

```
sql/schema/
├── 01_users.sql        →  22_automations.sql  (22 fichiers ordonnés)
├── 13_views.sql        (✅ vues uniquement, sans index dupliqué)
├── 14_indexes.sql      (index principaux centralisés)
├── 17_migrations_absorbees.sql  (✅ consolidé et idempotent)
└── INIT_COMPLET.sql    (compilé, régénéré + SHA256 vérifié)
```

### Actions

| # | Action | Détail | Phase |
|---|--------|--------|-------|
| S1 | ✅ Dédupliquer indexes | `13_views.sql` nettoyé → index conservés uniquement dans `14_indexes.sql` | Phase 3 |
| S2 | ✅ Résoudre fichier 17 | `17_migrations_absorbees.sql` rempli avec le nettoyage absorbé | Phase 3 |
| S3 | ✅ Drop tables orphelines | `stats_home`, `taches_home`, `archive_articles`, `journal_sante` nettoyées/supprimées | Phase 3 |
| S4 | ✅ Valider la gamification SQL | plus aucune table générique legacy `badges` / `points` / `historique_gamification` active | Phase 3 |
| S5 | ✅ Régénérer INIT_COMPLET.sql | `python scripts/db/regenerate_init.py` exécuté avec succès | Phase 3 |
| S6 | ✅ Audit ORM↔SQL | `python scripts/analysis/audit_orm_sql.py` + `pytest tests/sql/test_schema_coherence.py -q` | Phase 3 |

---

## Récapitulatif effort & dépendances

### Effort par phase

| Phase | Durée estimée | Focus |
|-------|---------------|-------|
| **Phase 1** — Corrections critiques ✅ | 1 jour | Bugs `pass`, suppression OCR/Vinted/gamif/legacy |
| **Phase 2** — Nettoyage nommage | 3-4 jours | 150+ commentaires, renommages, fichiers fourre-tout |
| **Phase 3** — SQL ✅ | 1 jour | Déduplication indexes, nettoyage legacy, audit ORM↔SQL |
| **Phase 4** — Tests | 5-7 jours | Batch cooking, routes, bridges, E2E |
| **Phase 5** — Documentation | 2-3 jours | Fusions, INTER_MODULES_MAP, DEPRECATED |
| **Phase 6** — Inter-modules | 3-4 jours | 9 nouveaux bridges |
| **Phase 7** — IA & automations | 4-5 jours | 10 opportunités IA, 7 jobs, 5 automations |
| **Phase 8** — Telegram & email | 3-4 jours | 8 commandes, interactions enrichies, emails |
| **Phase 9** — UI/UX | 7-10 jours | 14 améliorations, accessibilité, simplification flux |
| **Phase 10** — Admin | 2-3 jours | Simulateur date, données test, smoke test bridges |
| **Phase 11** — Innovations | 3-5 jours | Quick Add, Score foyer, Google Calendar |
| | | |
| **TOTAL** | **~35-53 jours** | **Séquentiel. Parallélisable sur certaines phases.** |

### Graphe de dépendances

```
Phase 1 (Corrections critiques)
├── Phase 2 (Nettoyage nommage)
│   └── Phase 5 (Documentation)
├── Phase 3 (SQL)
├── Phase 4 (Tests) ← nécessite Phase 1 (stubs implémentés)
├── Phase 6 (Inter-modules)
│   └── Phase 7 (IA & automations)
│       └── Phase 8 (Telegram & email)
│           └── Phase 10 (Admin avancé)
└── Phase 9 (UI/UX) ← nécessite Phase 2 (code propre)

Phase 11 (Innovations) → après Phases 6-9
```

### Sprints parallélisables après Phase 1

- **Phase 2** + **Phase 3** + **Phase 4** + **Phase 6** peuvent être travaillées en parallèle
- **Phase 9** parallélisable avec **Phase 7** et **Phase 8**

---

> **Note finale** : L'application est notée **7.8/10** — architecture solide (backend 8.5, frontend 9.0, admin 9.0), IA bien intégrée (7.5), interactions inter-modules excellentes (8.5). Les axes d'amélioration prioritaires sont : **corriger les 5 bugs critiques `pass`** (Phase 1), **supprimer le code mort** (OCR, Vinted, gamif), **renforcer les tests** (5.5/10 — batch cooking 0%, E2E minimal), et **enrichir Telegram** comme hub mobile. Le flux utilisateur doit rester simple : max 2-3 clics pour toute action courante.
