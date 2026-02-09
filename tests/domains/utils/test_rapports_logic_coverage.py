"""
Tests de couverture pour rapports_logic.py
Objectif: Atteindre ≥80% de couverture
"""

import pytest
from datetime import date, timedelta
from typing import Dict, Any, List

from src.domains.utils.logic.rapports_logic import (
    generer_rapport_synthese,
    calculer_statistiques_periode,
    generer_section_recettes,
    generer_section_courses,
    generer_section_activites,
    comparer_periodes,
    formater_rapport_texte,
    formater_rapport_markdown,
    formater_rapport_html,
    preparer_export_csv,
)


# ═══════════════════════════════════════════════════════════
# TESTS GENERER RAPPORT SYNTHESE
# ═══════════════════════════════════════════════════════════


class TestGenererRapportSynthese:
    """Tests pour generer_rapport_synthese."""
    
    def test_rapport_jour(self):
        """Génère rapport journalier."""
        data = {"recettes": [1, 2], "courses": [1]}
        
        result = generer_rapport_synthese(data, "jour")
        
        assert result["periode"] == "jour"
        assert result["titre"] == "Rapport jour"
        assert result["date_fin"] == date.today()
        assert result["date_debut"] == date.today() - timedelta(days=1)
        
    def test_rapport_semaine(self):
        """Génère rapport hebdomadaire."""
        data = {"recettes": [1, 2, 3]}
        
        result = generer_rapport_synthese(data, "semaine")
        
        assert result["periode"] == "semaine"
        assert result["date_debut"] == date.today() - timedelta(days=7)
        
    def test_rapport_mois(self):
        """Génère rapport mensuel (défaut)."""
        data = {"recettes": [], "activites": [1, 2]}
        
        result = generer_rapport_synthese(data, "mois")
        
        assert result["periode"] == "mois"
        assert result["date_debut"] == date.today() - timedelta(days=30)
        
    def test_rapport_annee(self):
        """Génère rapport annuel."""
        data = {"inventaire": [1, 2, 3, 4]}
        
        result = generer_rapport_synthese(data, "annee")
        
        assert result["periode"] == "annee"
        assert result["date_debut"] == date.today() - timedelta(days=365)
        
    def test_statistiques_comptees(self):
        """Statistiques comptent les éléments."""
        data = {
            "recettes": [1, 2, 3],
            "courses": [1, 2],
            "activites": [1],
            "inventaire": []
        }
        
        result = generer_rapport_synthese(data)
        
        assert result["statistiques"]["recettes"] == 3
        assert result["statistiques"]["courses"] == 2
        assert result["statistiques"]["activites"] == 1
        assert result["statistiques"]["inventaire"] == 0
        
    def test_data_vide(self):
        """Data vide génère zéros."""
        result = generer_rapport_synthese({})
        
        assert result["statistiques"]["recettes"] == 0
        assert result["statistiques"]["courses"] == 0
        
    def test_contient_date_generation(self):
        """Contient date de génération."""
        result = generer_rapport_synthese({})
        
        assert result["date_generation"] == date.today()


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER STATISTIQUES PERIODE
# ═══════════════════════════════════════════════════════════


