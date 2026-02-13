#!/usr/bin/env python3
"""
Script de reset complet de la base Supabase
Usage: python scripts/reset_supabase.py
"""

import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

import streamlit as st
from sqlalchemy import create_engine, text

from src.core.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_supabase_url():
    """RÃ©cupÃ¨re l'URL Supabase depuis les secrets"""
    try:
        db = st.secrets["db"]
        return (
            f"postgresql://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['name']}"
            f"?sslmode=require"
        )
    except KeyError as e:
        logger.error(f"Secret manquant: {e}")
        logger.error("Configure .streamlit/secrets.toml avec:")
        logger.error(
            """
[db]
host = "db.xxxxx.supabase.co"
port = "5432"
name = "postgres"
user = "postgres"
password = "ton_mot_de_passe"
        """
        )
        sys.exit(1)


def drop_all_tables(engine):
    """Supprime TOUTES les tables (mÃªme celles crÃ©Ã©es par Supabase)"""
    logger.info("ðŸ—‘ï¸  Suppression de toutes les tables...")

    with engine.connect() as conn:
        # DÃ©sactiver les contraintes FK temporairement
        conn.execute(text("SET session_replication_role = 'replica';"))

        # RÃ©cupÃ©rer toutes les tables du schÃ©ma public
        result = conn.execute(
            text(
                """
                                   SELECT tablename
                                   FROM pg_tables
                                   WHERE schemaname = 'public'
                                   """
            )
        )

        tables = [row[0] for row in result]

        # Supprimer chaque table
        for table in tables:
            logger.info(f"  - Suppression: {table}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

        # RÃ©activer les contraintes
        conn.execute(text("SET session_replication_role = 'origin';"))

        conn.commit()

    logger.info("âœ… Toutes les tables supprimÃ©es")


def create_all_tables(engine):
    """CrÃ©e toutes les tables depuis models.py"""
    logger.info("ðŸ—ï¸  CrÃ©ation des tables depuis models.py...")

    Base.metadata.create_all(bind=engine)

    logger.info("âœ… Tables crÃ©Ã©es")

    # Lister les tables crÃ©Ã©es
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                                   SELECT tablename
                                   FROM pg_tables
                                   WHERE schemaname = 'public'
                                   ORDER BY tablename
                                   """
            )
        )

        tables = [row[0] for row in result]
        logger.info(f"ðŸ“‹ {len(tables)} tables crÃ©Ã©es:")
        for table in tables:
            logger.info(f"  âœ“ {table}")


def seed_minimal_data(engine):
    """Ajoute des donnÃ©es minimales pour tester"""
    logger.info("ðŸŒ± Ajout de donnÃ©es de test...")

    with engine.connect() as conn:
        # Utilisateur de test
        conn.execute(
            text(
                """
                          INSERT INTO utilisateurs (nom_utilisateur, email, parametres, cree_le, modifie_le)
                          VALUES ('Anne', 'anne@test.fr', '{}', NOW(), NOW())
                          """
            )
        )

        # Quelques ingrÃ©dients de base
        ingredients = [
            ("Tomates", "kg", "LÃ©gumes"),
            ("PÃ¢tes", "g", "FÃ©culents"),
            ("Oeufs", "pcs", "ProtÃ©ines"),
            ("Fromage", "g", "Laitier"),
        ]

        for nom, unite, categorie in ingredients:
            conn.execute(
                text(
                    """
                              INSERT INTO ingredients (nom, unite, categorie, cree_le)
                              VALUES (:nom, :unite, :categorie, NOW())
                              """
                ),
                {"nom": nom, "unite": unite, "categorie": categorie},
            )

        conn.commit()

    logger.info("âœ… DonnÃ©es de test ajoutÃ©es")


def main():
    """Point d'entrÃ©e principal"""
    print("=" * 70)
    print("ðŸ”¥ RESET COMPLET DE LA BASE SUPABASE")
    print("=" * 70)
    print()
    print("âš ï¸  ATTENTION: Cette action est IRRÃ‰VERSIBLE !")
    print("   Toutes les donnÃ©es seront DÃ‰FINITIVEMENT SUPPRIMÃ‰ES.")
    print()

    # Demander confirmation
    confirmation = input("Taper 'RESET' en majuscules pour confirmer: ")

    if confirmation != "RESET":
        print("âŒ AnnulÃ©")
        sys.exit(0)

    print()
    logger.info("DÃ©marrage du reset...")

    try:
        # Connexion
        database_url = get_supabase_url()
        engine = create_engine(
            database_url, echo=False, connect_args={"connect_timeout": 10, "sslmode": "require"}
        )

        # Test connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("âœ… Connexion Supabase OK")

        # 1. Supprimer toutes les tables
        drop_all_tables(engine)

        # 2. CrÃ©er les nouvelles tables
        create_all_tables(engine)

        # 3. Ajouter donnÃ©es minimales
        seed_minimal_data(engine)

        print()
        print("=" * 70)
        print("âœ… RESET TERMINÃ‰ AVEC SUCCÃˆS")
        print("=" * 70)
        print()
        print("ðŸ“Š Base de donnÃ©es recrÃ©Ã©e avec:")
        print("  â€¢ Toutes les tables en franÃ§ais")
        print("  â€¢ 1 utilisateur de test (Anne)")
        print("  â€¢ 4 ingrÃ©dients de base")
        print()
        print("ðŸš€ Tu peux maintenant:")
        print("  1. Lancer l'app: streamlit run src/app.py")
        print("  2. GÃ©nÃ©rer des recettes avec l'IA")
        print()

    except Exception as e:
        logger.error(f"âŒ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
