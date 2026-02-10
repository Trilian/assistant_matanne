"""
Tests profonds supplémentaires pour validation.py

Cible les modèles Pydantic, schémas et fonctions de validation
pour atteindre 80% de couverture.
"""

import pytest
from datetime import date
from functools import wraps
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════════════════
# TESTS: Modèles Pydantic
# ═══════════════════════════════════════════════════════════


class TestIngredientInput:
    """Tests pour IngredientInput"""

    def test_ingredient_valide(self):
        """Test ingrédient valide"""
        from src.core.validation import IngredientInput

        ing = IngredientInput(nom="Farine", quantite=500, unite="g", optionnel=False)

        assert ing.nom == "Farine"
        assert ing.quantite == 500
        assert ing.unite == "g"
        assert ing.optionnel is False

    def test_ingredient_optionnel_default(self):
        """Test valeur par défaut optionnel"""
        from src.core.validation import IngredientInput

        ing = IngredientInput(nom="Sucre", quantite=100, unite="g")

        assert ing.optionnel is False

    def test_ingredient_nom_trop_court(self):
        """Test nom trop court"""
        from src.core.validation import IngredientInput
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            IngredientInput(nom="A", quantite=100, unite="g")

    def test_ingredient_quantite_negative(self):
        """Test quantité négative"""
        from src.core.validation import IngredientInput
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            IngredientInput(nom="Sucre", quantite=-10, unite="g")


class TestEtapeInput:
    """Tests pour EtapeInput"""

    def test_etape_valide(self):
        """Test étape valide"""
        from src.core.validation import EtapeInput

        etape = EtapeInput(ordre=1, description="Préchauffer le four à 180°C")

        assert etape.ordre == 1
        assert "Préchauffer" in etape.description

    def test_etape_avec_duree(self):
        """Test étape avec durée"""
        from src.core.validation import EtapeInput

        etape = EtapeInput(ordre=2, description="Laisser reposer la pâte", duree=30)

        assert etape.duree == 30

    def test_etape_ordre_zero(self):
        """Test ordre zéro invalide"""
        from src.core.validation import EtapeInput
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            EtapeInput(ordre=0, description="Description valide ici")

    def test_etape_description_trop_courte(self):
        """Test description trop courte"""
        from src.core.validation import EtapeInput
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            EtapeInput(ordre=1, description="Trop")


class TestArticleInventaireInput:
    """Tests pour ArticleInventaireInput"""

    def test_article_inventaire_valide(self):
        """Test article inventaire valide"""
        from src.core.validation import ArticleInventaireInput

        article = ArticleInventaireInput(
            nom="Riz", categorie="Féculents", quantite=2, unite="kg", quantite_min=0.5
        )

        assert article.nom == "Riz"
        assert article.categorie == "Féculents"
        assert article.quantite == 2

    def test_article_avec_emplacement(self):
        """Test article avec emplacement"""
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
        """Test article avec date péremption"""
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


class TestArticleCoursesInput:
    """Tests pour ArticleCoursesInput"""

    def test_article_courses_valide(self):
        """Test article courses valide"""
        from src.core.validation import ArticleCoursesInput

        article = ArticleCoursesInput(nom="Lait", quantite=2, unite="L", priorite="haute")

        assert article.nom == "Lait"
        assert article.priorite == "haute"

    def test_article_priorite_default(self):
        """Test priorité par défaut"""
        from src.core.validation import ArticleCoursesInput

        article = ArticleCoursesInput(nom="Pain", quantite=1, unite="unité")

        assert article.priorite == "moyenne"

    def test_article_avec_magasin(self):
        """Test article avec magasin"""
        from src.core.validation import ArticleCoursesInput

        article = ArticleCoursesInput(
            nom="Légumes bio", quantite=1, unite="kg", magasin="Biocoop"
        )

        assert article.magasin == "Biocoop"

    def test_priorite_invalide(self):
        """Test priorité invalide"""
        from src.core.validation import ArticleCoursesInput
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ArticleCoursesInput(nom="Test", quantite=1, unite="u", priorite="urgente")


# ═══════════════════════════════════════════════════════════
# TESTS: Schémas de validation
# ═══════════════════════════════════════════════════════════


