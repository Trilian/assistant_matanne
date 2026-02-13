"""
Tests de couverture complÃ©mentaires pour projets_logic.py
Objectif: atteindre 80%+ de couverture
Couvre les lignes non testÃ©es: 216-232, 245-258
"""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VALIDER_PROJET - lignes 216-232
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValiderProjet:
    """Tests pour valider_projet."""

    def test_projet_valide(self):
        """Projet avec titre valide."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"titre": "RÃ©novation cuisine", "statut": "En cours", "priorite": "Haute"}

        valide, erreurs = valider_projet(data)

        assert valide is True
        assert len(erreurs) == 0

    def test_projet_sans_titre(self):
        """Projet sans titre invalide."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"statut": "En cours"}

        valide, erreurs = valider_projet(data)

        assert valide is False
        assert any("titre" in e.lower() for e in erreurs)

    def test_projet_titre_vide(self):
        """Projet avec titre vide invalide."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"titre": "", "statut": "En cours"}

        valide, erreurs = valider_projet(data)

        assert valide is False
        assert any("titre" in e.lower() for e in erreurs)

    def test_projet_statut_invalide(self):
        """Statut non autorisÃ©."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"titre": "Test", "statut": "StatutInconnu"}

        valide, erreurs = valider_projet(data)

        assert valide is False
        assert any("statut" in e.lower() for e in erreurs)

    def test_projet_priorite_invalide(self):
        """PrioritÃ© non autorisÃ©e."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"titre": "Test", "priorite": "Urgentissime"}

        valide, erreurs = valider_projet(data)

        assert valide is False
        assert any("prioritÃ©" in e.lower() for e in erreurs)

    def test_projet_budget_negatif(self):
        """Budget nÃ©gatif invalide."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"titre": "Test", "budget": -100}

        valide, erreurs = valider_projet(data)

        assert valide is False
        assert any("budget" in e.lower() for e in erreurs)

    def test_projet_budget_non_numerique(self):
        """Budget non numÃ©rique invalide."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"titre": "Test", "budget": "mille"}

        valide, erreurs = valider_projet(data)

        assert valide is False
        assert any("budget" in e.lower() for e in erreurs)

    def test_projet_budget_zero_valide(self):
        """Budget Ã  zÃ©ro valide."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"titre": "Test", "budget": 0}

        valide, erreurs = valider_projet(data)

        assert valide is True

    def test_projet_budget_float_valide(self):
        """Budget en float valide."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"titre": "Test", "budget": 1500.50}

        valide, erreurs = valider_projet(data)

        assert valide is True

    def test_projet_multiple_erreurs(self):
        """Plusieurs erreurs Ã  la fois."""
        from src.modules.maison.logic.projets_logic import valider_projet

        data = {"statut": "Inconnu", "priorite": "SuperHaute", "budget": -50}

        valide, erreurs = valider_projet(data)

        assert valide is False
        assert len(erreurs) >= 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALCULER_PROGRESSION - lignes 245-258
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCalculerProgression:
    """Tests pour calculer_progression."""

    def test_progression_projet_termine(self):
        """Projet terminÃ© = 100%."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {"titre": "Test", "statut": "TerminÃ©"}

        result = calculer_progression(projet)

        assert result == 100.0

    def test_progression_projet_a_faire(self):
        """Projet Ã  faire = 0%."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {"titre": "Test", "statut": "Ã€ faire"}

        result = calculer_progression(projet)

        assert result == 0.0

    def test_progression_projet_en_cours_sans_taches(self):
        """Projet en cours sans tÃ¢ches = 50% par dÃ©faut."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {"titre": "Test", "statut": "En cours"}

        result = calculer_progression(projet)

        assert result == 50.0

    def test_progression_projet_en_cours_avec_taches_vides(self):
        """Projet en cours avec liste tÃ¢ches vide = 50%."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {"titre": "Test", "statut": "En cours", "taches": []}

        result = calculer_progression(projet)

        assert result == 50.0

    def test_progression_projet_en_cours_taches_partielles(self):
        """Projet en cours avec tÃ¢ches partiellement complÃ©tÃ©es."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {
            "titre": "Test",
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": True},
                {"nom": "T2", "completee": False},
                {"nom": "T3", "completee": True},
                {"nom": "T4", "completee": False},
            ],
        }

        result = calculer_progression(projet)

        assert result == 50.0  # 2/4 = 50%

    def test_progression_projet_en_cours_toutes_taches_completees(self):
        """Projet en cours avec toutes tÃ¢ches complÃ©tÃ©es."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {
            "titre": "Test",
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": True},
                {"nom": "T2", "completee": True},
            ],
        }

        result = calculer_progression(projet)

        assert result == 100.0

    def test_progression_projet_en_cours_aucune_tache_completee(self):
        """Projet en cours avec aucune tÃ¢che complÃ©tÃ©e."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {
            "titre": "Test",
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": False},
                {"nom": "T2", "completee": False},
            ],
        }

        result = calculer_progression(projet)

        assert result == 0.0

    def test_progression_projet_sans_statut(self):
        """Projet sans statut utilise 'Ã€ faire' par dÃ©faut."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {"titre": "Test"}

        result = calculer_progression(projet)

        assert result == 0.0

    def test_progression_calcul_decimal(self):
        """Calcul avec rÃ©sultat dÃ©cimal."""
        from src.modules.maison.logic.projets_logic import calculer_progression

        projet = {
            "titre": "Test",
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": True},
                {"nom": "T2", "completee": False},
                {"nom": "T3", "completee": False},
            ],
        }

        result = calculer_progression(projet)

        assert abs(result - 33.33333) < 0.01  # 1/3 â‰ˆ 33.33%
