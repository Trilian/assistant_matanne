"""Add batch cooking tables

Revision ID: 013
Revises: 012
Create Date: 2026-02-01 14:00:00.000000

Tables crÃ©Ã©es:
- config_batch_cooking: Configuration utilisateur
- sessions_batch_cooking: Sessions de batch cooking
- etapes_batch_cooking: Ã‰tapes d'une session
- preparations_batch: PrÃ©parations stockÃ©es

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TABLE: config_batch_cooking
    # Configuration singleton pour le batch cooking
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    op.create_table(
        'config_batch_cooking',
        sa.Column('id', sa.Integer(), primary_key=True),
        # Jours prÃ©fÃ©rÃ©s (JSON: [0, 6] pour lundi et dimanche)
        sa.Column('jours_batch', postgresql.JSONB(), default=lambda: [6]),
        sa.Column('heure_debut_preferee', sa.Time(), default=sa.text("'10:00:00'")),
        sa.Column('duree_max_session', sa.Integer(), default=180),
        # Mode famille
        sa.Column('avec_jules_par_defaut', sa.Boolean(), default=True),
        # Ã‰quipement (JSON: ["cookeo", "airfryer", ...])
        sa.Column('robots_disponibles', postgresql.JSONB(), default=lambda: ["four", "plaques"]),
        # PrÃ©fÃ©rences stockage
        sa.Column('preferences_stockage', postgresql.JSONB(), nullable=True),
        # Objectifs
        sa.Column('objectif_portions_semaine', sa.Integer(), default=20),
        sa.Column('notes', sa.Text(), nullable=True),
        # Timestamps
        sa.Column('cree_le', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('modifie_le', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TABLE: sessions_batch_cooking
    # Sessions de batch cooking planifiÃ©es/en cours/terminÃ©es
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    op.create_table(
        'sessions_batch_cooking',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nom', sa.String(200), nullable=False),
        # Planning temporel
        sa.Column('date_session', sa.Date(), nullable=False, index=True),
        sa.Column('heure_debut', sa.Time(), nullable=True),
        sa.Column('heure_fin', sa.Time(), nullable=True),
        sa.Column('duree_estimee', sa.Integer(), default=120),
        sa.Column('duree_reelle', sa.Integer(), nullable=True),
        # Statut
        sa.Column('statut', sa.String(20), default='planifiee', index=True),
        # Mode famille
        sa.Column('avec_jules', sa.Boolean(), default=False),
        # Liens
        sa.Column('planning_id', sa.Integer(), 
                  sa.ForeignKey('plannings.id', ondelete='SET NULL'), 
                  nullable=True, index=True),
        # DonnÃ©es session (JSON)
        sa.Column('recettes_selectionnees', postgresql.JSONB(), nullable=True),
        sa.Column('robots_utilises', postgresql.JSONB(), nullable=True),
        # Notes
        sa.Column('notes_avant', sa.Text(), nullable=True),
        sa.Column('notes_apres', sa.Text(), nullable=True),
        # IA
        sa.Column('genere_par_ia', sa.Boolean(), default=False),
        # MÃ©triques
        sa.Column('nb_portions_preparees', sa.Integer(), default=0),
        sa.Column('nb_recettes_completees', sa.Integer(), default=0),
        # Timestamps
        sa.Column('cree_le', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('modifie_le', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Index composÃ© pour recherche par date et statut
    op.create_index(
        'idx_session_date_statut', 
        'sessions_batch_cooking', 
        ['date_session', 'statut']
    )

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TABLE: etapes_batch_cooking
    # Ã‰tapes d'une session avec gestion de parallÃ©lisation
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    op.create_table(
        'etapes_batch_cooking',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.Integer(), 
                  sa.ForeignKey('sessions_batch_cooking.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('recette_id', sa.Integer(),
                  sa.ForeignKey('recettes.id', ondelete='SET NULL'),
                  nullable=True, index=True),
        # Ordre et parallÃ©lisation
        sa.Column('ordre', sa.Integer(), nullable=False),
        sa.Column('groupe_parallele', sa.Integer(), default=0),
        # Contenu
        sa.Column('titre', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        # Timing
        sa.Column('duree_minutes', sa.Integer(), default=10),
        sa.Column('duree_reelle', sa.Integer(), nullable=True),
        # Ã‰quipement (JSON: ["cookeo", "four"])
        sa.Column('robots_requis', postgresql.JSONB(), nullable=True),
        # CaractÃ©ristiques
        sa.Column('est_supervision', sa.Boolean(), default=False),
        sa.Column('alerte_bruit', sa.Boolean(), default=False),
        sa.Column('temperature', sa.Integer(), nullable=True),
        # Statut et timing rÃ©el
        sa.Column('statut', sa.String(20), default='a_faire'),
        sa.Column('heure_debut', sa.DateTime(), nullable=True),
        sa.Column('heure_fin', sa.DateTime(), nullable=True),
        # Notes
        sa.Column('notes', sa.Text(), nullable=True),
        # Timer
        sa.Column('timer_actif', sa.Boolean(), default=False),
    )

    # Index composÃ© pour recherche par session et ordre
    op.create_index(
        'idx_etape_session_ordre',
        'etapes_batch_cooking',
        ['session_id', 'ordre']
    )

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TABLE: preparations_batch
    # PrÃ©parations stockÃ©es issues du batch cooking
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    op.create_table(
        'preparations_batch',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.Integer(),
                  sa.ForeignKey('sessions_batch_cooking.id', ondelete='SET NULL'),
                  nullable=True, index=True),
        sa.Column('recette_id', sa.Integer(),
                  sa.ForeignKey('recettes.id', ondelete='SET NULL'),
                  nullable=True, index=True),
        # Identification
        sa.Column('nom', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        # Portions
        sa.Column('portions_initiales', sa.Integer(), nullable=False, default=4),
        sa.Column('portions_restantes', sa.Integer(), nullable=False, default=4),
        # Dates
        sa.Column('date_preparation', sa.Date(), nullable=False, index=True),
        sa.Column('date_peremption', sa.Date(), nullable=False, index=True),
        # Stockage
        sa.Column('localisation', sa.String(50), default='frigo', index=True),
        sa.Column('container', sa.String(100), nullable=True),
        sa.Column('etagere', sa.String(50), nullable=True),
        # Utilisation planifiÃ©e (JSON: [repas_id, ...])
        sa.Column('repas_attribues', postgresql.JSONB(), nullable=True),
        # MÃ©tadonnÃ©es
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('photo_url', sa.String(500), nullable=True),
        # Statut
        sa.Column('consomme', sa.Boolean(), default=False, index=True),
        # Timestamps
        sa.Column('cree_le', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('modifie_le', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Index composÃ©s pour les requÃªtes frÃ©quentes
    op.create_index(
        'idx_prep_localisation_peremption',
        'preparations_batch',
        ['localisation', 'date_peremption']
    )
    op.create_index(
        'idx_prep_consomme_peremption',
        'preparations_batch',
        ['consomme', 'date_peremption']
    )


def downgrade():
    # Supprimer les index d'abord
    op.drop_index('idx_prep_consomme_peremption', table_name='preparations_batch')
    op.drop_index('idx_prep_localisation_peremption', table_name='preparations_batch')
    op.drop_index('idx_etape_session_ordre', table_name='etapes_batch_cooking')
    op.drop_index('idx_session_date_statut', table_name='sessions_batch_cooking')
    
    # Supprimer les tables dans l'ordre inverse (dÃ©pendances)
    op.drop_table('preparations_batch')
    op.drop_table('etapes_batch_cooking')
    op.drop_table('sessions_batch_cooking')
    op.drop_table('config_batch_cooking')
