"""
Onglet Rapport Budget - UI Streamlit
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from src.core.session_keys import SK
from src.ui.fragments import cached_fragment

from .rapports_stocks import get_rapports_service


@cached_fragment(ttl=600)
def afficher_rapport_budget():
    """Rapport budget/depenses"""

    service = get_rapports_service()

    st.subheader("💡 Rapport Budget/Depenses")

    st.markdown("""
    Analysez vos depenses alimentaires:
    - Depenses totales et par categorie
    - Articles les plus coûteux
    - Évolution des depenses
    - Budget par categorie
    """)

    st.divider()

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        periode = st.selectbox(
            "Periode du rapport:",
            [(7, "7 jours"), (14, "2 semaines"), (30, "1 mois"), (90, "3 mois"), (365, "1 an")],
            format_func=lambda x: x[1],
            key="periode_budget",
            index=2,
        )[0]

    with col2:
        if st.button("🧹 Aperçu", key="btn_preview_budget", use_container_width=True):
            st.session_state[SK.PREVIEW_BUDGET] = True

    with col3:
        if st.button("📥 Télécharger PDF", key="btn_download_budget", use_container_width=True):
            st.session_state[SK.DOWNLOAD_BUDGET] = True

    # Aperçu
    if st.session_state.get(SK.PREVIEW_BUDGET):
        try:
            donnees = service.generer_donnees_rapport_budget(periode)

            # Resume financier
            st.info("📅 **RÉSUMÉ FINANCIER**")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Depenses totales", f"€{donnees.depenses_total:.2f}")

            with col2:
                if donnees.periode_jours > 0:
                    moy_jour = donnees.depenses_total / donnees.periode_jours
                    st.metric("Moyenne par jour", f"€{moy_jour:.2f}")

            with col3:
                st.metric("Periode", f"{donnees.periode_jours} jours")

            # Depenses par categorie
            if donnees.depenses_par_categorie:
                st.subheader("📊 Depenses par categorie")

                cat_data = []
                for cat, montant in donnees.depenses_par_categorie.items():
                    pct = (
                        (montant / donnees.depenses_total * 100)
                        if donnees.depenses_total > 0
                        else 0
                    )
                    cat_data.append(
                        {
                            "Categorie": cat,
                            "Montant €": f"{montant:.2f}",
                            "% du total": f"{pct:.1f}%",
                        }
                    )

                df_cat = pd.DataFrame(cat_data)
                st.dataframe(df_cat, width="stretch", hide_index=True)

                # Graphique
                cat_values = sorted(
                    donnees.depenses_par_categorie.items(), key=lambda x: x[1], reverse=True
                )
                chart_data = pd.DataFrame(cat_values, columns=["Categorie", "Montant"])
                st.bar_chart(chart_data.set_index("Categorie"))

            # Articles coûteux
            if donnees.articles_couteux:
                st.subheader("⭐ Articles les plus coûteux")
                df_couteux = pd.DataFrame(donnees.articles_couteux)
                st.dataframe(
                    df_couteux.rename(
                        columns={
                            "nom": "Article",
                            "categorie": "Categorie",
                            "quantite": "Quantite",
                            "unite": "Unite",
                            "prix_unitaire": "Prix unitaire €",
                            "cout_total": "Coût total €",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Prix unitaire €": st.column_config.NumberColumn(format="€%.2f"),
                        "Coût total €": st.column_config.NumberColumn(format="€%.2f"),
                    },
                )

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

    # Telechargement
    if st.session_state.get(SK.DOWNLOAD_BUDGET):
        try:
            pdf = service.generer_pdf_rapport_budget(periode)
            filename = f"rapport_budget_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            st.download_button(
                label="📥 Télécharger le PDF",
                data=pdf.getvalue(),
                file_name=filename,
                mime="application/pdf",
                key="download_button_budget",
            )
            st.success("✅ PDF généré - Cliquez sur le bouton pour télécharger")
            st.session_state[SK.DOWNLOAD_BUDGET] = False

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
