#!/usr/bin/env python3
"""
Script de reset complet de la base Supabase
Usage: python scripts/reset_supabase.py
"""
import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from sqlalchemy import create_engine, text, MetaData
from src.core.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_supabase_url():
    """Récupère l'URL Supabase depuis les secrets"""
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
        logger.error("""
[db]
host = "db.xxxxx.supabase.co"
port = "5432"
name = "postgres"
user = "postgres"
password = "ton_mot_de_passe"
        """)
        sys.exit(1)


def drop_all_tables(engine):
    """Supprime TOUTES les tables (même celles créées par Supabase)"""
    logger.info("🗑️  Suppression de toutes les tables...")

    with engine.connect() as conn:
        # Désactiver les contraintes FK temporairement
        conn.execute(text("SET session_replication_role = 'replica';"))

        # Récupérer toutes les tables du schéma public
        result = conn.execute(text("""
                                   SELECT tablename
                                   FROM pg_tables
                                   WHERE schemaname = 'public'
                                   """))

        tables = [row[0] for row in result]

        # Supprimer chaque table
        for table in tables:
            logger.info(f"  - Suppression: {table}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

        # Réactiver les contraintes
        conn.execute(text("SET session_replication_role = 'origin';"))

        conn.commit()

    logger.info("✅ Toutes les tables supprimées")


def create_all_tables(engine):
    """Crée toutes les tables depuis models.py"""
    logger.info("🏗️  Création des tables depuis models.py...")

    Base.metadata.create_all(bind=engine)

    logger.info("✅ Tables créées")

    # Lister les tables créées
    with engine.connect() as conn:
        result = conn.execute(text("""
                                   SELECT tablename
                                   FROM pg_tables
                                   WHERE schemaname = 'public'
                                   ORDER BY tablename
                                   """))

        tables = [row[0] for row in result]
        logger.info(f"📋 {len(tables)} tables créées:")
        for table in tables:
            logger.info(f"  ✓ {table}")


def seed_minimal_data(engine):
    """Ajoute des données minimales pour tester"""
    logger.info("🌱 Ajout de données de test...")

    with engine.connect() as conn:
        # Utilisateur de test
        conn.execute(text("""
                          INSERT INTO utilisateurs (nom_utilisateur, email, parametres, cree_le, modifie_le)
                          VALUES ('Anne', 'anne@test.fr', '{}', NOW(), NOW())
                          """))

        # Quelques ingrédients de base
        ingredients = [
            ('Tomates', 'kg', 'Légumes'),
            ('Pâtes', 'g', 'Féculents'),
            ('Oeufs', 'pcs', 'Protéines'),
            ('Fromage', 'g', 'Laitier'),
        ]

        for nom, unite, categorie in ingredients:
            conn.execute(text("""
                              INSERT INTO ingredients (nom, unite, categorie, cree_le)
                              VALUES (:nom, :unite, :categorie, NOW())
                              """), {"nom": nom, "unite": unite, "categorie": categorie})

        conn.commit()

    logger.info("✅ Données de test ajoutées")


def main():
    """Point d'entrée principal"""
    print("=" * 70)
    print("🔥 RESET COMPLET DE LA BASE SUPABASE")
    print("=" * 70)
    print()
    print("⚠️  ATTENTION: Cette action est IRRÉVERSIBLE !")
    print("   Toutes les données seront DÉFINITIVEMENT SUPPRIMÉES.")
    print()

    # Demander confirmation
    confirmation = input("Taper 'RESET' en majuscules pour confirmer: ")

    if confirmation != "RESET":
        print("❌ Annulé")
        sys.exit(0)

    print()
    logger.info("Démarrage du reset...")

    try:
        # Connexion
        database_url = get_supabase_url()
        engine = create_engine(
            database_url,
            echo=False,
            connect_args={
                "connect_timeout": 10,
                "sslmode": "require"
            }
        )

        # Test connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Connexion Supabase OK")

        # 1. Supprimer toutes les tables
        drop_all_tables(engine)

        # 2. Créer les nouvelles tables
        create_all_tables(engine)

        # 3. Ajouter données minimales
        seed_minimal_data(engine)

        print()
        print("=" * 70)
        print("✅ RESET TERMINÉ AVEC SUCCÈS")
        print("=" * 70)
        print()
        print("📊 Base de données recréée avec:")
        print("  • Toutes les tables en français")
        print("  • 1 utilisateur de test (Anne)")
        print("  • 4 ingrédients de base")
        print()
        print("🚀 Tu peux maintenant:")
        print("  1. Lancer l'app: streamlit run src/app.py")
        print("  2. Générer des recettes avec l'IA")
        print()

    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()