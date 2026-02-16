"""
Tests pour src/modules/outils/rapports_utils.py

Tests complets pour atteindre 80%+ de couverture.
"""

from datetime import date, timedelta

import pytest

from src.modules.utilitaires.rapports_utils import (
    calculer_statistiques_periode,
    comparer_periodes,
    formater_rapport_html,
    formater_rapport_markdown,
    formater_rapport_texte,
    generer_rapport_synthese,
    generer_section_activites,
    generer_section_courses,
    generer_section_recettes,
    preparer_export_csv,
)


class TestGenererRapportSynthese:
    """Tests pour la génération de rapport de synthèse"""

    def test_rapport_jour(self):
        """Teste la génération d'un rapport journalier"""
        data = {"recettes": [1, 2], "courses": [1, 2, 3]}
        rapport = generer_rapport_synthese(data, "jour")

        assert rapport["titre"] == "Rapport jour"
        assert rapport["periode"] == "jour"
        assert rapport["date_generation"] == date.today()
        assert rapport["statistiques"]["recettes"] == 2
        assert rapport["statistiques"]["courses"] == 3

    def test_rapport_semaine(self):
        """Teste la génération d'un rapport hebdomadaire"""
        data = {"recettes": [], "activites": [1]}
        rapport = generer_rapport_synthese(data, "semaine")

        assert rapport["titre"] == "Rapport semaine"
        assert rapport["periode"] == "semaine"
        expected_debut = date.today() - timedelta(days=7)
        assert rapport["date_debut"] == expected_debut

    def test_rapport_mois(self):
        """Teste la génération d'un rapport mensuel"""
        data = {"inventaire": [1, 2, 3, 4, 5]}
        rapport = generer_rapport_synthese(data, "mois")

        assert rapport["titre"] == "Rapport mois"
        assert rapport["statistiques"]["inventaire"] == 5

    def test_rapport_annee(self):
        """Teste la génération d'un rapport annuel"""
        data = {}
        rapport = generer_rapport_synthese(data, "annee")

        expected_debut = date.today() - timedelta(days=365)
        assert rapport["date_debut"] == expected_debut

    def test_rapport_donnees_vides(self):
        """Teste avec des données vides"""
        rapport = generer_rapport_synthese({}, "mois")

        assert rapport["statistiques"]["recettes"] == 0
        assert rapport["statistiques"]["courses"] == 0
        assert rapport["sections"] == []


class TestCalculerStatistiquesPeriode:
    """Tests pour le calcul de statistiques sur une période"""

    def test_items_dans_periode(self):
        """Teste avec des items dans la période"""
        aujourd_hui = date.today()
        items = [
            {"date": aujourd_hui.isoformat()},
            {"date": aujourd_hui.isoformat()},
            {"date": (aujourd_hui - timedelta(days=1)).isoformat()},
        ]
        debut = aujourd_hui - timedelta(days=7)
        fin = aujourd_hui

        stats = calculer_statistiques_periode(items, debut, fin)

        assert stats["total"] == 3
        assert len(stats["par_jour"]) == 2

    def test_items_hors_periode(self):
        """Teste avec des items hors période"""
        aujourd_hui = date.today()
        items = [
            {"date": (aujourd_hui - timedelta(days=30)).isoformat()},
        ]
        debut = aujourd_hui - timedelta(days=7)
        fin = aujourd_hui

        stats = calculer_statistiques_periode(items, debut, fin)

        assert stats["total"] == 0

    def test_items_sans_date(self):
        """Teste avec des items sans date"""
        items = [{"nom": "test"}, {"date": None}]
        stats = calculer_statistiques_periode(items, date.today(), date.today())

        assert stats["total"] == 0

    def test_liste_vide(self):
        """Teste avec une liste vide"""
        stats = calculer_statistiques_periode([], date.today(), date.today())

        assert stats["total"] == 0
        assert stats["par_jour"] == {}


