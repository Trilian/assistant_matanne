"""Commandes Telegram liées aux menus et à l'aide."""

from __future__ import annotations

from ._helpers import _construire_message_aide


async def _envoyer_aide_telegram(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=_construire_message_aide(),
        boutons=[
            {"id": "menu_principal", "title": "🏠 Menu principal"},
            {"id": "action_planning", "title": "🍽️ Planning"},
            {"id": "action_courses", "title": "🛒 Courses"},
        ],
    )


async def _envoyer_menu_principal(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=(
            "📲 <b>Menu principal MaTanne</b>\n\n"
            "Choisissez un module pour ouvrir les actions rapides Telegram."
        ),
        boutons=[
            {"id": "menu_cuisine", "title": "🍽️ Cuisine"},
            {"id": "menu_famille", "title": "👶 Famille"},
            {"id": "menu_maison", "title": "🏠 Maison"},
            {"id": "menu_outils", "title": "🧰 Outils"},
            {"id": "menu_aide", "title": "❓ Aide"},
        ],
    )


async def _envoyer_menu_module(chat_id: str, module_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    configuration = {
        "cuisine": {
            "titre": "🍽️ <b>Cuisine</b>",
            "boutons": [
                {"id": "action_planning", "title": "📅 Planning semaine"},
                {"id": "action_courses", "title": "🛒 Liste de courses"},
                {"id": "action_inventaire", "title": "🥫 Inventaire"},
                {"id": "action_batch", "title": "🍱 Batch cooking"},
                {"id": "action_repas_midi", "title": "☀️ Repas midi"},
                {"id": "action_repas_soir", "title": "🌙 Repas ce soir"},
            ],
        },
        "famille": {
            "titre": "👶 <b>Famille</b>",
            "boutons": [
                {"id": "action_jules", "title": "👶 Résumé Jules"},
                {"id": "action_budget", "title": "💰 Budget"},
                {"id": "action_meteo", "title": "🌦️ Météo & activités"},
            ],
        },
        "maison": {
            "titre": "🏠 <b>Maison</b>",
            "boutons": [
                {"id": "action_maison", "title": "🧹 Tâches du jour"},
                {"id": "action_jardin", "title": "🌿 Jardin"},
                {"id": "action_energie", "title": "⚡ Énergie"},
                {"id": "action_rappels", "title": "⏰ Rappels"},
                {"id": "action_budget", "title": "💰 Budget maison/famille"},
            ],
        },
        "outils": {
            "titre": "🧰 <b>Outils</b>",
            "boutons": [
                {"id": "action_meteo", "title": "🌦️ Météo"},
                {"id": "action_timer_10", "title": "⏱️ Timer 10 min"},
                {"id": "action_note_modele", "title": "📝 Note rapide"},
                {"id": "menu_aide", "title": "❓ Aide"},
            ],
        },
    }

    module = configuration.get(module_id)
    if not module:
        await _envoyer_menu_principal(chat_id)
        return

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=f"{module['titre']}\n\nActions rapides disponibles:",
        boutons=[*module["boutons"], {"id": "menu_retour", "title": "🏠 Menu principal"}],
    )
