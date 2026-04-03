"""
Routes API pour les rapports IA — Résumés, bilanset analyses..

Génération de rapports narratifs IA personnalisés par domaine.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA
from src.api.utils import executer_async, gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rapports", tags=["Rapports IA"])


@router.get("/bilan-mois", responses=REPONSES_IA)
@gerer_exception_api
async def bilan_fin_de_mois(
    mois: int = Query(0, ge=0, le=12, description="Mois (1-12). 0 = mois courant"),
    annee: int = Query(0, ge=0, description="Année. 0 = année courante"),
    user: dict[str, Any] = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    INNO-11: Bilan fin de mois IA — Rapport narratif personnalisé.

    Génère un rapport IA mensuel couvrant:
    - Budget familial (dépenses par catégorie, évolutions)
    - Repas et nutrition (équilibre, coûts)
    - Jules (développement, jalons, activités)
    - Maison (projets complétés, énergie, jardin)
    - Points forts et améliorations suggérées

    Cette innovation permet à l'utilisateur de comprendre rapidement
    les tendances du mois et d'identifier des zones d'amélioration.

    Args:
        mois: Mois à analyser (1-12). Défaut: mois courant
        annee: Année. Défaut: année courante
        user: Utilisateur authentifié

    Returns:
        Rapport narratif IA avec sections budget, repas, Jules, maison
        + points forts et recommandations

    Example:
        ```
        GET /api/v1/rapports/bilan-mois?mois=3&annee=2026
        Authorization: Bearer <token>

        Response:
        {
            "titre": "Bilan du mois de mars 2026",
            "periode": "2026-03-01 à 2026-03-31",
            "resume_court": "Mois équilibré avec budget en hausse (+12%)",
            "sections": {
                "budget": "Ce mois-ci, vos dépenses totales...",
                "repas": "Votre cuisine a montré...",
                "jules": "Jules a progressé dans...",
                "maison": "Votre maison a connue..."
            },
            "points_forts": ["Repas équilibrés", "Économies en cuisine"],
            "recommandations": ["Augmenter temps activités Jules", "Reprendre le jardin"],
            "statistiques": {
                "depenses_totales": 1250.50,
                "nombre_repas": 87,
                "temps_activites_jules": 42,
                "projets_maison": 3
            }
        }
        ```
    """
    from datetime import date, timedelta
    from src.services.core.base import BaseAIService
    from src.core.ai import obtenir_client_ia

    now = date.today()
    mois_cible = mois if mois > 0 else now.month
    annee_cible = annee if annee > 0 else now.year

    # Déterminer la période (1er au dernier jour du mois)
    if mois_cible == 12:
        date_debut = date(annee_cible, 12, 1)
        date_fin = date(annee_cible + 1, 1, 1) - timedelta(days=1)
    else:
        date_debut = date(annee_cible, mois_cible, 1)
        date_fin = date(annee_cible, mois_cible + 1, 1) - timedelta(days=1)

    def _generer_bilan():
        from src.services.utilitaires.rapports_ia import obtenir_rapports_service

        service = obtenir_rapports_service()
        rapport = service.generer_bilan_mois(
            user_id=user.get("sub") or user.get("id"),
            date_debut=date_debut,
            date_fin=date_fin,
        )
        return rapport.model_dump() if hasattr(rapport, "model_dump") else rapport

    bilan = await executer_async(_generer_bilan)

    return bilan


@router.get("/comparaison-semaine", responses=REPONSES_IA)
@gerer_exception_api
async def comparaison_semaine(
    user: dict[str, Any] = Depends(require_auth),
):
    """
    INNO-4: Comparaison cette semaine vs la semaine dernière.

    Compare:
    - Dépenses (budget)
    - Nombre et type de repas
    - Activités (famille)
    - Consommation d'énergie (maison)

    Args:
        user: Utilisateur authentifié

    Returns:
        Comparaison semaine courante vs précédente avec tendances
    """
    from src.services.utilitaires.rapports_ia import obtenir_rapports_service

    service = obtenir_rapports_service()

    def _generer():
        return service.comparer_semaines(user_id=user.get("sub") or user.get("id"))

    resultat = await executer_async(_generer)
    return resultat.model_dump() if hasattr(resultat, "model_dump") else resultat


@router.post("/telecharger-bilan", responses=REPONSES_IA)
@gerer_exception_api
async def telecharger_bilan_pdf(
    mois: int = Query(0, ge=0, le=12, description="Mois à exporter"),
    annee: int = Query(0, ge=0, description="Année"),
    user: dict[str, Any] = Depends(require_auth),
):
    """
    Télécharge le bilan du mois en PDF (bilan-mois + graphiques).

    Args:
        mois: Mois (défaut: courant)
        annee: Année (défaut: courante)

    Returns:
        Fichier PDF du bilan mensuel
    """
    from datetime import date, timedelta
    from fastapi import HTTPException
    from fastapi.responses import FileResponse

    now = date.today()
    mois_cible = mois if mois > 0 else now.month
    annee_cible = annee if annee > 0 else now.year

    if mois_cible == 12:
        date_debut = date(annee_cible, 12, 1)
        date_fin = date(annee_cible + 1, 1, 1) - timedelta(days=1)
    else:
        date_debut = date(annee_cible, mois_cible, 1)
        date_fin = date(annee_cible, mois_cible + 1, 1) - timedelta(days=1)

    def _generer():
        from src.services.rapports.export import obtenir_service_export_pdf

        service = obtenir_service_export_pdf()
        return service.exporter_bilan_mois_pdf(date_debut, date_fin)

    try:
        pdf_path = await executer_async(_generer)
        if not pdf_path or not pdf_path.exists():
            raise HTTPException(status_code=500, detail="Erreur lors de la génération du PDF")

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=f"bilan-{mois_cible:02d}-{annee_cible}.pdf",
        )
    except Exception as e:
        logger.error(f"Erreur export PDF: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du PDF")
