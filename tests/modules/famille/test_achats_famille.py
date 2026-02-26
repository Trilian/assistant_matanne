"""
Tests pour src/modules/famille/achats_famille

Tests complets avec mocking de Streamlit et des services DB.
"""

from datetime import date
from unittest.mock import MagicMock, patch

# ============================================================
# Tests d'import
# ============================================================


class TestImports:
    """Tests d'import du module achats_famille"""

    def test_import_module_principal(self):
        """Vérifie que le module principal peut être importé"""
        with patch("src.modules.famille.achats_famille.st"):
            import src.modules.famille.achats_famille as achats_famille

            assert achats_famille is not None

    def test_import_app_function(self):
        """Vérifie que la fonction app() est exportée"""
        with patch("src.modules.famille.achats_famille.st"):
            from src.modules.famille.achats_famille import app

            assert callable(app)

    def test_import_utils_functions(self):
        """Vérifie l'export des fonctions utilitaires"""
        with patch("src.modules.famille.achats_famille.st"):
            from src.modules.famille.achats_famille import (
                delete_purchase,
                get_all_purchases,
                get_purchases_by_category,
                get_purchases_by_groupe,
                get_stats,
                mark_as_bought,
            )

            assert callable(get_all_purchases)
            assert callable(get_purchases_by_category)
            assert callable(get_purchases_by_groupe)
            assert callable(get_stats)
            assert callable(mark_as_bought)
            assert callable(delete_purchase)

    def test_import_ui_functions(self):
        """Vérifie l'export des fonctions UI"""
        with patch("src.modules.famille.achats_famille.st"):
            from src.modules.famille.achats_famille import (
                afficher_achat_card,
                afficher_add_form,
                afficher_dashboard,
                afficher_historique,
                afficher_liste_groupe,
                afficher_par_magasin,
            )

            assert callable(afficher_dashboard)
            assert callable(afficher_liste_groupe)
            assert callable(afficher_achat_card)
            assert callable(afficher_add_form)
            assert callable(afficher_historique)
            assert callable(afficher_par_magasin)

    def test_module_all_exports(self):
        """Vérifie que __all__ est défini correctement"""
        with patch("src.modules.famille.achats_famille.st"):
            from src.modules.famille import achats_famille

            assert hasattr(achats_famille, "__all__")
            assert "app" in achats_famille.__all__
            assert "get_all_purchases" in achats_famille.__all__
            assert "afficher_dashboard" in achats_famille.__all__


# ============================================================
# Tests de la fonction app()
# ============================================================


