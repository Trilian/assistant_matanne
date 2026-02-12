"""
Tests approfondis pour src/utils/validators/
Objectif: Atteindre 80%+ de couverture

Couvre:
- common.py: is_valid_email, is_valid_phone, clamp, validate_range, validate_string_length, etc.
- dates.py: validate_date_range, is_future_date, is_past_date, validate_expiry_date, days_until
- food.py: validate_recipe, validate_ingredient, validate_inventory_item, validate_shopping_item, validate_meal
"""

import pytest
from datetime import date, timedelta


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COMMON VALIDATORS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIsValidEmail:
    """Tests pour is_valid_email"""
    
    def test_email_valide_simple(self):
        """Test email simple valide"""
        from src.utils.validators.common import is_valid_email
        
        assert is_valid_email("test@example.com") is True
    
    def test_email_valide_avec_points(self):
        """Test email avec points"""
        from src.utils.validators.common import is_valid_email
        
        assert is_valid_email("jean.dupont@example.com") is True
    
    def test_email_valide_avec_plus(self):
        """Test email avec +"""
        from src.utils.validators.common import is_valid_email
        
        assert is_valid_email("test+tag@example.com") is True
    
    def test_email_valide_sous_domaine(self):
        """Test email avec sous-domaine"""
        from src.utils.validators.common import is_valid_email
        
        assert is_valid_email("test@mail.example.com") is True
    
    def test_email_invalide_sans_arobase(self):
        """Test email sans @"""
        from src.utils.validators.common import is_valid_email
        
        assert is_valid_email("testexample.com") is False
    
    def test_email_invalide_sans_domaine(self):
        """Test email sans domaine"""
        from src.utils.validators.common import is_valid_email
        
        assert is_valid_email("test@") is False
    
    def test_email_invalide_sans_extension(self):
        """Test email sans extension"""
        from src.utils.validators.common import is_valid_email
        
        assert is_valid_email("test@example") is False
    
    def test_email_invalide_vide(self):
        """Test email vide"""
        from src.utils.validators.common import is_valid_email
        
        assert is_valid_email("") is False


class TestIsValidPhone:
    """Tests pour is_valid_phone"""
    
    def test_phone_valide_fr_classique(self):
        """Test numÃ©ro FR classique"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("0612345678") is True
    
    def test_phone_valide_fr_avec_espaces(self):
        """Test numÃ©ro FR avec espaces"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("06 12 34 56 78") is True
    
    def test_phone_valide_fr_avec_points(self):
        """Test numÃ©ro FR avec points"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("06.12.34.56.78") is True
    
    def test_phone_valide_fr_avec_tirets(self):
        """Test numÃ©ro FR avec tirets"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("06-12-34-56-78") is True
    
    def test_phone_valide_fr_avec_indicatif_33(self):
        """Test numÃ©ro FR avec +33"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("+33612345678") is True
    
    def test_phone_valide_fr_avec_0033(self):
        """Test numÃ©ro FR avec 0033"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("0033612345678") is True
    
    def test_phone_invalide_trop_court(self):
        """Test numÃ©ro trop court"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("061234") is False
    
    def test_phone_invalide_lettres(self):
        """Test numÃ©ro avec lettres"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("06ABCDEFGH") is False
    
    def test_phone_autre_pays_false(self):
        """Test autre pays non supportÃ©"""
        from src.utils.validators.common import is_valid_phone
        
        assert is_valid_phone("0612345678", country="US") is False


