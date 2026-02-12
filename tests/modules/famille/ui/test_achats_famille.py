"""
Tests pour src/domains/famille/ui/achats_famille/

Couverture ciblée: 80%
- helpers.py: get_all_purchases, get_purchases_by_category, get_stats, mark_as_bought, delete_purchase
- components.py: render_dashboard, render_liste_groupe, render_achat_card, render_add_form
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from contextlib import contextmanager

from tests.fixtures.ui_mocks import (
    create_streamlit_mock,
    create_ui_test_context,
    assert_streamlit_called,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_st():
    """Mock Streamlit configuré pour famille."""
    return create_ui_test_context("famille")


@pytest.fixture
def fake_purchase():
    """Crée un achat mockée."""
    purchase = MagicMock()
    purchase.id = 1
    purchase.nom = "Poussette"
    purchase.description = "Poussette compacte"
    purchase.categorie = "jules_equipement"
    purchase.priorite = "urgent"
    purchase.prix_estime = 200.0
    purchase.prix_reel = None
    purchase.achete = False
    purchase.date_achat = None
    purchase.suggere_par = "anne"
    purchase.url = None
    purchase.image_url = None
    purchase.magasin = "Amazon"
    purchase.cree_le = datetime.now()
    return purchase


@contextmanager
def mock_db_context(query_result=None):
    """Mock pour obtenir_contexte_db."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = query_result or []
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = query_result or []
    mock_db.query.return_value.filter_by.return_value.all.return_value = query_result or []
    mock_db.query.return_value.all.return_value = query_result or []
    mock_db.get.return_value = None
    
    @contextmanager
    def context():
        yield mock_db
    
    with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db", context):
        yield mock_db


# ═══════════════════════════════════════════════════════════
# TESTS IMPORTS
# ═══════════════════════════════════════════════════════════

class TestAchatsFamilleImports:
    """Tests d'import."""
    
    def test_import_module(self):
        """Vérifie l'import du module."""
        import src.domains.famille.ui.achats_famille
        assert hasattr(src.domains.famille.ui.achats_famille, "app")
    
    def test_import_helpers(self):
        """Vérifie l'import des helpers."""
        from src.domains.famille.ui.achats_famille.helpers import (
            get_all_purchases,
            get_purchases_by_category,
            get_purchases_by_groupe,
            get_stats,
            mark_as_bought,
            delete_purchase,
        )
        assert callable(get_all_purchases)
        assert callable(get_purchases_by_category)
        assert callable(get_purchases_by_groupe)
        assert callable(get_stats)
        assert callable(mark_as_bought)
        assert callable(delete_purchase)
    
    def test_import_components(self):
        """Vérifie l'import des composants."""
        from src.domains.famille.ui.achats_famille.components import (
            render_dashboard,
            render_liste_groupe,
            render_achat_card,
            render_add_form,
        )
        assert callable(render_dashboard)
        assert callable(render_liste_groupe)
        assert callable(render_achat_card)
        assert callable(render_add_form)


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS
# ═══════════════════════════════════════════════════════════

class TestGetAllPurchases:
    """Tests pour get_all_purchases()."""
    
    def test_get_all_purchases_empty(self):
        """Test sans achats."""
        from src.domains.famille.ui.achats_famille.helpers import get_all_purchases
        
        with mock_db_context([]):
            result = get_all_purchases()
        
        assert result == []
    
    def test_get_all_purchases_with_data(self, fake_purchase):
        """Test avec achats."""
        from src.domains.famille.ui.achats_famille.helpers import get_all_purchases
        
        with mock_db_context([fake_purchase]):
            result = get_all_purchases()
        
        assert len(result) == 1
        assert result[0].nom == "Poussette"
    
    def test_get_all_purchases_achete_true(self, fake_purchase):
        """Test avec achete=True."""
        from src.domains.famille.ui.achats_famille.helpers import get_all_purchases
        
        fake_purchase.achete = True
        
        with mock_db_context([fake_purchase]):
            result = get_all_purchases(achete=True)
        
        assert len(result) == 1
    
    def test_get_all_purchases_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.achats_famille.helpers import get_all_purchases
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            result = get_all_purchases()
        
        assert result == []


