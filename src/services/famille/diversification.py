"""
Service de diversification alimentaire bébé (Jules, ~19 mois).

Recommandations d'introduction d'aliments par âge, suivi des
aliments déjà introduits, et détection d'allergènes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class AlimentBebe:
    """Aliment avec recommandation d'âge d'introduction."""

    nom: str
    categorie: str  # legume, fruit, feculent, proteine, laitage, matiere_grasse
    age_intro_mois: int  # Âge minimum recommandé
    allergene: bool = False
    allergene_type: str = ""  # gluten, lait, oeuf, arachide, fruits_coque, poisson, etc.
    texture_recommandee: str = ""  # puree, mouline, morceaux_fondants, morceaux, cru
    notes: str = ""


@dataclass
class SuiviIntroduction:
    """Suivi de l'introduction d'un aliment pour le bébé."""

    aliment: str
    date_introduction: date
    age_mois: int
    reaction: str = "ok"  # ok, leger, modere, severe
    notes: str = ""


@dataclass
class RecommandationDiversification:
    """Recommandation personnalisée basée sur l'âge et le suivi."""

    age_mois: int
    aliments_a_introduire: list[AlimentBebe]
    aliments_deja_ok: list[str]
    allergenes_a_tester: list[AlimentBebe]
    prochaine_etape: str = ""


# ═══════════════════════════════════════════════════════════
# CATALOGUE DIVERSIFICATION (OMS + recommandations pédiatre FR)
# ═══════════════════════════════════════════════════════════

