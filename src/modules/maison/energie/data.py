"""
Fonctions de chargement de données pour le module Énergie.
"""

import logging
from datetime import date

import streamlit as st

from src.core.db import obtenir_contexte_db

from .constants import ENERGIES, MOIS_FR

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300)
def charger_historique_energie(type_energie: str, nb_mois: int = 12) -> list[dict]:
    """Charge l'historique de consommation énergétique depuis la DB.

    Args:
        type_energie: Type d'énergie (electricite, gaz, eau).
        nb_mois: Nombre de mois d'historique.

    Returns:
        Liste de dicts avec mois, annee, label, montant, consommation.
    """
    today = date.today()
    result = []

    try:
        with obtenir_contexte_db() as db:
            for i in range(nb_mois):
                # Calculer le mois cible (en remontant depuis aujourd'hui)
                mois_offset = nb_mois - 1 - i
                mois = today.month - mois_offset
                annee = today.year
                while mois <= 0:
                    mois += 12
                    annee -= 1

                label = MOIS_FR[mois] if 1 <= mois <= 12 else f"M{mois}"

                # Requête DB pour ce mois
                try:
                    from src.core.models import DepenseMaison
                except ImportError:
                    DepenseMaison = None

                montant = None
                consommation = None

                if DepenseMaison is not None:
                    depense = (
                        db.query(DepenseMaison)
                        .filter(
                            DepenseMaison.categorie == type_energie,
                            DepenseMaison.mois == mois,
                            DepenseMaison.annee == annee,
                        )
                        .first()
                    )
                    if depense:
                        montant = depense.montant
                        consommation = getattr(depense, "consommation", None)

                result.append(
                    {
                        "mois": mois,
                        "annee": annee,
                        "label": label,
                        "montant": montant,
                        "consommation": consommation,
                    }
                )
    except Exception as e:
        logger.error(f"Erreur chargement historique {type_energie}: {e}")
        # Retourner des entrées vides en cas d'erreur
        for i in range(nb_mois):
            mois_offset = nb_mois - 1 - i
            mois = today.month - mois_offset
            annee = today.year
            while mois <= 0:
                mois += 12
                annee -= 1
            label = MOIS_FR[mois] if 1 <= mois <= 12 else f"M{mois}"
            result.append(
                {
                    "mois": mois,
                    "annee": annee,
                    "label": label,
                    "montant": None,
                    "consommation": None,
                }
            )

    return result


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
