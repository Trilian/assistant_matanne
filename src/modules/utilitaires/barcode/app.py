"""
Point d'entrée module scanner barcode.
"""

from __future__ import annotations

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

_keys = KeyNamespace("barcode")

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


@profiler_rerun("barcode")
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
    TAB_LABELS = [
        "📷 Scanner",
        "➕ Ajout rapide",
        "✅ Vérifier stock",
        "📊 Gestion",
        "📥 Import/Export",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur scanner"):
            afficher_scanner()

    with tab2:
        with error_boundary(titre="Erreur ajout rapide"):
            afficher_ajout_rapide()

    with tab3:
        with error_boundary(titre="Erreur vérifier stock"):
            afficher_verifier_stock()

    with tab4:
        with error_boundary(titre="Erreur gestion barcodes"):
            afficher_gestion_barcodes()

    with tab5:
        with error_boundary(titre="Erreur import/export"):
            afficher_import_export()


# ═══════════════════════════════════════════════════════════
# PAGE ENTRY
# ═══════════════════════════════════════════════════════════


if __name__ == "__main__":
    app()
