"""
Tests pour src/utils/validators/common.py
"""
import pytest
from src.utils.validators.common import (
    valider_email,
    valider_telephone,
    borner,
    valider_plage,
    valider_longueur_texte,
    valider_champs_requis,
    valider_choix,
    valider_url,
)


class TestValiderEmail:
    """Tests pour valider_email."""

    def test_valid_email_simple(self):
        """Email simple valide."""
        assert valider_email("test@example.com") is True

    def test_valid_email_subdomain(self):
        """Email avec sous-domaine."""
        assert valider_email("user@mail.example.com") is True

    def test_valid_email_plus_sign(self):
        """Email avec +."""
        assert valider_email("user+tag@example.com") is True

    def test_invalid_email_no_at(self):
        """Sans @ invalide."""
        assert valider_email("testexample.com") is False

    def test_invalid_email_no_domain(self):
        """Sans domaine invalide."""
        assert valider_email("test@") is False

    def test_invalid_email_empty(self):
        """Email vide invalide."""
        assert valider_email("") is False

    def test_invalid_email_spaces(self):
        """Email avec espaces invalide."""
        assert valider_email("test @example.com") is False


class TestValiderTelephone:
    """Tests pour valider_telephone."""

    def test_valid_phone_french(self):
        """Numéro français valide."""
        assert valider_telephone("0612345678") is True

    def test_valid_phone_with_spaces(self):
        """Numéro avec espaces."""
        assert valider_telephone("06 12 34 56 78") is True

    def test_valid_phone_international(self):
        """Numéro international."""
        assert valider_telephone("+33612345678") is True

    def test_invalid_phone_short(self):
        """Numéro trop court."""
        assert valider_telephone("0612") is False

    def test_invalid_phone_letters(self):
        """Numéro avec lettres."""
        assert valider_telephone("06123abc78") is False

    def test_invalid_phone_empty(self):
        """Numéro vide."""
        assert valider_telephone("") is False


class TestBorner:
    """Tests pour borner."""

    def test_borner_in_range(self):
        """Valeur dans la plage."""
        assert borner(5, 0, 10) == 5

    def test_borner_below_min(self):
        """Valeur sous le minimum."""
        assert borner(-5, 0, 10) == 0

    def test_borner_above_max(self):
        """Valeur au-dessus du maximum."""
        assert borner(15, 0, 10) == 10

    def test_borner_at_min(self):
        """Valeur égale au minimum."""
        assert borner(0, 0, 10) == 0

    def test_borner_at_max(self):
        """Valeur égale au maximum."""
        assert borner(10, 0, 10) == 10

    def test_borner_floats(self):
        """Borner avec floats."""
        assert borner(5.5, 0.0, 10.0) == 5.5
        assert borner(-0.1, 0.0, 1.0) == 0.0


class TestValiderPlage:
    """Tests pour valider_plage (retourne tuple[bool, str])."""

    def test_valider_plage_valid(self):
        """Valeur dans la plage."""
        is_valid, msg = valider_plage(5, 0, 10)
        assert is_valid is True
        assert msg == ""

    def test_valider_plage_invalid_low(self):
        """Valeur trop basse."""
        is_valid, msg = valider_plage(-1, 0, 10)
        assert is_valid is False
        assert "0" in msg

    def test_valider_plage_invalid_high(self):
        """Valeur trop haute."""
        is_valid, msg = valider_plage(11, 0, 10)
        assert is_valid is False
        assert "10" in msg

    def test_valider_plage_boundaries(self):
        """Valeurs aux bornes (inclusif)."""
        is_valid_min, _ = valider_plage(0, 0, 10)
        is_valid_max, _ = valider_plage(10, 0, 10)
        assert is_valid_min is True
        assert is_valid_max is True


class TestValiderLongueurTexte:
    """Tests pour valider_longueur_texte (retourne tuple[bool, str])."""

    def test_valider_longueur_valid(self):
        """Longueur valide."""
        is_valid, msg = valider_longueur_texte("hello", min_length=1, max_length=10)
        assert is_valid is True
        assert msg == ""

    def test_valider_longueur_too_short(self):
        """Trop court."""
        is_valid, msg = valider_longueur_texte("ab", min_length=3)
        assert is_valid is False
        assert "3" in msg

    def test_valider_longueur_too_long(self):
        """Trop long."""
        is_valid, msg = valider_longueur_texte("hello world", max_length=5)
        assert is_valid is False

    def test_valider_longueur_exact_min(self):
        """Exactement le minimum."""
        is_valid, _ = valider_longueur_texte("abc", min_length=3)
        assert is_valid is True

    def test_valider_longueur_exact_max(self):
        """Exactement le maximum."""
        is_valid, _ = valider_longueur_texte("abcde", max_length=5)
        assert is_valid is True

    def test_valider_longueur_empty(self):
        """Chaîne vide."""
        is_valid_fail, _ = valider_longueur_texte("", min_length=1)
        is_valid_ok, _ = valider_longueur_texte("", min_length=0)
        assert is_valid_fail is False
        assert is_valid_ok is True

    def test_valider_longueur_not_string(self):
        """Pas une chaîne."""
        is_valid, msg = valider_longueur_texte(123, min_length=1)
        assert is_valid is False
        assert "texte" in msg


