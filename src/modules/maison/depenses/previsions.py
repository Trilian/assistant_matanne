"""
Depenses Maison - Prévisions IA

Estimation des dépenses futures basée sur l'historique (moyenne mobile + saisonnalité).
"""

import pandas as pd

try:
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from .crud import get_depenses_mois
from .utils import MOIS_FR, date, st


def afficher_previsions_ia():
    """Affiche les prévisions IA pour les prochains mois."""
    st.subheader("🤖 Prévisions IA")

    st.markdown("""
    Basé sur votre historique, l'IA estime vos dépenses pour les prochains mois.
    """)

    today = date.today()

    # Récupérer données des 6 derniers mois
    historique = []
    for i in range(6):
        mois = today.month - i
        annee = today.year
        while mois <= 0:
            mois += 12
            annee -= 1

        depenses = get_depenses_mois(mois, annee)
        total = sum(float(d.montant) for d in depenses)
        historique.append({"mois": mois, "annee": annee, "total": total})

    historique = list(reversed(historique))

    if not historique or all(h["total"] == 0 for h in historique):
        st.info("📊 Ajoutez des dépenses pour obtenir des prévisions personnalisées.")
        return

    # Calculs de prévision (moyenne mobile + saisonnalité simplifiée)
    moyenne = sum(h["total"] for h in historique) / len(historique)
    tendance = (
        (historique[-1]["total"] - historique[0]["total"]) / len(historique)
        if len(historique) > 1
        else 0
    )

    # Prévisions pour les 3 prochains mois
    previsions = []
    for i in range(1, 4):
        mois_prev = today.month + i
        annee_prev = today.year
        while mois_prev > 12:
            mois_prev -= 12
            annee_prev += 1

        # Estimation: moyenne + tendance + facteur saisonnier
        facteur_saison = 1.0
        if mois_prev in [1, 2, 12]:  # Mois froids = plus de chauffage
            facteur_saison = 1.15
        elif mois_prev in [7, 8]:  # Été = moins
            facteur_saison = 0.9

        estimation = (moyenne + tendance * i) * facteur_saison
        estimation = max(0, estimation)  # Pas de négatif

        previsions.append(
            {
                "Mois": f"{MOIS_FR[mois_prev]} {annee_prev}",
                "Estimation": estimation,
                "mois_num": mois_prev,
            }
        )

    # Affichage
    col1, col2, col3 = st.columns(3)

    for i, (col, prev) in enumerate(zip([col1, col2, col3], previsions, strict=False)):
        with col:
            variation = ""
            if historique:
                last_total = historique[-1]["total"]
                if last_total > 0:
                    pct = ((prev["Estimation"] - last_total) / last_total) * 100
                    variation = f"{pct:+.0f}%"

            st.metric(
                prev["Mois"], f"{prev['Estimation']:.0f}€", delta=variation, delta_color="inverse"
            )

    # Graphique prévisionnel
    if PLOTLY_AVAILABLE:
        # Combiner historique et prévisions
        df_hist = pd.DataFrame(
            [
                {"Mois": f"{MOIS_FR[h['mois']][:3]}", "Montant": h["total"], "Type": "Réel"}
                for h in historique
            ]
        )

        df_prev = pd.DataFrame(
            [
                {"Mois": p["Mois"][:3], "Montant": p["Estimation"], "Type": "Prévision"}
                for p in previsions
            ]
        )

        fig = go.Figure()

        # Historique
        fig.add_trace(
            go.Bar(x=df_hist["Mois"], y=df_hist["Montant"], name="Réel", marker_color="#8e44ad")
        )

        # Prévisions (hachuré)
        fig.add_trace(
            go.Bar(
                x=df_prev["Mois"],
                y=df_prev["Montant"],
                name="Prévision",
                marker_color="#9b59b6",
                marker_pattern_shape="/",
            )
        )

        fig.update_layout(
            title="Historique et prévisions",
            xaxis_title="",
            yaxis_title="Montant (€)",
            barmode="group",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )

        st.plotly_chart(fig, use_container_width=True)

    # Insights IA
    st.divider()
    st.markdown("### 💡 Insights")

    insights = []

    if tendance > 20:
        insights.append(
            "📈 **Tendance haussière** : Vos dépenses augmentent. Surveillez les postes en hausse."
        )
    elif tendance < -20:
        insights.append(
            "📉 **Tendance baissière** : Bravo ! Vos efforts de réduction portent leurs fruits."
        )
    else:
        insights.append("➡️ **Tendance stable** : Vos dépenses sont relativement constantes.")

    # Mois le plus cher
    if historique:
        mois_max = max(historique, key=lambda h: h["total"])
        if mois_max["total"] > 0:
            insights.append(
                f"💰 Mois le plus cher : **{MOIS_FR[mois_max['mois']]} {mois_max['annee']}** ({mois_max['total']:.0f}€)"
            )

    # Estimation annuelle
    estimation_annuelle = moyenne * 12
    insights.append(
        f"📅 Budget annuel estimé : **{estimation_annuelle:.0f}€** ({estimation_annuelle / 12:.0f}€/mois)"
    )

    for insight in insights:
        st.markdown(insight)
