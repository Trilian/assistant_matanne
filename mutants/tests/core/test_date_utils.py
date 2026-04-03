"""Tests pour src.core.date_utils — utilitaires de dates."""

from datetime import date, datetime, timedelta

import pytest

# ═══════════════════════════════════════════════════════════
# SEMAINES
# ═══════════════════════════════════════════════════════════


class TestObtenir_debut_semaine:
    """Tests obtenir_debut_semaine()."""

    def test_lundi_retourne_meme_jour(self):
        from src.core.date_utils import obtenir_debut_semaine

        lundi = date(2025, 1, 6)  # Lundi
        assert obtenir_debut_semaine(lundi) == lundi

    def test_jeudi_retourne_lundi(self):
        from src.core.date_utils import obtenir_debut_semaine

        jeudi = date(2024, 1, 18)
        assert obtenir_debut_semaine(jeudi) == date(2024, 1, 15)

    def test_dimanche_retourne_lundi(self):
        from src.core.date_utils import obtenir_debut_semaine

        dimanche = date(2025, 1, 12)
        assert obtenir_debut_semaine(dimanche) == date(2025, 1, 6)

    def test_none_utilise_aujourd_hui(self):
        from src.core.date_utils import obtenir_debut_semaine

        result = obtenir_debut_semaine(None)
        assert result.weekday() == 0  # Toujours un lundi

    def test_datetime_converti_en_date(self):
        from src.core.date_utils import obtenir_debut_semaine

        dt = datetime(2024, 1, 18, 14, 30, 0)
        assert obtenir_debut_semaine(dt) == date(2024, 1, 15)


class TestObtenir_fin_semaine:
    """Tests obtenir_fin_semaine()."""

    def test_retourne_dimanche(self):
        from src.core.date_utils import obtenir_fin_semaine

        mercredi = date(2025, 1, 8)
        assert obtenir_fin_semaine(mercredi) == date(2025, 1, 12)

    def test_dimanche_retourne_meme_jour(self):
        from src.core.date_utils import obtenir_fin_semaine

        dimanche = date(2025, 1, 12)
        assert obtenir_fin_semaine(dimanche) == dimanche


class TestObtenir_bornes_semaine:
    """Tests obtenir_bornes_semaine()."""

    def test_retourne_tuple_lundi_dimanche(self):
        from src.core.date_utils import obtenir_bornes_semaine

        lundi, dimanche = obtenir_bornes_semaine(date(2025, 1, 8))
        assert lundi == date(2025, 1, 6)
        assert dimanche == date(2025, 1, 12)
        assert lundi.weekday() == 0
        assert dimanche.weekday() == 6


class TestObtenir_jours_semaine:
    """Tests obtenir_jours_semaine()."""

    def test_retourne_7_jours(self):
        from src.core.date_utils import obtenir_jours_semaine

        jours = obtenir_jours_semaine(date(2025, 1, 8))
        assert len(jours) == 7

    def test_commence_lundi_finit_dimanche(self):
        from src.core.date_utils import obtenir_jours_semaine

        jours = obtenir_jours_semaine(date(2025, 1, 8))
        assert jours[0].weekday() == 0  # Lundi
        assert jours[6].weekday() == 6  # Dimanche

    def test_jours_consecutifs(self):
        from src.core.date_utils import obtenir_jours_semaine

        jours = obtenir_jours_semaine(date(2025, 1, 8))
        for i in range(1, 7):
            assert jours[i] - jours[i - 1] == timedelta(days=1)


class TestSemaineNavigation:
    """Tests navigation entre semaines."""

    def test_semaine_precedente(self):
        from src.core.date_utils import obtenir_semaine_precedente

        ref = date(2025, 1, 8)  # Mercredi
        result = obtenir_semaine_precedente(ref)
        assert result == date(2024, 12, 30)  # Lundi précédent
        assert result.weekday() == 0

    def test_semaine_suivante(self):
        from src.core.date_utils import obtenir_semaine_suivante

        ref = date(2025, 1, 8)
        result = obtenir_semaine_suivante(ref)
        assert result == date(2025, 1, 13)
        assert result.weekday() == 0

    def test_semaines_entre(self):
        from src.core.date_utils import semaines_entre

        assert semaines_entre(date(2025, 1, 1), date(2025, 1, 15)) == 2
        assert semaines_entre(date(2025, 1, 1), date(2025, 1, 1)) == 0
        assert semaines_entre(date(2025, 1, 1), date(2025, 1, 6)) == 0
        assert semaines_entre(date(2025, 1, 1), date(2025, 1, 8)) == 1


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════