class TestClamp:
    """Tests pour clamp"""
    
    def test_clamp_valeur_dans_range(self):
        """Test valeur dans range"""
        from src.utils.validators.common import clamp
        
        assert clamp(5, 0, 10) == 5
    
    def test_clamp_valeur_au_dessus_max(self):
        """Test valeur au-dessus du max"""
        from src.utils.validators.common import clamp
        
        assert clamp(15, 0, 10) == 10
    
    def test_clamp_valeur_en_dessous_min(self):
        """Test valeur en-dessous du min"""
        from src.utils.validators.common import clamp
        
        assert clamp(-5, 0, 10) == 0
    
    def test_clamp_valeur_egale_min(self):
        """Test valeur Ã©gale min"""
        from src.utils.validators.common import clamp
        
        assert clamp(0, 0, 10) == 0
    
    def test_clamp_valeur_egale_max(self):
        """Test valeur Ã©gale max"""
        from src.utils.validators.common import clamp
        
        assert clamp(10, 0, 10) == 10
    
    def test_clamp_floats(self):
        """Test avec floats"""
        from src.utils.validators.common import clamp
        
        assert clamp(0.5, 0.0, 1.0) == 0.5
        assert clamp(1.5, 0.0, 1.0) == 1.0
    
    def test_clamp_negatifs(self):
        """Test avec valeurs nÃ©gatives"""
        from src.utils.validators.common import clamp
        
        assert clamp(-15, -10, -5) == -10
        assert clamp(-3, -10, -5) == -5


class TestValidateRange:
    """Tests pour validate_range"""
    
    def test_validate_range_valide(self):
        """Test valeur dans range"""
        from src.utils.validators.common import validate_range
        
        is_valid, error = validate_range(5, 0, 10)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_range_au_dessus_max(self):
        """Test valeur au-dessus max"""
        from src.utils.validators.common import validate_range
        
        is_valid, error = validate_range(15, 0, 10)
        
        assert is_valid is False
        assert "<=" in error
    
    def test_validate_range_en_dessous_min(self):
        """Test valeur en-dessous min"""
        from src.utils.validators.common import validate_range
        
        is_valid, error = validate_range(-5, 0, 10)
        
        assert is_valid is False
        assert ">=" in error
    
    def test_validate_range_sans_min(self):
        """Test sans minimum"""
        from src.utils.validators.common import validate_range
        
        is_valid, error = validate_range(-1000, None, 10)
        
        assert is_valid is True
    
    def test_validate_range_sans_max(self):
        """Test sans maximum"""
        from src.utils.validators.common import validate_range
        
        is_valid, error = validate_range(1000, 0, None)
        
        assert is_valid is True
    
    def test_validate_range_valeur_invalide(self):
        """Test valeur non numÃ©rique"""
        from src.utils.validators.common import validate_range
        
        is_valid, error = validate_range("abc", 0, 10)
        
        assert is_valid is False
        assert "nombre" in error
    
    def test_validate_range_custom_field_name(self):
        """Test nom de champ personnalisÃ©"""
        from src.utils.validators.common import validate_range
        
        is_valid, error = validate_range(15, 0, 10, "quantitÃ©")
        
        assert "quantitÃ©" in error


class TestValidateStringLength:
    """Tests pour validate_string_length"""
    
    def test_validate_string_length_valide(self):
        """Test string valide"""
        from src.utils.validators.common import validate_string_length
        
        is_valid, error = validate_string_length("Hello", 1, 10)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_string_length_trop_court(self):
        """Test string trop court"""
        from src.utils.validators.common import validate_string_length
        
        is_valid, error = validate_string_length("Hi", 5, 10)
        
        assert is_valid is False
        assert "au moins" in error
    
    def test_validate_string_length_trop_long(self):
        """Test string trop long"""
        from src.utils.validators.common import validate_string_length
        
        is_valid, error = validate_string_length("Hello World!", 1, 5)
        
        assert is_valid is False
        assert "maximum" in error
    
    def test_validate_string_length_pas_string(self):
        """Test valeur non string"""
        from src.utils.validators.common import validate_string_length
        
        is_valid, error = validate_string_length(123, 1, 10)
        
        assert is_valid is False
        assert "texte" in error
    
    def test_validate_string_length_sans_max(self):
        """Test sans maximum"""
        from src.utils.validators.common import validate_string_length
        
        is_valid, error = validate_string_length("A" * 1000, 1, None)
        
        assert is_valid is True


