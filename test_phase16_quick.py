"""
Test direct Phase 16 - Recette Service Basic
"""

import sys
sys.path.insert(0, 'd:\\Projet_streamlit\\assistant_matanne')

from src.core.database import get_db_context
from src.core.models import Recette

def test_basic():
    """Test création recette"""
    with get_db_context() as session:
        r = Recette(
            nom="Test Recette",
            description="Test",
            difficulte="facile",
            type_repas="déjeuner",
            portions=4
        )
        session.add(r)
        session.commit()
        
        retrieved = session.query(Recette).filter_by(nom="Test Recette").first()
        assert retrieved is not None
        print(f"✅ Test réussi: {retrieved.nom}")

if __name__ == "__main__":
    try:
        test_basic()
        print("\n✅ Phase 16 peut être exécutée!")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
