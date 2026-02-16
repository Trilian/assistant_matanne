"""
Tests pour src/modules/maison/projets_utils.py
"""

from datetime import date, timedelta

import pytest

from src.modules.maison.projets_utils import (
    PRIORITES,
    STATUTS_PROJET,
    calculer_budget_total,
    calculer_jours_restants,
    calculer_progression,
    calculer_statistiques_projets,
    calculer_urgence_projet,
    filtrer_par_categorie,
    filtrer_par_priorite,
    filtrer_par_statut,
    get_projets_a_faire,
    get_projets_en_cours,
    get_projets_urgents,
    valider_projet,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def projet_basique():
    """Fixture: projet de base pour les tests"""
    return {
        "titre": "Rénovation cuisine",
        "statut": "En cours",
        "priorite": "Haute",
        "categorie": "Rénovation",
        "budget": 5000.0,
    }


@pytest.fixture
def projet_urgent():
    """Fixture: projet urgent avec date limite proche"""
    return {
        "titre": "Réparation fuite",
        "statut": "À faire",
        "priorite": "Urgente",
        "categorie": "Réparation",
        "date_limite": date.today() + timedelta(days=3),
        "budget": 500.0,
    }


@pytest.fixture
def liste_projets():
    """Fixture: liste de projets variés"""
    return [
        {
            "titre": "Projet A",
            "statut": "En cours",
            "priorite": "Haute",
            "categorie": "Rénovation",
            "budget": 1000.0,
            "cout_reel": 500.0,
            "date_limite": date.today() + timedelta(days=5),
        },
        {
            "titre": "Projet B",
            "statut": "À faire",
            "priorite": "Basse",
            "categorie": "Décoration",
            "budget": 200.0,
            "cout_reel": 0.0,
        },
        {
            "titre": "Projet C",
            "statut": "Terminé",
            "priorite": "Moyenne",
            "categorie": "Amélioration",
            "budget": 800.0,
            "cout_reel": 750.0,
        },
        {
            "titre": "Projet D",
            "statut": "En pause",
            "priorite": "Urgente",
            "categorie": "Réparation",
            "budget": 300.0,
            "cout_reel": 100.0,
            "date_limite": date.today() + timedelta(days=2),
        },
    ]


# ═══════════════════════════════════════════════════════════
# TESTS URGENCE
# ═══════════════════════════════════════════════════════════


class TestCalculerUrgenceProjet:
    """Tests pour la fonction calculer_urgence_projet"""

    def test_sans_date_limite(self):
        """Teste qu'un projet sans date limite garde sa priorité"""
        projet = {"priorite": "Moyenne"}
        assert calculer_urgence_projet(projet) == "Moyenne"

    def test_priorite_par_defaut(self):
        """Teste la priorité par défaut (Moyenne)"""
        projet = {}
        assert calculer_urgence_projet(projet) == "Moyenne"

    def test_urgente_si_priorite_urgente(self):
        """Teste qu'une priorité Urgente reste Urgente"""
        projet = {"priorite": "Urgente"}
        assert calculer_urgence_projet(projet) == "Urgente"

    def test_urgente_si_moins_de_7_jours(self):
        """Teste qu'un projet avec moins de 7 jours devient Urgent"""
        projet = {
            "priorite": "Basse",
            "date_limite": date.today() + timedelta(days=5),
        }
        assert calculer_urgence_projet(projet) == "Urgente"

    def test_haute_si_moins_de_14_jours_et_moyenne(self):
        """Teste qu'un projet Moyenne avec 7-14 jours devient Haute"""
        projet = {
            "priorite": "Moyenne",
            "date_limite": date.today() + timedelta(days=10),
        }
        assert calculer_urgence_projet(projet) == "Haute"

    def test_haute_si_moins_de_14_jours_et_haute(self):
        """Teste qu'un projet Haute avec 7-14 jours reste Haute"""
        projet = {
            "priorite": "Haute",
            "date_limite": date.today() + timedelta(days=10),
        }
        assert calculer_urgence_projet(projet) == "Haute"

    def test_garde_priorite_si_plus_de_14_jours(self):
        """Teste qu'un projet lointain garde sa priorité"""
        projet = {
            "priorite": "Basse",
            "date_limite": date.today() + timedelta(days=30),
        }
        assert calculer_urgence_projet(projet) == "Basse"

    def test_date_limite_string_iso(self):
        """Teste avec une date au format string ISO"""
        future_date = date.today() + timedelta(days=3)
        projet = {
            "priorite": "Basse",
            "date_limite": future_date.isoformat(),
        }
        assert calculer_urgence_projet(projet) == "Urgente"


# ═══════════════════════════════════════════════════════════
# TESTS JOURS RESTANTS
# ═══════════════════════════════════════════════════════════


class TestCalculerJoursRestants:
    """Tests pour la fonction calculer_jours_restants"""

    def test_sans_date_limite(self):
        """Teste qu'un projet sans date limite retourne None"""
        projet = {"titre": "Test"}
        assert calculer_jours_restants(projet) is None

    def test_date_dans_futur(self):
        """Teste une date limite dans le futur"""
        projet = {"date_limite": date.today() + timedelta(days=10)}
        assert calculer_jours_restants(projet) == 10

    def test_date_passee(self):
        """Teste une date limite dépassée (négatif)"""
        projet = {"date_limite": date.today() - timedelta(days=5)}
        assert calculer_jours_restants(projet) == -5

    def test_date_aujourdhui(self):
        """Teste une date limite aujourd'hui"""
        projet = {"date_limite": date.today()}
        assert calculer_jours_restants(projet) == 0

    def test_date_string_iso(self):
        """Teste avec une date au format string ISO"""
        future_date = date.today() + timedelta(days=7)
        projet = {"date_limite": future_date.isoformat()}
        assert calculer_jours_restants(projet) == 7


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════


class TestFiltrage:
    """Tests pour les fonctions de filtrage"""

    def test_filtrer_par_statut(self, liste_projets):
        """Teste le filtrage par statut"""
        resultat = filtrer_par_statut(liste_projets, "En cours")
        assert len(resultat) == 1
        assert resultat[0]["titre"] == "Projet A"

    def test_filtrer_par_statut_vide(self, liste_projets):
        """Teste le filtrage avec statut inexistant"""
        resultat = filtrer_par_statut(liste_projets, "Inexistant")
        assert len(resultat) == 0

    def test_filtrer_par_priorite(self, liste_projets):
        """Teste le filtrage par priorité"""
        resultat = filtrer_par_priorite(liste_projets, "Urgente")
        assert len(resultat) == 1
        assert resultat[0]["titre"] == "Projet D"

    def test_filtrer_par_priorite_vide(self, liste_projets):
        """Teste le filtrage avec priorité inexistante"""
        resultat = filtrer_par_priorite(liste_projets, "Inexistante")
        assert len(resultat) == 0

    def test_filtrer_par_categorie(self, liste_projets):
        """Teste le filtrage par catégorie"""
        resultat = filtrer_par_categorie(liste_projets, "Rénovation")
        assert len(resultat) == 1
        assert resultat[0]["titre"] == "Projet A"

    def test_filtrer_par_categorie_vide(self, liste_projets):
        """Teste le filtrage avec catégorie inexistante"""
        resultat = filtrer_par_categorie(liste_projets, "Inexistante")
        assert len(resultat) == 0

    def test_filtrer_liste_vide(self):
        """Teste le filtrage sur liste vide"""
        assert filtrer_par_statut([], "En cours") == []
        assert filtrer_par_priorite([], "Haute") == []
        assert filtrer_par_categorie([], "Rénovation") == []


# ═══════════════════════════════════════════════════════════
# TESTS PROJETS URGENTS/EN COURS/À FAIRE
# ═══════════════════════════════════════════════════════════


class TestGetProjetsUrgents:
    """Tests pour la fonction get_projets_urgents"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        assert get_projets_urgents([]) == []

    def test_detection_urgents(self, liste_projets):
        """Teste la détection des projets urgents"""
        resultat = get_projets_urgents(liste_projets)
        # Projet D est Urgente + Projet A < 7 jours donc Urgent aussi
        assert len(resultat) >= 1

    def test_tri_par_jours_restants(self):
        """Teste le tri par jours restants"""
        projets = [
            {"titre": "A", "priorite": "Urgente", "date_limite": date.today() + timedelta(days=10)},
            {"titre": "B", "priorite": "Urgente", "date_limite": date.today() + timedelta(days=2)},
            {"titre": "C", "priorite": "Urgente"},  # Sans date = 999
        ]
        resultat = get_projets_urgents(projets)
        assert resultat[0]["titre"] == "B"

    def test_inclut_jours_restants(self):
        """Teste que les jours restants sont inclus"""
        projets = [
            {
                "titre": "Test",
                "priorite": "Urgente",
                "date_limite": date.today() + timedelta(days=5),
            }
        ]
        resultat = get_projets_urgents(projets)
        assert "jours_restants" in resultat[0]
        assert resultat[0]["jours_restants"] == 5


class TestGetProjetsEnCours:
    """Tests pour la fonction get_projets_en_cours"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        assert get_projets_en_cours([]) == []

    def test_projets_en_cours(self, liste_projets):
        """Teste la récupération des projets en cours"""
        resultat = get_projets_en_cours(liste_projets)
        assert len(resultat) == 1
        assert resultat[0]["titre"] == "Projet A"


class TestGetProjetsAFaire:
    """Tests pour la fonction get_projets_a_faire"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        assert get_projets_a_faire([]) == []

    def test_projets_a_faire(self, liste_projets):
        """Teste la récupération des projets à faire"""
        resultat = get_projets_a_faire(liste_projets)
        assert len(resultat) == 1
        assert resultat[0]["titre"] == "Projet B"


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestCalculerStatistiquesProjets:
    """Tests pour la fonction calculer_statistiques_projets"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        stats = calculer_statistiques_projets([])
        assert stats["total"] == 0
        assert stats["taux_completion"] == 0.0
        assert stats["par_statut"] == {}
        assert stats["par_priorite"] == {}

    def test_comptage_statuts(self, liste_projets):
        """Teste le comptage par statut"""
        stats = calculer_statistiques_projets(liste_projets)
        assert stats["par_statut"]["En cours"] == 1
        assert stats["par_statut"]["À faire"] == 1
        assert stats["par_statut"]["Terminé"] == 1
        assert stats["par_statut"]["En pause"] == 1

    def test_comptage_priorites(self, liste_projets):
        """Teste le comptage par priorité"""
        stats = calculer_statistiques_projets(liste_projets)
        assert stats["par_priorite"]["Haute"] == 1
        assert stats["par_priorite"]["Basse"] == 1
        assert stats["par_priorite"]["Moyenne"] == 1
        assert stats["par_priorite"]["Urgente"] == 1

    def test_taux_completion(self, liste_projets):
        """Teste le calcul du taux de complétion"""
        stats = calculer_statistiques_projets(liste_projets)
        # 1 terminé sur 4 = 25%
        assert stats["taux_completion"] == 25.0

    def test_compteur_urgents(self, liste_projets):
        """Teste le comptage des urgents"""
        stats = calculer_statistiques_projets(liste_projets)
        assert "urgents" in stats
        assert stats["urgents"] >= 1

    def test_statut_inconnu_par_defaut(self):
        """Teste que les projets sans statut vont dans 'Inconnu'"""
        projets = [{"titre": "Test", "priorite": "Haute"}]
        stats = calculer_statistiques_projets(projets)
        assert stats["par_statut"].get("Inconnu", 0) == 1

    def test_priorite_moyenne_par_defaut(self):
        """Teste que les projets sans priorité vont dans 'Moyenne'"""
        projets = [{"titre": "Test", "statut": "En cours"}]
        stats = calculer_statistiques_projets(projets)
        assert stats["par_priorite"].get("Moyenne", 0) == 1


# ═══════════════════════════════════════════════════════════
# TESTS BUDGET
# ═══════════════════════════════════════════════════════════


class TestCalculerBudgetTotal:
    """Tests pour la fonction calculer_budget_total"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        budgets = calculer_budget_total([])
        assert budgets["budget_total"] == 0.0
        assert budgets["budget_depense"] == 0.0
        assert budgets["budget_restant"] == 0.0

    def test_calcul_budgets(self, liste_projets):
        """Teste le calcul des budgets"""
        budgets = calculer_budget_total(liste_projets)
        # 1000 + 200 + 800 + 300 = 2300
        assert budgets["budget_total"] == 2300.0
        # 500 + 0 + 750 + 100 = 1350
        assert budgets["budget_depense"] == 1350.0
        # 2300 - 1350 = 950
        assert budgets["budget_restant"] == 950.0

    def test_sans_budget(self):
        """Teste avec des projets sans budget"""
        projets = [{"titre": "Test"}]
        budgets = calculer_budget_total(projets)
        assert budgets["budget_total"] == 0.0

    def test_sans_cout_reel(self):
        """Teste avec des projets sans coût réel"""
        projets = [{"titre": "Test", "budget": 1000.0}]
        budgets = calculer_budget_total(projets)
        assert budgets["budget_depense"] == 0.0
        assert budgets["budget_restant"] == 1000.0


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValiderProjet:
    """Tests pour la fonction valider_projet"""

    def test_projet_valide(self, projet_basique):
        """Teste un projet valide"""
        valide, erreurs = valider_projet(projet_basique)
        assert valide is True
        assert len(erreurs) == 0

    def test_titre_manquant(self):
        """Teste qu'un titre manquant génère une erreur"""
        valide, erreurs = valider_projet({})
        assert valide is False
        assert "Le titre est requis" in erreurs

    def test_titre_vide(self):
        """Teste qu'un titre vide génère une erreur"""
        valide, erreurs = valider_projet({"titre": ""})
        assert valide is False
        assert "Le titre est requis" in erreurs

    def test_statut_invalide(self):
        """Teste qu'un statut invalide génère une erreur"""
        valide, erreurs = valider_projet({"titre": "Test", "statut": "Invalide"})
        assert valide is False
        assert any("Statut invalide" in e for e in erreurs)

    def test_statuts_valides(self):
        """Teste tous les statuts valides"""
        for statut in STATUTS_PROJET:
            valide, erreurs = valider_projet({"titre": "Test", "statut": statut})
            assert valide is True, f"Le statut {statut} devrait être valide"

    def test_priorite_invalide(self):
        """Teste qu'une priorité invalide génère une erreur"""
        valide, erreurs = valider_projet({"titre": "Test", "priorite": "Invalide"})
        assert valide is False
        assert any("Priorite invalide" in e for e in erreurs)

    def test_priorites_valides(self):
        """Teste toutes les priorités valides"""
        for priorite in PRIORITES:
            valide, erreurs = valider_projet({"titre": "Test", "priorite": priorite})
            assert valide is True, f"La priorité {priorite} devrait être valide"

    def test_budget_negatif(self):
        """Teste qu'un budget négatif génère une erreur"""
        valide, erreurs = valider_projet({"titre": "Test", "budget": -100})
        assert valide is False
        assert any("budget" in e.lower() for e in erreurs)

    def test_budget_string(self):
        """Teste qu'un budget en string génère une erreur"""
        valide, erreurs = valider_projet({"titre": "Test", "budget": "mille"})
        assert valide is False

    def test_budget_valide_zero(self):
        """Teste qu'un budget à 0 est valide"""
        valide, erreurs = valider_projet({"titre": "Test", "budget": 0})
        assert valide is True

    def test_budget_valide_float(self):
        """Teste qu'un budget en float est valide"""
        valide, erreurs = valider_projet({"titre": "Test", "budget": 1500.50})
        assert valide is True

    def test_erreurs_multiples(self):
        """Teste l'accumulation de plusieurs erreurs"""
        valide, erreurs = valider_projet(
            {
                "statut": "Invalide",
                "priorite": "Invalide",
                "budget": -100,
            }
        )
        assert valide is False
        assert len(erreurs) >= 3


# ═══════════════════════════════════════════════════════════
# TESTS PROGRESSION
# ═══════════════════════════════════════════════════════════


class TestCalculerProgression:
    """Tests pour la fonction calculer_progression"""

    def test_projet_termine(self):
        """Teste qu'un projet terminé retourne 100%"""
        projet = {"statut": "Termine"}
        assert calculer_progression(projet) == 100.0

    def test_projet_a_faire(self):
        """Teste qu'un projet à faire retourne 0%"""
        projet = {"statut": "À faire"}
        assert calculer_progression(projet) == 0.0

    def test_projet_en_cours_sans_taches(self):
        """Teste qu'un projet en cours sans tâches retourne 50%"""
        projet = {"statut": "En cours"}
        assert calculer_progression(projet) == 50.0

    def test_projet_en_cours_avec_taches(self):
        """Teste le calcul basé sur les tâches"""
        projet = {
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": True},
                {"nom": "T2", "completee": True},
                {"nom": "T3", "completee": False},
                {"nom": "T4", "completee": False},
            ],
        }
        # 2 sur 4 = 50%
        assert calculer_progression(projet) == 50.0

    def test_projet_en_cours_toutes_taches_completees(self):
        """Teste avec toutes les tâches complétées"""
        projet = {
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": True},
                {"nom": "T2", "completee": True},
            ],
        }
        assert calculer_progression(projet) == 100.0

    def test_projet_en_cours_aucune_tache_completee(self):
        """Teste avec aucune tâche complétée"""
        projet = {
            "statut": "En cours",
            "taches": [
                {"nom": "T1", "completee": False},
                {"nom": "T2", "completee": False},
            ],
        }
        assert calculer_progression(projet) == 0.0

    def test_projet_en_cours_taches_vides(self):
        """Teste avec une liste de tâches vide qui retourne 50%"""
        projet = {"statut": "En cours", "taches": []}
        assert calculer_progression(projet) == 50.0

    def test_statut_par_defaut(self):
        """Teste qu'un projet sans statut retourne 0%"""
        projet = {}
        assert calculer_progression(projet) == 0.0

    def test_statut_en_pause(self):
        """Teste qu'un projet en pause retourne 0%"""
        projet = {"statut": "En pause"}
        assert calculer_progression(projet) == 0.0
