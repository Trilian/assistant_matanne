"""
Tests pour accueil_logic.py
Couverture cible: 80%+
"""
import pytest
from datetime import date, datetime, timedelta

from src.domains.utils.logic.accueil_logic import (
    calculer_metriques_dashboard,
    compter_alertes_critiques,
    generer_notifications,
    trier_notifications_par_priorite,
    est_cette_semaine,
    est_aujourdhui,
    est_en_retard,
)


# ═══════════════════════════════════════════════════════════
# TESTS MÉTRIQUES DASHBOARD
# ═══════════════════════════════════════════════════════════


class TestCalculerMetriques:
    """Tests pour calculer_metriques_dashboard."""

    def test_retourne_dict(self):
        """Retourne un dictionnaire."""
        result = calculer_metriques_dashboard()
        assert isinstance(result, dict)

    def test_contient_cles_principales(self):
        """Contient les clés attendues."""
        result = calculer_metriques_dashboard()
        assert "recettes_total" in result
        assert "inventaire_alertes" in result
        assert "courses_a_acheter" in result
        assert "planning_semaine" in result
        assert "timestamp" in result


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES CRITIQUES
# ═══════════════════════════════════════════════════════════


class TestCompterAlertes:
    """Tests pour compter_alertes_critiques."""

    def test_liste_vide(self):
        """Retourne 0 pour liste vide."""
        assert compter_alertes_critiques([]) == 0

    def test_liste_none(self):
        """Retourne 0 pour None."""
        assert compter_alertes_critiques(None) == 0

    def test_compte_warnings(self):
        """Compte les alertes de type warning."""
        alertes = [
            {"type": "warning", "message": "Alerte 1"},
            {"type": "info", "message": "Info"},
            {"type": "warning", "message": "Alerte 2"},
        ]
        assert compter_alertes_critiques(alertes) == 2

    def test_pas_de_warnings(self):
        """Retourne 0 si aucun warning."""
        alertes = [
            {"type": "info", "message": "Info"},
            {"type": "success", "message": "OK"},
        ]
        assert compter_alertes_critiques(alertes) == 0


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class TestGenererNotifications:
    """Tests pour generer_notifications."""

    def test_aucune_notification(self):
        """Liste vide si rien à signaler."""
        result = generer_notifications()
        assert result == []

    def test_notification_inventaire_critique(self):
        """Génère notification pour inventaire critique."""
        result = generer_notifications(inventaire_critiques=[{"nom": "Lait"}])
        assert len(result) == 1
        assert result[0]["type"] == "warning"
        assert "critique" in result[0]["message"].lower()

    def test_notification_peremption(self):
        """Génère notification pour péremption proche."""
        result = generer_notifications(peremption_proche=[{"nom": "Yaourt"}])
        assert len(result) == 1
        assert "périment" in result[0]["message"].lower()

    def test_notification_planning_vide(self):
        """Génère notification pour planning vide."""
        result = generer_notifications(planning_vide=True)
        assert len(result) == 1
        assert result[0]["type"] == "info"

    def test_plusieurs_notifications(self):
        """Génère plusieurs notifications."""
        result = generer_notifications(
            inventaire_critiques=[{"nom": "Lait"}],
            peremption_proche=[{"nom": "Yaourt"}],
            planning_vide=True
        )
        assert len(result) == 3


# ═══════════════════════════════════════════════════════════
# TESTS TRI NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class TestTrierNotifications:
    """Tests pour trier_notifications_par_priorite."""

    def test_tri_priorites(self):
        """Trie haute > moyenne > basse."""
        notifications = [
            {"message": "N1", "priorite": "basse"},
            {"message": "N2", "priorite": "haute"},
            {"message": "N3", "priorite": "moyenne"},
        ]
        result = trier_notifications_par_priorite(notifications)
        assert result[0]["priorite"] == "haute"
        assert result[1]["priorite"] == "moyenne"
        assert result[2]["priorite"] == "basse"

    def test_liste_vide(self):
        """Gère liste vide."""
        result = trier_notifications_par_priorite([])
        assert result == []

    def test_priorite_inconnue(self):
        """Priorité inconnue = basse."""
        notifications = [
            {"message": "N1", "priorite": "haute"},
            {"message": "N2"},  # Pas de priorité
        ]
        result = trier_notifications_par_priorite(notifications)
        assert result[0]["priorite"] == "haute"


# ═══════════════════════════════════════════════════════════
# TESTS VÉRIFICATION DATES
# ═══════════════════════════════════════════════════════════


class TestEstCetteSemaine:
    """Tests pour est_cette_semaine."""

    def test_aujourdhui(self):
        """Aujourd'hui est cette semaine."""
        assert est_cette_semaine(date.today()) is True

    def test_demain(self):
        """Demain est probablement cette semaine (sauf dimanche)."""
        demain = date.today() + timedelta(days=1)
        # Si on est samedi ou dimanche, demain pourrait être la semaine prochaine
        if date.today().weekday() <= 4:  # Lundi à vendredi
            assert est_cette_semaine(demain) is True

    def test_semaine_prochaine(self):
        """Semaine prochaine n'est pas cette semaine."""
        dans_10_jours = date.today() + timedelta(days=10)
        assert est_cette_semaine(dans_10_jours) is False

    def test_date_string(self):
        """Gère les dates en string ISO."""
        assert est_cette_semaine(date.today().isoformat()) is True

    def test_datetime(self):
        """Gère les datetime."""
        assert est_cette_semaine(datetime.now()) is True


class TestEstAujourdhui:
    """Tests pour est_aujourdhui."""

    def test_aujourdhui(self):
        """Aujourd'hui = True."""
        assert est_aujourdhui(date.today()) is True

    def test_hier(self):
        """Hier = False."""
        hier = date.today() - timedelta(days=1)
        assert est_aujourdhui(hier) is False

    def test_demain(self):
        """Demain = False."""
        demain = date.today() + timedelta(days=1)
        assert est_aujourdhui(demain) is False

    def test_date_string(self):
        """Gère les dates en string ISO."""
        assert est_aujourdhui(date.today().isoformat()) is True


class TestEstEnRetard:
    """Tests pour est_en_retard."""

    def test_hier_en_retard(self):
        """Hier est en retard."""
        hier = date.today() - timedelta(days=1)
        assert est_en_retard(hier) is True

    def test_aujourdhui_pas_en_retard(self):
        """Aujourd'hui n'est pas en retard."""
        assert est_en_retard(date.today()) is False

    def test_demain_pas_en_retard(self):
        """Demain n'est pas en retard."""
        demain = date.today() + timedelta(days=1)
        assert est_en_retard(demain) is False

    def test_date_string(self):
        """Gère les dates en string ISO."""
        hier = (date.today() - timedelta(days=1)).isoformat()
        assert est_en_retard(hier) is True
