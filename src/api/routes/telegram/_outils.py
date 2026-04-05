"""Commandes Telegram liées aux outils (timer, note, photo)."""

from __future__ import annotations

import asyncio
import html
import logging
import re
from typing import Any

from ._helpers import _obtenir_url_app

logger = logging.getLogger(__name__)


async def _notifier_fin_minuteur(chat_id: str, minutes: int) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    await asyncio.sleep(minutes * 60)
    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=f"⏰ <b>Minuteur terminé</b> — {minutes} min écoulées.",
        boutons=[
            {"id": "action_repas_soir", "title": "🍽️ Voir le repas"},
            {"id": "menu_retour", "title": "🏠 Menu principal"},
        ],
    )


async def _lancer_minuteur_telegram(chat_id: str, argument: str) -> None:
    from src.services.integrations.telegram import envoyer_message_telegram

    match = re.search(r"(\d{1,3})", argument or "")
    if not match:
        await envoyer_message_telegram(chat_id, "⏱️ Utilise par exemple <code>/timer 15</code>.")
        return

    minutes = max(1, min(int(match.group(1)), 180))
    asyncio.create_task(_notifier_fin_minuteur(chat_id, minutes))
    await envoyer_message_telegram(chat_id, f"⏱️ Minuteur lancé pour <b>{minutes} min</b>.")


async def _creer_note_rapide_telegram(chat_id: str, texte_note: str) -> None:
    from src.services.integrations.telegram import envoyer_message_telegram
    from src.services.utilitaires import obtenir_notes_service

    contenu = (texte_note or "").strip()
    if not contenu:
        await envoyer_message_telegram(chat_id, "📝 Utilise <code>/note ton texte</code> pour créer un pense-bête.")
        return

    note = obtenir_notes_service().creer(
        titre=(contenu[:57] + "...") if len(contenu) > 60 else contenu,
        contenu=contenu,
        categorie="telegram",
        couleur="#FFF7CC",
        epingle=False,
        est_checklist=False,
    )
    await envoyer_message_telegram(chat_id, f"📝 Note créée avec succès (#{note.id}).")


async def _envoyer_aide_photo_telegram(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=(
            "📸 <b>Aide photo</b>\n\n"
            "Envoie directement une photo du <b>frigo</b>, d'une <b>plante</b>, d'une <b>pièce</b> ou d'un <b>document</b> "
            "et je te répondrai avec une analyse adaptée."
        ),
        boutons=[
            {"url": _obtenir_url_app("/cuisine/inventaire"), "title": "🥫 Ouvrir l'inventaire"},
            {"url": _obtenir_url_app("/maison/jardin"), "title": "🌿 Ouvrir le jardin"},
            {"id": "menu_principal", "title": "🏠 Menu principal"},
        ],
    )


def _normaliser_contexte_photo(contexte: str) -> str:
    """Ramène les contextes IA vers un petit ensemble exploitable côté Telegram."""

    contexte_norm = (contexte or "").strip().lower()
    if any(mot in contexte_norm for mot in ("recette", "plat", "frigo", "cuisine")):
        return "cuisine"
    if any(mot in contexte_norm for mot in ("plante", "jardin", "fleur")):
        return "plante"
    if any(mot in contexte_norm for mot in ("maison", "travaux", "piece", "pièce", "mur", "toit")):
        return "maison"
    if any(mot in contexte_norm for mot in ("document", "facture", "contrat", "papier")):
        return "document"
    return "autre"


def _extraire_points_photo(details: dict[str, Any]) -> list[str]:
    """Construit quelques points lisibles à partir des détails IA."""

    points: list[str] = []
    cles_prioritaires = [
        "nom_plante",
        "piece",
        "type_document",
        "ingredients",
        "problemes_detectes",
        "causes_probables",
        "informations_cles",
        "travaux_detectes",
    ]

    for cle in cles_prioritaires:
        valeur = details.get(cle)
        if valeur in (None, "", [], {}):
            continue
        libelle = cle.replace("_", " ")
        if isinstance(valeur, list):
            texte = ", ".join(str(item) for item in valeur[:3])
        elif isinstance(valeur, dict):
            texte = ", ".join(f"{k}: {v}" for k, v in list(valeur.items())[:3])
        else:
            texte = str(valeur)
        points.append(f"{libelle.capitalize()} : {texte}")
        if len(points) >= 3:
            break

    return points


