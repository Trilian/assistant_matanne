# 🗺️ ROADMAP - Assistant Matanne

> Dernière mise à jour: 26 janvier 2026

---

## ✅ Terminé (Session 26 janvier)

### Modèles & Base de données
- [x] Créer modèles SQLAlchemy pour nouvelles tables (`nouveaux.py`)
- [x] Mettre à jour `FamilyBudget` (ajout `magasin`, `est_recurrent`)
- [x] Corriger `budget.py` attributs manquants
- [x] Corriger `pdf_export.py` relation `Recette.ingredients`
- [x] Générer script SQL complet (`SUPABASE_COMPLET_V3.sql`)

### Documentation
- [x] Nettoyer 52 fichiers .md obsolètes
- [x] Créer `README.md` unifié
- [x] Créer `docs/ARCHITECTURE.md`

---

## 🔴 À faire demain (27 janvier) - PRIORITÉ HAUTE

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

### 4. Tests (2-3h)

```bash
# Objectif: passer de ~40% à 70% couverture
python manage.py test_coverage
```

**Fichiers tests à compléter:**
- [ ] `tests/test_budget.py` - Tester nouveau modèle Depense
- [ ] `tests/test_weather.py` - Créer fichier
- [ ] `tests/test_backup.py` - Créer fichier
- [ ] `tests/test_nouveaux_models.py` - Tester tous les nouveaux modèles

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

| Métrique | Actuel | Objectif |
|----------|--------|----------|
| Couverture tests | ~40% | 70% |
| Temps démarrage | ~2s | <1.5s |
| Tables SQL | 35 | ✅ |
| Services | 25 | ✅ |
| Fichiers .md | 3 | ✅ (était 52) |

---

## 🔧 Checklist rapide demain matin

```
□ Créer .env.example
□ Générer VAPID keys
□ Déployer SUPABASE_COMPLET_V3.sql
□ Tester streamlit run src/app.py
□ Vérifier logs pour erreurs
□ Commiter les changements
```

---

*Note: Cette roadmap remplace tous les fichiers TODO/PLANNING précédents.*
