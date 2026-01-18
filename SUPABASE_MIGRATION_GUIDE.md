# 🗄️ Guide: Appliquer les migrations sur Supabase

## ⚡ TL;DR - 30 secondes

1. Ouvre [Supabase Dashboard](https://app.supabase.com)
2. Va dans **SQL Editor**
3. Clique **+ New Query**
4. Copie le contenu de `MIGRATIONS_SUPABASE.sql`
5. Clique **Run** 🎉

---

## 📋 Détail des migrations

### Migration 004: Historique des modifications
```
CREATE TABLE historique_inventaire
```
- **Table**: Enregistre chaque modification d'article (ajout, mise à jour, suppression)
- **Champs**: Before/after pour quantité, date péremption, emplacement
- **Indexes**: 4 indexes pour les requêtes rapides
- **Foreign Keys**: Lien vers articles et ingrédients

### Migration 005: Photos pour articles
```
ALTER TABLE inventaire ADD COLUMN photo_url, photo_filename, photo_uploaded_at
```
- **photo_url**: URL vers l'image stockée
- **photo_filename**: Nom du fichier original
- **photo_uploaded_at**: Date de l'upload

---

## ✅ Checklist avant d'appliquer

- [ ] Backup de la base (Supabase Dashboard → Backups)
- [ ] Pas d'utilisateurs actifs (ou maintenance mode)
- [ ] Connexion stable à Supabase
- [ ] Lecture des changements ci-dessus

---

## 🚀 Étapes détaillées

### 1️⃣ Accéder à SQL Editor
```
Supabase Dashboard → Ton projet → SQL Editor
```

### 2️⃣ Créer une nouvelle requête
```
Clique "+ New Query" en haut à gauche
```

### 3️⃣ Copier les migrations
```
Ouvre MIGRATIONS_SUPABASE.sql
Copie TOUT le contenu
```

### 4️⃣ Coller dans l'éditeur
```
Clique dans l'éditeur SQL
Colle (Ctrl+V ou Cmd+V)
```

### 5️⃣ Exécuter
```
Clique "Run" (en bas à droite)
OU Ctrl+Enter / Cmd+Enter
```

### 6️⃣ Vérifier
```
Attends le message "Success" ✅
Refresh la page (F5)
Va dans "Table Editor" → vérifie "historique_inventaire"
```

---

## 🔍 Vérifier que ça marche

### Dans SQL Editor:
```sql
-- Vérifier les tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Vérifier les colonnes photos
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'inventaire' 
AND column_name LIKE 'photo%';

-- Compter les indexes
SELECT indexname FROM pg_indexes 
WHERE tablename = 'historique_inventaire';
```

### Dans Table Editor:
1. Clique **historique_inventaire** → doit montrer la structure
2. Clique **inventaire** → doit avoir les 3 colonnes `photo_*`

---

## ❌ Troubleshooting

### ❓ "Table already exists"
**Normal!** Les migrations ont `IF NOT EXISTS`, donc:
- ✅ Pas de problème
- ✅ Peut relancer sans danger

### ❓ "Foreign key constraint failed"
- Vérifier que `inventaire` et `ingredients` existent
- Vérifier qu'il y a des articles actifs

### ❓ Les colonnes photos n'apparaissent pas
- Refresh la page (F5)
- Puis "Table Editor" → click **inventaire**
- Scroll à droite pour voir les nouvelles colonnes

### ❓ Erreur de permission
- Vérifier que tu es en tant qu'admin du projet
- Supabase Dashboard → Settings → Users & Permissions

---

## 🔄 Si tu veux ANNULER

Colle ceci dans SQL Editor:
```sql
-- Supprimer la table d'historique
DROP TABLE IF EXISTS historique_inventaire CASCADE;

-- Supprimer les colonnes photos
ALTER TABLE inventaire 
    DROP COLUMN IF EXISTS photo_url,
    DROP COLUMN IF EXISTS photo_filename, 
    DROP COLUMN IF EXISTS photo_uploaded_at;
```

⚠️ **Attention**: Cela supprime TOUTES les données d'historique et photos!

---

## 📊 Après migration: Tester l'app

1. Redémarre Streamlit: `streamlit run src/app.py`
2. Va dans **Cuisine → Inventaire**
3. Teste:
   - ✅ Onglet "📜 Historique" → doit marcher
   - ✅ Onglet "📸 Photos" → doit marcher
   - ✅ Ajoute un article → check historique
   - ✅ Upload une photo → check historique

---

## 🎯 Prochaines étapes

Une fois les migrations appliquées:
- [ ] Tester les 2 nouveaux onglets
- [ ] Valider l'historique se met à jour
- [ ] Valider les uploads de photos
- [ ] Commencer les notifications push (prochain!)

---

## 💬 Besoin d'aide?

Si une erreur:
1. Copie le message d'erreur complet
2. Check le troubleshooting ci-dessus
3. Si rien ne marche, lance juste `alembic upgrade head` en local d'abord