class TestAppFunction:
    """Tests pour la fonction point d'entrée app()"""

    @patch("src.modules.famille.achats_famille.st")
    @patch("src.modules.famille.achats_famille.get_stats")
    @patch("src.modules.famille.achats_famille.afficher_dashboard")
    @patch("src.modules.famille.achats_famille.afficher_liste_groupe")
    @patch("src.modules.famille.achats_famille.afficher_par_magasin")
    @patch("src.modules.famille.achats_famille.afficher_add_form")
    @patch("src.modules.famille.achats_famille.afficher_historique")
    def test_app_affiche_titre(
        self,
        mock_render_historique,
        mock_render_add_form,
        mock_render_par_magasin,
        mock_render_liste_groupe,
        mock_render_dashboard,
        mock_get_stats,
        mock_st,
    ):
        """Vérifie que app() affiche le titre principal"""
        mock_get_stats.return_value = {"en_attente": 5, "total_estime": 150.0}
        mock_st.tabs.return_value = [MagicMock() for _ in range(6)]

        from src.modules.famille.achats_famille import app

        app()

        mock_st.title.assert_called_once_with("🛍️ Achats Famille")

    @patch("src.modules.famille.achats_famille.st")
    @patch("src.modules.famille.achats_famille.get_stats")
    @patch("src.modules.famille.achats_famille.afficher_dashboard")
    @patch("src.modules.famille.achats_famille.afficher_liste_groupe")
    @patch("src.modules.famille.achats_famille.afficher_par_magasin")
    @patch("src.modules.famille.achats_famille.afficher_add_form")
    @patch("src.modules.famille.achats_famille.afficher_historique")
    def test_app_affiche_stats_caption(
        self,
        mock_render_historique,
        mock_render_add_form,
        mock_render_par_magasin,
        mock_render_liste_groupe,
        mock_render_dashboard,
        mock_get_stats,
        mock_st,
    ):
        """Vérifie que app() affiche les stats en caption"""
        mock_get_stats.return_value = {"en_attente": 3, "total_estime": 100.0}
        mock_st.tabs.return_value = [MagicMock() for _ in range(6)]

        from src.modules.famille.achats_famille import app

        app()

        mock_st.caption.assert_called_once()
        call_args = mock_st.caption.call_args[0][0]
        assert "3 en attente" in call_args
        assert "100€" in call_args

    @patch("src.modules.famille.achats_famille.st")
    @patch("src.modules.famille.achats_famille.get_stats")
    @patch("src.modules.famille.achats_famille.afficher_dashboard")
    @patch("src.modules.famille.achats_famille.afficher_liste_groupe")
    @patch("src.modules.famille.achats_famille.afficher_par_magasin")
    @patch("src.modules.famille.achats_famille.afficher_add_form")
    @patch("src.modules.famille.achats_famille.afficher_historique")
    def test_app_cree_tabs(
        self,
        mock_render_historique,
        mock_render_add_form,
        mock_render_par_magasin,
        mock_render_liste_groupe,
        mock_render_dashboard,
        mock_get_stats,
        mock_st,
    ):
        """Vérifie que app() crée 6 tabs"""
        mock_get_stats.return_value = {"en_attente": 0, "total_estime": 0}
        mock_st.tabs.return_value = [MagicMock() for _ in range(6)]

        from src.modules.famille.achats_famille import app

        app()

        mock_st.tabs.assert_called_once()
        tab_names = mock_st.tabs.call_args[0][0]
        assert len(tab_names) == 6
        assert "Dashboard" in tab_names[0]
        assert "Jules" in tab_names[1]
        assert "Nous" in tab_names[2]


# ============================================================
# Tests des constantes (utils)
# ============================================================


class TestConstantes:
    """Tests pour les constantes CATEGORIES et PRIORITES"""

    def test_categories_structure_complete(self):
        """Vérifie la structure complète de CATEGORIES"""
        from src.modules.famille.achats_famille.utils import CATEGORIES

        assert len(CATEGORIES) >= 7

        for key, value in CATEGORIES.items():
            assert "emoji" in value
            assert "label" in value
            assert "groupe" in value
            assert isinstance(value["emoji"], str)
            assert isinstance(value["label"], str)
            assert value["groupe"] in ["jules", "nous", "maison"]

    def test_categories_groupes_jules(self):
        """Vérifie les catégories du groupe Jules"""
        from src.modules.famille.achats_famille.utils import CATEGORIES

        jules_categories = [k for k, v in CATEGORIES.items() if v["groupe"] == "jules"]
        assert len(jules_categories) >= 3
        assert "jules_vetements" in jules_categories
        assert "jules_jouets" in jules_categories
        assert "jules_equipement" in jules_categories

    def test_categories_groupes_nous(self):
        """Vérifie les catégories du groupe Nous"""
        from src.modules.famille.achats_famille.utils import CATEGORIES

        nous_categories = [k for k, v in CATEGORIES.items() if v["groupe"] == "nous"]
        assert len(nous_categories) >= 3
        assert "nous_jeux" in nous_categories
        assert "nous_loisirs" in nous_categories
        assert "nous_equipement" in nous_categories

    def test_priorites_ordre_logique(self):
        """Vérifie que les priorités ont un ordre logique"""
        from src.modules.famille.achats_famille.utils import PRIORITES

        assert PRIORITES["urgent"]["order"] == 1
        assert PRIORITES["haute"]["order"] == 2
        assert PRIORITES["moyenne"]["order"] == 3
        assert PRIORITES["basse"]["order"] == 4
        assert PRIORITES["optionnel"]["order"] == 5

    def test_priorites_emojis(self):
        """Vérifie que chaque priorité a un emoji distinct"""
        from src.modules.famille.achats_famille.utils import PRIORITES

        emojis = [v["emoji"] for v in PRIORITES.values()]
        assert len(emojis) == len(set(emojis))  # Tous uniques


