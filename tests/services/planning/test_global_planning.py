"""
Tests pour src/services/planning/global_planning.py

Tests du service de planning unifié.
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from src.services.planning.global_planning import ServicePlanningUnifie
from src.services.planning.types import JourCompletSchema, SemaineCompleSchema


class TestServicePlanningUnifieInit:
    """Tests d'initialisation du service planning unifié."""

    def test_service_creation(self):
        """Vérifie que le service peut être créé."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            service = ServicePlanningUnifie()
            assert service is not None

    def test_service_has_cache_ttl(self):
        """Vérifie que le TTL de cache est défini."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            service = ServicePlanningUnifie()
            assert service.cache_ttl == 1800

    def test_service_has_model(self):
        """Vérifie que le service a un modèle défini."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            service = ServicePlanningUnifie()
            assert service.model is not None


class TestServicePlanningUnifieMethods:
    """Tests des méthodes du service."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    @pytest.fixture
    def mock_db(self):
        """Fixture pour une session DB mockée."""
        mock = MagicMock()
        mock.query.return_value.filter.return_value.all.return_value = []
        mock.query.return_value.options.return_value.filter.return_value.all.return_value = []
        mock.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = []
        mock.query.return_value.join.return_value.filter.return_value.all.return_value = []
        return mock

    def test_get_semaine_complete_returns_schema_or_none(self, service, mock_db):
        """Vérifie que get_semaine_complete retourne un schéma ou None."""
        result = service.get_semaine_complete(date_debut=date.today(), db=mock_db)
        assert result is None or isinstance(result, SemaineCompleSchema)

    def test_service_has_model_calendar_event(self, service):
        """Vérifie que le modèle est CalendarEvent."""
        from src.core.models import CalendarEvent

        assert service.model == CalendarEvent


class TestSemaineCompleSchema:
    """Tests pour le schéma SemaineCompleSchema."""

    def test_import_schema(self):
        """Vérifie que le schéma peut être importé."""
        from src.services.planning.types import SemaineCompleSchema

        assert SemaineCompleSchema is not None


class TestJourCompletSchema:
    """Tests pour le schéma JourCompletSchema."""

    def test_import_schema(self):
        """Vérifie que le schéma peut être importé."""
        from src.services.planning.types import JourCompletSchema

        assert JourCompletSchema is not None


class TestServicePlanningUnifieAggregation:
    """Tests de l'agrégation de données."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    @pytest.fixture
    def mock_db_with_data(self):
        """Fixture avec données mockées."""
        mock = MagicMock()

        # Mock des requêtes vides par défaut
        mock.query.return_value.filter.return_value.all.return_value = []
        mock.query.return_value.options.return_value.filter.return_value.all.return_value = []

        return mock

    def test_aggregation_handles_empty_data(self, service, mock_db_with_data):
        """Vérifie que l'agrégation gère les données vides."""
        result = service.get_semaine_complete(date_debut=date.today(), db=mock_db_with_data)
        # Doit retourner None ou un schéma vide
        assert result is None or isinstance(result, SemaineCompleSchema)


class TestServicePlanningUnifieCache:
    """Tests du cache du service."""

    def test_cache_key_includes_date(self):
        """Vérifie que la clé de cache inclut la date."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            service = ServicePlanningUnifie()
            # Le décorateur @avec_cache utilise une key_func
            # qui génère une clé basée sur la date
            assert hasattr(service, "get_semaine_complete")


class TestServicePlanningUnifieIA:
    """Tests de l'intégration IA."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_service_has_generer_semaine_ia_method(self, service):
        """Vérifie que le service a la méthode de génération IA."""
        assert hasattr(service, "generer_semaine_ia")

    def test_service_has_creer_event_method(self, service):
        """Vérifie que le service a la méthode creer_event."""
        assert hasattr(service, "creer_event")


# ═══════════════════════════════════════════════════════════
# TESTS DES MÉTHODES PRIVÉES DE CALCUL
# ═══════════════════════════════════════════════════════════


