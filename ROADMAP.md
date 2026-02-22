# 🗺️ ROADMAP - Assistant Matanne

> Dernière mise à jour: 22 février 2025

---

## ✅ Terminé (Session 22 février)

### 🔧 REFACTORING 5 WORKSTREAMS — 0 FAILURE ATTEINT

Session majeure de stabilisation : 5 chantiers exécutés, **0 test en échec** (était 507+).

#### Chantier 1 — Adoption `KeyNamespace` (4 modules)

- Modules migrés : `accueil`, `cuisine`, `famille`, `parametres`
- Remplacement des clés session_state ad-hoc par `KeyNamespace` typé

#### Chantier 2 — Intégration `@profiler_rerun` (4 modules)

- Modules instrumentés : `accueil`, `cuisine/recettes`, `famille`, `parametres`
- Ajout monitoring performance sur les fonctions `app()` critiques

#### Chantier 3 — Correction de tous les tests en échec

- **Cause racine** : `__pycache__` obsolètes (`.pyc` référençant `obtenir_contexte_db` supprimé)
- 41 failures → 2 failures après purge des caches bytecode
- 2 derniers : accent manquant (`"ingredient"` → `"ingrédient"`) dans `valider_recette()`
- **Résultat final : 8 018 passed, 0 failed, 322 skipped**

#### Chantier 4 — Division des gros fichiers

| Fichier source                      | Avant  | Après    | Fichiers extraits                        |
| ----------------------------------- | ------ | -------- | ---------------------------------------- |
| `accueil/dashboard.py`              | 613 L  | 221 L    | `alerts.py`, `stats.py`, `summaries.py`  |
| `maison/depenses/components.py`     | 693 L  | 96 L     | `cards.py`, `charts.py`, `previsions.py`, `export.py` |

#### Chantier 5 — Documentation mise à jour

- `docs/ARCHITECTURE.md` : structure corrigée (IoC, CQRS, Event Bus)
- `docs/PATTERNS.md` : service factory, test patterns, event bus ajoutés
- `.github/copilot-instructions.md` : aligné avec la réalité du codebase

---

## ✅ Terminé (Session 19 février)

### 🎯 AMÉLIORATION COUVERTURE TESTS

Session focalisée sur l'augmentation de la couverture de tests avec 137 nouveaux tests.

#### Tests Loto (49 tests)

| Fichier                                      | Tests | Description                                                                                                            |
| -------------------------------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------- |
| `tests/modules/jeux/loto/test_calculs.py`    | 23    | Tests `verifier_grille`, `calculer_esperance_mathematique`                                                             |
| `tests/modules/jeux/loto/test_frequences.py` | 26    | Tests `calculer_frequences_numeros`, `calculer_ecart`, `identifier_numeros_chauds_froids`, `analyser_patterns_tirages` |

#### Tests Famille Utils (88 tests)

| Fichier                                         | Tests | Description                                                                                     |
| ----------------------------------------------- | ----- | ----------------------------------------------------------------------------------------------- |
| `tests/modules/famille/test_routines_utils.py`  | 49    | Tests complets des utilitaires routines (filtrage, statistiques, conflits horaires, régularité) |
| `tests/modules/famille/test_activites_utils.py` | 39    | Tests complets des utilitaires activités (filtrage, statistiques, recommandations, validation)  |

#### Nettoyage dette technique

- Commit `deea911`: Nettoyage fichiers modifiés (service.py mixin refactor, chemins tests)
- Suppression tests obsolètes (`test_calendar_sync_ui.py`)
- Correction tests loto (assertions froids, gestion None)

---

## ✅ Terminé (Session 18 février)

### 🎉 REFONTE MAJEURE ARCHITECTURE

Restructuration complète du codebase avec amélioration massive de la couverture de tests.

#### Refactoring UI (7 phases)

