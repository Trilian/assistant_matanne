"""Régressions Telegram — analyse photo multi-usage."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_traitement_photo_telegram_utilise_analyse_multi_usage():
    from src.api.routes.telegram._outils import _traiter_photo_frigo_telegram

    photos = [{"file_id": "file_large", "file_size": 9999, "width": 1280, "height": 720}]
    analyse = {
        "contexte_detecte": "plante",
        "resume": "La plante semble stressée et manque un peu d'eau.",
        "details": {
            "nom_plante": "Monstera",
            "problemes_detectes": ["feuilles sèches"],
        },
        "actions_suggerees": ["Arroser légèrement", "Éviter le soleil direct"],
        "confiance": 0.91,
    }

    with patch(
        "src.services.integrations.telegram.telecharger_fichier_telegram",
        new_callable=AsyncMock,
    ) as mock_download, patch(
        "src.services.integrations.telegram.envoyer_message_telegram",
        new_callable=AsyncMock,
    ) as mock_message, patch(
        "src.services.integrations.telegram.envoyer_message_interactif",
        new_callable=AsyncMock,
    ) as mock_interactif, patch(
        "src.services.ia_avancee.get_ia_avancee_service"
    ) as mock_ia:
        mock_download.return_value = b"fake-image"
        mock_ia.return_value.analyser_photo_multi_usage.return_value = analyse

        await _traiter_photo_frigo_telegram("123456", photos)

    mock_message.assert_any_await("123456", "📸 Photo reçue, j'analyse le contexte…")
    mock_ia.return_value.analyser_photo_multi_usage.assert_called_once_with(b"fake-image")

    corps = mock_interactif.await_args.kwargs["corps"]
    boutons = mock_interactif.await_args.kwargs["boutons"]

    assert "Monstera" in corps
    assert "Arroser légèrement" in corps
    assert any("/maison/jardin" in str(bouton.get("url", "")) for bouton in boutons)
