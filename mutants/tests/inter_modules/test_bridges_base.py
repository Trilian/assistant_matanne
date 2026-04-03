"""Tests bridges inter-modules de base. bridges inter-modules.

Objectif: couvrir 23 bridges existants avec des tests integration legers
et stables (retour structurel, comportement de base).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.mark.integration
def test_bridge_6_1_jardin_vers_recettes(test_db):
    from src.services.cuisine.inter_module_jardin_recettes import JardinRecettesInteractionService

    service = JardinRecettesInteractionService()
    result = service.suggerer_recettes_depuis_recolte(db=test_db)
    assert isinstance(result, dict)
    assert "message" in result


@pytest.mark.integration
def test_bridge_6_2_peremption_vers_recettes(test_db):
    from src.services.cuisine.inter_module_peremption_recettes import PeremptionRecettesInteractionService

    service = PeremptionRecettesInteractionService()
    result = service.suggerer_recettes_peremption(db=test_db)
    assert isinstance(result, dict)
    assert "recettes_suggerees" in result


@pytest.mark.integration
def test_bridge_6_3_batch_vers_inventaire(test_db):
    from src.services.cuisine.inter_module_batch_inventaire import BatchInventaireInteractionService

    service = BatchInventaireInteractionService()
    result = service.deduire_ingredients_session_terminee(session_id=999999, db=test_db)
    assert isinstance(result, dict)
    assert result.get("ok") is False


@pytest.mark.integration
def test_bridge_6_4_inventaire_vers_planning(test_db):
    from src.services.cuisine.inter_module_inventaire_planning import InventairePlanningInteractionService

    service = InventairePlanningInteractionService()
    result = service.suggerer_recettes_selon_stock(db=test_db)
    assert isinstance(result, dict)
    assert "message" in result


@pytest.mark.integration
def test_bridge_6_5_saison_vers_menu():
    from src.services.cuisine.inter_module_saison_menu import SaisonMenuInteractionService

    service = SaisonMenuInteractionService()
    result = service.obtenir_contexte_saisonnier_planning()
    assert isinstance(result, dict)
    assert "saison" in result


@pytest.mark.integration
def test_bridge_6_6_planning_vers_voyage(test_db):
    from src.services.cuisine.inter_module_planning_voyage import PlanningVoyageInteractionService

    service = PlanningVoyageInteractionService()
    result = service.suspendre_planning_voyage(
        voyage_id=42,
        date_debut="2026-04-10",
        date_fin="2026-04-15",
        db=test_db,
    )
    assert isinstance(result, dict)
    assert "nb_plannings_suspendus" in result or "error" in result


@pytest.mark.integration
def test_bridge_6_7_courses_vers_budget(test_db):
    from src.services.cuisine.inter_module_courses_budget import CoursesBudgetInteractionService

    service = CoursesBudgetInteractionService()
    result = service.synchroniser_total_courses_vers_budget(
        liste_id=100,
        montant_total=49.9,
        magasin="Intermarche",
        db=test_db,
    )
    assert isinstance(result, dict)
    assert "message" in result


@pytest.mark.integration
def test_bridge_6_8_jules_vers_nutrition(test_db):
    from src.services.cuisine.inter_module_jules_nutrition import JulesNutritionInteractionService

    service = JulesNutritionInteractionService()
    result = service.adapter_planning_nutrition_selon_croissance(db=test_db)
    assert isinstance(result, dict)
    assert "message" in result


@pytest.mark.integration
def test_bridge_6_9_weekend_vers_courses(test_db):
    from src.services.famille.inter_module_weekend_courses import WeekendCoursesInteractionService

    service = WeekendCoursesInteractionService()
    result = service.suggerer_fournitures_weekend(db=test_db)
    assert isinstance(result, dict)
    assert "fournitures_suggerees" in result


@pytest.mark.integration
def test_bridge_6_10_budget_vers_anomalie(test_db):
    from src.services.famille.inter_module_budget_anomalie import BudgetAnomalieNotificationService

    service = BudgetAnomalieNotificationService()
    result = service.detecter_et_notifier_anomalies(db=test_db)
    assert isinstance(result, dict)
    assert "nb_anomalies" in result


@pytest.mark.integration
def test_bridge_6_11_voyages_vers_budget(test_db):
    from src.services.famille.inter_module_voyages_budget import VoyagesBudgetInteractionService

    service = VoyagesBudgetInteractionService()
    result = service.synchroniser_voyages_vers_budget(db=test_db)
    assert isinstance(result, dict)
    assert "message" in result


@pytest.mark.integration
def test_bridge_6_12_meteo_vers_activites(test_db):
    from src.services.famille.inter_module_meteo_activites import MeteoActivitesInteractionService

    service = MeteoActivitesInteractionService()

    class _Prevision:
        def __init__(self, date, precip_mm, precip_proba):
            self.date = date
            self.precip_mm = precip_mm
            self.precip_proba = precip_proba

    class _Meteo:
        ville = "Paris"
        previsions = [_Prevision("2026-04-02", 0, 15), _Prevision("2026-04-03", 4, 80)]

    with patch(
        "src.services.utilitaires.meteo_service.obtenir_meteo_service",
        side_effect=lambda: type("MockServiceMeteo", (), {"obtenir_meteo": lambda self: _Meteo()})(),
    ):
        result = service.suggerer_activites_selon_meteo(db=test_db)

    assert isinstance(result, dict)
    assert "suggestions" in result


@pytest.mark.integration
def test_bridge_6_13_garmin_vers_health(test_db):
    from src.services.famille.inter_module_garmin_health import GarminHealthInteractionService

    service = GarminHealthInteractionService()
    result = service.calculer_macro_nutrition_ajustees(user_id="matanne", db=test_db)
    assert isinstance(result, dict)
    assert "calories_cible" in result or "error" in result


@pytest.mark.integration
def test_bridge_6_14_documents_vers_notifications(test_db):
    from src.services.famille.inter_module_documents_notifications import DocumentsNotificationsInteractionService

    service = DocumentsNotificationsInteractionService()
    result = service.verifier_et_notifier_documents_expirants(db=test_db)
    assert isinstance(result, dict)
    assert "documents_verifies" in result


@pytest.mark.integration
def test_bridge_6_15_entretien_vers_courses(test_db):
    from src.services.maison.inter_module_entretien_courses import EntretienCoursesInteractionService

    service = EntretienCoursesInteractionService()
    result = service.suggerer_produits_entretien_pour_courses(db=test_db)
    assert isinstance(result, dict)
    assert "suggestions" in result


@pytest.mark.integration
def test_bridge_6_16_jardin_vers_entretien(test_db):
    from src.services.maison.inter_module_jardin_entretien import JardinEntretienInteractionService

    service = JardinEntretienInteractionService()
    result = service.generer_taches_saisonnieres_depuis_plantes(db=test_db)
    assert isinstance(result, dict)
    assert "taches_creees" in result


@pytest.mark.integration
def test_bridge_6_17_charges_vers_energie(test_db):
    from src.services.maison.inter_module_charges_energie import ChargesEnergieInteractionService

    service = ChargesEnergieInteractionService()
    result = service.detecter_hausse_et_declencher_analyse(db=test_db)
    assert isinstance(result, dict)
    assert "message" in result


@pytest.mark.integration
def test_bridge_6_18_energie_vers_cuisine(test_db):
    from src.services.maison.inter_module_energie_cuisine import EnergiecuisineInteractionService

    service = EnergiecuisineInteractionService()
    result = service.obtenir_suggestions_heures_creuses(db=test_db)
    assert isinstance(result, dict)
    assert "plage" in result or "error" in result


@pytest.mark.integration
def test_bridge_6_19_diagnostics_vers_ia():
    from src.services.maison.inter_module_diagnostics_ia import DiagnosticsIAArtisansService

    service = DiagnosticsIAArtisansService()
    result = service.diagnostiquer_panne_photo(
        image_url="/tmp/fuite.jpg",
        description_panne="fuite sous l'evier",
    )
    assert isinstance(result, dict)
    assert "type_panne" in result or "error" in result


@pytest.mark.integration
def test_bridge_6_20_chat_vers_contexte_tous_modules():
    from src.services.utilitaires.inter_module_chat_contexte import ChatContexteMultiModuleService

    service = ChatContexteMultiModuleService()
    result = service.collecter_contexte_complet()
    assert isinstance(result, dict)


@pytest.mark.integration
def test_bridge_6_21_documents_vers_calendrier(test_db):
    from src.services.famille.inter_module_documents_calendrier import DocumentsCalendrierInteractionService

    service = DocumentsCalendrierInteractionService()
    result = service.synchroniser_documents_vers_calendrier(db=test_db)
    assert isinstance(result, dict)
    assert "documents_traites" in result


@pytest.mark.integration
def test_bridge_6_22_anniversaires_vers_budget(test_db):
    from src.services.famille.inter_module_anniversaires_budget import AnniversairesBudgetInteractionService

    service = AnniversairesBudgetInteractionService()
    result = service.reserver_budget_previsionnel_j14(db=test_db)
    assert isinstance(result, dict)
    assert "nb_reservations" in result


@pytest.mark.integration
def test_bridge_6_23_meteo_vers_entretien_bridge_ia(test_db):
    from src.services.ia.bridges import BridgesInterModulesService

    service = BridgesInterModulesService()
    result = service.meteo_vers_entretien(
        conditions_meteo={"temperature": -2, "vent_kmh": 45, "precipitations_mm": 12},
        db=test_db,
    )
    assert isinstance(result, list)
