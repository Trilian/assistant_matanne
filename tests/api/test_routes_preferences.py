"""Tests pour `src/api/routes/preferences.py`.

Couvre les régressions sur les endpoints `GET/PUT/PATCH /api/v1/preferences`.
"""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.dependencies import require_auth
from src.api.routes.preferences import router


@pytest.fixture
def client():
    """Client de test FastAPI isolé avec auth forcée."""
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}
    return TestClient(app)


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

PREFERENCES_CREATE = {
    "nb_adultes": 2,
    "jules_present": True,
    "jules_age_mois": 19,
    "temps_semaine": 30,
    "temps_weekend": 60,
    "aliments_exclus": ["arachides"],
    "aliments_favoris": ["saumon", "courgettes"],
    "poisson_par_semaine": 2,
    "vegetarien_par_semaine": 1,
    "viande_rouge_max": 2,
    "robots": ["airfryer"],
    "magasins_preferes": ["Biocoop", "Carrefour"],
}

PREFERENCES_PATCH = {
    "nb_adultes": 3,
    "temps_semaine": 25,
    "magasins_preferes": ["Biocoop"],
}


def _prefs_namespace(**overrides):
    """Construit un objet préférences minimal pour la sérialisation de réponse."""
    valeurs = {
        "user_id": "test-user",
        "nb_adultes": 2,
        "jules_present": True,
        "jules_age_mois": 19,
        "temps_semaine": 30,
        "temps_weekend": 60,
        "aliments_exclus": [],
        "aliments_favoris": [],
        "poisson_par_semaine": 2,
        "vegetarien_par_semaine": 1,
        "viande_rouge_max": 2,
        "robots": [],
        "magasins_preferes": [],
    }
    valeurs.update(overrides)
    return SimpleNamespace(**valeurs)


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES PRÉFÉRENCES
# ═══════════════════════════════════════════════════════════


class TestRoutesPreferences:
    """Tests des routes préférences avec assertions métier."""

    def test_obtenir_preferences_retourne_valeurs_par_defaut_si_absentes(self, client):
        """GET retourne les defaults attendus quand aucun enregistrement n'existe."""
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = None

        @contextmanager
        def _ctx():
            yield session

        with patch("src.api.routes.preferences.executer_avec_session", _ctx):
            response = client.get("/api/v1/preferences")

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        assert data["nb_adultes"] == 2
        assert data["aliments_exclus"] == []
        assert data["magasins_preferes"] == []

    def test_creer_preferences_upsert_persiste_et_serialise(self, client):
        """PUT crée les préférences et renvoie les champs persistés."""
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = None

        @contextmanager
        def _ctx():
            yield session

        with patch("src.api.routes.preferences.executer_avec_session", _ctx):
            response = client.put("/api/v1/preferences", json=PREFERENCES_CREATE)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        assert data["jules_age_mois"] == 19
        assert data["aliments_favoris"] == ["saumon", "courgettes"]
        assert data["magasins_preferes"] == ["Biocoop", "Carrefour"]
        session.commit.assert_called_once()
        session.refresh.assert_called_once()

    def test_modifier_preferences_met_a_jour_les_champs_cibles(self, client):
        """PATCH met à jour les champs demandés sans casser la sérialisation."""
        prefs = _prefs_namespace()
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = prefs

        @contextmanager
        def _ctx():
            yield session

        with patch("src.api.routes.preferences.executer_avec_session", _ctx):
            response = client.patch("/api/v1/preferences", json=PREFERENCES_PATCH)

        assert response.status_code == 200
        data = response.json()
        assert prefs.nb_adultes == 3
        assert prefs.temps_semaine == 25
        assert prefs.magasins_preferes == ["Biocoop"]
        assert data["nb_adultes"] == 3
        assert data["temps_semaine"] == 25
        assert data["magasins_preferes"] == ["Biocoop"]
        session.commit.assert_called_once()
        session.refresh.assert_called_once_with(prefs)

    def test_modifier_preferences_body_vide_retourne_422(self, client):
        """PATCH avec body vide retourne une erreur explicite."""
        prefs = _prefs_namespace()
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = prefs

        @contextmanager
        def _ctx():
            yield session

        with patch("src.api.routes.preferences.executer_avec_session", _ctx):
            response = client.patch("/api/v1/preferences", json={})

        assert response.status_code == 422
        assert "Aucun champ" in response.text
