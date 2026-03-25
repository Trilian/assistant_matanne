# 📁 Migrations SQL — Assistant MaTanne

## Convention de nommage

```
V{numero}_{description}.sql
```

Exemples :
- `V001_rls_security_fix.sql`
- `V002_user_id_uuid_standardization.sql`

## Workflow

```bash
# Créer une migration
python manage.py create-migration

# Appliquer les migrations en attente
python manage.py migrate

# Vérifier l'état
SELECT * FROM schema_migrations ORDER BY applied_at DESC;
```

## Règles

1. **Idempotent** : Utiliser `IF NOT EXISTS`, `IF EXISTS`, `DO $$ ... END $$` avec checks
2. **Non-destructif** : Pas de `DROP TABLE` sans `CREATE TABLE IF NOT EXISTS` de remplacement
3. **Réversible** : Documenter le rollback dans un commentaire en fin de fichier
4. **Commenté** : Décrire le pourquoi en haut du fichier
5. **Testé** : Tester sur une copie avant d'appliquer en production

## Suivi

Les migrations appliquées sont trackées dans la table `schema_migrations` :

```sql
SELECT numero, description, applied_at FROM schema_migrations;
```