class TestValidateRequiredFields:
    """Tests pour validate_required_fields"""
    
    def test_validate_required_fields_tous_presents(self):
        """Test tous champs prÃ©sents"""
        from src.utils.validators.common import validate_required_fields
        
        data = {"nom": "Test", "email": "test@test.com"}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        
        assert is_valid is True
        assert missing == []
    
    def test_validate_required_fields_manquant(self):
        """Test champ manquant"""
        from src.utils.validators.common import validate_required_fields
        
        data = {"nom": "Test"}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        
        assert is_valid is False
        assert "email" in missing
    
    def test_validate_required_fields_vide(self):
        """Test champ vide"""
        from src.utils.validators.common import validate_required_fields
        
        data = {"nom": "Test", "email": ""}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        
        assert is_valid is False
        assert "email" in missing
    
    def test_validate_required_fields_none(self):
        """Test champ None"""
        from src.utils.validators.common import validate_required_fields
        
        data = {"nom": "Test", "email": None}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        
        assert is_valid is False
        assert "email" in missing


class TestValidateChoice:
    """Tests pour validate_choice"""
    
    def test_validate_choice_valide(self):
        """Test choix valide"""
        from src.utils.validators.common import validate_choice
        
        is_valid, error = validate_choice("facile", ["facile", "moyen", "difficile"])
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_choice_invalide(self):
        """Test choix invalide"""
        from src.utils.validators.common import validate_choice
        
        is_valid, error = validate_choice("expert", ["facile", "moyen", "difficile"])
        
        assert is_valid is False
        assert "doit Ãªtre dans" in error


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DATE VALIDATORS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValidateDateRange:
    """Tests pour validate_date_range"""
    
    def test_validate_date_range_valide(self):
        """Test plage valide"""
        from src.utils.validators.dates import validate_date_range
        
        start = date(2025, 1, 1)
        end = date(2025, 1, 10)
        
        is_valid, error = validate_date_range(start, end)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_date_range_invalide_inversee(self):
        """Test plage inversÃ©e"""
        from src.utils.validators.dates import validate_date_range
        
        start = date(2025, 1, 10)
        end = date(2025, 1, 1)
        
        is_valid, error = validate_date_range(start, end)
        
        assert is_valid is False
        assert "avant" in error
    
    def test_validate_date_range_avec_max_days_ok(self):
        """Test avec max_days OK"""
        from src.utils.validators.dates import validate_date_range
        
        start = date(2025, 1, 1)
        end = date(2025, 1, 5)
        
        is_valid, error = validate_date_range(start, end, max_days=7)
        
        assert is_valid is True
    
    def test_validate_date_range_avec_max_days_depasse(self):
        """Test avec max_days dÃ©passÃ©"""
        from src.utils.validators.dates import validate_date_range
        
        start = date(2025, 1, 1)
        end = date(2025, 1, 15)
        
        is_valid, error = validate_date_range(start, end, max_days=7)
        
        assert is_valid is False
        assert "maximum" in error


class TestIsFutureDate:
    """Tests pour is_future_date"""
    
    def test_is_future_date_futur(self):
        """Test date dans le futur"""
        from src.utils.validators.dates import is_future_date
        
        future = date.today() + timedelta(days=30)
        
        assert is_future_date(future) is True
    
    def test_is_future_date_passe(self):
        """Test date dans le passÃ©"""
        from src.utils.validators.dates import is_future_date
        
        past = date.today() - timedelta(days=30)
        
        assert is_future_date(past) is False
    
    def test_is_future_date_aujourdhui(self):
        """Test date aujourd'hui"""
        from src.utils.validators.dates import is_future_date
        
        assert is_future_date(date.today()) is False