class TestGetPurchasesByCategory:
    """Tests pour get_purchases_by_category()."""
    
    def test_get_by_category_empty(self):
        """Test sans achats."""
        from src.domains.famille.ui.achats_famille.helpers import get_purchases_by_category
        
        with mock_db_context([]):
            result = get_purchases_by_category("jules_vetements")
        
        assert result == []
    
    def test_get_by_category_with_data(self, fake_purchase):
        """Test avec achats."""
        from src.domains.famille.ui.achats_famille.helpers import get_purchases_by_category
        
        with mock_db_context([fake_purchase]):
            result = get_purchases_by_category("jules_equipement")
        
        assert len(result) == 1
    
    def test_get_by_category_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.achats_famille.helpers import get_purchases_by_category
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            result = get_purchases_by_category("test")
        
        assert result == []


class TestGetPurchasesByGroupe:
    """Tests pour get_purchases_by_groupe()."""
    
    def test_get_by_groupe_jules(self, fake_purchase):
        """Test groupe jules."""
        from src.domains.famille.ui.achats_famille.helpers import get_purchases_by_groupe
        
        with mock_db_context([fake_purchase]):
            result = get_purchases_by_groupe("jules")
        
        assert len(result) == 1
    
    def test_get_by_groupe_nous(self):
        """Test groupe nous."""
        from src.domains.famille.ui.achats_famille.helpers import get_purchases_by_groupe
        
        purchase = MagicMock()
        purchase.categorie = "nous_jeux"
        
        with mock_db_context([purchase]):
            result = get_purchases_by_groupe("nous")
        
        assert len(result) == 1
    
    def test_get_by_groupe_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.achats_famille.helpers import get_purchases_by_groupe
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            result = get_purchases_by_groupe("jules")
        
        assert result == []


class TestGetStats:
    """Tests pour get_stats()."""
    
    def test_get_stats_empty(self):
        """Test statistiques vides."""
        from src.domains.famille.ui.achats_famille.helpers import get_stats
        
        with mock_db_context([]):
            result = get_stats()
        
        assert result["en_attente"] == 0
        assert result["total_estime"] == 0
    
    def test_get_stats_with_data(self, fake_purchase):
        """Test statistiques avec données."""
        from src.domains.famille.ui.achats_famille.helpers import get_stats
        
        # Mock de la session pour compter les achats
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.count.return_value = 2
        mock_db.query.return_value.filter_by.return_value.all.return_value = [fake_purchase]
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db", context):
            result = get_stats()
        
        assert isinstance(result, dict)
        assert "en_attente" in result
        assert "total_estime" in result
    
    def test_get_stats_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.achats_famille.helpers import get_stats
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            result = get_stats()
        
        assert result == {"en_attente": 0, "achetes": 0, "total_estime": 0, "total_depense": 0, "urgents": 0}


class TestMarkAsBought:
    """Tests pour mark_as_bought()."""
    
    def test_mark_as_bought_success(self, fake_purchase):
        """Test marquer comme acheté."""
        from src.domains.famille.ui.achats_famille.helpers import mark_as_bought
        
        mock_db = MagicMock()
        mock_db.get.return_value = fake_purchase
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db", context):
            mark_as_bought(1, prix_reel=180.0)
        
        assert fake_purchase.achete is True
        assert fake_purchase.prix_reel == 180.0
        mock_db.commit.assert_called_once()
    
    def test_mark_as_bought_not_found(self):
        """Test avec achat non trouvé."""
        from src.domains.famille.ui.achats_famille.helpers import mark_as_bought
        
        mock_db = MagicMock()
        mock_db.get.return_value = None
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db", context):
            mark_as_bought(999, prix_reel=100.0)
        
        mock_db.commit.assert_not_called()
    
    def test_mark_as_bought_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.achats_famille.helpers import mark_as_bought
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            # Ne doit pas lever d'exception
            mark_as_bought(1, prix_reel=50.0)


