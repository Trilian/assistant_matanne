"""
Migration Alembic - Refactoring v2.1

Migration complète pour la nouvelle architecture :
- Nouveaux modèles Planning/Repas
- Index optimisés
- Contraintes mises à jour
"""

# revision identifiers, used by Alembic.
revision = '20260108_refactoring_v21'
down_revision = '20251204_5638b60b96c2_maj'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    """Mise à jour vers architecture v2.1"""

    # ═══════════════════════════════════════════════════════════
    # 1. TABLES PLANNING (si n'existent pas)
    # ═══════════════════════════════════════════════════════════

    # Vérifier si plannings existe déjà
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'plannings' not in existing_tables:
        op.create_table(
            'plannings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nom', sa.String(length=200), nullable=False),
            sa.Column('semaine_debut', sa.Date(), nullable=False),
            sa.Column('semaine_fin', sa.Date(), nullable=False),
            sa.Column('actif', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('genere_par_ia', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('cree_le', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id', name='pk_plannings')
        )

        op.create_index('ix_semaine_debut', 'plannings', ['semaine_debut'])
        op.create_index('ix_actif', 'plannings', ['actif'])

    if 'repas' not in existing_tables:
        op.create_table(
            'repas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('planning_id', sa.Integer(), nullable=False),
            sa.Column('recette_id', sa.Integer(), nullable=True),
            sa.Column('date_repas', sa.Date(), nullable=False),
            sa.Column('type_repas', sa.String(length=50), nullable=False, server_default='dîner'),
            sa.Column('portion_ajustee', sa.Integer(), nullable=True),
            sa.Column('prepare', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['planning_id'], ['plannings.id'],
                                   name='fk_repas_planning_id_plannings', ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['recette_id'], ['recettes.id'],
                                   name='fk_repas_recette_id_recettes', ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id', name='pk_repas')
        )

        op.create_index('ix_planning_id', 'repas', ['planning_id'])
        op.create_index('ix_date_repas', 'repas', ['date_repas'])
        op.create_index('ix_type_repas', 'repas', ['type_repas'])

    # ═══════════════════════════════════════════════════════════
    # 2. INDEX OPTIMISÉS (si manquants)
    # ═══════════════════════════════════════════════════════════

    # Recettes
    try:
        op.create_index('ix_recettes_type_repas', 'recettes', ['type_repas'], if_not_exists=True)
        op.create_index('ix_recettes_saison', 'recettes', ['saison'], if_not_exists=True)
        op.create_index('ix_recettes_difficulte', 'recettes', ['difficulte'], if_not_exists=True)
        op.create_index('ix_recettes_est_rapide', 'recettes', ['est_rapide'], if_not_exists=True)
    except:
        pass

    # Inventaire
    try:
        op.create_index('ix_inventaire_emplacement', 'inventaire', ['emplacement'], if_not_exists=True)
        op.create_index('ix_inventaire_date_peremption', 'inventaire', ['date_peremption'], if_not_exists=True)
    except:
        pass

    # Courses
    try:
        op.create_index('ix_liste_courses_achete', 'liste_courses', ['achete'], if_not_exists=True)
        op.create_index('ix_liste_courses_priorite', 'liste_courses', ['priorite'], if_not_exists=True)
    except:
        pass


def downgrade():
    """Retour à l'architecture précédente"""

    # Supprimer tables planning si elles existent
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'repas' in existing_tables:
        op.drop_table('repas')

    if 'plannings' in existing_tables:
        op.drop_table('plannings')

    # Supprimer index
    try:
        op.drop_index('ix_recettes_type_repas', 'recettes')
        op.drop_index('ix_recettes_saison', 'recettes')
        op.drop_index('ix_recettes_difficulte', 'recettes')
        op.drop_index('ix_recettes_est_rapide', 'recettes')
        op.drop_index('ix_inventaire_emplacement', 'inventaire')
        op.drop_index('ix_inventaire_date_peremption', 'inventaire')
        op.drop_index('ix_liste_courses_achete', 'liste_courses')
        op.drop_index('ix_liste_courses_priorite', 'liste_courses')
    except:
        pass

