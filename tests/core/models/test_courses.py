"""
Tests unitaires pour courses.py

Module: src.core.models.courses
"""

from src.core.models.courses import (
    ListeCourses,
    ArticleCourses,
    ModeleCourses,
    ArticleModele,
    CorrespondanceDrive,
)


class TestCourses:
    """Tests pour le module courses."""

    class TestListeCourses:
        """Tests pour la classe ListeCourses."""

        def test_listecourses_creation(self):
            liste = ListeCourses(nom="Courses semaine")
            assert liste.nom == "Courses semaine"

        def test_listecourses_tablename(self):
            assert ListeCourses.__tablename__ == "listes_courses"

    class TestArticleCourses:
        """Tests pour la classe ArticleCourses."""

        def test_articlecourses_creation(self):
            article = ArticleCourses(
                liste_id=1,
                ingredient_id=10,
                quantite_necessaire=2.0,
                priorite="normale",
            )
            assert article.liste_id == 1
            assert article.ingredient_id == 10
            assert article.quantite_necessaire == 2.0

        def test_articlecourses_tablename(self):
            assert ArticleCourses.__tablename__ == "articles_courses"

    class TestModeleCourses:
        """Tests pour la classe ModeleCourses."""

        def test_modelecourses_creation(self):
            modele = ModeleCourses(
                nom="Courses hebdo",
                description="Liste standard de la semaine",
            )
            assert modele.nom == "Courses hebdo"

        def test_modelecourses_tablename(self):
            assert ModeleCourses.__tablename__ == "modeles_courses"

    class TestArticleModele:
        """Tests pour la classe ArticleModele."""

        def test_articlemodele_creation(self):
            art = ArticleModele(
                modele_id=1,
                nom_article="Lait",
                quantite=2.0,
                unite="L",
                rayon_magasin="Frais",
                priorite="normale",
                ordre=1,
            )
            assert art.nom_article == "Lait"
            assert art.quantite == 2.0
            assert art.unite == "L"

        def test_articlemodele_tablename(self):
            assert ArticleModele.__tablename__ == "articles_modeles"

    class TestCorrespondanceDrive:
        """Tests pour la classe CorrespondanceDrive."""

        def test_correspondance_drive_creation(self):
            correspondance = CorrespondanceDrive(
                nom_article="Lessive",
                produit_drive_id="prod-123",
                produit_drive_nom="Lessive Carrefour",
                quantite_par_defaut=1.0,
            )
            assert correspondance.nom_article == "Lessive"
            assert correspondance.produit_drive_id == "prod-123"
            assert correspondance.quantite_par_defaut == 1.0

        def test_correspondance_drive_tablename(self):
            assert CorrespondanceDrive.__tablename__ == "correspondances_drive"