class TestDeletePurchase:
    """Tests pour delete_purchase()."""
    
    def test_delete_purchase_success(self, fake_purchase):
        """Test suppression réussie."""
        from src.domains.famille.ui.achats_famille.helpers import delete_purchase
        
        mock_db = MagicMock()
        mock_db.get.return_value = fake_purchase
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db", context):
            delete_purchase(1)
        
        mock_db.delete.assert_called_once_with(fake_purchase)
        mock_db.commit.assert_called_once()
    
    def test_delete_purchase_not_found(self):
        """Test avec achat non trouvé."""
        from src.domains.famille.ui.achats_famille.helpers import delete_purchase
        
        mock_db = MagicMock()
        mock_db.get.return_value = None
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db", context):
            delete_purchase(999)
        
        mock_db.delete.assert_not_called()
    
    def test_delete_purchase_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.achats_famille.helpers import delete_purchase
        
        with patch("src.domains.famille.ui.achats_famille.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            # Ne doit pas lever d'exception
            delete_purchase(1)


# ═══════════════════════════════════════════════════════════
# TESTS COMPONENTS
# ═══════════════════════════════════════════════════════════

class TestAchatsFamilleComponents:
    """Tests pour les composants UI."""
    
    def test_render_dashboard(self, mock_st):
        """Test render_dashboard."""
        from src.domains.famille.ui.achats_famille import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_stats", return_value={
                "en_attente": 5, "achetes": 10, "total_estime": 500, "total_depense": 400, "urgents": 2
            }):
                components.render_dashboard()
        
        mock_st.subheader.assert_called()
        assert mock_st.columns.called
        assert mock_st.metric.called
    
    def test_render_liste_groupe(self, mock_st, fake_purchase):
        """Test render_liste_groupe."""
        from src.domains.famille.ui.achats_famille import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_purchases_by_groupe", return_value=[fake_purchase]):
                with patch.object(components, "render_achat_card", MagicMock()):
                    components.render_liste_groupe("jules", "👶 Achats Jules")
        
        mock_st.subheader.assert_called()
    
    def test_render_achat_card(self, mock_st, fake_purchase):
        """Test render_achat_card."""
        from src.domains.famille.ui.achats_famille import components
        
        with patch.object(components, "st", mock_st):
            components.render_achat_card(fake_purchase)
        
        # Vérifie que les éléments UI sont créés
        assert mock_st.expander.called or mock_st.columns.called


