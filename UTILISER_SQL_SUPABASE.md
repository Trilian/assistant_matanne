# 📝 Utiliser le fichier SQL sur Supabase

## 📄 Fichier SQL complet

**Fichier :** `sql/009_create_all_tables_complete.sql`

Contient les 24 tables complètes pour l'application.

---

## 🚀 Étapes pour exécuter sur Supabase

### 1️⃣ Aller sur Supabase

Allez à : https://supabase.com/dashboard
- Sélectionnez votre projet

### 2️⃣ Ouvrir SQL Editor

Cliquez sur **SQL Editor** dans le menu de gauche

### 3️⃣ Créer une nouvelle requête

Cliquez sur **+ New Query**

### 4️⃣ Copier le contenu du fichier

Ouvrez `sql/009_create_all_tables_complete.sql`
Copier TOUT le contenu

### 5️⃣ Coller dans Supabase

Collez le contenu dans l'éditeur SQL

### 6️⃣ Exécuter

Cliquez **▶ RUN** ou appuyez sur `Ctrl+Enter`

### 7️⃣ Vérifier

Allez dans **Table Editor** (colonne gauche)
Vous devez voir 24 tables créées :

```
✅ ingredients
✅ recettes
✅ recette_ingredients
✅ etapes_recettes
✅ versions_recettes
✅ articles_courses
✅ articles_inventaire
✅ child_profiles
✅ wellbeing_entries
✅ milestones
✅ family_activities
✅ health_routines
✅ health_objectives
✅ projects
✅ project_tasks
✅ garden_items
✅ garden_logs
✅ routines
✅ routine_tasks
✅ calendar_events
✅ plannings
✅ repas
✅ batch_meals
✅ family_budgets
```

---

## ⚡ Raccourci : Copier depuis terminal

```bash
# Windows PowerShell
Get-Content sql/009_create_all_tables_complete.sql | Set-Clipboard

# Linux/Mac
cat sql/009_create_all_tables_complete.sql | pbcopy
```

Puis collez dans Supabase SQL Editor.

---

## ⚠️ Important

- Le script utilise `IF NOT EXISTS` donc il est sûr de relancer
- Crée les indices automatiquement
- Pas de données d'exemple (tables vides)

---

## ✅ Après l'exécution

1. Relancez l'app : `streamlit run src/app.py`
2. L'erreur `calendar_events does not exist` doit disparaître
3. Naviguez vers 🏠 Maison

Prêt ! 🎉