class TestFormater_date_fr:
    """Tests formater_date_fr()."""

    def test_format_complet(self):
        from src.core.date_utils import formater_date_fr

        result = formater_date_fr(date(2024, 1, 15))
        assert "Lundi" in result
        assert "15" in result
        assert "Janvier" in result
        assert "2024" in result

    def test_sans_annee(self):
        from src.core.date_utils import formater_date_fr

        result = formater_date_fr(date(2024, 1, 15), avec_annee=False)
        assert "2024" not in result
        assert "Lundi" in result


class TestFormater_jour_fr:
    """Tests formater_jour_fr()."""

    def test_format_long(self):
        from src.core.date_utils import formater_jour_fr

        assert formater_jour_fr(date(2025, 1, 6)) == "Lundi"

    def test_format_court(self):
        from src.core.date_utils import formater_jour_fr

        result = formater_jour_fr(date(2025, 1, 6), court=True)
        assert result == "Lun"


class TestFormater_mois_fr:
    """Tests formater_mois_fr()."""

    def test_format_long(self):
        from src.core.date_utils import formater_mois_fr

        assert formater_mois_fr(date(2025, 1, 15)) == "Janvier"

    def test_format_court(self):
        from src.core.date_utils import formater_mois_fr

        assert formater_mois_fr(date(2025, 1, 15), court=True) == "Jan"


class TestFormater_label_semaine:
    """Tests formater_label_semaine()."""

    def test_format_standard(self):
        from src.core.date_utils import formater_label_semaine

        result = formater_label_semaine(date(2025, 1, 6))
        assert result == "Semaine du 06/01/2025"

    def test_alias_format_week_label(self):
        from src.core.date_utils import format_week_label, formater_label_semaine

        assert format_week_label is formater_label_semaine


class TestFormater_temps:
    """Tests formater_temps()."""

    def test_none_retourne_zero(self):
        from src.core.date_utils import formater_temps

        assert formater_temps(None) == "0min"

    def test_zero_retourne_zero(self):
        from src.core.date_utils import formater_temps

        assert formater_temps(0) == "0min"

    def test_minutes_simples(self):
        from src.core.date_utils import formater_temps

        assert formater_temps(45) == "45min"

    def test_avec_espace(self):
        from src.core.date_utils import formater_temps

        assert formater_temps(45, avec_espace=True) == "45 min"

    def test_heures_avec_minutes(self):
        from src.core.date_utils import formater_temps

        assert formater_temps(90) == "1h30"

    def test_heures_exactes(self):
        from src.core.date_utils import formater_temps

        assert formater_temps(120) == "2h"

    def test_zero_avec_espace(self):
        from src.core.date_utils import formater_temps

        assert formater_temps(None, avec_espace=True) == "0 min"

    def test_valeur_invalide(self):
        from src.core.date_utils import formater_temps

        assert formater_temps("abc") == "0min"


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


class TestEst_weekend:
    """Tests est_weekend()."""

    def test_samedi(self):
        from src.core.date_utils import est_weekend

        assert est_weekend(date(2025, 1, 11)) is True

    def test_dimanche(self):
        from src.core.date_utils import est_weekend

        assert est_weekend(date(2025, 1, 12)) is True

    def test_lundi(self):
        from src.core.date_utils import est_weekend

        assert est_weekend(date(2025, 1, 6)) is False

    def test_vendredi(self):
        from src.core.date_utils import est_weekend

        assert est_weekend(date(2025, 1, 10)) is False


class TestEst_aujourd_hui:
    """Tests est_aujourd_hui()."""

    def test_aujourd_hui(self):
        from src.core.date_utils import est_aujourd_hui

        assert est_aujourd_hui(date.today()) is True

    def test_hier(self):
        from src.core.date_utils import est_aujourd_hui

        assert est_aujourd_hui(date.today() - timedelta(days=1)) is False


