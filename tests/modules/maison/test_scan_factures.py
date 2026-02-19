"""
Tests pour src/modules/maison/scan_factures.py

Tests complets pour le module Scan Factures (extraction OCR de factures énergie).
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Module src.modules.maison.scan_factures non encore implémenté"
)
from datetime import date
from unittest.mock import MagicMock, patch

# ═══════════════════════════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════════════════════════


class TestImports:
    """Tests d'import des fonctions et constantes du module."""

    def test_import_constantes_fournisseurs(self):
        """Test import des fournisseurs connus."""
        from src.modules.maison.scan_factures import FOURNISSEURS_CONNUS

        assert FOURNISSEURS_CONNUS is not None
        assert isinstance(FOURNISSEURS_CONNUS, dict)
        assert "EDF" in FOURNISSEURS_CONNUS
        assert "ENGIE" in FOURNISSEURS_CONNUS
        assert "VEOLIA" in FOURNISSEURS_CONNUS

    def test_import_type_energie_labels(self):
        """Test import des labels de type d'énergie."""
        from src.modules.maison.scan_factures import TYPE_ENERGIE_LABELS

        assert TYPE_ENERGIE_LABELS is not None
        assert isinstance(TYPE_ENERGIE_LABELS, dict)
        assert "electricite" in TYPE_ENERGIE_LABELS
        assert "gaz" in TYPE_ENERGIE_LABELS
        assert "eau" in TYPE_ENERGIE_LABELS

    def test_import_mois_fr(self):
        """Test import des mois en français."""
        from src.modules.maison.scan_factures import MOIS_FR

        assert MOIS_FR is not None
        assert isinstance(MOIS_FR, list)
        assert len(MOIS_FR) == 13  # Index 0 vide + 12 mois
        assert MOIS_FR[1] == "Janvier"
        assert MOIS_FR[12] == "Decembre"

    def test_fournisseurs_structure(self):
        """Test structure des fournisseurs connus."""
        from src.modules.maison.scan_factures import FOURNISSEURS_CONNUS

        for fournisseur, info in FOURNISSEURS_CONNUS.items():
            assert "type" in info
            assert "emoji" in info
            assert info["type"] in ["electricite", "gaz", "eau"]

    @patch("src.modules.maison.scan_factures.st")
    def test_import_image_to_base64(self, mock_st):
        """Test import fonction image_to_base64."""
        from src.modules.maison.scan_factures import image_to_base64

        assert callable(image_to_base64)

    @patch("src.modules.maison.scan_factures.st")
    def test_import_sauvegarder_facture(self, mock_st):
        """Test import fonction sauvegarder_facture."""
        from src.modules.maison.scan_factures import sauvegarder_facture

        assert callable(sauvegarder_facture)

    @patch("src.modules.maison.scan_factures.st")
    def test_import_render_upload(self, mock_st):
        """Test import fonction afficher_upload."""
        from src.modules.maison.scan_factures import afficher_upload

        assert callable(afficher_upload)

    @patch("src.modules.maison.scan_factures.st")
    def test_import_render_resultat(self, mock_st):
        """Test import fonction afficher_resultat."""
        from src.modules.maison.scan_factures import afficher_resultat

        assert callable(afficher_resultat)

    @patch("src.modules.maison.scan_factures.st")
    def test_import_render_formulaire_correction(self, mock_st):
        """Test import fonction afficher_formulaire_correction."""
        from src.modules.maison.scan_factures import afficher_formulaire_correction

        assert callable(afficher_formulaire_correction)

    @patch("src.modules.maison.scan_factures.st")
    def test_import_render_historique(self, mock_st):
        """Test import fonction afficher_historique."""
        from src.modules.maison.scan_factures import afficher_historique

        assert callable(afficher_historique)

    @patch("src.modules.maison.scan_factures.st")
    def test_import_app(self, mock_st):
        """Test import fonction app."""
        from src.modules.maison.scan_factures import app

        assert callable(app)


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


