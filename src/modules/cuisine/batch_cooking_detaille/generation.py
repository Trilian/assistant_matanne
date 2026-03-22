"""Génération IA pour le module Batch Cooking Détaillé."""

import json
import logging
import math

import streamlit as st

from src.core.ai import obtenir_client_ia
from src.modules.cuisine.batch_cooking_temps import ROBOTS_INFO

logger = logging.getLogger(__name__)

# Nombre max de recettes par appel IA avant découpage automatique
_MAX_RECETTES_PAR_APPEL = 4
_MAX_TOKENS = 16000


def _compter_recettes(planning_data: dict) -> int:
    """Compte le nombre de recettes non-réchauffées dans le planning."""
    count = 0
    for _jour, repas in planning_data.items():
        for type_repas in ("midi", "soir"):
            r = repas.get(type_repas, {})
            if r and isinstance(r, dict) and not r.get("est_rechauffe"):
                count += 1
    return count


def _construire_prompt(
    planning_data: dict, type_session: str, avec_jules: bool, robots_section: str
) -> str:
    """Construit le prompt IA pour la génération batch cooking."""
    jules_txt = (
        "Avec Jules (19 mois) - prévoir des tâches simples et sécurisées pour lui"
        if avec_jules
        else "Session solo"
    )

    prompt = f"""Expert batch cooking familial. Génère des instructions détaillées et concrètes.

SESSION: {type_session.upper()}
{jules_txt}

ÉQUIPEMENT:
{robots_section}

RECETTES À PRÉPARER:
"""

    for jour, repas in planning_data.items():
        for type_repas in ("midi", "soir"):
            r = repas.get(type_repas, {})
            if r and isinstance(r, dict) and not r.get("est_rechauffe"):
                prompt += f"\n- {jour} {type_repas}: {r.get('nom', 'Recette')}"

    prompt += """

RÉPONDS EN JSON VALIDE avec cette structure:
{"session": {"duree_estimee_minutes": 120, "conseils_organisation": ["..."]},
 "recettes": [{"nom": "...", "pour_jours": ["Lundi midi"], "portions": 4,
   "ingredients": [{"nom": "carottes", "quantite": "500g", "decoupe": "rondelles 5mm", "tache_jules": "Laver"}],
   "etapes_batch": [{"titre": "Découper carottes en rondelles 5mm", "duree_minutes": 10, "robot": null, "temperature": null, "est_passif": false, "detail": "Économe, rondelles régulières 5mm", "jules_participation": false, "tache_jules": null}],
   "instructions_finition": ["Réchauffer 3min micro-ondes"],
   "stockage": "Boîte hermétique frigo", "duree_conservation_jours": 3}],
 "moments_jules": [{"temps": "0-15min", "tache": "Laver légumes"}],
 "timeline": [{"debut_min": 0, "fin_min": 15, "tache": "Découpe légumes", "robot": null}]}

RÈGLES:
1. Étapes CONCRÈTES: découpe exacte, grammes, °C, durée. Jamais "les légumes" → nommer chaque légume avec quantité
2. Robot utilisé: programme exact, température, vitesse, durée
3. PARALLÉLISER: pendant qu'un robot tourne (est_passif=true), travailler sur une autre recette. La timeline montre les opérations simultanées
4. Quantités en grammes/ml (sauf pièces: oeufs, oignons). Finition = réchauffage/assaisonnement jour J"""

    if avec_jules:
        prompt += "\n5. Jules 19 mois: UNIQUEMENT laver, mélanger dans un bol, verser (PAS de couteau, PAS de chaleur)"

    prompt += "\n\nRéponds UNIQUEMENT en JSON valide, sans commentaire ni markdown."

    return prompt


def _valider_et_reparer_reponse(response: dict | str | None) -> dict | None:
    """Valide et répare la réponse IA. Retourne un dict valide ou None."""

    if response and isinstance(response, dict):
        logger.info(
            f"Réponse IA dict reçue: {len(str(response))} chars, "
            f"clés={list(response.keys())}, "
            f"nb_recettes={len(response.get('recettes', []))}"
        )
        # Valider la structure minimale
        if "recettes" not in response or not isinstance(response.get("recettes"), list):
            logger.warning(f"Réponse IA sans 'recettes' valide. Clés: {list(response.keys())}")
            # Tenter de récupérer si la structure est imbriquée
            if "session" in response and isinstance(response["session"], dict):
                inner = response["session"]
                if isinstance(inner.get("recettes"), list):
                    response["recettes"] = inner["recettes"]
                    return response
            return None
        return response

    # Fallback: si generer_json a retourné une string brute, tenter le parsing
    if response and isinstance(response, str):
        logger.warning(
            f"generer_json batch a retourné une string ({len(response)} chars), "
            f"début: {response[:300]}..."
        )
        try:
            from src.core.ai.parser import AnalyseurIA

            json_str = AnalyseurIA._extraire_objet_json(response)
            json_str = AnalyseurIA._reparer_intelligemment(json_str)
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                logger.info(f"Parse manuelle réussie: clés={list(parsed.keys())}")
                return parsed
        except Exception as e:
            logger.warning(f"Parse manuelle échouée: {e}")

    if response:
        logger.warning(f"Réponse IA invalide (type={type(response).__name__}): {str(response)[:500]}")
    else:
        logger.warning("Réponse IA vide (None)")

    return None


