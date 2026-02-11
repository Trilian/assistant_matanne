"""
Tests pour src/services/rapports/export.py

Couverture cible: >80%
Teste l'export PDF de recettes, planning et courses.
"""

import pytest
from io import BytesIO
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

from src.services.rapports.export import (
    ServiceExportPDF,
    obtenir_service_export_pdf,
    PDFExportService,
    get_pdf_export_service,
)
from src.services.rapports.types import (
    DonneesRecettePDF,
    DonneesPlanningPDF,
    DonneesCoursesPDF,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Instance fraîche du service d'export PDF."""
    return ServiceExportPDF()


@pytest.fixture
def sample_recette_data():
    """Données de recette pour test."""
    return DonneesRecettePDF(
        id=1,
        nom="Tarte aux pommes",
        description="Une délicieuse tarte maison",
        temps_preparation=30,
        temps_cuisson=45,
        portions=8,
        difficulte="moyen",
        ingredients=[
            {"nom": "Pommes", "quantite": 6, "unite": "pièces"},
            {"nom": "Farine", "quantite": 250, "unite": "g"},
            {"nom": "Beurre", "quantite": 125, "unite": "g"},
            {"nom": "Sucre", "quantite": 100, "unite": "g"},
        ],
        etapes=[
            "Préparer la pâte en mélangeant farine et beurre",
            "Éplucher et couper les pommes en fines tranches",
            "Disposer les pommes sur la pâte",
            "Enfourner à 180°C pendant 45 minutes",
        ],
        tags=["dessert", "fruits", "classique"],
    )


@pytest.fixture
def sample_planning_data():
    """Données de planning pour test."""
    now = datetime.now()
    debut = now - timedelta(days=now.weekday())
    return DonneesPlanningPDF(
        semaine_debut=debut,
        semaine_fin=debut + timedelta(days=6),
        repas_par_jour={
            "Lundi": [
                {"type": "déjeuner", "recette": "Poulet rôti", "notes": ""},
                {"type": "dîner", "recette": "Soupe de légumes", "notes": ""},
            ],
            "Mardi": [
                {"type": "déjeuner", "recette": "Pâtes bolognaise", "notes": ""},
            ],
            "Mercredi": [
                {"type": "dîner", "recette": "Gratin dauphinois", "notes": ""},
            ],
        },
        total_repas=4,
    )


@pytest.fixture
def sample_courses_data():
    """Données de courses pour test."""
    return DonneesCoursesPDF(
        date_export=datetime.now(),
        articles=[
            {"nom": "Tomates", "quantite": 1, "categorie": "fruits_legumes"},
            {"nom": "Lait", "quantite": 2, "categorie": "produits_laitiers"},
            {"nom": "Pain", "quantite": 1, "categorie": "epicerie"},
        ],
        total_articles=3,
        par_categorie={
            "fruits_legumes": [
                {"nom": "Tomates", "quantite": 1, "unite": "kg", "urgent": False},
                {"nom": "Carottes", "quantite": 500, "unite": "g", "urgent": True},
            ],
            "produits_laitiers": [
                {"nom": "Lait", "quantite": 2, "unite": "L", "urgent": False},
            ],
            "epicerie": [
                {"nom": "Pain", "quantite": 1, "unite": "", "urgent": False},
            ],
        },
    )


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


class TestServiceExportPDFInit:
    """Tests d'initialisation du service."""

    def test_init_creates_styles(self, service):
        """Test que l'init crée les styles personnalisés."""
        assert service.styles is not None
        assert "TitreRecette" in [s for s in service.styles.byName.keys()]
        assert "SousTitre" in [s for s in service.styles.byName.keys()]
        assert "Etape" in [s for s in service.styles.byName.keys()]

    def test_configurer_styles(self, service):
        """Test que _configurer_styles ajoute les styles."""
        # Les styles doivent exister après init
        titre = service.styles["TitreRecette"]
        assert titre.fontSize == 24

        sous_titre = service.styles["SousTitre"]
        assert sous_titre.fontSize == 14

        etape = service.styles["Etape"]
        assert etape.fontSize == 11
        assert etape.leftIndent == 20


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION PDF RECETTE
# ═══════════════════════════════════════════════════════════


class TestGenererPDFRecette:
    """Tests de génération PDF de recettes."""

    def test_generer_pdf_recette_success(self, service, sample_recette_data):
        """Test génération PDF recette réussie."""
        result = service._generer_pdf_recette(sample_recette_data)

        assert isinstance(result, BytesIO)
        # Vérifier que le buffer contient des données
        result.seek(0)
        content = result.read()
        assert len(content) > 0
        # Vérifier signature PDF
        assert content[:4] == b"%PDF"

    def test_generer_pdf_recette_sans_description(self, service):
        """Test génération PDF recette sans description."""
        data = DonneesRecettePDF(
            id=2,
            nom="Recette simple",
            description="",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            difficulte="facile",
            ingredients=[{"nom": "Ingrédient", "quantite": 1, "unite": "u"}],
            etapes=["Faire cuire"],
            tags=[],
        )
        result = service._generer_pdf_recette(data)
        assert isinstance(result, BytesIO)

    def test_generer_pdf_recette_sans_tags(self, service):
        """Test génération PDF recette sans tags."""
        data = DonneesRecettePDF(
            id=3,
            nom="Recette sans tags",
            description="Description courte",
            temps_preparation=5,
            temps_cuisson=10,
            portions=2,
            difficulte="facile",
            ingredients=[],
            etapes=["Étape unique"],
            tags=[],
        )
        result = service._generer_pdf_recette(data)
        result.seek(0)
        assert result.read()[:4] == b"%PDF"

    def test_generer_pdf_recette_avec_tags(self, service, sample_recette_data):
        """Test génération PDF avec tags affichés."""
        result = service._generer_pdf_recette(sample_recette_data)
        assert isinstance(result, BytesIO)

    def test_generer_pdf_recette_ingredients_sans_quantite(self, service):
        """Test génération PDF avec ingrédients sans quantité."""
        data = DonneesRecettePDF(
            id=4,
            nom="Test ingrédients",
            ingredients=[
                {"nom": "Sel", "quantite": 0, "unite": ""},
                {"nom": "Poivre", "quantite": None, "unite": ""},
            ],
            etapes=["Assaisonner"],
        )
        result = service._generer_pdf_recette(data)
        assert isinstance(result, BytesIO)


class TestExporterRecette:
    """Tests de la méthode exporter_recette (avec DB mock)."""

    @patch("src.services.rapports.export.obtenir_contexte_db")
    def test_exporter_recette_success(self, mock_db_ctx, service):
        """Test export recette depuis DB."""
        # Setup mock DB
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        # Mock recette
        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.nom = "Test Recette"
        mock_recette.description = "Description test"
        mock_recette.temps_preparation = 20
        mock_recette.temps_cuisson = 30
        mock_recette.portions = 4
        mock_recette.difficulte = "facile"
        mock_recette.tags = ["tag1"]

        # Mock ingrédients
        mock_ri = MagicMock()
        mock_ri.ingredient.nom = "Ingrédient 1"
        mock_ri.quantite = 100
        mock_ri.unite = "g"
        mock_recette.ingredients = [mock_ri]

        # Mock étapes
        mock_etape = MagicMock()
        mock_etape.description = "Étape 1"
        mock_etape.ordre = 1
        mock_recette.etapes = [mock_etape]

        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_recette
        )

        result = service.exporter_recette(1)
        assert isinstance(result, BytesIO)

    @patch("src.services.rapports.export.obtenir_contexte_db")
    def test_exporter_recette_not_found(self, mock_db_ctx, service):
        """Test export recette non trouvée retourne None (décorateur)."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = (
            None
        )

        # Le décorateur @avec_gestion_erreurs capture l'erreur et retourne None
        result = service.exporter_recette(999)
        assert result is None

    @patch("src.services.rapports.export.obtenir_contexte_db")
    def test_exporter_recette_sans_ingredient_object(self, mock_db_ctx, service):
        """Test export recette avec ingrédient None."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.nom = "Test"
        mock_recette.description = None
        mock_recette.temps_preparation = None
        mock_recette.temps_cuisson = None
        mock_recette.portions = None
        mock_recette.difficulte = None
        mock_recette.tags = None

        # Ingrédient sans relation
        mock_ri = MagicMock()
        mock_ri.ingredient = None
        mock_ri.quantite = None
        mock_ri.unite = None
        mock_recette.ingredients = [mock_ri]
        mock_recette.etapes = []

        # Simule hasattr retournant False pour tags
        del mock_recette.tags

        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_recette
        )

        result = service.exporter_recette(1)
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION PDF PLANNING
# ═══════════════════════════════════════════════════════════


