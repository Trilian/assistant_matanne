"""
Module Journal de Bord — Suivi quotidien de la vie familiale.

Journal intime avec humeur, événements marquants, gratitudes,
historique et statistiques hebdomadaires.
"""

import logging
from datetime import date, timedelta

import streamlit as st

from src.core.models.utilitaires import HumeurEnum
from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.service import get_journal_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("journal_bord")

HUMEUR_EMOJIS = {
    HumeurEnum.EXCELLENT: "😄",
    HumeurEnum.BIEN: "🙂",
    HumeurEnum.NEUTRE: "😐",
    HumeurEnum.FATIGUE: "😴",
    HumeurEnum.STRESSE: "😰",
    HumeurEnum.TRISTE: "😢",
}


@profiler_rerun("journal_bord")
def app():
    """Point d'entrée module Journal de Bord."""
    st.title("📓 Journal de Bord")
    st.caption("Chronique quotidienne de la vie familiale")

    with error_boundary(titre="Erreur journal"):
        service = get_journal_service()

        tab1, tab2, tab3 = st.tabs(["✏️ Aujourd'hui", "📖 Historique", "📊 Statistiques"])

        with tab1:
            _onglet_aujourd_hui(service)
        with tab2:
            _onglet_historique(service)
        with tab3:
            _onglet_statistiques(service)


def _onglet_aujourd_hui(service):
    """Formulaire d'entrée pour aujourd'hui."""
    aujourd_hui = date.today()
    entree = service.obtenir_par_date(aujourd_hui)

    st.subheader(f"📅 {aujourd_hui.strftime('%A %d %B %Y')}")

    with st.form("form_journal", clear_on_submit=False):
        # Humeur
        st.markdown("**Comment ça va aujourd'hui ?**")
        humeur_options = list(HumeurEnum)
        humeur_labels = [f"{HUMEUR_EMOJIS[h]} {h.value.capitalize()}" for h in humeur_options]
        idx_defaut = humeur_options.index(HumeurEnum(entree.humeur)) if entree else 1
        humeur_idx = st.radio(
            "Humeur",
            options=range(len(humeur_options)),
            format_func=lambda i: humeur_labels[i],
            horizontal=True,
            index=idx_defaut,
            key=_keys("humeur"),
            label_visibility="collapsed",
        )

        # Contenu
        contenu = st.text_area(
            "Qu'est-ce qui s'est passé aujourd'hui ?",
            value=entree.contenu if entree else "",
            height=150,
            key=_keys("contenu"),
        )

        # Gratitudes
        gratitudes_str = st.text_area(
            "🙏 Gratitudes (une par ligne)",
            value="\n".join(entree.gratitudes or []) if entree else "",
            height=80,
            key=_keys("gratitudes"),
        )

        # Énergie
        energie = st.slider(
            "⚡ Niveau d'énergie",
            min_value=1,
            max_value=10,
            value=entree.energie if entree and entree.energie else 5,
            key=_keys("energie"),
        )

        # Tags
        tags_str = st.text_input(
            "🏷️ Tags (séparés par des virgules)",
            value=", ".join(entree.tags or []) if entree else "",
            key=_keys("tags"),
        )

        submitted = st.form_submit_button(
            "💾 Enregistrer" if not entree else "💾 Mettre à jour",
            use_container_width=True,
        )

        if submitted:
            gratitudes = [g.strip() for g in gratitudes_str.split("\n") if g.strip()]
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            humeur = humeur_options[humeur_idx].value

            service.creer_ou_modifier(
                aujourd_hui,
                contenu=contenu,
                humeur=humeur,
                gratitudes=gratitudes,
                energie=energie,
                tags=tags,
            )
            st.success("Journal enregistré !" if not entree else "Journal mis à jour !")
            st.rerun()


def _onglet_historique(service):
    """Affiche l'historique des entrées."""
    st.subheader("📖 Historique")

    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input(
            "Du",
            value=date.today() - timedelta(days=30),
            key=_keys("hist_debut"),
        )
    with col2:
        date_fin = st.date_input("Au", value=date.today(), key=_keys("hist_fin"))

    entrees = service.lister(date_debut=date_debut, date_fin=date_fin)

    if not entrees:
        st.info("Aucune entrée sur cette période.")
        return

    for entree in entrees:
        emoji = HUMEUR_EMOJIS.get(HumeurEnum(entree.humeur), "😐") if entree.humeur else "📝"
        with st.expander(
            f"{emoji} {entree.date_entree.strftime('%d/%m/%Y')} — {entree.humeur or 'N/A'}"
        ):
            st.markdown(entree.contenu or "_Pas de contenu_")
            if entree.gratitudes:
                st.markdown("**🙏 Gratitudes:**")
                for g in entree.gratitudes:
                    st.markdown(f"- {g}")
            if entree.energie:
                st.progress(entree.energie / 10, text=f"Énergie: {entree.energie}/10")
            tags = entree.tags or []
            if tags:
                st.caption(" ".join(f"`{t}`" for t in tags))


def _onglet_statistiques(service):
    """Statistiques du journal."""
    st.subheader("📊 Statistiques")

    stats = service.statistiques(jours=30)

    if not stats:
        st.info("Pas assez de données pour les statistiques.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Entrées (30j)", stats.get("total_entrees", 0))
    with col2:
        st.metric("😊 Humeur dominante", stats.get("humeur_dominante", "N/A"))
    with col3:
        st.metric("⚡ Énergie moyenne", f"{stats.get('energie_moyenne', 0):.1f}/10")

    # Distribution humeurs
    if stats.get("distribution_humeurs"):
        st.markdown("**Distribution des humeurs:**")
        for humeur, count in stats["distribution_humeurs"].items():
            emoji = HUMEUR_EMOJIS.get(HumeurEnum(humeur), "")
            st.progress(
                count / max(stats.get("total_entrees", 1), 1),
                text=f"{emoji} {humeur}: {count}",
            )
