"""
Tests de couverture Ã©tendus pour src/services - Partie 7
Tests plus profonds: mÃ©thodes de service, logique mÃ©tier, helpers
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = MagicMock()
    session.query.return_value = session
    session.filter.return_value = session
    session.filter_by.return_value = session
    session.order_by.return_value = session
    session.offset.return_value = session
    session.limit.return_value = session
    session.options.return_value = session
    session.all.return_value = []
    session.first.return_value = None
    session.count.return_value = 0
    session.get.return_value = None
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock(return_value=1)
    return session


@pytest.fixture
def patch_db_context(mock_db_session):
    """Patch database context manager to use mock session."""
    from contextlib import contextmanager

    @contextmanager
    def mock_context():
        yield mock_db_session

    with (
        patch("src.core.database.obtenir_contexte_db", mock_context),
        patch("src.core.database.get_db_context", mock_context),
    ):
        yield mock_db_session


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BASE SERVICE AVANCÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBaseServiceHelpers:
    """Tests des mÃ©thodes helper du BaseService."""

    def test_model_to_dict_exists(self):
        """Teste que _model_to_dict existe."""
        from src.core.models import Recette
        from src.services.base_service import BaseService

        service = BaseService(Recette)
        assert hasattr(service, "_model_to_dict")

    def test_apply_filters_exists(self):
        """Teste que _apply_filters existe."""
        from src.core.models import Recette
        from src.services.base_service import BaseService

        service = BaseService(Recette)
        assert hasattr(service, "_apply_filters")

    def test_with_session_exists(self):
        """Teste que _with_session existe."""
        from src.core.models import Recette
        from src.services.base_service import BaseService

        service = BaseService(Recette)
        assert hasattr(service, "_with_session")


class TestBaseServiceBulk:
    """Tests des opÃ©rations bulk du BaseService."""

    def test_bulk_create_with_merge_exists(self):
        """Teste que bulk_create_with_merge existe."""
        from src.core.models import Recette
        from src.services.base_service import BaseService

        service = BaseService(Recette)
        assert hasattr(service, "bulk_create_with_merge")
        assert callable(service.bulk_create_with_merge)


class TestBaseServiceStats:
    """Tests des statistiques du BaseService."""

    def test_get_stats_exists(self):
        """Teste que get_stats existe."""
        from src.core.models import Recette
        from src.services.base_service import BaseService

        service = BaseService(Recette)
        assert hasattr(service, "get_stats")
        assert callable(service.get_stats)

    def test_count_by_status_exists(self):
        """Teste que count_by_status existe."""
        from src.core.models import Recette
        from src.services.base_service import BaseService

        service = BaseService(Recette)
        assert hasattr(service, "count_by_status")
        assert callable(service.count_by_status)

    def test_mark_as_exists(self):
        """Teste que mark_as existe."""
        from src.core.models import Recette
        from src.services.base_service import BaseService

        service = BaseService(Recette)
        assert hasattr(service, "mark_as")
        assert callable(service.mark_as)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS NOTIFICATION SERVICE AVANCÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationServiceAdvanced:
    """Tests avancÃ©s du NotificationService."""

    def test_multiple_users_notifications(self):
        """Teste les notifications pour plusieurs utilisateurs."""
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        notif1 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Notification user 1",
            message="Message pour utilisateur 1",
        )

        notif2 = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=2,
            ingredient_id=20,
            titre="Notification user 2",
            message="Message pour utilisateur 2",
        )

        service.ajouter_notification(notif1, utilisateur_id=1)
        service.ajouter_notification(notif2, utilisateur_id=2)

        assert 1 in service.notifications
        assert 2 in service.notifications
        assert len(service.notifications[1]) == 1
        assert len(service.notifications[2]) == 1

    def test_different_types_same_article(self):
        """Teste diffÃ©rents types de notif pour le mÃªme article."""
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        notif1 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Stock bas",
            message="Stock bas pour cet article",
        )

        notif2 = Notification(
            type_alerte=TypeAlerte.PEREMPTION_PROCHE,  # Type diffÃ©rent
            article_id=1,
            ingredient_id=10,
            titre="PÃ©remption proche",
            message="PÃ©remption proche pour cet article",
        )

        service.ajouter_notification(notif1, utilisateur_id=1)
        service.ajouter_notification(notif2, utilisateur_id=1)

        # Les deux devraient Ãªtre ajoutÃ©es car types diffÃ©rents
        assert len(service.notifications[1]) == 2


class TestNotificationPriorities:
    """Tests des prioritÃ©s de notification."""

    def test_notification_haute_priorite(self):
        """Teste la notification haute prioritÃ©."""
        from src.services.notifications import Notification, TypeAlerte

        notif = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=1,
            ingredient_id=10,
            titre="Test haute prioritÃ©",
            message="Test message haute prioritÃ©",
            priorite="haute",
        )

        assert notif.priorite == "haute"

    def test_notification_basse_priorite(self):
        """Teste la notification basse prioritÃ©."""
        from src.services.notifications import Notification, TypeAlerte

        notif = Notification(
            type_alerte=TypeAlerte.ARTICLE_AJOUTE,
            article_id=1,
            ingredient_id=10,
            titre="Test basse prioritÃ©",
            message="Test message basse prioritÃ©",
            priorite="basse",
        )

        assert notif.priorite == "basse"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RECETTE SERVICE AVANCÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRecetteServiceInit:
    """Tests d'initialisation du RecetteService."""

    def test_recette_service_init(self):
        """Teste l'initialisation du RecetteService."""
        from src.services.recettes import RecetteService

        service = RecetteService()

        # Devrait hÃ©riter de BaseService et BaseAIService
        assert hasattr(service, "model")
        assert hasattr(service, "cache_ttl")

    def test_recette_service_has_crud_methods(self):
        """Teste que RecetteService a les mÃ©thodes CRUD."""
        from src.services.recettes import RecetteService

        service = RecetteService()

        assert hasattr(service, "create")
        assert hasattr(service, "get_by_id")
        assert hasattr(service, "get_all")
        assert hasattr(service, "update")
        assert hasattr(service, "delete")


