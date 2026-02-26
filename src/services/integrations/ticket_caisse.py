"""
Service de scan de tickets de caisse — OCR via Pixtral.

Utilise Pixtral (Mistral Vision) pour extraire les articles et prix
d'une photo de ticket de caisse, avec fallback regex.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import date

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class LigneTicket:
    """Ligne extraite d'un ticket de caisse."""

    article: str
    prix: float
    quantite: int = 1
    categorie: str = ""
    rayon: str = ""


@dataclass
class TicketCaisse:
    """Ticket de caisse complet parsé."""

    magasin: str = ""
    date_achat: date | None = None
    lignes: list[LigneTicket] = field(default_factory=list)
    total: float = 0.0
    mode_paiement: str = ""
    confiance_ocr: float = 0.0  # 0-1

    @property
    def total_calcule(self) -> float:
        return sum(l.prix * l.quantite for l in self.lignes)

    @property
    def nb_articles(self) -> int:
        return len(self.lignes)


# ═══════════════════════════════════════════════════════════
# PROMPTS IA (Pixtral Vision)
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT_TICKET = """Tu es un expert en extraction de données de tickets de caisse.

À partir de l'image d'un ticket de caisse, extrais TOUTES les informations structurées.

RÉPONDS UNIQUEMENT en JSON valide avec cette structure:
{
  "magasin": "nom du magasin",
  "date": "YYYY-MM-DD",
  "lignes": [
    {"article": "nom article", "prix": 2.50, "quantite": 1, "categorie": "alimentation"}
  ],
  "total": 45.30,
  "mode_paiement": "CB"
}

RÈGLES:
- Extrais CHAQUE ligne du ticket, même les remises
- Les prix sont en euros
- Si la quantité n'est pas visible, mets 1
- Catégorise: alimentation, hygiène, entretien, bébé, autre
- Si une info n'est pas lisible, utilise "" ou 0
- N'invente RIEN — n'inclus que ce qui est sur le ticket"""


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def scanner_ticket_vision(image_base64: str) -> TicketCaisse:
    """
    Extrait les données d'un ticket de caisse via Pixtral (Mistral Vision).

    Args:
        image_base64: Image encodée en base64

    Returns:
        TicketCaisse parsé
    """
    try:
        from src.core.ai.client import ClientIA

        client = ClientIA()

        # Appel vision Pixtral
        reponse = client.generer_texte(
            prompt="Extrais toutes les informations de ce ticket de caisse.",
            system_prompt=SYSTEM_PROMPT_TICKET,
            images=[image_base64],
            modele="pixtral-12b-2409",
            temperature=0.1,  # Précision max
        )

        return _parser_reponse_vision(reponse)

    except Exception:
        logger.exception("Erreur OCR vision Pixtral")
        return TicketCaisse(confiance_ocr=0.0)


def _parser_reponse_vision(reponse: str) -> TicketCaisse:
    """Parse la réponse JSON de Pixtral."""
    try:
        # Nettoyer markdown code blocks
        texte = reponse.strip()
        if texte.startswith("```"):
            texte = texte.split("\n", 1)[1] if "\n" in texte else texte[3:]
        if texte.endswith("```"):
            texte = texte[:-3]
        texte = texte.strip()

        data = json.loads(texte)

        lignes = []
        for l in data.get("lignes", []):
            lignes.append(
                LigneTicket(
                    article=l.get("article", ""),
                    prix=float(l.get("prix", 0)),
                    quantite=int(l.get("quantite", 1)),
                    categorie=l.get("categorie", "alimentation"),
                )
            )

        date_achat = None
        if date_str := data.get("date"):
            try:
                date_achat = date.fromisoformat(date_str)
            except ValueError:
                pass

        return TicketCaisse(
            magasin=data.get("magasin", ""),
            date_achat=date_achat,
            lignes=lignes,
            total=float(data.get("total", 0)),
            mode_paiement=data.get("mode_paiement", ""),
            confiance_ocr=0.85,  # Vision OCR fiable
        )

    except (json.JSONDecodeError, KeyError):
        logger.warning("Impossible de parser la réponse Vision pour le ticket")
        return TicketCaisse(confiance_ocr=0.0)


def scanner_ticket_texte(texte_brut: str) -> TicketCaisse:
    """
    Extraction fallback par regex depuis du texte brut (copié-collé).

    Args:
        texte_brut: Texte du ticket (OCR externe ou copié)

    Returns:
        TicketCaisse parsé
    """
    lignes_ticket = []

    # Pattern: "NOM ARTICLE ..... PRIX"
    pattern = re.compile(
        r"^\s*(.+?)\s{2,}(\d+[.,]\d{2})\s*$",
        re.MULTILINE,
    )

    for match in pattern.finditer(texte_brut):
        article = match.group(1).strip()
        prix_str = match.group(2).replace(",", ".")

        # Ignorer les lignes de remise / sous-total
        if any(
            mot in article.lower()
            for mot in ["total", "sous-total", "remise", "tva", "cb ", "espèces"]
        ):
            continue

        try:
            prix = float(prix_str)
        except ValueError:
            continue

        # Détecter quantité "2x" en début
        qte_match = re.match(r"^(\d+)\s*[xX×]\s*(.+)", article)
        quantite = 1
        if qte_match:
            quantite = int(qte_match.group(1))
            article = qte_match.group(2).strip()

        lignes_ticket.append(LigneTicket(article=article, prix=prix, quantite=quantite))

    # Extraire le total
    total_match = re.search(r"TOTAL\s*[:\s]*(\d+[.,]\d{2})", texte_brut, re.IGNORECASE)
    total = float(total_match.group(1).replace(",", ".")) if total_match else 0.0

    # Extraire le magasin (première ligne non vide)
    premiere_ligne = ""
    for line in texte_brut.strip().split("\n"):
        stripped = line.strip()
        if stripped and len(stripped) > 3:
            premiere_ligne = stripped
            break

    return TicketCaisse(
        magasin=premiere_ligne,
        lignes=lignes_ticket,
        total=total,
        confiance_ocr=0.5,  # Texte brut moins fiable
    )


def ticket_vers_depenses(
    ticket: TicketCaisse,
) -> list[dict]:
    """
    Convertit un ticket parsé en dépenses prêtes à enregistrer.

    Returns:
        Liste de dicts compatibles avec enregistrer_depense_course()
    """
    depenses = []
    for ligne in ticket.lignes:
        depenses.append(
            {
                "montant": round(ligne.prix * ligne.quantite, 2),
                "description": ligne.article,
                "rayon": ligne.rayon or ligne.categorie,
                "date": ticket.date_achat,
                "magasin": ticket.magasin,
            }
        )
    return depenses


__all__ = [
    "LigneTicket",
    "TicketCaisse",
    "scanner_ticket_vision",
    "scanner_ticket_texte",
    "ticket_vers_depenses",
]
