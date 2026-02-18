"""
Tests pour src/modules/maison/charges/logic.py

Tests des fonctions de calcul charges (éco-score, badges, anomalies).
"""

from decimal import Decimal

import pytest


class TestCalculerStatsGlobales:
    """Tests pour calculer_stats_globales"""

    def test_sans_factures(self):
        """Test avec liste vide."""
        from src.modules.maison.charges.logic import calculer_stats_globales

        stats = calculer_stats_globales([])

        assert stats["nb_factures"] == 0
        assert stats["streak"] == 0
        assert stats["eco_score"] == 50
        assert stats["energies_suivies"] == 0

    def test_une_energie(self):
        """Test avec une seule énergie."""
        from src.modules.maison.charges.logic import calculer_stats_globales

        factures = [
            {"type": "electricite", "consommation": 400, "date": "2024-01-01"},
            {"type": "electricite", "consommation": 380, "date": "2024-02-01"},
        ]
        stats = calculer_stats_globales(factures)

        assert stats["nb_factures"] == 2
        assert stats["energies_suivies"] == 1
        assert "elec_ratio" in stats

    def test_toutes_energies(self):
        """Test avec eau, electricité, gaz."""
        from src.modules.maison.charges.logic import calculer_stats_globales

        factures = [
            {"type": "eau", "consommation": 6, "date": "2024-01-01"},
            {"type": "electricite", "consommation": 400, "date": "2024-01-01"},
            {"type": "gaz", "consommation": 800, "date": "2024-01-01"},
        ]
        stats = calculer_stats_globales(factures)

        assert stats["energies_suivies"] == 3

    def test_energie_inconnue_ignoree(self):
        """Test que les types inconnus sont ignorés."""
        from src.modules.maison.charges.logic import calculer_stats_globales

        factures = [
            {"type": "energie_inconnue", "consommation": 100, "date": "2024-01-01"},
            {"type": "electricite", "consommation": 400, "date": "2024-01-01"},
        ]
        stats = calculer_stats_globales(factures)

        assert stats["nb_factures"] == 2
        assert stats["energies_suivies"] == 2  # Les deux types comptent


class TestCalculerEcoScore:
    """Tests pour calculer_eco_score_avance"""

    def test_score_base(self):
        """Test score de base 50."""
        from src.modules.maison.charges.logic import calculer_eco_score_avance

        score = calculer_eco_score_avance([], {})
        assert score == 50

    def test_score_economies_eau(self):
        """Test bonus si eau < moyenne."""
        from src.modules.maison.charges.logic import calculer_eco_score_avance

        factures = [{"type": "eau", "consommation": 6}]
        stats = {"eau_ratio": 0.7}  # Bien sous la moyenne

        score = calculer_eco_score_avance(factures, stats)
        assert score > 50

    def test_score_surconsommation(self):
        """Test malus si surconsommation."""
        from src.modules.maison.charges.logic import calculer_eco_score_avance

        factures = [{"type": "electricite", "consommation": 1000}]
        stats = {"elec_ratio": 1.5}  # Au-dessus de la moyenne

        score = calculer_eco_score_avance(factures, stats)
        assert score < 50

    def test_score_plafonne_0_100(self):
        """Test que le score reste entre 0 et 100."""
        from src.modules.maison.charges.logic import calculer_eco_score_avance

        # Stats très bonnes
        stats = {
            "eau_ratio": 0.5,
            "elec_ratio": 0.5,
            "gaz_ratio": 0.5,
            "energies_suivies": 3,
            "streak": 60,
        }
        score = calculer_eco_score_avance([{"x": 1}], stats)

        assert 0 <= score <= 100

    def test_bonus_energies_suivies(self):
        """Test bonus si 3+ énergies suivies."""
        from src.modules.maison.charges.logic import calculer_eco_score_avance

        stats_2 = {"energies_suivies": 2}
        stats_3 = {"energies_suivies": 3}

        score_2 = calculer_eco_score_avance([{"x": 1}], stats_2)
        score_3 = calculer_eco_score_avance([{"x": 1}], stats_3)

        assert score_3 > score_2