class TestRecetteServiceMethods:
    """Tests des mÃ©thodes du RecetteService."""

    def test_has_search_method(self):
        """Teste que RecetteService a une mÃ©thode de recherche."""
        from src.services.recettes import RecetteService

        service = RecetteService()

        # Devrait avoir advanced_search de BaseService
        assert hasattr(service, "advanced_search")


class TestRecetteSuggestionValidation:
    """Tests de validation RecetteSuggestion."""

    def test_nom_trop_court(self):
        """Teste que nom trop court est rejetÃ©."""
        from pydantic import ValidationError

        from src.services.recettes import RecetteSuggestion

        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="AB",  # Min 3 caractÃ¨res
                description="Description valide pour le test",
                temps_preparation=20,
                temps_cuisson=30,
                portions=4,
                difficulte="facile",
                type_repas="dÃ®ner",
                ingredients=[],
                etapes=[],
            )

    def test_description_trop_courte(self):
        """Teste que description trop courte est rejetÃ©e."""
        from pydantic import ValidationError

        from src.services.recettes import RecetteSuggestion

        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Nom valide",
                description="Court",  # Min 10 caractÃ¨res
                temps_preparation=20,
                temps_cuisson=30,
                portions=4,
                difficulte="facile",
                type_repas="dÃ®ner",
                ingredients=[],
                etapes=[],
            )

    def test_difficulte_invalide(self):
        """Teste que difficultÃ© invalide est rejetÃ©e."""
        from pydantic import ValidationError

        from src.services.recettes import RecetteSuggestion

        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Nom valide",
                description="Description valide pour le test",
                temps_preparation=20,
                temps_cuisson=30,
                portions=4,
                difficulte="extreme",  # Doit Ãªtre facile, moyen ou difficile
                type_repas="dÃ®ner",
                ingredients=[],
                etapes=[],
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COURSES SERVICE AVANCÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCoursesServiceInit:
    """Tests d'initialisation du CoursesService."""

    def test_courses_service_init(self):
        """Teste l'initialisation du CoursesService."""
        from src.services.courses import CoursesService

        service = CoursesService()

        assert hasattr(service, "model")
        assert hasattr(service, "cache_ttl")

    def test_courses_service_has_crud_methods(self):
        """Teste que CoursesService a les mÃ©thodes CRUD."""
        from src.services.courses import CoursesService

        service = CoursesService()

        assert hasattr(service, "create")
        assert hasattr(service, "get_by_id")
        assert hasattr(service, "delete")


