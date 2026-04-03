# Audit Complet — Assistant Matanne

> **Date** : 3 avril 2026
> **Périmètre** : Application complète (Backend + Frontend + SQL + Tests + Docs + UI)
> **Objectif** : Détection bugs, gaps, manques, plan d'amélioration, notation par catégorie

---

## Table des matières

1. [Notation par catégorie](#1-notation-par-categorie)
2. [État des lieux par module](#2-etat-des-lieux-par-module)
3. [Bugs et problèmes détectés](#3-bugs-et-problemes-detectes)
4. [Code à supprimer (legacy / rejeté)](#4-code-a-supprimer)
5. [Nettoyage des commentaires Phase/Sprint](#5-nettoyage-commentaires)
6. [Consolidation SQL](#6-consolidation-sql)
7. [Tests — Gaps et plan](#7-tests)
8. [Documentation — Réorganisation](#8-documentation)
9. [Interactions inter-modules — État et opportunités](#9-inter-modules)
10. [IA — Intégrations existantes et opportunités](#10-ia)
11. [Automatisations et jobs CRON](#11-automatisations)
12. [Telegram — Couverture et extensions](#12-telegram)
13. [Mode Admin manuel (dev/test)](#13-admin-manuel)
14. [UI/UX — État actuel et améliorations](#14-ui-ux)
15. [Simplification des flux utilisateur](#15-flux-utilisateur)
16. [Fichiers fourre-tout à éclater](#16-fichiers-fourre-tout)
17. [Axes d'innovation](#17-innovation)
18. [Plan d'exécution priorisé](#18-plan-execution)

---

## 1. Notation par catégorie

| Catégorie | Note | Commentaire |
|-----------|------|-------------|
| **Architecture backend** | 9/10 | Excellente : lazy-loading, service factory, event bus, décorateurs, résilience. Très mature. |
| **Architecture frontend** | 8.5/10 | Solide : App Router, TanStack Query, Zustand, hooks typés. Manque code-splitting avancé. |
| **Modèles de données (SQL/ORM)** | 8.5/10 | ✅ Sprint 2 complété : 06_maison.sql éclaté (5 fichiers), 6 indexes ajoutés, RLS complète (150+ tables, jeux_bankroll_historique included), 32 seed data. Format SQL-first avec regenerate_init.py. |
| **API REST** | 8/10 | 300+ endpoints bien structurés. Manque : exemples Swagger, contraintes longueur strings. |
| **Services métier** | 8.5/10 | 150+ services, 40 AI, patterns cohérents. Trop de bridges (31 fichiers à consolider). |
| **Intégration IA (Mistral)** | 9/10 | Rate limiting, cache sémantique, circuit breaker, streaming, vision. Très complet. |
| **Tests** | 6.5/10 | Backend fort (4932 tests), frontend faible (~77 stubs), E2E incomplet, WebSocket non testé. |
| **Documentation** | 7/10 | 43 fichiers, bonne couverture. Doublons, références OCR/Phase obsolètes, pas de CHANGELOG. |
| **UI/UX Design** | 7.5/10 | shadcn/ui + Tailwind v4, dark mode, responsive. Manque : animations, micro-interactions, polish. |
| **Visualisation données** | 8/10 | 18 graphiques (Recharts, D3, SVG custom), 1 vue 3D (Three.js), 1 jardin SVG. Bon niveau. |
| **Automatisations (CRON)** | 8.5/10 | 52 jobs bien organisés. Manque : email, monitoring échecs, retry automatique. |
| **Telegram** | 8/10 | 26 fonctions, inline keyboards, state. Manque : commandes interactives, menus riches. |
| **Admin/DevTools** | 7.5/10 | Panel flottant, triggers manuels, flags. Manque : logs temps réel, historique exécutions. |
| **Sécurité** | 8/10 | JWT, RLS, sanitizer XSS, rate limiting, CORS. RLS incomplet sur toutes les tables. |
| **Performance** | 7.5/10 | Cache multi-niveaux, lazy loading. Manque : indexes DB, bundle splitting, memoization. |
| **Organisation du code** | 7/10 | Bonne structure mais : fichiers fourre-tout, noms de phases dans code, dead code restant. |
| | | |
| **Note globale** | **7.9/10** | **Application très fonctionnelle et bien architecturée. Amélioration +0.1 via Sprint 2 (SQL consolidé, indexes + RLS + data). Points faibles restants : polish UI, tests frontend, nettoyage legacy.** |

---

## 2. État des lieux par module

### Cuisine (Recettes, Planning, Courses, Inventaire, Batch Cooking)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Recettes CRUD | ✅ | ✅ | ✅ | Suggestions | Complet |
| Planning repas | ✅ | ✅ | ✅ | Génération IA | Complet |
| Courses | ✅ + WebSocket | ✅ | ⚠️ WS non testé | Agrégation IA | Complet |
| Inventaire/Stock | ✅ | ✅ | ✅ | Basique | Complet |
| Batch Cooking | ✅ | ✅ | ✅ | Planning IA | Complet |
| Anti-gaspillage | ✅ | ✅ | ⚠️ Léger | Suggestions | Complet |
| Import recettes URL/PDF | ✅ | ✅ | ✅ | Parsing IA | Complet |
| Nutrition (Jules) | ✅ | ✅ | ✅ | Adaptation IA | Complet |

### Famille (Jules, Budget, Activités, Routines, Documents)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Profil Jules | ✅ | ✅ | ✅ | Développement IA | Complet |
| Budget famille | ✅ | ✅ | ✅ | Prévisions IA | Complet |
| Activités | ✅ | ✅ | ✅ | Suggestions météo | Complet |
| Routines | ✅ | ✅ | ✅ | — | Complet |
| Documents (expiration) | ✅ | ✅ | ✅ | Alertes | Complet |
| Anniversaires | ✅ | ✅ | ✅ | — | Complet |
| Weekend | ✅ | ✅ | ✅ | Suggestions IA | Complet |
| Journal | ✅ | ✅ | ⚠️ | — | À vérifier |
| Contacts | ✅ | ✅ | ⚠️ | — | À vérifier |
| Voyages | ✅ | ✅ | ⚠️ Léger | Destockage IA | À vérifier |

### Maison (Projets, Entretien, Énergie, Jardin, Équipements)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Projets (Kanban) | ✅ | ✅ | ✅ | Conseils IA | Complet |
| Entretien saisonnier | ✅ | ✅ | ✅ | Fiches tâches IA | Complet |
| Énergie | ✅ | ✅ | ✅ | — | Complet |
| Jardin/Plantes | ✅ | ✅ vue SVG | ✅ | Basique | Complet |
| Équipements/Meubles | ✅ | ✅ | ⚠️ | — | Complet |
| Artisans | ✅ | ✅ | ⚠️ | — | Complet |
| Charges/Abonnements | ✅ | ✅ | ⚠️ | Comparateur | Complet |
| Visualisation 3D | ✅ | ✅ Three.js | — | — | Complet |
| Provisions/Cellier | ✅ | ✅ | ⚠️ | — | Complet |

### Jeux (Paris sportifs, Loto, Euromillions, Bankroll)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Paris sportifs | ✅ | ✅ | ✅ | Analyse cotes IA | Complet |
| Loto | ✅ | ✅ heatmap | ✅ | Patterns IA | Complet |
| Euromillions | ✅ | ✅ heatmap + backtest | ✅ | Backtest IA | Complet |
| Bankroll | ✅ | ✅ widget | ✅ | — | Complet |
| Performance/Stats | ✅ | ✅ graphiques | ✅ | — | Complet |

### Outils (Chat IA, Convertisseur, Météo, Notes, Minuteur)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Chat IA | ✅ streaming | ✅ | ⚠️ | Conversationnel | Complet |
| Convertisseur | ✅ | ✅ | ✅ | — | Complet |
| Météo | ✅ | ✅ | ✅ | Impact IA | Complet |
| Notes | ✅ | ✅ | ⚠️ | — | Complet |
| Minuteur | — (frontend only) | ✅ | ⚠️ | — | Complet |
| Assistant vocal | — | ✅ hooks | — | — | Complet |
| Résumé IA hebdo | ✅ | ✅ | ✅ | Résumé IA | Complet |
| Automations | ✅ | ✅ | ⚠️ | Rules engine | Complet |

### Habitat (Veille immo, DVF, Marché)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Veille immobilière | ✅ | ✅ | ⚠️ | — | Complet |
| Données DVF | ✅ | ✅ graphiques | ⚠️ | — | Complet |
| Déco/Scénarios | ✅ | ✅ | ⚠️ | — | Complet |

### Admin & Dashboard

| Sous-module | Backend | Frontend | Tests | Status |
|-------------|---------|----------|-------|--------|
| Dashboard accueil | ✅ | ✅ DnD | ✅ | Complet |
| Panel admin flottant | ✅ | ✅ Ctrl+Shift+A | — | Complet |
| Jobs management | ✅ 52 jobs | ✅ | ⚠️ | Complet |
| Feature flags | ✅ 12 flags | ✅ | ⚠️ | Complet |
| Audit logs | ✅ | ✅ | ⚠️ | Complet |

---

## 3. Bugs et problèmes détectés

### Problèmes critiques

| # | Problème | Localisation | Impact | Action |
|---|----------|-------------|--------|--------|
| B1 | **WebSocket courses non testé** | `src/api/websocket_courses.py` | Collaboration temps réel peut casser silencieusement | Écrire tests WebSocket |
| B2 | **Migration V002 bloquée** — UUID conversion incomplète | `sql/migrations/V002_*.sql` | Données user_id en VARCHAR au lieu d'UUID | Nettoyer données puis appliquer |
| B3 | **RLS incomplet** — seulement ~17/150 tables vérifiées | `sql/` | Données potentiellement accessibles cross-user | Auditer toutes les tables |
| B4 | **Indexes manquants** sur champs requêtés fréquemment | `src/core/models/` | Requêtes lentes en production | Ajouter indexes |
| B5 | **WhatsApp alias encore dans le code** | `notif_dispatcher.py`, `notifications_historique.py` | Confusion + code mort | Supprimer |

### Problèmes modérés

| # | Problème | Localisation | Action |
|---|----------|-------------|--------|
| M1 | **Schemas Pydantic sans `example`** — Swagger appauvri | `src/api/schemas/` | Ajouter exemples pour documentation interactive |
| M2 | **Pas de contraintes longueur sur strings** | `src/api/schemas/` | Ajouter `max_length` sur champs texte |
| M3 | **Frontend : `alt` manquant sur images** — accessibilité | Composants image | Ajouter attributs `alt` descriptifs |
| M4 | **D3/Three.js non lazy-loaded partout** | Composants graphiques | Vérifier `dynamic()` import sur tous les composants lourds |
| M5 | **Email non implémenté** — rapports mentionnent email | Services rapports | Implémenter ou retirer les références |
| M6 | **06_maison.sql = 43 tables dans 1 fichier** | `sql/06_maison.sql` | Éclater en sous-fichiers |

### Problèmes mineurs

| # | Problème | Action |
|---|----------|--------|
| m1 | Tests frontend majoritairement stubs | Étoffer progressivement |
| m2 | Pas de tests de charge (load testing) | Configurer k6/locust |
| m3 | Pas de mutation testing | Activer mutmut (configuré mais inutilisé) |
| m4 | Pas de tests contract/OpenAPI | Implémenter schemathesis |
| m5 | Composants formulaires longs sans code-splitting | Découper avec `React.lazy` |

---

## 4. Code à supprimer

### Fichiers à supprimer (features rejetées)

| Fichier | Raison | Priorité |
|---------|--------|----------|
| `src/api/routes/partage.py` | Partage social rejeté (pas de marketplace/communautaire) | 🔴 Haute |
| `src/services/cuisine/partage_recettes.py` | Service de partage recettes (plus utilisé) | 🔴 Haute |
| `src/services/utilitaires/ocr_service.py` | OCR rejeté (pas de scan tickets) | 🔴 Haute |
| `frontend/src/app/share/recette/[token]/page.tsx` | Page publique de partage recette | 🔴 Haute |
| `src/services/innovations/cuisine_ia.py` | Optimisation coûts alimentaires (rejeté) | 🟡 Moyenne |

### Code à nettoyer dans des fichiers existants

| Fichier | Ce qu'il faut retirer |
|---------|----------------------|
| `src/services/core/notifications/notif_dispatcher.py` | Alias "whatsapp" (lignes 26, 58, 133, 389, 461) |
| `src/core/models/notifications_historique.py` | "whatsapp" dans l'enum `Canal` |
| `src/api/main.py` | Vérifier si `partage_router` est encore inclus |
| Tests associés | Supprimer tests des features retirées |

### Tables SQL à supprimer

| Table | Raison |
|-------|--------|
| `garanties` | Rejeté — badge "sous garantie" sur fiche équipement suffit |
| `incidents_sav` | Rejeté — pas de module SAV dédié |
| `contrats` | Rejeté — pas d'alertes renouvellement, juste comparateur |
| `preferences_home` | Inutile si préférences sont gérées côté frontend |

---

## 5. Nettoyage des commentaires Phase/Sprint

### Fichiers avec references Phase/Sprint dans le code

150+ occurrences trouvées. Voici les fichiers principaux à nettoyer :

**Backend — Priorité haute :**

| Fichier | Exemples de commentaires à mettre à jour |
|---------|------------------------------------------|
| `src/api/routes/fonctionnalites_avancees.py` | 24 endpoints avec `/phase9/` et `/phasee/` dans les URLs |
| `src/api/routes/webhooks_telegram.py` | "Phase 5.2: Webhook callbacks" |
| `src/api/routes/notifications_enrichies.py` | "Routes API pour Sprint E" |
| `src/services/innovations/service.py` | "Service Innovations — Phases 9 et 10" |
| `src/services/innovations/types.py` | "Types Pydantic pour les services Innovations — Phase 10" |
| `src/api/dependencies.py` | Références "Phase A" |
| `src/api/auth.py` | Références "Phase A" |
| `src/core/models/*.py` | Multiples "Phase A/B" dans docstrings |

**Frontend — Priorité haute :**

| Fichier | Exemples |
|---------|----------|
| `frontend/src/app/(app)/admin/services/page.tsx` | `obtenirStatutBridgesPhase5` |
| `frontend/src/app/(app)/admin/page.tsx` | Structure de données Phase 5 / Phase E |
| `frontend/src/composants/disposition/coquille-app.tsx` | "Phase W" |
| `frontend/src/app/(app)/outils/resume-ia/page.tsx` | "Phase B" |
| `frontend/src/app/(app)/jeux/paris/page.tsx` | "Phase T" |
| `frontend/src/app/(app)/famille/page.tsx` | "Phase Refonte" |

**Tests :**

| Fichier | Action |
|---------|--------|
| `tests/inter_modules/test_bridges_phase2.py` | Renommer → `test_bridges_inter_modules.py` |
| Tous les tests avec "Phase X" dans les noms | Renommer avec description fonctionnelle |

**Règle** : Remplacer tout commentaire "Phase X" / "Sprint Y" par une description fonctionnelle de ce que fait le code.

---

## 6. Consolidation SQL

### État actuel (Sprint 2 ✅ Complété)

```
sql/schema/
├── 01_extensions.sql       # Extensions PostgreSQL
├── 02_functions.sql        # Fonctions utilitaires
├── 03_systeme.sql          # Tables système
├── 04_cuisine.sql          # Module cuisine
├── 05_famille.sql          # Module famille
├── 06a_projets.sql         # Maison — Projets & routines
├── 06b_entretien.sql       # Maison — Entretien & tâches
├── 06c_jardin.sql          # Maison — Jardin & autonomie
├── 06d_equipements.sql     # Maison — Équipements & artisans
├── 06e_energie.sql         # Maison — Énergie & subscriptions
├── 07_habitat.sql          # Module habitat
├── 08_jeux.sql             # Module jeux
├── 09_notifications.sql    # Notifications
├── 10_finances.sql         # Module finances
├── 11_utilitaires.sql      # Utilitaires divers
├── 12_triggers.sql         # Triggers PostgreSQL
├── 13_views.sql            # Vues matérialisées
├── 14_indexes.sql          # Indexes de performance
├── 15_rls_policies.sql     # Row Level Security (150+ tables ✅)
├── 16_seed_data.sql        # Données baseline (32 rows ✅)
├── 17_migrations_absorbees.sql  # Migrations SQL-first
├── 99_footer.sql           # Footer SQL
├── INIT_COMPLET.sql        # Généré automatiquement (5535 lignes, 151 tables)
└── migrations/
    ├── V001_*.sql           # RLS + sécurité (appliquée)
    └── V002_*.sql           # UUID conversion (SQL-first pipeline, N/A)
```

### Plan d'action (Sprint 2 ✅ Réalisé)

| Action | Détail | Priorité | Statut |
|--------|--------|----------|--------|
| **Éclater `06_maison.sql`** | Séparer en `06a_projets.sql`, `06b_entretien.sql`, `06c_jardin.sql`, `06d_equipements.sql`, `06e_energie.sql` | 🔴 Haute | ✅ **COMPLÉTÉ** — 5 fichiers créés, validés, 0 duplicates |
| **Ajouter indexes** | 6 indexes cibles : `ix_garden_items_derniere_action`, `ix_furniture_date_achat`, `idx_objets_maison_date_achat`, `ix_interventions_artisans_date`, `ix_articles_cellier_date_achat`, `ix_devis_date_validite` (partial) | 🔴 Haute | ✅ **COMPLÉTÉ** — Index appliqués + nommage unifié |
| **Auditer RLS** | Vérifier les 150 tables, ajouter coverage manquante | 🔴 Haute | ✅ **COMPLÉTÉ** — `jeux_bankroll_historique` ajouté à shared_tables |
| **Ajouter seed data** | Catalogue ingrédients (10), normes OMS (18), plantes baseline (4) | 🟢 Basse | ✅ **COMPLÉTÉ** — 32 rows idempotentes (ON CONFLICT DO NOTHING) |
| **Régénérer INIT_COMPLET.sql** | Après modifications + validation | 🟢 Basse | ✅ **COMPLÉTÉ** — 5535 lignes, 22 fichiers, sync validée |
| **Supprimer tables mortes** | `garanties`, `incidents_sav`, `contrats`, `preferences_home` | 🟡 Moyenne | ⏳ Sprint 3 — Nettoyage legacy |
| **Résoudre V002** | Nettoyer données VARCHAR user_id → UUID | 🟡 Moyenne | ⏳ Sprint 3 — Migration données | 
| **EXPLAIN ANALYZE** | Valider 10 queries critiques sur DB cible | 🟡 Moyenne | ⏳ En attente — Accès Supabase requis |

---

## 7. Tests

### Couverture actuelle

| Couche | Fichiers test | Tests | Qualité | Note |
|--------|---------------|-------|---------|------|
| **Backend API** | 55 | ~2000 | ✅ Solide | 8/10 |
| **Backend Services** | 50+ | ~1500 | ⚠️ Inégal | 7/10 |
| **Backend Core** | 20 | ~500 | ✅ Bon | 8/10 |
| **Backend Inter-modules** | 10+ | ~400 | ⚠️ | 7/10 |
| **Frontend Unit (Vitest)** | 77 | ~200 | ⚠️ Stubs | 4/10 |
| **Frontend E2E (Playwright)** | 21 | ~100 | ⚠️ Partiel | 5/10 |
| **Total** | **233+** | **~4932** | | **6.5/10** |

### Gaps critiques à combler

| Gap | Quoi tester | Effort estimé |
|-----|-------------|---------------|
| **WebSocket courses** | Connexion, messages, synchronisation multi-user | 4h |
| **PWA / Service Worker** | Installation, cache offline, sync en ligne | 4h |
| **Frontend composants clés** | Formulaire recette, planning hebdo, dashboard DnD | 8h |
| **E2E parcours complets** | Login → créer recette → planifier → courses → cocher articles | 8h |
| **Tests inter-modules E2E** | Jardin récolte → suggestion recette → courses | 4h |
| **Tests de charge API** | 100 req/s sur endpoints critiques (k6 ou locust) | 4h |
| **Contract tests OpenAPI** | Valider que l'API respecte les schemas (schemathesis) | 4h |
| **Mutation testing** | mutmut configuré mais pas utilisé | 2h |

---

## 8. Documentation

### Fichiers à garder, fusionner ou supprimer

| Fichier | Action | Raison |
|---------|--------|--------|
| `docs/INDEX.md` | ❌ Supprimer | Doublon de `README.md` |
| `docs/INTER_MODULES.md` + `INTER_MODULES_GUIDE.md` | 🔄 Fusionner en 1 seul | Contenu dupliqué |
| `docs/API_REFERENCE.md` + `API_SCHEMAS.md` | 🔄 Fusionner | Chevauchement |
| `docs/TESTING.md` + `TESTING_ADVANCED.md` | 🔄 Fusionner en 1 seul | Complémentaire |
| `docs/guides/IA_AVANCEE.md` | ✏️ Mettre à jour | Références OCR à retirer |
| `docs/guides/jeux/README.md` | ✏️ Mettre à jour | Références phases à retirer |
| `docs/guides/famille/README.md` | ✏️ Mettre à jour | Références phases à retirer |
| `docs/SERVICES_REFERENCE.md` | ✏️ Mettre à jour | Référence `obtenir_ocr_service` |
| `docs/AI_SERVICES.md` | ✏️ Mettre à jour | MultiModalAIService liste OCR |
| `PLANNING_IMPLEMENTATION.md` | ❌ Remplacer par ce document | Contenu phases obsolète |

### Documentation manquante à créer

| Fichier à créer | Contenu |
|-----------------|---------|
| `docs/CHANGELOG.md` | Historique des changements par version |
| `docs/DEPRECATED.md` | Features retirées et raisons (WhatsApp, OCR, partage, etc.) |
| `docs/ADMIN_MODE.md` | Guide du mode admin : triggers manuels, flags, monitoring |
| `docs/AUTOMATION_GUIDE.md` | Inventaire des 52 jobs, configuration, monitoring |

---

## 9. Interactions inter-modules

### Bridges existants (31) — État

```
Cuisine ↔ Inventaire     ✅ Stock → suggestions recettes, FIFO, budget
Cuisine ↔ Jules           ✅ Nutrition adaptée âge/allergies
Cuisine ↔ Jardin          ✅ Récolte → recettes de saison
Cuisine ↔ Météo/Saison    ✅ Contexte saisonnier → menus
Cuisine ↔ Budget          ✅ Courses → impact budget
Cuisine ↔ Garmin          ✅ Activité sportive → nutrition adultes
Cuisine ↔ Voyage          ✅ Départ → destockage frigo
Cuisine ↔ Batch Cooking   ✅ Batch → inventaire

Famille ↔ Météo           ✅ Météo → suggestions activités
Famille ↔ Weekend         ✅ Weekend → liste courses
Famille ↔ Budget/Jeux     ✅ Séparation budgets (volontaire)
Famille ↔ Anniversaires   ✅ Anniversaires → impact budget
Famille ↔ Documents       ✅ Expiration → alertes dashboard
Famille ↔ Garmin          ✅ Suivi activité

Maison ↔ Jardin           ✅ Jardin → entretien planifié
Maison ↔ Entretien        ✅ Produits entretien → courses
Maison ↔ Budget           ✅ Entretien → coûts
Maison ↔ Énergie          ✅ Charges → suivi énergie

Utilitaires ↔ Tout        ✅ Chat IA enrichi du contexte tous modules
Dashboard ↔ Actions       ✅ Actions rapides cross-module
```

### Interactions MANQUANTES à implémenter

| # | De → Vers | Description | Valeur |
|---|-----------|-------------|--------|
| **IM-1** | Entretien → Artisans | Tâche échouée → proposer artisan de la liste | ⭐⭐⭐ |
| **IM-2** | Inventaire péremption → Briefing matinal | Articles qui expirent aujourd'hui → dans le digest matin | ⭐⭐⭐ |
| **IM-3** | Anniversaire → Planning repas | Anniversaire proche → suggérer menu festif (gâteau, etc.) | ⭐⭐ |
| **IM-4** | Jardin récolte → Inventaire stock | Récolte déclarée → ajouter automatiquement au stock | ⭐⭐⭐ |
| **IM-5** | Énergie tarif HC/HP → Planning machines | Lancer la machine pendant heures creuses | ⭐⭐ |
| **IM-6** | Jules jalons → Timeline famille | Jalon atteint → événement dans le journal famille | ⭐⭐ |

---

## 10. IA — Intégrations existantes et opportunités

### Couverture IA actuelle (40 services)

```
Cuisine    : 6 services IA (suggestions, import, planning, courses, batch, nutrition)
Famille    : 7 services IA (Jules, weekend, achats, budget, résumé, soirée, recettes Jules)
Maison     : 6 services IA (entretien, fiches, projets, conseiller, contexte, diagnostics)
Jeux       : 3 services IA (paris, euromillions, loto)
Intégrations: 4 services IA (multimodal, facture OCR, météo impact, habitudes)
Dashboard  : 2 services IA (résumé famille, suggestions)
Rapports   : 1 service IA (bilan mensuel)
Utilitaires: 3 services IA (briefing, chat, inventaire)
IA avancée : 4 services IA (suggestions, planificateur, prévisions, résumé)
```

### Opportunités IA non exploitées

| # | Module | Cas d'usage IA | Impact |
|---|--------|----------------|--------|
| **IA-1** | **Jardin** | Détection maladies plantes via photo (Vision Mistral) | ⭐⭐⭐ |
| **IA-2** | **Jardin** | Calendrier semis/récolte personnalisé (région + météo) | ⭐⭐⭐ |
| **IA-3** | **Entretien** | Diagnostic panne équipement via description symptômes | ⭐⭐⭐ |
| **IA-4** | **Habitat/DVF** | Estimation prix bien + ROI rénovation | ⭐⭐ |
| **IA-5** | **Rapports** | Narration insights mensuel (pas juste données, analyse) | ⭐⭐⭐ |
| **IA-6** | **Planning famille** | Optimisation planning semaine (activités Jules + ménage + courses) | ⭐⭐⭐ |
| **IA-7** | **Artisans** | Estimation devis + comparaison via IA | ⭐⭐ |
| **IA-8** | **Garmin** | Recommandations santé personnalisées (sommeil, activité, nutrition) | ⭐⭐ |
| **IA-9** | **Anniversaires** | Idées cadeaux (basé historique achats + centres d'intérêt) | ⭐ |
| **IA-10** | **Énergie** | Prédiction consommation + conseils économies énergie | ⭐⭐⭐ |
| **IA-11** | **Documents** | Extraction automatique date expiration depuis photo document | ⭐⭐ |

---

## 11. Automatisations et jobs CRON

### Jobs existants (52) — Catégorisés

**Quotidiens (10) :**
- `rappels_famille` (07h00), `rappels_maison` (08h00), `push_quotidien` (09h00)
- `push_contextuel_soir` (18h00), `alertes_peremption_48h` (06h00)
- `peremptions_urgentes` (08h00), `alerte_stock_bas` (07h00)
- `garmin_sync_matinal` (06h00), `digest_ntfy` (09h00)
- `automations_runner` (toutes les 5 min)

**Hebdomadaires (8) :**
- `resume_hebdo` (lun 07h30), `entretien_saisonnier` (lun 06h00)
- `analyse_nutrition_hebdo` (dim 20h00), `score_bienetre` (dim 20h00)
- `rapport_jardin` (mer 20h00), `job_nutrition_adultes_weekly` (dim 20h15)
- `s16_resume_weekend_telegram` (ven 18h00), `s16_bilan_nutrition_telegram` (dim 20h30)

**Mensuels (4) :**
- `rapport_mensuel_budget` (1er 08h15), `rapport_maison_mensuel` (1er 09h30)
- `s16_rapport_famille_mensuel` (1er 09h00)
- `nettoyage_logs` (dim 04h00)

**Autres :**
- `digest_notifications_queue` (toutes les 2h)
- `sync_google_calendar` (23h00), `sync_calendrier_scolaire` (05h30)
- `sync_openfoodfacts` (dim 03h00), `archive_batches_expires` (02h00)

### Jobs manquants à ajouter

| Job | Déclencheur | Action |
|-----|-------------|--------|
| **Vérification santé services** | Toutes les 15 min | Ping DB, Mistral, Telegram → alerte si down |
| **Nettoyage cache périmé** | Quotidien 03h00 | Purger cache L3 fichier (fichiers > 7 jours) |
| **Backup BDD automatique** | Quotidien 02h00 | pg_dump → stockage |
| **Rapport anomalies IA** | Hebdomadaire | Résumé des erreurs circuit breaker + rate limit |
| **Mise à jour catalogue produits** | Hebdomadaire | Refresh OpenFoodFacts pour produits suivis |
| **Vérification SSL/domaine** | Mensuel | Alerter si certificat expire bientôt |
| **Comparateur prix abonnements** | Mensuel | Scraper/API → alerter si offre moins chère |

---

## 12. Telegram — Couverture et extensions

### Fonctions existantes (26)

Alertes bien couvertes : péremption, budget, entretien, nutrition, planning, courses, météo, weekend.

### Extensions Telegram à ajouter

| # | Commande/Action | Description |
|---|-----------------|-------------|
| **T-1** | `/planning` | Afficher le planning de la semaine en 1 message formaté |
| **T-2** | `/courses` | Envoyer la liste de courses avec cases à cocher inline |
| **T-3** | `/ajout [article]` | Ajouter un article à la liste de courses par commande texte |
| **T-4** | `/repas [soir/midi]` | Voir ou changer le repas du jour |
| **T-5** | `/jules` | Résumé santé/développement Jules du jour |
| **T-6** | `/maison` | Tâches d'entretien du jour |
| **T-7** | `/budget` | Résumé budget du mois en cours |
| **T-8** | `/meteo` | Météo du jour + impact sur les activités |
| **T-9** | Menu interactif | Bouton "Menu principal" avec sous-menus par module |
| **T-10** | Réponses rapides | Répondre "OK" à une suggestion pour valider un repas |
| **T-11** | `/aide` | Liste de toutes les commandes disponibles |

---

## 13. Mode Admin manuel (dev/test)

### Existant

- **Panel flottant** : `Ctrl+Shift+A` → bouton en bas à droite (non visible pour l'utilisateur final)
- **Triggers manuels** : 4 actions (score bien-être, points famille, automations, clear cache)
- **Feature flags** : 12 flags toggleables
- **52 jobs déclenchables** via `POST /admin/jobs/run`

### Améliorations à apporter

| # | Amélioration | Description |
|---|-------------|-------------|
| **A-1** | **Bouton "Lancer tous les jobs matin"** | 1 clic → exécute séquentiellement : garmin_sync, rappels, push, digest | 
| **A-2** | **Bouton "Simuler journée complète"** | Lance tous les jobs d'une journée en accéléré |
| **A-3** | **Logs temps réel dans le panel** | Stream SSE des logs d'exécution (pas besoin d'aller dans la console) |
| **A-4** | **Historique exécutions** | Tableau des 50 dernières exécutions manuelles avec statut/durée |
| **A-5** | **Bouton "Tester notification"** | Envoyer un message test Telegram/push/ntfy depuis le panel |
| **A-6** | **Bouton "Régénérer suggestions IA"** | Forcer le recalcul des suggestions (recettes, activités, weekend) |
| **A-7** | **Toggle "Mode démo"** | Remplir l'app avec des données fictives réalistes pour tester |
| **A-8** | **Dry-run mode** | Exécuter un job sans effets de bord (preview du résultat) |
| **A-9** | **Export état complet** | Dump JSON de tout l'état (pour debug/support) |
| **A-10** | **Visibilité** | Le panel DOIT rester invisible pour l'utilisateur (conditionné par `ENVIRONMENT=development` ou `admin.mode_test` flag) |

---

## 14. UI/UX — État actuel et améliorations

### État actuel

| Aspect | État | Détails |
|--------|------|---------|
| **Design System** | ✅ Bon | shadcn/ui + Tailwind v4, cohérent |
| **Dark Mode** | ✅ Complet | next-themes, CSS variables |
| **Responsive** | ✅ Bon | Mobile-first, bottom nav, sidebar collapsible |
| **Accessibilité** | ⚠️ Partiel | aria-labels OK, `alt` images manquants |
| **Animations** | ⚠️ Basique | Framer Motion présent mais sous-utilisé |
| **Loading states** | ✅ Bon | Skeleton components |
| **Empty states** | ✅ Bon | `etat-vide.tsx` réutilisable |
| **Error handling UI** | ⚠️ Basique | Error boundary OK, pas de retry/toast granulaire |
| **Micro-interactions** | ❌ Manquant | Pas de feedback tactile, transitions entre pages basiques |
| **Illustrations** | ❌ Manquant | Pas d'illustrations/icônes custom |

### Plan d'amélioration UI/UX

| # | Amélioration | Description | Impact visuel |
|---|-------------|-------------|---------------|
| **UI-1** | **Transitions de page** | `framer-motion` AnimatePresence entre les routes | ⭐⭐⭐ |
| **UI-2** | **Micro-interactions** | Hover effects, press feedback, swipe gestures sur les cartes | ⭐⭐⭐ |
| **UI-3** | **Onboarding amélioré** | Tour guidé avec spotlight sur les fonctionnalités clés (driver.js) | ⭐⭐ |
| **UI-4** | **Dashboard : widgets animés** | Compteurs animés au chargement, sparklines fluides | ⭐⭐ |
| **UI-5** | **Graphiques : thème unifié** | Palette couleurs cohérente sur Recharts/D3/SVG, transitions fluides | ⭐⭐⭐ |
| **UI-6** | **Plan 3D maison : enrichir** | Ajouter textures, ombres, selection room → drawer détails | ⭐⭐ |
| **UI-7** | **Jardin : vue isométrique** | Passer de SVG plat à vue isométrique 2.5D (comme un mini-jeu) | ⭐⭐⭐ |
| **UI-8** | **Timeline famille** | Timeline verticale interactive avec zoom, filtres, jalons Jules | ⭐⭐ |
| **UI-9** | **Calendrier repas mosaïque** | Vue hebdo avec vignettes photos des recettes | ⭐⭐⭐ |
| **UI-10** | **Skeleton → Content** | Animation de révélation (fade-in staggered quand les données arrivent) | ⭐⭐ |
| **UI-11** | **Palette couleurs par module** | Chaque module a sa couleur accent (cuisine=vert, famille=bleu, etc.) | ⭐⭐⭐ |
| **UI-12** | **Notifications toast améliorées** | Toast avec progress bar, undo intégré, actions | ⭐⭐ |
| **UI-13** | **Mode tablette optimisé** | Layout 2 colonnes sur tablette, widgets adaptés | ⭐⭐ |
| **UI-14** | **Graphiques interactifs** | Tooltip riches, zoom, drill-down sur tous les graphiques | ⭐⭐ |
| **UI-15** | **Sankey flux budget** | Visualisation flux financiers animée (d'où vient l'argent, où il va) | ⭐⭐⭐ |

### Visualisation 2D/3D — État et plan

| Composant existant | Technologie | Amélioration possible |
|--------------------|-------------|----------------------|
| Plan 3D maison | Three.js + R3F | Textures réalistes, meubles 3D, navigation fluide |
| Jardin interactif | SVG React | Vue isométrique 2.5D, animations pousse plantes |
| Heatmap nutrition | CSS Grid custom | D3 heatmap avec transitions |
| Sankey budget | SVG custom | D3 Sankey avec animation flux |
| Treemap budget | Custom | Recharts Treemap avec zoom drill-down |
| Treemap inventaire | Custom | Recharts Treemap animé |
| Radar nutrition | Recharts | Overlay comparaison temporelle |
| Radar compétences Jules | Recharts | Animation progression, benchmark âge |
| Graphe réseau modules (admin) | D3 force | Ajouter filtres, détails on-hover |

---

## 15. Simplification des flux utilisateur

### Principe : l'utilisateur final ne devrait JAMAIS avoir plus de 3 clics pour une action courante

| Flux | Clics actuels | Cible | Comment simplifier |
|------|---------------|-------|-------------------|
| Voir le planning de la semaine | 2 | 1 | Widget dashboard dédié |
| Ajouter un article aux courses | 3-4 | 1-2 | FAB + commande vocale + suggestion auto |
| Cocher un article acheté | 2 | 1 | Swipe-to-check sur mobile |
| Voir les recettes du jour | 2 | 1 | Card sur le dashboard |
| Lancer le batch cooking | 3-4 | 2 | Bouton direct depuis le planning |
| Voir les tâches ménage du jour | 3 | 1 | Widget dashboard avec toggle |
| Déclarer une récolte jardin | 4+ | 2 | Bouton rapide sur la fiche plante |
| Consulter le budget restant | 2 | 0 | Badge permanent dans la sidebar |
| Ajouter une note rapide | 3 | 1 | FAB + input inline |
| Voir les documents expirant | 3 | 1 | Badge notification + widget dashboard |

### Actions rapides recommandées

- **FAB (Floating Action Button)** : Déjà présent (`fab-actions-rapides.tsx`), enrichir avec les 5 actions les plus fréquentes
- **Commandes vocales** : Hooks existants (`utiliser-reconnaissance-vocale.ts`), connecter aux actions fréquentes
- **Suggestions proactives** : Bandeau existant (`bandeau-suggestion-proactive.tsx`), alimenter par IA contextuelle
- **Swipe gestures** : Hook existant (`swipeable-item.tsx`), appliquer sur listes courses/tâches

---

## 16. Fichiers fourre-tout à éclater

| Fichier actuel | Problème | Action |
|----------------|----------|--------|
| `src/api/routes/fonctionnalites_avancees.py` | Mix de 24 endpoints `/phase9/` et `/phasee/` sans cohérence | Éclater par domaine (IA avancée, prédictions, pilotage) ou fusionner dans les routes existantes |
| `src/api/routes/admin_shared.py` | 1000+ lignes — schemas, constantes, helpers, jobs config | Séparer `admin_schemas.py`, `admin_constants.py`, `admin_helpers.py` |
| `sql/06_maison.sql` | 43 tables dans 1 fichier | Éclater en 5 sous-fichiers (projets, entretien, jardin, équipements, énergie) |
| `src/services/innovations/service.py` | "Innovations" pas clair, mélange features expérimentales | Renommer en `src/services/experimental/` ou intégrer dans les modules concernés |
| `src/services/innovations/types.py` | Types "innovations" isolés | Déplacer dans `src/api/schemas/` avec les autres types |
| `PLANNING_IMPLEMENTATION.md` | Phases obsolètes, remplacé par cet audit | Remplacer par ce document |

---

## 17. Axes d'innovation

### Innovations proposées (au-delà de ce qui est demandé)

| # | Innovation | Description | Effort |
|---|-----------|-------------|--------|
| **INNO-1** | **Briefing matinal Telegram** | 1 message à 7h : météo + repas du jour + tâches + Jules + péremptions | 4h (bridge à enrichir) |
| **INNO-2** | **Mode "Soirée"** | Activation manuelle → éteint les notifs, suggère un film/activité, prépare le planning lendemain | 8h |
| **INNO-3** | **Score maison global** | Note composite : entretien à jour, énergie, jardin, rangement → évolution dans le temps | 4h |
| **INNO-4** | **Comparaison semaine/semaine** | Dashboard : cette semaine vs la semaine dernière (repas, budget, activités, énergie) | 6h |
| **INNO-5** | **"Qu'est-ce qu'on mange ?"** | 1 bouton → IA propose 3 options basées sur : stock frigo, météo, goûts, derniers repas, Jules | 4h |
| **INNO-6** | **Planning familial unifié** | Vue calendrier unique : repas + activités + ménage + jardin + RDV | 8h |
| **INNO-7** | **Photo → Inventaire** | Prendre une photo du frigo → IA identifie les produits et met à jour l'inventaire | 6h (Vision Mistral) |
| **INNO-8** | **Historique prix produits** | Suivi prix automatique (scraping API) des produits habituels → graphique tendance | 8h |
| **INNO-9** | **Backup export familial** | 1 clic → export complet (recettes, planning, budget, documents) en JSON/ZIP | 4h |
| **INNO-10** | **Widget tablette cuisine** | Écran permanent tablette : recette en cours + timer + liste courses | 4h (page dédiée) |
| **INNO-11** | **Bilan de fin de mois** | Rapport IA narratif : "Ce mois-ci vous avez..." (budget, repas, Jules, maison) | 4h |
| **INNO-12** | **Mode vacances** | Activation → pause des rappels, checklist départ, destockage frigo auto | 6h |
| **INNO-13** | **Routines intelligentes** | IA apprend les habitudes → propose d'automatiser les routines récurrentes | 8h |

| **INNO-15** | **Multi-device sync indicator** | Pastille "en cours d'édition sur un autre appareil" (courses, planning) | 4h |

---

## 18. Plan d'exécution priorisé

### Sprint 1 — Nettoyage (5-7 jours)

> Objectif : code propre, sans dead code ni références legacy

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 1.1 | Supprimer fichiers rejetés (partage, OCR, cuisine_ia) | 1h | 🔴 |
| 1.2 | Nettoyer alias WhatsApp dans le code | 1h | 🔴 |
| 1.3 | Supprimer tables SQL mortes (garanties, incidents_sav, contrats, preferences_home) | 1h | 🔴 |
| 1.4 | Nettoyer 150+ commentaires Phase/Sprint → descriptions fonctionnelles | 4h | 🔴 |
| 1.5 | Renommer `test_bridges_phase2.py` → `test_bridges_inter_modules.py` | 15min | 🔴 |
| 1.6 | Renommer `fonctionnalites_avancees.py` → éclater dans les routes par domaine | 2h | 🔴 |
| 1.7 | Renommer `innovations/` → `experimental/` ou intégrer | 1h | 🔴 |
| 1.8 | Éclater `admin_shared.py` en 3 fichiers | 1h | 🟡 |
| 1.9 | Supprimer `PLANNING_IMPLEMENTATION.md` et `docs/INDEX.md` | 15min | 🟡 |
| 1.10 | Fusionner docs doublons (INTER_MODULES, API_*, TESTING) | 2h | 🟡 |
| 1.11 | Mettre à jour docs avec références OCR/Phase | 1h | 🟡 |

### Sprint 2 — SQL et données (3-5 jours)

> Objectif : base solide, performante, sécurisée

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 2.1 | Éclater `06_maison.sql` en 5 sous-fichiers | 2h | 🔴 |
| 2.2 | Ajouter indexes sur champs requêtés (10+ indexes) | 2h | 🔴 |
| 2.3 | Audit RLS complet (150 tables) | 4h | 🔴 |
| 2.4 | Résoudre migration V002 (UUID) | 2h | 🟡 |
| 2.5 | Régénérer `INIT_COMPLET.sql` | 30min | 🟡 |
| 2.6 | Créer seed data (ingrédients, OMS, plantes) | 4h | 🟢 |

### Sprint 3 — Tests (5-7 jours)

> Objectif : couverture confiance sur les flux critiques

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 3.1 | Tests WebSocket courses (connexion, sync, multi-user) | 4h | 🔴 |
| 3.2 | Tests E2E parcours complet (login → recette → planning → courses) | 8h | 🔴 |
| 3.3 | Tests frontend composants clés (formulaire recette, planning, dashboard) | 8h | 🟡 |
| 3.4 | Tests inter-modules E2E (jardin → recette → courses) | 4h | 🟡 |
| 3.5 | Tests de charge API (k6 sur 5 endpoints critiques) | 4h | 🟡 |
| 3.6 | Contract tests OpenAPI (schemathesis) | 4h | 🟢 |
| 3.7 | PWA / Service Worker tests | 4h | 🟢 |

### Sprint 4 — Inter-modules et IA (5-7 jours)

> Objectif : modules connectés intelligemment

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 4.1 | IM-2 : Péremption inventaire → briefing matinal | 2h | 🔴 |
| 4.2 | IM-1 : Entretien échoué → proposer artisan | 3h | 🔴 |
| 4.3 | IM-4 : Récolte jardin → stock inventaire automatique | 3h | 🔴 |
| 4.4 | IA-1 : Photo plante → diagnostic maladie (Vision Mistral) | 4h | 🟡 |
| 4.6 | IA-3 : Diagnostic panne équipement via IA | 3h | 🟡 |
| 4.7 | IA-6 : Rapport mensuel narratif IA | 3h | 🟡 |
| 4.8 | IA-11 : Prédiction consommation énergie | 4h | 🟢 |
| 4.9 | Consolider 31 bridges → max 15-20 fichiers | 4h | 🟡 |

### Sprint 5 — Automatisations et Telegram (3-5 jours)

> Objectif : tout marche tout seul, Telegram est le hub mobile

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 5.1 | INNO-1 : Briefing matinal Telegram enrichi | 4h | 🔴 |
| 5.2 | T-1 à T-8 : Commandes Telegram interactives | 6h | 🔴 |
| 5.3 | T-9 : Menu principal avec sous-menus | 2h | 🟡 |
| 5.4 | Jobs manquants (santé services, nettoyage cache, backup) | 4h | 🟡 |
| 5.5 | Implémenter envoi email (rapports mensuels en PDF) | 4h | 🟡 |
| 5.6 | T-10 : Réponses rapides ("OK" pour valider un repas) | 2h | 🟢 |

### Sprint 6 — Admin manuel (2-3 jours)

> Objectif : pouvoir tout tester en 1 clic, invisible pour l'utilisateur

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 6.1 | A-1 : Bouton "tous les jobs matin" | 2h | 🔴 |
| 6.2 | A-3 : Logs temps réel SSE dans le panel | 4h | 🔴 |
| 6.3 | A-4 : Historique exécutions manuelles | 2h | 🟡 |
| 6.4 | A-5 : Bouton test notification (Telegram/push/ntfy) | 1h | 🟡 |
| 6.5 | A-6 : Bouton régénérer suggestions IA | 1h | 🟡 |
| 6.6 | A-7 : Toggle mode démo | 2h | 🟢 |
| 6.7 | A-8 : Dry-run mode pour jobs | 2h | 🟢 |
| 6.8 | A-10 : Conditionner visibilité panel (env=dev uniquement) | 30min | 🔴 |

### Sprint 7 — UI/UX Polish (7-10 jours)

> Objectif : interface moderne, fluide, plaisante à utiliser

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 7.1 | UI-11 : Palette couleurs par module | 2h | 🔴 |
| 7.2 | UI-1 : Transitions de page (Framer Motion) | 4h | 🔴 |
| 7.3 | UI-2 : Micro-interactions (hover, press, swipe) | 6h | 🔴 |
| 7.4 | UI-5 : Thème unifié graphiques (palette Recharts/D3) | 3h | 🟡 |
| 7.5 | UI-9 : Calendrier repas mosaïque avec vignettes | 6h | 🟡 |
| 7.6 | UI-10 : Animation skeleton → content (fade-in staggered) | 2h | 🟡 |
| 7.7 | UI-12 : Toast améliorés (progress bar, undo, actions) | 3h | 🟡 |
| 7.8 | UI-7 : Jardin vue isométrique 2.5D | 8h | 🟢 |
| 7.9 | UI-6 : Plan 3D maison enrichi (textures, meubles) | 8h | 🟢 |
| 7.10 | UI-13 : Mode tablette optimisé | 4h | 🟢 |
| 7.11 | UI-14 : Graphiques interactifs (tooltip, zoom, drill-down) | 4h | 🟢 |
| 7.12 | Corriger `alt` manquants sur images | 1h | 🟡 |

### Sprint 8 — Flux utilisateur et innovations (5-7 jours)

> Objectif : expérience simple et proactive

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 8.1 | INNO-5 : Bouton "Qu'est-ce qu'on mange ?" | 4h | 🔴 |
| 8.2 | INNO-10 : Widget tablette cuisine (recette + timer + courses) | 4h | 🔴 |
| 8.3 | Enrichir le FAB avec les 5 actions les plus fréquentes | 2h | 🔴 |
| 8.4 | INNO-9 : Export backup familial (JSON/ZIP) | 4h | 🟡 |
| 8.5 | INNO-11 : Bilan fin de mois IA narratif | 4h | 🟡 |
| 8.6 | INNO-12 : Mode vacances (pause rappels, checklist départ) | 6h | 🟡 |
| 8.7 | INNO-6 : Planning familial unifié (calendrier unique) | 8h | 🟢 |
| 8.8 | INNO-7 : Photo frigo → inventaire IA (Vision) | 6h | 🟢 |

### Sprint 9 — Documentation finale (2-3 jours)

> Objectif : documentation complète et à jour

| # | Tâche | Effort | Priorité |
|---|-------|--------|----------|
| 9.1 | Créer `docs/CHANGELOG.md` | 2h | 🔴 |
| 9.2 | Créer `docs/DEPRECATED.md` | 1h | 🔴 |
| 9.3 | Créer `docs/ADMIN_MODE.md` (guide admin/dev) | 2h | 🟡 |
| 9.4 | Créer `docs/AUTOMATION_GUIDE.md` (52 jobs documentés) | 2h | 🟡 |
| 9.5 | Mettre à jour `copilot-instructions.md` | 1h | 🟡 |
| 9.6 | Mettre à jour `README.md` | 1h | 🟡 |
| 9.7 | Ajouter exemples Swagger sur tous les schemas | 4h | 🟢 |
| 9.8 | Ajouter `max_length` sur les champs string des schemas | 2h | 🟢 |

---

## Récapitulatif effort total estimé

| Sprint | Durée | Focus |
|--------|-------|-------|
| **Sprint 1** — Nettoyage | 5-7 jours | Dead code, legacy, commentaires, fichiers fourre-tout |
| **Sprint 2** — SQL | 3-5 jours | Base de données, indexes, RLS, seed |
| **Sprint 3** — Tests | 5-7 jours | WebSocket, E2E, composants, charge |
| **Sprint 4** — Inter-modules & IA | 5-7 jours | Bridges manquants, nouvelles intégrations IA |
| **Sprint 5** — Automatisations | 3-5 jours | Telegram enrichi, jobs manquants, email |
| **Sprint 6** — Admin | 2-3 jours | Panel enrichi, triggers, logs temps réel |
| **Sprint 7** — UI/UX | 7-10 jours | Animations, palette, graphiques, 3D |
| **Sprint 8** — Flux & Innovation | 5-7 jours | Simplification UX, features innovantes |
| **Sprint 9** — Documentation | 2-3 jours | CHANGELOG, guides, Swagger |
| | | |
| **Total estimé** | **~40-55 jours** | **En séquentiel. Parallélisable sur certains sprints.** |

---

> **Note finale** : L'application est solide architecturalement (9/10 backend, 8.5/10 frontend). Les principaux axes d'amélioration sont le polish UI (animations, micro-interactions), la couverture tests frontend, le nettoyage legacy, et l'exploitation maximale de l'IA et des interactions inter-modules. Le flux utilisateur doit rester simple : maximum 2-3 clics pour toute action courante, avec Telegram comme hub mobile et le dashboard comme hub desktop.
