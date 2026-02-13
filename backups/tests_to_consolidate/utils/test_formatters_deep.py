"""
Tests approfondis pour src/utils/formatters/
Objectif: Atteindre 80%+ de couverture

Couvre:
- dates.py: format_date, format_datetime, format_relative_date, format_time, format_duration
- numbers.py: format_quantity, format_price, format_currency, format_percentage, format_number, etc.
- text.py: truncate, clean_text, slugify, extract_number, capitalize_first
- units.py: format_weight, format_volume
"""

from datetime import date, datetime, timedelta

import pytest

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMATTERS DATES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormatDate:
    """Tests pour format_date"""

    def test_format_date_short(self):
        """Test format court"""
        from src.utils.formatters.dates import format_date

        result = format_date(date(2025, 12, 1), "short")
        assert result == "01/12"

    def test_format_date_medium(self):
        """Test format moyen"""
        from src.utils.formatters.dates import format_date

        result = format_date(date(2025, 12, 1), "medium")
        assert result == "01/12/2025"

    def test_format_date_long_fr(self):
        """Test format long franÃ§ais"""
        from src.utils.formatters.dates import format_date

        result = format_date(date(2025, 12, 1), "long", "fr")
        assert result == "1 dÃ©cembre 2025"

    def test_format_date_long_en(self):
        """Test format long anglais"""
        from src.utils.formatters.dates import format_date

        result = format_date(date(2025, 12, 1), "long", "en")
        assert "December" in result or "12" in result

    def test_format_date_defaut(self):
        """Test format par dÃ©faut"""
        from src.utils.formatters.dates import format_date

        result = format_date(date(2025, 12, 1), "unknown")
        assert result == "01/12/2025"

    def test_format_date_none(self):
        """Test avec None"""
        from src.utils.formatters.dates import format_date

        result = format_date(None)
        assert result == "â€”"

    def test_format_date_datetime_input(self):
        """Test avec datetime au lieu de date"""
        from src.utils.formatters.dates import format_date

        result = format_date(datetime(2025, 12, 1, 14, 30), "short")
        assert result == "01/12"

    @pytest.mark.parametrize(
        "month,expected",
        [
            (1, "janvier"),
            (2, "fÃ©vrier"),
            (3, "mars"),
            (4, "avril"),
            (5, "mai"),
            (6, "juin"),
            (7, "juillet"),
            (8, "aoÃ»t"),
            (9, "septembre"),
            (10, "octobre"),
            (11, "novembre"),
            (12, "dÃ©cembre"),
        ],
    )
    def test_format_date_tous_les_mois(self, month, expected):
        """Test tous les mois en franÃ§ais"""
        from src.utils.formatters.dates import format_date

        result = format_date(date(2025, month, 15), "long", "fr")
        assert expected in result


class TestFormatDatetime:
    """Tests pour format_datetime"""

    def test_format_datetime_short(self):
        """Test format court"""
        from src.utils.formatters.dates import format_datetime

        result = format_datetime(datetime(2025, 12, 1, 14, 30), "short")
        assert result == "01/12 14:30"

    def test_format_datetime_medium(self):
        """Test format moyen"""
        from src.utils.formatters.dates import format_datetime

        result = format_datetime(datetime(2025, 12, 1, 14, 30), "medium")
        assert result == "01/12/2025 14:30"

    def test_format_datetime_long(self):
        """Test format long"""
        from src.utils.formatters.dates import format_datetime

        result = format_datetime(datetime(2025, 12, 1, 14, 30), "long", "fr")
        assert "1 dÃ©cembre 2025" in result
        assert "14:30" in result

    def test_format_datetime_defaut(self):
        """Test format par dÃ©faut"""
        from src.utils.formatters.dates import format_datetime

        result = format_datetime(datetime(2025, 12, 1, 14, 30), "unknown")
        assert result == "01/12/2025 14:30"

    def test_format_datetime_none(self):
        """Test avec None"""
        from src.utils.formatters.dates import format_datetime

        result = format_datetime(None)
        assert result == "â€”"


