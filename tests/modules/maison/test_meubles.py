"""
Tests pour src/modules/maison/meubles.py

Module Meubles - Wishlist d'achats par pièce avec budget.
"""

from contextlib import contextmanager
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════


class TestMeublesImport:
    """Tests d'import du module meubles"""

    def test_import_module(self):
        """Test que le module s'importe correctement"""
        from src.modules.maison import meubles

        assert meubles is not None

    def test_import_constantes(self):
        """Test que les constantes sont définies"""
        from src.modules.maison.meubles import (
            PIECES_LABELS,
            PRIORITES_LABELS,
            STATUTS_LABELS,
        )

        assert isinstance(PIECES_LABELS, dict)
        assert isinstance(STATUTS_LABELS, dict)
        assert isinstance(PRIORITES_LABELS, dict)
        assert len(PIECES_LABELS) > 0
        assert len(STATUTS_LABELS) > 0
        assert len(PRIORITES_LABELS) > 0

    def test_import_crud_functions(self):
        """Test que les fonctions CRUD sont importables"""
        from src.modules.maison.meubles import (
            create_meuble,
            delete_meuble,
            get_all_meubles,
            get_budget_resume,
            get_meuble_by_id,
            update_meuble,
        )

        assert callable(get_all_meubles)
        assert callable(get_meuble_by_id)
        assert callable(create_meuble)
        assert callable(update_meuble)
        assert callable(delete_meuble)
        assert callable(get_budget_resume)

    def test_import_app(self):
        """Test que la fonction app est importable"""
        from src.modules.maison.meubles import app

        assert callable(app)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_meuble():
    """Fixture mock d'un meuble"""
    meuble = MagicMock()
    meuble.id = 1
    meuble.nom = "Table basse"
    meuble.piece = "salon"
    meuble.description = "Table en bois moderne"
    meuble.priorite = "normale"
    meuble.statut = "souhaite"
    meuble.prix_estime = Decimal("150.00")
    meuble.prix_max = Decimal("200.00")
    meuble.magasin = "IKEA"
    meuble.url = "https://ikea.com/table"
    meuble.dimensions = "120x60x45 cm"
    return meuble


@pytest.fixture
def mock_meuble_minimal():
    """Fixture mock d'un meuble minimal (sans optionnels)"""
    meuble = MagicMock()
    meuble.id = 2
    meuble.nom = "Chaise"
    meuble.piece = "cuisine"
    meuble.description = None
    meuble.priorite = "basse"
    meuble.statut = "recherche"
    meuble.prix_estime = None
    meuble.prix_max = None
    meuble.magasin = None
    meuble.url = None
    meuble.dimensions = None
    return meuble


@pytest.fixture
def mock_db_session():
    """Fixture mock de session DB"""
    session = MagicMock()
    session.query.return_value = session
    session.filter.return_value = session
    session.order_by.return_value = session
    session.all.return_value = []
    session.first.return_value = None
    return session


@contextmanager
def mock_db_context(session):
    """Context manager pour mocker obtenir_contexte_db"""
    yield session


# ═══════════════════════════════════════════════════════════
# TESTS CRUD
# ═══════════════════════════════════════════════════════════