class TestCalculerStatistiquesPeriode:
    """Tests pour calculer_statistiques_periode."""
    
    def test_items_dans_periode(self):
        """Compte les items dans la période."""
        items = [
            {"date": date(2024, 1, 15)},
            {"date": date(2024, 1, 16)},
            {"date": date(2024, 1, 17)},
        ]
        
        result = calculer_statistiques_periode(
            items,
            date(2024, 1, 15),
            date(2024, 1, 16)
        )
        
        assert result["total"] == 2  # 15 et 16
        
    def test_items_hors_periode(self):
        """Items hors période non comptés."""
        items = [
            {"date": date(2024, 1, 10)},
            {"date": date(2024, 1, 20)},
        ]
        
        result = calculer_statistiques_periode(
            items,
            date(2024, 1, 14),
            date(2024, 1, 16)
        )
        
        assert result["total"] == 0
        
    def test_par_jour(self):
        """Compte par jour."""
        items = [
            {"date": date(2024, 1, 15)},
            {"date": date(2024, 1, 15)},
            {"date": date(2024, 1, 16)},
        ]
        
        result = calculer_statistiques_periode(
            items,
            date(2024, 1, 15),
            date(2024, 1, 16)
        )
        
        assert result["par_jour"]["2024-01-15"] == 2
        assert result["par_jour"]["2024-01-16"] == 1
        
    def test_date_string_iso(self):
        """Supporte dates en string ISO."""
        items = [
            {"date": "2024-01-15"},
        ]
        
        result = calculer_statistiques_periode(
            items,
            date(2024, 1, 15),
            date(2024, 1, 16)
        )
        
        assert result["total"] == 1
        
    def test_items_sans_date(self):
        """Items sans date ignorés."""
        items = [
            {"nom": "test"},
            {"date": date(2024, 1, 15)},
        ]
        
        result = calculer_statistiques_periode(
            items,
            date(2024, 1, 15),
            date(2024, 1, 16)
        )
        
        assert result["total"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS GENERER SECTION RECETTES
# ═══════════════════════════════════════════════════════════


class TestGenererSectionRecettes:
    """Tests pour generer_section_recettes."""
    
    def test_section_vide(self):
        """Section avec liste vide."""
        result = generer_section_recettes([], "mois")
        
        assert result["total"] == 0
        assert result["par_type"] == {}
        
    def test_compte_total(self):
        """Compte le total des recettes."""
        recettes = [
            {"nom": "Pâtes"},
            {"nom": "Riz"},
            {"nom": "Salade"}
        ]
        
        result = generer_section_recettes(recettes, "mois")
        
        assert result["total"] == 3
        
    def test_par_type(self):
        """Groupe par type de repas."""
        recettes = [
            {"type_repas": "déjeuner"},
            {"type_repas": "déjeuner"},
            {"type_repas": "dîner"},
        ]
        
        result = generer_section_recettes(recettes, "mois")
        
        assert result["par_type"]["déjeuner"] == 2
        assert result["par_type"]["dîner"] == 1
        
    def test_par_difficulte(self):
        """Groupe par difficulté."""
        recettes = [
            {"difficulte": "facile"},
            {"difficulte": "facile"},
            {"difficulte": "difficile"},
        ]
        
        result = generer_section_recettes(recettes, "mois")
        
        assert result["par_difficulte"]["facile"] == 2
        assert result["par_difficulte"]["difficile"] == 1
        
    def test_type_manquant(self):
        """Type manquant devient "Autre"."""
        recettes = [{"nom": "Test"}]
        
        result = generer_section_recettes(recettes, "mois")
        
        assert result["par_type"].get("Autre", 0) == 1
        
    def test_moyenne_par_jour_mois(self):
        """Calcule moyenne par jour pour mois."""
        recettes = [{"nom": f"R{i}"} for i in range(30)]
        
        result = generer_section_recettes(recettes, "mois")
        
        assert result["moyenne_par_jour"] == 1.0
        
    def test_moyenne_autre_periode(self):
        """Moyenne = total pour autre période."""
        recettes = [{"nom": "Test"}]
        
        result = generer_section_recettes(recettes, "semaine")
        
        assert result["moyenne_par_jour"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS GENERER SECTION COURSES
# ═══════════════════════════════════════════════════════════


class TestGenererSectionCourses:
    """Tests pour generer_section_courses."""
    
    def test_section_vide(self):
        """Section avec liste vide."""
        result = generer_section_courses([])
        
        assert result["total"] == 0
        assert result["achetes"] == 0
        assert result["taux_completion"] == 0
        
    def test_compte_achetes(self):
        """Compte les articles achetés."""
        courses = [
            {"achete": True},
            {"achete": True},
            {"achete": False},
        ]
        
        result = generer_section_courses(courses)
        
        assert result["achetes"] == 2
        assert result["non_achetes"] == 1
        
    def test_taux_completion(self):
        """Calcule le taux de completion."""
        courses = [
            {"achete": True},
            {"achete": True},
            {"achete": False},
            {"achete": False},
        ]
        
        result = generer_section_courses(courses)
        
        assert result["taux_completion"] == 50.0
        
    def test_montant_total(self):
        """Calcule le montant total."""
        courses = [
            {"prix": 10.0, "quantite": 2},
            {"prix": 5.0, "quantite": 3},
        ]
        
        result = generer_section_courses(courses)
        
        assert result["montant_total"] == 35.0  # 10*2 + 5*3
        
    def test_montant_sans_quantite(self):
        """Quantité par défaut = 1."""
        courses = [
            {"prix": 10.0},
        ]
        
        result = generer_section_courses(courses)
        
        assert result["montant_total"] == 10.0
        
    def test_par_categorie(self):
        """Groupe par catégorie."""
        courses = [
            {"categorie": "Fruits"},
            {"categorie": "Fruits"},
            {"categorie": "Légumes"},
        ]
        
        result = generer_section_courses(courses)
        
        assert result["par_categorie"]["Fruits"] == 2
        assert result["par_categorie"]["Légumes"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS GENERER SECTION ACTIVITES
# ═══════════════════════════════════════════════════════════


class TestGenererSectionActivites:
    """Tests pour generer_section_activites."""
    
    def test_section_vide(self):
        """Section avec liste vide."""
        result = generer_section_activites([])
        
        assert result["total"] == 0
        assert result["cout_moyen"] == 0
        
    def test_par_type(self):
        """Groupe par type d'activité."""
        activites = [
            {"type": "sport"},
            {"type": "sport"},
            {"type": "culture"},
        ]
        
        result = generer_section_activites(activites)
        
        assert result["par_type"]["sport"] == 2
        assert result["par_type"]["culture"] == 1
        
    def test_cout_total(self):
        """Calcule le coût total."""
        activites = [
            {"cout": 20.0},
            {"cout": 30.0},
        ]
        
        result = generer_section_activites(activites)
        
        assert result["cout_total"] == 50.0
        
    def test_cout_moyen(self):
        """Calcule le coût moyen."""
        activites = [
            {"cout": 20.0},
            {"cout": 40.0},
        ]
        
        result = generer_section_activites(activites)
        
        assert result["cout_moyen"] == 30.0


# ═══════════════════════════════════════════════════════════
# TESTS COMPARER PERIODES
# ═══════════════════════════════════════════════════════════


class TestComparerPeriodes:
    """Tests pour comparer_periodes."""
    
    def test_hausse(self):
        """Détecte une hausse > 10%."""
        periode1 = {"recettes": [1, 2, 3, 4, 5]}  # 5
        periode2 = {"recettes": [1, 2, 3, 4, 5, 6, 7]}  # 7
        
        result = comparer_periodes(periode1, periode2)
        
        assert result["recettes"]["tendance"] == "hausse"
        assert result["recettes"]["evolution"] == 2
        
    def test_baisse(self):
        """Détecte une baisse > 10%."""
        periode1 = {"recettes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}  # 10
        periode2 = {"recettes": [1, 2, 3, 4, 5]}  # 5
        
        result = comparer_periodes(periode1, periode2)
        
        assert result["recettes"]["tendance"] == "baisse"
        assert result["recettes"]["pourcentage"] == -50.0
        
    def test_stable(self):
        """Détecte stabilité (-10% à +10%)."""
        periode1 = {"recettes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}  # 10
        periode2 = {"recettes": [1, 2, 3, 4, 5, 6, 7, 8, 9]}  # 9 = -10%
        
        result = comparer_periodes(periode1, periode2)
        
        assert result["recettes"]["tendance"] == "stable"
        
    def test_periode1_vide(self):
        """Période 1 vide = pas d'évolution."""
        periode1 = {"recettes": []}
        periode2 = {"recettes": [1, 2, 3]}
        
        result = comparer_periodes(periode1, periode2)
        
        assert result["recettes"]["tendance"] == "stable"
        assert result["recettes"]["evolution"] == 0
        
    def test_compare_toutes_categories(self):
        """Compare recettes, courses et activités."""
        periode1 = {
            "recettes": [1, 2],
            "courses": [1],
            "activites": [1, 2, 3]
        }
        periode2 = {
            "recettes": [1, 2, 3],
            "courses": [1, 2],
            "activites": [1]
        }
        
        result = comparer_periodes(periode1, periode2)
        
        assert "recettes" in result
        assert "courses" in result
        assert "activites" in result


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER RAPPORT TEXTE
# ═══════════════════════════════════════════════════════════


class TestFormaterRapportTexte:
    """Tests pour formater_rapport_texte."""
    
    @pytest.fixture
    def rapport_test(self):
        """Rapport de test."""
        return {
            "titre": "Rapport Test",
            "periode": "mois",
            "date_debut": date(2024, 1, 1),
            "date_fin": date(2024, 1, 31),
            "date_generation": date(2024, 2, 1),
            "statistiques": {
                "recettes": 30,
                "courses": 15
            },
            "sections": [
                {"titre": "📅 Recettes", "total": 30}
            ]
        }
    
    def test_contient_titre(self, rapport_test):
        """Texte contient le titre."""
        result = formater_rapport_texte(rapport_test)
        
        assert "RAPPORT TEST" in result
        
    def test_contient_periode(self, rapport_test):
        """Texte contient la période."""
        result = formater_rapport_texte(rapport_test)
        
        assert "mois" in result
        
    def test_contient_statistiques(self, rapport_test):
        """Texte contient les statistiques."""
        result = formater_rapport_texte(rapport_test)
        
        assert "Recettes" in result
        assert "30" in result
        
    def test_contient_sections(self, rapport_test):
        """Texte contient les sections."""
        result = formater_rapport_texte(rapport_test)
        
        assert "DÉTAILS PAR SECTION" in result
        
    def test_rapport_sans_sections(self):
        """Rapport sans sections."""
        rapport = {
            "titre": "Test",
            "statistiques": {}
        }
        
        result = formater_rapport_texte(rapport)
        
        assert "Test" in result


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER RAPPORT MARKDOWN
# ═══════════════════════════════════════════════════════════


class TestFormaterRapportMarkdown:
    """Tests pour formater_rapport_markdown."""
    
    @pytest.fixture
    def rapport_test(self):
        """Rapport de test."""
        return {
            "titre": "Rapport MD",
            "periode": "semaine",
            "date_debut": date(2024, 1, 15),
            "date_fin": date(2024, 1, 21),
            "date_generation": date(2024, 1, 22),
            "statistiques": {
                "recettes": 14,
                "activites": 5
            },
            "sections": [
                {"titre": "Cuisine", "total": 14, "par_type": {"déjeuner": 7, "dîner": 7}}
            ]
        }
    
    def test_titre_h1(self, rapport_test):
        """Titre en H1."""
        result = formater_rapport_markdown(rapport_test)
        
        assert result.startswith("#")
        assert "Rapport MD" in result
        
    def test_contient_periode_bold(self, rapport_test):
        """Période en gras."""
        result = formater_rapport_markdown(rapport_test)
        
        assert "**Période:**" in result
        
    def test_statistiques_liste(self, rapport_test):
        """Statistiques en liste."""
        result = formater_rapport_markdown(rapport_test)
        
        assert "- **Recettes:**" in result
        
    def test_sections_h3(self, rapport_test):
        """Sections en H3."""
        result = formater_rapport_markdown(rapport_test)
        
        assert "### Cuisine" in result
        
    def test_repartition(self, rapport_test):
        """Répartition affichée."""
        result = formater_rapport_markdown(rapport_test)
        
        assert "déjeuner: 7" in result


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER RAPPORT HTML
# ═══════════════════════════════════════════════════════════


class TestFormaterRapportHtml:
    """Tests pour formater_rapport_html."""
    
    @pytest.fixture
    def rapport_test(self):
        """Rapport de test."""
        return {
            "titre": "Rapport HTML",
            "periode": "mois",
            "date_debut": date(2024, 1, 1),
            "date_fin": date(2024, 1, 31),
            "date_generation": date(2024, 2, 1),
            "statistiques": {
                "recettes": 30
            },
            "sections": [
                {"titre": "Section 1", "total": 10}
            ]
        }
    
    def test_structure_html(self, rapport_test):
        """Contient structure HTML."""
        result = formater_rapport_html(rapport_test)
        
        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "</html>" in result
        
    def test_contient_titre(self, rapport_test):
        """Contient le titre."""
        result = formater_rapport_html(rapport_test)
        
        assert "Rapport HTML" in result
        
    def test_contient_style(self, rapport_test):
        """Contient du CSS."""
        result = formater_rapport_html(rapport_test)
        
        assert "<style>" in result
        
    def test_contient_sections(self, rapport_test):
        """Contient les sections."""
        result = formater_rapport_html(rapport_test)
        
        assert "Section 1" in result
        assert "class=\"section\"" in result
        
    def test_rapport_sans_sections(self):
        """Rapport sans sections."""
        rapport = {
            "titre": "Test",
            "statistiques": {"total": 0}
        }
        
        result = formater_rapport_html(rapport)
        
        assert "<html>" in result


# ═══════════════════════════════════════════════════════════
# TESTS PREPARER EXPORT CSV
# ═══════════════════════════════════════════════════════════


class TestPreparerExportCsv:
    """Tests pour preparer_export_csv."""
    
    def test_export_basique(self):
        """Export CSV basique."""
        data = [
            {"nom": "A", "valeur": 1},
            {"nom": "B", "valeur": 2},
        ]
        colonnes = ["nom", "valeur"]
        
        result = preparer_export_csv(data, colonnes)
        
        lines = result.split("\n")
        assert lines[0] == "nom;valeur"
        assert lines[1] == "A;1"
        assert lines[2] == "B;2"
        
    def test_colonnes_manquantes(self):
        """Colonne manquante = vide."""
        data = [
            {"nom": "A"},
        ]
        colonnes = ["nom", "valeur"]
        
        result = preparer_export_csv(data, colonnes)
        
        assert "A;" in result
        
    def test_liste_vide(self):
        """Liste vide = seulement en-têtes."""
        data = []
        colonnes = ["col1", "col2"]
        
        result = preparer_export_csv(data, colonnes)
        
        assert result == "col1;col2"
        
    def test_separateur_point_virgule(self):
        """Utilise point-virgule comme séparateur."""
        data = [{"a": 1, "b": 2}]
        colonnes = ["a", "b"]
        
        result = preparer_export_csv(data, colonnes)
        
        assert ";" in result
        assert "," not in result.replace(",", "")  # Pas de virgule comme séparateur
