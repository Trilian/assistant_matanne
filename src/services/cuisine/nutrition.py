"""
Service d'enrichissement nutritionnel des recettes.

Utilise OpenFoodFacts pour estimer les valeurs nutritionnelles
à partir des ingrédients d'une recette.
"""

import logging
import re
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models.recettes import Ingredient, Recette, RecetteIngredient
from src.services.core.registry import service_factory
from src.services.integrations.produit import (
    OpenFoodFactsService,
    ProduitOpenFoodFacts,
    obtenir_service_openfoodfacts,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONVERSION UNITÉS → GRAMMES (approximations)
# ═══════════════════════════════════════════════════════════

CONVERSION_GRAMMES: dict[str, float] = {
    "g": 1.0,
    "kg": 1000.0,
    "ml": 1.0,
    "cl": 10.0,
    "dl": 100.0,
    "l": 1000.0,
    "litre": 1000.0,
    "litres": 1000.0,
    "pièce": 100.0,
    "pièces": 100.0,
    "pcs": 100.0,
    "unité": 100.0,
    "unités": 100.0,
    "c. à soupe": 15.0,
    "c. à café": 5.0,
    "cas": 15.0,
    "cac": 5.0,
    "cuillère à soupe": 15.0,
    "cuillère à café": 5.0,
    "gousse": 5.0,
    "gousses": 5.0,
    "tranche": 30.0,
    "tranches": 30.0,
    "feuille": 3.0,
    "feuilles": 3.0,
    "botte": 150.0,
    "bottes": 150.0,
    "bouquet": 30.0,
    "branche": 10.0,
    "branches": 10.0,
    "pincée": 1.0,
    "pincées": 1.0,
    "verre": 200.0,
    "tasse": 250.0,
    "bol": 300.0,
    "sachet": 10.0,
    "sachets": 10.0,
    "boîte": 400.0,
    "pot": 125.0,
}

BIO_KEYWORDS = {"bio", "agriculture biologique", "ab", "organic", "eu organic"}
LOCAL_KEYWORDS = {"france", "français", "française", "produit en france", "origine france"}


def _convertir_en_grammes(quantite: float, unite: str) -> float:
    """Convertit une quantité dans une unité donnée en grammes."""
    unite_lower = unite.lower().strip()
    factor = CONVERSION_GRAMMES.get(unite_lower, 100.0)
    return quantite * factor


class NutritionEnrichmentService:
    """Service d'enrichissement nutritionnel via OpenFoodFacts."""

    def __init__(self):
        self.off_service: OpenFoodFactsService = obtenir_service_openfoodfacts()

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def enrichir_recette(
        self, recette_id: int, db: Session | None = None
    ) -> dict[str, Any] | None:
        """Enrichit une recette avec les données nutritionnelles OpenFoodFacts.

        Pour chaque ingrédient de la recette :
        1. Recherche sur OpenFoodFacts par nom
        2. Calcule la contribution nutritionnelle (proportionnelle à la quantité)
        3. Somme les contributions
        4. Divise par le nombre de portions

        Met à jour les champs calories, proteines, lipides, glucides,
        score_bio, score_local sur la recette.

        Returns:
            Dict avec les totaux calculés, ou None si échec
        """
        assert db is not None

        recette = db.query(Recette).filter(Recette.id == recette_id).first()
        if not recette:
            logger.warning(f"Recette {recette_id} non trouvée")
            return None

        ingredients = (
            db.query(RecetteIngredient)
            .filter(RecetteIngredient.recette_id == recette_id)
            .all()
        )

        if not ingredients:
            logger.info(f"Recette {recette_id} sans ingrédients, enrichissement ignoré")
            return None

        total_cal = 0.0
        total_prot = 0.0
        total_lip = 0.0
        total_gluc = 0.0
        nb_bio = 0
        nb_local = 0
        nb_enrichis = 0
        details = []

        for ri in ingredients:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ri.ingredient_id).first()
            if not ingredient:
                continue

            # Chercher sur OpenFoodFacts par nom
            produits = self.off_service.rechercher_par_nom(ingredient.nom, limite=1)
            if not produits:
                details.append({"ingredient": ingredient.nom, "status": "non_trouvé"})
                continue

            produit: ProduitOpenFoodFacts = produits[0]
            if not produit.nutrition:
                details.append({"ingredient": ingredient.nom, "status": "pas_de_nutrition"})
                continue

            # Convertir la quantité en grammes
            grammes = _convertir_en_grammes(ri.quantite, ri.unite)

            # Calculer la contribution (nutrition est pour 100g)
            ratio = grammes / 100.0
            nutr = produit.nutrition

            cal = (nutr.energie_kcal or 0) * ratio
            prot = (nutr.proteines_g or 0) * ratio
            lip = (nutr.lipides_g or 0) * ratio
            gluc = (nutr.glucides_g or 0) * ratio

            total_cal += cal
            total_prot += prot
            total_lip += lip
            total_gluc += gluc
            nb_enrichis += 1

            # Vérifier bio/local
            labels_lower = {l.lower() for l in produit.labels}
            if labels_lower & BIO_KEYWORDS:
                nb_bio += 1
            origine_lower = (produit.origine or "").lower()
            if any(kw in origine_lower for kw in LOCAL_KEYWORDS):
                nb_local += 1

            details.append({
                "ingredient": ingredient.nom,
                "status": "enrichi",
                "calories": round(cal, 1),
                "nutriscore": nutr.nutriscore,
            })

        if nb_enrichis == 0:
            logger.info(f"Recette {recette_id}: aucun ingrédient enrichi")
            return None

        # Diviser par portions
        portions = recette.portions or 1
        recette.calories = round(total_cal / portions)
        recette.proteines = round(total_prot / portions, 1)
        recette.lipides = round(total_lip / portions, 1)
        recette.glucides = round(total_gluc / portions, 1)

        # Scores bio/local
        nb_total = len(ingredients)
        recette.score_bio = round((nb_bio / nb_total) * 100) if nb_total > 0 else 0
        recette.score_local = round((nb_local / nb_total) * 100) if nb_total > 0 else 0
        recette.est_bio = recette.score_bio >= 80
        recette.est_local = recette.score_local >= 80

        db.commit()

        logger.info(
            f"Recette {recette_id} enrichie: {recette.calories} kcal/portion, "
            f"{nb_enrichis}/{nb_total} ingrédients enrichis"
        )

        return {
            "recette_id": recette_id,
            "calories": recette.calories,
            "proteines": recette.proteines,
            "lipides": recette.lipides,
            "glucides": recette.glucides,
            "score_bio": recette.score_bio,
            "score_local": recette.score_local,
            "ingredients_enrichis": nb_enrichis,
            "ingredients_total": nb_total,
            "details": details,
        }

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def enrichir_batch(
        self, limite: int = 50, db: Session | None = None
    ) -> dict[str, Any] | None:
        """Enrichit en batch les recettes qui n'ont pas encore de données nutritionnelles.

        Args:
            limite: Nombre max de recettes à traiter
        """
        assert db is not None

        # Trouver les recettes sans calories et avec des ingrédients
        from sqlalchemy import exists, select

        subq = select(RecetteIngredient.recette_id).correlate(Recette)
        recettes = (
            db.query(Recette)
            .filter(
                Recette.calories.is_(None),
                exists(subq.where(RecetteIngredient.recette_id == Recette.id)),
            )
            .limit(limite)
            .all()
        )

        resultats = {"enrichies": 0, "echouees": 0, "total": len(recettes)}

        for recette in recettes:
            try:
                resultat = self.enrichir_recette(recette.id)
                if resultat:
                    resultats["enrichies"] += 1
                else:
                    resultats["echouees"] += 1
            except Exception as e:
                logger.error(f"Erreur enrichissement recette {recette.id}: {e}")
                resultats["echouees"] += 1

        return resultats

    def estimer_nutriscore(self, recette_id: int) -> str | None:
        """Estime un Nutri-Score approximatif pour une recette.

        Basé sur les calories par portion:
        - A: < 200 kcal
        - B: 200-350 kcal
        - C: 350-500 kcal
        - D: 500-700 kcal
        - E: > 700 kcal
        """
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as db:
            recette = db.query(Recette).filter(Recette.id == recette_id).first()
            if not recette or recette.calories is None:
                return None

            cal = recette.calories
            if cal < 200:
                return "A"
            elif cal < 350:
                return "B"
            elif cal < 500:
                return "C"
            elif cal < 700:
                return "D"
            else:
                return "E"


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════


@service_factory("nutrition_enrichment", tags={"cuisine", "nutrition"})
def obtenir_service_nutrition() -> NutritionEnrichmentService:
    """Factory pour le service d'enrichissement nutritionnel."""
    return NutritionEnrichmentService()
