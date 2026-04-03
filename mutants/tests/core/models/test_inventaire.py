"""
Tests unitaires pour inventaire.py

Module: src.core.models.inventaire
"""

from src.core.models.inventaire import ArticleInventaire, HistoriqueInventaire


class TestInventaire:
    """Tests pour le module inventaire."""

    class TestArticleInventaire:
        """Tests pour la classe ArticleInventaire."""

        def test_articleinventaire_creation(self):
            article = ArticleInventaire(
                ingredient_id=1,
                quantite=5.0,
                quantite_min=2.0,
                emplacement="Frigo",
            )
            assert article.ingredient_id == 1
            assert article.quantite == 5.0
            assert article.quantite_min == 2.0
            assert article.emplacement == "Frigo"

        def test_articleinventaire_tablename(self):
            assert ArticleInventaire.__tablename__ == "inventaire"

        def test_articleinventaire_code_barres(self):
            article = ArticleInventaire(
                ingredient_id=2,
                quantite=1.0,
                quantite_min=1.0,
                code_barres="3017620422003",
            )
            assert article.code_barres == "3017620422003"

    class TestHistoriqueInventaire:
        """Tests pour la classe HistoriqueInventaire."""

        def test_historiqueinventaire_creation(self):
            hist = HistoriqueInventaire(
                article_id=1,
                ingredient_id=1,
                type_modification="ajout",
                quantite_avant=0.0,
                quantite_apres=5.0,
            )
            assert hist.type_modification == "ajout"
            assert hist.quantite_avant == 0.0
            assert hist.quantite_apres == 5.0

        def test_historiqueinventaire_tablename(self):
            assert HistoriqueInventaire.__tablename__ == "historique_inventaire"