class TestFormatRelativeDate:
    """Tests pour format_relative_date"""

    def test_format_relative_aujourdhui(self):
        """Test aujourd'hui"""
        from src.utils.formatters.dates import format_relative_date

        result = format_relative_date(date.today())
        assert result == "Aujourd'hui"

    def test_format_relative_demain(self):
        """Test demain"""
        from src.utils.formatters.dates import format_relative_date

        result = format_relative_date(date.today() + timedelta(days=1))
        assert result == "Demain"

    def test_format_relative_hier(self):
        """Test hier"""
        from src.utils.formatters.dates import format_relative_date

        result = format_relative_date(date.today() - timedelta(days=1))
        assert result == "Hier"

    def test_format_relative_dans_x_jours(self):
        """Test dans X jours"""
        from src.utils.formatters.dates import format_relative_date

        result = format_relative_date(date.today() + timedelta(days=3))
        assert result == "Dans 3 jours"

    def test_format_relative_il_y_a_x_jours(self):
        """Test il y a X jours"""
        from src.utils.formatters.dates import format_relative_date

        result = format_relative_date(date.today() - timedelta(days=5))
        assert result == "Il y a 5 jours"

    def test_format_relative_plus_de_7_jours(self):
        """Test plus de 7 jours dans le futur"""
        from src.utils.formatters.dates import format_relative_date

        result = format_relative_date(date.today() + timedelta(days=30))
        assert "/" in result  # Format medium

    def test_format_relative_plus_de_7_jours_passe(self):
        """Test plus de 7 jours dans le passÃ©"""
        from src.utils.formatters.dates import format_relative_date

        result = format_relative_date(date.today() - timedelta(days=30))
        assert "/" in result  # Format medium

    def test_format_relative_datetime_input(self):
        """Test avec datetime au lieu de date"""
        from src.utils.formatters.dates import format_relative_date

        result = format_relative_date(datetime.now())
        assert result == "Aujourd'hui"


class TestFormatTime:
    """Tests pour format_time"""

    def test_format_time_minutes(self):
        """Test minutes seules"""
        from src.utils.formatters.dates import format_time

        result = format_time(45)
        assert result == "45min"

    def test_format_time_heures(self):
        """Test heures seules"""
        from src.utils.formatters.dates import format_time

        result = format_time(120)
        assert result == "2h"

    def test_format_time_heures_et_minutes(self):
        """Test heures et minutes"""
        from src.utils.formatters.dates import format_time

        result = format_time(90)
        assert result == "1h30"

    def test_format_time_zero(self):
        """Test zÃ©ro minutes"""
        from src.utils.formatters.dates import format_time

        result = format_time(0)
        assert result == "0min"

    def test_format_time_none(self):
        """Test None"""
        from src.utils.formatters.dates import format_time

        result = format_time(None)
        assert result == "0min"

    def test_format_time_float(self):
        """Test avec float"""
        from src.utils.formatters.dates import format_time

        result = format_time(45.7)
        assert result == "45min"

    def test_format_time_invalide(self):
        """Test avec valeur invalide"""
        from src.utils.formatters.dates import format_time

        result = format_time("invalid")
        assert result == "0min"


