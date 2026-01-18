# 📋 Guide Complet: Migrations & Déploiement Supabase

**Dernier update:** 18 Jan 2026  
**Status:** ✅ 3 features complétées (Historique, Photos, Notifications)  
**Prochaine étape:** Import/Export avancé ou Prévisions ML

---

## 📑 Table des matières

1. [Migrations SQL](#migrations-sql) - Code à lancer
2. [Guide d'application](#guide-dapplication) - Étapes détaillées
3. [Vérification](#vérification) - Comment tester
4. [Rollback](#rollback) - Si problème
5. [FAQ](#faq) - Questions fréquentes

---

## 🗄️ Migrations SQL

### À lancer EN ORDRE sur Supabase

```sql
-- ============================================================================
-- MIGRATION 004: Créer table historique_inventaire
-- ============================================================================
-- Description: Tracking automatique des modifications d'articles
-- Status: À lancer EN PREMIER

CREATE TABLE IF NOT EXISTS historique_inventaire (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    type_modification VARCHAR(50) NOT NULL,
    quantite_avant FLOAT,
    quantite_apres FLOAT,
    quantite_min_avant FLOAT,
    quantite_min_apres FLOAT,
    date_peremption_avant DATE,
    date_peremption_apres DATE,
    emplacement_avant VARCHAR(100),
    emplacement_apres VARCHAR(100),
    date_modification TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    utilisateur VARCHAR(100),
    notes TEXT,
    CONSTRAINT fk_historique_article FOREIGN KEY (article_id) 
        REFERENCES inventaire(id) ON DELETE CASCADE,
    CONSTRAINT fk_historique_ingredient FOREIGN KEY (ingredient_id) 
        REFERENCES ingredients(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_historique_article_id ON historique_inventaire(article_id);
CREATE INDEX IF NOT EXISTS idx_historique_ingredient_id ON historique_inventaire(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_historique_type_modification ON historique_inventaire(type_modification);
CREATE INDEX IF NOT EXISTS idx_historique_date_modification ON historique_inventaire(date_modification);

ALTER TABLE historique_inventaire ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- MIGRATION 005: Ajouter colonnes photos
-- ============================================================================
-- Description: Support des photos pour articles
-- Status: À lancer EN DEUXIÈME (après 004)

ALTER TABLE inventaire
ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS photo_filename VARCHAR(200),
ADD COLUMN IF NOT EXISTS photo_uploaded_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_inventaire_photo_url 
    ON inventaire(photo_url) WHERE photo_url IS NOT NULL;
```

### Copier depuis fichier
Fichier complet: **`MIGRATIONS_SUPABASE.sql`**

---

## 🚀 Guide d'application

### Étape 1: Backup
```
Supabase Dashboard → [Projet] → Settings → Backups → Create Backup
Attends le message "Backup complete" ✅
```

### Étape 2: Ouvrir SQL Editor
```
Dashboard → SQL Editor (en haut)
```

### Étape 3: Créer nouvelle requête
```
Clique "+ New Query"
```

### Étape 4: Copier les migrations
```
Option A: Copie MIGRATIONS_SUPABASE.sql entièrement
Option B: Copie juste le code SQL ci-dessus

Colle dans l'éditeur
```

### Étape 5: Exécuter
```
Clique "Run" (bas-droit)
OU Ctrl+Enter / Cmd+Enter

Attends le message "Success" ✅
```

### Étape 6: Redémarrer app
```
Terminal local: Ctrl+C (arrête Streamlit)
Terminal local: streamlit run src/app.py (redémarre)

Attends "You can now view your Streamlit app in your browser"
```

---

## ✅ Vérification

### Dans Supabase SQL Editor:
```sql
-- Vérifie que les tables existent
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('historique_inventaire', 'inventaire')
ORDER BY table_name;

-- Résultat attendu:
-- historique_inventaire
-- inventaire

-- Vérifie les colonnes photos
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'inventaire' 
AND column_name LIKE 'photo%'
ORDER BY column_name;

-- Résultat attendu:
-- photo_filename | character varying
-- photo_uploaded_at | timestamp without time zone
-- photo_url | character varying

-- Vérifie les indexes
SELECT indexname FROM pg_indexes 
WHERE tablename = 'historique_inventaire'
ORDER BY indexname;

-- Résultat attendu: 4 indexes
-- idx_historique_article_id
-- idx_historique_date_modification
-- idx_historique_ingredient_id
-- idx_historique_type_modification
```

### Dans Table Editor Supabase:
1. Clique **historique_inventaire** → doit voir 15 colonnes
2. Clique **inventaire** → scroll droite → doit voir colonnes photo_*

### Dans Streamlit:
1. Aller **Cuisine → Inventaire → 📜 Historique**
   - Doit afficher un tableau avec dates, modifications
   - Filtres doivent fonctionner

2. Aller **Cuisine → Inventaire → 📸 Photos**
   - Doit avoir sélecteur d'articles
   - Boutons Upload doivent exister

3. Aller **Cuisine → Inventaire → 🔔 Notifications**
   - Bouton "Actualiser les alertes" doit marcher
   - Doit afficher alertes stock/péremption

---

## ↩️ Rollback

### Si ça ne marche pas, annuler tout:

```sql
-- SUPPRIMER la table d'historique
DROP TABLE IF EXISTS historique_inventaire CASCADE;

-- SUPPRIMER les colonnes photos
ALTER TABLE inventaire 
    DROP COLUMN IF EXISTS photo_url,
    DROP COLUMN IF EXISTS photo_filename, 
    DROP COLUMN IF EXISTS photo_uploaded_at;
```

**⚠️ Attention:** Cela supprime TOUTES les données d'historique et photos!

Après rollback:
1. Redémarrer Streamlit
2. Vérifier que "Historique", "Photos", "Notifications" affichent "Pas de données"

---

## ❓ FAQ

### Q: "Table already exists" (erreur)
**R:** Normal avec `IF NOT EXISTS`. Pas grave, la migration s'est bien passée.

### Q: Les colonnes photos n'apparaissent pas dans inventaire
**R:** 
- Refresh page (F5) 
- Allez Table Editor → inventaire
- Scroll complètement à droite
- Si toujours rien: relancer la migration 005

### Q: Historique_inventaire vide après migration
**R:** Normal! Elle se remplit quand vous ajoutez/modifiez des articles.
Test: Allez **Stock** → Modifiez un article → Allez **Historique** → Doit apparaître

### Q: Supabase dit "Foreign key constraint failed"
**R:** Vérifier que:
- Table `inventaire` existe
- Table `ingredients` existe
- Il y a au moins un article dans `inventaire`

### Q: Rien ne se passe au click sur "Actualiser alertes"
**R:**
- Vérifier qu'il y a articles dans Stock
- Vérifier certains ont `quantite < quantite_min`
- Vérifier certains ont une date_peremption < 7 jours

### Q: Où se stockent les notifications?
**R:** En mémoire (Streamlit session_state). Disparaissent au refresh.
Pour persistence: à ajouter table `notifications` en future enhancement.

### Q: Peux-je utilisér email/Slack maintenant?
**R:** Non, c'est des stubs pour future implémentation.
Actuellement: notifications Streamlit uniquement.

---

## 📊 Fichiers modifiés

### Code Python:
- `src/core/models.py` - ArticleInventaire + HistoriqueInventaire
- `src/services/inventaire.py` - 3 sections nouvelles (PHOTOS, HISTORIQUE, NOTIFICATIONS)
- `src/services/notifications.py` - **NEW** Service complet
- `src/modules/cuisine/inventaire.py` - 4 nouvelles fonctions (photos, historique, notifications)

### Migrations:
- `alembic/versions/004_add_historique_inventaire.py` - Table historique
- `alembic/versions/005_add_photos_inventaire.py` - Colonnes photos

### Documentation:
- `MIGRATIONS_SUPABASE.sql` - Code SQL exact
- `SUPABASE_MIGRATION_GUIDE.md` - Guide détaillé
- `NOTIFICATIONS_RESUME.md` - Features notifications
- `DEPLOIMEMENT_SUPABASE_INDEX.md` - **VOUS ÊTES ICI**

---

## 🎯 Checklist Final

- [ ] Backup créé
- [ ] Migration 004 lancée ✅
- [ ] Migration 005 lancée ✅
- [ ] Onglet Historique fonctionne
- [ ] Onglet Photos fonctionne
- [ ] Onglet Notifications fonctionne
- [ ] Vous voyez des alertes au click "Actualiser"

---

## 📞 Support

Si problème:
1. Check la section FAQ ci-dessus
2. Lancer le rollback SQL
3. Redémarrer Streamlit
4. Relancer les migrations une seule fois (sans les IF EXISTS, ca fail)