class TestValiderChampsRequis:
    """Tests pour valider_champs_requis avec données recettes."""

    def test_recette_complete(self):
        """Recette avec tous champs requis."""
        recette = {"nom": "Gâteau au chocolat", "temps_preparation": 30}
        is_valid, missing = valider_champs_requis(recette, ["nom", "temps_preparation"])
        assert is_valid is True
        assert missing == []

    def test_recette_nom_manquant(self):
        """Recette sans nom."""
        recette = {"temps_preparation": 30}
        is_valid, missing = valider_champs_requis(recette, ["nom", "temps_preparation"])
        assert is_valid is False
        assert "nom" in missing

    def test_recette_champs_vides(self):
        """Recette avec champs vides."""
        recette = {"nom": "", "temps_preparation": None}
        is_valid, missing = valider_champs_requis(recette, ["nom", "temps_preparation"])
        assert is_valid is False
        assert "nom" in missing
        assert "temps_preparation" in missing

    def test_ingredient_complet(self):
        """Ingrédient avec tous champs."""
        ingredient = {"nom": "Farine", "quantite": 500, "unite": "g"}
        is_valid, missing = valider_champs_requis(ingredient, ["nom", "quantite"])
        assert is_valid is True
        assert missing == []

    def test_ingredient_sans_quantite(self):
        """Ingrédient sans quantité."""
        ingredient = {"nom": "Sel"}
        is_valid, missing = valider_champs_requis(ingredient, ["nom", "quantite"])
        assert is_valid is False
        assert "quantite" in missing

    def test_aucun_champ_requis(self):
        """Aucun champ requis."""
        data = {}
        is_valid, missing = valider_champs_requis(data, [])
        assert is_valid is True
        assert missing == []


class TestValiderChoix:
    """Tests pour valider_choix avec choix cuisine."""

    def test_difficulte_valide(self):
        """Difficulté valide."""
        is_valid, msg = valider_choix("facile", ["facile", "moyen", "difficile"])
        assert is_valid is True
        assert msg == ""

    def test_difficulte_invalide(self):
        """Difficulté invalide."""
        is_valid, msg = valider_choix("expert", ["facile", "moyen", "difficile"])
        assert is_valid is False
        assert "facile" in msg

    def test_type_repas_valide(self):
        """Type de repas valide."""
        is_valid, _ = valider_choix("déjeuner", ["petit-déjeuner", "déjeuner", "dîner", "goûter"])
        assert is_valid is True

    def test_saison_valide(self):
        """Saison valide."""
        is_valid, _ = valider_choix("été", ["printemps", "été", "automne", "hiver"])
        assert is_valid is True

    def test_unite_valide(self):
        """Unité de mesure valide."""
        is_valid, _ = valider_choix("g", ["g", "kg", "mL", "L", "pcs"])
        assert is_valid is True

    def test_unite_invalide(self):
        """Unité de mesure invalide."""
        is_valid, msg = valider_choix("litres", ["g", "kg", "mL", "L", "pcs"])
        assert is_valid is False


class TestValiderUrl:
    """Tests pour valider_url avec URLs images recettes."""

    def test_url_https_valide(self):
        """URL HTTPS valide."""
        assert valider_url("https://example.com/recette.jpg") is True

    def test_url_http_valide(self):
        """URL HTTP valide."""
        assert valider_url("http://images.cuisine.fr/plat.png") is True

    def test_url_avec_path(self):
        """URL avec chemin."""
        assert valider_url("https://cdn.recettes.com/images/tarte-pommes.jpg") is True

    def test_url_sous_domaine(self):
        """URL avec sous-domaine."""
        assert valider_url("https://images.cdn.marmiton.org/photo.jpg") is True

    def test_url_sans_protocole(self):
        """URL sans protocole invalide."""
        assert valider_url("example.com/image.jpg") is False

    def test_url_ftp_invalide(self):
        """URL FTP invalide."""
        assert valider_url("ftp://files.example.com/doc.pdf") is False

    def test_url_vide(self):
        """URL vide invalide."""
        assert valider_url("") is False

    def test_url_invalide(self):
        """URL invalide."""
        assert valider_url("pas une url") is False
