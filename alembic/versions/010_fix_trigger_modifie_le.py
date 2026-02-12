"""
Migration 010 - Ajouter colonne updated_at aux tables recettes et modeles_courses

RÃ©vision ID: 010
Down revision: 009
Date: 2026-01-29

ProblÃ¨me: Le trigger update_updated_at_column() essaie de modifier
NEW.updated_at sur recettes et modeles_courses, mais ces colonnes n'existent pas.

Solution: Ajouter la colonne updated_at Ã :
- recettes
- modeles_courses

Ces tables utilisaient modifie_le mais les triggers s'attendent Ã  updated_at.
On ajoute la colonne pour que le trigger fonctionne.

Les autres tables (depenses, budgets, config_meteo, etc.) ont dÃ©jÃ  updated_at.
"""

# Revision identifiers, used by Alembic
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    """
    Ajouter colonne updated_at Ã  recettes et modeles_courses
    """
    from alembic import op
    import sqlalchemy as sa
    
    # Ajouter updated_at Ã  recettes
    op.add_column('recettes', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Ajouter updated_at Ã  modeles_courses  
    op.add_column('modeles_courses', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Initialiser les valeurs existantes avec modifie_le (ou NOW() pour les NULL)
    op.execute("""
        UPDATE recettes
        SET updated_at = COALESCE(modifie_le, NOW())
        WHERE updated_at IS NULL
    """)
    
    op.execute("""
        UPDATE modeles_courses
        SET updated_at = COALESCE(modifie_le, NOW())
        WHERE updated_at IS NULL
    """)
    
    # Maintenant qu'il y a des donnÃ©es, on peut le rendre NOT NULL
    op.alter_column('recettes', 'updated_at', nullable=False)
    op.alter_column('modeles_courses', 'updated_at', nullable=False)


def downgrade():
    """
    Supprimer la colonne updated_at des deux tables
    """
    from alembic import op
    
    op.drop_column('recettes', 'updated_at')
    op.drop_column('modeles_courses', 'updated_at')