class TestGenererSectionRecettes:
    """Tests pour la génération de section recettes"""

    def test_section_recettes_complete(self):
        """Teste la génération avec données complètes"""
        recettes = [
            {"type_repas": "Déjeuner", "difficulte": "facile"},
            {"type_repas": "Déjeuner", "difficulte": "moyen"},
            {"type_repas": "Dîner", "difficulte": "difficile"},
        ]
        section = generer_section_recettes(recettes, "mois")

        assert section["titre"] == "📅 Recettes"
        assert section["total"] == 3
        assert section["par_type"]["Déjeuner"] == 2
        assert section["par_type"]["Dîner"] == 1
        assert section["par_difficulte"]["facile"] == 1

    def test_section_recettes_vide(self):
        """Teste avec liste vide"""
        section = generer_section_recettes([], "mois")

        assert section["total"] == 0
        assert section["par_type"] == {}

    def test_section_recettes_sans_type(self):
        """Teste avec recettes sans type défini"""
        recettes = [{"nom": "Test"}]
        section = generer_section_recettes(recettes, "mois")

        assert section["par_type"]["Autre"] == 1
        assert section["par_difficulte"]["moyen"] == 1

    def test_moyenne_par_jour(self):
        """Teste le calcul de la moyenne par jour"""
        recettes = [{"type_repas": "Test"} for _ in range(30)]
        section = generer_section_recettes(recettes, "mois")

        assert section["moyenne_par_jour"] == 1.0


class TestGenererSectionCourses:
    """Tests pour la génération de section courses"""

    def test_section_courses_complete(self):
        """Teste la génération avec données complètes"""
        courses = [
            {"achete": True, "prix": 10, "quantite": 2, "categorie": "Fruits"},
            {"achete": True, "prix": 5, "quantite": 1, "categorie": "Légumes"},
            {"achete": False, "prix": 3, "quantite": 3, "categorie": "Fruits"},
        ]
        section = generer_section_courses(courses)

        assert section["titre"] == "💡 Courses"
        assert section["total"] == 3
        assert section["achetes"] == 2
        assert section["non_achetes"] == 1
        assert section["montant_total"] == 34  # 10*2 + 5*1 + 3*3

    def test_section_courses_vide(self):
        """Teste avec liste vide"""
        section = generer_section_courses([])

        assert section["total"] == 0
        assert section["taux_completion"] == 0

    def test_taux_completion(self):
        """Teste le calcul du taux de complétion"""
        courses = [{"achete": True}, {"achete": True}, {"achete": False}, {"achete": False}]
        section = generer_section_courses(courses)

        assert section["taux_completion"] == 50.0

    def test_par_categorie(self):
        """Teste le groupement par catégorie"""
        courses = [
            {"categorie": "Cat1"},
            {"categorie": "Cat1"},
            {"categorie": "Cat2"},
        ]
        section = generer_section_courses(courses)

        assert section["par_categorie"]["Cat1"] == 2
        assert section["par_categorie"]["Cat2"] == 1


class TestGenererSectionActivites:
    """Tests pour la génération de section activités"""

    def test_section_activites_complete(self):
        """Teste la génération avec données complètes"""
        activites = [
            {"type": "Sport", "cout": 50},
            {"type": "Sport", "cout": 30},
            {"type": "Culture", "cout": 20},
        ]
        section = generer_section_activites(activites)

        assert section["titre"] == "🎯 Activités"
        assert section["total"] == 3
        assert section["cout_total"] == 100
        assert section["cout_moyen"] == pytest.approx(33.33, rel=0.01)

    def test_section_activites_vide(self):
        """Teste avec liste vide"""
        section = generer_section_activites([])

        assert section["total"] == 0
        assert section["cout_moyen"] == 0

    def test_par_type_activites(self):
        """Teste le groupement par type"""
        activites = [{"type": "A"}, {"type": "B"}, {"type": "A"}]
        section = generer_section_activites(activites)

        assert section["par_type"]["A"] == 2
        assert section["par_type"]["B"] == 1


