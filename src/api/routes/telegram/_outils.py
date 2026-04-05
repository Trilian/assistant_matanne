"""Commandes Telegram liées aux outils (timer, note, photo)."""

from __future__ import annotations

import asyncio
import html
import logging
import re

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
            "Envoie directement une photo du <b>frigo</b>, d'une <b>plante</b> ou d'une <b>pièce de la maison</b> "
            "et je te répondrai avec une analyse rapide."
        ),
        boutons=[
            {"url": _obtenir_url_app("/cuisine/inventaire"), "title": "🥫 Ouvrir l'inventaire"},
            {"url": _obtenir_url_app("/maison/jardin"), "title": "🌿 Ouvrir le jardin"},
            {"id": "menu_principal", "title": "🏠 Menu principal"},
        ],
    )


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

    await envoyer_message_telegram(chat_id, "📸 Photo du frigo reçue, j'analyse les ingrédients…")
    image_bytes = await telecharger_fichier_telegram(file_id)
    if not image_bytes:
        await envoyer_message_telegram(chat_id, "📸 Analyse indisponible : téléchargement Telegram impossible.")
        return

    resultat = await obtenir_photo_frigo_service().analyser_photo_frigo(image_bytes)
    if not resultat.ingredients_detectes and not resultat.recettes_db and not resultat.recettes_suggerees:
        await envoyer_message_telegram(chat_id, "📸 Je n'ai pas détecté assez d'ingrédients exploitables sur cette photo.")
        return

    ingredients = ", ".join(ingredient.nom for ingredient in resultat.ingredients_detectes[:6]) or "aucun"
    recettes = [recette.nom for recette in resultat.recettes_db[:3]] or [
        recette.nom for recette in resultat.recettes_suggerees[:3]
    ]
    lignes = [
        "📸 <b>Analyse photo frigo</b>",
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
