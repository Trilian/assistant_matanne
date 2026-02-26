"""
Fonctions de chargement de données pour le module Énergie.
"""

import logging
from typing import TYPE_CHECKING

import streamlit as st

from .constants import MOIS_FR

if TYPE_CHECKING:
    from src.services.maison.depenses_crud_service import DepensesCrudService

logger = logging.getLogger(__name__)


def _get_service() -> "DepensesCrudService":
    """Charge paresseusement le service dépenses."""
    from src.services.maison.depenses_crud_service import get_depenses_crud_service

    return get_depenses_crud_service()


@st.cache_data(ttl=300)
def charger_historique_energie(type_energie: str, nb_mois: int = 12) -> list[dict]:
    """Charge l'historique de consommation énergétique depuis la DB.

    Args:
        type_energie: Type d'énergie (electricite, gaz, eau).
        nb_mois: Nombre de mois d'historique.

    Returns:
        Liste de dicts avec mois, annee, label, montant, consommation.
    """
    return _get_service().charger_historique_energie(type_energie, nb_mois)


def get_stats_energie(type_energie: str) -> dict:
    """Calcule les statistiques pour un type d'énergie.

    Args:
        type_energie: Type d'énergie.

    Returns:
        Dict avec total_annuel, moyenne_mensuelle, conso_totale, etc.
    """
    historique = charger_historique_energie(type_energie)

    montants = [h["montant"] for h in historique if h["montant"] is not None]
    consos = [h["consommation"] for h in historique if h["consommation"] is not None]

    total_annuel = sum(montants) if montants else 0
    moyenne_mensuelle = total_annuel / len(montants) if montants else 0
    conso_totale = sum(consos) if consos else 0
    conso_moyenne = conso_totale / len(consos) if consos else 0

    dernier_montant = montants[-1] if montants else 0
    derniere_conso = consos[-1] if consos else 0
    avant_dernier_montant = montants[-2] if len(montants) >= 2 else dernier_montant
    avant_derniere_conso = consos[-2] if len(consos) >= 2 else derniere_conso

    delta_montant = dernier_montant - avant_dernier_montant
    delta_conso = derniere_conso - avant_derniere_conso
    prix_unitaire = (total_annuel / conso_totale) if conso_totale > 0 else 0

    return {
        "total_annuel": total_annuel,
        "moyenne_mensuelle": moyenne_mensuelle,
        "conso_totale": conso_totale,
        "conso_moyenne": conso_moyenne,
        "dernier_montant": dernier_montant,
        "derniere_conso": derniere_conso,
        "delta_montant": delta_montant,
        "delta_conso": delta_conso,
        "prix_unitaire": prix_unitaire,
    }
