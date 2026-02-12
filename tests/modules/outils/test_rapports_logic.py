"""
Tests pour rapports_logic.py - Fonctions pures de génération de rapports
"""

import pytest
from datetime import date, timedelta
from typing import Dict, Any, List

from src.modules.outils.rapports_utils import (
    generer_rapport_synthese,
    calculer_statistiques_periode,
    generer_section_recettes,
    generer_section_courses,
    generer_section_activites,
    comparer_periodes,
    formater_rapport_texte,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Génération Rapport Synthèse
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererRapportSynthese:
    """Tests pour generer_rapport_synthese."""

    def test_rapport_mois_defaut(self):
        """Génère un rapport mensuel par défaut."""
        data = {"recettes": [1, 2, 3], "courses": [1], "activites": [], "inventaire": [1, 2]}
        rapport = generer_rapport_synthese(data)
        
        assert rapport["periode"] == "mois"
        assert rapport["titre"] == "Rapport mois"
        assert rapport["date_generation"] == date.today()

    def test_rapport_jour(self):
        """Génère un rapport journalier."""
        data = {"recettes": [], "courses": [], "activites": [], "inventaire": []}
        rapport = generer_rapport_synthese(data, periode="jour")
        
        assert rapport["periode"] == "jour"
        assert rapport["date_debut"] == date.today() - timedelta(days=1)

    def test_rapport_semaine(self):
        """Génère un rapport hebdomadaire."""
        data = {"recettes": [], "courses": [], "activites": [], "inventaire": []}
        rapport = generer_rapport_synthese(data, periode="semaine")
        
        assert rapport["periode"] == "semaine"
        assert rapport["date_debut"] == date.today() - timedelta(days=7)

    def test_rapport_annee(self):
        """Génère un rapport annuel."""
        data = {"recettes": [], "courses": [], "activites": [], "inventaire": []}
        rapport = generer_rapport_synthese(data, periode="annee")
        
        assert rapport["periode"] == "annee"
        assert rapport["date_debut"] == date.today() - timedelta(days=365)

    def test_statistiques_comptees(self):
        """Compte correctement les statistiques."""
        data = {
            "recettes": [1, 2, 3],
            "courses": [1, 2],
            "activites": [1],
            "inventaire": [1, 2, 3, 4, 5]
        }
        rapport = generer_rapport_synthese(data)
        
        assert rapport["statistiques"]["recettes"] == 3
        assert rapport["statistiques"]["courses"] == 2
        assert rapport["statistiques"]["activites"] == 1
        assert rapport["statistiques"]["inventaire"] == 5

    def test_donnees_manquantes(self):
        """Gère les clés manquantes."""
        rapport = generer_rapport_synthese({})
        
        assert rapport["statistiques"]["recettes"] == 0
        assert rapport["statistiques"]["courses"] == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Calcul Statistiques Période
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCalculerStatistiquesPeriode:
    """Tests pour calculer_statistiques_periode."""

    def test_items_dans_periode(self):
        """Compte les items dans la période."""
        aujourd_hui = date.today()
        hier = aujourd_hui - timedelta(days=1)
        
        items = [
            {"date": aujourd_hui},
            {"date": hier},
            {"date": aujourd_hui - timedelta(days=10)},  # Hors période
        ]
        
        stats = calculer_statistiques_periode(
            items,
            date_debut=hier,
            date_fin=aujourd_hui
        )
        
        assert stats["total"] == 2

    def test_comptage_par_jour(self):
        """Compte les items par jour."""
        aujourd_hui = date.today()
        
        items = [
            {"date": aujourd_hui},
            {"date": aujourd_hui},
            {"date": aujourd_hui - timedelta(days=1)},
        ]
        
        stats = calculer_statistiques_periode(
            items,
            date_debut=aujourd_hui - timedelta(days=1),
            date_fin=aujourd_hui
        )
        
        jour_key = aujourd_hui.strftime("%Y-%m-%d")
        assert stats["par_jour"][jour_key] == 2

    def test_liste_vide(self):
        """Gère une liste vide."""
        stats = calculer_statistiques_periode(
            [],
            date_debut=date.today() - timedelta(days=7),
            date_fin=date.today()
        )
        
        assert stats["total"] == 0
        assert stats["par_jour"] == {}

    def test_date_string_iso(self):
        """Gère les dates au format ISO string."""
        aujourd_hui = date.today()
        items = [
            {"date": aujourd_hui.isoformat()},
        ]
        
        stats = calculer_statistiques_periode(
            items,
            date_debut=aujourd_hui,
            date_fin=aujourd_hui
        )
        
        assert stats["total"] == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Génération Section Recettes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererSectionRecettes:
    """Tests pour generer_section_recettes."""

    def test_section_basique(self):
        """Génère une section basique."""
        recettes = [
            {"type_repas": "déjeuner", "difficulte": "facile"},
            {"type_repas": "dîner", "difficulte": "moyen"},
        ]
        
        section = generer_section_recettes(recettes, "mois")
        
        assert section["titre"] == "ðŸ“… Recettes"
        assert section["total"] == 2

    def test_comptage_par_type(self):
        """Compte les recettes par type."""
        recettes = [
            {"type_repas": "déjeuner"},
            {"type_repas": "déjeuner"},
            {"type_repas": "dîner"},
        ]
        
        section = generer_section_recettes(recettes, "mois")
        
        assert section["par_type"]["déjeuner"] == 2
        assert section["par_type"]["dîner"] == 1

    def test_comptage_par_difficulte(self):
        """Compte les recettes par difficulté."""
        recettes = [
            {"difficulte": "facile"},
            {"difficulte": "facile"},
            {"difficulte": "difficile"},
        ]
        
        section = generer_section_recettes(recettes, "mois")
        
        assert section["par_difficulte"]["facile"] == 2
        assert section["par_difficulte"]["difficile"] == 1

    def test_type_defaut(self):
        """Utilise 'Autre' si type non spécifié."""
        recettes = [{"nom": "Sans type"}]
        
        section = generer_section_recettes(recettes, "mois")
        
        assert "Autre" in section["par_type"]

    def test_moyenne_par_jour_mois(self):
        """Calcule la moyenne par jour pour un mois."""
        recettes = [{"type_repas": "déjeuner"} for _ in range(30)]
        
        section = generer_section_recettes(recettes, "mois")
        
        assert section["moyenne_par_jour"] == 1.0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Génération Section Courses
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererSectionCourses:
    """Tests pour generer_section_courses."""

    def test_section_basique(self):
        """Génère une section basique."""
        courses = [
            {"nom": "Pain", "achete": True, "prix": 2.0, "quantite": 1},
            {"nom": "Lait", "achete": False, "prix": 1.5, "quantite": 2},
        ]
        
        section = generer_section_courses(courses)
        
        assert section["titre"] == "ðŸ’¡ Courses"
        assert section["total"] == 2
        assert section["achetes"] == 1
        assert section["non_achetes"] == 1

    def test_taux_completion(self):
        """Calcule le taux de complétion."""
        courses = [
            {"achete": True},
            {"achete": True},
            {"achete": False},
            {"achete": False},
        ]
        
        section = generer_section_courses(courses)
        
        assert section["taux_completion"] == 50.0

    def test_taux_completion_liste_vide(self):
        """Gère le taux pour liste vide."""
        section = generer_section_courses([])
        
        assert section["taux_completion"] == 0

    def test_montant_total(self):
        """Calcule le montant total."""
        courses = [
            {"prix": 10.0, "quantite": 2},  # 20
            {"prix": 5.0, "quantite": 1},   # 5
        ]
        
        section = generer_section_courses(courses)
        
        assert section["montant_total"] == 25.0

    def test_comptage_par_categorie(self):
        """Compte par catégorie."""
        courses = [
            {"categorie": "Fruits"},
            {"categorie": "Fruits"},
            {"categorie": "Légumes"},
        ]
        
        section = generer_section_courses(courses)
        
        assert section["par_categorie"]["Fruits"] == 2
        assert section["par_categorie"]["Légumes"] == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Génération Section Activités
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererSectionActivites:
    """Tests pour generer_section_activites."""

    def test_section_basique(self):
        """Génère une section basique."""
        activites = [
            {"type": "Sport", "cout": 10},
            {"type": "Culture", "cout": 15},
        ]
        
        section = generer_section_activites(activites)
        
        assert section["titre"] == "ðŸŽ¯ Activités"
        assert section["total"] == 2

    def test_comptage_par_type(self):
        """Compte les activités par type."""
        activites = [
            {"type": "Sport"},
            {"type": "Sport"},
            {"type": "Culture"},
        ]
        
        section = generer_section_activites(activites)
        
        assert section["par_type"]["Sport"] == 2
        assert section["par_type"]["Culture"] == 1

    def test_cout_total(self):
        """Calcule le coût total."""
        activites = [
            {"cout": 20},
            {"cout": 30},
        ]
        
        section = generer_section_activites(activites)
        
        assert section["cout_total"] == 50

    def test_cout_moyen(self):
        """Calcule le coût moyen."""
        activites = [
            {"cout": 10},
            {"cout": 20},
            {"cout": 30},
        ]
        
        section = generer_section_activites(activites)
        
        assert section["cout_moyen"] == 20.0

    def test_cout_moyen_liste_vide(self):
        """Gère le coût moyen pour liste vide."""
        section = generer_section_activites([])
        
        assert section["cout_moyen"] == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Comparaison Périodes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestComparerPeriodes:
    """Tests pour comparer_periodes."""

    def test_comparaison_hausse(self):
        """Détecte une hausse."""
        periode1 = {"recettes": [1, 2]}
        periode2 = {"recettes": [1, 2, 3, 4, 5]}  # +150%
        
        comparaison = comparer_periodes(periode1, periode2)
        
        assert comparaison["recettes"]["tendance"] == "hausse"
        assert comparaison["recettes"]["evolution"] == 3

    def test_comparaison_baisse(self):
        """Détecte une baisse."""
        periode1 = {"recettes": [1, 2, 3, 4, 5]}
        periode2 = {"recettes": [1, 2]}  # -60%
        
        comparaison = comparer_periodes(periode1, periode2)
        
        assert comparaison["recettes"]["tendance"] == "baisse"
        assert comparaison["recettes"]["evolution"] == -3

    def test_comparaison_stable(self):
        """Détecte une période stable."""
        periode1 = {"recettes": [1, 2, 3, 4, 5]}
        periode2 = {"recettes": [1, 2, 3, 4, 5]}  # 0%
        
        comparaison = comparer_periodes(periode1, periode2)
        
        assert comparaison["recettes"]["tendance"] == "stable"

    def test_comparaison_depuis_zero(self):
        """Gère la comparaison depuis zéro."""
        periode1 = {"recettes": []}
        periode2 = {"recettes": [1, 2, 3]}
        
        comparaison = comparer_periodes(periode1, periode2)
        
        assert comparaison["recettes"]["tendance"] == "stable"  # Division par zéro évitée

    def test_multiples_categories(self):
        """Compare plusieurs catégories."""
        periode1 = {"recettes": [1], "courses": [1, 2], "activites": [1, 2, 3]}
        periode2 = {"recettes": [1, 2, 3], "courses": [1], "activites": [1, 2, 3]}
        
        comparaison = comparer_periodes(periode1, periode2)
        
        assert "recettes" in comparaison
        assert "courses" in comparaison
        assert "activites" in comparaison


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Formatage Rapport Texte
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormaterRapportTexte:
    """Tests pour formater_rapport_texte."""

    def test_format_basique(self):
        """Formate un rapport basique."""
        rapport = {
            "titre": "Rapport test",
            "periode": "mois",
            "date_debut": date(2024, 1, 1),
            "date_fin": date(2024, 1, 31),
            "date_generation": date(2024, 2, 1),
            "statistiques": {"recettes": 10, "courses": 5},
            "sections": []
        }
        
        texte = formater_rapport_texte(rapport)
        
        assert "RAPPORT TEST" in texte
        assert "mois" in texte
        assert "2024-01-01" in texte or "01/01/2024" in texte

    def test_inclut_statistiques(self):
        """Inclut les statistiques dans le texte."""
        rapport = {
            "titre": "Test",
            "periode": "mois",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {"recettes": 15, "activites": 8},
            "sections": []
        }
        
        texte = formater_rapport_texte(rapport)
        
        assert "Recettes: 15" in texte
        assert "Activites: 8" in texte

    def test_inclut_sections(self):
        """Inclut les sections dans le texte."""
        rapport = {
            "titre": "Test",
            "periode": "mois",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {},
            "sections": [
                {"titre": "Section A", "total": 42}
            ]
        }
        
        texte = formater_rapport_texte(rapport)
        
        assert "Section A" in texte
        assert "42" in texte

    def test_retourne_string(self):
        """Retourne bien une chaîne."""
        rapport = {
            "titre": "Test",
            "statistiques": {},
            "sections": []
        }
        
        texte = formater_rapport_texte(rapport)
        
        assert isinstance(texte, str)
