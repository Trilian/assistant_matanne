"""
Migration 007 - Ajouter modÃ¨les pour module Famille refondÃ©
- Milestone (jalons Jules)
- FamilyActivity (activitÃ©s familiales)
- HealthRoutine + HealthObjective + HealthEntry (santÃ©/sport)
- FamilyBudget (budget famille)
"""


# Migration basique: si les tables n'existent pas, on les crÃ©e via ORM
def upgrade():
    # Les tables seront crÃ©Ã©es via SQLAlchemy ORM lors du premier dÃ©marrage
    # car get_db_context() appelle create_all()
    pass


def downgrade():
    # Ã€ implÃ©menter si besoin de rollback
    pass
