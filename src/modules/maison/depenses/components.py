"""
Module Depenses Maison - Composants UI (orchestrateur)

Ré-exporte les fonctions depuis les sous-modules:
  - cards.py: Cards de dépense et formulaire
  - charts.py: Graphiques Plotly (évolution, répartition, comparaison)
  - previsions.py: Prévisions IA
  - export.py: Export CSV/Excel
"""

from src.ui.fragments import cached_fragment, ui_fragment
from src.ui.tokens_semantic import Sem

from .cards import afficher_depense_card, afficher_formulaire
from .charts import (
    afficher_comparaison_mois,
    afficher_graphique_evolution,
    afficher_graphique_repartition,
)
from .crud import get_depenses_mois, get_stats_globales
from .export import afficher_export_section
from .previsions import afficher_previsions_ia
from .utils import CATEGORY_LABELS, MOIS_FR, date, st


@cached_fragment(ttl=300)
def afficher_stats_dashboard():
    """Affiche le dashboard de stats"""
    stats = get_stats_globales()
    today = date.today()

    st.subheader(f"📊 Resume {MOIS_FR[today.month]} {today.year}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_str = f"{stats['delta']:+.0f}€" if stats["delta"] != 0 else None
        st.metric("Ce mois", f"{stats['total_mois']:.0f}€", delta=delta_str, delta_color="inverse")

    with col2:
        st.metric("Mois precedent", f"{stats['total_prec']:.0f}€")

    with col3:
        md = (
            f'<div style="text-align:center;min-width:0;">'
            f'<div style="font-size:1.3rem;font-weight:700;line-height:1.2;">{stats["moyenne_mensuelle"]:.0f}€</div>'
            f'<div style="font-size:0.72rem;color:{Sem.ON_SURFACE_SECONDARY};white-space:normal;overflow:visible;word-break:break-word;">Moyenne mensuelle</div>'
            '</div>'
        )
        st.markdown(md, unsafe_allow_html=True)

    with col4:
        st.metric("Categories", stats["nb_categories"])


@ui_fragment
def afficher_onglet_mois():
    """Onglet depenses du mois"""
    today = date.today()

    col1, col2 = st.columns(2)
    with col1:
        mois = st.selectbox(
            "Mois", options=range(1, 13), format_func=lambda x: MOIS_FR[x], index=today.month - 1
        )
    with col2:
        annee = st.number_input("Annee", min_value=2020, max_value=2030, value=today.year)

    depenses = get_depenses_mois(mois, int(annee))

    if not depenses:
        st.info(f"Aucune dépense enregistrée pour {MOIS_FR[mois]} {annee}")
        return

    # Total
    total = sum(float(d.montant) for d in depenses)
    st.metric(f"Total {MOIS_FR[mois]} {annee}", f"{total:.2f}€")

    st.divider()

    for depense in depenses:
        afficher_depense_card(depense)


@ui_fragment
def afficher_onglet_ajouter():
    """Onglet ajout"""
    st.subheader("➕ Ajouter une depense")
    afficher_formulaire(None)


@ui_fragment
def afficher_onglet_analyse():
    """Onglet analyse et graphiques enrichie avec Plotly, export et prévisions IA."""

    # Sous-onglets pour organisation
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(
        ["📈 Évolution", "🥧 Répartition", "🤖 Prévisions IA", "📥 Export"]
    )

    with sub_tab1:
        afficher_graphique_evolution()
        st.divider()
        afficher_comparaison_mois()

    with sub_tab2:
        afficher_graphique_repartition()

    with sub_tab3:
        afficher_previsions_ia()

    with sub_tab4:
        afficher_export_section()
