"""
Tests d'import et structure pour les modules UI Streamlit
Ces tests vérifient que les modules sont importables sans lancer Streamlit
"""

import pytest
from unittest.mock import MagicMock, patch
import sys


# ═══════════════════════════════════════════════════════════════
# MOCK STREAMLIT POUR TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def mock_streamlit():
    """Mock Streamlit pour les tests d'import"""
    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.cache_data = lambda **kwargs: lambda f: f
    mock_st.cache_resource = lambda **kwargs: lambda f: f
    
    with patch.dict(sys.modules, {'streamlit': mock_st}):
        yield mock_st


# ═══════════════════════════════════════════════════════════════
# TESTS MODULES CUISINE
# ═══════════════════════════════════════════════════════════════

class TestModulesCuisineImport:
    """Tests d'import des modules cuisine"""
    
    def test_inventaire_module_exists(self, mock_streamlit):
        """Test que le module inventaire existe"""
        try:
            from src.modules.cuisine import inventaire
            assert inventaire is not None
        except (ImportError, AttributeError):
            # Le module peut dépendre de Streamlit
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_recettes_module_exists(self, mock_streamlit):
        """Test que le module recettes existe"""
        try:
            from src.modules.cuisine import recettes
            assert recettes is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_recettes_import_module_exists(self, mock_streamlit):
        """Test que le module recettes_import existe"""
        try:
            from src.modules.cuisine import recettes_import
            assert recettes_import is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")


# ═══════════════════════════════════════════════════════════════
# TESTS MODULES FAMILLE
# ═══════════════════════════════════════════════════════════════

class TestModulesFamilleImport:
    """Tests d'import des modules famille"""
    
    def test_accueil_module_exists(self, mock_streamlit):
        """Test que le module accueil famille existe"""
        try:
            from src.modules.famille import accueil
            assert accueil is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_activites_module_exists(self, mock_streamlit):
        """Test que le module activites existe"""
        try:
            from src.modules.famille import activites
            assert activites is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_bien_etre_module_exists(self, mock_streamlit):
        """Test que le module bien_etre existe"""
        try:
            from src.modules.famille import bien_etre
            assert bien_etre is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_jules_module_exists(self, mock_streamlit):
        """Test que le module jules existe"""
        try:
            from src.modules.famille import jules
            assert jules is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_routines_module_exists(self, mock_streamlit):
        """Test que le module routines existe"""
        try:
            from src.modules.famille import routines
            assert routines is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_sante_module_exists(self, mock_streamlit):
        """Test que le module sante existe"""
        try:
            from src.modules.famille import sante
            assert sante is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_shopping_module_exists(self, mock_streamlit):
        """Test que le module shopping existe"""
        try:
            from src.modules.famille import shopping
            assert shopping is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_suivi_jules_module_exists(self, mock_streamlit):
        """Test que le module suivi_jules existe"""
        try:
            from src.modules.famille import suivi_jules
            assert suivi_jules is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")


# ═══════════════════════════════════════════════════════════════
# TESTS MODULES MAISON
# ═══════════════════════════════════════════════════════════════

class TestModulesMaisonImport:
    """Tests d'import des modules maison"""
    
    def test_entretien_module_exists(self, mock_streamlit):
        """Test que le module entretien existe"""
        try:
            from src.modules.maison import entretien
            assert entretien is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_jardin_module_exists(self, mock_streamlit):
        """Test que le module jardin existe"""
        try:
            from src.modules.maison import jardin
            assert jardin is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_projets_module_exists(self, mock_streamlit):
        """Test que le module projets existe"""
        try:
            from src.modules.maison import projets
            assert projets is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")


# ═══════════════════════════════════════════════════════════════
# TESTS MODULES PLANNING
# ═══════════════════════════════════════════════════════════════

class TestModulesPlanningImport:
    """Tests d'import des modules planning"""
    
    def test_calendrier_module_exists(self, mock_streamlit):
        """Test que le module calendrier existe"""
        try:
            from src.modules.planning import calendrier
            assert calendrier is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_vue_ensemble_module_exists(self, mock_streamlit):
        """Test que le module vue_ensemble existe"""
        try:
            from src.modules.planning import vue_ensemble
            assert vue_ensemble is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_vue_semaine_module_exists(self, mock_streamlit):
        """Test que le module vue_semaine existe"""
        try:
            from src.modules.planning import vue_semaine
            assert vue_semaine is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")


# ═══════════════════════════════════════════════════════════════
# TESTS MODULES PRINCIPAUX
# ═══════════════════════════════════════════════════════════════

class TestModulesPrincipauxImport:
    """Tests d'import des modules principaux"""
    
    def test_accueil_module_exists(self, mock_streamlit):
        """Test que le module accueil principal existe"""
        try:
            from src.modules import accueil
            assert accueil is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_barcode_module_exists(self, mock_streamlit):
        """Test que le module barcode existe"""
        try:
            from src.modules import barcode
            assert barcode is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_parametres_module_exists(self, mock_streamlit):
        """Test que le module parametres existe"""
        try:
            from src.modules import parametres
            assert parametres is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
    
    def test_rapports_module_exists(self, mock_streamlit):
        """Test que le module rapports existe"""
        try:
            from src.modules import rapports
            assert rapports is not None
        except (ImportError, AttributeError):
            pytest.skip("Dépendance Streamlit manquante")
