"""
Service d'enrichissement des recettes importées.

Calcule automatiquement : nutrition, tags bio/local, classification (rapide, batch,
équilibré), détection appareils (Cookeo, Airfryer, etc.).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.core.logging import obtenir_logger
from src.services.core.base import BaseAIService

logger = obtenir_logger(__name__)


# ═══════════════════════════════════════════════════════════
# Modèles Pydantic
# ═══════════════════════════════════════════════════════════


class ImportedIngredient(BaseModel):
    """Ingrédient importé (avant transformation en DB)."""

    nom: str
    quantite: float | None = None
    unite: str | None = None


class ImportedRecipe(BaseModel):
    """Recette importée (avant enrichissement)."""

    nom: str
    description: str | None = None
    temps_preparation: int = 0
    temps_cuisson: int = 0
    portions: int = 4
    ingredients: list[ImportedIngredient] = []
    etapes: list[str] = []


class EnrichmentResult(BaseModel):
    """Résultat complet de l'enrichissement."""

    # Nutrition
    calories: int | None = None
    proteines: float | None = None
    lipides: float | None = None
    glucides: float | None = None

    # Bio/Local
    est_bio: bool = False
    est_local: bool = False
    score_bio: int = 0
    score_local: int = 0

    # Tags auto
    est_rapide: bool = False
    est_equilibre: bool = False
    compatible_batch: bool = False
    congelable: bool = False
    compatible_bebe: bool = False

    # Robots
    compatible_cookeo: bool = False
    compatible_airfryer: bool = False
    compatible_monsieur_cuisine: bool = False
    compatible_multicooker: bool = False


# ═══════════════════════════════════════════════════════════
# Enrichisseurs
# ═══════════════════════════════════════════════════════════


class NutritionEnricher:
    """Calculateur de valeurs nutritionnelles."""

    def __init__(self):
        self.table_nutrition = self._charger_table_nutrition()

    def _charger_table_nutrition(self) -> dict[str, dict]:
        """Charge la table de référence nutritionnelle."""
        fichier = (
            Path(__file__).parent.parent.parent.parent.parent
            / "data"
            / "reference"
            / "nutrition_table.json"
        )
        if fichier.exists():
            with open(fichier, encoding="utf-8") as f:
                return json.load(f)
        logger.warning("Table nutrition absente, retour dict vide")
        return {}

    def calculate(self, recipe: ImportedRecipe) -> dict[str, float | None]:
        """Calcule nutrition pour 1 portion."""
        if not recipe.ingredients or recipe.portions == 0:
            return {"calories": None, "proteines": None, "lipides": None, "glucides": None}

        total_cals = 0.0
        total_prot = 0.0
        total_lip = 0.0
        total_gluc = 0.0
        matched = 0

        for ing in recipe.ingredients:
            # Matching simple (normalisation lowercase, suppression accents)
            nom_clean = ing.nom.lower().strip()
            for key, data in self.table_nutrition.items():
                if key.lower() in nom_clean or nom_clean in key.lower():
                    # Quantité en grammes (approximation si None)
                    qte_g = ing.quantite or 100.0
                    if ing.unite in ("kg", "l"):
                        qte_g *= 1000
                    elif ing.unite in ("ml", "cl"):
                        qte_g = (ing.quantite or 100.0) * (10 if ing.unite == "cl" else 1)

                    # Calcul proportionnel (valeurs pour 100g)
                    ratio = qte_g / 100.0
                    total_cals += data.get("calories", 0) * ratio
                    total_prot += data.get("proteines", 0) * ratio
                    total_lip += data.get("lipides", 0) * ratio
                    total_gluc += data.get("glucides", 0) * ratio
                    matched += 1
                    break

        if matched == 0:
            return {"calories": None, "proteines": None, "lipides": None, "glucides": None}

        # Par portion
        portions = recipe.portions if recipe.portions > 0 else 4
        return {
            "calories": int(total_cals / portions),
            "proteines": round(total_prot / portions, 1),
            "lipides": round(total_lip / portions, 1),
            "glucides": round(total_gluc / portions, 1),
        }