class TestFormatDuration:
    """Tests pour format_duration"""

    def test_format_duration_short_seconds(self):
        """Test secondes format court"""
        from src.utils.formatters.dates import format_duration

        result = format_duration(45, short=True)
        assert result == "45s"

    def test_format_duration_short_minutes(self):
        """Test minutes format court"""
        from src.utils.formatters.dates import format_duration

        result = format_duration(90, short=True)
        assert result == "1min 30s"

    def test_format_duration_short_heures(self):
        """Test heures format court"""
        from src.utils.formatters.dates import format_duration

        result = format_duration(3665, short=True)
        assert result == "1h 1min 5s"

    def test_format_duration_long_secondes(self):
        """Test secondes format long"""
        from src.utils.formatters.dates import format_duration

        result = format_duration(1, short=False)
        assert result == "1 seconde"

    def test_format_duration_long_pluriel(self):
        """Test pluriel format long"""
        from src.utils.formatters.dates import format_duration

        result = format_duration(7325, short=False)
        assert "heures" in result
        assert "minutes" in result
        assert "secondes" in result

    def test_format_duration_zero(self):
        """Test zÃ©ro"""
        from src.utils.formatters.dates import format_duration

        result_short = format_duration(0, short=True)
        result_long = format_duration(0, short=False)
        assert result_short == "0s"
        assert result_long == "0 seconde"

    def test_format_duration_none(self):
        """Test None"""
        from src.utils.formatters.dates import format_duration

        result = format_duration(None)
        assert result in ["0s", "0 seconde"]

    def test_format_duration_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.dates import format_duration

        result = format_duration("invalid")
        assert "0" in result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMATTERS NUMBERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormatQuantity:
    """Tests pour format_quantity"""

    def test_format_quantity_entier(self):
        """Test quantitÃ© entiÃ¨re"""
        from src.utils.formatters.numbers import format_quantity

        result = format_quantity(2.0)
        assert result == "2"

    def test_format_quantity_decimal(self):
        """Test quantitÃ© dÃ©cimale"""
        from src.utils.formatters.numbers import format_quantity

        result = format_quantity(2.5)
        assert result == "2.5"

    def test_format_quantity_precision(self):
        """Test prÃ©cision"""
        from src.utils.formatters.numbers import format_quantity

        result = format_quantity(2.123, decimals=2)
        assert result == "2.12"

    def test_format_quantity_zero(self):
        """Test zÃ©ro"""
        from src.utils.formatters.numbers import format_quantity

        result = format_quantity(0)
        assert result == "0"

    def test_format_quantity_none(self):
        """Test None"""
        from src.utils.formatters.numbers import format_quantity

        result = format_quantity(None)
        assert result == "0"

    def test_format_quantity_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.numbers import format_quantity

        result = format_quantity("invalid")
        assert result == "0"

    def test_format_quantity_trailing_zeros(self):
        """Test suppression zeros trailing"""
        from src.utils.formatters.numbers import format_quantity

        result = format_quantity(2.10, decimals=2)
        assert result == "2.1"


class TestFormatQuantityWithUnit:
    """Tests pour format_quantity_with_unit"""

    def test_format_quantity_with_unit_simple(self):
        """Test avec unitÃ©"""
        from src.utils.formatters.numbers import format_quantity_with_unit

        result = format_quantity_with_unit(2.5, "kg")
        assert result == "2.5 kg"

    def test_format_quantity_with_unit_none(self):
        """Test sans unitÃ©"""
        from src.utils.formatters.numbers import format_quantity_with_unit

        result = format_quantity_with_unit(2.5, None)
        assert result == "2.5"

    def test_format_quantity_with_unit_vide(self):
        """Test avec unitÃ© vide"""
        from src.utils.formatters.numbers import format_quantity_with_unit

        result = format_quantity_with_unit(2.5, "")
        assert result == "2.5"

    def test_format_quantity_with_unit_espaces(self):
        """Test avec espaces dans unitÃ©"""
        from src.utils.formatters.numbers import format_quantity_with_unit

        result = format_quantity_with_unit(2.5, "  kg  ")
        assert result == "2.5 kg"


class TestFormatPrice:
    """Tests pour format_price"""

    def test_format_price_entier(self):
        """Test prix entier"""
        from src.utils.formatters.numbers import format_price

        result = format_price(10.0)
        assert result == "10â‚¬"

    def test_format_price_decimal(self):
        """Test prix dÃ©cimal"""
        from src.utils.formatters.numbers import format_price

        result = format_price(10.50)
        assert result == "10.50â‚¬"

    def test_format_price_none(self):
        """Test None"""
        from src.utils.formatters.numbers import format_price

        result = format_price(None)
        assert result == "0â‚¬"

    def test_format_price_custom_currency(self):
        """Test devise personnalisÃ©e"""
        from src.utils.formatters.numbers import format_price

        result = format_price(10, "$")
        assert result == "10$"

    def test_format_price_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.numbers import format_price

        result = format_price("invalid")
        assert result == "0â‚¬"


