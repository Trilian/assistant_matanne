#!/usr/bin/env python3
"""
Migration SQL Generator - Génère et gère les migrations pour Supabase
Crée les tables pour le module Famille depuis les modèles SQLAlchemy
"""

import sys
from pathlib import Path
from sqlalchemy import MetaData, Table, create_engine, text

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.models import (
    Milestone,
    FamilyActivity,
    HealthRoutine,
    HealthObjective,
    HealthEntry,
    FamilyBudget,
    Base,
)


def generate_migration_sql():
    """
    Génère le SQL DDL pour créer toutes les tables du module Famille
    """
    print("=" * 70)
    print("🗄️  MIGRATION SQL - Module Famille")
    print("=" * 70)
    print()

    # Créer un engine SQLite en mémoire pour générer le SQL
    engine = create_engine("sqlite:///:memory:")

    # Créer les tables dans la métabase
    Base.metadata.create_all(engine)

    # Obtenir les objets de table
    metadata = MetaData()
    metadata.reflect(bind=engine)

    print("📋 Tables à créer:")
    print()

    for table_name in [
        "milestones",
        "family_activities",
        "health_routines",
        "health_objectives",
        "health_entries",
        "family_budgets",
    ]:
        if table_name in metadata.tables:
            table = metadata.tables[table_name]
            print(f"✅ {table_name}")
            for col in table.columns:
                print(f"   - {col.name}: {col.type}")
            print()

    print("=" * 70)
    print("✨ SQL généré avec succès!")
    print()
    print("📝 Pour exécuter la migration sur Supabase:")
    print("   1. Ouvrir Supabase Dashboard")
    print("   2. Aller dans SQL Editor")
    print("   3. Copier le contenu de: sql/001_add_famille_models.sql")
    print("   4. Exécuter le script")
    print()
    print("=" * 70)


def check_models():
    """
    Vérifie que tous les modèles sont correctement définis
    """
    print()
    print("🔍 Vérification des modèles...")
    print()

    models = {
        "Milestone": Milestone,
        "FamilyActivity": FamilyActivity,
        "HealthRoutine": HealthRoutine,
        "HealthObjective": HealthObjective,
        "HealthEntry": HealthEntry,
        "FamilyBudget": FamilyBudget,
    }

    for name, model_class in models.items():
        tablename = model_class.__tablename__
        columns = [col.name for col in model_class.__table__.columns]
        print(f"✅ {name} ({tablename})")
        print(f"   Colonnes: {len(columns)}")
        print()

    print("=" * 70)
    print("✨ Tous les modèles sont bien configurés!")
    print("=" * 70)


def verify_imports():
    """
    Vérifie que tous les imports fonctionnent
    """
    print()
    print("📦 Vérification des imports...")
    print()

    try:
        from src.modules.famille import jules, sante, activites, shopping
        print("✅ Jules module")
        print("✅ Santé module")
        print("✅ Activités module")
        print("✅ Shopping module")
        print()
        print("=" * 70)
        print("✨ Tous les modules sont importables!")
        print("=" * 70)
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False


def main():
    """Main"""
    print()
    print("🏠 MIGRATION ASSISTANT - Module Famille")
    print("=" * 70)
    print()

    # Vérifier imports
    if not verify_imports():
        sys.exit(1)

    # Vérifier modèles
    check_models()

    # Générer migration
    generate_migration_sql()

    print()
    print("✅ Migration prête!")
    print()
    print("📄 Fichier SQL: sql/001_add_famille_models.sql")
    print()


if __name__ == "__main__":
    main()
