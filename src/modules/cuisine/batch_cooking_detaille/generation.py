"""Génération IA pour le module Batch Cooking Détaillé.

Wrapper UI mince — toute la logique IA (prompt, sanitization, retry,
chunking) est dans le service :
``src.services.cuisine.batch_cooking.batch_cooking_ia.BatchCookingIAMixin``
"""

import logging

import streamlit as st

from src.services.cuisine.batch_cooking import get_batch_cooking_service

logger = logging.getLogger(__name__)


def generer_batch_ia(
    planning_data: dict, type_session: str, avec_jules: bool, robots_user: list[str] | None = None
) -> dict:
    """Génère les instructions de batch cooking via le service IA.

    Délègue à ``ServiceBatchCooking.generer_plan_depuis_planning()`` qui gère
    sanitization des entrées, retry avec @avec_resilience, chunking et
    validation Pydantic.
    """
    try:
        service = get_batch_cooking_service()
        result = service.generer_plan_depuis_planning(
            planning_data=planning_data,
            type_session=type_session,
            avec_jules=avec_jules,
            robots_user=robots_user,
        )
        if result:
            return result

        st.error(
            "❌ L'IA n'a pas pu générer les instructions. "
            "Vérifie ta connexion et réessaie."
        )
    except Exception as e:
        logger.error("Erreur génération batch IA: %s", e, exc_info=True)
        st.error(f"❌ Erreur IA: {e}")

    return {}
