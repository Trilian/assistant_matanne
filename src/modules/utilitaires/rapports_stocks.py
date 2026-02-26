"""
Onglet Rapport Stocks - UI Streamlit
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from src.core.session_keys import SK
from src.ui.fragments import cached_fragment


def get_rapports_service():
    """Get ou creer service rapports (via registre singleton)."""
    from src.services.rapports import obtenir_service_rapports_pdf

    return obtenir_service_rapports_pdf()


@cached_fragment(ttl=600)
def afficher_rapport_stocks():
    """Rapport hebdo stocks"""

    service = get_rapports_service()

    st.subheader("📦 Rapport Stocks Hebdomadaire")

    st.markdown("""
    Generez un rapport detaille de votre stock chaque semaine:
    - Vue d'ensemble du stock total
    - Articles en faible stock
    - Articles perimes
    - Valeur du stock par categorie
    """)

    st.divider()

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        periode = st.selectbox(
            "Periode du rapport:",
            [(7, "Derniers 7 jours"), (14, "2 semaines"), (30, "1 mois")],
            format_func=lambda x: x[1],
            key="periode_stocks",
        )[0]

    with col2:
        if st.button("🧹 Aperçu", key="btn_preview_stocks", use_container_width=True):
            st.session_state[SK.PREVIEW_STOCKS] = True

    with col3:
        if st.button("📥 Télécharger PDF", key="btn_download_stocks", use_container_width=True):
            st.session_state[SK.DOWNLOAD_STOCKS] = True

    # Aperçu
    if st.session_state.get(SK.PREVIEW_STOCKS):
        try:
            donnees = service.generer_donnees_rapport_stocks(periode)

            # Resume general
            st.info("📍**RÉSUMÉ GÉNÉRAL**")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total articles", donnees.articles_total)

            with col2:
                st.metric("Valeur stock", f"€{donnees.valeur_stock_total:.2f}")

            with col3:
                st.metric("Faible stock", len(donnees.articles_faible_stock))

            with col4:
                st.metric("Perimes", len(donnees.articles_perimes))

            # Articles faible stock
            if donnees.articles_faible_stock:
                st.subheader("⚠️ Articles en faible stock")
                df_faible = pd.DataFrame(donnees.articles_faible_stock)
                st.dataframe(
                    df_faible.rename(
                        columns={
                            "nom": "Article",
                            "quantite": "Stock",
                            "quantite_min": "Minimum",
                            "unite": "Unite",
                            "emplacement": "Emplacement",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            # Articles perimes
            if donnees.articles_perimes:
                st.subheader("❌ Articles perimes")
                df_perimes = pd.DataFrame(donnees.articles_perimes)
                df_perimes["date_peremption"] = pd.to_datetime(
                    df_perimes["date_peremption"]
                ).dt.strftime("%d/%m/%Y")
                st.dataframe(
                    df_perimes.rename(
                        columns={
                            "nom": "Article",
                            "date_peremption": "Date peremption",
                            "jours_perime": "Jours ecart",
                            "quantite": "Quantite",
                            "unite": "Unite",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            # Categories
            if donnees.categories_resumee:
                st.subheader("📊 Stock par categorie")
                cat_data = []
                for cat, data in donnees.categories_resumee.items():
                    cat_data.append(
                        {
                            "Categorie": cat,
                            "Articles": data["articles"],
                            "Quantite": data["quantite"],
                            "Valeur €": data["valeur"],
                        }
                    )
                df_cat = pd.DataFrame(cat_data)
                st.dataframe(df_cat, width="stretch", hide_index=True)

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

    # Telechargement
    if st.session_state.get(SK.DOWNLOAD_STOCKS):
        try:
            pdf = service.generer_pdf_rapport_stocks(periode)
            filename = f"rapport_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            st.download_button(
                label="📥 Télécharger le PDF",
                data=pdf.getvalue(),
                file_name=filename,
                mime="application/pdf",
                key="download_button_stocks",
            )
            st.success("✅ PDF généré - Cliquez sur le bouton pour télécharger")
            st.session_state[SK.DOWNLOAD_STOCKS] = False

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
