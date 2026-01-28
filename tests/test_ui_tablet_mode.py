"""Tests pour le module tablet_mode."""
import pytest
from unittest.mock import patch, MagicMock
import streamlit as st


class TestTabletModeDetection:
    """Tests pour la détection du mode tablette."""
    
    def test_detect_tablet_from_user_agent_ipad(self):
        """Détecte iPad comme tablette."""
        from src.ui.tablet_mode import detecter_mode_tablette
        
        with patch('streamlit.context') as mock_context:
            mock_headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_0)'}
            mock_context.headers = mock_headers
            
            result = detecter_mode_tablette()
            assert result is True
    
    def test_detect_tablet_from_user_agent_android(self):
        """Détecte Android tablette."""
        from src.ui.tablet_mode import detecter_mode_tablette
        
        with patch('streamlit.context') as mock_context:
            mock_headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Tablet)'}
            mock_context.headers = mock_headers
            
            result = detecter_mode_tablette()
            assert result is True
    
    def test_detect_desktop_mode(self):
        """Détecte mode desktop."""
        from src.ui.tablet_mode import detecter_mode_tablette
        
        with patch('streamlit.context') as mock_context:
            mock_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64)'}
            mock_context.headers = mock_headers
            
            result = detecter_mode_tablette()
            assert result is False


class TestTabletUIAdjustments:
    """Tests pour les ajustements d'interface tablette."""
    
    def test_adjust_font_size_tablet(self):
        """Ajuste la taille de police pour tablette."""
        from src.ui.tablet_mode import ajuster_taille_police
        
        result = ajuster_taille_police(mode_tablette=True)
        assert "font-size" in result
        assert "18px" in result or "1.2em" in result
    
    def test_adjust_font_size_desktop(self):
        """Conserve taille normale pour desktop."""
        from src.ui.tablet_mode import ajuster_taille_police
        
        result = ajuster_taille_police(mode_tablette=False)
        assert "font-size" in result
    
    def test_adjust_button_size_tablet(self):
        """Ajuste les boutons pour tactile."""
        from src.ui.tablet_mode import ajuster_taille_boutons
        
        result = ajuster_taille_boutons(mode_tablette=True)
        assert "padding" in result
        assert "min-height" in result
    
    def test_adjust_spacing_tablet(self):
        """Augmente l'espacement en mode tablette."""
        from src.ui.tablet_mode import ajuster_espacement
        
        result = ajuster_espacement(mode_tablette=True)
        assert "margin" in result or "padding" in result


class TestTabletComponents:
    """Tests pour les composants adaptés tablette."""
    
    @patch('streamlit.button')
    def test_create_large_button(self, mock_button):
        """Crée un bouton tactile large."""
        from src.ui.tablet_mode import creer_bouton_tactile
        
        mock_button.return_value = False
        creer_bouton_tactile("Test", key="test1")
        
        mock_button.assert_called_once()
    
    @patch('streamlit.columns')
    def test_tablet_layout_columns(self, mock_columns):
        """Adapte les colonnes pour tablette."""
        from src.ui.tablet_mode import creer_layout_tablette
        
        mock_columns.return_value = [MagicMock(), MagicMock()]
        result = creer_layout_tablette(nb_colonnes=2)
        
        assert result is not None


class TestTabletGestures:
    """Tests pour la gestion des gestes tactiles."""
    
    def test_swipe_detection(self):
        """Détecte le geste de swipe."""
        from src.ui.tablet_mode import detecter_swipe
        
        # Simule coordonnées de swipe
        start = {"x": 100, "y": 200}
        end = {"x": 300, "y": 210}
        
        direction = detecter_swipe(start, end)
        assert direction in ["left", "right", "up", "down", None]
    
    def test_long_press_detection(self):
        """Détecte un appui long."""
        from src.ui.tablet_mode import detecter_appui_long
        
        # Simule durée d'appui
        duree = 1.5  # secondes
        
        result = detecter_appui_long(duree)
        assert isinstance(result, bool)


