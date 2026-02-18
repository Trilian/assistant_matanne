"""
Tests pour src/utils/formatters/dates.py
Données réelles de cuisine familiale
"""

from datetime import date, datetime, timedelta

import pytest

from src.core.formatters import (
    formater_date,
    formater_datetime,
    formater_duree,
    formater_temps,
    temps_ecoule,
)


@pytest.mark.unit
class TestFormaterDate:
    """Tests pour formater_date avec données cuisine réelles."""

    # Format short
    def test_format_short_noel(self):
        """Noël format court."""
        assert formater_date(date(2026, 12, 25), "short") == "25/12"

    def test_format_short_nouvel_an(self):
        """Nouvel an format court."""
        assert formater_date(date(2027, 1, 1), "short") == "01/01"

    def test_format_short_anniversaire_jules(self):
        """Anniversaire Jules (19 mois) format court."""
        assert formater_date(date(2024, 7, 15), "short") == "15/07"

    # Format medium
    def test_format_medium_date_peremption(self):
        """Date péremption yaourt format medium."""
        assert formater_date(date(2026, 2, 20), "medium") == "20/02/2026"

    def test_format_medium_livraison_courses(self):
        """Date livraison courses."""
        assert formater_date(date(2026, 3, 5), "medium") == "05/03/2026"

    # Format long français - tous les mois
    def test_format_long_fr_janvier(self):
        """Long format janvier francais."""
        result = formater_date(date(2026, 1, 15), "long", "fr")
        assert result == "15 janvier 2026"

    def test_format_long_fr_fevrier(self):
        """Long format février francais."""
        result = formater_date(date(2026, 2, 4), "long", "fr")
        assert result == "4 février 2026"

    def test_format_long_fr_mars(self):
        """Long format mars francais."""
        result = formater_date(date(2026, 3, 21), "long", "fr")
        assert result == "21 mars 2026"

    def test_format_long_fr_avril(self):
        """Long format avril."""
        result = formater_date(date(2026, 4, 10), "long", "fr")
        assert result == "10 avril 2026"

    def test_format_long_fr_mai(self):
        """Long format mai."""
        result = formater_date(date(2026, 5, 1), "long", "fr")
        assert result == "1 mai 2026"

    def test_format_long_fr_juin(self):
        """Long format juin."""
        result = formater_date(date(2026, 6, 21), "long", "fr")
        assert result == "21 juin 2026"

    def test_format_long_fr_juillet(self):
        """Long format juillet (anniversaire Jules)."""
        result = formater_date(date(2024, 7, 15), "long", "fr")
        assert result == "15 juillet 2024"

    def test_format_long_fr_aout(self):
        """Long format août."""
        result = formater_date(date(2026, 8, 15), "long", "fr")
        assert result == "15 août 2026"

    def test_format_long_fr_septembre(self):
        """Long format septembre (rentrée)."""
        result = formater_date(date(2026, 9, 1), "long", "fr")
        assert result == "1 septembre 2026"

    def test_format_long_fr_octobre(self):
        """Long format octobre."""
        result = formater_date(date(2026, 10, 31), "long", "fr")
        assert result == "31 octobre 2026"

    def test_format_long_fr_novembre(self):
        """Long format novembre."""
        result = formater_date(date(2026, 11, 11), "long", "fr")
        assert result == "11 novembre 2026"

    def test_format_long_fr_decembre(self):
        """Long format décembre (Noël)."""
        result = formater_date(date(2026, 12, 25), "long", "fr")
        assert result == "25 décembre 2026"

    # Format long anglais
    def test_format_long_en(self):
        """Long format anglais."""
        result = formater_date(date(2026, 1, 15), "long", "en")
        assert result is not None

    # Format invalide (fallback)
    def test_format_invalid_fallback(self):
        """Format invalide retourne medium."""
        result = formater_date(date(2026, 5, 10), "invalid")
        assert result == "10/05/2026"

    # None et datetime
    def test_format_none(self):
        """None retourne tiret."""
        assert formater_date(None) == "—"

    def test_format_datetime_input(self):
        """Datetime converti en date."""
        dt = datetime(2026, 2, 4, 14, 30, 0)
        assert formater_date(dt, "short") == "04/02"


@pytest.mark.unit
class TestFormaterDatetime:
    """Tests pour formater_datetime avec repas planifiés."""

    def test_datetime_short_dejeuner(self):
        """Déjeuner 12h30 format court."""
        dt = datetime(2026, 2, 10, 12, 30, 0)
        result = formater_datetime(dt, "short")
        assert "10/02" in result
        assert "12:30" in result

    def test_datetime_short_diner(self):
        """Dîner 19h00 format court."""
        dt = datetime(2026, 2, 10, 19, 0, 0)
        result = formater_datetime(dt, "short")
        assert "19:00" in result

    def test_datetime_medium_gouter(self):
        """Goûter 16h30 format medium."""
        dt = datetime(2026, 2, 10, 16, 30, 0)
        result = formater_datetime(dt, "medium")
        assert "10/02/2026" in result
        assert "16:30" in result

    def test_datetime_long_repas_fete(self):
        """Repas de fête format long."""
        dt = datetime(2026, 12, 25, 13, 0, 0)
        result = formater_datetime(dt, "long", "fr")
        assert "décembre" in result
        assert "13:00" in result
        assert "à" in result

    def test_datetime_none(self):
        """None retourne tiret."""
        assert formater_datetime(None) == "—"

    def test_datetime_invalid_format(self):
        """Format invalide fallback."""
        dt = datetime(2026, 5, 10, 10, 0)
        result = formater_datetime(dt, "invalid")
        assert "10/05/2026" in result


