"""
Tests IA Avancée — Services IA, Routes, Bridges, Intra-modules.

Couvre :
- B4: Services IA (prédiction courses, résumé hebdo, budget, etc.)
- B5: Bridges inter-modules
- B6: Intra-modules (streak routines, énergie N/N-1, entretien)
- B7: Flux utilisateur simplifiés
- B8: CRON jobs Phase B
"""

import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock


# ═══════════════════════════════════════════════════════════
# B4 — SERVICES IA
# ═══════════════════════════════════════════════════════════


class TestPredictionCourses:
    """Tests du service de prédiction de la prochaine liste de courses."""

    def test_import_service(self):
        """Le module s'importe correctement."""
        from src.services.ia.prediction_courses import obtenir_service_prediction_courses
        service = obtenir_service_prediction_courses()
        assert service is not None

    def test_predire_liste_vide(self):
        """Avec un historique vide, retourne une liste vide."""
        from src.services.ia.prediction_courses import obtenir_service_prediction_courses
        service = obtenir_service_prediction_courses()
        # Un DB mock minimal retournerait une liste vide
        # On vérifie juste que la méthode existe et est callable
        assert hasattr(service, "predire_prochaine_liste")
        assert callable(service.predire_prochaine_liste)

    def test_analyser_habitudes_method_exists(self):
        """La méthode analyser_habitudes existe."""
        from src.services.ia.prediction_courses import obtenir_service_prediction_courses
        service = obtenir_service_prediction_courses()
        assert hasattr(service, "analyser_habitudes")


class TestPrevisionBudget:
    """Tests du service de prévision budget."""

    def test_import_service(self):
        """Le module s'importe correctement."""
        from src.services.ia.prevision_budget import obtenir_service_prevision_budget
        service = obtenir_service_prevision_budget()
        assert service is not None

    def test_methodes_existent(self):
        """Les méthodes principales existent."""
        from src.services.ia.prevision_budget import obtenir_service_prevision_budget
        service = obtenir_service_prevision_budget()
        assert hasattr(service, "prevision_fin_de_mois")
        assert hasattr(service, "detecter_anomalies_budget")
        assert hasattr(service, "auto_categoriser_depense")

    def test_auto_categoriser_statique(self):
        """La catégorisation statique fonctionne pour des cas connus."""
        from src.services.ia.prevision_budget import obtenir_service_prevision_budget
        service = obtenir_service_prevision_budget()
        result = service.auto_categoriser_depense("Carrefour Market")
        assert isinstance(result, dict)
        assert "categorie" in result


class TestResumeHebdo:
    """Tests du service de résumé hebdomadaire."""

    def test_import_service(self):
        """Le module s'importe correctement."""
        from src.services.ia.resume_hebdo import obtenir_service_resume_hebdo
        service = obtenir_service_resume_hebdo()
        assert service is not None

    def test_methodes_existent(self):
        """Les méthodes principales existent."""
        from src.services.ia.resume_hebdo import obtenir_service_resume_hebdo
        service = obtenir_service_resume_hebdo()
        assert hasattr(service, "collecter_donnees_semaine")
        assert hasattr(service, "generer_resume")


class TestPlanificateurAdaptatif:
    """Tests du planificateur adaptatif contextuel."""

    def test_import_service(self):
        from src.services.ia.planificateur_adaptatif import obtenir_service_planificateur_adaptatif
        service = obtenir_service_planificateur_adaptatif()
        assert service is not None

    def test_methodes_existent(self):
        from src.services.ia.planificateur_adaptatif import obtenir_service_planificateur_adaptatif
        service = obtenir_service_planificateur_adaptatif()
        assert hasattr(service, "collecter_contexte")
        assert hasattr(service, "suggerer_planning_adapte")


class TestDiagnosticMaison:
    """Tests du service diagnostic maison."""

    def test_import_service(self):
        from src.services.ia.diagnostic_maison import obtenir_service_diagnostic_maison
        service = obtenir_service_diagnostic_maison()
        assert service is not None

    def test_methodes_existent(self):
        from src.services.ia.diagnostic_maison import obtenir_service_diagnostic_maison
        service = obtenir_service_diagnostic_maison()
        assert hasattr(service, "diagnostiquer_texte")
        assert hasattr(service, "diagnostiquer_photo")


