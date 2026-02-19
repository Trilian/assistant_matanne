"""
Enums pour les services Maison.

Tous les StrEnum/Enum utilisés par les schemas du module maison:
- NiveauUrgence, TypeAlerteMaison
- TypeZoneJardin, EtatPlante
"""

from enum import StrEnum

__all__ = [
    "NiveauUrgence",
    "TypeAlerteMaison",
    "TypeZoneJardin",
    "EtatPlante",
]


# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class NiveauUrgence(StrEnum):
    """Niveau d'urgence pour alertes."""

    CRITIQUE = "critique"
    HAUTE = "haute"
    MOYENNE = "moyenne"
    BASSE = "basse"
    INFO = "info"


class TypeAlerteMaison(StrEnum):
    """Types d'alertes maison."""

    METEO = "meteo"
    ENTRETIEN = "entretien"
    PROJET = "projet"
    STOCK = "stock"
    ENERGIE = "energie"
    JARDIN = "jardin"


class TypeZoneJardin(StrEnum):
    """Types de zones jardin."""

    POTAGER = "potager"
    PELOUSE = "pelouse"
    MASSIF = "massif"
    VERGER = "verger"
    HAIE = "haie"
    TERRASSE = "terrasse"
    COMPOST = "compost"
    SERRE = "serre"
    CABANE = "cabane"
    ALLEE = "allee"
    FLEURS = "fleurs"
    AROMATIQUES = "aromatiques"
    ABRI = "abri"
    BASSIN = "bassin"
    AUTRE = "autre"


class EtatPlante(StrEnum):
    """État de santé d'une plante."""

    EXCELLENT = "excellent"
    BON = "bon"
    ATTENTION = "attention"
    PROBLEME = "probleme"
    RECOLTE = "recolte"