class TestGenererPDFPlanning:
    """Tests de génération PDF de planning."""

    def test_generer_pdf_planning_success(self, service, sample_planning_data):
        """Test génération PDF planning réussie."""
        result = service._generer_pdf_planning(sample_planning_data, "Planning Test")

        assert isinstance(result, BytesIO)
        result.seek(0)
        content = result.read()
        assert content[:4] == b"%PDF"

    def test_generer_pdf_planning_vide(self, service):
        """Test génération PDF planning vide."""
        data = DonneesPlanningPDF(
            semaine_debut=datetime.now(),
            semaine_fin=datetime.now() + timedelta(days=6),
            repas_par_jour={},
            total_repas=0,
        )
        result = service._generer_pdf_planning(data, "Planning Vide")
        assert isinstance(result, BytesIO)

    def test_generer_pdf_planning_tous_jours(self, service):
        """Test génération PDF avec tous les jours."""
        now = datetime.now()
        debut = now - timedelta(days=now.weekday())
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        repas_par_jour = {
            jour: [{"type": "déjeuner", "recette": f"Repas {jour}", "notes": ""}]
            for jour in jours
        }
        data = DonneesPlanningPDF(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            repas_par_jour=repas_par_jour,
            total_repas=7,
        )
        result = service._generer_pdf_planning(data, "Semaine complète")
        assert isinstance(result, BytesIO)


