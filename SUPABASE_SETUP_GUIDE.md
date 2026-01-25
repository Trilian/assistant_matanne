# 🗄️ Scripts SQL - Module Maison pour Supabase

## 📋 Contenu

Scripts pour créer les tables du module Maison (Projets, Jardin, Entretien) :

- ✅ `projects` - Projets maison
- ✅ `project_tasks` - Tâches des projets
- ✅ `garden_items` - Plantes du jardin
- ✅ `garden_logs` - Journal du jardin
- ✅ `routines` - Routines ménagères
- ✅ `routine_tasks` - Tâches des routines

**Fichier** : [sql/008_add_maison_models.sql](sql/008_add_maison_models.sql)

## 🚀 Méthode 1 : Supabase Web Interface (Plus facile)

### Étapes

1. **Accéder à Supabase**
   - Aller sur [supabase.com](https://supabase.com)
   - Se connecter à votre projet
   - Cliquer sur "SQL Editor" dans la sidebar

2. **Créer une nouvelle requête**
   - Cliquer sur "+ New Query"
   - Donner un nom : "Create Maison Tables"

3. **Copier le contenu du script**
   - Ouvrir [sql/008_add_maison_models.sql](sql/008_add_maison_models.sql)
   - Copier tout le contenu
   - Coller dans l'éditeur SQL de Supabase

4. **Exécuter la requête**
   - Cliquer sur "Run" (ou Ctrl+Enter)
   - Vérifier : "success" message en haut

5. **Vérifier les tables**
   - Aller dans "Table Editor" (sidebar)
   - Vous devez voir :
     - `projects`
     - `project_tasks`
     - `garden_items`
     - `garden_logs`
     - `routines`
     - `routine_tasks`

## 🔧 Méthode 2 : Via psql (Ligne de commande)

### Prérequis

```bash
# Installer postgresql-client si pas fait
# Windows : https://www.postgresql.org/download/windows/
# Mac : brew install postgresql
# Linux : sudo apt install postgresql-client
```

### Étapes

1. **Récupérer la chaîne de connexion**
   ```
   postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

2. **Exécuter le script**
   ```bash
   psql "postgresql://user:password@host:6543/postgres" < sql/008_add_maison_models.sql
   ```

3. **Ou fichier par fichier**
   ```bash
   cat sql/008_add_maison_models.sql | psql "postgresql://user:password@host:6543/postgres"
   ```

## 🐍 Méthode 3 : Via Python (Automatisé)

```python
import psycopg2
from pathlib import Path

# Connexion
conn = psycopg2.connect(
    "postgresql://user:password@host:6543/postgres"
)
cursor = conn.cursor()

# Lire le script
with open("sql/008_add_maison_models.sql", "r") as f:
    script = f.read()

# Exécuter
cursor.execute(script)
conn.commit()
cursor.close()
conn.close()

print("✅ Tables créées!")
```

## ✅ Vérification

Après exécution, vérifier dans Supabase :

```sql
-- Compter les tables créées
SELECT 
    table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN ('projects', 'project_tasks', 'garden_items', 'garden_logs', 'routines', 'routine_tasks');
```

**Résultat attendu** : 6 lignes

Ou vérifier dans l'interface Supabase → "Table Editor" → Vous devez voir les 6 tables listées.

## 📊 Schéma des tables

### projects
```
id (PK) | nom | description | statut | priorite | date_debut | date_fin_prevue | date_fin_reelle | cree_le
```

### project_tasks
```
id (PK) | project_id (FK) | nom | description | statut | priorite | date_echéance | assigné_à | cree_le
```

### garden_items
```
id (PK) | nom | type | location | statut | date_plantation | date_recolte_prevue | notes | cree_le
```

### garden_logs
```
id (PK) | garden_item_id (FK) | date | action | notes | cree_le
```

### routines
```
id (PK) | nom | description | categorie | frequence | actif | cree_le
```

### routine_tasks
```
id (PK) | routine_id (FK) | nom | description | ordre | heure_prevue | fait_le | notes | cree_le
```

## 🔐 Indices (Performance)

Les indices suivants sont créés automatiquement :

### Projets
- `idx_projects_statut` - Recherche par statut
- `idx_projects_priorite` - Recherche par priorité

### Tâches Projets
- `idx_project_tasks_project_id` - Retrouver tâches d'un projet
- `idx_project_tasks_statut` - Recherche par statut

### Jardin
- `idx_garden_items_type` - Retrouver plantes par type
- `idx_garden_items_statut` - Retrouver plantes actives
- `idx_garden_logs_garden_item_id` - Historique d'une plante
- `idx_garden_logs_date` - Logs par date

### Routines
- `idx_routines_categorie` - Retrouver routines par catégorie
- `idx_routines_actif` - Lister routines actives
- `idx_routine_tasks_routine_id` - Tâches d'une routine

## ⚠️ Contraintes de validation

Les contraintes suivantes garantissent la validité des données :

### Projets
- `ck_statut` : statut ∈ {à_faire, en_cours, terminé, annulé}
- `ck_priorite` : priorite ∈ {basse, moyenne, haute, urgente}

### Tâches
- `ck_task_statut` : statut ∈ {à_faire, en_cours, terminé, annulé}
- `ck_task_priorite` : priorite ∈ {basse, moyenne, haute, urgente}

### Jardin
- `ck_garden_statut` : statut ∈ {actif, inactif, mort}

### Routines
- `ck_frequence` : frequence ∈ {quotidien, hebdomadaire, bi-hebdomadaire, mensuel}

## 🚨 Troubleshooting

### "relation already exists"
- ✅ Normal si tables déjà créées
- Solution : Supprimer puis recréer
  ```sql
  DROP TABLE IF EXISTS routine_tasks CASCADE;
  DROP TABLE IF EXISTS routines CASCADE;
  DROP TABLE IF EXISTS garden_logs CASCADE;
  DROP TABLE IF EXISTS garden_items CASCADE;
  DROP TABLE IF EXISTS project_tasks CASCADE;
  DROP TABLE IF EXISTS projects CASCADE;
  ```

### "Permission denied"
- ❌ Utilisateur sans droit CREATE
- Solution : Utiliser compte admin Supabase

### "Cannot connect"
- ❌ Connection string incorrecte
- Vérifier : host, port, user, password

## 🔄 Alternative : Alembic Migration

Si vous préférez utiliser Alembic :

```bash
# Créer migration
alembic revision --autogenerate -m "Add maison models"

# Appliquer
alembic upgrade head
```

Mais l'exécution directe du SQL est plus rapide.

---

**Prêt?** ✅  
Copier le contenu de [sql/008_add_maison_models.sql](sql/008_add_maison_models.sql) et exécuter sur Supabase!