- Suppression des wrappers dépréciés (`dashboard_widgets`, `google_calendar_sync`, `base_module`, `tablet_mode`)
- Restructuration `ui/components` en `atoms`, `charts`, `metrics`, `system`
- Nouveaux modules: `ui/tablet/`, `ui/views/`, `ui/integrations/`
- Ajout `ui/core/crud_renderer`, `module_config`

#### Refactoring Services

- Services divisés en sous-modules (inventaire, jeux, maison)
- Nouveaux packages: `cuisine/`, `infrastructure/`, `integrations/meteo/`
- Restructuration `jeux` en `_internal/` sub-package
- Extraction: `google_calendar`, `planning_pdf`, `recettes_ia_generation`

#### Refactoring Core

- `config.py` → `config/` package (settings, loader)
- `validation.py` → `validation/` package (schemas, sanitizer, validators)
- Nouveaux packages: `caching/`, `db/`, `monitoring/`
- Annotations type modernisées (PEP 604: `X | Y`)

#### Tests & Coverage

- **12 fichiers tests corrigés** (imports `src.utils`/`src.modules.shared` → `src.core`)
- **6 fichiers tests fantômes supprimés** (testaient du code inexistant)
- **44 nouveaux tests** pour `image_generator.py` avec mocking API
- Coverage améliorée: `helpers` 0→92%, `formatters` 12→94%, `date_utils` 49→81%

---

## ✅ Terminé (Session 2 février)

### 🎉 REFONTE MODULE FAMILLE

Refonte complète du module Famille avec navigation par cartes et intégration Garmin.

#### Nouveaux fichiers créés

| Fichier                                    | Description                                                                                                    |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| `src/core/models/users.py`                 | Modèles UserProfile, GarminToken, GarminActivity, GarminDailySummary, FoodLog, WeekendActivity, FamilyPurchase |
| `src/services/garmin_sync.py`              | Service OAuth 1.0a Garmin Connect (sync activités + sommeil + stress)                                          |
| `src/modules/famille/ui/hub_famille.py`    | Hub avec cartes cliquables (Jules, Weekend, Anne, Mathieu, Achats)                                             |
| `src/modules/famille/ui/jules.py`          | Module Jules: activités adaptées âge, shopping, conseils IA                                                    |
| `src/modules/famille/ui/suivi_perso.py`    | Suivi perso: switch Anne/Mathieu, Garmin, alimentation                                                         |
| `src/modules/famille/ui/weekend.py`        | Planning weekend + suggestions IA                                                                              |
| `src/modules/famille/ui/achats_famille.py` | Wishlist famille par catégorie                                                                                 |
| `sql/015_famille_refonte.sql`              | ✅ Migration SQL déployée sur Supabase                                                                         |

#### Nouvelles tables SQL

- `user_profiles`, `garmin_tokens`, `garmin_activities`, `garmin_daily_summaries`
- `food_logs`, `weekend_activities`, `family_purchases`

### Google Calendar & Services DB

- [x] Export/import bidirectionnel Google Calendar
- [x] Service `weather.py`, `backup.py`, `calendar_sync.py` connectés aux modèles DB
- [x] Service `UserPreferenceService` pour persistance préférences
- [x] Planificateur repas connecté à DB (préférences + feedbacks)

### Session 28 janvier

- [x] Créer 11 fichiers de tests (~315 tests)
- [x] Couverture passée de 26% à **28.32%** (+1.80%)

---

## 🔴 À faire - PRIORITÉ HAUTE

### 1. Tests skippés — modules non implémentés (322 tests)

Les 322 tests skippés correspondent à des modules maison pas encore codés :

- `maison/projets`, `maison/scan_factures`, `maison/utils`
- `maison/eco_tips`, `maison/energie`, `maison/entretien`
- `maison/jardin`, `maison/meubles`, `maison/jardin_zones`

**Action** : implémenter les modules ou supprimer les tests fantômes.

### 2. Couverture de code

Fichiers avec 0% coverage à tester :

