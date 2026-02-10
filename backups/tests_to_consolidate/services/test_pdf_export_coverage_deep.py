"""
Tests complets pour src/services/pdf_export.py

Couverture cible: >80%
"""

import pytest
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestRecettePDFData:
    """Tests schéma RecettePDFData."""

    def test_import_schema(self):
        from src.services.pdf_export import RecettePDFData
        assert RecettePDFData is not None

    def test_creation_minimal(self):
        from src.services.pdf_export import RecettePDFData
        
        data = RecettePDFData(id=1, nom="Tarte aux pommes")
        
        assert data.id == 1
        assert data.nom == "Tarte aux pommes"
        assert data.description == ""
        assert data.temps_preparation == 0
        assert data.temps_cuisson == 0
        assert data.portions == 4
        assert data.difficulte == "facile"
        assert data.ingredients == []
        assert data.etapes == []
        assert data.tags == []

    def test_creation_complete(self):
        from src.services.pdf_export import RecettePDFData
        
        data = RecettePDFData(
            id=1,
            nom="Tarte aux pommes",
            description="Délicieuse tarte familiale",
            temps_preparation=30,
            temps_cuisson=45,
            portions=8,
            difficulte="moyen",
            ingredients=[
                {"nom": "Pommes", "quantite": 4, "unite": "unités"},
                {"nom": "Sucre", "quantite": 100, "unite": "g"}
            ],
            etapes=["Éplucher les pommes", "Préparer la pâte"],
            tags=["dessert", "familial"]
        )
        
        assert data.temps_preparation == 30
        assert data.temps_cuisson == 45
        assert len(data.ingredients) == 2
        assert len(data.etapes) == 2
        assert "dessert" in data.tags


class TestPlanningPDFData:
    """Tests schéma PlanningPDFData."""

    def test_creation_minimal(self):
        from src.services.pdf_export import PlanningPDFData
        
        now = datetime.now()
        data = PlanningPDFData(
            semaine_debut=now,
            semaine_fin=now + timedelta(days=7)
        )
        
        assert data.semaine_debut is not None
        assert data.semaine_fin is not None
        assert data.repas_par_jour == {}
        assert data.total_repas == 0

    def test_creation_complete(self):
        from src.services.pdf_export import PlanningPDFData
        
        now = datetime.now()
        data = PlanningPDFData(
            semaine_debut=now,
            semaine_fin=now + timedelta(days=7),
            repas_par_jour={
                "Lundi": ["Petit-déj", "Déjeuner", "Dîner"],
                "Mardi": ["Petit-déj", "Déjeuner", "Dîner"]
            },
            total_repas=6
        )
        
        assert len(data.repas_par_jour) == 2
        assert data.total_repas == 6


class TestCoursesPDFData:
    """Tests schéma CoursesPDFData."""

    def test_creation_minimal(self):
        from src.services.pdf_export import CoursesPDFData
        
        data = CoursesPDFData()
        
        assert data.date_export is not None
        assert data.articles == []
        assert data.total_articles == 0
        assert data.par_categorie == {}

    def test_creation_complete(self):
        from src.services.pdf_export import CoursesPDFData
        
        data = CoursesPDFData(
            articles=[
                {"nom": "Lait", "quantite": 2},
                {"nom": "Pain", "quantite": 1}
            ],
            total_articles=2,
            par_categorie={
                "Frais": 1,
                "Boulangerie": 1
            }
        )
        
        assert len(data.articles) == 2
        assert data.total_articles == 2
        assert len(data.par_categorie) == 2


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE PDF EXPORT
# ═══════════════════════════════════════════════════════════


class TestPDFExportServiceInit:
    """Tests initialisation PDFExportService."""

    def test_import_service(self):
        from src.services.pdf_export import PDFExportService
        assert PDFExportService is not None

    def test_init_service(self):
        from src.services.pdf_export import PDFExportService
        
        service = PDFExportService()
        
        assert service.styles is not None
        assert hasattr(service, 'styles')

    def test_custom_styles_created(self):
        from src.services.pdf_export import PDFExportService
        
        service = PDFExportService()
        
        # Vérifier que les styles personnalisés sont créés
        assert 'TitreRecette' in service.styles.byName
        assert 'SousTitre' in service.styles.byName
        assert 'Etape' in service.styles.byName


