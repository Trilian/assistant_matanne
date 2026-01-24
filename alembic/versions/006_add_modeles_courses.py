"""Add ModeleCourses table for Phase 2 persistent templates.

Revision ID: 006
Revises: 005_add_photos_inventaire.py
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005_add_photos_inventaire'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create modeles_courses and articles_modeles tables."""
    
    # Create modeles_courses table
    op.create_table(
        'modeles_courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('utilisateur_id', sa.String(length=100), nullable=True),
        sa.Column('cree_le', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('modifie_le', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('actif', sa.Boolean(), nullable=False, server_default=True),
        sa.Column('articles_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_modeles_courses')),
    )
    
    # Create indexes
    op.create_index(op.f('ix_modeles_courses_nom'), 'modeles_courses', ['nom'], unique=False)
    op.create_index(op.f('ix_modeles_courses_utilisateur_id'), 'modeles_courses', ['utilisateur_id'], unique=False)
    op.create_index(op.f('ix_modeles_courses_actif'), 'modeles_courses', ['actif'], unique=False)
    
    # Create articles_modeles table
    op.create_table(
        'articles_modeles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('modele_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=True),
        sa.Column('nom_article', sa.String(length=100), nullable=False),
        sa.Column('quantite', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('unite', sa.String(length=20), nullable=False, server_default='pièce'),
        sa.Column('rayon_magasin', sa.String(length=100), nullable=False, server_default='Autre'),
        sa.Column('priorite', sa.String(length=20), nullable=False, server_default='moyenne'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('ordre', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cree_le', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        
        sa.ForeignKeyConstraint(['modele_id'], ['modeles_courses.id'], name=op.f('fk_articles_modeles_modele_id_modeles_courses'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], name=op.f('fk_articles_modeles_ingredient_id_ingredients'), ondelete='SET NULL'),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_articles_modeles')),
        
        # Constraints
        sa.CheckConstraint('quantite > 0', name='ck_article_modele_quantite_positive'),
        sa.CheckConstraint("priorite IN ('haute', 'moyenne', 'basse')", name='ck_article_modele_priorite_valide'),
    )
    
    # Create indexes
    op.create_index(op.f('ix_articles_modeles_modele_id'), 'articles_modeles', ['modele_id'], unique=False)
    op.create_index(op.f('ix_articles_modeles_ingredient_id'), 'articles_modeles', ['ingredient_id'], unique=False)


def downgrade() -> None:
    """Drop modeles_courses and articles_modeles tables."""
    
    op.drop_index(op.f('ix_articles_modeles_ingredient_id'), table_name='articles_modeles')
    op.drop_index(op.f('ix_articles_modeles_modele_id'), table_name='articles_modeles')
    op.drop_table('articles_modeles')
    
    op.drop_index(op.f('ix_modeles_courses_actif'), table_name='modeles_courses')
    op.drop_index(op.f('ix_modeles_courses_utilisateur_id'), table_name='modeles_courses')
    op.drop_index(op.f('ix_modeles_courses_nom'), table_name='modeles_courses')
    op.drop_table('modeles_courses')

