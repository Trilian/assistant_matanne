"""Jardin - Onglet export CSV.

Extrait de onglets.py (Phase 4 Audit, item 18 — split >500 LOC).
"""

import logging

import streamlit as st

from src.ui import etat_vide
from src.ui.fragments import lazy, ui_fragment

from .data import charger_catalogue_plantes

# Import pandas pour export
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

logger = logging.getLogger(__name__)


@lazy(condition=lambda: st.session_state.get("jardin_export_ready", False), show_skeleton=True)
def _export_data_panel(mes_plantes: list[dict], recoltes: list[dict]):
    """Panneau export CSV (chargé conditionnellement)."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌱 Mes Plantations")

        if not mes_plantes:
            etat_vide("Aucune plantation à exporter", "🌱")
        else:
            catalogue = charger_catalogue_plantes()

            df_plantes = pd.DataFrame(
                [
                    {
                        "Plante": catalogue.get("plantes", {})
                        .get(p.get("plante_id"), {})
                        .get("nom", p.get("plante_id")),
                        "Surface (m²)": p.get("surface_m2", 0),
                        "Quantité": p.get("quantite", 0),
                        "Zone": p.get("zone", ""),
                        "Semis fait": "Oui" if p.get("semis_fait") else "Non",
                        "En terre": "Oui" if p.get("plante_en_terre") else "Non",
                        "Date ajout": p.get("date_ajout", ""),
                    }
                    for p in mes_plantes
                ]
            )

            st.dataframe(df_plantes, use_container_width=True, height=250)

            csv = df_plantes.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger Plantations CSV",
                data=csv,
                file_name="jardin_plantations.csv",
                mime="text/csv",
            )

    with col2:
        st.markdown("### 🍅 Mes Récoltes")

        if not recoltes:
            etat_vide("Aucune récolte à exporter", "🍅")
        else:
            catalogue = charger_catalogue_plantes()

            df_recoltes = pd.DataFrame(
                [
                    {
                        "Plante": catalogue.get("plantes", {})
                        .get(r.get("plante_id"), {})
                        .get("nom", r.get("plante_id")),
                        "Quantité (kg)": r.get("quantite_kg", 0),
                        "Date": r.get("date", ""),
                        "Notes": r.get("notes", ""),
                    }
                    for r in recoltes
                ]
            )

            st.dataframe(df_recoltes, use_container_width=True, height=250)

            csv = df_recoltes.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger Récoltes CSV",
                data=csv,
                file_name="jardin_recoltes.csv",
                mime="text/csv",
            )


@ui_fragment
def onglet_export(mes_plantes: list[dict], recoltes: list[dict]):
    """Onglet export CSV des données jardin."""
    st.subheader("📥 Export des données")

    if not HAS_PANDAS:
        st.warning("📦 Pandas non installé. `pip install pandas` pour l'export.")
        return

    st.checkbox(
        "📂 Préparer les données pour l'export",
        key="jardin_export_ready",
        help="Charge les tableaux de données pour téléchargement",
    )
    _export_data_panel(mes_plantes, recoltes)