class TestMeublesCrud:
    """Tests des fonctions CRUD"""

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_get_all_meubles_sans_filtre(self, mock_ctx, mock_meuble):
        """Test récupération de tous les meubles sans filtre"""
        from src.modules.maison.meubles import get_all_meubles

        mock_session = MagicMock()
        mock_session.query.return_value.order_by.return_value.all.return_value = [mock_meuble]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = get_all_meubles()

        assert len(result) == 1
        assert result[0].nom == "Table basse"

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_get_all_meubles_avec_filtre_statut(self, mock_ctx, mock_meuble):
        """Test récupération avec filtre statut"""
        from src.modules.maison.meubles import get_all_meubles

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value.all.return_value = [mock_meuble]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = get_all_meubles(filtre_statut="souhaite")

        assert len(result) == 1
        mock_query.filter.assert_called()

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_get_all_meubles_avec_filtre_piece(self, mock_ctx, mock_meuble):
        """Test récupération avec filtre pièce"""
        from src.modules.maison.meubles import get_all_meubles

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value.all.return_value = [mock_meuble]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = get_all_meubles(filtre_piece="salon")

        assert len(result) == 1

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_get_meuble_by_id_existant(self, mock_ctx, mock_meuble):
        """Test récupération d'un meuble existant par ID"""
        from src.modules.maison.meubles import get_meuble_by_id

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_meuble
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = get_meuble_by_id(1)

        assert result is not None
        assert result.id == 1

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_get_meuble_by_id_inexistant(self, mock_ctx):
        """Test récupération d'un meuble inexistant"""
        from src.modules.maison.meubles import get_meuble_by_id

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = get_meuble_by_id(999)

        assert result is None

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_create_meuble(self, mock_ctx):
        """Test création d'un nouveau meuble"""
        from src.modules.maison.meubles import create_meuble

        mock_session = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        data = {
            "nom": "Nouvelle étagère",
            "piece": "bureau",
            "priorite": "haute",
            "statut": "souhaite",
        }

        create_meuble(data)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_update_meuble_existant(self, mock_ctx, mock_meuble):
        """Test mise à jour d'un meuble existant"""
        from src.modules.maison.meubles import update_meuble

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_meuble
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        data = {"nom": "Table basse modifiée", "statut": "achete"}

        result = update_meuble(1, data)

        assert result is not None
        mock_session.commit.assert_called_once()

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_update_meuble_inexistant(self, mock_ctx):
        """Test mise à jour d'un meuble inexistant"""
        from src.modules.maison.meubles import update_meuble

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = update_meuble(999, {"nom": "Test"})

        assert result is None

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_delete_meuble_existant(self, mock_ctx, mock_meuble):
        """Test suppression d'un meuble existant"""
        from src.modules.maison.meubles import delete_meuble

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_meuble
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = delete_meuble(1)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_meuble)
        mock_session.commit.assert_called_once()

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_delete_meuble_inexistant(self, mock_ctx):
        """Test suppression d'un meuble inexistant"""
        from src.modules.maison.meubles import delete_meuble

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = delete_meuble(999)

        assert result is False

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_get_budget_resume(self, mock_ctx, mock_meuble, mock_meuble_minimal):
        """Test calcul du résumé budget"""
        from src.modules.maison.meubles import get_budget_resume

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [
            mock_meuble,
            mock_meuble_minimal,
        ]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = get_budget_resume()

        assert "par_piece" in result
        assert "total_estime" in result
        assert "total_max" in result
        assert "nb_articles" in result
        assert result["nb_articles"] == 2

    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_get_budget_resume_vide(self, mock_ctx):
        """Test résumé budget sans meubles"""
        from src.modules.maison.meubles import get_budget_resume

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = get_budget_resume()

        assert result["nb_articles"] == 0
        assert result["total_estime"] == 0
        assert result["total_max"] == 0


# ═══════════════════════════════════════════════════════════
# TESTS UI
# ═══════════════════════════════════════════════════════════


class TestMeublesUI:
    """Tests des fonctions d'affichage UI"""

    @patch("src.modules.maison.meubles.st")
    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_render_formulaire_nouveau(self, mock_ctx, mock_st):
        """Test formulaire d'ajout nouveau meuble"""
        from src.modules.maison.meubles import afficher_formulaire

        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.form_submit_button.return_value = False

        afficher_formulaire(None)

        mock_st.form.assert_called_once()
        mock_st.text_input.assert_called()

    @patch("src.modules.maison.meubles.st")
    @patch("src.modules.maison.meubles.obtenir_contexte_db")
    def test_render_formulaire_edition(self, mock_ctx, mock_st, mock_meuble):
        """Test formulaire d'édition meuble existant"""
        from src.modules.maison.meubles import afficher_formulaire

        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.form_submit_button.return_value = False

        afficher_formulaire(mock_meuble)

        mock_st.form.assert_called_once()

    @patch("src.modules.maison.meubles.st")
    def test_render_meuble_card(self, mock_st, mock_meuble):
        """Test affichage card meuble"""
        from src.modules.maison.meubles import afficher_meuble_card

        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        # Premier appel: 3 colonnes pour la card, deuxième appel: 2 colonnes pour les boutons
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_col_edit, mock_col_del = MagicMock(), MagicMock()
        for col in [mock_col1, mock_col2, mock_col3, mock_col_edit, mock_col_del]:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.side_effect = [
            [mock_col1, mock_col2, mock_col3],  # Premier appel avec [3, 1, 1]
            [mock_col_edit, mock_col_del],  # Deuxième appel avec 2
        ]
        mock_st.button.return_value = False

        afficher_meuble_card(mock_meuble)

        mock_st.container.assert_called_once()
        mock_st.markdown.assert_called()

    @patch("src.modules.maison.meubles.st")
    def test_render_meuble_card_description_longue(self, mock_st, mock_meuble):
        """Test card avec description longue (tronquée)"""
        from src.modules.maison.meubles import afficher_meuble_card

        mock_meuble.description = "A" * 150  # Description > 100 chars

        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_col_edit, mock_col_del = MagicMock(), MagicMock()
        for col in [mock_col1, mock_col2, mock_col3, mock_col_edit, mock_col_del]:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.side_effect = [
            [mock_col1, mock_col2, mock_col3],
            [mock_col_edit, mock_col_del],
        ]
        mock_st.button.return_value = False

        afficher_meuble_card(mock_meuble)

        mock_st.container.assert_called()

    @patch("src.modules.maison.meubles.get_budget_resume")
    @patch("src.modules.maison.meubles.st")
    def test_render_budget_summary(self, mock_st, mock_budget):
        """Test affichage résumé budget"""
        from src.modules.maison.meubles import afficher_budget_summary

        mock_budget.return_value = {
            "nb_articles": 5,
            "total_estime": 1000.0,
            "total_max": 1500.0,
            "par_piece": {"salon": {"count": 2, "total_estime": 500, "total_max": 700}},
        }
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

        afficher_budget_summary()

        mock_st.subheader.assert_called()
        mock_st.metric.assert_called()

    @patch("src.modules.maison.meubles.get_all_meubles")
    @patch("src.modules.maison.meubles.st")
    def test_render_vue_par_piece_vide(self, mock_st, mock_get_all):
        """Test vue par pièce sans meubles"""
        from src.modules.maison.meubles import afficher_vue_par_piece

        mock_get_all.return_value = []

        afficher_vue_par_piece()

        mock_st.info.assert_called_once()

    @patch("src.modules.maison.meubles.afficher_meuble_card")
    @patch("src.modules.maison.meubles.get_all_meubles")
    @patch("src.modules.maison.meubles.st")
    def test_render_vue_par_piece_avec_meubles(
        self, mock_st, mock_get_all, mock_render_card, mock_meuble
    ):
        """Test vue par pièce avec meubles"""
        from src.modules.maison.meubles import afficher_vue_par_piece

        mock_get_all.return_value = [mock_meuble]
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        afficher_vue_par_piece()

        mock_st.expander.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS ONGLETS