def _construire_reponse_photo_multi_usage(analyse: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    """Formate la réponse Telegram en fonction du contexte détecté."""

    contexte = _normaliser_contexte_photo(str(analyse.get("contexte_detecte") or ""))
    resume = str(analyse.get("resume") or "Analyse terminée.").strip()
    confiance = float(analyse.get("confiance") or 0)
    details = analyse.get("details") if isinstance(analyse.get("details"), dict) else {}
    actions = [str(item) for item in (analyse.get("actions_suggerees") or [])[:3]]

    configuration = {
        "cuisine": {
            "titre": "📸 <b>Analyse photo cuisine</b>",
            "label": "Cuisine / repas",
            "boutons": [
                {"url": _obtenir_url_app("/cuisine/inventaire"), "title": "🥫 Inventaire"},
                {"url": _obtenir_url_app("/cuisine/recettes"), "title": "📖 Recettes"},
                {"id": "action_planning", "title": "🍽️ Planning"},
            ],
        },
        "plante": {
            "titre": "🌿 <b>Diagnostic plante</b>",
            "label": "Plante / jardin",
            "boutons": [
                {"url": _obtenir_url_app("/maison/jardin"), "title": "🌱 Ouvrir le jardin"},
                {"url": _obtenir_url_app("/ia-avancee/diagnostic-plante"), "title": "🔎 Diagnostic détaillé"},
                {"id": "menu_principal", "title": "🏠 Menu principal"},
            ],
        },
        "maison": {
            "titre": "🏡 <b>Analyse photo maison</b>",
            "label": "Maison / travaux",
            "boutons": [
                {"url": _obtenir_url_app("/maison/visualisation"), "title": "🧭 Vue maison"},
                {"url": _obtenir_url_app("/maison"), "title": "🛠️ Module maison"},
                {"id": "menu_principal", "title": "🏠 Menu principal"},
            ],
        },
        "document": {
            "titre": "📄 <b>Analyse document</b>",
            "label": "Document",
            "boutons": [
                {"url": _obtenir_url_app("/famille/documents"), "title": "📂 Documents"},
                {"url": _obtenir_url_app("/outils"), "title": "🧰 Outils"},
                {"id": "menu_principal", "title": "🏠 Menu principal"},
            ],
        },
        "autre": {
            "titre": "📸 <b>Analyse photo</b>",
            "label": "Contexte varié",
            "boutons": [
                {"url": _obtenir_url_app("/ia-avancee/analyse-photo"), "title": "🤖 Analyse avancée"},
                {"id": "menu_principal", "title": "🏠 Menu principal"},
            ],
        },
    }[contexte]

    lignes = [
        configuration["titre"],
        f"Contexte détecté : {html.escape(str(configuration['label']))}",
        f"Confiance IA : {int(confiance * 100)}%",
        "",
        html.escape(resume),
    ]

    for point in _extraire_points_photo(details):
        lignes.append(f"• {html.escape(point)}")

    if actions:
        lignes.append("")
        lignes.append("<b>Actions suggérées</b>")
        lignes.extend(f"• {html.escape(action)}" for action in actions)

    return "\n".join(lignes), list(configuration["boutons"])


async def _traiter_photo_frigo_telegram(chat_id: str, photos: list[dict[str, object]]) -> None:
    from src.services.cuisine.photo_frigo import obtenir_photo_frigo_service
    from src.services.integrations.telegram import (
        envoyer_message_interactif,
        envoyer_message_telegram,
        telecharger_fichier_telegram,
    )

    if not photos:
        await envoyer_message_telegram(chat_id, "📸 Photo reçue, mais le fichier est introuvable.")
        return

    photo = max(photos, key=lambda item: int(item.get("file_size") or 0))
    file_id = str(photo.get("file_id") or "")
    if not file_id:
        await envoyer_message_telegram(chat_id, "📸 Photo reçue, mais le fichier est incomplet.")
        return

    await envoyer_message_telegram(chat_id, "📸 Photo reçue, j'analyse le contexte…")
    image_bytes = await telecharger_fichier_telegram(file_id)
    if not image_bytes:
        await envoyer_message_telegram(chat_id, "📸 Analyse indisponible : téléchargement Telegram impossible.")
        return

    analyse_multi: dict[str, Any] | None = None
    try:
        from src.services.ia_avancee import get_ia_avancee_service

        resultat_multi = get_ia_avancee_service().analyser_photo_multi_usage(image_bytes)
        if hasattr(resultat_multi, "model_dump"):
            analyse_multi = resultat_multi.model_dump()
        elif isinstance(resultat_multi, dict):
            analyse_multi = resultat_multi
    except Exception as exc:  # noqa: BLE001
        logger.debug("Analyse photo multi-usage indisponible: %s", exc)

    contexte = _normaliser_contexte_photo(str((analyse_multi or {}).get("contexte_detecte") or ""))
    if contexte == "cuisine":
        resultat = await obtenir_photo_frigo_service().analyser_photo_frigo(image_bytes)
        if resultat.ingredients_detectes or resultat.recettes_db or resultat.recettes_suggerees:
            ingredients = ", ".join(ingredient.nom for ingredient in resultat.ingredients_detectes[:6]) or "aucun"
            recettes = [recette.nom for recette in resultat.recettes_db[:3]] or [
                recette.nom for recette in resultat.recettes_suggerees[:3]
            ]
            lignes = [
                "📸 <b>Analyse photo cuisine</b>",
                f"Ingrédients détectés : {html.escape(ingredients)}",
            ]
            if analyse_multi and analyse_multi.get("resume"):
                lignes.extend(["", html.escape(str(analyse_multi["resume"]))])
            if recettes:
                lignes.append("")
                lignes.append("<b>Idées de recettes</b>")
                lignes.extend(f"• {html.escape(str(nom))}" for nom in recettes[:3])

            await envoyer_message_interactif(
                destinataire=chat_id,
                corps="\n".join(lignes),
                boutons=[
                    {"id": "action_courses", "title": "🛒 Voir les courses"},
                    {"id": "action_planning", "title": "🍽️ Voir le planning"},
                    {"url": _obtenir_url_app("/cuisine/recettes"), "title": "📖 Ouvrir les recettes"},
                ],
            )
            return

    if analyse_multi:
        corps, boutons = _construire_reponse_photo_multi_usage(analyse_multi)
        await envoyer_message_interactif(destinataire=chat_id, corps=corps, boutons=boutons)
        return

    resultat = await obtenir_photo_frigo_service().analyser_photo_frigo(image_bytes)
    if not resultat.ingredients_detectes and not resultat.recettes_db and not resultat.recettes_suggerees:
        await envoyer_message_telegram(chat_id, "📸 Je n'ai pas détecté assez d'éléments exploitables sur cette photo.")
        return

    ingredients = ", ".join(ingredient.nom for ingredient in resultat.ingredients_detectes[:6]) or "aucun"
    recettes = [recette.nom for recette in resultat.recettes_db[:3]] or [
        recette.nom for recette in resultat.recettes_suggerees[:3]
    ]
    lignes = [
        "📸 <b>Analyse photo cuisine</b>",
        f"Ingrédients détectés : {html.escape(ingredients)}",
    ]
    if recettes:
        lignes.append("")
        lignes.append("<b>Idées de recettes</b>")
        lignes.extend(f"• {html.escape(str(nom))}" for nom in recettes[:3])

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "action_courses", "title": "🛒 Voir les courses"},
            {"id": "action_planning", "title": "🍽️ Voir le planning"},
            {"url": _obtenir_url_app("/cuisine/recettes"), "title": "📖 Ouvrir les recettes"},
        ],
    )
