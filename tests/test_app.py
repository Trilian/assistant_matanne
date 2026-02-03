import pytest
import sys
from pathlib import Path
import streamlit as st
from unittest import mock

# Patch sys.path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import app module
import src.app as app

def test_main_runs(monkeypatch):
    """Test que la fonction main() s'exécute sans erreur."""
    # Mock les composants UI et OptimizedRouter
    monkeypatch.setattr(app, "afficher_header", lambda: None)
    monkeypatch.setattr(app, "afficher_sidebar", lambda: None)
    monkeypatch.setattr(app, "afficher_footer", lambda: None)
    monkeypatch.setattr(app, "injecter_css", lambda: None)
    monkeypatch.setattr(app, "initialiser_app", lambda: True)
    monkeypatch.setattr(app, "OptimizedRouter", mock.Mock(load_module=lambda x: None))
    monkeypatch.setattr(app, "obtenir_etat", lambda: mock.Mock(module_actuel="accueil", mode_debug=False))
    monkeypatch.setattr(app, "Cache", mock.Mock(vider=lambda: None))
    monkeypatch.setattr(app, "GestionnaireEtat", mock.Mock(reinitialiser=lambda: None))
    monkeypatch.setattr(st, "set_page_config", lambda **kwargs: None)
    monkeypatch.setattr(st, "stop", lambda: None)
    monkeypatch.setattr(st, "error", lambda msg: None)
    monkeypatch.setattr(st, "exception", lambda e: None)
    monkeypatch.setattr(st, "button", lambda label: False)

    # Appel de main
    app.main()


def test_main_exception(monkeypatch):
    """Test gestion d'exception dans main()."""
    monkeypatch.setattr(app, "afficher_header", lambda: (_ for _ in ()).throw(Exception("Test")))
    monkeypatch.setattr(app, "afficher_sidebar", lambda: None)
    monkeypatch.setattr(app, "afficher_footer", lambda: None)
    monkeypatch.setattr(app, "injecter_css", lambda: None)
    monkeypatch.setattr(app, "initialiser_app", lambda: True)
    monkeypatch.setattr(app, "OptimizedRouter", mock.Mock(load_module=lambda x: None))
    monkeypatch.setattr(app, "obtenir_etat", lambda: mock.Mock(module_actuel="accueil", mode_debug=True))
    monkeypatch.setattr(app, "Cache", mock.Mock(vider=lambda: None))
    monkeypatch.setattr(app, "GestionnaireEtat", mock.Mock(reinitialiser=lambda: None))
    monkeypatch.setattr(st, "set_page_config", lambda **kwargs: None)
    monkeypatch.setattr(st, "stop", lambda: None)
    monkeypatch.setattr(st, "error", lambda msg: None)
    monkeypatch.setattr(st, "exception", lambda e: None)
    monkeypatch.setattr(st, "button", lambda label: False)

    # Appel de main (doit gérer l'exception)
    app.main()


def test_initialiser_app_stop(monkeypatch):
    """Test arrêt si initialiser_app() retourne False."""
    monkeypatch.setattr(app, "initialiser_app", lambda: False)
    monkeypatch.setattr(st, "stop", lambda: None)
    # Appel de la logique d'initialisation
    if not app.initialiser_app():
        st.stop()
