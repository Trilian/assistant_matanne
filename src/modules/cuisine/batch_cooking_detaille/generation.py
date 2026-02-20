"""Génération IA pour le module Batch Cooking Détaillé."""

import json
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

RÉPONDS EN JSON avec cette structure EXACTE:
{
  "session": {
    "duree_estimee_minutes": 120,
    "conseils_organisation": ["Conseil 1", "Conseil 2"]
  },
  "recettes": [
    {
      "nom": "Nom recette",
      "pour_jours": ["Lundi midi", "Mardi soir"],
      "portions": 4,
      "ingredients": [
        {
          "nom": "carottes",
          "quantite": 2,
          "unite": "pièces",
          "poids_g": 200,
          "description": "taille moyenne",
          "decoupe": "rondelles",
          "taille_decoupe": "1cm",
          "instruction_prep": "Éplucher et laver",
          "jules_peut_aider": true,
          "tache_jules": "Laver les carottes"
        }
      ],
      "etapes_batch": [
        {
          "titre": "Préparer les légumes",
          "description": "Éplucher et couper tous les légumes",
          "duree_minutes": 15,
          "est_passif": false,
          "robot": null,
          "jules_participation": true,
          "tache_jules": "Mettre les légumes dans le saladier"
        },
        {
          "titre": "Cuisson Cookeo",
          "description": "Cuisson sous pression des légumes",
          "duree_minutes": 20,
          "est_passif": true,
          "robot": {
            "type": "cookeo",
            "programme": "Sous pression",
            "duree_secondes": 1200
          },
          "jules_participation": false
        }
      ],
      "instructions_finition": [
        "Sortir du frigo 15min avant",
        "Réchauffer 5min au micro-ondes"
      ],
      "stockage": "frigo",
      "duree_conservation_jours": 4,
      "temps_finition_minutes": 10,
      "version_jules": "Mixer la portion de Jules plus finement"
    }
  ],
  "moments_jules": [
    "0-15min: Laver les légumes ensemble",
    "30-40min: Mélanger les ingrédients"
  ],
  "liste_courses": {
    "fruits_legumes": [
      {"nom": "carottes", "quantite": 4, "unite": "pièces", "poids_g": 400}
    ],
    "viandes": [],
    "cremerie": [],
    "epicerie": [],
    "surgeles": []
  }
}

IMPORTANT:
- Découpes possibles: rondelles, cubes, julienne, brunoise, lamelles, cisele, emince, rape
- Monsieur Cuisine: vitesse 1-10, duree_secondes, temperature
- Cookeo: programme (Sous pression, Dorer, Mijoter, Cuisson rapide, Cuisson douce)
- Four: mode (Chaleur tournante, Grill), temperature, duree_secondes
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
            system_prompt="Tu es un expert batch cooking. Réponds UNIQUEMENT en JSON valide.",
        )

        if response and isinstance(response, dict):
            return response

        if isinstance(response, str):
            return json.loads(response)

    except Exception as e:
        logger.error(f"Erreur génération batch IA: {e}")
        st.error(f"❌ Erreur IA: {str(e)}")

    return {}
