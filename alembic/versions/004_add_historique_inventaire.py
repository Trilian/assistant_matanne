"""Add HistoriqueInventaire table for tracking inventory modifications.

Revision ID: 004
Revises: 003
Create Date: 2026-01-18 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create historique_inventaire table
    op.create_table(
        'historique_inventaire',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('type_modification', sa.String(length=50), nullable=False),
        sa.Column('quantite_avant', sa.Float(), nullable=True),
        sa.Column('quantite_apres', sa.Float(), nullable=True),
        sa.Column('quantite_min_avant', sa.Float(), nullable=True),
        sa.Column('quantite_min_apres', sa.Float(), nullable=True),
        sa.Column('date_peremption_avant', sa.Date(), nullable=True),
        sa.Column('date_peremption_apres', sa.Date(), nullable=True),
        sa.Column('emplacement_avant', sa.String(length=100), nullable=True),
        sa.Column('emplacement_apres', sa.String(length=100), nullable=True),
        sa.Column('date_modification', sa.DateTime(), nullable=False),
        sa.Column('utilisateur', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['inventaire.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_historique_inventaire_article_id', 'historique_inventaire', ['article_id'])
    op.create_index('ix_historique_inventaire_ingredient_id', 'historique_inventaire', ['ingredient_id'])
    op.create_index('ix_historique_inventaire_type_modification', 'historique_inventaire', ['type_modification'])
    op.create_index('ix_historique_inventaire_date_modification', 'historique_inventaire', ['date_modification'])


def downgrade() -> None:
    op.drop_index('ix_historique_inventaire_date_modification', table_name='historique_inventaire')
    op.drop_index('ix_historique_inventaire_type_modification', table_name='historique_inventaire')
    op.drop_index('ix_historique_inventaire_ingredient_id', table_name='historique_inventaire')
    op.drop_index('ix_historique_inventaire_article_id', table_name='historique_inventaire')
    op.drop_table('historique_inventaire')
