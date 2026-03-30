<!-- markdownlint-disable MD013 MD032 MD040 MD060 -->

# PLANNING D'IMPLÉMENTATION — Assistant MaTanne

> **Basé sur** : ANALYSE_COMPLETE.md — Audit 360° du 30 mars 2026
> **Périmètre** : Backend (FastAPI/Python) + Frontend (Next.js 16) + SQL + Tests + Docs + IA + Jobs + Notifications + Admin + UX + Gamification + Innovation
> **Objectif** : Transformer l'audit exhaustif en plan d'implémentation structuré, actionnable et priorisé — **toutes sections incluses**

---

## Table des matières

1. [Vue d'ensemble du projet & Métriques](#1-vue-densemble-du-projet--métriques)
2. [Inventaire complet (point de départ)](#2-inventaire-complet-point-de-départ)
3. [Bugs & implémentations incomplètes — Plan de résolution](#3-bugs--implémentations-incomplètes--plan-de-résolution)
4. [Gaps & features manquantes — Plan de comblement](#4-gaps--features-manquantes--plan-de-comblement)
5. [SQL — État et consolidation](#5-sql--état-et-consolidation)
6. [Tests — Couverture et plan d'amélioration](#6-tests--couverture-et-plan-damélioration)
7. [Documentation — Audit qualité et plan de mise à jour](#7-documentation--audit-qualité-et-plan-de-mise-à-jour)
8. [Interactions intra-modules — Référence & actions](#8-interactions-intra-modules--référence--actions)
9. [Interactions inter-modules — Référence & implémentations](#9-interactions-inter-modules--référence--implémentations)
10. [Opportunités IA — Plan d'enrichissement](#10-opportunités-ia--plan-denrichissement)
11. [Jobs automatiques (CRON) — Plan d'action](#11-jobs-automatiques-cron--plan-daction)
12. [Notifications — WhatsApp, Email, Push — Plan de consolidation](#12-notifications--whatsapp-email-push--plan-de-consolidation)
13. [Mode Admin manuel (test) — Plan d'implémentation](#13-mode-admin-manuel-test--plan-dimplémentation)
14. [UX — Simplification du flux utilisateur](#14-ux--simplification-du-flux-utilisateur)
15. [Gamification — Plan d'implémentation](#15-gamification--plan-dimplémentation)
16. [Axes d'innovation — Plan d'exploration](#16-axes-dinnovation--plan-dexploration)
17. [Plan d'action global priorisé par phase](#17-plan-daction-global-priorisé-par-phase)
18. [Annexe A — Fichiers à surveiller](#annexe-a--fichiers-à-surveiller)
19. [Annexe B — Stack technique complète](#annexe-b--stack-technique-complète)
20. [Annexe C — Variables d'environnement requises](#annexe-c--variables-denvironnement-requises)

---

## 1. Vue d'ensemble du projet & Métriques

### 1.1 Chiffres clés (point de départ)

| Métrique | Valeur |
|----------|--------|
| **Tables SQL** | 143 |
| **Modèles ORM** | 30 fichiers (~80+ classes) |
| **Routes API** | 242+ endpoints sur 35 fichiers |
| **Schémas Pydantic** | 24 fichiers |
| **Services métier** | 60+ services sur 13 packages |
| **Pages frontend** | 70+ pages complètes |
| **Composants React** | 104+ composants |
| **Clients API frontend** | 24 modules |
| **Hooks React** | 13 hooks custom |
| **Stores Zustand** | 4 stores |
| **Tests Python** | 45+ fichiers, 200+ tests |
| **Tests E2E (Playwright)** | 12 specs |
| **Fichiers documentation** | 30+ docs |
| **Jobs CRON** | 38+ jobs planifiés |
| **Données de référence** | 15 fichiers JSON/CSV |

### 1.2 Modules applicatifs — État et objectifs

| Module | Backend | Frontend | IA | Tests | Complétude | Objectif |
|--------|---------|----------|----|-------|------------|---------|
| 🍽️ Cuisine (recettes, planning, courses, inventaire, batch, anti-gaspi) | ✅ | ✅ | ✅ | ✅ | 95% | 98% |
| 👶 Famille (Jules, activités, routines, budget, voyages, contacts) | ✅ | ✅ | ✅ | ✅ | 90% | 95% |
| 🏡 Maison (projets, jardin, entretien, artisans, contrats, diagnostics) | ✅ | ✅ | ✅ | ✅ | 90% | 95% |
| 🏠 Habitat (immobilier, déco, plans, scénarios) | ✅ | ✅ | ✅ | ⚠️ | 85% | 92% |
| 🎮 Jeux (paris, loto, euromillions, bankroll) | ✅ | ✅ | ✅ | ✅ | 80% | 90% |
| 📊 Dashboard (agrégation, alertes, résumé IA) | ✅ | ✅ | ✅ | ⚠️ | 90% | 95% |
| 🛠️ Outils (chat IA, notes, météo, convertisseur, minuteur) | ✅ | ✅ | ✅ | ⚠️ | 85% | 90% |
| ⚙️ Admin (audit, jobs, cache, users, feature flags) | ✅ | ✅ | — | ✅ | 90% | 95% |

### 1.3 Scores actuels → Objectifs cibles

| Dimension | Score actuel | Objectif | Actions principales |
|-----------|-------------|----------|---------------------|
| Architecture | 9/10 | 9/10 | Maintenir |
| Sécurité | 9/10 | 9.5/10 | Guards admin frontend |
| Typage | 8/10 | 9/10 | Éliminer `# type: ignore`, compléter stubs |
| Tests | 6/10 | 8/10 | +150 tests ciblés (admin, cron, WhatsApp, multi-user) |
| Documentation | 6/10 | 8/10 | 6 docs manquantes + mise à jour guides |
| Couverture IA | 7/10 | 9/10 | 15 nouvelles features IA |
| Inter-modules | 5/10 | 8/10 | 13 interactions manquantes à implémenter |
| Notifications | 6/10 | 8/10 | Failover, préférences unifiées, throttling |
| Automatisations | 6/10 | 8/10 | 10 jobs CRON à ajouter |
| UX | 7/10 | 9/10 | 10 améliorations flux utilisateur |
| Gamification | 5/10 | 8/10 | Triggers badges sport + nutrition |

---

## 2. Inventaire complet (point de départ)

### 2.1 Backend — Routes API (35 fichiers)

**Auth** : login, register, forgot-password, refresh, me, 2FA (enable/verify/disable/status/login)

**Cuisine** :
- `recettes.py` — CRUD complet + import URL/PDF + version Jules + photo → recette + enrichir nutrition + depuis jardin + favoris + surprise (20+ endpoints)
- `courses.py` — CRUD listes + export + QR + depuis planning + scan code-barre + fusion + suggestions IA + WebSocket collaboration (20+ endpoints)
- `planning.py` — semaine/mensuel + conflits + repas + génération IA + suggestions rapides + export iCal (15+ endpoints)
- `inventaire.py` — CRUD articles + alertes péremption
- `batch_cooking.py` — sessions + génération IA
- `anti_gaspillage.py` — suggestions IA anti-gaspillage
- `suggestions.py` — suggestions IA globales

**Famille** :
- `famille.py` — profils enfants, jalons, activités, routines, budget, événements, anniversaires, contacts, documents, santé, weekend IA, shopping Vinted

**Maison** :
- `maison_projets.py` — projets + estimation IA + priorisation IA
- `maison_jardin.py` — éléments jardin + calendrier semis + suggestions IA + stocks + traitements nuisibles (500+ lignes)
- `maison_finances.py` — artisans + contrats + garanties/SAV + diagnostics photo IA + estimations immobilières + éco-actions + charges + dépenses (900+ lignes)

**Jeux** :
- `jeux.py` — paris sportifs (dashboard, matchs, prédictions, bankroll Kelly, stats, alertes séries, value bets) + loto (tirages, grilles, stats, génération) + euromillions (tirages, grilles, IA, analyse expert) + jeu responsable + OCR ticket (2400+ lignes)

**Support** :
- `admin.py`, `assistant.py`, `automations.py`, `calendriers.py`, `dashboard.py`, `documents.py`, `export.py`, `habitat.py`, `garmin.py`, `partage.py`, `preferences.py`, `push.py`, `recherche.py`, `rgpd.py`, `upload.py`, `utilitaires.py`, `voyages.py`, `webhooks.py`, `webhooks_whatsapp.py`

### 2.2 Backend — Services (60+ services)

| Package | Services clés |
|---------|---------------|
| `core/base/` | BaseAIService, streaming, mixins, protocols, pipeline |
| `core/registry` | ServiceFactory (@service_factory singletons) |
| `core/cron/` | Scheduler, jobs planifiés |
| `core/notifications/` | Dispatcher multi-canal (ntfy, push, email, WhatsApp) |
| `core/events/` | Bus pub/sub avec wildcards |
| `core/utilisateur/` | Auth, profils, 2FA, historique |
| `core/backup/` | Backup & restore |
| `cuisine/recettes/` | CRUD + import + enrichissement + recherche |
| `cuisine/courses/` | Listes + suggestions IA |
| `cuisine/planning/` | Planification + nutrition + agrégation |
| `cuisine/batch_cooking/` | Sessions batch cooking |
| `famille/` | Jules IA, Weekend IA, Soirée IA, Budget IA, Achats IA, Résumé hebdo |
| `maison/` | 10+ CRUD services + conseiller IA + énergie anomalies IA |
| `jeux/` | Bankroll (Kelly), IA paris, CRON loteries, stats personnelles |
| `integrations/` | Multimodal (Pixtral), codes-barres, ticket OCR, météo, Google Calendar, Garmin |
| `dashboard/` | Agrégation, résumé famille IA, anomalies financières, points gamification |

### 2.3 Frontend — Pages (70+)

| Module | Pages | Sous-pages notables |
|--------|-------|---------------------|
| Dashboard | 1 | 11 widgets configurables |
| Cuisine | 12 | recettes, courses, inventaire, planning, batch-cooking, anti-gaspillage, nutrition, photo-frigo |
| Famille | 19 | jules, activités, anniversaires, budget, calendriers, contacts, documents, gamification, garmin, journal, routines, timeline, voyages, weekend |
| Maison | 17 | travaux, jardin, ménage, équipements, artisans, charges, contrats, diagnostics, meubles, provisions, visualisation 3D, finances |
| Habitat | 9 | marché, jardin, déco, plans, scénarios, veille-immo, **veille-emploi** |
| Jeux | 11 | paris, loto, euromillions, bankroll, performance, jeu responsable, OCR ticket |
| Outils | 12 | chat-ia, assistant-vocal, notes, météo, minuteur, convertisseur, nutritionniste, automations |
| Paramètres | 1 | 7 onglets (profil, cuisine, notifications, affichage, IA, données, sécurité) |
| Admin | 6 | dashboard, utilisateurs, jobs, notifications, services, sql-views |

### 2.4 Composants UI (104+)

- **shadcn/ui** : 29 composants de base (button, card, dialog, tabs, table, sidebar, etc.)
- **Layout** : 16 composants (sidebar, header, nav-mobile, onboarding, recherche globale, FAB chat IA, minuteur flottant, etc.)
- **Cuisine** : 8 composants (formulaire recette, badge nutriscore/ecoscore, import, QR, etc.)
- **Famille** : 9 composants (graphique croissance, suggestion IA, anniversaire, budget insights, etc.)
- **Maison** : 14 composants (plan 3D, drawer projet/garantie, cartes alertes/conseils/tâches, etc.)
- **Jeux** : 13 composants (tableaux expert, heatmaps, grille IA pondérée, bankroll widget, pattern detection, etc.)
- **Graphiques** : 4 composants (ROI, jalons, camembert budget)
- **Habitat** : 3 composants (graphiques marché, entête, carte veille)

---

## 3. Bugs & implémentations incomplètes — Plan de résolution

### 3.1 🔴 P0 — Bloquants

| # | Fichier | Ligne | Description | Impact | Action |
|---|---------|-------|-------------|--------|--------|
| 1 | `src/services/jeux/cron_jobs_loteries.py` | 51 | `# TODO: Implémenter scraping réel` — Le scraping FDJ est en mode **SIMULATION uniquement** | Le module Loto/Euromillions ne récupère aucune donnée réelle | Implémenter source de données loterie réelle (API ou scraping FDJ) |
| 2 | `src/services/jeux/cron_jobs_loteries.py` | 67 | `# TODO: Insérer vrai tirage depuis API` — Insertion de données fictives | Les tirages affichés sont faux | Idem — fait partie du même correctif |
| 3 | `src/services/cuisine/cron_cuisine.py` | 63 | Alertes péremption détectées mais **notifications jamais envoyées** | L'utilisateur n'est pas prévenu des produits qui expirent | Câbler les notifications push/WhatsApp sur les alertes péremption |
| 4 | `src/services/cuisine/cron_cuisine.py` | 105 | Planning manquant détecté mais **aucun rappel envoyé** | L'utilisateur oublie de planifier ses repas | Câbler le rappel planning manquant |
| 5 | `src/services/cuisine/cron_cuisine.py` | 133 | Stock bas détecté mais **pas d'ajout auto à la liste de courses** | Circuit inventaire → courses cassé | Connecter stock bas → ajout auto courses |

### 3.2 🟡 P1 — Importants

| # | Fichier | Ligne | Description | Impact | Action |
|---|---------|-------|-------------|--------|--------|
| 6 | `src/api/routes/preferences.py` | 285 | `pass` — Échec silencieux du parsing de l'heure | Préférences horaires potentiellement ignorées | Ajouter log d'avertissement + valeur par défaut explicite |
| 7 | `src/api/routes/webhooks_whatsapp.py` | 576 | `pass` — Échec silencieux du parsing de date | Les rappels anniversaires WhatsApp peuvent dysfonctionner | Ajouter log + gestion d'erreur |
| 8 | `src/services/famille/version_recette_jules.py` | 37 | `...` — Implémentation incomplète | Adaptation recettes pour Jules partiellement fonctionnelle | Compléter l'implémentation |
| 9 | `src/api/routes/admin.py` | — | Historique des jobs uniquement en mémoire | Perdu au redémarrage du serveur | Persister en DB (Phase 7) |

### 3.3 🟢 P2 — Mineurs

| # | Fichier | Ligne | Description | Action |
|---|---------|-------|-------------|--------|
| 10 | `src/api/routes/export.py` | 204 | `pass` — Content-type permissif (intentionnel) | Aucune — intentionnel |
| 11 | `src/api/routes/auth.py` | 94 | `pass` — Fallback numeric parse (intentionnel) | Aucune — intentionnel |
| 12 | `src/api/routes/planning.py` | 688 | `...` — Placeholder docstring | Ajouter la docstring |

### 3.4 Recherche globale TODO/FIXME/HACK

| Marqueur | Nombre | Localisation |
|----------|--------|--------------|
| `TODO` | 6 | cuisine/cron (3), jeux/cron (2), scripts/analysis (1) |
| `FIXME` | 0 | ✅ Aucun |
| `HACK` | 0 | ✅ Aucun |
| `NotImplemented` | 0 | ✅ Aucun en code (seulement règle linter) |

---

## 4. Gaps & features manquantes — Plan de comblement

### 4.1 Fonctionnalités backend manquantes

| Module | Feature manquante | Priorité | Effort | Phase |
|--------|-------------------|----------|--------|-------|
| **Cuisine** | Notifications push/WhatsApp pour alertes péremption | P0 | Faible | 1 |
| **Cuisine** | Rappel automatique si planning semaine non rempli | P0 | Faible | 1 |
| **Cuisine** | Ajout automatique à la liste de courses si stock bas | P0 | Moyen | 1 |
| **Jeux** | Scraping réel tirages FDJ (Loto + EuroMillions) | P0 | Moyen | 1 |
| **Jeux** | API tirage en temps réel (ou source de données fiable) | P1 | Moyen | 1 |
| **Admin** | Persistance historique jobs en DB (pas juste mémoire) | P1 | Faible | 7 |
| **WhatsApp** | Validation numéro de téléphone | P1 | Faible | 5 |
| **WhatsApp** | Rate limiting sur les envois | P1 | Faible | 5 |
| **WhatsApp** | Fonction `_envoyer_aide_admin()` manquante (référencée mais non définie) | P1 | Faible | 5 |
| **Email** | Système de templates HTML (Jinja2 + dossier templates/) | P2 | Moyen | 5 |
| **Notifications** | Failover entre canaux (si push échoue → essayer email → WhatsApp) | P2 | Moyen | 5 |
| **Gamification** | Triggers badges sport + nutrition (pas implémentés dans le code) | P2 | Moyen | 9 |
| **Inventaire** | `suggerer_courses_ia()` marqué `# pragma: no cover` — non implémenté | P2 | Moyen | 6 |
| **Planning** | Suggestions IA pour périodes chargées (planning intelligent) | P2 | Moyen | 6 |

### 4.2 Fonctionnalités frontend manquantes

| Module | Feature manquante | Priorité | Phase |
|--------|-------------------|----------|-------|
| **Admin** | Toggle "Mode Debug" visible admin-only | P1 | 1 |
| **Famille** | Trop de sous-menus (19) — regrouper en catégories | P2 | 4 |
| **Gamification** | Détail des badges sport + nutrition (liste, progression) | P2 | 9 |
| **All** | Mode offline (service worker + queue) — partiellement implémenté | P3 | 10 |

---

## 5. SQL — État et consolidation

### 5.1 État actuel

| Élément | Valeur |
|---------|--------|
| Fichier principal | `sql/INIT_COMPLET.sql` (~3 366 lignes) |
| Tables | 143 CREATE TABLE |
| Migrations appliquées | 5 fichiers (V003 à V007) |
| Stratégie | SQL-direct (Alembic archivé depuis Sprint 7) |

### 5.2 Cohérence ORM ↔ SQL

✅ **Pas d'incohérences majeures détectées** entre les 30 fichiers modèles SQLAlchemy et le schéma SQL.

### 5.3 Plan de consolidation SQL

| # | Action | Description | Priorité | Phase |
|---|--------|-------------|----------|-------|
| 1 | **Absorber V003→V007 dans INIT_COMPLET** | Les 5 migrations doivent être fusionnées dans le fichier maître puisqu'on est en dev | P1 | 1 |
| 2 | **Supprimer le dossier `alembic/`** | Archivé et inutile — source de confusion | P2 | 1 |
| 3 | **Ajouter un script de vérification ORM↔SQL** | `scripts/audit_orm_sql.py` existe déjà — le rendre automatique dans CI | P2 | 3 |
| 4 | **Documenter les index** | Certaines tables manquent d'index explicites sur les FK fréquemment requêtées | P3 | 8 |
| 5 | **Centraliser les ENUMs SQL** | Certains ENUMs sont définis inline dans CREATE — les centraliser en début de fichier | P3 | 8 |

### 5.4 Tables à vérifier

| Catégorie | Tables | Notes |
|-----------|--------|-------|
| Tables orphelines potentielles | `openfoodfacts_cache`, `alertes_meteo`, `config_meteo` | Vérifier si utilisées activement |
| Tables très spécialisées | `presse_papier_entrees`, `mots_de_passe_maison`, `liens_favoris` | Peu de références dans le code |
| Tables volumineuses | `jeux_cotes_historique`, `historique_actions`, `logs_securite` | Prévoir purge/archivage |

---

## 6. Tests — Couverture et plan d'amélioration

### 6.1 État actuel

| Catégorie | Fichiers | Tests approx. | Couverture |
|-----------|----------|---------------|------------|
| API Routes | 38 fichiers | 150+ | ✅ Bonne |
| Services | 13 répertoires | 40+ | ⚠️ Moyenne |
| Core (cache, config, DB, decorators) | 13+ fichiers | 50+ | ✅ Bonne |
| Benchmarks | 1 fichier | 5+ | ⚠️ Basique |
| Contracts (OpenAPI/Schemathesis) | 1 fichier | Auto | ✅ Bon |
| Load (k6) | 1 fichier | Auto | ⚠️ Basique |
| SQL cohérence | 1 fichier | Auto | ✅ Bon |
| Frontend unit (Vitest) | stores + composants | 10+ | ⚠️ Faible |
| Frontend E2E (Playwright) | 12 fichiers | 30+ | ✅ Bonne |

### 6.2 Modules sans tests ou avec tests insuffisants

| Module/Service | Fichiers de test | Verdict |
|----------------|-----------------|---------|
| `services/habitat/` | ❌ Aucun test service dédié | **Manque** |
| `services/dashboard/` | ❌ Aucun test service dédié | **Manque** |
| `services/utilitaires/` | ❌ Aucun test service dédié | **Manque** |
| `services/integrations/weather/` | ❌ Aucun test | **Manque** |
| `services/integrations/google_calendar.py` | ❌ Aucun test | **Manque** |
| `services/integrations/garmin/` | Test basique via API route | **Insuffisant** |
| `core/ai/` | Tests basiques | **À renforcer** |
| `core/caching/` | test_cache + test_cache_multi | ✅ OK |
| Frontend composants | Pas de tests unitaires composants | **Manque** |
| Frontend hooks | Pas de tests unitaires hooks | **Manque** |

### 6.3 Plan d'amélioration tests

| # | Action | Priorité | Effort | Phase |
|---|--------|----------|--------|-------|
| 1 | Ajouter tests services habitat (plans IA, déco IA) | P1 | Moyen | 3 |
| 2 | Ajouter tests services dashboard (agrégation, anomalies) | P1 | Moyen | 3 |
| 3 | Tests fonctionnels intégrations (météo, calendrier Google, Garmin) | P1 | Moyen | 3 |
| 4 | Tests composants React (formulaire-recette, plan-3d, heatmaps) | P2 | Élevé | 3 |
| 5 | Tests hooks React (utiliser-websocket, utiliser-crud) | P2 | Moyen | 3 |
| 6 | Augmenter seuils couverture Vitest (50% → 70% lignes) | P2 | — | 3 |
| 7 | Ajouter tests de performance backend (au-delà de k6 baseline) | P3 | Élevé | 10 |
| 8 | Tests mutation (mutmut) intégrés en CI | P3 | Moyen | 10 |

---

## 7. Documentation — Audit qualité et plan de mise à jour

### 7.1 Inventaire docs existantes

| Fichier | Lignes | Qualité | À jour |
|---------|--------|---------|--------|
| `ARCHITECTURE.md` | Complet | ✅ Excellent | ✅ |
| `MODULES.md` | Complet | ✅ Excellent | ✅ |
| `API_REFERENCE.md` | 242 endpoints | ✅ Excellent | ✅ |
| `SERVICES_REFERENCE.md` | Modéré | ✅ Bon | ⚠️ |
| `PATTERNS.md` | Complet | ✅ Excellent | ✅ |
| `DEPLOYMENT.md` | Complet | ✅ Excellent | ✅ |
| `DEVELOPER_SETUP.md` | Complet | ✅ Excellent | ✅ |
| `ERD_SCHEMA.md` | Modéré | ✅ Bon | ⚠️ |
| `TESTING_ADVANCED.md` | Modéré | ✅ Bon | ✅ |
| `MIGRATION_GUIDE.md` | Modéré | ✅ Bon | ✅ |
| `INTER_MODULES.md` | Modéré | ✅ Bon | ⚠️ |
| `NOTIFICATIONS.md` | Modéré | ✅ Bon | ✅ |
| `CRON_JOBS.md` | Modéré | ✅ Bon | ✅ |
| `AUTOMATIONS.md` | Modéré | ✅ Bon | ⚠️ |
| `guides/` (8 sous-dossiers) | Varié | ✅ Bon | ⚠️ |
| `user-guide/` | FAQ + getting-started | ✅ Bon | ⚠️ |

### 7.2 Docs manquantes à créer

| # | Document | Contenu attendu | Priorité | Phase |
|---|----------|-----------------|----------|-------|
| 1 | `FRONTEND_ARCHITECTURE.md` | Architecture CSS (Tailwind v4), composants, state management, routing | P1 | 3 |
| 2 | `ADMIN_GUIDE.md` | Guide dédié au panneau admin (jobs, feature flags, notifications test) | P1 | 3 |
| 3 | `WHATSAPP_SETUP.md` | Configuration Meta WhatsApp Business API, commandes disponibles | P2 | 3 |
| 4 | `GAMIFICATION.md` | Système de points/badges sport + nutrition uniquement | P2 | 9 |
| 5 | `HABITAT_MODULE.md` | Guide spécifique module habitat/immobilier | P3 | 10 |
| 6 | `CHANGELOG.md` | Historique des versions/sprints | P3 | 10 |

### 7.3 Docs à mettre à jour

| Document | Raison | Phase |
|----------|--------|-------|
| `SERVICES_REFERENCE.md` | Ajouter les 10+ nouveaux services maison CRUD | 3 |
| `ERD_SCHEMA.md` | Ajouter diagrammes pour tables habitat, garmin, gamification (sport+nutrition) | 3 |
| `INTER_MODULES.md` | Documenter les nouveaux flux inter-modules (jardin→recettes, garmin→points) | 3 |
| `AUTOMATIONS.md` | Ajouter les 38 jobs CRON et leur statut actuel | 3 |

---

## 8. Interactions intra-modules — Référence & actions

### 8.1 Cuisine (déjà connecté)

```
Recettes ←→ Ingrédients ←→ Étapes
    ↓                         ↓
Planning ──→ Courses ←── Inventaire
    ↓              ↓
Batch Cooking    Anti-gaspi
    ↓              ↓
Nutrition ←────────┘
```

**Connexions manquantes intra-cuisine** :

| # | De | Vers | Action | État | Phase |
|---|-----|------|--------|------|-------|
| 1 | Inventaire (stock bas) | Courses (ajout auto) | Ingrédient expirant → article courses | ❌ Non connecté | 1 |
| 2 | Anti-gaspi (produits expirants) | Recettes (suggestions) | Suggérer recettes avec produits à consommer | ⚠️ Logique existe mais pas déclenchée auto | 2 |
| 3 | Batch cooking (session terminée) | Inventaire (mise à jour stock) | Déduire les ingrédients utilisés du stock | ❌ Non connecté | 2 |
| 4 | Recettes (saison) | Planning (suggestions saisonnières) | Proposer recettes de saison en priorité | ⚠️ Partiellement | 6 |

### 8.2 Famille (déjà connecté)

```
Jules (développement) ──→ Activités ──→ Routines
         ↓                                  ↓
    Santé/Croissance              Budget familial
         ↓                                  ↓
    Gamification ←──── Garmin      Contacts/Documents
```

**Connexions manquantes intra-famille** :

| # | De | Vers | Action | État | Phase |
|---|-----|------|--------|------|-------|
| 1 | Anniversaires | Budget | Provisioner budget cadeaux automatiquement | ❌ | 2 |
| 2 | Voyages | Budget | Intégrer dépenses voyage dans budget | ❌ | 2 |
| 3 | Routines | Gamification | ~~Points pour routines complétées~~ **Exclu** — gamification limitée au sport + nutrition | ❌ Exclu | — |
| 4 | Documents (expiration) | Notifications | Alertes documents expirants | ⚠️ Existe mais notification pas envoyée | 2 |

### 8.3 Maison (déjà connecté)

```
Projets ←→ Artisans ←→ Contrats
    ↓          ↓           ↓
Tâches    Interventions  Garanties/SAV
    ↓                        ↓
Entretien ──→ Diagnostics ←─┘
    ↓
Jardin ←→ Stocks/Provisions
```

**Connexions manquantes intra-maison** :

| # | De | Vers | Action | État | Phase |
|---|-----|------|--------|------|-------|
| 1 | Diagnostics (problème détecté) | Artisans (matching) | Suggérer artisans pour le problème diagnostiqué | ⚠️ IA existe mais pas auto | 6 |
| 2 | Entretien saisonnier | Stocks | Vérifier si produits d'entretien en stock | ❌ | 8 |
| 3 | Charges (facture élevée) | Énergie anomalies IA | Déclencher analyse si facture anormale | ❌ | 8 |

---

## 9. Interactions inter-modules — Référence & implémentations

### 9.1 Connexions existantes (actives)

```
┌──────────┐      ┌──────────┐      ┌──────────┐
│  Cuisine │──────│ Planning │──────│  Courses │
└────┬─────┘      └─────┬────┘      └─────┬────┘
     │                  │                  │
     │    ┌─────────────┘                  │
     │    │                                │
┌────▼────▼─┐     ┌──────────┐      ┌─────▼────┐
│  Famille  │     │  Maison  │      │Inventaire│
└────┬──────┘     └─────┬────┘      └──────────┘
     │                  │
     │    ┌─────────────┘
     │    │
┌────▼────▼─┐
│ Dashboard │ ←── Agrège TOUS les modules
└───────────┘
```

| De | Vers | Flux | État |
|----|------|------|------|
| Planning | Courses | Générer liste depuis planning repas | ✅ Actif |
| Recettes | Famille/Jules | Adapter recettes pour enfant | ✅ Actif |
| Jardin (récoltes) | Recettes | Recettes depuis le jardin | ✅ Actif |
| Dashboard | Tous | Agréger métriques de tous les modules | ✅ Actif |
| Garmin | Gamification | Steps → points sport | ✅ Actif |
| Cuisine | Gamification | Anti-gaspi → points alimentation | ✅ Actif |

### 9.2 Exclusions volontaires

| Connexion | Raison |
|-----------|--------|
| Jeux (gains/pertes) → Budget famille | L'argent gagné via les paris reste dans l'app de pari, pas de sync vers le budget familial |
| Garmin (sommeil) → Famille/Jules | Le suivi du sommeil via Garmin (ou autre) n'est pas souhaité — hors périmètre |
| Gamification → autres modules | La gamification est limitée au sport et à la nutrition. Pas de badges/points pour recettes, routines, maison, jardin, budget, etc. |

### 9.3 Connexions inter-modules manquantes (à implémenter)

| # | De | Vers | Flux proposé | Priorité | Impact | Phase |
|---|-----|------|-------------|----------|--------|-------|
| 1 | **Inventaire (péremption)** | **Recettes (suggestions)** | Produits expirant sous 48h → proposer recettes les utilisant | P1 | ★★★ | 2 |
| 2 | **Météo** | **Planning repas** | Temps froid → suggestions plats chauds ; canicule → salades/gazpacho | P2 | ★★ | 6 |
| 3 | **Météo** | **Jardin** | Gel annoncé → alerte protection plantes ; pluie → ne pas arroser | P2 | ★★ | 6 |
| 4 | **Météo** | **Activités famille** | Pluie → indoor ; beau temps → outdoor ; neige → luge/ski | P2 | ★★ | 6 |
| 5 | **Entretien maison** | **Budget maison** | Intervention artisan → dépense budget automatique | P2 | ★★ | 8 |
| 6 | **Courses (achat)** | **Budget famille** | Total courses → catégorie alimentation budget | P1 | ★★★ | 2 |
| 7 | **Batch cooking** | **Inventaire** | Session terminée → déduire ingrédients consommés | P2 | ★★ | 2 |
| 8 | **Anniversaires** | **Courses** | Anniversaire proche → ajouter idées cadeaux/courses fête | P3 | ★ | 10 |
| 9 | **Voyages** | **Calendrier/Planning** | Voyage planifié → bloquer jours planning repas + activités | P2 | ★★ | 8 |
| 10 | **Contrats (fin proche)** | **Budget** | Contrat expirant → provisionner renouvellement | P3 | ★ | 10 |
| 11 | **Charges (énergie)** | **Dashboard** | Anomalie conso → alerte widget dashboard | P2 | ★★ | 8 |
| 12 | **Documents (expiration)** | **Notifications** | Passeport/carte identité expirant → rappel multi-canal | P1 | ★★★ | 2 |
| 13 | **Chat IA** | **Contexte multi-module** | Le chat IA connaît le contenu du frigo, le planning, les courses, le budget | P1 | ★★★ | 2 |

---

## 10. Opportunités IA — Plan d'enrichissement

### 10.1 Modules AVEC IA déjà intégrée (25+ services)

| Module | Services IA | Fonctionnalité |
|--------|-------------|----------------|
| Cuisine | Suggestions recettes, import URL/PDF, enrichissement nutritionnel, batch cooking, anti-gaspi, courses intelligentes | ✅ Complet |
| Famille | Jules IA (développement), Weekend IA, Soirée IA, Budget IA (anomalies), Achats IA, Résumé hebdo | ✅ Complet |
| Maison | Entretien IA, Conseiller maison, Énergie anomalies, Diagnostics photo (Pixtral), Fiches tâches IA | ✅ Complet |
| Habitat | Plans IA, Déco IA | ✅ Bon |
| Jeux | Paris sportifs IA, EuroMillions IA | ✅ Bon |
| Dashboard | Résumé famille IA, Anomalies financières IA | ✅ Bon |
| Outils | Chat IA généraliste, OCR factures/tickets | ✅ Bon |

### 10.2 Nouvelles opportunités IA (à implémenter)

| # | Module | Feature IA | Description | Priorité | Effort | Phase |
|---|--------|-----------|-------------|----------|--------|-------|
| 1 | **Inventaire** | Suggestion achats intelligents | Analyser historique de consommation → prévoir les besoins | P1 | Moyen | 6 |
| 2 | **Planning** | Planning adaptatif | Ajuster le planning selon météo, énergie (Garmin), budget restant | P1 | Élevé | 6 |
| 3 | **Routines** | Optimisation routines | Analyser l'efficacité des routines et suggérer des améliorations | P2 | Moyen | 6 |
| 4 | **Contacts** | Enrichissement contacts | Suggérer catégorisation, rappels relationnels (« vous n'avez pas contacté X depuis 3 mois ») | P3 | Faible | 10 |
| 5 | **Anniversaires** | Idées cadeaux IA | Profil de la personne → 5 idées cadeaux avec budget | P2 | Faible | 6 |
| 6 | **Documents** | Analyse documents photo | Photographier un document → extraction OCR + classement auto | P2 | Moyen | 6 |
| 7 | **Jardin** | Diagnostic plantes photo | Photo d'une plante malade → diagnostic + traitement IA (Pixtral) | P1 | Faible (infra existe) | 6 |
| 8 | **Budget** | Prévision dépenses | Modèle prédictif basé sur l'historique → « vous allez dépasser votre budget fin de mois » | P1 | Moyen | 6 |
| 9 | **Courses** | Optimisation parcours magasin | Grouper les articles par rayon → ordre de parcours optimal | P3 | Moyen | 10 |
| 10 | **Chat IA** | Contexte multi-module | Le chat connaît frigo, planning, budget, météo, Jules → réponses contextuelles | P1 | Élevé | 2 |
| 11 | **Maison** | Estimation travaux IA améliorée | Photo avant/après + description → estimation coût/durée réaliste | P2 | Moyen | 6 |
| 12 | **Voyages** | Planning voyage IA | Destination + dates + budget → itinéraire complet avec activités | P2 | Moyen | 6 |
| 13 | **Énergie** | Recommandations économies | Analyser relevés compteurs → top 3 actions pour réduire la facture | P2 | Faible | 6 |
| 14 | **Loto/Euromillions** | Analyse tendances avancée | Analyse de fréquence + patterns + générateur statistique amélioré | P3 | Moyen | 10 |
| 15 | **Entretien** | Prédiction pannes | Historique entretien + âge équipements → « votre chauffe-eau aura probablement besoin d'entretien dans 3 mois » | P2 | Moyen | 6 |

---

## 11. Jobs automatiques (CRON) — Plan d'action

### 11.1 Jobs existants (38+)

| Job | Horaire | Module | Statut | Action requise |
|-----|---------|--------|--------|----------------|
| `alertes_peremption_48h` | Quotidien 7h | Cuisine | ✅ OK | ✅ Phase 1 — notification câblée |
| `suggestion_planning_semaine` | Dimanche 18h | Cuisine | ✅ OK | ✅ Phase 1 — notification câblée |
| `alerte_stock_bas` | Quotidien 8h | Cuisine | ✅ OK | ✅ Phase 1 — auto-ajout courses connecté |
| `nettoyage_plannings_anciens` | Mensuel | Cuisine | ✅ OK | Aucune |
| `rappels_famille` | Quotidien 7h | Famille | ✅ OK | Aucune |
| `rappels_maison` | Quotidien 8h | Maison | ✅ OK | Aucune |
| `points_famille_hebdo` | Dimanche 20h | Gamification | ✅ OK | Aucune |
| `scraper_resultats_fdj` | Quotidien 21h30 | Jeux | ✅ OK | ✅ Phase 1 — scraping CSV FDJ réel |
| `scraper_euromillions` | Mardi/Vendredi 21h30 | Jeux | ✅ OK | ✅ Phase 1 — scraping CSV FDJ réel |
| `garmin_sync_matinal` | Quotidien 6h | Famille | ✅ OK | Aucune |
| `sync_google_calendar` | Quotidien 23h | Famille | ✅ OK | Aucune |
| `enrichissement_catalogues` | 1er/mois 3h | Core | ✅ OK | Aucune |
| `automations_runner` | Toutes les 5 min | Core | ✅ OK | Aucune |
| `digest_quotidien` | Quotidien 7h30 | Notifications | ✅ OK | Aucune |
| `digest_hebdo` | Dimanche 18h | Notifications | ✅ OK | Aucune |
| `purge_cache` | Quotidien 3h | Core | ✅ OK | Aucune |
| `nettoyage_logs` | Mensuel | Admin | ✅ OK | Aucune |
| `backup_auto` | Quotidien 2h | Core | ✅ OK | Aucune |
| ... | ... | ... | ... | ... |

### 11.2 Jobs à ajouter

| # | Job | Horaire proposé | Module | Description | Priorité | Phase |
|---|-----|-----------------|--------|-------------|----------|-------|
| 1 | `rappel_documents_expirants` | Quotidien 8h | Famille | Alerter si document expire dans 30/15/7 jours | P1 | 8 |
| 2 | `rapport_mensuel_auto` | 1er/mois 8h | Dashboard | Générer et envoyer le rapport mensuel automatiquement | P2 | 8 |
| 3 | `sync_contrats_alertes` | Hebdo lundi 9h | Maison | Contrats expirant sous 30 jours → alerte | P2 | 8 |
| 4 | `optimisation_routines` | Mensuel | Famille | Analyser efficacité routines → suggestions IA | P3 | 10 |
| 5 | `bilan_energetique` | Mensuel | Maison | Comparer conso énergie mois précédent → alerte si anomalie | P2 | 8 |
| 6 | `rappel_vaccins` | Lundi 9h | Famille | Vérifier calendrier vaccinal Jules → rappel si retard | P2 | 8 |
| 7 | `suggestions_saison` | 1er/mois | Cuisine | Mettre en avant les produits de saison du mois | P3 | 10 |
| 8 | `purge_historique_jeux` | Mensuel | Jeux | Archiver données de paris > 12 mois | P3 | 10 |
| 9 | `check_garanties_expirant` | Hebdo | Maison | Garanties qui expirent sous 60 jours → alerte | P2 | 8 |
| 10 | `veille_emploi` | Quotidien 7h | Habitat | Scraper multi-sites (Indeed, LinkedIn, WTTJ, France Travail, Apec) pour offres RH hybride/télétravail à ~30 min → alerte si nouvelle offre | P2 | 10 |

---

## 12. Notifications — WhatsApp, Email, Push — Plan de consolidation

### 12.1 État actuel des canaux

| Canal | Backend | Frontend | Configuration | État |
|-------|---------|----------|---------------|------|
| **Web Push** (ntfy.sh) | ✅ | ✅ | `NTFY_TOPIC` | ✅ Fonctionnel |
| **Push navigateur** | ✅ | ✅ | VAPID keys | ✅ Fonctionnel |
| **Email** (Resend) | ✅ | ✅ Config | `RESEND_API_KEY` | ⚠️ Fonctionnel mais sans templates HTML |
| **WhatsApp** (Meta Business) | ✅ 10 commandes | — | `META_WHATSAPP_TOKEN` | ⚠️ Fonctionnel avec bugs mineurs |

### 12.2 Commandes WhatsApp implémentées

| Commande | Action |
|----------|--------|
| `menu` | Afficher le menu principal |
| `courses` | Voir la liste de courses active |
| `frigo` | Voir le contenu du frigo/inventaire |
| `jules` | Infos développement Jules |
| `ajouter [item]` | Ajouter un article aux courses |
| `budget` | Résumé budget familial |
| `anniversaires` | Anniversaires à venir |
| `recette [terme]` | Chercher une recette |
| `tâches` | Tâches ménage du jour |
| `admin` | Commandes admin |

### 12.3 Plan d'améliorations notifications

| # | Amélioration | Canal | Priorité | Phase |
|---|-------------|-------|----------|-------|
| 1 | **Cascade failover** : Push → Email → WhatsApp si échec | Tous | P1 | 5 |
| 2 | **Templates email HTML** avec Jinja2 | Email | P1 | 5 |
| 3 | **Commandes WhatsApp supplémentaires** : `planning`, `météo`, `rappels`, `jardin` | WhatsApp | P2 | 5 |
| 4 | **Boutons interactifs WhatsApp** : valider/modifier planning, cocher article courses | WhatsApp | P2 | 5 |
| 5 | **Digest WhatsApp matinal** : résumé de la journée (tâches, repas, météo, rappels) | WhatsApp | P1 | 5 |
| 6 | **Rate limiting WhatsApp** | WhatsApp | P1 | 5 |
| 7 | **Validation numéro téléphone** | WhatsApp | P1 | 5 |
| 8 | **Réponses vocales WhatsApp** → transcription IA | WhatsApp | P3 | 10 |
| 9 | **Email résumé hebdo** automatique | Email | P2 | 5 |
| 10 | **Notifications contextuelles** (basées sur localisation, heure, habitudes) | Push | P3 | 10 |

---

## 13. Mode Admin manuel (test) — Plan d'implémentation

### 13.1 Ce qui existe

Le panneau admin est **déjà bien avancé** avec :

- **13 endpoints API admin** protégés par `require_role("admin")`
- **6 pages frontend admin** (dashboard, utilisateurs, jobs, notifications, services, sql-views)
- **38+ jobs CRON** déclenchables manuellement via `POST /api/v1/admin/jobs/{id}/run`
- **Test notifications** via `POST /api/v1/admin/notifications/test`
- **Cache management** : stats, purge par pattern, clear total
- **Feature flags** : toggles runtime stockés en DB
- **Audit logs** : historique complet + export CSV

### 13.2 Plan d'améliorations admin

| # | Feature | Description | Priorité | Phase |
|---|---------|-------------|----------|-------|
| 1 | **Toggle "Mode Test" global** | Un switch admin-only qui active les logs verbose, désactive le rate limiting, affiche les IDs internes — invisible pour l'utilisateur normal | P0 | 1 |
| 2 | **Console d'exécution manuelle** | UI admin pour exécuter n'importe quel job CRON avec paramètres custom (date simulée, user cible, etc.) | P1 | 7 |
| 3 | **Simulateur de flux** | Pouvoir simuler un flux complet (ex : « Simuler une péremption dans 24h ») et voir le résultat sans toucher aux données réelles | P2 | 7 |
| 4 | **Dashboard temps réel admin** | Métriques live : requêtes/sec, latence API, cache hit rate, erreurs, files d'attente | P2 | 7 |
| 5 | **Persistance historique jobs en DB** | Les logs de jobs sont en mémoire et perdus au restart — les persister | P1 | 7 |
| 6 | **Bouton "Déclencher all notifications"** | Tester tous les canaux d'un coup (push + email + WhatsApp) avec un payload de test | P1 | 7 |
| 7 | **Dry-run mode pour CRON** | Exécuter un job en mode preview (voir ce qu'il ferait sans commit) | P2 | 7 |
| 8 | **Reset module** | Bouton admin pour remettre à zéro un module entier (données de test) | P3 | 10 |
| 9 | **Import/export config** | Sauvegarder et restaurer la configuration complète (feature flags, preferences, automations) | P2 | 7 |
| 10 | **Logs structurés temps réel** | WebSocket admin qui stream les logs du serveur en temps réel | P3 | 10 |

### 13.3 Visibilité admin vs utilisateur

**Principe** : le mode admin doit être **invisible** pour les utilisateurs normaux.

```
┌─────────────────────────────────────────────┐
│  Utilisateur normal                         │
│  ✅ Voit : sidebar, pages, fonctionnalités  │
│  ❌ Ne voit pas : admin, debug, logs, jobs  │
│  ❌ Pas de badge/icône admin                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Admin (toi en test)                        │
│  ✅ Tout + panneau admin dans sidebar       │
│  ✅ Toggle mode test (logs verbose)         │
│  ✅ Exécuter jobs manuellement              │
│  ✅ Voir métriques temps réel               │
│  ✅ Simuler des scénarios                   │
│  ✅ Feature flags on/off                    │
└─────────────────────────────────────────────┘
```

**Implémentation existante** : Le layout admin (`frontend/src/app/(app)/admin/layout.tsx`) vérifie déjà le rôle et redirige les non-admins. Le lien admin dans la sidebar n'apparaît que pour le rôle admin.

---

## 14. UX — Simplification du flux utilisateur

### 14.1 Navigation actuelle

La sidebar actuelle contient :
- 7 modules principaux + sous-menus dépliants
- Le module **Famille** a **19 sous-pages** → trop pour un menu

### 14.2 Plan d'améliorations UX

| # | Zone | Problème | Solution | Priorité | Phase |
|---|------|----------|----------|----------|-------|
| 1 | **Sidebar Famille** | 19 sous-menus = surcharge cognitive | Regrouper en 4 catégories : **Enfant** (Jules, santé, gamification), **Vie quotidienne** (activités, routines, weekend), **Finances** (budget, achats), **Admin famille** (contacts, documents, voyages) | P1 | 4 |
| 2 | **Sidebar Maison** | 11 sous-menus | Regrouper en 3 : **Entretien** (ménage, jardin, travaux, équipements), **Finances** (charges, contrats, artisans, diagnostics), **Inventaire** (provisions, meubles, documents) | P2 | 4 |
| 3 | **Actions rapides dashboard** | Présentes mais pas assez mises en avant | Ajouter un FAB (Floating Action Button) mobile pour les 3 actions les plus fréquentes : ajouter recette, ajouter article courses, noter dépense | P1 | 4 |
| 4 | **Ma Semaine** | Existe en doublon (sidebar + cuisine) | Unifier en un seul point d'accès : vue unifiée semaine = repas + tâches maison + activités Jules + anniversaires | P1 | 4 |
| 5 | **Flux ajout recette** | Nombre de champs du formulaire | Mode simplifié (nom + photo) et mode avancé (tous les champs) | P2 | 4 |
| 6 | **Flux courses** | Créer une liste → ajouter articles → cocher | « Ajouter article » visible en permanence en bas de la liste active (pas de navigation) | P1 | 4 |
| 7 | **Onboarding** | 5 étapes — ok mais pas de personnalisation | Ajouter une étape « Quels modules utilisez-vous ? » → cacher les modules inutiles | P2 | 4 |
| 8 | **Recherche globale** | Existe mais Ctrl+K | Ajouter un champ de recherche visible en permanence sur mobile (icône en header) | P2 | 4 |
| 9 | **Nombre de clics** | 2 clics max pour les actions fréquentes | Raccourcis swipe sur mobile (swipe gauche = supprimer, swipe droite = cocher/valider) — composant `swipeable-item.tsx` existe déjà | P2 | 4 |
| 10 | **Home widgets** | 11 widgets — potentiellement surchargé | Permettre à l'utilisateur de choisir ses 4-6 widgets préférés (déjà configurable) + presets par profil (« Cuisine », « Famille complète ») | P3 | 10 |

### 14.3 Flux utilisateur idéal (1-2 clics)

```
📱 Ouvrir l'app
    │
    ├→ Dashboard : vue d'ensemble (météo, rappels, tâches du jour, repas)
    │
    ├→ « Ma Semaine » : planning unifié (repas + tâches + activités)
    │   └→ Cliquer sur un jour → voir/modifier le détail
    │
    ├→ « + » (FAB) : action rapide
    │   ├→ 🍳 Ajouter recette (mode simplifié)
    │   ├→ 🛒 Ajouter aux courses
    │   ├→ 💰 Noter une dépense
    │   └→ 📸 Scanner (code-barre ou fridge photo)
    │
    └→ Sidebar : accès à tous les modules (collapsible)
```

---

## 15. Gamification — Plan d'implémentation

> **Périmètre volontairement limité** : La gamification sert uniquement à inciter à **faire du sport** et **bien manger**. Aucun badge/point pour d'autres modules (maison, recettes cuisinées, routines, budget, jardin, etc.).

### 15.1 État actuel

| Élément | État | Notes |
|---------|------|-------|
| **Modèle PointsUtilisateur** | ✅ | Points sport + alimentation par semaine |
| **Modèle BadgeUtilisateur** | ✅ | Type, label, date acquisition, méta |
| **Calcul points hebdo** | ✅ | CRON dimanche 20h, agrège Garmin (sport) + nutrition |
| **Page gamification frontend** | ✅ | Cartes métriques + barres de progression |
| **API points-famille** | ✅ | GET endpoint fonctionnel |

### 15.2 Plan d'implémentation gamification (sport + nutrition uniquement)

| # | Feature | Description | Priorité | Phase |
|---|---------|-------------|----------|-------|
| 1 | **Triggers badges sport** | Conditions : X pas/jour pendant 7j consécutifs, N sessions sport/semaine, objectif calories brûlées atteint — pas implémentés dans le code | P2 | 9 |
| 2 | **Triggers badges nutrition** | Conditions : planning repas équilibré N jours de suite, score nutritionnel moyen > seuil, anti-gaspi zéro déchet sur 1 semaine | P2 | 9 |
| 3 | **Détail badges** | Liste des badges sport + nutrition possibles avec progression (ex : 15/30 jours de marche) | P2 | 9 |
| 4 | **Notifications badges** | Alerte push quand un badge sport ou nutrition est débloqué | P2 | 9 |
| 5 | **Historique points** | Graphique évolution des points sport + nutrition semaine par semaine | P3 | 9 |

---

## 16. Axes d'innovation — Plan d'exploration

### 16.1 Innovations techniques

| # | Innovation | Description | Impact | Effort | Phase |
|---|-----------|-------------|--------|--------|-------|
| 1 | **Assistant vocal intégré** | Le composant `fab-assistant-vocal.tsx` existe — connecter au chat IA avec contexte multi-module | ★★★ | Moyen | 10 |
| 2 | **Mode hors-ligne complet** | Service worker + IndexedDB queue (infra PWA existe, logique partielle) → sync au retour réseau | ★★★ | Élevé | 10 |
| 3 | **Widgets home personnalisables** | Drag & drop widgets (composant `grille-widgets.tsx` existe) — ajouter des widgets par module | ★★ | Moyen | 10 |
| 4 | **API GraphQL** | Option GraphQL pour le frontend (réduire les appels réseau sur le dashboard qui fait 11 requêtes) | ★★ | Élevé | 10 |
| 5 | **WebSocket temps réel étendu** | Étendre le WebSocket courses à d'autres modules (planning partagé, tâches maison) | ★★ | Moyen | 10 |

### 16.2 Innovations fonctionnelles

| # | Innovation | Description | Impact | Effort | Phase |
|---|-----------|-------------|--------|--------|-------|
| 6 | **Briefing matinal IA** | Chaque matin à 7h → digest personnalisé : météo + repas du jour + tâches + rappels + anniversaires + résumé budget. **Configurable** par utilisateur (activable/désactivable) car ne plaira pas forcément à tout le monde (ex : Mathieu) | ★★★ | Faible | 2 |
| 7 | **Analyse photos multi-usage** | Un seul bouton photo → IA détecte le contexte : frigo → inventaire, reçu → dépense, plante → diagnostic, document → classement | ★★★ | Moyen | 6 |
| 8 | **Tableau de bord familial partagé** | Un mode "famille" où chaque membre voit sa vue mais les données sont partagées (courses, planning, tâches) | ★★★ | Élevé | 10 |
| 9 | **Score bien-être familial** | Combiner Garmin (sport), nutrition (planning), budget (stress financier), routines (régularité) → score global 0-100 | ★★ | Moyen | 10 |
| 10 | **Suggestions proactives** | Au lieu d'attendre que l'utilisateur demande → l'app propose : "Vous n'avez rien prévu pour mercredi, voici 3 recettes rapides avec ce qui vous reste" | ★★★ | Moyen | 6 |
| 11 | **Intégration supermarché** | Connexion API drives (Carrefour, Leclerc, Auchan) → envoyer la liste de courses directement en commande | ★★ | Élevé | 10 |
| 12 | **Compagnon vocal WhatsApp** | Au lieu de taper des commandes → audio WhatsApp transcrit par IA → action automatique | ★★ | Moyen | 10 |
| 13 | **Mini-jeux éducatifs Jules** | Relier les jalons développementaux à des activités interactives adaptées à l'âge + suggestions d'achats de jeux adaptés au stade de développement | ★★ | Élevé | 10 |
| 14 | **Mode invité** | Un lien partageable pour que la nounou/grands-parents voient certaines infos (repas Jules, routines, contacts urgence) sans compte | ★★ | Moyen | 10 |
| 15 | **Bilan annuel automatique** | En décembre → rapport IA complet : recettes cuisinées, budget dépensé, projets maison terminés, croissance Jules, points gaming | ★★ | Faible | 10 |
| 16 | **Rappels intelligents contextuels** | Le service `rappels_intelligents.py` existe — l'enrichir : rappeler les courses si vous passez près d'un magasin (géoloc), rappeler le ménage si Garmin montre que vous êtes à la maison | ★★ | Élevé | 10 |
| 17 | **Gestion multi-enfants** | L'app est centrée sur Jules — prévoir l'architecture pour un éventuel frère ou sœur (périmètre famille uniquement, pas multi-famille) | ★★ | Moyen | 10 |
| 18 | **Veille emploi (Habitat)** | Scanner quotidien multi-sites (Indeed, LinkedIn, Welcome to the Jungle, France Travail, Apec, etc.) pour détecter les offres RH (ou autre domaine paramétrable) avec télétravail/hybride, CDI/consultant, possibilité 4j/semaine, dans un rayon de ~30 min en voiture (paramétrable). Alerte push/WhatsApp/email si nouvelle offre. Impact direct sur la décision habitat (partir/rester). Pour Mathieu principalement. **Tous les critères paramétrables** : domaine, mots-clés, type contrat, mode de travail, rayon, fréquence. | ★★★ | Moyen | 10 |

---

## 17. Plan d'action global priorisé par phase

### Phase 1 — Corrections critiques (P0) ✅ TERMINÉE

> **Objectif** : Corriger les bugs bloquants, connecter les circuits interrompus, consolider SQL
> **Statut** : ✅ Complétée — toutes les tâches implémentées

| # | Action | Fichier(s) | Type | Statut |
|---|--------|-----------|------|--------|
| 1.1 | Câbler les notifications push/WhatsApp sur les alertes péremption | `cron_cuisine.py` | Bug fix | ✅ |
| 1.2 | Câbler le rappel planning manquant | `cron_cuisine.py` | Bug fix | ✅ |
| 1.3 | Connecter stock bas → ajout auto courses | `cron_cuisine.py` | Bug fix | ✅ |
| 1.4 | Implémenter source de données loterie réelle (API ou scraping FDJ) | `cron_jobs_loteries.py` | Feature | ✅ |
| 1.5 | Absorber migrations V003→V007 dans `INIT_COMPLET.sql` | `sql/` | Consolidation | ✅ |
| 1.6 | Créer le toggle "Mode Test" admin-only | `admin.py` + middleware | Feature | ✅ |

### Phase 2 — Connexions inter-modules (P1)

> **Objectif** : Tous les modules communiquent de façon fluide

| # | Action | Flux | Statut | Détails implémentés |
|---|--------|------|--------|---------------------|
| 2.1 | Inventaire péremption → Suggestions recettes | Produits expirants → proposition auto | ✅ | Service `inter_module_peremption_recettes.py` (recherche recettes DB + fallback IA) |
| 2.2 | Courses total → Budget catégorie alimentation | Synchronisation achats | ✅ | Service `inter_module_courses_budget.py` (sync total courses vers `BudgetFamille`) |
| 2.3 | Documents expiration → Notifications multi-canal | Alerte 30/15/7 jours | ✅ | Service `inter_module_documents_notifications.py` (seuils J-30/J-15/J-7/J-1 + dispatcher) |
| 2.4 | Chat IA → Contexte multi-module | Le chat connaît frigo + planning + budget + météo | ✅ | Service `inter_module_chat_contexte.py` (agrégation inter-modules + injection contexte IA) |
| 2.5 | Briefing matinal IA | Digest quotidien personnalisé 7h — configurable on/off par utilisateur | ✅ | Service `briefing_matinal.py` (collecte sections + résumé IA + envoi notification) |
| 2.6 | Batch cooking → Inventaire | Session terminée → déduire ingrédients consommés | ✅ | Service `inter_module_batch_inventaire.py` + hook auto dans `terminer_session()` |
| 2.7 | Anniversaires → Budget | Provisioner budget cadeaux automatiquement | ✅ | Service `inter_module_anniversaires_budget.py` (provisions auto anniversaires proches) |
| 2.8 | Voyages → Budget | Intégrer dépenses voyage dans budget | ✅ | Service `inter_module_voyages_budget.py` (sync budget prévu/réel vers budget famille) |

### Phase 3 — Tests & documentation (P1-P2)

> **Objectif** : Couverture tests > 80%, documentation complète
> **Statut (2026-03-30)** : ✅ Implémenté

| # | Action | Statut |
|---|--------|--------|
| 3.1 | Tests services habitat (plans IA, déco IA) | ✅ Fait |
| 3.2 | Tests services dashboard (agrégation, anomalies) | ✅ Fait |
| 3.3 | Tests intégrations (météo, Google Calendar, Garmin) | ✅ Fait |
| 3.4 | Tests composants React (formulaire-recette, plan-3d, heatmaps) | ✅ Fait |
| 3.5 | Tests hooks React (utiliser-websocket, utiliser-crud) | ✅ Fait |
| 3.6 | Créer `FRONTEND_ARCHITECTURE.md` | ✅ Fait |
| 3.7 | Créer `ADMIN_GUIDE.md` | ✅ Fait |
| 3.8 | Créer `WHATSAPP_SETUP.md` | ✅ Fait |
| 3.9 | Mettre à jour `ERD_SCHEMA.md` (ajout habitat, garmin, gamification) | ✅ Fait |
| 3.10 | Mettre à jour `SERVICES_REFERENCE.md` (services maison CRUD) | ✅ Fait |
| 3.11 | Mettre à jour `INTER_MODULES.md` (nouveaux flux) | ✅ Fait |
| 3.12 | Mettre à jour `AUTOMATIONS.md` (38 jobs CRON + statuts) | ✅ Fait |

### Phase 4 — UX simplification (P1-P2) ✅ COMPLÉTÉE

> **Objectif** : Flux utilisateur en 1-2 clics, interface épurée
> **Statut** : COMPLÉTÉE — Phase 4 du 30 mars 2026

| # | Action | Statut |
|---|--------|--------|
| 4.1 | Regrouper sous-menus Famille (19 → 4 catégories) | ✅ Fait — 4 catégories ajoutées (Enfant, Budget & Achats, Événements, Organisation) |
| 4.2 | FAB mobile (+) pour actions rapides (recette, courses, dépense, scan) | ✅ Fait — FabActionsRapides.tsx crée avec menu circulaire |
| 4.3 | Vue "Ma Semaine" unifiée (repas + tâches + activités + anniversaires) | ✅ Existant — Page /ma-semaine complète avec timeline unifiée |
| 4.4 | Mode simplifié formulaire recette (nom + photo) | ✅ Fait — FormulaireRecette avec modeSimple + page /cuisine/recettes/rapide |
| 4.5 | Champ "ajouter article" toujours visible sur la liste de courses active | ✅ Fait — Input sticky au-dessus des articles sur /cuisine/courses |
| 4.6 | Regrouper sous-menus Maison (11 → 3 catégories) | ✅ Fait — 3 catégories ajoutées (Habitat, Travaux & Équipements, Admin & Finances) |
| 4.7 | Onboarding personnalisé (choix modules) | ✅ Existant — TourOnboarding avec 6 étapes déjà complètes |
| 4.8 | Recherche globale visible mobile (icône header) | ✅ Existant — Icône 🔍 dans EnTete.tsx sur mobile |
| 4.9 | Raccourcis swipe mobile (supprimer / cocher) | ✅ Existant — SwipeableItem.tsx disponible pour intégration |

**Détails implémentation** :**Détails implémentation** :

- **4.1 & 4.6** : Nouvelles interfaces `CategorieNav` dans barre-laterale.tsx avec rendu groupé par catégories pour Famille et Maison
- **4.2** : Nouveau composant `FabActionsRapides.tsx` avec menu circulaire (70px rayon) — 4 actions : recette, courses, dépense, scan
- **4.4** : Propriété `modeSimple` sur FormulaireRecette + page dédiée `/cuisine/recettes/rapide`
- **4.5** : Input collante au-dessus de la grille articles via `sticky top-0 z-10` sur le formulaire
- **4.7, 4.8, 4.9** : Composants déjà existants et fonctionnels

### Phase 5 — Notifications avancées (P1-P2)

> **Objectif** : Système de notification fiable et multi-canal
> **Statut (2026-03-30)** : ✅ Implémenté

| # | Action | Statut | Détails implémentés |
|---|--------|--------|---------------------|
| 5.1 | Cascade failover (Push → Email → WhatsApp) | ✅ | Dispatcher enrichi avec chaîne de fallback multi-canal et journalisation des bascules réussies/échouées |
| 5.2 | Templates email HTML (Jinja2) | ✅ | `ServiceEmail` refactoré avec Jinja2 + dossier `templates/` (`reset_password`, `verification_email`, `resume_hebdo`, `rapport_mensuel`, `alerte_critique`, `invitation_famille`, `digest`) |
| 5.3 | Rate limiting WhatsApp | ✅ | Limites in-memory ajoutées côté intégration WhatsApp (`10/h` par destinataire, `100/jour` global) |
| 5.4 | Validation numéro téléphone | ✅ | Validation E.164 + normalisation des numéros FR avant envoi WhatsApp |
| 5.5 | Commandes WhatsApp supplémentaires (planning, météo, jardin) | ✅ | Webhook enrichi avec commandes `météo`, `jardin`, `énergie`, `entretien` + handlers dédiés |
| 5.6 | Digest WhatsApp matinal | ✅ | Nouveau digest matinal WhatsApp avec repas du jour, péremptions proches et tâches du jour |
| 5.7 | Fix `_envoyer_aide_admin()` manquant | ✅ | Handler admin présent et complété avec les nouvelles commandes Phase 5 |
| 5.8 | Boutons interactifs WhatsApp | ✅ | Support boutons + listes interactives, nouveaux handlers d'actions (`digest`, `courses`, `entretien`) et réponses `button_reply` / `list_reply` |
| 5.9 | Email résumé hebdo automatique | ✅ | Job cron hebdo corrigé pour toujours tenter le canal email via résolution automatique de l'adresse utilisateur dans le dispatcher |

### Phase 6 — IA avancée (P1-P2)

> **Objectif** : IA proactive et contextuelle
> **Statut (2026-03-30)** : ✅ Implémenté

| # | Action | Statut | Détails implémentés |
|---|--------|--------|---------------------|
| 6.1 | Inventaire → suggestions achats IA (historique consommation) | ✅ | Endpoint `GET /api/v1/ia-avancee/suggestions-achats` + analyse inventaire/stock bas |
| 6.2 | Planning adaptatif (météo + énergie Garmin + budget) | ✅ | Endpoint `POST /api/v1/ia-avancee/planning-adaptatif` + contexte planning/budget |
| 6.3 | Diagnostic plantes photo (Pixtral — infra existe) | ✅ | Endpoint `POST /api/v1/ia-avancee/diagnostic-plante` via service multimodal Pixtral |
| 6.4 | Budget → prévision dépenses fin de mois | ✅ | Endpoint `GET /api/v1/ia-avancee/prevision-depenses` + agrégation budget mensuelle |
| 6.5 | Idées cadeaux IA (anniversaires) | ✅ | Endpoint `POST /api/v1/ia-avancee/idees-cadeaux` + scoring contexte occasion/budget |
| 6.6 | Analyse photo multi-usage (un bouton, IA détecte le contexte) | ✅ | Endpoint `POST /api/v1/ia-avancee/analyse-photo` avec autodétection recette/plante/maison/document/plat |
| 6.7 | Optimisation routines IA | ✅ | Endpoint `GET /api/v1/ia-avancee/optimisation-routines` + analyse routines existantes |
| 6.8 | Analyse documents photo (OCR + classement auto) | ✅ | Endpoint `POST /api/v1/ia-avancee/analyse-document` + OCR/classification/actions suggérées |
| 6.9 | Estimation travaux IA améliorée (photo avant/après) | ✅ | Endpoint `POST /api/v1/ia-avancee/estimation-travaux` + budget/durée/DIY/artisans |
| 6.10 | Planning voyage IA (destination + dates + budget → itinéraire) | ✅ | Endpoint `POST /api/v1/ia-avancee/planning-voyage` + itinéraire jour par jour |
| 6.11 | Recommandations économies énergie | ✅ | Endpoint `GET /api/v1/ia-avancee/recommandations-energie` + lecture relevés compteur |
| 6.12 | Prédiction pannes entretien | ✅ | Endpoint `GET /api/v1/ia-avancee/prediction-pannes` + score santé équipements |
| 6.13 | Suggestions proactives (l'app propose sans qu'on demande) | ✅ | Endpoint `GET /api/v1/ia-avancee/suggestions-proactives` + agrégation multi-modules |
| 6.14 | Météo → Planning repas / Jardin / Activités famille | ✅ | Endpoint `POST /api/v1/ia-avancee/adaptations-meteo` + adaptations repas/jardin/activités |

**Détails implémentation** :

- Nouveau package `src/services/ia_avancee/` avec `IAAvanceeService` centralisant les 14 fonctionnalités Phase 6
- Nouveaux schémas typés dans `src/services/ia_avancee/types.py` et `src/api/schemas/ia_avancee.py`
- Nouveau routeur FastAPI `src/api/routes/ia_avancee.py` avec 14 endpoints protégés par auth + rate limiting IA
- Réutilisation de l'infrastructure existante `BaseAIService` (cache sémantique, circuit breaker, parsing JSON, rate limiting)
- Réutilisation du service multimodal Pixtral pour les analyses photo/plante/document/travaux
- Intégration de contexte DB réel pour inventaire, budget, planning, routines, énergie et suggestions proactives

### Phase 7 — Mode admin avancé (P1-P2)

> **Objectif** : Admin peut tout tester et monitorer

| # | Action |
|---|--------|
| 7.1 | Persistance historique jobs en DB |
| 7.2 | Console d'exécution manuelle avec paramètres custom |
| 7.3 | Bouton "Tester tous les canaux notifications" |
| 7.4 | Dry-run mode CRON (preview sans commit) |
| 7.5 | Import/export configuration complète |
| 7.6 | Simulateur de flux |
| 7.7 | Dashboard temps réel admin (requêtes/sec, latence, cache) |

### Phase 8 — Jobs CRON additionnels (P2)

> **Objectif** : Automatisations complètes

| # | Action |
|---|--------|
| 8.1 | `rappel_documents_expirants` (quotidien 8h) |
| 8.2 | `rapport_mensuel_auto` (1er/mois 8h) |
| 8.3 | `sync_contrats_alertes` (hebdo lundi 9h) |
| 8.4 | `check_garanties_expirant` (hebdo) |
| 8.5 | `bilan_energetique` (mensuel) |
| 8.6 | `rappel_vaccins` (lundi 9h) |
| 8.7 | Connexions inter-modules restantes : Entretien→Budget, Voyages→Calendrier, Charges→Dashboard |

### Phase 9 — Gamification sport + nutrition (P2-P3)

> **Objectif** : Inciter à faire du sport et bien manger via badges et points (périmètre limité volontairement)

| # | Action |
|---|--------|
| 9.1 | Implémenter triggers badges sport (pas/jour, sessions/semaine, calories brûlées) |
| 9.2 | Implémenter triggers badges nutrition (planning équilibré, score nutritionnel, anti-gaspi) |
| 9.3 | Page détail badges sport + nutrition (liste + progression) |
| 9.4 | Notifications push badges débloqués |
| 9.5 | Historique points sport + nutrition (graphique hebdomadaire) |
| 9.6 | Créer `GAMIFICATION.md` |

### Phase 10 — Innovations (P2-P3)

> **Objectif** : Différenciation et valeur ajoutée

| # | Action |
|---|--------|
| 10.1 | Assistant vocal connecté (fab-assistant-vocal.tsx → chat IA) |
| 10.2 | Suggestions proactives (app qui propose sans qu'on demande) |
| 10.3 | Mode invité (lien partageable nounou/grands-parents) |
| 10.4 | Bilan annuel automatique IA |
| 10.5 | Score bien-être familial composite |
| 10.6 | WebSocket étendu (planning partagé, tâches maison temps réel) |
| 10.7 | Gestion multi-enfants (futur frère/sœur Jules, pas multi-famille) |
| 10.8 | Veille emploi Habitat — scan quotidien multi-sites, critères configurables (domaine, contrat, télétravail, rayon), alertes |
| 10.9 | Mode hors-ligne complet (service worker + IndexedDB queue + sync) |
| 10.10 | API GraphQL (réduction appels réseau dashboard) |
| 10.11 | Compagnon vocal WhatsApp (audio → transcription IA → action) |
| 10.12 | Intégration supermarché (API drives → commande directe) |
| 10.13 | Rappels intelligents contextuels (géoloc, habitudes Garmin) |
| 10.14 | Mini-jeux éducatifs Jules |
| 10.15 | Tableau de bord familial partagé (multi-vues, données partagées) |
| 10.16 | Widgets home personnalisables (drag & drop) + presets profil |
| 10.17 | Enrichissement contacts IA (catégorisation, rappels relationnels) |
| 10.18 | Analyse tendances Loto/Euromillions avancée |
| 10.19 | Optimisation parcours magasin IA |
| 10.20 | Jobs CRON restants (optimisation_routines, suggestions_saison, purge_historique_jeux, veille_emploi) |
| 10.21 | Réponses vocales WhatsApp → transcription IA |
| 10.22 | Notifications contextuelles (localisation, heure, habitudes) |
| 10.23 | Créer `HABITAT_MODULE.md` + `CHANGELOG.md` |
| 10.24 | Tests mutation (mutmut) CI + tests performance avancés |
| 10.25 | Reset module admin + logs structurés temps réel WebSocket |

---

## Annexe A — Fichiers à surveiller

| Fichier | Raison | Action |
|---------|--------|--------|
| `src/api/routes/jeux.py` | 2400+ lignes | Envisager split en 3 fichiers (paris, loto, euromillions) |
| `src/api/routes/maison_finances.py` | 900+ lignes | Déjà splitté mais encore gros |
| `sql/INIT_COMPLET.sql` | 3366 lignes | Absorber les migrations V003-V007 |
| `alembic/` | Archivé | Supprimer le dossier |
| `tests/conftest.py` | 710+ lignes | Envisager split par module |

---

## Annexe B — Stack technique complète

| Couche | Technologies |
|--------|-------------|
| **Backend** | Python 3.13+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn |
| **Frontend** | Next.js 16.2.1, React 19, TypeScript 5, Tailwind CSS v4 |
| **State** | Zustand 5, TanStack Query v5 |
| **Validation** | Pydantic (backend), Zod 4.3.6 (frontend) |
| **IA** | Mistral AI (small-latest), Pixtral (images) |
| **DB** | Supabase PostgreSQL, SQLite (tests) |
| **Cache** | Multi-niveaux (L1 mémoire, L3 fichier), Redis (optionnel) |
| **Auth** | JWT HS256, Supabase GoTrue, 2FA TOTP |
| **Notifications** | ntfy.sh, Web Push (VAPID), Resend (email), Meta WhatsApp Business |
| **Monitoring** | Sentry, Prometheus, logs structurés |
| **Tests** | Pytest, Playwright, Vitest, Schemathesis, k6 |
| **CI/CD** | Vercel (frontend), Railway (backend), Docker |
| **Intégrations** | Garmin, Google Calendar, OpenWeatherMap, OpenFoodFacts |

---

## Annexe C — Variables d'environnement requises

| Variable | Module | Obligatoire |
|----------|--------|-------------|
| `DATABASE_URL` | Core | ✅ |
| `API_SECRET_KEY` | Auth | ✅ (auto-générée sinon) |
| `MISTRAL_API_KEY` | IA | ✅ |
| `SUPABASE_URL` + `SUPABASE_KEY` | Auth/DB | ✅ |
| `RESEND_API_KEY` | Email | ⚠️ Optionnel |
| `META_WHATSAPP_TOKEN` | WhatsApp | ⚠️ Optionnel |
| `NTFY_TOPIC` | Push | ⚠️ Optionnel |
| `OPENWEATHER_API_KEY` | Météo | ⚠️ Optionnel |
| `FOOTBALL_DATA_API_KEY` | Jeux/Paris | ⚠️ Optionnel |
| `GOOGLE_CLIENT_ID` + `SECRET` | Calendar | ⚠️ Optionnel |
| `SENTRY_DSN` | Monitoring | ⚠️ Optionnel |
| `REDIS_URL` | Cache distribué | ⚠️ Optionnel |

---

> **Résumé** : L'application est mature et bien structurée (90%+ de complétude). Les corrections critiques se limitent à 5 bugs (notifications non câblées + scraping loterie simulé). Les plus grandes opportunités résident dans les connexions inter-modules, l'IA proactive, et la simplification UX. Le mode admin est déjà fonctionnel et mérite quelques améliorations pour le rendre parfait pour les tests manuels. Le plan couvre 10 phases structurées, de la correction de bugs (Phase 1) aux innovations long terme (Phase 10).