class TestComparerPeriodes:
    """Tests pour la comparaison de périodes"""

    def test_comparaison_hausse(self):
        """Teste la détection d'une hausse"""
        data1 = {"recettes": [1, 2]}
        data2 = {"recettes": [1, 2, 3, 4]}

        comparaison = comparer_periodes(data1, data2)

        assert comparaison["recettes"]["tendance"] == "hausse"
        assert comparaison["recettes"]["evolution"] == 2

    def test_comparaison_baisse(self):
        """Teste la détection d'une baisse"""
        data1 = {"recettes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
        data2 = {"recettes": [1, 2]}

        comparaison = comparer_periodes(data1, data2)

        assert comparaison["recettes"]["tendance"] == "baisse"

    def test_comparaison_stable(self):
        """Teste la détection d'une stabilité"""
        data1 = {"recettes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
        data2 = {"recettes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

        comparaison = comparer_periodes(data1, data2)

        assert comparaison["recettes"]["tendance"] == "stable"

    def test_comparaison_depuis_zero(self):
        """Teste la comparaison depuis zéro"""
        data1 = {"recettes": []}
        data2 = {"recettes": [1, 2, 3]}

        comparaison = comparer_periodes(data1, data2)

        assert comparaison["recettes"]["pourcentage"] == 0

    def test_comparaison_toutes_categories(self):
        """Teste la comparaison de toutes les catégories"""
        data1 = {"recettes": [1], "courses": [1, 2], "activites": [1]}
        data2 = {"recettes": [1, 2], "courses": [1], "activites": [1, 2, 3]}

        comparaison = comparer_periodes(data1, data2)

        assert "recettes" in comparaison
        assert "courses" in comparaison
        assert "activites" in comparaison


class TestFormaterRapportTexte:
    """Tests pour le formatage en texte brut"""

    def test_format_texte_basique(self):
        """Teste le formatage texte basique"""
        rapport = {
            "titre": "Test",
            "periode": "mois",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {"recettes": 5, "courses": 10},
            "sections": [],
        }
        texte = formater_rapport_texte(rapport)

        assert "TEST" in texte
        assert "mois" in texte
        assert "Recettes: 5" in texte

    def test_format_texte_avec_sections(self):
        """Teste le formatage avec sections"""
        rapport = {
            "titre": "Test",
            "periode": "mois",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {},
            "sections": [{"titre": "Section 1", "total": 42}],
        }
        texte = formater_rapport_texte(rapport)

        assert "Section 1" in texte
        assert "42" in texte


class TestFormaterRapportMarkdown:
    """Tests pour le formatage Markdown"""

    def test_format_markdown_basique(self):
        """Teste le formatage Markdown basique"""
        rapport = {
            "titre": "Mon Rapport",
            "periode": "semaine",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {"test": 123},
            "sections": [],
        }
        md = formater_rapport_markdown(rapport)

        assert "# " in md  # Titre H1
        assert "**Periode:**" in md
        assert "## Statistiques" in md

    def test_format_markdown_avec_sections(self):
        """Teste le formatage avec sections détaillées"""
        rapport = {
            "titre": "Test",
            "periode": "mois",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {},
            "sections": [{"titre": "Section", "total": 5, "par_type": {"A": 3, "B": 2}}],
        }
        md = formater_rapport_markdown(rapport)

        assert "### Section" in md
        assert "A: 3" in md


class TestFormaterRapportHtml:
    """Tests pour le formatage HTML"""

    def test_format_html_basique(self):
        """Teste le formatage HTML basique"""
        rapport = {
            "titre": "Rapport HTML",
            "periode": "mois",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {"items": 42},
            "sections": [],
        }
        html = formater_rapport_html(rapport)

        assert "<!DOCTYPE html>" in html
        assert "<title>Rapport HTML</title>" in html
        assert "<h1>" in html
        assert "Items:</strong> 42" in html

    def test_format_html_avec_sections(self):
        """Teste le formatage avec sections"""
        rapport = {
            "titre": "Test",
            "periode": "mois",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {},
            "sections": [{"titre": "Ma Section", "total": 10}],
        }
        html = formater_rapport_html(rapport)

        assert "Ma Section" in html
        assert 'class="section"' in html


class TestPreparerExportCsv:
    """Tests pour la préparation export CSV"""

    def test_export_csv_basique(self):
        """Teste l'export CSV basique"""
        data = [
            {"nom": "A", "valeur": 1},
            {"nom": "B", "valeur": 2},
        ]
        csv = preparer_export_csv(data, ["nom", "valeur"])

        lignes = csv.split("\n")
        assert lignes[0] == "nom;valeur"
        assert lignes[1] == "A;1"
        assert lignes[2] == "B;2"

    def test_export_csv_colonnes_manquantes(self):
        """Teste avec colonnes manquantes dans les données"""
        data = [{"nom": "Test"}]
        csv = preparer_export_csv(data, ["nom", "manquant"])

        assert "Test;" in csv

    def test_export_csv_vide(self):
        """Teste avec données vides"""
        csv = preparer_export_csv([], ["col1", "col2"])

        assert csv == "col1;col2"
