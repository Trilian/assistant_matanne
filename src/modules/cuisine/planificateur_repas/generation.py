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


def generer_semaine_ia(
    date_debut: date,
    date_fin: date | None = None,
    jours_a_planifier: list[str] | None = None,
    bases_choisies: dict[str, list[str]] | None = None,
    recettes_imposees: list[str] | None = None,
    mode: str = "ia",
) -> dict:
    """Génère une semaine complète avec l'IA.

    Args:
        mode: "ia" (génération pure IA) ou "mixte" (priorité recettes DB).
    """

    prefs = charger_preferences()
    feedbacks = charger_feedbacks()

    # En mode mixte, charger les noms de recettes existantes
    recettes_existantes = None
    if mode == "mixte":
        try:
            from src.services.cuisine.recettes import obtenir_service_recettes

            service = obtenir_service_recettes()
            if service:
                all_recipes = service.get_all(limit=200)
                recettes_existantes = [r.nom for r in all_recipes] if all_recipes else None
        except Exception:
            pass

    prompt = generer_prompt_semaine(
        prefs,
        feedbacks,
        date_debut,
        jours_a_planifier,
        bases_choisies=bases_choisies,
        recettes_imposees=recettes_imposees,
        recettes_existantes=recettes_existantes,
    )

    try:
        client = obtenir_client_ia()
        if not client:
            st.error("❌ Client IA non disponible")
            return {}

        response = client.generer_json(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT,
            max_tokens=6000,
            temperature=0.8,
            utiliser_cache=False,
        )

        # generer_json retourne un dict parsé, une string brute, ou None
        if response and isinstance(response, dict):
            return response

        # Fallback: si generer_json a retourné une string brute, tenter le parsing
        if response and isinstance(response, str):
            import json
            import re

            logger.warning("generer_json a retourné une string, tentative de parse manuelle")
            try:
                from src.core.ai.parser import AnalyseurIA

                json_str = AnalyseurIA._extraire_objet_json(response)
                json_str = AnalyseurIA._reparer_intelligemment(json_str)
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                # Dernier recours: regex
                try:
                    cleaned = re.sub(r",\s*([}\]])", r"\1", response)
                    cleaned = re.sub(r'"\s*\n\s*"', '",\n"', cleaned)
                    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(0))
                        if isinstance(parsed, dict):
                            return parsed
                except Exception:
                    pass

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
        difficulte_raw = (recette_dict.get("difficulte") or "moyen").lower().strip()
        _DIFFICULTE_MAP = {
            "facile": "facile",
            "easy": "facile",
            "simple": "facile",
            "moyen": "moyen",
            "moyenne": "moyen",
            "medium": "moyen",
            "modéré": "moyen",
            "moderé": "moyen",
            "difficile": "difficile",
            "hard": "difficile",
            "complexe": "difficile",
        }
        difficulte = _DIFFICULTE_MAP.get(difficulte_raw, "moyen")
        jules_adaptation = recette_dict.get("jules_adaptation", "")

        # Utiliser les ingrédients/étapes déjà présents dans le dict IA si disponibles
        description = ""
        ingredients = []
        etapes = []
        temps_cuisson = 0
        portions_ia = 4

        # Vérifier si le dict IA contient déjà des données substantielles
        _ingredients_ia = recette_dict.get("ingredients", [])
        _etapes_ia = recette_dict.get("etapes", [])
        _has_good_data = (
            isinstance(_ingredients_ia, list)
            and len(_ingredients_ia) >= 2
            and isinstance(_etapes_ia, list)
            and len(_etapes_ia) >= 2
        )

        if _has_good_data:
            # Utiliser directement les données du prompt IA — pas besoin d'un 2e appel
            import re as _re

            for ing in _ingredients_ia:
                if not isinstance(ing, dict):
                    continue
                q = ing.get("quantite", 0)
                unite = ing.get("unite", "")
                try:
                    if isinstance(q, str):
                        match = _re.search(r"(\d+([.,]\d+)?)", q.replace(",", "."))
                        if match:
                            q = float(match.group(1))
                        else:
                            if not unite:
                                unite = str(q)
                            q = 0.01
                    else:
                        q = float(q)
                except (ValueError, TypeError):
                    q = 0.01
                if q <= 0:
                    q = 0.01
                ing["quantite"] = q
                ing["unite"] = unite
                ingredients.append(ing)

            if _etapes_ia and isinstance(_etapes_ia[0], str):
                etapes = [
                    {"description": e, "ordre": i + 1} for i, e in enumerate(_etapes_ia)
                ]
            else:
                etapes = _etapes_ia

            # Description de base
            description_parts = [f"Plat à base de {proteine or 'ingrédients variés'}."]
            if jules_adaptation:
                description_parts.append(f"Version Jules : {jules_adaptation}")
            description = " ".join(description_parts)

            logger.info(
                f"Données IA directes pour '{nom}': "
                f"{len(ingredients)} ingrédients, {len(etapes)} étapes"
            )

        robot_context = ""
        if robot:
            robot_label = robot.replace("_", " ").title()
            robot_context = f"\nCette recette est préparée avec un {robot_label}. Adapte les étapes pour utiliser ce robot (temps, modes, réglages spécifiques)."

        # Appel IA secondaire uniquement si on n'a pas déjà les données du prompt
        if not _has_good_data:
            try:
                client = obtenir_client_ia()
                if client:
                    prompt_details = f"""Génère les détails complets pour la recette : "{nom}".
Contexte : famille de 2 adultes + 1 bébé de 19 mois.
Protéine principale : {proteine or "non spécifiée"}.{robot_context}

Réponds UNIQUEMENT en JSON valide :
{{
  "description": "Description appétissante de la recette en 1-2 phrases (PAS 'Recette générée par IA')",
  "temps_preparation": <temps de préparation en minutes (entier)>,
  "temps_cuisson": <temps de cuisson en minutes (entier)>,
  "portions": <nombre de portions (entier, typiquement 4)>,
  "ingredients": [
    {{"nom": "nom ingrédient", "quantite": 200, "unite": "g"}},
    {{"nom": "autre ingrédient", "quantite": 1, "unite": "pièce"}}
  ],
  "etapes": [
    "Description détaillée de l'étape 1...",
    "Description détaillée de l'étape 2...",
    "Description détaillée de l'étape 3..."
  ]
}}
IMPORTANT:
- La description doit être appétissante et décrire le plat (goût, texture, accompagnement), PAS mentionner l'IA.
- Liste TOUS les ingrédients nécessaires (minimum 4-5), avec des quantités réalistes.
- Détaille TOUTES les étapes de préparation (minimum 3-4 étapes), claires et précises.
- Les temps doivent être réalistes pour cette recette.
- Les quantités en grammes, cl, pièces, cuillères à soupe, etc."""
                    details = client.generer_json(
                        prompt_details,
                        system_prompt="Tu es un chef cuisinier expert en cuisine familiale. Tu donnes des recettes détaillées et précises.",
                        max_tokens=2000,
                    )
                    if details and isinstance(details, dict):
                        # Extraire description IA
                        desc_ia = details.get("description", "")
                        if desc_ia and not any(
                            x in desc_ia.lower() for x in ("généré", "ia", "planificateur")
                        ):
                            description = desc_ia
                            if jules_adaptation:
                                description += f" Version Jules : {jules_adaptation}"

                        # Extraire temps de cuisson et portions
                        temps_cuisson_ia = details.get("temps_cuisson")
                        if (
                            temps_cuisson_ia
                            and isinstance(temps_cuisson_ia, int | float)
                            and temps_cuisson_ia > 0
                        ):
                            temps_cuisson = int(temps_cuisson_ia)

                        temps_prep_ia = details.get("temps_preparation")
                        if (
                            temps_prep_ia
                            and isinstance(temps_prep_ia, int | float)
                            and temps_prep_ia > 0
                        ):
                            temps = int(temps_prep_ia)

                        portions_detail = details.get("portions")
                        if (
                            portions_detail
                            and isinstance(portions_detail, int | float)
                            and portions_detail > 0
                        ):
                            portions_ia = int(min(portions_detail, 20))

                        ingredients_raw = details.get("ingredients", [])
                        ingredients = []
                        import re

                        for ing in ingredients_raw:
                            q = ing.get("quantite", 0)
                            unite = ing.get("unite", "")
                            try:
                                if isinstance(q, str):
                                    match = re.search(r"(\d+([.,]\d+)?)", q.replace(",", "."))
                                    if match:
                                        q = float(match.group(1))
                                    else:
                                        if not unite:
                                            unite = str(q)
                                        q = 0.01
                                else:
                                    q = float(q)
                            except (ValueError, TypeError):
                                q = 0.01

                            if q <= 0:
                                q = 0.01

                            ing["quantite"] = q
                            ing["unite"] = unite
                            ingredients.append(ing)

                        etapes_raw = details.get("etapes", [])
                        if etapes_raw and isinstance(etapes_raw[0], str):
                            etapes = [
                                {"description": e, "ordre": i + 1} for i, e in enumerate(etapes_raw)
                            ]
                        else:
                            etapes = etapes_raw
            except Exception as e:
                logger.warning(f"Impossible de générer les détails pour {nom}: {e}")

        # Fallback description si l'IA n'a pas pu en générer
        if not description:
            description_parts = [f"Plat à base de {proteine or 'ingrédients variés'}."]
            if jules_adaptation:
                description_parts.append(f"Version Jules : {jules_adaptation}")
            description = " ".join(description_parts)

        # Fallback: si aucun ingrédient/étape n'a été généré, en créer des minimaux
        if not ingredients:
            # Utiliser la protéine comme ingrédient principal plutôt que le nom de recette
            fallback_nom = type_proteines if type_proteines else "ingrédients divers"
            ingredients = [{"nom": fallback_nom, "quantite": 1.0, "unite": "portion"}]
            logger.warning(f"Fallback ingrédients pour '{nom}': [{fallback_nom}]")
        if not etapes:
            etapes = [{"description": f"Préparer {nom} selon la recette.", "ordre": 1}]

        data = {
            "nom": nom,
            "description": description,
            "temps_preparation": temps,
            "temps_cuisson": temps_cuisson,
            "portions": portions_ia,
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

        # Deduplication: vérifier si une recette avec ce nom existe déjà
        existing = service.find_existing_recette(nom)
        if existing:
            logger.info(f"Recette existante réutilisée : '{nom}' (ID: {existing.id})")
            return existing.id

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
