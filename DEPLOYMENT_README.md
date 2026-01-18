# 🚀 Déploiement: Historique + Photos + Notifications

**Status:** ✅ Prêt à déployer  
**Dernière update:** 18 Jan 2026  
**Files clés:** 2 migrations SQL + 4 services Python

---

## ⚡ Quick Start (5 min)

### Option 1: Déploiement automatique (Recommandé)
```bash
cd /workspaces/assistant_matanne
./deploy.sh
```

### Option 2: Déploiement manuel
```bash
# 1. Appliquer migrations
alembic upgrade head

# 2. Redémarrer Streamlit
streamlit run src/app.py
```

### Option 3: Déployer sur Supabase
```bash
# 1. Aller sur https://app.supabase.com/project/[votre-projet]/sql/new
# 2. Copier-coller le contenu de MIGRATIONS_SUPABASE.sql
# 3. Lancer "Run"
# 4. Redémarrer l'app
```

---

## 📋 Fichiers modifiés

### Code Python (4 fichiers)
| Fichier | Lignes | Changes |
|---------|--------|---------|
| `src/core/models.py` | +40 | HistoriqueInventaire model |
| `src/services/inventaire.py` | +130 | 2 SECTIONS (PHOTOS, NOTIFICATIONS) |
| `src/services/notifications.py` | 323 | **NEW** Service complet |
| `src/modules/cuisine/inventaire.py` | +250 | 4 nouvelles fonctions UI |

### Migrations (2 fichiers)
| Fichier | Rôle |
|---------|------|
| `alembic/versions/004_add_historique_inventaire.py` | Crée table historique |
| `alembic/versions/005_add_photos_inventaire.py` | Ajoute colonnes photos |

### Documentation (4 fichiers)
- `MIGRATIONS_SUPABASE.sql` - Code SQL prêt à lancer
- `SUPABASE_MIGRATION_GUIDE.md` - Guide détaillé pas-à-pas
- `NOTIFICATIONS_RESUME.md` - Details features notifications
- `DEPLOIEMENT_SUPABASE_INDEX.md` - Index complet

---

## ✅ Pré-requis

- [x] Python 3.8+
- [x] Streamlit 1.0+
- [x] SQLAlchemy 2.0+
- [x] Alembic 1.0+
- [x] Pydantic 2.0+
- [x] Base de données (local ou Supabase)

Tous déjà installés ✅

---

## 🎯 Ce qui est inclus

### 1. 📜 Historique des modifications
- Tracking auto avant/après
- Filtres par date, article, type
- Table `historique_inventaire` (15 colonnes)
- 4 indexes performance

### 2. 📸 Photos d'articles
- Upload d'images (JPG, PNG, WebP)
- Aperçu avant confirmation
- Suppression avec historique
- Champs: `photo_url`, `photo_filename`, `photo_uploaded_at`

### 3. 🔔 Notifications d'alerte
- Stock critique (< 50% seuil)
- Stock bas (< seuil minimum)
- Péremption proche (< 7 jours)
- Groupage par priorité (haute/moyenne/basse)
- Actions: Marquer lue, supprimer

---

## 🚀 Deployment Steps

### Local SQLite
```bash
# 1. Appliquer migrations
python -m alembic upgrade head

# 2. Redémarrer Streamlit
streamlit run src/app.py

# 3. Test
# → Allez à Cuisine → Inventaire → 📜 Historique
# → Modifiez un article
# → L'historique doit se mettre à jour
```

### Supabase
```bash
# 1. Copier MIGRATIONS_SUPABASE.sql
# 2. Ouvrir SQL Editor sur Supabase
# 3. Coller + Run
# 4. Redémarrer Streamlit
# 5. Test comme ci-dessus
```

---

## ✔️ Checklist post-déploiement

- [ ] Migrations appliquées sans erreur
- [ ] Streamlit redémarré
- [ ] Onglet Historique affiche les changements
- [ ] Onglet Photos permet upload
- [ ] Onglet Notifications affiche les alertes
- [ ] Bouton "Actualiser alertes" fonctionne

---

## 🔍 Validation

### Tests rapides
```bash
# 1. Modifier un article
Cuisine → Inventaire → 📊 Stock
→ Sélectionner article
→ Changer quantité
→ Clique "Mettre à jour"

# 2. Vérifier historique
→ Tab 📜 Historique
→ Doit voir le changement

# 3. Upload photo
→ Tab 📸 Photos
→ Sélectionner article
→ Upload une image
→ Confirmer

# 4. Vérifier notifications
→ Tab 🔔 Notifications
→ Clique "Actualiser alertes"
→ Doit voir liste d'alertes
```

---

## 🐛 Troubleshooting

### Erreur: "Table already exists"
**Solution:** Normal avec `IF NOT EXISTS`. Juste continuer.

### Historique vide après migration
**Solution:** Normal. Elle se remplit en modification articles.

### Photos n'apparaissent pas
**Solution:** 
1. Refresh page (F5)
2. Redémarrer Streamlit
3. Relancer migration 005

### Notifications ne génèrent pas alertes
**Solution:**
1. Vérifier qu'il y a articles
2. Vérifier certains ont quantité < seuil
3. Vérifier certains ont date péremption bientôt

---

## 📚 Documentation complète

Pour plus de details, voir:
- **SQL:** `MIGRATIONS_SUPABASE.sql`
- **Guide Supabase:** `SUPABASE_MIGRATION_GUIDE.md`
- **Features details:** `NOTIFICATIONS_RESUME.md`
- **Deployment index:** `DEPLOIEMENT_SUPABASE_INDEX.md`

---

## 🔄 Rollback (Si problème)

```sql
-- Supprimer les nouvelles features
DROP TABLE IF EXISTS historique_inventaire CASCADE;
ALTER TABLE inventaire 
    DROP COLUMN IF EXISTS photo_url,
    DROP COLUMN IF EXISTS photo_filename,
    DROP COLUMN IF EXISTS photo_uploaded_at;
```

Puis redémarrer Streamlit.

---

## 🎉 Success!

Une fois déployé, vous avez:
- ✅ Audit trail complet (Historique)
- ✅ Gestion média (Photos)
- ✅ Système d'alertes (Notifications)

Prochaines étapes:
- Import/Export CSV/Excel avancé
- Prévisions ML (patterns consommation)
- Multi-utilisateurs

