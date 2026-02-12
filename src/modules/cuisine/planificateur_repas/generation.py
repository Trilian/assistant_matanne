"""
Module Planificateur de Repas - GÃenÃeration IA
"""

from ._common import (
    st, date, json, logger,
    obtenir_client_ia, generer_prompt_semaine
)
from .preferences import charger_preferences, charger_feedbacks


def generer_semaine_ia(date_debut: date) -> dict:
    """GÃenère une semaine complète avec l'IA."""
    
    prefs = charger_preferences()
    feedbacks = charger_feedbacks()
    
    prompt = generer_prompt_semaine(prefs, feedbacks, date_debut)
    
    try:
        client = obtenir_client_ia()
        if not client:
            st.error("âŒ Client IA non disponible")
            return {}
        
        response = client.generer_json(
            prompt=prompt,
            system_prompt="Tu es un assistant culinaire familial. RÃeponds UNIQUEMENT en JSON valide.",
        )
        
        if response and isinstance(response, dict):
            return response
        
        # Tenter de parser si c'est une string
        if isinstance(response, str):
            return json.loads(response)
        
    except Exception as e:
        logger.error(f"Erreur gÃenÃeration IA: {e}")
        st.error(f"âŒ Erreur IA: {str(e)}")
    
    return {}