def _appel_ia_batch(
    prompt: str, max_tokens: int = _MAX_TOKENS
) -> dict | None:
    """Effectue l'appel IA et retourne un dict validé ou None."""
    client = obtenir_client_ia()
    if not client:
        return None

    logger.info(f"Appel IA batch cooking: prompt={len(prompt)} chars, max_tokens={max_tokens}")

    response = client.generer_json(
        prompt=prompt,
        system_prompt="Tu es un chef expérimenté spécialiste du batch cooking familial. Réponds UNIQUEMENT en JSON valide. Sois très détaillé et concret sur les découpes, poids, températures et temps.",
        max_tokens=max_tokens,
    )

    return _valider_et_reparer_reponse(response)


def _decouper_planning(planning_data: dict) -> list[dict]:
    """Découpe le planning en sous-plannings de max _MAX_RECETTES_PAR_APPEL recettes."""
    items: list[tuple[str, str, dict]] = []
    for jour, repas in planning_data.items():
        for type_repas in ("midi", "soir"):
            r = repas.get(type_repas, {})
            if r and isinstance(r, dict) and not r.get("est_rechauffe"):
                items.append((jour, type_repas, r))

    taille_chunk = max(2, math.ceil(len(items) / 2))
    chunks: list[dict] = []
    for i in range(0, len(items), taille_chunk):
        sub: dict = {}
        for jour, type_repas, r in items[i : i + taille_chunk]:
            sub.setdefault(jour, {})[type_repas] = r
        chunks.append(sub)
    return chunks


def _fusionner_resultats(resultats: list[dict]) -> dict:
    """Fusionne plusieurs résultats IA en un seul."""
    if len(resultats) == 1:
        return resultats[0]

    merged: dict = {
        "session": {
            "duree_estimee_minutes": 0,
            "conseils_organisation": [],
        },
        "recettes": [],
        "moments_jules": [],
        "timeline": [],
    }

    offset_min = 0
    for r in resultats:
        session = r.get("session", {})
        duree = session.get("duree_estimee_minutes", 0)
        merged["session"]["duree_estimee_minutes"] += duree
        merged["session"]["conseils_organisation"].extend(
            session.get("conseils_organisation", [])
        )
        merged["recettes"].extend(r.get("recettes", []))
        merged["moments_jules"].extend(r.get("moments_jules", []))

        # Décaler la timeline du chunk pour la mettre à la suite
        for entry in r.get("timeline", []):
            shifted = {**entry}
            shifted["debut_min"] = entry.get("debut_min", 0) + offset_min
            shifted["fin_min"] = entry.get("fin_min", 0) + offset_min
            merged["timeline"].append(shifted)

        offset_min += duree

    return merged


def generer_batch_ia(
    planning_data: dict, type_session: str, avec_jules: bool, robots_user: list[str] | None = None
) -> dict:
    """Génère les instructions de batch cooking avec l'IA.

    Stratégie:
    1. Appel unique si ≤ _MAX_RECETTES_PAR_APPEL recettes
    2. Si échec, retry avec max_tokens augmenté
    3. Si toujours en échec, découpage en sous-groupes + fusion
    """
    # Robots disponibles
    if not robots_user:
        robots_user = ["four", "plaques"]
    robots_txt = []
    for r in robots_user:
        info = ROBOTS_INFO.get(r, {})
        parallel = "peut fonctionner en parallèle" if info.get("peut_parallele") else "UNE tâche à la fois"
        robots_txt.append(f"  - {info.get('nom', r)} ({parallel})")
    robots_section = "\n".join(robots_txt)

    nb_recettes = _compter_recettes(planning_data)
    logger.info(f"Batch cooking: {nb_recettes} recettes, session={type_session}, jules={avec_jules}")

    try:
        prompt = _construire_prompt(planning_data, type_session, avec_jules, robots_section)

        # Tentative 1: appel unique
        result = _appel_ia_batch(prompt, max_tokens=_MAX_TOKENS)
        if result:
            return result

        # Tentative 2: retry avec plus de tokens
        logger.warning("Tentative 1 échouée, retry avec max_tokens augmenté")
        result = _appel_ia_batch(prompt, max_tokens=_MAX_TOKENS + 8000)
        if result:
            return result

        # Tentative 3: découpage en sous-groupes (si plus de 2 recettes)
        if nb_recettes > 2:
            logger.warning(
                f"Tentative 2 échouée, découpage en sous-groupes ({nb_recettes} recettes)"
            )
            chunks = _decouper_planning(planning_data)
            resultats: list[dict] = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Génération chunk {i + 1}/{len(chunks)}: {_compter_recettes(chunk)} recettes")
                chunk_prompt = _construire_prompt(chunk, type_session, avec_jules, robots_section)
                chunk_result = _appel_ia_batch(chunk_prompt)
                if chunk_result:
                    resultats.append(chunk_result)
                else:
                    logger.error(f"Chunk {i + 1} échoué")
                    st.error(
                        f"❌ L'IA n'a pas pu traiter le groupe {i + 1}. "
                        "Réduis le nombre de recettes et réessaie."
                    )
                    return {}

            merged = _fusionner_resultats(resultats)
            logger.info(
                f"Fusion réussie: {len(merged.get('recettes', []))} recettes, "
                f"durée={merged.get('session', {}).get('duree_estimee_minutes')}min"
            )
            return merged

        st.error(
            f"❌ L'IA n'a pas pu générer les instructions pour {nb_recettes} recette(s). "
            "Vérifie ta connexion et réessaie."
        )

    except Exception as e:
        logger.error(f"Erreur génération batch IA: {e}", exc_info=True)
        st.error(f"❌ Erreur IA: {str(e)}")

    return {}
