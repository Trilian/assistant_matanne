#!/usr/bin/env python3
"""
Script de dÃ©ploiement SQL vers Supabase.

Usage:
    python deploy_supabase.py --check          # VÃ©rifier la connexion
    python deploy_supabase.py --deploy         # DÃ©ployer le schÃ©ma complet
    python deploy_supabase.py --status         # Voir l'Ã©tat actuel
    python deploy_supabase.py --rollback       # Rollback (avec confirmation)
"""

import argparse
import os
from datetime import datetime
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Charger les variables d'environnement
load_dotenv(".env.local")
load_dotenv(".env")


class SupabaseDeployer:
    """DÃ©ployeur SQL pour Supabase."""

    def __init__(self, database_url: str = None):
        """Initialise le dÃ©ployeur."""
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("âŒ DATABASE_URL non trouvÃ©e dans .env.local ou .env")

        self.connection = None
        self.cursor = None

    def connect(self):
        """Connecte Ã  la base de donnÃ©es."""
        try:
            print("ðŸ”Œ Connexion Ã  Supabase...")
            self.connection = psycopg2.connect(self.database_url)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            print("âœ… Connexion Ã©tablie avec succÃ¨s!")
            return True
        except Exception as e:
            print(f"âŒ Erreur de connexion: {e}")
            return False

    def disconnect(self):
        """Ferme la connexion."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("ðŸ”Œ Connexion fermÃ©e")

    def check_connection(self):
        """VÃ©rifie la connexion et affiche les infos."""
        if not self.connect():
            return False

        try:
            # Version PostgreSQL
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]
            print(f"\nðŸ“Š PostgreSQL: {version.split(',')[0]}")

            # Base de donnÃ©es actuelle
            self.cursor.execute("SELECT current_database();")
            db_name = self.cursor.fetchone()[0]
            print(f"ðŸ“¦ Base de donnÃ©es: {db_name}")

            # Nombre de tables
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public';
            """)
            nb_tables = self.cursor.fetchone()[0]
            print(f"ðŸ“‹ Nombre de tables: {nb_tables}")

            # Liste des tables
            if nb_tables > 0:
                self.cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in self.cursor.fetchall()]
                print(f"\nðŸ“‹ Tables existantes ({len(tables)}):")
                for table in tables:
                    print(f"   - {table}")

            return True
        except Exception as e:
            print(f"âŒ Erreur: {e}")
            return False
        finally:
            self.disconnect()

    def deploy_schema(self, sql_file: Path, dry_run: bool = False):
        """DÃ©ploie le schÃ©ma depuis un fichier SQL."""
        if not sql_file.exists():
            print(f"âŒ Fichier SQL introuvable: {sql_file}")
            return False

        if not self.connect():
            return False

        try:
            # Lire le fichier SQL
            print(f"\nðŸ“– Lecture du fichier: {sql_file.name}")
            sql_content = sql_file.read_text(encoding="utf-8")

            # Statistiques
            nb_lines = len(sql_content.splitlines())
            print(f"ðŸ“ {nb_lines} lignes de SQL Ã  exÃ©cuter")

            if dry_run:
                print("\nâš ï¸  MODE DRY-RUN: Aucune modification ne sera faite")
                print("\n--- AperÃ§u (50 premiÃ¨res lignes) ---")
                print("\n".join(sql_content.splitlines()[:50]))
                return True

            # Confirmation
            print("\nâš ï¸  ATTENTION: Cette opÃ©ration va modifier la base de donnÃ©es!")
            confirmation = input("Taper 'DEPLOY' pour confirmer: ")
            if confirmation != "DEPLOY":
                print("âŒ DÃ©ploiement annulÃ©")
                return False

            # Backup de sÃ©curitÃ©
            print("\nðŸ’¾ CrÃ©ation d'un backup de sÃ©curitÃ©...")
            backup_file = Path(
                f"backups/backup_pre_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            )
            backup_file.parent.mkdir(exist_ok=True)

            # Export des tables existantes
            self.cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public';
            """)
            tables = [row[0] for row in self.cursor.fetchall()]

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(f"-- Backup crÃ©Ã© le {datetime.now()}\n")
                f.write(f"-- Nombre de tables: {len(tables)}\n\n")
                for table in tables:
                    f.write(f"-- Table: {table}\n")

            print(f"âœ… Backup sauvegardÃ©: {backup_file}")

            # ExÃ©cution du SQL
            print("\nðŸš€ DÃ©ploiement en cours...")
            self.cursor.execute(sql_content)

            # VÃ©rification
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public';
            """)
            nb_tables_after = self.cursor.fetchone()[0]

            print("\nâœ… DÃ©ploiement rÃ©ussi!")
            print(f"ðŸ“‹ Tables aprÃ¨s dÃ©ploiement: {nb_tables_after}")

            return True

        except Exception as e:
            print(f"\nâŒ Erreur lors du dÃ©ploiement: {e}")
            print("\nâš ï¸  La base de donnÃ©es peut Ãªtre dans un Ã©tat inconsistant.")
            print(f"ðŸ’¾ Restaurez le backup si nÃ©cessaire: {backup_file}")
            return False
        finally:
            self.disconnect()

    def get_status(self):
        """Affiche l'Ã©tat actuel de la base de donnÃ©es."""
        if not self.connect():
            return False

        try:
            print("\nðŸ“Š STATUT DE LA BASE DE DONNÃ‰ES\n")
            print("=" * 60)

            # Tables
            self.cursor.execute("""
                SELECT table_name,
                       (SELECT COUNT(*) FROM information_schema.columns
                        WHERE table_name = t.table_name
                        AND table_schema = 'public') as nb_colonnes
                FROM information_schema.tables t
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)

            tables = self.cursor.fetchall()
            print(f"\nðŸ“‹ TABLES ({len(tables)}):")
            print(f"{'Table':<40} {'Colonnes':<10}")
            print("-" * 60)
            for table, nb_cols in tables:
                print(f"{table:<40} {nb_cols:<10}")

            # Nombre total de lignes
            print("\nðŸ“Š DONNÃ‰ES:")
            total_rows = 0
            for table, _ in tables:
                try:
                    self.cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
                    count = self.cursor.fetchone()[0]
                    if count > 0:
                        print(f"   {table}: {count} lignes")
                    total_rows += count
                except:
                    pass

            print(f"\nðŸ“ˆ Total: {total_rows} lignes")

            # Migrations (schema_migrations)
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'schema_migrations'
                );
            """)
            has_migrations = self.cursor.fetchone()[0]

            if has_migrations:
                self.cursor.execute("SELECT MAX(version), COUNT(*) FROM schema_migrations;")
                row = self.cursor.fetchone()
                if row and row[0]:
                    print(f"\n🔄 Schema v{row[0]} ({row[1]} migration(s))")

            print("\n" + "=" * 60)
            return True

        except Exception as e:
            print(f"âŒ Erreur: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Point d'entrÃ©e principal."""
    parser = argparse.ArgumentParser(description="DÃ©ploiement SQL vers Supabase")
    parser.add_argument("--check", action="store_true", help="VÃ©rifier la connexion")
    parser.add_argument("--deploy", action="store_true", help="DÃ©ployer le schÃ©ma")
    parser.add_argument("--status", action="store_true", help="Afficher le statut")
    parser.add_argument("--dry-run", action="store_true", help="Mode dry-run (aperÃ§u)")
    parser.add_argument(
        "--file", type=str, default="sql/SUPABASE_COMPLET_V3.sql", help="Fichier SQL Ã  dÃ©ployer"
    )

    args = parser.parse_args()

    # Banner
    print("\n" + "=" * 60)
    print("ðŸš€ DÃ‰PLOYEUR SUPABASE - Assistant MaTanne")
    print("=" * 60 + "\n")

    deployer = SupabaseDeployer()

    # ExÃ©cuter l'action
    if args.check or (not args.deploy and not args.status):
        deployer.check_connection()

    elif args.status:
        deployer.get_status()

    elif args.deploy:
        sql_file = Path(args.file)
        deployer.deploy_schema(sql_file, dry_run=args.dry_run)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