class TestHelpers:
    """Tests pour les fonctions helper."""

    def test_image_to_base64(self):
        """Test conversion image en base64."""
        from src.modules.maison.scan_factures import image_to_base64

        # Mock fichier uploadé
        mock_file = MagicMock()
        mock_file.getvalue.return_value = b"test image data"

        result = image_to_base64(mock_file)

        assert result is not None
        assert isinstance(result, str)
        # Vérifier que c'est du base64 valide
        import base64

        decoded = base64.b64decode(result)
        assert decoded == b"test image data"

    def test_image_to_base64_empty_file(self):
        """Test conversion avec fichier vide."""
        from src.modules.maison.scan_factures import image_to_base64

        mock_file = MagicMock()
        mock_file.getvalue.return_value = b""

        result = image_to_base64(mock_file)

        assert result == ""

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.obtenir_contexte_db")
    @patch("src.modules.maison.scan_factures.get_budget_service")
    def test_sauvegarder_facture_success(self, mock_get_service, mock_db_context, mock_st):
        """Test sauvegarde facture avec succès."""
        from src.services.integrations import DonneesFacture

        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db

        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.50,
            consommation=200,
            unite_consommation="kWh",
            mois_facturation=3,
            annee_facturation=2025,
            confiance=0.85,
        )

        from src.modules.maison.scan_factures import sauvegarder_facture

        result = sauvegarder_facture(donnees)

        assert result is True
        mock_service.ajouter_facture_maison.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.obtenir_contexte_db")
    @patch("src.modules.maison.scan_factures.get_budget_service")
    def test_sauvegarder_facture_with_default_date(
        self, mock_get_service, mock_db_context, mock_st
    ):
        """Test sauvegarde facture avec dates par défaut."""
        from src.services.integrations import DonneesFacture

        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db

        donnees = DonneesFacture(
            fournisseur="ENGIE",
            type_energie="gaz",
            montant_ttc=80.00,
            confiance=0.90,
        )

        from src.modules.maison.scan_factures import sauvegarder_facture

        result = sauvegarder_facture(donnees)

        assert result is True
        mock_service.ajouter_facture_maison.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.obtenir_contexte_db")
    @patch("src.modules.maison.scan_factures.get_budget_service")
    def test_sauvegarder_facture_error(self, mock_get_service, mock_db_context, mock_st):
        """Test sauvegarde facture avec erreur."""
        from src.services.integrations import DonneesFacture

        mock_get_service.side_effect = Exception("Erreur de service")

        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.50,
            confiance=0.85,
        )

        from src.modules.maison.scan_factures import sauvegarder_facture

        result = sauvegarder_facture(donnees)

        assert result is False
        mock_st.error.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.obtenir_contexte_db")
    @patch("src.modules.maison.scan_factures.get_budget_service")
    def test_sauvegarder_facture_type_mapping(self, mock_get_service, mock_db_context, mock_st):
        """Test mapping des types d'énergie vers catégories."""
        from src.services.integrations import DonneesFacture

        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db

        # Test avec type "eau"
        donnees = DonneesFacture(
            fournisseur="VEOLIA",
            type_energie="eau",
            montant_ttc=45.00,
            consommation=15,
            unite_consommation="m³",
            confiance=0.75,
        )

        from src.modules.maison.scan_factures import sauvegarder_facture

        result = sauvegarder_facture(donnees)

        assert result is True


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS RENDER UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════


class TestRenderUpload:
    """Tests pour la fonction afficher_upload."""

    @patch("src.modules.maison.scan_factures.st")
    def test_render_upload_no_file(self, mock_st):
        """Test afficher_upload sans fichier uploadé."""
        mock_st.file_uploader.return_value = None

        from src.modules.maison.scan_factures import afficher_upload

        result = afficher_upload()

        assert result is None
        mock_st.subheader.assert_called_once()
        mock_st.info.assert_called_once()
        mock_st.file_uploader.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    def test_render_upload_with_file(self, mock_st):
        """Test afficher_upload avec fichier uploadé."""
        mock_file = MagicMock()
        mock_file.name = "facture.jpg"
        mock_file.size = 1024 * 500  # 500 Ko
        mock_st.file_uploader.return_value = mock_file
        mock_st.button.return_value = False

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        from src.modules.maison.scan_factures import afficher_upload

        result = afficher_upload()

        assert result == mock_file
        mock_st.image.assert_called()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.image_to_base64")
    @patch("src.modules.maison.scan_factures.get_facture_ocr_service")
    def test_render_upload_analyze_button(self, mock_get_service, mock_to_base64, mock_st):
        """Test afficher_upload avec clic sur analyse."""
        from src.services.integrations import DonneesFacture, ResultatOCR

        mock_file = MagicMock()
        mock_file.name = "facture.jpg"
        mock_file.size = 1024 * 500
        mock_st.file_uploader.return_value = mock_file
        mock_st.button.return_value = True  # Bouton cliqué

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # Mock spinner
        mock_spinner = MagicMock()
        mock_spinner.__enter__ = MagicMock(return_value=mock_spinner)
        mock_spinner.__exit__ = MagicMock(return_value=False)
        mock_st.spinner.return_value = mock_spinner

        # Mock OCR service
        mock_service = MagicMock()
        mock_resultat = ResultatOCR(
            succes=True,
            donnees=DonneesFacture(
                fournisseur="EDF",
                type_energie="electricite",
                montant_ttc=100.0,
                confiance=0.9,
            ),
            message="OK",
        )
        mock_service.extraire_donnees_facture_sync.return_value = mock_resultat
        mock_get_service.return_value = mock_service

        mock_to_base64.return_value = "base64string"

        # Mock session_state
        mock_st.session_state = {}

        from src.modules.maison.scan_factures import afficher_upload

        afficher_upload()

        mock_st.spinner.assert_called_once()
        mock_to_base64.assert_called_once_with(mock_file)
        mock_service.extraire_donnees_facture_sync.assert_called_once_with("base64string")
        mock_st.rerun.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS RENDER RESULTAT