class TestIsPastDate:
    """Tests pour is_past_date"""
    
    def test_is_past_date_passe(self):
        """Test date dans le passÃ©"""
        from src.utils.validators.dates import is_past_date
        
        past = date.today() - timedelta(days=30)
        
        assert is_past_date(past) is True
    
    def test_is_past_date_futur(self):
        """Test date dans le futur"""
        from src.utils.validators.dates import is_past_date
        
        future = date.today() + timedelta(days=30)
        
        assert is_past_date(future) is False
    
    def test_is_past_date_aujourdhui(self):
        """Test date aujourd'hui"""
        from src.utils.validators.dates import is_past_date
        
        assert is_past_date(date.today()) is False


class TestValidateExpiryDate:
    """Tests pour validate_expiry_date"""
    
    def test_validate_expiry_date_valide(self):
        """Test date expiration valide"""
        from src.utils.validators.dates import validate_expiry_date
        
        expiry = date.today() + timedelta(days=30)
        
        is_valid, error = validate_expiry_date(expiry)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_expiry_date_passee(self):
        """Test date expiration passÃ©e"""
        from src.utils.validators.dates import validate_expiry_date
        
        expiry = date.today() - timedelta(days=1)
        
        is_valid, error = validate_expiry_date(expiry)
        
        assert is_valid is False
        assert "passÃ©e" in error
    
    def test_validate_expiry_date_trop_proche(self):
        """Test date expiration trop proche"""
        from src.utils.validators.dates import validate_expiry_date
        
        # Expiration demain mais min_days_ahead = 3
        expiry = date.today() + timedelta(days=1)
        
        is_valid, error = validate_expiry_date(expiry, min_days_ahead=3)
        
        assert is_valid is False
        assert "3 jour" in error


class TestDaysUntil:
    """Tests pour days_until"""
    
    def test_days_until_futur(self):
        """Test jours jusqu'Ã  date future"""
        from src.utils.validators.dates import days_until
        
        target = date.today() + timedelta(days=7)
        
        assert days_until(target) == 7
    
    def test_days_until_passe(self):
        """Test jours jusqu'Ã  date passÃ©e (nÃ©gatif)"""
        from src.utils.validators.dates import days_until
        
        target = date.today() - timedelta(days=3)
        
        assert days_until(target) == -3
    
    def test_days_until_aujourdhui(self):
        """Test jours jusqu'Ã  aujourd'hui"""
        from src.utils.validators.dates import days_until
        
        assert days_until(date.today()) == 0


