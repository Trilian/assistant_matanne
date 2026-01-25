# 🔧 Guide de Création de TOUTES les Tables

Le script `scripts/create_maison_tables.py` crée maintenant **TOUTES les tables manquantes** en une seule exécution.

## ⚡ Exécution rapide

```bash
python scripts/create_maison_tables.py
```

## 📋 Ce que crée le script

Le script crée les tables de **TOUS les modules** :

### 🍽️ Recettes
- `recettes` - Recettes de cuisine
- `ingredients` - Ingrédients
- `recette_ingredients` - Associations recettes/ingrédients
- `etapes_recettes` - Étapes de préparation
- `versions_recettes` - Versions historiques

### 🛍️ Courses
- `articles_courses` - Articles de la liste de courses
- `articles_inventaire` - Stock de cuisine

### 👨‍👩‍👧‍👦 Famille
- `child_profiles` - Profils enfants (Jules)
- `wellbeing_entries` - Journal de bien-être
- `milestones` - Jalons du développement
- `family_activities` - Activités familiales
- `health_routines` - Routines de santé
- `health_objectives` - Objectifs de santé

### 🏠 Maison
- `projects` - Projets (rénovation, etc.)
- `project_tasks` - Tâches des projets
- `garden_items` - Plantes du jardin
- `garden_logs` - Journal d'entretien
- `routines` - Routines ménagères
- `routine_tasks` - Tâches des routines

### 📅 Planning
- `calendar_events` - Événements du calendrier
- `plannings` - Planifications
- `repas` - Repas planifiés

### 👨‍🍳 Batch Cooking
- `batch_meals` - Repas préparés en batch

### 💰 Budget
- `family_budgets` - Budgets familiaux

## ✅ Vérification du résultat

Le script affiche automatiquement le résumé de création :

```
📊 VÉRIFICATION DES TABLES CRÉÉES
═══════════════════════════════════════════════════════════════════════════

🍽️  RECETTES
  ✅ recettes                        (12 colonnes)
  ✅ ingredients                     ( 5 colonnes)
  ...

👨‍👩‍👧‍👦 FAMILLE
  ✅ child_profiles                  ( 9 colonnes)
  ...

🏠 MAISON
  ✅ projects                        ( 9 colonnes)
  ✅ project_tasks                   (10 colonnes)
  ✅ garden_items                    (10 colonnes)
  ...

🎉 RÉSUMÉ: 30/30 tables créées
```

## 🚀 Prochaines étapes

1. **Relancer l'application :**
   ```bash
   streamlit run src/app.py
   ```

2. **Naviguer vers 🏠 Maison** dans la barre latérale

3. **Les 3 sous-modules sont maintenant fonctionnels :**
   - 🌱 Jardin - Gérer les plantes
   - 📋 Projets - Créer des projets maison
   - ☑️ Entretien - Créer des routines

## ❌ Dépannage

### Erreur: "configuration DB manquante"
Créez `.env.local` à la racine du projet :
```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Erreur: "psycopg2.errors.OperationalError"
- Vérifiez la connexion Supabase
- Vérifiez les credentials DATABASE_URL

### Erreur: "table already exists"
C'est normal ! Le script utilise `CREATE TABLE IF NOT EXISTS`, il ne recréera pas les tables existantes.

## 📊 Alternative : Via Supabase SQL Editor

Si vous préférez, vous pouvez exécuter les migrations Alembic :
```bash
alembic upgrade head
```

Cette commande exécutera la migration Alembic `008_add_planning_and_missing_tables.py` qui crée les mêmes tables.

