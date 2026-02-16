"""
Tests pour src/modules/outils/accueil_utils.py
"""

from datetime import date, datetime, timedelta

import pytest

from src.modules.accueil.utils import (
    calculer_metriques_dashboard,
    compter_alertes_critiques,
    est_aujourdhui,
    est_cette_semaine,
    est_en_retard,
    generer_notifications,
    trier_notifications_par_priorite,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def alertes_variees():
    """Fixture: liste d'alertes variées"""
    return [
        {"type": "warning", "message": "Stock critique"},
        {"type": "warning", "message": "Péremption proche"},
        {"type": "info", "message": "Info normale"},
        {"type": "error", "message": "Erreur système"},
    ]


@pytest.fixture
def notifications_variees():
    """Fixture: liste de notifications avec priorités variées"""
    return [
        {"type": "info", "message": "Info", "priorite": "basse"},
        {"type": "warning", "message": "Warning", "priorite": "haute"},
        {"type": "info", "message": "Moyenne", "priorite": "moyenne"},
    ]


# ═══════════════════════════════════════════════════════════
# TESTS MÉTRIQUES DASHBOARD
# ═══════════════════════════════════════════════════════════


class TestCalculerMetriquesDashboard:
    """Tests pour la fonction calculer_metriques_dashboard"""

    def test_retourne_dictionnaire(self):
        """Teste que la fonction retourne un dictionnaire"""
        result = calculer_metriques_dashboard()
        assert isinstance(result, dict)

    def test_contient_cles_requises(self):
        """Teste que toutes les clés requises sont présentes"""
        result = calculer_metriques_dashboard()
        cles_attendues = [
            "recettes_total",
            "inventaire_alertes",
            "courses_a_acheter",
            "planning_semaine",
            "timestamp",
        ]
        for cle in cles_attendues:
            assert cle in result, f"Clé {cle} manquante"

    def test_valeurs_par_defaut(self):
        """Teste les valeurs par défaut"""
        result = calculer_metriques_dashboard()
        assert result["recettes_total"] == 0
        assert result["inventaire_alertes"] == 0
        assert result["courses_a_acheter"] == 0
        assert result["planning_semaine"] == 0

    def test_timestamp_format_iso(self):
        """Teste que le timestamp est au format ISO"""
        result = calculer_metriques_dashboard()
        # Doit pouvoir être parsé sans erreur
        datetime.fromisoformat(result["timestamp"])


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES CRITIQUES
# ═══════════════════════════════════════════════════════════


class TestCompterAlertesCritiques:
    """Tests pour la fonction compter_alertes_critiques"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        assert compter_alertes_critiques([]) == 0

    def test_none(self):
        """Teste avec None"""
        assert compter_alertes_critiques(None) == 0

    def test_avec_alertes_warning(self, alertes_variees):
        """Teste le comptage des alertes warning"""
        count = compter_alertes_critiques(alertes_variees)
        assert count == 2, "Devrait compter 2 alertes warning"

    def test_sans_alertes_warning(self):
        """Teste avec aucune alerte warning"""
        alertes = [
            {"type": "info", "message": "Info"},
            {"type": "error", "message": "Erreur"},
        ]
        assert compter_alertes_critiques(alertes) == 0

    def test_toutes_warning(self):
        """Teste avec toutes les alertes en warning"""
        alertes = [
            {"type": "warning", "message": "A"},
            {"type": "warning", "message": "B"},
            {"type": "warning", "message": "C"},
        ]
        assert compter_alertes_critiques(alertes) == 3


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class TestGenererNotifications:
    """Tests pour la fonction generer_notifications"""

    def test_aucun_parametre(self):
        """Teste avec aucun paramètre (tous None/False)"""
        notifications = generer_notifications()
        assert notifications == []

    def test_inventaire_critiques(self):
        """Teste avec des articles en stock critique"""
        articles = [{"nom": "Lait"}, {"nom": "Pain"}]
        notifications = generer_notifications(inventaire_critiques=articles)
        assert len(notifications) == 1
        assert notifications[0]["type"] == "warning"
        assert "2 article(s)" in notifications[0]["message"]
        assert notifications[0]["priorite"] == "haute"

    def test_peremption_proche(self):
        """Teste avec des articles proches de la péremption"""
        articles = [{"nom": "Yaourt"}]
        notifications = generer_notifications(peremption_proche=articles)
        assert len(notifications) == 1
        assert "périment bientôt" in notifications[0]["message"]

    def test_planning_vide(self):
        """Teste avec un planning vide"""
        notifications = generer_notifications(planning_vide=True)
        assert len(notifications) == 1
        assert notifications[0]["type"] == "info"
        assert notifications[0]["priorite"] == "basse"

    def test_combinaison_notifications(self):
        """Teste avec plusieurs notifications"""
        notifications = generer_notifications(
            inventaire_critiques=[{"nom": "A"}],
            peremption_proche=[{"nom": "B"}],
            planning_vide=True,
        )
        assert len(notifications) == 3

    def test_inventaire_critiques_vide(self):
        """Teste avec une liste vide de critiques"""
        notifications = generer_notifications(inventaire_critiques=[])
        assert len(notifications) == 0

    def test_peremption_proche_vide(self):
        """Teste avec une liste vide de péremption"""
        notifications = generer_notifications(peremption_proche=[])
        assert len(notifications) == 0


# ═══════════════════════════════════════════════════════════
# TESTS TRI NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class TestTrierNotificationsParPriorite:
    """Tests pour la fonction trier_notifications_par_priorite"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        assert trier_notifications_par_priorite([]) == []

    def test_tri_correct(self, notifications_variees):
        """Teste que le tri est correct (haute → moyenne → basse)"""
        triees = trier_notifications_par_priorite(notifications_variees)
        assert triees[0]["priorite"] == "haute"
        assert triees[1]["priorite"] == "moyenne"
        assert triees[2]["priorite"] == "basse"

    def test_priorite_manquante_va_en_fin(self):
        """Teste que les notifications sans priorité vont en fin"""
        notifications = [
            {"type": "info", "message": "Sans priorité"},
            {"type": "warning", "message": "Haute", "priorite": "haute"},
        ]
        triees = trier_notifications_par_priorite(notifications)
        assert triees[0]["priorite"] == "haute"
        assert triees[1].get("priorite") is None

    def test_meme_priorite_garde_ordre(self):
        """Teste que les notifications de même priorité gardent leur ordre"""
        notifications = [
            {"type": "warning", "message": "Premier", "priorite": "haute"},
            {"type": "warning", "message": "Deuxième", "priorite": "haute"},
        ]
        triees = trier_notifications_par_priorite(notifications)
        assert triees[0]["message"] == "Premier"
        assert triees[1]["message"] == "Deuxième"


# ═══════════════════════════════════════════════════════════
# TESTS EST_CETTE_SEMAINE
# ═══════════════════════════════════════════════════════════


class TestEstCetteSemaine:
    """Tests pour la fonction est_cette_semaine"""

    def test_avec_date_aujourdhui(self):
        """Teste avec la date d'aujourd'hui"""
        assert est_cette_semaine(date.today()) is True

    def test_avec_date_semaine_prochaine(self):
        """Teste avec une date la semaine prochaine"""
        semaine_prochaine = date.today() + timedelta(days=8)
        assert est_cette_semaine(semaine_prochaine) is False

    def test_avec_date_semaine_derniere(self):
        """Teste avec une date la semaine dernière"""
        semaine_derniere = date.today() - timedelta(days=8)
        assert est_cette_semaine(semaine_derniere) is False

    def test_avec_string_iso(self):
        """Teste avec une date au format string ISO"""
        assert est_cette_semaine(date.today().isoformat()) is True

    def test_avec_datetime(self):
        """Teste avec un objet datetime"""
        assert est_cette_semaine(datetime.now()) is True

    def test_debut_semaine(self):
        """Teste avec le début de la semaine courante"""
        aujourd_hui = date.today()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        assert est_cette_semaine(debut_semaine) is True

    def test_fin_semaine(self):
        """Teste avec la fin de la semaine courante"""
        aujourd_hui = date.today()
        fin_semaine = aujourd_hui + timedelta(days=6 - aujourd_hui.weekday())
        assert est_cette_semaine(fin_semaine) is True


# ═══════════════════════════════════════════════════════════
# TESTS EST_AUJOURDHUI
# ═══════════════════════════════════════════════════════════


class TestEstAujourdhui:
    """Tests pour la fonction est_aujourdhui"""

    def test_avec_date_aujourdhui(self):
        """Teste avec la date d'aujourd'hui"""
        assert est_aujourdhui(date.today()) is True

    def test_avec_date_hier(self):
        """Teste avec la date d'hier"""
        hier = date.today() - timedelta(days=1)
        assert est_aujourdhui(hier) is False

    def test_avec_date_demain(self):
        """Teste avec la date de demain"""
        demain = date.today() + timedelta(days=1)
        assert est_aujourdhui(demain) is False

    def test_avec_string_iso(self):
        """Teste avec une date au format string ISO"""
        assert est_aujourdhui(date.today().isoformat()) is True

    def test_avec_datetime(self):
        """Teste avec un objet datetime"""
        assert est_aujourdhui(datetime.now()) is True

    def test_avec_datetime_string(self):
        """Teste avec un datetime string ISO"""
        assert est_aujourdhui(datetime.now().isoformat()) is True


# ═══════════════════════════════════════════════════════════
# TESTS EST_EN_RETARD
# ═══════════════════════════════════════════════════════════


class TestEstEnRetard:
    """Tests pour la fonction est_en_retard"""

    def test_avec_date_aujourdhui(self):
        """Teste avec la date d'aujourd'hui - pas en retard"""
        assert est_en_retard(date.today()) is False

    def test_avec_date_hier(self):
        """Teste avec la date d'hier - en retard"""
        hier = date.today() - timedelta(days=1)
        assert est_en_retard(hier) is True

    def test_avec_date_demain(self):
        """Teste avec la date de demain - pas en retard"""
        demain = date.today() + timedelta(days=1)
        assert est_en_retard(demain) is False

    def test_avec_date_ancienne(self):
        """Teste avec une date ancienne"""
        ancienne = date.today() - timedelta(days=100)
        assert est_en_retard(ancienne) is True

    def test_avec_string_iso(self):
        """Teste avec une date au format string ISO"""
        hier_str = (date.today() - timedelta(days=1)).isoformat()
        assert est_en_retard(hier_str) is True

    def test_avec_datetime(self):
        """Teste avec un objet datetime hier"""
        hier_dt = datetime.now() - timedelta(days=1)
        assert est_en_retard(hier_dt) is True

    def test_avec_datetime_demain(self):
        """Teste avec un datetime de demain"""
        demain_dt = datetime.now() + timedelta(days=1)
        assert est_en_retard(demain_dt) is False
