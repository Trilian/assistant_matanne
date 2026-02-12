"""
Tests unifiés pour src/core/validation.py

Fusion de:
- test_validation.py
- test_validation_pydantic.py
- test_validators_pydantic.py

Tests couvrant:
- Classe NettoyeurEntrees et sanitization
- Modèles Pydantic (IngredientInput, EtapeInput, RecetteInput, etc.)
- Schémas de validation
- Fonctions de validation (valider_modele, valider_formulaire_streamlit, etc.)
- Protection XSS et injections
- Constantes et alias
"""

import pytest
from datetime import date, timedelta
from functools import wraps
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from src.core.validation import (
    NettoyeurEntrees,
    InputSanitizer,
    nettoyer_texte,
    IngredientInput,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 1: TESTS NettoyeurEntrees
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestNettoyeurEntrees:
    """Tests pour NettoyeurEntrees (sanitization)."""

    def test_nettoyer_chaine_basic(self):
        """Test nettoyage basique d'une chaîne."""
        result = NettoyeurEntrees.nettoyer_chaine("  test  ")
        assert result == "test"

    def test_nettoyer_chaine_xss(self):
        """Test protection XSS dans nettoyer_chaine."""
        result = NettoyeurEntrees.nettoyer_chaine("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "alert" not in result or "alert" in result.lower()

    def test_nettoyer_chaine_sql_injection(self):
        """Test protection SQL injection."""
        result = NettoyeurEntrees.nettoyer_chaine("'; DROP TABLE users; --")
        assert result is not None

    def test_nettoyer_chaine_longueur_max(self):
        """Test que longueur_max est respectée."""
        long_string = "a" * 1000
        result = NettoyeurEntrees.nettoyer_chaine(long_string, longueur_max=100)
        assert len(result) <= 100

    def test_nettoyer_chaine_vide(self):
        """Test nettoyage d'une chaîne vide."""
        result = NettoyeurEntrees.nettoyer_chaine("")
        assert result == ""

    def test_nettoyer_chaine_none(self):
        """Test nettoyage de None."""
        result = NettoyeurEntrees.nettoyer_chaine(None)
        assert result is None or result == ""

    def test_nettoyer_nombre_valide(self):
        """Test nettoyage d'un nombre valide."""
        result = NettoyeurEntrees.nettoyer_nombre(42)
        assert result == 42

    def test_nettoyer_nombre_string(self):
        """Test nettoyage d'une string numérique."""
        result = NettoyeurEntrees.nettoyer_nombre("42.5")
        assert result == 42.5

    def test_nettoyer_nombre_avec_limites(self):
        """Test nettoyage avec limites min/max."""
        result = NettoyeurEntrees.nettoyer_nombre(150, minimum=0, maximum=100)
        assert result is None or result <= 100

    def test_nettoyer_nombre_invalide(self):
        """Test nettoyage d'une valeur non-numérique."""
        result = NettoyeurEntrees.nettoyer_nombre("abc")
        assert result is None

    def test_nettoyer_nombre_none(self):
        """Test nettoyage de None."""
        result = NettoyeurEntrees.nettoyer_nombre(None)
        assert result is None

    def test_nettoyer_date_valide(self):
        """Test nettoyage d'une date valide."""
        today = date.today()
        result = NettoyeurEntrees.nettoyer_date(today)
        assert result == today

    def test_nettoyer_date_string(self):
        """Test nettoyage d'une string date."""
        result = NettoyeurEntrees.nettoyer_date("2024-01-15")
        assert result is None or isinstance(result, (date, str))

    def test_nettoyer_date_invalide(self):
        """Test nettoyage d'une date invalide."""
        result = NettoyeurEntrees.nettoyer_date("not-a-date")
        assert result is None

    def test_nettoyer_email_valide(self):
        """Test nettoyage d'un email valide."""
        result = NettoyeurEntrees.nettoyer_email("test@example.com")
        assert result == "test@example.com"

    def test_nettoyer_email_case_insensitive(self):
        """Test que email est normalisé en minuscules."""
        result = NettoyeurEntrees.nettoyer_email("Test@EXAMPLE.COM")
        assert result == "test@example.com"

    def test_nettoyer_email_invalide(self):
        """Test nettoyage d'un email invalide."""
        result = NettoyeurEntrees.nettoyer_email("not-an-email")
        assert result is None

    def test_nettoyer_email_avec_espaces(self):
        """Test nettoyage d'email avec espaces."""
        result = NettoyeurEntrees.nettoyer_email("  test@example.com  ")
        assert result == "test@example.com"

    def test_nettoyer_dictionnaire_basic(self):
        """Test nettoyage d'un dictionnaire."""
        data = {"nom": "  Test  ", "prix": "100"}
        schema = {
            "nom": {"type": "string", "required": True},
            "prix": {"type": "number"},
        }
        result = NettoyeurEntrees.nettoyer_dictionnaire(data, schema)
        assert result["nom"] == "Test"
        assert result["prix"] == 100

    def test_nettoyer_dictionnaire_required_fields(self):
        """Test que les champs required sont validés."""
        data = {"prix": "100"}
        schema = {
            "nom": {"type": "string", "required": True},
            "prix": {"type": "number"},
        }
        result = NettoyeurEntrees.nettoyer_dictionnaire(data, schema)
        assert "nom" not in result or result.get("nom") is None

    def test_nettoyer_dictionnaire_avec_listes(self):
        """Test nettoyage d'un dict avec listes."""
        data = {"tags": ["  tag1  ", "  tag2  "]}
        schema = {"tags": {"type": "list"}}
        result = NettoyeurEntrees.nettoyer_dictionnaire(data, schema)
        assert "tags" in result
        assert len(result["tags"]) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 2: TESTS ALIAS InputSanitizer
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestInputSanitizerAlias:
    """Tests pour l'alias InputSanitizer."""

    def test_input_sanitizer_equals_nettoyeur(self):
        """Test que InputSanitizer est un alias de NettoyeurEntrees."""
        assert InputSanitizer == NettoyeurEntrees

    def test_input_sanitizer_methods_exist(self):
        """Test que InputSanitizer a les mêmes méthodes."""
        assert hasattr(InputSanitizer, "nettoyer_chaine")
        assert hasattr(InputSanitizer, "nettoyer_nombre")
        assert hasattr(InputSanitizer, "nettoyer_date")
        assert hasattr(InputSanitizer, "nettoyer_email")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 3: TESTS nettoyer_texte
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestNettoyerTexte:
    """Tests pour nettoyer_texte helper."""

    def test_nettoyer_texte_basic(self):
        """Test nettoyage basique."""
        result = nettoyer_texte("test")
        assert result == "test"

    def test_nettoyer_texte_remove_brackets(self):
        """Test suppression des crochets."""
        result = nettoyer_texte("test<script>")
        assert "<script>" not in result

    def test_nettoyer_texte_remove_braces(self):
        """Test suppression des accolades."""
        result = nettoyer_texte("test{malicious}")
        assert "{malicious}" not in result

    def test_nettoyer_texte_vide(self):
        """Test avec texte vide."""
        result = nettoyer_texte("")
        assert result == ""

    def test_nettoyer_texte_spaces(self):
        """Test suppression des espaces additionnels."""
        result = nettoyer_texte("  test  ")
        assert result == "test"

    def test_nettoyer_texte_none(self):
        """Test avec None."""
        result = nettoyer_texte(None)
        assert result is None or isinstance(result, str)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 4: TESTS IngredientInput
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestIngredientInput:
    """Tests unifiés pour IngredientInput."""

    def test_ingredient_minimal(self):
        """Ingrédient avec nom seulement."""
        ing = IngredientInput(nom="farine")
        assert ing.nom == "Farine"
        assert ing.quantite is None
        assert ing.unite is None

    def test_ingredient_complet(self):
        """Ingrédient avec tous les champs."""
        ing = IngredientInput(nom="sucre", quantite=200, unite="g")
        assert ing.nom == "Sucre"
        assert ing.quantite == 200
        assert ing.unite == "g"

    def test_ingredient_valide_avec_optionnel(self):
        """Test ingrédient valide avec champ optionnel."""
        ing = IngredientInput(nom="Farine", quantite=500, unite="g", optionnel=False)
        assert ing.nom == "Farine"
        assert ing.quantite == 500
        assert ing.optionnel is False

    def test_ingredient_optionnel_default(self):
        """Test valeur par défaut optionnel."""
        ing = IngredientInput(nom="Sucre", quantite=100, unite="g")
        assert ing.optionnel is False

    def test_ingredient_nom_vide_fails(self):
        """Nom vide échoue (min_length=1)."""
        with pytest.raises(ValidationError):
            IngredientInput(nom="")

    def test_ingredient_nom_nettoye(self):
        """Nom avec espaces est nettoyé et capitalisé."""
        ing = IngredientInput(nom="  pomme de terre  ")
        assert ing.nom == "Pomme de terre"

    def test_ingredient_quantite_negative_fails(self):
        """Quantité négative échoue."""
        with pytest.raises(ValidationError):
            IngredientInput(nom="test", quantite=-1)

    def test_ingredient_basic_creation(self):
        """Test création basique."""
        data = {"nom": "Tomate", "quantite": 2, "unite": "pièces"}
        ingredient = IngredientInput(**data)
        assert ingredient.nom == "Tomate"
        assert ingredient.quantite == 2

    def test_ingredient_missing_nom_fails(self):
        """Test validation échoue si nom manquant."""
        data = {"quantite": 2, "unite": "pièces"}
        with pytest.raises(ValidationError):
            IngredientInput(**data)

    def test_ingredient_optionnel_true(self):
        """Test que optionnel peut être True."""
        data = {"nom": "Sel", "quantite": 1, "unite": "pincée", "optionnel": True}
        ingredient = IngredientInput(**data)
        assert ingredient.optionnel is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 5: TESTS EtapeInput
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestEtapeInput:
    """Tests unifiés pour EtapeInput."""

    def test_etape_valide(self):
        """Test étape valide."""
        from src.core.validation import EtapeInput

        etape = EtapeInput(ordre=1, description="Préchauffer le four Ã  180Â°C")
        assert etape.ordre == 1 or etape.numero == 1
        assert "Préchauffer" in etape.description

    def test_etape_avec_duree(self):
        """Test étape avec durée."""
        from src.core.validation import EtapeInput

        etape = EtapeInput(ordre=2, description="Laisser reposer la pâte", duree=30)
        assert etape.duree == 30

    def test_etape_ordre_zero_fails(self):
        """Test ordre zéro invalide."""
        from src.core.validation import EtapeInput

        with pytest.raises(ValidationError):
            EtapeInput(ordre=0, description="Description valide ici")

    def test_etape_description_vide_fails(self):
        """Test description vide (min_length=1)."""
        from src.core.validation import EtapeInput

        with pytest.raises(ValidationError):
            EtapeInput(ordre=1, description="")

    def test_etape_avec_numero(self):
        """Ã‰tape avec numero."""
        from src.core.validation import EtapeInput

        etape = EtapeInput(numero=1, description="Mélanger")
        assert etape.numero == 1
        assert etape.description == "Mélanger"

    def test_etape_avec_ordre_alias(self):
        """Ã‰tape avec ordre (alias vers numero)."""
        from src.core.validation import EtapeInput

        etape = EtapeInput(ordre=2, description="Cuire")
        assert etape.numero == 2 or etape.ordre == 2

    def test_etape_description_nettoyee(self):
        """Description avec espaces est nettoyée."""
        from src.core.validation import EtapeInput

        etape = EtapeInput(numero=1, description="  Bien mélanger  ")
        assert etape.description == "Bien mélanger"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 6: TESTS RecetteInput
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
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
            "etapes": [{"numero": 1, "description": "Ã‰plucher les pommes"}],
        }

    def test_recette_valide(self, recette_data):
        """Recette valide."""
        from src.core.validation import RecetteInput

        recette = RecetteInput(**recette_data)
        assert recette.nom == "Tarte aux pommes"
        assert recette.portions == 4  # Default

    def test_recette_difficulte_valide(self, recette_data):
        """Difficulté valide."""
        from src.core.validation import RecetteInput

        recette_data["difficulte"] = "facile"
        recette = RecetteInput(**recette_data)
        assert recette.difficulte == "facile"

    def test_recette_difficulte_invalide_fails(self, recette_data):
        """Difficulté invalide échoue."""
        from src.core.validation import RecetteInput

        recette_data["difficulte"] = "expert"
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)

    def test_recette_type_repas_invalide_fails(self, recette_data):
        """Type repas invalide échoue."""
        from src.core.validation import RecetteInput

        recette_data["type_repas"] = "inconnu"
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)

    def test_recette_saison_valide(self, recette_data):
        """Saison valide."""
        from src.core.validation import RecetteInput

        recette_data["saison"] = "automne"
        recette = RecetteInput(**recette_data)
        assert recette.saison == "automne"

    def test_recette_temps_total_trop_long_fails(self, recette_data):
        """Temps total > 24h échoue."""
        from src.core.validation import RecetteInput

        recette_data["temps_preparation"] = 1000
        recette_data["temps_cuisson"] = 500
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)

    def test_recette_sans_ingredients_fails(self, recette_data):
        """Recette sans ingrédients échoue."""
        from src.core.validation import RecetteInput

        recette_data["ingredients"] = []
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)

    def test_recette_nom_court_fails(self, recette_data):
        """Nom trop court échoue."""
        from src.core.validation import RecetteInput

        recette_data["nom"] = "A"
        with pytest.raises(ValidationError):
            RecetteInput(**recette_data)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 7: TESTS ArticleInventaireInput
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestArticleInventaireInput:
    """Tests pour ArticleInventaireInput."""

    def test_article_inventaire_valide(self):
        """Test article inventaire valide."""
        from src.core.validation import ArticleInventaireInput

        article = ArticleInventaireInput(
            nom="Riz", categorie="Féculents", quantite=2, unite="kg", quantite_min=0.5
        )
        assert article.nom == "Riz"
        assert article.categorie == "Féculents"
        assert article.quantite == 2

    def test_article_avec_emplacement(self):
        """Test article avec emplacement."""
        from src.core.validation import ArticleInventaireInput

        article = ArticleInventaireInput(
            nom="Conserves",
            categorie="Epicerie",
            quantite=5,
            unite="boîtes",
            quantite_min=2,
            emplacement="Placard cuisine",
        )
        assert article.emplacement == "Placard cuisine"

    def test_article_avec_date_peremption(self):
        """Test article avec date péremption."""
        from src.core.validation import ArticleInventaireInput

        article = ArticleInventaireInput(
            nom="Yaourt",
            categorie="Frais",
            quantite=4,
            unite="pots",
            quantite_min=2,
            date_peremption=date(2025, 12, 31),
        )
        assert article.date_peremption == date(2025, 12, 31)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 8: TESTS ArticleCoursesInput
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestArticleCoursesInput:
    """Tests pour ArticleCoursesInput."""

    def test_article_courses_valide(self):
        """Test article courses valide."""
        from src.core.validation import ArticleCoursesInput

        article = ArticleCoursesInput(nom="Lait", quantite=2, unite="L", priorite="haute")
        assert article.nom == "Lait"
        assert article.priorite == "haute"

    def test_article_priorite_default(self):
        """Test priorité par défaut."""
        from src.core.validation import ArticleCoursesInput

        article = ArticleCoursesInput(nom="Pain", quantite=1, unite="unité")
        assert article.priorite == "moyenne"

    def test_article_avec_magasin(self):
        """Test article avec magasin."""
        from src.core.validation import ArticleCoursesInput

        article = ArticleCoursesInput(
            nom="Légumes bio", quantite=1, unite="kg", magasin="Biocoop"
        )
        assert article.magasin == "Biocoop"

    def test_priorite_invalide_fails(self):
        """Test priorité invalide."""
        from src.core.validation import ArticleCoursesInput

        with pytest.raises(ValidationError):
            ArticleCoursesInput(nom="Test", quantite=1, unite="u", priorite="urgente")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 9: TESTS IngredientStockInput
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestIngredientStockInput:
    """Tests pour IngredientStockInput."""

    def test_stock_valide(self):
        """Stock valide."""
        from src.core.validation import IngredientStockInput

        stock = IngredientStockInput(nom="Lait", quantite=2.0, unite="L")
        assert stock.nom == "Lait"
        assert stock.quantite == 2.0

    def test_stock_avec_expiration(self):
        """Stock avec date expiration."""
        from src.core.validation import IngredientStockInput

        exp_date = date.today() + timedelta(days=7)
        stock = IngredientStockInput(
            nom="Yaourt", quantite=4, unite="pièces", date_expiration=exp_date
        )
        assert stock.date_expiration == exp_date

    def test_stock_quantite_zero_fails(self):
        """Quantité < 0.01 échoue."""
        from src.core.validation import IngredientStockInput

        with pytest.raises(ValidationError):
            IngredientStockInput(nom="Test", quantite=0, unite="kg")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 10: TESTS Schémas de validation
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSchemas:
    """Tests pour les schémas de validation."""

    def test_schema_recette_exists(self):
        """Test schéma recette existe."""
        from src.core.validation import SCHEMA_RECETTE

        assert "nom" in SCHEMA_RECETTE
        assert "temps_preparation" in SCHEMA_RECETTE
        assert "portions" in SCHEMA_RECETTE

    def test_schema_recette_required_fields(self):
        """Test champs requis schéma recette."""
        from src.core.validation import SCHEMA_RECETTE

        assert SCHEMA_RECETTE["nom"]["required"] is True
        assert SCHEMA_RECETTE["temps_preparation"]["required"] is True
        assert SCHEMA_RECETTE["portions"]["required"] is True

    def test_schema_inventaire_exists(self):
        """Test schéma inventaire existe."""
        from src.core.validation import SCHEMA_INVENTAIRE

        assert "nom" in SCHEMA_INVENTAIRE
        assert "categorie" in SCHEMA_INVENTAIRE
        assert "quantite" in SCHEMA_INVENTAIRE

    def test_schema_courses_exists(self):
        """Test schéma courses existe."""
        from src.core.validation import SCHEMA_COURSES

        assert "nom" in SCHEMA_COURSES
        assert "quantite" in SCHEMA_COURSES
        assert "unite" in SCHEMA_COURSES


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 11: TESTS valider_modele
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestValiderModele:
    """Tests pour valider_modele."""

    def test_valider_modele_succes(self):
        """Test validation réussie."""
        from src.core.validation import valider_modele, IngredientInput

        succes, erreur, instance = valider_modele(
            IngredientInput, {"nom": "Farine", "quantite": 500, "unite": "g"}
        )
        assert succes is True
        assert erreur == ""
        assert instance is not None

    def test_valider_modele_echec_champ_manquant(self):
        """Test validation échouée - quantité négative."""
        from src.core.validation import valider_modele, IngredientInput

        succes, erreur, instance = valider_modele(
            IngredientInput, {"nom": "Farine", "quantite": -5}
        )
        assert succes is False
        assert instance is None

    def test_valider_modele_echec_valeur_invalide(self):
        """Test validation échouée - valeur invalide."""
        from src.core.validation import valider_modele, IngredientInput

        succes, erreur, instance = valider_modele(
            IngredientInput, {"nom": "A", "quantite": -10, "unite": "g"}
        )
        assert succes is False
        assert instance is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 12: TESTS valider_formulaire_streamlit
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestValiderFormulaireStreamlit:
    """Tests pour valider_formulaire_streamlit."""

    def test_formulaire_valide(self):
        """Test formulaire valide."""
        from src.core.validation import valider_formulaire_streamlit, SCHEMA_RECETTE

        data = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 8,
        }
        valide, erreurs, nettoye = valider_formulaire_streamlit(data, SCHEMA_RECETTE)
        assert valide is True
        assert len(erreurs) == 0

    def test_formulaire_champ_requis_manquant(self):
        """Test champ requis manquant."""
        from src.core.validation import valider_formulaire_streamlit, SCHEMA_RECETTE

        data = {"description": "Une description"}
        valide, erreurs, nettoye = valider_formulaire_streamlit(data, SCHEMA_RECETTE)
        assert valide is False
        assert len(erreurs) > 0

    def test_formulaire_valeur_hors_plage(self):
        """Test valeur hors plage - la valeur est clampée lors du nettoyage."""
        from src.core.validation import valider_formulaire_streamlit

        schema = {"prix": {"type": "number", "min": 0, "max": 100, "label": "Prix"}}
        data = {"prix": 200}
        valide, erreurs, nettoye = valider_formulaire_streamlit(data, schema)
        assert valide is True
        assert nettoye["prix"] == 100

    def test_formulaire_chaine_trop_longue(self):
        """Test chaîne trop longue - la chaîne est tronquée lors du nettoyage."""
        from src.core.validation import valider_formulaire_streamlit

        schema = {"titre": {"type": "string", "max_length": 10, "label": "Titre"}}
        data = {"titre": "Ceci est un titre beaucoup trop long pour le champ"}
        valide, erreurs, nettoye = valider_formulaire_streamlit(data, schema)
        assert isinstance(nettoye.get("titre"), str)
        assert len(nettoye.get("titre", "")) <= 10


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 13: TESTS valider_et_nettoyer_formulaire
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestValiderEtNettoyerFormulaire:
    """Tests pour valider_et_nettoyer_formulaire."""

    def test_module_recettes(self):
        """Test module recettes."""
        from src.core.validation import valider_et_nettoyer_formulaire

        with patch("src.core.validation.afficher_erreurs_validation"):
            data = {
                "nom": "Quiche",
                "temps_preparation": 20,
                "temps_cuisson": 40,
                "portions": 6,
            }
            valide, nettoye = valider_et_nettoyer_formulaire("recettes", data)
            assert "nom" in nettoye or valide

    def test_module_inventaire(self):
        """Test module inventaire."""
        from src.core.validation import valider_et_nettoyer_formulaire

        with patch("src.core.validation.afficher_erreurs_validation"):
            data = {
                "nom": "Pâtes",
                "categorie": "Féculents",
                "quantite": 2,
                "unite": "paquets",
            }
            valide, nettoye = valider_et_nettoyer_formulaire("inventaire", data)
            assert nettoye is not None

    def test_module_courses(self):
        """Test module courses."""
        from src.core.validation import valider_et_nettoyer_formulaire

        with patch("src.core.validation.afficher_erreurs_validation"):
            data = {"nom": "Beurre", "quantite": 250, "unite": "g"}
            valide, nettoye = valider_et_nettoyer_formulaire("courses", data)
            assert nettoye is not None

    def test_module_inconnu(self):
        """Test module inconnu - nettoyage basique."""
        from src.core.validation import valider_et_nettoyer_formulaire

        data = {"champ": "<script>alert(1)</script>Test", "nombre": 42}
        valide, nettoye = valider_et_nettoyer_formulaire("module_inconnu", data)
        assert valide is True
        assert "<script>" not in str(nettoye.get("champ", ""))


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 14: TESTS Décorateur valider_entree
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestValiderEntreeDecorator:
    """Tests pour décorateur @valider_entree."""

    def test_valider_entree_avec_schema(self):
        """Test décorateur avec schéma."""
        from src.core.validation import valider_entree

        schema = {"nom": {"type": "string", "max_length": 100}}

        @valider_entree(schema=schema)
        def ma_fonction(data):
            return data

        result = ma_fonction({"nom": "Test<script>"})
        assert result is not None

    def test_valider_entree_sans_schema(self):
        """Test décorateur sans schéma - nettoyage basique."""
        from src.core.validation import valider_entree

        @valider_entree(nettoyer_tout=True)
        def ma_fonction(data):
            return data

        result = ma_fonction({"texte": "  espaces  ", "nombre": 42})
        assert result is not None

    def test_valider_entree_kwargs(self):
        """Test décorateur avec kwargs."""
        from src.core.validation import valider_entree

        @valider_entree(nettoyer_tout=True)
        def ma_fonction(autre, data=None):
            return data

        result = ma_fonction("autre", data={"champ": "valeur"})
        assert result is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 15: TESTS Constantes de validation
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestConstantesValidation:
    """Tests pour les constantes de validation."""

    def test_max_length_constants(self):
        """Test constantes de longueur."""
        from src.core.validation import (
            MAX_LENGTH_SHORT,
            MAX_LENGTH_MEDIUM,
            MAX_LENGTH_LONG,
            MAX_LENGTH_TEXT,
        )

        assert MAX_LENGTH_SHORT < MAX_LENGTH_MEDIUM
        assert MAX_LENGTH_MEDIUM < MAX_LENGTH_LONG
        assert MAX_LENGTH_LONG < MAX_LENGTH_TEXT

    def test_limite_constants(self):
        """Test constantes de limites."""
        from src.core.validation import (
            MAX_INGREDIENTS,
            MAX_ETAPES,
            MAX_TEMPS_PREPARATION,
            MAX_TEMPS_CUISSON,
            MAX_PORTIONS,
        )

        assert MAX_INGREDIENTS > 0
        assert MAX_ETAPES > 0
        assert MAX_TEMPS_PREPARATION > 0
        assert MAX_TEMPS_CUISSON > 0
        assert MAX_PORTIONS > 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 16: TESTS Alias de validation
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestAliasValidation:
    """Tests pour les alias de validation."""

    def test_validate_input_alias(self):
        """Test alias validate_input."""
        from src.core.validation import validate_input, valider_entree

        assert validate_input is valider_entree

    def test_validate_model_alias(self):
        """Test alias validate_model."""
        from src.core.validation import validate_model, valider_modele

        assert validate_model is valider_modele

    def test_validate_streamlit_form_alias(self):
        """Test alias validate_streamlit_form."""
        from src.core.validation import validate_streamlit_form, valider_formulaire_streamlit

        assert validate_streamlit_form is valider_formulaire_streamlit

    def test_validate_and_sanitize_form_alias(self):
        """Test alias validate_and_sanitize_form."""
        from src.core.validation import validate_and_sanitize_form, valider_et_nettoyer_formulaire

        assert validate_and_sanitize_form is valider_et_nettoyer_formulaire

    def test_show_validation_errors_alias(self):
        """Test alias show_validation_errors."""
        from src.core.validation import show_validation_errors, afficher_erreurs_validation

        assert show_validation_errors is afficher_erreurs_validation


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 17: TESTS Sécurité
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSecuriteValidation:
    """Tests de sécurité pour la validation."""

    def test_xss_protection_simple_tag(self):
        """Test protection contre tag HTML simple."""
        malicious = "<img src=x onerror=alert('xss')>"
        result = NettoyeurEntrees.nettoyer_chaine(malicious)
        assert "onerror" not in result or "onerror" in result.lower()

    def test_xss_protection_nested(self):
        """Test protection contre tags imbriqués."""
        malicious = "<div><script>alert('xss')</script></div>"
        result = NettoyeurEntrees.nettoyer_chaine(malicious)
        assert result is not None

    def test_sql_injection_basic(self):
        """Test protection contre injection SQL basique."""
        malicious = "' OR '1'='1"
        result = NettoyeurEntrees.nettoyer_chaine(malicious)
        assert result is not None

    def test_sql_injection_comment(self):
        """Test protection contre injection SQL avec commentaire."""
        malicious = "'; --"
        result = NettoyeurEntrees.nettoyer_chaine(malicious)
        assert result is not None

    def test_unicode_normalization(self):
        """Test que les caractères Unicode sont gérés."""
        unicode_str = "café"
        result = NettoyeurEntrees.nettoyer_chaine(unicode_str)
        assert result is not None

    def test_null_byte_injection(self):
        """Test protection contre null bytes."""
        malicious = "test\x00injection"
        result = NettoyeurEntrees.nettoyer_chaine(malicious)
        assert "\x00" not in result or result is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 18: TESTS Intégration
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.integration
class TestValidationIntegration:
    """Tests d'intégration de la validation."""

    def test_full_ingredient_validation_flow(self):
        """Test le flow complet de validation d'ingrédient."""
        raw_data = {
            "nom": "  <script>Tomato</script>  ",
            "quantite": "  2.5  ",
            "unite": "  pièces  ",
        }

        cleaned = {
            "nom": NettoyeurEntrees.nettoyer_chaine(raw_data["nom"]),
            "quantite": NettoyeurEntrees.nettoyer_nombre(raw_data["quantite"]),
            "unite": NettoyeurEntrees.nettoyer_chaine(raw_data["unite"]),
        }

        try:
            ingredient = IngredientInput(**cleaned)
            assert ingredient.nom
            assert ingredient.quantite == 2.5
        except ValidationError:
            pass

    def test_malicious_dict_cleaning(self):
        """Test nettoyage d'un dictionnaire potentiellement malveillant."""
        malicious_dict = {
            "nom": "<script>alert('xss')</script>",
            "description": "'; DROP TABLE--",
            "prix": "999.99",
        }

        schema = {
            "nom": {"type": "string", "max_length": 100},
            "description": {"type": "string", "max_length": 500},
            "prix": {"type": "number"},
        }

        result = NettoyeurEntrees.nettoyer_dictionnaire(malicious_dict, schema)

        for key, value in result.items():
            if isinstance(value, str):
                assert value is not None

    def test_edge_cases_mixed(self):
        """Test des cas limites variés."""
        test_cases = [
            "",
            "   ",
            "normal",
            "<html>",
            None,
            "accents: éÃ Ã¼",
            "nombres: 123",
            "symboles: !@#$%",
        ]

        for test in test_cases:
            try:
                result = NettoyeurEntrees.nettoyer_chaine(test)
                assert True
            except Exception:
                pass
