"""
Point d'entrée module scanner barcode.
"""

from __future__ import annotations


# ═══════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════


def get_barcode_service() -> BarcodeService:
    """Get ou creer service barcode"""
    from src.modules.utilitaires.barcode import BarcodeService, st

    if "barcode_service" not in st.session_state:
        st.session_state.barcode_service = BarcodeService()
    return st.session_state.barcode_service


# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entree module scanner barcode"""

    from src.modules.utilitaires.barcode import (
        afficher_ajout_rapide,
        afficher_gestion_barcodes,
        afficher_import_export,
        afficher_scanner,
        afficher_verifier_stock,
        st,
    )

    st.markdown(
        "<h1 style='text-align: center;'>💰 Scanner Code-Barres/QR</h1>",
        unsafe_allow_html=True,
    )

    st.markdown("Scannez codes-barres, QR codes pour gestion rapide inventaire")
    st.markdown("---")

    # Onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📷 Scanner", "➕ Ajout rapide", "✅ Vérifier stock", "📊 Gestion", "📥 Import/Export"]
    )

    with tab1:
        afficher_scanner()

    with tab2:
        afficher_ajout_rapide()

    with tab3:
        afficher_verifier_stock()

    with tab4:
        afficher_gestion_barcodes()

    with tab5:
        afficher_import_export()


# ═══════════════════════════════════════════════════════════
# PAGE ENTRY
# ═══════════════════════════════════════════════════════════


if __name__ == "__main__":
    app()
