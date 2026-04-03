"""Tests unitaires pour src/services/utilitaires/automations_engine.py (moteur automations)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch


def _regle(
    id_: int = 1,
    user_id: int = 1,
    declencheur: dict | None = None,
    action: dict | None = None,
    active: bool = True,
):
    return SimpleNamespace(
        id=id_,
        user_id=user_id,
        active=active,
        declencheur=declencheur or {"type": "stock_bas", "seuil": 2},
        action=action or {"type": "ajouter_courses", "quantite": 1},
        execution_count=0,
        derniere_execution=None,
    )


class TestMoteurAutomationsService:
    @staticmethod
    def _unwrap(func):
        """Retire les décorateurs (@wraps) pour tester la logique métier pure."""
        unwrapped = func
        while hasattr(unwrapped, "__wrapped__"):
            unwrapped = unwrapped.__wrapped__
        return unwrapped

    def test_declencheur_non_supporte_retourne_erreur(self):
        from src.services.utilitaires.automations_engine import MoteurAutomationsService

        service = MoteurAutomationsService()
        regle = _regle(declencheur={"type": "inconnu"})

        result = service._executer_une_regle(regle, db=MagicMock())

        assert result["success"] is False
        assert "Déclencheur non supporté" in result["message"]
        assert result["automation_id"] == regle.id

    def test_action_non_supportee_retourne_erreur(self):
        from src.services.utilitaires.automations_engine import MoteurAutomationsService

        service = MoteurAutomationsService()
        regle = _regle(action={"type": "action_inconnue"})

        with patch.object(service, "_declenche_stock_bas", return_value=[SimpleNamespace(nom="Lait")]):
            result = service._executer_une_regle(regle, db=MagicMock())

        assert result["success"] is False
        assert "Action non supportée" in result["message"]

    def test_action_notifier_succes(self):
        from src.services.utilitaires.automations_engine import MoteurAutomationsService

        service = MoteurAutomationsService()
        regle = _regle(action={"type": "notifier", "titre": "Stock bas"})
        items = [SimpleNamespace(nom="Lait"), SimpleNamespace(nom="Oeufs")]

        mock_dispatcher = MagicMock()
        mock_dispatcher.envoyer.return_value = {"ntfy": True, "push": False}

        with (
            patch.object(service, "_declenche_stock_bas", return_value=items),
            patch("src.services.utilitaires.automations_engine.get_dispatcher_notifications", return_value=mock_dispatcher),
        ):
            result = service._executer_une_regle(regle, db=MagicMock())

        assert result["success"] is True
        assert result["executed"] == 1
        assert result["items_declenches"] == 2
        assert regle.execution_count == 1

    def test_executer_automation_par_id_refuse_autre_user(self):
        from src.services.utilitaires.automations_engine import MoteurAutomationsService

        service = MoteurAutomationsService()
        regle = _regle(id_=7, user_id=42)

        db = MagicMock()
        db.get.return_value = regle

        method = self._unwrap(service.executer_automation_par_id)
        result = method(
            service,
            automation_id=7,
            user_id=99,
            db=db,
        )

        assert result["success"] is False
        assert result["message"] == "Automation introuvable"

    def test_executer_automation_par_id_inactive(self):
        from src.services.utilitaires.automations_engine import MoteurAutomationsService

        service = MoteurAutomationsService()
        regle = _regle(id_=9, user_id=1, active=False)

        db = MagicMock()
        db.get.return_value = regle

        method = self._unwrap(service.executer_automation_par_id)
        result = method(
            service,
            automation_id=9,
            user_id=1,
            db=db,
        )

        assert result["success"] is False
        assert result["message"] == "Automation inactive"
