"""
Service de faisabilité — Score de réalisabilité des recettes depuis le stock.

Croise RecetteIngredient × ArticleInventaire pour calculer
le pourcentage d'ingrédients disponibles par recette.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta

from src.core.decorators import avec_cache, avec_session_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class IngredientStatus:
    """Statut d'un ingrédient pour une recette."""

    nom: str
    requis: float
    unite: str
    en_stock: float
    disponible: bool
    jours_avant_peremption: int | None = None
    optionnel: bool = False


@dataclass
class ScoreFaisabilite:
    """Score de faisabilité d'une recette."""

    recette_id: int
    recette_nom: str
    score: float  # 0.0 à 1.0
    nb_ingredients_total: int
    nb_ingredients_disponibles: int
    nb_ingredients_manquants: int
    ingredients_manquants: list[IngredientStatus] = field(default_factory=list)
    ingredients_disponibles: list[IngredientStatus] = field(default_factory=list)
    ingredients_urgents: list[IngredientStatus] = field(default_factory=list)
    temps_total: int = 0

    @property
    def tier(self) -> str:
        """Classifie la faisabilité en tiers."""
        if self.score >= 1.0:
            return "complet"
        if self.score >= 0.8:
            return "quasi_complet"
        if self.score >= 0.5:
            return "partiel"
        return "insuffisant"

    @property
    def label_tier(self) -> str:
        """Label français du tier."""
        labels = {
            "complet": "🟢 100% réalisable",
            "quasi_complet": "🟡 Presque complet",
            "partiel": "🟠 Courses légères",
            "insuffisant": "🔴 Courses nécessaires",
        }
        return labels.get(self.tier, "❓ Inconnu")


@dataclass
class SuggestionRepasStock:
    """Suggestion de repas basée sur le stock."""

    faisabilite: ScoreFaisabilite
    raison: str
    priorite_antigaspi: float = 0.0  # bonus si utilise produits urgents


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


@avec_session_db
def calculer_faisabilite(recette_id: int, *, db) -> ScoreFaisabilite | None:
    """
    Calcule le score de faisabilité d'une recette vis-à-vis du stock actuel.

    Returns:
        ScoreFaisabilite ou None si recette introuvable
    """
    from src.core.models.inventaire import ArticleInventaire
    from src.core.models.recettes import Recette, RecetteIngredient

    recette = db.query(Recette).filter(Recette.id == recette_id).first()
    if not recette:
        return None

    # Charger tous les ingrédients de la recette avec jointure
    ri_list = db.query(RecetteIngredient).filter(RecetteIngredient.recette_id == recette_id).all()

    if not ri_list:
        return ScoreFaisabilite(
            recette_id=recette_id,
            recette_nom=recette.nom,
            score=1.0,
            nb_ingredients_total=0,
            nb_ingredients_disponibles=0,
            nb_ingredients_manquants=0,
            temps_total=recette.temps_preparation + recette.temps_cuisson,
        )

    today = date.today()
    disponibles: list[IngredientStatus] = []
    manquants: list[IngredientStatus] = []
    urgents: list[IngredientStatus] = []

    for ri in ri_list:
        ingredient = ri.ingredient
        nom = ingredient.nom if ingredient else f"Ingrédient #{ri.ingredient_id}"

        # Chercher dans l'inventaire
        stock = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.ingredient_id == ri.ingredient_id)
            .first()
        )

        en_stock = stock.quantite if stock else 0.0
        jours_peremption = None
        if stock and stock.date_peremption:
            jours_peremption = (stock.date_peremption - today).days

        status = IngredientStatus(
            nom=nom,
            requis=ri.quantite,
            unite=ri.unite,
            en_stock=en_stock,
            disponible=en_stock >= ri.quantite,
            jours_avant_peremption=jours_peremption,
            optionnel=ri.optionnel,
        )

        if status.disponible:
            disponibles.append(status)
            if jours_peremption is not None and jours_peremption <= 7:
                urgents.append(status)
        else:
            manquants.append(status)

    # Calcul du score (les optionnels comptent moins)
    total_poids = 0.0
    poids_dispo = 0.0
    for ri in ri_list:
        poids = 0.5 if ri.optionnel else 1.0
        total_poids += poids
        ingredient = ri.ingredient
        nom = ingredient.nom if ingredient else ""
        if any(d.nom == nom and d.disponible for d in disponibles):
            poids_dispo += poids

    score = poids_dispo / total_poids if total_poids > 0 else 0.0

    return ScoreFaisabilite(
        recette_id=recette_id,
        recette_nom=recette.nom,
        score=score,
        nb_ingredients_total=len(ri_list),
        nb_ingredients_disponibles=len(disponibles),
        nb_ingredients_manquants=len([m for m in manquants if not m.optionnel]),
        ingredients_manquants=manquants,
        ingredients_disponibles=disponibles,
        ingredients_urgents=urgents,
        temps_total=recette.temps_preparation + recette.temps_cuisson,
    )


