# 🚀 Guide de déploiement SQL Supabase

## Prérequis

1. **DATABASE_URL configurée** dans `.env.local`:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

2. **Dépendances Python**:
   ```bash
   pip install psycopg2-binary python-dotenv
   ```

## Commandes disponibles

### 1. Vérifier la connexion
```bash
python deploy_supabase.py --check
```
Affiche:
- Version PostgreSQL
- Nom de la base de données
- Nombre de tables existantes
- Liste des tables

### 2. Voir le statut actuel
```bash
python deploy_supabase.py --status
```
Affiche:
- Toutes les tables avec nombre de colonnes
- Nombre de lignes par table
- Version Alembic

### 3. Aperçu du déploiement (dry-run)
```bash
python deploy_supabase.py --deploy --dry-run
```
Montre les 50 premières lignes du SQL sans exécuter.

### 4. Déployer le schéma complet
```bash
python deploy_supabase.py --deploy
```

**⚠️ ATTENTION:**
- Vous devrez taper `DEPLOY` pour confirmer
- Un backup sera créé automatiquement dans `backups/`
- Le fichier par défaut est `sql/SUPABASE_COMPLET_V3.sql`

### 5. Déployer un fichier spécifique
```bash
python deploy_supabase.py --deploy --file sql/autre_fichier.sql
```

## Workflow recommandé

### Première installation
```bash
# 1. Vérifier la connexion
python deploy_supabase.py --check

# 2. Voir ce qui existe déjà
python deploy_supabase.py --status

# 3. Aperçu du déploiement
python deploy_supabase.py --deploy --dry-run

# 4. Déploiement réel
python deploy_supabase.py --deploy
# Taper 'DEPLOY' quand demandé

# 5. Vérifier le résultat
python deploy_supabase.py --status
```

### Mise à jour
```bash
# 1. Backup actuel
python deploy_supabase.py --status

# 2. Déployer la mise à jour
python deploy_supabase.py --deploy --file sql/migration_xxx.sql

# 3. Vérifier
python deploy_supabase.py --status
```

## Sécurité

✅ **Le script créé automatiquement:**
- Un backup avant chaque déploiement dans `backups/backup_pre_deploy_YYYYMMDD_HHMMSS.sql`
- Demande une confirmation explicite (`DEPLOY`)
- Mode dry-run pour tester

⚠️ **En cas d'erreur:**
1. Le script affiche le chemin du backup
2. Vous pouvez restaurer manuellement via l'éditeur SQL Supabase
3. Ou utiliser psql: `psql $DATABASE_URL < backups/backup_file.sql`

## Alternative: Déploiement manuel via Supabase UI

Si vous préférez l'interface Supabase:

1. Aller sur https://app.supabase.com
2. Sélectionner votre projet
3. Aller dans **SQL Editor**
4. Créer une nouvelle query
5. Copier le contenu de `sql/SUPABASE_COMPLET_V3.sql`
6. Exécuter (bouton Run ou Ctrl+Enter)

## Fichiers SQL disponibles

- `sql/SUPABASE_COMPLET_V3.sql` - **Schéma complet** (recommandé)
- `sql/SUPABASE_SCHEMA_CORRECT.sql` - Schéma alternatif
- `sql/migration_*.sql` - Migrations spécifiques

## Troubleshooting

### Erreur de connexion
```bash
# Vérifier DATABASE_URL
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env.local'); print(os.getenv('DATABASE_URL'))"
```

### Permission refusée
Vérifier que l'utilisateur PostgreSQL a les droits CREATE TABLE, CREATE INDEX, etc.

### Tables déjà existantes
Le script SQL inclut `DROP TABLE IF EXISTS`, donc les tables existantes seront remplacées.

**⚠️ Backup important avant déploiement si vous avez des données!**

## Support

En cas de problème:
1. Vérifier les logs du script
2. Consulter les backups dans `backups/`
3. Vérifier l'état avec `--status`
4. Restaurer le backup si nécessaire