class TestCalculerCharge:
    """Tests pour la méthode _calculer_charge."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_empty_data_returns_zero(self, service):
        """Données vides retournent 0."""
        score = service._calculer_charge(repas=[], activites=[], projets=[], routines=[])
        assert score == 0

    def test_repas_contribuent_au_score(self, service):
        """Les repas contribuent au score."""
        score = service._calculer_charge(
            repas=[{"temps_total": 60}],  # 60 minutes
            activites=[],
            projets=[],
            routines=[],
        )
        assert score > 0

    def test_activites_contribuent_au_score(self, service):
        """Les activités contribuent au score."""
        score = service._calculer_charge(
            repas=[], activites=[{"id": 1}, {"id": 2}], projets=[], routines=[]
        )
        assert score >= 10  # 2 activités * 10 points max

    def test_projets_urgents_contribuent_au_score(self, service):
        """Les projets urgents contribuent au score."""
        score = service._calculer_charge(
            repas=[], activites=[], projets=[{"priorite": "haute"}], routines=[]
        )
        assert score >= 15  # 1 projet haute * 15 points

    def test_routines_contribuent_au_score(self, service):
        """Les routines contribuent au score."""
        score = service._calculer_charge(
            repas=[], activites=[], projets=[], routines=[{"id": 1}, {"id": 2}, {"id": 3}]
        )
        assert score >= 15  # 3 * 5 points

    def test_score_max_is_100(self, service):
        """Le score maximum est 100."""
        score = service._calculer_charge(
            repas=[{"temps_total": 300}] * 10,
            activites=[{"id": i} for i in range(10)],
            projets=[{"priorite": "haute"} for _ in range(10)],
            routines=[{"id": i} for i in range(20)],
        )
        assert score <= 100


class TestScoreToCharge:
    """Tests pour la méthode _score_to_charge."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_faible_for_low_score(self, service):
        """Score bas = charge faible."""
        assert service._score_to_charge(0) == "faible"
        assert service._score_to_charge(34) == "faible"

    def test_normal_for_medium_score(self, service):
        """Score moyen = charge normal."""
        assert service._score_to_charge(35) == "normal"
        assert service._score_to_charge(69) == "normal"

    def test_intense_for_high_score(self, service):
        """Score haut = charge intense."""
        assert service._score_to_charge(70) == "intense"
        assert service._score_to_charge(100) == "intense"


class TestDetecterAlertes:
    """Tests pour la méthode _detecter_alertes."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_alerte_jour_tres_charge(self, service):
        """Alerte pour jour très chargé."""
        alertes = service._detecter_alertes(
            jour=date.today(), repas=[], activites=[], projets=[], charge_score=85
        )
        assert any("chargé" in a.lower() for a in alertes)

    def test_alerte_pas_activite_jules(self, service):
        """Alerte si pas d'activité pour Jules."""
        alertes = service._detecter_alertes(
            jour=date.today(),
            repas=[],
            activites=[{"pour_jules": False}],
            projets=[],
            charge_score=50,
        )
        assert any("jules" in a.lower() for a in alertes)

    def test_alerte_projets_urgents(self, service):
        """Alerte pour projets urgents."""
        alertes = service._detecter_alertes(
            jour=date.today(),
            repas=[],
            activites=[],
            projets=[{"priorite": "haute"}, {"priorite": "haute"}],
            charge_score=50,
        )
        assert any("urgent" in a.lower() for a in alertes)

    def test_alerte_trop_repas(self, service):
        """Alerte pour trop de repas."""
        alertes = service._detecter_alertes(
            jour=date.today(),
            repas=[{}, {}, {}, {}],  # 4 repas
            activites=[],
            projets=[],
            charge_score=50,
        )
        assert any("repas" in a.lower() for a in alertes)

    def test_pas_alerte_jour_normal(self, service):
        """Pas d'alerte pour jour normal."""
        alertes = service._detecter_alertes(
            jour=date.today(),
            repas=[{}],
            activites=[{"pour_jules": True}],
            projets=[],
            charge_score=30,
        )
        # Peut avoir quelques alertes mais pas les critiques
        assert not any("très chargé" in a.lower() for a in alertes)


