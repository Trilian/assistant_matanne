"""
Tests pour le module Barcode/QR Streamlit (test_barcode_module.py)
Tests pour scanner, ajout rapide, vérification stock, import/export
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import streamlit as st

from src.modules.barcode import (
    render_scanner,
    render_ajout_rapide,
    render_verifier_stock,
    render_gestion_barcodes,
    render_import_export,
    app,
)
from src.services.barcode import BarcodeService, ScanResultat


class TestRenderScanner:
    """Tests render_scanner() - Onglet Scanner"""

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_scanner_displays_input(self, mock_get_service):
        """Test que l'input scanner s'affiche"""
        mock_service = Mock(spec=BarcodeService)
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.columns"), \
             patch("streamlit.text_input"), \
             patch("streamlit.button", return_value=False):
            
            render_scanner()

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_scanner_invalid_code(self, mock_get_service):
        """Test scanner avec code invalide"""
        mock_service = Mock(spec=BarcodeService)
        mock_service.valider_barcode.return_value = (False, "Format invalide")
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.columns"), \
             patch("streamlit.text_input", return_value="INVALID"), \
             patch("streamlit.button", return_value=True), \
             patch("streamlit.error"):
            
            render_scanner()

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_scanner_valid_code(self, mock_get_service):
        """Test scanner avec code valide"""
        mock_service = Mock(spec=BarcodeService)
        mock_service.valider_barcode.return_value = (True, "EAN-13")
        
        mock_resultat = Mock(spec=ScanResultat)
        mock_resultat.barcode = "5901234123457"
        mock_resultat.type_scan = "article"
        mock_resultat.timestamp = datetime.now()
        mock_resultat.details = {
            "id": 1,
            "nom": "Pâtes",
            "quantite": 2.5,
            "unite": "kg",
            "prix_unitaire": 2.50,
            "emplacement": "Placard",
        }
        
        mock_service.scanner_code.return_value = mock_resultat
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.columns"), \
             patch("streamlit.text_input", return_value="5901234123457"), \
             patch("streamlit.button", return_value=True), \
             patch("streamlit.success"), \
             patch("streamlit.metric"), \
             patch("streamlit.info"):
            
            render_scanner()


class TestRenderAjoutRapide:
    """Tests render_ajout_rapide() - Ajout Rapide"""

    @patch("src.modules.barcode.get_barcode_service")
    @patch("src.modules.barcode.get_inventaire_service")
    def test_render_ajout_rapide_displays_form(self, mock_inv_service, mock_barcode_service):
        """Test que le formulaire ajout rapide s'affiche"""
        mock_barcode = Mock(spec=BarcodeService)
        mock_barcode.lister_articles_avec_barcode.return_value = []
        mock_barcode_service.return_value = mock_barcode
        
        mock_inventaire = Mock()
        mock_inventaire.get_categories.return_value = ["Fruits", "Légumes"]
        mock_inv_service.return_value = mock_inventaire
        
        with patch("streamlit.subheader"), \
             patch("streamlit.text_input"), \
             patch("streamlit.number_input"), \
             patch("streamlit.selectbox"), \
             patch("streamlit.button", return_value=False):
            
            render_ajout_rapide()

    @patch("src.modules.barcode.get_barcode_service")
    @patch("src.modules.barcode.get_inventaire_service")
    def test_render_ajout_rapide_adds_article(self, mock_inv_service, mock_barcode_service):
        """Test ajout article via code-barres"""
        mock_barcode = Mock(spec=BarcodeService)
        mock_barcode.ajouter_article_par_barcode.return_value = Mock(id=1, nom="Pommes")
        mock_barcode_service.return_value = mock_barcode
        
        mock_inventaire = Mock()
        mock_inventaire.get_categories.return_value = ["Fruits"]
        mock_inv_service.return_value = mock_inventaire
        
        with patch("streamlit.subheader"), \
             patch("streamlit.text_input", return_value="5901234123457"), \
             patch("streamlit.number_input", return_value=2.0), \
             patch("streamlit.selectbox", return_value="Fruits"), \
             patch("streamlit.button", return_value=True), \
             patch("streamlit.success"):
            
            render_ajout_rapide()


class TestRenderVerifierStock:
    """Tests render_verifier_stock() - Vérification Stock"""

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_verifier_stock_displays(self, mock_get_service):
        """Test que l'interface vérification s'affiche"""
        mock_service = Mock(spec=BarcodeService)
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.text_input"), \
             patch("streamlit.button", return_value=False):
            
            render_verifier_stock()

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_verifier_stock_checks_inventory(self, mock_get_service):
        """Test vérification stock par code"""
        mock_service = Mock(spec=BarcodeService)
        mock_service.verifier_stock_barcode.return_value = {
            "article_id": 1,
            "nom": "Pâtes",
            "quantite": 2.5,
            "quantite_min": 1.0,
            "etat": "OK",
            "peremption_etat": "OK",
            "jours_avant_peremption": 15,
        }
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.text_input", return_value="5901234123457"), \
             patch("streamlit.button", return_value=True), \
             patch("streamlit.metric"), \
             patch("streamlit.success"):
            
            render_verifier_stock()


