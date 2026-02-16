"""
Script d'initialisation de la base de donnÃ©es
CrÃ©e toutes les tables depuis les modÃ¨les SQLAlchemy

Usage:
    python scripts/init_db.py
"""

import sys
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from src.core.database import obtenir_moteur
from src.core.logging import get_logger
from src.core.models import Base

logger = get_logger(__name__)


def drop_all_tables():
    """Supprime toutes les tables existantes"""
    engine = obtenir_moteur()

    logger.warning("ðŸ—‘ï¸ Suppression de toutes les tables...")

    with engine.begin() as conn:
        # DÃ©sactiver les contraintes FK temporairement
        conn.execute(text("SET session_replication_role = 'replica';"))

        # RÃ©cupÃ©rer toutes les tables
        result = conn.execute(
            text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
        )

        tables = [row[0] for row in result]

        # Supprimer chaque table
        for table in tables:
            logger.info(f"  Suppression: {table}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

        # RÃ©activer les contraintes FK
        conn.execute(text("SET session_replication_role = 'origin';"))

        # Supprimer les enums custom si existants
        conn.execute(text("DROP TYPE IF EXISTS prioriteenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS saisonenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS typerepasenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS typeversionrecetteenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS statusenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS priorityenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS moodenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS seasonenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS mealtypeenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS recipeversionenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS humeurenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS statutenum CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS versionrecetteenum CASCADE"))

    logger.info("âœ… Toutes les tables supprimÃ©es")


def create_all_tables():
    """CrÃ©e toutes les tables depuis les modÃ¨les"""
    engine = obtenir_moteur()

    logger.info("ðŸ“¦ CrÃ©ation des tables depuis les modÃ¨les...")

    # CrÃ©er toutes les tables
    Base.metadata.create_all(bind=engine)

    logger.info("âœ… Tables crÃ©Ã©es avec succÃ¨s")

    # Afficher les tables crÃ©Ã©es
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        )

        tables = [row[0] for row in result]

        logger.info(f"\nðŸ“‹ Tables crÃ©Ã©es ({len(tables)}):")
        for table in tables:
            logger.info(f"  âœ“ {table}")


def verify_schema():
    """VÃ©rifie que le schÃ©ma est correct"""
    engine = obtenir_moteur()

    logger.info("\nðŸ” VÃ©rification du schÃ©ma...")

    expected_tables = [
        "ingredients",
        "recettes",
        "recette_ingredients",
        "etapes_recette",
        "versions_recette",
        "inventaire",
        "liste_courses",
        "plannings",
        "repas",
    ]

    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
        )

        existing_tables = [row[0] for row in result]

    missing = set(expected_tables) - set(existing_tables)
    extra = set(existing_tables) - set(expected_tables)

    if missing:
        logger.warning(f"âš ï¸ Tables manquantes: {missing}")

    if extra:
        logger.info(f"â„¹ï¸ Tables supplÃ©mentaires: {extra}")

    if not missing:
        logger.info("âœ… Toutes les tables essentielles sont prÃ©sentes")

    return len(missing) == 0


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Initialiser la base de donnÃ©es")
    parser.add_argument(
        "--drop", action="store_true", help="Supprimer toutes les tables avant de crÃ©er"
    )
    parser.add_argument(
        "--no-verify", action="store_true", help="Ne pas vÃ©rifier le schÃ©ma aprÃ¨s crÃ©ation"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("ðŸš€ INITIALISATION BASE DE DONNÃ‰ES")
    logger.info("=" * 60)

    try:
        # Supprimer si demandÃ©
        if args.drop:
            confirmation = input(
                "\nâš ï¸ ATTENTION : Toutes les donnÃ©es seront perdues. Continuer ? (oui/non): "
            )
            if confirmation.lower() != "oui":
                logger.info("âŒ OpÃ©ration annulÃ©e")
                return

            drop_all_tables()

        # CrÃ©er les tables
        create_all_tables()

        # VÃ©rifier
        if not args.no_verify:
            success = verify_schema()

            if success:
                logger.info("\n" + "=" * 60)
                logger.info("âœ… INITIALISATION RÃ‰USSIE !")
                logger.info("=" * 60)
            else:
                logger.warning("\nâš ï¸ SchÃ©ma incomplet, vÃ©rifier les erreurs ci-dessus")

    except Exception as e:
        logger.error(f"\nâŒ ERREUR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
