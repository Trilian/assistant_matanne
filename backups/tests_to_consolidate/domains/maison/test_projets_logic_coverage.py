"""
Tests de couverture complémentaires pour projets_logic.py
Objectif: atteindre 80%+ de couverture
Couvre les lignes non testées: 216-232, 245-258
"""
import pytest


# ═══════════════════════════════════════════════════════════
# TESTS VALIDER_PROJET - lignes 216-232
# ═══════════════════════════════════════════════════════════

class TestValiderProjet:
    """Tests pour valider_projet."""

    def test_projet_valide(self):
        """Projet avec titre valide."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"titre": "Rénovation cuisine", "statut": "En cours", "priorite": "Haute"}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is True
        assert len(erreurs) == 0

    def test_projet_sans_titre(self):
        """Projet sans titre invalide."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"statut": "En cours"}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is False
        assert any("titre" in e.lower() for e in erreurs)

    def test_projet_titre_vide(self):
        """Projet avec titre vide invalide."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"titre": "", "statut": "En cours"}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is False
        assert any("titre" in e.lower() for e in erreurs)

    def test_projet_statut_invalide(self):
        """Statut non autorisé."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"titre": "Test", "statut": "StatutInconnu"}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is False
        assert any("statut" in e.lower() for e in erreurs)

    def test_projet_priorite_invalide(self):
        """Priorité non autorisée."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"titre": "Test", "priorite": "Urgentissime"}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is False
        assert any("priorité" in e.lower() for e in erreurs)

    def test_projet_budget_negatif(self):
        """Budget négatif invalide."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"titre": "Test", "budget": -100}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is False
        assert any("budget" in e.lower() for e in erreurs)

    def test_projet_budget_non_numerique(self):
        """Budget non numérique invalide."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"titre": "Test", "budget": "mille"}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is False
        assert any("budget" in e.lower() for e in erreurs)

    def test_projet_budget_zero_valide(self):
        """Budget à zéro valide."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"titre": "Test", "budget": 0}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is True

    def test_projet_budget_float_valide(self):
        """Budget en float valide."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"titre": "Test", "budget": 1500.50}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is True

    def test_projet_multiple_erreurs(self):
        """Plusieurs erreurs à la fois."""
        from src.domains.maison.logic.projets_logic import valider_projet
        
        data = {"statut": "Inconnu", "priorite": "SuperHaute", "budget": -50}
        
        valide, erreurs = valider_projet(data)
        
        assert valide is False
        assert len(erreurs) >= 3


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER_PROGRESSION - lignes 245-258
# ═══════════════════════════════════════════════════════════

class TestCalculerProgression:
    """Tests pour calculer_progression."""

    def test_progression_projet_termine(self):
        """Projet terminé = 100%."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {"titre": "Test", "statut": "Terminé"}
        
        result = calculer_progression(projet)
        
        assert result == 100.0

    def test_progression_projet_a_faire(self):
        """Projet à faire = 0%."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {"titre": "Test", "statut": "À faire"}
        
        result = calculer_progression(projet)
        
        assert result == 0.0

    def test_progression_projet_en_cours_sans_taches(self):
        """Projet en cours sans tâches = 50% par défaut."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {"titre": "Test", "statut": "En cours"}
        
        result = calculer_progression(projet)
        
        assert result == 50.0

    def test_progression_projet_en_cours_avec_taches_vides(self):
        """Projet en cours avec liste tâches vide = 50%."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {"titre": "Test", "statut": "En cours", "taches": []}
        
        result = calculer_progression(projet)
        
        assert result == 50.0

    def test_progression_projet_en_cours_taches_partielles(self):
        """Projet en cours avec tâches partiellement complétées."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {
            "titre": "Test",
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": True},
                {"nom": "T2", "completee": False},
                {"nom": "T3", "completee": True},
                {"nom": "T4", "completee": False},
            ]
        }
        
        result = calculer_progression(projet)
        
        assert result == 50.0  # 2/4 = 50%

    def test_progression_projet_en_cours_toutes_taches_completees(self):
        """Projet en cours avec toutes tâches complétées."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {
            "titre": "Test",
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": True},
                {"nom": "T2", "completee": True},
            ]
        }
        
        result = calculer_progression(projet)
        
        assert result == 100.0

    def test_progression_projet_en_cours_aucune_tache_completee(self):
        """Projet en cours avec aucune tâche complétée."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {
            "titre": "Test",
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": False},
                {"nom": "T2", "completee": False},
            ]
        }
        
        result = calculer_progression(projet)
        
        assert result == 0.0

    def test_progression_projet_sans_statut(self):
        """Projet sans statut utilise 'À faire' par défaut."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {"titre": "Test"}
        
        result = calculer_progression(projet)
        
        assert result == 0.0

    def test_progression_calcul_decimal(self):
        """Calcul avec résultat décimal."""
        from src.domains.maison.logic.projets_logic import calculer_progression
        
        projet = {
            "titre": "Test",
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": True},
                {"nom": "T2", "completee": False},
                {"nom": "T3", "completee": False},
            ]
        }
        
        result = calculer_progression(projet)
        
        assert abs(result - 33.33333) < 0.01  # 1/3 ≈ 33.33%
