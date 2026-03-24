"""
Tests pour src/services/multimodal.py

Tests pour MultiModalAIService:
- Factory singleton
- Structure des schémas Pydantic (validation des types de données)

Note: Les tests d'IA réels (analyse d'images) nécessitent des clés API actives
et sont exclus des tests unitaires. Focus sur la structure et la validation.
"""

import pytest

from src.services.multimodal import (
    AnalyseNutritionnelle,
    FactureExtraite,
    IngredientExtrait,
    LigneFacture,
    MultiModalAIService,
    RecetteExtraite,
    get_multimodal_service,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Instance du service multimodal."""
    return MultiModalAIService()


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
def test_get_multimodal_service_singleton():
    """Vérifie que la factory retourne un singleton."""
    service1 = get_multimodal_service()
    service2 = get_multimodal_service()
    
    assert isinstance(service1, MultiModalAIService)
    assert service1 is service2  # Singleton via @service_factory


@pytest.mark.unit
def test_multimodal_service_initialization(service):
    """Test initialisation du service."""
    assert service._vision_model == "pixtral-12b-2024-09-18"
    assert service.service_name == "multimodal"
    assert service.cache_prefix == "multimodal"


# ═══════════════════════════════════════════════════════════
# TESTS SCHEMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
def test_ingredient_extrait_schema():
    """Test du schéma IngredientExtrait."""
    ingredient = IngredientExtrait(
        nom="Tomate",
        quantite="200",
        unite="g",
        confiance=0.9
    )
    
    assert ingredient.nom == "Tomate"
    assert ingredient.quantite == "200"
    assert ingredient.unite == "g"
    assert ingredient.confiance == 0.9


@pytest.mark.unit
def test_ingredient_extrait_defaults():
    """Test des valeurs par défaut du schéma IngredientExtrait."""
    ingredient = IngredientExtrait(nom="Sel")
    
    assert ingredient.nom == "Sel"
    assert ingredient.quantite is None
    assert ingredient.unite is None
    assert ingredient.confiance == 0.8  # Valeur par défaut


@pytest.mark.unit
def test_recette_extraite_schema():
    """Test du schéma RecetteExtraite."""
    recette = RecetteExtraite(
        nom="Tarte aux pommes",
        ingredients=[
            IngredientExtrait(nom="Pommes", quantite="3", unite="unités"),
            IngredientExtrait(nom="Sucre", quantite="100", unite="g"),
        ],
        etapes=["Éplucher les pommes", "Préparer la pâte"],
        temps_preparation="20 min",
        difficulte="facile",
        categorie="dessert"
    )
    
    assert recette.nom == "Tarte aux pommes"
    assert len(recette.ingredients) == 2
    assert len(recette.etapes) == 2
    assert recette.difficulte == "facile"
    assert recette.categorie == "dessert"


@pytest.mark.unit
def test_recette_extraite_defaults():
    """Test des valeurs par défaut du schéma RecetteExtraite."""
    recette = RecetteExtraite()
    
    assert recette.nom == "Recette sans nom"
    assert recette.ingredients == []
    assert recette.etapes == []
    assert recette.temps_preparation is None


@pytest.mark.unit
def test_ligne_facture_schema():
    """Test du schéma LigneFacture."""
    ligne = LigneFacture(
        description="Pain complet",
        quantite=2,
        prix_unitaire=1.50,
        prix_total=3.00
    )
    
    assert ligne.description == "Pain complet"
    assert ligne.quantite == 2
    assert ligne.prix_unitaire == 1.50
    assert ligne.prix_total == 3.00


@pytest.mark.unit
def test_facture_extraite_schema():
    """Test du schéma FactureExtraite."""
    facture = FactureExtraite(
        magasin="Carrefour",
        date="01/01/2024",
        lignes=[
            LigneFacture(description="Pain", quantite=1, prix_total=1.5),
            LigneFacture(description="Lait", quantite=2, prix_total=2.8),
        ],
        total=4.30
    )
    
    assert facture.magasin == "Carrefour"
    assert facture.date == "01/01/2024"
    assert len(facture.lignes) == 2
    assert facture.total == 4.30


@pytest.mark.unit
def test_facture_extraite_defaults():
    """Test des valeurs par défaut du schéma FactureExtraite."""
    facture = FactureExtraite()
    
    assert facture.magasin is None
    assert facture.lignes == []
    assert facture.total is None


@pytest.mark.unit
def test_analyse_nutritionnelle_schema():
    """Test du schéma AnalyseNutritionnelle."""
    analyse = AnalyseNutritionnelle(
        description="Salade César",
        calories_estimees=350,
        proteines_g=25.0,
        glucides_g=15.0,
        lipides_g=20.0,
        fibres_g=5.0,
        portion_estimee="300g",
        ingredients_detectes=["Poulet", "Laitue", "Parmesan"],
        equilibre="Bien équilibré",
        conseils=["Réduire la sauce", "Ajouter des légumes"]
    )
    
    assert analyse.description == "Salade César"
    assert analyse.calories_estimees == 350
    assert analyse.proteines_g == 25.0
    assert analyse.glucides_g == 15.0
    assert analyse.lipides_g == 20.0
    assert analyse.fibres_g == 5.0
    assert len(analyse.ingredients_detectes) == 3
    assert analyse.equilibre == "Bien équilibré"
    assert len(analyse.conseils) == 2


@pytest.mark.unit
def test_analyse_nutritionnelle_defaults():
    """Test des valeurs par défaut du schéma AnalyseNutritionnelle."""
    analyse = AnalyseNutritionnelle(description="Plat mystère")
    
    assert analyse.description == "Plat mystère"
    assert analyse.calories_estimees == 0
    assert analyse.proteines_g is None
    assert analyse.ingredients_detectes == []
    assert analyse.conseils == []


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION PYDANTIC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
def test_ingredient_confiance_range_validation():
    """Test que la confiance reste dans [0, 1]."""
    from pydantic import ValidationError
    
    # Confiance valide
    ingredient = IngredientExtrait(nom="Sel", confiance=0.5)
    assert 0 <= ingredient.confiance <= 1
    
    # Confiance invalide (hors limites) — Pydantic devrait lever une erreur
    with pytest.raises(ValidationError):
        IngredientExtrait(nom="Sel", confiance=1.5)
    
    with pytest.raises(ValidationError):
        IngredientExtrait(nom="Sel", confiance=-0.1)
