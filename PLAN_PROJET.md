# Plan Projet — Assistant Matanne

> **Date** : 2 avril 2026
> **Statut** : Audit complet + plan d'amélioration
> **Règle** : Ce document est le plan de référence. Rien ne doit être implémenté sans validation.

---

## Table des matières

1. [Inventaire de l'existant](#1-inventaire-de-lexistant)
2. [Bugs et problèmes détectés](#2-bugs-et-problèmes-détectés)
3. [Code à supprimer](#3-code-à-supprimer)
4. [Nettoyage et réorganisation](#4-nettoyage-et-réorganisation)
5. [SQL — Consolidation](#5-sql--consolidation)
6. [Tests — État et plan](#6-tests--état-et-plan)
7. [Documentation — État et plan](#7-documentation--état-et-plan)
8. [Interactions inter-modules](#8-interactions-inter-modules)
9. [IA — Nouvelles intégrations](#9-ia--nouvelles-intégrations)
10. [Jobs automatiques et CRON](#10-jobs-automatiques-et-cron)
11. [Notifications — WhatsApp, Email, Push](#11-notifications--whatsapp-email-push)
12. [Mode Admin manuel](#12-mode-admin-manuel)
13. [UI/UX — Améliorations visuelles](#13-uiux--améliorations-visuelles)
14. [Simplification du flux utilisateur](#14-simplification-du-flux-utilisateur)
15. [Axes d'innovation](#15-axes-dinnovation)
16. [Plan d'exécution par priorité](#16-plan-dexécution-par-priorité)

---

## 1. Inventaire de l'existant

### Backend Python (FastAPI)

| Catégorie | Nombre | Détail |
|-----------|--------|--------|
| Routes API | 42 fichiers | 20 domaines métier + admin + bridges + IA |
| Schémas Pydantic | 24 fichiers | Validation/sérialisation par domaine |
| Modèles ORM | 30 fichiers | ~150 tables SQLAlchemy 2.0 |
| Services | 138+ factories | 16 packages de services |
| Core packages | 14 sous-packages | ai, caching, config, db, decorators, etc. |
| Jobs CRON | 55+ jobs | APScheduler, planification 24h |
| Tests Python | 4932 collectés | 493 derniers échoués maintenant OK |

### Frontend Next.js

| Catégorie | Nombre | Détail |
|-----------|--------|--------|
| Pages (routes) | ~121 | 15 modules principaux |
| Composants | 130+ | UI (29 shadcn) + layout (22) + métier |
| Clients API | 31 modules | Un par domaine |
| Hooks custom | 19 | Auth, API, WebSocket, CRUD, etc. |
| Stores Zustand | 4 | auth, ui, notifications, maison |
| Types TS | 15 fichiers | Interfaces par domaine |
| Tests frontend | 31 fichiers | Vitest + Playwright |

### Modules fonctionnels

| Module | Backend | Frontend | IA | CRON | Status |
|--------|---------|----------|----|------|--------|
| **Cuisine** | Routes + services | 15 pages | Suggestions, planning IA | 4 jobs | Complet |
| **Famille** | Routes + 25 services | 16 pages | Résumé, prévision budget | 8 jobs | Complet |
| **Maison** | Routes + 15 services | 15 pages | Diagnostics, fiches tâche | 6 jobs | Complet |
| **Jeux** | Routes + 15 services | 5 pages | Prédictions, backtest | 3 jobs | Complet |
| **Outils** | Routes + 12 services | 14 pages | Chat IA, briefing | 2 jobs | Complet |
| **Planning** | Routes + 5 services | 2 pages | Planification semaine | 2 jobs | Complet |
| **Habitat** | Routes + 5 services | 1 page | Déco IA, plans IA | 1 job | Complet |
| **Admin** | Routes admin | 13 pages | — | — | Complet |
| **Dashboard** | Routes + 8 services | 1 page | Score bien-être | 3 jobs | Complet |

---

## 2. Bugs et problèmes détectés

### 2.1 Fichiers fourre-tout

| Fichier | Lignes | Problème |
|---------|--------|----------|
| `src/services/innovations/service.py` | ~999 | **60+ méthodes** mélangées : suggestions repas, énergie, analytics, WhatsApp, batch cooking, comparateur prix, mode vacances. Impossible à maintenir. |
| `src/api/routes/admin.py` | ~800 | 65+ endpoints : santé, config, logs, backups, métriques, users. Trop de responsabilités. |
| `src/api/routes/dashboard.py` | ~1000 | Dashboard + gamification + stats famille dans un seul fichier. |

**Action** : Éclater chaque fichier en services/routes focalisés (voir section 4).

### 2.2 Code legacy / rétrocompatibilité

| Pattern | Occurrences | Fichiers concernés |
|---------|-------------|-------------------|
| Champs legacy dans modèles | 8-10 | `models/planning.py`, `models/jeux.py` — champs marqués "legacy, remplacé par..." |
| Validateurs legacy | 5-7 | `schemas/phase_b.py` — `_legacy_single_article` |
| `TypeNotificationLegacy` | 3 | `store-notifications.ts` — alias rétrocompat |
| Shims compatibilité | 20+ | `jeux/euromillions_ia.py`, `jeux/bankroll_manager.py` — `_to_legacy_grille()` |
| `cleanup_legacy_cache()` | 2 | `core/caching/file.py` — nettoyage pickle |
| Ancien format planning | 3 | `cuisine/planning/service.py` — support "jour_0" vs "jour_0_midi/soir" |
| Fonctions deprecated | 5 | `core/exceptions.py` — marquées Deprecated mais toujours présentes |
| Pagination backward | 3 | `api/pagination.py` — direction "backward" |
| Ré-exports rétrocompat | 4 | `integrations/images/generator.py` — "backward compatibility" |

**Action** : Supprimer tout le code legacy en une passe (voir section 3).

### 2.3 Références phase/sprint dans le code

**150+ commentaires** contenant des noms de phases ou sprints :
- Docstrings : `"Phase 9 et 10 du planning"`, `"S21 IN1"`, `"P9-01"`
- Cache keys : `"phase_e_score_famille_hebdo"`
- Section headers : `"# PHASE 8 — Connexions inter-modules"`
- Décorateurs : `@chronometre("innovations.p9.mange_ce_soir")`
- Classes de test : `TestEventsPhaseB`, `TestSprintE2E`

**Action** : Renommer partout avec des noms fonctionnels (voir section 4.2).

### 2.4 Fichiers nommés avec phase/sprint

| Fichier actuel | Nouveau nom proposé |
|----------------|-------------------|
| `src/api/routes/ia_sprint13.py` | `ia_modules.py` |
| `src/api/schemas/sprint13_ai.py` | `ia_modules.py` |
| `src/services/core/cron_phase_b.py` | `cron_bridges.py` |
| `src/api/routes/notifications_sprint_e.py` | `notifications_enrichies.py` |
| `src/services/core/notifications/notifications_enrichis_sprint_e.py` | `notifications_enrichies.py` |
| `frontend/src/crochets/utiliser-sprint13-ia.ts` | `utiliser-ia-modules.ts` |
| `frontend/src/bibliotheque/api/ia-sprint13.ts` | `ia-modules.ts` |
| `tests/test_sprint_12_bridges.py` | `test_bridges_inter_modules.py` |
| `tests/services/test_sprint13_simple.py` | `test_ia_modules.py` |
| `tests/services/test_sprint13_new_ai_services.py` | `test_ia_services.py` |
| `tests/inter_modules/test_bridges_sprint6.py` | `test_bridges_base.py` |
| `tests/inter_modules/test_bridges_sprint11.py` | `test_bridges_avances.py` |
| `tests/services/famille/test_sprint14_events.py` | `test_famille_events.py` |
| `tests/e2e/test_sprint13_integration.py` | `test_ia_integration.py` |
| `tests/api/test_routes_ia_sprint13.py` | `test_routes_ia_modules.py` |

### 2.5 Stubs et code mort

| Fichier | Problème |
|---------|----------|
| `frontend/src/composants/maison/drawer-garantie.tsx` | Stub 2 lignes : `"fonctionnalité non retenue"` |
| `src/services/innovations/service.py` | Méthodes qui appellent des helpers privés inexistants (`_recettes_rapides`, `_patterns_recettes`, etc.) |
| `data/exports/` | 152 fichiers ZIP d'exports RGPD de test |

---

## 3. Code à supprimer / transformer

### 3.1 Module RGPD → Backup personnel

Supprimer le label et la logique RGPD, mais **conserver la possibilité de faire un backup** de ses données personnelles.

| Type | Action |
|------|--------|
| Route | Supprimer `src/api/routes/rgpd.py` — remplacer par un endpoint simplifié `POST /api/v1/export/backup` dans `export.py` |
| Schéma | Supprimer `src/api/schemas/rgpd.py` — un simple `BackupResponse(url: str, date: datetime)` dans `export.py` suffit |
| Service | Refactorer `src/services/core/utilisateur/rgpd.py` → extraire la logique d'export en ZIP dans un `backup_personnel.py`, supprimer tout le reste (droit à l'oubli, data summary, conformité) |
| Client API | Supprimer `frontend/src/bibliotheque/api/rgpd.ts` — ajouter `exporterBackup()` dans `export.ts` |
| Page frontend | Remplacer la section "Export RGPD" dans `parametres/onglet-donnees.tsx` par un simple bouton "Télécharger mon backup" sans mention RGPD |
| Tests | Supprimer `tests/api/test_rgpd.py` — ajouter des tests backup dans `test_routes_export.py` |
| Données | Supprimer les 152 fichiers `data/exports/export_rgpd_*.zip` (données de test) |
| Docs | Retirer les mentions RGPD/conformité dans `docs/user-guide/FAQ.md`, garder la mention backup |
| Enregistrement | Retirer `rgpd_router` de `src/api/main.py` et `routes/__init__.py` |

### 3.2 Module Garanties → Vérification garantie en cas de panne

Supprimer le module complet de gestion des garanties (CRUD, alertes, incidents SAV) mais **garder une fonctionnalité simple** : pouvoir vérifier si un équipement est encore sous garantie quand il tombe en panne.

| Type | Action |
|------|--------|
| SQL | Simplifier : garder une colonne `date_achat` et `duree_garantie_mois` sur la table `equipements` (pas de table `garanties` séparée ni `incidents_sav`) |
| Modèle ORM | Ajouter les champs `date_achat` et `duree_garantie_mois` sur le modèle Equipement existant, supprimer le modèle Garantie séparé |
| Frontend | Remplacer `drawer-garantie.tsx` (stub) par un badge "Sous garantie ✅ / Hors garantie ❌" sur la fiche équipement, calculé à partir de `date_achat + duree_garantie_mois` |
| Routes API | Supprimer les endpoints CRUD `/maison/garanties` — la garantie est juste un champ de l'équipement |
| Schémas | Supprimer `AlerteGarantieResponse`, `GarantieCreate`, etc. — enrichir `EquipementResponse` avec `sous_garantie: bool` (calculé) |
| CRON | Supprimer `controle_contrats_garanties`, `check_garanties_expirant` — pas d'alertes automatiques, juste une consultation à la demande |
| Docs | Mettre à jour : "La garantie est visible sur la fiche équipement, pas de gestion dédiée" |

### 3.3 Module Contrats → Comparateur d'abonnements

Ne pas supprimer les contrats mais **recentrer** sur un comparateur d'abonnements pour les dépenses récurrentes du foyer. L'objectif : pouvoir comparer et changer ses abonnements (eau, électricité, gaz, assurances, chaudière, téléphone, internet).

| Type | Action |
|------|--------|
| Modèle | Renommer `contrats_artisans.py` → `abonnements.py`. Simplifier le modèle : `Abonnement(type, fournisseur, prix_mensuel, date_debut, date_fin_engagement, notes)`. Types : `eau`, `electricite`, `gaz`, `assurance_habitation`, `assurance_auto`, `chaudiere`, `telephone`, `internet` |
| Routes API | Remplacer `/maison/contrats` → `/maison/abonnements` : CRUD simple + endpoint `GET /maison/abonnements/resume` (coût total mensuel par type) |
| Frontend | Page dédiée `maison/abonnements/page.tsx` : tableau récapitulatif de tous les abonnements avec coût total, date de fin d'engagement, possibilité de noter un meilleur prix trouvé |
| Comparateur | Ajouter un champ `meilleur_prix_trouve` et `fournisseur_alternatif` sur chaque abonnement pour noter les alternatives repérées manuellement |
| IA (futur) | Potentiel : l'IA peut analyser les abonnements et suggérer des alternatives quand les engagements se terminent |
| CRON | Remplacer `sync_contrats_alertes` par un rappel simple : "Engagement {type} se termine dans 30 jours — c'est le moment de comparer" |
| SQL | Simplifier les tables : une seule table `abonnements` remplaçant `contrats`, `contrats_maison`, `factures`. Garder `comparatifs` renommé en `alternatives_abonnement` |
| Docs | Mettre à jour la doc maison : section "Abonnements et comparateur" |

### 3.4 Code legacy à purger

| Catégorie | Action |
|-----------|--------|
| Champs "legacy" dans les modèles ORM | Supprimer les colonnes et migrer proprement |
| `_legacy_single_article` validator | Supprimer le validateur et l'ancien format |
| `TypeNotificationLegacy` mapping | Supprimer l'alias, utiliser les types modernes |
| `_to_legacy_grille()` et shims jeux | Supprimer, adapter les callers |
| `cleanup_legacy_cache()` | Supprimer le support pickle, garder JSON only |
| Support ancien format "jour_0" planning | Supprimer, garder uniquement "jour_0_midi/soir" |
| Fonctions deprecated dans `core/exceptions.py` | Supprimer, vérifier qu'elles ne sont plus appelées |
| Ré-exports rétrocompat images | Supprimer, mettre à jour les imports |

### 3.5 Fichiers de documentation obsolètes

| Fichier | Raison |
|---------|--------|
| `docs/SPRINT13_COMPLETION_SUMMARY.md` | Historique de sprint, pas utile |
| `docs/SPRINT13_INTEGRATION_GUIDE.md` | Idem |
| `docs/SPRINT13_QUICKSTART.md` | Idem |
| `docs/CHANGELOG_MODULES.md` | Historique de changements par sprint |
| `scripts/_archive/` | Scripts archivés (legacy) |

### 3.6 Fichier innovations — renommer et éclater

Le fichier `src/services/innovations/service.py` est un fourre-tout de ~999 lignes. Ce n'est pas un nom clair.

**Éclater en :**

| Nouveau service | Méthodes à déplacer |
|----------------|---------------------|
| `src/services/cuisine/suggestions_repas.py` | `mange_ce_soir()`, `recettes_rapides()`, `patterns_recettes()` |
| `src/services/maison/energie_ia.py` | `anomalies_energie()`, `eco_scoring()`, `puissance_linky()` |
| `src/services/famille/analytics_famille.py` | `score_famille_hebdo()`, `journal_familial()`, `rapport_mensuel()` |
| `src/services/integrations/comparateur_prix.py` | `comparateur_prix()`, `veille_prix()` |
| `src/services/ia/assistant_mode.py` | `mode_pilote()`, `mode_vacances()`, `coach_routines()` |

Puis **supprimer** `src/services/innovations/` entièrement.

---

## 4. Nettoyage et réorganisation

### 4.1 Renommage des fichiers (sprint/phase → fonctionnel)

Voir le tableau complet en section 2.4. Chaque fichier doit être renommé, les imports mis à jour, les tests renommés en cohérence.

### 4.2 Nettoyage des commentaires

**Règle** : Aucun commentaire ne doit contenir le nom d'une phase, d'un sprint, ou d'un code interne (`P9-01`, `S21 IN1`, etc.).

Actions :
- Supprimer tous les commentaires de section type `# PHASE 8 — ...` ou `# Sprint D — ...`
- Remplacer par des commentaires fonctionnels : `# Connexions inter-modules` au lieu de `# Phase 8`
- Renommer les cache keys : `"phase_e_score_famille_hebdo"` → `"score_famille_hebdo"`
- Renommer les décorateurs de métriques : `"innovations.p9.mange_ce_soir"` → `"cuisine.mange_ce_soir"`
- Renommer les classes de test : `TestEventsPhaseB` → `TestEventsBridges`

### 4.3 Éclater les fichiers trop gros

| Fichier actuel | Découpage proposé |
|----------------|-------------------|
| `src/api/routes/admin.py` (~800 lignes) | `admin_sante.py`, `admin_cache.py`, `admin_jobs.py`, `admin_users.py`, `admin_logs.py` |
| `src/api/routes/dashboard.py` (~1000 lignes) | `dashboard_accueil.py`, `dashboard_gamification.py`, `dashboard_stats.py` |
| `src/services/innovations/service.py` (~999 lignes) | Voir section 3.6 |

### 4.4 Unifier les fichiers doublons

| Pattern | Action |
|---------|--------|
| `utilitaires.ts` + `utils.ts` dans `frontend/src/bibliotheque/` | Fusionner en un seul `utilitaires.ts` |
| `bandeau-meteo.tsx` existe dans `famille/` ET `maison/` | Factoriser en composant partagé `composants/partages/bandeau-meteo.tsx` |

---

## 5. SQL — Consolidation

### État actuel

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

### Actions SQL

| Action | Détail |
|--------|--------|
| Supprimer les tables `garanties`, `incidents_sav` | Tables fonctionnalité rejetée (section 3.2) |
| Supprimer les tables `contrats`, `contrats_maison`, `factures`, `comparatifs` | Tables fonctionnalité rejetée (section 3.3) |
| Vérifier cohérence ORM ↔ SQL | Lancer `python scripts/audit_orm_sql.py` pour détecter les désalignements |
| Régénérer `INIT_COMPLET.sql` après modifications | `python scripts/db/regenerate_init.py` |
| Pas de migration/versioning pour le moment | En dev, on travaille directement sur `schema/*.sql` + régénération |

### Regroupement SQL à vérifier

- `06_maison.sql` contient **43 tables** — vérifier si les tables supprimées (garanties, contrats) sont dedans
- `10_finances.sql` peut contenir des références aux contrats → nettoyer
- `12_triggers.sql` peut avoir des triggers liés aux garanties/contrats → nettoyer

---

## 6. Tests — État et plan

### État actuel

| Métrique | Valeur |
|----------|--------|
| Tests collectés | 4932 |
| Tests fonctionnels | ✅ Tous passent (493 derniers échoués re-testés OK) |
| Coverage backend cible | 82% (configuré dans pyproject.toml) |
| Coverage frontend cible | 50% lignes, 40% branches |
| Tests E2E backend | 1 fichier (minimal) |
| Tests E2E frontend | Playwright configuré |
| Tests de charge | 1 fichier (minimal) |

### Actions tests

| Priorité | Action |
|----------|--------|
| Haute | Supprimer les tests des modules supprimés (RGPD, garanties, contrats) |
| Haute | Renommer les tests avec noms de sprint (voir section 2.4) |
| Haute | Mettre à jour les classes de test avec noms de phase → noms fonctionnels |
| Moyenne | Ajouter des tests E2E pour les flux critiques : inscription → connexion → créer recette → planifier → courses |
| Moyenne | Compléter les tests sur les bridges inter-modules |
| Basse | Étendre les tests de charge pour simuler un usage réel |
| Basse | Ajouter des tests visuels (screenshots) sur les pages principales |

### Tests manquants identifiés

| Module | Manque |
|--------|--------|
| Bridges inter-modules | Tests pour les nouveaux bridges proposés (section 8) |
| Admin panel | Tests des endpoints de trigger manuel |
| WebSocket courses | Test annoté `@skip` car deadlock en TestClient — revoir avec async |
| Mode hors-ligne frontend | Aucun test pour la sync offline |
| Service Worker (PWA) | Pas de tests pour l'enregistrement SW |

---

## 7. Documentation — État et plan

### État actuel : 44 fichiers docs

**Points positifs** :
- Architecture bien documentée
- Guides utilisateur présents
- API Reference complète
- Docs inter-modules

**Problèmes** :
| Problème | Fichiers concernés |
|----------|-------------------|
| Docs sprint-spécifiques | `SPRINT13_COMPLETION_SUMMARY.md`, `SPRINT13_INTEGRATION_GUIDE.md`, `SPRINT13_QUICKSTART.md` — à supprimer |
| Références garanties/contrats | `API_REFERENCE.md`, `API_SCHEMAS.md`, `MODULES.md`, `guides/maison/` — à nettoyer |
| Références RGPD | `user-guide/FAQ.md` — à retirer |
| `CHANGELOG_MODULES.md` | Historique de sprints — à supprimer ou convertir en CHANGELOG fonctionnel |
| Docs CRON avec jobs supprimés | `CRON_JOBS.md` liste les jobs garanties/contrats — à mettre à jour |

### Plan documentation

| Action | Détail |
|--------|--------|
| Supprimer les 3 docs sprint13 | Historique inutile |
| Nettoyer `API_REFERENCE.md` | Retirer garanties, contrats, RGPD |
| Nettoyer `API_SCHEMAS.md` | Idem |
| Mettre à jour `MODULES.md` | Retirer modules supprimés |
| Mettre à jour `CRON_JOBS.md` | Retirer jobs supprimés |
| Mettre à jour `guides/maison/` | Retirer sections garanties/contrats |
| Convertir `CHANGELOG_MODULES.md` | Remplacer par un vrai CHANGELOG.md sans noms de sprints |
| Mettre à jour `INDEX.md` | Refléter la nouvelle structure |

---

## 8. Interactions inter-modules

### Bridges existants

| Bridge | Source → Destination | Mécanisme |
|--------|---------------------|-----------|
| B5.1 | Récolte jardin → Recettes | API bridge + IA |
| B5.3 | Documents expiration → Alertes | CRON + notifications |
| B5.5 | Planning unifié (entretien + activités) | Vue combinée |
| B5.8 | Météo → Entretien maison | API bridge + IA |
| B6 | Routine streaks + énergie | Intra-module |
| B7 | Flux simplifiés (3-click cuisine, digest) | Intra-module |
| EventBus | Cache invalidation multi-domaines | Pub/Sub |

### Nouveaux bridges proposés

| Bridge | Source → Destination | Valeur | Priorité |
|--------|---------------------|--------|----------|
| Planification repas → Courses auto | Planning semaine → Liste courses générée | Réduire les étapes manuelles | Haute |
| Inventaire périmé → Suggestions anti-gaspi | Stock bientôt périmé → Recettes de récupération IA | Automatiser l'anti-gaspillage | Haute |
| Budget famille → Dashboard alertes | Seuil budget dépassé → Notification + widget dashboard | Visibilité financière temps réel | Haute |
| Activités complétées → Timeline Jules | Activité terminée → Jalon enregistré automatiquement | Moins de saisie manuelle | Moyenne |
| Projets maison → Calendrier unifié | Tâche projet avec deadline → Événement calendrier | Vue unifiée des tâches | Moyenne |
| Jardin saison → Planning repas | Légumes de saison du jardin → Suggestions recettes | Circuit court | Moyenne |
| Résultats jeux → Dashboard jeux | Résultat automatisé → Stats P&L auto | Moins de saisie | Moyenne |
| Météo → Activités weekend | Prévisions → Suggestions activités adaptées | Déjà partiellement existant (B5.8) — étendre | Basse |
| Entretien planifié → Rappels push | Tâche entretien due → Notification matin | Rappels contextuels | Basse |

### Mécanisme recommandé pour les nouveaux bridges

Utiliser l'EventBus existant (`src/services/core/events/`) avec des subscribers dédiés. Pattern :

```python
# Dans subscribers.py — bridge planification → courses
@event_handler("planning.semaine_validee")
async def generer_courses_depuis_planning(event):
    """Génère automatiquement la liste de courses à partir du planning validé."""
    planning = event.data
    courses_service = get_courses_service()
    courses_service.generer_depuis_planning(planning)
```

---

## 9. IA — Nouvelles intégrations

### IA déjà en place (12 services)

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

### Nouvelles intégrations IA proposées

| Module | Intégration proposée | Description | Priorité |
|--------|---------------------|-------------|----------|
| **Cuisine** | Analyse photo frigo → recettes | L'utilisateur prend une photo du frigo, l'IA identifie les ingrédients et propose des recettes. Le composant `photo-frigo` existe déjà côté frontend. | Haute |
| **Cuisine** | Adaptation recettes Jules | Adapter automatiquement chaque recette pour Jules (sans sel, mixé, portions adaptées). Le modèle portions par âge existe dans `data/reference/portions_age.json`. | Haute |
| **Inventaire** | Prédiction besoins stocks | Analyser l'historique de consommation pour prédire quand un produit sera épuisé et alerter. | Moyenne |
| **Maison** | Optimisation planning entretien | L'IA analyse les tâches d'entretien, la météo, et propose un planning optimal de la semaine. | Moyenne |
| **Jeux** | Analyse tendances paris | L'IA analyse les tendances de cotes et propose des value bets. Backtest existant — ajouter une couche analyse narrative. | Moyenne |
| **Famille** | Journal automatique enrichi | À partir des événements de la journée (repas, activités, météo), générer un résumé journal quotidien. | Basse |
| **Dashboard** | Insights proactifs | L'IA scanne les données et propose des insights non demandés ("tu n'as pas planifié la semaine prochaine", "stock de lait bientôt épuisé"). | Basse |
| **Jardin** | Calendrier plantation IA | Proposer un calendrier de plantation basé sur la zone géographique, la saison, et les plantes existantes. | Basse |

### Points IA non encore exposés dans l'UI

| Service implémenté backend | Frontend manquant |
|----------------------------|-------------------|
| Prédiction courses | Pas de page/widget dédié |
| Scoring nutrition avancé | Pas de visualisation détaillée |
| Suggestions jardinage | Pas de widget jardin IA |
| Recommandations proactives | Bannière existe mais contenu limité |

---

## 10. Jobs automatiques et CRON

### Jobs existants (55+)

**Matin (6h-9h)** : Rappels famille, alertes péremption, vérif stocks, météo, briefing matinal
**Soir (17h-23h)** : Digest quotidien, planning auto, résultats sportifs, sync jeux
**Hebdo** : Résumé famille (lun 7h30), planning semaine (dim 18h), jardin
**Mensuel** : Bilan budget, énergie, rapport mensuel
**Maintenance** : Cache cleanup (2h), backup DB (1h), purge logs

### Nouveaux jobs proposés

| Job | Schedule | Description | Priorité |
|-----|----------|-------------|----------|
| Vérification cohérence planning ↔ courses | Dim 19h (après planning) | Vérifier que tous les ingrédients du planning sont dans la liste de courses | Haute |
| Alerte budget instantanée | Quotidien 20h | Si dépenses > X% du budget prévu, notifier | Haute |
| Sync résultats paris automatique | Après chaque journée de matchs | Récupérer les résultats et mettre à jour les paris | Moyenne |
| Rapport jardin saisonnier | 1er de chaque mois | Résumé : ce qu'il faut planter, récolter, entretenir | Moyenne |
| Nettoyage exports anciens | Hebdo dim 3h | Supprimer les exports de plus de 30 jours | Basse |
| Health check services IA | Toutes les 6h | Vérifier que Mistral répond, alerter si circuit breaker ouvert | Basse |

### Mode admin — Trigger manuel

L'admin peut déjà trigger manuellement les jobs via `POST /api/v1/admin/jobs/{id}/run` (rate-limited 5/min, dry-run supporté).

**Améliorations proposées :**
- Ajouter un mode `--force` qui bypass les conditions (ex: trigger le planning même si c'est pas dimanche)
- Ajouter un log détaillé visible dans l'admin UI avec les résultats du job
- Ajouter un bouton "Relancer" sur chaque job dans la page admin/scheduler
- Permettre de modifier le schedule temporairement depuis l'admin UI

---

## 11. Notifications — WhatsApp, Email, Push

### État actuel

| Canal | Implémenté | Configuration |
|-------|-----------|---------------|
| Web Push | ✅ Complet | VAPID keys, service worker |
| WhatsApp | ✅ Complet | Meta Cloud API, webhook, state machine |
| Email | ✅ Complet | Digest pipeline, templates |
| Notification in-app | ✅ Complet | Store Zustand + sonner toasts |

### WhatsApp — commandes existantes

- Planning du dimanche soir → feedback utilisateur
- Alertes péremption quotidiennes
- Briefing matin
- Réponses interactives (état machine)

### Nouvelles notifications proposées

| Notification | Canal | Trigger | Priorité |
|-------------|-------|---------|----------|
| "Recette du soir" rappel | WhatsApp + Push | 16h si repas planifié, avec lien recette | Haute |
| "Courses de la semaine prêtes" | WhatsApp | Après génération auto courses | Haute |
| "Budget alerte" | Push + Email | Seuil dépassé (job CRON) | Haute |
| "Tâches entretien de la semaine" | WhatsApp lundi matin | Résumé des tâches planifiées | Moyenne |
| "Résultats paris" | Push | Après sync résultats | Moyenne |
| "Jardin — actions du mois" | Email mensuel | Rapport jardin saisonnier | Basse |
| "Jules — jalon développement" | Push | Quand un jalon est atteint selon l'âge | Basse |

### Admin — Test notifications manuellement

L'admin peut déjà tester tous les canaux via `admin/notifications`. Améliorer avec :
- Template preview avant envoi
- Historique des notifications envoyées avec statut de livraison
- Bouton "Simuler notification" (dry-run qui montre le rendu sans envoyer)

---

## 12. Mode Admin manuel

### Fonctionnalités admin existantes (13 pages)

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

### Le panneau admin flottant

`panneau-admin-flottant.tsx` — panneau qui apparaît en dev/admin pour accès rapide. **Non visible pour l'utilisateur final.**

### Améliorations admin proposées

| Amélioration | Description | Priorité |
|-------------|-------------|----------|
| Bouton "Tout exécuter" | Trigger une séquence de jobs (planning → courses → notifications) | Haute |
| Log viewer temps réel | WebSocket pour voir les logs serveur en direct | Haute |
| Simulateur de scénarios | "Simuler lundi 7h" pour tester les CRON sans attendre | Moyenne |
| DB explorer | Interface pour voir/chercher dans les tables (lecture seule) | Moyenne |
| Mode maintenance toggle | Activer/désactiver le mode maintenance depuis l'admin | Basse |
| Métriques IA détaillées | Graphiques tokens utilisés, coût estimé, cache hits | Basse |

---

## 13. UI/UX — Améliorations visuelles

### Stack visuel actuel

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

### Composants graphiques existants

| Composant | Type | Module |
|-----------|------|--------|
| `treemap-budget.tsx` | Treemap D3 | Budget |
| `heatmap-nutritionnel.tsx` | Heatmap | Nutrition |
| `sankey-flux-financiers.tsx` | Sankey D3 | Finances |
| `radar-skill-jules.tsx` | Radar | Jules |
| `radar-nutrition-famille.tsx` | Radar | Nutrition |
| `graphique-roi.tsx` | Ligne/Barre | Retour sur investissement |
| `graphique-jalons.tsx` | Timeline | Jules jalons |
| `camembert-budget.tsx` | Pie chart | Budget |
| `calendrier-energie.tsx` | Calendrier heatmap | Énergie |
| `sparkline.tsx` | Mini graphe inline | Dashboard |
| `heatmap-numeros.tsx` | Heatmap | Loto numéros |
| `heatmap-cotes.tsx` | Heatmap | Paris cotes |
| `plan-3d.tsx` | Three.js 3D | Maison plan |
| `vue-jardin-interactive.tsx` | Canvas interactif | Jardin |
| `graphe-reseau-modules.tsx` | Network graph | Admin |

### Améliorations UI proposées

#### Visualisations à ajouter

| Visualisation | Module | Technologie | Description | Priorité |
|--------------|--------|-------------|-------------|----------|
| Timeline interactive famille | Dashboard | D3 / Framer Motion | Frise chronologique visuelle de la semaine (repas, activités, tâches). Défilable, cliquable. | Haute |
| Kanban drag & drop projets | Maison/Travaux | DnD Kit | Vue Kanban avec colonnes (à faire, en cours, fait) pour les projets | Haute |
| Graphique croissance Jules OMS | Famille/Jules | Recharts | Courbe de croissance superposée aux normes OMS avec zones colorées | Haute |
| Calendrier mosaïque repas | Cuisine/Planning | Grid CSS + images | Vue semaine avec miniatures de chaque repas planifié | Haute |
| Gauge score bien-être | Dashboard | SVG animé | Jauge circulaire animée pour le score bien-être famille | Moyenne |
| Graphique budget vs réel | Famille/Budget | Recharts barres groupées | Budget prévu vs dépensé par catégorie, code couleur vert/rouge | Moyenne |
| Treemap inventaire | Cuisine/Inventaire | D3 | Vue visuelle des stocks par catégorie et quantité | Moyenne |
| Carte zones jardin 2D | Maison/Jardin | Canvas/SVG | Vue aérienne du jardin avec les zones et plantes (existe partiellement) | Moyenne |
| Dashboard widgets configurables | Dashboard | DnD Kit (existe) | Permettre à l'utilisateur de choisir ses widgets — le DnD existe, s'assurer que c'est fonctionnel | Moyenne |
| Animations transitions pages | Global | Framer Motion | Transitions fluides entre les pages (pas de rechargement brutal) | Basse |
| Vue "focus du jour" | Ma Journée | Layout cards | Cards empilées : météo, repas, tâches, activités, rappels | Basse |

#### Améliorations design existant

| Amélioration | Détail | Priorité |
|-------------|--------|----------|
| Mode sombre cohérent | Vérifier que toutes les pages respectent le thème sombre (certains composants custom peuvent ne pas supporter) | Haute |
| Responsive mobile | Vérifier toutes les pages en vue mobile (navBar bottom existe, mais certaines pages complexes peuvent déborder) | Haute |
| Empty states | Ajouter des illustrations/messages pour les pages vides (premier lancement) : "Aucune recette — Commencez par en ajouter une !" | Haute |
| Loading skeletons | Remplacer les spinners par des skeletons (le composant skeleton shadcn existe) partout | Moyenne |
| Animations micro-interactions | Hover effects, click feedback, transitions douces sur les cartes | Moyenne |
| Confettis célébration | `confettis.ts` existe — l'utiliser quand un jalon Jules est atteint, un badge gagné | Basse |

---

## 14. Simplification du flux utilisateur

### Principe : l'utilisateur ne fait que l'essentiel, l'IA et les automatisations font le reste.

### Flux actuels à simplifier

| Flux actuel | Étapes actuelles | Flux simplifié | Étapes simplifiées |
|------------|------------------|----------------|-------------------|
| Planifier la semaine | 1. Aller dans planning 2. Choisir chaque repas 3. Valider 4. Aller dans courses 5. Ajouter ingrédients | 1. L'IA propose un planning 2. L'utilisateur valide/ajuste 3. Courses générées automatiquement | 2-3 clics |
| Ajouter une recette | 1. Aller dans recettes 2. Remplir le formulaire (titre, ingrédients, étapes, temps, portions) | 1. Coller un lien ou décrire en texte 2. L'IA pré-remplit tout 3. Valider | 2-3 clics |
| Gérer les courses | 1. Ouvrir liste 2. Cocher un par un 3. Retirer les cochés | 1. Les articles viennent du planning auto 2. Vue catégorisée par rayon 3. Swipe pour cocher | 1-2 gestes |
| Saisir une activité weekend | 1. Aller dans famille 2. Aller dans activités 3. Remplir formulaire 4. Choisir date/heure | 1. Via WhatsApp : "Ajoute parc samedi 14h" 2. Ou depuis le briefing du matin : "Quelque chose de prévu ce weekend ?" | 1 message |
| Vérifier le budget | 1. Aller dans famille 2. Budget 3. Consulter les graphiques | 1. Widget dashboard avec résumé 2. Alerte push si anomalie | 0 action (proactif) |

### Actions pour simplifier

| Action | Description | Priorité |
|--------|-------------|----------|
| Flow 3-clics cuisine | Planning IA → Validation → Courses auto. Le "flux B7" existe partiellement. Le finaliser. | Haute |
| Import recette par lien | Le composant `dialogue-import-recette.tsx` et le service `importer.py` existent. S'assurer que le pré-remplissage IA est complet. | Haute |
| Commandes WhatsApp enrichies | Ajouter des commandes naturelles : "Qu'est-ce qu'on mange ce soir ?", "Ajoute lait à la liste", "Activité samedi ?" | Haute |
| Widgets dashboard actionnables | Chaque widget du dashboard doit avoir un CTA direct (pas juste de l'info) | Moyenne |
| Notifications actionnables | Chaque notification push/WhatsApp doit avoir un lien direct vers l'action | Moyenne |
| Onboarding premier lancement | Le composant `tour-onboarding.tsx` existe — s'assurer qu'il guide correctement | Basse |

---

## 15. Axes d'innovation

### 15.1 Pas encore implémenté et pertinent

| Innovation | Description | Module | Complexité |
|-----------|-------------|--------|-----------|
| **Mode tablette cuisine** | Interface épurée pour la tablette en cuisine : recette en cours en plein écran, minuteurs intégrés, navigation vocale ("étape suivante") | Cuisine | Moyenne |
| **Scan codes-barres → inventaire** | Le composant `scanneur-multi-codes.tsx` et `@zxing/browser` existent. Connecter au service inventaire pour ajout rapide. | Inventaire | Faible |
| **Briefing vocal matin** | Le composant `bouton-vocal.tsx` et les hooks `synthese-vocale`/`reconnaissance-vocale` existent. Le briefing matinal existe côté backend. Connecter les deux. | Outils | Moyenne |
| **Google Assistant deep linking** | La page `google-assistant/page.tsx` existe, `docs/GOOGLE_ASSISTANT_SETUP.md` aussi. S'assurer que les commandes Actions on Google fonctionnent. | Intégrations | Haute |
| **Dashboard personnalisable** | Le DnD grid et les widgets existent. Permettre à l'utilisateur de choisir et organiser ses widgets. | Dashboard | Moyenne |
| **PWA install + offline** | Le composant `install-prompt.tsx` et le hook `utiliser-hors-ligne.ts` existent. Le service worker `enregistrement-sw.tsx` existe. Vérifier que le mode offline fonctionne réellement. | Global | Moyenne |
| **Leaflet carte activités** | Leaflet est installé. Ajouter une carte des activités/sorties avec rayon autour de la maison. | Famille | Moyenne |
| **Comparateur prix ingrédients** | Backend existe dans innovations (à déplacer). Ajouter une vue frontend pour voir les prix comparés. | Cuisine | Moyenne |

### 15.2 Automatisations intelligentes

| Automatisation | Trigger | Action | Module |
|---------------|---------|--------|--------|
| Inventaire auto-replenish | Stock < seuil minimum | Ajouter à la liste de courses | Inventaire → Courses |
| Suggestion weekend auto | Vendredi soir si rien de planifié | L'IA propose des activités selon météo + historique | Famille |
| Archivage projets terminés | Projet marqué "terminé" depuis 30j | Archiver automatiquement | Maison |
| Rappel anniversaire J-7 | 7 jours avant un anniversaire | Notification + suggestions cadeaux IA | Famille |
| Bilan mensuel auto | 1er du mois | Générer et envoyer par email le bilan complet | Rapports |

### 15.3 Améliorations techniques

| Amélioration | Description | Impact |
|-------------|-------------|--------|
| **SSR pour les pages publiques** | Actuellement tout est client-side. Les pages login/inscription pourraient être SSR pour le SEO et la performance. | Performance |
| **Streaming IA** | Le backend supporte le streaming Mistral. Implémenter le rendu progressif côté frontend pour les réponses IA. | UX |
| **Optimistic updates** | TanStack Query supporte les mises à jour optimistes. Les ajouter pour les actions CRUD courantes (cocher course, ajouter note). | UX |
| **Prefetch routes** | Next.js 16 supporte le prefetch. L'ajouter sur les liens de navigation fréquents. | Performance |
| **Bundle analysis** | `@next/bundle-analyzer` est installé. Analyser et optimiser le bundle size (Three.js est lourd — lazy load). | Performance |

---

## 16. Plan d'exécution par priorité

### Phase 1 — Nettoyage (estimé : volume important)

> Objectif : codebase propre, sans dette technique, sans code mort.

- [ ] RGPD → Backup : supprimer le module RGPD, refactorer en endpoint backup simplifié dans `export.py`, nettoyer frontend/tests/docs
- [ ] Garanties → Simplifier : supprimer le CRUD garanties, garder juste `date_achat` + `duree_garantie_mois` sur Equipement, badge "sous garantie" sur la fiche
- [ ] Contrats → Abonnements : renommer en `abonnements`, simplifier le modèle (eau, élec, gaz, assurances, chaudière, tel, internet), ajouter comparateur
- [ ] Éclater `src/services/innovations/service.py` en 5 services focalisés puis supprimer le package
- [ ] Renommer les 15 fichiers avec sprint/phase dans le nom (voir tableau section 2.4)
- [ ] Nettoyer les 150+ commentaires contenant des noms de phases/sprints
- [ ] Supprimer tout le code legacy (champs, validateurs, shims, aliases — voir section 3.4)
- [ ] Fusionner `utils.ts` + `utilitaires.ts` dans le frontend
- [ ] Factoriser `bandeau-meteo.tsx` (doublon famille/maison)
- [ ] Supprimer les 3 docs sprint13 + `CHANGELOG_MODULES.md`
- [ ] Éclater `admin.py` routes en 5 fichiers
- [ ] Éclater `dashboard.py` routes en 3 fichiers
- [ ] Nettoyer les 152 exports RGPD dans `data/exports/`
- [ ] Nettoyer le SQL (simplifier tables garanties → champs sur equipements, renommer contrats → abonnements)
- [ ] Régénérer `INIT_COMPLET.sql`
- [ ] Mettre à jour les tests (adapter tests garanties/contrats/RGPD, renommer tests sprint)
- [ ] Mettre à jour toute la documentation (retirer références modules supprimés, noms sprints)
- [ ] Lancer `pytest` complet et fixer toute régression

### Phase 2 — Consolidation inter-modules

> Objectif : les modules communiquent entre eux automatiquement.

- [ ] Bridge : Planning validé → Génération courses automatique
- [ ] Bridge : Inventaire périmé → Suggestions anti-gaspi IA
- [ ] Bridge : Budget seuil → Notification alerte
- [ ] Bridge : Activités complétées → Timeline Jules auto
- [ ] Bridge : Projets deadline → Calendrier unifié
- [ ] Bridge : Jardin saison → Suggestions recettes
- [ ] Connecter le composant photo-frigo à l'IA vision (backend existe)
- [ ] Implémenter l'adaptation recettes Jules (portions + restrictions)
- [ ] Tests inter-modules pour chaque nouveau bridge

### Phase 3 — IA et automatisations

> Objectif : l'IA anticipe et réduit le travail manuel.

- [ ] IA : Prédiction besoins stocks (backend) + widget inventaire (frontend)
- [ ] IA : Optimisation planning entretien
- [ ] IA : Journal automatique enrichi quotidien
- [ ] IA : Insights proactifs dashboard (bannière suggestions)
- [ ] IA : Streaming réponses IA côté frontend
- [ ] Jobs CRON : Cohérence planning ↔ courses
- [ ] Jobs CRON : Alerte budget instantanée
- [ ] Jobs CRON : Health check services IA
- [ ] Commandes WhatsApp enrichies (langage naturel)
- [ ] Notifications actionnables (liens directs)
- [ ] Nouvelles notifications (recette du soir, tâches semaine)
- [ ] Mode admin : bouton "Tout exécuter" (séquence jobs)
- [ ] Mode admin : simulateur de scénarios temporels

### Phase 4 — UI/UX moderne

> Objectif : interface belle, fluide, avec des visualisations riches.

- [ ] Timeline interactive famille (D3/Framer Motion)
- [ ] Kanban drag & drop projets maison
- [ ] Graphique croissance Jules OMS
- [ ] Calendrier mosaïque repas
- [ ] Gauge score bien-être dashboard
- [ ] Graphique budget vs réel
- [ ] Mode sombre — audit cohérence toutes les pages
- [ ] Responsive mobile — audit toutes les pages
- [ ] Empty states avec illustrations
- [ ] Loading skeletons partout
- [ ] Animations micro-interactions
- [ ] Transitions pages (Framer Motion)
- [ ] Mode tablette cuisine (plein écran)
- [ ] Dashboard personnalisable (DnD widgets)

### Phase 5 — Simplification flux

> Objectif : l'utilisateur fait le minimum, l'app fait le reste.

- [ ] Flux 3-clics cuisine complet (IA → validation → courses)
- [ ] Import recette par lien perfectionné
- [ ] Scan codes-barres → inventaire (composant existe)
- [ ] Briefing vocal matin (hooks vocaux existent)
- [ ] Widgets dashboard actionnables (CTA sur chaque widget)
- [ ] Onboarding premier lancement
- [ ] Google Assistant deep linking
- [ ] PWA + offline vérifié et fonctionnel

### Phase 6 — Optimisation technique

> Objectif : performance, bundle size, robustesse.

- [ ] Bundle analysis + lazy load Three.js
- [ ] SSR pages publiques (login, inscription)
- [ ] Optimistic updates TanStack Query
- [ ] Prefetch routes navigation
- [ ] Tests E2E flux critiques (Playwright)
- [ ] Tests de charge production
- [ ] Tests visuels (screenshots) pages principales

---

## 17. Limitations Railway — Rester en Free ($0/mois)

### 17.1 État des limites Railway Free

| Critère | Railway Free | Usage actuel |
|---------|-------------|-------------|
| Projets | 1 | 1 |
| Services par projet | 3 | 1 (FastAPI) |
| CPU par service | 1 vCPU | ~0.2 vCPU |
| RAM par service | **0.5 GB** | ~300 MB |
| Volume storage | 0.5 GB | Non utilisé (DB sur Supabase) |
| **CRON jobs natifs** | **NON** | **85 jobs via APScheduler interne** (pas impacté) |
| Custom domains | **0** | URL `*.railway.app` (OK pour usage perso) |
| Build timeout | 10 min | OK |
| Replicas | 1 | 1 |

> **Point clé** : Les CRON jobs Railway natifs ne sont pas disponibles en Free. Mais les 85 jobs de l'app utilisent **APScheduler en interne** dans le process Python — ils tournent tant que le process FastAPI est actif, indépendamment du plan Railway.

### 17.2 Risques du plan Free et mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Service mis en sommeil si inactif | APScheduler s'arrête, plus de CRON | Healthcheck ping `/health` toutes les 5 min (déjà en place) |
| 0.5 GB RAM max | FastAPI + APScheduler + cache L1 + 138 services | Optimisations mémoire obligatoires (voir 17.3) |
| Pas de custom domain | URL = `*.railway.app` | Acceptable pour app familiale privée |
| Pas de CRON Railway natif | Aucun impact | APScheduler tourne dans le process |
| Build timeout 10 min | Builds longs échouent | Image Docker optimisée, multi-stage build |

### 17.3 Optimisations mémoire — OBLIGATOIRES

Ces optimisations ne sont pas optionnelles — elles sont nécessaires pour tenir sous 0.5 GB RAM.

| # | Optimisation | Description | Gain estimé |
|---|-------------|-------------|-------------|
| 1 | **Cache L1 mémoire borné** | Limiter `CacheMemoire` à 500 entrées max avec eviction LRU. Actuellement pas de taille max explicite. | -50-100 MB |
| 2 | **Lazy-load modèles IA** | `ClientIA`, `AnalyseurIA` instanciés au premier appel IA, pas au démarrage de l'app | -30 MB |
| 3 | **Import lazy services** | Les 138 service factories sont importés au démarrage via les `__init__.py`. Passer en import lazy (importlib) | -20 MB |
| 4 | **1 worker uvicorn** | `uvicorn --workers 1` (déjà le cas). Pas de multi-worker sur Free. | Déjà OK |
| 5 | **Désactiver Prometheus** | Les métriques Prometheus consomment de la mémoire pour les histogrammes. Désactiver si inutilisé. | -10 MB |

**Fichiers concernés** :

- `src/core/caching/memory.py` — ajouter `maxsize=500` + LRU eviction
- `src/core/ai/client.py` — lazy init du client Mistral
- `src/services/core/registry.py` — import lazy des factories
- `src/api/prometheus.py` — flag pour désactiver

### 17.4 Mistral AI — Optimiser les appels

| Métrique | Valeur |
|----------|--------|
| Limite quotidienne | 100 appels/jour |
| Limite horaire | 30 appels/heure |
| Usage CRON actuel | ~0.29 appel/jour (<1%) |

| Optimisation | Description |
|-------------|-------------|
| **Cache sémantique TTL 48h** | Augmenter le TTL du `CacheIA` à 48h pour les suggestions récurrentes (déjà implémenté, ajuster TTL) |
| **Batch prompts** | Combiner résumé hebdo + planning IA du dimanche en un seul prompt multi-tâche |
| **Fallback règles locales** | Catégorisation ingrédients, calcul portions → règles Python au lieu d'appels IA |
| **Rate limit utilisateur** | Limiter le chat IA à 20 messages/jour/utilisateur |

### 17.5 Budget mensuel total

| Service | Coût |
|---------|------|
| Railway | **$0** (Free) |
| Telegram Bot API | **$0** (gratuit illimité) |
| Mistral AI | **$0** (free tier, <1% utilisé) |
| Supabase | **$0** (free tier) |
| Vercel | **$0** (free tier) |
| **Total** | **$0/mois** |

---

## 18. Migration WhatsApp → Telegram (100% gratuit)

### 18.1 Pourquoi remplacer WhatsApp par Telegram

| Critère | WhatsApp Business API (Meta) | Telegram Bot API |
|---------|------------------------------|-----------------|
| **Coût messages proactifs** | ~0.02€/msg (Utility) | **Gratuit, illimité** |
| **Coût actuel** | ~2.40€/mois (4 msgs/jour) | **0€** |
| **Fenêtre de réponse** | 24h max pour réponses gratuites | **Aucune limite** |
| **Templates à approuver** | Oui (validation Meta, délai 24-48h) | **Non requis** |
| **Boutons interactifs** | 3 max par message (reply buttons) | **Illimité** (inline keyboards) |
| **Catégories de messages** | Service / Utility / Marketing / Auth | **Aucune catégorie** |
| **API complexity** | Élevée (webhooks Meta, tokens multiples) | **Simple** (1 token, BotFather) |
| **Disponibilité tablette** | WhatsApp Web (navigateur) | **App native Android + Web** |

### 18.2 API Telegram — Concepts clés

```
1. Créer le bot via @BotFather → obtenir TELEGRAM_BOT_TOKEN
2. Récupérer le TELEGRAM_CHAT_ID (ton ID utilisateur)
3. Envoyer des messages : POST https://api.telegram.org/bot{TOKEN}/sendMessage
4. Boutons interactifs : InlineKeyboardMarkup dans le payload
5. Recevoir les réponses : Webhook POST vers /api/v1/telegram/webhook
6. Recevoir les clics boutons : callback_query dans le webhook
```

**Bibliothèque recommandée** : `python-telegram-bot` (async, bien maintenue) ou appels HTTP directs via `httpx` (plus léger, cohérent avec le reste du code).

### 18.3 Mapping fonctions WhatsApp → Telegram

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

### 18.4 Architecture cible

```
src/services/integrations/
├── telegram.py              # NOUVEAU — 14 fonctions publiques (remplace whatsapp.py)
└── whatsapp.py              # SUPPRIMER après migration

src/api/routes/
├── webhooks_telegram.py     # NOUVEAU — webhook Telegram (updates + callback_query)
└── webhooks_whatsapp.py     # SUPPRIMER après migration

src/core/config/settings.py  # Remplacer META_WHATSAPP_* par TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
```

### 18.5 Stratégie notifications par canal

| Canal | Usage | Coût |
|-------|-------|------|
| **Telegram** | Digest matin, planning semaine, courses, weekend, entretien, nutrition, validation interactive, commandes conversationnelles | **$0** |
| **Push Web** (VAPID) | Rappels rapides, alertes péremption, toutes notifications non interactives | **$0** |
| **Email** (SMTP Supabase) | Bilan mensuel PDF, rapports | **$0** |
| **In-app** (sonner) | Toasts, confirmations, micro-interactions | **$0** |

### 18.6 Plan de migration étape par étape

| Étape | Action | Fichiers |
|-------|--------|----------|
| 1 | Créer bot Telegram via @BotFather, obtenir token | `.env.local` |
| 2 | Créer `telegram.py` avec les 14 fonctions (mêmes signatures) | `src/services/integrations/telegram.py` |
| 3 | Créer `webhooks_telegram.py` (réception messages + callback_query) | `src/api/routes/webhooks_telegram.py` |
| 4 | Adapter le dispatcher de notifications : canal "telegram" | `src/services/core/notifications/notif_dispatcher.py` |
| 5 | Adapter les notifications enrichies | `src/services/core/notifications/notifications_enrichies.py` |
| 6 | Adapter l'engine d'automations | `src/services/utilitaires/automations_engine.py` |
| 7 | Adapter la config | `src/core/config/settings.py` |
| 8 | Adapter les 4 CRON jobs (imports) | `src/services/core/cron/jobs.py` |
| 9 | Adapter le frontend admin | `frontend/src/app/(app)/admin/` (3 pages) |
| 10 | Adapter les préférences notifications | `frontend/src/app/(app)/parametres/preferences-notifications/` |
| 11 | Adapter les clients API frontend | `frontend/src/bibliotheque/api/admin.ts`, `avance.ts` |
| 12 | Réécrire les tests | `tests/services/integrations/test_telegram_service.py` |
| 13 | Réécrire la documentation | `docs/TELEGRAM_SETUP.md`, `docs/TELEGRAM_COMMANDS.md` |
| 14 | Supprimer les fichiers WhatsApp | `whatsapp.py`, `webhooks_whatsapp.py`, `WHATSAPP_*.md` |
| 15 | Tester le flux complet (digest + validation + commandes) | Tests manuels + E2E |

---

## 19. Flux utilisateur avec validation (v2)

### 19.1 Principe : IA propose, utilisateur valide, app exécute

Les "3 clics" ne suppriment pas la validation — ils suppriment la **saisie**. L'utilisateur garde le contrôle sur chaque décision mais ne tape rien. L'IA pré-remplit, l'utilisateur valide ou ajuste, depuis le **web OU Telegram**.

### 19.2 Flux cuisine : IA → Brouillon → Validation → Courses

Le flux actuel (`src/services/ia/flux_utilisateur.py`, `src/api/routes/intra_flux.py`) détecte automatiquement l'étape mais ne propose pas de brouillon éditable et passe directement à la génération de courses.

**Nouveau flux** :

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

### 19.3 Modèle brouillon/validation

Ajouter un champ `etat` sur les entités qui nécessitent une validation :

| Entité | Statuts | Qui crée | Qui valide |
|--------|---------|----------|------------|
| **Planning semaine** | `brouillon` → `valide` → `archive` | IA ou CRON | Utilisateur (web ou Telegram) |
| **Liste de courses** | `brouillon` → `active` → `terminee` | Bridge depuis planning | Utilisateur (web ou Telegram) |
| **Suggestions weekend** | `suggeree` → `planifiee` → `terminee` | IA | Utilisateur |
| **Sessions batch cooking** | `brouillon` → `en_cours` → `termine` | IA | Utilisateur |

**NE nécessitent PAS de validation** (informatifs) :
- Alertes péremption, briefing matin, rappels entretien, insights budget, suggestions recettes ponctuelles

### 19.4 Pattern UI web de validation

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

### 19.5 Pattern Telegram de validation

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

### 19.6 Règles par module

| Module | IA propose | Validation obligatoire ? | Sans validation |
|--------|-----------|--------------------------|-----------------|
| **Planning repas** | Planning semaine | ✅ Oui (web ou Telegram) | Non |
| **Liste courses** | Articles depuis planning | ✅ Oui (web ou Telegram) | Non |
| **Activités weekend** | Suggestions d'activités | ✅ Si ajouté au calendrier | Consulter = OK |
| **Batch cooking** | Sessions proposées | ✅ Avant de lancer | Non |
| **Suggestions recettes** | "Ce soir..." | ❌ Informatif | — |
| **Alertes péremption** | Recettes anti-gaspi | ❌ Informatif | — |
| **Briefing matin** | Résumé journée | ❌ Informatif | — |
| **Entretien maison** | Tâches semaine | Optionnel (marquer planifié) | Rappels auto OK |
| **Budget alerte** | Seuil dépassé | ❌ Informatif | — |

### 19.7 Modifications techniques nécessaires

| Composant | Modification |
|-----------|-------------|
| `src/core/models/planning.py` | Ajouter `etat: Mapped[str]` (brouillon/valide/archive) avec default "brouillon" |
| `src/core/models/courses.py` | Ajouter `etat: Mapped[str]` (brouillon/active/terminee) avec default "brouillon" |
| `src/services/ia/flux_utilisateur.py` | Modifier la logique : étape 2 = "valider le brouillon", bloquer auto-progression |
| `src/api/routes/planning.py` | Ajouter `POST /api/v1/planning/{id}/valider` et `POST /api/v1/planning/{id}/regenerer` |
| `src/api/routes/courses.py` | Ajouter `POST /api/v1/courses/{id}/confirmer` |
| `src/api/routes/intra_flux.py` | Adapter flux B7 : ne pas auto-générer courses sans validation du planning |
| `src/services/integrations/telegram.py` | `InlineKeyboardMarkup` avec boutons ✅/✏️/🔄 pour chaque entité |
| `src/api/routes/webhooks_telegram.py` | Handler `callback_query` qui appelle les endpoints de validation |
| Frontend planning page | Bandeau brouillon/validé + boutons valider/modifier/régénérer |
| Frontend courses page | Mode brouillon avec confirmation obligatoire avant mode courses |
| `sql/` | Migration : `ALTER TABLE planning ADD COLUMN etat VARCHAR(20) DEFAULT 'brouillon'` |
| `sql/` | Migration : `ALTER TABLE listes_courses ADD COLUMN etat VARCHAR(20) DEFAULT 'brouillon'` |

---

> **Rappel** : Ce plan est un guide. Chaque phase doit être validée avant exécution. Ne rien implémenter sans accord explicite.