CATALOGUE_ALIMENTS: list[AlimentBebe] = [
    # Légumes (4-6 mois) — purée lisse
    AlimentBebe("carotte", "legume", 4, texture_recommandee="puree"),
    AlimentBebe("haricot vert", "legume", 4, texture_recommandee="puree"),
    AlimentBebe("courgette", "legume", 4, texture_recommandee="puree"),
    AlimentBebe("épinard", "legume", 4, texture_recommandee="puree"),
    AlimentBebe("potiron", "legume", 4, texture_recommandee="puree"),
    AlimentBebe("petit pois", "legume", 4, texture_recommandee="puree"),
    AlimentBebe("brocoli", "legume", 4, texture_recommandee="puree"),
    AlimentBebe("patate douce", "legume", 4, texture_recommandee="puree"),
    AlimentBebe("artichaut", "legume", 6, texture_recommandee="puree"),
    AlimentBebe("poireau", "legume", 6, texture_recommandee="puree"),
    AlimentBebe("navet", "legume", 6, texture_recommandee="puree"),
    AlimentBebe("betterave", "legume", 6, texture_recommandee="puree"),
    AlimentBebe("aubergine", "legume", 6, texture_recommandee="puree"),
    AlimentBebe("tomate (cuite)", "legume", 6, texture_recommandee="puree"),
    AlimentBebe("poivron", "legume", 8, texture_recommandee="mouline"),
    AlimentBebe("champignon", "legume", 8, texture_recommandee="mouline"),
    AlimentBebe("concombre", "legume", 12, texture_recommandee="morceaux"),
    AlimentBebe("tomate (crue)", "legume", 12, texture_recommandee="morceaux"),
    # Fruits (4-6 mois)
    AlimentBebe("pomme", "fruit", 4, texture_recommandee="compote"),
    AlimentBebe("poire", "fruit", 4, texture_recommandee="compote"),
    AlimentBebe("banane", "fruit", 4, texture_recommandee="puree"),
    AlimentBebe("pêche", "fruit", 6, texture_recommandee="compote"),
    AlimentBebe("abricot", "fruit", 6, texture_recommandee="compote"),
    AlimentBebe("prune", "fruit", 6, texture_recommandee="compote"),
    AlimentBebe("fraise", "fruit", 6, texture_recommandee="puree"),
    AlimentBebe("framboise", "fruit", 8, texture_recommandee="puree"),
    AlimentBebe("melon", "fruit", 8, texture_recommandee="morceaux_fondants"),
    AlimentBebe("mangue", "fruit", 8, texture_recommandee="puree"),
    AlimentBebe("kiwi", "fruit", 9, texture_recommandee="morceaux_fondants"),
    AlimentBebe("agrumes", "fruit", 9, texture_recommandee="morceaux"),
    # Féculents (4-6 mois)
    AlimentBebe("pomme de terre", "feculent", 4, texture_recommandee="puree"),
    AlimentBebe("riz", "feculent", 6, texture_recommandee="mouline"),
    AlimentBebe("semoule", "feculent", 7, allergene=True, allergene_type="gluten"),
    AlimentBebe("pâtes", "feculent", 7, allergene=True, allergene_type="gluten"),
    AlimentBebe("pain", "feculent", 8, allergene=True, allergene_type="gluten"),
    AlimentBebe("quinoa", "feculent", 8, texture_recommandee="mouline"),
    AlimentBebe("lentilles", "feculent", 8, texture_recommandee="mouline"),
    # Protéines (6 mois)
    AlimentBebe(
        "poulet", "proteine", 6, texture_recommandee="puree", notes="10g/j à 6m, 20g à 12m"
    ),
    AlimentBebe("dinde", "proteine", 6, texture_recommandee="puree"),
    AlimentBebe("boeuf", "proteine", 6, texture_recommandee="puree"),
    AlimentBebe("jambon blanc", "proteine", 6, texture_recommandee="puree"),
    AlimentBebe(
        "poisson blanc",
        "proteine",
        6,
        allergene=True,
        allergene_type="poisson",
        texture_recommandee="puree",
    ),
    AlimentBebe("saumon", "proteine", 8, allergene=True, allergene_type="poisson"),
    AlimentBebe("oeuf (jaune)", "proteine", 6, allergene=True, allergene_type="oeuf"),
    AlimentBebe("oeuf (entier)", "proteine", 9, allergene=True, allergene_type="oeuf"),
    AlimentBebe("crevette", "proteine", 12, allergene=True, allergene_type="crustaces"),
    # Laitages
    AlimentBebe("yaourt nature", "laitage", 6, allergene=True, allergene_type="lait"),
    AlimentBebe("fromage frais", "laitage", 6, allergene=True, allergene_type="lait"),
    AlimentBebe("fromage à pâte cuite", "laitage", 9, allergene=True, allergene_type="lait"),
    AlimentBebe("lait de vache", "laitage", 12, allergene=True, allergene_type="lait"),
    # Matières grasses
    AlimentBebe("huile de colza", "matiere_grasse", 4),
    AlimentBebe("huile d'olive", "matiere_grasse", 4),
    AlimentBebe("beurre", "matiere_grasse", 6, allergene=True, allergene_type="lait"),
    # Fruits à coque (allergènes majeurs)
    AlimentBebe(
        "amande (poudre)",
        "allergene",
        4,
        allergene=True,
        allergene_type="fruits_coque",
        notes="Introduction précoce recommandée",
    ),
    AlimentBebe("noisette (poudre)", "allergene", 4, allergene=True, allergene_type="fruits_coque"),
    AlimentBebe(
        "arachide (poudre fine)",
        "allergene",
        4,
        allergene=True,
        allergene_type="arachide",
        notes="Introduction précoce recommandée",
    ),
]


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def obtenir_recommandations(
    age_mois: int,
    aliments_deja_ok: list[str] | None = None,
) -> RecommandationDiversification:
    """
    Génère des recommandations de diversification personnalisées.

    Args:
        age_mois: Âge du bébé en mois
        aliments_deja_ok: Aliments déjà introduits avec succès

    Returns:
        RecommandationDiversification
    """
    if aliments_deja_ok is None:
        aliments_deja_ok = []

    deja_ok_lower = {a.lower() for a in aliments_deja_ok}

    # Aliments adaptés à l'âge et pas encore introduits
    a_introduire = [
        aliment
        for aliment in CATALOGUE_ALIMENTS
        if aliment.age_intro_mois <= age_mois
        and aliment.nom.lower() not in deja_ok_lower
        and not aliment.allergene
    ]

    # Allergènes à tester (adaptés à l'âge, pas encore testés)
    allergenes = [
        aliment
        for aliment in CATALOGUE_ALIMENTS
        if aliment.allergene
        and aliment.age_intro_mois <= age_mois
        and aliment.nom.lower() not in deja_ok_lower
    ]

    # Prochaine étape
    etapes = {
        range(0, 4): "Allaitement/lait exclusif encore quelques semaines",
        range(4, 6): "Commencez par les légumes en purée lisse, un par un",
        range(6, 8): "Introduisez les protéines (poulet, poisson blanc) et les fruits",
        range(8, 10): "Textures moulinées, nouveaux féculents avec gluten",
        range(10, 12): "Morceaux fondants, diversifiez les protéines",
        range(12, 18): "Morceaux, alimentation familiale adaptée",
        range(18, 48): "Alimentation famille — vérifier le dernier tiers d'allergènes",
    }

    prochaine = "Continuez la diversification !"
    for age_range, conseil in etapes.items():
        if age_mois in age_range:
            prochaine = conseil
            break

    return RecommandationDiversification(
        age_mois=age_mois,
        aliments_a_introduire=a_introduire[:10],  # Limiter à 10 suggestions
        aliments_deja_ok=list(deja_ok_lower),
        allergenes_a_tester=allergenes,
        prochaine_etape=prochaine,
    )


def texture_par_age(age_mois: int) -> str:
    """Retourne la texture recommandée par âge."""
    if age_mois < 6:
        return "puree"
    if age_mois < 8:
        return "mouline"
    if age_mois < 12:
        return "morceaux_fondants"
    if age_mois < 18:
        return "morceaux"
    return "normal"


def lister_allergenes_majeurs() -> list[AlimentBebe]:
    """Liste les 14 allergènes majeurs du catalogue."""
    return [a for a in CATALOGUE_ALIMENTS if a.allergene]


def rechercher_aliment(nom: str) -> AlimentBebe | None:
    """Recherche un aliment dans le catalogue."""
    nom_lower = nom.lower()
    for aliment in CATALOGUE_ALIMENTS:
        if aliment.nom.lower() == nom_lower or nom_lower in aliment.nom.lower():
            return aliment
    return None


__all__ = [
    "AlimentBebe",
    "SuiviIntroduction",
    "RecommandationDiversification",
    "CATALOGUE_ALIMENTS",
    "obtenir_recommandations",
    "texture_par_age",
    "lister_allergenes_majeurs",
    "rechercher_aliment",
]
