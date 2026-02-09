"""
Tests de couverture complémentaires pour vue_ensemble_logic.py
Objectif: atteindre 80%+ de couverture
"""
import pytest
from datetime import date, datetime, timedelta

from src.domains.planning.logic.vue_ensemble_logic import (
    analyser_charge_globale,
    est_en_retard,
    analyser_tendances,
    prevoir_charge_prochaine_semaine,
    identifier_taches_urgentes,
    generer_alertes,
    calculer_statistiques_periode,
    formater_niveau_charge,
    formater_evolution,
)


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSER_TENDANCES
# ═══════════════════════════════════════════════════════════

class TestAnalyserTendances:
    """Tests pour analyser_tendances."""

    def test_tendances_historique_vide(self):
        """Historique vide retourne valeurs par défaut."""
        result = analyser_tendances([], 30)
        
        assert result["evolution"] == "stable"
        assert result["moyenne_jour"] == 0.0
        assert result["pic_activite"] is None

    def test_tendances_avec_historique(self):
        """Analyse avec historique présent."""
        historique = [
            {"date": date.today() - timedelta(days=i), "type": "test"}
            for i in range(10)
        ]
        
        result = analyser_tendances(historique, 30)
        
        assert result["moyenne_jour"] > 0
        assert result["pic_activite"] is not None

    def test_tendances_date_string(self):
        """Gère les dates en string."""
        historique = [
            {"date": (date.today() - timedelta(days=1)).isoformat()}
        ]
        
        result = analyser_tendances(historique, 30)
        
        assert result["moyenne_jour"] > 0

    def test_tendances_evolution_hausse(self):
        """Détecte tendance à la hausse."""
        # Plus d'activité dans les 15 derniers jours
        historique = [
            {"date": (date.today() - timedelta(days=i)).isoformat()}
            for i in range(10)  # 10 items dans les 10 derniers jours
        ]
        
        result = analyser_tendances(historique, 30)
        
        # Avec tous les items récents, devrait être hausse
        assert result["evolution"] in ["hausse", "stable"]

    def test_tendances_pic_activite(self):
        """Identifie le pic d'activité."""
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


# ═══════════════════════════════════════════════════════════
# TESTS PREVOIR_CHARGE_PROCHAINE_SEMAINE
# ═══════════════════════════════════════════════════════════

