"""Tests unitaires phase 7 pour les nouvelles actions du moteur d'automations."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch


def _regle(
    id_: int = 1,
    user_id: int = 1,
    declencheur: dict | None = None,
    action: dict | None = None,
):
    return SimpleNamespace(
        id=id_,
        user_id=user_id,
        active=True,
        declencheur=declencheur or {"type": "feedback_recette_negatif", "jours": 30},
        action=action or {"type": "ajuster_suggestions_recette", "seuil_note": 2},
        execution_count=0,
        derniere_execution=None,
    )


class TestAutomationsPhase7:
    def test_feedback_recette_negatif_ajuste_les_suggestions(self):
        from src.services.utilitaires.automations_engine import MoteurAutomationsService

        service = MoteurAutomationsService()
        regle = _regle()

        with (
            patch.object(
                service,
                "_declenche_feedback_recette_negatif",
                return_value=[SimpleNamespace(recette_id=12, feedback="dislike", user_id="matanne")],
            ),
            patch.object(service, "_executer_action_ajuster_suggestions_recette", return_value=1),
        ):
            result = service._executer_une_regle(regle, db=MagicMock())

        assert result["success"] is True
        assert result["executed"] == 1

    def test_planning_valide_genere_les_courses(self):
        from src.services.utilitaires.automations_engine import MoteurAutomationsService

        service = MoteurAutomationsService()
        regle = _regle(
            declencheur={"type": "planning_valide", "jours": 14},
            action={"type": "generer_courses_planning"},
        )

        with (
            patch.object(service, "_declenche_planning_valide", return_value=[SimpleNamespace(id=5, semaine_debut=None)]),
            patch.object(service, "_executer_action_generer_courses_planning", return_value=1),
        ):
            result = service._executer_une_regle(regle, db=MagicMock())

        assert result["success"] is True
        assert result["executed"] == 1

    def test_batch_termine_pre_remplit_le_planning(self):
        from src.services.utilitaires.automations_engine import MoteurAutomationsService

        service = MoteurAutomationsService()
        regle = _regle(
            declencheur={"type": "batch_termine", "jours": 7},
            action={"type": "pre_remplir_planning_batch"},
        )

        with (
            patch.object(service, "_declenche_batch_termine", return_value=[SimpleNamespace(id=7)]),
            patch.object(service, "_executer_action_pre_remplir_planning_batch", return_value=1),
        ):
            result = service._executer_une_regle(regle, db=MagicMock())

        assert result["success"] is True
        assert result["executed"] == 1
