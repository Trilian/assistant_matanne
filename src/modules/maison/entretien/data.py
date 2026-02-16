"""
Entretien - Chargement des données.

Catalogue des tâches d'entretien et équipements.
"""

import json
import logging
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)


# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================


@st.cache_data(ttl=3600)
def charger_catalogue_entretien() -> dict:
    """Charge le catalogue des tâches d'entretien."""
    chemin = Path(__file__).parents[4] / "data" / "entretien_catalogue.json"
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement catalogue entretien: {e}")
        return _catalogue_defaut()


def _catalogue_defaut() -> dict:
    """Catalogue d'entretien par défaut."""
    return {
        "categories": {
            "electromenager": {
                "icon": "🔌",
                "couleur": "#3498db",
                "objets": {
                    "refrigerateur": {
                        "nom": "Réfrigérateur",
                        "taches": [
                            {"nom": "Nettoyer joints", "frequence_jours": 30, "duree_min": 10},
                            {"nom": "Nettoyer intérieur", "frequence_jours": 60, "duree_min": 30},
                            {
                                "nom": "Dégivrer congélateur",
                                "frequence_jours": 180,
                                "duree_min": 45,
                            },
                        ],
                    },
                    "lave_linge": {
                        "nom": "Lave-linge",
                        "taches": [
                            {"nom": "Nettoyer filtre", "frequence_jours": 30, "duree_min": 15},
                            {
                                "nom": "Cycle tambour vide 90°",
                                "frequence_jours": 30,
                                "duree_min": 5,
                            },
                            {"nom": "Nettoyer bac lessive", "frequence_jours": 14, "duree_min": 10},
                        ],
                    },
                    "lave_vaisselle": {
                        "nom": "Lave-vaisselle",
                        "taches": [
                            {"nom": "Nettoyer filtre", "frequence_jours": 14, "duree_min": 10},
                            {"nom": "Cycle entretien", "frequence_jours": 30, "duree_min": 5},
                        ],
                    },
                    "four": {
                        "nom": "Four",
                        "taches": [
                            {"nom": "Nettoyer intérieur", "frequence_jours": 30, "duree_min": 30},
                            {"nom": "Nettoyer vitre", "frequence_jours": 14, "duree_min": 10},
                        ],
                    },
                },
            },
            "sanitaires": {
                "icon": "🚿",
                "couleur": "#1abc9c",
                "objets": {
                    "douche": {
                        "nom": "Douche",
                        "taches": [
                            {"nom": "Détartrer pommeau", "frequence_jours": 30, "duree_min": 20},
                            {"nom": "Nettoyer joints", "frequence_jours": 14, "duree_min": 15},
                        ],
                    },
                    "toilettes": {
                        "nom": "Toilettes",
                        "taches": [
                            {"nom": "Nettoyage complet", "frequence_jours": 7, "duree_min": 15},
                            {"nom": "Détartrer cuvette", "frequence_jours": 30, "duree_min": 20},
                        ],
                    },
                },
            },
            "surfaces": {
                "icon": "🧹",
                "couleur": "#e74c3c",
                "objets": {
                    "sols": {
                        "nom": "Sols",
                        "taches": [
                            {"nom": "Aspirer", "frequence_jours": 3, "duree_min": 20},
                            {"nom": "Laver", "frequence_jours": 7, "duree_min": 30},
                        ],
                    },
                    "vitres": {
                        "nom": "Vitres",
                        "taches": [
                            {
                                "nom": "Nettoyer vitres intérieures",
                                "frequence_jours": 30,
                                "duree_min": 30,
                            },
                            {
                                "nom": "Nettoyer vitres extérieures",
                                "frequence_jours": 90,
                                "duree_min": 60,
                                "pro": True,
                            },
                        ],
                    },
                },
            },
            "exterieur": {
                "icon": "🏡",
                "couleur": "#27ae60",
                "objets": {
                    "gouttières": {
                        "nom": "Gouttières",
                        "taches": [
                            {
                                "nom": "Nettoyer",
                                "frequence_jours": 180,
                                "duree_min": 60,
                                "mois": [4, 10],
                            }
                        ],
                    },
                    "terrasse": {
                        "nom": "Terrasse",
                        "taches": [
                            {"nom": "Balayer", "frequence_jours": 7, "duree_min": 15},
                            {
                                "nom": "Nettoyer haute pression",
                                "frequence_jours": 180,
                                "duree_min": 90,
                                "mois": [4, 5],
                            },
                        ],
                    },
                },
            },
        },
        "pieces_type": {
            "cuisine": {
                "nom": "Cuisine",
                "icon": "🍳",
                "objets_courants": ["refrigerateur", "four", "lave_vaisselle"],
            },
            "salle_de_bain": {
                "nom": "Salle de bain",
                "icon": "🛁",
                "objets_courants": ["douche", "toilettes", "lave_linge"],
            },
            "salon": {"nom": "Salon", "icon": "🛋️", "objets_courants": ["sols", "vitres"]},
            "chambre": {"nom": "Chambre", "icon": "🛏️", "objets_courants": ["sols"]},
            "exterieur": {
                "nom": "Extérieur",
                "icon": "🏡",
                "objets_courants": ["gouttières", "terrasse"],
            },
        },
    }
