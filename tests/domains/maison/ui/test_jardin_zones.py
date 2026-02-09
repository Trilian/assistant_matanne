import importlib
import pytest

# Tests réactivés - prochaine_action est bien présent dans le modèle GardenZone

def test_import_jardin_zones_ui():
    import src.domains.maison.ui.jardin_zones

def test_import_jardin_zones():
    module = importlib.import_module("src.domains.maison.ui.jardin_zones")
    assert module is not None

import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from decimal import Decimal

import src.domains.maison.ui.jardin_zones as jardin_zones
from src.core.models.maison_extended import GardenZone

@pytest.fixture
def fake_zone_dict():
    return {
        "nom": "Zone Test",
        "type_zone": "pelouse",
        "surface_m2": 100,
        "etat_note": 3,
        "etat_description": "Etat ok",
        "objectif": "Avoir une belle pelouse",
        "budget_estime": Decimal("50.0"),
        "prochaine_action": "Tondre",
        "date_prochaine_action": date.today(),
        "photos_url": [],
        # created_at et updated_at ont des defaults dans le modèle
    }

@pytest.fixture(autouse=True)
def clean_db(db):
    db.query(GardenZone).delete()
    db.commit()

def test_charger_zones(db, fake_zone_dict):
    zone = GardenZone(**fake_zone_dict)
    db.add(zone)
    db.commit()
    with patch("src.domains.maison.ui.jardin_zones.obtenir_contexte_db", return_value=MagicMock(__enter__=lambda s: db, __exit__=lambda s, a, b, c: None)):
        zones = jardin_zones.charger_zones()
        assert any(z["nom"] == "Zone Test" for z in zones)

def test_mettre_a_jour_zone(db, fake_zone_dict):
    zone = GardenZone(**fake_zone_dict)
    db.add(zone)
    db.commit()
    with patch("src.domains.maison.ui.jardin_zones.obtenir_contexte_db", return_value=MagicMock(__enter__=lambda s: db, __exit__=lambda s, a, b, c: None)):
        ok = jardin_zones.mettre_a_jour_zone(zone.id, {"etat_note": 5}, db=db)
        assert ok
        db.refresh(zone)
        assert zone.etat_note == 5

def test_ajouter_photo_zone(db, fake_zone_dict):
    zone = GardenZone(**fake_zone_dict)
    db.add(zone)
    db.commit()
    with patch("src.domains.maison.ui.jardin_zones.obtenir_contexte_db", return_value=MagicMock(__enter__=lambda s: db, __exit__=lambda s, a, b, c: None)):
        ok = jardin_zones.ajouter_photo_zone(zone.id, "http://photo", est_avant=True, db=db)
        assert ok
        db.refresh(zone)
        assert any("avant:" in p for p in zone.photos_url)

def test_render_carte_zone(monkeypatch, fake_zone_dict):
    zone = fake_zone_dict.copy()
    zone["id"] = 1  # Ajouter id pour le test
    monkeypatch.setattr(jardin_zones.st, "container", lambda border: MagicMock(__enter__=lambda s: None, __exit__=lambda s, a, b, c: None))
    monkeypatch.setattr(jardin_zones.st, "columns", lambda n: [MagicMock() for _ in range(len(n) if isinstance(n, list) else n)])
    monkeypatch.setattr(jardin_zones.st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "progress", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "info", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "image", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "button", lambda *a, **k: False)
    jardin_zones.render_carte_zone(zone)

def test_render_vue_ensemble(monkeypatch):
    monkeypatch.setattr(jardin_zones, "charger_zones", lambda: [{"nom": "Zone1", "surface_m2": 100, "etat_note": 3, "type_zone": "pelouse", "prochaine_action": "Tondre"}, {"nom": "Zone2", "surface_m2": 200, "etat_note": 2, "type_zone": "potager", "prochaine_action": "Arroser"}])
    monkeypatch.setattr(jardin_zones.st, "columns", lambda n: [MagicMock() for _ in range(len(n) if isinstance(n, list) else n)])
    monkeypatch.setattr(jardin_zones.st, "metric", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "divider", lambda: None)
    monkeypatch.setattr(jardin_zones.st, "plotly_chart", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "warning", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "error", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "markdown", lambda *a, **k: None)
    jardin_zones.render_vue_ensemble()

def test_render_detail_zone(monkeypatch, fake_zone_dict):
    zone = fake_zone_dict.copy()
    zone["id"] = 1  # Ajouter id pour le test
    monkeypatch.setattr(jardin_zones.st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "columns", lambda n: [MagicMock() for _ in range(len(n) if isinstance(n, list) else n)])
    monkeypatch.setattr(jardin_zones.st, "progress", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "info", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "success", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "tabs", lambda labels: [MagicMock() for _ in labels])
    monkeypatch.setattr(jardin_zones.st, "text_input", lambda *a, **k: "http://photo")
    monkeypatch.setattr(jardin_zones.st, "button", lambda *a, **k: False)
    monkeypatch.setattr(jardin_zones.st, "divider", lambda: None)
    monkeypatch.setattr(jardin_zones.st, "form", lambda key: MagicMock(__enter__=lambda s: None, __exit__=lambda s, a, b, c: None))
    monkeypatch.setattr(jardin_zones.st, "slider", lambda *a, **k: 3)
    monkeypatch.setattr(jardin_zones.st, "text_area", lambda *a, **k: "")
    monkeypatch.setattr(jardin_zones.st, "form_submit_button", lambda *a, **k: False)
    jardin_zones.render_detail_zone(zone)

def test_render_conseils_amelioration(monkeypatch):
    monkeypatch.setattr(jardin_zones.st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "info", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "expander", lambda *a, **k: MagicMock(__enter__=lambda s: None, __exit__=lambda s, a, b, c: None))
    jardin_zones.render_conseils_amelioration()

def test_app(monkeypatch):
    monkeypatch.setattr(jardin_zones.st, "title", lambda *a, **k: None)
    monkeypatch.setattr(jardin_zones.st, "caption", lambda *a, **k: None)
    # Fixture complète avec tous les champs requis
    fake_zones = [{"id": 1, "nom": "Zone1", "surface_m2": 100, "etat_note": 3, "type_zone": "pelouse", 
                   "prochaine_action": "Tondre", "etat_description": "", "objectif": "", 
                   "date_prochaine_action": None, "photos_url": [], "budget_estime": 0}]
    monkeypatch.setattr(jardin_zones, "charger_zones", lambda: fake_zones)
    monkeypatch.setattr(jardin_zones.st, "tabs", lambda labels: [MagicMock() for _ in labels])
    monkeypatch.setattr(jardin_zones, "render_vue_ensemble", lambda: None)
    monkeypatch.setattr(jardin_zones, "render_detail_zone", lambda z: None)
    monkeypatch.setattr(jardin_zones, "render_conseils_amelioration", lambda: None)
    monkeypatch.setattr(jardin_zones.st, "divider", lambda: None)
    monkeypatch.setattr(jardin_zones.st, "columns", lambda n: [MagicMock() for _ in range(len(n) if isinstance(n, list) else n)])
    monkeypatch.setattr(jardin_zones.st, "selectbox", lambda *a, **k: "Zone1")
    jardin_zones.app()