# ═══════════════════════════════════════════════════════════


class TestMeublesOnglets:
    """Tests des onglets"""

    @patch("src.modules.maison.meubles.afficher_meuble_card")
    @patch("src.modules.maison.meubles.get_all_meubles")
    @patch("src.modules.maison.meubles.st")
    def test_render_onglet_wishlist_vide(self, mock_st, mock_get_all, mock_render_card):
        """Test onglet wishlist vide"""
        from src.modules.maison.meubles import afficher_onglet_wishlist

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.selectbox.return_value = ""
        mock_get_all.return_value = []

        afficher_onglet_wishlist()

        mock_st.info.assert_called()

    @patch("src.modules.maison.meubles.afficher_meuble_card")
    @patch("src.modules.maison.meubles.get_all_meubles")
    @patch("src.modules.maison.meubles.st")
    def test_render_onglet_wishlist_avec_filtres(
        self, mock_st, mock_get_all, mock_render_card, mock_meuble
    ):
        """Test onglet wishlist avec filtres et résultats"""
        from src.modules.maison.meubles import afficher_onglet_wishlist

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.selectbox.side_effect = ["souhaite", "salon"]
        mock_get_all.return_value = [mock_meuble]

        afficher_onglet_wishlist()

        mock_st.caption.assert_called()
        mock_render_card.assert_called_once_with(mock_meuble)

    @patch("src.modules.maison.meubles.afficher_formulaire")
    @patch("src.modules.maison.meubles.st")
    def test_render_onglet_ajouter(self, mock_st, mock_render_form):
        """Test onglet ajout"""
        from src.modules.maison.meubles import afficher_onglet_ajouter

        afficher_onglet_ajouter()

        mock_st.subheader.assert_called_once()
        mock_render_form.assert_called_once_with(None)

    @patch("src.modules.maison.meubles.afficher_vue_par_piece")
    @patch("src.modules.maison.meubles.afficher_budget_summary")
    @patch("src.modules.maison.meubles.st")
    def test_render_onglet_budget(self, mock_st, mock_summary, mock_vue):
        """Test onglet budget"""
        from src.modules.maison.meubles import afficher_onglet_budget

        afficher_onglet_budget()

        mock_summary.assert_called_once()
        mock_st.divider.assert_called_once()
        mock_vue.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS APP (POINT D'ENTRÉE)
# ═══════════════════════════════════════════════════════════


class TestMeublesApp:
    """Tests de la fonction app() - point d'entrée"""

    @patch("src.modules.maison.meubles.afficher_onglet_budget")
    @patch("src.modules.maison.meubles.afficher_onglet_ajouter")
    @patch("src.modules.maison.meubles.afficher_onglet_wishlist")
    @patch("src.modules.maison.meubles.st")
    def test_app_affichage_normal(self, mock_st, mock_wishlist, mock_ajouter, mock_budget):
        """Test app en mode normal (pas d'édition)"""
        from src.modules.maison.meubles import app

        mock_st.session_state = {}
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]

        app()

        mock_st.title.assert_called_once()
        mock_st.caption.assert_called_once()
        mock_st.tabs.assert_called_once()

    @patch("src.modules.maison.meubles.afficher_formulaire")
    @patch("src.modules.maison.meubles.get_meuble_by_id")
    @patch("src.modules.maison.meubles.st")
    def test_app_mode_edition(self, mock_st, mock_get_by_id, mock_formulaire, mock_meuble):
        """Test app en mode édition"""
        from src.modules.maison.meubles import app

        mock_st.session_state = {"meubles__edit_id": 1}
        mock_get_by_id.return_value = mock_meuble
        mock_st.button.return_value = False

        app()

        mock_st.title.assert_called()
        mock_st.subheader.assert_called()
        mock_formulaire.assert_called_once_with(mock_meuble)

    @patch("src.modules.maison.meubles.afficher_onglet_budget")
    @patch("src.modules.maison.meubles.afficher_onglet_ajouter")
    @patch("src.modules.maison.meubles.afficher_onglet_wishlist")
    @patch("src.modules.maison.meubles.get_meuble_by_id")
    @patch("src.modules.maison.meubles.st")
    def test_app_mode_edition_meuble_inexistant(
        self, mock_st, mock_get_by_id, mock_wishlist, mock_ajouter, mock_budget
    ):
        """Test app mode édition avec meuble supprimé entre-temps"""
        from src.modules.maison.meubles import app

        mock_st.session_state = {"meubles__edit_id": 999}
        mock_get_by_id.return_value = None
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]

        app()

        # Devrait continuer vers l'affichage normal
        mock_st.tabs.assert_called()

    @patch("src.modules.maison.meubles.afficher_formulaire")
    @patch("src.modules.maison.meubles.get_meuble_by_id")
    @patch("src.modules.maison.meubles.st")
    def test_app_annulation_edition(self, mock_st, mock_get_by_id, mock_formulaire, mock_meuble):
        """Test annulation de l'édition"""
        from src.modules.maison.meubles import app

        # Utiliser un vrai dict pour session_state afin que del fonctionne (namespace meubles__)
        session_state = {"meubles__edit_id": 1}
        mock_st.session_state = session_state
        mock_get_by_id.return_value = mock_meuble
        mock_st.button.return_value = True  # Clic sur "Annuler"
        # Simuler que rerun() arrête l'exécution
        mock_st.rerun.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            app()

        # Vérifier que meubles__edit_id a été supprimé avant le rerun
        assert "meubles__edit_id" not in session_state


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestMeublesConstantes:
    """Tests de validation des constantes"""

    def test_pieces_labels_contient_principales(self):
        """Test que les pièces principales sont définies"""
        from src.modules.maison.meubles import PIECES_LABELS

        pieces_attendues = ["salon", "cuisine", "chambre_parentale", "bureau"]
        for piece in pieces_attendues:
            assert piece in PIECES_LABELS

    def test_statuts_labels_workflow(self):
        """Test que tous les statuts du workflow sont présents"""
        from src.modules.maison.meubles import STATUTS_LABELS

        statuts_attendus = ["souhaite", "recherche", "trouve", "commande", "achete", "annule"]
        for statut in statuts_attendus:
            assert statut in STATUTS_LABELS

    def test_priorites_labels_complets(self):
        """Test que toutes les priorités sont définies"""
        from src.modules.maison.meubles import PRIORITES_LABELS

        priorites_attendues = ["urgent", "haute", "normale", "basse", "plus_tard"]
        for priorite in priorites_attendues:
            assert priorite in PRIORITES_LABELS

    def test_labels_contiennent_emoji(self):
        """Test que les labels contiennent des emojis"""
        from src.modules.maison.meubles import (
            PIECES_LABELS,
            PRIORITES_LABELS,
            STATUTS_LABELS,
        )

        # Au moins un label de chaque type doit contenir un emoji
        assert any("🛋️" in v or "🍳" in v for v in PIECES_LABELS.values())
        assert any("💭" in v or "✅" in v for v in STATUTS_LABELS.values())
        assert any("🔴" in v or "🟢" in v for v in PRIORITES_LABELS.values())
