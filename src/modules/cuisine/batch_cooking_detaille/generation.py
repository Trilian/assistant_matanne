"""Génération IA pour le module Batch Cooking Détaillé."""

import logging

import streamlit as st

from src.core.ai import obtenir_client_ia

logger = logging.getLogger(__name__)


def generer_batch_ia(planning_data: dict, type_session: str, avec_jules: bool) -> dict:
    """Génère les instructions de batch cooking avec l'IA."""

    prompt = f"""Tu es un expert en batch cooking familial. Génère des instructions TRÈS DÉTAILLÉES.

SESSION: {type_session.upper()}
{"Avec Jules (19 mois) - prévoir des tâches simples et sécurisées" if avec_jules else "Session solo"}

RECETTES À PRÉPARER:
"""

    for jour, repas in planning_data.items():
        for type_repas in ["midi", "soir"]:
            r = repas.get(type_repas, {})
            if r and isinstance(r, dict) and not r.get("est_rechauffe"):
                prompt += f"\n- {jour} {type_repas}: {r.get('nom', 'Recette')}"

    prompt += """

RÉPONDS EN JSON avec cette structure EXACTE (réponse courte et stricte):
{
  "session": {
    "duree_estimee_minutes": 120,
    "conseils_organisation": ["Conseil 1", "Conseil 2"]
  },
  "recettes": [
    {
      "nom": "Nom recette",
      "pour_jours": ["Lundi midi"],
      "portions": 4,
      "ingredients": [
        {
          "nom": "carottes",
          "quantite": 2,
          "unite": "pièces",
          "decoupe": "rondelles",
          "tache_jules": "Laver"
        }
      ],
      "etapes_batch": [
        {
          "titre": "Préparer les légumes",
          "duree_minutes": 15,
          "est_passif": false,
          "jules_participation": true,
          "tache_jules": "Laver..."
        }
      ],
      "instructions_finition": [
        "Réchauffer..."
      ],
      "stockage": "frigo",
      "duree_conservation_jours": 3
    }
  ],
  "moments_jules": [
    "0-15min: Laver les légumes"
  ],
  "liste_courses": {
    "Fruits et légumes": ["carottes 500g", "oignons 3 pièces"],
    "Viandes": ["poulet 600g"],
    "Epicerie": ["huile olive", "sel"]
  }
}

IMPORTANT:
- Réponds UNIQUEMENT en JSON.
- Quantités: TOUJOURS poids approximatif en grammes
- Jules 19 mois: tâches TRÈS simples (laver, mélanger, verser)
"""

    try:
        client = obtenir_client_ia()
        if not client:
            st.error("❌ Client IA non disponible")
            return {}

        response = client.generer_json(
            prompt=prompt,
            system_prompt="Tu es un expert batch cooking. Réponds UNIQUEMENT en JSON valide, sans commentaire, sans markdown. Sois concis.",
            max_tokens=6000,
        )

        # generer_json retourne un dict parsé, une string brute, ou None
        if response and isinstance(response, dict):
            # Valider la structure minimale
            if "recettes" not in response or not isinstance(response.get("recettes"), list):
                logger.warning(f"Réponse IA sans 'recettes' valide. Clés: {list(response.keys())}")
                # Tenter de récupérer si la structure est imbriquée
                if "session" in response and isinstance(response["session"], dict):
                    inner = response["session"]
                    if isinstance(inner.get("recettes"), list):
                        response["recettes"] = inner["recettes"]
            return response

        # Fallback: si generer_json a retourné une string brute, tenter le parsing
        if response and isinstance(response, str):
            import json

            logger.warning("generer_json batch a retourné une string, tentative parse manuelle")
            try:
                from src.core.ai.parser import AnalyseurIA

                json_str = AnalyseurIA._extraire_objet_json(response)
                json_str = AnalyseurIA._reparer_intelligemment(json_str)
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

        # Debugging info if JSON fails
        if response:
            logger.warning(f"Réponse IA invalide (non-dict): {str(response)[:500]}...")
        else:
            logger.warning("Réponse IA vide (None)")

        st.error("❌ Réponse IA invalide ou vide (essaie de simplifier le planning)")

    except Exception as e:
        logger.error(f"Erreur génération batch IA: {e}")
        st.error(f"❌ Erreur IA: {str(e)}")

    return {}
