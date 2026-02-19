"""
Tests pour src/modules/cuisine/courses/historique.py

Couverture complète des fonctions UI historique courses.
"""

from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


def make_db_context(mock_session):
    """Crée un contexte DB mock."""

    @contextmanager
    def db_context():
        yield mock_session

    return db_context


def make_db_context_error(error):
    """Crée un contexte DB qui lève une erreur."""

    @contextmanager
    def db_context():
        raise error
        yield

    return db_context


class TestRenderHistorique:
    """Tests pour afficher_historique()."""

    def test_import(self):
        """Test import réussi."""
        from src.modules.cuisine.courses.historique import afficher_historique

        assert afficher_historique is not None

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.obtenir_contexte_db")
    def test_render_historique_no_articles(self, mock_db, mock_st, mock_service):
        """Test avec aucun article acheté."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter.return_value.all.return_value = []
        mock_db.return_value = make_db_context(mock_session)()

        afficher_historique()

        mock_st.subheader.assert_called()
        mock_st.info.assert_called_with("Aucun achat pendant cette période")

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.historique.pd")
    def test_render_historique_with_articles(self, mock_pd, mock_db, mock_st, mock_service):
        """Test avec articles achetés."""
        from src.modules.cuisine.courses.historique import afficher_historique

        # Ensure columns returns enough mocks
        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],  # date inputs
            [MagicMock(), MagicMock(), MagicMock()],  # metrics
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        # Créer article mock
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Tomates"
        mock_ingredient.unite = "kg"

        mock_article = MagicMock()
        mock_article.ingredient = mock_ingredient
        mock_article.quantite_necessaire = 2.0
        mock_article.priorite = "haute"
        mock_article.rayon_magasin = "Fruits et légumes"
        mock_article.achete_le = datetime.now()
        mock_article.suggere_par_ia = False

        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter.return_value.all.return_value = [
            mock_article
        ]
        mock_db.return_value = make_db_context(mock_session)()

        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.to_csv.return_value = "test,csv"
        mock_pd.DataFrame.return_value = mock_df

        afficher_historique()

        mock_st.metric.assert_called()
        mock_st.dataframe.assert_called()
        mock_st.download_button.assert_called()

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.obtenir_contexte_db")
    def test_render_historique_with_multiple_rayons(self, mock_db, mock_st, mock_service):
        """Test statistiques multiples rayons."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],  # date inputs
            [MagicMock(), MagicMock(), MagicMock()],  # metrics
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Lait"
        mock_ingredient.unite = "l"

        articles = []
        for i, rayon in enumerate(["Crèmerie", "Boulangerie", "Crèmerie"]):
            art = MagicMock()
            art.ingredient = mock_ingredient
            art.quantite_necessaire = 1.0
            art.priorite = "moyenne" if i != 0 else "haute"
            art.rayon_magasin = rayon
            art.achete_le = datetime.now()
            art.suggere_par_ia = i == 0
            articles.append(art)

        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter.return_value.all.return_value = articles
        mock_db.return_value = make_db_context(mock_session)()

        afficher_historique()

        # Verify metrics called with stats
        assert mock_st.metric.call_count >= 3

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.historique.logger")
    def test_render_historique_exception(self, mock_logger, mock_db, mock_st, mock_service):
        """Test gestion erreur."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]
        mock_db.return_value = make_db_context_error(Exception("DB error"))()

        afficher_historique()

        mock_st.error.assert_called()
        mock_logger.error.assert_called()

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.obtenir_contexte_db")
    def test_render_historique_ia_badge(self, mock_db, mock_st, mock_service):
        """Test badge IA pour suggestions."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],  # date
            [MagicMock(), MagicMock(), MagicMock()],  # metrics
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=7),
            datetime.now().date(),
        ]

        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Pommes"
        mock_ingredient.unite = "kg"

        mock_article = MagicMock()
        mock_article.ingredient = mock_ingredient
        mock_article.quantite_necessaire = 1.5
        mock_article.priorite = "basse"
        mock_article.rayon_magasin = "Fruits"
        mock_article.achete_le = datetime.now()
        mock_article.suggere_par_ia = True  # IA suggestion

        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter.return_value.all.return_value = [
            mock_article
        ]
        mock_db.return_value = make_db_context(mock_session)()

        afficher_historique()

        mock_st.dataframe.assert_called()

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.obtenir_contexte_db")
    def test_render_historique_empty_df(self, mock_db, mock_st, mock_service):
        """Test avec DataFrame vide (cas edge)."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=1),
            datetime.now().date(),
        ]

        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter.return_value.all.return_value = []
        mock_db.return_value = make_db_context(mock_session)()

        afficher_historique()

        mock_st.info.assert_called_with("Aucun achat pendant cette période")

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.obtenir_contexte_db")
    def test_render_historique_null_ingredient(self, mock_db, mock_st, mock_service):
        """Test avec ingrédient null."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],  # date
            [MagicMock(), MagicMock(), MagicMock()],  # metrics
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_article = MagicMock()
        mock_article.ingredient = None  # Null ingredient
        mock_article.quantite_necessaire = 1.0
        mock_article.priorite = "moyenne"
        mock_article.rayon_magasin = None  # Null rayon
        mock_article.achete_le = None  # Null date
        mock_article.suggere_par_ia = False

        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter.return_value.all.return_value = [
            mock_article
        ]
        mock_db.return_value = make_db_context(mock_session)()

        afficher_historique()

        mock_st.dataframe.assert_called()

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.obtenir_contexte_db")
    def test_render_historique_unknown_priority(self, mock_db, mock_st, mock_service):
        """Test avec priorité inconnue."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],
            [MagicMock(), MagicMock(), MagicMock()],
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Test"
        mock_ingredient.unite = "kg"

        mock_article = MagicMock()
        mock_article.ingredient = mock_ingredient
        mock_article.quantite_necessaire = 1.0
        mock_article.priorite = "inconnu"  # Unknown priority
        mock_article.rayon_magasin = "Autre"
        mock_article.achete_le = datetime.now()
        mock_article.suggere_par_ia = False

        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter.return_value.all.return_value = [
            mock_article
        ]
        mock_db.return_value = make_db_context(mock_session)()

        afficher_historique()

        mock_st.dataframe.assert_called()


class TestHistoriqueModule:
    """Tests module-level."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from src.modules.cuisine.courses import historique

        assert "afficher_historique" in historique.__all__