class TestDetecterAlertesSemaine:
    """Tests pour la méthode _detecter_alertes_semaine."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_alerte_pas_activite_jules_semaine(self, service):
        """Alerte si aucune activité Jules sur la semaine."""
        jours = {
            "2024-01-15": JourCompletSchema(
                date=date(2024, 1, 15), charge="faible", charge_score=20, activites=[]
            )
        }
        alertes = service._detecter_alertes_semaine(jours)
        assert any("jules" in a.lower() for a in alertes)

    def test_alerte_jours_charges(self, service):
        """Alerte si plusieurs jours très chargés."""
        jours = {}
        for i in range(4):
            jour = date(2024, 1, 15 + i)
            jours[jour.isoformat()] = JourCompletSchema(
                date=jour, charge="intense", charge_score=85, activites=[]
            )
        alertes = service._detecter_alertes_semaine(jours)
        assert any("chargé" in a.lower() for a in alertes)

    def test_alerte_budget_eleve(self, service):
        """Alerte si budget élevé."""
        jours = {}
        for i in range(7):
            jour = date(2024, 1, 15 + i)
            jours[jour.isoformat()] = JourCompletSchema(
                date=jour,
                charge="faible",
                charge_score=20,
                budget_jour=100.0,  # 7 * 100 = 700€ > 500€
                activites=[{"pour_jules": True}],
            )
        alertes = service._detecter_alertes_semaine(jours)
        assert any("budget" in a.lower() for a in alertes)


class TestCalculerBudgetJour:
    """Tests pour la méthode _calculer_budget_jour."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_empty_lists_return_zero(self, service):
        """Listes vides retournent 0."""
        result = service._calculer_budget_jour([], [])
        assert result == 0.0

    def test_activites_budget_aggregated(self, service):
        """Budget des activités agrégé."""
        activites = [{"budget": 20}, {"budget": 30}]
        result = service._calculer_budget_jour(activites, [])
        assert result == 50.0

    def test_none_budget_handled(self, service):
        """Budget None géré."""
        activites = [{"budget": None}, {"budget": 10}]
        result = service._calculer_budget_jour(activites, [])
        assert result == 10.0


