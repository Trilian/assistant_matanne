"""
Module Loto - Simulation et gestion des tirages
"""

from ._common import (
    CHANCE_MAX,
    CHANCE_MIN,
    NUMERO_MAX,
    NUMERO_MIN,
    analyser_patterns_tirages,
    calculer_frequences_numeros,
    date,
    etat_vide,
    go,
    logger,
    pd,
    random,
    simuler_strategie,
    st,
)
from .crud import ajouter_tirage
from .sync import sync_tirages_loto
from .utils import charger_tirages


def afficher_simulation():
    """Interface de simulation de stratégies"""

    st.markdown("### 🔬 Simulation de stratégies")
    st.caption("Testez différentes stratégies sur l'historique des tirages")

    tirages = charger_tirages(limite=500)

    if len(tirages) < 10:
        st.warning("⚠️ Pas assez de tirages pour une simulation fiable (minimum 10)")
        return

    col1, col2 = st.columns(2)

    with col1:
        nb_tirages = st.slider(
            "Nombre de tirages à simuler", 10, len(tirages), min(100, len(tirages))
        )

    with col2:
        grilles_par_tirage = st.slider("Grilles par tirage", 1, 10, 1)

    if st.button("🚀 Lancer la simulation", type="primary"):
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
                    patterns=patterns,
                )
                resultats[strat] = res
                progress.progress((i + 1) / len(strategies))

            progress.empty()

        # Afficher résultats
        st.divider()
        st.markdown("### 📊 Résultats de la simulation")

        df_res = pd.DataFrame(
            [
                {
                    "Stratégie": strat,
                    "Grilles": res["nb_grilles"],
                    "Mise totale": f"{res['mises_totales']:.2f}€",
                    "Gains": f"{res['gains_totaux']:.2f}€",
                    "Profit": f"{res['profit']:+.2f}€",
                    "ROI": f"{res['roi']:+.1f}%",
                    "Gagnants": res["nb_gagnants"],
                    "Taux": f"{res['taux_gain']:.1f}%",
                }
                for strat, res in resultats.items()
            ]
        )

        st.dataframe(df_res, hide_index=True, width="stretch")

        # Graphique comparatif
        fig = go.Figure(
            data=[
                go.Bar(
                    x=list(resultats.keys()),
                    y=[r["roi"] for r in resultats.values()],
                    marker_color=[
                        "#4CAF50" if r["roi"] > 0 else "#f44336" for r in resultats.values()
                    ],
                    text=[f"{r['roi']:+.1f}%" for r in resultats.values()],
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title="Comparaison des ROI par stratégie",
            xaxis_title="Stratégie",
            yaxis_title="ROI (%)",
            height=300,
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")

        st.plotly_chart(fig, width="stretch", key="loto_roi_chart")


def afficher_gestion_tirages():
    """Interface pour gérer les tirages"""

    # Boutons de synchronisation
    st.markdown("### 🔄 Synchronisation")

    col_sync1, col_sync2 = st.columns([1, 1])

    with col_sync1:
        if st.button("📥 Sync Tirages FDJ", help="Charge les derniers tirages du Loto FDJ"):
            st.info("⏳ Synchronisation en cours...")
            try:
                with st.spinner("Récupération des tirages..."):
                    logger.info("🔘 Bouton SYNC LOTO cliqué!")
                    count = sync_tirages_loto(limite=50)
                    logger.info(f"📊 Résultat sync loto: {count} tirages")
                    if count > 0:
                        st.success(f"✅ {count} nouveau(x) tirage(s) ajouté(s)!")
                    else:
                        st.info("✅ Tous les tirages sont à jour")
                    st.rerun()
            except Exception as e:
                logger.error(f"❌ Erreur sync loto: {e}", exc_info=True)
                st.error(f"❌ Erreur: {e}")

    st.divider()

    st.markdown("### ➕ Ajouter un tirage")

    col1, col2 = st.columns([2, 1])

    with col1:
        date_tirage = st.date_input("Date du tirage", value=date.today())

        st.write("**Numéros (1-49):**")
        cols_num = st.columns(5)
        numeros = []
        for i in range(5):
            with cols_num[i]:
                num = st.number_input(
                    f"N°{i + 1}",
                    NUMERO_MIN,
                    NUMERO_MAX,
                    value=random.randint(NUMERO_MIN, NUMERO_MAX),
                    key=f"tirage_num_{i}",
                )
                numeros.append(num)

    with col2:
        chance = st.number_input("N° Chance (1-10)", CHANCE_MIN, CHANCE_MAX, value=1)
        jackpot = st.number_input("Jackpot (€)", 0, 100_000_000, value=2_000_000, step=1_000_000)

    # Validation
    if len(set(numeros)) != 5:
        st.warning("⚠️ Les 5 numéros doivent être différents")
    else:
        if st.button("💾 Enregistrer le tirage", type="primary"):
            ajouter_tirage(date_tirage, numeros, chance, jackpot)
            st.rerun()

    st.divider()

    # Historique
    st.markdown("### 📜 Historique des tirages")
    tirages = charger_tirages(limite=20)

    if tirages:
        df = pd.DataFrame(
            [
                {
                    "Date": t["date_tirage"],
                    "Numéros": t["numeros_str"],
                    "Jackpot": f"{t['jackpot_euros']:,}€" if t.get("jackpot_euros") else "-",
                }
                for t in tirages
            ]
        )
        st.dataframe(df, hide_index=True, width="stretch")
    else:
        etat_vide("Aucun tirage enregistré", "🎲")
