"""Add jeux tables (paris sportifs & loto)

Revision ID: 012
Revises: 011
Create Date: 2026-02-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    # ═══════════════════════════════════════════════════════════
    # TABLE: jeux_equipes
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        'jeux_equipes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nom', sa.String(100), nullable=False),
        sa.Column('nom_court', sa.String(50), nullable=True),
        sa.Column('championnat', sa.String(50), nullable=False),
        sa.Column('pays', sa.String(50), nullable=True),
        sa.Column('logo_url', sa.String(255), nullable=True),
        # Stats agrégées
        sa.Column('matchs_joues', sa.Integer(), default=0),
        sa.Column('victoires', sa.Integer(), default=0),
        sa.Column('nuls', sa.Integer(), default=0),
        sa.Column('defaites', sa.Integer(), default=0),
        sa.Column('buts_marques', sa.Integer(), default=0),
        sa.Column('buts_encaisses', sa.Integer(), default=0),
        # Méta
        sa.Column('cree_le', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('modifie_le', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Index pour recherche par championnat
    op.create_index('ix_jeux_equipes_championnat', 'jeux_equipes', ['championnat'])

    # ═══════════════════════════════════════════════════════════
    # TABLE: jeux_matchs
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        'jeux_matchs',
        sa.Column('id', sa.Integer(), primary_key=True),
        # Équipes
        sa.Column('equipe_domicile_id', sa.Integer(), sa.ForeignKey('jeux_equipes.id'), nullable=False),
        sa.Column('equipe_exterieur_id', sa.Integer(), sa.ForeignKey('jeux_equipes.id'), nullable=False),
        # Infos match
        sa.Column('championnat', sa.String(50), nullable=False),
        sa.Column('journee', sa.Integer(), nullable=True),
        sa.Column('date_match', sa.Date(), nullable=False),
        sa.Column('heure', sa.String(5), nullable=True),
        # Résultat
        sa.Column('score_domicile', sa.Integer(), nullable=True),
        sa.Column('score_exterieur', sa.Integer(), nullable=True),
        sa.Column('resultat', sa.String(10), nullable=True),
        sa.Column('joue', sa.Boolean(), default=False),
        # Cotes
        sa.Column('cote_domicile', sa.Float(), nullable=True),
        sa.Column('cote_nul', sa.Float(), nullable=True),
        sa.Column('cote_exterieur', sa.Float(), nullable=True),
        # Prédiction IA
        sa.Column('prediction_resultat', sa.String(10), nullable=True),
        sa.Column('prediction_proba_dom', sa.Float(), nullable=True),
        sa.Column('prediction_proba_nul', sa.Float(), nullable=True),
        sa.Column('prediction_proba_ext', sa.Float(), nullable=True),
        sa.Column('prediction_confiance', sa.Float(), nullable=True),
        sa.Column('prediction_raison', sa.Text(), nullable=True),
        # Méta
        sa.Column('cree_le', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('modifie_le', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Index pour recherche par date
    op.create_index('ix_jeux_matchs_date', 'jeux_matchs', ['date_match'])
    op.create_index('ix_jeux_matchs_championnat', 'jeux_matchs', ['championnat'])

    # ═══════════════════════════════════════════════════════════
    # TABLE: jeux_paris_sportifs
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        'jeux_paris_sportifs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('match_id', sa.Integer(), sa.ForeignKey('jeux_matchs.id'), nullable=False),
        # Détails du pari
        sa.Column('type_pari', sa.String(30), default='1N2'),
        sa.Column('prediction', sa.String(20), nullable=False),
        sa.Column('cote', sa.Float(), nullable=False),
        sa.Column('mise', sa.Numeric(10, 2), default=0),
        # Résultat
        sa.Column('statut', sa.String(20), default='en_attente'),
        sa.Column('gain', sa.Numeric(10, 2), nullable=True),
        # Tracking
        sa.Column('est_virtuel', sa.Boolean(), default=True),
        sa.Column('confiance_prediction', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        # Méta
        sa.Column('cree_le', sa.DateTime(), server_default=sa.func.now()),
    )
    
    op.create_index('ix_jeux_paris_statut', 'jeux_paris_sportifs', ['statut'])

    # ═══════════════════════════════════════════════════════════
    # TABLE: jeux_tirages_loto
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        'jeux_tirages_loto',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date_tirage', sa.Date(), nullable=False, unique=True),
        # Numéros
        sa.Column('numero_1', sa.Integer(), nullable=False),
        sa.Column('numero_2', sa.Integer(), nullable=False),
        sa.Column('numero_3', sa.Integer(), nullable=False),
        sa.Column('numero_4', sa.Integer(), nullable=False),
        sa.Column('numero_5', sa.Integer(), nullable=False),
        sa.Column('numero_chance', sa.Integer(), nullable=False),
        # Infos jackpot
        sa.Column('jackpot_euros', sa.Integer(), nullable=True),
        sa.Column('gagnants_rang1', sa.Integer(), nullable=True),
        # Méta
        sa.Column('cree_le', sa.DateTime(), server_default=sa.func.now()),
    )
    
    op.create_index('ix_jeux_tirages_date', 'jeux_tirages_loto', ['date_tirage'])

    # ═══════════════════════════════════════════════════════════
    # TABLE: jeux_grilles_loto
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        'jeux_grilles_loto',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tirage_id', sa.Integer(), sa.ForeignKey('jeux_tirages_loto.id'), nullable=True),
        # Numéros choisis
        sa.Column('numero_1', sa.Integer(), nullable=False),
        sa.Column('numero_2', sa.Integer(), nullable=False),
        sa.Column('numero_3', sa.Integer(), nullable=False),
        sa.Column('numero_4', sa.Integer(), nullable=False),
        sa.Column('numero_5', sa.Integer(), nullable=False),
        sa.Column('numero_chance', sa.Integer(), nullable=False),
        # Tracking
        sa.Column('est_virtuelle', sa.Boolean(), default=True),
        sa.Column('source_prediction', sa.String(50), default='manuel'),
        sa.Column('mise', sa.Numeric(10, 2), default=2.20),
        # Résultat
        sa.Column('numeros_trouves', sa.Integer(), nullable=True),
        sa.Column('chance_trouvee', sa.Boolean(), nullable=True),
        sa.Column('gain', sa.Numeric(10, 2), nullable=True),
        sa.Column('rang', sa.Integer(), nullable=True),
        # Méta
        sa.Column('date_creation', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: jeux_stats_loto
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        'jeux_stats_loto',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date_calcul', sa.DateTime(), server_default=sa.func.now()),
        # Stats (JSON)
        sa.Column('frequences_numeros', sa.JSON(), nullable=True),
        sa.Column('frequences_chance', sa.JSON(), nullable=True),
        sa.Column('numeros_chauds', sa.JSON(), nullable=True),
        sa.Column('numeros_froids', sa.JSON(), nullable=True),
        sa.Column('numeros_retard', sa.JSON(), nullable=True),
        # Patterns
        sa.Column('somme_moyenne', sa.Float(), nullable=True),
        sa.Column('paires_frequentes', sa.JSON(), nullable=True),
        # Méta
        sa.Column('nb_tirages_analyses', sa.Integer(), default=0),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: jeux_historique
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        'jeux_historique',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('type_jeu', sa.String(20), nullable=False),
        # Cumuls du jour
        sa.Column('nb_paris', sa.Integer(), default=0),
        sa.Column('mises_totales', sa.Numeric(10, 2), default=0),
        sa.Column('gains_totaux', sa.Numeric(10, 2), default=0),
        sa.Column('paris_gagnes', sa.Integer(), default=0),
        sa.Column('paris_perdus', sa.Integer(), default=0),
        # Performance IA
        sa.Column('predictions_correctes', sa.Integer(), default=0),
        sa.Column('predictions_totales', sa.Integer(), default=0),
        # Méta
        sa.Column('cree_le', sa.DateTime(), server_default=sa.func.now()),
    )
    
    op.create_index('ix_jeux_historique_date_type', 'jeux_historique', ['date', 'type_jeu'])


def downgrade():
    # Supprimer les tables dans l'ordre inverse (dépendances)
    op.drop_table('jeux_historique')
    op.drop_table('jeux_stats_loto')
    op.drop_table('jeux_grilles_loto')
    op.drop_table('jeux_tirages_loto')
    op.drop_table('jeux_paris_sportifs')
    op.drop_table('jeux_matchs')
    op.drop_table('jeux_equipes')
