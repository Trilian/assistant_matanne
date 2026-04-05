"""Tests service AssistantProactif."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.services.ia_avancee.types import PlanningAdaptatif
from src.services.utilitaires.chat.assistant_proactif import AssistantProactifService


def test_traiter_evenement_repas_saute_declenche_un_reajustement_de_planning():
    """Un repas sauté doit produire une suggestion concrète de réajustement."""
    service = AssistantProactifService()

    faux_service_ia = MagicMock()
    faux_service_ia.generer_suggestions_proactives.return_value = None
    faux_service_ia.generer_planning_adaptatif.return_value = PlanningAdaptatif(
        recommandations=["Décaler le repas prévu à demain et garder une option rapide ce soir."],
        repas_suggerees=[
            {"jour": "Mardi", "repas": "Omelette express", "raison": "soirée plus chargée"}
        ],
        activites_suggerees=[],
        score_adaptation=81,
        contexte_utilise={"planning": True},
    )

    with patch(
        "src.services.utilitaires.assistant_proactif.get_ia_avancee_service",
        return_value=faux_service_ia,
    ):
        resultat = service.traiter_evenement(
            "planning.repas_saute",
            {"repas_nom": "Gratin de légumes", "jour": "lundi", "budget_restant": 42.0},
        )

    assert resultat["status"] == "updated"
    faux_service_ia.generer_planning_adaptatif.assert_called_once()

    payload = service.obtenir_derniere_suggestion()
    messages = " ".join(str(item.get("message", "")) for item in payload["suggestions"])
    titres = " ".join(str(item.get("titre", "")) for item in payload["suggestions"])

    assert "planning" in payload["event_type"]
    assert "réajust" in (titres + " " + messages).lower() or "décaler" in messages.lower()
