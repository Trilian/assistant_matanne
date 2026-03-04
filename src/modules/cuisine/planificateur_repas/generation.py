"""
Module Planificateur de Repas - Génération IA
"""

import logging
from datetime import date

import streamlit as st

from src.core.ai import obtenir_client_ia

from .preferences import charger_feedbacks, charger_preferences
from .utils import generer_prompt_alternative, generer_prompt_semaine

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = "Tu es un assistant culinaire familial. Réponds UNIQUEMENT en JSON valide, sans commentaire, sans markdown."


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
            system_prompt=_SYSTEM_PROMPT,
            max_tokens=3000,
        )

        # generer_json retourne déjà un dict parsé ou None — ne jamais re-parser
        if response and isinstance(response, dict):
            return response

        st.error("❌ Réponse IA invalide ou vide")

    except Exception as e:
        logger.error(f"Erreur génération IA semaine: {e}")
        st.error(f"❌ Erreur IA: {str(e)}")

    return {}


def sauvegarder_recette_ia(recette_dict: dict, type_repas_slot: str) -> int | None:
    """
    Sauvegarde une recette générée par l'IA dans la base de données.

    Args:
        recette_dict: Dict IA minimal {nom, proteine, temps_minutes, robot, difficulte, jules_adaptation}
        type_repas_slot: Slot d'origine ("midi", "soir", "gouter")

    Returns:
        ID de la recette créée, ou None en cas d'échec
    """
    try:
        from src.services.cuisine.recettes import obtenir_service_recettes

        # Mapping slot → type_repas DB
        _slot_to_type = {
            "midi": "déjeuner",
            "soir": "dîner",
            "gouter": "goûter",
        }
        type_repas_db = _slot_to_type.get(type_repas_slot, "dîner")

        # Mapping proteine → flags DB
        proteine = recette_dict.get("proteine", "")
        est_vegetarien = proteine == "vegetarien"
        type_proteines = proteine if proteine else None

        # Mapping robot → flags compatibilité
        robot = (recette_dict.get("robot") or "").lower()
        compatible_cookeo = "cookeo" in robot
        compatible_monsieur_cuisine = "monsieur" in robot
        compatible_airfryer = "airfryer" in robot
        compatible_multicooker = "multicooker" in robot

        temps = max(1, recette_dict.get("temps_minutes") or 30)
        nom = recette_dict.get("nom", "Recette IA").strip()
        difficulte = recette_dict.get("difficulte", "moyen")
        jules_adaptation = recette_dict.get("jules_adaptation", "")

        description_parts = ["Recette générée par l'IA via le planificateur."]
        if jules_adaptation:
            description_parts.append(f"Version Jules : {jules_adaptation}")
        description = " ".join(description_parts)

        # Générer les détails manquants (ingrédients/étapes) via IA
        ingredients = []
        etapes = []

        try:
            client = obtenir_client_ia()
            if client:
                prompt_details = f"""Génère les ingrédients et étapes pour la recette : "{nom}" (pour 4 personnes).
Réponds UNIQUEMENT en JSON valide :
{{
  "ingredients": [
    {{"nom": "nom ingrédient", "quantite": 100, "unite": "g"}}
  ],
  "etapes": [
    "Etape 1...",
    "Etape 2..."
  ]
}}"""
                details = client.generer_json(
                    prompt_details, system_prompt="Tu es un chef cuisinier.", max_tokens=1500
                )
                if details and isinstance(details, dict):
                    ingredients_raw = details.get("ingredients", [])
                    # Sanitization ingredients (conversion quantité en float obligatoire)
                    ingredients = []
                    import re

                    for ing in ingredients_raw:
                        q = ing.get("quantite", 0)
                        unite = ing.get("unite", "")
                        try:
                            if isinstance(q, str):
                                # Si c'est du texte comme "à votre goût", on met 0
                                # Sinon on essaie d'extraire un nombre (ex: "100g")
                                match = re.search(r"(\d+([.,]\d+)?)", q.replace(",", "."))
                                if match:
                                    q = float(match.group(1))
                                else:
                                    # Cas "sel, poivre", "à votre goût" -> quantité 0, et on met l'info dans l'unité si vide
                                    if not unite:
                                        unite = str(q)
                                    q = 0.0
                            else:
                                q = float(q)
                        except (ValueError, TypeError):
                            q = 0.0

                        ing["quantite"] = q
                        ing["unite"] = unite
                        ingredients.append(ing)

                    etapes_raw = details.get("etapes", [])
                    # Convertir étapes en format dict si nécessaire ou garder liste strings
                    # Le service attend souvent list[dict] ou list[str]. On va supposer list[dict] pour ingredients
                    # Pour étapes, ServiceRecettes.create_complete attend indexé ?
                    # Vérifions models/recettes.py, mais en général simple liste strings passe pour création simple
                    # ou liste de dicts avec "description".
                    if etapes_raw and isinstance(etapes_raw[0], str):
                        etapes = [
                            {"description": e, "ordre": i + 1} for i, e in enumerate(etapes_raw)
                        ]
                    else:
                        etapes = etapes_raw
        except Exception as e:
            logger.warning(f"Impossible de générer les détails pour {nom}: {e}")

        data = {
            "nom": nom,
            "description": description,
            "temps_preparation": temps,
            "temps_cuisson": 0,
            "portions": 4,
            "difficulte": difficulte,
            "type_repas": type_repas_db,
            "categorie": "Plat",
            "est_rapide": temps <= 30,
            "est_vegetarien": est_vegetarien,
            "compatible_batch": True,
            "genere_par_ia": True,
            "type_proteines": type_proteines,
            "compatible_cookeo": compatible_cookeo,
            "compatible_monsieur_cuisine": compatible_monsieur_cuisine,
            "compatible_airfryer": compatible_airfryer,
            "compatible_multicooker": compatible_multicooker,
            "ingredients": ingredients,
            "etapes": etapes,
        }

        service = obtenir_service_recettes()
        recette = service.create_complete(data)
        if recette:
            logger.info(f"✅ Recette IA sauvegardée : {nom} (ID: {recette.id})")
            return recette.id

    except Exception as e:
        logger.error(f"Erreur sauvegarde recette IA '{recette_dict.get('nom')}': {e}")

    return None


def generer_alternative_ia(
    recette_actuelle: dict,
    jour: str,
    type_repas: str,
    equilibre_actuel: dict | None = None,
) -> dict | None:
    """Génère une alternative à une recette pour un jour/repas donné."""

    prefs = charger_preferences()
    contraintes = equilibre_actuel or {}

    prompt = generer_prompt_alternative(
        recette_a_remplacer=recette_actuelle.get("nom", "recette inconnue"),
        type_repas=type_repas,
        jour=jour,
        preferences=prefs,
        contraintes_equilibre=contraintes,
    )

    try:
        client = obtenir_client_ia()
        if not client:
            return None

        response = client.generer_json(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT,
            max_tokens=800,
        )

        if response and isinstance(response, dict):
            alternatives = response.get("alternatives", [])
            if alternatives:
                # Prendre la première alternative et la formater
                alt = alternatives[0]
                return {
                    "nom": alt.get("nom", ""),
                    "proteine": alt.get("proteine", ""),
                    "temps_minutes": alt.get("temps_minutes", 30),
                    "robot": alt.get("robot"),
                    "difficulte": alt.get("difficulte", "facile"),
                    "jules_adaptation": alt.get("jules_adaptation", ""),
                }

    except Exception as e:
        logger.error(f"Erreur génération alternative IA: {e}")

    return None
