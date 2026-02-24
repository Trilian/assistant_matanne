"""
Depenses Maison - Graphiques Plotly

Graphiques d'évolution, répartition par catégorie et comparaison mensuelle.
"""

import pandas as pd

try:
    import plotly.express as px

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("depenses")

from .crud import get_depenses_mois, get_historique_categorie
from .utils import CATEGORY_LABELS, MOIS_FR, date, st


def afficher_graphique_evolution():
    """Affiche le graphique d'evolution avec Plotly"""
    st.subheader("📈 Évolution")

    # Selection categorie
    categorie = st.selectbox(
        "Categorie à afficher",
        options=["total"] + list(CATEGORY_LABELS.keys()),
        format_func=lambda x: (
            "📊 Total toutes categories" if x == "total" else CATEGORY_LABELS.get(x, x)
        ),
    )

    today = date.today()

    if categorie == "total":
        # Calculer le total par mois
        data = []
        for i in range(12):
            mois = today.month - i
            annee = today.year
            while mois <= 0:
                mois += 12
                annee -= 1

            depenses = get_depenses_mois(mois, annee)
            total = sum(float(d.montant) for d in depenses)
            data.append(
                {
                    "Mois": f"{MOIS_FR[mois][:3]} {annee}",
                    "Montant": total,
                    "mois_num": mois,
                    "annee": annee,
                }
            )
        data = list(reversed(data))
    else:
        historique = get_historique_categorie(categorie, 12)
        data = [{"Mois": h["label"], "Montant": h["montant"]} for h in historique]

    if data:
        df = pd.DataFrame(data)

        if PLOTLY_AVAILABLE:
            titre = f"Évolution {'totale' if categorie == 'total' else CATEGORY_LABELS.get(categorie, categorie)}"
            fig = _build_evolution_bar(tuple(df["Mois"]), tuple(df["Montant"]), titre)
            st.plotly_chart(fig, use_container_width=True)

            # Graphique tendance (ligne)
            if len(df) >= 3:
                fig_line = _build_evolution_line(tuple(df["Mois"]), tuple(df["Montant"]))
                st.plotly_chart(fig_line, use_container_width=True)
        else:
            # Fallback: graphique Streamlit natif
            st.bar_chart(df.set_index("Mois")["Montant"])


@cached_fragment(ttl=300)
def _build_evolution_bar(mois: tuple, montants: tuple, titre: str):
    """Construit le bar chart d'évolution (caché 5 min)."""
    df = pd.DataFrame({"Mois": list(mois), "Montant": list(montants)})
    fig = px.bar(
        df,
        x="Mois",
        y="Montant",
        title=titre,
        text="Montant",
        color_discrete_sequence=["#8e44ad"],
    )
    fig.update_traces(texttemplate="%{text:.0f}€", textposition="outside")
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Montant (€)",
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui", size=12),
        margin=dict(t=50, b=50, l=50, r=20),
    )
    return fig


@cached_fragment(ttl=300)
def _build_evolution_line(mois: tuple, montants: tuple):
    """Construit le line chart de tendance (caché 5 min)."""
    df = pd.DataFrame({"Mois": list(mois), "Montant": list(montants)})
    fig = px.line(df, x="Mois", y="Montant", title="Tendance", markers=True)
    fig.update_traces(line_color="#27ae60")
    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig


@cached_fragment(ttl=300)
def _build_repartition_pie(categories: tuple, montants: tuple, titre: str):
    """Construit le pie chart de répartition (caché 5 min)."""
    df = pd.DataFrame({"Catégorie": list(categories), "Montant": list(montants)})
    fig = px.pie(
        df,
        values="Montant",
        names="Catégorie",
        title=titre,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value:.0f}€<br>%{percent}",
    )
    fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
    return fig


def afficher_graphique_repartition():
    """Affiche un graphique camembert de répartition par catégorie."""
    st.subheader("🥧 Répartition par catégorie")

    today = date.today()

    col1, col2 = st.columns(2)
    with col1:
        mois = st.selectbox(
            "Mois",
            options=range(1, 13),
            format_func=lambda x: MOIS_FR[x],
            index=today.month - 1,
            key=_keys("repartition_mois"),
        )
    with col2:
        annee = st.number_input(
            "Année",
            min_value=2020,
            max_value=2030,
            value=today.year,
            key=_keys("repartition_annee"),
        )

    depenses = get_depenses_mois(mois, int(annee))

    if not depenses:
        st.info(f"Aucune dépense pour {MOIS_FR[mois]} {annee}")
        return

    # Grouper par catégorie
    par_cat = {}
    for d in depenses:
        cat = CATEGORY_LABELS.get(d.categorie, d.categorie)
        par_cat[cat] = par_cat.get(cat, 0) + float(d.montant)

    df = pd.DataFrame([{"Catégorie": k, "Montant": v} for k, v in par_cat.items()])

    if PLOTLY_AVAILABLE and not df.empty:
        fig = _build_repartition_pie(
            tuple(df["Catégorie"]),
            tuple(df["Montant"]),
            f"Répartition {MOIS_FR[mois]} {annee}",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback simple
        for cat, montant in par_cat.items():
            st.write(f"{cat}: {montant:.0f}€")


def afficher_comparaison_mois():
    """Compare les depenses de 2 mois"""
    st.subheader("⚖️ Comparaison")

    today = date.today()

    col1, col2 = st.columns(2)

    with col1:
        st.caption("Mois 1")
        mois1 = st.selectbox(
            "Mois",
            range(1, 13),
            format_func=lambda x: MOIS_FR[x],
            index=today.month - 1,
            key=_keys("mois1"),
        )
        annee1 = st.number_input("Annee", 2020, 2030, today.year, key=_keys("annee1"))

    with col2:
        st.caption("Mois 2")
        mois_prec = today.month - 1 if today.month > 1 else 12
        annee_prec = today.year if today.month > 1 else today.year - 1
        mois2 = st.selectbox(
            "Mois",
            range(1, 13),
            format_func=lambda x: MOIS_FR[x],
            index=mois_prec - 1,
            key=_keys("mois2"),
        )
        annee2 = st.number_input("Annee", 2020, 2030, annee_prec, key=_keys("annee2"))

    if st.button("Comparer", type="primary"):
        dep1 = get_depenses_mois(mois1, int(annee1))
        dep2 = get_depenses_mois(mois2, int(annee2))

        # Grouper par categorie
        par_cat1 = {d.categorie: float(d.montant) for d in dep1}
        par_cat2 = {d.categorie: float(d.montant) for d in dep2}

        all_cats = set(par_cat1.keys()) | set(par_cat2.keys())

        st.divider()

        for cat in sorted(all_cats):
            val1 = par_cat1.get(cat, 0)
            val2 = par_cat2.get(cat, 0)
            delta = val1 - val2

            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.markdown(f"**{CATEGORY_LABELS.get(cat, cat)}**")
            with col_b:
                st.caption(f"{MOIS_FR[mois1]}: {val1:.0f}€")
                st.caption(f"{MOIS_FR[mois2]}: {val2:.0f}€")
            with col_c:
                if delta != 0:
                    color = "🔴" if delta > 0 else "🟢"
                    st.markdown(f"{color} {delta:+.0f}€")

        st.divider()
        total1 = sum(par_cat1.values())
        total2 = sum(par_cat2.values())
        delta_total = total1 - total2

        st.markdown(f"**TOTAL**: {total1:.0f}€ vs {total2:.0f}€ = **{delta_total:+.0f}€**")