class TestAchatsFamilleComponentsAdvanced:
    """Tests avancés pour achats_famille/components.py"""
    
    def test_render_add_form(self, mock_st):
        """Test render_add_form formulaire."""
        from src.domains.famille.ui.achats_famille import components
        
        mock_st.form_submit_button.return_value = False
        mock_st.selectbox.return_value = "jules_vetements"  # Pour éviter TypeError
        mock_st.number_input.return_value = 0.0
        mock_st.text_input.return_value = ""
        mock_st.text_area.return_value = ""
        
        with patch.object(components, "st", mock_st):
            components.render_add_form()
        
        mock_st.subheader.assert_called()
        mock_st.form.assert_called()
        mock_st.text_input.assert_called()
    
    def test_render_add_form_submit_success(self, mock_st):
        """Test render_add_form soumission valide."""
        from src.domains.famille.ui.achats_famille import components
        
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.side_effect = ["Poussette test", "", "Amazon", "https://amazon.com"]
        mock_st.selectbox.side_effect = ["jules_equipement", "urgent"]
        mock_st.number_input.return_value = 150.0
        mock_st.text_area.return_value = "Notes test"
        
        mock_db = MagicMock()
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "obtenir_contexte_db", context):
                components.render_add_form()
        
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        mock_st.success.assert_called()
    
    def test_render_add_form_submit_empty(self, mock_st):
        """Test render_add_form soumission sans nom."""
        from src.domains.famille.ui.achats_famille import components
        
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = ""  # Nom vide
        mock_st.selectbox.return_value = "jules_vetements"  # Pour éviter TypeError
        mock_st.number_input.return_value = 0.0
        mock_st.text_area.return_value = ""
        
        with patch.object(components, "st", mock_st):
            components.render_add_form()
        
        mock_st.error.assert_called()
    
    def test_render_historique_empty(self, mock_st):
        """Test render_historique sans achats."""
        from src.domains.famille.ui.achats_famille import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_all_purchases", return_value=[]):
                components.render_historique()
        
        mock_st.subheader.assert_called()
        mock_st.info.assert_called()
    
    def test_render_historique_with_data(self, mock_st, fake_purchase):
        """Test render_historique avec achats."""
        from src.domains.famille.ui.achats_famille import components
        
        fake_purchase.achete = True
        fake_purchase.date_achat = date.today()
        fake_purchase.prix_reel = 180.0
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_all_purchases", return_value=[fake_purchase]):
                components.render_historique()
        
        mock_st.subheader.assert_called()
        mock_st.metric.assert_called()
        assert mock_st.container.called
    
    def test_render_par_magasin_empty(self, mock_st):
        """Test render_par_magasin sans achats."""
        from src.domains.famille.ui.achats_famille import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_all_purchases", return_value=[]):
                components.render_par_magasin()
        
        mock_st.subheader.assert_called()
        mock_st.info.assert_called()
    
    def test_render_par_magasin_with_data(self, mock_st, fake_purchase):
        """Test render_par_magasin avec achats."""
        from src.domains.famille.ui.achats_famille import components
        
        fake_purchase.magasin = "Amazon"
        
        purchase_sans_magasin = MagicMock()
        purchase_sans_magasin.id = 2
        purchase_sans_magasin.nom = "Article sans magasin"
        purchase_sans_magasin.categorie = "jules_jouets"
        purchase_sans_magasin.priorite = "moyenne"
        purchase_sans_magasin.prix_estime = 25.0
        purchase_sans_magasin.magasin = None
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_all_purchases", return_value=[fake_purchase, purchase_sans_magasin]):
                with patch.object(components, "render_achat_card", MagicMock()):
                    components.render_par_magasin()
        
        mock_st.subheader.assert_called()
    
    def test_render_liste_groupe_empty(self, mock_st):
        """Test render_liste_groupe vide."""
        from src.domains.famille.ui.achats_famille import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_purchases_by_groupe", return_value=[]):
                components.render_liste_groupe("jules", "👶 Jules")
        
        mock_st.subheader.assert_called()
        mock_st.info.assert_called()
    
    def test_render_achat_card_complete(self, mock_st, fake_purchase):
        """Test render_achat_card avec toutes les infos."""
        from src.domains.famille.ui.achats_famille import components
        
        fake_purchase.url = "https://amazon.com"
        fake_purchase.image_url = "https://img.com/photo.jpg"
        fake_purchase.taille = "86"
        
        with patch.object(components, "st", mock_st):
            components.render_achat_card(fake_purchase)
        
        assert mock_st.container.called or mock_st.columns.called
    
    def test_render_achat_card_mark_bought(self, mock_st, fake_purchase):
        """Test render_achat_card bouton achat."""
        from src.domains.famille.ui.achats_famille import components
        
        mock_st.button.return_value = True  # Bouton cliqué
        mock_st.number_input.return_value = 150.0
        
        mock_db = MagicMock()
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "mark_as_bought", MagicMock()):
                components.render_achat_card(fake_purchase)


# ═══════════════════════════════════════════════════════════
# TESTS MODULE APP
# ═══════════════════════════════════════════════════════════

class TestAchatsFamilleApp:
    """Tests pour le point d'entrée app()."""
    
    def test_app_renders(self, mock_st):
        """Test que app() s'exécute."""
        from src.domains.famille.ui import achats_famille
        
        with patch.object(achats_famille, "st", mock_st):
            with patch.object(achats_famille, "get_stats", return_value={
                "en_attente": 0, "achetes": 0, "total_estime": 0, "total_depense": 0, "urgents": 0
            }):
                with patch.object(achats_famille, "render_dashboard", MagicMock()):
                    with patch.object(achats_famille, "render_liste_groupe", MagicMock()):
                        with patch.object(achats_famille, "render_par_magasin", MagicMock()):
                            with patch.object(achats_famille, "render_add_form", MagicMock()):
                                with patch.object(achats_famille, "render_historique", MagicMock()):
                                    achats_famille.app()
        
        mock_st.title.assert_called()
        assert mock_st.tabs.called

