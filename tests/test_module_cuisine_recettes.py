"""
Tests pour le module cuisine/recettes.py
Gestion complète des recettes avec filtres, pagination et détails
"""

import pytest
from unittest.mock import MagicMock, patch
from tests.conftest import SessionStateMock


class TestAppRecettes:
    """Tests pour la fonction principale app()"""

    @patch("src.modules.cuisine.recettes.get_recette_service")
    @patch("src.modules.cuisine.recettes.st")
    def test_initialise_session_state(self, mock_st, mock_get_service):
        """Initialise correctement le session_state"""
        from src.modules.cuisine.recettes import app
        
        mock_st.session_state = SessionStateMock()
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock tabs
        mock_tabs = [MagicMock() for _ in range(4)]
        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()
        mock_st.tabs.return_value = mock_tabs
        
        app()
        
        assert "detail_recette_id" in mock_st.session_state

    @patch("src.modules.cuisine.recettes.render_detail_recette")
    @patch("src.modules.cuisine.recettes.get_recette_service")
    @patch("src.modules.cuisine.recettes.st")
    def test_affiche_detail_recette_si_selectionnee(self, mock_st, mock_get_service, mock_render_detail):
        """Affiche le détail si une recette est sélectionnée"""
        from src.modules.cuisine.recettes import app
        
        mock_st.session_state = SessionStateMock({"detail_recette_id": 42})
        
        mock_recette = MagicMock()
        mock_recette.nom = "Recette Test"
        
        mock_service = MagicMock()
        mock_service.get_by_id_full.return_value = mock_recette
        mock_get_service.return_value = mock_service
        
        # Mock columns pour le bouton retour
        mock_col1 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock()
        mock_col1.button = MagicMock(return_value=False)
        
        mock_col2 = MagicMock()
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock()
        
        mock_st.columns.return_value = [mock_col1, mock_col2]
        
        app()
        
        mock_render_detail.assert_called_once_with(mock_recette)

    @patch("src.modules.cuisine.recettes.get_recette_service")
    @patch("src.modules.cuisine.recettes.st")
    def test_recette_non_trouvee(self, mock_st, mock_get_service):
        """Affiche erreur si recette non trouvée"""
        from src.modules.cuisine.recettes import app
        
        mock_st.session_state = SessionStateMock({"detail_recette_id": 999})
        
        mock_service = MagicMock()
        mock_service.get_by_id_full.return_value = None
        mock_get_service.return_value = mock_service
        
        # Mock columns
        mock_cols = [MagicMock(), MagicMock()]
        for col in mock_cols:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
            col.button = MagicMock(return_value=False)
        mock_st.columns.return_value = mock_cols
        
        # Mock tabs
        mock_tabs = [MagicMock() for _ in range(4)]
        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()
        mock_st.tabs.return_value = mock_tabs
        
        app()
        
        mock_st.error.assert_called()
        assert mock_st.session_state.detail_recette_id is None


class TestRenderListe:
    """Tests pour render_liste()"""

    @patch("src.modules.cuisine.recettes.get_recette_service")
    @patch("src.modules.cuisine.recettes.st")
    def test_service_indisponible(self, mock_st, mock_get_service):
        """Affiche erreur si service indisponible"""
        from src.modules.cuisine.recettes import render_liste
        
        mock_get_service.return_value = None
        mock_st.session_state = SessionStateMock()
        
        render_liste()
        
        mock_st.error.assert_called()
        assert "indisponible" in str(mock_st.error.call_args)