class TestExporterPlanningSemaine:
    """Tests de la méthode exporter_planning_semaine."""

    @patch("src.services.rapports.export.obtenir_contexte_db")
    def test_exporter_planning_semaine_success(self, mock_db_ctx, service):
        """Test export planning semaine depuis DB."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        # Mock planning
        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_planning.nom = "Planning Test"

        # Mock repas avec date dans la semaine
        now = datetime.now()
        debut = now - timedelta(days=now.weekday())
        mock_repas = MagicMock()
        mock_repas.date = debut.date()
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette.nom = "Test Recette"
        mock_repas.notes = ""
        mock_planning.repas = [mock_repas]

        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_planning
        )

        result = service.exporter_planning_semaine(1)
        assert isinstance(result, BytesIO)

    @patch("src.services.rapports.export.obtenir_contexte_db")
    def test_exporter_planning_semaine_not_found(self, mock_db_ctx, service):
        """Test export planning non trouvé retourne None (décorateur)."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = (
            None
        )

        # Le décorateur @avec_gestion_erreurs capture l'erreur et retourne None
        result = service.exporter_planning_semaine(999)
        assert result is None

    @patch("src.services.rapports.export.obtenir_contexte_db")
    def test_exporter_planning_semaine_avec_date(self, mock_db_ctx, service):
        """Test export planning avec date de début spécifiée."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_planning.nom = "Planning"
        mock_planning.repas = []

        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_planning
        )

        date_debut = datetime(2025, 1, 6)  # Un lundi
        result = service.exporter_planning_semaine(1, date_debut=date_debut)
        assert isinstance(result, BytesIO)

    @patch("src.services.rapports.export.obtenir_contexte_db")
    def test_exporter_planning_repas_hors_semaine(self, mock_db_ctx, service):
        """Test que les repas hors semaine sont ignorés."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_planning.nom = "Planning"

        # Repas avec date hors semaine
        mock_repas = MagicMock()
        mock_repas.date = (datetime.now() - timedelta(days=30)).date()
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette.nom = "Ancien repas"
        mock_repas.notes = ""
        mock_planning.repas = [mock_repas]

        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_planning
        )

        result = service.exporter_planning_semaine(1)
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION PDF COURSES
# ═══════════════════════════════════════════════════════════


