"""Fonctions journal familial extraites du service innovations."""

from __future__ import annotations

from datetime import date
from typing import Any

from .types_transverses import JournalFamilialAutoResponse, RapportMensuelPdfResponse


def generer_journal_familial_auto(service: Any) -> JournalFamilialAutoResponse | None:
    """Journal familial automatique hebdomadaire."""
    contexte = service._collecter_contexte_mensuel()
    prompt = f"""Redige un journal familial hebdomadaire court et chaleureux a partir du contexte:
{contexte}

Retourne un JSON avec:
- semaine_reference
- titre
- resume
- faits_marquants (3 a 5)
- moments_joyeux (2 a 4)
- points_attention (1 a 3)
"""
    return service.call_with_parsing_sync(
        prompt=prompt,
        response_model=JournalFamilialAutoResponse,
        system_prompt="Tu es chroniqueur familial positif, concret et concis.",
    )


def generer_journal_familial_pdf(service: Any) -> RapportMensuelPdfResponse | None:
    """Export PDF du journal familial automatique."""
    journal = service.generer_journal_familial_auto()
    if not journal:
        return None
    contenu = service._generer_pdf_simple(
        titre=journal.titre or "Journal familial",
        sections=[
            ("Resume", [journal.resume]),
            ("Faits marquants", journal.faits_marquants),
            ("Moments joyeux", journal.moments_joyeux),
            ("Points d'attention", journal.points_attention),
        ],
    )
    return RapportMensuelPdfResponse(
        mois_reference=journal.semaine_reference,
        filename=f"journal_familial_{date.today().isoformat()}.pdf",
        contenu_base64=contenu,
    )


def generer_rapport_mensuel_pdf(service: Any, mois: str | None = None) -> RapportMensuelPdfResponse | None:
    """Rapport mensuel PDF consolide avec narratif IA."""
    mois_ref = mois or date.today().strftime("%Y-%m")
    bilan = service.generer_resume_mensuel_ia()
    score = service.calculer_score_famille_hebdo()
    sections = [
        ("Synthese IA", [bilan.resume_global] if bilan else ["Synthese indisponible"]),
        ("Faits marquants", bilan.faits_marquants if bilan else []),
        (
            "Score famille hebdomadaire",
            [f"Score global: {score.score_global}/100"] if score else ["Score indisponible"],
        ),
        ("Recommandations", bilan.recommandations if bilan else []),
    ]
    contenu = service._generer_pdf_simple(
        titre=f"Rapport mensuel {mois_ref}",
        sections=sections,
    )
    return RapportMensuelPdfResponse(
        mois_reference=mois_ref,
        filename=f"rapport_mensuel_{mois_ref}.pdf",
        contenu_base64=contenu,
    )
