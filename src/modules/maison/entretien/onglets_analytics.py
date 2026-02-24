"""Entretien - Onglets analytiques (historique, stats, graphiques)."""

import logging
from datetime import date, datetime, timedelta

import streamlit as st

from .data import charger_catalogue_entretien
from .logic import (
    calculer_score_proprete,
    calculer_stats_globales,
    calculer_streak,
    generer_alertes_predictives,
    generer_planning_previsionnel,
    generer_taches_entretien,
    obtenir_badges_obtenus,
)
from .ui import afficher_alertes_predictives as ui_alertes_predictives
from .ui import afficher_badges_entretien, afficher_score_gamifie, afficher_timeline_item

# Import optionnel Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

logger = logging.getLogger(__name__)

from src.ui.fragments import cached_fragment, ui_fragment


@ui_fragment
def onglet_historique(historique: list[dict]):
    """Onglet historique des entretiens."""
    st.subheader("📜 Historique")

    if not historique:
        st.info(
            "L'historique apparaîtra ici une fois que vous aurez effectué des tâches d'entretien."
        )
        return

    catalogue = charger_catalogue_entretien()

    # Trier par date décroissante
    historique_trie = sorted(historique, key=lambda h: h.get("date", ""), reverse=True)

    # Stats rapides
    total_taches = len(historique_trie)
    derniere_semaine = len(
        [
            h
            for h in historique_trie
            if h.get("date", "") >= (date.today() - timedelta(days=7)).isoformat()
        ]
    )

    col1, col2 = st.columns(2)
    col1.metric("Total accompli", total_taches)
    col2.metric("Cette semaine", derniere_semaine)

    st.divider()

    # Timeline
    st.markdown("### Timeline")

    date_courante = None
    for h in historique_trie[:50]:  # Limiter à 50 entrées
        h_date = h.get("date", "")

        # Séparer par jour
        if h_date != date_courante:
            date_courante = h_date
            try:
                d = datetime.fromisoformat(h_date).date()
                if d == date.today():
                    label_date = "Aujourd'hui"
                elif d == date.today() - timedelta(days=1):
                    label_date = "Hier"
                else:
                    label_date = d.strftime("%d/%m/%Y")
            except Exception:
                label_date = h_date

            st.markdown(f"**{label_date}**")

        afficher_timeline_item(h, catalogue)