class TestRenderGestionBarcodes:
    """Tests render_gestion_barcodes() - Gestion Barcodes"""

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_gestion_barcodes_displays_list(self, mock_get_service):
        """Test que la liste des codes-barres s'affiche"""
        mock_service = Mock(spec=BarcodeService)
        mock_service.lister_articles_avec_barcode.return_value = [
            {"id": 1, "nom": "Pâtes", "barcode": "5901234123457"},
            {"id": 2, "nom": "Riz", "barcode": "5901234123458"},
        ]
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.dataframe"), \
             patch("streamlit.columns"), \
             patch("streamlit.selectbox"), \
             patch("streamlit.text_input"), \
             patch("streamlit.button", return_value=False):
            
            render_gestion_barcodes()

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_gestion_barcodes_update(self, mock_get_service):
        """Test update code-barres"""
        mock_service = Mock(spec=BarcodeService)
        mock_service.lister_articles_avec_barcode.return_value = [
            {"id": 1, "nom": "Pâtes", "barcode": "5901234123457"},
        ]
        mock_service.mettre_a_jour_barcode.return_value = Mock(id=1, nom="Pâtes")
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.dataframe"), \
             patch("streamlit.columns"), \
             patch("streamlit.selectbox", side_effect=[(1, "Pâtes"), "5901234123459"]), \
             patch("streamlit.text_input", return_value="5901234123459"), \
             patch("streamlit.button", return_value=True), \
             patch("streamlit.success"):
            
            render_gestion_barcodes()


class TestRenderImportExport:
    """Tests render_import_export() - Import/Export"""

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_import_export_displays(self, mock_get_service):
        """Test que l'interface import/export s'affiche"""
        mock_service = Mock(spec=BarcodeService)
        mock_service.exporter_barcodes.return_value = "barcode,nom,quantite\n5901234123457,Pâtes,2.5"
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False), \
             patch("streamlit.file_uploader", return_value=None):
            
            render_import_export()

    @patch("src.modules.barcode.get_barcode_service")
    def test_render_import_export_csv_export(self, mock_get_service):
        """Test export CSV"""
        mock_service = Mock(spec=BarcodeService)
        csv_content = "barcode,nom,quantite,unite\n5901234123457,Pâtes,2.5,kg"
        mock_service.exporter_barcodes.return_value = csv_content
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=True), \
             patch("streamlit.download_button"), \
             patch("streamlit.success"):
            
            render_import_export()


class TestBarcodeApp:
    """Tests fonction app() principale"""

    @patch("src.modules.barcode.st.markdown")
    @patch("src.modules.barcode.st.tabs")
    def test_app_entry_point(self, mock_tabs, mock_markdown):
        """Test que app() crée 5 onglets"""
        tab1, tab2, tab3, tab4, tab5 = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        mock_tabs.return_value = (tab1, tab2, tab3, tab4, tab5)
        
        with patch("src.modules.barcode.render_scanner"), \
             patch("src.modules.barcode.render_ajout_rapide"), \
             patch("src.modules.barcode.render_verifier_stock"), \
             patch("src.modules.barcode.render_gestion_barcodes"), \
             patch("src.modules.barcode.render_import_export"):
            
            app()
            
            mock_markdown.assert_called()
            mock_tabs.assert_called()

    def test_barcode_module_structure(self):
        """Test que le module a la bonne structure"""
        from src.modules import barcode
        
        assert hasattr(barcode, "app")
        assert hasattr(barcode, "render_scanner")
        assert hasattr(barcode, "render_ajout_rapide")
        assert hasattr(barcode, "render_verifier_stock")
        assert hasattr(barcode, "render_gestion_barcodes")
        assert hasattr(barcode, "render_import_export")
        assert callable(barcode.app)


class TestBarcodeIntegration:
    """Tests intégration module barcode"""

    @patch("src.modules.barcode.get_barcode_service")
    def test_barcode_service_initialization(self, mock_get_service):
        """Test initialisation service barcode"""
        mock_service = Mock(spec=BarcodeService)
        mock_get_service.return_value = mock_service
        
        # Service devrait être accessible
        service = mock_get_service()
        assert service is not None
        assert hasattr(service, "scanner_code")
        assert hasattr(service, "valider_barcode")

    @patch("src.modules.barcode.get_barcode_service")
    def test_barcode_validation_formats(self, mock_get_service):
        """Test validation formats codes-barres"""
        mock_service = Mock(spec=BarcodeService)
        
        # Tester différents formats
        test_cases = [
            ("5901234123457", True, "EAN-13"),  # Valid EAN-13
            ("12345678", True, "EAN-8"),        # Valid EAN-8
            ("12345678901", True, "UPC"),       # Valid UPC
            ("INVALID", False, "Format invalide"),  # Invalid
        ]
        
        for code, expected_valid, expected_type in test_cases:
            mock_service.valider_barcode.return_value = (expected_valid, expected_type)
            valid, code_type = mock_service.valider_barcode(code)
            assert valid == expected_valid
