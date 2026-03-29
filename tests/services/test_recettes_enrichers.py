"""
T6e — Tests service enrichissement de recettes.

Couvre src/services/cuisine/recettes/enrichers.py :
- NutritionEnricher.calculate     : calcul valeurs nutritionnelles
- BioLocalTagger.tag              : détection bio/local
- RecipeClassifier.classify       : classification (rapide, batch, bébé)
- ApplianceDetector.detect        : détection appareils
- RecipeEnricher.enrich           : enrichissement complet
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.services.cuisine.recettes.enrichers import (
    ApplianceDetector,
    BioLocalTagger,
    EnrichmentResult,
    ImportedIngredient,
    ImportedRecipe,
    NutritionEnricher,
    RecipeClassifier,
    RecipeEnricher,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


def _recette_basique() -> ImportedRecipe:
    return ImportedRecipe(
        nom="Poulet rôti",
        temps_preparation=15,
        temps_cuisson=45,
        portions=4,
        ingredients=[
            ImportedIngredient(nom="poulet", quantite=1200, unite="g"),
            ImportedIngredient(nom="tomate", quantite=200, unite="g"),
            ImportedIngredient(nom="riz", quantite=200, unite="g"),
        ],
        etapes=["Préchauffer le four.", "Rôtir le poulet pendant 45 minutes."],
    )


def _recette_rapide_bio() -> ImportedRecipe:
    return ImportedRecipe(
        nom="Salade bio",
        temps_preparation=10,
        temps_cuisson=0,
        portions=2,
        ingredients=[
            ImportedIngredient(nom="salade bio", quantite=100, unite="g"),
            ImportedIngredient(nom="tomates bio", quantite=150, unite="g"),
        ],
        etapes=["Mélanger les ingrédients."],
    )


# ═══════════════════════════════════════════════════════════
# TESTS — NutritionEnricher
# ═══════════════════════════════════════════════════════════


class TestNutritionEnricher:
    """Tests NutritionEnricher.calculate()."""

    def test_recette_sans_ingredients_retourne_null(self):
        """Recette sans ingrédients → tous None."""
        enricher = NutritionEnricher()
        recette = ImportedRecipe(nom="Vide", portions=4)
        result = enricher.calculate(recette)

        assert result["calories"] is None
        assert result["proteines"] is None

    def test_recette_sans_portions_retourne_null(self):
        """Recette avec portions=0 → tous None (évite division par zéro)."""
        enricher = NutritionEnricher()
        recette = ImportedRecipe(
            nom="Sans portions",
            portions=0,
            ingredients=[ImportedIngredient(nom="poulet", quantite=200, unite="g")],
        )
        result = enricher.calculate(recette)
        assert result["calories"] is None

    def test_recette_avec_ingredients_connus(self):
        """Recette avec ingrédients de la table → calories calculées."""
        # Patcher la table nutrition pour éviter dépendance fichier
        table_mock = {
            "poulet": {"calories": 165, "proteines": 31, "lipides": 3.6, "glucides": 0},
            "riz": {"calories": 130, "proteines": 2.7, "lipides": 0.3, "glucides": 28},
        }
        enricher = NutritionEnricher()
        enricher.table_nutrition = table_mock

        recette = ImportedRecipe(
            nom="Poulet riz",
            portions=4,
            ingredients=[
                ImportedIngredient(nom="poulet", quantite=400, unite="g"),
                ImportedIngredient(nom="riz", quantite=200, unite="g"),
            ],
        )
        result = enricher.calculate(recette)

        # Calories par portion = (165*400/100 + 130*200/100) / 4 = (660 + 260) / 4 = 230
        assert result["calories"] is not None
        assert result["calories"] == 230


# ═══════════════════════════════════════════════════════════
# TESTS — BioLocalTagger
# ═══════════════════════════════════════════════════════════


class TestBioLocalTagger:
    """Tests BioLocalTagger.tag()."""

    def test_recette_sans_ingredients_retourne_false(self):
        """Recette vide → non bio, non local."""
        tagger = BioLocalTagger()
        recette = ImportedRecipe(nom="Vide")
        result = tagger.tag(recette)

        assert result["est_bio"] is False
        assert result["est_local"] is False
        assert result["score_bio"] == 0

    def test_ingredients_bio_detectes(self):
        """Ingrédients avec 'bio' → est_bio True."""
        tagger = BioLocalTagger()
        recette = _recette_rapide_bio()
        result = tagger.tag(recette)

        assert result["est_bio"] is True
        assert result["score_bio"] > 0

    def test_ingredients_locaux_detectes(self):
        """Ingrédients avec 'fermier' → local True."""
        tagger = BioLocalTagger()
        recette = ImportedRecipe(
            nom="Poulet fermier",
            portions=4,
            ingredients=[ImportedIngredient(nom="poulet fermier", quantite=1000, unite="g")],
        )
        result = tagger.tag(recette)
        assert result["est_local"] is True


# ═══════════════════════════════════════════════════════════
# TESTS — RecipeClassifier
# ═══════════════════════════════════════════════════════════


class TestRecipeClassifier:
    """Tests RecipeClassifier.classify()."""

    def test_recette_rapide_detectee(self):
        """Recette ≤30 min totale → est_rapide True."""
        classifier = RecipeClassifier()
        recette = ImportedRecipe(nom="Rapide", temps_preparation=10, temps_cuisson=15)
        result = classifier.classify(recette)
        assert result["est_rapide"] is True

    def test_recette_longue_non_rapide(self):
        """Recette >30 min → est_rapide False."""
        classifier = RecipeClassifier()
        recette = ImportedRecipe(nom="Longue", temps_preparation=20, temps_cuisson=60)
        result = classifier.classify(recette)
        assert result["est_rapide"] is False

    def test_recette_batch_grandes_portions(self):
        """Recette ≥6 portions → compatible_batch True."""
        classifier = RecipeClassifier()
        recette = ImportedRecipe(nom="Batch", portions=8)
        result = classifier.classify(recette)
        assert result["compatible_batch"] is True

    def test_recette_equilibree(self):
        """Féculents + protéines + légumes → est_equilibre True."""
        classifier = RecipeClassifier()
        recette = ImportedRecipe(
            nom="Équilibré",
            ingredients=[
                ImportedIngredient(nom="riz", quantite=200, unite="g"),
                ImportedIngredient(nom="poulet", quantite=300, unite="g"),
                ImportedIngredient(nom="tomate", quantite=150, unite="g"),
            ],
        )
        result = classifier.classify(recette)
        assert result["est_equilibre"] is True

    def test_recette_sans_ingredients_non_equilibree(self):
        """Recette vide → est_equilibre False."""
        classifier = RecipeClassifier()
        recette = ImportedRecipe(nom="Vide")
        result = classifier.classify(recette)
        assert result["est_equilibre"] is False


# ═══════════════════════════════════════════════════════════
# TESTS — ApplianceDetector
# ═══════════════════════════════════════════════════════════


class TestApplianceDetector:
    """Tests ApplianceDetector.detect()."""

    def test_cookeo_mentionne_detecte(self):
        """Étapes mentionnant 'cookeo' → compatible_cookeo True."""
        detector = ApplianceDetector()
        recette = ImportedRecipe(
            nom="Soupe cookeo",
            etapes=["Mettre dans le cookeo pendant 15 minutes."],
        )
        result = detector.detect(recette)
        assert result["compatible_cookeo"] is True

    def test_airfryer_heuristique(self):
        """Recette four-grillé courte → compatible_airfryer True."""
        detector = ApplianceDetector()
        recette = ImportedRecipe(
            nom="Frites croustillantes",
            temps_cuisson=20,
            etapes=["Cuire au four. Griller jusqu'à ce que ce soit croustillant."],
        )
        result = detector.detect(recette)
        assert result["compatible_airfryer"] is True

    def test_recette_standard_pas_appareils(self):
        """Recette classique → aucun appareil détecté."""
        detector = ApplianceDetector()
        recette = ImportedRecipe(
            nom="Recette classique",
            temps_cuisson=60,
            etapes=["Préparer les ingrédients.", "Cuire à feu doux."],
        )
        result = detector.detect(recette)
        assert result["compatible_monsieur_cuisine"] is False
        assert result["compatible_airfryer"] is False


# ═══════════════════════════════════════════════════════════
# TESTS — RecipeEnricher (enrichissement complet)
# ═══════════════════════════════════════════════════════════


class TestRecipeEnricher:
    """Tests RecipeEnricher.enrich() — enrichissement complet."""

    def test_enrich_retourne_enrichment_result(self):
        """enrich() retourne un EnrichmentResult."""
        enricher = RecipeEnricher()
        recette = _recette_basique()

        result = enricher.enrich(recette)

        assert isinstance(result, EnrichmentResult)

    def test_enrich_recette_rapide(self):
        """Recette ≤30 min → est_rapide True dans le résultat."""
        enricher = RecipeEnricher()
        recette = ImportedRecipe(
            nom="Rapide",
            temps_preparation=5,
            temps_cuisson=10,
        )
        result = enricher.enrich(recette)
        assert result.est_rapide is True

    def test_enrich_recette_bio(self):
        """Recette avec ingrédients bio → est_bio True."""
        enricher = RecipeEnricher()
        recette = _recette_rapide_bio()
        result = enricher.enrich(recette)
        assert result.est_bio is True
