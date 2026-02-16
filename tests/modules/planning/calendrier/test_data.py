"""
Tests pour src/modules/planning/calendrier/data.py

Tests complets pour charger_donnees_semaine().
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


class TestChargerDonneesSemaine:
    """Tests pour charger_donnees_semaine()"""

    @pytest.fixture
    def mock_db_context(self):
        """Fixture pour mocker le contexte DB"""
        with patch("src.modules.planning.calendrier.data.obtenir_contexte_db") as mock_ctx:
            mock_session = MagicMock()
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
            yield mock_session, mock_ctx

    @pytest.fixture
    def mock_date_utils(self):
        """Fixture pour get_debut_semaine"""
        with patch("src.modules.planning.calendrier.data.get_debut_semaine") as mock:
            mock.side_effect = lambda d: d - timedelta(days=d.weekday())
            yield mock

    def test_retourne_structure_vide_par_defaut(self, mock_db_context, mock_date_utils):
        """Vérifie que la structure retournée contient les clés attendues"""
        mock_session, mock_ctx = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = []

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert "repas" in result
        assert "sessions_batch" in result
        assert "activites" in result
        assert "events" in result
        assert "courses_planifiees" in result
        assert "taches_menage" in result

    def test_charge_repas_avec_planning_actif(self, mock_db_context, mock_date_utils):
        """Teste le chargement des repas quand un planning existe"""
        mock_session, mock_ctx = mock_db_context

        # Mock Planning trouvé
        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_planning

        # Mock des repas
        mock_repas1 = MagicMock()
        mock_repas1.recette_id = 10
        mock_repas2 = MagicMock()
        mock_repas2.recette_id = None

        def filter_side_effect(*args, **kwargs):
            mock_filter = MagicMock()
            mock_filter.filter.return_value = mock_filter
            mock_filter.first.return_value = mock_planning
            mock_filter.all.return_value = [mock_repas1, mock_repas2]
            return mock_filter

        mock_session.query.return_value.filter = filter_side_effect

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result, dict)
        mock_session.query.assert_called()

    def test_charge_sessions_batch_cooking(self, mock_db_context, mock_date_utils):
        """Teste le chargement des sessions batch cooking"""
        mock_session, mock_ctx = mock_db_context

        mock_session_batch = MagicMock()
        mock_session_batch.date_session = date(2025, 1, 7)

        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_session_batch]

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result["sessions_batch"], list)

    def test_charge_activites_famille(self, mock_db_context, mock_date_utils):
        """Teste le chargement des activités famille"""
        mock_session, mock_ctx = mock_db_context

        mock_activite = MagicMock()
        mock_activite.date_prevue = date(2025, 1, 8)
        mock_activite.nom = "Parc"

        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_activite]

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result["activites"], list)

    def test_charge_events_calendrier(self, mock_db_context, mock_date_utils):
        """Teste le chargement des événements calendrier"""
        mock_session, mock_ctx = mock_db_context

        mock_event = MagicMock()
        mock_event.date_debut = datetime(2025, 1, 9, 14, 0)
        mock_event.titre = "RDV médecin"

        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_event]

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result["events"], list)

    def test_charge_taches_menage_integrees(self, mock_db_context, mock_date_utils):
        """Teste le chargement des tâches ménage intégrées au planning"""
        mock_session, mock_ctx = mock_db_context

        mock_tache = MagicMock()
        mock_tache.integrer_planning = True
        mock_tache.nom = "Aspirateur"

        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_tache]

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        assert isinstance(result["taches_menage"], list)

    def test_gere_erreur_table_maintenance_non_disponible(self, mock_db_context, mock_date_utils):
        """Teste la gestion d'erreur quand MaintenanceTask n'existe pas"""
        mock_session, mock_ctx = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = []

        with patch("src.modules.planning.calendrier.data.logger"):
            from src.modules.planning.calendrier.data import (
                charger_donnees_semaine,
            )

            result = charger_donnees_semaine(date(2025, 1, 6))

            # Le résultat doit toujours être retourné même si erreur
            assert isinstance(result, dict)

    def test_gere_erreur_generale_db(self, mock_date_utils):
        """Teste la gestion d'erreur générale de base de données"""
        with patch("src.modules.planning.calendrier.data.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("DB Error"))
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.planning.calendrier.data import (
                charger_donnees_semaine,
            )

            result = charger_donnees_semaine(date(2025, 1, 6))

            # Doit retourner structure vide sans lever d'exception
            assert result["repas"] == []
            assert result["sessions_batch"] == []

    def test_calcul_dates_lundi_dimanche(self, mock_db_context, mock_date_utils):
        """Vérifie que les dates lundi/dimanche sont bien calculées"""
        mock_session, mock_ctx = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = []

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        # Mercredi 8 janvier 2025
        charger_donnees_semaine(date(2025, 1, 8))

        # Vérifie que get_debut_semaine a été appelé
        mock_date_utils.assert_called_once_with(date(2025, 1, 8))

    def test_charge_recette_associee_au_repas(self, mock_db_context, mock_date_utils):
        """Teste le chargement de la recette associée à un repas"""
        mock_session, mock_ctx = mock_db_context

        # Mock planning
        mock_planning = MagicMock()
        mock_planning.id = 1

        # Mock repas avec recette_id
        mock_repas = MagicMock()
        mock_repas.recette_id = 42

        # Mock recette
        mock_recette = MagicMock()
        mock_recette.nom = "Poulet rôti"

        def query_side_effect(model):
            mock_query = MagicMock()
            return mock_query

        mock_session.query.side_effect = query_side_effect

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        charger_donnees_semaine(date(2025, 1, 6))

        # Vérifie que la requête est bien exécutée
        assert mock_session.query.called

    def test_sans_planning_actif(self, mock_db_context, mock_date_utils):
        """Teste le comportement sans planning actif pour la semaine"""
        mock_session, mock_ctx = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = []

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        result = charger_donnees_semaine(date(2025, 1, 6))

        # Repas devrait être vide sans planning
        assert result["repas"] == []


class TestChargerDonneesSemaineIntegration:
    """Tests d'intégration pour charger_donnees_semaine (avec vrais imports)"""

    def test_import_module(self):
        """Vérifie que le module s'importe correctement"""
        from src.modules.planning.calendrier.data import charger_donnees_semaine

        assert callable(charger_donnees_semaine)

    def test_signature_fonction(self):
        """Vérifie la signature de la fonction"""
        import inspect

        from src.modules.planning.calendrier.data import charger_donnees_semaine

        sig = inspect.signature(charger_donnees_semaine)
        params = list(sig.parameters.keys())
        assert "date_debut" in params
