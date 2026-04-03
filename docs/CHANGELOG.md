# Changelog

> Historique synthétique des grandes évolutions du projet.
>
> Ce document privilégie les jalons fonctionnels et techniques plutôt qu'un journal commit-par-commit.

---

## 2026-04-03 - Sprint 9 documentation finale

### Ajouté

- création de `docs/CHANGELOG.md`
- création de `docs/DEPRECATED.md`
- création de `docs/ADMIN_MODE.md`
- création de `docs/AUTOMATION_GUIDE.md`

### Mis à jour

- `README.md` aligné sur l'état actuel du projet et enrichi avec les guides de référence prioritaires
- `.github/copilot-instructions.md` aligné avec l'état actuel du périmètre produit
- `PLANNING_IMPLEMENTATION.md` mis à jour avec le statut réel du sprint 9
- nettoyage des références documentaires obsolètes dans les guides IA, jeux, famille et FAQ

### Nettoyage

- suppression des références documentaires liées aux fonctionnalités dépréciées hors historique dédié
- suppression des références `Phase ...` et assimilées dans les guides utilisateur concernés
- remplacement des références documentaires cassées (`API_SCHEMAS`, `TESTING_ADVANCED`)

### Reste à finaliser

- exemples Swagger systématiques sur l'ensemble des schémas Pydantic
- contraintes `max_length` homogènes sur l'ensemble des champs texte backend

---

## 2026 - Vague admin, observabilité et automatisations

### Canaux et notifications

- module admin étendu avec audit, jobs, services, cache, notifications, maintenance, re-sync et console rapide
- persistance des exécutions de jobs dans `job_executions`
- feature flags runtime admin et configuration dynamique
- matrice centralisée des jobs APScheduler dans `src/services/core/cron/jobs_schedule.py`
- monitoring services, cache, sécurité et métriques API/IA

### Effets visibles

- déclenchement manuel des jobs avec `dry_run`
- exécution par lot, simulation de journée et batch du matin
- mise à jour dynamique des schedules cron
- cockpit admin et journalisation des actions sensibles

---

## 2026 - Notifications et canaux conversationnels

### Livré

- Telegram est devenu le canal conversationnel de référence
- callbacks Telegram, digests, rappels et rapports proactifs
- templates admin de notifications Telegram et email
- guides d'exploitation Telegram et recette manuelle de validation

### Retiré

- dépendance fonctionnelle à l'ancien canal propriétaire de messagerie
- documentation active autour des anciens flux de messagerie

---

## 2026 - Consolidation fonctionnelle des modules

### Cuisine

- enrichissement recettes, planning repas, anti-gaspillage, batch cooking, prédiction courses et péremption
- meilleure articulation inventaire <-> courses <-> planning

### Famille

- refonte des activités, routines, achats, journal, weekend, documents et suivi Jules
- adaptation Jules aux repas de la famille avec contraintes enfant

### Maison

- extension des domaines projets, entretien, jardin, énergie, habitat, stocks et diagnostics

### Jeux

- consolidation paris, loto, Euromillions, analyses IA et tableaux de bord dédiés

### Dashboard et utilitaires

- agrégations multi-modules, anomalies budgétaires, chat IA et outils transverses

---

## 2026 - Durcissement du socle technique

### Backend

- généralisation du pattern `@service_factory`
- cache multi-niveaux, résilience, rate limiting et circuit breaker IA
- event bus, audit, observabilité et métriques Prometheus
- routes FastAPI uniformisées avec gestion d'erreurs et sessions SQL centralisées

### Frontend

- SPA Next.js App Router avec providers auth/query/theme
- TanStack Query + Zustand + Zod généralisés sur les modules principaux
- surface admin et navigation modulaire consolidées

### Documentation et qualité

- guides architecture, tests, services, SQLAlchemy, monitoring, deployment et design system
- inventaires repo/backend/frontend produits pendant les phases de stabilisation

---

## Repères historiques couverts

- phases fondatrices `A` à `H` : structuration backend, services, documentation et complétion progressive
- sprints `1` à `5` : base produit, hardening SQL/tests, premiers flux Telegram et rapports
- sprints `6` à `9` : consolidation modules, admin, documentation et nettoyage
- sprints `10` à `16` : admin avancé, jobs, notifications Telegram/email, IA et automatisations proactives
- sprints `17` à `19` : stabilisation, finalisations documentaires et alignement global

Pour les détails techniques par zone, voir aussi `docs/ARCHITECTURE.md`, `docs/CRON_JOBS.md`, `docs/ADMIN_RUNBOOK.md` et `docs/SERVICES_REFERENCE.md`.
