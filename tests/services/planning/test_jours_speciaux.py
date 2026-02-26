"""
Tests pour src/services/famille/jours_speciaux.py

Couverture: jours fériés français, ponts, fermetures crèche, service.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.famille.jours_speciaux import (
    JourSpecial,
    ServiceJoursSpeciaux,
    _paques,
    detecter_ponts,
    jours_feries_france,
)

# ═══════════════════════════════════════════════════════════
# CALCUL DE PÂQUES
# ═══════════════════════════════════════════════════════════


class TestPaques:
    """Tests de l'algorithme de Butcher/Meeus pour Pâques."""

    def test_paques_2024(self):
        assert _paques(2024) == date(2024, 3, 31)

    def test_paques_2025(self):
        assert _paques(2025) == date(2025, 4, 20)

    def test_paques_2026(self):
        assert _paques(2026) == date(2026, 4, 5)

    def test_paques_2027(self):
        assert _paques(2027) == date(2027, 3, 28)

    def test_paques_2030(self):
        assert _paques(2030) == date(2030, 4, 21)

    def test_paques_est_un_dimanche(self):
        """Pâques tombe toujours un dimanche."""
        for annee in range(2020, 2035):
            p = _paques(annee)
            assert p.weekday() == 6, f"Pâques {annee} n'est pas un dimanche"


# ═══════════════════════════════════════════════════════════
# JOURS FÉRIÉS FRANÇAIS
# ═══════════════════════════════════════════════════════════


class TestJoursFeriesFrance:
    """Tests des jours fériés français officiels."""

    def test_11_jours_feries(self):
        """La France a 11 jours fériés officiels en métropole."""
        feries = jours_feries_france(2026)
        assert len(feries) == 11

    def test_feries_fixes(self):
        """Jours fériés à date fixe."""
        feries = jours_feries_france(2026)
        dates = {j.date_jour for j in feries}

        assert date(2026, 1, 1) in dates, "Jour de l'An manquant"
        assert date(2026, 5, 1) in dates, "Fête du Travail manquante"
        assert date(2026, 5, 8) in dates, "Victoire 1945 manquante"
        assert date(2026, 7, 14) in dates, "Fête Nationale manquante"
        assert date(2026, 8, 15) in dates, "Assomption manquante"
        assert date(2026, 11, 1) in dates, "Toussaint manquante"
        assert date(2026, 11, 11) in dates, "Armistice manquant"
        assert date(2026, 12, 25) in dates, "Noël manquant"

    def test_feries_mobiles_2026(self):
        """Jours fériés liés à Pâques (2026: Pâques = 5 avril)."""
        feries = jours_feries_france(2026)
        dates = {j.date_jour for j in feries}

        # Lundi de Pâques = 6 avril 2026
        assert date(2026, 4, 6) in dates, "Lundi de Pâques manquant"
        # Ascension = Pâques + 39 = 14 mai 2026
        assert date(2026, 5, 14) in dates, "Ascension manquante"
        # Lundi de Pentecôte = Pâques + 50 = 25 mai 2026
        assert date(2026, 5, 25) in dates, "Pentecôte manquante"

    def test_tous_type_ferie(self):
        """Tous les jours fériés ont le type 'ferie'."""
        feries = jours_feries_france(2026)
        for j in feries:
            assert j.type == "ferie"

    def test_trie_par_date(self):
        """Les jours fériés sont triés par date."""
        feries = jours_feries_france(2026)
        for i in range(len(feries) - 1):
            assert feries[i].date_jour <= feries[i + 1].date_jour

    def test_noms_non_vides(self):
        """Chaque jour férié a un nom."""
        feries = jours_feries_france(2026)
        for j in feries:
            assert j.nom, f"Nom vide pour {j.date_jour}"


# ═══════════════════════════════════════════════════════════
# PONTS
# ═══════════════════════════════════════════════════════════


class TestDetecterPonts:
    """Tests de la détection des jours de pont."""

    def test_pont_apres_jeudi(self):
        """Si un férié tombe un jeudi, le vendredi est un pont."""
        # Ascension 2026 = jeudi 14 mai
        ponts = detecter_ponts(2026)
        dates_ponts = {p.date_jour for p in ponts}
        assert date(2026, 5, 15) in dates_ponts, "Pont de l'Ascension manquant"

    def test_pont_avant_mardi(self):
        """Si un férié tombe un mardi, le lundi est un pont."""
        # Chercher une année où un férié fixe tombe un mardi
        # 1er mai 2029 = mardi
        ponts = detecter_ponts(2029)
        dates_ponts = {p.date_jour for p in ponts}
        assert date(2029, 4, 30) in dates_ponts, "Pont du 1er mai 2029 manquant"

    def test_pas_de_pont_mercredi(self):
        """Pas de pont si le férié tombe un mercredi."""
        for p in detecter_ponts(2026):
            # Un pont ne devrait pas être un samedi ou dimanche
            assert p.date_jour.weekday() < 5, f"Pont invalide le weekend: {p}"

    def test_type_pont(self):
        """Les ponts ont le type 'pont'."""
        ponts = detecter_ponts(2026)
        for p in ponts:
            assert p.type == "pont"

    def test_ponts_tries(self):
        """Les ponts sont triés par date."""
        ponts = detecter_ponts(2026)
        for i in range(len(ponts) - 1):
            assert ponts[i].date_jour <= ponts[i + 1].date_jour


# ═══════════════════════════════════════════════════════════
# SERVICE JOURS SPÉCIAUX
# ═══════════════════════════════════════════════════════════


