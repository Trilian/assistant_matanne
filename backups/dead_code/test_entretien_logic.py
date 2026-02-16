"""
Tests pour entretien_logic.py - Module Maison
Couverture cible: 80%+
"""

from datetime import date, timedelta

import pytest

from src.modules.maison.entretien_utils import (
    CATEGORIES_TACHE,
    # Constantes
    FREQUENCES,
    PIECES,
    calculer_jours_avant_tache,
    # Calcul des dates
    calculer_prochaine_occurrence,
    # Statistiques
    calculer_statistiques_entretien,
    calculer_taux_completion,
    # Filtrage
    filtrer_par_categorie,
    filtrer_par_frequence,
    filtrer_par_piece,
    # Alertes et priorités
    get_taches_aujourd_hui,
    get_taches_en_retard,
    get_taches_semaine,
    grouper_par_piece,
    # Validation
    valider_tache,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def taches_sample():
    """Liste de tâches d'entretien de test."""
    today = date.today()
    return [
        {
            "id": 1,
            "titre": "Nettoyage cuisine",
            "categorie": "Ménage",
            "piece": "Cuisine",
            "frequence": "Quotidienne",
            "derniere_execution": today - timedelta(days=1),
        },
        {
            "id": 2,
            "titre": "Aspirateur salon",
            "categorie": "Ménage",
            "piece": "Salon",
            "frequence": "Hebdomadaire",
            "derniere_execution": today - timedelta(days=5),
        },
        {
            "id": 3,
            "titre": "Vérifier chaudière",
            "categorie": "Contrôle",
            "piece": "Garage",
            "frequence": "Annuelle",
            "derniere_execution": today - timedelta(days=200),
        },
        {
            "id": 4,
            "titre": "Nettoyer filtres hotte",
            "categorie": "Maintenance",
            "piece": "Cuisine",
            "frequence": "Mensuelle",
            "derniere_execution": today - timedelta(days=45),
        },
        {
            "id": 5,
            "titre": "Laver vitres",
            "categorie": "Ménage",
            "piece": "Salon",
            "frequence": "Trimestrielle",
            "derniere_execution": today - timedelta(days=100),
        },
    ]


@pytest.fixture
def taches_vides():
    """Liste vide."""
    return []


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantesEntretien:
    """Tests des constantes."""

    def test_frequences_definies(self):
        """Fréquences disponibles."""
        assert "Quotidienne" in FREQUENCES
        assert "Hebdomadaire" in FREQUENCES
        assert "Mensuelle" in FREQUENCES
        assert "Annuelle" in FREQUENCES

    def test_categories_definies(self):
        """Catégories de tâches."""
        assert "Ménage" in CATEGORIES_TACHE
        assert "Maintenance" in CATEGORIES_TACHE
        assert "Contrôle" in CATEGORIES_TACHE

    def test_pieces_definies(self):
        """Pièces de la maison."""
        assert "Cuisine" in PIECES
        assert "Salon" in PIECES
        assert "Chambre" in PIECES
        assert "Salle de bain" in PIECES


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL DES DATES
# ═══════════════════════════════════════════════════════════


class TestCalculDates:
    """Tests des fonctions de calcul de dates."""

    def test_prochaine_quotidienne(self):
        """Prochaine occurrence quotidienne = +1 jour."""
        derniere = date(2024, 1, 1)
        prochaine = calculer_prochaine_occurrence(derniere, "Quotidienne")
        assert prochaine == date(2024, 1, 2)

    def test_prochaine_hebdomadaire(self):
        """Prochaine occurrence hebdomadaire = +7 jours."""
        derniere = date(2024, 1, 1)
        prochaine = calculer_prochaine_occurrence(derniere, "Hebdomadaire")
        assert prochaine == date(2024, 1, 8)

    def test_prochaine_mensuelle(self):
        """Prochaine occurrence mensuelle = +30 jours."""
        derniere = date(2024, 1, 1)
        prochaine = calculer_prochaine_occurrence(derniere, "Mensuelle")
        assert prochaine == date(2024, 1, 31)

    def test_prochaine_trimestrielle(self):
        """Prochaine occurrence trimestrielle = +90 jours."""
        derniere = date(2024, 1, 1)
        prochaine = calculer_prochaine_occurrence(derniere, "Trimestrielle")
        assert prochaine == date(2024, 3, 31)

    def test_prochaine_annuelle(self):
        """Prochaine occurrence annuelle = +365 jours."""
        derniere = date(2024, 1, 1)
        prochaine = calculer_prochaine_occurrence(derniere, "Annuelle")
        # 2024 est bissextile, donc 2024-01-01 + 365 jours = 2024-12-31
        assert prochaine == date(2024, 12, 31)

    def test_prochaine_frequence_inconnue(self):
        """Fréquence inconnue = +7 jours par défaut."""
        derniere = date(2024, 1, 1)
        prochaine = calculer_prochaine_occurrence(derniere, "Inconnue")
        assert prochaine == date(2024, 1, 8)

    def test_jours_avant_tache_future(self):
        """Tâche future = jours positifs."""
        today = date.today()
        tache = {"frequence": "Hebdomadaire", "derniere_execution": today - timedelta(days=3)}
        jours = calculer_jours_avant_tache(tache)
        # Prochaine dans 4 jours (7 - 3)
        assert jours == 4

    def test_jours_avant_tache_retard(self):
        """Tâche en retard = jours négatifs."""
        today = date.today()
        tache = {"frequence": "Hebdomadaire", "derniere_execution": today - timedelta(days=10)}
        jours = calculer_jours_avant_tache(tache)
        # En retard de 3 jours
        assert jours == -3

    def test_jours_avant_tache_sans_execution(self):
        """Tâche jamais exécutée = 0 (à faire immédiatement)."""
        tache = {"frequence": "Hebdomadaire"}
        jours = calculer_jours_avant_tache(tache)
        assert jours == 0

    def test_jours_avant_tache_string_date(self):
        """Date en format string ISO."""
        today = date.today()
        tache = {
            "frequence": "Quotidienne",
            "derniere_execution": (today - timedelta(days=2)).isoformat(),
        }
        jours = calculer_jours_avant_tache(tache)
        # En retard de 1 jour
        assert jours == -1


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES ET PRIORITÉS
# ═══════════════════════════════════════════════════════════


class TestAlertesPriorites:
    """Tests des fonctions d'alertes."""

    def test_get_taches_aujourd_hui(self, taches_sample):
        """Tâches à faire aujourd'hui (jours <= 0)."""
        result = get_taches_aujourd_hui(taches_sample)
        # Au moins une tâche devrait être à faire
        assert isinstance(result, list)
        # Toutes ont un retard
        for t in result:
            assert "jours_retard" in t

    def test_get_taches_semaine(self, taches_sample):
        """Tâches de la semaine (0 <= jours <= 7)."""
        result = get_taches_semaine(taches_sample)
        assert isinstance(result, list)
        # Toutes ont des jours restants
        for t in result:
            assert "jours_restants" in t

    def test_get_taches_en_retard(self, taches_sample):
        """Tâches en retard (jours < 0)."""
        result = get_taches_en_retard(taches_sample)
        # Tri par retard décroissant
        if len(result) > 1:
            assert result[0]["jours_retard"] >= result[1]["jours_retard"]

    def test_get_taches_aujourd_hui_vide(self, taches_vides):
        """Liste vide retourne liste vide."""
        result = get_taches_aujourd_hui(taches_vides)
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════


class TestFiltrageEntretien:
    """Tests des fonctions de filtrage."""

    def test_filtrer_par_categorie(self, taches_sample):
        """Filtre par catégorie."""
        result = filtrer_par_categorie(taches_sample, "Ménage")
        assert len(result) == 3
        assert all(t["categorie"] == "Ménage" for t in result)

    def test_filtrer_par_categorie_inexistante(self, taches_sample):
        """Catégorie inexistante = liste vide."""
        result = filtrer_par_categorie(taches_sample, "Inexistante")
        assert len(result) == 0

    def test_filtrer_par_piece(self, taches_sample):
        """Filtre par pièce."""
        result = filtrer_par_piece(taches_sample, "Cuisine")
        assert len(result) == 2
        assert all(t["piece"] == "Cuisine" for t in result)

    def test_filtrer_par_frequence(self, taches_sample):
        """Filtre par fréquence."""
        result = filtrer_par_frequence(taches_sample, "Hebdomadaire")
        assert len(result) == 1
        assert result[0]["titre"] == "Aspirateur salon"


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestStatistiquesEntretien:
    """Tests des fonctions de statistiques."""

    def test_calculer_statistiques_entretien(self, taches_sample):
        """Statistiques complètes."""
        result = calculer_statistiques_entretien(taches_sample)

        assert result["total_taches"] == 5
        assert "par_categorie" in result
        assert "par_frequence" in result
        assert result["par_categorie"]["Ménage"] == 3

    def test_calculer_statistiques_alertes(self, taches_sample):
        """Statistiques d'alertes."""
        result = calculer_statistiques_entretien(taches_sample)

        assert "aujourd_hui" in result
        assert "en_retard" in result
        assert "cette_semaine" in result

    def test_calculer_taux_completion(self, taches_sample):
        """Taux de complétion."""
        result = calculer_taux_completion(taches_sample, periode_jours=30)
        # Doit être un pourcentage
        assert 0 <= result <= 100

    def test_calculer_taux_completion_vide(self, taches_vides):
        """Taux de complétion liste vide = 0."""
        result = calculer_taux_completion(taches_vides)
        assert result == 0.0


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValidationEntretien:
    """Tests de validation."""

    def test_valider_tache_valide(self):
        """Tâche valide."""
        data = {"titre": "Nettoyage", "frequence": "Hebdomadaire", "categorie": "Ménage"}
        valide, erreurs = valider_tache(data)
        assert valide is True
        assert len(erreurs) == 0

    def test_valider_tache_titre_manquant(self):
        """Titre manquant."""
        data = {"frequence": "Hebdomadaire"}
        valide, erreurs = valider_tache(data)
        assert valide is False
        assert any("titre" in e.lower() for e in erreurs)

    def test_valider_tache_frequence_invalide(self):
        """Fréquence invalide."""
        data = {"titre": "Test", "frequence": "Invalide"}
        valide, erreurs = valider_tache(data)
        assert valide is False
        assert any("fréquence" in e.lower() for e in erreurs)

    def test_valider_tache_categorie_invalide(self):
        """Catégorie invalide."""
        data = {"titre": "Test", "categorie": "Invalide"}
        valide, erreurs = valider_tache(data)
        assert valide is False
        assert any("catégorie" in e.lower() for e in erreurs)


# ═══════════════════════════════════════════════════════════
# TESTS GROUPEMENT
# ═══════════════════════════════════════════════════════════


class TestGroupementEntretien:
    """Tests de groupement."""

    def test_grouper_par_piece(self, taches_sample):
        """Groupement par pièce."""
        result = grouper_par_piece(taches_sample)

        assert "Cuisine" in result
        assert "Salon" in result
        assert "Garage" in result
        assert len(result["Cuisine"]) == 2
        assert len(result["Salon"]) == 2

    def test_grouper_par_piece_autre(self):
        """Pièce manquante = 'Autre'."""
        taches = [{"titre": "Test"}]
        result = grouper_par_piece(taches)
        assert "Autre" in result
        assert len(result["Autre"]) == 1
