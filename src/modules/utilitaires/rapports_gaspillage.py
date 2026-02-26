"""
Onglet Analyse Gaspillage - UI Streamlit
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from src.core.session_keys import SK
from src.ui.fragments import cached_fragment

from .rapports_stocks import get_rapports_service


@cached_fragment(ttl=600)
def afficher_analyse_gaspillage():
    """Analyse gaspillage"""

    service = get_rapports_service()

    st.subheader("🎯 Analyse Gaspillage")

    st.markdown("""
    Identifiez et reduisez le gaspillage:
    - Articles perimes et valeur perdue
    - Gaspillage par categorie
    - Recommandations de reduction
    - Tendances et patterns
    """)

    st.divider()

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        periode = st.selectbox(
            "Periode d'analyse:",
            [(7, "7 jours"), (14, "2 semaines"), (30, "1 mois"), (90, "3 mois")],
            format_func=lambda x: x[1],
            key="periode_gaspillage",
            index=2,
        )[0]

    with col2:
        if st.button("🧹 Aperçu", key="btn_preview_gaspillage", use_container_width=True):
            st.session_state[SK.PREVIEW_GASPILLAGE] = True

    with col3:
        if st.button("📥 Télécharger PDF", key="btn_download_gaspillage", use_container_width=True):
            st.session_state[SK.DOWNLOAD_GASPILLAGE] = True

    # Aperçu
    if st.session_state.get(SK.PREVIEW_GASPILLAGE):
        try:
            analyse = service.generer_analyse_gaspillage(periode)

            # Resume
            st.warning("⚠️ **RÉSUMÉ GASPILLAGE**")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Articles perimes", analyse.articles_perimes_total)

            with col2:
                st.metric("Valeur perdue", f"€{analyse.valeur_perdue:.2f}")

            with col3:
                if analyse.articles_perimes_total > 0:
                    moy_perte = analyse.valeur_perdue / analyse.articles_perimes_total
                    st.metric("Moyenne perte", f"€{moy_perte:.2f}")

            # Recommandations
            if analyse.recommandations:
                st.subheader("💰 Recommandations")
                for rec in analyse.recommandations:
                    st.info(rec)

            # Gaspillage par categorie
            if analyse.categories_gaspillage:
                st.subheader("📊 Gaspillage par categorie")

                cat_data = []
                for cat, data in sorted(
                    analyse.categories_gaspillage.items(),
                    key=lambda x: x[1]["valeur"],
                    reverse=True,
                ):
                    cat_data.append(
                        {
                            "Categorie": cat,
                            "Articles": data["articles"],
                            "Valeur perdue €": f"{data['valeur']:.2f}",
                        }
                    )

                df_cat = pd.DataFrame(cat_data)
                st.dataframe(df_cat, width="stretch", hide_index=True)

            # Articles detail
            if analyse.articles_perimes_detail:
                st.subheader("❌ Articles perimes (detail)")
                df_detail = pd.DataFrame(analyse.articles_perimes_detail)
                st.dataframe(
                    df_detail.rename(
                        columns={
                            "nom": "Article",
                            "date_peremption": "Date peremption",
                            "jours_perime": "Jours ecart",
                            "quantite": "Quantite",
                            "unite": "Unite",
                            "valeur_perdue": "Valeur perdue €",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Valeur perdue €": st.column_config.NumberColumn(format="€%.2f")
                    },
                )

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

    # Telechargement
    if st.session_state.get(SK.DOWNLOAD_GASPILLAGE):
        try:
            pdf = service.generer_pdf_analyse_gaspillage(periode)
            filename = f"analyse_gaspillage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            st.download_button(
                label="📥 Télécharger le PDF",
                data=pdf.getvalue(),
                file_name=filename,
                mime="application/pdf",
                key="download_button_gaspillage",
            )
            st.success("✅ PDF généré - Cliquez sur le bouton pour télécharger")
            st.session_state[SK.DOWNLOAD_GASPILLAGE] = False

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
