# Analyse Complète — Assistant MaTanne

> **Date** : 30 mars 2026
> **Périmètre** : Backend (FastAPI/Python) + Frontend (Next.js 16) + SQL + Tests + Docs
> **Objectif** : Audit 360° — bugs, gaps, features manquantes, opportunités IA, jobs automatiques, notifications, mode admin, UX, tests, docs, organisation

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Inventaire complet](#2-inventaire-complet)
3. [Bugs & implémentations incomplètes](#3-bugs--implémentations-incomplètes)
4. [Gaps & features manquantes](#4-gaps--features-manquantes)
5. [SQL — État et consolidation](#5-sql--état-et-consolidation)
6. [Tests — Couverture et manques](#6-tests--couverture-et-manques)
7. [Documentation — Audit qualité](#7-documentation--audit-qualité)
8. [Interactions intra-modules](#8-interactions-intra-modules)
9. [Interactions inter-modules](#9-interactions-inter-modules)
10. [Opportunités IA à ajouter](#10-opportunités-ia-à-ajouter)
11. [Jobs automatiques (CRON)](#11-jobs-automatiques-cron)
12. [Notifications — WhatsApp, Email, Push](#12-notifications--whatsapp-email-push)
13. [Mode Admin manuel (test)](#13-mode-admin-manuel-test)
14. [UX — Simplification du flux utilisateur](#14-ux--simplification-du-flux-utilisateur)
15. [Gamification](#15-gamification)
16. [Axes d'innovation](#16-axes-dinnovation)
17. [Plan d'action priorisé](#17-plan-daction-priorisé)

---

## 1. Vue d'ensemble du projet

### Chiffres clés

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

### Modules applicatifs

| Module | Backend | Frontend | IA | Tests | Completude |
|--------|---------|----------|----|-------|------------|
| 🍽️ Cuisine (recettes, planning, courses, inventaire, batch, anti-gaspi) | ✅ | ✅ | ✅ | ✅ | 95% |
| 👶 Famille (Jules, activités, routines, budget, voyages, contacts) | ✅ | ✅ | ✅ | ✅ | 90% |
| 🏡 Maison (projets, jardin, entretien, artisans, contrats, diagnostics) | ✅ | ✅ | ✅ | ✅ | 90% |
| 🏠 Habitat (immobilier, déco, plans, scénarios) | ✅ | ✅ | ✅ | ⚠️ | 85% |
| 🎮 Jeux (paris, loto, euromillions, bankroll) | ✅ | ✅ | ✅ | ✅ | 80% |
| 📊 Dashboard (agrégation, alertes, résumé IA) | ✅ | ✅ | ✅ | ⚠️ | 90% |
| 🛠️ Outils (chat IA, notes, météo, convertisseur, minuteur) | ✅ | ✅ | ✅ | ⚠️ | 85% |
| ⚙️ Admin (audit, jobs, cache, users, feature flags) | ✅ | ✅ | — | ✅ | 90% |

---

## 2. Inventaire complet

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

## 3. Bugs & implémentations incomplètes

### 🔴 P0 — Bloquants

| # | Fichier | Ligne | Description | Impact |
|---|---------|-------|-------------|--------|
| 1 | `src/services/jeux/cron_jobs_loteries.py` | 51 | `# TODO: Implémenter scraping réel` — Le scraping FDJ est en mode **SIMULATION uniquement** | Le module Loto/Euromillions ne récupère aucune donnée réelle |
| 2 | `src/services/jeux/cron_jobs_loteries.py` | 67 | `# TODO: Insérer vrai tirage depuis API` — Insertion de données fictives | Les tirages affichés sont faux |
| 3 | `src/services/cuisine/cron_cuisine.py` | 63 | Alertes péremption détectées mais **notifications jamais envoyées** | L'utilisateur n'est pas prévenu des produits qui expirent |
| 4 | `src/services/cuisine/cron_cuisine.py` | 105 | Planning manquant détecté mais **aucun rappel envoyé** | L'utilisateur oublie de planifier ses repas |
| 5 | `src/services/cuisine/cron_cuisine.py` | 133 | Stock bas détecté mais **pas d'ajout auto à la liste de courses** | Circuit inventaire → courses cassé |

### 🟡 P1 — Importants

| # | Fichier | Ligne | Description | Impact |
|---|---------|-------|-------------|--------|
| 6 | `src/api/routes/preferences.py` | 285 | `pass` — Échec silencieux du parsing de l'heure | Préférences horaires potentiellement ignorées |
| 7 | `src/api/routes/webhooks_whatsapp.py` | 576 | `pass` — Échec silencieux du parsing de date | Les rappels anniversaires WhatsApp peuvent dysfonctionner |
| 8 | `src/services/famille/version_recette_jules.py` | 37 | `...` — Implémentation incomplète | Adaptation recettes pour Jules partiellement fonctionnelle |
| 9 | `src/api/routes/admin.py` | — | Historique des jobs uniquement en mémoire | Perdu au redémarrage du serveur |

### 🟢 P2 — Mineurs

| # | Fichier | Ligne | Description |
|---|---------|-------|-------------|
| 10 | `src/api/routes/export.py` | 204 | `pass` — Content-type permissif (intentionnel) |
| 11 | `src/api/routes/auth.py` | 94 | `pass` — Fallback numeric parse (intentionnel) |
| 12 | `src/api/routes/planning.py` | 688 | `...` — Placeholder docstring |

### Recherche globale TODO/FIXME/HACK

| Marqueur | Nombre | Localisation |
|----------|--------|--------------|
| `TODO` | 6 | cuisine/cron (3), jeux/cron (2), scripts/analysis (1) |
| `FIXME` | 0 | ✅ Aucun |
| `HACK` | 0 | ✅ Aucun |
| `NotImplemented` | 0 | ✅ Aucun en code (seulement règle linter) |

---

## 4. Gaps & features manquantes

### 4.1 Fonctionnalités backend manquantes

| Module | Feature manquante | Priorité | Effort |
|--------|-------------------|----------|--------|
| **Cuisine** | Notifications push/WhatsApp pour alertes péremption | P0 | Faible |
| **Cuisine** | Rappel automatique si planning semaine non rempli | P0 | Faible |
| **Cuisine** | Ajout automatique à la liste de courses si stock bas | P0 | Moyen |
| **Jeux** | Scraping réel tirages FDJ (Loto + EuroMillions) | P0 | Moyen |
| **Jeux** | API tirage en temps réel (ou source de données fiable) | P1 | Moyen |
| **Admin** | Persistance historique jobs en DB (pas juste mémoire) | P1 | Faible |
| **WhatsApp** | Validation numéro de téléphone | P1 | Faible |
| **WhatsApp** | Rate limiting sur les envois | P1 | Faible |
| **WhatsApp** | Fonction `_envoyer_aide_admin()` manquante (référencée mais non définie) | P1 | Faible |
| **Email** | Système de templates HTML (Jinja2 + dossier templates/) | P2 | Moyen |
| **Notifications** | Failover entre canaux (si push échoue → essayer email → WhatsApp) | P2 | Moyen |
| **Gamification** | Triggers badges sport + nutrition (pas implémentés dans le code) | P2 | Moyen |
| **Inventaire** | `suggerer_courses_ia()` marqué `# pragma: no cover` — non implémenté | P2 | Moyen |
| **Planning** | Suggestions IA pour périodes chargées (planning intelligent) | P2 | Moyen |

### 4.2 Fonctionnalités frontend manquantes

| Module | Feature manquante | Priorité |
|--------|-------------------|----------|
| **Admin** | Toggle "Mode Debug" visible admin-only | P1 |
| **Famille** | Trop de sous-menus (19) — regrouper en catégories | P2 |
| **Gamification** | Détail des badges sport + nutrition (liste, progression) | P2 |
| **All** | Mode offline (service worker + queue) — partiellement implémenté | P3 |

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

### 5.3 Recommandations de consolidation

| Action | Description | Priorité |
|--------|-------------|----------|
| **Absorber V003→V007 dans INIT_COMPLET** | Les 5 migrations doivent être fusionnées dans le fichier maître puisqu'on est en dev | P1 |
| **Supprimer le dossier `alembic/`** | Archivé et inutile — source de confusion | P2 |
| **Ajouter un script de vérification ORM↔SQL** | `scripts/audit_orm_sql.py` existe déjà — le rendre automatique dans CI | P2 |
| **Documenter les index** | Certaines tables manquent d'index explicites sur les FK fréquemment requêtées | P3 |
| **Centraliser les ENUMs SQL** | Certains ENUMs sont définis inline dans CREATE — les centraliser en début de fichier | P3 |

### 5.4 Tables à vérifier

| Catégorie | Tables | Notes |
|-----------|--------|-------|
| Tables orphelines potentielles | `openfoodfacts_cache`, `alertes_meteo`, `config_meteo` | Vérifier si utilisées activement |
| Tables très spécialisées | `presse_papier_entrees`, `mots_de_passe_maison`, `liens_favoris` | Peu de références dans le code |
| Tables volumineuses | `jeux_cotes_historique`, `historique_actions`, `logs_securite` | Prévoir purge/archivage |

---

## 6. Tests — Couverture et manques

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

### 6.3 Recommandations tests

| Action | Priorité | Effort |
|--------|----------|--------|
| Ajouter tests services habitat (plans IA, déco IA) | P1 | Moyen |
| Ajouter tests services dashboard (agrégation, anomalies) | P1 | Moyen |
| Tests fonctionnels intégrations (météo, calendrier Google, Garmin) | P1 | Moyen |
| Tests composants React (formulaire-recette, plan-3d, heatmaps) | P2 | Élevé |
| Tests hooks React (utiliser-websocket, utiliser-crud) | P2 | Moyen |
| Augmenter seuils couverture Vitest (50% → 70% lignes) | P2 | — |
| Ajouter tests de performance backend (au-delà de k6 baseline) | P3 | Élevé |
| Tests mutation (mutmut) intégrés en CI | P3 | Moyen |

---

## 7. Documentation — Audit qualité

### 7.1 Inventaire docs

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

### 7.2 Docs manquantes ou à créer

| Document | Contenu attendu | Priorité |
|----------|-----------------|----------|
| `FRONTEND_ARCHITECTURE.md` | Architecture CSS (Tailwind v4), composants, state management, routing | P1 |
| `ADMIN_GUIDE.md` | Guide dédié au panneau admin (jobs, feature flags, notifications test) | P1 |
| `WHATSAPP_SETUP.md` | Configuration Meta WhatsApp Business API, commandes disponibles | P2 |
| `GAMIFICATION.md` | Système de points/badges sport + nutrition uniquement | P2 |
| `HABITAT_MODULE.md` | Guide spécifique module habitat/immobilier | P3 |
| `CHANGELOG.md` | Historique des versions/sprints | P3 |

### 7.3 Docs à mettre à jour

| Document | Raison |
|----------|--------|
| `SERVICES_REFERENCE.md` | Ajouter les 10+ nouveaux services maison CRUD |
| `ERD_SCHEMA.md` | Ajouter diagrammes pour tables habitat, garmin, gamification (sport+nutrition) |
| `INTER_MODULES.md` | Documenter les nouveaux flux inter-modules (jardin→recettes, garmin→points) |
| `AUTOMATIONS.md` | Ajouter les 38 jobs CRON et leur statut actuel |

---

## 8. Interactions intra-modules

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
| De | Vers | Action | État |
|----|------|--------|------|
| Inventaire (stock bas) | Courses (ajout auto) | Ingrédient expirant → article courses | ❌ Non connecté |
| Anti-gaspi (produits expirants) | Recettes (suggestions) | Suggérer recettes avec produits à consommer | ⚠️ Logique existe mais pas déclenchée auto |
| Batch cooking (session terminée) | Inventaire (mise à jour stock) | Déduire les ingrédients utilisés du stock | ❌ Non connecté |
| Recettes (saison) | Planning (suggestions saisonnières) | Proposer recettes de saison en priorité | ⚠️ Partiellement |

### 8.2 Famille (déjà connecté)

```
Jules (développement) ──→ Activités ──→ Routines
         ↓                                  ↓
    Santé/Croissance              Budget familial
         ↓                                  ↓
    Gamification ←──── Garmin      Contacts/Documents
```

**Connexions manquantes intra-famille** :
| De | Vers | Action | État |
|----|------|--------|------|
| Anniversaires | Budget | Provisioner budget cadeaux automatiquement | ❌ |
| Voyages | Budget | Intégrer dépenses voyage dans budget | ❌ |
| Routines | Gamification | ~~Points pour routines complétées~~ **Exclu** — gamification limitée au sport + nutrition | ❌ Exclu |
| Documents (expiration) | Notifications | Alertes documents expirants | ⚠️ Existe mais notification pas envoyée |

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
| De | Vers | Action | État |
|----|------|--------|------|
| Diagnostics (problème détecté) | Artisans (matching) | Suggérer artisans pour le problème diagnostiqué | ⚠️ IA existe mais pas auto |
| Entretien saisonnier | Stocks | Vérifier si produits d'entretien en stock | ❌ |
| Charges (facture élevée) | Énergie anomalies IA | Déclencher analyse si facture anormale | ❌ |

---

## 9. Interactions inter-modules

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
| Jeux (gains/pertes) → Budget famille | L’argent gagné via les paris reste dans l’app de pari, pas de sync vers le budget familial |
| Garmin (sommeil) → Famille/Jules | Le suivi du sommeil via Garmin (ou autre) n’est pas souhaité — hors périmètre || Gamification → autres modules | La gamification est limitée au sport et à la nutrition. Pas de badges/points pour recettes, routines, maison, jardin, budget, etc. |
### 9.3 Connexions inter-modules manquantes (à créer)

| # | De | Vers | Flux proposé | Priorité | Impact |
|---|-----|------|-------------|----------|--------|
| 1 | **Inventaire (péremption)** | **Recettes (suggestions)** | Produits expirant sous 48h → proposer recettes les utilisant | P1 | ★★★ |
| 2 | **Météo** | **Planning repas** | Temps froid → suggestions plats chauds ; canicule → salades/gazpacho | P2 | ★★ |
| 3 | **Météo** | **Jardin** | Gel annoncé → alerte protection plantes ; pluie → ne pas arroser | P2 | ★★ |
| 4 | **Météo** | **Activités famille** | Pluie → indoor ; beau temps → outdoor ; neige → luge/ski | P2 | ★★ |
| 5 | **Entretien maison** | **Budget maison** | Intervention artisan → dépense budget automatique | P2 | ★★ |
| 6 | **Courses (achat)** | **Budget famille** | Total courses → catégorie alimentation budget | P1 | ★★★ |
| 7 | **Batch cooking** | **Inventaire** | Session terminée → déduire ingrédients consommés | P2 | ★★ |
| 8 | **Anniversaires** | **Courses** | Anniversaire proche → ajouter idées cadeaux/courses fête | P3 | ★ |
| 9 | **Voyages** | **Calendrier/Planning** | Voyage planifié → bloquer jours planning repas + activités | P2 | ★★ |
| 10 | **Contrats (fin proche)** | **Budget** | Contrat expirant → provisionner renouvellement | P3 | ★ |
| 11 | **Charges (énergie)** | **Dashboard** | Anomalie conso → alerte widget dashboard | P2 | ★★ |
| 12 | **Documents (expiration)** | **Notifications** | Passeport/carte identité expirant → rappel multi-canal | P1 | ★★★ |
| 13 | **Chat IA** | **Contexte multi-module** | Le chat IA connaît le contenu du frigo, le planning, les courses, le budget | P1 | ★★★ |

---

## 10. Opportunités IA à ajouter

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

| # | Module | Feature IA | Description | Priorité | Effort |
|---|--------|-----------|-------------|----------|--------|
| 1 | **Inventaire** | Suggestion achats intelligents | Analyser historique de consommation → prévoir les besoins | P1 | Moyen |
| 2 | **Planning** | Planning adaptatif | Ajuster le planning selon météo, énergie (Garmin), budget restant | P1 | Élevé |
| 3 | **Routines** | Optimisation routines | Analyser l'efficacité des routines et suggérer des améliorations | P2 | Moyen |
| 4 | **Contacts** | Enrichissement contacts | Suggérer catégorisation, rappels relationnels (« vous n'avez pas contacté X depuis 3 mois ») | P3 | Faible |
| 5 | **Anniversaires** | Idées cadeaux IA | Profil de la personne → 5 idées cadeaux avec budget | P2 | Faible |
| 6 | **Documents** | Analyse documents photo | Photographier un document → extraction OCR + classement auto | P2 | Moyen |
| 7 | **Jardin** | Diagnostic plantes photo | Photo d'une plante malade → diagnostic + traitement IA (Pixtral) | P1 | Faible (infra existe) |
| 8 | **Budget** | Prévision dépenses | Modèle prédictif basé sur l'historique → « vous allez dépasser votre budget fin de mois » | P1 | Moyen |
| 9 | **Courses** | Optimisation parcours magasin | Grouper les articles par rayon → ordre de parcours optimal | P3 | Moyen |
| 10 | **Chat IA** | Contexte multi-module | Le chat connaît frigo, planning, budget, météo, Jules → réponses contextuelles | P1 | Élevé |
| 11 | **Maison** | Estimation travaux IA améliorée | Photo avant/après + description → estimation coût/durée réaliste | P2 | Moyen |
| 12 | **Voyages** | Planning voyage IA | Destination + dates + budget → itinéraire complet avec activités | P2 | Moyen |
| 13 | **Énergie** | Recommandations économies | Analyser relevés compteurs → top 3 actions pour réduire la facture | P2 | Faible |
| 14 | **Loto/Euromillions** | Analyse tendances avancée | Analyse de fréquence + patterns + générateur statistique amélioré | P3 | Moyen |
| 15 | **Entretien** | Prédiction pannes | Historique entretien + âge équipements → « votre chauffe-eau aura probablement besoin d'entretien dans 3 mois » | P2 | Moyen |

---

## 11. Jobs automatiques (CRON)

### 11.1 Jobs existants (38+)

| Job | Horaire | Module | Statut |
|-----|---------|--------|--------|
| `alertes_peremption_48h` | Quotidien 7h | Cuisine | ⚠️ Détection OK, notification KO |
| `suggestion_planning_semaine` | Dimanche 18h | Cuisine | ⚠️ Détection OK, notification KO |
| `alerte_stock_bas` | Quotidien 8h | Cuisine | ⚠️ Détection OK, ajout auto KO |
| `nettoyage_plannings_anciens` | Mensuel | Cuisine | ✅ OK |
| `rappels_famille` | Quotidien 7h | Famille | ✅ OK |
| `rappels_maison` | Quotidien 8h | Maison | ✅ OK |
| `points_famille_hebdo` | Dimanche 20h | Gamification | ✅ OK |
| `scraper_resultats_fdj` | Quotidien 21h30 | Jeux | ❌ Simulation |
| `scraper_euromillions` | Mardi/Vendredi 21h30 | Jeux | ❌ Simulation |
| `garmin_sync_matinal` | Quotidien 6h | Famille | ✅ OK |
| `sync_google_calendar` | Quotidien 23h | Famille | ✅ OK |
| `enrichissement_catalogues` | 1er/mois 3h | Core | ✅ OK |
| `automations_runner` | Toutes les 5 min | Core | ✅ OK |
| `digest_quotidien` | Quotidien 7h30 | Notifications | ✅ OK |
| `digest_hebdo` | Dimanche 18h | Notifications | ✅ OK |
| `purge_cache` | Quotidien 3h | Core | ✅ OK |
| `nettoyage_logs` | Mensuel | Admin | ✅ OK |
| `backup_auto` | Quotidien 2h | Core | ✅ OK |
| ... | ... | ... | ... |

### 11.2 Jobs à ajouter

| Job | Horaire proposé | Module | Description | Priorité |
|-----|-----------------|--------|-------------|----------|
| `rappel_documents_expirants` | Quotidien 8h | Famille | Alerter si document expire dans 30/15/7 jours | P1 |
| `rapport_mensuel_auto` | 1er/mois 8h | Dashboard | Générer et envoyer le rapport mensuel automatiquement | P2 |
| `sync_contrats_alertes` | Hebdo lundi 9h | Maison | Contrats expirant sous 30 jours → alerte | P2 |
| `optimisation_routines` | Mensuel | Famille | Analyser efficacité routines → suggestions IA | P3 |
| `bilan_energetique` | Mensuel | Maison | Comparer conso énergie mois précédent → alerte si anomalie | P2 |
| `rappel_vaccins` | Lundi 9h | Famille | Vérifier calendrier vaccinal Jules → rappel si retard | P2 |
| `suggestions_saison` | 1er/mois | Cuisine | Mettre en avant les produits de saison du mois | P3 |
| `purge_historique_jeux` | Mensuel | Jeux | Archiver données de paris > 12 mois | P3 |
| `check_garanties_expirant` | Hebdo | Maison | Garanties qui expirent sous 60 jours → alerte | P2 |
| `veille_emploi` | Quotidien 7h | Habitat | Scraper multi-sites (Indeed, LinkedIn, WTTJ, France Travail, Apec) pour offres RH hybride/télétravail à ~30 min → alerte si nouvelle offre | P2 |

---

## 12. Notifications — WhatsApp, Email, Push

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

### 12.3 Améliorations notifications proposées

| # | Amélioration | Canal | Priorité |
|---|-------------|-------|----------|
| 1 | **Cascade failover** : Push → Email → WhatsApp si échec | Tous | P1 |
| 2 | **Templates email HTML** avec Jinja2 | Email | P1 |
| 3 | **Commandes WhatsApp supplémentaires** : `planning`, `météo`, `rappels`, `jardin` | WhatsApp | P2 |
| 4 | **Boutons interactifs WhatsApp** : valider/modifier planning, cocher article courses | WhatsApp | P2 |
| 5 | **Digest WhatsApp matinal** : résumé de la journée (tâches, repas, météo, rappels) | WhatsApp | P1 |
| 6 | **Rate limiting WhatsApp** | WhatsApp | P1 |
| 7 | **Validation numéro téléphone** | WhatsApp | P1 |
| 8 | **Réponses vocales WhatsApp** → transcription IA | WhatsApp | P3 |
| 9 | **Email résumé hebdo** automatique | Email | P2 |
| 10 | **Notifications contextuelles** (basées sur localisation, heure, habitudes) | Push | P3 |

---

## 13. Mode Admin manuel (test)

### 13.1 Ce qui existe

Le panneau admin est **déjà bien avancé** avec :

- **13 endpoints API admin** protégés par `require_role("admin")`
- **6 pages frontend admin** (dashboard, utilisateurs, jobs, notifications, services, sql-views)
- **38+ jobs CRON** déclenchables manuellement via `POST /api/v1/admin/jobs/{id}/run`
- **Test notifications** via `POST /api/v1/admin/notifications/test`
- **Cache management** : stats, purge par pattern, clear total
- **Feature flags** : toggles runtime stockés en DB
- **Audit logs** : historique complet + export CSV

### 13.2 Améliorations proposées pour le mode admin

| # | Feature | Description | Priorité |
|---|---------|-------------|----------|
| 1 | **Toggle "Mode Test" global** | Un switch admin-only qui active les logs verbose, désactive le rate limiting, affiche les IDs internes — invisible pour l'utilisateur normal | P0 |
| 2 | **Console d'exécution manuelle** | UI admin pour exécuter n'importe quel job CRON avec paramètres custom (date simulée, user cible, etc.) | P1 |
| 3 | **Simulateur de flux** | Pouvoir simuler un flux complet (ex : « Simuler une péremption dans 24h ») et voir le résultat sans toucher aux données réelles | P2 |
| 4 | **Dashboard temps réel admin** | Métriques live : requêtes/sec, latence API, cache hit rate, erreurs, files d'attente | P2 |
| 5 | **Persistance historique jobs en DB** | Les logs de jobs sont en mémoire et perdus au restart — les persister | P1 |
| 6 | **Bouton "Déclencher all notifications"** | Tester tous les canaux d'un coup (push + email + WhatsApp) avec un payload de test | P1 |
| 7 | **Dry-run mode pour CRON** | Exécuter un job en mode preview (voir ce qu'il ferait sans commit) | P2 |
| 8 | **Reset module** | Bouton admin pour remettre à zéro un module entier (données de test) | P3 |
| 9 | **Import/export config** | Sauvegarder et restaurer la configuration complète (feature flags, preferences, automations) | P2 |
| 10 | **Logs structurés temps réel** | WebSocket admin qui stream les logs du serveur en temps réel | P3 |

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

### 14.2 Recommandations de simplification

| # | Zone | Problème | Solution | Priorité |
|---|------|----------|----------|----------|
| 1 | **Sidebar Famille** | 19 sous-menus = surcharge cognitive | Regrouper en 4 catégories : **Enfant** (Jules, santé, gamification), **Vie quotidienne** (activités, routines, weekend), **Finances** (budget, achats), **Admin famille** (contacts, documents, voyages) | P1 |
| 2 | **Sidebar Maison** | 11 sous-menus | Regrouper en 3 : **Entretien** (ménage, jardin, travaux, équipements), **Finances** (charges, contrats, artisans, diagnostics), **Inventaire** (provisions, meubles, documents) | P2 |
| 3 | **Actions rapides dashboard** | Présentes mais pas assez mises en avant | Ajouter un FAB (Floating Action Button) mobile pour les 3 actions les plus fréquentes : ajouter recette, ajouter article courses, noter dépense | P1 |
| 4 | **Ma Semaine** | Existe en doublon (sidebar + cuisine) | Unifier en un seul point d'accès : vue unifiée semaine = repas + tâches maison + activités Jules + anniversaires | P1 |
| 5 | **Flux ajout recette** | Nombre de champs du formulaire | Mode simplifié (nom + photo) et mode avancé (tous les champs) | P2 |
| 6 | **Flux courses** | Créer une liste → ajouter articles → cocher | « Ajouter article » visible en permanence en bas de la liste active (pas de navigation) | P1 |
| 7 | **Onboarding** | 5 étapes — ok mais pas de personnalisation | Ajouter une étape « Quels modules utilisez-vous ? » → cacher les modules inutiles | P2 |
| 8 | **Recherche globale** | Existe mais Ctrl+K | Ajouter un champ de recherche visible en permanence sur mobile (icône en header) | P2 |
| 9 | **Nombre de clics** | 2 clics max pour les actions fréquentes | Raccourcis swipe sur mobile (swipe gauche = supprimer, swipe droite = cocher/valider) — composant `swipeable-item.tsx` existe déjà | P2 |
| 10 | **Home widgets** | 11 widgets — potentiellement surchargé | Permettre à l'utilisateur de choisir ses 4-6 widgets préférés (déjà configurable) + presets par profil (« Cuisine », « Famille complète ») | P3 |

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

## 15. Gamification

> **Périmètre volontairement limité** : La gamification sert uniquement à inciter à **faire du sport** et **bien manger**. Aucun badge/point pour d'autres modules (maison, recettes cuisinées, routines, budget, jardin, etc.).

### 15.1 État actuel

| Élément | État | Notes |
|---------|------|-------|
| **Modèle PointsUtilisateur** | ✅ | Points sport + alimentation par semaine |
| **Modèle BadgeUtilisateur** | ✅ | Type, label, date acquisition, méta |
| **Calcul points hebdo** | ✅ | CRON dimanche 20h, agrège Garmin (sport) + nutrition |
| **Page gamification frontend** | ✅ | Cartes métriques + barres de progression |
| **API points-famille** | ✅ | GET endpoint fonctionnel |

### 15.2 Manques gamification (sport + nutrition uniquement)

| Feature | Description | Priorité |
|---------|-------------|----------|
| **Triggers badges sport** | Conditions : X pas/jour pendant 7j consécutifs, N sessions sport/semaine, objectif calories brûlées atteint — pas implémentés dans le code | P2 |
| **Triggers badges nutrition** | Conditions : planning repas équilibré N jours de suite, score nutritionnel moyen > seuil, anti-gaspi zéro déchet sur 1 semaine | P2 |
| **Détail badges** | Liste des badges sport + nutrition possibles avec progression (ex : 15/30 jours de marche) | P2 |
| **Historique points** | Graphique évolution des points sport + nutrition semaine par semaine | P3 |
| **Notifications badges** | Alerte push quand un badge sport ou nutrition est débloqué | P2 |

---

## 16. Axes d'innovation

### 16.1 Innovations techniques

| # | Innovation | Description | Impact | Effort |
|---|-----------|-------------|--------|--------|
| 1 | **Assistant vocal intégré** | Le composant `fab-assistant-vocal.tsx` existe — connecter au chat IA avec contexte multi-module | ★★★ | Moyen |
| 2 | **Mode hors-ligne complet** | Service worker + IndexedDB queue (infra PWA existe, logique partielle) → sync au retour réseau | ★★★ | Élevé |
| 3 | **Widgets home personnalisables** | Drag & drop widgets (composant `grille-widgets.tsx` existe) — ajouter des widgets par module | ★★ | Moyen |
| 4 | **API GraphQL** | Option GraphQL pour le frontend (réduire les appels réseau sur le dashboard qui fait 11 requêtes) | ★★ | Élevé |
| 5 | **WebSocket temps réel étendu** | Étendre le WebSocket courses à d'autres modules (planning partagé, tâches maison) | ★★ | Moyen |

### 16.2 Innovations fonctionnelles

| # | Innovation | Description | Impact | Effort |
|---|-----------|-------------|--------|--------|
| 6 | **Briefing matinal IA** | Chaque matin à 7h → digest personnalisé : météo + repas du jour + tâches + rappels + anniversaires + résumé budget. **Configurable** par utilisateur (activable/désactivable) car ne plaira pas forcément à tout le monde (ex : Mathieu) | ★★★ | Faible |
| 7 | **Analyse photos multi-usage** | Un seul bouton photo → IA détecte le contexte : frigo → inventaire, reçu → dépense, plante → diagnostic, document → classement | ★★★ | Moyen |
| 8 | **Tableau de bord familial partagé** | Un mode "famille" où chaque membre voit sa vue mais les données sont partagées (courses, planning, tâches) | ★★★ | Élevé |
| 9 | **Score bien-être familial** | Combiner Garmin (sport), nutrition (planning), budget (stress financier), routines (régularité) → score global 0-100 | ★★ | Moyen |
| 10 | **Suggestions proactives** | Au lieu d'attendre que l'utilisateur demande → l'app propose : "Vous n'avez rien prévu pour mercredi, voici 3 recettes rapides avec ce qui vous reste" | ★★★ | Moyen |
| 11 | **Intégration supermarché** | Connexion API drives (Carrefour, Leclerc, Auchan) → envoyer la liste de courses directement en commande | ★★ | Élevé |
| 12 | **Compagnon vocal WhatsApp** | Au lieu de taper des commandes → audio WhatsApp transcrit par IA → action automatique | ★★ | Moyen |
| 13 | **Mini-jeux éducatifs Jules** | Relier les jalons développementaux à des activités interactives adaptées à l'âge + suggestions d'achats de jeux adaptés au stade de développement | ★★ | Élevé |
| 14 | **Mode invité** | Un lien partageable pour que la nounou/grands-parents voient certaines infos (repas Jules, routines, contacts urgence) sans compte | ★★ | Moyen |
| 15 | **Bilan annuel automatique** | En décembre → rapport IA complet : recettes cuisinées, budget dépensé, projets maison terminés, croissance Jules, points gaming | ★★ | Faible |
| 16 | **Rappels intelligents contextuels** | Le service `rappels_intelligents.py` existe — l'enrichir : rappeler les courses si vous passez près d'un magasin (géoloc), rappeler le ménage si Garmin montre que vous êtes à la maison | ★★ | Élevé |
| 17 | **Gestion multi-enfants** | L'app est centrée sur Jules — prévoir l'architecture pour un éventuel frère ou sœur (périmètre famille uniquement, pas multi-famille) | ★★ | Moyen |
| 18 | **Veille emploi (Habitat)** | Scanner quotidien multi-sites (Indeed, LinkedIn, Welcome to the Jungle, France Travail, Apec, etc.) pour détecter les offres RH (ou autre domaine paramétrable) avec télétravail/hybride, CDI/consultant, possibilité 4j/semaine, dans un rayon de ~30 min en voiture (paramétrable). Alerte push/WhatsApp/email si nouvelle offre. Impact direct sur la décision habitat (partir/rester). Pour Mathieu principalement. **Tous les critères paramétrables** : domaine, mots-clés, type contrat, mode de travail, rayon, fréquence. | ★★★ | Moyen |

---

## 17. Plan d'action priorisé

### Phase 1 — Corrections critiques (P0)

> **Objectif** : Corriger les bugs bloquants et connecter les circuits interrompus

| # | Action | Fichier(s) | Type |
|---|--------|-----------|------|
| 1.1 | Câbler les notifications push/WhatsApp sur les alertes péremption | `cron_cuisine.py:63` | Bug fix |
| 1.2 | Câbler le rappel planning manquant | `cron_cuisine.py:105` | Bug fix |
| 1.3 | Connecter stock bas → ajout auto courses | `cron_cuisine.py:133` | Bug fix |
| 1.4 | Implémenter source de données loterie réelle (API ou scraping FDJ) | `cron_jobs_loteries.py:51,67` | Feature |
| 1.5 | Absorber migrations V003→V007 dans `INIT_COMPLET.sql` | `sql/` | Consolidation |
| 1.6 | Créer le toggle "Mode Test" admin-only | `admin.py` + frontend | Feature |

### Phase 2 — Connexions inter-modules (P1)

> **Objectif** : Tous les modules communiquent de façon fluide

| # | Action | Flux |
|---|--------|------|
| 2.1 | Inventaire péremption → Suggestions recettes | Produits expirants → proposition auto |
| 2.2 | Courses total → Budget catégorie alimentation | Synchronisation achats |
| 2.3 | Documents expiration → Notifications multi-canal | Alerte 30/15/7 jours |
| 2.4 | Chat IA → Contexte multi-module | Le chat connaît frigo + planning + budget + météo |
| 2.5 | Briefing matinal IA | Digest quotidien personnalisé 7h — configurable on/off par utilisateur |

### Phase 3 — Tests & documentation (P1-P2)

> **Objectif** : Couverture tests > 80%, documentation complète

| # | Action |
|---|--------|
| 3.1 | Tests services habitat (plans IA, déco IA) |
| 3.2 | Tests services dashboard (agrégation, anomalies) |
| 3.3 | Tests intégrations (météo, Google Calendar, Garmin) |
| 3.4 | Tests composants React (formulaire-recette, plan-3d, heatmaps) |
| 3.5 | Créer `FRONTEND_ARCHITECTURE.md` |
| 3.6 | Créer `ADMIN_GUIDE.md` |
| 3.7 | Créer `WHATSAPP_SETUP.md` |
| 3.8 | Mettre à jour `ERD_SCHEMA.md` (ajout habitat, garmin, gamification) |
| 3.9 | Mettre à jour `SERVICES_REFERENCE.md` (services maison CRUD) |

### Phase 4 — UX simplification (P1-P2)

> **Objectif** : Flux utilisateur en 1-2 clics, interface épurée

| # | Action |
|---|--------|
| 4.1 | Regrouper sous-menus Famille (19 → 4 catégories) |
| 4.2 | FAB mobile (+) pour actions rapides (recette, courses, dépense, scan) |
| 4.3 | Vue "Ma Semaine" unifiée (repas + tâches + activités + anniversaires) |
| 4.4 | Mode simplifié formulaire recette (nom + photo) |
| 4.5 | Champ "ajouter article" toujours visible sur la liste de courses active |
| 4.6 | Regrouper sous-menus Maison (11 → 3 catégories) |

### Phase 5 — Notifications avancées (P1-P2)

> **Objectif** : Système de notification fiable et multi-canal

| # | Action |
|---|--------|
| 5.1 | Cascade failover (Push → Email → WhatsApp) |
| 5.2 | Templates email HTML (Jinja2) |
| 5.3 | Rate limiting WhatsApp |
| 5.4 | Validation numéro téléphone |
| 5.5 | Commandes WhatsApp supplémentaires (planning, météo, jardin) |
| 5.6 | Digest WhatsApp matinal |
| 5.7 | Fix `_envoyer_aide_admin()` manquant |

### Phase 6 — IA avancée (P1-P2)

> **Objectif** : IA proactive et contextuelle

| # | Action |
|---|--------|
| 6.1 | Inventaire → suggestions achats IA (historique consommation) |
| 6.2 | Planning adaptatif (météo + énergie Garmin + budget) |
| 6.3 | Diagnostic plantes photo (Pixtral — infra existe) |
| 6.4 | Budget → prévision dépenses fin de mois |
| 6.5 | Idées cadeaux IA (anniversaires) |
| 6.6 | Analyse photo multi-usage (un bouton, IA détecte le contexte) |

### Phase 7 — Mode admin avancé (P1-P2)

> **Objectif** : Admin peut tout tester et monitorer

| # | Action |
|---|--------|
| 7.1 | Persistance historique jobs en DB |
| 7.2 | Console d'exécution manuelle avec paramètres custom |
| 7.3 | Bouton "Tester tous les canaux notifications" |
| 7.4 | Dry-run mode CRON (preview sans commit) |
| 7.5 | Import/export configuration complète |

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

### Phase 9 — Gamification sport + nutrition (P2-P3)

> **Objectif** : Inciter à faire du sport et bien manger via badges et points (périmètre limité volontairement)

| # | Action |
|---|--------|
| 9.1 | Implémenter triggers badges sport (pas/jour, sessions/semaine, calories brûlées) |
| 9.2 | Implémenter triggers badges nutrition (planning équilibré, score nutritionnel, anti-gaspi) |
| 9.3 | Page détail badges sport + nutrition (liste + progression) |
| 9.4 | Notifications push badges débloqués |
| 9.5 | Historique points sport + nutrition (graphique hebdomadaire) |

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

---

## Annexe A — Fichiers à surveiller

| Fichier | Raison | Action |
|---------|--------|--------|
| `src/api/routes/jeux.py` | 2400+ lignes | Envisager split en 3 fichiers (paris, loto, euromillions) |
| `src/api/routes/maison_finances.py` | 900+ lignes | Déjà splitté mais encore gros |
| `sql/INIT_COMPLET.sql` | 3366 lignes | Absorber les migrations V003-V007 |
| `alembic/` | Archivé | Supprimer le dossier |
| `tests/conftest.py` | 710+ lignes | Envisager split par module |

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

> **Résumé** : L'application est mature et bien structurée (90%+ de complétude). Les corrections critiques se limitent à 5 bugs (notifications non câblées + scraping loterie simulé). Les plus grandes opportunités résident dans les connexions inter-modules, l'IA proactive, et la simplification UX. Le mode admin est déjà fonctionnel et mérite quelques améliorations pour le rendre parfait pour les tests manuels.