class TestFormatCurrency:
    """Tests pour format_currency"""

    def test_format_currency_fr(self):
        """Test format franÃ§ais"""
        from src.utils.formatters.numbers import format_currency

        result = format_currency(1234.56, "EUR", "fr_FR")
        assert "1 234,56" in result
        assert "â‚¬" in result

    def test_format_currency_en(self):
        """Test format anglais"""
        from src.utils.formatters.numbers import format_currency

        result = format_currency(1234.56, "USD", "en_US")
        assert "$" in result
        assert "1,234.56" in result

    def test_format_currency_none(self):
        """Test None"""
        from src.utils.formatters.numbers import format_currency

        result = format_currency(None)
        assert "0" in result

    def test_format_currency_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.numbers import format_currency

        result = format_currency("invalid")
        assert "0" in result

    @pytest.mark.parametrize(
        "currency,symbol", [("EUR", "â‚¬"), ("USD", "$"), ("GBP", "Â£"), ("CHF", "CHF")]
    )
    def test_format_currency_symboles(self, currency, symbol):
        """Test diffÃ©rents symboles"""
        from src.utils.formatters.numbers import format_currency

        result = format_currency(100, currency, "fr_FR")
        assert symbol in result


class TestFormatPercentage:
    """Tests pour format_percentage"""

    def test_format_percentage_entier(self):
        """Test pourcentage entier"""
        from src.utils.formatters.numbers import format_percentage

        result = format_percentage(85.0)
        assert result == "85%"

    def test_format_percentage_decimal(self):
        """Test pourcentage dÃ©cimal"""
        from src.utils.formatters.numbers import format_percentage

        result = format_percentage(85.5)
        assert result == "85.5%"

    def test_format_percentage_none(self):
        """Test None"""
        from src.utils.formatters.numbers import format_percentage

        result = format_percentage(None)
        assert result == "0%"

    def test_format_percentage_custom_symbol(self):
        """Test symbole personnalisÃ©"""
        from src.utils.formatters.numbers import format_percentage

        result = format_percentage(85, symbol=" pourcent")
        assert result == "85 pourcent"

    def test_format_percentage_precision(self):
        """Test prÃ©cision"""
        from src.utils.formatters.numbers import format_percentage

        result = format_percentage(85.123, decimals=2)
        assert "85.12" in result

    def test_format_percentage_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.numbers import format_percentage

        result = format_percentage("invalid")
        assert result == "0%"


class TestFormatNumber:
    """Tests pour format_number"""

    def test_format_number_milliers(self):
        """Test sÃ©parateur milliers"""
        from src.utils.formatters.numbers import format_number

        result = format_number(1234567)
        assert result == "1 234 567"

    def test_format_number_decimales(self):
        """Test avec dÃ©cimales"""
        from src.utils.formatters.numbers import format_number

        result = format_number(1234.56, decimals=2)
        assert "1 234" in result
        assert "56" in result

    def test_format_number_none(self):
        """Test None"""
        from src.utils.formatters.numbers import format_number

        result = format_number(None)
        assert result == "0"

    def test_format_number_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.numbers import format_number

        result = format_number("invalid")
        assert result == "0"


class TestFormatFileSize:
    """Tests pour format_file_size"""

    def test_format_file_size_octets(self):
        """Test octets"""
        from src.utils.formatters.numbers import format_file_size

        result = format_file_size(500)
        assert result == "500 o"

    def test_format_file_size_ko(self):
        """Test kilo-octets"""
        from src.utils.formatters.numbers import format_file_size

        result = format_file_size(1024)
        assert result == "1 Ko"

    def test_format_file_size_mo(self):
        """Test mega-octets"""
        from src.utils.formatters.numbers import format_file_size

        result = format_file_size(1048576)
        assert result == "1 Mo"

    def test_format_file_size_go(self):
        """Test giga-octets"""
        from src.utils.formatters.numbers import format_file_size

        result = format_file_size(1073741824)
        assert result == "1 Go"

    def test_format_file_size_zero(self):
        """Test zÃ©ro"""
        from src.utils.formatters.numbers import format_file_size

        result = format_file_size(0)
        assert result == "0 o"

    def test_format_file_size_none(self):
        """Test None"""
        from src.utils.formatters.numbers import format_file_size

        result = format_file_size(None)
        assert result == "0 o"

    def test_format_file_size_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.numbers import format_file_size

        result = format_file_size("invalid")
        assert result == "0 o"