@ui_fragment
def onglet_stats(mes_objets: list[dict], historique: list[dict]):
    """Onglet statistiques détaillées avec gamification."""
    st.subheader("📊 Statistiques & Badges")

    score = calculer_score_proprete(mes_objets, historique)
    streak = calculer_streak(historique)
    stats = calculer_stats_globales(mes_objets, historique)
    badges_obtenus = obtenir_badges_obtenus(stats)

    col1, col2 = st.columns([1, 2])

    with col1:
        afficher_score_gamifie(score, streak)

    with col2:
        # Stats rapides
        st.markdown("### 📈 Vos performances")
        m1, m2, m3 = st.columns(3)
        m1.metric(
            "Tâches accomplies", stats["taches_accomplies"], help="Total des entretiens effectués"
        )
        m2.metric("Équipements", stats["nb_objets"], help="Nombre d'appareils enregistrés")
        m3.metric(
            "Streak actuel",
            f"{streak}j 🔥" if streak > 0 else "0j",
            help="Jours consécutifs d'entretien",
        )

        # Alertes
        alertes = generer_alertes_predictives(mes_objets, historique)
        if alertes:
            ui_alertes_predictives(alertes)

    st.divider()

    # Badges collection
    afficher_badges_entretien(badges_obtenus, stats)

    st.divider()

    # Stats par catégorie
    st.markdown("### 📦 Par catégorie d'équipement")

    catalogue = charger_catalogue_entretien()
    taches = generer_taches_entretien(mes_objets, historique)

    # Compter par catégorie
    par_cat = {}
    for obj in mes_objets:
        cat = obj.get("categorie_id", "divers")
        if cat not in par_cat:
            par_cat[cat] = {"objets": 0, "taches": 0}
        par_cat[cat]["objets"] += 1

    for t in taches:
        cat = t.get("categorie_id", "divers")
        if cat in par_cat:
            par_cat[cat]["taches"] += 1

    cols = st.columns(3)
    for i, (cat_id, data) in enumerate(par_cat.items()):
        cat_data = catalogue.get("categories", {}).get(cat_id, {})
        with cols[i % 3]:
            st.markdown(
                f"""
            <div class="entretien-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem">{cat_data.get("icon", "📦")}</div>
                <div style="font-weight: 600">{cat_id.replace("_", " ").capitalize()}</div>
                <div style="font-size: 0.85rem; color: #718096">
                    {data["objets"]} équipements • {data["taches"]} tâches en attente
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


@cached_fragment(ttl=300)  # Cache 5 min (graphiques Plotly lourds)
def onglet_graphiques(mes_objets: list[dict], historique: list[dict]):
    """Onglet graphiques Plotly avec visualisations interactives."""
    st.subheader("📈 Graphiques & Analyses")

    if not HAS_PLOTLY:
        st.warning("📦 Plotly non installé. `pip install plotly` pour les graphiques interactifs.")
        return

    if not historique:
        st.info("📊 Les graphiques apparaîtront avec vos premières tâches accomplies.")
        return

    # Tab internes pour différents graphiques
    g1, g2, g3 = st.tabs(["📅 Évolution", "🗂️ Répartition", "📊 Planning"])

    with g1:
        # Graphique évolution des tâches dans le temps
        st.markdown("### Évolution des entretiens")

        # Préparer les données par mois
        par_mois = {}
        for h in historique:
            date_str = h.get("date", "")
            if date_str:
                try:
                    d = datetime.fromisoformat(date_str).date()
                    mois_key = d.strftime("%Y-%m")
                    par_mois[mois_key] = par_mois.get(mois_key, 0) + 1
                except Exception:
                    pass

        if par_mois:
            mois_sorted = sorted(par_mois.keys())
            counts = [par_mois[m] for m in mois_sorted]
            mois_labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in mois_sorted]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=mois_labels,
                    y=counts,
                    mode="lines+markers",
                    name="Tâches accomplies",
                    line={"color": "#3498db", "width": 3},
                    marker={"size": 10, "color": "#3498db"},
                    fill="tozeroy",
                    fillcolor="rgba(52, 152, 219, 0.2)",
                )
            )
            fig.update_layout(
                title="Tâches d'entretien par mois",
                xaxis_title="Mois",
                yaxis_title="Nombre de tâches",
                template="plotly_dark",
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données pour le graphique d'évolution.")

    with g2:
        # Répartition par catégorie
        st.markdown("### Répartition par catégorie")

        catalogue = charger_catalogue_entretien()
        par_cat = {}
        for h in historique:
            obj_id = h.get("objet_id", "inconnu")
            # Trouver la catégorie
            cat_found = "Autre"
            for cat_id, cat_data in catalogue.get("categories", {}).items():
                if obj_id in cat_data.get("objets", {}):
                    cat_found = cat_id.replace("_", " ").capitalize()
                    break
            par_cat[cat_found] = par_cat.get(cat_found, 0) + 1

        if par_cat:
            fig = px.pie(
                values=list(par_cat.values()),
                names=list(par_cat.keys()),
                title="Entretiens par catégorie",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4,
            )
            fig.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas de données pour la répartition.")

    with g3:
        # Planning prévisionnel visuel
        st.markdown("### Planning prévisionnel")

        planning = generer_planning_previsionnel(mes_objets, historique, horizon_jours=60)

        if planning:
            # Créer un timeline
            df_planning = []
            for t in planning[:20]:
                df_planning.append(
                    {
                        "Tâche": t["tache_nom"][:20],
                        "Jours": t["jours_restants"],
                        "Objet": t["objet_nom"],
                        "Pièce": t["piece"],
                    }
                )

            fig = px.bar(
                df_planning,
                y="Tâche",
                x="Jours",
                orientation="h",
                color="Jours",
                color_continuous_scale=["#e74c3c", "#f39c12", "#27ae60"],
                title="Prochaines tâches (jours restants)",
            )
            fig.update_layout(
                template="plotly_dark", height=400, yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✨ Aucune tâche prévue dans les 60 prochains jours !")
