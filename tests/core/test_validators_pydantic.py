"""
Tests pour src/core/validators_pydantic.py
"""
import pytest
from datetime import date, timedelta
from pydantic import ValidationError


class TestIngredientInput:
    """Tests pour IngredientInput."""

    def test_ingredient_minimal(self):
        """Ingrédient avec nom seulement."""
        from src.core.validators_pydantic import IngredientInput
        
        ing = IngredientInput(nom="farine")
        assert ing.nom == "Farine"  # Capitalized
        assert ing.quantite is None
        assert ing.unite is None

    def test_ingredient_complet(self):
        """Ingrédient avec tous les champs."""
        from src.core.validators_pydantic import IngredientInput
        
        ing = IngredientInput(nom="sucre", quantite=200, unite="g")
        assert ing.nom == "Sucre"
        assert ing.quantite == 200
        assert ing.unite == "g"

    def test_ingredient_nom_empty_fails(self):
        """Nom vide échoue."""
        from src.core.validators_pydantic import IngredientInput
        
        with pytest.raises(ValidationError):
            IngredientInput(nom="")

    def test_ingredient_nom_nettoye(self):
        """Nom avec espaces est nettoyé."""
        from src.core.validators_pydantic import IngredientInput
        
        ing = IngredientInput(nom="  pomme de terre  ")
        assert ing.nom == "Pomme de terre"

    def test_ingredient_quantite_negative_fails(self):
        """Quantité négative échoue."""
        from src.core.validators_pydantic import IngredientInput
        
        with pytest.raises(ValidationError):
            IngredientInput(nom="test", quantite=-1)


class TestEtapeInput:
    """Tests pour EtapeInput."""

    def test_etape_avec_numero(self):
        """Étape avec numero."""
        from src.core.validators_pydantic import EtapeInput
        
        etape = EtapeInput(numero=1, description="Mélanger")
        assert etape.numero == 1
        assert etape.description == "Mélanger"

    def test_etape_avec_ordre(self):
        """Étape avec ordre (alias)."""
        from src.core.validators_pydantic import EtapeInput
        
        etape = EtapeInput(ordre=2, description="Cuire")
        assert etape.numero == 2  # Ordre copié vers numero

    def test_etape_sans_numero_ni_ordre_fails(self):
        """Étape sans numero ni ordre échoue."""
        from src.core.validators_pydantic import EtapeInput
        
        with pytest.raises(ValidationError):
            EtapeInput(description="Test")

    def test_etape_description_nettoyee(self):
        """Description avec espaces est nettoyée."""
        from src.core.validators_pydantic import EtapeInput
        
        etape = EtapeInput(numero=1, description="  Bien mélanger  ")
        assert etape.description == "Bien mélanger"

    def test_etape_duree_valide(self):
        """Durée valide."""
        from src.core.validators_pydantic import EtapeInput
        
        etape = EtapeInput(numero=1, description="Cuire", duree=30)
        assert etape.duree == 30


class TestRecetteInput:
    """Tests pour RecetteInput."""

    @pytest.fixture
    def recette_data(self):
        """Données de recette valide."""
        return {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "type_repas": "dessert",
            "ingredients": [{"nom": "pomme", "quantite": 500, "unite": "g"}],
            "etapes": [{"numero": 1, "description": "Éplucher les pommes"}],
        }

    def test_recette_valide(self, recette_data):
        """Recette valide."""
        from src.core.validators_pydantic import RecetteInput
        
        recette = RecetteInput(**recette_data)
        assert recette.nom == "Tarte aux pommes"
        assert recette.portions == 4  # Default

    def test_recette_difficulte_valide(self, recette_data):
        """Difficulté valide."""
        from src.core.validators_pydantic import RecetteInput
        
        recette_data["difficulte"] = "facile"
        recette = RecetteInput(**recette_data)
        assert recette.difficulte == "facile"

    def test_recette_difficulte_invalide(self, recette_data):
        """Difficulté invalide échoue."""
        from src.core.validators_pydantic import RecetteInput
        
        recette_data["difficulte"] = "expert"
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)

    def test_recette_type_repas_invalide(self, recette_data):
        """Type repas invalide échoue."""
        from src.core.validators_pydantic import RecetteInput
        
        recette_data["type_repas"] = "inconnu"
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)

    def test_recette_saison_valide(self, recette_data):
        """Saison valide."""
        from src.core.validators_pydantic import RecetteInput
        
        recette_data["saison"] = "automne"
        recette = RecetteInput(**recette_data)
        assert recette.saison == "automne"

    def test_recette_temps_total_trop_long(self, recette_data):
        """Temps total > 24h échoue."""
        from src.core.validators_pydantic import RecetteInput
        
        recette_data["temps_preparation"] = 1000
        recette_data["temps_cuisson"] = 500  # Total = 1500 > 1440
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)

    def test_recette_sans_ingredients_fails(self, recette_data):
        """Recette sans ingrédients échoue."""
        from src.core.validators_pydantic import RecetteInput
        
        recette_data["ingredients"] = []
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)

    def test_recette_nom_court_fails(self, recette_data):
        """Nom trop court échoue."""
        from src.core.validators_pydantic import RecetteInput
        
        recette_data["nom"] = "A"
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)


class TestIngredientStockInput:
    """Tests pour IngredientStockInput."""

    def test_stock_valide(self):
        """Stock valide."""
        from src.core.validators_pydantic import IngredientStockInput
        
        stock = IngredientStockInput(
            nom="Lait",
            quantite=2.0,
            unite="L"
        )
        assert stock.nom == "Lait"
        assert stock.quantite == 2.0

    def test_stock_avec_expiration(self):
        """Stock avec date expiration."""
        from src.core.validators_pydantic import IngredientStockInput
        
        exp_date = date.today() + timedelta(days=7)
        stock = IngredientStockInput(
            nom="Yaourt",
            quantite=4,
            unite="pièces",
            date_expiration=exp_date
        )
        assert stock.date_expiration == exp_date

    def test_stock_quantite_zero_fails(self):
        """Quantité < 0.01 échoue."""
        from src.core.validators_pydantic import IngredientStockInput
        
        with pytest.raises(ValidationError):
            IngredientStockInput(nom="Test", quantite=0, unite="kg")