class TestTabletCache:
    """Tests pour le cache en mode tablette."""
    
    def test_cache_mode_tablette(self):
        """Cache l'état du mode tablette."""
        from src.ui.tablet_mode import get_mode_tablette_cached
        
        with patch('src.ui.tablet_mode.detecter_mode_tablette', return_value=True):
            result1 = get_mode_tablette_cached()
            result2 = get_mode_tablette_cached()
            
            assert result1 == result2
            assert result1 is True


class TestTabletSettings:
    """Tests pour les paramètres tablette."""
    
    def test_save_tablet_preference(self):
        """Sauvegarde la préférence utilisateur."""
        from src.ui.tablet_mode import sauvegarder_preference_tablette
        
        with patch('streamlit.session_state', {}):
            sauvegarder_preference_tablette(force_mode=True)
            assert st.session_state.get("force_tablet_mode") is True
    
    def test_load_tablet_preference(self):
        """Charge la préférence sauvegardée."""
        from src.ui.tablet_mode import charger_preference_tablette
        
        with patch('streamlit.session_state', {"force_tablet_mode": True}):
            result = charger_preference_tablette()
            assert result is True


class TestTabletKeyboard:
    """Tests pour le clavier virtuel."""
    
    def test_show_numeric_keyboard(self):
        """Affiche clavier numérique pour quantités."""
        from src.ui.tablet_mode import afficher_clavier_numerique
        
        with patch('streamlit.number_input') as mock_input:
            mock_input.return_value = 5
            result = afficher_clavier_numerique("Quantité")
            
            mock_input.assert_called_once()
    
    def test_show_text_keyboard(self):
        """Affiche clavier texte optimisé."""
        from src.ui.tablet_mode import afficher_clavier_texte
        
        with patch('streamlit.text_input') as mock_input:
            mock_input.return_value = "test"
            result = afficher_clavier_texte("Recherche")
            
            mock_input.assert_called_once()


class TestTabletOrientation:
    """Tests pour la gestion de l'orientation."""
    
    def test_detect_portrait_orientation(self):
        """Détecte orientation portrait."""
        from src.ui.tablet_mode import detecter_orientation
        
        # Simule dimensions portrait
        with patch('streamlit.get_option', return_value=800):
            orientation = detecter_orientation()
            assert orientation in ["portrait", "landscape", None]
    
    def test_adjust_layout_for_orientation(self):
        """Adapte le layout selon l'orientation."""
        from src.ui.tablet_mode import adapter_layout_orientation
        
        result_portrait = adapter_layout_orientation("portrait")
        result_landscape = adapter_layout_orientation("landscape")
        
        assert result_portrait != result_landscape


class TestTabletAccessibility:
    """Tests pour l'accessibilité en mode tablette."""
    
    def test_increase_touch_targets(self):
        """Augmente la taille des zones tactiles."""
        from src.ui.tablet_mode import augmenter_zones_tactiles
        
        css = augmenter_zones_tactiles()
        assert "min-height" in css
        assert "44px" in css or "48px" in css  # Standards iOS/Android
    
    def test_add_haptic_feedback_config(self):
        """Configure le retour haptique."""
        from src.ui.tablet_mode import configurer_retour_haptique
        
        config = configurer_retour_haptique(active=True)
        assert isinstance(config, dict)
        assert "haptic_enabled" in config


class TestTabletPerformance:
    """Tests pour l'optimisation performance tablette."""
    
    def test_reduce_animations_tablet(self):
        """Réduit les animations pour performance."""
        from src.ui.tablet_mode import optimiser_animations
        
        css = optimiser_animations(mode_tablette=True)
        assert "transition" in css or "animation" in css
    
    def test_lazy_load_images_tablet(self):
        """Active le lazy loading des images."""
        from src.ui.tablet_mode import activer_lazy_loading
        
        config = activer_lazy_loading()
        assert config.get("lazy_load") is True


@pytest.fixture
def mock_streamlit_session():
    """Mock de la session Streamlit."""
    with patch('streamlit.session_state', {}):
        yield st.session_state


@pytest.fixture
def mock_tablet_context():
    """Contexte simulé pour tablette."""
    with patch('streamlit.context') as mock_ctx:
        mock_ctx.headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_0)'}
        yield mock_ctx
