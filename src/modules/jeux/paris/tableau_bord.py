"""
Dashboard de performance des paris.
"""

from .utils import st, pd, calculer_performance_paris
from .utilitaires import charger_paris_utilisateur


def afficher_dashboard_performance():
    """Affiche le tableau de bord de performance des paris"""
    paris = charger_paris_utilisateur()
    
    if not paris:
        st.info("ðŸ“Š Aucun pari enregistrÃe. Commencez par faire des prÃedictions!")
        return
    
    # Calculs
    perf = calculer_performance_paris(paris)
    
    # MÃetriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ðŸŽ¯ Total Paris", perf["nb_paris"])
    
    with col2:
        taux = perf.get("taux_reussite", 0)
        st.metric("âœ… Taux RÃeussite", f"{taux:.1f}%")
    
    with col3:
        profit = perf.get("profit", 0)
        st.metric("ðŸ’° Profit/Perte", f"{profit:+.2f}â‚¬", 
                  delta_color="normal" if profit >= 0 else "inverse")
    
    with col4:
        roi = perf.get("roi", 0)
        st.metric("ðŸ“ˆ ROI", f"{roi:+.1f}%",
                  delta_color="normal" if roi >= 0 else "inverse")
    
    st.divider()
    
    # Graphique Ãevolution
    if len(paris) > 1:
        df = pd.DataFrame(paris)
        df = df[df["statut"] != "en_attente"]
        
        if not df.empty:
            df["profit_cumul"] = df.apply(
                lambda x: float(x["gain"]) - float(x["mise"]) if x["statut"] == "gagne" 
                else -float(x["mise"]), axis=1
            ).cumsum()
            
            st.line_chart(df["profit_cumul"])
            st.caption("ðŸ“ˆ Évolution du profit cumulÃe")
    
    st.divider()
    
    # Historique des paris
    st.subheader("ðŸ“‹ Historique rÃecent")
    
    for pari in paris[:10]:
        statut_emoji = {
            "en_attente": "â³",
            "gagne": "âœ…",
            "perdu": "âŒ"
        }.get(pari["statut"], "?")
        
        pred_label = {"1": "Dom", "N": "Nul", "2": "Ext"}.get(pari["prediction"], "?")
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.write(f"{statut_emoji} Match #{pari['match_id']}")
        with col2:
            st.write(f"PrÃed: {pred_label}")
        with col3:
            st.write(f"Cote: {pari['cote']:.2f}")
        with col4:
            if pari["statut"] == "gagne":
                st.write(f"ðŸ’° +{pari['gain']:.2f}â‚¬")
            elif pari["statut"] == "perdu":
                st.write(f"ðŸ“‰ -{pari['mise']:.2f}â‚¬")


__all__ = ["afficher_dashboard_performance"]
