"""Génération IA pour le module Batch Cooking Détaillé."""

import logging

import streamlit as st

from src.core.ai import obtenir_client_ia
from src.modules.cuisine.batch_cooking_temps import ROBOTS_INFO

logger = logging.getLogger(__name__)


def generer_batch_ia(
    planning_data: dict, type_session: str, avec_jules: bool, robots_user: list[str] | None = None
) -> dict:
    """Génère les instructions de batch cooking avec l'IA."""

    # Robots disponibles
    if not robots_user:
        robots_user = ["four", "plaques"]
    robots_txt = []
    for r in robots_user:
        info = ROBOTS_INFO.get(r, {})
        parallel = "peut fonctionner en parallèle" if info.get("peut_parallele") else "UNE tâche à la fois"
        robots_txt.append(f"  - {info.get('nom', r)} ({parallel})")
    robots_section = "\n".join(robots_txt)

    prompt = f"""Tu es un expert en batch cooking familial. Génère des instructions ULTRA-DÉTAILLÉES et CONCRÈTES.

SESSION: {type_session.upper()}
{"Avec Jules (19 mois) - prévoir des tâches simples et sécurisées pour lui" if avec_jules else "Session solo"}

ÉQUIPEMENT DISPONIBLE:
{robots_section}

RECETTES À PRÉPARER:
"""

    for jour, repas in planning_data.items():
        for type_repas in ["midi", "soir"]:
            r = repas.get(type_repas, {})
            if r and isinstance(r, dict) and not r.get("est_rechauffe"):
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
      "pour_jours": ["Lundi midi"],
      "portions": 4,
      "ingredients": [
        {
          "nom": "carottes",
          "quantite": "500g",
          "decoupe": "rondelles de 5mm",
          "tache_jules": "Laver sous l'eau"
        }
      ],
      "etapes_batch": [
        {
          "titre": "Éplucher et découper les carottes en rondelles de 5mm",
          "duree_minutes": 10,
          "robot": null,
          "temperature": null,
          "est_passif": false,
          "detail": "Utiliser l'économe. Découper les carottes en rondelles régulières de 5mm.",
          "jules_participation": true,
          "tache_jules": "Laver les carottes dans la passoire"
        },
        {
          "titre": "Cuire les carottes au Cookeo 12min",
          "duree_minutes": 12,
          "robot": "cookeo",
          "temperature": null,
          "est_passif": true,
          "detail": "Programme pression, 12 minutes. Ajouter 100ml d'eau.",
          "jules_participation": false,
          "tache_jules": null
        }
      ],
      "instructions_finition": [
        "Réchauffer 3min micro-ondes ou 5min poêle avec une noix de beurre."
      ],
      "stockage": "Boîte hermétique au frigo",
      "duree_conservation_jours": 3
    }
  ],
  "moments_jules": [
    {"temps": "0-15min", "tache": "Laver les légumes dans la passoire"},
    {"temps": "30-35min", "tache": "Verser les pâtes dans le saladier"}
  ],
  "timeline": [
    {"debut_min": 0, "fin_min": 15, "tache": "Découpe légumes (manuel)", "robot": null},
    {"debut_min": 0, "fin_min": 12, "tache": "Cuisson carottes", "robot": "cookeo"},
    {"debut_min": 15, "fin_min": 30, "tache": "Préparation viande", "robot": "monsieur_cuisine"}
  ]
}

RÈGLES IMPÉRATIVES:
1. CHAQUE étape doit être CONCRÈTE: type de découpe exact, quantité en grammes, température en °C, durée exacte
2. JAMAIS "les légumes" → NOMMER: "200g de courgettes en dés de 1cm + 300g de carottes en rondelles"
3. Si un robot est utilisé: programme exact, température, vitesse, durée
4. PARALLÉLISER au maximum: pendant qu'un robot tourne (est_passif), travailler sur une autre recette
5. La timeline doit montrer ce qui se fait EN MÊME TEMPS
6. Quantités: TOUJOURS en grammes ou ml (sauf pièces pour oeufs, oignons)
7. Instructions finition = ce qu'on fait le jour J pour servir (réchauffer, assaisonner)
8. Jules 19 mois: UNIQUEMENT laver, mélanger dans un bol, verser des ingrédients (pas de couteau, pas de chaleur)
- Réponds UNIQUEMENT en JSON valide, sans commentaire, sans markdown.
"""

    try:
        client = obtenir_client_ia()
        if not client:
            st.error("❌ Client IA non disponible")
            return {}

        response = client.generer_json(
            prompt=prompt,
            system_prompt="Tu es un chef expérimenté spécialiste du batch cooking familial. Réponds UNIQUEMENT en JSON valide. Sois TRÈS détaillé et concret sur les découpes, poids, températures et temps.",
            max_tokens=8000,
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
