"""
Tests pour src/utils/constants.py
"""
import pytest
import re
from src.utils.constants import (
    DIFFICULTES,
    TYPES_REPAS,
    SAISONS,
    CATEGORIES_INGREDIENTS,
    EMPLACEMENTS,
    UNITES_MESURE,
    PRIORITES_COURSES,
    MAGASINS,
    JOURS_SEMAINE,
    STATUTS_REPAS,
    COLORS,
    STATUT_COLORS,
    DATE_FORMAT_SHORT,
    DATE_FORMAT_MEDIUM,
    DATE_FORMAT_LONG,
    MAX_STRING_LENGTH,
    MAX_TEXT_LENGTH,
    MAX_UPLOAD_SIZE_MB,
    EMAIL_PATTERN,
    PHONE_PATTERN,
)


@pytest.mark.unit
class TestDifficultes:
    """Tests pour DIFFICULTES."""

    def test_difficultes_count(self):
        """3 niveaux de difficulté."""
        assert len(DIFFICULTES) == 3

    def test_difficultes_values(self):
        """Contient les niveaux attendus."""
        assert "facile" in DIFFICULTES
        assert "moyen" in DIFFICULTES
        assert "difficile" in DIFFICULTES


@pytest.mark.unit
class TestTypesRepas:
    """Tests pour TYPES_REPAS."""

    def test_types_repas_count(self):
        """5 types de repas."""
        assert len(TYPES_REPAS) == 5

    def test_types_repas_contains_bebe(self):
        """Inclut le type bébé."""
        assert "bébé" in TYPES_REPAS

    def test_types_repas_contains_main_meals(self):
        """Contient les repas principaux."""
        assert "déjeuner" in TYPES_REPAS
        assert "dîner" in TYPES_REPAS


@pytest.mark.unit
class TestSaisons:
    """Tests pour SAISONS."""

    def test_saisons_count(self):
        """5 saisons (4 + toute_année)."""
        assert len(SAISONS) == 5

    def test_saisons_contains_all_year(self):
        """Inclut toute_année."""
        assert "toute_année" in SAISONS


@pytest.mark.unit
class TestCategoriesIngredients:
    """Tests pour CATEGORIES_INGREDIENTS."""

    def test_categories_not_empty(self):
        """Au moins 5 catégories."""
        assert len(CATEGORIES_INGREDIENTS) >= 5

    def test_categories_contains_basics(self):
        """Contient les catégories de base."""
        assert "Fruits & Légumes" in CATEGORIES_INGREDIENTS
        assert "Produits Laitiers" in CATEGORIES_INGREDIENTS
        assert "Surgelés" in CATEGORIES_INGREDIENTS


@pytest.mark.unit
class TestEmplacements:
    """Tests pour EMPLACEMENTS."""

    def test_emplacements_contains_frigo(self):
        """Contient le frigo."""
        assert "Frigo" in EMPLACEMENTS

    def test_emplacements_contains_congelateur(self):
        """Contient le congélateur."""
        assert "Congélateur" in EMPLACEMENTS


@pytest.mark.unit
class TestUnitesMesure:
    """Tests pour UNITES_MESURE."""

    def test_unites_contains_kg(self):
        """Contient kg."""
        assert "kg" in UNITES_MESURE

    def test_unites_contains_pieces(self):
        """Contient pcs."""
        assert "pcs" in UNITES_MESURE


@pytest.mark.unit
class TestMagasins:
    """Tests pour MAGASINS."""

    def test_magasins_not_empty(self):
        """Liste non vide."""
        assert len(MAGASINS) > 0

    def test_magasins_carrefour_has_color(self):
        """Carrefour a une couleur."""
        assert "Carrefour" in MAGASINS


@pytest.mark.unit
class TestJoursSemaine:
    """Tests pour JOURS_SEMAINE."""

    def test_jours_count(self):
        """7 jours."""
        assert len(JOURS_SEMAINE) == 7

    def test_jours_starts_lundi(self):
        """Commence par Lundi."""
        assert JOURS_SEMAINE[0] == "Lundi"

    def test_jours_ends_dimanche(self):
        """Termine par Dimanche."""
        assert JOURS_SEMAINE[-1] == "Dimanche"


@pytest.mark.unit
class TestStatutsRepas:
    """Tests pour STATUTS_REPAS."""

    def test_statuts_count(self):
        """4 statuts."""
        assert len(STATUTS_REPAS) == 4

    def test_statuts_contains_planifie(self):
        """Contient planifié."""
        assert "planifié" in STATUTS_REPAS


@pytest.mark.unit
class TestColors:
    """Tests pour COLORS."""

    def test_colors_has_success(self):
        """Contient success."""
        assert "success" in COLORS

    def test_colors_has_error(self):
        """Contient error."""
        assert "error" in COLORS

    def test_colors_are_hex(self):
        """Les couleurs sont en format hex."""
        for name, color in COLORS.items():
            assert color.startswith("#"), f"{name} should be hex"


@pytest.mark.unit
class TestStatutColors:
    """Tests pour STATUT_COLORS."""

    def test_statut_colors_has_ok(self):
        """Contient ok."""
        assert "ok" in STATUT_COLORS

    def test_statut_colors_has_critique(self):
        """Contient critique."""
        assert "critique" in STATUT_COLORS


@pytest.mark.unit
class TestDateFormats:
    """Tests pour les formats de date."""

    def test_date_format_short(self):
        """Format court contient jour et mois."""
        assert "%d" in DATE_FORMAT_SHORT
        assert "%m" in DATE_FORMAT_SHORT

    def test_date_format_medium(self):
        """Format medium contient l'année."""
        assert "%Y" in DATE_FORMAT_MEDIUM

    def test_date_format_long(self):
        """Format long contient le mois en lettres."""
        assert "%B" in DATE_FORMAT_LONG


@pytest.mark.unit
class TestLimites:
    """Tests pour les limites."""

    def test_max_string_length_positive(self):
        """Limite string positive."""
        assert MAX_STRING_LENGTH > 0

    def test_max_text_length_greater_than_string(self):
        """Texte plus long que string."""
        assert MAX_TEXT_LENGTH > MAX_STRING_LENGTH

    def test_max_upload_size_reasonable(self):
        """Taille upload raisonnable (1-100 MB)."""
        assert 1 <= MAX_UPLOAD_SIZE_MB <= 100


@pytest.mark.unit
class TestRegexPatterns:
    """Tests pour les patterns regex."""

    def test_email_pattern_valid_email(self):
        """Pattern email accepte emails valides."""
        assert re.match(EMAIL_PATTERN, "test@example.com")
        assert re.match(EMAIL_PATTERN, "user.name@domain.fr")

    def test_email_pattern_rejects_invalid(self):
        """Pattern email rejette invalides."""
        assert not re.match(EMAIL_PATTERN, "not-an-email")
        assert not re.match(EMAIL_PATTERN, "@nodomain.com")

    def test_phone_pattern_valid_french(self):
        """Pattern téléphone accepte numéros français."""
        assert re.match(PHONE_PATTERN, "0612345678")
        assert re.match(PHONE_PATTERN, "06 12 34 56 78")
        assert re.match(PHONE_PATTERN, "+33612345678")

    def test_phone_pattern_rejects_invalid(self):
        """Pattern téléphone rejette invalides."""
        assert not re.match(PHONE_PATTERN, "123")
        assert not re.match(PHONE_PATTERN, "abcdefghij")