@avec_session_db
def obtenir_recettes_faisables(
    *,
    type_repas: str | None = None,
    temps_max: int | None = None,
    nb_resultats: int = 20,
    db,
) -> list[ScoreFaisabilite]:
    """
    Retourne les recettes triées par faisabilité depuis le stock.

    Args:
        type_repas: Filtrer par type (dejeuner, diner, etc.)
        temps_max: Temps max en minutes
        nb_resultats: Nombre max de résultats

    Returns:
        Liste de ScoreFaisabilite triée par score décroissant
    """
    from src.core.models.recettes import Recette

    query = db.query(Recette)
    if type_repas:
        query = query.filter(Recette.type_repas == type_repas)
    if temps_max:
        query = query.filter((Recette.temps_preparation + Recette.temps_cuisson) <= temps_max)

    recettes = query.limit(200).all()

    resultats = []
    for recette in recettes:
        score = calculer_faisabilite(recette.id)
        if score:
            resultats.append(score)

    # Trier par score décroissant
    resultats.sort(key=lambda s: s.score, reverse=True)
    return resultats[:nb_resultats]


@avec_session_db
def suggerer_repas_stock(
    *,
    type_repas: str | None = None,
    temps_max: int | None = None,
    nb_resultats: int = 5,
    db,
) -> list[SuggestionRepasStock]:
    """
    Suggestions de repas enrichies avec raisons et priorité anti-gaspi.

    Retourne 3 tiers :
    - Tier 1 : 100% faisable
    - Tier 2 : 1-2 ingrédients manquants
    - Tier 3 : courses légères nécessaires
    """
    faisabilites = obtenir_recettes_faisables(
        type_repas=type_repas,
        temps_max=temps_max,
        nb_resultats=nb_resultats * 3,
    )

    suggestions = []
    for f in faisabilites:
        # Calculer bonus anti-gaspi
        bonus_gaspi = sum(
            max(0, 8 - (ing.jours_avant_peremption or 999)) for ing in f.ingredients_urgents
        )

        # Générer raison
        raisons = []
        if f.score >= 1.0:
            raisons.append("Tout en stock !")
        elif f.nb_ingredients_manquants <= 2:
            noms = [m.nom for m in f.ingredients_manquants if not m.optionnel][:2]
            raisons.append(f"Il manque juste : {', '.join(noms)}")

        if f.ingredients_urgents:
            noms_urgents = [u.nom for u in f.ingredients_urgents][:2]
            raisons.append(f"Utilise {', '.join(noms_urgents)} (à consommer vite)")

        suggestions.append(
            SuggestionRepasStock(
                faisabilite=f,
                raison=". ".join(raisons) if raisons else "Suggestion basée sur le stock",
                priorite_antigaspi=bonus_gaspi,
            )
        )

    # Trier par score + bonus anti-gaspi
    suggestions.sort(
        key=lambda s: s.faisabilite.score * 100 + s.priorite_antigaspi,
        reverse=True,
    )
    return suggestions[:nb_resultats]


__all__ = [
    "ScoreFaisabilite",
    "SuggestionRepasStock",
    "IngredientStatus",
    "calculer_faisabilite",
    "obtenir_recettes_faisables",
    "suggerer_repas_stock",
]
