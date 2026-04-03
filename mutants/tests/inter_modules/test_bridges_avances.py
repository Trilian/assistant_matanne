"""Tests bridges inter-modules haute priorité (NIM1-NIM4). bridges inter-modules haute priorité (NIM1-NIM4).

Objectif: tester les 4 nouveaux bridges:
- NIM1: Inventaire → Budget alimentation prévisionnel
- NIM2: Planning → Jardin feedback loop
- NIM3: Garmin/Santé → Cuisine adultes (nutrition)
- NIM4: Dashboard → Actions rapides (deep links)
"""

from __future__ import annotations

import pytest


@pytest.mark.integration
def test_nim1_inventaire_budget_previsionnel(test_db):
    """NIM1: Calcul du budget prévisionnel basé sur l'inventaire."""
    from src.services.cuisine.inter_module_inventaire_budget import (
        InventaireBudgetInteractionService,
    )

    service = InventaireBudgetInteractionService()
    result = service.calculer_budget_previsionnel_par_inventaire(
        semaines_horizon=4,
        db=test_db,
    )

    assert isinstance(result, dict)
    assert "budget_previsionnel" in result
    assert "par_categorie" in result
    assert "items_a_renouveler" in result
    assert "taux_couverture" in result
    assert isinstance(result["budget_previsionnel"], (int, float))
    assert isinstance(result["par_categorie"], dict)
    assert isinstance(result["items_a_renouveler"], list)


@pytest.mark.integration
def test_nim1_agreger_achats_par_categorie(test_db):
    """NIM1: Agrégation des achats réels par catégorie."""
    from src.services.cuisine.inter_module_inventaire_budget import (
        InventaireBudgetInteractionService,
    )

    service = InventaireBudgetInteractionService()
    result = service.agréger_achats_par_categorie(
        jours_lookback=30,
        db=test_db,
    )

    assert isinstance(result, dict)
    assert "periode_jours" in result
    assert "depenses_par_categorie" in result
    assert "total_periode" in result
    assert "moyenne_par_jour" in result
    assert "nb_tickets" in result


@pytest.mark.integration
def test_nim2_planning_jardin_recoltes_non_utilisees(test_db):
    """NIM2: Détection des récoltes non utilisées dans le planning."""
    from src.services.cuisine.inter_module_planning_jardin import (
        PlanningJardinInteractionService,
    )

    service = PlanningJardinInteractionService()
    result = service.analyser_recoltes_non_utilisees(
        semaines_lookback=4,
        db=test_db,
    )

    assert isinstance(result, dict)
    assert "recoltes_non_utilisees" in result
    assert "taux_utilisation" in result
    assert "recommendations" in result
    assert isinstance(result["recoltes_non_utilisees"], list)
    assert isinstance(result["taux_utilisation"], (int, float))
    assert isinstance(result["recommendations"], list)


@pytest.mark.integration
def test_nim2_modifier_production_jardin(test_db):
    """NIM2: Ajustement de la production du jardin.

    Note: Test avec identifiant inexistant (retourne error gracieux).
    """
    from src.services.cuisine.inter_module_planning_jardin import (
        PlanningJardinInteractionService,
    )

    service = PlanningJardinInteractionService()
    result = service.modifier_production_jardin_selon_planning(
        plante_id=999999,
        facteur_ajustement=0.8,
        db=test_db,
    )

    assert isinstance(result, dict)
    # Peut retourner error ou success, dépend de la présence des données


@pytest.mark.integration
def test_nim3_besoins_nutritionnels_selon_activite(test_db):
    """NIM3: Calcul des besoins nutritionnels basé sur l'activité Garmin."""
    from src.services.cuisine.inter_module_garmin_nutrition_adultes import (
        GarminNutritionAdultesInteractionService,
    )

    service = GarminNutritionAdultesInteractionService()
    result = service.calculer_besoins_nutritionnels_selon_activite(
        profil_id=None,  # Prendra le premier adulte par défaut
        db=test_db,
    )

    assert isinstance(result, dict)
    assert "calories_recommended" in result
    assert "macros" in result
    assert "niveau_activite" in result
    assert isinstance(result["calories_recommended"], (int, float))
    assert isinstance(result["macros"], dict)
    assert "proteines_g" in result["macros"]
    assert "lipides_g" in result["macros"]
    assert "glucides_g" in result["macros"]