class TestSuggestionCoursesValidation:
    """Tests de validation SuggestionCourses."""

    def test_priorite_invalide(self):
        """Teste que prioritÃ© invalide est rejetÃ©e."""
        from pydantic import ValidationError

        from src.services.courses import SuggestionCourses

        with pytest.raises(ValidationError):
            SuggestionCourses(
                nom="Lait",
                quantite=2.0,
                unite="L",
                priorite="urgente",  # Doit Ãªtre haute, moyenne ou basse
                rayon="Produits frais",
            )

    def test_quantite_negative(self):
        """Teste que quantitÃ© nÃ©gative est rejetÃ©e."""
        from pydantic import ValidationError

        from src.services.courses import SuggestionCourses

        with pytest.raises(ValidationError):
            SuggestionCourses(
                nom="Lait",
                quantite=-1.0,  # Doit Ãªtre > 0
                unite="L",
                priorite="haute",
                rayon="Produits frais",
            )

    def test_normalisation_priority_high(self):
        """Teste la normalisation de priority 'high' â†’ 'haute'."""
        from src.services.courses import SuggestionCourses

        data = {
            "nom": "Pain",
            "quantite": 1.0,
            "unite": "unitÃ©",
            "priority": "high",
            "rayon": "Boulangerie",
        }

        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.priorite == "haute"

    def test_normalisation_priority_medium(self):
        """Teste la normalisation de priority 'medium' â†’ 'moyenne'."""
        from src.services.courses import SuggestionCourses

        data = {
            "nom": "Huile",
            "quantite": 1.0,
            "unite": "L",
            "priority": "medium",
            "rayon": "Ã‰picerie",
        }

        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.priorite == "moyenne"

    def test_normalisation_priority_low(self):
        """Teste la normalisation de priority 'low' â†’ 'basse'."""
        from src.services.courses import SuggestionCourses

        data = {
            "nom": "Serviettes",
            "quantite": 1.0,
            "unite": "paquet",
            "priority": "low",
            "rayon": "HygiÃ¨ne",
        }

        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.priorite == "basse"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PLANNING SERVICE AVANCÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPlanningServiceInit:
    """Tests d'initialisation du PlanningService."""

    def test_planning_service_init(self):
        """Teste l'initialisation du PlanningService."""
        from src.services.planning import PlanningService

        service = PlanningService()

        assert hasattr(service, "model")
        assert hasattr(service, "cache_ttl")

    def test_planning_service_has_crud_methods(self):
        """Teste que PlanningService a les mÃ©thodes CRUD."""
        from src.services.planning import PlanningService

        service = PlanningService()

        assert hasattr(service, "create")
        assert hasattr(service, "get_by_id")
        assert hasattr(service, "delete")


class TestParametresEquilibreValidation:
    """Tests de validation ParametresEquilibre."""

    def test_pates_riz_count_min(self):
        """Teste la valeur minimale de pates_riz_count."""
        from pydantic import ValidationError

        from src.services.planning import ParametresEquilibre

        with pytest.raises(ValidationError):
            ParametresEquilibre(pates_riz_count=0)  # Min = 1

    def test_pates_riz_count_max(self):
        """Teste la valeur maximale de pates_riz_count."""
        from pydantic import ValidationError

        from src.services.planning import ParametresEquilibre

        with pytest.raises(ValidationError):
            ParametresEquilibre(pates_riz_count=10)  # Max = 5


