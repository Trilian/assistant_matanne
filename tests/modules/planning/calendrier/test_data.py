"""
Tests pour src/modules/planning/calendrier/data.py

Tests pour charger_donnees_semaine() — facade vers ServiceCalendrierPlanning.
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


class TestChargerDonneesSemaine:
    """Tests pour charger_donnees_semaine()"""

    @pytest.fixture(autouse=True)
    def reset_service(self):
        """Reset le singleton du service entre chaque test."""
        import src.modules.planning.calendrier.data as data_mod

        data_mod._service = None
        yield
        data_mod._service = None

    @pytest.fixture
    def mock_service(self):
        """Fixture pour mocker le service calendrier planning."""
        mock_svc = MagicMock()
        with patch(
            "src.modules.planning.calendrier.data._get_service",
            return_value=mock_svc,
        ):
            yield mock_svc

    def _default_donnees(self, **overrides):
        """Retourne une structure de données par défaut."""
        donnees = {
            "repas": [],
            "sessions_batch": [],
            "activites": [],
            "events": [],
            "courses_planifiees": [],
            "taches_menage": [],
        }
        donnees.update(overrides)
        return donnees

    def test_retourne_structure_vide_par_defaut(self, mock_service):
        """Vérifie que la structure retournée contient les clés attendues."""
        mock_service.charger_donnees_semaine.return_value = self._default_donnees()

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert "repas" in result
        assert "sessions_batch" in result
        assert "activites" in result
        assert "events" in result
        assert "courses_planifiees" in result
        assert "taches_menage" in result

    def test_charge_repas_avec_planning_actif(self, mock_service):
        """Teste le chargement des repas quand un planning existe."""
        mock_repas = [MagicMock(), MagicMock()]
        mock_service.charger_donnees_semaine.return_value = self._default_donnees(repas=mock_repas)

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result, dict)
        assert len(result["repas"]) == 2
        mock_service.charger_donnees_semaine.assert_called_once_with(date(2025, 1, 6))

    def test_charge_sessions_batch_cooking(self, mock_service):
        """Teste le chargement des sessions batch cooking."""
        mock_session_batch = MagicMock()
        mock_session_batch.date_session = date(2025, 1, 7)
        mock_service.charger_donnees_semaine.return_value = self._default_donnees(
            sessions_batch=[mock_session_batch]
        )

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result["sessions_batch"], list)
        assert len(result["sessions_batch"]) == 1

    def test_charge_activites_famille(self, mock_service):
        """Teste le chargement des activités famille."""
        mock_activite = MagicMock()
        mock_activite.date_prevue = date(2025, 1, 8)
        mock_service.charger_donnees_semaine.return_value = self._default_donnees(
            activites=[mock_activite]
        )

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result["activites"], list)
        assert len(result["activites"]) == 1

    def test_charge_events_calendrier(self, mock_service):
        """Teste le chargement des événements calendrier."""
        mock_event = MagicMock()
        mock_event.date_debut = datetime(2025, 1, 9, 14, 0)
        mock_service.charger_donnees_semaine.return_value = self._default_donnees(
            events=[mock_event]
        )

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result["events"], list)
        assert len(result["events"]) == 1

    def test_charge_taches_menage_integrees(self, mock_service):
        """Teste le chargement des tâches ménage intégrées au planning."""
        mock_tache = MagicMock()
        mock_tache.integrer_planning = True
        mock_service.charger_donnees_semaine.return_value = self._default_donnees(
            taches_menage=[mock_tache]
        )

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result["taches_menage"], list)
        assert len(result["taches_menage"]) == 1

    def test_gere_erreur_table_maintenance_non_disponible(self, mock_service):
        """Teste la gestion d'erreur quand le service retourne taches_menage vide."""
        mock_service.charger_donnees_semaine.return_value = self._default_donnees()

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result, dict)
        assert result["taches_menage"] == []

    def test_gere_erreur_generale_db(self):
        """Teste la gestion d'erreur générale de base de données."""
        with patch(
            "src.modules.planning.calendrier.data._get_service",
        ) as mock_get:
            mock_get.return_value.charger_donnees_semaine.side_effect = Exception("DB Error")

            from src.modules.planning.calendrier.data import charger_donnees_semaine

            result = charger_donnees_semaine(date(2025, 1, 6))

            # Doit retourner structure vide sans lever d'exception
            assert result["repas"] == []
            assert result["sessions_batch"] == []

    def test_delegue_au_service(self, mock_service):
        """Vérifie que charger_donnees_semaine délègue au service."""
        mock_service.charger_donnees_semaine.return_value = self._default_donnees()

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        charger_donnees_semaine(date(2025, 1, 8))

        mock_service.charger_donnees_semaine.assert_called_once_with(date(2025, 1, 8))

    def test_charge_recette_associee_au_repas(self, mock_service):
        """Teste que les repas avec recettes sont chargés via le service."""
        mock_repas = MagicMock()
        mock_repas.recette_id = 42
        mock_repas.recette = MagicMock(nom="Poulet rôti")
        mock_service.charger_donnees_semaine.return_value = self._default_donnees(
            repas=[mock_repas]
        )

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert len(result["repas"]) == 1
        assert result["repas"][0].recette.nom == "Poulet rôti"

    def test_sans_planning_actif(self, mock_service):
        """Teste le comportement sans planning actif pour la semaine."""
        mock_service.charger_donnees_semaine.return_value = self._default_donnees()

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert result["repas"] == []


class TestChargerDonneesSemaineIntegration:
    """Tests d'intégration pour charger_donnees_semaine (avec vrais imports)"""

    def test_import_module(self):
        """Vérifie que le module s'importe correctement."""
        from src.modules.planning.calendrier.data import charger_donnees_semaine

        assert callable(charger_donnees_semaine)

    def test_signature_fonction(self):
        """Vérifie la signature de la fonction."""
        import inspect

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        sig = inspect.signature(charger_donnees_semaine)
        params = list(sig.parameters.keys())
        assert "date_debut" in params