class BioLocalTagger:
    """Détecteur d'ingrédients bio/locaux."""

    BIO_KEYWORDS = ["bio", "biologique", "ab", "agriculture biologique"]
    LOCAL_KEYWORDS = ["local", "fermier", "aop", "igp", "terroir", "du producteur"]

    def __init__(self):
        self.produits_saison = self._charger_produits_saison()

    def _charger_produits_saison(self) -> dict[str, list[int]]:
        """Charge produits_de_saison.json."""
        fichier = (
            Path(__file__).parent.parent.parent.parent.parent
            / "data"
            / "reference"
            / "produits_de_saison.json"
        )
        if fichier.exists():
            with open(fichier, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    items = data.get("produits", data.get("items", []))
                else:
                    items = data
                return {
                    str(p.get("nom", "")).lower(): list(p.get("mois", []))
                    for p in items
                    if isinstance(p, dict) and p.get("nom")
                }
        return {}

    def tag(self, recipe: ImportedRecipe) -> dict[str, Any]:
        """Calcule scores bio/local."""
        if not recipe.ingredients:
            return {"est_bio": False, "est_local": False, "score_bio": 0, "score_local": 0}

        bio_count = 0
        local_count = 0

        for ing in recipe.ingredients:
            nom_lower = ing.nom.lower()

            # Bio?
            if any(kw in nom_lower for kw in self.BIO_KEYWORDS):
                bio_count += 1

            # Local? (keywords OU produit de saison)
            if any(kw in nom_lower for kw in self.LOCAL_KEYWORDS):
                local_count += 1
            elif any(prod in nom_lower for prod in self.produits_saison.keys()):
                local_count += 1

        total = len(recipe.ingredients)
        score_bio = int((bio_count / total) * 100) if total > 0 else 0
        score_local = int((local_count / total) * 100) if total > 0 else 0

        return {
            "est_bio": score_bio >= 50,
            "est_local": score_local >= 50,
            "score_bio": score_bio,
            "score_local": score_local,
        }


class RecipeClassifier:
    """Classification automatique basée sur règles + IA légère."""

    BATCH_KEYWORDS = ["batch", "à l'avance", "préparer en lot", "pour la semaine", "se conserve"]
    CONGELABLE_KEYWORDS = ["se congèle", "à congeler", "congélation", "peut être congelé"]
    BEBE_FORBIDDEN = ["épices fortes", "piment", "sel ajouté", "sucre ajouté", "miel"]

    def classify(self, recipe: ImportedRecipe) -> dict[str, bool]:
        """Classifie la recette."""
        texte = f"{recipe.nom} {recipe.description or ''} {' '.join(recipe.etapes)}".lower()

        # Rapide ?
        temps_total = recipe.temps_preparation + recipe.temps_cuisson
        est_rapide = temps_total <= 30

        # Batch ?
        compatible_batch = recipe.portions >= 6 or any(kw in texte for kw in self.BATCH_KEYWORDS)

        # Congelable ?
        congelable = any(kw in texte for kw in self.CONGELABLE_KEYWORDS)

        # Bébé ?
        compatible_bebe = not any(kw in texte for kw in self.BEBE_FORBIDDEN)

        # Équilibré ? (heuristique simple : féculents + protéines + légumes)
        ingredients_text = " ".join(i.nom.lower() for i in recipe.ingredients)
        a_feculents = any(
            mot in ingredients_text
            for mot in ["riz", "pâtes", "pomme de terre", "quinoa", "semoule"]
        )
        a_proteines = any(
            mot in ingredients_text
            for mot in ["poulet", "poisson", "viande", "œuf", "lentilles", "pois chiche"]
        )
        a_legumes = any(
            mot in ingredients_text
            for mot in ["tomate", "courgette", "carotte", "brocoli", "épinard", "poivron"]
        )
        est_equilibre = a_feculents and a_proteines and a_legumes

        return {
            "est_rapide": est_rapide,
            "est_equilibre": est_equilibre,
            "compatible_batch": compatible_batch,
            "congelable": congelable,
            "compatible_bebe": compatible_bebe,
        }


class ApplianceDetector:
    """Détection appareils compatibles (Cookeo, Airfryer, etc.)."""

    COOKEO_KEYWORDS = ["cookeo", "mode vapeur", "mode mijotage", "multicuiseur"]
    AIRFRYER_KEYWORDS = ["airfryer", "friteuse sans huile", "air fryer", "friture à l'air"]
    MONSIEUR_CUISINE_KEYWORDS = ["monsieur cuisine", "thermomix", "robot cuiseur"]

    def detect(self, recipe: ImportedRecipe) -> dict[str, bool]:
        """Détecte compatibilité robots."""
        texte = " ".join(recipe.etapes).lower()

        # Détection explicite (keywords)
        compatible_cookeo = any(kw in texte for kw in self.COOKEO_KEYWORDS)
        compatible_airfryer = any(kw in texte for kw in self.AIRFRYER_KEYWORDS)
        compatible_monsieur_cuisine = any(kw in texte for kw in self.MONSIEUR_CUISINE_KEYWORDS)

        # Heuristiques supplémentaires
        if not compatible_airfryer:
            # Airfryer : cuisson courte haute T° + pas de mijotage
            if recipe.temps_cuisson <= 25 and "mijoter" not in texte:
                if any(mot in texte for mot in ["four", "griller", "croustillant", "frire"]):
                    compatible_airfryer = True

        if not compatible_cookeo:
            # Cookeo : mijotage, soupe, riz
            if any(mot in texte for mot in ["mijoter", "soupe", "riz", "ragoût"]):
                compatible_cookeo = True

        compatible_multicooker = compatible_cookeo or compatible_monsieur_cuisine

        return {
            "compatible_cookeo": compatible_cookeo,
            "compatible_airfryer": compatible_airfryer,
            "compatible_monsieur_cuisine": compatible_monsieur_cuisine,
            "compatible_multicooker": compatible_multicooker,
        }


# ═══════════════════════════════════════════════════════════
# Service principal
# ═══════════════════════════════════════════════════════════


class RecipeEnricher(BaseAIService):
    """Service d'enrichissement complet des recettes importées."""

    def __init__(self):
        super().__init__()
        self.nutrition_enricher = NutritionEnricher()
        self.bio_local_tagger = BioLocalTagger()
        self.recipe_classifier = RecipeClassifier()
        self.appliance_detector = ApplianceDetector()

    def enrich(self, recipe: ImportedRecipe) -> EnrichmentResult:
        """Enrichissement complet."""
        logger.info(f"Enrichissement de la recette : {recipe.nom}")

        try:
            nutrition = self.nutrition_enricher.calculate(recipe)
            bio_local = self.bio_local_tagger.tag(recipe)
            auto_tags = self.recipe_classifier.classify(recipe)
            appliances = self.appliance_detector.detect(recipe)

            result = EnrichmentResult(
                **nutrition,
                **bio_local,
                **auto_tags,
                **appliances,
            )

            logger.info(f"Enrichissement réussi : {result.model_dump()}")
            return result

        except Exception as e:
            logger.error(f"Erreur enrichissement : {e}", exc_info=True)
            return EnrichmentResult()


# ═══════════════════════════════════════════════════════════
# Factory
# ═══════════════════════════════════════════════════════════


def get_recipe_enricher() -> RecipeEnricher:
    """Factory singleton."""
    return RecipeEnricher()