class TestIsWithinDays:
    """Tests pour is_within_days"""
    
    def test_is_within_days_dans_limite(self):
        """Test date dans la limite"""
        from src.utils.validators.dates import is_within_days
        
        target = date.today() + timedelta(days=3)
        
        assert is_within_days(target, 7) is True
    
    def test_is_within_days_hors_limite(self):
        """Test date hors limite"""
        from src.utils.validators.dates import is_within_days
        
        target = date.today() + timedelta(days=10)
        
        assert is_within_days(target, 7) is False
    
    def test_is_within_days_passe(self):
        """Test date passÃ©e"""
        from src.utils.validators.dates import is_within_days
        
        target = date.today() - timedelta(days=1)
        
        assert is_within_days(target, 7) is False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FOOD VALIDATORS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValidateRecipe:
    """Tests pour validate_recipe"""
    
    def test_validate_recipe_valide(self):
        """Test recette valide"""
        from src.utils.validators.food import validate_recipe
        
        data = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 8
        }
        
        is_valid, errors = validate_recipe(data)
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_recipe_champ_manquant(self):
        """Test recette champ manquant"""
        from src.utils.validators.food import validate_recipe
        
        data = {
            "nom": "Tarte",
            "temps_preparation": 30
            # manque temps_cuisson et portions
        }
        
        is_valid, errors = validate_recipe(data)
        
        assert is_valid is False
        assert any("temps_cuisson" in e for e in errors)
    
    def test_validate_recipe_nom_trop_court(self):
        """Test recette nom trop court"""
        from src.utils.validators.food import validate_recipe
        
        data = {
            "nom": "Ta",  # < 3 caractÃ¨res
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 8
        }
        
        is_valid, errors = validate_recipe(data)
        
        assert is_valid is False
        assert any("3 caractÃ¨res" in e for e in errors)
    
    def test_validate_recipe_nom_trop_long(self):
        """Test recette nom trop long"""
        from src.utils.validators.food import validate_recipe
        
        data = {
            "nom": "A" * 250,  # > 200 caractÃ¨res
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 8
        }
        
        is_valid, errors = validate_recipe(data)
        
        assert is_valid is False
        assert any("trop long" in e for e in errors)
    
    def test_validate_recipe_temps_negatif(self):
        """Test recette temps nÃ©gatif"""
        from src.utils.validators.food import validate_recipe
        
        data = {
            "nom": "Tarte",
            "temps_preparation": -10,
            "temps_cuisson": 45,
            "portions": 8
        }
        
        is_valid, errors = validate_recipe(data)
        
        assert is_valid is False
        assert any("0 et 600" in e for e in errors)
    
    def test_validate_recipe_portions_invalide(self):
        """Test recette portions invalide"""
        from src.utils.validators.food import validate_recipe
        
        data = {
            "nom": "Tarte",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 100  # > 50
        }
        
        is_valid, errors = validate_recipe(data)
        
        assert is_valid is False
        assert any("entre 1 et 50" in e for e in errors)
    
    def test_validate_recipe_difficulte_invalide(self):
        """Test recette difficultÃ© invalide"""
        from src.utils.validators.food import validate_recipe
        
        data = {
            "nom": "Tarte",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 8,
            "difficulte": "expert"  # non valide
        }
        
        is_valid, errors = validate_recipe(data)
        
        assert is_valid is False
        assert any("difficulte" in e for e in errors)


class TestValidateIngredient:
    """Tests pour validate_ingredient"""
    
    def test_validate_ingredient_valide(self):
        """Test ingrÃ©dient valide"""
        from src.utils.validators.food import validate_ingredient
        
        data = {
            "nom": "Pommes",
            "unite": "kg"
        }
        
        is_valid, errors = validate_ingredient(data)
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_ingredient_nom_manquant(self):
        """Test ingrÃ©dient nom manquant"""
        from src.utils.validators.food import validate_ingredient
        
        data = {"unite": "kg"}
        
        is_valid, errors = validate_ingredient(data)
        
        assert is_valid is False
        assert any("nom" in e for e in errors)
    
    def test_validate_ingredient_nom_trop_court(self):
        """Test ingrÃ©dient nom trop court"""
        from src.utils.validators.food import validate_ingredient
        
        data = {"nom": "P", "unite": "kg"}
        
        is_valid, errors = validate_ingredient(data)
        
        assert is_valid is False
        assert any("2 caractÃ¨res" in e for e in errors)
    
    def test_validate_ingredient_unite_invalide(self):
        """Test ingrÃ©dient unitÃ© invalide"""
        from src.utils.validators.food import validate_ingredient
        
        data = {"nom": "Pommes", "unite": "xyz"}
        
        is_valid, errors = validate_ingredient(data)
        
        assert is_valid is False
        assert any("unite" in e for e in errors)


