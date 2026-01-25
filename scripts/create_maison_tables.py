#!/usr/bin/env python3
"""
Script d'exécution des migrations SQL pour Supabase
Crée les tables du module Maison automatiquement
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Exécute les migrations SQL"""
    
    try:
        # Import tardif pour meilleure gestion des erreurs
        from src.core.database import obtenir_moteur
        from src.core.models import Base
        
        logger.info("🔧 Création des tables du module Maison...")
        logger.info("═" * 60)
        
        # Obtenir le moteur
        moteur = obtenir_moteur()
        logger.info("✅ Connexion BD établie")
        
        # Créer toutes les tables
        logger.info("📋 Création des tables...")
        Base.metadata.create_all(bind=moteur)
        logger.info("✅ Tables créées avec succès!")
        
        # Vérifier les tables
        from sqlalchemy import inspect
        inspector = inspect(moteur)
        tables = inspector.get_table_names()
        
        maison_tables = [
            "projects", 
            "project_tasks", 
            "garden_items", 
            "garden_logs",
            "routines",
            "routine_tasks"
        ]
        
        logger.info("═" * 60)
        logger.info("📊 Tables créées :")
        
        for table in maison_tables:
            if table in tables:
                cols = len(inspector.get_columns(table))
                logger.info(f"  ✅ {table:20} ({cols} colonnes)")
            else:
                logger.warning(f"  ⚠️  {table:20} (manquante)")
        
        logger.info("═" * 60)
        logger.info("✨ Migration complète!")
        logger.info("")
        logger.info("Prochaines étapes:")
        logger.info("1. Relancer l'app : streamlit run src/app.py")
        logger.info("2. Naviguer vers 🏠 Maison")
        logger.info("3. Créer projets, plantes, routines")
        logger.info("")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        logger.error("")
        logger.error("Vérifier:")
        logger.error("1. .env.local contient DATABASE_URL")
        logger.error("2. Supabase accessible")
        logger.error("3. Credentials correctes")
        logger.error("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
