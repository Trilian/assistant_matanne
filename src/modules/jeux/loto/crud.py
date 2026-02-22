"""
Module Loto - Operations CRUD (creation/mise à jour)

Délègue au service LotoCrudService pour toutes les opérations DB.
"""

from datetime import date

import streamlit as st

from src.services.jeux import get_loto_crud_service

from .calculs import verifier_grille
from .constants import COUT_GRILLE


def ajouter_tirage(date_t: date, numeros: list, chance: int, jackpot: int = None):
    """Ajoute un nouveau tirage"""
    try:
        if len(numeros) != 5:
            st.error("Il faut exactement 5 numeros")
            return False

        service = get_loto_crud_service()
        result = service.ajouter_tirage(
            date_t=date_t,
            numeros=numeros,
            chance=chance,
            jackpot=jackpot,
            verifier_fn=verifier_grille,
        )

        if result:
            st.success(f"✅ Tirage du {date_t} enregistre!")
        return result

    except Exception as e:
        st.error(f"❌ Erreur ajout tirage: {e}")
        return False


def enregistrer_grille(
    numeros: list, chance: int, source: str = "manuel", est_virtuelle: bool = True
):
    """Enregistre une nouvelle grille"""
    try:
        if len(numeros) != 5:
            st.error("Il faut exactement 5 numeros")
            return False

        service = get_loto_crud_service()
        result = service.enregistrer_grille(
            numeros=numeros, chance=chance, source=source, est_virtuelle=est_virtuelle
        )

        if result:
            numeros_tries = sorted(numeros)
            st.success(f"✅ Grille enregistrée: {'-'.join(map(str, numeros_tries))} + N°{chance}")
        return result

    except Exception as e:
        st.error(f"❌ Erreur enregistrement grille: {e}")
        return False
