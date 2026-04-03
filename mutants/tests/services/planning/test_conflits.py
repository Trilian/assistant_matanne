"""
Tests pour src/services/planning/conflits.py

Couverture: détection de conflits, chevauchements, surcharge, jours spéciaux.
"""

from datetime import date, time, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.planning.conflits import (
    HEURE_MAX_NORMALE,
    HEURE_MIN_NORMALE,
    MARGE_MINUTES_DEFAUT,
    SEUIL_SURCHARGE,
    Conflit,
    NiveauConflit,
    RapportConflits,
    ServiceConflits,
    TypeConflit,
    _ajouter_duree,
)

# ═══════════════════════════════════════════════════════════
# TYPES ET DATACLASSES
# ═══════════════════════════════════════════════════════════


class TestNiveauConflit:
    def test_valeurs(self):
        assert NiveauConflit.ERREUR == "erreur"
        assert NiveauConflit.AVERTISSEMENT == "avertissement"
        assert NiveauConflit.INFO == "info"


class TestTypeConflit:
    def test_valeurs(self):
        assert TypeConflit.CHEVAUCHEMENT == "chevauchement"
        assert TypeConflit.SANS_MARGE == "sans_marge"
        assert TypeConflit.JOUR_FERIE == "jour_ferie"
        assert TypeConflit.CRECHE_FERMEE == "creche_fermee"
        assert TypeConflit.SURCHARGE == "surcharge"
        assert TypeConflit.HORS_HORAIRES == "hors_horaires"


class TestConflit:
    def test_creation(self):
        c = Conflit(
            type=TypeConflit.CHEVAUCHEMENT,
            niveau=NiveauConflit.ERREUR,
            message="Test conflit",
            date_jour=date(2026, 3, 1),
        )
        assert c.type == TypeConflit.CHEVAUCHEMENT
        assert c.niveau == NiveauConflit.ERREUR

    def test_emoji_erreur(self):
        c = Conflit(
            type=TypeConflit.CHEVAUCHEMENT,
            niveau=NiveauConflit.ERREUR,
            message="",
            date_jour=date.today(),
        )
        assert c.emoji == "🔴"

    def test_emoji_avertissement(self):
        c = Conflit(
            type=TypeConflit.SURCHARGE,
            niveau=NiveauConflit.AVERTISSEMENT,
            message="",
            date_jour=date.today(),
        )
        assert c.emoji == "🟡"

    def test_emoji_info(self):
        c = Conflit(
            type=TypeConflit.HORS_HORAIRES,
            niveau=NiveauConflit.INFO,
            message="",
            date_jour=date.today(),
        )
        assert c.emoji == "🔵"


class TestRapportConflits:
    def test_rapport_vide(self):
        r = RapportConflits(date_debut=date(2026, 3, 2), date_fin=date(2026, 3, 8))
        assert r.nb_erreurs == 0
        assert r.nb_avertissements == 0
        assert r.nb_infos == 0
        assert not r.a_conflits_critiques
        assert "Aucun conflit" in r.resume

    def test_rapport_avec_conflits(self):
        conflits = [
            Conflit(TypeConflit.CHEVAUCHEMENT, NiveauConflit.ERREUR, "c1", date.today()),
            Conflit(TypeConflit.SURCHARGE, NiveauConflit.AVERTISSEMENT, "c2", date.today()),
            Conflit(TypeConflit.HORS_HORAIRES, NiveauConflit.INFO, "c3", date.today()),
        ]
        r = RapportConflits(
            date_debut=date(2026, 3, 2),
            date_fin=date(2026, 3, 8),
            conflits=conflits,
        )
        assert r.nb_erreurs == 1
        assert r.nb_avertissements == 1
        assert r.nb_infos == 1
        assert r.a_conflits_critiques
        assert "🔴" in r.resume


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


class TestAjouterDuree:
    def test_ajout_normal(self):
        result = _ajouter_duree(time(10, 0), 60)
        assert result == time(11, 0)

    def test_ajout_avec_minutes(self):
        result = _ajouter_duree(time(10, 30), 45)
        assert result == time(11, 15)

    def test_ajout_none(self):
        result = _ajouter_duree(None, 60)
        assert result == time(23, 59)


