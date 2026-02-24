"""
Tests pour src/modules/shared/date_utils.py

Tests des fonctions utilitaires de manipulation de dates.
"""

from datetime import date

from src.core.date_utils import (
    formater_date_fr,
    formater_jour_fr,
    formater_mois_fr,
    obtenir_debut_semaine,
    obtenir_fin_semaine,
    obtenir_jours_semaine,
    obtenir_semaine_precedente,
    obtenir_semaine_suivante,
)


class TestObtenirDebutSemaine:
    """Tests pour obtenir_debut_semaine."""

    def test_lundi_retourne_meme_date(self):
        """Un lundi retourne le même jour."""
        lundi = date(2024, 1, 1)  # Lundi
        assert obtenir_debut_semaine(lundi) == lundi

    def test_mercredi_retourne_lundi(self):
        """Un mercredi retourne le lundi de la même semaine."""
        mercredi = date(2024, 1, 3)  # Mercredi
        assert obtenir_debut_semaine(mercredi) == date(2024, 1, 1)

    def test_dimanche_retourne_lundi(self):
        """Un dimanche retourne le lundi de la même semaine."""
        dimanche = date(2024, 1, 7)  # Dimanche
        assert obtenir_debut_semaine(dimanche) == date(2024, 1, 1)

    def test_none_retourne_lundi_courant(self):
        """None utilise la date d'aujourd'hui."""
        result = obtenir_debut_semaine(None)
        assert result.weekday() == 0  # Lundi


class TestObtenirFinSemaine:
    """Tests pour obtenir_fin_semaine."""

    def test_lundi_retourne_dimanche(self):
        """Un lundi retourne le dimanche de la même semaine."""
        lundi = date(2024, 1, 1)  # Lundi
        assert obtenir_fin_semaine(lundi) == date(2024, 1, 7)  # Dimanche

    def test_dimanche_retourne_meme_date(self):
        """Un dimanche retourne le même jour."""
        dimanche = date(2024, 1, 7)  # Dimanche
        assert obtenir_fin_semaine(dimanche) == dimanche

    def test_mercredi_retourne_dimanche(self):
        """Un mercredi retourne le dimanche de la même semaine."""
        mercredi = date(2024, 1, 3)
        assert obtenir_fin_semaine(mercredi) == date(2024, 1, 7)


class TestObtenirJoursSemaine:
    """Tests pour obtenir_jours_semaine."""

    def test_retourne_7_jours(self):
        """Retourne exactement 7 jours."""
        lundi = date(2024, 1, 1)
        jours = obtenir_jours_semaine(lundi)
        assert len(jours) == 7

    def test_commence_par_lundi(self):
        """Le premier jour est un lundi."""
        lundi = date(2024, 1, 1)
        jours = obtenir_jours_semaine(lundi)
        assert jours[0].weekday() == 0

    def test_finit_par_dimanche(self):
        """Le dernier jour est un dimanche."""
        lundi = date(2024, 1, 1)
        jours = obtenir_jours_semaine(lundi)
        assert jours[6].weekday() == 6

    def test_jours_consecutifs(self):
        """Les jours sont consécutifs."""
        lundi = date(2024, 1, 1)
        jours = obtenir_jours_semaine(lundi)
        for i in range(1, 7):
            diff = (jours[i] - jours[i - 1]).days
            assert diff == 1


class TestObtenirSemainePrecedente:
    """Tests pour obtenir_semaine_precedente."""

    def test_retourne_lundi_precedent(self):
        """Retourne le lundi de la semaine précédente."""
        lundi = date(2024, 1, 8)  # 2ème lundi de janvier
        result = obtenir_semaine_precedente(lundi)
        assert result == date(2024, 1, 1)

    def test_difference_7_jours(self):
        """Différence de 7 jours avec le lundi courant."""
        ref = date(2024, 1, 10)  # Mercredi
        debut_courant = obtenir_debut_semaine(ref)
        debut_precedent = obtenir_semaine_precedente(ref)
        assert (debut_courant - debut_precedent).days == 7


class TestObtenirSemaineSuivante:
    """Tests pour obtenir_semaine_suivante."""

    def test_retourne_lundi_suivant(self):
        """Retourne le lundi de la semaine suivante."""
        lundi = date(2024, 1, 1)
        result = obtenir_semaine_suivante(lundi)
        assert result == date(2024, 1, 8)

    def test_difference_7_jours(self):
        """Différence de 7 jours avec le lundi courant."""
        ref = date(2024, 1, 10)
        debut_courant = obtenir_debut_semaine(ref)
        debut_suivant = obtenir_semaine_suivante(ref)
        assert (debut_suivant - debut_courant).days == 7


class TestFormaterDateFr:
    """Tests pour formater_date_fr."""

    def test_format_complet(self):
        """Format complet avec année."""
        d = date(2024, 1, 15)  # Lundi
        result = formater_date_fr(d, avec_annee=True)
        assert "Lundi" in result
        assert "15" in result
        assert "Janvier" in result
        assert "2024" in result

    def test_format_sans_annee(self):
        """Format sans année."""
        d = date(2024, 1, 15)
        result = formater_date_fr(d, avec_annee=False)
        assert "2024" not in result
        assert "Janvier" in result


class TestFormaterJourFr:
    """Tests pour formater_jour_fr."""

    def test_lundi(self):
        """Retourne 'Lundi' pour un lundi."""
        lundi = date(2024, 1, 1)
        assert formater_jour_fr(lundi) == "Lundi"

    def test_dimanche(self):
        """Retourne 'Dimanche' pour un dimanche."""
        dimanche = date(2024, 1, 7)
        assert formater_jour_fr(dimanche) == "Dimanche"

    def test_format_court(self):
        """Format court (Lun, Mar, etc.)."""
        lundi = date(2024, 1, 1)
        result = formater_jour_fr(lundi, court=True)
        assert result == "Lun"


class TestFormaterMoisFr:
    """Tests pour formater_mois_fr."""

    def test_janvier(self):
        """Retourne 'Janvier' pour janvier."""
        d = date(2024, 1, 15)
        assert formater_mois_fr(d) == "Janvier"

    def test_decembre(self):
        """Retourne 'Décembre' pour décembre."""
        d = date(2024, 12, 15)
        assert formater_mois_fr(d) == "Décembre"

    def test_format_court(self):
        """Format court (Jan, Fév, etc.)."""
        d = date(2024, 1, 15)
        result = formater_mois_fr(d, court=True)
        assert result == "Jan"
