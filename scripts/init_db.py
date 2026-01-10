"""
Script d'initialisation de la base de données
Crée toutes les tables depuis les modèles SQLAlchemy

Usage:
    python scripts/init_db.py
"""
import sys
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.core.models import Base
from src.core.database import obtenir_moteur
from src.core.logging import get_logger

logger = get_logger(__name__)


def drop_all_tables():
    """Supprime toutes les tables existantes"""
    engine = obtenir_moteur()

    logger.warning("🗑️ Suppression de toutes les tables...")

    with engine.begin() as conn:
        # Désactiver les contraintes FK temporairement
        conn.execute(text("SET session_replication_role = 'replica';"))

        # Récupérer toutes les tables
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """))

        tables = [row[0] for row in result]

        # Supprimer chaque table
        for table in tables:
            logger.info(f"  Suppression: {table}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

        # Réactiver les contraintes FK
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

    logger.info("✅ Toutes les tables supprimées")


def create_all_tables():
    """Crée toutes les tables depuis les modèles"""
    engine = obtenir_moteur()

    logger.info("📦 Création des tables depuis les modèles...")

    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)

    logger.info("✅ Tables créées avec succès")

    # Afficher les tables créées
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """))

        tables = [row[0] for row in result]

        logger.info(f"\n📋 Tables créées ({len(tables)}):")
        for table in tables:
            logger.info(f"  ✓ {table}")


def verify_schema():
    """Vérifie que le schéma est correct"""
    engine = obtenir_moteur()

    logger.info("\n🔍 Vérification du schéma...")

    expected_tables = [
        'ingredients',
        'recettes',
        'recette_ingredients',
        'etapes_recette',
        'versions_recette',
        'inventaire',
        'liste_courses',
        'plannings',
        'repas',
    ]

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """))

        existing_tables = [row[0] for row in result]

    missing = set(expected_tables) - set(existing_tables)
    extra = set(existing_tables) - set(expected_tables)

    if missing:
        logger.warning(f"⚠️ Tables manquantes: {missing}")

    if extra:
        logger.info(f"ℹ️ Tables supplémentaires: {extra}")

    if not missing:
        logger.info("✅ Toutes les tables essentielles sont présentes")

    return len(missing) == 0


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description='Initialiser la base de données')
    parser.add_argument(
        '--drop',
        action='store_true',
        help='Supprimer toutes les tables avant de créer'
    )
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Ne pas vérifier le schéma après création'
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("🚀 INITIALISATION BASE DE DONNÉES")
    logger.info("=" * 60)

    try:
        # Supprimer si demandé
        if args.drop:
            confirmation = input("\n⚠️ ATTENTION : Toutes les données seront perdues. Continuer ? (oui/non): ")
            if confirmation.lower() != 'oui':
                logger.info("❌ Opération annulée")
                return

            drop_all_tables()

        # Créer les tables
        create_all_tables()

        # Vérifier
        if not args.no_verify:
            success = verify_schema()

            if success:
                logger.info("\n" + "=" * 60)
                logger.info("✅ INITIALISATION RÉUSSIE !")
                logger.info("=" * 60)
            else:
                logger.warning("\n⚠️ Schéma incomplet, vérifier les erreurs ci-dessus")

    except Exception as e:
        logger.error(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()