class TestGenererPDFCourses:
    """Tests de génération PDF de courses."""

    def test_generer_pdf_courses_success(self, service, sample_courses_data):
        """Test génération PDF courses réussie."""
        result = service._generer_pdf_courses(sample_courses_data)

        assert isinstance(result, BytesIO)
        result.seek(0)
        content = result.read()
        assert content[:4] == b"%PDF"

    def test_generer_pdf_courses_vide(self, service):
        """Test génération PDF courses vide."""
        data = DonneesCoursesPDF(
            date_export=datetime.now(),
            articles=[],
            total_articles=0,
            par_categorie={},
        )
        result = service._generer_pdf_courses(data)
        assert isinstance(result, BytesIO)

    def test_generer_pdf_courses_toutes_categories(self, service):
        """Test génération PDF avec toutes les catégories."""
        categories = [
            "fruits_legumes",
            "viande",
            "poisson",
            "produits_laitiers",
            "epicerie",
            "surgeles",
            "boissons",
            "hygiene",
            "autre",
            "categorie_inconnue",
        ]
        par_categorie = {}
        for cat in categories:
            par_categorie[cat] = [
                {"nom": f"Article {cat}", "quantite": 1, "unite": "u", "urgent": False}
            ]

        data = DonneesCoursesPDF(
            date_export=datetime.now(),
            articles=[],
            total_articles=len(categories),
            par_categorie=par_categorie,
        )
        result = service._generer_pdf_courses(data)
        assert isinstance(result, BytesIO)

    def test_generer_pdf_courses_articles_urgents(self, service):
        """Test génération PDF avec articles urgents."""
        data = DonneesCoursesPDF(
            date_export=datetime.now(),
            articles=[],
            total_articles=2,
            par_categorie={
                "epicerie": [
                    {"nom": "Article urgent", "quantite": 1, "unite": "", "urgent": True},
                    {"nom": "Article normal", "quantite": 2, "unite": "kg", "urgent": False},
                ]
            },
        )
        result = service._generer_pdf_courses(data)
        assert isinstance(result, BytesIO)

    def test_generer_pdf_courses_sans_quantite(self, service):
        """Test génération PDF avec articles sans quantité."""
        data = DonneesCoursesPDF(
            date_export=datetime.now(),
            articles=[],
            total_articles=1,
            par_categorie={
                "autre": [{"nom": "Article", "quantite": 0, "unite": "", "urgent": False}]
            },
        )
        result = service._generer_pdf_courses(data)
        assert isinstance(result, BytesIO)


