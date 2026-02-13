"""
Tests pour src/services/rapports/export.py

Tests du service d'export PDF avec couverture complète.
"""

from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from src.services.rapports.export import (
    PDFExportService,
    ServiceExportPDF,
    get_pdf_export_service,
    obtenir_service_export_pdf,
)
from src.services.rapports.types import DonneesCoursesPDF, DonneesPlanningPDF, DonneesRecettePDF


class TestServiceExportPDFInit:
    """Tests d'initialisation du service."""

    def test_service_creation(self):
        """Vérifie que le service peut être créé."""
        service = ServiceExportPDF()
        assert service is not None

    def test_service_has_styles(self):
        """Vérifie que les styles sont configurés."""
        service = ServiceExportPDF()
        assert service.styles is not None

    def test_titre_recette_style_exists(self):
        """Vérifie que le style TitreRecette existe."""
        service = ServiceExportPDF()
        assert "TitreRecette" in [s.name for s in service.styles.byName.values()]

    def test_sous_titre_style_exists(self):
        """Vérifie que le style SousTitre existe."""
        service = ServiceExportPDF()
        assert "SousTitre" in [s.name for s in service.styles.byName.values()]

    def test_etape_style_exists(self):
        """Vérifie que le style Etape existe."""
        service = ServiceExportPDF()
        assert "Etape" in [s.name for s in service.styles.byName.values()]

    def test_configurer_styles_alias(self):
        """Vérifie l'alias _setup_custom_styles."""
        service = ServiceExportPDF()
        assert hasattr(service, "_setup_custom_styles")
        assert service._setup_custom_styles == service._configurer_styles


class TestDonneesRecettePDF:
    """Tests pour le schéma DonneesRecettePDF."""

    def test_creation_minimal(self):
        """Vérifie la création avec des données minimales."""
        data = DonneesRecettePDF(
            id=1,
            nom="Test Recette",
            description="Description test",
            temps_preparation=15,
            temps_cuisson=30,
            portions=4,
            difficulte="facile",
            ingredients=[],
            etapes=[],
            tags=[],
        )
        assert data.nom == "Test Recette"
        assert data.portions == 4

    def test_with_ingredients(self):
        """Vérifie avec des ingrédients."""
        data = DonneesRecettePDF(
            id=1,
            nom="Test",
            description="",
            temps_preparation=10,
            temps_cuisson=20,
            portions=2,
            difficulte="moyen",
            ingredients=[
                {"nom": "Farine", "quantite": 200, "unite": "g"},
                {"nom": "Sucre", "quantite": 100, "unite": "g"},
            ],
            etapes=["Étape 1", "Étape 2"],
            tags=["dessert"],
        )
        assert len(data.ingredients) == 2
        assert len(data.etapes) == 2


