"""
Tests pour src/modules/maison/jardin_utils.py
"""

from datetime import date, timedelta
from unittest.mock import patch

import pytest

from src.modules.maison.jardin_utils import (
    CATEGORIES_PLANTES,
    calculer_jours_avant_arrosage,
    calculer_jours_avant_recolte,
    calculer_statistiques_jardin,
    filtrer_par_categorie,
    filtrer_par_saison,
    filtrer_par_status,
    get_plantes_a_arroser,
    get_recoltes_proches,
    get_saison_actuelle,
    valider_plante,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def plante_basique():
    """Fixture: plante de base pour les tests"""
    return {
        "nom": "Tomate",
        "categorie": "Légumes",
        "status": "Pousse",
        "frequence_arrosage": 3,
        "dernier_arrosage": date.today() - timedelta(days=2),
    }


@pytest.fixture
def plante_avec_recolte():
    """Fixture: plante avec date de récolte"""
    return {
        "nom": "Carotte",
        "categorie": "Légumes",
        "status": "Mature",
        "date_recolte_estimee": date.today() + timedelta(days=5),
    }


@pytest.fixture
def liste_plantes():
    """Fixture: liste de plantes variées"""
    return [
        {
            "nom": "Tomate",
            "categorie": "Légumes",
            "status": "Pousse",
            "frequence_arrosage": 2,
            "dernier_arrosage": date.today() - timedelta(days=3),
        },
        {
            "nom": "Basilic",
            "categorie": "Herbes",
            "status": "Mature",
            "frequence_arrosage": 1,
            "dernier_arrosage": date.today(),
            "saisons_plantation": ["Printemps", "Été"],
        },
        {
            "nom": "Rose",
            "categorie": "Fleurs",
            "status": "Mature",
            "frequence_arrosage": 5,
            "dernier_arrosage": date.today() - timedelta(days=10),
            "date_recolte_estimee": date.today() + timedelta(days=3),
        },
        {
            "nom": "Fraise",
            "categorie": "Fruits",
            "status": "Récolte",
            "date_recolte_estimee": date.today() + timedelta(days=1),
            "saisons_plantation": ["Printemps"],
        },
    ]


# ═══════════════════════════════════════════════════════════
# TESTS SAISON
# ═══════════════════════════════════════════════════════════


class TestGetSaisonActuelle:
    """Tests pour la fonction get_saison_actuelle"""

    def test_printemps(self):
        """Teste que mars/avril/mai retournent Printemps"""
        for mois in [3, 4, 5]:
            with patch("src.modules.maison.jardin_utils.date") as mock_date:
                mock_date.today.return_value = date(2024, mois, 15)
                assert get_saison_actuelle() == "Printemps"

    def test_ete(self):
        """Teste que juin/juillet/août retournent Été"""
        for mois in [6, 7, 8]:
            with patch("src.modules.maison.jardin_utils.date") as mock_date:
                mock_date.today.return_value = date(2024, mois, 15)
                assert get_saison_actuelle() == "Été"

    def test_automne(self):
        """Teste que septembre/octobre/novembre retournent Automne"""
        for mois in [9, 10, 11]:
            with patch("src.modules.maison.jardin_utils.date") as mock_date:
                mock_date.today.return_value = date(2024, mois, 15)
                assert get_saison_actuelle() == "Automne"

    def test_hiver(self):
        """Teste que décembre/janvier/février retournent Hiver"""
        for mois in [12, 1, 2]:
            with patch("src.modules.maison.jardin_utils.date") as mock_date:
                mock_date.today.return_value = date(2024, mois, 15)
                assert get_saison_actuelle() == "Hiver"


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL ARROSAGE
# ═══════════════════════════════════════════════════════════


class TestCalculerJoursAvantArrosage:
    """Tests pour la fonction calculer_jours_avant_arrosage"""

    def test_sans_dernier_arrosage(self):
        """Teste qu'une plante sans dernier_arrosage retourne 0"""
        plante = {"nom": "Test"}
        assert calculer_jours_avant_arrosage(plante) == 0

    def test_dernier_arrosage_none(self):
        """Teste qu'un dernier_arrosage à None retourne 0"""
        plante = {"nom": "Test", "dernier_arrosage": None}
        assert calculer_jours_avant_arrosage(plante) == 0

    def test_arrosage_a_jour(self):
        """Teste une plante arrosée récemment (jours positifs restants)"""
        plante = {
            "nom": "Tomate",
            "frequence_arrosage": 7,
            "dernier_arrosage": date.today() - timedelta(days=3),
        }
        jours = calculer_jours_avant_arrosage(plante)
        assert jours == 4, "Devrait rester 4 jours avant prochain arrosage"

    def test_arrosage_en_retard(self):
        """Teste une plante en retard d'arrosage (jours négatifs)"""
        plante = {
            "nom": "Basilic",
            "frequence_arrosage": 2,
            "dernier_arrosage": date.today() - timedelta(days=5),
        }
        jours = calculer_jours_avant_arrosage(plante)
        assert jours == -3, "Devrait être en retard de 3 jours"

    def test_frequence_par_defaut(self):
        """Teste que la fréquence par défaut est 7 jours"""
        plante = {
            "nom": "Rose",
            "dernier_arrosage": date.today() - timedelta(days=3),
        }
        jours = calculer_jours_avant_arrosage(plante)
        assert jours == 4, "Avec fréquence par défaut de 7j, il reste 4j"

    def test_dernier_arrosage_string_iso(self):
        """Teste avec une date au format string ISO"""
        hier = date.today() - timedelta(days=1)
        plante = {
            "nom": "Test",
            "frequence_arrosage": 5,
            "dernier_arrosage": hier.isoformat(),
        }
        jours = calculer_jours_avant_arrosage(plante)
        assert jours == 4


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL RÉCOLTE
# ═══════════════════════════════════════════════════════════


class TestCalculerJoursAvantRecolte:
    """Tests pour la fonction calculer_jours_avant_recolte"""

    def test_sans_date_recolte(self):
        """Teste qu'une plante sans date_recolte retourne None"""
        plante = {"nom": "Test"}
        assert calculer_jours_avant_recolte(plante) is None

    def test_date_recolte_none(self):
        """Teste qu'une date_recolte à None retourne None"""
        plante = {"nom": "Test", "date_recolte_estimee": None}
        assert calculer_jours_avant_recolte(plante) is None

    def test_recolte_dans_futur(self):
        """Teste une récolte prévue dans le futur"""
        plante = {
            "nom": "Tomate",
            "date_recolte_estimee": date.today() + timedelta(days=10),
        }
        jours = calculer_jours_avant_recolte(plante)
        assert jours == 10

    def test_recolte_passee(self):
        """Teste une récolte déjà passée (jours négatifs)"""
        plante = {
            "nom": "Carotte",
            "date_recolte_estimee": date.today() - timedelta(days=3),
        }
        jours = calculer_jours_avant_recolte(plante)
        assert jours == -3

    def test_date_recolte_string_iso(self):
        """Teste avec une date au format string ISO"""
        future_date = date.today() + timedelta(days=7)
        plante = {
            "nom": "Test",
            "date_recolte_estimee": future_date.isoformat(),
        }
        jours = calculer_jours_avant_recolte(plante)
        assert jours == 7


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES ARROSAGE
# ═══════════════════════════════════════════════════════════


class TestGetPlantesAArroser:
    """Tests pour la fonction get_plantes_a_arroser"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        resultat = get_plantes_a_arroser([])
        assert resultat == []

    def test_aucune_plante_a_arroser(self):
        """Teste quand aucune plante n'a besoin d'arrosage"""
        plantes = [
            {
                "nom": "Test",
                "frequence_arrosage": 10,
                "dernier_arrosage": date.today(),
            }
        ]
        resultat = get_plantes_a_arroser(plantes, jours_avance=1)
        assert len(resultat) == 0

    def test_plante_urgente(self, liste_plantes):
        """Teste que les plantes en retard sont marquées urgentes"""
        resultat = get_plantes_a_arroser(liste_plantes)
        urgentes = [p for p in resultat if p["priorite"] == "urgent"]
        assert len(urgentes) >= 1, "Au moins une plante devrait être urgente"

    def test_tri_par_jours_restants(self):
        """Teste que le résultat est trié par jours restants"""
        plantes = [
            {"nom": "A", "frequence_arrosage": 1, "dernier_arrosage": date.today()},
            {
                "nom": "B",
                "frequence_arrosage": 1,
                "dernier_arrosage": date.today() - timedelta(days=5),
            },
            {
                "nom": "C",
                "frequence_arrosage": 1,
                "dernier_arrosage": date.today() - timedelta(days=2),
            },
        ]
        resultat = get_plantes_a_arroser(plantes, jours_avance=5)
        assert resultat[0]["nom"] == "B", "B devrait être en premier (plus en retard)"

    def test_priorite_bientot(self):
        """Teste la priorité 'bientot' pour les plantes à arroser demain"""
        plantes = [
            {
                "nom": "Test",
                "frequence_arrosage": 2,
                "dernier_arrosage": date.today() - timedelta(days=1),
            }
        ]
        resultat = get_plantes_a_arroser(plantes, jours_avance=1)
        assert len(resultat) == 1
        assert resultat[0]["priorite"] == "bientot"


# ═══════════════════════════════════════════════════════════
# TESTS RÉCOLTES PROCHES
# ═══════════════════════════════════════════════════════════


class TestGetRecoltesProches:
    """Tests pour la fonction get_recoltes_proches"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        assert get_recoltes_proches([]) == []

    def test_aucune_recolte_proche(self):
        """Teste quand aucune récolte n'est proche"""
        plantes = [{"nom": "Test", "date_recolte_estimee": date.today() + timedelta(days=30)}]
        resultat = get_recoltes_proches(plantes, jours_avance=7)
        assert len(resultat) == 0

    def test_recolte_dans_delai(self, liste_plantes):
        """Teste la détection des récoltes dans le délai"""
        resultat = get_recoltes_proches(liste_plantes, jours_avance=7)
        assert len(resultat) >= 1

    def test_recolte_passee_exclue(self):
        """Teste que les récoltes passées sont exclues"""
        plantes = [{"nom": "Test", "date_recolte_estimee": date.today() - timedelta(days=1)}]
        resultat = get_recoltes_proches(plantes, jours_avance=7)
        assert len(resultat) == 0

    def test_tri_par_jours_restants(self):
        """Teste le tri par jours restants"""
        plantes = [
            {"nom": "A", "date_recolte_estimee": date.today() + timedelta(days=5)},
            {"nom": "B", "date_recolte_estimee": date.today() + timedelta(days=1)},
            {"nom": "C", "date_recolte_estimee": date.today() + timedelta(days=3)},
        ]
        resultat = get_recoltes_proches(plantes, jours_avance=7)
        assert resultat[0]["nom"] == "B"
        assert resultat[1]["nom"] == "C"
        assert resultat[2]["nom"] == "A"


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestCalculerStatistiquesJardin:
    """Tests pour la fonction calculer_statistiques_jardin"""

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        stats = calculer_statistiques_jardin([])
        assert stats["total_plantes"] == 0
        assert stats["par_categorie"] == {}
        assert stats["par_status"] == {}

    def test_comptage_categories(self, liste_plantes):
        """Teste le comptage par catégorie"""
        stats = calculer_statistiques_jardin(liste_plantes)
        assert stats["par_categorie"]["Légumes"] == 1
        assert stats["par_categorie"]["Herbes"] == 1
        assert stats["par_categorie"]["Fleurs"] == 1
        assert stats["par_categorie"]["Fruits"] == 1

    def test_comptage_status(self, liste_plantes):
        """Teste le comptage par status"""
        stats = calculer_statistiques_jardin(liste_plantes)
        assert "Pousse" in stats["par_status"]
        assert "Mature" in stats["par_status"]

    def test_alertes_arrosage_recolte(self, liste_plantes):
        """Teste les compteurs d'alertes"""
        stats = calculer_statistiques_jardin(liste_plantes)
        assert "alertes_arrosage" in stats
        assert "alertes_recolte" in stats

    def test_categorie_autre_par_defaut(self):
        """Teste que les plantes sans catégorie vont dans 'Autre'"""
        plantes = [{"nom": "Test", "status": "Pousse"}]
        stats = calculer_statistiques_jardin(plantes)
        assert stats["par_categorie"].get("Autre", 0) == 1

    def test_status_inconnu_par_defaut(self):
        """Teste que les plantes sans status vont dans 'Inconnu'"""
        plantes = [{"nom": "Test", "categorie": "Légumes"}]
        stats = calculer_statistiques_jardin(plantes)
        assert stats["par_status"].get("Inconnu", 0) == 1


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════


class TestFiltrage:
    """Tests pour les fonctions de filtrage"""

    def test_filtrer_par_categorie(self, liste_plantes):
        """Teste le filtrage par catégorie"""
        resultat = filtrer_par_categorie(liste_plantes, "Légumes")
        assert len(resultat) == 1
        assert resultat[0]["nom"] == "Tomate"

    def test_filtrer_par_categorie_vide(self, liste_plantes):
        """Teste le filtrage avec catégorie inexistante"""
        resultat = filtrer_par_categorie(liste_plantes, "Arbres")
        assert len(resultat) == 0

    def test_filtrer_par_status(self, liste_plantes):
        """Teste le filtrage par status"""
        resultat = filtrer_par_status(liste_plantes, "Mature")
        assert len(resultat) == 2

    def test_filtrer_par_status_vide(self, liste_plantes):
        """Teste le filtrage avec status inexistant"""
        resultat = filtrer_par_status(liste_plantes, "Dormant")
        assert len(resultat) == 0

    def test_filtrer_par_saison(self, liste_plantes):
        """Teste le filtrage par saison de plantation"""
        resultat = filtrer_par_saison(liste_plantes, "Printemps")
        assert len(resultat) == 2

    def test_filtrer_par_saison_vide(self, liste_plantes):
        """Teste le filtrage avec saison non présente"""
        resultat = filtrer_par_saison(liste_plantes, "Hiver")
        assert len(resultat) == 0

    def test_filtrer_liste_vide(self):
        """Teste le filtrage sur liste vide"""
        assert filtrer_par_categorie([], "Légumes") == []
        assert filtrer_par_status([], "Pousse") == []
        assert filtrer_par_saison([], "Printemps") == []


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValiderPlante:
    """Tests pour la fonction valider_plante"""

    def test_plante_valide(self, plante_basique):
        """Teste une plante valide"""
        valide, erreurs = valider_plante(plante_basique)
        assert valide is True
        assert len(erreurs) == 0

    def test_nom_manquant(self):
        """Teste qu'un nom manquant génère une erreur"""
        valide, erreurs = valider_plante({})
        assert valide is False
        assert "Le nom est requis" in erreurs

    def test_nom_vide(self):
        """Teste qu'un nom vide génère une erreur"""
        valide, erreurs = valider_plante({"nom": ""})
        assert valide is False
        assert "Le nom est requis" in erreurs

    def test_categorie_invalide(self):
        """Teste qu'une catégorie invalide génère une erreur"""
        valide, erreurs = valider_plante({"nom": "Test", "categorie": "Invalide"})
        assert valide is False
        assert any("Categorie invalide" in e for e in erreurs)

    def test_categorie_valide(self):
        """Teste toutes les catégories valides"""
        for cat in CATEGORIES_PLANTES:
            valide, erreurs = valider_plante({"nom": "Test", "categorie": cat})
            assert valide is True, f"La catégorie {cat} devrait être valide"

    def test_frequence_arrosage_invalide_zero(self):
        """Teste qu'une fréquence à 0 génère une erreur"""
        valide, erreurs = valider_plante({"nom": "Test", "frequence_arrosage": 0})
        assert valide is False
        assert any("frequence d'arrosage" in e for e in erreurs)

    def test_frequence_arrosage_invalide_negative(self):
        """Teste qu'une fréquence négative génère une erreur"""
        valide, erreurs = valider_plante({"nom": "Test", "frequence_arrosage": -1})
        assert valide is False

    def test_frequence_arrosage_invalide_string(self):
        """Teste qu'une fréquence en string génère une erreur"""
        valide, erreurs = valider_plante({"nom": "Test", "frequence_arrosage": "cinq"})
        assert valide is False

    def test_frequence_arrosage_valide(self):
        """Teste une fréquence d'arrosage valide"""
        valide, erreurs = valider_plante({"nom": "Test", "frequence_arrosage": 5})
        assert valide is True

    def test_erreurs_multiples(self):
        """Teste l'accumulation de plusieurs erreurs"""
        valide, erreurs = valider_plante(
            {
                "categorie": "Invalide",
                "frequence_arrosage": -1,
            }
        )
        assert valide is False
        assert len(erreurs) >= 2