# ============================================================
# Tests des fonctions utilitaires avec mocking DB
# ============================================================


class TestGetAllPurchases:
    """Tests pour get_all_purchases"""

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_retourne_achats_non_achetes_par_defaut(self, mock_factory):
        """get_all_purchases retourne les achats non achetés par défaut"""
        mock_purchase1 = MagicMock(achete=False, nom="Article 1")
        mock_purchase2 = MagicMock(achete=False, nom="Article 2")

        mock_service = MagicMock()
        mock_service.lister_achats.return_value = [mock_purchase1, mock_purchase2]
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import get_all_purchases

        result = get_all_purchases()

        assert len(result) == 2
        mock_service.lister_achats.assert_called_with(achete=False)

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_retourne_achats_achetes_si_specifie(self, mock_factory):
        """get_all_purchases retourne les achats achetés si achete=True"""
        mock_purchase = MagicMock(achete=True)

        mock_service = MagicMock()
        mock_service.lister_achats.return_value = [mock_purchase]
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import get_all_purchases

        result = get_all_purchases(achete=True)

        mock_service.lister_achats.assert_called_with(achete=True)

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_retourne_liste_vide_sur_erreur(self, mock_factory):
        """get_all_purchases retourne [] en cas d'exception"""
        mock_factory.side_effect = Exception("DB Error")

        from src.modules.famille.achats_famille.utils import get_all_purchases

        result = get_all_purchases()

        assert result == []


class TestGetPurchasesByCategory:
    """Tests pour get_purchases_by_category"""

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_filtre_par_categorie(self, mock_factory):
        """get_purchases_by_category filtre correctement par catégorie"""
        mock_purchase = MagicMock(categorie="jules_vetements", achete=False)

        mock_service = MagicMock()
        mock_service.lister_par_categorie.return_value = [mock_purchase]
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import get_purchases_by_category

        result = get_purchases_by_category("jules_vetements")

        assert len(result) == 1

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_retourne_liste_vide_sur_erreur(self, mock_factory):
        """get_purchases_by_category retourne [] en cas d'exception"""
        mock_factory.side_effect = Exception("DB Error")

        from src.modules.famille.achats_famille.utils import get_purchases_by_category

        result = get_purchases_by_category("jules_vetements")

        assert result == []


class TestGetPurchasesByGroupe:
    """Tests pour get_purchases_by_groupe"""

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_filtre_groupe_jules(self, mock_factory):
        """get_purchases_by_groupe filtre les catégories du groupe jules"""
        mock_purchase = MagicMock()

        mock_service = MagicMock()
        mock_service.lister_par_groupe.return_value = [mock_purchase]
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import get_purchases_by_groupe

        result = get_purchases_by_groupe("jules")

        assert len(result) == 1

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_retourne_liste_vide_sur_erreur(self, mock_factory):
        """get_purchases_by_groupe retourne [] en cas d'exception"""
        mock_factory.side_effect = Exception("DB Error")

        from src.modules.famille.achats_famille.utils import get_purchases_by_groupe

        result = get_purchases_by_groupe("nous")

        assert result == []


class TestGetStats:
    """Tests pour get_stats"""

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_calcule_stats_correctement(self, mock_factory):
        """get_stats calcule les statistiques correctement"""
        mock_service = MagicMock()
        mock_service.get_stats.return_value = {
            "en_attente": 2,
            "achetes": 1,
            "total_estime": 80.0,
            "total_depense": 45.0,
            "urgents": 1,
        }
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import get_stats

        stats = get_stats()

        assert stats["en_attente"] == 2
        assert stats["achetes"] == 1
        assert stats["total_estime"] == 80.0
        assert stats["urgents"] == 1

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_retourne_stats_vides_sur_erreur(self, mock_factory):
        """get_stats retourne des stats \u00e0 z\u00e9ro en cas d'erreur"""
        mock_factory.side_effect = Exception("DB Error")

        from src.modules.famille.achats_famille.utils import get_stats

        stats = get_stats()

        assert stats["en_attente"] == 0
        assert stats["achetes"] == 0
        assert stats["total_estime"] == 0
        assert stats["total_depense"] == 0
        assert stats["urgents"] == 0


