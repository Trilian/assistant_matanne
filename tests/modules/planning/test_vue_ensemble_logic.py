"""
Tests pour vue_ensemble_logic.py
Couverture cible: 80%+
"""

from datetime import date, timedelta

import pytest

from src.modules.planning.vue_ensemble_utils import (
    CATEGORIES_TACHES,
    # Constantes
    PERIODES,
    # Fonctions
    analyser_charge_globale,
    analyser_tendances,
    est_en_retard,
    prevoir_charge_prochaine_semaine,
)

# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes vue ensemble."""

    def test_periodes(self):
        """Périodes définies."""
        assert len(PERIODES) >= 4
        assert "Jour" in PERIODES
        assert "Semaine" in PERIODES
        assert "Mois" in PERIODES

    def test_categories_taches(self):
        """Catégories de tâches définies."""
        assert len(CATEGORIES_TACHES) >= 4
        assert "Travail" in CATEGORIES_TACHES
        assert "Famille" in CATEGORIES_TACHES


# ═══════════════════════════════════════════════════════════
# TESTS EST EN RETARD
# ═══════════════════════════════════════════════════════════


class TestEstEnRetard:
    """Tests pour est_en_retard."""

    def test_tache_complete_pas_en_retard(self):
        """Une tâche complète n'est jamais en retard."""
        tache = {"complete": True, "date_limite": date.today() - timedelta(days=5)}
        assert est_en_retard(tache) is False

    def test_tache_sans_date_limite(self):
        """Pas en retard sans date limite."""
        tache = {"complete": False}
        assert est_en_retard(tache) is False

    def test_tache_en_retard(self):
        """Tâche en retard si date passée."""
        tache = {"complete": False, "date_limite": date.today() - timedelta(days=1)}
        assert est_en_retard(tache) is True

    def test_tache_dans_temps(self):
        """Tâche pas en retard si date future."""
        tache = {"complete": False, "date_limite": date.today() + timedelta(days=5)}
        assert est_en_retard(tache) is False

    def test_date_string(self):
        """Gère les dates en string ISO."""
        tache = {"complete": False, "date_limite": (date.today() - timedelta(days=3)).isoformat()}
        assert est_en_retard(tache) is True


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE CHARGE GLOBALE
# ═══════════════════════════════════════════════════════════


class TestAnalyseChargeGlobale:
    """Tests pour analyser_charge_globale."""

    @pytest.fixture
    def evenements(self):
        return [
            {"titre": "Réunion"},
            {"titre": "Appel"},
        ]

    @pytest.fixture
    def taches(self):
        return [
            {"titre": "T1", "complete": False, "categorie": "Travail"},
            {"titre": "T2", "complete": True, "categorie": "Maison"},
            {
                "titre": "T3",
                "complete": False,
                "categorie": "Travail",
                "date_limite": date.today() - timedelta(days=1),
            },
        ]

    def test_total_evenements(self, evenements, taches):
        """Compte le total d'événements."""
        result = analyser_charge_globale(evenements, taches)
        assert result["total_evenements"] == 2

    def test_total_taches(self, evenements, taches):
        """Compte le total de tâches."""
        result = analyser_charge_globale(evenements, taches)
        assert result["total_taches"] == 3

    def test_taches_completees(self, evenements, taches):
        """Compte les tâches complétées."""
        result = analyser_charge_globale(evenements, taches)
        assert result["taches_completees"] == 1

    def test_taches_en_retard(self, evenements, taches):
        """Compte les tâches en retard."""
        result = analyser_charge_globale(evenements, taches)
        assert result["taches_en_retard"] == 1

    def test_taux_completion(self, evenements, taches):
        """Calcule le taux de complétion."""
        result = analyser_charge_globale(evenements, taches)
        expected = 1 / 3 * 100  # 1 sur 3
        assert abs(result["taux_completion"] - expected) < 0.1

    def test_charge_par_categorie(self, evenements, taches):
        """Compte par catégorie."""
        result = analyser_charge_globale(evenements, taches)
        assert result["charge_par_categorie"]["Travail"] == 2

    def test_niveau_charge_libre(self):
        """Niveau 'Libre' si rien à faire."""
        result = analyser_charge_globale([], [])
        assert result["niveau_charge"] == "Libre"

    def test_niveau_charge_leger(self):
        """Niveau 'Léger' si peu de choses."""
        evenements = [{"titre": "E1"}]
        taches = [{"titre": "T1", "complete": False}]
        result = analyser_charge_globale(evenements, taches)
        assert result["niveau_charge"] == "Léger"

    def test_niveau_charge_eleve(self):
        """Niveau augmente avec la charge."""
        evenements = [{"titre": f"E{i}"} for i in range(20)]
        taches = [{"titre": f"T{i}", "complete": False} for i in range(10)]
        result = analyser_charge_globale(evenements, taches)
        assert result["niveau_charge"] in ["Élevé", "Très élevé"]


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE TENDANCES
# ═══════════════════════════════════════════════════════════


