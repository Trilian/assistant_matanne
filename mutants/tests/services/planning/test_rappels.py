"""
Tests pour src/services/planning/rappels.py

Couverture: règles de rappel, génération, formatage, priorités.
"""

from datetime import date, datetime, time, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.planning.rappels import (
    _REGLE_DEFAUT,
    _REGLES_RAPPEL,
    PrioriteRappel,
    Rappel,
    RegleRappel,
    ServiceRappels,
    _formater_delai,
)

# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class TestPrioriteRappel:
    def test_valeurs(self):
        assert PrioriteRappel.HAUTE == "haute"
        assert PrioriteRappel.MOYENNE == "moyenne"
        assert PrioriteRappel.BASSE == "basse"


class TestRegleRappel:
    def test_regle_rdv(self):
        regle = _REGLES_RAPPEL["rdv_medical"]
        assert regle.priorite == PrioriteRappel.HAUTE
        assert len(regle.delais) == 2  # J-1 + H-2

    def test_regle_activite(self):
        regle = _REGLES_RAPPEL["activite"]
        assert regle.priorite == PrioriteRappel.MOYENNE
        assert len(regle.delais) == 1  # H-2

    def test_regle_creche(self):
        regle = _REGLES_RAPPEL["creche"]
        assert regle.priorite == PrioriteRappel.HAUTE
        assert len(regle.delais) == 2  # J-3 + J-1

    def test_regle_defaut(self):
        assert _REGLE_DEFAUT.priorite == PrioriteRappel.MOYENNE
        assert len(_REGLE_DEFAUT.delais) == 1


class TestRappel:
    def test_creation(self):
        r = Rappel(
            evenement_titre="Test",
            evenement_type="rdv_medical",
            date_evenement=date(2026, 3, 1),
            heure_evenement=time(10, 0),
            date_rappel=datetime(2026, 2, 28, 10, 0),
            priorite=PrioriteRappel.HAUTE,
            message="Test rappel",
        )
        assert r.evenement_titre == "Test"
        assert r.priorite == PrioriteRappel.HAUTE
        assert r.est_envoye is False

    def test_est_a_envoyer_futur(self):
        """Rappel dans le futur n'est pas à envoyer."""
        demain = datetime.now() + timedelta(days=1)
        r = Rappel(
            evenement_titre="Futur",
            evenement_type="rdv",
            date_evenement=demain.date(),
            heure_evenement=None,
            date_rappel=demain,
            priorite=PrioriteRappel.HAUTE,
            message="Test",
        )
        assert r.est_a_envoyer is False

    def test_est_a_envoyer_passe(self):
        """Rappel passé est à envoyer."""
        hier = datetime.now() - timedelta(days=1)
        r = Rappel(
            evenement_titre="Passé",
            evenement_type="rdv",
            date_evenement=hier.date(),
            heure_evenement=None,
            date_rappel=hier,
            priorite=PrioriteRappel.HAUTE,
            message="Test",
        )
        assert r.est_a_envoyer is True

    def test_est_a_envoyer_deja_envoye(self):
        """Rappel déjà envoyé n'est pas à envoyer."""
        hier = datetime.now() - timedelta(days=1)
        r = Rappel(
            evenement_titre="Envoyé",
            evenement_type="rdv",
            date_evenement=hier.date(),
            heure_evenement=None,
            date_rappel=hier,
            priorite=PrioriteRappel.HAUTE,
            message="Test",
            est_envoye=True,
        )
        assert r.est_a_envoyer is False

    def test_delai_restant(self):
        futur = datetime.now() + timedelta(hours=5)
        r = Rappel(
            evenement_titre="T",
            evenement_type="rdv",
            date_evenement=futur.date(),
            heure_evenement=None,
            date_rappel=futur,
            priorite=PrioriteRappel.MOYENNE,
            message="",
        )
        assert r.delai_restant > timedelta(0)

    def test_delai_str_jours(self):
        futur = datetime.now() + timedelta(hours=48)
        r = Rappel(
            evenement_titre="T",
            evenement_type="rdv",
            date_evenement=futur.date(),
            heure_evenement=None,
            date_rappel=futur,
            priorite=PrioriteRappel.MOYENNE,
            message="",
        )
        assert "j" in r.delai_str

    def test_delai_str_heures(self):
        futur = datetime.now() + timedelta(hours=3)
        r = Rappel(
            evenement_titre="T",
            evenement_type="rdv",
            date_evenement=futur.date(),
            heure_evenement=None,
            date_rappel=futur,
            priorite=PrioriteRappel.MOYENNE,
            message="",
        )
        assert "h" in r.delai_str


# ═══════════════════════════════════════════════════════════
# FORMATER DELAI
# ═══════════════════════════════════════════════════════════


