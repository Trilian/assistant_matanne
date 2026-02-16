"""
Tests pour src/services/jeux/prediction_service.py

Tests unitaires du service de prédiction de matchs.
"""

import pytest

from src.services.jeux.prediction_service import (
    PredictionService,
    get_prediction_service,
    predire_resultat_match,
    predire_over_under,
    generer_conseils_avances,
)


class TestPredictionService:
    """Tests pour PredictionService"""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service de prédiction."""
        return get_prediction_service()

    @pytest.fixture
    def forme_equipe_forte(self):
        """Équipe en excellente forme."""
        return {
            "score": 80,
            "nb_matchs": 5,
            "forme_str": "VVVVV",
            "serie_en_cours": "V5",
            "matchs_sans_nul": 5,
            "buts_marques": 12,
            "buts_encaisses": 3,
        }

    @pytest.fixture
    def forme_equipe_faible(self):
        """Équipe en mauvaise forme."""
        return {
            "score": 30,
            "nb_matchs": 5,
            "forme_str": "DDDDD",
            "serie_en_cours": "D5",
            "matchs_sans_nul": 5,
            "buts_marques": 2,
            "buts_encaisses": 10,
        }

    @pytest.fixture
    def h2h_neutre(self):
        """Historique H2H neutre."""
        return {"nb_matchs": 0, "avantage": None}

    def test_predire_resultat_equipe_forte_vs_faible(
        self, service, forme_equipe_forte, forme_equipe_faible, h2h_neutre
    ):
        """Test: équipe forte à domicile doit être favorite."""
        result = service.predire_resultat_match(
            forme_equipe_forte, forme_equipe_faible, h2h_neutre
        )

        assert result.prediction == "1"  # Victoire domicile
        assert result.probabilites["domicile"] > result.probabilites["exterieur"]
        assert result.confiance > 50

    def test_predire_resultat_avec_cotes(
        self, service, forme_equipe_forte, forme_equipe_faible, h2h_neutre
    ):
        """Test: les cotes influencent la prédiction."""
        cotes = {"domicile": 1.5, "nul": 4.0, "exterieur": 6.0}
        result = service.predire_resultat_match(
            forme_equipe_forte, forme_equipe_faible, h2h_neutre, cotes
        )

        assert result.prediction == "1"
        assert "conseil" in result.model_dump()

    def test_predire_over_under_equipes_offensives(self, service, forme_equipe_forte):
        """Test: équipes offensives devraient prédire over."""
        forme_offensive = {
            **forme_equipe_forte,
            "buts_marques": 15,
            "buts_encaisses": 8,
        }

        result = service.predire_over_under(forme_offensive, forme_offensive, seuil=2.5)

        assert result.buts_attendus > 2.5
        assert result.prediction == "over"

    def test_predire_over_under_equipes_defensives(self, service):
        """Test: équipes défensives devraient prédire under."""
        forme_defensive = {
            "score": 50,
            "nb_matchs": 5,
            "buts_marques": 3,
            "buts_encaisses": 2,
        }

        result = service.predire_over_under(forme_defensive, forme_defensive, seuil=2.5)

        assert result.buts_attendus < 2.5
        assert result.prediction == "under"

    def test_generer_conseils_avances_serie_sans_nul(self, service):
        """Test: série sans nuls génère un conseil."""
        forme_sans_nul = {
            "score": 50,
            "nb_matchs": 10,
            "matchs_sans_nul": 8,
            "buts_marques": 10,
            "buts_encaisses": 10,
        }

        conseils = service.generer_conseils_avances(forme_sans_nul, forme_sans_nul)

        # Au moins un conseil sur les nuls
        types_conseils = [c.type for c in conseils]
        assert any("NUL" in t for t in types_conseils)


class TestFonctionsCompatibilite:
    """Tests pour les fonctions de compatibilité."""

    def test_predire_resultat_match_retourne_dict(self):
        """Test: fonction de compat retourne un dict."""
        forme = {"score": 50, "nb_matchs": 3}
        h2h = {"nb_matchs": 0}

        result = predire_resultat_match(forme, forme, h2h)

        assert isinstance(result, dict)
        assert "prediction" in result
        assert "probabilites" in result
        assert "confiance" in result

    def test_predire_over_under_retourne_dict(self):
        """Test: fonction de compat retourne un dict."""
        forme = {"score": 50, "nb_matchs": 3, "buts_marques": 5, "buts_encaisses": 5}

        result = predire_over_under(forme, forme)

        assert isinstance(result, dict)
        assert "prediction" in result
        assert "buts_attendus" in result

    def test_generer_conseils_avances_retourne_list_dict(self):
        """Test: fonction de compat retourne une liste de dicts."""
        forme = {
            "score": 50,
            "nb_matchs": 5,
            "matchs_sans_nul": 7,
            "buts_marques": 10,
            "buts_encaisses": 10,
        }

        result = generer_conseils_avances(forme, forme)

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)