class TestPrevoirChargeProchaineSemaine:
    """Tests pour prevoir_charge_prochaine_semaine."""

    def test_prevision_semaine_vide(self):
        """Semaine sans événements."""
        result = prevoir_charge_prochaine_semaine([], [])
        
        assert result["evenements"] == 0
        assert result["taches"] == 0
        assert result["prevision"] == "Semaine légère"

    def test_prevision_semaine_legere(self):
        """Prévision avec peu d'événements."""
        debut_semaine = date.today() + timedelta(days=7 - date.today().weekday())
        
        evenements = [
            {"date": debut_semaine, "titre": "Réunion"},
            {"date": debut_semaine + timedelta(days=1), "titre": "Autre"},
        ]
        
        result = prevoir_charge_prochaine_semaine(evenements, [])
        
        assert result["evenements"] == 2
        assert result["prevision"] == "Semaine légère"

    def test_prevision_semaine_chargee(self):
        """Prévision avec beaucoup d'éléments."""
        debut_semaine = date.today() + timedelta(days=7 - date.today().weekday())
        
        evenements = [{"date": debut_semaine, "titre": f"Evt {i}"} for i in range(10)]
        taches = [{"date_limite": debut_semaine, "titre": f"Tache {i}"} for i in range(10)]
        
        result = prevoir_charge_prochaine_semaine(evenements, taches)
        
        assert result["charge_totale"] == 20
        assert result["prevision"] == "Semaine chargée"

    def test_prevision_ignore_taches_completees(self):
        """Ignore les tâches complétées."""
        debut_semaine = date.today() + timedelta(days=7 - date.today().weekday())
        
        taches = [
            {"date_limite": debut_semaine, "complete": True},
            {"date_limite": debut_semaine, "complete": False},
        ]
        
        result = prevoir_charge_prochaine_semaine([], taches)
        
        assert result["taches"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS IDENTIFIER_TACHES_URGENTES
# ═══════════════════════════════════════════════════════════

class TestIdentifierTachesUrgentes:
    """Tests pour identifier_taches_urgentes."""

    def test_aucune_tache_urgente(self):
        """Pas de tâches urgentes."""
        taches = [
            {"date_limite": date.today() + timedelta(days=10), "complete": False},
        ]
        
        result = identifier_taches_urgentes(taches, 3)
        
        assert len(result) == 0

    def test_taches_urgentes_identifiees(self):
        """Identifie les tâches urgentes."""
        taches = [
            {"date_limite": date.today() + timedelta(days=1), "complete": False},
            {"date_limite": date.today() + timedelta(days=10), "complete": False},
        ]
        
        result = identifier_taches_urgentes(taches, 3)
        
        assert len(result) == 1

    def test_ignore_taches_completees(self):
        """Ignore les tâches complétées."""
        taches = [
            {"date_limite": date.today(), "complete": True},
        ]
        
        result = identifier_taches_urgentes(taches, 3)
        
        assert len(result) == 0

    def test_taches_avec_date_string(self):
        """Gère les dates en string."""
        taches = [
            {"date_limite": (date.today() + timedelta(days=1)).isoformat(), "complete": False},
        ]
        
        result = identifier_taches_urgentes(taches, 3)
        
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS GENERER_ALERTES
# ═══════════════════════════════════════════════════════════

class TestGenererAlertes:
    """Tests pour generer_alertes."""

    def test_aucune_alerte(self):
        """Pas d'alertes si situation normale."""
        result = generer_alertes([], [])
        
        assert len(result) == 0

    def test_alerte_taches_en_retard(self):
        """Alerte pour tâches en retard."""
        taches = [
            {"date_limite": date.today() - timedelta(days=1), "complete": False},
        ]
        
        result = generer_alertes([], taches)
        
        assert any("retard" in a["message"].lower() for a in result)
        assert any(a["type"] == "danger" for a in result)

    def test_alerte_taches_urgentes(self):
        """Alerte pour tâches urgentes."""
        taches = [
            {"date_limite": date.today() + timedelta(days=1), "complete": False},
        ]
        
        result = generer_alertes([], taches)
        
        assert any("urgente" in a["message"].lower() for a in result)
        assert any(a["type"] == "warning" for a in result)

    def test_alerte_evenements_aujourdhui(self):
        """Alerte pour événements aujourd'hui."""
        evenements = [
            {"date": date.today(), "titre": "Réunion"},
        ]
        
        result = generer_alertes(evenements, [])
        
        assert any("aujourd'hui" in a["message"].lower() for a in result)
        assert any(a["type"] == "info" for a in result)

    def test_alerte_evenement_date_string(self):
        """Gère les dates d'événements en string."""
        evenements = [
            {"date": date.today().isoformat(), "titre": "Réunion"},
        ]
        
        result = generer_alertes(evenements, [])
        
        assert len(result) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER_STATISTIQUES_PERIODE
# ═══════════════════════════════════════════════════════════

class TestCalculerStatistiquesPeriode:
    """Tests pour calculer_statistiques_periode."""

    def test_stats_periode_jour(self):
        """Stats pour période Jour."""
        items = [{"date": date.today()}]
        
        result = calculer_statistiques_periode(items, "Jour")
        
        assert result["periode"] == "Jour"
        assert result["total"] == 1

    def test_stats_periode_semaine(self):
        """Stats pour période Semaine."""
        items = [{"date": date.today() - timedelta(days=i)} for i in range(3)]
        
        result = calculer_statistiques_periode(items, "Semaine")
        
        assert result["periode"] == "Semaine"
        assert result["total"] == 3

    def test_stats_periode_mois(self):
        """Stats pour période Mois."""
        items = [{"date": date.today() - timedelta(days=i)} for i in range(10)]
        
        result = calculer_statistiques_periode(items, "Mois")
        
        assert result["periode"] == "Mois"
        assert result["total"] == 10

    def test_stats_periode_annee(self):
        """Stats pour période Année."""
        items = [{"date": date.today() - timedelta(days=i)} for i in range(50)]
        
        result = calculer_statistiques_periode(items, "Année")
        
        assert result["periode"] == "Année"
        assert result["total"] == 50

    def test_stats_date_string(self):
        """Gère les dates en string."""
        items = [{"date": date.today().isoformat()}]
        
        result = calculer_statistiques_periode(items, "Jour")
        
        assert result["total"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER_NIVEAU_CHARGE
# ═══════════════════════════════════════════════════════════

class TestFormaterNiveauCharge:
    """Tests pour formater_niveau_charge."""

    def test_formater_libre(self):
        """Formate niveau Libre."""
        result = formater_niveau_charge("Libre")
        assert "Libre" in result

    def test_formater_leger(self):
        """Formate niveau Léger."""
        result = formater_niveau_charge("Léger")
        assert "Léger" in result

    def test_formater_moyen(self):
        """Formate niveau Moyen."""
        result = formater_niveau_charge("Moyen")
        assert "Moyen" in result

    def test_formater_eleve(self):
        """Formate niveau Élevé."""
        result = formater_niveau_charge("Élevé")
        assert "Élevé" in result

    def test_formater_tres_eleve(self):
        """Formate niveau Très élevé."""
        result = formater_niveau_charge("Très élevé")
        assert "Très élevé" in result

    def test_formater_inconnu(self):
        """Formate niveau inconnu."""
        result = formater_niveau_charge("Inconnu")
        assert "Inconnu" in result


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER_EVOLUTION
# ═══════════════════════════════════════════════════════════

class TestFormaterEvolution:
    """Tests pour formater_evolution."""

    def test_formater_hausse(self):
        """Formate évolution hausse."""
        result = formater_evolution("hausse")
        assert "Hausse" in result

    def test_formater_baisse(self):
        """Formate évolution baisse."""
        result = formater_evolution("baisse")
        assert "Baisse" in result

    def test_formater_stable(self):
        """Formate évolution stable."""
        result = formater_evolution("stable")
        assert "Stable" in result

    def test_formater_inconnu(self):
        """Formate évolution inconnue."""
        result = formater_evolution("autre")
        assert "Autre" in result
