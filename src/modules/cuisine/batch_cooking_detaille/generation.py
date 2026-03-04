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
            if r:
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
          "poids_g": 200,
          "decoupe": "rondelles",
          "taille_decoupe": "1cm",
          "instruction_prep": "Éplucher et laver",
          "tache_jules": "Laver les carottes (si applicable)"
        }
      ],
      "etapes_batch": [
        {
          "titre": "Préparer les légumes",
          "description": "Éplucher et couper...",
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
  ]
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
            system_prompt="Tu es un expert batch cooking. Réponds UNIQUEMENT en JSON valide, sans commentaire, sans markdown.",
            max_tokens=3000,
        )

        # generer_json retourne déjà un dict parsé — ne jamais re-parser
        if response and isinstance(response, dict):
            return response

        st.error("❌ Réponse IA invalide ou vide (essaie de simplifier le planning)")

    except Exception as e:
        logger.error(f"Erreur génération batch IA: {e}")
        st.error(f"❌ Erreur IA: {str(e)}")

    return {}
