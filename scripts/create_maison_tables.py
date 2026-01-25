#!/usr/bin/env python3
"""
Script pour créer TOUTES les tables de la base de données
Exécute la création de tables depuis les modèles SQLAlchemy
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Crée TOUTES les tables de la base de données"""
    
    try:
        logger.info("📊 Initialisation de la base de données...")
        
        # Import tardif pour meilleure gestion des erreurs
        from src.core.database import obtenir_moteur
        from src.core.models import Base
        
        logger.info("═" * 70)
        logger.info("🔧 CRÉATION DE TOUTES LES TABLES")
        logger.info("═" * 70)
        
        # Obtenir le moteur
        moteur = obtenir_moteur()
        logger.info("✅ Connexion BD établie")
        
        # Créer TOUTES les tables
        logger.info("📋 Création de TOUTES les tables...")
        Base.metadata.create_all(bind=moteur)
        logger.info("✅ Tables créées avec succès!")
        
        # Vérifier les tables
        from sqlalchemy import inspect
        inspector = inspect(moteur)
        tables = inspector.get_table_names()
        
        # Tables attendues (groupées par module)
        tables_par_module = {
            "🍽️  RECETTES": [
                "recettes", "ingredients", "recette_ingredients", 
                "etapes_recettes", "versions_recettes"
            ],
            "🛍️  COURSES": [
                "articles_courses", "articles_inventaire"
            ],
            "👨‍👩‍👧‍👦 FAMILLE": [
                "child_profiles", "wellbeing_entries", "milestones", 
                "family_activities", "health_routines", "health_objectives"
            ],
            "🏠 MAISON": [
                "projects", "project_tasks", "garden_items", "garden_logs",
                "routines", "routine_tasks"
            ],
            "📅 PLANNING": [
                "calendar_events", "plannings", "repas"
            ],
            "👨‍🍳 BATCH COOKING": [
                "batch_meals"
            ],
            "💰 BUDGET": [
                "family_budgets"
            ]
        }
        
        logger.info("═" * 70)
        logger.info("📊 VÉRIFICATION DES TABLES CRÉÉES")
        logger.info("═" * 70)
        
        total_attendues = 0
        total_creees = 0
        
        for module, table_list in tables_par_module.items():
            logger.info(f"\n{module}")
            for table_name in table_list:
                total_attendues += 1
                if table_name in tables:
                    cols = len(inspector.get_columns(table_name))
                    logger.info(f"  ✅ {table_name:30} ({cols:2d} colonnes)")
                    total_creees += 1
                else:
                    logger.warning(f"  ⚠️  {table_name:30} (manquante)")
        
        logger.info("\n" + "═" * 70)
        logger.info(f"🎉 RÉSUMÉ: {total_creees}/{total_attendues} tables créées")
        logger.info(f"📊 Total en base: {len(tables)} tables")
        logger.info("═" * 70)
        
        if total_creees == total_attendues:
            logger.info("✨ SUCCÈS! Toutes les tables sont créées.")
            return 0
        else:
            logger.warning(f"⚠️  {total_attendues - total_creees} table(s) manquante(s)")
            return 1
        
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
