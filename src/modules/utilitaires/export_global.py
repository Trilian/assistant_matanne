"""
Module Export Global — Hub centralisé d'export multi-format.

Exporte les données de tous les domaines (recettes, courses, inventaire,
dépenses, planning, notes, contacts) en JSON, CSV, Excel ou ZIP.
"""

import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.export_service import DOMAINES_EXPORT, get_export_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("export_global")


@profiler_rerun("export_global")
def app():
    """Point d'entrée module Export Global."""
    st.title("📦 Export Global de Données")
    st.caption("Exportez vos données familiales en JSON, CSV, Excel ou ZIP")

    with error_boundary(titre="Erreur export"):
        service = get_export_service()

        # Sélection des domaines
        st.subheader("📋 Sélection des données")

        domaines_disponibles = {k: v["label"] for k, v in DOMAINES_EXPORT.items()}

        selectionnes = []
        cols = st.columns(3)
        for i, (key, label) in enumerate(domaines_disponibles.items()):
            with cols[i % 3]:
                try:
                    count = service.compter(key)
                    aide = f"{count} enregistrements"
                except Exception:
                    count = 0
                    aide = "Non disponible"

                if st.checkbox(
                    f"{label} ({count})",
                    key=_keys("dom", key),
                    disabled=count == 0,
                    help=aide,
                ):
                    selectionnes.append(key)

        if not selectionnes:
            st.info("👆 Sélectionnez au moins un domaine à exporter.")
            return

        st.divider()

        # Aperçu
        with st.expander("👁️ Aperçu des données", expanded=False):
            for domaine in selectionnes:
                st.markdown(f"**{DOMAINES_EXPORT[domaine]['label']}**")
                try:
                    apercu = service.apercu(domaine, limite=3)
                    if apercu:
                        st.dataframe(apercu, use_container_width=True)
                    else:
                        st.caption("Aucune donnée")
                except Exception as e:
                    st.warning(f"Erreur aperçu: {e}")

        st.divider()

        # Choix du format et export
        st.subheader("📥 Format d'export")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📄 JSON", key=_keys("json"), use_container_width=True, type="primary"):
                with st.spinner("Export JSON..."):
                    data = service.exporter_json(selectionnes)
                    st.download_button(
                        "⬇️ Télécharger JSON",
                        data=data,
                        file_name="matanne_export.json",
                        mime="application/json",
                        key=_keys("dl_json"),
                    )

        with col2:
            if st.button("📊 Excel", key=_keys("excel"), use_container_width=True):
                with st.spinner("Export Excel..."):
                    data = service.exporter_excel(selectionnes)
                    st.download_button(
                        "⬇️ Télécharger Excel",
                        data=data,
                        file_name="matanne_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=_keys("dl_excel"),
                    )

        with col3:
            if st.button("📁 ZIP (CSV)", key=_keys("zip_csv"), use_container_width=True):
                with st.spinner("Export ZIP..."):
                    data = service.exporter_zip(selectionnes, format_csv=True)
                    st.download_button(
                        "⬇️ Télécharger ZIP",
                        data=data,
                        file_name="matanne_export_csv.zip",
                        mime="application/zip",
                        key=_keys("dl_zip"),
                    )

        with col4:
            if st.button("📁 ZIP (JSON)", key=_keys("zip_json"), use_container_width=True):
                with st.spinner("Export ZIP..."):
                    data = service.exporter_zip(selectionnes, format_csv=False)
                    st.download_button(
                        "⬇️ Télécharger ZIP",
                        data=data,
                        file_name="matanne_export_json.zip",
                        mime="application/zip",
                        key=_keys("dl_zip_json"),
                    )

        # Résumé
        st.divider()
        total = sum(service.compter(d) for d in selectionnes)
        st.metric("📊 Total enregistrements sélectionnés", total)