class TestPDFExportServiceStyles:
    """Tests styles PDF personnalisés."""

    def test_style_titre_recette(self):
        from src.services.pdf_export import PDFExportService
        
        service = PDFExportService()
        style = service.styles['TitreRecette']
        
        assert style.fontSize == 24

    def test_style_sous_titre(self):
        from src.services.pdf_export import PDFExportService
        
        service = PDFExportService()
        style = service.styles['SousTitre']
        
        assert style.fontSize == 14

    def test_style_etape(self):
        from src.services.pdf_export import PDFExportService
        
        service = PDFExportService()
        style = service.styles['Etape']
        
        assert style.fontSize == 11


# ═══════════════════════════════════════════════════════════
# TESTS GENERATION PDF
# ═══════════════════════════════════════════════════════════


class TestPDFGeneration:
    """Tests génération de PDF."""

    def test_generer_pdf_recette(self):
        from src.services.pdf_export import PDFExportService, RecettePDFData
        
        service = PDFExportService()
        
        data = RecettePDFData(
            id=1,
            nom="Test Recette",
            description="Description test",
            temps_preparation=15,
            temps_cuisson=30,
            portions=4,
            difficulte="facile",
            ingredients=[{"nom": "Test", "quantite": 1, "unite": "unité"}],
            etapes=["Étape 1", "Étape 2"]
        )
        
        # Appeler la méthode privée de génération
        result = service._generer_pdf_recette(data)
        
        assert isinstance(result, BytesIO)
        # Vérifier que le buffer a du contenu avec getvalue()
        assert len(result.getvalue()) > 0

    def test_generer_pdf_recette_sans_description(self):
        from src.services.pdf_export import PDFExportService, RecettePDFData
        
        service = PDFExportService()
        
        data = RecettePDFData(
            id=1,
            nom="Recette Simple",
            ingredients=[{"nom": "Item", "quantite": 0, "unite": ""}],
            etapes=["Faire la recette"]
        )
        
        result = service._generer_pdf_recette(data)
        
        assert isinstance(result, BytesIO)

    def test_generer_pdf_recette_sans_ingredients(self):
        from src.services.pdf_export import PDFExportService, RecettePDFData
        
        service = PDFExportService()
        
        data = RecettePDFData(
            id=1,
            nom="Recette Vide"
        )
        
        result = service._generer_pdf_recette(data)
        
        assert isinstance(result, BytesIO)

    def test_generer_pdf_recette_avec_tags(self):
        from src.services.pdf_export import PDFExportService, RecettePDFData
        
        service = PDFExportService()
        
        data = RecettePDFData(
            id=1,
            nom="Recette Tags",
            tags=["végétarien", "rapide", "économique"]
        )
        
        result = service._generer_pdf_recette(data)
        
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestPDFExportEdgeCases:
    """Tests cas limites."""

    def test_recette_nom_long(self):
        from src.services.pdf_export import RecettePDFData
        
        data = RecettePDFData(
            id=1,
            nom="Recette avec un nom vraiment très très long qui pourrait poser des problèmes de mise en page"
        )
        
        assert len(data.nom) > 50

    def test_recette_description_longue(self):
        from src.services.pdf_export import RecettePDFData
        
        data = RecettePDFData(
            id=1,
            nom="Test",
            description="Lorem ipsum " * 100
        )
        
        assert len(data.description) > 500

    def test_recette_beaucoup_ingredients(self):
        from src.services.pdf_export import RecettePDFData
        
        ingredients = [
            {"nom": f"Ingrédient {i}", "quantite": i, "unite": "g"}
            for i in range(50)
        ]
        
        data = RecettePDFData(
            id=1,
            nom="Test",
            ingredients=ingredients
        )
        
        assert len(data.ingredients) == 50

    def test_recette_beaucoup_etapes(self):
        from src.services.pdf_export import RecettePDFData
        
        etapes = [f"Étape numéro {i} avec des instructions détaillées." for i in range(30)]
        
        data = RecettePDFData(
            id=1,
            nom="Test",
            etapes=etapes
        )
        
        assert len(data.etapes) == 30

    def test_planning_semaine_complete(self):
        from src.services.pdf_export import PlanningPDFData
        
        now = datetime.now()
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        repas = {jour: ["Petit-déj", "Déjeuner", "Goûter", "Dîner"] for jour in jours}
        
        data = PlanningPDFData(
            semaine_debut=now,
            semaine_fin=now + timedelta(days=7),
            repas_par_jour=repas,
            total_repas=28
        )
        
        assert len(data.repas_par_jour) == 7
        assert data.total_repas == 28


