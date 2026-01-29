"""
Module Rapports PDF - Interface Streamlit

âœ… Rapport hebdo stocks
âœ… Rapport budget/dépenses  
âœ… Analyse gaspillage
âœ… Export professionnel
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from src.core.state import StateManager, get_state
from src.services.rapports_pdf import RapportsPDFService

# Logique métier pure
from src.domains.shared.logic.rapports_logic import (
    generer_rapport_synthese,
    calculer_statistiques_periode
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# INITIALISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def get_rapports_service() -> RapportsPDFService:
    """Get ou créer service rapports"""
    if "rapports_service" not in st.session_state:
        st.session_state.rapports_service = RapportsPDFService()
    return st.session_state.rapports_service


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODULE PRINCIPAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def app():
    """Point d'entrée module rapports PDF"""
    
    st.markdown(
        "<h1 style='text-align: center;'>[CHART] Rapports PDF</h1>",
        unsafe_allow_html=True,
    )
    
    st.markdown("Générez des rapports professionnels pour votre gestion")
    st.markdown("---")
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "[PKG] Stocks",
        "ðŸ’° Budget",
        "ðŸ—‘ï¸ Gaspillage",
        "ðŸ“ˆ Historique"
    ])
    
    with tab1:
        render_rapport_stocks()
    
    with tab2:
        render_rapport_budget()
    
    with tab3:
        render_analyse_gaspillage()
    
    with tab4:
        render_historique()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ONGLET 1: RAPPORT STOCKS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_rapport_stocks():
    """Rapport hebdo stocks"""
    
    service = get_rapports_service()
    
    st.subheader("[PKG] Rapport Stocks Hebdomadaire")
    
    st.markdown("""
    Générez un rapport détaillé de votre stock chaque semaine:
    - Vue d'ensemble du stock total
    - Articles en faible stock
    - Articles périmés
    - Valeur du stock par catégorie
    """)
    
    st.divider()
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        periode = st.selectbox(
            "Période du rapport:",
            [(7, "Derniers 7 jours"), (14, "2 semaines"), (30, "1 mois")],
            format_func=lambda x: x[1],
            key="periode_stocks"
        )[0]
    
    with col2:
        if st.button("ðŸ‘ï¸ Aperçu", key="btn_preview_stocks", use_container_width=True):
            st.session_state.preview_stocks = True
    
    with col3:
        if st.button("ðŸ“¥ Télécharger PDF", key="btn_download_stocks", use_container_width=True):
            st.session_state.download_stocks = True
    
    # Aperçu
    if st.session_state.get("preview_stocks"):
        try:
            donnees = service.generer_donnees_rapport_stocks(periode)
            
            # Résumé général
            st.info("ðŸ” **RÃ‰SUMÃ‰ GÃ‰NÃ‰RAL**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total articles", donnees.articles_total)
            
            with col2:
                st.metric("Valeur stock", f"â‚¬{donnees.valeur_stock_total:.2f}")
            
            with col3:
                st.metric("Faible stock", len(donnees.articles_faible_stock))
            
            with col4:
                st.metric("Périmés", len(donnees.articles_perimes))
            
            # Articles faible stock
            if donnees.articles_faible_stock:
                st.subheader("âš ï¸ Articles en faible stock")
                df_faible = pd.DataFrame(donnees.articles_faible_stock)
                st.dataframe(
                    df_faible.rename(columns={
                        "nom": "Article",
                        "quantite": "Stock",
                        "quantite_min": "Minimum",
                        "unite": "Unité",
                        "emplacement": "Emplacement"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            
            # Articles périmés
            if donnees.articles_perimes:
                st.subheader("âŒ Articles périmés")
                df_perimes = pd.DataFrame(donnees.articles_perimes)
                df_perimes["date_peremption"] = pd.to_datetime(df_perimes["date_peremption"]).dt.strftime('%d/%m/%Y')
                st.dataframe(
                    df_perimes.rename(columns={
                        "nom": "Article",
                        "date_peremption": "Date péremption",
                        "jours_perime": "Jours écart",
                        "quantite": "Quantité",
                        "unite": "Unité"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            
            # Catégories
            if donnees.categories_resumee:
                st.subheader("[CHART] Stock par catégorie")
                cat_data = []
                for cat, data in donnees.categories_resumee.items():
                    cat_data.append({
                        "Catégorie": cat,
                        "Articles": data["articles"],
                        "Quantité": data["quantite"],
                        "Valeur â‚¬": data["valeur"]
                    })
                df_cat = pd.DataFrame(cat_data)
                st.dataframe(
                    df_cat,
                    use_container_width=True,
                    hide_index=True
                )
        
        except Exception as e:
            st.error(f"âŒ Erreur: {str(e)}")
    
    # Téléchargement
    if st.session_state.get("download_stocks"):
        try:
            pdf = service.generer_pdf_rapport_stocks(periode)
            filename = f"rapport_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            st.download_button(
                label="ðŸ“¥ Télécharger le PDF",
                data=pdf.getvalue(),
                file_name=filename,
                mime="application/pdf",
                key="download_button_stocks"
            )
            st.success("âœ… PDF généré - Cliquez sur le bouton pour télécharger")
            st.session_state.download_stocks = False
        
        except Exception as e:
            st.error(f"âŒ Erreur: {str(e)}")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ONGLET 2: RAPPORT BUDGET
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_rapport_budget():
    """Rapport budget/dépenses"""
    
    service = get_rapports_service()
    
    st.subheader("ðŸ’° Rapport Budget/Dépenses")
    
    st.markdown("""
    Analysez vos dépenses alimentaires:
    - Dépenses totales et par catégorie
    - Articles les plus coûteux
    - Ã‰volution des dépenses
    - Budget par catégorie
    """)
    
    st.divider()
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        periode = st.selectbox(
            "Période du rapport:",
            [(7, "7 jours"), (14, "2 semaines"), (30, "1 mois"), (90, "3 mois"), (365, "1 an")],
            format_func=lambda x: x[1],
            key="periode_budget",
            index=2
        )[0]
    
    with col2:
        if st.button("ðŸ‘ï¸ Aperçu", key="btn_preview_budget", use_container_width=True):
            st.session_state.preview_budget = True
    
    with col3:
        if st.button("ðŸ“¥ Télécharger PDF", key="btn_download_budget", use_container_width=True):
            st.session_state.download_budget = True
    
    # Aperçu
    if st.session_state.get("preview_budget"):
        try:
            donnees = service.generer_donnees_rapport_budget(periode)
            
            # Résumé financier
            st.info("ðŸ’µ **RÃ‰SUMÃ‰ FINANCIER**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Dépenses totales", f"â‚¬{donnees.depenses_total:.2f}")
            
            with col2:
                if donnees.periode_jours > 0:
                    moy_jour = donnees.depenses_total / donnees.periode_jours
                    st.metric("Moyenne par jour", f"â‚¬{moy_jour:.2f}")
            
            with col3:
                st.metric("Période", f"{donnees.periode_jours} jours")
            
            # Dépenses par catégorie
            if donnees.depenses_par_categorie:
                st.subheader("[CHART] Dépenses par catégorie")
                
                cat_data = []
                for cat, montant in donnees.depenses_par_categorie.items():
                    pct = (montant / donnees.depenses_total * 100) if donnees.depenses_total > 0 else 0
                    cat_data.append({
                        "Catégorie": cat,
                        "Montant â‚¬": f"{montant:.2f}",
                        "% du total": f"{pct:.1f}%"
                    })
                
                df_cat = pd.DataFrame(cat_data)
                st.dataframe(
                    df_cat,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Graphique
                cat_values = sorted(
                    donnees.depenses_par_categorie.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                chart_data = pd.DataFrame(cat_values, columns=['Catégorie', 'Montant'])
                st.bar_chart(chart_data.set_index('Catégorie'))
            
            # Articles coûteux
            if donnees.articles_couteux:
                st.subheader("â­ Articles les plus coûteux")
                df_couteux = pd.DataFrame(donnees.articles_couteux)
                st.dataframe(
                    df_couteux.rename(columns={
                        "nom": "Article",
                        "categorie": "Catégorie",
                        "quantite": "Quantité",
                        "unite": "Unité",
                        "prix_unitaire": "Prix unitaire â‚¬",
                        "cout_total": "Coût total â‚¬"
                    }),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Prix unitaire â‚¬": st.column_config.NumberColumn(format="â‚¬%.2f"),
                        "Coût total â‚¬": st.column_config.NumberColumn(format="â‚¬%.2f")
                    }
                )
        
        except Exception as e:
            st.error(f"âŒ Erreur: {str(e)}")
    
    # Téléchargement
    if st.session_state.get("download_budget"):
        try:
            pdf = service.generer_pdf_rapport_budget(periode)
            filename = f"rapport_budget_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            st.download_button(
                label="ðŸ“¥ Télécharger le PDF",
                data=pdf.getvalue(),
                file_name=filename,
                mime="application/pdf",
                key="download_button_budget"
            )
            st.success("âœ… PDF généré - Cliquez sur le bouton pour télécharger")
            st.session_state.download_budget = False
        
        except Exception as e:
            st.error(f"âŒ Erreur: {str(e)}")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ONGLET 3: ANALYSE GASPILLAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_analyse_gaspillage():
    """Analyse gaspillage"""
    
    service = get_rapports_service()
    
    st.subheader("ðŸ—‘ï¸ Analyse Gaspillage")
    
    st.markdown("""
    Identifiez et réduisez le gaspillage:
    - Articles périmés et valeur perdue
    - Gaspillage par catégorie
    - Recommandations de réduction
    - Tendances et patterns
    """)
    
    st.divider()
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        periode = st.selectbox(
            "Période d'analyse:",
            [(7, "7 jours"), (14, "2 semaines"), (30, "1 mois"), (90, "3 mois")],
            format_func=lambda x: x[1],
            key="periode_gaspillage",
            index=2
        )[0]
    
    with col2:
        if st.button("ðŸ‘ï¸ Aperçu", key="btn_preview_gaspillage", use_container_width=True):
            st.session_state.preview_gaspillage = True
    
    with col3:
        if st.button("ðŸ“¥ Télécharger PDF", key="btn_download_gaspillage", use_container_width=True):
            st.session_state.download_gaspillage = True
    
    # Aperçu
    if st.session_state.get("preview_gaspillage"):
        try:
            analyse = service.generer_analyse_gaspillage(periode)
            
            # Résumé
            st.warning("âš ï¸ **RÃ‰SUMÃ‰ GASPILLAGE**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Articles périmés", analyse.articles_perimes_total)
            
            with col2:
                st.metric("Valeur perdue", f"â‚¬{analyse.valeur_perdue:.2f}")
            
            with col3:
                if analyse.articles_perimes_total > 0:
                    moy_perte = analyse.valeur_perdue / analyse.articles_perimes_total
                    st.metric("Moyenne perte", f"â‚¬{moy_perte:.2f}")
            
            # Recommandations
            if analyse.recommandations:
                st.subheader("ðŸ’¡ Recommandations")
                for rec in analyse.recommandations:
                    st.info(rec)
            
            # Gaspillage par catégorie
            if analyse.categories_gaspillage:
                st.subheader("[CHART] Gaspillage par catégorie")
                
                cat_data = []
                for cat, data in sorted(
                    analyse.categories_gaspillage.items(),
                    key=lambda x: x[1]["valeur"],
                    reverse=True
                ):
                    cat_data.append({
                        "Catégorie": cat,
                        "Articles": data["articles"],
                        "Valeur perdue â‚¬": f"{data['valeur']:.2f}"
                    })
                
                df_cat = pd.DataFrame(cat_data)
                st.dataframe(
                    df_cat,
                    use_container_width=True,
                    hide_index=True
                )
            
            # Articles détail
            if analyse.articles_perimes_detail:
                st.subheader("âŒ Articles périmés (détail)")
                df_detail = pd.DataFrame(analyse.articles_perimes_detail)
                st.dataframe(
                    df_detail.rename(columns={
                        "nom": "Article",
                        "date_peremption": "Date péremption",
                        "jours_perime": "Jours écart",
                        "quantite": "Quantité",
                        "unite": "Unité",
                        "valeur_perdue": "Valeur perdue â‚¬"
                    }),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Valeur perdue â‚¬": st.column_config.NumberColumn(format="â‚¬%.2f")
                    }
                )
        
        except Exception as e:
            st.error(f"âŒ Erreur: {str(e)}")
    
    # Téléchargement
    if st.session_state.get("download_gaspillage"):
        try:
            pdf = service.generer_pdf_analyse_gaspillage(periode)
            filename = f"analyse_gaspillage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            st.download_button(
                label="ðŸ“¥ Télécharger le PDF",
                data=pdf.getvalue(),
                file_name=filename,
                mime="application/pdf",
                key="download_button_gaspillage"
            )
            st.success("âœ… PDF généré - Cliquez sur le bouton pour télécharger")
            st.session_state.download_gaspillage = False
        
        except Exception as e:
            st.error(f"âŒ Erreur: {str(e)}")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ONGLET 4: HISTORIQUE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_historique():
    """Historique rapports générés"""
    
    st.subheader("ðŸ“ˆ Historique & Planification")
    
    st.markdown("""
    Planifiez la génération automatique de rapports.
    """)
    
    # Planification
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ðŸ“… Rapports Hebdomadaires")
        
        st.markdown("""
        âœ… Rapport stocks - chaque lundi
        âœ… Rapport budget - chaque dimanche
        âœ… Analyse gaspillage - chaque vendredi
        """)
        
        if st.button("âš™ï¸ Configurer planification", key="btn_schedule"):
            st.info("""
            Pour configurer les rapports automatiques:
            1. Utilisez le menu Paramètres
            2. Activez "Rapports automatiques"
            3. Choisissez les jours et heures
            """)
    
    with col2:
        st.subheader("[CHART] Statistiques")
        
        st.metric("Rapports générés ce mois", 12)
        st.metric("Articles analysés", 47)
        st.metric("Valeur stock totale", "â‚¬1,234.56")
    
    # Guide
    st.divider()
    st.subheader("ðŸ“š Guide d'utilisation")
    
    with st.expander("â„¹ï¸ Comment utiliser les rapports"):
        st.markdown("""
        **Rapport Stocks:**
        - Généré chaque semaine
        - Montre articles en faible stock
        - Identifie articles périmés
        - Calcule valeur du stock
        
        **Rapport Budget:**
        - Analyse dépenses par catégorie
        - Identifie articles coûteux
        - Compare avec semaines précédentes
        - Aide à budgéter les courses
        
        **Analyse Gaspillage:**
        - Calcule valeur perdue
        - Identifie patterns de gaspillage
        - Donne recommandations
        - Aide à réduire pertes
        """)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PAGE ENTRY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


if __name__ == "__main__":
    app()

