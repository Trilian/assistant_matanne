"""Tests des routes API des services IA du modules IA."""

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

    with patch("src.api.routes.ia_modules._get_inventaire_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/modules/inventaire/prediction-consommation",
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
    service.analyser_variete_semaine = AsyncMock(
        return_value={
            "score_variete": 78,
            "proteins_bien_repartis": True,
            "types_cuisines": ["française", "asiatique"],
            "repetitions_problematiques": [],
            "recommandations": ["Ajouter une journée végétarienne"],
        }
    )

    with patch("src.api.routes.ia_modules._get_planning_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/modules/planning/analyse-variete",
            json={
                "planning_repas": [
                    {"jour": "lundi", "petit_dej": "yaourt", "midi": "poulet", "soir": "soupe"}
                ]
            },
        )

    assert response.status_code == 200
    assert response.json()["score_variete"] == 78
    service.analyser_variete_semaine.assert_awaited_once()


def test_optimisation_nutrition_planning_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.optimiser_nutrition_semaine.return_value = {
        "calories_jour": {"lundi": 2100},
        "proteines_equilibree": True,
        "fruits_legumes_quota": 0.86,
        "equilibre_fibre": True,
        "aliments_a_privilegier": ["légumineuses", "légumes verts"],
        "aliments_a_limiter": ["desserts ultra-sucrés"],
    }

    with patch("src.api.routes.ia_modules._get_planning_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/modules/planning/optimisation-nutrition",
            json={
                "planning_repas": [
                    {"jour": "lundi", "petit_dej": "yaourt", "midi": "poulet", "soir": "soupe"}
                ],
                "restrictions": ["sans alcool"],
            },
        )

    assert response.status_code == 200
    assert response.json()["proteines_equilibree"] is True
    assert response.json()["fruits_legumes_quota"] == 0.86
    service.optimiser_nutrition_semaine.assert_called_once_with(
        [
            {"jour": "lundi", "petit_dej": "yaourt", "midi": "poulet", "soir": "soupe"}
        ],
        restrictions=["sans alcool"],
    )


def test_suggestions_simplification_planning_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.suggerer_simplification.return_value = {
        "nb_recettes_complexes": 3,
        "suggestions_simplification": ["Remplacer le mercredi par un one-pot"],
        "gain_temps_minutes": 55,
        "recettes_simples_substitution": ["Pâtes aux légumes"],
        "charge_globale": "chargé",
    }

    with patch("src.api.routes.ia_modules._get_planning_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/modules/planning/suggestions-simplification",
            json={
                "planning_repas": [
                    {"jour": "lundi", "petit_dej": "yaourt", "midi": "poulet", "soir": "soupe"}
                ],
                "nb_heures_cuisine_max": 4,
            },
        )

    assert response.status_code == 200
    assert response.json()["charge_globale"] == "chargé"
    service.suggerer_simplification.assert_called_once_with(
        [
            {"jour": "lundi", "petit_dej": "yaourt", "midi": "poulet", "soir": "soupe"}
        ],
        nb_heures_cuisine_max=4,
    )


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

    with patch("src.api.routes.ia_modules._get_meteo_impact_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/modules/meteo/impacts",
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

    with patch("src.api.routes.ia_modules._get_habitudes_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/modules/habitudes/analyse",
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

    with patch("src.api.routes.ia_modules._get_projets_maison_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/modules/maison/projets/estimation",
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

    with patch("src.api.routes.ia_modules._get_nutrition_famille_ai_service", return_value=service):
        response = client.post(
            "/api/v1/ia/modules/nutrition/personne",
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
        "/api/v1/ia/modules/meteo/impacts",
        json={
            "previsions_7j": [{"date": "2026-04-02"}],
            "saison": "mousson",
        },
    )
    assert response.status_code == 422


def test_validation_prediction_consommation_stock_negatif(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ia/modules/inventaire/prediction-consommation",
        json={
            "ingredient_nom": "Lait",
            "stock_actuel_kg": -1,
            "historique_achat_mensuel": [],
        },
    )
    assert response.status_code == 422


def test_prediction_consommation_energie_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.analyser_anomalies.side_effect = [
        {
            "points": [{"mois": "2026-02", "conso": 420.0}, {"mois": "2026-03", "conso": 460.0}],
            "moyenne": 440.0,
            "score_anormalite_global": 26.0,
            "nb_anomalies": 1,
        },
        {
            "points": [{"mois": "2026-02", "conso": 120.0}, {"mois": "2026-03", "conso": 110.0}],
            "moyenne": 115.0,
            "score_anormalite_global": 10.0,
            "nb_anomalies": 0,
        },
        {
            "points": [{"mois": "2026-02", "conso": 85.0}, {"mois": "2026-03", "conso": 93.0}],
            "moyenne": 89.0,
            "score_anormalite_global": 18.0,
            "nb_anomalies": 1,
        },
    ]

    with patch("src.services.maison.energie_anomalies_ia.obtenir_service_energie_anomalies_ia", return_value=service):
        response = client.get("/api/v1/ia/modules/energie/prediction-consommation?nb_mois=12")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mois_reference"]
    assert payload["predictions"]["electricite"]["tendance"] == "hausse"
    assert payload["predictions"]["gaz"]["tendance"] == "baisse"
    assert payload["nb_anomalies"] == 2


def test_calendrier_semis_personnalise_endpoint(client: TestClient) -> None:
    meteo_service = MagicMock()
    meteo_service.obtenir_meteo.return_value = MagicMock(
        previsions=[
            MagicMock(temp_max=22.0, temp_min=10.0, precip_mm=1.0),
            MagicMock(temp_max=24.0, temp_min=11.0, precip_mm=0.0),
        ],
        suggestions=["Semaine favorable"],
    )

    with (
        patch("src.api.routes.ia_modules.MeteoService", return_value=meteo_service),
        patch(
            "src.api.routes.ia_modules._charger_catalogue_plantes",
            return_value=[
                {"nom": "Tomate", "type": "legume", "mois_semis": [4], "mois_recolte": [8, 9]},
                {"nom": "Salade", "type": "legume", "mois_semis": [3, 4], "mois_plantation": [4]},
            ],
        ),
    ):
        response = client.get("/api/v1/ia/modules/jardin/calendrier-personnalise?region=Annecy&mois=4")

    assert response.status_code == 200
    payload = response.json()
    assert payload["region"] == "Annecy"
    assert len(payload["a_semer"]) >= 1
    assert payload["meteo_resume"]["temp_moy_max"] > 0


def test_estimation_roi_habitat_endpoint(client: TestClient) -> None:
    dvf_service = MagicMock()
    dvf_service.obtenir_historique_marche.return_value = {
        "resume": {"prix_m2_median": 4300.0},
    }

    projet_service = MagicMock()
    projet_service.estimer_projet = AsyncMock(
        return_value=MagicMock(
            budget_total_max=28000.0,
        )
    )

    with (
        patch("src.api.routes.ia_modules.obtenir_service_dvf_habitat", return_value=dvf_service),
        patch("src.api.routes.ia_modules._get_projets_maison_ai_service", return_value=projet_service),
    ):
        response = client.get(
            "/api/v1/ia/modules/habitat/estimation-roi"
            "?surface_m2=95&code_postal=74000&commune=Annecy&budget_travaux=25000"
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["prix_m2_reference"] == 4300.0
    assert payload["valeur_estimee_bien"] == 408500.0
    assert payload["verdict"] in {"favorable", "equilibre", "defavorable"}


def test_comparaison_devis_artisans_endpoint(client: TestClient) -> None:
    devis_1 = MagicMock(id=1, montant_ttc=12000.0, delai_travaux_jours=20, statut="recu")
    devis_2 = MagicMock(id=2, montant_ttc=9800.0, delai_travaux_jours=35, statut="recu")
    artisan_1 = MagicMock(id=10, nom="Atelier Martin", metier="peintre", note=5)
    artisan_2 = MagicMock(id=11, nom="Duo Habitat", metier="peintre", note=3)

    with patch(
        "src.api.routes.ia_modules._charger_devis_avec_artisans",
        return_value=[(devis_1, artisan_1), (devis_2, artisan_2)],
    ):
        response = client.get("/api/v1/ia/modules/artisans/comparaison-devis?projet_id=42")

    assert response.status_code == 200
    payload = response.json()
    assert payload["projet_id"] == 42
    assert payload["estimation_reference"]["nb_devis"] == 2
    assert payload["recommandation"]["devis_recommande"]["devis_id"] in {1, 2}