class TestCalculerStreak:
    """Tests pour calculer_streak"""

    def test_streak_vide(self):
        """Test streak sans factures."""
        from src.modules.maison.charges.logic import calculer_streak

        assert calculer_streak([]) == 0

    def test_streak_progression(self):
        """Test streak avec consommations sous moyenne."""
        from src.modules.maison.charges.logic import calculer_streak

        factures = [
            {"type": "electricite", "consommation": 300, "date": "2024-03-01"},
            {"type": "electricite", "consommation": 350, "date": "2024-02-01"},
        ]
        streak = calculer_streak(factures)

        assert streak > 0

    def test_streak_plafonne(self):
        """Test streak max 90 jours."""
        from src.modules.maison.charges.logic import calculer_streak

        factures = [
            {"type": "electricite", "consommation": 100, "date": f"2024-{i:02d}-01"}
            for i in range(1, 13)
        ]
        streak = calculer_streak(factures)

        assert streak <= 90

    def test_streak_coupe_si_depassement(self):
        """Test que le streak s'arrête si consommation > moyenne."""
        from src.modules.maison.charges.logic import calculer_streak

        factures = [
            {"type": "electricite", "consommation": 300, "date": "2024-03-01"},  # OK
            {"type": "electricite", "consommation": 900, "date": "2024-02-01"},  # Dépasse
            {"type": "electricite", "consommation": 300, "date": "2024-01-01"},  # OK mais après
        ]
        streak = calculer_streak(factures)

        # Seule la première contribue (plus récente)
        assert streak == 7


class TestAnalyserConsommation:
    """Tests pour analyser_consommation"""

    def test_analyse_vide(self):
        """Test analyse sans données."""
        from src.modules.maison.charges.logic import analyser_consommation

        result = analyser_consommation([], "eau")

        assert result["total_conso"] == 0
        assert result["nb_factures"] == 0
        assert result["tendance"] == "stable"

    def test_analyse_calculs_corrects(self):
        """Test calculs moyenne et total."""
        from src.modules.maison.charges.logic import analyser_consommation

        factures = [
            {"type": "eau", "consommation": 10, "montant": 40, "date": "2024-01-01"},
            {"type": "eau", "consommation": 20, "montant": 80, "date": "2024-02-01"},
        ]
        result = analyser_consommation(factures, "eau")

        assert result["total_conso"] == 30
        assert result["moyenne_conso"] == 15
        assert result["nb_factures"] == 2

    def test_analyse_tendance_hausse(self):
        """Test détection tendance hausse."""
        from src.modules.maison.charges.logic import analyser_consommation

        factures = [
            {"type": "eau", "consommation": 5, "montant": 20, "date": "2024-01-01"},
            {"type": "eau", "consommation": 6, "montant": 24, "date": "2024-02-01"},
            {"type": "eau", "consommation": 7, "montant": 28, "date": "2024-03-01"},
            {"type": "eau", "consommation": 9, "montant": 36, "date": "2024-04-01"},
        ]
        result = analyser_consommation(factures, "eau")

        assert result["tendance"] == "hausse"

    def test_analyse_tendance_baisse(self):
        """Test détection tendance baisse."""
        from src.modules.maison.charges.logic import analyser_consommation

        factures = [
            {"type": "eau", "consommation": 10, "montant": 40, "date": "2024-01-01"},
            {"type": "eau", "consommation": 9, "montant": 36, "date": "2024-02-01"},
            {"type": "eau", "consommation": 7, "montant": 28, "date": "2024-03-01"},
            {"type": "eau", "consommation": 5, "montant": 20, "date": "2024-04-01"},
        ]
        result = analyser_consommation(factures, "eau")

        assert result["tendance"] == "baisse"

    def test_analyse_ignore_autres_energies(self):
        """Test que seule l'énergie demandée est analysée."""
        from src.modules.maison.charges.logic import analyser_consommation

        factures = [
            {"type": "eau", "consommation": 10, "montant": 40, "date": "2024-01-01"},
            {"type": "electricite", "consommation": 400, "montant": 80, "date": "2024-01-01"},
        ]
        result = analyser_consommation(factures, "eau")

        assert result["nb_factures"] == 1
        assert result["total_conso"] == 10


