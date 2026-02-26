"""
Optimisation de trajets courses — Multi-magasins.

Compare les prix entre magasins et optimise le parcours
pour minimiser temps + coût total (distance + économies).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class Magasin:
    """Un magasin de courses."""

    nom: str
    adresse: str = ""
    type_magasin: str = "supermarche"  # supermarche, bio, marche, producteur, drive
    latitude: float | None = None
    longitude: float | None = None
    specialites: list[str] = field(default_factory=list)  # bio, local, vrac, etc.
    url_drive: str = ""
    horaires: str = ""
    note_qualite: float = 0.0  # 0-5
    distance_km: float = 0.0  # Distance depuis domicile


@dataclass
class ArticleMagasin:
    """Article disponible dans un magasin avec prix."""

    nom_article: str
    magasin: str
    prix_estime: float = 0.0
    disponible: bool = True
    bio: bool = False
    local: bool = False


@dataclass
class PlanCourses:
    """Plan de courses optimisé multi-magasins."""

    magasins_prevus: list[Magasin]
    articles_par_magasin: dict[str, list[ArticleMagasin]] = field(default_factory=dict)
    cout_total_estime: float = 0.0
    economie_vs_un_seul: float = 0.0
    distance_totale_km: float = 0.0
    temps_estime_min: int = 0
    ordre_visite: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# MAGASINS par défaut (configurables par l'utilisateur)
# ═══════════════════════════════════════════════════════════

MAGASINS_DEFAUT: list[Magasin] = [
    Magasin(
        nom="La Fourche",
        type_magasin="drive",
        specialites=["bio", "zéro déchet", "vrac"],
        url_drive="https://www.lafourche.fr/",
        note_qualite=4.5,
    ),
    Magasin(
        nom="Mon Petit Potager",
        type_magasin="producteur",
        specialites=["local", "bio", "frais", "maraîcher"],
        url_drive="https://www.monpetitpotager.fr/",
        note_qualite=4.8,
    ),
]


# ═══════════════════════════════════════════════════════════
# AFFINITÉS ARTICLE → MAGASIN
# ═══════════════════════════════════════════════════════════

# Mapping catégorie → meilleur type de magasin
AFFINITE_MAGASIN: dict[str, list[str]] = {
    "Fruits et Légumes": ["producteur", "marche", "bio"],
    "Bio": ["bio", "drive"],
    "Boucherie": ["boucherie", "marche"],
    "Poissonnerie": ["poissonnerie", "marche"],
    "Fromage": ["fromagerie", "marche"],
    "Boulangerie": ["boulangerie"],
    "Épicerie salée": ["supermarche", "drive"],
    "Épicerie sucrée": ["supermarche", "drive"],
    "Conserves": ["supermarche", "drive"],
    "Boissons": ["supermarche", "drive"],
    "Hygiène": ["supermarche", "drive"],
    "Entretien": ["supermarche", "drive"],
    "Bébé": ["supermarche", "drive"],
}


def optimiser_trajet(
    articles: list[dict],
    magasins: list[Magasin] | None = None,
    priorite: str = "economie",  # economie, temps, bio
) -> PlanCourses:
    """
    Optimise la répartition des courses entre magasins.

    Algorithme simplifié (heuristique gloutonne):
    1. Attribue chaque article au meilleur magasin selon la priorité
    2. Élimine les magasins avec trop peu d'articles
    3. Ordonne les magasins par distance

    Args:
        articles: Liste de dicts {nom, rayon, quantite, bio_prefere}
        magasins: Magasins disponibles (défaut: MAGASINS_DEFAUT)
        priorite: Critère d'optimisation

    Returns:
        PlanCourses optimisé
    """
    if magasins is None:
        magasins = MAGASINS_DEFAUT.copy()

    if not magasins or not articles:
        return PlanCourses(magasins_prevus=[], ordre_visite=[])

    articles_par_mag: dict[str, list[ArticleMagasin]] = {m.nom: [] for m in magasins}

    for art in articles:
        nom = art.get("nom", "")
        rayon = art.get("rayon", "Autre")
        bio_pref = art.get("bio_prefere", False)

        meilleur = _choisir_magasin(rayon, bio_pref, magasins, priorite)
        articles_par_mag[meilleur.nom].append(
            ArticleMagasin(
                nom_article=nom,
                magasin=meilleur.nom,
                bio=bio_pref or "bio" in meilleur.specialites,
                local="local" in meilleur.specialites,
            )
        )

    # Éliminer les magasins vides
    magasins_actifs = [m for m in magasins if articles_par_mag.get(m.nom)]
    articles_par_mag = {k: v for k, v in articles_par_mag.items() if v}

    # Ordonner par distance
    magasins_actifs.sort(key=lambda m: m.distance_km)
    ordre = [m.nom for m in magasins_actifs]

    # Estimer le temps: 5 min/magasin + 2 min/trajet + temps par article
    nb_articles = sum(len(v) for v in articles_par_mag.values())
    temps = len(magasins_actifs) * 10 + nb_articles * 0.5
    distance = sum(m.distance_km for m in magasins_actifs) * 2  # Aller-retour

    return PlanCourses(
        magasins_prevus=magasins_actifs,
        articles_par_magasin=articles_par_mag,
        distance_totale_km=round(distance, 1),
        temps_estime_min=max(10, int(temps)),
        ordre_visite=ordre,
    )


def _choisir_magasin(
    rayon: str,
    bio_prefere: bool,
    magasins: list[Magasin],
    priorite: str,
) -> Magasin:
    """Choisit le meilleur magasin pour un article."""
    scores: dict[str, float] = {}

    types_preferes = AFFINITE_MAGASIN.get(rayon, ["supermarche"])

    for m in magasins:
        score = 0.0

        # Affinité rayon → type magasin
        if m.type_magasin in types_preferes:
            score += 10

        # Bio
        if bio_prefere and "bio" in m.specialites:
            score += 5 if priorite == "bio" else 3

        # Local
        if "local" in m.specialites:
            score += 2

        # Distance (pénalité)
        if priorite == "temps":
            score -= m.distance_km * 2

        # Qualité
        score += m.note_qualite

        scores[m.nom] = score

    meilleur_nom = max(scores, key=lambda k: scores[k])
    return next(m for m in magasins if m.nom == meilleur_nom)


def generer_deep_links(
    plan: PlanCourses,
    magasins: list[Magasin] | None = None,
) -> dict[str, str]:
    """
    Génère des liens directs vers les drives/sites des magasins.

    Returns:
        Dict magasin_nom → URL
    """
    if magasins is None:
        magasins = MAGASINS_DEFAUT

    mag_urls = {m.nom: m.url_drive for m in magasins if m.url_drive}
    liens = {}

    for nom_mag in plan.ordre_visite:
        if url := mag_urls.get(nom_mag):
            liens[nom_mag] = url

    return liens


__all__ = [
    "Magasin",
    "ArticleMagasin",
    "PlanCourses",
    "MAGASINS_DEFAUT",
    "optimiser_trajet",
    "generer_deep_links",
]
