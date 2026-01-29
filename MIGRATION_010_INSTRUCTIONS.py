#!/usr/bin/env python3
"""Instructions pour appliquer la migration Supabase 010"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   MIGRATION SUPABASE 010 - updated_at columns                ║
╚══════════════════════════════════════════════════════════════════════════════╝

OBJECTIF: Ajouter la colonne 'updated_at' aux tables 'recettes' et 'modeles_courses'

POURQUOI: Le trigger PostgreSQL 'update_updated_at_column' s'attend à cette colonne
mais elle n'existait pas, causant l'erreur:
  "record 'new' has no field 'updated_at'"

FICHIERS:
  ✓ Migration Alembic: alembic/versions/010_fix_trigger_modifie_le.py
  ✓ Script SQL direct: sql/010_add_updated_at_columns.sql

OPTIONS D'APPLICATION:

┌─ Option 1: Utiliser Alembic (Recommandé pour tracking)
│  $ alembic upgrade head
│  Cela appliquera toutes les migrations jusqu'à la version actuelle.

┌─ Option 2: SQL direct via Supabase Editor
│  1. Ouvrir https://supabase.com/dashboard
│  2. Aller à SQL Editor
│  3. Créer une nouvelle query
│  4. Copier le contenu de: sql/010_add_updated_at_columns.sql
│  5. Exécuter

┌─ Option 3: Python avec Database Manager
│  $ python -c "from src.core.database import GestionnaireMigrations; \\
                  GestionnaireMigrations.appliquer_migrations()"

VÉRIFICATION APRÈS MIGRATION:
  $ psql -h aws-0-eu-central-1.pooler.supabase.com -U postgres -d postgres \\
         -c "SELECT column_name FROM information_schema.columns \\
             WHERE table_name IN ('recettes', 'modeles_courses') \\
             AND column_name = 'updated_at' ORDER BY table_name;"

RÉSULTAT ATTENDU:
  recettes         | updated_at
  modeles_courses  | updated_at

═══════════════════════════════════════════════════════════════════════════════

ÉTAPES RECOMMANDÉES:

1. Backup Supabase (Optional but recommended):
   $ python scripts/backup_supabase.py

2. Appliquer la migration Alembic:
   $ python manage.py migrate
   
3. Vérifier la migration:
   $ python -c "from src.core.database import GestionnaireMigrations; \\
                  print(GestionnaireMigrations.obtenir_version_courante())"

4. Vérifier les colonnes en DB:
   $ python test_db_schema.py

5. Relancer l'application:
   $ python manage.py run
""")

# Option: Appliquer directement
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        print("\n⚠️  Applying migration...")
        try:
            from src.core.database import GestionnaireMigrations
            GestionnaireMigrations.appliquer_migrations()
            print("[OK] Migration applied successfully!")
        except Exception as e:
            print(f"[ERROR] Failed to apply migration: {e}")
            sys.exit(1)