class TestMarkAsBought:
    """Tests pour mark_as_bought"""

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_marque_achat_comme_achete(self, mock_factory):
        """mark_as_bought marque un achat comme achet\u00e9"""
        mock_service = MagicMock()
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import mark_as_bought

        mark_as_bought(1)

        mock_service.marquer_achete.assert_called_once_with(1, prix_reel=None)

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_marque_avec_prix_reel(self, mock_factory):
        """mark_as_bought enregistre le prix r\u00e9el si fourni"""
        mock_service = MagicMock()
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import mark_as_bought

        mark_as_bought(1, prix_reel=99.99)

        mock_service.marquer_achete.assert_called_once_with(1, prix_reel=99.99)

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_ne_fait_rien_si_achat_inexistant(self, mock_factory):
        """mark_as_bought d\u00e9l\u00e8gue au service"""
        mock_service = MagicMock()
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import mark_as_bought

        mark_as_bought(999)

        mock_service.marquer_achete.assert_called_once_with(999, prix_reel=None)

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_gere_erreur_silencieusement(self, mock_factory):
        """mark_as_bought g\u00e8re les erreurs silencieusement"""
        mock_factory.side_effect = Exception("DB Error")

        from src.modules.famille.achats_famille.utils import mark_as_bought

        # Ne doit pas lever d'exception
        mark_as_bought(1)


class TestDeletePurchase:
    """Tests pour delete_purchase"""

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_supprime_achat(self, mock_factory):
        """delete_purchase supprime un achat existant"""
        mock_service = MagicMock()
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import delete_purchase

        delete_purchase(1)

        mock_service.supprimer_achat.assert_called_once_with(1)

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_ne_fait_rien_si_achat_inexistant(self, mock_factory):
        """delete_purchase d\u00e9l\u00e8gue au service"""
        mock_service = MagicMock()
        mock_factory.return_value = mock_service

        from src.modules.famille.achats_famille.utils import delete_purchase

        delete_purchase(999)

        mock_service.supprimer_achat.assert_called_once_with(999)

    @patch("src.modules.famille.achats_famille.utils.obtenir_service_achats_famille")
    def test_gere_erreur_silencieusement(self, mock_factory):
        """delete_purchase g\u00e8re les erreurs silencieusement"""
        mock_factory.side_effect = Exception("DB Error")

        from src.modules.famille.achats_famille.utils import delete_purchase

        # Ne doit pas lever d'exception
        delete_purchase(1)


# ============================================================
# Tests des composants UI avec mocking Streamlit
# ============================================================


class TestRenderDashboard:
    """Tests pour afficher_dashboard"""

    @patch("src.modules.famille.achats_famille.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.get_stats")
    def test_affiche_metriques(self, mock_get_stats, mock_st, mock_svc_factory):
        """afficher_dashboard affiche les m\u00e9triques principales"""
        mock_get_stats.return_value = {
            "en_attente": 5,
            "urgents": 2,
            "total_estime": 150.0,
            "achetes": 10,
        }

        mock_service = MagicMock()
        mock_service.get_urgents.return_value = []
        mock_svc_factory.return_value = mock_service

        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col, mock_col]

        from src.modules.famille.achats_famille.components import afficher_dashboard

        afficher_dashboard()

        mock_st.subheader.assert_called_once_with("\U0001f4ca Vue d'ensemble")
        assert mock_st.columns.called

    @patch("src.modules.famille.achats_famille.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.get_stats")
    def test_affiche_message_si_pas_urgents(self, mock_get_stats, mock_st, mock_svc_factory):
        """afficher_dashboard affiche un message si aucun achat urgent"""
        mock_get_stats.return_value = {
            "en_attente": 0,
            "urgents": 0,
            "total_estime": 0,
            "achetes": 0,
        }

        mock_service = MagicMock()
        mock_service.get_urgents.return_value = []
        mock_svc_factory.return_value = mock_service

        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col, mock_col]

        from src.modules.famille.achats_famille.components import afficher_dashboard

        afficher_dashboard()

        mock_st.success.assert_called_once_with("\u2705 Rien d'urgent!")