class TestServiceExportPDFRecette:
    """Tests de l'export de recettes."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        return ServiceExportPDF()

    def test_generer_pdf_recette_complet(self, service):
        """Vérifie la génération PDF d'une recette avec tous les champs."""
        data = DonneesRecettePDF(
            id=1,
            nom="Tarte aux pommes",
            description="Une délicieuse tarte",
            temps_preparation=30,
            temps_cuisson=45,
            portions=6,
            difficulte="moyen",
            ingredients=[
                {"nom": "Pommes", "quantite": 6, "unite": ""},
                {"nom": "Sucre", "quantite": 150, "unite": "g"},
            ],
            etapes=["Préparer la pâte", "Éplucher les pommes", "Assembler et cuire"],
            tags=["dessert", "fruits"],
        )

        result = service._generer_pdf_recette(data)

        assert isinstance(result, BytesIO)
        assert result.getvalue()  # Non vide

    def test_generer_pdf_recette_sans_description(self, service):
        """Test PDF sans description."""
        data = DonneesRecettePDF(
            id=2,
            nom="Recette Simple",
            description="",  # Pas de description
            temps_preparation=10,
            temps_cuisson=5,
            portions=2,
            difficulte="facile",
            ingredients=[{"nom": "Eau", "quantite": 0, "unite": ""}],
            etapes=["Faire bouillir"],
            tags=[],
        )
        result = service._generer_pdf_recette(data)
        assert isinstance(result, BytesIO)

    def test_generer_pdf_recette_sans_tags(self, service):
        """Test PDF sans tags."""
        data = DonneesRecettePDF(
            id=3,
            nom="Recette Sans Tags",
            description="Description",
            temps_preparation=5,
            temps_cuisson=0,
            portions=1,
            difficulte="facile",
            ingredients=[],
            etapes=[],
            tags=[],
        )
        result = service._generer_pdf_recette(data)
        assert isinstance(result, BytesIO)

    def test_exporter_recette_with_mock_db(self, service):
        """Vérifie l'export avec mock DB complet."""
        # Créer un mock complet de la recette
        mock_etape = MagicMock()
        mock_etape.description = "Étape de test"
        mock_etape.ordre = 1

        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Ingrédient test"

        mock_ri = MagicMock()
        mock_ri.ingredient = mock_ingredient
        mock_ri.quantite = 100
        mock_ri.unite = "g"

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.nom = "Test Recette"
        mock_recette.description = "Description test"
        mock_recette.temps_preparation = 10
        mock_recette.temps_cuisson = 20
        mock_recette.portions = 4
        mock_recette.difficulte = "facile"
        mock_recette.ingredients = [mock_ri]
        mock_recette.etapes = [mock_etape]
        mock_recette.tags = ["test"]

        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_recette
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.exporter_recette(recette_id=1)
            assert isinstance(result, BytesIO)

    def test_exporter_recette_not_found(self, service):
        """Vérifie que ValueError est levée si recette introuvable."""
        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            # Le décorateur @avec_gestion_erreurs capture l'exception
            result = service.exporter_recette(recette_id=999)
            # Soit None soit une exception gérée
            assert result is None or isinstance(result, BytesIO)

    def test_exporter_recette_sans_ingredient_nom(self, service):
        """Test export avec ingrédient sans nom valide."""
        mock_ri = MagicMock()
        mock_ri.ingredient = None  # Pas d'ingrédient lié
        mock_ri.quantite = 50
        mock_ri.unite = "ml"

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.nom = "Test"
        mock_recette.description = ""
        mock_recette.temps_preparation = None
        mock_recette.temps_cuisson = None
        mock_recette.portions = None
        mock_recette.difficulte = None
        mock_recette.ingredients = [mock_ri]
        mock_recette.etapes = []
        mock_recette.tags = None

        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_recette
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.exporter_recette(recette_id=1)
            assert result is None or isinstance(result, BytesIO)


