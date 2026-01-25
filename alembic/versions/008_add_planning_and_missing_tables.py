"""
Migration 008 - Ajouter les tables manquantes
- calendar_events (planification)
- batch_meals (batch cooking)
- family_budget (budget famille)
Toutes les autres tables doivent déjà exister
"""

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Float, Boolean,
    ForeignKey, Index, CheckConstraint, create_engine, event
)
from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Créer les tables manquantes"""
    
    # Table calendar_events
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titre', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('date_debut', sa.DateTime(), nullable=False),
        sa.Column('date_fin', sa.DateTime(), nullable=True),
        sa.Column('lieu', sa.String(200), nullable=True),
        sa.Column('type_event', sa.String(50), nullable=False, server_default='autre'),
        sa.Column('couleur', sa.String(20), nullable=True),
        sa.Column('rappel_avant_minutes', sa.Integer(), nullable=True),
        sa.Column('cree_le', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_calendar_events_date_debut', 'calendar_events', ['date_debut'])
    op.create_index('idx_calendar_events_type_event', 'calendar_events', ['type_event'])
    op.create_index('idx_date_type', 'calendar_events', ['date_debut', 'type_event'])
    op.create_index('idx_date_range', 'calendar_events', ['date_debut', 'date_fin'])
    
    # Table batch_meals
    op.create_table(
        'batch_meals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recette_id', sa.Integer(), nullable=True),
        sa.Column('nom', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('portions', sa.Integer(), nullable=True),
        sa.Column('date_preparation', sa.Date(), nullable=False),
        sa.Column('jours_conservation', sa.Integer(), nullable=True),
        sa.Column('conteneurs_utilises', sa.Integer(), nullable=True),
        sa.Column('cout_total', sa.Float(), nullable=True),
        sa.Column('cree_le', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['recette_id'], ['recettes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_batch_meals_recette_id', 'batch_meals', ['recette_id'])
    op.create_index('idx_batch_meals_date_preparation', 'batch_meals', ['date_preparation'])
    
    # Table family_budgets
    op.create_table(
        'family_budgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titre', sa.String(200), nullable=False),
        sa.Column('montant_budget', sa.Float(), nullable=False),
        sa.Column('montant_utilise', sa.Float(), nullable=False, server_default='0'),
        sa.Column('categorie', sa.String(100), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=True),
        sa.Column('couleur', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('cree_le', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_family_budgets_categorie', 'family_budgets', ['categorie'])
    op.create_index('idx_family_budgets_date_debut', 'family_budgets', ['date_debut'])


def downgrade():
    """Supprimer les tables créées"""
    op.drop_table('family_budgets')
    op.drop_table('batch_meals')
    op.drop_table('calendar_events')
