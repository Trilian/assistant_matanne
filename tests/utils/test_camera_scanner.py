"""
Tests unitaires pour camera_scanner.py - Scan code-barres
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import numpy as np


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MOCK STREAMLIT ET DÃ‰PENDANCES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock Streamlit et autres dépendances"""
    mock_st = MagicMock()
    mock_st.session_state = {}
    
    with patch.dict(sys.modules, {
        'streamlit': mock_st,
        'streamlit_webrtc': MagicMock(),
    }):
        if 'src.ui.components.camera_scanner' in sys.modules:
            del sys.modules['src.ui.components.camera_scanner']
        yield mock_st


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FONCTION DETECT BARCODE PYZBAR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestDetectBarcodePyzbar:
    """Tests de la détection avec pyzbar"""
    
    def test_function_exists(self, mock_dependencies):
        """Test que la fonction existe"""
        from src.ui.components.camera_scanner import _detect_barcode_pyzbar
        
        assert callable(_detect_barcode_pyzbar)
    
    def test_returns_list(self, mock_dependencies):
        """Test que la fonction retourne une liste"""
        from src.ui.components.camera_scanner import _detect_barcode_pyzbar
        
        # Créer une frame vide
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch.dict(sys.modules, {
            'pyzbar': MagicMock(),
            'pyzbar.pyzbar': MagicMock(decode=MagicMock(return_value=[])),
            'cv2': MagicMock(cvtColor=MagicMock(return_value=frame)),
        }):
            result = _detect_barcode_pyzbar(frame)
            assert isinstance(result, list)
    
    def test_handles_import_error(self, mock_dependencies):
        """Test gestion ImportError pyzbar"""
        from src.ui.components.camera_scanner import _detect_barcode_pyzbar
        
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Sans pyzbar installé, devrait retourner liste vide
        result = _detect_barcode_pyzbar(frame)
        assert isinstance(result, list)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FONCTION DETECT BARCODE ZXING
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestDetectBarcodeZxing:
    """Tests de la détection avec zxing"""
    
    def test_function_exists(self, mock_dependencies):
        """Test que la fonction existe"""
        from src.ui.components.camera_scanner import _detect_barcode_zxing
        
        assert callable(_detect_barcode_zxing)
    
    def test_returns_list(self, mock_dependencies):
        """Test que la fonction retourne une liste"""
        from src.ui.components.camera_scanner import _detect_barcode_zxing
        
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = _detect_barcode_zxing(frame)
        assert isinstance(result, list)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODULE IMPORT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestCameraScannerImport:
    """Tests d'import du module"""
    
    def test_module_importable(self, mock_dependencies):
        """Test que le module s'importe"""
        from src.ui.components import camera_scanner
        
        assert camera_scanner is not None
    
    def test_has_detect_functions(self, mock_dependencies):
        """Test que les fonctions de détection existent"""
        from src.ui.components import camera_scanner
        
        assert hasattr(camera_scanner, '_detect_barcode_pyzbar')
        assert hasattr(camera_scanner, '_detect_barcode_zxing')

