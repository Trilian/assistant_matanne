# 🗺️ ROADMAP - Assistant Matanne

> Dernière mise à jour: 28 janvier 2026

---

## ✅ Terminé (Session 28 janvier)

### Tests & Couverture
- [x] Créer 11 fichiers de tests pour modules 0% couverture (~315 tests)
- [x] Corriger tests alignés avec vraie structure services
- [x] Corriger bug Pydantic v2 dans `budget.py` (`date: date` → `date_type`)
- [x] Couverture passée de 26% à **28.32%** (+1.80%)
- [x] Tests: **1491 passés**, 37 skippés, 1 échec mineur (TTL cache)

### Session 26 janvier
- [x] Modèles SQLAlchemy pour nouvelles tables (`nouveaux.py`)
- [x] Mise à jour `FamilyBudget` (ajout `magasin`, `est_recurrent`)
- [x] Correction `budget.py` attributs manquants
- [x] Script SQL complet (`SUPABASE_COMPLET_V3.sql`)
- [x] Nettoyage 52 fichiers .md obsolètes
- [x] Création `README.md` unifié + `docs/ARCHITECTURE.md`

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

### 3. Connecter services aux nouveaux modèles (2-3h)

| Service | Action |
|---------|--------|
| `weather.py` | Remplacer `AlerteMeteo` Pydantic par modèle DB |
| `backup.py` | Utiliser modèle `Backup` pour historique |
| `calendar_sync.py` | Utiliser `CalendrierExterne`, `EvenementCalendrier` |
| `push_notifications.py` | Utiliser `PushSubscription`, `NotificationPreference` |
| `budget.py` | Migrer vers nouveau modèle `Depense` |

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

| Métrique | Actuel | Objectif | Status |
|----------|--------|----------|--------|
| Couverture tests | **28.32%** | 70% | 🟡 En cours |
| Tests passés | **1491** | 2000+ | 🟢 |
| Temps démarrage | ~2s | <1.5s | 🟡 |
| Tables SQL | 35 | ✅ | ✅ |
| Services | 25 | ✅ | ✅ |
| Fichiers .md | 3 | ✅ | ✅ (était 52) |

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

*Note: Cette roadmap remplace tous les fichiers TODO/PLANNING précédents.*