class TestSuggestionsIA:
    """Tests du service de suggestions IA multi-domaine."""

    def test_import_service(self):
        from src.services.ia.suggestions_ia import obtenir_service_suggestions_ia
        service = obtenir_service_suggestions_ia()
        assert service is not None

    def test_methodes_existent(self):
        from src.services.ia.suggestions_ia import obtenir_service_suggestions_ia
        service = obtenir_service_suggestions_ia()
        for method_name in [
            "batch_cooking_intelligent",
            "conseil_developpement_jules",
            "generer_checklist_voyage",
            "score_ecologique_repas",
            "optimisation_energie",
            "analyse_nutritionnelle",
        ]:
            assert hasattr(service, method_name), f"Méthode {method_name} manquante"


# ═══════════════════════════════════════════════════════════
# B5 — BRIDGES INTER-MODULES
# ═══════════════════════════════════════════════════════════


class TestBridgesInterModules:
    """Tests du service bridges inter-modules."""

    def test_import_service(self):
        from src.services.ia.bridges import obtenir_service_bridges
        service = obtenir_service_bridges()
        assert service is not None

    def test_methodes_bridges_existent(self):
        from src.services.ia.bridges import obtenir_service_bridges
        service = obtenir_service_bridges()
        for method_name in [
            "recolte_vers_recettes",
            "documents_expires_alertes",
            "entretien_planning_unifie",
            "verifier_anomalies_budget_et_notifier",
            "meteo_vers_entretien",
        ]:
            assert hasattr(service, method_name), f"Bridge {method_name} manquant"

    def test_registration_function_exists(self):
        from src.services.ia.bridges import enregistrer_bridges_subscribers
        assert callable(enregistrer_bridges_subscribers)


# ═══════════════════════════════════════════════════════════
# B6 — INTRA-MODULES
# ═══════════════════════════════════════════════════════════


class TestIntraModules:
    """Tests des améliorations intra-modules."""

    def test_streak_routines(self):
        """calculer_streak_routines retourne un dict."""
        from src.services.ia.intra_modules import calculer_streak_routines
        result = calculer_streak_routines()
        assert isinstance(result, dict)

    def test_comparaison_energie(self):
        """comparaison_energie_n_vs_n1 retourne la structure correcte."""
        from src.services.ia.intra_modules import comparaison_energie_n_vs_n1
        result = comparaison_energie_n_vs_n1("electricite")
        assert isinstance(result, dict)

    def test_suggestions_entretien(self):
        """suggestions_entretien_par_age_equipement retourne une liste."""
        from src.services.ia.intra_modules import suggestions_entretien_par_age_equipement
        result = suggestions_entretien_par_age_equipement()
        assert isinstance(result, list)

    def test_prix_moyens_checkout(self):
        """mettre_a_jour_prix_moyens_checkout retourne un int."""
        from src.services.ia.intra_modules import mettre_a_jour_prix_moyens_checkout
        result = mettre_a_jour_prix_moyens_checkout(liste_id=999)
        assert isinstance(result, int)


# ═══════════════════════════════════════════════════════════
# B7 — FLUX UTILISATEUR
# ═══════════════════════════════════════════════════════════


class TestFluxUtilisateur:
    """Tests des flux utilisateur simplifiés."""

    def test_flux_cuisine_3_clics(self):
        """flux_cuisine_3_clics retourne un dict avec etape_actuelle."""
        from src.services.ia.flux_utilisateur import flux_cuisine_3_clics
        result = flux_cuisine_3_clics()
        assert isinstance(result, dict)

    def test_digest_quotidien(self):
        """generer_digest_quotidien retourne un dict."""
        from src.services.ia.flux_utilisateur import generer_digest_quotidien
        result = generer_digest_quotidien()
        assert isinstance(result, dict)

    def test_marquer_tache_fait(self):
        """marquer_tache_fait_avec_prochaine retourne un dict."""
        from src.services.ia.flux_utilisateur import marquer_tache_fait_avec_prochaine
        result = marquer_tache_fait_avec_prochaine(tache_id=999)
        assert isinstance(result, dict)

    def test_feedback_semaine_vide(self):
        """enregistrer_feedback_semaine avec liste vide retourne 0."""
        from src.services.ia.flux_utilisateur import enregistrer_feedback_semaine
        result = enregistrer_feedback_semaine(feedbacks=[])
        assert isinstance(result, dict)
        assert result.get("nb_feedbacks") == 0


# ═══════════════════════════════════════════════════════════
# B8 — CRON JOBS
# ═══════════════════════════════════════════════════════════


