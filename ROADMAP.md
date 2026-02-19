# 🗺️ ROADMAP - Assistant Matanne

> Dernière mise à jour: 19 février 2026

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

### 🎉 REFONTE MODULE FAMILLE (Nouveau!)

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

- `user_profiles` - Profils Anne/Mathieu avec objectifs fitness
- `garmin_tokens` - Tokens OAuth Garmin
- `garmin_activities` - Activités synchronisées
- `garmin_daily_summaries` - Résumés quotidiens (pas, sommeil, stress)
- `food_logs` - Journal alimentaire
- `weekend_activities` - Planning sorties weekend
- `family_purchases` - Wishlist achats famille

#### Configuration Garmin requise

```bash
# À ajouter dans .env.local
GARMIN_CONSUMER_KEY=xxx    # Depuis developer.garmin.com
GARMIN_CONSUMER_SECRET=xxx
```

### Google Calendar & Services DB

- [x] Export planning vers Google Calendar (repas + activités)
- [x] Synchronisation bidirectionnelle Google (import + export)
- [x] Scope OAuth étendu (lecture + écriture)
- [x] Service `weather.py` utilise modèles DB (`AlerteMeteo`, `ConfigMeteo`)
- [x] Service `backup.py` utilise modèle DB (`Backup`)
- [x] Service `calendar_sync.py` utilise modèle DB (`ExternalCalendarConfig`)
- [x] Service `UserPreferenceService` pour persistance préférences
- [x] Planificateur repas connecté à DB (préférences + feedbacks)

### Session 28 janvier

- [x] Créer 11 fichiers de tests (~315 tests)
- [x] Corriger tests alignés avec vraie structure services
- [x] Couverture passée de 26% à **28.32%** (+1.80%)

---

## 🔴 À faire - PRIORITÉ HAUTE

### 1. Configuration & Secrets (1-2h)

#### Variables d'environnement manquantes

```bash
# À ajouter dans .env.local
VAPID_PRIVATE_KEY=xxx          # Pour push notifications
VAPID_PUBLIC_KEY=xxx           # Déjà présent dans le code, à externaliser
OPENWEATHER_API_KEY=xxx        # Pour météo (optionnel)
GOOGLE_CALENDAR_CLIENT_ID=xxx  # Pour sync calendrier (optionnel)
```

**Générer clés VAPID:**

```bash
npx web-push generate-vapid-keys
```

#### Fichier `.env.example` à créer

```env
# Base de données
DATABASE_URL=postgresql://user:password@host:5432/database

# IA
MISTRAL_API_KEY=

# Cache (optionnel)
REDIS_URL=redis://localhost:6379

# Push Notifications (optionnel)
VAPID_PUBLIC_KEY=
VAPID_PRIVATE_KEY=

# APIs externes (optionnel)
OPENWEATHER_API_KEY=
```

### 2. Déployer SQL sur Supabase (30min)

1. Ouvrir https://app.supabase.com
2. Aller dans SQL Editor
3. Copier `sql/SUPABASE_COMPLET_V3.sql`
4. Exécuter
5. Vérifier: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';`

### 3. Connecter services aux nouveaux modèles ✅ FAIT

| Service                 | Statut                                                       |
| ----------------------- | ------------------------------------------------------------ |
| `weather.py`            | ✅ Utilise `AlerteMeteo`, `ConfigMeteo` (DB)                 |
| `backup.py`             | ✅ Utilise modèle `Backup` pour historique                   |
| `calendar_sync.py`      | ✅ Utilise `CalendrierExterne`, `EvenementCalendrier`        |
| `push_notifications.py` | ✅ Utilise `PushSubscription`, `NotificationPreference` (DB) |
| `budget.py`             | ✅ Utilise `BudgetMensuelDB` pour budgets par catégorie      |

**Exemple migration weather.py:**

```python
# Avant (Pydantic local)
class AlerteMeteo(BaseModel):
    type_alerte: str
    ...

# Après (import modèle DB)
from src.core.models import AlerteMeteo  # SQLAlchemy

@with_db_session
def sauvegarder_alerte(alerte: dict, db: Session):
    db_alerte = AlerteMeteo(**alerte)
    db.add(db_alerte)
    db.commit()
```

---