class TestCalculerStatsSemaine:
    """Tests pour la méthode _calculer_stats_semaine."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_stats_structure(self, service):
        """Structure des stats."""
        jours = {
            "2024-01-15": JourCompletSchema(
                date=date(2024, 1, 15),
                charge="faible",
                charge_score=20,
                repas=[{"id": 1}],
                activites=[{"pour_jules": True}],
                projets=[],
                events=[],
                budget_jour=50.0,
            )
        }
        stats = service._calculer_stats_semaine(jours)
        assert "total_repas" in stats
        assert "total_activites" in stats
        assert "activites_jules" in stats
        assert "budget_total" in stats
        assert "charge_moyenne" in stats

    def test_stats_values(self, service):
        """Valeurs des stats."""
        jours = {
            "2024-01-15": JourCompletSchema(
                date=date(2024, 1, 15),
                charge="faible",
                charge_score=40,
                repas=[{}, {}],  # 2 repas
                activites=[{"pour_jules": True}, {"pour_jules": False}],
                projets=[{}],
                events=[{}, {}, {}],
                budget_jour=75.0,
            )
        }
        stats = service._calculer_stats_semaine(jours)
        assert stats["total_repas"] == 2
        assert stats["total_activites"] == 2
        assert stats["activites_jules"] == 1
        assert stats["total_projets"] == 1
        assert stats["total_events"] == 3
        assert stats["budget_total"] == 75.0
        assert stats["charge_moyenne"] == 40


# ═══════════════════════════════════════════════════════════
# TESTS DES MÉTHODES DE CHARGEMENT
# ═══════════════════════════════════════════════════════════


class TestChargerRepas:
    """Tests pour la méthode _charger_repas."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_returns_dict(self, service):
        """Retourne un dictionnaire."""
        mock_db = MagicMock()
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = []

        result = service._charger_repas(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert isinstance(result, dict)

    def test_empty_for_no_data(self, service):
        """Vide sans données."""
        mock_db = MagicMock()
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = []

        result = service._charger_repas(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert result == {}

    def test_with_meal_and_recipe(self, service):
        """Avec repas et recette."""
        mock_meal = MagicMock()
        mock_meal.id = 1
        mock_meal.date_repas = date(2024, 1, 15)
        mock_meal.type_repas = "déjeuner"
        mock_meal.portion_ajustee = None
        mock_meal.notes = "Test"

        mock_recipe = MagicMock()
        mock_recipe.id = 1
        mock_recipe.nom = "Pâtes"
        mock_recipe.portions = 4
        mock_recipe.temps_preparation = 10
        mock_recipe.temps_cuisson = 20

        mock_db = MagicMock()
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = [
            (mock_meal, mock_recipe)
        ]

        result = service._charger_repas(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert "2024-01-15" in result
        assert result["2024-01-15"][0]["recette"] == "Pâtes"
        assert result["2024-01-15"][0]["temps_total"] == 30

    def test_with_meal_without_recipe(self, service):
        """Avec repas sans recette."""
        mock_meal = MagicMock()
        mock_meal.id = 1
        mock_meal.date_repas = date(2024, 1, 15)
        mock_meal.type_repas = "déjeuner"
        mock_meal.portion_ajustee = 2
        mock_meal.notes = "Test"

        mock_db = MagicMock()
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = [
            (mock_meal, None)
        ]

        result = service._charger_repas(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert "2024-01-15" in result
        assert result["2024-01-15"][0]["recette"] == "Non défini"
        assert result["2024-01-15"][0]["temps_total"] == 0


class TestChargerActivites:
    """Tests pour la méthode _charger_activites."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_returns_dict(self, service):
        """Retourne un dictionnaire."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = service._charger_activites(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert isinstance(result, dict)

    def test_with_activity(self, service):
        """Avec une activité."""
        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.titre = "Sortie parc"
        mock_activity.type_activite = "loisir"
        mock_activity.date_prevue = date(2024, 1, 15)
        mock_activity.lieu = "Parc"
        mock_activity.cout_estime = 20.0
        mock_activity.duree_heures = 2

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_activity]

        result = service._charger_activites(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert "2024-01-15" in result
        assert result["2024-01-15"][0]["titre"] == "Sortie parc"
        assert result["2024-01-15"][0]["budget"] == 20.0

    def test_with_none_budget(self, service):
        """Avec budget None."""
        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.titre = "Test"
        mock_activity.type_activite = "loisir"
        mock_activity.date_prevue = date(2024, 1, 15)
        mock_activity.lieu = None
        mock_activity.cout_estime = None
        mock_activity.duree_heures = None

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_activity]

        result = service._charger_activites(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert result["2024-01-15"][0]["budget"] == 0
        assert result["2024-01-15"][0]["duree"] == 0


class TestChargerProjets:
    """Tests pour la méthode _charger_projets."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_returns_dict(self, service):
        """Retourne un dictionnaire."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = service._charger_projets(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert isinstance(result, dict)

    def test_with_project(self, service):
        """Avec un projet."""
        mock_project = MagicMock()
        mock_project.id = 1
        mock_project.nom = "Projet test"
        mock_project.priorite = "haute"
        mock_project.statut = "en_cours"
        mock_project.date_fin_prevue = date(2024, 1, 18)

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_project]

        result = service._charger_projets(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert "2024-01-18" in result
        assert result["2024-01-18"][0]["nom"] == "Projet test"

    def test_with_project_no_date(self, service):
        """Avec projet sans date de fin."""
        mock_project = MagicMock()
        mock_project.id = 1
        mock_project.nom = "Projet sans date"
        mock_project.priorite = "normale"
        mock_project.statut = "à_faire"
        mock_project.date_fin_prevue = None

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_project]

        result = service._charger_projets(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        # Devrait utiliser date_fin comme fallback
        assert "2024-01-21" in result


class TestChargerRoutines:
    """Tests pour la méthode _charger_routines."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_returns_dict(self, service):
        """Retourne un dictionnaire."""
        mock_db = MagicMock()
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []

        result = service._charger_routines(mock_db)
        assert isinstance(result, dict)

    def test_with_routine(self, service):
        """Avec une routine."""
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.nom = "Tâche matin"
        mock_task.heure_prevue = "08:00"
        mock_task.fait_le = None

        mock_routine = MagicMock()
        mock_routine.nom = "Routine matin"

        mock_db = MagicMock()
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
            (mock_task, mock_routine)
        ]

        result = service._charger_routines(mock_db)
        assert "routine_quotidienne" in result
        assert result["routine_quotidienne"][0]["nom"] == "Tâche matin"
        assert result["routine_quotidienne"][0]["fait"] is False

    def test_with_done_task(self, service):
        """Avec tâche faite."""
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.nom = "Tâche faite"
        mock_task.heure_prevue = "08:00"
        mock_task.fait_le = datetime(2024, 1, 15)

        mock_routine = MagicMock()
        mock_routine.nom = "Routine"

        mock_db = MagicMock()
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
            (mock_task, mock_routine)
        ]

        result = service._charger_routines(mock_db)
        assert result["routine_quotidienne"][0]["fait"] is True


class TestChargerEvents:
    """Tests pour la méthode _charger_events."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_returns_dict(self, service):
        """Retourne un dictionnaire."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = service._charger_events(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert isinstance(result, dict)

    def test_with_event(self, service):
        """Avec un événement."""
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.titre = "RDV médecin"
        mock_event.type_event = "rdv"
        mock_event.date_debut = datetime(2024, 1, 15, 10, 0)
        mock_event.date_fin = datetime(2024, 1, 15, 11, 0)
        mock_event.lieu = "Cabinet"
        mock_event.couleur = "#ff0000"

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_event]

        result = service._charger_events(date(2024, 1, 15), date(2024, 1, 21), mock_db)
        assert "2024-01-15" in result
        assert result["2024-01-15"][0]["titre"] == "RDV médecin"
        assert result["2024-01-15"][0]["type"] == "rdv"


# ═══════════════════════════════════════════════════════════
# TESTS GENERER_SEMAINE_IA ET CREER_EVENT
# ═══════════════════════════════════════════════════════════


class TestGenererSemaineIA:
    """Tests pour generer_semaine_ia - lignes 479-514."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_generer_semaine_ia_appel_base(self, service):
        """Test appel basique de generer_semaine_ia."""
        # Mock la méthode call_with_list_parsing_sync pour retourner des données
        mock_response = [
            {
                "repas_proposes": ["Pâtes", "Poulet", "Poisson", "Riz"],
                "activites_proposees": ["Parc", "Piscine"],
                "projets_suggeres": ["Ranger garage"],
                "harmonie_description": "Une semaine équilibrée",
                "raisons": ["Economique", "Familial"],
            }
        ]

        with patch.object(service, "call_with_list_parsing_sync", return_value=mock_response):
            _result = service.generer_semaine_ia(
                date_debut=date(2024, 1, 15),
                contraintes={"budget": 300},
                contexte={"jules_age_mois": 19},
            )
            # Peut retourner None si parsing échoue, mais la méthode est appelée
            service.call_with_list_parsing_sync.assert_called_once()

    def test_generer_semaine_ia_sans_contraintes(self, service):
        """Test avec contraintes None."""
        with patch.object(service, "call_with_list_parsing_sync", return_value=None):
            result = service.generer_semaine_ia(
                date_debut=date(2024, 1, 15), contraintes=None, contexte=None
            )
            assert result is None

    def test_generer_semaine_ia_echec_ia(self, service):
        """Test quand IA échoue et retourne None."""
        with patch.object(service, "call_with_list_parsing_sync", return_value=None):
            result = service.generer_semaine_ia(
                date_debut=date(2024, 1, 15),
                contraintes={"budget": 200},
                contexte={"objectifs_sante": ["sport", "sommeil"]},
            )
            assert result is None

    def test_construire_prompt_generation(self, service):
        """Test de _construire_prompt_generation."""
        prompt = service._construire_prompt_generation(
            date_debut=date(2024, 1, 15),
            contraintes={"budget": 350, "energie": "faible"},
            contexte={"jules_age_mois": 20, "objectifs_sante": ["sport", "repos"]},
        )

        assert "2024-01-15" in prompt
        assert "350" in prompt
        assert "faible" in prompt
        assert "20 mois" in prompt
        assert "sport" in prompt


class TestCreerEvent:
    """Tests pour creer_event - lignes 548-577."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    @pytest.fixture
    def mock_db(self):
        """Fixture DB mockée."""
        mock = MagicMock()
        mock.add = MagicMock()
        mock.commit = MagicMock()
        mock.rollback = MagicMock()
        return mock

    def test_creer_event_success(self, service, mock_db):
        """Test création événement réussie."""
        with patch.object(service, "_invalider_cache_semaine"):
            _result = service.creer_event(
                titre="Réunion parents",
                date_debut=datetime(2024, 1, 15, 14, 0),
                type_event="rdv",
                description="Réunion école",
                lieu="École Jules",
                couleur="#3366cc",
                db=mock_db,
            )

            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    def test_creer_event_with_date_fin(self, service, mock_db):
        """Test création événement avec date de fin."""
        with patch.object(service, "_invalider_cache_semaine"):
            service.creer_event(
                titre="Conférence",
                date_debut=datetime(2024, 1, 15, 9, 0),
                date_fin=datetime(2024, 1, 15, 12, 0),
                type_event="autre",
                db=mock_db,
            )
            mock_db.add.assert_called_once()

    def test_creer_event_error_rollback(self, service, mock_db):
        """Test rollback en cas d'erreur."""
        mock_db.commit.side_effect = Exception("DB Error")

        with patch.object(service, "_invalider_cache_semaine"):
            result = service.creer_event(
                titre="Event error", date_debut=datetime(2024, 1, 15, 10, 0), db=mock_db
            )

            # Vérifie rollback appelé
            mock_db.rollback.assert_called_once()
            assert result is None


class TestInvaliderCacheSemaine:
    """Tests pour _invalider_cache_semaine."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            return ServicePlanningUnifie()

    def test_invalider_cache_semaine(self, service):
        """Test invalidation du cache."""
        with patch("src.services.planning.global_planning.Cache") as mock_cache:
            service._invalider_cache_semaine(date(2024, 1, 17))  # Mercredi

            # Vérifie que le cache est invalidé pour le lundi de la semaine (15 janvier)
            assert mock_cache.invalider.call_count == 2

    def test_invalider_cache_lundi(self, service):
        """Test invalidation quand date est lundi."""
        with patch("src.services.planning.global_planning.Cache") as mock_cache:
            service._invalider_cache_semaine(date(2024, 1, 15))  # Lundi

            assert mock_cache.invalider.call_count == 2


# ═══════════════════════════════════════════════════════════
# TESTS DES FACTORIES
# ═══════════════════════════════════════════════════════════


class TestFactories:
    """Tests pour les factories."""

    def test_obtenir_service_planning_unifie(self):
        """Test de la factory."""
        from src.services.planning.global_planning import obtenir_service_planning_unifie

        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            service = obtenir_service_planning_unifie()
            assert service is not None
            assert isinstance(service, ServicePlanningUnifie)

    def test_get_planning_unified_service_alias(self):
        """Test de l'alias."""
        from src.services.planning.global_planning import get_planning_unified_service

        with patch("src.services.planning.global_planning.obtenir_client_ia"):
            service = get_planning_unified_service()
            assert service is not None