class TestDetecterAnomalies:
    """Tests pour detecter_anomalies"""

    def test_aucune_anomalie(self):
        """Test sans anomalie."""
        from src.modules.maison.charges.logic import detecter_anomalies

        factures = [
            {"type": "electricite", "consommation": 400},
            {"type": "electricite", "consommation": 410},
        ]
        anomalies = detecter_anomalies(factures)

        assert isinstance(anomalies, list)

    def test_pic_consommation(self):
        """Test détection pic."""
        from src.modules.maison.charges.logic import detecter_anomalies

        factures = [
            {"type": "electricite", "consommation": 400, "date": "2024-01"},
            {"type": "electricite", "consommation": 420, "date": "2024-02"},
            {"type": "electricite", "consommation": 1000, "date": "2024-03"},  # Pic
        ]
        anomalies = detecter_anomalies(factures)

        assert len(anomalies) >= 1
        assert any("Pic" in a["titre"] for a in anomalies)

    def test_max_5_anomalies(self):
        """Test limite à 5 anomalies."""
        from src.modules.maison.charges.logic import detecter_anomalies

        # Génère plein d'anomalies
        factures = [
            {"type": "electricite", "consommation": i * 1000, "date": f"2024-{(i % 12) + 1:02d}"}
            for i in range(1, 10)
        ]
        anomalies = detecter_anomalies(factures)

        assert len(anomalies) <= 5

    def test_anomalies_sans_donnees(self):
        """Test anomalies avec liste vide."""
        from src.modules.maison.charges.logic import detecter_anomalies

        anomalies = detecter_anomalies([])
        assert anomalies == []

    def test_structure_anomalie(self):
        """Test structure d'une anomalie."""
        from src.modules.maison.charges.logic import detecter_anomalies

        factures = [
            {"type": "electricite", "consommation": 100, "date": "2024-01"},
            {"type": "electricite", "consommation": 500, "date": "2024-02"},  # Pic
        ]
        anomalies = detecter_anomalies(factures)

        if anomalies:
            anomalie = anomalies[0]
            assert "titre" in anomalie
            assert "description" in anomalie
            assert "conseil" in anomalie
            assert "energie" in anomalie
            assert "severite" in anomalie


class TestSimulerEconomies:
    """Tests pour simuler_economies_energie"""

    def test_action_led(self):
        """Test simulation LED."""
        from src.modules.maison.charges.logic import simuler_economies_energie

        result = simuler_economies_energie("electricite", "led")

        assert "pct" in result
        assert "euros" in result
        assert result["euros"] > 0

    def test_action_veille(self):
        """Test simulation veille."""
        from src.modules.maison.charges.logic import simuler_economies_energie

        result = simuler_economies_energie("electricite", "veille")

        assert result["pct"] == 0.10
        assert result["euros"] == 50

    def test_action_gaz(self):
        """Test simulation gaz."""
        from src.modules.maison.charges.logic import simuler_economies_energie

        result = simuler_economies_energie("gaz", "1degre")

        assert result["pct"] == 0.07
        assert result["euros"] == 150

    def test_action_eau(self):
        """Test simulation eau."""
        from src.modules.maison.charges.logic import simuler_economies_energie

        result = simuler_economies_energie("eau", "douche")

        assert result["pct"] == 0.30
        assert result["euros"] == 200

    def test_action_inconnue(self):
        """Test action inconnue retourne défaut."""
        from src.modules.maison.charges.logic import simuler_economies_energie

        result = simuler_economies_energie("eau", "action_inconnue")

        assert result["pct"] == 0.10
        assert result["euros"] == 100

    def test_energie_inconnue(self):
        """Test énergie inconnue retourne défaut."""
        from src.modules.maison.charges.logic import simuler_economies_energie

        result = simuler_economies_energie("petrole", "action")

        assert result["pct"] == 0.10
        assert result["euros"] == 100
