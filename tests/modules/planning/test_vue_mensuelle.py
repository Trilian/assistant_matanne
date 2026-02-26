"""
Tests pour src/modules/planning/calendrier/vue_mensuelle.py

Couverture: chargement données mois, grille, statistiques.
"""

from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.modules.planning.calendrier.types import TypeEvenement
from src.modules.planning.calendrier.vue_mensuelle import (
    _COULEUR_PASTILLE,
    _COULEUR_PASTILLE_EMOJI,
    _charger_donnees_mois,
)

# ═══════════════════════════════════════════════════════════
# COULEURS / EMOJIS
# ═══════════════════════════════════════════════════════════


class TestPastilles:
    """Tests des mappings de couleurs/emojis."""

    def test_couleur_pastille_repas(self):
        assert TypeEvenement.REPAS_MIDI in _COULEUR_PASTILLE
        assert TypeEvenement.REPAS_SOIR in _COULEUR_PASTILLE

    def test_couleur_pastille_jours_speciaux(self):
        assert TypeEvenement.FERIE in _COULEUR_PASTILLE
        assert TypeEvenement.CRECHE in _COULEUR_PASTILLE
        assert TypeEvenement.PONT in _COULEUR_PASTILLE

    def test_emoji_pastille_types(self):
        assert TypeEvenement.REPAS_MIDI in _COULEUR_PASTILLE_EMOJI
        assert TypeEvenement.RDV_MEDICAL in _COULEUR_PASTILLE_EMOJI
        assert TypeEvenement.FERIE in _COULEUR_PASTILLE_EMOJI

    def test_toutes_couleurs_hex(self):
        """Toutes les couleurs sont au format hex."""
        for typ, couleur in _COULEUR_PASTILLE.items():
            assert couleur.startswith("#"), f"Couleur invalide pour {typ}: {couleur}"


# ═══════════════════════════════════════════════════════════
# CHARGEMENT DONNÉES MOIS
# ═══════════════════════════════════════════════════════════


class TestChargerDonneesMois:
    """Tests du chargement des données mensuelles."""

    @patch("src.modules.planning.calendrier.data.charger_donnees_semaine")
    @patch("src.modules.planning.calendrier.aggregation.construire_semaine_calendrier")
    @patch("src.core.date_utils.obtenir_debut_semaine")
    def test_retourne_dict_par_date(self, mock_debut, mock_construire, mock_charger):
        """Le résultat contient une entrée pour chaque jour du mois."""
        # Mock: chaque semaine retourne des jours vides
        mock_debut.side_effect = lambda d: d - timedelta(days=d.weekday())
        mock_charger.return_value = {
            "repas": [],
            "sessions_batch": [],
            "activites": [],
            "events": [],
            "courses_planifiees": [],
            "taches_menage": [],
        }

        # Créer des jours mockés
        def fake_semaine(**kwargs):
            debut = kwargs["date_debut"]
            jours = []
            for i in range(7):
                j = debut + timedelta(days=i)
                jours.append(
                    SimpleNamespace(
                        date_jour=j,
                        nb_evenements=0,
                        evenements=[],
                        charge_score=0,
                        jours_speciaux=[],
                    )
                )
            return SimpleNamespace(jours=jours)

        mock_construire.side_effect = fake_semaine

        result = _charger_donnees_mois(2026, 3)

        # Mars 2026 a 31 jours
        assert len(result) == 31
        assert date(2026, 3, 1) in result
        assert date(2026, 3, 31) in result
        assert date(2026, 4, 1) not in result

    def test_mois_fevrier_non_bissextile(self):
        """Février 2026 a 28 jours (pas bissextile)."""
        with patch("src.modules.planning.calendrier.data.charger_donnees_semaine") as mock_ch:
            mock_ch.side_effect = Exception("DB not available")
            result = _charger_donnees_mois(2026, 2)
            assert len(result) == 28

    def test_mois_fevrier_bissextile(self):
        """Février 2028 a 29 jours (bissextile)."""
        with patch("src.modules.planning.calendrier.data.charger_donnees_semaine") as mock_ch:
            mock_ch.side_effect = Exception("DB not available")
            result = _charger_donnees_mois(2028, 2)
            assert len(result) == 29

    def test_mois_decembre(self):
        """Décembre correctement géré (cas limites année)."""
        with patch("src.modules.planning.calendrier.data.charger_donnees_semaine") as mock_ch:
            mock_ch.side_effect = Exception("DB not available")
            result = _charger_donnees_mois(2026, 12)
            assert len(result) == 31

    def test_donnees_par_defaut_quand_erreur(self):
        """En cas d'erreur de chargement, les données par défaut sont retournées."""
        with patch("src.modules.planning.calendrier.data.charger_donnees_semaine") as mock_ch:
            mock_ch.side_effect = Exception("DB error")
            result = _charger_donnees_mois(2026, 3)

            assert len(result) == 31
            for d, data in result.items():
                assert data["nb_events"] == 0
                assert data["charge"] == 0
                assert data["types"] == set()
                assert data["jours_speciaux"] == []
                assert data["titres"] == []

    @patch("src.modules.planning.calendrier.data.charger_donnees_semaine")
    @patch("src.modules.planning.calendrier.aggregation.construire_semaine_calendrier")
    @patch("src.core.date_utils.obtenir_debut_semaine")
    def test_donnees_remplies(self, mock_debut, mock_construire, mock_charger):
        """Les données d'événements sont correctement extraites."""
        mock_debut.side_effect = lambda d: d - timedelta(days=d.weekday())
        mock_charger.return_value = {
            "repas": [],
            "sessions_batch": [],
            "activites": [],
            "events": [],
            "courses_planifiees": [],
            "taches_menage": [],
        }

        evt = SimpleNamespace(
            type=TypeEvenement.ACTIVITE,
            titre="Parc",
            heure_debut=None,
            heure_fin=None,
        )

        def fake_semaine(**kwargs):
            debut = kwargs["date_debut"]
            jours = []
            for i in range(7):
                j = debut + timedelta(days=i)
                evts = [evt] if j == date(2026, 3, 5) else []
                jours.append(
                    SimpleNamespace(
                        date_jour=j,
                        nb_evenements=len(evts),
                        evenements=evts,
                        charge_score=30 if evts else 0,
                        jours_speciaux=[],
                    )
                )
            return SimpleNamespace(jours=jours)

        mock_construire.side_effect = fake_semaine

        result = _charger_donnees_mois(2026, 3)

        # Le 5 mars devrait avoir des données
        data_5 = result[date(2026, 3, 5)]
        assert data_5["nb_events"] == 1
        assert TypeEvenement.ACTIVITE in data_5["types"]
        assert "Parc" in data_5["titres"]