class TestDomaineJours:
    """Tests obtenir_noms_jours_semaine / obtenir_nom_jour_semaine / obtenir_index_jour_semaine."""

    def test_noms_jours_liste_7(self):
        from src.core.date_utils import obtenir_noms_jours_semaine

        noms = obtenir_noms_jours_semaine()
        assert len(noms) == 7
        assert noms[0] == "Lundi"
        assert noms[6] == "Dimanche"

    def test_nom_jour_valide(self):
        from src.core.date_utils import obtenir_nom_jour_semaine

        assert obtenir_nom_jour_semaine(0) == "Lundi"
        assert obtenir_nom_jour_semaine(4) == "Vendredi"

    def test_nom_jour_invalide(self):
        from src.core.date_utils import obtenir_nom_jour_semaine

        assert obtenir_nom_jour_semaine(7) == ""
        assert obtenir_nom_jour_semaine(-1) == ""

    def test_index_jour_valide(self):
        from src.core.date_utils import obtenir_index_jour_semaine

        assert obtenir_index_jour_semaine("Lundi") == 0
        assert obtenir_index_jour_semaine("lundi") == 0  # Case insensitive

    def test_index_jour_invalide(self):
        from src.core.date_utils import obtenir_index_jour_semaine

        assert obtenir_index_jour_semaine("Lundiiii") == -1

    def test_aliases(self):
        from src.core.date_utils import (
            get_weekday_index,
            get_weekday_name,
            get_weekday_names,
            obtenir_index_jour_semaine,
            obtenir_nom_jour_semaine,
            obtenir_noms_jours_semaine,
        )

        assert get_weekday_names is obtenir_noms_jours_semaine
        assert get_weekday_name is obtenir_nom_jour_semaine
        assert get_weekday_index is obtenir_index_jour_semaine


# ═══════════════════════════════════════════════════════════
# PERIODES
# ═══════════════════════════════════════════════════════════


class TestObtenir_bornes_mois:
    """Tests obtenir_bornes_mois()."""

    def test_janvier(self):
        from src.core.date_utils import obtenir_bornes_mois

        premier, dernier = obtenir_bornes_mois(date(2025, 1, 15))
        assert premier == date(2025, 1, 1)
        assert dernier == date(2025, 1, 31)

    def test_fevrier_non_bissextile(self):
        from src.core.date_utils import obtenir_bornes_mois

        premier, dernier = obtenir_bornes_mois(date(2025, 2, 15))
        assert premier == date(2025, 2, 1)
        assert dernier == date(2025, 2, 28)

    def test_fevrier_bissextile(self):
        from src.core.date_utils import obtenir_bornes_mois

        premier, dernier = obtenir_bornes_mois(date(2024, 2, 15))
        assert premier == date(2024, 2, 1)
        assert dernier == date(2024, 2, 29)

    def test_decembre(self):
        from src.core.date_utils import obtenir_bornes_mois

        premier, dernier = obtenir_bornes_mois(date(2025, 12, 1))
        assert premier == date(2025, 12, 1)
        assert dernier == date(2025, 12, 31)

    def test_none_utilise_aujourd_hui(self):
        from src.core.date_utils import obtenir_bornes_mois

        premier, dernier = obtenir_bornes_mois(None)
        assert premier.day == 1
        assert (dernier + timedelta(days=1)).day == 1


class TestObtenir_trimestre:
    """Tests obtenir_trimestre()."""

    def test_trimestres(self):
        from src.core.date_utils import obtenir_trimestre

        assert obtenir_trimestre(date(2025, 1, 1)) == 1
        assert obtenir_trimestre(date(2025, 3, 31)) == 1
        assert obtenir_trimestre(date(2025, 4, 1)) == 2
        assert obtenir_trimestre(date(2025, 7, 1)) == 3
        assert obtenir_trimestre(date(2025, 10, 1)) == 4
        assert obtenir_trimestre(date(2025, 12, 31)) == 4


class TestPlage_dates:
    """Tests plage_dates()."""

    def test_plage_3_jours(self):
        from src.core.date_utils import plage_dates

        result = plage_dates(date(2025, 1, 1), date(2025, 1, 3))
        assert len(result) == 3
        assert result[0] == date(2025, 1, 1)
        assert result[2] == date(2025, 1, 3)

    def test_meme_jour(self):
        from src.core.date_utils import plage_dates

        result = plage_dates(date(2025, 1, 1), date(2025, 1, 1))
        assert len(result) == 1


class TestAjouter_jours_ouvres:
    """Tests ajouter_jours_ouvres()."""

    def test_5_jours_ouvres_depuis_lundi(self):
        from src.core.date_utils import ajouter_jours_ouvres

        lundi = date(2025, 1, 6)
        result = ajouter_jours_ouvres(lundi, 5)
        assert result == date(2025, 1, 13)  # Lundi suivant

    def test_skip_weekend(self):
        from src.core.date_utils import ajouter_jours_ouvres

        vendredi = date(2025, 1, 10)
        result = ajouter_jours_ouvres(vendredi, 1)
        assert result == date(2025, 1, 13)  # Lundi

    def test_zero_jours(self):
        from src.core.date_utils import ajouter_jours_ouvres

        ref = date(2025, 1, 6)
        result = ajouter_jours_ouvres(ref, 0)
        assert result == ref
