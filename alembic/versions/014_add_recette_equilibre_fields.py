"""Add est_vegetarien and type_proteines fields to recettes

Revision ID: 014_add_recette_equilibre_fields
Revises: 013_add_batch_cooking_tables
Create Date: 2026-02-01 18:47:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014_add_recette_equilibre_fields'
down_revision = '013_add_batch_cooking_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQL direct pour ajouter les colonnes Ã  recettes
    
    # 1. Ajouter colonne est_vegetarien avec valeur par dÃ©faut false
    op.execute("""
        ALTER TABLE recettes 
        ADD COLUMN est_vegetarien BOOLEAN NOT NULL DEFAULT false;
    """)
    
    # 2. CrÃ©er index sur est_vegetarien pour les filtres
    op.execute("""
        CREATE INDEX idx_recettes_est_vegetarien ON recettes (est_vegetarien);
    """)
    
    # 3. Ajouter colonne type_proteines pour catÃ©goriser les protÃ©ines
    # Values: 'poisson', 'viande', 'volaille', 'vegetarien', 'mixte'
    op.execute("""
        ALTER TABLE recettes 
        ADD COLUMN type_proteines VARCHAR(100) NULL;
    """)


def downgrade() -> None:
    # Supprimer dans l'ordre inverse
    
    # 1. Supprimer la colonne type_proteines
    op.execute("""
        ALTER TABLE recettes 
        DROP COLUMN IF EXISTS type_proteines;
    """)
    
    # 2. Supprimer l'index
    op.execute("""
        DROP INDEX IF EXISTS idx_recettes_est_vegetarien;
    """)
    
    # 3. Supprimer la colonne est_vegetarien
    op.execute("""
        ALTER TABLE recettes 
        DROP COLUMN IF EXISTS est_vegetarien;
    """)