- [ ] `src/modules/utilitaires/barcode.py` (288 stmts)
- [ ] `src/services/rapports/generation.py` (248 stmts)
- [ ] `src/modules/maison/ui/plan_jardin.py` (240 stmts)
- [ ] `src/modules/utilitaires/rapports.py` (200 stmts)

### 3. Déployer SQL sur Supabase (30min)

```bash
# Appliquer les migrations en attente
python manage.py migrate
```

---

## 🟡 À faire - PRIORITÉ MOYENNE

### 4. Performance

- [ ] Activer Redis en production (`REDIS_URL` dans `.env.local`)
- [ ] Optimiser requêtes N+1 avec `joinedload` / `selectinload`
- [ ] Lazy load images recettes côté UI

### 5. Monitoring & Logs

- [ ] Intégrer Sentry pour error tracking
- [ ] Structurer logs JSON pour analyse
- [ ] Ajouter métriques Prometheus/Grafana

### 6. Validation complète

```bash
streamlit run src/app.py
# Tester chaque module manuellement
```

---

## 🟢 Améliorations futures - PRIORITÉ BASSE

### 7. Fonctionnalités avancées

- [ ] Reconnaissance vocale pour ajout rapide
- [ ] Mode hors-ligne (Service Worker)
- [ ] Multi-famille (comptes partagés)

---

## 📊 Métriques projet

| Métrique             | Actuel         | Objectif | Status         |
| -------------------- | -------------- | -------- | -------------- |
| Tests collectés      | **8 340**      | ✅       | ✅             |
| Tests passés         | **8 018**      | 100%     | ✅ 96.1%       |
| Tests en échec       | **0**          | 0        | ✅ 0%          |
| Tests skippés        | **322**        | 0        | 🟡 modules manquants |
| Lint (ruff)          | **0 issues**   | 0        | ✅             |
| Temps démarrage      | ~1.5s          | <1.5s    | ✅             |
| Tables SQL           | 35             | ✅       | ✅             |
| Services             | 30+            | ✅       | ✅             |

---

## 🔧 Prochaines actions recommandées

```
🔴 PRIORITÉ HAUTE:
□ Implémenter modules maison manquants (322 skipped tests)
□ Augmenter coverage des fichiers à 0%
□ Déployer migrations SQL sur Supabase

🟡 PRIORITÉ MOYENNE:
□ Activer Redis en production
□ Optimiser requêtes N+1 (joinedload)
□ Intégrer Sentry pour error tracking

🟢 PRIORITÉ BASSE:
□ Générer VAPID keys: npx web-push generate-vapid-keys
□ Mode hors-ligne (Service Worker)
□ Reconnaissance vocale
```

---

## 📁 Configuration

Le fichier `.env.example` (171 lignes) documente toutes les variables d'environnement.
Voir aussi `.env.example.images` pour les APIs de génération d'images.

Variables critiques :

| Variable             | Obligatoire | Description                    |
| -------------------- | ----------- | ------------------------------ |
| `DATABASE_URL`       | ✅          | PostgreSQL (Supabase)          |
| `MISTRAL_API_KEY`    | ✅          | API Mistral AI                 |
| `GOOGLE_CLIENT_ID`   | Optionnel   | OAuth2 Google Calendar         |
| `GOOGLE_CLIENT_SECRET` | Optionnel | OAuth2 Google Calendar         |
| `GARMIN_CONSUMER_KEY` | Optionnel  | Garmin Connect OAuth           |
| `FOOTBALL_DATA_API_KEY` | Optionnel | football-data.org             |
| `VAPID_PUBLIC_KEY`   | Optionnel   | Push notifications             |
| `VAPID_PRIVATE_KEY`  | Optionnel   | Push notifications             |
| `REDIS_URL`          | Optionnel   | Cache Redis (prod)             |

---

_Note: Cette roadmap remplace tous les fichiers TODO/PLANNING précédents._
