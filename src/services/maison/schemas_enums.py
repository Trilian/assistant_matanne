"""
Enums pour les services Maison.

Tous les StrEnum/Enum utilisés par les schemas du module maison:
- NiveauUrgence, TypeAlerteMaison, CategorieObjet
- TypeZoneJardin, EtatPlante, StatutObjet
- TypeModificationPiece, PrioriteRemplacement
"""

from enum import Enum, StrEnum

__all__ = [
    "NiveauUrgence",
    "TypeAlerteMaison",
    "CategorieObjet",
    "TypeZoneJardin",
    "EtatPlante",
    "StatutObjet",
    "TypeModificationPiece",
    "PrioriteRemplacement",
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


class CategorieObjet(StrEnum):
    """Catégories d'objets maison."""

    ELECTROMENAGER = "electromenager"
    VAISSELLE = "vaisselle"
    OUTIL = "outil"
    DECORATION = "decoration"
    VETEMENT = "vetement"
    ELECTRONIQUE = "electronique"
    MEUBLE = "meuble"
    LINGE = "linge"
    JOUET = "jouet"
    LIVRE = "livre"
    AUTRE = "autre"


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


class StatutObjet(StrEnum):
    """Statut d'un objet dans l'inventaire."""

    FONCTIONNE = "fonctionne"  # En bon état
    A_REPARER = "a_reparer"  # Nécessite réparation
    A_CHANGER = "a_changer"  # À remplacer
    A_ACHETER = "a_acheter"  # Nouvel achat prévu
    EN_COMMANDE = "en_commande"  # Déjà commandé
    HORS_SERVICE = "hors_service"  # Ne fonctionne plus
    A_DONNER = "a_donner"  # À donner/vendre
    ARCHIVE = "archive"  # Historique seulement


class TypeModificationPiece(StrEnum):
    """Types de modifications de pièce."""

    AJOUT_MEUBLE = "ajout_meuble"
    RETRAIT_MEUBLE = "retrait_meuble"
    DEPLACEMENT = "deplacement"
    RENOVATION = "renovation"
    PEINTURE = "peinture"
    AMENAGEMENT = "amenagement"
    REPARATION = "reparation"


class PrioriteRemplacement(StrEnum):
    """Priorité pour remplacement d'objet."""

    URGENTE = "urgente"  # Dans la semaine
    HAUTE = "haute"  # Dans le mois
    NORMALE = "normale"  # Quand budget permet
    BASSE = "basse"  # Optionnel
    FUTURE = "future"  # Un jour...