# ═══════════════════════════════════════════════════════════════════════════════


class TestRenderResultat:
    """Tests pour la fonction afficher_resultat."""

    @patch("src.modules.maison.scan_factures.st")
    def test_render_resultat_echec(self, mock_st):
        """Test afficher_resultat avec échec."""
        from src.services.integrations import ResultatOCR

        resultat = ResultatOCR(succes=False, message="Erreur OCR")

        from src.modules.maison.scan_factures import afficher_resultat

        afficher_resultat(resultat)

        mock_st.error.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    def test_render_resultat_no_data(self, mock_st):
        """Test afficher_resultat sans données."""
        from src.services.integrations import ResultatOCR

        resultat = ResultatOCR(succes=True, donnees=None)

        from src.modules.maison.scan_factures import afficher_resultat

        afficher_resultat(resultat)

        mock_st.warning.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    def test_render_resultat_success_high_confidence(self, mock_st):
        """Test afficher_resultat avec succès et haute confiance."""
        from src.services.integrations import DonneesFacture, ResultatOCR

        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.50,
            consommation=200,
            unite_consommation="kWh",
            confiance=0.85,
        )
        resultat = ResultatOCR(succes=True, donnees=donnees)

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        from src.modules.maison.scan_factures import afficher_resultat

        afficher_resultat(resultat)

        mock_st.subheader.assert_called_once()
        mock_st.metric.assert_called()

    @patch("src.modules.maison.scan_factures.st")
    def test_render_resultat_with_errors(self, mock_st):
        """Test afficher_resultat avec erreurs d'extraction."""
        from src.services.integrations import DonneesFacture, ResultatOCR

        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.50,
            confiance=0.50,
            erreurs=["Montant incertain", "Date non trouvée"],
        )
        resultat = ResultatOCR(succes=True, donnees=donnees)

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        from src.modules.maison.scan_factures import afficher_resultat

        afficher_resultat(resultat)

        # Vérifier que les erreurs sont affichées (2 warnings)
        assert mock_st.warning.call_count == 2

    @patch("src.modules.maison.scan_factures.st")
    def test_render_resultat_with_periode(self, mock_st):
        """Test afficher_resultat avec période de facturation."""
        from src.services.integrations import DonneesFacture, ResultatOCR

        donnees = DonneesFacture(
            fournisseur="ENGIE",
            type_energie="gaz",
            montant_ttc=80.00,
            mois_facturation=2,
            annee_facturation=2025,
            date_debut=date(2025, 1, 15),
            date_fin=date(2025, 2, 14),
            confiance=0.90,
        )
        resultat = ResultatOCR(succes=True, donnees=donnees)

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        from src.modules.maison.scan_factures import afficher_resultat

        afficher_resultat(resultat)

        # Vérifier que la période est affichée
        mock_st.markdown.assert_called()
        mock_st.caption.assert_called()

    @patch("src.modules.maison.scan_factures.st")
    def test_render_resultat_with_tarif_details(self, mock_st):
        """Test afficher_resultat avec détails tarif."""
        from src.services.integrations import DonneesFacture, ResultatOCR

        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.00,
            prix_kwh=0.1740,
            abonnement=12.50,
            confiance=0.88,
        )
        resultat = ResultatOCR(succes=True, donnees=donnees)

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        from src.modules.maison.scan_factures import afficher_resultat

        afficher_resultat(resultat)

        # Les détails tarif devraient être affichés
        mock_st.divider.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS RENDER FORMULAIRE CORRECTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestRenderFormulaireCorrection:
    """Tests pour la fonction afficher_formulaire_correction."""

    @patch("src.modules.maison.scan_factures.st")
    def test_render_formulaire_correction_display(self, mock_st):
        """Test affichage formulaire correction."""
        from src.services.integrations import DonneesFacture

        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.50,
            consommation=200,
            unite_consommation="kWh",
            mois_facturation=3,
            annee_facturation=2025,
            confiance=0.85,
        )

        # Mock form
        mock_form = MagicMock()
        mock_form.__enter__ = MagicMock(return_value=mock_form)
        mock_form.__exit__ = MagicMock(return_value=False)
        mock_st.form.return_value = mock_form

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        mock_st.form_submit_button.return_value = False

        from src.modules.maison.scan_factures import afficher_formulaire_correction

        result = afficher_formulaire_correction(donnees)

        mock_st.subheader.assert_called_once()
        mock_st.form.assert_called_once()
        assert result == donnees

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.sauvegarder_facture")
    def test_render_formulaire_correction_submit(self, mock_sauvegarder, mock_st):
        """Test soumission formulaire correction."""
        from src.services.integrations import DonneesFacture

        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.50,
            confiance=0.85,
        )

        # Mock form
        mock_form = MagicMock()
        mock_form.__enter__ = MagicMock(return_value=mock_form)
        mock_form.__exit__ = MagicMock(return_value=False)
        mock_st.form.return_value = mock_form

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # Mock form inputs
        mock_st.text_input.return_value = "EDF"
        mock_st.selectbox.side_effect = ["electricite", 3]  # type et mois
        mock_st.number_input.side_effect = [150.50, 200.0, 2025]  # montant, conso, année

        # Premier appel submit (enregistrer), second appel cancel
        mock_st.form_submit_button.side_effect = [True, False]
        mock_sauvegarder.return_value = True

        mock_st.session_state = {}

        from src.modules.maison.scan_factures import afficher_formulaire_correction

        afficher_formulaire_correction(donnees)

        mock_sauvegarder.assert_called_once()
        mock_st.success.assert_called_once()
        mock_st.rerun.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    def test_render_formulaire_correction_cancel(self, mock_st):
        """Test annulation formulaire correction."""
        from src.services.integrations import DonneesFacture

        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.50,
            confiance=0.85,
        )

        # Mock form
        mock_form = MagicMock()
        mock_form.__enter__ = MagicMock(return_value=mock_form)
        mock_form.__exit__ = MagicMock(return_value=False)
        mock_st.form.return_value = mock_form

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # Mock form inputs
        mock_st.text_input.return_value = "EDF"
        mock_st.selectbox.side_effect = ["electricite", 3]
        mock_st.number_input.side_effect = [150.50, 200.0, 2025]

        # Premier appel submit (non cliqué), second appel cancel (cliqué)
        mock_st.form_submit_button.side_effect = [False, True]

        mock_st.session_state = {"ocr_resultat": MagicMock()}

        from src.modules.maison.scan_factures import afficher_formulaire_correction

        afficher_formulaire_correction(donnees)

        assert "ocr_resultat" not in mock_st.session_state
        mock_st.rerun.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS RENDER HISTORIQUE
