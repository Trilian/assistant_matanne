# 🗺️ ROADMAP - Assistant Matanne

> Dernière mise à jour: 2 février 2026

---

## ✅ Terminé (Session 2 février)

### 🎉 REFONTE MODULE FAMILLE (Nouveau!)

Refonte complète du module Famille avec navigation par cartes et intégration Garmin.

#### Nouveaux fichiers créés

| Fichier                                    | Description                                                                                                    |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| `src/core/models/users.py`                 | Modèles UserProfile, GarminToken, GarminActivity, GarminDailySummary, FoodLog, WeekendActivity, FamilyPurchase |
| `src/services/garmin_sync.py`              | Service OAuth 1.0a Garmin Connect (sync activités + sommeil + stress)                                          |
| `src/domains/famille/ui/hub_famille.py`    | Hub avec cartes cliquables (Jules, Weekend, Anne, Mathieu, Achats)                                             |
| `src/domains/famille/ui/jules.py`          | Module Jules: activités adaptées âge, shopping, conseils IA                                                    |
| `src/domains/famille/ui/suivi_perso.py`    | Suivi perso: switch Anne/Mathieu, Garmin, alimentation                                                         |
| `src/domains/famille/ui/weekend.py`        | Planning weekend + suggestions IA                                                                              |
| `src/domains/famille/ui/achats_famille.py` | Wishlist famille par catégorie                                                                                 |
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

### 4. Tests - PARTIELLEMENT TERMINÉ ✅

```bash
# Objectif: passer de ~40% à 70% couverture
# Actuel: 28.32% (amélioration significative)
python manage.py test_coverage
```

**Fichiers tests créés:**

- [x] `tests/test_budget.py` - 26 tests pour modèles Depense
- [x] `tests/test_notifications.py` - 20 tests
- [x] `tests/test_predictions.py` - 24 tests
- [x] `tests/test_action_history.py` - 24 tests
- [x] `tests/test_suggestions_ia.py` - 16 tests
- [x] `tests/test_recipe_import.py` - 36 tests
- [x] `tests/test_redis_multi_tenant.py` - 22 tests

**Fichiers tests à créer:**

- [ ] `tests/test_weather.py` - Service météo
- [ ] `tests/test_backup.py` - Service backup
- [ ] `tests/test_calendar_sync.py` - Sync calendrier

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

| Métrique         | Actuel     | Objectif | Status        |
| ---------------- | ---------- | -------- | ------------- |
| Couverture tests | **28.32%** | 70%      | 🟡 En cours   |
| Tests passés     | **1491**   | 2000+    | 🟢            |
| Temps démarrage  | ~2s        | <1.5s    | 🟡            |
| Tables SQL       | 35         | ✅       | ✅            |
| Services         | 25         | ✅       | ✅            |
| Fichiers .md     | 3          | ✅       | ✅ (était 52) |

---

## 🔧 Prochaines actions recommandées

```
✅ .env.example existe déjà (complet)
□ Générer VAPID keys: npx web-push generate-vapid-keys
□ Déployer SUPABASE_COMPLET_V3.sql
□ Migrer services vers nouveaux modèles DB
□ Créer tests pour weather, backup, calendar_sync
□ Viser 40% couverture (+12%)
```

---

_Note: Cette roadmap remplace tous les fichiers TODO/PLANNING précédents._
