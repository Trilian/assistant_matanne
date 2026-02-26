"""
Service anti-gaspillage — Score et suggestions pour éviter le gaspillage.

Calcule un score mensuel, propose des recettes utilisant les produits
proches de la date de péremption, et track le gaspillage réel.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta

from src.core.decorators import avec_session_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class ProduitUrgent:
    """Produit en stock proche de la péremption."""

    article_id: int
    nom: str
    quantite: float
    unite: str
    date_peremption: date
    jours_restants: int
    urgence: int  # 1-5 (5=expiré)

    @property
    def emoji_urgence(self) -> str:
        """Emoji représentant le niveau d'urgence."""
        emojis = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "💀"}
        return emojis.get(self.urgence, "❓")


@dataclass
class RecetteAntiGaspi:
    """Recette recommandée pour réduire le gaspillage."""

    recette_id: int
    recette_nom: str
    score_antigaspi: float  # 0-100
    produits_sauves: list[str]
    temps_total: int
    nb_portions: int


@dataclass
class ScoreMensuelAntiGaspi:
    """Score anti-gaspillage mensuel pour gamification."""

    mois: str
    kg_sauves_estime: float
    nb_recettes_antigaspi: int
    nb_produits_expires: int
    nb_produits_consommes_a_temps: int
    taux_reussite: float  # 0-100%
    badge: str
    badge_emoji: str


# Badges et seuils de gamification
BADGES_ANTIGASPI = [
    (90, "Zéro Déchet", "🏆"),
    (75, "Éco-Champion", "🏅"),
    (60, "Éco-Héros", "🌟"),
    (40, "Éco-Apprenti", "🌱"),
    (0, "En progrès", "🔰"),
]


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


def _calculer_urgence(jours_restants: int) -> int:
    """Calcule le niveau d'urgence (1-5) selon les jours restants."""
    if jours_restants <= 0:
        return 5
    if jours_restants <= 1:
        return 4
    if jours_restants <= 3:
        return 3
    if jours_restants <= 7:
        return 2
    return 1


@avec_session_db
def obtenir_produits_urgents(*, seuil_jours: int = 7, db) -> list[ProduitUrgent]:
    """
    Récupère les produits en stock proches de la péremption.

    Args:
        seuil_jours: Nombre de jours avant péremption (défaut: 7)

    Returns:
        Liste de ProduitUrgent triée par urgence décroissante
    """
    from src.core.models.inventaire import ArticleInventaire

    today = date.today()
    date_limite = today + timedelta(days=seuil_jours)

    articles = (
        db.query(ArticleInventaire)
        .filter(
            ArticleInventaire.date_peremption.isnot(None),
            ArticleInventaire.date_peremption <= date_limite,
            ArticleInventaire.quantite > 0,
        )
        .all()
    )

    produits = []
    for art in articles:
        jours = (art.date_peremption - today).days
        produits.append(
            ProduitUrgent(
                article_id=art.id,
                nom=art.nom,
                quantite=art.quantite,
                unite=art.unite,
                date_peremption=art.date_peremption,
                jours_restants=jours,
                urgence=_calculer_urgence(jours),
            )
        )

    produits.sort(key=lambda p: p.jours_restants)
    return produits