class TestRenderListeGroupe:
    """Tests pour afficher_liste_groupe"""

    @patch("src.modules.famille.achats_famille.components.etat_vide")
    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.get_purchases_by_groupe")
    @patch("src.modules.famille.achats_famille.components.afficher_achat_card")
    def test_affiche_message_si_vide(
        self, mock_render_card, mock_get_purchases, mock_st, mock_etat_vide
    ):
        """afficher_liste_groupe affiche un message si aucun achat"""
        mock_get_purchases.return_value = []

        from src.modules.famille.achats_famille.components import afficher_liste_groupe

        afficher_liste_groupe("jules", "👶 Achats pour Jules")

        mock_etat_vide.assert_called()
        mock_render_card.assert_not_called()

    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.get_purchases_by_groupe")
    @patch("src.modules.famille.achats_famille.components.afficher_achat_card")
    def test_affiche_achats_par_priorite(self, mock_render_card, mock_get_purchases, mock_st):
        """afficher_liste_groupe affiche les achats groupés par priorité"""
        mock_achat_urgent = MagicMock(priorite="urgent", nom="Article urgent")
        mock_achat_moyenne = MagicMock(priorite="moyenne", nom="Article moyen")
        mock_get_purchases.return_value = [mock_achat_urgent, mock_achat_moyenne]

        from src.modules.famille.achats_famille.components import afficher_liste_groupe

        afficher_liste_groupe("jules", "👶 Achats pour Jules")

        assert mock_render_card.call_count == 2


class TestRenderAchatCard:
    """Tests pour afficher_achat_card"""

    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.mark_as_bought")
    @patch("src.modules.famille.achats_famille.components.delete_purchase")
    def test_affiche_card_avec_infos(self, mock_delete, mock_mark, mock_st):
        """afficher_achat_card affiche les informations de l'achat"""
        mock_achat = MagicMock(
            id=1,
            nom="Test Article",
            categorie="jules_vetements",
            taille="18 mois",
            magasin="Amazon",
            description="Une description",
            url="https://example.com",
            prix_estime=29.99,
        )

        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col]

        # Mock buttons to return False (non cliqués)
        mock_st.button.return_value = False

        from src.modules.famille.achats_famille.components import afficher_achat_card

        afficher_achat_card(mock_achat)

        mock_st.container.assert_called_once_with(border=True)

    @patch("src.modules.famille.achats_famille.components.rerun")
    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.mark_as_bought")
    @patch("src.modules.famille.achats_famille.components.delete_purchase")
    def test_bouton_acheter_appelle_mark_as_bought(
        self, mock_delete, mock_mark, mock_st, mock_rerun
    ):
        """Le bouton ✅ appelle mark_as_bought"""
        mock_achat = MagicMock(
            id=42,
            nom="Test",
            categorie="jules_vetements",
            taille=None,
            magasin=None,
            description=None,
            url=None,
            prix_estime=None,
        )

        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col]

        # Premier bouton (✅) cliqué, deuxième non
        mock_st.button.side_effect = [True, False]

        from src.modules.famille.achats_famille.components import afficher_achat_card

        afficher_achat_card(mock_achat)

        mock_mark.assert_called_once_with(42)
        mock_rerun.assert_called()


class TestRenderAddForm:
    """Tests pour afficher_add_form"""

    @patch("src.modules.famille.achats_famille.components.st")
    def test_affiche_formulaire(self, mock_st):
        """afficher_add_form affiche le formulaire d'ajout"""
        mock_form = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=mock_form)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)

        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col]

        mock_st.text_input.return_value = ""
        mock_st.selectbox.return_value = "jules_vetements"
        mock_st.number_input.return_value = 0
        mock_st.text_area.return_value = ""
        mock_st.form_submit_button.return_value = False

        from src.modules.famille.achats_famille.components import afficher_add_form

        afficher_add_form()

        mock_st.subheader.assert_called_once_with("➕ Ajouter un article")
        mock_st.form.assert_called_once_with("add_purchase")


