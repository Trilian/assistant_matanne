"""
Migration 007 - Ajouter modèles pour module Famille refondé
- Milestone (jalons Jules)
- FamilyActivity (activités familiales)
- HealthRoutine + HealthObjective + HealthEntry (santé/sport)
- FamilyBudget (budget famille)
"""

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Float, Boolean,
    ForeignKey, CheckConstraint,
    create_engine, MetaData, Table
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

# Migration basique: si les tables n'existent pas, on les crée via ORM
def upgrade():
    # Les tables seront créées via SQLAlchemy ORM lors du premier démarrage
    # car get_db_context() appelle create_all()
    pass

def downgrade():
    # À implémenter si besoin de rollback
    pass