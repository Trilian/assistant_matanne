"""
Service Bio/Local — Producteurs, circuits courts, saisonnalité.

Gère un annuaire de producteurs locaux avec spécialités,
et croise avec les besoins de la liste de courses.
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
class Producteur:
    """Producteur local ou fournisseur bio."""

    nom: str
    specialites: list[str] = field(default_factory=list)
    type_vente: str = "marché"  # marché, ferme, drive, panier, AMAP
    adresse: str = ""
    ville: str = ""
    telephone: str = ""
    url: str = ""
    jours_vente: list[str] = field(default_factory=list)  # ["samedi", "mercredi"]
    bio: bool = False
    note: float = 0.0  # 0-5 étoiles
    commentaire: str = ""
    actif: bool = True


@dataclass
class MatchProducteur:
    """Correspondance entre un besoin et un producteur."""

    article_nom: str
    producteur: Producteur
    confiance: float = 0.0  # 0-1
    disponible_saison: bool = True


@dataclass
class GuideLocal:
    """Guide d'achat local pour une liste de courses."""

    matches: list[MatchProducteur]
    producteurs_recommandes: list[Producteur]
    articles_non_trouves: list[str]
    pourcentage_local: float = 0.0


# ═══════════════════════════════════════════════════════════
# ANNUAIRE PRODUCTEURS (configurable par l'utilisateur)
# ═══════════════════════════════════════════════════════════

PRODUCTEURS_DEFAUT: list[Producteur] = [
    Producteur(
        nom="Mon Petit Potager",
        specialites=["légumes", "fruits", "herbes aromatiques"],
        type_vente="drive",
        url="https://www.monpetitpotager.fr/",
        bio=True,
        note=4.8,
        commentaire="Maraîcher local, paniers hebdomadaires",
    ),
    Producteur(
        nom="La Fourche",
        specialites=["épicerie bio", "produits secs", "hygiène", "vrac"],
        type_vente="drive",
        url="https://www.lafourche.fr/",
        bio=True,
        note=4.5,
        commentaire="Supermarché bio en ligne, adhésion annuelle",
    ),
]

# Catégories d'articles favorables au circuit court
CATEGORIES_CIRCUIT_COURT = {
    "Fruits et Légumes": ["légumes", "fruits", "herbes aromatiques"],
    "Boucherie": ["viande", "volaille"],
    "Poissonnerie": ["poisson", "fruits de mer"],
    "Fromage": ["fromage", "produits laitiers"],
    "Boulangerie": ["pain", "viennoiserie"],
    "Crèmerie": ["œufs", "lait", "beurre", "crème"],
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def trouver_producteurs(
    article_nom: str,
    producteurs: list[Producteur] | None = None,
    bio_seulement: bool = False,
) -> list[MatchProducteur]:
    """
    Trouve les producteurs pouvant fournir un article.

    Args:
        article_nom: Nom de l'article à trouver
        producteurs: Annuaire (défaut: PRODUCTEURS_DEFAUT)
        bio_seulement: Filtrer bio uniquement

    Returns:
        Matches triés par confiance
    """
    if producteurs is None:
        producteurs = PRODUCTEURS_DEFAUT

    article_lower = article_nom.lower()
    matches = []

    for prod in producteurs:
        if not prod.actif:
            continue
        if bio_seulement and not prod.bio:
            continue

        confiance = _calculer_confiance(article_lower, prod)
        if confiance > 0:
            matches.append(
                MatchProducteur(
                    article_nom=article_nom,
                    producteur=prod,
                    confiance=confiance,
                )
            )

    matches.sort(key=lambda m: m.confiance, reverse=True)
    return matches


def _calculer_confiance(article_lower: str, producteur: Producteur) -> float:
    """Calcule la confiance qu'un producteur fournit un article."""
    confiance = 0.0

    for spec in producteur.specialites:
        spec_lower = spec.lower()
        if article_lower in spec_lower or spec_lower in article_lower:
            confiance += 0.8
        # Vérifier si l'article appartient à une catégorie du producteur
        for _cat, items in CATEGORIES_CIRCUIT_COURT.items():
            if spec_lower in [i.lower() for i in items]:
                # Le producteur fait cette catégorie
                for cat_items in CATEGORIES_CIRCUIT_COURT.values():
                    if any(
                        article_lower in ci.lower() or ci.lower() in article_lower
                        for ci in cat_items
                    ):
                        if spec_lower in [ci.lower() for ci in cat_items]:
                            confiance += 0.5
                            break

    # Bonus bio
    if producteur.bio:
        confiance += 0.1

    # Bonus note
    confiance += producteur.note * 0.02

    return min(1.0, confiance)


def generer_guide_local(
    articles: list[dict],
    producteurs: list[Producteur] | None = None,
    bio_prioritaire: bool = True,
) -> GuideLocal:
    """
    Génère un guide d'achat local pour une liste de courses complète.

    Args:
        articles: Liste de dicts {nom, rayon, quantite}
        producteurs: Annuaire
        bio_prioritaire: Prioriser les producteurs bio

    Returns:
        GuideLocal avec matches et recommandations
    """
    if producteurs is None:
        producteurs = PRODUCTEURS_DEFAUT

    tous_matches = []
    non_trouves = []
    producteurs_utilises: set[str] = set()

    for art in articles:
        nom = art.get("nom", "")
        matches = trouver_producteurs(nom, producteurs, bio_seulement=bio_prioritaire)

        if matches:
            best = matches[0]
            tous_matches.append(best)
            producteurs_utilises.add(best.producteur.nom)
        else:
            # Retenter sans filtre bio
            if bio_prioritaire:
                matches = trouver_producteurs(nom, producteurs, bio_seulement=False)
                if matches:
                    tous_matches.append(matches[0])
                    producteurs_utilises.add(matches[0].producteur.nom)
                    continue
            non_trouves.append(nom)

    pct_local = len(tous_matches) / len(articles) * 100 if articles else 0

    recommandes = [p for p in producteurs if p.nom in producteurs_utilises]
    recommandes.sort(key=lambda p: p.note, reverse=True)

    return GuideLocal(
        matches=tous_matches,
        producteurs_recommandes=recommandes,
        articles_non_trouves=non_trouves,
        pourcentage_local=round(pct_local, 1),
    )


def obtenir_producteurs_actifs(
    producteurs: list[Producteur] | None = None,
    jour: str | None = None,
) -> list[Producteur]:
    """
    Liste les producteurs actifs, optionnellement filtrés par jour de vente.

    Args:
        producteurs: Annuaire
        jour: Jour de la semaine en français (ex: "samedi")
    """
    if producteurs is None:
        producteurs = PRODUCTEURS_DEFAUT

    actifs = [p for p in producteurs if p.actif]

    if jour:
        jour_lower = jour.lower()
        actifs = [
            p
            for p in actifs
            if not p.jours_vente or jour_lower in [j.lower() for j in p.jours_vente]
        ]

    return actifs


__all__ = [
    "Producteur",
    "MatchProducteur",
    "GuideLocal",
    "PRODUCTEURS_DEFAUT",
    "trouver_producteurs",
    "generer_guide_local",
    "obtenir_producteurs_actifs",
]
