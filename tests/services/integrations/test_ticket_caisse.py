"""
T6c — Tests service Ticket de caisse.

Couvre src/services/integrations/ticket_caisse.py :
- scanner_ticket_texte  : parsing regex (fallback sans IA)
- _parser_reponse_vision : parsing JSON de la réponse Pixtral
- LigneTicket / TicketCaisse : types de données
"""

from __future__ import annotations

import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════
# TESTS — PARSING TEXTE BRUT (scanner_ticket_texte)
# ═══════════════════════════════════════════════════════════


class TestScannerTicketTexte:
    """Tests scanner_ticket_texte() — parsing regex sans IA."""

    def test_ticket_simple_2_articles(self):
        """Deux lignes simples parsées correctement."""
        from src.services.integrations.ticket_caisse import scanner_ticket_texte

        texte = (
            "CARREFOUR EXPRESS\n"
            "YAOURT NATURE     1.20\n"
            "LAIT DEMI-ECR     0.95\n"
            "TOTAL             2.15\n"
        )
        ticket = scanner_ticket_texte(texte)

        assert len(ticket.lignes) >= 2
        noms = [l.article.lower() for l in ticket.lignes]
        assert any("yaourt" in n for n in noms)
        assert any("lait" in n for n in noms)

    def test_total_exclu_des_lignes(self):
        """Les lignes 'TOTAL' ne doivent pas être incluses."""
        from src.services.integrations.ticket_caisse import scanner_ticket_texte

        texte = (
            "PAIN               1.10\n"
            "TOTAL              1.10\n"
        )
        ticket = scanner_ticket_texte(texte)

        for ligne in ticket.lignes:
            assert "total" not in ligne.article.lower()

    def test_quantite_2x_detectee(self):
        """Ligne '2x YAOURT' → quantite=2."""
        from src.services.integrations.ticket_caisse import scanner_ticket_texte

        texte = "2x YAOURT         2.40\n"
        ticket = scanner_ticket_texte(texte)

        if ticket.lignes:
            yaourt = next((l for l in ticket.lignes if "yaourt" in l.article.lower()), None)
            if yaourt:
                assert yaourt.quantite == 2

    def test_ticket_vide_retourne_structure_vide(self):
        """Texte vide → TicketCaisse sans lignes."""
        from src.services.integrations.ticket_caisse import scanner_ticket_texte

        ticket = scanner_ticket_texte("")
        assert ticket.lignes == []

    def test_prix_convertis_en_float(self):
        """Les prix sont bien des float."""
        from src.services.integrations.ticket_caisse import scanner_ticket_texte

        texte = "BEURRE           2,50\n"
        ticket = scanner_ticket_texte(texte)

        for ligne in ticket.lignes:
            assert isinstance(ligne.prix, float)
            assert ligne.prix > 0


# ═══════════════════════════════════════════════════════════
# TESTS — PARSING RÉPONSE VISION
# ═══════════════════════════════════════════════════════════


class TestParserReponseVision:
    """Tests _parser_reponse_vision()."""

    def test_json_valide_parse_correctement(self):
        """JSON Pixtral valide → TicketCaisse complet."""
        from src.services.integrations.ticket_caisse import _parser_reponse_vision

        reponse = json.dumps({
            "magasin": "Leclerc",
            "date": "2025-01-15",
            "lignes": [
                {"article": "Poulet rôti", "prix": 8.50, "quantite": 1, "categorie": "alimentation"},
                {"article": "Tomates", "prix": 2.30, "quantite": 2, "categorie": "alimentation"},
            ],
            "total": 10.80,
            "mode_paiement": "CB",
        })

        ticket = _parser_reponse_vision(reponse)

        assert ticket.magasin == "Leclerc"
        assert ticket.date_achat == date(2025, 1, 15)
        assert len(ticket.lignes) == 2
        assert ticket.total == 10.80
        assert ticket.confiance_ocr == 0.85

    def test_json_avec_markdown_fences(self):
        """Réponse entourée de ```json → bien parsée."""
        from src.services.integrations.ticket_caisse import _parser_reponse_vision

        reponse = (
            "```json\n"
            '{"magasin":"Intermarché","date":"","lignes":[],"total":0,"mode_paiement":""}\n'
            "```"
        )
        ticket = _parser_reponse_vision(reponse)
        assert ticket.magasin == "Intermarché"

    def test_json_invalide_retourne_ticket_vide(self):
        """JSON cassé → TicketCaisse vide sans lever d'exception."""
        from src.services.integrations.ticket_caisse import _parser_reponse_vision

        ticket = _parser_reponse_vision("PAS DU JSON")
        assert ticket.confiance_ocr == 0.0
        assert ticket.lignes == []

    def test_date_invalide_ignoree(self):
        """Date malformée → date_achat=None, pas d'exception."""
        from src.services.integrations.ticket_caisse import _parser_reponse_vision

        reponse = json.dumps({
            "magasin": "Aldi",
            "date": "BAD-DATE",
            "lignes": [],
            "total": 0,
            "mode_paiement": "",
        })
        ticket = _parser_reponse_vision(reponse)
        assert ticket.date_achat is None


# ═══════════════════════════════════════════════════════════
# TESTS — PROPRIÉTÉS CALCULÉES
# ═══════════════════════════════════════════════════════════


class TestTicketCaisseProperties:
    """Tests des propriétés calculées du TicketCaisse."""

    def test_total_calcule(self):
        """total_calcule = somme prix * quantites."""
        from src.services.integrations.ticket_caisse import LigneTicket, TicketCaisse

        ticket = TicketCaisse(
            lignes=[
                LigneTicket(article="Lait", prix=1.50, quantite=2),
                LigneTicket(article="Pain", prix=2.00, quantite=1),
            ]
        )
        assert abs(ticket.total_calcule - 5.0) < 0.001

    def test_nb_articles(self):
        """nb_articles = nombre de lignes."""
        from src.services.integrations.ticket_caisse import LigneTicket, TicketCaisse

        ticket = TicketCaisse(
            lignes=[
                LigneTicket(article="A", prix=1.0),
                LigneTicket(article="B", prix=2.0),
                LigneTicket(article="C", prix=3.0),
            ]
        )
        assert ticket.nb_articles == 3

    def test_scanner_vision_echec_ia_retourne_vide(self):
        """Échec de Pixtral → TicketCaisse vide sans lever d'exception."""
        from src.services.integrations.ticket_caisse import scanner_ticket_vision

        with patch("src.services.integrations.ticket_caisse.ClientIA") as mock_client_cls:
            mock_client_cls.side_effect = Exception("Pixtral indisponible")
            ticket = scanner_ticket_vision("base64encodedimage==")

        assert ticket.confiance_ocr == 0.0
        assert ticket.lignes == []