# ═══════════════════════════════════════════════════════════
# SERVICE CONFLITS
# ═══════════════════════════════════════════════════════════


class TestServiceConflitsDetection:
    """Tests de détection des conflits au sein d'un jour."""

    @pytest.fixture
    def service(self):
        return ServiceConflits()

    def test_pas_de_conflit_sans_events(self, service):
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), [])
        assert conflits == []

    def test_pas_de_conflit_events_sans_heure(self, service):
        events = [
            {"titre": "Truc", "type": "autre"},
            {"titre": "Chose", "type": "autre"},
        ]
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), events)
        assert conflits == []

    def test_chevauchement_detecte(self, service):
        events = [
            {
                "titre": "Réunion",
                "heure_debut": time(10, 0),
                "heure_fin": time(11, 0),
                "type": "rdv",
            },
            {
                "titre": "Courses",
                "heure_debut": time(10, 30),
                "heure_fin": time(11, 30),
                "type": "courses",
            },
        ]
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), events)
        types = [c.type for c in conflits]
        assert TypeConflit.CHEVAUCHEMENT in types

    def test_pas_de_chevauchement_events_espaces(self, service):
        events = [
            {"titre": "A", "heure_debut": time(9, 0), "heure_fin": time(10, 0), "type": "autre"},
            {"titre": "B", "heure_debut": time(11, 0), "heure_fin": time(12, 0), "type": "autre"},
        ]
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), events)
        chevauchements = [c for c in conflits if c.type == TypeConflit.CHEVAUCHEMENT]
        assert len(chevauchements) == 0

    def test_sans_marge_detecte(self, service):
        """Deux événements consécutifs sans marge suffisante."""
        events = [
            {"titre": "A", "heure_debut": time(10, 0), "heure_fin": time(11, 0), "type": "autre"},
            {"titre": "B", "heure_debut": time(11, 5), "heure_fin": time(12, 0), "type": "autre"},
        ]
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), events)
        types = [c.type for c in conflits]
        assert TypeConflit.SANS_MARGE in types

    def test_surcharge_detectee(self, service):
        """Trop d'événements dans une journée."""
        events = [{"titre": f"E{i}", "type": "autre"} for i in range(SEUIL_SURCHARGE)]
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), events)
        types = [c.type for c in conflits]
        assert TypeConflit.SURCHARGE in types

    def test_pas_surcharge_sous_seuil(self, service):
        events = [{"titre": f"E{i}", "type": "autre"} for i in range(SEUIL_SURCHARGE - 1)]
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), events)
        types = [c.type for c in conflits]
        assert TypeConflit.SURCHARGE not in types

    def test_hors_horaires_tot(self, service):
        events = [
            {"titre": "Tôt", "heure_debut": time(5, 0), "heure_fin": time(6, 0), "type": "autre"},
        ]
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), events)
        types = [c.type for c in conflits]
        assert TypeConflit.HORS_HORAIRES in types

    def test_hors_horaires_tard(self, service):
        events = [
            {
                "titre": "Tard",
                "heure_debut": time(23, 0),
                "heure_fin": time(23, 30),
                "type": "autre",
            },
        ]
        conflits = service.detecter_conflits_jour(date(2026, 3, 1), events)
        types = [c.type for c in conflits]
        assert TypeConflit.HORS_HORAIRES in types


