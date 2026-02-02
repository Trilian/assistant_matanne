"""Add user preferences, recipe feedbacks, openfoodfacts cache and calendar config tables

Revision ID: 016_user_prefs
Revises: 014_add_recette_equilibre_fields
Create Date: 2025-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '016_user_prefs'
down_revision: Union[str, None] = '014_add_recette_equilibre_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Table user_preferences - Préférences familiales pour l'IA
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=False),
        
        # Composition familiale
        sa.Column('nb_adultes', sa.Integer(), server_default='2'),
        sa.Column('nb_enfants', sa.Integer(), server_default='1'),
        sa.Column('jules_present', sa.Boolean(), server_default='true'),
        
        # Contraintes temps
        sa.Column('temps_semaine', sa.Integer(), server_default='30', comment='Minutes max en semaine'),
        sa.Column('temps_weekend', sa.Integer(), server_default='90', comment='Minutes max le weekend'),
        
        # Préférences alimentaires (JSONB arrays)
        sa.Column('aliments_exclus', postgresql.JSONB(astext_type=sa.Text()), server_default='[]'),
        sa.Column('aliments_preferes', postgresql.JSONB(astext_type=sa.Text()), server_default='[]'),
        sa.Column('cuisines_preferees', postgresql.JSONB(astext_type=sa.Text()), server_default='[]'),
        
        # Équipements
        sa.Column('robots_disponibles', postgresql.JSONB(astext_type=sa.Text()), 
                  server_default='["thermomix", "airfryer", "cookeo"]'),
        
        # Métadonnées
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                  onupdate=sa.text('now()')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_preferences_user_id')
    )
    
    # Index pour recherche rapide
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])
    
    # Table recipe_feedbacks - Apprentissage IA des goûts
    op.create_table(
        'recipe_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('recette_id', sa.Integer(), nullable=False),
        
        # Feedback type: like, dislike, neutral
        sa.Column('feedback_type', sa.String(20), nullable=False),
        sa.Column('commentaire', sa.Text(), nullable=True),
        
        # Contexte du feedback
        sa.Column('jules_a_aime', sa.Boolean(), nullable=True, comment='Si Jules était présent et a aimé'),
        sa.Column('contexte', sa.String(50), nullable=True, comment='batch_cooking, semaine, weekend'),
        
        # Métadonnées
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['recette_id'], ['recettes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'recette_id', name='uq_recipe_feedback_user_recette')
    )
    
    # Index pour analyse des préférences
    op.create_index('ix_recipe_feedbacks_user_id', 'recipe_feedbacks', ['user_id'])
    op.create_index('ix_recipe_feedbacks_recette_id', 'recipe_feedbacks', ['recette_id'])
    op.create_index('ix_recipe_feedbacks_feedback_type', 'recipe_feedbacks', ['feedback_type'])
    
    # Table openfoodfacts_cache - Cache des produits scannés
    op.create_table(
        'openfoodfacts_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code_barres', sa.String(50), nullable=False),
        
        # Données produit
        sa.Column('nom_produit', sa.String(255), nullable=True),
        sa.Column('marque', sa.String(100), nullable=True),
        sa.Column('categorie', sa.String(100), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        
        # Nutrition
        sa.Column('nutriscore', sa.String(1), nullable=True),
        sa.Column('ecoscore', sa.String(1), nullable=True),
        sa.Column('nova_group', sa.Integer(), nullable=True),
        sa.Column('nutrition_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        
        # Métadonnées cache
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Date expiration cache (30 jours par défaut)'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code_barres', name='uq_openfoodfacts_cache_barcode')
    )
    
    op.create_index('ix_openfoodfacts_cache_code_barres', 'openfoodfacts_cache', ['code_barres'])
    
    # Table external_calendar_configs - Configuration calendriers externes
    op.create_table(
        'external_calendar_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=False),
        
        # Provider: google, apple, outlook
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('calendar_id', sa.String(255), nullable=True, comment='ID calendrier spécifique'),
        
        # OAuth tokens (chiffrés en production)
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        
        # Sync settings
        sa.Column('sync_enabled', sa.Boolean(), server_default='true'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_direction', sa.String(20), server_default='bidirectional',
                  comment='import_only, export_only, bidirectional'),
        
        # Métadonnées
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                  onupdate=sa.text('now()')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'provider', name='uq_external_calendar_user_provider')
    )
    
    op.create_index('ix_external_calendar_configs_user_id', 'external_calendar_configs', ['user_id'])


def downgrade() -> None:
    # Suppression des tables dans l'ordre inverse
    op.drop_table('external_calendar_configs')
    op.drop_table('openfoodfacts_cache')
    op.drop_table('recipe_feedbacks')
    op.drop_table('user_preferences')