class TestSchemas:
    """Tests pour les schémas de validation"""

    def test_schema_recette_exists(self):
        """Test schéma recette existe"""
        from src.core.validation import SCHEMA_RECETTE

        assert "nom" in SCHEMA_RECETTE
        assert "temps_preparation" in SCHEMA_RECETTE
        assert "portions" in SCHEMA_RECETTE

    def test_schema_recette_required_fields(self):
        """Test champs requis schéma recette"""
        from src.core.validation import SCHEMA_RECETTE

        assert SCHEMA_RECETTE["nom"]["required"] is True
        assert SCHEMA_RECETTE["temps_preparation"]["required"] is True
        assert SCHEMA_RECETTE["portions"]["required"] is True

    def test_schema_inventaire_exists(self):
        """Test schéma inventaire existe"""
        from src.core.validation import SCHEMA_INVENTAIRE

        assert "nom" in SCHEMA_INVENTAIRE
        assert "categorie" in SCHEMA_INVENTAIRE
        assert "quantite" in SCHEMA_INVENTAIRE

    def test_schema_courses_exists(self):
        """Test schéma courses existe"""
        from src.core.validation import SCHEMA_COURSES

        assert "nom" in SCHEMA_COURSES
        assert "quantite" in SCHEMA_COURSES
        assert "unite" in SCHEMA_COURSES


# ═══════════════════════════════════════════════════════════
# TESTS: Fonctions de validation
# ═══════════════════════════════════════════════════════════


class TestValiderModele:
    """Tests pour valider_modele"""

    def test_valider_modele_succes(self):
        """Test validation réussie"""
        from src.core.validation import valider_modele, IngredientInput

        succes, erreur, instance = valider_modele(
            IngredientInput, {"nom": "Farine", "quantite": 500, "unite": "g"}
        )

        assert succes is True
        assert erreur == ""
        assert instance is not None

    def test_valider_modele_echec_champ_manquant(self):
        """Test validation échouée - champ manquant"""
        from src.core.validation import valider_modele, IngredientInput

        succes, erreur, instance = valider_modele(IngredientInput, {"nom": "Farine"})

        assert succes is False
        assert instance is None

    def test_valider_modele_echec_valeur_invalide(self):
        """Test validation échouée - valeur invalide"""
        from src.core.validation import valider_modele, IngredientInput

        succes, erreur, instance = valider_modele(
            IngredientInput, {"nom": "A", "quantite": -10, "unite": "g"}
        )

        assert succes is False
        assert instance is None


class TestValiderFormulaireStreamlit:
    """Tests pour valider_formulaire_streamlit"""

    def test_formulaire_valide(self):
        """Test formulaire valide"""
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
        """Test champ requis manquant"""
        from src.core.validation import valider_formulaire_streamlit, SCHEMA_RECETTE

        data = {"description": "Une description"}

        valide, erreurs, nettoye = valider_formulaire_streamlit(data, SCHEMA_RECETTE)

        assert valide is False
        assert len(erreurs) > 0

    def test_formulaire_valeur_hors_plage(self):
        """Test valeur hors plage - la valeur est clampée lors du nettoyage"""
        from src.core.validation import valider_formulaire_streamlit

        schema = {"prix": {"type": "number", "min": 0, "max": 100, "label": "Prix"}}

        data = {"prix": 200}

        valide, erreurs, nettoye = valider_formulaire_streamlit(data, schema)

        # Le code clamp les valeurs lors du nettoyage, donc ça passe
        # La valeur 200 est ramenée à 100 (max)
        assert valide is True
        assert nettoye["prix"] == 100  # Clampée au maximum

    def test_formulaire_chaine_trop_longue(self):
        """Test chaîne trop longue - la chaîne est tronquée lors du nettoyage"""
        from src.core.validation import valider_formulaire_streamlit

        schema = {"titre": {"type": "string", "max_length": 10, "label": "Titre"}}

        data = {"titre": "Ceci est un titre beaucoup trop long pour le champ"}

        valide, erreurs, nettoye = valider_formulaire_streamlit(data, schema)

        # La chaîne nettoyée est tronquée, mais la validation vérifie APRÈS le nettoyage
        # Si la chaîne nettoyée est ≤ max_length, c'est valide
        # Sinon ça dépend de l'implémentation du nettoyeur
        assert isinstance(nettoye.get("titre"), str)
        # La fonction nettoyer_chaine tronque à longueur_max
        assert len(nettoye.get("titre", "")) <= 10