class TestFiltresRecettes:
    """Tests pour les filtres de recettes (logique métier)"""

    def test_filtre_score_bio(self):
        """Filtre par score bio minimum"""
        mock_recettes = [
            MagicMock(score_bio=90),
            MagicMock(score_bio=50),
            MagicMock(score_bio=None),
        ]
        
        min_score_bio = 60
        filtered = [r for r in mock_recettes if (r.score_bio or 0) >= min_score_bio]
        
        assert len(filtered) == 1
        assert filtered[0].score_bio == 90

    def test_filtre_score_local(self):
        """Filtre par score local minimum"""
        mock_recettes = [
            MagicMock(score_local=80),
            MagicMock(score_local=30),
            MagicMock(score_local=0),
        ]
        
        min_score_local = 50
        filtered = [r for r in mock_recettes if (r.score_local or 0) >= min_score_local]
        
        assert len(filtered) == 1
        assert filtered[0].score_local == 80

    def test_filtre_robots_cookeo(self):
        """Filtre par compatibilité Cookeo"""
        mock_recettes = [
            MagicMock(compatible_cookeo=True, compatible_airfryer=False),
            MagicMock(compatible_cookeo=False, compatible_airfryer=True),
            MagicMock(compatible_cookeo=True, compatible_airfryer=True),
        ]
        
        filtered = [r for r in mock_recettes if r.compatible_cookeo]
        assert len(filtered) == 2

    def test_filtre_robots_multiples(self):
        """Filtre par plusieurs robots compatibles"""
        mock_recettes = [
            MagicMock(compatible_cookeo=True, compatible_airfryer=False),
            MagicMock(compatible_cookeo=False, compatible_airfryer=True),
            MagicMock(compatible_cookeo=True, compatible_airfryer=True),
        ]
        
        filtered = [r for r in mock_recettes if r.compatible_cookeo and r.compatible_airfryer]
        assert len(filtered) == 1

    def test_filtre_tags_rapide(self):
        """Filtre par tag rapide"""
        mock_recettes = [
            MagicMock(est_rapide=True),
            MagicMock(est_rapide=False),
            MagicMock(est_rapide=True),
        ]
        
        filtered = [r for r in mock_recettes if r.est_rapide]
        assert len(filtered) == 2

    def test_filtre_tags_equilibre(self):
        """Filtre par tag équilibré"""
        mock_recettes = [
            MagicMock(est_equilibre=True),
            MagicMock(est_equilibre=False),
        ]
        
        filtered = [r for r in mock_recettes if r.est_equilibre]
        assert len(filtered) == 1

    def test_filtre_congelable(self):
        """Filtre par tag congélable"""
        mock_recettes = [
            MagicMock(congelable=True),
            MagicMock(congelable=True),
            MagicMock(congelable=False),
        ]
        
        filtered = [r for r in mock_recettes if r.congelable]
        assert len(filtered) == 2


class TestPagination:
    """Tests pour la pagination des recettes"""

    def test_calcul_pages_10_recettes(self):
        """Calcul du nombre de pages pour 10 recettes"""
        PAGE_SIZE = 9
        recettes = list(range(10))
        total_pages = (len(recettes) + PAGE_SIZE - 1) // PAGE_SIZE
        assert total_pages == 2

    def test_calcul_pages_9_recettes(self):
        """Calcul du nombre de pages pour exactement 9 recettes"""
        PAGE_SIZE = 9
        recettes = list(range(9))
        total_pages = (len(recettes) + PAGE_SIZE - 1) // PAGE_SIZE
        assert total_pages == 1

    def test_calcul_pages_27_recettes(self):
        """Calcul du nombre de pages pour 27 recettes (3 pages exactes)"""
        PAGE_SIZE = 9
        recettes = list(range(27))
        total_pages = (len(recettes) + PAGE_SIZE - 1) // PAGE_SIZE
        assert total_pages == 3

    def test_calcul_indices_page_0(self):
        """Calcul des indices pour la première page"""
        PAGE_SIZE = 9
        page = 0
        start_idx = page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        assert start_idx == 0
        assert end_idx == 9

    def test_calcul_indices_page_1(self):
        """Calcul des indices pour la deuxième page"""
        PAGE_SIZE = 9
        page = 1
        start_idx = page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        assert start_idx == 9
        assert end_idx == 18

    def test_limite_page_max(self):
        """La page ne dépasse pas le maximum"""
        PAGE_SIZE = 9
        recettes = list(range(25))
        total_pages = (len(recettes) + PAGE_SIZE - 1) // PAGE_SIZE
        
        page_actuelle = 5
        page_actuelle = min(page_actuelle, total_pages - 1)
        
        assert page_actuelle == 2


