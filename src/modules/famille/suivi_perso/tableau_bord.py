"""
Module Suivi Perso - Dashboard et graphiques
"""

from .utils import date, get_current_user, go, set_current_user, st, timedelta


def afficher_user_switch():
    """Affiche le switch utilisateur"""
    current = get_current_user()

    col1, col2 = st.columns(2)

    with col1:
        btn_type = "primary" if current == "anne" else "secondary"
        if st.button("👩 Anne", key="switch_anne", use_container_width=True, type=btn_type):
            set_current_user("anne")
            st.rerun()

    with col2:
        btn_type = "primary" if current == "mathieu" else "secondary"
        if st.button("💨 Mathieu", key="switch_mathieu", use_container_width=True, type=btn_type):
            set_current_user("mathieu")
            st.rerun()


def afficher_dashboard(data: dict):
    """Affiche le dashboard principal"""
    user = data.get("user")
    if not user:
        st.warning("Utilisateur non trouvé")
        return

    st.markdown("##### 📊 Dashboard")

    # CSS pour réduire la taille des métriques
    st.markdown(
        """
        <style>
        [data-testid="stMetric"] {
            padding: 8px 12px;
        }
        [data-testid="stMetric"] label {
            font-size: 0.85rem !important;
        }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-size: 0.75rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        streak = data.get("streak", 0)
        st.metric("🔥 Streak", f"{streak} jours")

    with col2:
        today_summary = None
        for s in data.get("summaries", []):
            if s.date == date.today():
                today_summary = s
                break

        today_pas = today_summary.pas if today_summary else 0
        objectif = data.get("objectif_pas", 10000)
        pct = min(100, (today_pas / objectif) * 100)
        st.metric("👣 Pas aujourd'hui", f"{today_pas:,}", f"{pct:.0f}%")

    with col3:
        today_cal = today_summary.calories_actives if today_summary else 0
        st.metric("🔥 Calories", f"{today_cal}")

    with col4:
        garmin = "✅ Connecté" if data.get("garmin_connected") else "❌ Non connecté"
        st.metric("⌚ Garmin", garmin)

    # Graphique des 7 derniers jours
    st.markdown("---")
    afficher_weekly_chart(data.get("summaries", []), data.get("objectif_pas", 10000))


def afficher_weekly_chart(summaries: list, objectif: int):
    """Affiche le graphique des 7 derniers jours"""
    if not summaries:
        st.info("Pas de données Garmin. Connectez votre montre pour voir vos stats.")
        return

    # Préparer les données
    dates = []
    pas_values = []
    calories_values = []

    for i in range(7):
        d = date.today() - timedelta(days=6 - i)
        dates.append(d.strftime("%a %d"))

        summary = next((s for s in summaries if s.date == d), None)
        pas_values.append(summary.pas if summary else 0)
        calories_values.append(summary.calories_actives if summary else 0)

    # Créer le graphique
    fig = go.Figure()

    # Barres pour les pas
    colors = ["#4CAF50" if p >= objectif else "#FFC107" for p in pas_values]
    fig.add_trace(go.Bar(x=dates, y=pas_values, name="Pas", marker_color=colors))

    # Ligne objectif
    fig.add_hline(
        y=objectif, line_dash="dash", line_color="red", annotation_text=f"Objectif: {objectif:,}"
    )

    fig.update_layout(
        title="📝ˆ Pas quotidiens (7 derniers jours)",
        xaxis_title="",
        yaxis_title="Pas",
        showlegend=False,
        height=300,
    )

    st.plotly_chart(fig, width="stretch")
