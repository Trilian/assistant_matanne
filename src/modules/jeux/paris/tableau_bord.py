"""
Dashboard de performance des paris.
"""

from src.ui import etat_vide
from src.ui.fragments import cached_fragment

from .utils import calculer_performance_paris, charger_paris_utilisateur, pd, st


@cached_fragment(ttl=300)
def afficher_dashboard_performance():
    """Affiche le tableau de bord de performance des paris"""
    paris = charger_paris_utilisateur()

    if not paris:
        etat_vide("Aucun pari enregistré", "📊", "Commencez par faire des prédictions !")
        return

    # Calculs
    perf = calculer_performance_paris(paris)

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🎯 Total Paris", perf["nb_paris"])

    with col2:
        taux = perf.get("taux_reussite", 0)
        st.metric("✅ Taux Réussite", f"{taux:.1f}%")

    with col3:
        profit = perf.get("profit", 0)
        st.metric(
            "💰 Profit/Perte",
            f"{profit:+.2f}€",
            delta_color="normal" if profit >= 0 else "inverse",
        )

    with col4:
        roi = perf.get("roi", 0)
        st.metric("📝ˆ ROI", f"{roi:+.1f}%", delta_color="normal" if roi >= 0 else "inverse")

    st.divider()

    # Graphique évolution
    if len(paris) > 1:
        df = pd.DataFrame(paris)
        df = df[df["statut"] != "en_attente"]

        if not df.empty:
            df["profit_cumul"] = df.apply(
                lambda x: (
                    float(x["gain"]) - float(x["mise"])
                    if x["statut"] == "gagne"
                    else -float(x["mise"])
                ),
                axis=1,
            ).cumsum()

            st.line_chart(df["profit_cumul"])
            st.caption("📝ˆ Évolution du profit cumulé")

    st.divider()

    # Historique des paris
    st.subheader("📋 Historique récent")

    for pari in paris[:10]:
        statut_emoji = {"en_attente": "⏳", "gagne": "✅", "perdu": "❌"}.get(pari["statut"], "?")

        pred_label = {"1": "Dom", "N": "Nul", "2": "Ext"}.get(pari["prediction"], "?")

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.write(f"{statut_emoji} Match #{pari['match_id']}")
        with col2:
            st.write(f"Préd: {pred_label}")
        with col3:
            st.write(f"Cote: {pari['cote']:.2f}")
        with col4:
            if pari["statut"] == "gagne":
                st.write(f"💰 +{pari['gain']:.2f}€")
            elif pari["statut"] == "perdu":
                st.write(f"📝‰ -{pari['mise']:.2f}€")


__all__ = ["afficher_dashboard_performance"]