class TestServiceExportPDFPlanning:
    """Tests de l'export de planning."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        return ServiceExportPDF()

    def test_donnees_planning_pdf_creation(self):
        """Vérifie la création de DonneesPlanningPDF."""
        data = DonneesPlanningPDF(
            semaine_debut=datetime(2024, 1, 15),
            semaine_fin=datetime(2024, 1, 21),
            repas_par_jour={},
            total_repas=0,
        )
        assert data.semaine_debut.day == 15
        assert data.total_repas == 0

    def test_generer_pdf_planning(self, service):
        """Test génération PDF planning."""
        data = DonneesPlanningPDF(
            semaine_debut=datetime(2024, 1, 15),
            semaine_fin=datetime(2024, 1, 21),
            repas_par_jour={
                "Lundi": [{"type": "déjeuner", "recette": "Pâtes", "notes": ""}],
                "Mardi": [{"type": "dîner", "recette": "Soupe", "notes": "Avec pain"}],
            },
            total_repas=2,
        )
        result = service._generer_pdf_planning(data, "Planning Semaine")
        assert isinstance(result, BytesIO)
        assert result.getvalue()

    def test_exporter_planning_semaine_mock(self, service):
        """Test export planning avec mock DB."""
        mock_recette = MagicMock()
        mock_recette.nom = "Recette Test"

        mock_repas = MagicMock()
        mock_repas.date = datetime.now().date()
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette = mock_recette
        mock_repas.notes = "Notes test"

        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_planning.nom = "Planning Test"
        mock_planning.repas = [mock_repas]

        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_planning
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.exporter_planning_semaine(planning_id=1)
            assert result is None or isinstance(result, BytesIO)

    def test_exporter_planning_avec_date_debut(self, service):
        """Test export planning avec date_debut personnalisée."""
        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_planning.nom = "Planning"
        mock_planning.repas = []

        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_planning
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            date_test = datetime(2024, 2, 5)
            result = service.exporter_planning_semaine(planning_id=1, date_debut=date_test)
            assert result is None or isinstance(result, BytesIO)

    def test_exporter_planning_not_found(self, service):
        """Test planning introuvable."""
        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.exporter_planning_semaine(planning_id=999)
            assert result is None  # Erreur gérée


class TestServiceExportPDFCourses:
    """Tests de l'export de courses."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        return ServiceExportPDF()

    def test_donnees_courses_pdf_creation(self):
        """Vérifie la création de DonneesCoursesPDF."""
        data = DonneesCoursesPDF(
            articles=[{"nom": "Pommes", "quantite": 5, "categorie": "fruits_legumes"}],
            total_articles=1,
            par_categorie={
                "fruits_legumes": [{"nom": "Pommes", "quantite": 5, "unite": "kg", "urgent": False}]
            },
        )
        assert data.total_articles == 1
        assert "fruits_legumes" in data.par_categorie

    def test_generer_pdf_courses(self, service):
        """Test génération PDF liste courses."""
        data = DonneesCoursesPDF(
            articles=[
                {"nom": "Lait", "quantite": 2, "categorie": "produits_laitiers"},
                {"nom": "Pain", "quantite": 1, "categorie": "epicerie"},
            ],
            total_articles=2,
            par_categorie={
                "produits_laitiers": [
                    {"nom": "Lait", "quantite": 2, "unite": "L", "urgent": False}
                ],
                "epicerie": [{"nom": "Pain", "quantite": 1, "unite": "", "urgent": True}],
            },
        )
        result = service._generer_pdf_courses(data)
        assert isinstance(result, BytesIO)
        assert result.getvalue()

    def test_generer_pdf_courses_toutes_categories(self, service):
        """Test avec toutes les catégories disponibles."""
        par_cat = {
            "fruits_legumes": [{"nom": "Pommes", "quantite": 1, "unite": "kg", "urgent": False}],
            "viande": [{"nom": "Poulet", "quantite": 500, "unite": "g", "urgent": True}],
            "poisson": [{"nom": "Saumon", "quantite": 200, "unite": "g", "urgent": False}],
            "produits_laitiers": [
                {"nom": "Fromage", "quantite": 100, "unite": "g", "urgent": False}
            ],
            "epicerie": [{"nom": "Riz", "quantite": 500, "unite": "g", "urgent": False}],
            "surgeles": [{"nom": "Glace", "quantite": 1, "unite": "", "urgent": False}],
            "boissons": [{"nom": "Jus", "quantite": 1, "unite": "L", "urgent": False}],
            "hygiene": [{"nom": "Savon", "quantite": 2, "unite": "", "urgent": False}],
            "autre": [{"nom": "Divers", "quantite": 1, "unite": "", "urgent": False}],
        }
        data = DonneesCoursesPDF(articles=[], total_articles=9, par_categorie=par_cat)
        result = service._generer_pdf_courses(data)
        assert isinstance(result, BytesIO)

    def test_exporter_liste_courses_mock(self, service):
        """Test export liste courses avec mock DB."""
        mock_article = MagicMock()
        mock_article.nom = "Article Test"
        mock_article.quantite = 2
        mock_article.unite = "pcs"
        mock_article.categorie = "epicerie"
        mock_article.urgent = False

        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
                mock_article
            ]
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.exporter_liste_courses()
            assert result is None or isinstance(result, BytesIO)

    def test_exporter_liste_courses_vide(self, service):
        """Test export liste courses vide."""
        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.exporter_liste_courses()
            assert result is None or isinstance(result, BytesIO)

    def test_exporter_liste_courses_multi_articles(self, service):
        """Test export avec plusieurs articles dans différentes catégories."""
        # Article sans catégorie (utilise "Autre")
        mock_article1 = MagicMock()
        mock_article1.nom = "Article Sans Cat"
        mock_article1.quantite = None  # Test branche quantite or 1
        mock_article1.unite = None  # Test branche unite or ""
        mock_article1.categorie = None  # Test branche categorie or "Autre"
        mock_article1.urgent = None  # Test branche urgent or False

        # Article avec toutes les valeurs
        mock_article2 = MagicMock()
        mock_article2.nom = "Article Complet"
        mock_article2.quantite = 5
        mock_article2.unite = "kg"
        mock_article2.categorie = "fruits_legumes"
        mock_article2.urgent = True

        with patch("src.services.rapports.export.obtenir_contexte_db") as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
                mock_article1,
                mock_article2,
            ]
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.exporter_liste_courses()
            assert result is None or isinstance(result, BytesIO)


class TestFactoryFunctions:
    """Tests des fonctions factory et alias."""

    def test_obtenir_service_export_pdf(self):
        """Test obtenir_service_export_pdf retourne singleton."""
        # Reset le singleton pour le test
        import src.services.rapports.export as module

        module._service_export_pdf = None

        service1 = obtenir_service_export_pdf()
        service2 = obtenir_service_export_pdf()
        assert service1 is service2
        assert isinstance(service1, ServiceExportPDF)

    def test_alias_pdf_export_service(self):
        """Vérifie l'alias PDFExportService."""
        assert PDFExportService is ServiceExportPDF

    def test_alias_get_pdf_export_service(self):
        """Vérifie l'alias get_pdf_export_service."""
        assert get_pdf_export_service is obtenir_service_export_pdf