class TestExporterListeCourses:
    """Tests de la méthode exporter_liste_courses."""

    @patch.object(ServiceExportPDF, "_generer_pdf_courses")
    @patch("src.services.rapports.export.obtenir_contexte_db")
    @patch("src.services.rapports.export.ArticleCourses")
    def test_exporter_liste_courses_success(self, mock_article_class, mock_db_ctx, mock_gen_pdf, service):
        """Test export liste courses depuis DB."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        # Mock articles
        mock_article1 = MagicMock()
        mock_article1.nom = "Tomates"
        mock_article1.categorie = "fruits_legumes"
        mock_article1.quantite = 1
        mock_article1.unite = "kg"
        mock_article1.urgent = False

        mock_article2 = MagicMock()
        mock_article2.nom = "Lait"
        mock_article2.categorie = "produits_laitiers"
        mock_article2.quantite = 2
        mock_article2.unite = "L"
        mock_article2.urgent = True

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_article1,
            mock_article2,
        ]

        # Mock la génération PDF
        mock_gen_pdf.return_value = BytesIO(b"%PDF-test")

        result = service.exporter_liste_courses()
        assert isinstance(result, BytesIO)

    @patch.object(ServiceExportPDF, "_generer_pdf_courses")
    @patch("src.services.rapports.export.obtenir_contexte_db")
    @patch("src.services.rapports.export.ArticleCourses")
    def test_exporter_liste_courses_vide(self, mock_article_class, mock_db_ctx, mock_gen_pdf, service):
        """Test export liste courses vide."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
            []
        )

        # Mock la génération PDF
        mock_gen_pdf.return_value = BytesIO(b"%PDF-test")

        result = service.exporter_liste_courses()
        assert isinstance(result, BytesIO)

    @patch.object(ServiceExportPDF, "_generer_pdf_courses")
    @patch("src.services.rapports.export.obtenir_contexte_db")
    @patch("src.services.rapports.export.ArticleCourses")
    def test_exporter_liste_courses_article_sans_categorie(self, mock_article_class, mock_db_ctx, mock_gen_pdf, service):
        """Test export avec article sans catégorie."""
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        mock_article = MagicMock()
        mock_article.nom = "Article"
        mock_article.categorie = None
        mock_article.quantite = None
        mock_article.unite = None
        mock_article.urgent = None

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_article
        ]

        # Mock la génération PDF
        mock_gen_pdf.return_value = BytesIO(b"%PDF-test")

        result = service.exporter_liste_courses()
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY / SINGLETON
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests de la factory function."""

    def test_obtenir_service_export_pdf(self):
        """Test que la factory retourne une instance."""
        # Reset singleton
        import src.services.rapports.export as module

        module._service_export_pdf = None

        service = obtenir_service_export_pdf()
        assert isinstance(service, ServiceExportPDF)

    def test_obtenir_service_export_pdf_singleton(self):
        """Test que la factory retourne toujours la même instance."""
        service1 = obtenir_service_export_pdf()
        service2 = obtenir_service_export_pdf()
        assert service1 is service2


class TestAliasRetrocompatibilite:
    """Tests des alias de rétrocompatibilité."""

    def test_pdexportservice_alias(self):
        """Test alias PDFExportService."""
        assert PDFExportService is ServiceExportPDF

    def test_get_pdf_export_service_alias(self):
        """Test alias get_pdf_export_service."""
        assert get_pdf_export_service is obtenir_service_export_pdf

    def test_setup_custom_styles_alias(self, service):
        """Test alias _setup_custom_styles."""
        assert service._setup_custom_styles == service._configurer_styles


# ═══════════════════════════════════════════════════════════
# TESTS BORD / ERREURS
# ═══════════════════════════════════════════════════════════


class TestCasLimites:
    """Tests des cas limites et erreurs."""

    def test_generer_pdf_recette_nom_long(self, service):
        """Test génération avec nom très long."""
        data = DonneesRecettePDF(
            id=1,
            nom="A" * 200,
            description="B" * 500,
            ingredients=[{"nom": "C" * 100, "quantite": 1, "unite": "D" * 50}],
            etapes=["E" * 500],
        )
        result = service._generer_pdf_recette(data)
        assert isinstance(result, BytesIO)

    def test_generer_pdf_planning_nom_long(self, service):
        """Test génération planning avec nom long."""
        data = DonneesPlanningPDF(
            semaine_debut=datetime.now(),
            semaine_fin=datetime.now() + timedelta(days=6),
            repas_par_jour={
                "Lundi": [{"type": "déjeuner", "recette": "R" * 100, "notes": "N" * 200}]
            },
            total_repas=1,
        )
        result = service._generer_pdf_planning(data, "P" * 100)
        assert isinstance(result, BytesIO)

    def test_generer_pdf_courses_beaucoup_articles(self, service):
        """Test génération avec beaucoup d'articles."""
        par_categorie = {
            "epicerie": [
                {"nom": f"Article {i}", "quantite": i, "unite": "u", "urgent": i % 2 == 0}
                for i in range(50)
            ]
        }
        data = DonneesCoursesPDF(
            date_export=datetime.now(),
            articles=[],
            total_articles=50,
            par_categorie=par_categorie,
        )
        result = service._generer_pdf_courses(data)
        assert isinstance(result, BytesIO)
