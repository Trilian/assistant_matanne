#!/usr/bin/env python3
"""
Script de migration pour Supabase
Migration: Ajout colonnes code_barres et prix_unitaire
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
env_file = project_root / ".env.local"
if env_file.exists():
    load_dotenv(env_file, override=True)

from sqlalchemy import create_engine, text

from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from src.core.config import obtenir_parametres

parametres = obtenir_parametres()


def afficher_menu():
    """Affiche le menu principal"""
    print(
        "\nâ•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—"
    )
    print("â•‘         ðŸ—„ï¸ Migration Supabase - Code-Barres/Rapports      â•‘")
    print(
        "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"
    )
    print("\nðŸ“‹ Options:")
    print("  1. VÃ©rifier l'Ã©tat actuel")
    print("  2. Lancer la migration (upgrade)")
    print("  3. Annuler la migration (downgrade)")
    print("  4. Voir l'historique des migrations")
    print("  5. Quitter")
    print()


def verifier_connexion():
    """VÃ©rifie la connexion Ã  la BD"""
    try:
        engine = create_engine(parametres.DATABASE_URL, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("âœ… Connexion Ã  Supabase: OK")
            print(f"   Version PostgreSQL: {version[:50]}...")
            return engine
    except Exception as e:
        print(f"âŒ Erreur connexion: {str(e)}")
        return None


def verifier_colonnes(engine):
    """VÃ©rifie les colonnes existantes"""
    print("\nðŸ“Š Ã‰tat actuel de la table ArticleInventaire:")
    try:
        with engine.connect() as conn:
            # VÃ©rifier colonnes
            query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'article_inventaire'
            ORDER BY ordinal_position
            """
            result = conn.execute(text(query))

            print("\n   Colonnes existantes:")
            colonnes = {}
            for col_name, col_type, nullable in result:
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"     â€¢ {col_name:25} {col_type:15} {nullable_str}")
                colonnes[col_name] = col_type

            # VÃ©rifier colonnes nouvelles
            print("\n   Statut nouvelles colonnes:")
            if "code_barres" in colonnes:
                print(f"     âœ… code_barres existe ({colonnes['code_barres']})")
            else:
                print("     âŒ code_barres MANQUANTE")

            if "prix_unitaire" in colonnes:
                print(f"     âœ… prix_unitaire existe ({colonnes['prix_unitaire']})")
            else:
                print("     âŒ prix_unitaire MANQUANTE")

            return colonnes
    except Exception as e:
        print(f"âŒ Erreur: {str(e)}")
        return None


def lancer_migration(engine):
    """Lance la migration"""
    print("\nðŸš€ Lancement de la migration...")
    try:
        # Configuration Alembic
        alembic_cfg = Config(str(project_root / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", parametres.DATABASE_URL)

        # ExÃ©cuter upgrade
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)

            # Lire la migration
            migrations_dir = project_root / "alembic" / "versions"
            migration_file = migrations_dir / "003_add_barcode_price.py"

            if not migration_file.exists():
                print(f"âŒ Fichier migration non trouvÃ©: {migration_file}")
                return False

            print(f"   ðŸ“„ Migration: {migration_file.name}")

            # Importer et exÃ©cuter la migration
            import importlib.util

            spec = importlib.util.spec_from_file_location("migration", migration_file)
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)

            print("   â³ ExÃ©cution de upgrade()...")
            migration.upgrade()
            print("   âœ… Migration appliquÃ©e!")

        return True
    except Exception as e:
        print(f"âŒ Erreur migration: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def voir_historique():
    """Affiche l'historique des migrations"""
    print("\nðŸ“œ Historique des migrations:")
    migrations_dir = project_root / "alembic" / "versions"

    if not migrations_dir.exists():
        print("   âŒ Dossier migrations non trouvÃ©")
        return

    migrations = sorted(migrations_dir.glob("*.py"))
    for i, mig in enumerate(migrations, 1):
        if mig.name == "__init__.py":
            continue
        print(f"   {i}. {mig.name}")


def main():
    """Fonction principale"""
    print("\nðŸ”§ Script Migration Supabase")
    print(
        f"   BD: {parametres.DATABASE_URL.split('@')[1] if '@' in parametres.DATABASE_URL else 'local'}"
    )

    # VÃ©rifier connexion
    engine = verifier_connexion()
    if not engine:
        print("\nâŒ Impossible de continuer sans connexion BD")
        sys.exit(1)

    while True:
        afficher_menu()
        choix = input("ðŸ‘‰ Choix (1-5): ").strip()

        if choix == "1":
            verifier_colonnes(engine)

        elif choix == "2":
            verifier_colonnes(engine)
            confirm = input("\nâš ï¸  ÃŠtes-vous sÃ»r? (oui/non): ").strip().lower()
            if confirm == "oui":
                if lancer_migration(engine):
                    print("\nâœ… Migration rÃ©ussie!")
                    verifier_colonnes(engine)

        elif choix == "3":
            print("\nâš ï¸  Downgrade non implÃ©mentÃ© pour ce script")
            print("   Utilisez: alembic downgrade -1")

        elif choix == "4":
            voir_historique()

        elif choix == "5":
            print("\nðŸ‘‹ Au revoir!")
            break

        else:
            print("âŒ Choix invalide")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nðŸ‘‹ Interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\nâŒ Erreur: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