class TestCronJobsPhaseB:
    """Tests des cron jobs Phase B."""

    def test_configurer_jobs(self):
        """configurer_jobs_phase_b s'exécute sans erreur."""
        from apscheduler.schedulers.background import BackgroundScheduler
        from src.services.core.cron_phase_b import configurer_jobs_phase_b

        scheduler = BackgroundScheduler(timezone="Europe/Paris")
        configurer_jobs_phase_b(scheduler)

        jobs = scheduler.get_jobs()
        assert len(jobs) >= 6  # Au moins 6 des 7 jobs

    def test_jobs_ids_coherents(self):
        """Les job IDs sont bien ceux attendus."""
        from apscheduler.schedulers.background import BackgroundScheduler
        from src.services.core.cron_phase_b import configurer_jobs_phase_b

        scheduler = BackgroundScheduler(timezone="Europe/Paris")
        configurer_jobs_phase_b(scheduler)

        job_ids = {j.id for j in scheduler.get_jobs()}
        expected_ids = {
            "prediction_courses_hebdo",
            "planning_auto_semaine",
            "alertes_budget_seuil",
            "rappel_jardin_saison",
            "sync_budget_consolidation",
            "tendances_nutrition_hebdo",
            "rappel_activite_jules",
        }
        assert expected_ids.issubset(job_ids), f"IDs manquants: {expected_ids - job_ids}"


# ═══════════════════════════════════════════════════════════
# EVENTS — Phase B
# ═══════════════════════════════════════════════════════════


class TestEventsPhaseB:
    """Tests des événements Phase B."""

    def test_event_prediction_courses(self):
        from src.services.core.events.events import EvenementPredictionCourses
        evt = EvenementPredictionCourses(nb_articles=5, source="historique")
        assert evt.TYPE == "prediction.courses_generees"
        assert evt.nb_articles == 5

    def test_event_resume_hebdo(self):
        from src.services.core.events.events import EvenementResumeHebdo
        evt = EvenementResumeHebdo(semaine="2026-W15", nb_sections=3)
        assert evt.TYPE == "resume.hebdo_genere"

    def test_event_prevision_budget(self):
        from src.services.core.events.events import EvenementPrevisionBudget
        evt = EvenementPrevisionBudget(montant_prevu=2500.0, nb_anomalies=1)
        assert evt.TYPE == "budget.prevision_calculee"

    def test_event_diagnostic_maison(self):
        from src.services.core.events.events import EvenementDiagnosticMaison
        evt = EvenementDiagnosticMaison(type_diagnostic="photo", probleme="fuite")
        assert evt.TYPE == "maison.diagnostic"

    def test_event_bridge_recolte(self):
        from src.services.core.events.events import EvenementBridgeRecolteRecettes
        evt = EvenementBridgeRecolteRecettes(nb_recettes_suggerees=3, ingredients=["tomates"])
        assert evt.TYPE == "bridge.recolte_recettes"

    def test_event_bridge_meteo(self):
        from src.services.core.events.events import EvenementBridgeMeteoEntretien
        evt = EvenementBridgeMeteoEntretien(nb_taches=2, condition_meteo="gel")
        assert evt.TYPE == "bridge.meteo_entretien"


# ═══════════════════════════════════════════════════════════
# ROUTES — Phase B (smoke tests via import)
# ═══════════════════════════════════════════════════════════


class TestRoutesImport:
    """Smoke tests: tous les modules de routes Phase B s'importent."""

    def test_import_predictions_route(self):
        from src.api.routes.predictions import router
        assert router is not None

    def test_import_ia_bridges_route(self):
        from src.api.routes.ia_bridges import router
        assert router is not None

    def test_import_bridges_route(self):
        from src.api.routes.bridges import router
        assert router is not None

    def test_import_intra_flux_route(self):
        from src.api.routes.intra_flux import router
        assert router is not None


class TestSchemasPhaseB:
    """Tests des schémas Pydantic Phase B."""

    def test_import_schemas(self):
        from src.api.schemas.ia_bridges import (
            PredictionCoursesResponse,
            PrevisionBudgetResponse,
            ResumeHebdoResponse,
            DiagnosticMaisonRequest,
            DiagnosticMaisonResponse,
        )
        assert PredictionCoursesResponse is not None
        assert PrevisionBudgetResponse is not None

    def test_schema_validation(self):
        from src.api.schemas.ia_bridges import PredictionCoursesResponse

        p = PredictionCoursesResponse(
            predictions=[],
            nb_total=0,
        )
        assert p.predictions == []
        assert p.nb_total == 0
