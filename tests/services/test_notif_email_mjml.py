"""Tests ciblés D9 pour ServiceEmail (render MJML avec fallback HTML)."""

from __future__ import annotations

from unittest.mock import patch


def _service_email():
    from src.services.core.notifications.notif_email import ServiceEmail

    return ServiceEmail()


def test_render_mjml_fallback_html_si_compilateur_indisponible():
    service = _service_email()

    with patch("src.services.core.notifications.notif_email.logger.warning"):
        html = service._render_mjml(
            "rapport_mensuel.mjml",
            fallback_html_template="rapport_mensuel.html",
            sujet="Test",
            mois="2026-04",
            total_depenses=100,
            budget_prevu=200,
            ecart=-100,
            categories=[],
        )

    assert isinstance(html, str)
    assert "<html" in html.lower() or "<body" in html.lower()


def test_envoyer_rapport_mensuel_utilise_render_mjml():
    service = _service_email()

    with (
        patch.object(service, "_render_mjml", return_value="<html>ok</html>") as mock_render,
        patch.object(service, "_envoyer", return_value=True) as mock_send,
    ):
        ok = service.envoyer_rapport_mensuel(
            "test@example.com",
            {
                "mois": "2026-04",
                "total_depenses": 1200,
                "budget_prevu": 1000,
                "categories": [{"nom": "courses", "montant": 400}],
            },
        )

    assert ok is True
    mock_render.assert_called_once()
    mock_send.assert_called_once()


def test_envoyer_rapport_famille_mensuel_complet_joint_un_pdf():
    service = _service_email()

    with patch.object(service, "_envoyer", return_value=True) as mock_send:
        ok = service.envoyer_rapport_famille_mensuel_complet(
            "test@example.com",
            {
                "mois": "04/2026",
                "budget": "1200 EUR",
                "nutrition": "60 repas",
                "maison": "3 projets",
                "jardin": "2 actions",
                "jules": "RAS",
            },
        )

    assert ok is True
    kwargs = mock_send.call_args.kwargs
    assert kwargs.get("attachments")
    assert kwargs["attachments"][0]["filename"].endswith(".pdf")


def test_envoyer_rapport_maison_trimestriel_joint_un_pdf():
    service = _service_email()

    with patch.object(service, "_envoyer", return_value=True) as mock_send:
        ok = service.envoyer_rapport_maison_trimestriel(
            "test@example.com",
            {
                "trimestre": "T2 2026",
                "projets": "4 projets",
                "energie": "430 kWh",
                "jardin": "8 tâches",
                "entretien": "5 rappels",
            },
        )

    assert ok is True
    kwargs = mock_send.call_args.kwargs
    assert kwargs.get("attachments")
    assert kwargs["attachments"][0]["filename"].endswith(".pdf")