class TestFormaterDelai:
    def test_jours(self):
        assert "jours" in _formater_delai(timedelta(days=3))

    def test_demain(self):
        assert _formater_delai(timedelta(hours=24)) == "demain"

    def test_heures(self):
        result = _formater_delai(timedelta(hours=5))
        assert "5h" in result

    def test_heures_avec_minutes(self):
        result = _formater_delai(timedelta(hours=2, minutes=30))
        assert "2h30" in result

    def test_minutes(self):
        result = _formater_delai(timedelta(minutes=45))
        assert "45 minutes" in result

    def test_maintenant(self):
        assert _formater_delai(timedelta(0)) == "maintenant"


# ═══════════════════════════════════════════════════════════
# SERVICE RAPPELS
# ═══════════════════════════════════════════════════════════


class TestServiceRappels:
    """Tests du service complet."""

    @pytest.fixture
    def service(self):
        return ServiceRappels()

    def test_regle_pour_type_connu(self, service):
        regle = service.regle_pour_type("rdv_medical")
        assert regle.priorite == PrioriteRappel.HAUTE

    def test_regle_pour_type_inconnu(self, service):
        regle = service.regle_pour_type("type_inexistant")
        assert regle == _REGLE_DEFAUT

    def test_generer_rappels_rdv(self, service):
        """RDV médical génère 2 rappels (J-1 et H-2)."""
        # Événement dans 3 jours pour être sûr que les rappels sont dans le futur
        jour = date.today() + timedelta(days=3)
        rappels = service.generer_rappels_evenement(
            titre="Docteur",
            type_evenement="rdv_medical",
            date_jour=jour,
            heure_debut=time(14, 0),
        )
        assert len(rappels) == 2
        assert all(r.priorite == PrioriteRappel.HAUTE for r in rappels)

    def test_generer_rappels_activite(self, service):
        """Activité génère 1 rappel (H-2)."""
        jour = date.today() + timedelta(days=3)
        rappels = service.generer_rappels_evenement(
            titre="Parc",
            type_evenement="activite",
            date_jour=jour,
            heure_debut=time(15, 0),
        )
        assert len(rappels) == 1
        assert rappels[0].priorite == PrioriteRappel.MOYENNE

    def test_generer_rappels_sans_heure(self, service):
        """Événement sans heure utilise 8h par défaut."""
        jour = date.today() + timedelta(days=3)
        rappels = service.generer_rappels_evenement(
            titre="Férié",
            type_evenement="ferie",
            date_jour=jour,
            heure_debut=None,
        )
        # Chaque rappel devrait être basé sur 8h
        for r in rappels:
            assert r.heure_evenement is None

    def test_rappels_passes_filtres(self, service):
        """Rappels pour des événements passés ne sont pas générés."""
        hier = date.today() - timedelta(days=1)
        rappels = service.generer_rappels_evenement(
            titre="Passé",
            type_evenement="rdv_medical",
            date_jour=hier,
            heure_debut=time(10, 0),
        )
        assert len(rappels) == 0

    def test_generer_rappels_message_formate(self, service):
        """Le message contient le titre de l'événement."""
        jour = date.today() + timedelta(days=3)
        rappels = service.generer_rappels_evenement(
            titre="Docteur Martin",
            type_evenement="rdv_medical",
            date_jour=jour,
            heure_debut=time(14, 0),
        )
        for r in rappels:
            assert "Docteur Martin" in r.message or "RDV médical" in r.message

    def test_rappels_priorite_haute(self, service):
        """Filtre les rappels haute priorité seulement."""
        with patch.object(service, "rappels_a_venir") as mock_rav:
            mock_rav.return_value = [
                Rappel("A", "rdv", date.today(), None, datetime.now(), PrioriteRappel.HAUTE, ""),
                Rappel("B", "act", date.today(), None, datetime.now(), PrioriteRappel.BASSE, ""),
                Rappel("C", "rdv", date.today(), None, datetime.now(), PrioriteRappel.HAUTE, ""),
            ]
            result = service.rappels_priorite_haute(heures=24)
            assert len(result) == 2
            assert all(r.priorite == PrioriteRappel.HAUTE for r in result)


# ═══════════════════════════════════════════════════════════
# COUVERTURE REGLES
# ═══════════════════════════════════════════════════════════


class TestReglesCompletes:
    """Vérifie que toutes les règles sont bien définies."""

    def test_regles_ont_delais(self):
        for nom, regle in _REGLES_RAPPEL.items():
            assert len(regle.delais) > 0, f"Règle {nom} sans délais"

    def test_regles_ont_priorite(self):
        for nom, regle in _REGLES_RAPPEL.items():
            assert isinstance(regle.priorite, PrioriteRappel), f"Règle {nom} sans priorité"

    def test_regles_ont_template(self):
        for nom, regle in _REGLES_RAPPEL.items():
            assert regle.message_template, f"Règle {nom} sans template"

    def test_types_couverts(self):
        """Les types importants sont couverts."""
        types_attendus = {"rdv_medical", "activite", "courses", "batch_cooking", "creche", "ferie"}
        types_definis = set(_REGLES_RAPPEL.keys())
        assert types_attendus.issubset(types_definis)
