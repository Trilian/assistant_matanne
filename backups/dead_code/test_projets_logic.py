"""
Tests pour projets_logic.py
Couverture cible: 80%+
"""

from datetime import date, timedelta

import pytest

from src.modules.maison.projets_utils import (
    CATEGORIES_PROJET,
    PRIORITES,
    # Constantes
    STATUTS_PROJET,
    calculer_budget_total,
    calculer_jours_restants,
    calculer_statistiques_projets,
    # Fonctions
    calculer_urgence_projet,
    filtrer_par_categorie,
    filtrer_par_priorite,
    filtrer_par_statut,
    get_projets_a_faire,
    get_projets_en_cours,
    get_projets_urgents,
)

# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes projets."""

    def test_statuts_projet(self):
        """Statuts de projet définis."""
        assert len(STATUTS_PROJET) >= 4
        assert "À faire" in STATUTS_PROJET
        assert "En cours" in STATUTS_PROJET
        assert "Terminé" in STATUTS_PROJET

    def test_priorites(self):
        """Priorités définies."""
        assert len(PRIORITES) >= 4
        assert "Basse" in PRIORITES
        assert "Urgente" in PRIORITES

    def test_categories_projet(self):
        """Catégories de projet définies."""
        assert len(CATEGORIES_PROJET) >= 4
        assert "Rénovation" in CATEGORIES_PROJET
        assert "Réparation" in CATEGORIES_PROJET


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL URGENCE
# ═══════════════════════════════════════════════════════════


class TestCalculUrgence:
    """Tests pour calculer_urgence_projet."""

    def test_urgence_sans_date_limite(self):
        """Retourne la priorité si pas de date limite."""
        projet = {"priorite": "Moyenne"}
        assert calculer_urgence_projet(projet) == "Moyenne"

    def test_urgence_moins_7_jours(self):
        """Urgent si moins de 7 jours."""
        projet = {"priorite": "Basse", "date_limite": date.today() + timedelta(days=5)}
        assert calculer_urgence_projet(projet) == "Urgente"

    def test_urgence_priorite_urgente(self):
        """Urgent si priorité déjà urgente."""
        projet = {"priorite": "Urgente", "date_limite": date.today() + timedelta(days=30)}
        assert calculer_urgence_projet(projet) == "Urgente"

    def test_haute_si_moins_14_jours(self):
        """Haute si 7-14 jours et priorité moyenne+."""
        projet = {"priorite": "Moyenne", "date_limite": date.today() + timedelta(days=10)}
        assert calculer_urgence_projet(projet) == "Haute"

    def test_garde_priorite_si_loin(self):
        """Garde la priorité si date loin."""
        projet = {"priorite": "Basse", "date_limite": date.today() + timedelta(days=30)}
        assert calculer_urgence_projet(projet) == "Basse"

    def test_date_string(self):
        """Gère les dates en string ISO."""
        projet = {
            "priorite": "Moyenne",
            "date_limite": (date.today() + timedelta(days=3)).isoformat(),
        }
        assert calculer_urgence_projet(projet) == "Urgente"


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL JOURS RESTANTS
# ═══════════════════════════════════════════════════════════


class TestCalculJoursRestants:
    """Tests pour calculer_jours_restants."""

    def test_sans_date_limite(self):
        """Retourne None si pas de date limite."""
        projet = {"titre": "Projet"}
        assert calculer_jours_restants(projet) is None

    def test_jours_positifs(self):
        """Calcule jours restants dans le futur."""
        projet = {"date_limite": date.today() + timedelta(days=10)}
        assert calculer_jours_restants(projet) == 10

    def test_jours_negatifs(self):
        """Retourne négatif si dépassé."""
        projet = {"date_limite": date.today() - timedelta(days=5)}
        assert calculer_jours_restants(projet) == -5

    def test_date_string(self):
        """Gère les dates en string ISO."""
        projet = {"date_limite": (date.today() + timedelta(days=7)).isoformat()}
        assert calculer_jours_restants(projet) == 7


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════


class TestFiltrageProjets:
    """Tests pour les fonctions de filtrage."""

    @pytest.fixture
    def projets(self):
        return [
            {
                "titre": "Cuisine",
                "statut": "En cours",
                "priorite": "Haute",
                "categorie": "Rénovation",
            },
            {
                "titre": "Peinture",
                "statut": "À faire",
                "priorite": "Moyenne",
                "categorie": "Décoration",
            },
            {
                "titre": "Jardin",
                "statut": "Terminé",
                "priorite": "Basse",
                "categorie": "Amélioration",
            },
        ]

    def test_filtrer_par_statut(self, projets):
        """Filtre par statut."""
        result = filtrer_par_statut(projets, "En cours")
        assert len(result) == 1
        assert result[0]["titre"] == "Cuisine"

    def test_filtrer_par_priorite(self, projets):
        """Filtre par priorité."""
        result = filtrer_par_priorite(projets, "Haute")
        assert len(result) == 1

    def test_filtrer_par_categorie(self, projets):
        """Filtre par catégorie."""
        result = filtrer_par_categorie(projets, "Rénovation")
        assert len(result) == 1