class TestRenderHistorique:
    """Tests pour afficher_historique"""

    @patch("src.modules.famille.achats_famille.components.etat_vide")
    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.get_all_purchases")
    def test_affiche_message_si_vide(self, mock_get_all, mock_st, mock_etat_vide):
        """afficher_historique affiche un message si aucun historique"""
        mock_get_all.return_value = []

        from src.modules.famille.achats_famille.components import afficher_historique

        afficher_historique()

        mock_etat_vide.assert_called()

    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.get_all_purchases")
    def test_affiche_total_depense(self, mock_get_all, mock_st):
        """afficher_historique affiche le total dépensé"""
        mock_achat = MagicMock(
            prix_reel=50.0,
            prix_estime=45.0,
            date_achat=date.today(),
            categorie="jules_vetements",
            nom="Article",
            magasin="Amazon",
        )
        mock_get_all.return_value = [mock_achat]

        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col]

        from src.modules.famille.achats_famille.components import afficher_historique

        afficher_historique()

        mock_st.metric.assert_called_once()
        call_args = mock_st.metric.call_args
        assert "Total" in call_args[0][0] or "Total" in str(call_args)


class TestRenderParMagasin:
    """Tests pour afficher_par_magasin"""

    @patch("src.modules.famille.achats_famille.components.etat_vide")
    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.get_all_purchases")
    def test_affiche_message_si_vide(self, mock_get_all, mock_st, mock_etat_vide):
        """afficher_par_magasin affiche un message si aucun article"""
        mock_get_all.return_value = []

        from src.modules.famille.achats_famille.components import afficher_par_magasin

        afficher_par_magasin()

        mock_etat_vide.assert_called()

    @patch("src.modules.famille.achats_famille.components.st")
    @patch("src.modules.famille.achats_famille.components.get_all_purchases")
    @patch("src.modules.famille.achats_famille.components.mark_as_bought")
    def test_groupe_par_magasin(self, mock_mark, mock_get_all, mock_st):
        """afficher_par_magasin groupe les achats par magasin"""
        mock_achat1 = MagicMock(magasin="Amazon", nom="Article 1", prix_estime=20.0, id=1)
        mock_achat2 = MagicMock(magasin="Amazon", nom="Article 2", prix_estime=30.0, id=2)
        mock_achat3 = MagicMock(magasin=None, nom="Article 3", prix_estime=10.0, id=3)

        mock_get_all.return_value = [mock_achat1, mock_achat2, mock_achat3]

        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col]
        mock_st.checkbox.return_value = False

        from src.modules.famille.achats_famille.components import afficher_par_magasin

        afficher_par_magasin()

        # Vérifie qu'il y a au moins 2 expanders (Amazon + Sans magasin)
        assert mock_st.expander.call_count >= 2


# ============================================================
# Tests d'intégration légère
# ============================================================


class TestIntegrationBasique:
    """Tests d'intégration basiques"""

    def test_module_structure_coherente(self):
        """Vérifie que la structure du module est cohérente"""
        with patch("src.modules.famille.achats_famille.st"):
            from src.modules.famille.achats_famille import (
                afficher_dashboard,
                app,
                get_all_purchases,
                get_stats,
            )

            # Vérifie que toutes les fonctions sont appelables
            assert callable(app)
            assert callable(get_all_purchases)
            assert callable(get_stats)
            assert callable(afficher_dashboard)

    def test_categories_utilisees_dans_components(self):
        """Vérifie que les constantes sont accessibles depuis components"""
        from src.modules.famille.achats_famille.components import CATEGORIES as COMP_CATEGORIES
        from src.modules.famille.achats_famille.utils import CATEGORIES

        # Les constantes doivent être les mêmes
        assert CATEGORIES == COMP_CATEGORIES