@avec_session_db
def obtenir_recettes_antigaspi(*, nb_resultats: int = 5, db) -> list[RecetteAntiGaspi]:
    """
    Retourne les recettes utilisant le plus de produits proches péremption.

    Cross-match ArticleInventaire (urgent) × RecetteIngredient.
    """
    from src.core.models.inventaire import ArticleInventaire
    from src.core.models.recettes import Recette, RecetteIngredient

    today = date.today()
    date_limite = today + timedelta(days=7)

    # Produits urgents (id → info)
    articles_urgents = (
        db.query(ArticleInventaire)
        .filter(
            ArticleInventaire.date_peremption.isnot(None),
            ArticleInventaire.date_peremption <= date_limite,
            ArticleInventaire.quantite > 0,
        )
        .all()
    )

    if not articles_urgents:
        return []

    ids_ingredients_urgents = {a.ingredient_id: a for a in articles_urgents}

    # Trouver les recettes utilisant ces ingrédients
    ri_matches = (
        db.query(RecetteIngredient)
        .filter(RecetteIngredient.ingredient_id.in_(ids_ingredients_urgents.keys()))
        .all()
    )

    # Grouper par recette
    recette_scores: dict[int, list[str]] = {}
    for ri in ri_matches:
        art = ids_ingredients_urgents[ri.ingredient_id]
        recette_scores.setdefault(ri.recette_id, []).append(art.nom)

    # Charger les recettes et calculer les scores
    resultats = []
    for recette_id, produits_sauves in recette_scores.items():
        recette = db.query(Recette).filter(Recette.id == recette_id).first()
        if not recette:
            continue

        # Score pondéré par nombre de produits urgents utilisés et jours restants
        score = 0.0
        for nom in produits_sauves:
            for art in articles_urgents:
                if art.nom == nom:
                    jours = (art.date_peremption - today).days
                    score += max(1, 8 - jours) * 10  # Plus urgence est haute, plus le score monte
                    break

        resultats.append(
            RecetteAntiGaspi(
                recette_id=recette.id,
                recette_nom=recette.nom,
                score_antigaspi=min(100.0, score),
                produits_sauves=produits_sauves,
                temps_total=recette.temps_preparation + recette.temps_cuisson,
                nb_portions=recette.portions,
            )
        )

    resultats.sort(key=lambda r: r.score_antigaspi, reverse=True)
    return resultats[:nb_resultats]


@avec_session_db
def calculer_score_mensuel(*, mois: date | None = None, db) -> ScoreMensuelAntiGaspi:
    """
    Calcule le score mensuel anti-gaspillage pour la gamification.

    Basé sur le ratio produits consommés à temps vs produits expirés.
    """
    from src.core.models.inventaire import HistoriqueInventaire

    if mois is None:
        mois = date.today().replace(day=1)

    debut_mois = mois.replace(day=1)
    if mois.month == 12:
        fin_mois = mois.replace(year=mois.year + 1, month=1, day=1)
    else:
        fin_mois = mois.replace(month=mois.month + 1, day=1)

    # Compter les modifications d'inventaire du mois
    historique = (
        db.query(HistoriqueInventaire)
        .filter(
            HistoriqueInventaire.date_modification >= debut_mois,
            HistoriqueInventaire.date_modification < fin_mois,
        )
        .all()
    )

    consommes = sum(
        1
        for h in historique
        if h.type_modification == "modification"
        and h.quantite_apres is not None
        and h.quantite_avant is not None
        and h.quantite_apres < h.quantite_avant
    )
    supprimes = sum(1 for h in historique if h.type_modification == "suppression")

    total = consommes + supprimes
    taux = (consommes / total * 100) if total > 0 else 100.0

    # Estimation kg sauvés (estimation grossière: 0.3kg par consommation)
    kg_sauves = consommes * 0.3

    # Badge
    badge_nom = "En progrès"
    badge_emoji = "🔰"
    for seuil, nom, emoji in BADGES_ANTIGASPI:
        if taux >= seuil:
            badge_nom = nom
            badge_emoji = emoji
            break

    mois_str = mois.strftime("%B %Y")

    return ScoreMensuelAntiGaspi(
        mois=mois_str,
        kg_sauves_estime=round(kg_sauves, 1),
        nb_recettes_antigaspi=0,  # TODO: tracker les recettes anti-gaspi cuisinées
        nb_produits_expires=supprimes,
        nb_produits_consommes_a_temps=consommes,
        taux_reussite=round(taux, 1),
        badge=badge_nom,
        badge_emoji=badge_emoji,
    )


__all__ = [
    "ProduitUrgent",
    "RecetteAntiGaspi",
    "ScoreMensuelAntiGaspi",
    "BADGES_ANTIGASPI",
    "obtenir_produits_urgents",
    "obtenir_recettes_antigaspi",
    "calculer_score_mensuel",
]
