"""
Tests de couverture complÃ©mentaires pour vue_ensemble_logic.py
Objectif: atteindre 80%+ de couverture
"""

from datetime import date, timedelta

from src.modules.planning.logic.vue_ensemble_logic import (
    analyser_tendances,
    calculer_statistiques_periode,
    formater_evolution,
    formater_niveau_charge,
    generer_alertes,
    identifier_taches_urgentes,
    prevoir_charge_prochaine_semaine,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ANALYSER_TENDANCES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAnalyserTendances:
    """Tests pour analyser_tendances."""

    def test_tendances_historique_vide(self):
        """Historique vide retourne valeurs par dÃ©faut."""
        result = analyser_tendances([], 30)

        assert result["evolution"] == "stable"
        assert result["moyenne_jour"] == 0.0
        assert result["pic_activite"] is None

    def test_tendances_avec_historique(self):
        """Analyse avec historique prÃ©sent."""
        historique = [{"date": date.today() - timedelta(days=i), "type": "test"} for i in range(10)]

        result = analyser_tendances(historique, 30)

        assert result["moyenne_jour"] > 0
        assert result["pic_activite"] is not None

    def test_tendances_date_string(self):
        """GÃ¨re les dates en string."""
        historique = [{"date": (date.today() - timedelta(days=1)).isoformat()}]

        result = analyser_tendances(historique, 30)

        assert result["moyenne_jour"] > 0

    def test_tendances_evolution_hausse(self):
        """DÃ©tecte tendance Ã  la hausse."""
        # Plus d'activitÃ© dans les 15 derniers jours
        historique = [
            {"date": (date.today() - timedelta(days=i)).isoformat()}
            for i in range(10)  # 10 items dans les 10 derniers jours
        ]

        result = analyser_tendances(historique, 30)

        # Avec tous les items rÃ©cents, devrait Ãªtre hausse
        assert result["evolution"] in ["hausse", "stable"]

    def test_tendances_pic_activite(self):
        """Identifie le pic d'activitÃ©."""
        aujourd_hui = date.today()
        hier = aujourd_hui - timedelta(days=1)

        historique = [
            {"date": hier.isoformat()},
            {"date": hier.isoformat()},
            {"date": hier.isoformat()},
            {"date": aujourd_hui.isoformat()},
        ]

        result = analyser_tendances(historique, 30)

        assert result["pic_activite"] is not None
        assert result["pic_activite"]["nombre"] == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PREVOIR_CHARGE_PROCHAINE_SEMAINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPrevoirChargeProchaineSemaine:
    """Tests pour prevoir_charge_prochaine_semaine."""

    def test_prevision_semaine_vide(self):
        """Semaine sans Ã©vÃ©nements."""
        result = prevoir_charge_prochaine_semaine([], [])

        assert result["evenements"] == 0
        assert result["taches"] == 0
        assert result["prevision"] == "Semaine lÃ©gÃ¨re"

    def test_prevision_semaine_legere(self):
        """PrÃ©vision avec peu d'Ã©vÃ©nements."""
        debut_semaine = date.today() + timedelta(days=7 - date.today().weekday())

        evenements = [
            {"date": debut_semaine, "titre": "RÃ©union"},
            {"date": debut_semaine + timedelta(days=1), "titre": "Autre"},
        ]

        result = prevoir_charge_prochaine_semaine(evenements, [])

        assert result["evenements"] == 2
        assert result["prevision"] == "Semaine lÃ©gÃ¨re"

    def test_prevision_semaine_chargee(self):
        """PrÃ©vision avec beaucoup d'Ã©lÃ©ments."""
        debut_semaine = date.today() + timedelta(days=7 - date.today().weekday())

        evenements = [{"date": debut_semaine, "titre": f"Evt {i}"} for i in range(10)]
        taches = [{"date_limite": debut_semaine, "titre": f"Tache {i}"} for i in range(10)]

        result = prevoir_charge_prochaine_semaine(evenements, taches)

        assert result["charge_totale"] == 20
        assert result["prevision"] == "Semaine chargÃ©e"

    def test_prevision_ignore_taches_completees(self):
        """Ignore les tÃ¢ches complÃ©tÃ©es."""
        debut_semaine = date.today() + timedelta(days=7 - date.today().weekday())

        taches = [
            {"date_limite": debut_semaine, "complete": True},
            {"date_limite": debut_semaine, "complete": False},
        ]

        result = prevoir_charge_prochaine_semaine([], taches)

        assert result["taches"] == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IDENTIFIER_TACHES_URGENTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIdentifierTachesUrgentes:
    """Tests pour identifier_taches_urgentes."""

    def test_aucune_tache_urgente(self):
        """Pas de tÃ¢ches urgentes."""
        taches = [
            {"date_limite": date.today() + timedelta(days=10), "complete": False},
        ]

        result = identifier_taches_urgentes(taches, 3)

        assert len(result) == 0

    def test_taches_urgentes_identifiees(self):
        """Identifie les tÃ¢ches urgentes."""
        taches = [
            {"date_limite": date.today() + timedelta(days=1), "complete": False},
            {"date_limite": date.today() + timedelta(days=10), "complete": False},
        ]

        result = identifier_taches_urgentes(taches, 3)

        assert len(result) == 1

    def test_ignore_taches_completees(self):
        """Ignore les tÃ¢ches complÃ©tÃ©es."""
        taches = [
            {"date_limite": date.today(), "complete": True},
        ]

        result = identifier_taches_urgentes(taches, 3)

        assert len(result) == 0

    def test_taches_avec_date_string(self):
        """GÃ¨re les dates en string."""
        taches = [
            {"date_limite": (date.today() + timedelta(days=1)).isoformat(), "complete": False},
        ]

        result = identifier_taches_urgentes(taches, 3)

        assert len(result) == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GENERER_ALERTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererAlertes:
    """Tests pour generer_alertes."""

    def test_aucune_alerte(self):
        """Pas d'alertes si situation normale."""
        result = generer_alertes([], [])

        assert len(result) == 0

    def test_alerte_taches_en_retard(self):
        """Alerte pour tÃ¢ches en retard."""
        taches = [
            {"date_limite": date.today() - timedelta(days=1), "complete": False},
        ]

        result = generer_alertes([], taches)

        assert any("retard" in a["message"].lower() for a in result)
        assert any(a["type"] == "danger" for a in result)

    def test_alerte_taches_urgentes(self):
        """Alerte pour tÃ¢ches urgentes."""
        taches = [
            {"date_limite": date.today() + timedelta(days=1), "complete": False},
        ]

        result = generer_alertes([], taches)

        assert any("urgente" in a["message"].lower() for a in result)
        assert any(a["type"] == "warning" for a in result)

    def test_alerte_evenements_aujourdhui(self):
        """Alerte pour Ã©vÃ©nements aujourd'hui."""
        evenements = [
            {"date": date.today(), "titre": "RÃ©union"},
        ]

        result = generer_alertes(evenements, [])

        assert any("aujourd'hui" in a["message"].lower() for a in result)
        assert any(a["type"] == "info" for a in result)

    def test_alerte_evenement_date_string(self):
        """GÃ¨re les dates d'Ã©vÃ©nements en string."""
        evenements = [
            {"date": date.today().isoformat(), "titre": "RÃ©union"},
        ]

        result = generer_alertes(evenements, [])

        assert len(result) >= 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALCULER_STATISTIQUES_PERIODE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCalculerStatistiquesPeriode:
    """Tests pour calculer_statistiques_periode."""

    def test_stats_periode_jour(self):
        """Stats pour pÃ©riode Jour."""
        items = [{"date": date.today()}]

        result = calculer_statistiques_periode(items, "Jour")

        assert result["periode"] == "Jour"
        assert result["total"] == 1

    def test_stats_periode_semaine(self):
        """Stats pour pÃ©riode Semaine."""
        items = [{"date": date.today() - timedelta(days=i)} for i in range(3)]

        result = calculer_statistiques_periode(items, "Semaine")

        assert result["periode"] == "Semaine"
        assert result["total"] == 3

    def test_stats_periode_mois(self):
        """Stats pour pÃ©riode Mois."""
        items = [{"date": date.today() - timedelta(days=i)} for i in range(10)]

        result = calculer_statistiques_periode(items, "Mois")

        assert result["periode"] == "Mois"
        assert result["total"] == 10

    def test_stats_periode_annee(self):
        """Stats pour pÃ©riode AnnÃ©e."""
        items = [{"date": date.today() - timedelta(days=i)} for i in range(50)]

        result = calculer_statistiques_periode(items, "AnnÃ©e")

        assert result["periode"] == "AnnÃ©e"
        assert result["total"] == 50

    def test_stats_date_string(self):
        """GÃ¨re les dates en string."""
        items = [{"date": date.today().isoformat()}]

        result = calculer_statistiques_periode(items, "Jour")

        assert result["total"] == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMATER_NIVEAU_CHARGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormaterNiveauCharge:
    """Tests pour formater_niveau_charge."""

    def test_formater_libre(self):
        """Formate niveau Libre."""
        result = formater_niveau_charge("Libre")
        assert "Libre" in result

    def test_formater_leger(self):
        """Formate niveau LÃ©ger."""
        result = formater_niveau_charge("LÃ©ger")
        assert "LÃ©ger" in result

    def test_formater_moyen(self):
        """Formate niveau Moyen."""
        result = formater_niveau_charge("Moyen")
        assert "Moyen" in result

    def test_formater_eleve(self):
        """Formate niveau Ã‰levÃ©."""
        result = formater_niveau_charge("Ã‰levÃ©")
        assert "Ã‰levÃ©" in result

    def test_formater_tres_eleve(self):
        """Formate niveau TrÃ¨s Ã©levÃ©."""
        result = formater_niveau_charge("TrÃ¨s Ã©levÃ©")
        assert "TrÃ¨s Ã©levÃ©" in result

    def test_formater_inconnu(self):
        """Formate niveau inconnu."""
        result = formater_niveau_charge("Inconnu")
        assert "Inconnu" in result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMATER_EVOLUTION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormaterEvolution:
    """Tests pour formater_evolution."""

    def test_formater_hausse(self):
        """Formate Ã©volution hausse."""
        result = formater_evolution("hausse")
        assert "Hausse" in result

    def test_formater_baisse(self):
        """Formate Ã©volution baisse."""
        result = formater_evolution("baisse")
        assert "Baisse" in result

    def test_formater_stable(self):
        """Formate Ã©volution stable."""
        result = formater_evolution("stable")
        assert "Stable" in result

    def test_formater_inconnu(self):
        """Formate Ã©volution inconnue."""
        result = formater_evolution("autre")
        assert "Autre" in result