@pytest.mark.unit
class TestTempsEcoule:
    """Tests pour temps_ecoule (dates relatives)."""

    def test_aujourdhui(self):
        """Date aujourd'hui."""
        assert temps_ecoule(date.today()) == "Aujourd'hui"

    def test_demain(self):
        """Date demain - courses prévues."""
        assert temps_ecoule(date.today() + timedelta(days=1)) == "Demain"

    def test_hier(self):
        """Date hier - repas passé."""
        assert temps_ecoule(date.today() - timedelta(days=1)) == "Hier"

    def test_dans_3_jours(self):
        """Dans 3 jours - livraison."""
        result = temps_ecoule(date.today() + timedelta(days=3))
        assert "Dans 3 jours" in result

    def test_dans_7_jours(self):
        """Dans 7 jours - semaine prochaine."""
        result = temps_ecoule(date.today() + timedelta(days=7))
        assert "Dans 7 jours" in result

    def test_il_y_a_2_jours(self):
        """Il y a 2 jours."""
        result = temps_ecoule(date.today() - timedelta(days=2))
        assert "Il y a 2 jours" in result

    def test_il_y_a_5_jours(self):
        """Il y a 5 jours."""
        result = temps_ecoule(date.today() - timedelta(days=5))
        assert "Il y a 5 jours" in result

    def test_date_lointaine_futur(self):
        """Date lointaine - format classique."""
        result = temps_ecoule(date.today() + timedelta(days=30))
        assert "/" in result

    def test_date_lointaine_passe(self):
        """Date lointaine passée - format classique."""
        result = temps_ecoule(date.today() - timedelta(days=30))
        assert "/" in result

    def test_datetime_input(self):
        """Datetime converti en date."""
        assert temps_ecoule(datetime.now()) == "Aujourd'hui"


@pytest.mark.unit
class TestFormaterTemps:
    """Tests pour formater_temps (durées recettes)."""

    # Minutes seules
    def test_temps_5min_oeuf_coque(self):
        """Oeuf à la coque 5min."""
        assert formater_temps(5) == "5min"

    def test_temps_15min_salade(self):
        """Salade rapide 15min."""
        assert formater_temps(15) == "15min"

    def test_temps_30min_pates(self):
        """Pâtes bolognaise 30min."""
        assert formater_temps(30) == "30min"

    def test_temps_45min_gratin(self):
        """Gratin 45min."""
        assert formater_temps(45) == "45min"

    # Heures exactes
    def test_temps_1h_poulet_roti(self):
        """Poulet rôti 1h."""
        assert formater_temps(60) == "1h"

    def test_temps_2h_boeuf_bourguignon(self):
        """Boeuf bourguignon 2h."""
        assert formater_temps(120) == "2h"

    def test_temps_3h_pot_au_feu(self):
        """Pot-au-feu 3h."""
        assert formater_temps(180) == "3h"

    # Heures + minutes
    def test_temps_1h15_tarte(self):
        """Tarte aux pommes 1h15."""
        assert formater_temps(75) == "1h15"

    def test_temps_1h30_lasagnes(self):
        """Lasagnes 1h30."""
        assert formater_temps(90) == "1h30"

    def test_temps_2h30_cassoulet(self):
        """Cassoulet 2h30."""
        assert formater_temps(150) == "2h30"

    # Cas limites
    def test_temps_0(self):
        """0 minutes."""
        assert formater_temps(0) == "0min"

    def test_temps_none(self):
        """None."""
        assert formater_temps(None) == "0min"

    def test_temps_float(self):
        """Float arrondi."""
        assert formater_temps(90.5) == "1h30"

    def test_temps_invalid_string(self):
        """String invalide."""
        assert formater_temps("abc") == "0min"


@pytest.mark.unit
class TestFormaterDuree:
    """Tests pour formater_duree (durées en secondes)."""

    # Secondes seules
    def test_duree_30s_court(self):
        """30 secondes format court."""
        result = formater_duree(30, short=True)
        assert "30" in result
        assert "s" in result.lower()

    def test_duree_45s_long(self):
        """45 secondes format long."""
        result = formater_duree(45, short=False)
        assert result is not None

    # Minutes
    def test_duree_2min_court(self):
        """2 minutes format court."""
        result = formater_duree(120, short=True)
        assert "2" in result
        assert "min" in result.lower() or "m" in result

    def test_duree_5min_long(self):
        """5 minutes format long."""
        result = formater_duree(300, short=False)
        assert "5" in result

    # Heures
    def test_duree_1h_court(self):
        """1 heure format court."""
        result = formater_duree(3600, short=True)
        assert "1" in result
        assert "h" in result.lower()

    # Combinaisons
    def test_duree_1h30min_court(self):
        """1h30min format court."""
        result = formater_duree(5400, short=True)
        assert "1h" in result

    def test_duree_1h1min5s(self):
        """1h 1min 5s."""
        result = formater_duree(3665, short=True)
        assert result is not None

    # Cas limites
    def test_duree_0(self):
        """0 secondes."""
        assert formater_duree(0, short=True) == "0s"

    def test_duree_none(self):
        """None."""
        result = formater_duree(None)
        assert result is not None

    def test_duree_invalid(self):
        """Valeur invalide."""
        assert formater_duree("abc") == "0s"