class TestServiceConflitsJoursSpeciaux:
    """Tests des conflits avec jours fériés / crèche."""

    @pytest.fixture
    def service(self):
        return ServiceConflits()

    @patch("src.services.famille.jours_speciaux.obtenir_service_jours_speciaux")
    def test_conflit_jour_ferie(self, mock_svc, service):
        """RDV planifié un jour férié."""
        from src.services.famille.jours_speciaux import JourSpecial

        mock_instance = MagicMock()
        mock_instance.est_jour_special.return_value = JourSpecial(
            date(2026, 12, 25), "Noël", "ferie"
        )
        mock_svc.return_value = mock_instance

        events = [
            {"titre": "RDV docteur", "heure_debut": time(10, 0), "type": "rdv"},
        ]
        conflits = service.detecter_conflits_jour(date(2026, 12, 25), events)
        types = [c.type for c in conflits]
        assert TypeConflit.JOUR_FERIE in types

    @patch("src.services.famille.jours_speciaux.obtenir_service_jours_speciaux")
    def test_conflit_creche_fermee(self, mock_svc, service):
        """Activité Jules quand crèche fermée."""
        from src.services.famille.jours_speciaux import JourSpecial

        mock_instance = MagicMock()
        mock_instance.est_jour_special.return_value = JourSpecial(
            date(2026, 8, 3), "Crèche fermée (Été)", "creche"
        )
        mock_svc.return_value = mock_instance

        events = [
            {
                "titre": "Parc Jules",
                "heure_debut": time(10, 0),
                "type": "activite",
                "pour_jules": True,
            },
        ]
        conflits = service.detecter_conflits_jour(date(2026, 8, 3), events)
        types = [c.type for c in conflits]
        assert TypeConflit.CRECHE_FERMEE in types


class TestServiceConflitsSemaine:
    """Tests de la détection semaine."""

    @pytest.fixture
    def service(self):
        return ServiceConflits()

    def test_semaine_fournit_events(self, service):
        """Détection avec événements fournis manuellement."""
        lundi = date(2026, 3, 2)
        events_par_jour = {
            lundi: [
                {"titre": "A", "heure_debut": time(10, 0), "heure_fin": time(11, 0), "type": "rdv"},
                {
                    "titre": "B",
                    "heure_debut": time(10, 30),
                    "heure_fin": time(11, 30),
                    "type": "rdv",
                },
            ],
        }
        rapport = service.detecter_conflits_semaine(lundi, events_par_jour)
        assert isinstance(rapport, RapportConflits)
        assert rapport.nb_erreurs >= 1

    def test_semaine_vide(self, service):
        lundi = date(2026, 3, 2)
        events_par_jour = {}
        rapport = service.detecter_conflits_semaine(lundi, events_par_jour)
        assert rapport.nb_erreurs == 0
        assert "Aucun conflit" in rapport.resume


class TestServiceConflitsVerifierNouvel:
    """Tests de verifier_nouvel_evenement."""

    @pytest.fixture
    def service(self):
        return ServiceConflits()

    @patch.object(ServiceConflits, "_charger_evenements_jour")
    def test_nouvel_event_sans_conflit(self, mock_charger, service):
        mock_charger.return_value = []
        conflits = service.verifier_nouvel_evenement(
            date(2026, 3, 1), time(10, 0), time(11, 0), "Test"
        )
        # Pas de chevauchement quand il n'y a pas d'événement existant
        chevauchements = [c for c in conflits if c.type == TypeConflit.CHEVAUCHEMENT]
        assert len(chevauchements) == 0

    @patch.object(ServiceConflits, "_charger_evenements_jour")
    def test_nouvel_event_avec_conflit(self, mock_charger, service):
        mock_charger.return_value = [
            {
                "titre": "Existant",
                "heure_debut": time(10, 0),
                "heure_fin": time(11, 0),
                "type": "rdv",
            },
        ]
        conflits = service.verifier_nouvel_evenement(
            date(2026, 3, 1), time(10, 30), time(11, 30), "Nouveau"
        )
        chevauchements = [c for c in conflits if c.type == TypeConflit.CHEVAUCHEMENT]
        assert len(chevauchements) >= 1


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    def test_marge_defaut(self):
        assert MARGE_MINUTES_DEFAUT == 15

    def test_seuil_surcharge(self):
        assert SEUIL_SURCHARGE == 6

    def test_heures_normales(self):
        assert HEURE_MIN_NORMALE == time(7, 0)
        assert HEURE_MAX_NORMALE == time(22, 0)
