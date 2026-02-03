"""
Tests minimaux pour src/domains/famille/ui/achats_famille.py
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

import src.domains.famille.ui.achats_famille as achats_famille
from src.core.models.users import FamilyPurchase

@pytest.fixture
def fake_purchase_dict():
    return {
        "nom": "Poussette",
        "description": "Poussette compacte",
        "categorie": "jules_equipement",
        "priorite": "urgent",
        "prix_estime": 200.0,
        "prix_reel": None,
        "url": None,
        "image_url": None,
        "magasin": None,
        "taille": None,
        "age_recommande_mois": None,
        "achete": False,
        "date_achat": None,
        "suggere_par": "anne",
        "notes": None,
        "cree_le": datetime.now(),
        "modifie_le": datetime.now(),
    }

@pytest.fixture(autouse=True)
def clean_db(db):
    db.query(FamilyPurchase).delete()
    db.commit()

def test_create_and_get_purchase(db, fake_purchase_dict):
    purchase = FamilyPurchase(**fake_purchase_dict)
    db.add(purchase)
    db.commit()
    with patch("src.domains.famille.ui.achats_famille.get_db_context", return_value=MagicMock(__enter__=lambda s: db, __exit__=lambda s, a, b, c: None)):
        all_p = achats_famille.get_all_purchases()
        assert any(p.nom == "Poussette" for p in all_p)
        by_cat = achats_famille.get_purchases_by_category("jules_equipement")
        assert any(p.nom == "Poussette" for p in by_cat)
        by_groupe = achats_famille.get_purchases_by_groupe("jules")
        assert any(p.nom == "Poussette" for p in by_groupe)

def test_stats(db, fake_purchase_dict):
    purchase = FamilyPurchase(**fake_purchase_dict)
    db.add(purchase)
    db.commit()
    with patch("src.domains.famille.ui.achats_famille.get_db_context", return_value=MagicMock(__enter__=lambda s: db, __exit__=lambda s, a, b, c: None)):
        stats = achats_famille.get_stats()
        assert stats["en_attente"] >= 1
        assert stats["total_estime"] >= 200

def test_mark_as_bought_and_delete(db, fake_purchase_dict):
    purchase = FamilyPurchase(**fake_purchase_dict)
    db.add(purchase)
    db.commit()
    with patch("src.domains.famille.ui.achats_famille.get_db_context", return_value=MagicMock(__enter__=lambda s: db, __exit__=lambda s, a, b, c: None)):
        achats_famille.mark_as_bought(purchase.id, prix_reel=180.0)
        db.refresh(purchase)
        assert purchase.achete is True
        assert purchase.prix_reel == 180.0
        achats_famille.delete_purchase(purchase.id)
        assert db.query(FamilyPurchase).filter_by(id=purchase.id).first() is None

def test_import_achats_famille_ui():
    import src.domains.famille.ui.achats_famille

def test_render_dashboard(monkeypatch):
    monkeypatch.setattr(achats_famille, "get_stats", lambda: {"en_attente": 1, "achetes": 2, "total_estime": 100, "total_depense": 50, "urgents": 1})
    monkeypatch.setattr(achats_famille.st, "subheader", lambda *a, **k: None)
    monkeypatch.setattr(achats_famille.st, "columns", lambda n: [MagicMock() for _ in range(n)])
    monkeypatch.setattr(achats_famille.st, "metric", lambda *a, **k: None)
    monkeypatch.setattr(achats_famille.st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(achats_famille.st, "write", lambda *a, **k: None)
    monkeypatch.setattr(achats_famille.st, "divider", lambda: None)
    monkeypatch.setattr(achats_famille, "get_db_context", lambda: MagicMock(__enter__=lambda s: [], __exit__=lambda s, a, b, c: None))
    achats_famille.render_dashboard()
