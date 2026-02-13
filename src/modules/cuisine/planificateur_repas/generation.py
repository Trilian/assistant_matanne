"""
Module Planificateur de Repas - Génération IA
"""

from ._common import date, generer_prompt_semaine, json, logger, obtenir_client_ia, st
from .preferences import charger_feedbacks, charger_preferences


def generer_semaine_ia(date_debut: date) -> dict:
    """Génère une semaine complète avec l'IA."""

    prefs = charger_preferences()
    feedbacks = charger_feedbacks()

    prompt = generer_prompt_semaine(prefs, feedbacks, date_debut)

    try:
        client = obtenir_client_ia()
        if not client:
            st.error("❌ Client IA non disponible")
            return {}

        response = client.generer_json(
            prompt=prompt,
            system_prompt="Tu es un assistant culinaire familial. Réponds UNIQUEMENT en JSON valide.",
        )

        if response and isinstance(response, dict):
            return response

        # Tenter de parser si c'est une string
        if isinstance(response, str):
            return json.loads(response)

    except Exception as e:
        logger.error(f"Erreur génération IA: {e}")
        st.error(f"❌ Erreur IA: {str(e)}")

    return {}
