"""
Tests pour jardin_logic.py
Couverture cible: 80%+
"""

from datetime import date, timedelta

import pytest

from src.modules.maison.jardin_utils import (
    # Constantes
    CATEGORIES_PLANTES,
    SAISONS,
    STATUS_PLANTES,
    calculer_jours_avant_arrosage,
    calculer_jours_avant_recolte,
    calculer_statistiques_jardin,
    filtrer_par_categorie,
    filtrer_par_status,
    get_plantes_a_arroser,
    get_recoltes_proches,
    # Fonctions
    get_saison_actuelle,
)

# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes jardin."""

    def test_categories_plantes(self):
        """Catégories de plantes définies."""
        assert len(CATEGORIES_PLANTES) > 0
        assert "Légumes" in CATEGORIES_PLANTES
        assert "Fruits" in CATEGORIES_PLANTES
        assert "Herbes" in CATEGORIES_PLANTES

    def test_saisons(self):
        """4 saisons définies."""
        assert len(SAISONS) == 4
        assert "Printemps" in SAISONS
        assert "Hiver" in SAISONS

    def test_status_plantes(self):
        """Status de plantes définis."""
        assert "Semis" in STATUS_PLANTES
        assert "Récolte" in STATUS_PLANTES


# ═══════════════════════════════════════════════════════════
# TESTS SAISONS
# ═══════════════════════════════════════════════════════════


class TestSaisons:
    """Tests pour get_saison_actuelle."""

    def test_saison_retourne_string(self):
        """Retourne une chaîne."""
        saison = get_saison_actuelle()
        assert isinstance(saison, str)
        assert saison in SAISONS

    def test_saison_fevrier_hiver(self):
        """Février = Hiver (test basé sur date actuelle 02/02/2026)."""
        # La date actuelle est février 2026
        saison = get_saison_actuelle()
        assert saison == "Hiver"


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL ARROSAGE
# ═══════════════════════════════════════════════════════════


class TestCalculArrosage:
    """Tests pour calculer_jours_avant_arrosage."""

    def test_pas_de_dernier_arrosage(self):
        """Retourne 0 si pas de dernier arrosage."""
        plante = {"nom": "Tomate"}
        assert calculer_jours_avant_arrosage(plante) == 0

    def test_arrosage_dans_futur(self):
        """Calcule jours restants si arrosage dans le futur."""
        plante = {"dernier_arrosage": date.today() - timedelta(days=3), "frequence_arrosage": 7}
        result = calculer_jours_avant_arrosage(plante)
        assert result == 4  # 7 - 3 = 4 jours

    def test_arrosage_en_retard(self):
        """Retourne négatif si en retard."""
        plante = {"dernier_arrosage": date.today() - timedelta(days=10), "frequence_arrosage": 7}
        result = calculer_jours_avant_arrosage(plante)
        assert result == -3  # 10 - 7 = 3 jours de retard

    def test_arrosage_date_string(self):
        """Gère les dates en string ISO."""
        plante = {
            "dernier_arrosage": (date.today() - timedelta(days=3)).isoformat(),
            "frequence_arrosage": 7,
        }
        result = calculer_jours_avant_arrosage(plante)
        assert result == 4

    def test_frequence_defaut(self):
        """Utilise fréquence par défaut de 7 jours."""
        plante = {"dernier_arrosage": date.today() - timedelta(days=3)}
        result = calculer_jours_avant_arrosage(plante)
        assert result == 4


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL RÉCOLTE
# ═══════════════════════════════════════════════════════════


class TestCalculRecolte:
    """Tests pour calculer_jours_avant_recolte."""

    def test_pas_de_date_recolte(self):
        """Retourne None si pas de date de récolte."""
        plante = {"nom": "Basilic"}
        assert calculer_jours_avant_recolte(plante) is None

    def test_recolte_dans_futur(self):
        """Calcule jours avant récolte."""
        plante = {"date_recolte_estimee": date.today() + timedelta(days=15)}
        result = calculer_jours_avant_recolte(plante)
        assert result == 15

    def test_recolte_passee(self):
        """Retourne négatif si date passée."""
        plante = {"date_recolte_estimee": date.today() - timedelta(days=5)}
        result = calculer_jours_avant_recolte(plante)
        assert result == -5

    def test_recolte_date_string(self):
        """Gère les dates en string ISO."""
        plante = {"date_recolte_estimee": (date.today() + timedelta(days=10)).isoformat()}
        result = calculer_jours_avant_recolte(plante)
        assert result == 10


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES
# ═══════════════════════════════════════════════════════════


