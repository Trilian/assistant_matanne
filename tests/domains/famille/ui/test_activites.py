"""
Tests minimaux pour src/domains/famille/ui/activites.py
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

import src.domains.famille.ui.activites as activites
from src.core.models.famille import FamilyActivity

@pytest.fixture
def fake_activity_dict():
    return {
        "titre": "Sortie Parc",
        "description": "Sortie au parc",
        "type_activite": "parc",
        "date_prevue": date.today(),
        "duree_heures": 2.0,
        "lieu": "Parc Central",
        "qui_participe": ["Jules", "Anne"],
        "age_minimal_recommande": 24,
        "cout_estime": 20.0,
        "cout_reel": None,
        "statut": "planifié",
        "notes": None,
        "cree_le": date.today(),
    }

@pytest.fixture(autouse=True)
def clean_db(db):
    db.query(FamilyActivity).delete()
    db.commit()

def test_import_activites_ui():
    import src.domains.famille.ui.activites
    assert src.domains.famille.ui.activites.__name__ == "src.domains.famille.ui.activites"

def test_ajouter_activite(db, fake_activity_dict):
    with patch("src.domains.famille.ui.activites.get_session", return_value=MagicMock(__enter__=lambda s: db, __exit__=lambda s, a, b, c: None)):
        ok = activites.ajouter_activite(
            "Sortie Parc", "parc", date.today(), 2.0, "Parc Central", ["Jules", "Anne"], 20.0, notes="Test",)
        assert ok
        assert db.query(FamilyActivity).filter_by(titre="Sortie Parc").first() is not None

def test_marquer_terminee(db, fake_activity_dict):
    activity = FamilyActivity(**fake_activity_dict)
    db.add(activity)
    db.commit()
    with patch("src.domains.famille.ui.activites.get_session", return_value=MagicMock(__enter__=lambda s: db, __exit__=lambda s, a, b, c: None)):
        activites.marquer_terminee(activity.id, cout_reel=18.0, notes="Fait")
        db.refresh(activity)
        assert activity.statut == "terminé"
        assert activity.cout_reel == 18.0
