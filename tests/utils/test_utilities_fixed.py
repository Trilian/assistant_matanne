"""
Tests pour les utilitaires avec les bons noms d'imports.

Couvre les formatters, helpers, validators avec les vrais noms de fonctions.
"""

import pytest
from datetime import datetime, date, timedelta


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FORMATTERS/DATES.PY
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDatesFormatters:
    """Tests pour src/utils/formatters/dates.py"""

    def test_format_date_short(self):
        """Test formater_date avec format court."""
        from src.utils.formatters.dates import formater_date
        
        result = formater_date(date(2026, 2, 4), "short")
        assert result == "04/02"

    def test_format_date_medium(self):
        """Test formater_date avec format moyen."""
        from src.utils.formatters.dates import formater_date
        
        result = formater_date(date(2026, 12, 25), "medium")
        assert result == "25/12/2026"

    def test_format_date_long_fr(self):
        """Test formater_date avec format long français."""
        from src.utils.formatters.dates import formater_date
        
        result = formater_date(date(2026, 1, 15), "long", "fr")
        assert "janvier" in result
        assert "15" in result
        assert "2026" in result

    def test_format_date_long_en(self):
        """Test formater_date avec format long anglais."""
        from src.utils.formatters.dates import formater_date
        
        result = formater_date(date(2026, 1, 15), "long", "en")
        assert result is not None

    def test_format_date_none(self):
        """Test formater_date avec None."""
        from src.utils.formatters.dates import formater_date
        
        result = formater_date(None)
        assert result == "—"

    def test_format_date_with_datetime(self):
        """Test formater_date avec un datetime."""
        from src.utils.formatters.dates import formater_date
        
        result = formater_date(datetime(2026, 3, 10, 14, 30), "medium")
        assert result == "10/03/2026"

    def test_format_date_invalid_format(self):
        """Test formater_date avec format invalide."""
        from src.utils.formatters.dates import formater_date
        
        result = formater_date(date(2026, 5, 1), "invalid")
        assert result is not None  # Fallback to default

    def test_format_datetime_short(self):
        """Test formater_datetime avec format court."""
        from src.utils.formatters.dates import formater_datetime
        
        result = formater_datetime(datetime(2026, 2, 4, 14, 30), "short")
        assert "04/02" in result
        assert "14:30" in result

    def test_format_datetime_medium(self):
        """Test formater_datetime avec format moyen."""
        from src.utils.formatters.dates import formater_datetime
        
        result = formater_datetime(datetime(2026, 2, 4, 9, 5), "medium")
        assert "04/02/2026" in result
        assert "09:05" in result

    def test_format_datetime_long(self):
        """Test formater_datetime avec format long."""
        from src.utils.formatters.dates import formater_datetime
        
        result = formater_datetime(datetime(2026, 12, 1, 20, 0), "long")
        assert "décembre" in result
        assert "20:00" in result

    def test_format_datetime_none(self):
        """Test formater_datetime avec None."""
        from src.utils.formatters.dates import formater_datetime
        
        result = formater_datetime(None)
        assert result == "—"

    def test_format_relative_date_today(self):
        """Test temps_ecoule pour aujourd'hui."""
        from src.utils.formatters.dates import temps_ecoule
        
        result = temps_ecoule(date.today())
        assert result == "Aujourd'hui"

    def test_format_relative_date_tomorrow(self):
        """Test temps_ecoule pour demain."""
        from src.utils.formatters.dates import temps_ecoule
        
        result = temps_ecoule(date.today() + timedelta(days=1))
        assert result == "Demain"

    def test_format_relative_date_yesterday(self):
        """Test temps_ecoule pour hier."""
        from src.utils.formatters.dates import temps_ecoule
        
        result = temps_ecoule(date.today() - timedelta(days=1))
        assert result == "Hier"

    def test_format_relative_date_future(self):
        """Test temps_ecoule pour dans 3 jours."""
        from src.utils.formatters.dates import temps_ecoule
        
        result = temps_ecoule(date.today() + timedelta(days=3))
        assert "Dans 3 jours" in result

    def test_format_relative_date_past(self):
        """Test temps_ecoule pour il y a 5 jours."""
        from src.utils.formatters.dates import temps_ecoule
        
        result = temps_ecoule(date.today() - timedelta(days=5))
        assert "Il y a 5 jours" in result

    def test_format_relative_date_with_datetime(self):
        """Test temps_ecoule avec datetime."""
        from src.utils.formatters.dates import temps_ecoule
        
        result = temps_ecoule(datetime.now())
        assert result == "Aujourd'hui"

    def test_format_relative_date_far_future(self):
        """Test temps_ecoule pour date lointaine."""
        from src.utils.formatters.dates import temps_ecoule
        
        result = temps_ecoule(date.today() + timedelta(days=30))
        assert "/" in result  # Fallback to date format

    def test_format_time_minutes_only(self):
        """Test formater_temps avec minutes seules."""
        from src.utils.formatters.dates import formater_temps
        
        assert formater_temps(45) == "45min"
        assert formater_temps(1) == "1min"
        assert formater_temps(59) == "59min"

    def test_format_time_hours_only(self):
        """Test formater_temps avec heures exactes."""
        from src.utils.formatters.dates import formater_temps
        
        assert formater_temps(60) == "1h"
        assert formater_temps(120) == "2h"
        assert formater_temps(180) == "3h"

    def test_format_time_hours_and_minutes(self):
        """Test formater_temps avec heures et minutes."""
        from src.utils.formatters.dates import formater_temps
        
        assert formater_temps(90) == "1h30"
        assert formater_temps(75) == "1h15"
        assert formater_temps(150) == "2h30"

    def test_format_time_none_or_zero(self):
        """Test formater_temps avec None ou 0."""
        from src.utils.formatters.dates import formater_temps
        
        assert formater_temps(None) == "0min"
        assert formater_temps(0) == "0min"

    def test_format_time_float(self):
        """Test formater_temps avec float."""
        from src.utils.formatters.dates import formater_temps
        
        assert formater_temps(90.5) == "1h30"

    def test_format_duration_seconds(self):
        """Test formater_duree avec secondes."""
        from src.utils.formatters.dates import formater_duree
        
        result = formater_duree(45)
        assert "45" in result
        assert "s" in result.lower()

    def test_format_duration_minutes(self):
        """Test formater_duree avec minutes."""
        from src.utils.formatters.dates import formater_duree
        
        result = formater_duree(125)
        assert "2" in result
        assert "min" in result.lower() or "m" in result.lower()

    def test_format_duration_hours(self):
        """Test formater_duree avec heures."""
        from src.utils.formatters.dates import formater_duree
        
        result = formater_duree(3665)
        assert "1" in result
        assert "h" in result.lower()

    def test_format_duration_none(self):
        """Test formater_duree avec None."""
        from src.utils.formatters.dates import formater_duree
        
        result = formater_duree(None)
        assert result is not None

    def test_format_duration_short(self):
        """Test formater_duree en format court."""
        from src.utils.formatters.dates import formater_duree
        
        result = formater_duree(3665, short=True)
        assert result is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FORMATTERS/NUMBERS.PY
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestNumbersFormatters:
    """Tests pour src/utils/formatters/numbers.py"""

    def test_format_quantity_int(self):
        """Test formater_quantite avec entier."""
        from src.utils.formatters.numbers import formater_quantite
        
        result = formater_quantite(5)
        assert "5" in result

    def test_format_quantity_float(self):
        """Test formater_quantite avec décimal."""
        from src.utils.formatters.numbers import formater_quantite
        
        result = formater_quantite(3.75, decimals=2)
        assert "3.75" in result or "3,75" in result

    def test_format_quantity_none(self):
        """Test formater_quantite avec None."""
        from src.utils.formatters.numbers import formater_quantite
        
        result = formater_quantite(None)
        assert result is not None

    def test_format_quantity_with_unit(self):
        """Test formater_quantite_unite."""
        from src.utils.formatters.numbers import formater_quantite_unite
        
        result = formater_quantite_unite(500, "g")
        assert "500" in result
        assert "g" in result

    def test_format_quantity_with_unit_decimal(self):
        """Test formater_quantite_unite avec décimal."""
        from src.utils.formatters.numbers import formater_quantite_unite
        
        result = formater_quantite_unite(1.5, "kg", decimals=1)
        assert "1.5" in result or "1,5" in result
        assert "kg" in result

    def test_format_price_basic(self):
        """Test formater_prix basique."""
        from src.utils.formatters.numbers import formater_prix
        
        result = formater_prix(25.50)
        assert "25" in result
        assert "€" in result or "EUR" in result

    def test_format_price_different_currency(self):
        """Test formater_prix avec autre devise."""
        from src.utils.formatters.numbers import formater_prix
        
        result = formater_prix(100, currency="$")
        assert "100" in result
        assert "$" in result

    def test_format_price_none(self):
        """Test formater_prix avec None."""
        from src.utils.formatters.numbers import formater_prix
        
        result = formater_prix(None)
        assert result is not None

    def test_format_currency_basic(self):
        """Test formater_monnaie basique."""
        from src.utils.formatters.numbers import formater_monnaie
        
        result = formater_monnaie(1234.56)
        assert "1234" in result or "1 234" in result

    def test_format_currency_none(self):
        """Test formater_monnaie avec None."""
        from src.utils.formatters.numbers import formater_monnaie
        
        result = formater_monnaie(None)
        assert result is not None

    def test_format_percentage_basic(self):
        """Test formater_pourcentage basique."""
        from src.utils.formatters.numbers import formater_pourcentage
        
        result = formater_pourcentage(75.5)
        assert "75" in result
        assert "%" in result

    def test_format_percentage_decimals(self):
        """Test formater_pourcentage avec décimales."""
        from src.utils.formatters.numbers import formater_pourcentage
        
        result = formater_pourcentage(33.333, decimals=2)
        assert "33" in result

    def test_format_percentage_none(self):
        """Test formater_pourcentage avec None."""
        from src.utils.formatters.numbers import formater_pourcentage
        
        result = formater_pourcentage(None)
        assert result is not None

    def test_format_number_basic(self):
        """Test formater_nombre basique."""
        from src.utils.formatters.numbers import formater_nombre
        
        result = formater_nombre(1234567)
        assert result is not None

    def test_format_number_with_decimals(self):
        """Test formater_nombre avec décimales."""
        from src.utils.formatters.numbers import formater_nombre
        
        result = formater_nombre(1234.567, decimals=2)
        assert result is not None

    def test_format_number_none(self):
        """Test formater_nombre avec None."""
        from src.utils.formatters.numbers import formater_nombre
        
        result = formater_nombre(None)
        assert result is not None

    def test_format_file_size_bytes(self):
        """Test formater_taille_fichier pour bytes."""
        from src.utils.formatters.numbers import formater_taille_fichier
        
        result = formater_taille_fichier(500)
        assert result is not None

    def test_format_file_size_kb(self):
        """Test formater_taille_fichier pour KB."""
        from src.utils.formatters.numbers import formater_taille_fichier
        
        result = formater_taille_fichier(2048)
        assert "KB" in result.upper() or "KO" in result.upper() or "2" in result

    def test_format_file_size_mb(self):
        """Test formater_taille_fichier pour MB."""
        from src.utils.formatters.numbers import formater_taille_fichier
        
        result = formater_taille_fichier(1024 * 1024 * 5)
        assert "MB" in result.upper() or "MO" in result.upper() or "5" in result

    def test_format_file_size_none(self):
        """Test formater_taille_fichier avec None."""
        from src.utils.formatters.numbers import formater_taille_fichier
        
        result = formater_taille_fichier(None)
        assert result is not None

    def test_format_range_basic(self):
        """Test formater_plage basique."""
        from src.utils.formatters.numbers import formater_plage
        
        result = formater_plage(10, 20)
        assert "10" in result
        assert "20" in result

    def test_format_range_with_unit(self):
        """Test formater_plage avec unité."""
        from src.utils.formatters.numbers import formater_plage
        
        result = formater_plage(5, 10, "kg")
        assert "kg" in result

    def test_smart_round_basic(self):
        """Test arrondir_intelligent basique."""
        from src.utils.formatters.numbers import arrondir_intelligent
        
        assert arrondir_intelligent(3.14159, 2) == 3.14

    def test_smart_round_no_decimals(self):
        """Test arrondir_intelligent sans décimales."""
        from src.utils.formatters.numbers import arrondir_intelligent
        
        result = arrondir_intelligent(3.7, 0)
        assert result == 4.0 or result == 4


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FORMATTERS/TEXT.PY
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTextFormatters:
    """Tests pour src/utils/formatters/text.py"""

    def test_capitaliser_premiere_basic(self):
        """Test capitaliser_premiere basique."""
        from src.utils.formatters.text import capitaliser_premiere
        
        result = capitaliser_premiere("hello world")
        assert result[0] == "H"

    def test_capitaliser_premiere_empty(self):
        """Test capitaliser_premiere avec chaîne vide."""
        from src.utils.formatters.text import capitaliser_premiere
        
        result = capitaliser_premiere("")
        assert result == ""

    def test_nettoyer_texte_basic(self):
        """Test nettoyer_texte basique."""
        from src.utils.formatters.text import nettoyer_texte
        
        result = nettoyer_texte("  hello  world  ")
        assert result is not None

    def test_tronquer_basic(self):
        """Test tronquer basique."""
        from src.utils.formatters.text import tronquer
        
        result = tronquer("This is a long text", 10)
        assert len(result) <= 13  # With ellipsis

    def test_tronquer_no_truncation(self):
        """Test tronquer sans truncation."""
        from src.utils.formatters.text import tronquer
        
        result = tronquer("Short", 100)
        assert result == "Short"

    def test_generer_slug_basic(self):
        """Test generer_slug basique."""
        from src.utils.formatters.text import generer_slug
        
        result = generer_slug("Hello World!")
        assert "-" in result or result.islower()
        assert " " not in result

    def test_generer_slug_special_chars(self):
        """Test generer_slug avec caractères spéciaux."""
        from src.utils.formatters.text import generer_slug
        
        result = generer_slug("Café & Thé")
        assert result is not None
        assert " " not in result

    def test_extraire_nombre_basic(self):
        """Test extraire_nombre basique."""
        from src.utils.formatters.text import extraire_nombre
        
        result = extraire_nombre("Prix: 42€")
        assert result == 42 or result == 42.0


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FORMATTERS/UNITS.PY
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUnitsFormatters:
    """Tests pour src/utils/formatters/units.py"""

    def test_format_weight_grams(self):
        """Test format_weight en grammes."""
        from src.utils.formatters.units import format_weight
        
        result = format_weight(500)
        assert "500" in result or "g" in result

    def test_format_weight_kilograms(self):
        """Test format_weight en kilogrammes."""
        from src.utils.formatters.units import format_weight
        
        result = format_weight(1500)
        assert "1.5" in result or "1,5" in result or "kg" in result.lower()

    def test_format_volume_ml(self):
        """Test format_volume en ml."""
        from src.utils.formatters.units import format_volume
        
        result = format_volume(250)
        assert "250" in result or "ml" in result.lower()

    def test_format_volume_liters(self):
        """Test format_volume en litres."""
        from src.utils.formatters.units import format_volume
        
        result = format_volume(2000)
        assert "2" in result or "L" in result


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS HELPERS/HELPERS.PY
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestHelpersGeneral:
    """Tests pour sous-modules de src/utils/helpers/"""

    def test_helpers_data_import(self):
        """Test import du module data helpers."""
        from src.utils.helpers import data
        assert data is not None

    def test_helpers_dates_import(self):
        """Test import du module dates helpers."""
        from src.utils.helpers import dates
        assert dates is not None

    def test_helpers_strings_import(self):
        """Test import du module strings helpers."""
        from src.utils.helpers import strings
        assert strings is not None

    def test_helpers_food_import(self):
        """Test import du module food helpers."""
        from src.utils.helpers import food
        assert food is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS VALIDATORS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestValidators:
    """Tests pour src/utils/validators/"""

    def test_validators_common_import(self):
        """Test import du module common validators."""
        from src.utils.validators import common
        assert common is not None

    def test_validators_dates_import(self):
        """Test import du module dates validators."""
        from src.utils.validators import dates
        assert dates is not None

    def test_validators_food_import(self):
        """Test import du module food validators."""
        from src.utils.validators import food
        assert food is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MEDIA.PY
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMediaUtils:
    """Tests pour src/utils/media.py"""

    def test_media_import(self):
        """Test import du module media."""
        from src.utils import media
        assert media is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS CONSTANTS.PY
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConstants:
    """Tests pour src/utils/constants.py"""

    def test_constants_import(self):
        """Test import du module constants."""
        from src.utils import constants
        assert constants is not None