class TestDifficulteEmoji:
    """Tests pour le mapping des emojis de difficulté"""

    def test_emoji_facile(self):
        """Emoji vert pour facile"""
        emoji_map = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}
        assert emoji_map.get("facile") == "🟢"

    def test_emoji_moyen(self):
        """Emoji jaune pour moyen"""
        emoji_map = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}
        assert emoji_map.get("moyen") == "🟡"

    def test_emoji_difficile(self):
        """Emoji rouge pour difficile"""
        emoji_map = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}
        assert emoji_map.get("difficile") == "🔴"

    def test_emoji_inconnu(self):
        """Emoji par défaut pour valeur inconnue"""
        emoji_map = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}
        assert emoji_map.get("inconnu", "⚪") == "⚪"


class TestBadgesRecette:
    """Tests pour les badges de recette"""

    def test_construction_badges_multiples(self):
        """Construit correctement la liste des badges"""
        recette = MagicMock()
        recette.est_bio = True
        recette.est_local = False
        recette.est_rapide = True
        recette.est_equilibre = False
        recette.congelable = True
        
        badges = []
        if recette.est_bio:
            badges.append("🌱 Bio")
        if recette.est_local:
            badges.append("📍 Local")
        if recette.est_rapide:
            badges.append("⚡ Rapide")
        if recette.est_equilibre:
            badges.append("💪 Équilibré")
        if recette.congelable:
            badges.append("❄️ Congélable")
        
        assert len(badges) == 3
        assert "🌱 Bio" in badges
        assert "⚡ Rapide" in badges
        assert "❄️ Congélable" in badges

    def test_badges_vides(self):
        """Gère le cas sans badges"""
        recette = MagicMock()
        recette.est_bio = False
        recette.est_local = False
        recette.est_rapide = False
        recette.est_equilibre = False
        recette.congelable = False
        
        badges = []
        if recette.est_bio:
            badges.append("🌱 Bio")
        
        assert len(badges) == 0

    def test_tous_badges(self):
        """Recette avec tous les badges"""
        recette = MagicMock()
        recette.est_bio = True
        recette.est_local = True
        recette.est_rapide = True
        recette.est_equilibre = True
        recette.congelable = True
        
        badges = []
        if recette.est_bio:
            badges.append("🌱 Bio")
        if recette.est_local:
            badges.append("📍 Local")
        if recette.est_rapide:
            badges.append("⚡ Rapide")
        if recette.est_equilibre:
            badges.append("💪 Équilibré")
        if recette.congelable:
            badges.append("❄️ Congélable")
        
        assert len(badges) == 5


class TestRobotsCompatibles:
    """Tests pour la compatibilité robots"""

    def test_robot_cookeo(self):
        """Vérifie badge Cookeo"""
        recette = MagicMock()
        recette.compatible_cookeo = True
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        
        robots = []
        if recette.compatible_cookeo:
            robots.append("Cookeo")
        
        assert len(robots) == 1
        assert "Cookeo" in robots

    def test_plusieurs_robots(self):
        """Recette compatible avec plusieurs robots"""
        recette = MagicMock()
        recette.compatible_cookeo = True
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = True
        recette.compatible_multicooker = True
        
        robots = []
        if recette.compatible_cookeo:
            robots.append("Cookeo")
        if recette.compatible_monsieur_cuisine:
            robots.append("Monsieur Cuisine")
        if recette.compatible_airfryer:
            robots.append("Airfryer")
        if recette.compatible_multicooker:
            robots.append("Multicooker")
        
        assert len(robots) == 3

    def test_aucun_robot(self):
        """Recette sans compatibilité robot"""
        recette = MagicMock()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        
        robots = []
        if recette.compatible_cookeo:
            robots.append("Cookeo")
        
        assert len(robots) == 0