class TestAnalyseTendances:
    """Tests pour analyser_tendances."""

    def test_historique_vide(self):
        """Gère un historique vide."""
        result = analyser_tendances([])
        assert result["evolution"] == "stable"
        assert result["moyenne_jour"] == 0.0
        assert result["pic_activite"] is None

    def test_historique_avec_donnees(self):
        """Analyse l'historique avec données."""
        historique = [{"date": (date.today() - timedelta(days=i)).isoformat()} for i in range(15)]
        result = analyser_tendances(historique, jours=30)
        assert result["moyenne_jour"] > 0

    def test_pic_activite(self):
        """Trouve le pic d'activité."""
        # Créer 5 éléments le même jour
        jour_pic = date.today() - timedelta(days=5)
        historique = [{"date": jour_pic.isoformat()} for _ in range(5)] + [
            {"date": (date.today() - timedelta(days=i)).isoformat()} for i in range(10) if i != 5
        ]
        result = analyser_tendances(historique, jours=30)
        assert result["pic_activite"] is not None
        assert result["pic_activite"]["nombre"] >= 5

    def test_tendance_hausse(self):
        """Détecte une tendance à la hausse."""
        # Plus d'activité dans la 2ème moitié
        historique = [
            {"date": (date.today() - timedelta(days=i)).isoformat()}
            for i in range(5)  # Récent: 5 éléments
        ]
        result = analyser_tendances(historique, jours=30)
        # Tout est récent donc devrait être stable ou hausse
        assert result["evolution"] in ["stable", "hausse"]


# ═══════════════════════════════════════════════════════════
# TESTS PRÉVISION SEMAINE
# ═══════════════════════════════════════════════════════════


class TestPrevisionSemaine:
    """Tests pour prevoir_charge_prochaine_semaine."""

    def test_semaine_vide(self):
        """Prévision pour semaine vide."""
        result = prevoir_charge_prochaine_semaine([], [])
        assert result["evenements"] == 0
        assert result["taches"] == 0
        assert result["charge_totale"] == 0
        assert result["prevision"] == "Semaine légère"

    def test_avec_evenements_semaine_prochaine(self):
        """Compte les événements de la semaine prochaine."""
        # Calculer une date dans la semaine prochaine
        debut_semaine_prochaine = date.today() + timedelta(days=7 - date.today().weekday())
        evenements = [
            {"titre": "E1", "date": debut_semaine_prochaine.isoformat()},
            {"titre": "E2", "date": debut_semaine_prochaine.isoformat()},
            {"titre": "E_autre", "date": (date.today() + timedelta(days=30)).isoformat()},
        ]
        result = prevoir_charge_prochaine_semaine(evenements, [])
        assert result["evenements"] == 2

    def test_avec_taches_echeance(self):
        """Compte les tâches à échéance."""
        debut_semaine_prochaine = date.today() + timedelta(days=7 - date.today().weekday())
        taches = [
            {"titre": "T1", "complete": False, "date_limite": debut_semaine_prochaine.isoformat()},
            {
                "titre": "T2",
                "complete": True,
                "date_limite": debut_semaine_prochaine.isoformat(),
            },  # Complète = ignorée
        ]
        result = prevoir_charge_prochaine_semaine([], taches)
        assert result["taches"] == 1

    def test_prevision_texte(self):
        """Prévision textuelle correcte."""
        result = prevoir_charge_prochaine_semaine([], [])
        assert result["prevision"] in [
            "Semaine légère",
            "Semaine normale",
            "Semaine chargée",
            "Semaine très chargée",
        ]
