"""Tests des routes API des services IA du Sprint 13."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    from src.api.dependencies import require_auth
    from src.api.main import app
    from src.api.rate_limiting import verifier_limite_debit_ia

    async def _mock_auth() -> dict:
        return {"sub": "test-user", "role": "admin"}

    async def _mock_rate() -> dict:
        return {"allowed": True, "remaining": 999}

    app.dependency_overrides[require_auth] = _mock_auth
    app.dependency_overrides[verifier_limite_debit_ia] = _mock_rate

    yield TestClient(app, raise_server_exceptions=False)

    app.dependency_overrides.pop(require_auth, None)
    app.dependency_overrides.pop(verifier_limite_debit_ia, None)


def test_prediction_consommation_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.predire_consommation.return_value = {
        "ingredient_nom": "Lait",
        "consommation_hebdo_kg": 2.0,
        "stock_actuel_kg": 1.5,
        "jours_autonomie": 5,
        "seuil_reapprovisionnement_kg": 4.0,
        "raison": "Historique stable",
    }

    with patch("src.api.routes.ia_sprint13._get_inventaire_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/sprint13/inventaire/prediction-consommation",
            json={
                "ingredient_nom": "Lait",
                "stock_actuel_kg": 1.5,
                "historique_achat_mensuel": [{"date": "2026-04-01", "quantite_kg": 2.0}],
            },
        )

    assert response.status_code == 200
    assert response.json()["ingredient_nom"] == "Lait"
    service.predire_consommation.assert_called_once()


def test_analyse_variete_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.analyser_variete_semaine.return_value = {
        "score_variete": 78,
        "proteins_bien_repartis": True,
        "types_cuisines": ["française", "asiatique"],
        "repetitions_problematiques": [],
        "recommandations": ["Ajouter une journée végétarienne"],
    }

    with patch("src.api.routes.ia_sprint13._get_planning_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/sprint13/planning/analyse-variete",
            json={
                "planning_repas": [
                    {"jour": "lundi", "petit_dej": "yaourt", "midi": "poulet", "soir": "soupe"}
                ]
            },
        )

    assert response.status_code == 200
    assert response.json()["score_variete"] == 78
    service.analyser_variete_semaine.assert_called_once()


def test_analyse_impacts_meteo_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.analyser_impacts = AsyncMock(
        return_value=[
            {
                "date": "2026-04-02",
                "conditions": "pluie",
                "temperature_min": 8,
                "temperature_max": 12,
                "humidite": 80,
                "chance_pluie": 90,
                "vent_km_h": 20,
                "impacts": [
                    {
                        "domaine": "jardin",
                        "type_impact": "arrosage",
                        "severite": "faible",
                        "recommandation": "Reporter l'arrosage",
                        "urgence": False,
                    }
                ],
            }
        ]
    )

    with patch("src.api.routes.ia_sprint13._get_meteo_impact_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/sprint13/meteo/impacts",
            json={
                "previsions_7j": [
                    {
                        "date": "2026-04-02",
                        "conditions": "pluie",
                        "temp_min": 8,
                        "temp_max": 12,
                        "humidite": 80,
                        "chance_pluie": 90,
                        "vent_km_h": 20,
                    }
                ],
                "saison": "printemps",
            },
        )

    assert response.status_code == 200
    assert response.json()[0]["conditions"] == "pluie"
    service.analyser_impacts.assert_awaited_once()


def test_analyse_habitude_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.analyser_habitude = AsyncMock(
        return_value={
            "habitude": "lecture",
            "frequence_hebdo": 5,
            "consistency": 0.7,
            "jours_preferres": ["lundi"],
            "heures_preferees": ["soir"],
            "status": "etablie",
            "impact_positif": ["apaisement"],
            "facteurs_decouplage": ["fatigue"],
        }
    )

    with patch("src.api.routes.ia_sprint13._get_habitudes_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/sprint13/habitudes/analyse",
            json={
                "habitude_nom": "lecture",
                "historique_7j": [{"date": "2026-04-01", "realise": True, "heure": "20:00"}],
                "description_contexte": "semaine normale",
            },
        )

    assert response.status_code == 200
    assert response.json()["habitude"] == "lecture"
    service.analyser_habitude.assert_awaited_once()


def test_estimation_projet_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.estimer_projet = AsyncMock(
        return_value={
            "projet_nom": "Peinture salon",
            "complexite": "moyen",
            "temps_jours": 3,
            "est_diy": True,
            "competences_requises": ["préparation"],
            "materiaux_principaux": ["peinture"],
            "budget_materialisation": 200.0,
            "budget_main_oeuvre": None,
            "budget_total_min": 200.0,
            "budget_total_max": 450.0,
            "risques": ["finitions"],
            "etapes_cles": ["poncer", "peindre"],
            "prerequisites": ["vider la pièce"],
            "recommandations": ["tester une sous-couche"],
        }
    )

    with patch("src.api.routes.ia_sprint13._get_projets_maison_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/sprint13/maison/projets/estimation",
            json={
                "projet_description": "Repeindre le salon en blanc cassé",
                "surface_m2": 25,
                "type_maison": "maison_2020",
                "contraintes": ["finir en une semaine"],
            },
        )

    assert response.status_code == 200
    assert response.json()["complexite"] == "moyen"
    service.estimer_projet.assert_awaited_once()


def test_analyse_nutrition_personne_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.analyser_nutrition_personne = AsyncMock(
        return_value={
            "personne": "Marie",
            "periode": "semaine dernière",
            "calories_moyenne": 2100.0,
            "proteines_g": 75.0,
            "glucides_g": 220.0,
            "lipides_g": 70.0,
            "fibres_g": 28.0,
            "fruits_legumes_portions": 5.0,
            "eau_litres": 2.0,
            "equilibre_score": 82,
        }
    )

    with patch("src.api.routes.ia_sprint13._get_nutrition_famille_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/sprint13/nutrition/personne",
            json={
                "personne_nom": "Marie",
                "age_ans": 35,
                "sexe": "F",
                "activite_niveau": "modere",
                "donnees_garmin_semaine": {"pas": 8500},
                "recettes_semaine": ["salade", "poisson"],
                "objectif_sante": "maintien",
            },
        )

    assert response.status_code == 200
    assert response.json()["personne"] == "Marie"
    service.analyser_nutrition_personne.assert_awaited_once()


def test_validation_saison_meteo(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ia/sprint13/meteo/impacts",
        json={
            "previsions_7j": [{"date": "2026-04-02"}],
            "saison": "mousson",
        },
    )
    assert response.status_code == 422


def test_validation_prediction_consommation_stock_negatif(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ia/sprint13/inventaire/prediction-consommation",
        json={
            "ingredient_nom": "Lait",
            "stock_actuel_kg": -1,
            "historique_achat_mensuel": [],
        },
    )
    assert response.status_code == 422