class TestValidateInventoryItem:
    """Tests pour validate_inventory_item"""
    
    def test_validate_inventory_item_valide(self):
        """Test article inventaire valide"""
        from src.utils.validators.food import validate_inventory_item
        
        data = {
            "ingredient_id": 1,
            "quantite": 5.0
        }
        
        is_valid, errors = validate_inventory_item(data)
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_inventory_item_champ_manquant(self):
        """Test article inventaire champ manquant"""
        from src.utils.validators.food import validate_inventory_item
        
        data = {"ingredient_id": 1}
        
        is_valid, errors = validate_inventory_item(data)
        
        assert is_valid is False
        assert any("quantite" in e for e in errors)
    
    def test_validate_inventory_item_quantite_negative(self):
        """Test article inventaire quantitÃ© nÃ©gative"""
        from src.utils.validators.food import validate_inventory_item
        
        data = {"ingredient_id": 1, "quantite": -5}
        
        is_valid, errors = validate_inventory_item(data)
        
        assert is_valid is False
        assert any(">= 0" in e for e in errors)
    
    def test_validate_inventory_item_quantite_min_negative(self):
        """Test article inventaire quantite_min nÃ©gative"""
        from src.utils.validators.food import validate_inventory_item
        
        data = {"ingredient_id": 1, "quantite": 5, "quantite_min": -2}
        
        is_valid, errors = validate_inventory_item(data)
        
        assert is_valid is False


class TestValidateShoppingItem:
    """Tests pour validate_shopping_item"""
    
    def test_validate_shopping_item_valide(self):
        """Test article courses valide"""
        from src.utils.validators.food import validate_shopping_item
        
        data = {
            "ingredient_id": 1,
            "quantite_necessaire": 2.0
        }
        
        is_valid, errors = validate_shopping_item(data)
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_shopping_item_quantite_zero(self):
        """Test article courses quantitÃ© zÃ©ro"""
        from src.utils.validators.food import validate_shopping_item
        
        data = {"ingredient_id": 1, "quantite_necessaire": 0}
        
        is_valid, errors = validate_shopping_item(data)
        
        assert is_valid is False
        assert any("> 0" in e for e in errors)
    
    def test_validate_shopping_item_priorite_invalide(self):
        """Test article courses prioritÃ© invalide"""
        from src.utils.validators.food import validate_shopping_item
        
        data = {
            "ingredient_id": 1,
            "quantite_necessaire": 2,
            "priorite": "ultra_urgent"
        }
        
        is_valid, errors = validate_shopping_item(data)
        
        assert is_valid is False
        assert any("priorite" in e for e in errors)


class TestValidateMeal:
    """Tests pour validate_meal"""
    
    def test_validate_meal_valide(self):
        """Test repas valide"""
        from src.utils.validators.food import validate_meal
        
        data = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": date.today(),
            "type_repas": "dÃ©jeuner"
        }
        
        is_valid, errors = validate_meal(data)
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_meal_champ_manquant(self):
        """Test repas champ manquant"""
        from src.utils.validators.food import validate_meal
        
        data = {"planning_id": 1, "jour_semaine": 0}
        
        is_valid, errors = validate_meal(data)
        
        assert is_valid is False
        assert any("date" in e or "type_repas" in e for e in errors)
    
    def test_validate_meal_jour_semaine_invalide(self):
        """Test repas jour_semaine invalide"""
        from src.utils.validators.food import validate_meal
        
        data = {
            "planning_id": 1,
            "jour_semaine": 10,  # > 6
            "date": date.today(),
            "type_repas": "dÃ©jeuner"
        }
        
        is_valid, errors = validate_meal(data)
        
        assert is_valid is False
        assert any("entre 0 et 6" in e for e in errors)
    
    def test_validate_meal_type_repas_invalide(self):
        """Test repas type_repas invalide"""
        from src.utils.validators.food import validate_meal
        
        data = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": date.today(),
            "type_repas": "brunch"  # non valide
        }
        
        is_valid, errors = validate_meal(data)
        
        assert is_valid is False
        assert any("type_repas" in e for e in errors)
    
    def test_validate_meal_portions_invalide(self):
        """Test repas portions invalide"""
        from src.utils.validators.food import validate_meal
        
        data = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": date.today(),
            "type_repas": "dÃ©jeuner",
            "portions": 100  # > 50
        }
        
        is_valid, errors = validate_meal(data)
        
        assert is_valid is False
        assert any("entre 1 et 50" in e for e in errors)
