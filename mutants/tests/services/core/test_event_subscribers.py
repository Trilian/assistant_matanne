"""Tests ciblÃ©s â€” Ã©vÃ©nements inter-modules et subscribers business."""

# pyright: reportPrivateUsage=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownVariableType=false

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from src.services.core.events.bus import EvenementDomaine


class TestJardinEventsSubscribe:
    def test_jardin_recolte_emis_depuis_modification(self):
        from src.services.maison.jardin_crud_mixin import JardinCrudMixin

        with patch("src.services.maison.jardin_crud_mixin.obtenir_bus") as mock_bus:
            JardinCrudMixin.emettre_modification(element_id=12, nom="Tomates", action="recolte")

        assert mock_bus.return_value.emettre.call_count == 2
        event_types = [call.args[0] for call in mock_bus.return_value.emettre.call_args_list]
        assert "jardin.modifie" in event_types
        assert "jardin.recolte" in event_types

    def test_budget_alertes_emet_depassement(self):
        from src.services.famille.budget.budget_alertes import BudgetAlertesMixin

        class _Categorie:
            value = "courses"

        class _Depense:
            categorie = _Categorie()
            montant = 120.0

        categorie_unique = _Depense.categorie

        class _Service(BudgetAlertesMixin):
            def get_tous_budgets(self, mois, annee, db=None):
                return {categorie_unique: 100.0}

            def get_depenses_mois(self, mois, annee, db=None):
                return [_Depense()]

        service = _Service()
        with patch("src.services.famille.budget.budget_alertes.emettre_evenement_simple") as emettre:
            alertes = service._verifier_alertes_budget(3, 2026, db=MagicMock())

        assert alertes
        emitted_types = [call.args[0] for call in emettre.call_args_list]
        assert "budget.depassement" in emitted_types


class TestEventSubscribers:
    def test_event_subscribers_enregistres(self):
        import src.services.core.events.subscribers as mod
        from src.services.core.events.subscribers import enregistrer_subscribers

        mod._subscribers_enregistres = False
        with patch("src.services.core.events.bus.obtenir_bus") as mock_bus_fn:
            mock_bus = MagicMock()
            mock_bus_fn.return_value = mock_bus
            enregistrer_subscribers()

        events = [call.args[0] for call in mock_bus.souscrire.call_args_list]
        assert "jardin.recolte" in events
        assert "energie.anomalie" in events
        assert "budget.depassement" in events
        assert "inventaire.modification_importante" in events
        assert "recette.feedback" in events
        assert "dashboard.widget.action_rapide" in events
        mod._subscribers_enregistres = False

    def test_subscriber_energie_cree_tache_entretien(self):
        from src.services.core.events.subscribers import _creer_tache_entretien_sur_anomalie_energie

        event = EvenementDomaine(
            type="energie.anomalie",
            data={"details": ["electricite: +35%"], "message": "Anomalie Ã©nergie dÃ©tectÃ©e"},
            source="test",
        )

        mock_session = MagicMock()

        @contextmanager
        def _ctx():
            yield mock_session

        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):
            _creer_tache_entretien_sur_anomalie_energie(event)

        assert mock_session.add.called
        assert mock_session.commit.called

    def test_subscriber_budget_dashboard_invalide_cache(self):
        from src.services.core.events.subscribers import _publier_alerte_dashboard_budget

        event = EvenementDomaine(type="budget.depassement", data={"categorie": "courses"}, source="test")
        with patch("src.core.caching.obtenir_cache") as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache_fn.return_value = mock_cache
            _publier_alerte_dashboard_budget(event)

        patterns = [call.kwargs.get("pattern") for call in mock_cache.invalidate.call_args_list]
        assert "dashboard" in patterns
        assert "budget" in patterns

    def test_subscriber_dashboard_widget_action_invalide_cache(self):
        from src.services.core.events.subscribers import _traiter_action_rapide_dashboard

        event = EvenementDomaine(
            type="dashboard.widget.action_rapide",
            data={"widget_id": "checklist_jour", "action": "valider_tache"},
            source="test",
        )
        with patch("src.core.caching.obtenir_cache") as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache_fn.return_value = mock_cache
            _traiter_action_rapide_dashboard(event)

        patterns = [call.kwargs.get("pattern") for call in mock_cache.invalidate.call_args_list]
        assert "dashboard" in patterns