class TestGetProjetsSpecifiques:
    """Tests pour get_projets_urgents, en_cours, a_faire."""

    @pytest.fixture
    def projets(self):
        return [
            {"titre": "Urgent1", "priorite": "Urgente", "statut": "En cours"},
            {
                "titre": "Urgent2",
                "priorite": "Moyenne",
                "statut": "À faire",
                "date_limite": date.today() + timedelta(days=3),
            },
            {
                "titre": "Normal",
                "priorite": "Basse",
                "statut": "À faire",
                "date_limite": date.today() + timedelta(days=30),
            },
            {"titre": "EnCours", "priorite": "Moyenne", "statut": "En cours"},
        ]

    def test_get_projets_urgents(self, projets):
        """Retourne les projets urgents."""
        result = get_projets_urgents(projets)
        assert len(result) >= 2

    def test_urgents_tries(self, projets):
        """Projets urgents triés par jours restants."""
        result = get_projets_urgents(projets)
        if len(result) >= 2:
            j1 = result[0].get("jours_restants")
            j2 = result[1].get("jours_restants")
            if j1 is not None and j2 is not None:
                assert j1 <= j2

    def test_get_projets_en_cours(self, projets):
        """Retourne les projets en cours."""
        result = get_projets_en_cours(projets)
        assert len(result) == 2

    def test_get_projets_a_faire(self, projets):
        """Retourne les projets à faire."""
        result = get_projets_a_faire(projets)
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestStatistiquesProjets:
    """Tests pour calculer_statistiques_projets."""

    @pytest.fixture
    def projets(self):
        return [
            {"titre": "P1", "statut": "Terminé", "priorite": "Haute"},
            {"titre": "P2", "statut": "En cours", "priorite": "Moyenne"},
            {
                "titre": "P3",
                "statut": "À faire",
                "priorite": "Urgente",
                "date_limite": date.today() + timedelta(days=3),
            },
            {"titre": "P4", "statut": "Terminé", "priorite": "Basse"},
        ]

    def test_total(self, projets):
        """Compte le total de projets."""
        result = calculer_statistiques_projets(projets)
        assert result["total"] == 4

    def test_par_statut(self, projets):
        """Compte par statut."""
        result = calculer_statistiques_projets(projets)
        assert result["par_statut"]["Terminé"] == 2
        assert result["par_statut"]["En cours"] == 1

    def test_par_priorite(self, projets):
        """Compte par priorité."""
        result = calculer_statistiques_projets(projets)
        assert "Haute" in result["par_priorite"]

    def test_urgents(self, projets):
        """Compte les urgents."""
        result = calculer_statistiques_projets(projets)
        assert result["urgents"] >= 1

    def test_taux_completion(self, projets):
        """Calcule le taux de complétion."""
        result = calculer_statistiques_projets(projets)
        assert result["taux_completion"] == 50.0  # 2/4 = 50%

    def test_liste_vide(self):
        """Gère une liste vide."""
        result = calculer_statistiques_projets([])
        assert result["total"] == 0
        assert result["taux_completion"] == 0.0


# ═══════════════════════════════════════════════════════════
# TESTS BUDGET
# ═══════════════════════════════════════════════════════════


class TestCalculBudget:
    """Tests pour calculer_budget_total."""

    @pytest.fixture
    def projets(self):
        return [
            {"titre": "P1", "budget": 1000.0, "cout_reel": 800.0},
            {"titre": "P2", "budget": 500.0, "cout_reel": 600.0},
            {"titre": "P3", "budget": 200.0},
        ]

    def test_budget_total(self, projets):
        """Calcule le budget total."""
        result = calculer_budget_total(projets)
        assert result["budget_total"] == 1700.0

    def test_budget_depense(self, projets):
        """Calcule le budget dépensé."""
        result = calculer_budget_total(projets)
        assert result["budget_depense"] == 1400.0

    def test_budget_restant(self, projets):
        """Calcule le budget restant."""
        result = calculer_budget_total(projets)
        assert result["budget_restant"] == 300.0

    def test_liste_vide(self):
        """Gère une liste vide."""
        result = calculer_budget_total([])
        assert result["budget_total"] == 0.0
        assert result["budget_depense"] == 0.0