# ═══════════════════════════════════════════════════════════════════════════════


class TestRenderHistorique:
    """Tests pour la fonction afficher_historique."""

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.obtenir_contexte_db")
    def test_render_historique_empty(self, mock_db_context, mock_st):
        """Test historique vide."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_db_context.return_value.__enter__.return_value = mock_db

        from src.modules.maison.scan_factures import afficher_historique

        afficher_historique()

        mock_st.subheader.assert_called_once()
        mock_st.caption.assert_called()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.obtenir_contexte_db")
    def test_render_historique_with_data(self, mock_db_context, mock_st):
        """Test historique avec données."""
        mock_facture = MagicMock()
        mock_facture.categorie = "electricite"
        mock_facture.fournisseur = "EDF"
        mock_facture.mois = 2
        mock_facture.annee = 2025
        mock_facture.montant = 150.50
        mock_facture.consommation = 200

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_facture
        ]
        mock_db_context.return_value.__enter__.return_value = mock_db

        # Mock container
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value = mock_container

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        from src.modules.maison.scan_factures import afficher_historique

        afficher_historique()

        mock_st.subheader.assert_called_once()
        mock_st.container.assert_called()
        mock_st.metric.assert_called()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.obtenir_contexte_db")
    def test_render_historique_db_error(self, mock_db_context, mock_st):
        """Test historique avec erreur DB."""
        mock_db_context.return_value.__enter__.side_effect = Exception("Erreur DB")

        from src.modules.maison.scan_factures import afficher_historique

        afficher_historique()

        mock_st.error.assert_called()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.obtenir_contexte_db")
    def test_render_historique_gaz(self, mock_db_context, mock_st):
        """Test historique avec facture gaz."""
        mock_facture = MagicMock()
        mock_facture.categorie = "gaz"
        mock_facture.fournisseur = "ENGIE"
        mock_facture.mois = 1
        mock_facture.annee = 2025
        mock_facture.montant = 80.00
        mock_facture.consommation = 150

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_facture
        ]
        mock_db_context.return_value.__enter__.return_value = mock_db

        # Mock container
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value = mock_container

        # Mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        from src.modules.maison.scan_factures import afficher_historique

        afficher_historique()

        mock_st.subheader.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS APP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════


class TestApp:
    """Tests pour la fonction app principale."""

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.afficher_upload")
    @patch("src.modules.maison.scan_factures.afficher_historique")
    def test_app_initial_state(self, mock_historique, mock_upload, mock_st):
        """Test app sans résultat OCR en session."""
        mock_st.session_state = {}

        # Mock tabs
        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_tab1.__enter__ = MagicMock(return_value=mock_tab1)
        mock_tab1.__exit__ = MagicMock(return_value=False)
        mock_tab2.__enter__ = MagicMock(return_value=mock_tab2)
        mock_tab2.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab1, mock_tab2]

        from src.modules.maison.scan_factures import app

        app()

        mock_st.title.assert_called_once()
        mock_st.caption.assert_called_once()
        mock_st.tabs.assert_called_once()
        mock_upload.assert_called_once()
        mock_historique.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.afficher_resultat")
    @patch("src.modules.maison.scan_factures.afficher_formulaire_correction")
    @patch("src.modules.maison.scan_factures.afficher_historique")
    def test_app_with_ocr_result(self, mock_historique, mock_correction, mock_resultat, mock_st):
        """Test app avec résultat OCR en session."""
        from src.services.integrations import DonneesFacture, ResultatOCR

        mock_donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=150.00,
            confiance=0.9,
        )
        mock_ocr = ResultatOCR(succes=True, donnees=mock_donnees)

        mock_st.session_state = {"ocr_resultat": mock_ocr}

        # Mock tabs
        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_tab1.__enter__ = MagicMock(return_value=mock_tab1)
        mock_tab1.__exit__ = MagicMock(return_value=False)
        mock_tab2.__enter__ = MagicMock(return_value=mock_tab2)
        mock_tab2.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab1, mock_tab2]

        from src.modules.maison.scan_factures import app

        app()

        mock_resultat.assert_called_once()
        mock_correction.assert_called_once()
        mock_historique.assert_called_once()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.afficher_upload")
    @patch("src.modules.maison.scan_factures.afficher_historique")
    def test_app_with_failed_ocr(self, mock_historique, mock_upload, mock_st):
        """Test app avec OCR échoué."""
        from src.services.integrations import ResultatOCR

        mock_ocr = ResultatOCR(succes=False, message="Erreur extraction")

        mock_st.session_state = {"ocr_resultat": mock_ocr}

        # Mock tabs
        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_tab1.__enter__ = MagicMock(return_value=mock_tab1)
        mock_tab1.__exit__ = MagicMock(return_value=False)
        mock_tab2.__enter__ = MagicMock(return_value=mock_tab2)
        mock_tab2.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab1, mock_tab2]

        from src.modules.maison.scan_factures import app

        app()

        mock_upload.assert_called_once()
        mock_st.error.assert_called()

    @patch("src.modules.maison.scan_factures.st")
    @patch("src.modules.maison.scan_factures.afficher_upload")
    @patch("src.modules.maison.scan_factures.afficher_historique")
    def test_app_tabs_structure(self, mock_historique, mock_upload, mock_st):
        """Test structure des onglets."""
        mock_st.session_state = {}

        # Mock tabs
        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_tab1.__enter__ = MagicMock(return_value=mock_tab1)
        mock_tab1.__exit__ = MagicMock(return_value=False)
        mock_tab2.__enter__ = MagicMock(return_value=mock_tab2)
        mock_tab2.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab1, mock_tab2]

        from src.modules.maison.scan_factures import app

        app()

        # Vérifier que les tabs sont créés avec les bons noms
        mock_st.tabs.assert_called_once_with(["📤 Scanner", "📋 Historique"])
        pass
