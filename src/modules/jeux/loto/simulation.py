"""
Module Loto - Simulation et gestion des tirages
"""

from ._common import (
    st, date, pd, go, random, logger,
    NUMERO_MIN, NUMERO_MAX, CHANCE_MIN, CHANCE_MAX,
    calculer_frequences_numeros, analyser_patterns_tirages, simuler_strategie
)
from .sync import sync_tirages_loto
from .crud import ajouter_tirage
from .utilitaires import charger_tirages


def afficher_simulation():
    """Interface de simulation de stratÃegies"""
    
    st.markdown("### ðŸ”¬ Simulation de stratÃegies")
    st.caption("Testez diffÃerentes stratÃegies sur l'historique des tirages")
    
    tirages = charger_tirages(limite=500)
    
    if len(tirages) < 10:
        st.warning("âš ï¸ Pas assez de tirages pour une simulation fiable (minimum 10)")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        nb_tirages = st.slider("Nombre de tirages Ã  simuler", 10, len(tirages), min(100, len(tirages)))
    
    with col2:
        grilles_par_tirage = st.slider("Grilles par tirage", 1, 10, 1)
    
    if st.button("ðŸš€ Lancer la simulation", type="primary"):
        with st.spinner("Simulation en cours..."):
            freq_data = calculer_frequences_numeros(tirages[:nb_tirages])
            patterns = analyser_patterns_tirages(tirages[:nb_tirages])
            
            resultats = {}
            strategies = ["aleatoire", "eviter_populaires", "equilibree", "chauds", "froids"]
            
            progress = st.progress(0)
            
            for i, strat in enumerate(strategies):
                res = simuler_strategie(
                    tirages[:nb_tirages],
                    strategie=strat,
                    nb_grilles_par_tirage=grilles_par_tirage,
                    frequences=freq_data.get("frequences"),
                    patterns=patterns
                )
                resultats[strat] = res
                progress.progress((i + 1) / len(strategies))
            
            progress.empty()
        
        # Afficher rÃesultats
        st.divider()
        st.markdown("### ðŸ“Š RÃesultats de la simulation")
        
        df_res = pd.DataFrame([
            {
                "StratÃegie": strat,
                "Grilles": res["nb_grilles"],
                "Mise totale": f"{res['mises_totales']:.2f}â‚¬",
                "Gains": f"{res['gains_totaux']:.2f}â‚¬",
                "Profit": f"{res['profit']:+.2f}â‚¬",
                "ROI": f"{res['roi']:+.1f}%",
                "Gagnants": res["nb_gagnants"],
                "Taux": f"{res['taux_gain']:.1f}%"
            }
            for strat, res in resultats.items()
        ])
        
        st.dataframe(df_res, hide_index=True, width="stretch")
        
        # Graphique comparatif
        fig = go.Figure(data=[
            go.Bar(
                x=list(resultats.keys()),
                y=[r["roi"] for r in resultats.values()],
                marker_color=["#4CAF50" if r["roi"] > 0 else "#f44336" for r in resultats.values()],
                text=[f"{r['roi']:+.1f}%" for r in resultats.values()],
                textposition="auto"
            )
        ])
        
        fig.update_layout(
            title="Comparaison des ROI par stratÃegie",
            xaxis_title="StratÃegie",
            yaxis_title="ROI (%)",
            height=300
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        st.plotly_chart(fig, width="stretch", key="loto_roi_chart")


def afficher_gestion_tirages():
    """Interface pour gÃerer les tirages"""
    
    # Boutons de synchronisation
    st.markdown("### ðŸ”„ Synchronisation")
    
    col_sync1, col_sync2 = st.columns([1, 1])
    
    with col_sync1:
        if st.button("ðŸ“¥ Sync Tirages FDJ", help="Charge les derniers tirages du Loto FDJ"):
            st.info("â³ Synchronisation en cours...")
            try:
                with st.spinner("RÃecupÃeration des tirages..."):
                    logger.info("ðŸ”˜ Bouton SYNC LOTO cliquÃe!")
                    count = sync_tirages_loto(limite=50)
                    logger.info(f"ðŸ“Š RÃesultat sync loto: {count} tirages")
                    if count > 0:
                        st.success(f"âœ… {count} nouveau(x) tirage(s) ajoutÃe(s)!")
                    else:
                        st.info("âœ… Tous les tirages sont Ã  jour")
                    st.rerun()
            except Exception as e:
                logger.error(f"âŒ Erreur sync loto: {e}", exc_info=True)
                st.error(f"âŒ Erreur: {e}")
    
    st.divider()
    
    st.markdown("### âž• Ajouter un tirage")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        date_tirage = st.date_input("Date du tirage", value=date.today())
        
        st.write("**NumÃeros (1-49):**")
        cols_num = st.columns(5)
        numeros = []
        for i in range(5):
            with cols_num[i]:
                num = st.number_input(f"NÂ°{i+1}", NUMERO_MIN, NUMERO_MAX, 
                                     value=random.randint(NUMERO_MIN, NUMERO_MAX),
                                     key=f"tirage_num_{i}")
                numeros.append(num)
    
    with col2:
        chance = st.number_input("NÂ° Chance (1-10)", CHANCE_MIN, CHANCE_MAX, value=1)
        jackpot = st.number_input("Jackpot (â‚¬)", 0, 100_000_000, value=2_000_000, step=1_000_000)
    
    # Validation
    if len(set(numeros)) != 5:
        st.warning("âš ï¸ Les 5 numÃeros doivent être diffÃerents")
    else:
        if st.button("ðŸ’¾ Enregistrer le tirage", type="primary"):
            ajouter_tirage(date_tirage, numeros, chance, jackpot)
            st.rerun()
    
    st.divider()
    
    # Historique
    st.markdown("### ðŸ“œ Historique des tirages")
    tirages = charger_tirages(limite=20)
    
    if tirages:
        df = pd.DataFrame([
            {
                "Date": t["date_tirage"],
                "NumÃeros": t["numeros_str"],
                "Jackpot": f"{t['jackpot_euros']:,}â‚¬" if t.get("jackpot_euros") else "-"
            }
            for t in tirages
        ])
        st.dataframe(df, hide_index=True, width="stretch")
    else:
        st.info("Aucun tirage enregistrÃe")