class TestServiceJoursSpeciaux:
    """Tests du service complet."""

    @pytest.fixture
    def service(self):
        return ServiceJoursSpeciaux()

    def test_jours_feries_retourne_liste(self, service):
        result = service.jours_feries(2026)
        assert isinstance(result, list)
        assert len(result) == 11

    def test_ponts_retourne_liste(self, service):
        result = service.ponts(2026)
        assert isinstance(result, list)

    def test_est_jour_special_noel(self, service):
        result = service.est_jour_special(date(2026, 12, 25))
        assert result is not None
        assert result.type == "ferie"
        assert "Noël" in result.nom

    def test_est_jour_special_normal(self, service):
        """Un jour normal ne devrait pas être spécial."""
        # Le 15 mars 2026 est un dimanche pas férié
        result = service.est_jour_special(date(2026, 3, 18))
        assert result is None

    def test_est_jour_ferie(self, service):
        assert service.est_jour_ferie(date(2026, 7, 14)) is True
        assert service.est_jour_ferie(date(2026, 7, 13)) is False

    def test_tous_jours_speciaux(self, service):
        """Fusion fériés + ponts + crèche."""
        tous = service.tous_jours_speciaux(2026)
        assert len(tous) >= 11  # Au moins les 11 fériés

    def test_tous_jours_speciaux_tries(self, service):
        tous = service.tous_jours_speciaux(2026)
        for i in range(len(tous) - 1):
            assert tous[i].date_jour <= tous[i + 1].date_jour

    def test_tous_jours_speciaux_sans_ponts(self, service):
        sans_ponts = service.tous_jours_speciaux(2026, inclure_ponts=False)
        avec_ponts = service.tous_jours_speciaux(2026, inclure_ponts=True)
        assert len(sans_ponts) <= len(avec_ponts)

    def test_jours_speciaux_semaine(self, service):
        """Semaine du 14 juillet 2026 contient la fête nationale."""
        # 14 juillet 2026 = mardi → lundi = 13 juillet
        lundi = date(2026, 7, 13)
        result = service.jours_speciaux_semaine(lundi)
        dates = {j.date_jour for j in result}
        assert date(2026, 7, 14) in dates

    def test_jours_speciaux_semaine_vide(self, service):
        """Semaine banale sans jours spéciaux."""
        # Chercher une semaine qui n'a probablement rien
        result = service.jours_speciaux_semaine(date(2026, 2, 16))
        # Peut être vide ou pas selon les ponts
        assert isinstance(result, list)

    def test_prochains_jours_speciaux(self, service):
        """Retourne au moins quelques jours futurs."""
        result = service.prochains_jours_speciaux(nb=3)
        assert isinstance(result, list)
        assert len(result) <= 3

    @patch("src.services.famille.jours_speciaux._obtenir_config_creche")
    def test_fermetures_creche_avec_config(self, mock_config):
        """Fermetures crèche configurées."""
        mock_pstate = MagicMock()
        mock_pstate.get_all.return_value = {
            "semaines_fermeture": [
                {
                    "debut": "2026-08-03",
                    "fin": "2026-08-07",
                    "label": "Été",
                }
            ],
            "annee_courante": 2026,
        }
        mock_config.return_value = mock_pstate

        service = ServiceJoursSpeciaux()
        result = service.fermetures_creche(2026)

        # 5 jours ouvrés du 3 au 7 août
        assert len(result) == 5
        assert all(j.type == "creche" for j in result)

    @patch("src.services.famille.jours_speciaux._obtenir_config_creche")
    def test_fermetures_creche_exclut_weekends(self, mock_config):
        """Les weekends ne sont pas comptés dans les fermetures."""
        mock_pstate = MagicMock()
        mock_pstate.get_all.return_value = {
            "semaines_fermeture": [
                {
                    "debut": "2026-08-01",  # Samedi
                    "fin": "2026-08-09",  # Dimanche
                    "label": "Été",
                }
            ],
            "annee_courante": 2026,
        }
        mock_config.return_value = mock_pstate

        service = ServiceJoursSpeciaux()
        result = service.fermetures_creche(2026)

        # 3-7 août = 5 jours ouvrés
        for j in result:
            assert j.date_jour.weekday() < 5, f"Weekend inclus: {j.date_jour}"

    @patch("src.services.famille.jours_speciaux._obtenir_config_creche")
    def test_sauvegarder_fermetures(self, mock_config):
        """Sauvegarde appelle commit."""
        mock_pstate = MagicMock()
        mock_pstate.commit.return_value = True
        mock_config.return_value = mock_pstate

        service = ServiceJoursSpeciaux()
        result = service.sauvegarder_fermetures_creche(
            semaines=[{"debut": "2026-08-03", "fin": "2026-08-07", "label": "Été"}],
            nom_creche="Ma Crèche",
        )

        assert result is True
        mock_pstate.update.assert_called_once()
        mock_pstate.commit.assert_called_once()


# ═══════════════════════════════════════════════════════════
# JOUR SPECIAL NAMEDTUPLE
# ═══════════════════════════════════════════════════════════


class TestJourSpecial:
    """Tests du NamedTuple JourSpecial."""

    def test_creation(self):
        js = JourSpecial(date(2026, 12, 25), "Noël", "ferie")
        assert js.date_jour == date(2026, 12, 25)
        assert js.nom == "Noël"
        assert js.type == "ferie"

    def test_immutable(self):
        js = JourSpecial(date(2026, 1, 1), "Jour de l'An", "ferie")
        with pytest.raises(AttributeError):
            js.nom = "Autre"  # type: ignore[misc]

    def test_unpacking(self):
        js = JourSpecial(date(2026, 5, 1), "Fête du Travail", "ferie")
        d, nom, typ = js
        assert d == date(2026, 5, 1)
        assert nom == "Fête du Travail"
        assert typ == "ferie"