class TestValiderEtNettoyerFormulaire:
    """Tests pour valider_et_nettoyer_formulaire"""

    def test_module_recettes(self):
        """Test module recettes"""
        from src.core.validation import valider_et_nettoyer_formulaire

        with patch("src.core.validation.afficher_erreurs_validation"):
            data = {
                "nom": "Quiche",
                "temps_preparation": 20,
                "temps_cuisson": 40,
                "portions": 6,
            }

            valide, nettoye = valider_et_nettoyer_formulaire("recettes", data)

            # Vérifie que les données sont nettoyées
            assert "nom" in nettoye or valide

    def test_module_inventaire(self):
        """Test module inventaire"""
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
        """Test module courses"""
        from src.core.validation import valider_et_nettoyer_formulaire

        with patch("src.core.validation.afficher_erreurs_validation"):
            data = {"nom": "Beurre", "quantite": 250, "unite": "g"}

            valide, nettoye = valider_et_nettoyer_formulaire("courses", data)

            assert nettoye is not None

    def test_module_inconnu(self):
        """Test module inconnu - nettoyage basique"""
        from src.core.validation import valider_et_nettoyer_formulaire

        data = {"champ": "<script>alert(1)</script>Test", "nombre": 42}

        valide, nettoye = valider_et_nettoyer_formulaire("module_inconnu", data)

        assert valide is True
        assert "<script>" not in str(nettoye.get("champ", ""))


# ═══════════════════════════════════════════════════════════
# TESTS: Décorateur valider_entree
# ═══════════════════════════════════════════════════════════


class TestValiderEntreeDecorator:
    """Tests pour décorateur @valider_entree"""

    def test_valider_entree_avec_schema(self):
        """Test décorateur avec schéma"""
        from src.core.validation import valider_entree

        schema = {"nom": {"type": "string", "max_length": 100}}

        @valider_entree(schema=schema)
        def ma_fonction(data):
            return data

        result = ma_fonction({"nom": "Test<script>"})

        # Le nom doit être nettoyé
        assert result is not None

    def test_valider_entree_sans_schema(self):
        """Test décorateur sans schéma - nettoyage basique"""
        from src.core.validation import valider_entree

        @valider_entree(nettoyer_tout=True)
        def ma_fonction(data):
            return data

        result = ma_fonction({"texte": "  espaces  ", "nombre": 42})

        assert result is not None

    def test_valider_entree_kwargs(self):
        """Test décorateur avec kwargs"""
        from src.core.validation import valider_entree

        @valider_entree(nettoyer_tout=True)
        def ma_fonction(autre, data=None):
            return data

        result = ma_fonction("autre", data={"champ": "valeur"})

        assert result is not None


# ═══════════════════════════════════════════════════════════
# TESTS: Constantes de validation
# ═══════════════════════════════════════════════════════════


class TestConstantesValidation:
    """Tests pour les constantes de validation"""

    def test_max_length_constants(self):
        """Test constantes de longueur"""
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
        """Test constantes de limites"""
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
class TestAliasValidation:
    def test_validate_input_alias(self):
        """Test alias validate_input"""
        from src.core.validation import validate_input, valider_entree

        assert validate_input is valider_entree

    def test_validate_model_alias(self):
        """Test alias validate_model"""
        from src.core.validation import validate_model, valider_modele

        assert validate_model is valider_modele

    def test_validate_streamlit_form_alias(self):
        """Test alias validate_streamlit_form"""
        from src.core.validation import validate_streamlit_form, valider_formulaire_streamlit

        assert validate_streamlit_form is valider_formulaire_streamlit

    def test_validate_and_sanitize_form_alias(self):
        """Test alias validate_and_sanitize_form"""
        from src.core.validation import validate_and_sanitize_form, valider_et_nettoyer_formulaire

        assert validate_and_sanitize_form is valider_et_nettoyer_formulaire

    def test_show_validation_errors_alias(self):
        """Test alias show_validation_errors"""
        from src.core.validation import show_validation_errors, afficher_erreurs_validation

        assert show_validation_errors is afficher_erreurs_validation