class TestPDFExportIntegration:
    """Tests d'intégration."""

    def test_workflow_export_recette(self):
        from src.services.pdf_export import PDFExportService, RecettePDFData
        
        service = PDFExportService()
        
        # Créer les données
        data = RecettePDFData(
            id=42,
            nom="Poulet rôti",
            description="Recette traditionnelle de poulet rôti aux herbes",
            temps_preparation=20,
            temps_cuisson=90,
            portions=6,
            difficulte="moyen",
            ingredients=[
                {"nom": "Poulet entier", "quantite": 1.5, "unite": "kg"},
                {"nom": "Thym", "quantite": 2, "unite": "branches"},
                {"nom": "Romarin", "quantite": 1, "unite": "branche"},
                {"nom": "Beurre", "quantite": 50, "unite": "g"}
            ],
            etapes=[
                "Préchauffer le four à 200°C",
                "Placer les herbes dans la cavité du poulet",
                "Badigeonner de beurre fondu",
                "Enfourner et cuire 1h30",
                "Arroser régulièrement"
            ],
            tags=["viande", "familial", "four"]
        )
        
        # Générer le PDF
        pdf_buffer = service._generer_pdf_recette(data)
        
        # Vérifier le résultat
        assert isinstance(pdf_buffer, BytesIO)
        pdf_content = pdf_buffer.getvalue()
        assert len(pdf_content) > 0
        # Vérifier signature PDF
        assert pdf_content[:4] == b'%PDF'

    def test_workflow_courses_liste(self):
        from src.services.pdf_export import CoursesPDFData
        
        articles = [
            {"nom": "Lait", "quantite": 2, "categorie": "Frais"},
            {"nom": "Beurre", "quantite": 1, "categorie": "Frais"},
            {"nom": "Pain", "quantite": 1, "categorie": "Boulangerie"},
            {"nom": "Pommes", "quantite": 6, "categorie": "Fruits"},
        ]
        
        par_categorie = {}
        for article in articles:
            cat = article["categorie"]
            par_categorie[cat] = par_categorie.get(cat, 0) + 1
        
        data = CoursesPDFData(
            articles=articles,
            total_articles=len(articles),
            par_categorie=par_categorie
        )
        
        assert data.total_articles == 4
        assert data.par_categorie["Frais"] == 2


class TestPDFExportImports:
    """Tests imports du module."""

    def test_import_reportlab(self):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
        
        assert A4 is not None
        assert getSampleStyleSheet is not None

    def test_import_models(self):
        from src.core.models import Recette, RecetteIngredient, Planning
        
        assert Recette is not None
        assert RecetteIngredient is not None

    def test_import_decorators(self):
        from src.core.decorators import with_db_session, with_error_handling
        
        assert with_db_session is not None
        assert with_error_handling is not None

    def test_bytesio_usage(self):
        from io import BytesIO
        
        buffer = BytesIO()
        buffer.write(b"test content")
        buffer.seek(0)
        
        assert buffer.read() == b"test content"