class TestAlertesArrosage:
    """Tests pour get_plantes_a_arroser."""

    @pytest.fixture
    def plantes(self):
        return [
            {
                "nom": "Tomate",
                "dernier_arrosage": date.today() - timedelta(days=6),
                "frequence_arrosage": 7,
            },
            {
                "nom": "Basilic",
                "dernier_arrosage": date.today() - timedelta(days=10),
                "frequence_arrosage": 3,
            },
            {"nom": "Salade", "dernier_arrosage": date.today(), "frequence_arrosage": 2},
        ]

    def test_plantes_a_arroser_demain(self, plantes):
        """Trouve plantes à arroser demain (1 jour)."""
        result = get_plantes_a_arroser(plantes, jours_avance=1)
        # Tomate: 7-6=1 jour, Basilic: 3-10=-7 (retard)
        assert len(result) >= 2

    def test_plantes_urgentes(self, plantes):
        """Identifie les plantes urgentes (retard)."""
        result = get_plantes_a_arroser(plantes, jours_avance=1)
        urgentes = [p for p in result if p.get("priorite") == "urgent"]
        assert len(urgentes) >= 1

    def test_triee_par_jours(self, plantes):
        """Liste triée par jours restants."""
        result = get_plantes_a_arroser(plantes, jours_avance=2)
        if len(result) >= 2:
            assert result[0]["jours_restants"] <= result[1]["jours_restants"]

    def test_liste_vide(self):
        """Retourne liste vide si aucune plante."""
        result = get_plantes_a_arroser([])
        assert result == []


class TestAlertesRecolte:
    """Tests pour get_recoltes_proches."""

    @pytest.fixture
    def plantes(self):
        return [
            {"nom": "Tomate", "date_recolte_estimee": date.today() + timedelta(days=3)},
            {"nom": "Carotte", "date_recolte_estimee": date.today() + timedelta(days=10)},
            {"nom": "Concombre", "date_recolte_estimee": date.today() - timedelta(days=2)},
        ]

    def test_recoltes_proches(self, plantes):
        """Trouve récoltes dans les 7 jours."""
        result = get_recoltes_proches(plantes, jours_avance=7)
        assert len(result) == 1  # Tomate seulement (3 jours)

    def test_exclut_passees(self, plantes):
        """Exclut les récoltes passées."""
        result = get_recoltes_proches(plantes, jours_avance=7)
        noms = [p["nom"] for p in result]
        assert "Concombre" not in noms

    def test_triee_par_jours(self, plantes):
        """Liste triée par jours restants."""
        result = get_recoltes_proches(plantes, jours_avance=15)
        if len(result) >= 2:
            assert result[0]["jours_restants"] <= result[1]["jours_restants"]


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestStatistiquesJardin:
    """Tests pour calculer_statistiques_jardin."""

    @pytest.fixture
    def plantes(self):
        return [
            {
                "nom": "Tomate",
                "categorie": "Légumes",
                "status": "Mature",
                "dernier_arrosage": date.today() - timedelta(days=10),
                "frequence_arrosage": 3,
            },
            {"nom": "Basilic", "categorie": "Herbes", "status": "Pousse"},
            {
                "nom": "Carotte",
                "categorie": "Légumes",
                "status": "Semis",
                "date_recolte_estimee": date.today() + timedelta(days=3),
            },
        ]

    def test_total_plantes(self, plantes):
        """Compte le total de plantes."""
        result = calculer_statistiques_jardin(plantes)
        assert result["total_plantes"] == 3

    def test_par_categorie(self, plantes):
        """Compte par catégorie."""
        result = calculer_statistiques_jardin(plantes)
        assert result["par_categorie"]["Légumes"] == 2
        assert result["par_categorie"]["Herbes"] == 1

    def test_par_status(self, plantes):
        """Compte par status."""
        result = calculer_statistiques_jardin(plantes)
        assert "Mature" in result["par_status"]
        assert "Pousse" in result["par_status"]

    def test_alertes_arrosage(self, plantes):
        """Compte les alertes d'arrosage."""
        result = calculer_statistiques_jardin(plantes)
        assert result["alertes_arrosage"] >= 1

    def test_alertes_recolte(self, plantes):
        """Compte les alertes de récolte."""
        result = calculer_statistiques_jardin(plantes)
        assert result["alertes_recolte"] >= 1

    def test_liste_vide(self):
        """Gère une liste vide."""
        result = calculer_statistiques_jardin([])
        assert result["total_plantes"] == 0


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════


class TestFiltrageJardin:
    """Tests pour les fonctions de filtrage."""

    @pytest.fixture
    def plantes(self):
        return [
            {"nom": "Tomate", "categorie": "Légumes", "status": "Mature"},
            {"nom": "Basilic", "categorie": "Herbes", "status": "Pousse"},
            {"nom": "Carotte", "categorie": "Légumes", "status": "Semis"},
        ]

    def test_filtrer_par_categorie(self, plantes):
        """Filtre par catégorie."""
        result = filtrer_par_categorie(plantes, "Légumes")
        assert len(result) == 2

    def test_filtrer_par_status(self, plantes):
        """Filtre par status."""
        result = filtrer_par_status(plantes, "Mature")
        assert len(result) == 1
        assert result[0]["nom"] == "Tomate"