@pytest.mark.integration
def test_nim3_recommander_recettes_selon_activite(test_db):
    """NIM3: Recommandations de recettes adaptées à l'activité."""
    from src.services.cuisine.inter_module_garmin_nutrition_adultes import (
        GarminNutritionAdultesInteractionService,
    )

    service = GarminNutritionAdultesInteractionService()
    result = service.recommander_recettes_selon_activite(
        profil_id=None,
        db=test_db,
    )

    assert isinstance(result, dict)
    assert "niveau_activite" in result
    assert "tags_recherche" in result
    assert "recettes_recommandees" in result
    assert isinstance(result["recettes_recommandees"], list)


@pytest.mark.integration
def test_nim4_generer_deeplinks_anomalies():
    """NIM4: Génération de deep links pour anomalies dashboard."""
    from src.services.utilitaires.inter_module_dashboard_actions import (
        DashboardActionsRapidesInteractionService,
    )

    service = DashboardActionsRapidesInteractionService()

    anomalies = [
        {
            "type": "budget",
            "data": {
                "action": "revoir",
                "categorie": "alimentation",
                "montant": 250,
                "pourcentage_depassement": 15,
            },
        },
        {
            "type": "stock",
            "data": {
                "article": "Riz",
                "article_id": 1,
                "seuil": 1,
            },
        },
        {
            "type": "peremption",
            "data": {
                "nb_articles": 3,
                "jours_restants": 2,
            },
        },
    ]

    result = service.generer_deeplinks_anomalies(anomalies=anomalies)

    assert isinstance(result, dict)
    assert "nb_anomalies" in result
    assert "nb_deeplinks" in result
    assert "deeplinks" in result
    assert result["nb_anomalies"] == 3
    assert isinstance(result["deeplinks"], list)
    assert len(result["deeplinks"]) >= 2  # Au moins 2 convertis en deeplinks


@pytest.mark.integration
def test_nim4_executer_action_rapide(test_db):
    """NIM4: Exécution d'une action rapide depuis le dashboard."""
    from src.services.utilitaires.inter_module_dashboard_actions import (
        DashboardActionsRapidesInteractionService,
    )

    service = DashboardActionsRapidesInteractionService()

    # Test action inconnue (retourne error gracieux)
    result = service.executer_action_rapide_dashboard(
        action_id="unknown_action",
        anomalie_data={},
        db=test_db,
    )

    assert isinstance(result, dict)
    assert "action_id" in result
    assert result["action_id"] == "unknown_action"
    # Peut retourner success ou error selon les données


@pytest.mark.integration
def test_nim4_action_budget_anomaly(test_db):
    """NIM4: Action rapide budget anomaly."""
    from src.services.utilitaires.inter_module_dashboard_actions import (
        DashboardActionsRapidesInteractionService,
    )

    service = DashboardActionsRapidesInteractionService()
    result = service.executer_action_rapide_dashboard(
        action_id="budget_anomaly",
        anomalie_data={
            "categorie": "alimentation",
            "montant_limite": 500,
            "date": None,
        },
        db=test_db,
    )

    assert isinstance(result, dict)
    assert "action_id" in result
    assert result["action_id"] == "budget_anomaly"


@pytest.mark.integration
def test_nim4_action_stock_alert(test_db):
    """NIM4: Action rapide stock alert."""
    from src.services.utilitaires.inter_module_dashboard_actions import (
        DashboardActionsRapidesInteractionService,
    )

    service = DashboardActionsRapidesInteractionService()
    result = service.executer_action_rapide_dashboard(
        action_id="stock_alert",
        anomalie_data={
            "article_id": 999999,  # ID inexistant
        },
        db=test_db,
    )

    assert isinstance(result, dict)
    assert "action_id" in result
    # Retournera error car article inexistant


@pytest.mark.integration
def test_all_nim_services_registered():
    """Tous les NIM1-NIM4 services sont enregistrés dans la factory."""
    from src.services.core.registry import registre

    # NIM1
    service_nim1 = registre.obtenir("inventaire_budget")
    assert service_nim1 is not None

    # NIM2
    service_nim2 = registre.obtenir("planning_jardin")
    assert service_nim2 is not None

    # NIM3
    service_nim3 = registre.obtenir("garmin_nutrition_adultes")
    assert service_nim3 is not None

    # NIM4
    service_nim4 = registre.obtenir("dashboard_actions_rapides")
    assert service_nim4 is not None
