"""
Outils utilitaires pour les courses.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.services.cuisine.courses import obtenir_service_courses
from src.ui.fragments import ui_fragment

from .budget_ui import afficher_budget_courses
from .scan_ticket_ui import afficher_scan_ticket


@ui_fragment
def afficher_outils():
    """Outils utilitaires: Budget, Scan Ticket, Export/Import."""
    st.subheader("🔧 Outils")

    tab_budget, tab_ticket, tab_export = st.tabs(
        ["💰 Budget", "🧾 Scan Ticket", "💾 Export/Import"]
    )

    with tab_budget:
        afficher_budget_courses()

    with tab_ticket:
        afficher_scan_ticket()

    with tab_export:
        _afficher_export_import()


def _afficher_export_import():
    """Exporter/Importer des listes de courses."""
    st.write("**Exporter/Importer listes**")

    col1, col2 = st.columns(2)
    with col1:
        service = obtenir_service_courses()
        liste = service.get_liste_courses(achetes=False)

        if liste:
            df = pd.DataFrame(
                [
                    {
                        "Article": a.get("ingredient_nom"),
                        "Quantité": a.get("quantite_necessaire"),
                        "Unité": a.get("unite"),
                        "Priorité": a.get("priorite"),
                        "Rayon": a.get("rayon_magasin"),
                        "Notes": a.get("notes", ""),
                    }
                    for a in liste
                ]
            )

            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger liste (CSV)",
                data=csv,
                file_name=f"liste_courses_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

    with col2:
        uploaded = st.file_uploader("📤 Importer liste (CSV)", type=["csv"], key="import_csv")
        if uploaded:
            try:
                import io

                df_import = pd.read_csv(io.BytesIO(uploaded.getvalue()))
                st.write(f"✅ Fichier contient {len(df_import)} articles")

                if st.button("✅ Confirmer import"):
                    service = obtenir_service_courses()
                    count = service.importer_articles_csv(df_import.to_dict("records"))
                    st.success(f"✅ {count} articles importés!")
                    st.session_state[SK.COURSES_REFRESH] += 1
                    rerun()
            except Exception as e:
                st.error(f"❌ Erreur import: {str(e)}")


__all__ = ["afficher_outils"]
