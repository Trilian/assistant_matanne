"""
Service Bio & Local — Analyse de saisonnalité et circuits courts.

Centralise la logique bio/local :
- Saisonnalité des produits (produits_de_saison.json)
- Matching producteurs locaux (producteurs.py)
- Recommandations unifiées par article

Utilisé par l'endpoint courses bio-local et le planning.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .producteurs import (
    PRODUCTEURS_DEFAUT,
    GuideLocal,
    Producteur,
    generer_guide_local,
    trouver_producteurs,
)

logger = logging.getLogger(__name__)

MOIS_NOMS = [
    "",
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]

_SAISON_PATH = Path("data/reference/produits_de_saison.json")


@dataclass
class InfoBioLocal:
    """Résultat d'analyse bio/local pour un article."""

    article_id: int
    nom: str
    en_saison: bool = False
    bio_disponible: bool = False
    local_disponible: bool = False
    producteur: str | None = None
    alternative_bio: str | None = None


@dataclass
class AnalyseBioLocal:
    """Résultat complet de l'analyse bio/local d'une liste."""

    liste_id: int
    mois: str
    suggestions: list[InfoBioLocal] = field(default_factory=list)

    @property
    def nb_en_saison(self) -> int:
        return sum(1 for s in self.suggestions if s.en_saison)

    @property
    def nb_local(self) -> int:
        return sum(1 for s in self.suggestions if s.local_disponible)

    @property
    def pourcentage_saison(self) -> float:
        if not self.suggestions:
            return 0.0
        return round(self.nb_en_saison / len(self.suggestions) * 100, 1)


def charger_produits_saison() -> dict:
    """Charge le référentiel de saisonnalité."""
    if _SAISON_PATH.exists():
        return json.loads(_SAISON_PATH.read_text(encoding="utf-8"))
    logger.warning("Fichier produits_de_saison.json introuvable")
    return {}


def verifier_saisonnalite(
    nom_article: str,
    mois: int | None = None,
    produits_saison: dict | None = None,
) -> bool:
    """Vérifie si un article est de saison.

    Args:
        nom_article: Nom de l'article (insensible à la casse).
        mois: Numéro du mois (1-12). Défaut : mois courant.
        produits_saison: Référentiel chargé (optionnel, chargé si absent).

    Returns:
        True si le produit est de saison.
    """
    if produits_saison is None:
        produits_saison = charger_produits_saison()

    if mois is None:
        mois = date.today().month

    mois_str = MOIS_NOMS[mois]
    nom_lower = nom_article.lower()

    for _categorie, produits in produits_saison.items():
        if not isinstance(produits, list):
            continue
        for p in produits:
            if isinstance(p, dict) and nom_lower in p.get("nom", "").lower():
                mois_dispo = p.get("mois", [])
                if mois_str in mois_dispo or mois in mois_dispo:
                    return True
    return False


def analyser_articles_bio_local(
    articles: list[dict],
    liste_id: int = 0,
    producteurs: list[Producteur] | None = None,
    bio_prioritaire: bool = True,
) -> AnalyseBioLocal:
    """Analyse une liste d'articles pour bio/local/saison.

    Args:
        articles: Liste de dicts avec au minimum {"id": int, "nom": str}.
        liste_id: ID de la liste source.
        producteurs: Annuaire de producteurs (défaut : PRODUCTEURS_DEFAUT).
        bio_prioritaire: Prioriser les producteurs bio.

    Returns:
        AnalyseBioLocal avec les suggestions par article.
    """
    if producteurs is None:
        producteurs = PRODUCTEURS_DEFAUT

    mois_actuel = date.today().month
    mois_str = MOIS_NOMS[mois_actuel]
    produits_saison = charger_produits_saison()

    suggestions: list[InfoBioLocal] = []

    for art in articles:
        nom = art.get("nom", "")
        info = InfoBioLocal(
            article_id=art.get("id", 0),
            nom=nom,
        )

        # Saisonnalité
        info.en_saison = verifier_saisonnalite(nom, mois_actuel, produits_saison)

        # Producteurs locaux
        matches = trouver_producteurs(nom, producteurs, bio_seulement=False)
        if matches:
            best = matches[0]
            info.local_disponible = True
            info.producteur = best.producteur.nom
            info.bio_disponible = best.producteur.bio

        suggestions.append(info)

    return AnalyseBioLocal(
        liste_id=liste_id,
        mois=mois_str,
        suggestions=suggestions,
    )


def generer_recommandations_locales(
    noms_articles: list[str],
    producteurs: list[Producteur] | None = None,
    bio_prioritaire: bool = True,
) -> GuideLocal:
    """Génère un guide d'achat local pour une liste d'articles.

    Wrapper pratique autour de generer_guide_local() de producteurs.py.
    """
    return generer_guide_local(
        articles=noms_articles,
        producteurs=producteurs,
        bio_prioritaire=bio_prioritaire,
    )


__all__ = [
    "InfoBioLocal",
    "AnalyseBioLocal",
    "charger_produits_saison",
    "verifier_saisonnalite",
    "analyser_articles_bio_local",
    "generer_recommandations_locales",
]