class TestFormatRange:
    """Tests pour format_range"""

    def test_format_range_avec_unite(self):
        """Test avec unitÃ©"""
        from src.utils.formatters.numbers import format_range

        result = format_range(10, 20, "â‚¬")
        assert result == "10-20 â‚¬"

    def test_format_range_sans_unite(self):
        """Test sans unitÃ©"""
        from src.utils.formatters.numbers import format_range

        result = format_range(10, 20)
        assert result == "10-20"

    def test_format_range_decimales(self):
        """Test avec dÃ©cimales"""
        from src.utils.formatters.numbers import format_range

        result = format_range(10.5, 20.5, "kg")
        assert "10.5-20.5 kg" == result


class TestSmartRound:
    """Tests pour smart_round"""

    def test_smart_round_normal(self):
        """Test arrondi normal"""
        from src.utils.formatters.numbers import smart_round

        result = smart_round(2.5000000001)
        assert result == 2.5

    def test_smart_round_precision(self):
        """Test avec prÃ©cision"""
        from src.utils.formatters.numbers import smart_round

        result = smart_round(2.123456, precision=3)
        assert result == 2.123

    def test_smart_round_none(self):
        """Test None"""
        from src.utils.formatters.numbers import smart_round

        result = smart_round(None)
        assert result == 0.0

    def test_smart_round_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.numbers import smart_round

        result = smart_round("invalid")
        assert result == 0.0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMATTERS TEXT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTruncate:
    """Tests pour truncate"""

    def test_truncate_court(self):
        """Test texte plus court que limite"""
        from src.utils.formatters.text import truncate

        result = truncate("Hello", length=10)
        assert result == "Hello"

    def test_truncate_long(self):
        """Test texte plus long que limite"""
        from src.utils.formatters.text import truncate

        result = truncate("Un texte trÃ¨s long...", length=10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_truncate_custom_suffix(self):
        """Test suffixe personnalisÃ©"""
        from src.utils.formatters.text import truncate

        result = truncate("Un texte trÃ¨s long...", length=15, suffix="[...]")
        assert result.endswith("[...]")


class TestCleanText:
    """Tests pour clean_text"""

    def test_clean_text_xss(self):
        """Test protection XSS"""
        from src.utils.formatters.text import clean_text

        result = clean_text("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result

    def test_clean_text_accolades(self):
        """Test suppression accolades"""
        from src.utils.formatters.text import clean_text

        result = clean_text("{test}")
        assert "{" not in result
        assert "}" not in result

    def test_clean_text_vide(self):
        """Test texte vide"""
        from src.utils.formatters.text import clean_text

        result = clean_text("")
        assert result == ""

    def test_clean_text_none(self):
        """Test None (devrait retourner None ou lever exception)"""
        from src.utils.formatters.text import clean_text

        # Le comportement peut varier selon l'implÃ©mentation
        result = clean_text(None)
        assert result is None


class TestSlugify:
    """Tests pour slugify"""

    def test_slugify_simple(self):
        """Test slug simple"""
        from src.utils.formatters.text import slugify

        result = slugify("Tarte aux Pommes")
        assert result == "tarte-aux-pommes"

    def test_slugify_accents(self):
        """Test avec accents"""
        from src.utils.formatters.text import slugify

        result = slugify("CrÃ¨me brÃ»lÃ©e Ã  la franÃ§aise")
        assert "creme" in result
        assert "brulee" in result
        assert "francaise" in result

    def test_slugify_caracteres_speciaux(self):
        """Test avec caractÃ¨res spÃ©ciaux"""
        from src.utils.formatters.text import slugify

        result = slugify("Test!@#$%^&*()")
        assert "!" not in result
        assert "@" not in result

    def test_slugify_espaces_multiples(self):
        """Test avec espaces multiples"""
        from src.utils.formatters.text import slugify

        result = slugify("Tarte   aux   pommes")
        assert "--" not in result  # Pas de doubles tirets


class TestExtractNumber:
    """Tests pour extract_number"""

    def test_extract_number_simple(self):
        """Test extraction simple"""
        from src.utils.formatters.text import extract_number

        result = extract_number("2.5 kg")
        assert result == 2.5

    def test_extract_number_avec_virgule(self):
        """Test avec virgule"""
        from src.utils.formatters.text import extract_number

        result = extract_number("Prix: 10,50â‚¬")
        assert result == 10.5

    def test_extract_number_negatif(self):
        """Test nombre nÃ©gatif"""
        from src.utils.formatters.text import extract_number

        result = extract_number("-5 degrÃ©s")
        assert result == -5.0

    def test_extract_number_none(self):
        """Test None"""
        from src.utils.formatters.text import extract_number

        result = extract_number(None)
        assert result is None

    def test_extract_number_vide(self):
        """Test texte vide"""
        from src.utils.formatters.text import extract_number

        result = extract_number("")
        assert result is None

    def test_extract_number_sans_nombre(self):
        """Test texte sans nombre"""
        from src.utils.formatters.text import extract_number

        result = extract_number("aucun nombre ici")
        assert result is None


class TestCapitalizeFirst:
    """Tests pour capitalize_first"""

    def test_capitalize_first_simple(self):
        """Test capitalisation simple"""
        from src.utils.formatters.text import capitalize_first

        result = capitalize_first("tomate")
        assert result == "Tomate"

    def test_capitalize_first_majuscules(self):
        """Test avec majuscules"""
        from src.utils.formatters.text import capitalize_first

        result = capitalize_first("TOMATE")
        assert result == "Tomate"

    def test_capitalize_first_vide(self):
        """Test texte vide"""
        from src.utils.formatters.text import capitalize_first

        result = capitalize_first("")
        assert result == ""

    def test_capitalize_first_un_caractere(self):
        """Test un seul caractÃ¨re"""
        from src.utils.formatters.text import capitalize_first

        result = capitalize_first("a")
        assert result == "A"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMATTERS UNITS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormatWeight:
    """Tests pour format_weight"""

    def test_format_weight_grammes(self):
        """Test grammes"""
        from src.utils.formatters.units import format_weight

        result = format_weight(500)
        assert result == "500 g"

    def test_format_weight_kg(self):
        """Test kilogrammes"""
        from src.utils.formatters.units import format_weight

        result = format_weight(1000)
        assert result == "1 kg"

    def test_format_weight_kg_decimal(self):
        """Test kilogrammes dÃ©cimaux"""
        from src.utils.formatters.units import format_weight

        result = format_weight(1500)
        assert result == "1.5 kg"

    def test_format_weight_zero(self):
        """Test zÃ©ro"""
        from src.utils.formatters.units import format_weight

        result = format_weight(0)
        assert result == "0 g"

    def test_format_weight_none(self):
        """Test None"""
        from src.utils.formatters.units import format_weight

        result = format_weight(None)
        assert result == "0 g"

    def test_format_weight_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.units import format_weight

        result = format_weight("invalid")
        assert result == "0 g"


class TestFormatVolume:
    """Tests pour format_volume"""

    def test_format_volume_ml(self):
        """Test millilitres"""
        from src.utils.formatters.units import format_volume

        result = format_volume(500)
        assert result == "500 mL"

    def test_format_volume_litres(self):
        """Test litres"""
        from src.utils.formatters.units import format_volume

        result = format_volume(1000)
        assert result == "1 L"

    def test_format_volume_litres_decimal(self):
        """Test litres dÃ©cimaux"""
        from src.utils.formatters.units import format_volume

        result = format_volume(1500)
        assert result == "1.5 L"

    def test_format_volume_zero(self):
        """Test zÃ©ro"""
        from src.utils.formatters.units import format_volume

        result = format_volume(0)
        assert result == "0 mL"

    def test_format_volume_none(self):
        """Test None"""
        from src.utils.formatters.units import format_volume

        result = format_volume(None)
        assert result == "0 mL"

    def test_format_volume_invalide(self):
        """Test valeur invalide"""
        from src.utils.formatters.units import format_volume

        result = format_volume("invalid")
        assert result == "0 mL"