class TestJourPlanningValidation:
    """Tests de validation JourPlanning."""

    def test_jour_trop_court(self):
        """Teste que jour trop court est rejetÃ©."""
        from pydantic import ValidationError

        from src.services.planning import JourPlanning

        with pytest.raises(ValidationError):
            JourPlanning(
                jour="2026",  # Min 6 caractÃ¨res
                dejeuner="Salade",
                diner="Soupe",
            )

    def test_dejeuner_trop_court(self):
        """Teste que dÃ©jeuner trop court est rejetÃ©."""
        from pydantic import ValidationError

        from src.services.planning import JourPlanning

        with pytest.raises(ValidationError):
            JourPlanning(
                jour="2026-02-06",
                dejeuner="A",  # Min 3 caractÃ¨res
                diner="Soupe de lÃ©gumes",
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INVENTAIRE SERVICE AVANCÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestInventaireServiceInit:
    """Tests d'initialisation du InventaireService."""

    def test_inventaire_service_init(self):
        """Teste l'initialisation du InventaireService."""
        from src.services.inventaire import InventaireService

        service = InventaireService()

        assert hasattr(service, "model")
        assert hasattr(service, "cache_ttl")


class TestArticleImportValidation:
    """Tests de validation ArticleImport."""

    def test_nom_trop_court(self):
        """Teste que nom trop court est rejetÃ©."""
        from pydantic import ValidationError

        from src.services.inventaire import ArticleImport

        with pytest.raises(ValidationError):
            ArticleImport(
                nom="A",  # Min 2 caractÃ¨res
                quantite=1.0,
                quantite_min=0.5,
                unite="kg",
            )

    def test_quantite_negative(self):
        """Teste que quantitÃ© nÃ©gative est rejetÃ©e."""
        from pydantic import ValidationError

        from src.services.inventaire import ArticleImport

        with pytest.raises(ValidationError):
            ArticleImport(
                nom="Sel",
                quantite=-1.0,  # Doit Ãªtre >= 0
                quantite_min=0.5,
                unite="kg",
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS WEATHER SERVICE AVANCÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestMeteoJourValidation:
    """Tests de validation MeteoJour."""

    def test_meteo_jour_all_fields(self):
        """Teste MeteoJour avec tous les champs."""

        from src.services.weather import MeteoJour

        meteo = MeteoJour(
            date=date(2026, 2, 6),
            temperature_min=-5.0,
            temperature_max=15.0,
            temperature_moyenne=5.0,
            humidite=80,
            precipitation_mm=10.5,
            probabilite_pluie=70,
            vent_km_h=35.0,
            direction_vent="NO",
            uv_index=3,
            lever_soleil="07:30",
            coucher_soleil="18:00",
            condition="pluvieux",
            icone="ðŸŒ§ï¸",
        )

        assert meteo.direction_vent == "NO"
        assert meteo.uv_index == 3
        assert meteo.lever_soleil == "07:30"
        assert meteo.condition == "pluvieux"


class TestConseilJardinValidation:
    """Tests de validation ConseilJardin."""

    def test_conseil_jardin_defaults(self):
        """Teste les valeurs par dÃ©faut de ConseilJardin."""
        from src.services.weather import ConseilJardin

        conseil = ConseilJardin(titre="Arrosage", description="Arroser les plantes")

        assert conseil.priorite == 1
        assert conseil.icone == "ðŸŒ±"
        assert conseil.plantes_concernees == []
        assert conseil.action_recommandee == ""


class TestAlerteMeteoValidation:
    """Tests de validation AlerteMeteo."""

    def test_alerte_meteo_with_date_fin(self):
        """Teste AlerteMeteo avec date de fin."""

        from src.services.weather import AlerteMeteo, NiveauAlerte, TypeAlertMeteo

        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.CANICULE,
            niveau=NiveauAlerte.DANGER,
            titre="Canicule",
            message="Vague de chaleur prÃ©vue",
            conseil_jardin="Arroser matin et soir",
            date_debut=date(2026, 7, 15),
            date_fin=date(2026, 7, 20),
            temperature=38.0,
        )

        assert alerte.date_fin == date(2026, 7, 20)
        assert alerte.temperature == 38.0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BACKUP SERVICE AVANCÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupMetadataAdvanced:
    """Tests avancÃ©s de BackupMetadata."""

    def test_backup_metadata_with_values(self):
        """Teste BackupMetadata avec valeurs."""

        from src.services.backup import BackupMetadata

        now = datetime.now()

        meta = BackupMetadata(
            id="backup_20260206_123456",
            created_at=now,
            version="2.0",
            tables_count=15,
            total_records=5000,
            file_size_bytes=1024000,
            compressed=True,
            checksum="abc123def456",
        )

        assert meta.id == "backup_20260206_123456"
        assert meta.version == "2.0"
        assert meta.tables_count == 15
        assert meta.total_records == 5000
        assert meta.file_size_bytes == 1024000
        assert meta.compressed is True
        assert meta.checksum == "abc123def456"


class TestBackupConfigAdvanced:
    """Tests avancÃ©s de BackupConfig."""

    def test_all_options_disabled(self):
        """Teste avec toutes les options dÃ©sactivÃ©es."""
        from src.services.backup import BackupConfig

        config = BackupConfig(
            backup_dir="minimal_backups",
            max_backups=1,
            compress=False,
            include_timestamps=False,
            auto_backup_enabled=False,
            auto_backup_interval_hours=1,
        )

        assert config.compress is False
        assert config.include_timestamps is False
        assert config.auto_backup_enabled is False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VERSION GENEREE ADVANCED
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestVersionBebeGenereeAdvanced:
    """Tests avancÃ©s de VersionBebeGeneree."""

    def test_age_minimum_bounds(self):
        """Teste les bornes de age_minimum_mois."""
        from pydantic import ValidationError

        from src.services.recettes import VersionBebeGeneree

        # Age trop bas
        with pytest.raises(ValidationError):
            VersionBebeGeneree(
                instructions_modifiees="Test",
                notes_bebe="Notes",
                age_minimum_mois=4,  # Min = 6
            )

        # Age trop haut
        with pytest.raises(ValidationError):
            VersionBebeGeneree(
                instructions_modifiees="Test",
                notes_bebe="Notes",
                age_minimum_mois=48,  # Max = 36
            )


class TestVersionBatchCookingAdvanced:
    """Tests avancÃ©s de VersionBatchCookingGeneree."""

    def test_portions_bounds(self):
        """Teste les bornes de nombre_portions_recommande."""
        from pydantic import ValidationError

        from src.services.recettes import VersionBatchCookingGeneree

        # Portions trop basses
        with pytest.raises(ValidationError):
            VersionBatchCookingGeneree(
                instructions_modifiees="Test",
                nombre_portions_recommande=2,  # Min = 4
                temps_preparation_total_heures=2.0,
                conseils_conservation="Au frigo",
                conseils_congelation="Congeler",
                calendrier_preparation="Dimanche",
            )


class TestVersionRobotAdvanced:
    """Tests avancÃ©s de VersionRobotGeneree."""

    def test_temps_cuisson_bounds(self):
        """Teste les bornes de temps_cuisson_adapte_minutes."""
        from pydantic import ValidationError

        from src.services.recettes import VersionRobotGeneree

        # Temps trop court
        with pytest.raises(ValidationError):
            VersionRobotGeneree(
                instructions_modifiees="Test",
                reglages_robot="Vitesse 5",
                temps_cuisson_adapte_minutes=2,  # Min = 5
                conseils_preparation="Couper",
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE TYPES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestServiceTypes:
    """Tests du module types."""

    def test_import_base_service_from_types(self):
        """Teste l'import de BaseService depuis types."""
        from src.services.types import BaseService

        assert BaseService is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IO SERVICE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIOService:
    """Tests du service IO."""

    def test_import_io_service(self):
        """Teste l'import du module io_service."""
        from src.services import io_service

        assert io_service is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS AUTRES SERVICES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPWAService:
    """Tests du service PWA."""

    def test_import_pwa_service(self):
        """Teste l'import du module pwa."""
        from src.services import pwa

        assert pwa is not None


class TestRealtimeSyncService:
    """Tests du service realtime_sync."""

    def test_import_realtime_sync_service(self):
        """Teste l'import du module realtime_sync."""
        from src.services import realtime_sync

        assert realtime_sync is not None


class TestOpenFoodFactsService:
    """Tests du service openfoodfacts."""

    def test_import_openfoodfacts_service(self):
        """Teste l'import du module openfoodfacts."""
        from src.services import openfoodfacts

        assert openfoodfacts is not None


class TestPDFExportService:
    """Tests du service pdf_export."""

    def test_import_pdf_export_service(self):
        """Teste l'import du module pdf_export."""
        from src.services import pdf_export

        assert pdf_export is not None


class TestFactureOCRService:
    """Tests du service facture_ocr."""

    def test_import_facture_ocr_service(self):
        """Teste l'import du module facture_ocr."""
        from src.services import facture_ocr

        assert facture_ocr is not None


class TestCoursesIntelligentesService:
    """Tests du service courses_intelligentes."""

    def test_import_courses_intelligentes_service(self):
        """Teste l'import du module courses_intelligentes."""
        from src.services import courses_intelligentes

        assert courses_intelligentes is not None


class TestPlanningUnifiedService:
    """Tests du service planning_unified."""

    def test_import_planning_unified_service(self):
        """Teste l'import du module planning_unified."""
        from src.services import planning_unified

        assert planning_unified is not None


class TestActionHistoryService:
    """Tests du service action_history."""

    def test_import_action_history_service(self):
        """Teste l'import du module action_history."""
        from src.services import action_history

        assert action_history is not None


class TestNotificationsPushService:
    """Tests du service notifications_push."""

    def test_import_notifications_push_service(self):
        """Teste l'import du module notifications_push."""
        from src.services import notifications_push

        assert notifications_push is not None


class TestPushNotificationsService:
    """Tests du service push_notifications."""

    def test_import_push_notifications_service(self):
        """Teste l'import du module push_notifications."""
        from src.services import push_notifications

        assert push_notifications is not None


class TestRecipeImportService:
    """Tests du service recipe_import."""

    def test_import_recipe_import_service(self):
        """Teste l'import du module recipe_import."""
        from src.services import recipe_import

        assert recipe_import is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