## 🟡 À faire cette semaine - PRIORITÉ MOYENNE

### 4. Tests - ✅ COUVERTURE ATTEINTE, CORRECTIONS EN COURS

```bash
# État actuel: 8661 tests, 8115 passent (93.7%)
# 507 tests en échec à corriger
python -m pytest --tb=no -q
```

**Fichiers tests à corriger (507 failures):**

- [ ] `tests/services/utilisateur/` - 67 failures (authentification, historique)
- [ ] `tests/services/web/` - 53 failures (synchronisation)
- [ ] `tests/modules/maison/` - ~250 failures (projets, eco_tips, scan_factures, meubles, utils, énergie, jardin, entretien)
- [ ] `tests/modules/accueil/` - 21 failures
- [ ] `tests/services/jeux/` - 22 errors (imports cassés)

**Fichiers avec 0% coverage à tester:**

- [ ] `src/core/image_generator.py` (311 stmts) — 44 tests créés, vérifier coverage
- [ ] `src/modules/utilitaires/barcode.py` (288 stmts)
- [ ] `src/services/rapports/generation.py` (248 stmts)
- [ ] `src/modules/maison/ui/plan_jardin.py` (240 stmts)
- [ ] `src/modules/utilitaires/rapports.py` (200 stmts)

### 5. Migration Alembic (1h)

```bash
# Générer migration pour FamilyBudget modifié
python manage.py create_migration "Ajout magasin et recurrence FamilyBudget"
alembic upgrade head
```

### 6. Validation complète (1h)

```bash
# Lancer l'app et tester chaque module
streamlit run src/app.py

# Vérifier les logs
# Tester: Cuisine > Recettes > Ajouter
# Tester: Budget > Ajouter dépense
# Tester: Inventaire > Stock
```

---

## 🟢 Améliorations futures - PRIORITÉ BASSE

### 7. Monitoring & Logs (optionnel)

- [ ] Intégrer Sentry pour error tracking
- [ ] Structurer logs JSON pour analyse
- [ ] Ajouter métriques Prometheus/Grafana

### 8. Performance

- [ ] Activer Redis en production
- [ ] Optimiser requêtes N+1 (joinedload)
- [ ] Lazy load images recettes

### 9. Fonctionnalités avancées

- [ ] Reconnaissance vocale pour ajout rapide
- [ ] Mode hors-ligne (Service Worker)
- [ ] Multi-famille (comptes partagés)

---

## 📊 Métriques projet

| Métrique             | Actuel       | Objectif | Status          |
| -------------------- | ------------ | -------- | --------------- |
| Tests collectés      | **8 661**    | ✅       | ✅              |
| Tests passés         | **8 115**    | 100%     | 🟡 93.7%        |
| Tests en échec       | **507**      | 0        | 🔴 5.9%         |
| Couverture tests     | **~70%**     | 80%      | 🟢 (était 28%)  |
| Lint (ruff)          | **2 issues** | 0        | 🟡 auto-fixable |
| Fichiers 0% coverage | **22**       | 0        | 🟡 2758 stmts   |
| Temps démarrage      | ~1.5s        | <1.5s    | ✅              |
| Tables SQL           | 35           | ✅       | ✅              |
| Services             | 30+          | ✅       | ✅              |

---

## 🔧 Prochaines actions recommandées

```
🔴 PRIORITÉ HAUTE:
□ Corriger 507 tests en échec (35 fichiers)
  - services/utilisateur (67 failures)
  - services/web (53 failures)
  - modules/maison (~250 failures)
  - modules/accueil (21 failures)
  - services/jeux (22 errors - imports cassés)

□ Committer les changements en cours (11 fichiers modifiés)
□ Fix lint: ruff check src tests --fix

🟡 PRIORITÉ MOYENNE:
□ Nettoyer ~16 fichiers temp à la racine
□ Augmenter coverage des 22 fichiers à 0%
□ Déployer SUPABASE_COMPLET_V3.sql

🟢 PRIORITÉ BASSE:
□ Générer VAPID keys: npx web-push generate-vapid-keys
□ Intégrer Sentry pour error tracking
□ Activer Redis en production
```

---

_Note: Cette roadmap remplace tous les fichiers TODO/PLANNING précédents._
