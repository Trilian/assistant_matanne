"""
Fonctions CRUD pour les paris, equipes et matchs.

Délègue au service ParisCrudService pour toutes les opérations DB.
"""

import logging
from datetime import date
from decimal import Decimal

import streamlit as st

from src.services.jeux import get_paris_crud_service

logger = logging.getLogger(__name__)


def enregistrer_pari(
    match_id: int, prediction: str, cote: float, mise: float = 0, est_virtuel: bool = True
):
    """Enregistre un nouveau pari"""
    try:
        service = get_paris_crud_service()
        result = service.enregistrer_pari(
            match_id=match_id,
            prediction=prediction,
            cote=cote,
            mise=mise,
            est_virtuel=est_virtuel,
        )
        return result
    except Exception as e:
        st.error(f"❌ Erreur enregistrement pari: {e}")
        return False


def ajouter_equipe(nom: str, championnat: str):
    """Ajoute une nouvelle equipe"""
    try:
        service = get_paris_crud_service()
        result = service.ajouter_equipe(nom=nom, championnat=championnat)
        if result:
            st.success(f"✅ Équipe '{nom}' ajoutee!")
        return result
    except Exception as e:
        st.error(f"❌ Erreur ajout equipe: {e}")
        return False


def ajouter_match(
    equipe_dom_id: int, equipe_ext_id: int, championnat: str, date_match: date, heure: str = None
):
    """Ajoute un nouveau match"""
    try:
        service = get_paris_crud_service()
        result = service.ajouter_match(
            equipe_dom_id=equipe_dom_id,
            equipe_ext_id=equipe_ext_id,
            championnat=championnat,
            date_match=date_match,
            heure=heure,
        )
        if result:
            st.success("✅ Match ajoute!")
        return result
    except Exception as e:
        st.error(f"❌ Erreur ajout match: {e}")
        return False


def enregistrer_resultat_match(match_id: int, score_dom: int, score_ext: int):
    """Enregistre le resultat d'un match"""
    try:
        service = get_paris_crud_service()
        result = service.enregistrer_resultat_match(
            match_id=match_id, score_dom=score_dom, score_ext=score_ext
        )
        if result:
            st.success(f"✅ Resultat enregistre: {score_dom}-{score_ext}")
        return result
    except Exception as e:
        st.error(f"❌ Erreur enregistrement resultat: {e}")
        return False


def supprimer_match(match_id: int) -> bool:
    """
    Supprime un match et ses paris associes.

    Args:
        match_id: ID du match à supprimer

    Returns:
        True si suppression reussie
    """
    try:
        service = get_paris_crud_service()
        return service.supprimer_match(match_id)
    except Exception as e:
        logger.error(f"❌ Erreur suppression match: {e}")
        return False


__all__ = [
    "enregistrer_pari",
    "ajouter_equipe",
    "ajouter_match",
    "enregistrer_resultat_match",
    "supprimer_match",
]
